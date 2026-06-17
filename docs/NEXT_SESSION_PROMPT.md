# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-17 / git head: e77423e / branch: feature-trio-clean
Image: sha256:5ded295e2621c48bd05e01c2e9334f84c8707d2e21030c7d6d4e957b2ec49728

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```
Expected when healthy:
- fault-trigger-ui: 1/1 Running
- **ollama replicas=0 (GPU OFF — DO NOT scale up)**
- ollama_online: False, model: offline (expected dev default)
- field_intel=11, rag_documents=20

## STEP 2: Read DEMO_MASTER.md
```bash
cat docs/DEMO_MASTER.md
```

## STEP 3: Next Implementation Tasks

### PRIORITY 1 (first task next session) — Slide deck readability pass
Both `gke/fault-trigger-ui/slides/intro.html` and `gke/fault-trigger-ui/slides/h1.html` need a batched readability and layout upgrade pass. These were reviewed live on the BenQ display during Session BS+17 and a precise, high-fidelity list of changes was captured. **Implement everything below in a SINGLE `replace_in_file` call per file, then a single verify + build + deploy.**

---

### A. `slides/intro.html` — All Three Slides Enlarged

#### Slide 1 (What is GDC?)
- **`.s1-left` flex-basis**: 540px → **600px** (larger left column for text card)
- **`.s1-desc` font-size**: 1.25rem → **1.45rem**; max-width: 440px → **540px**
- **Bottom bullet font-size**: 0.72rem → **0.88rem**

#### Slide 2 (When Should You Consider GDC?)
- **Title highlight**: Change `<em style="font-style:normal;color:#3b82f6">Consider</em> Using GDC` to highlight the **entire phrase**: `<em style="font-style:normal;color:#3b82f6">Consider Using GDC</em>` — all three words in bright blue.
- **`.s2-pillar` padding**: 32px 24px → **40px 28px**; gap: 16px → **20px**
- **`.s2-icon` size**: 56px × 56px → **72px × 72px**; inner SVG viewBox `width/height` 34 → **42** (scale SVGs uniformly)
- **`.s2-pillar h3`**: 1.2rem → **1.4rem**
- **`.s2-pillar p`**: 0.88rem → **1.02rem**

#### Slide 3 (Flexible Deployment Models)
- **`.s3-hw-box`**: width 180px × height 120px → **width 220px × height 140px**; inner SVG `width/height` scale to match (140×100 → 176×126 approximately, adjust viewBox scale uniformly)
- **`.s3-model h3`**: 1.15rem → **1.38rem**
- **`.s3-model p`**: 0.88rem → **1.02rem**; max-width: 280px → **330px**

---

### B. `slides/h1.html` — Five Slides Upgraded

#### Slide 1 (THE SCENARIO) — Well description box & sensor gauges
- **`.well-label` font-size**: 0.65rem → **0.85rem**; width: 116px → **140px**
- **`.well-val` font-size**: 0.65rem → **0.85rem**; line-height 1.5 → **1.65**
- **Tile range direction (LOW on LEFT)**: Swap the order inside `class="tile-range"` for PIP and Amps so the fault/low value is on the left and nominal is on the right, with a left-pointing arrow:
  - PIP: was `~1,245 PSI ... → ~850 PSI` → becomes `~850 PSI ← ... ~1,245 PSI` (amber span first, green span second, arrow ←)
  - Amps: was `~68 A ... → ~28 A` → becomes `~28 A ← ... ~68 A` (amber first, green second)
- **Winding Temp tile — add IDs** (currently static, needs to become scrubber-reactive):
  - Card div: add `id="p1-tmp-card"`
  - Header `div.tile-header`: add `id="p1-tmp-header"`
  - Arrow `<span>`: change `WINDING TEMP →` to `WINDING TEMP <span id="p1-tmp-arrow">→</span>`, add status: `<span style="font-size:0.50rem" id="p1-tmp-status">NOMINAL</span>`
  - Bar fill: add `id="p1-tmp-fill"` to the inner div
  - Readout `div`: add `id="p1-tmp-readout"`
- **Vibration tile — add IDs** (same pattern):
  - Card div: add `id="p1-vib-card"`
  - Header: add `id="p1-vib-header"`; change `VIBRATION →` to `VIBRATION <span id="p1-vib-arrow">→</span>`, add `id="p1-vib-status"`
  - Bar fill: add `id="p1-vib-fill"`
  - Readout: add `id="p1-vib-readout"`
- **`applyState` Slide 0 block** — extend to animate Temp (UP) and Vib (UP):
  ```js
  // Winding Temp — goes UP as t increases (bad = high, amber at t>0.5)
  var tmpFill = document.getElementById('p1-tmp-fill');
  if (tmpFill) { tmpFill.style.width = (40 + 45*t).toFixed(1) + '%'; tmpFill.style.background = isF ? amber : green; }
  var tmpH = document.getElementById('p1-tmp-header');
  if (tmpH) tmpH.style.color = isF ? 'var(--amber)' : '#94a3b8';
  var tmpAr = document.getElementById('p1-tmp-arrow');
  if (tmpAr) tmpAr.textContent = isF ? '↑' : '→';
  var tmpSt = document.getElementById('p1-tmp-status');
  if (tmpSt) { tmpSt.textContent = isF ? 'RISING' : 'FLAT EARLY'; tmpSt.style.color = isF ? 'var(--amber)' : 'rgba(100,116,139,0.5)'; }
  var tmpRo = document.getElementById('p1-tmp-readout');
  if (tmpRo) { tmpRo.textContent = isF ? '~248°F · rising' : '~197°F · stays flat early'; tmpRo.style.color = isF ? 'rgba(251,191,36,0.75)' : 'rgba(74,222,128,0.6)'; }
  var tmpCard = document.getElementById('p1-tmp-card');
  if (tmpCard) tmpCard.style.borderColor = isF ? 'rgba(251,191,36,0.32)' : 'rgba(100,116,139,0.2)';

  // Vibration — goes UP as t increases (bad = high, amber at t>0.5)
  var vibFill = document.getElementById('p1-vib-fill');
  if (vibFill) { vibFill.style.width = (20 + 55*t).toFixed(1) + '%'; vibFill.style.background = isF ? amber : green; }
  var vibH = document.getElementById('p1-vib-header');
  if (vibH) vibH.style.color = isF ? 'var(--amber)' : '#94a3b8';
  var vibAr = document.getElementById('p1-vib-arrow');
  if (vibAr) vibAr.textContent = isF ? '↑' : '→';
  var vibSt = document.getElementById('p1-vib-status');
  if (vibSt) { vibSt.textContent = isF ? 'RISING' : 'FLAT'; vibSt.style.color = isF ? 'var(--amber)' : 'rgba(100,116,139,0.5)'; }
  var vibRo = document.getElementById('p1-vib-readout');
  if (vibRo) { vibRo.textContent = isF ? '~5.4 mm/s · alert' : '~1.4 mm/s · stays flat'; vibRo.style.color = isF ? 'rgba(251,191,36,0.75)' : 'rgba(74,222,128,0.6)'; }
  var vibCard = document.getElementById('p1-vib-card');
  if (vibCard) vibCard.style.borderColor = isF ? 'rgba(251,191,36,0.32)' : 'rgba(100,116,139,0.2)';
  ```

#### Slide 2 (AMBIGUOUS TELEMETRY) — Two-line description
- **Split top `slide-sub`** at the period to remove the run-on sentence. Break after "sensor string." so the result is two visible sentences:
  - Line 1: `Gas Entrainment and Fluid Drawdown produce <strong style="color:#93c5fd">identical Pump Inlet Pressure and Amps decline</strong> on an intake-only sensor string.`
  - Line 2: `The cause — and the safe action — are not in these numbers.`

#### Slide 3 (DECISION SUPPORT) — CHOICE headers, bigger text, two-line sub
- **Split top `slide-sub`** at "Neither" — break into two separate paragraphs:
  - P1: `An unloading well forces a blind trade-off: slow down to clear gas and risk sand settling, or shut in and risk sand fallback.`
  - P2 (use `<p class="slide-sub" style="margin-top:4px">`): `<strong style="color:#fbbf24">Neither is safe without knowing the well's completion history.</strong>`
- **Card header font-size**: 0.65rem → **0.82rem**; prepend `CHOICE: ` to both card titles:
  - Card 1 header: `CHOICE: VFD SPEED-DOWN <span style="font-weight:400;color:var(--muted)">52 → 44 Hz</span>`
  - Card 2 header: `CHOICE: EMERGENCY SHUT-IN <span style="font-weight:400;color:var(--muted)">Stop Pump</span>`
- **Outcome title font-size**: 0.60rem → **0.72rem**
- **Outcome detail font-size**: 0.55rem → **0.65rem**
- **Bottom callout text**: 0.85rem → **1.05rem** for headline; 0.65rem → **0.80rem** for sub

#### Slide 4 (ADDING CONTEXT) — Honest GDC timing, bigger text, white bottom statements
- **All text inside Without GDC box**: increase font sizes ~25% (0.58rem→0.72rem; 0.52rem→0.65rem; 0.75rem→0.88rem)
- **All text inside With GDC box**: same scale-up
- **Change `< 2 SECONDS`** → **`< 10 SECONDS`** (in the `font-size:0.75rem;font-weight:800;color:#60a5fa` div above the stopwatch)
- **Change bottom footer text**: `in under 2 seconds` → **`in under 10 seconds`**
- **Change text**: `GDC reads the file` → **`GDC does the research`** (the bottom italic statement in the With GDC box)
- **Bottom significant-difference statements**: Remove `background:rgba(...)`, `border:1px solid (...)`, and `border-radius:...` from the boxed bottom statements in both columns. Replace with:
  - Without GDC: plain `<div style="margin-top:auto;padding-top:8px;font-size:0.75rem;color:#e2e8f0;font-style:italic;line-height:1.5">Finding and assembling these correctly, under alarm load, before the window closes — this is what gets missed.</div>`
  - With GDC: `<div style="margin-top:auto;padding-top:8px;font-size:0.75rem;color:#e2e8f0;font-style:italic;line-height:1.5">GDC does the research. The call is confident, cited, and auditable.</div>`

#### Slide 5 (INDUSTRIAL APPLICATION) — Two-line header, remove faint artifacts, unified column headers, larger text, no repeated STATE/CONTEXT labels
- **Split top `slide-sub`** into two lines, breaking after the colon:
  - Line 1: `Every industry running physical assets faces the same structural gap:`
  - Line 2 (bold): `<strong style="color:#4ade80">telemetry reports state; unstructured documents hold context</strong>. GDC brings AI/ML to the data — on-premises.`
- **Remove faint background artifacts**: Search for any `color:rgba(74,222,128,0.75)` or similar ultra-faint text inside the row divs that may render as dim background text. Remove any `.anim-row` children containing only decorative/low-opacity text that serves no real informational purpose.
- **Add unified column header row** at the top of the flex column, BEFORE the 3 animated rows:
  ```html
  <div style="flex-shrink:0;display:flex;gap:12px;padding:5px 16px;margin-bottom:4px;font-size:0.58rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:rgba(148,163,184,0.55)">
    <div style="flex:0 0 110px">VERTICAL</div>
    <div style="flex:1">OBSERVATIONAL STATE (SCADA / APM)</div>
    <div style="font-size:1rem;color:rgba(148,163,184,0.25);flex-shrink:0;padding:0 6px">→</div>
    <div style="flex:1">DOCUMENTED CONTEXT (GDC)</div>
    <div style="flex:0 0 200px;text-align:right">EXAMPLE RESOLUTION</div>
  </div>
  ```
- **Remove the per-row `STATE` and `CONTEXT` labels** (the `font-size:0.50rem;font-weight:700;text-transform:uppercase` divs) from all 3 rows — they are now represented by the header above.
- **Increase row text sizes**: main text 0.70rem → **0.85rem**; sub-description 0.58rem → **0.70rem**; asset badge 0.60rem → **0.72rem**
- **Right-column `EXAMPLE RESOLUTION` items**: change their `flex:0 0 185px` to `flex:0 0 200px` and font-size from `0.55rem` to `0.68rem` to match the column header width

---

## STEP 4: After Discern Deck changes, also update Intro Deck separately (second deploy)

The `.s1-left` flex-basis override in the `slide-body` inline style and the CSS class for `.s1-left` conflict — use the inline style override on the `<div class="s1-left">` tag, not the CSS class itself.

---

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| `PIP` (61 occurrences) → `Pump Inlet Pressure` in app.js/app.py/templates | ⏸ Deferred — decks use terms.js; slides use full name; app gets a separate cleanup pass |
| Authored `~$2,500` / `~$150k` → comparative language in app replay sections | ⏸ Deferred — decks are clean; live replay narrative still has authored $ |
| `$150,000` × 3 in tab_architecture.html (ROI Equation + Fleet Financials Ledger) | ⏸ Deferred — Architecture tab, not H1 demo path |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Slides: `gke/fault-trigger-ui/slides/` — **baked into the image** (COPY slides/ in Dockerfile). Always docker build + push + rollout restart after slide edits.
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` ONLY for explicit LLM test; ALWAYS pair with gpu-stop.sh
- **NO ollama-scheduler CronJobs** — both deleted Session BS+9 (conflict with GPU discipline)
- No Jinja2 in templates
- **Vizier:** 3 billing auto-triggers removed (Session BS+9). One call per explicit ▶ Run click.

## Build / deploy commands
```bash
cd gke/fault-trigger-ui
python3 ../../scripts/verify_templates.py   # must pass before build
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=90s
```

## Slide URLs for live review
| Purpose | URL |
|---|---|
| H1 deck | gdc-pm.bdau.io/slides/h1.html |
| H2 deck | gdc-pm.bdau.io/slides/h2.html |
| H3 deck | gdc-pm.bdau.io/slides/h3.html |
| Intro deck | gdc-pm.bdau.io/slides/intro.html |
| Full demo | gdc-pm.bdau.io |
| Author mode (split debug) | gdc-pm.bdau.io/slides/h1.html?author |
