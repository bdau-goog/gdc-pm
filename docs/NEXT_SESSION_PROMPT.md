# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 8, 2026 (Session L prep — Triage & Surveillance redesign spec locked)
**git head:** `ff27e7f` (docs: Session K handoff)
**fault-trigger-ui image:** `sha256:d66b61e6` (1/1 Running — Session K)
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
source .env && kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
source .env && kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2 · rag_documents: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Task — Session L

### Context: Design Decisions Locked in Session L Prep

**CRITICAL — READ BEFORE WRITING CODE:**

The user reviewed the H1 "Discern" tab and identified three fundamental design requirements that require a clean-slate rework of the Left telemetry column:

**Decision 1 — De-Gamification:** Remove ALL game/gamble terminology:
- "Double-Blind Choice Game" → **"Comparative Detection Scenario"**
- "Blind Gamble" / "🎲" → **"Reactive Manual Intervention"**
- "Ready for Double-Blind Choice Game" → **"Pad Alpha Surveillance Active"**
- "Inject Unloading Anomaly" → **"Ingest Pad Anomalies"**

**Decision 2 — Resizability:** ALL panels must be resizable:
- **Horizontal**: A vertical `.h1-splitter` drag handle between the Left (Telemetry) and Right (Decision Console) columns, adjusting `h1SplitPercent` from 25%–75%.
- **Vertical**: A horizontal `.h1-v-splitter` drag handle inside the Left column between sensor cards and the trend sparkline area, adjusting `h1ChartH` from 80px–320px.
- Plotly chart resize must fire after both drags via `$nextTick`.

**Decision 3 — Workload Scaling via Randomized Pad Triage:**
- Replace single-well sensor bars with a **Pad Alpha 6-well surveillance grid** (Wells A-1 to A-6, interactive click-through) at the top of the Left column.
- Clicking `⚡ Ingest Pad Anomalies` **randomly selects a target well** to inject the unloading anomaly (gas lock or drawdown, 50/50 as before).
- Two adjacent wells experience **benign transient disturbances** (gas venting) that trigger SCADA nuisance alarms — but GDC automatically suppresses them based on retrieved Daily Well Test logs.
- Clicking any well (alerting, suppressed, or nominal) dynamically loads that well's live sensor data and GDC Advisor verdict.

**Decision 4 — Live Sparkline Cards replacing Sensor Bars:**
- Remove the 4 ISA-101 horizontal progress bars entirely.
- Replace with **4 individual stacked Plotly sparkline trend charts** (PIP, Amps, Temp, Vib).
- Each card has a **large bold digital readout** (live real-time value in the chart title/annotation).
- Each card has a **subtle horizontal dashed red line** at the SCADA alarm threshold.

**Decision 5 — Anomaly Departure Rate:**
- Add a `h1RampSpeed` selector in the banner: **Standard** (900s / 15–30 min window) and **Accelerated** (300s / 5–10 min window). This maps directly to `duration_seconds` in the API call.

---

### Session L Implementation Steps (in order)

**Step 1 — Update DEMO_MASTER.md §4** (doc only — confirm spec before coding):
- Update §4 heading, all action button labels, all "game/gamble" language per decisions above.
- No code written until spec is confirmed.

**Step 2 — app.js data() state additions:**
```js
h1SelectedWell: 'ESP-ALPHA-1',    // currently viewed well in left column
h1TargetWell: null,               // randomly injected alerting well
h1NuisanceWells: [],              // benign disturbance wells (2 adjacent)
h1SplitPercent: 38,               // horizontal split % between L/R columns
h1ChartH: 140,                    // vertical sparkline height (px)
h1RampSpeed: 'standard',          // 'standard' | 'accelerated'
h1WellData: {},                   // per-well telemetry cache: { 'ESP-ALPHA-N': {psi, amps, temp, vib} }
```

**Step 3 — launchHorizon1Unloading()** changes:
- Pick `h1TargetWell` randomly from `['ESP-ALPHA-1'..'ESP-ALPHA-6']`.
- Pick two adjacent well IDs as `h1NuisanceWells`.
- Inject `fault_type` (gas_lock or fluid_drawdown, 50/50) on `h1TargetWell` only.
- Set `duration_seconds = h1RampSpeed === 'accelerated' ? 300 : 900`.

**Step 4 — initH1SplitterDrag() and initH1ChartVerticalDrag()** (new app.js methods):
- Horizontal drag: track `mousedown` on `.h1-splitter`, update `h1SplitPercent` on mousemove, call `Plotly.Plots.resize` on all 4 sparkline DOM elements.
- Vertical drag: track `mousedown` on `.h1-v-splitter`, update `h1ChartH` on mousemove, call Plotly resize.
- Double-click on either handle resets to defaults.

**Step 5 — _renderH1Charts(d)** rewrite:
- Remove the existing dual-axis PIP/Amps combined chart.
- Render 4 separate Plotly sparklines into `#h1-spark-psi`, `#h1-spark-amps`, `#h1-spark-temp`, `#h1-spark-vib`.
- Each chart uses `height: this.h1ChartH`.
- Traces use historical data from `d.sensors.psi.traces[0]` etc.
- Add a horizontal `shape` (dashed red line) at the SCADA threshold (800 PSI, 50A, 280°F, 8.0 mm/s).
- Add an `annotation` in top-right corner with the current live value in large text.

**Step 6 — index.html Left column rebuild:**
- Replace the existing `.h1-telemetry-col` contents.
- Add interactive Pad Alpha Surveillance Grid (6 well cards, clickable, color-coded by status).
- Stack 4 sparkline chart divs (`h1-spark-psi`, `h1-spark-amps`, `h1-spark-temp`, `h1-spark-vib`).
- Insert `.h1-v-splitter` handle below the Pad Grid.
- Insert `.h1-splitter` handle between Left and Right columns.

**Step 7 — index.html Right column changes:**
- Update banner: "Ingest Pad Anomalies" button with a ramp speed toggle.
- De-gamify all text labels per Decisions 1 above.

**Step 8 — styles.css additions:**
- `.h1-splitter`, `.h1-v-splitter`: cursor, size, hover/drag states.
- `.h1-well-card`, `.h1-well-card-alerting`, `.h1-well-card-suppressed`: grid/hover colors.
- `.h1-spark-card`: container for each individual trend chart.

**Step 9 — Build, push, rollout, verify** per standard procedure.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 game/gamble labels | ⚠ Stale — Session L | All to be replaced per Decision 1 |
| H1 sensor bars (horizontal) | ⚠ Remove — Session L | Replace with sparkline cards |
| H1 dual-axis chart | ⚠ Remove — Session L | Replace with 4 individual sparklines |
| H1 resizability | ⚠ Missing — Session L | Add horizontal + vertical drag handles |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- Batch all edits to same file in ONE `replace_in_file` call
- ALL kubectl/gcloud commands require `source .env &&` prefix
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
