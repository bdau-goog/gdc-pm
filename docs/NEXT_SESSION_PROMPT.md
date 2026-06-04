# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session M end)
**Git Head:** `9b77d4b` — clean working tree
**fault-trigger-ui image digest:** `sha256:55e5626853cc1d6da10390159b90432eeacaf60e265254d765428cdb1a26a0db`
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected healthy:**
- All pods 1/1 Running · fault-trigger-ui-64d4b6b944-9m5xb
- ollama_online: True · model: gemma4:latest
- field_intel: ~99–110 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read the **last 2 entries** in SESSION_LOG.md (Sessions M and L).

---

## STEP 3: What Was Built This Session (H1 Bug Fixes)

**Live at:** `http://gdc-pm.bdau.io` → "Detect" tab

### Changes deployed (commit `9b77d4b`):

**Cost-zone chart** — `_renderH1Charts` completely rewritten:
- Pre-injection: shows "Live Sensor Reading" + "SCADA Alarm Threshold" only. Clean "NOW — Monitoring" label. No fault projection, no declining lines.
- Post-injection: adds "GDC ML Forecast" (orange dashed) + three colored background zones (green=$0, amber=~$2k, red=$150k) + "🤖 AI detects — ACT NOW", "📡 SCADA alarms T+Xm", "⛔ PNR" event pins + cost labels at bottom of each zone.
- Removed "ML RUL Projection" label (integrity violation) — replaced with "GDC ML Forecast".

**Column resize splitters** — two `.h1-splitter` divs added between well-strip↔center and center↔copilot. `initH1CenterSplit(e, side)` method wired to both. Replaces dead `initH1Resize` (was pointing at `.h3-main-body` which doesn't exist in H1 layout).

**NS resize handle** — `<div class="h1-ns-handle">` added between chart and Window of Options (v-if="h1Injected"). `initH1NsSplit` wired. `h1ChartH` data property (starts 200px) controls chart height dynamically via `:style`.

**Well strip wider** — width 82px → 110px. SVG `max-height:215px` → `flex:1;min-height:0` so it fills the full column height.

**Intel feed timestamps** — `<span class="h1-ic-time">{{ item.ts_label }}</span>` added to each `.h1-ic-row`. The `ts_label` field is already returned by `/api/intelligence-feed` (computed server-side as "just now", "Xm ago", "Xh ago").

**`h1SplitPercent` initial value** changed 60 → 36 (matches h1-center's CSS `flex:0 0 36%`). `h1ChartH: 200` added to data.

---

## STEP 4: Next Session Flow

### A. Collect visual feedback on Detect tab

Open `http://gdc-pm.bdau.io`, navigate to "Detect" tab. Key things to verify:
1. Well strip — now 110px wide, fills full column height?
2. Chart pre-injection — clean "Live Sensor Reading" + SCADA threshold, no fault elements?
3. Column drag handles — left and right splitters draggable?
4. Intel feed rows — timestamp shows (e.g., "2h ago")?
5. Inject fault — cost-zone chart appears with green/amber/red zones + AI vs SCADA pins?
6. NS handle appears below chart after injection — draggable?

### B. After visual feedback: H2 (Discern) tab redesign

Per DEMO_MASTER.md §5:
- Reuse ALL CSS from H1 redesign (`.dr-bar`, `.h1-body`, `.h1-copilot-pane`, `.h1-intel-compact`)
- Primary visual: two-line superimposed chart — Vibration (rising, orange) + Motor Temp (flat, blue)
- H2 evidence chips in dual-reality bar: 📊 Vibration↑, 📊 Temp─(flat), 📋 Shift note, 🧪 Separator test, 📋 Choke log, 📖 OEM guide
- LLM copilot: "$1,500 truck roll, not $150,000 pump pull"
- No Window of Options for H2

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — no `browser_action` tool
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain
- Fleet Operations tab: do NOT re-add
- Financial case: LLM only, no static financial cards
- Token budget: batch all edits to same file in ONE replace_in_file call
- Correct registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
