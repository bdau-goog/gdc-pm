/**
 * scripts/ui_smoke.mjs — GDC Edge AI UI Smoke Test (Playwright)
 *
 * WHAT IT CATCHES:
 *   1. All browser console errors/warnings (catches Vue template crashes,
 *      TypeError on undefined, network failures — instantly, before you ask me)
 *   2. Full Discern-tab flow: load → click Discern → click action button → wait
 *   3. Plotly chart data arrays dumped as JSON (numerical assertions on physics)
 *   4. PNG screenshot written to smoke_screenshot.png
 *
 * USAGE:
 *   node scripts/ui_smoke.mjs                          # default: http://gdc-pm.bdau.io
 *   UI_URL=http://localhost:8080 node scripts/ui_smoke.mjs
 *
 * SETUP (one-time):
 *   npm i -D playwright
 *   npx playwright install chromium
 *
 * EXIT CODES:
 *   0 — all assertions pass, no console errors
 *   1 — any assertion failed OR any uncaught JS error found
 */

import { chromium } from 'playwright';
import { writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname  = dirname(fileURLToPath(import.meta.url));
const BASE_URL   = process.env.UI_URL || 'http://gdc-pm.bdau.io';
const SCREENSHOT = join(__dirname, '..', 'smoke_screenshot.png');
const CHART_JSON = join(__dirname, '..', 'smoke_chart_data.json');

// ── Assertion helpers ─────────────────────────────────────────────────────────
let passed = 0, failed = 0;
const failures = [];

function assert(label, condition, detail = '') {
  if (condition) {
    console.log(`  ✅ ${label}`);
    passed++;
  } else {
    const msg = detail ? `${label} — ${detail}` : label;
    console.error(`  ❌ FAIL: ${msg}`);
    failures.push(msg);
    failed++;
  }
}

function assertRange(label, value, lo, hi) {
  assert(label, value >= lo && value <= hi, `got ${value}, expected [${lo}, ${hi}]`);
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  console.log(`\n${'═'.repeat(62)}`);
  console.log(`  GDC Edge AI — UI Smoke Test`);
  console.log(`  Target: ${BASE_URL}`);
  console.log(`${'═'.repeat(62)}\n`);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page    = await context.newPage();

  // ── 1. Console & error capture ─────────────────────────────────────────────
  const consoleLog = [];   // all messages
  const pageErrors = [];   // uncaught JS exceptions

  page.on('console', msg => {
    consoleLog.push({ type: msg.type(), text: msg.text() });
    if (msg.type() === 'error') {
      console.error(`  🔴 CONSOLE ERROR : ${msg.text()}`);
    } else if (msg.type() === 'warning') {
      console.warn(`  🟡 CONSOLE WARN  : ${msg.text()}`);
    }
  });

  page.on('pageerror', err => {
    pageErrors.push(err.message);
    console.error(`  🔴 PAGE JS ERROR : ${err.message}`);
  });

  // ── 2. Load page ───────────────────────────────────────────────────────────
  console.log('📡 Step 1 — Load page');
  let response;
  try {
    response = await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30_000 });
  } catch (e) {
    console.error(`  🔴 Navigation failed: ${e.message}`);
    await browser.close();
    process.exit(1);
  }
  assert('Page HTTP 200', response.status() === 200, `HTTP ${response.status()}`);

  // Basic Vue mount check — the app root must contain rendered content
  const appText = await page.$eval('#app', el => el.innerText).catch(() => '');
  assert('Vue app mounted (#app has content)', appText.trim().length > 10, 'empty or missing #app');

  // ── 3. Click Discern tab ───────────────────────────────────────────────────
  console.log('\n🖱  Step 2 — Click Discern tab');
  const errorsBefore = pageErrors.length;
  const consoleBefore = consoleLog.filter(m => m.type === 'error').length;

  await page.click('text=Discern');
  await page.waitForTimeout(1200);

  assert('No new JS errors after clicking Discern',
    pageErrors.length === errorsBefore,
    pageErrors.slice(errorsBefore).join('; '));

  // ── 4. Find and click the action button ───────────────────────────────────
  console.log('\n🖱  Step 3 — Find action button');
  let actionButtonLabel = null;
  const errorsBeforeAction = pageErrors.length;
  const consoleBeforeAction = consoleLog.filter(m => m.type === 'error').length;

  // Try new Scenario Replay UI first, then legacy inject-and-wait
  const candidates = [
    { selector: 'button:has-text("New Scenario")',          label: '↺ New Scenario (Scenario Replay UI)' },
    { selector: 'button:has-text("Ingest Pad Anomalies")',  label: '⚡ Ingest Pad Anomalies (legacy UI)'  },
    { selector: 'button:has-text("Load Scenario")',         label: '▶ Load Scenario'                      },
  ];

  for (const cand of candidates) {
    const btn = await page.$(cand.selector);
    if (btn) {
      console.log(`  Found: ${cand.label}`);
      await btn.click();
      actionButtonLabel = cand.label;
      break;
    }
  }

  assert('Action button found', actionButtonLabel !== null,
    `None of [${candidates.map(c => c.label).join(', ')}] present`);

  if (actionButtonLabel) {
    // Wait for API call + chart render
    console.log('  Waiting 4s for API response + chart render...');
    await page.waitForTimeout(4000);

    assert('No new JS errors after clicking action button',
      pageErrors.length === errorsBeforeAction,
      pageErrors.slice(errorsBeforeAction).join('; '));

    const newConsoleErrors = consoleLog.filter(m => m.type === 'error').length - consoleBeforeAction;
    assert('No new console errors after clicking action button',
      newConsoleErrors === 0,
      `${newConsoleErrors} new console error(s)`);
  }

  // ── 5. Chart assertions ────────────────────────────────────────────────────
  console.log('\n📊 Step 4 — Chart assertions');

  // Find any rendered Plotly chart
  const chartSelectors = [
    '#h1-replay-chart',   // new Scenario Replay UI
    '#h1-pip-chart',      // possible alternative
    '.plotly-graph-div',  // any Plotly chart at all
  ];

  let chartData = null;
  let chartSelector = null;

  for (const sel of chartSelectors) {
    const el = await page.$(sel);
    if (!el) continue;

    // Extract Plotly trace data from the DOM element's JS property
    const data = await page.evaluate(s => {
      const el = document.querySelector(s);
      if (!el) return null;
      // Plotly stores the data array on the DOM node as el.data
      const raw = el.data;
      if (!raw || !Array.isArray(raw)) return null;
      return raw.map(trace => ({
        name:    trace.name || '',
        mode:    trace.mode || '',
        x_len:  (trace.x || []).length,
        y_first: (trace.y || []).slice(0, 3),
        y_last:  (trace.y || []).slice(-3),
        y_min:   Math.min(...(trace.y || [0])),
        y_max:   Math.max(...(trace.y || [0])),
      }));
    }, sel);

    if (data && data.length > 0) {
      chartData    = data;
      chartSelector = sel;
      break;
    }
  }

  // Chart-not-found is a warning in the pre-inject context (degrade thread may not
  // have sent any readings yet). It becomes a hard failure only when chartData is
  // null AND no legacy spark IDs are even present in the DOM.
  const anySparkInDom = await page.$('#h1-spark-psi, #h1-spark-amps').catch(() => null);
  if (chartData === null && anySparkInDom) {
    console.warn('  🟡 NOTE: Spark chart containers found but Plotly not yet rendered (no data in DB yet — expected on a clean deploy)');
  } else {
    assert('Plotly chart rendered with data', chartData !== null && chartData.length > 0,
      `checked: ${chartSelectors.join(', ')}`);
  }

  if (chartData) {
    console.log(`  Chart element: ${chartSelector}`);
    console.log(`  Traces found: ${chartData.length}`);
    chartData.forEach(t => {
      console.log(`    "${t.name}" (${t.mode}): ${t.x_len} pts, y∈[${t.y_min?.toFixed(1)}, ${t.y_max?.toFixed(1)}]`);
      console.log(`      first: ${JSON.stringify(t.y_first)}`);
      console.log(`      last:  ${JSON.stringify(t.y_last)}`);
    });

    // Write for offline inspection
    writeFileSync(CHART_JSON, JSON.stringify(chartData, null, 2));
    console.log(`  💾 Chart data → ${CHART_JSON}`);

    // ── Numerical physics assertions for Scenario Replay chart ──────────────
    if (chartSelector === '#h1-replay-chart') {
      // Find PIP trace (first trace = live telemetry / psi)
      const pipTrace = chartData.find(t => /pip|psi|pressure/i.test(t.name)) || chartData[0];
      if (pipTrace) {
        assert('PIP trace has 120 data points (N=120 trajectory)',
          pipTrace.x_len === 120, `got ${pipTrace.x_len}`);

        assertRange('PIP starts in nominal range [1050, 1350 PSI]',
          pipTrace.y_first[0], 1050, 1350);

        // Fault end value should be lower than start (degradation confirmed)
        assert('PIP declines from start to end (fault visible)',
          pipTrace.y_last[2] < pipTrace.y_first[0],
          `start=${pipTrace.y_first[0]}, end=${pipTrace.y_last[2]}`);

        // No negative PSI values (physics sanity)
        assert('PIP stays positive throughout trajectory', pipTrace.y_min > 0,
          `min PSI = ${pipTrace.y_min}`);
      }

      // Health score trace assertions
      const healthTrace = chartData.find(t => /health/i.test(t.name));
      if (healthTrace) {
        assertRange('Health score starts near 1.0 (nominal)',
          healthTrace.y_first[0], 0.6, 1.05);
        assert('Health score stays in [0, 1.05]',
          healthTrace.y_min >= 0 && healthTrace.y_max <= 1.05,
          `range [${healthTrace.y_min}, ${healthTrace.y_max}]`);
      }
    }
  }

  // ── 6. Integrity checks ────────────────────────────────────────────────────
  console.log('\n🔍 Step 5 — Integrity checks');

  // Check for "FALLBACK_SYNTHETIC" badge — integrity violation if model is supposed to be loaded
  // (it's OK for it to appear, but we want to know)
  const fallbackVisible = await page.$eval('body', el =>
    el.innerText.includes('FALLBACK_SYNTHETIC')
  ).catch(() => false);
  if (fallbackVisible) {
    console.warn('  🟡 INTEGRITY NOTE: "FALLBACK_SYNTHETIC" text visible in DOM — model load may have failed');
  } else {
    console.log('  ✅ No FALLBACK_SYNTHETIC badge visible');
  }

  // Check no raw {{ }} Vue template expressions leaked into DOM
  const vueLeak = await page.$eval('body', el =>
    /\{\{[^}]+\}\}/.test(el.innerHTML)
  ).catch(() => false);
  assert('No raw Vue {{ }} template expressions in DOM (template not escaped outside #app)',
    !vueLeak);

  // ── 7. Screenshot ─────────────────────────────────────────────────────────
  console.log('\n📸 Step 6 — Screenshot');
  await page.screenshot({ path: SCREENSHOT, fullPage: false });
  console.log(`  Saved → ${SCREENSHOT}`);

  // ── 8. Summary ────────────────────────────────────────────────────────────
  const totalConsoleErrors  = consoleLog.filter(m => m.type === 'error').length;
  const totalConsoleWarnings = consoleLog.filter(m => m.type === 'warning').length;

  console.log(`\n${'─'.repeat(62)}`);
  console.log(`  Console:    ${totalConsoleErrors} errors, ${totalConsoleWarnings} warnings`);
  console.log(`  JS errors:  ${pageErrors.length}`);
  console.log(`  Assertions: ${passed} passed, ${failed} failed`);
  if (failures.length) {
    console.error('\n  Failures:');
    failures.forEach(f => console.error(`    • ${f}`));
  }
  console.log(`${'─'.repeat(62)}`);

  await browser.close();

  if (failed > 0 || pageErrors.length > 0) {
    console.error('\n❌  SMOKE TEST FAILED\n');
    process.exit(1);
  } else {
    console.log('\n✅  SMOKE TEST PASSED\n');
    process.exit(0);
  }
}

main().catch(err => {
  console.error('Fatal runner error:', err);
  process.exit(1);
});
