# GDC-PM Phase 3 — Deployment Status & Handoff
**Status:** Complete — All 7 Tasks + 3 Bug Fixes Deployed  
**Date:** 2026-05-08  
**Preceded by:** `PHASE_2_DEPLOYMENT_STATUS.md`  
**UI:** http://35.188.3.97  

---

## What Phase 3 Delivered

### Task 1: XGBoost RUL — Fault-Only Clean Feature Extraction (`app.py`)
**Root cause fixed:** The 10-minute query window mixed pre-fault normal readings with fault readings, causing training-serving skew ("arc" artifact). Slope started near-zero (inflated RUL ~3.5h) then steepened as the window filled with fault data (RUL crashed to ~41m).

**Fix:** Filter to fault-labeled readings only before computing slope features. If ≥6 fault readings exist, use fault-only window; otherwise fall back to full window. Feature vector: `[last_psi, last_temp, last_vib, dpsi_dt, dtemp_dt, dvib_dt]` where slopes are converted to PSI/min (× 12 readings/min). V1 model output used directly as minutes.

**Smoothing:** 10-reading exponential-weighted average (α=0.75) on XGBoost output — prevents single noisy predictions from flipping the display.

**Important:** V1 model variance is intentional — it's the MLOps demo's opening act.

---

### Task 7: Fault Onset Time Tracking (`app.py` — `_run_degrade_thread`)
Added `fault_onset_utc` to `active_degrades` dict at ramp start. Used by:
- PNR state detection (is_pnr_exceeded computation)
- Cloud Alert vertical line placement (fault_onset + T+20m)
- Time-to-React arrows on the Edge vs Cloud chart

---

### Task 2: V2 RUL Model Training (`scripts/retrain_edge_models.py`)
Generated training data matching the exact 5-second noise profile of `_run_degrade_thread`:
- `psi ± psi × 0.002`, `temp ± temp × 0.001`, `vib ± vib × 0.005`
- 300 sequences × 11 fault types × 720 steps = ~2.4M rows total
- Slope features computed over 60-reading (5-minute) rolling window
- RUL label: minutes (0–60.0)

**Results:**

| Asset Class | RMSE (min) | Spot-check error (t=50%) |
|---|---|---|
| ESP | 0.204 | 0.1m |
| Gas Lift | 0.227 | 0.1m |
| Mud Pump | 0.166 | 0.2m |
| Top Drive | 0.176 | 0.3m |

V2 models saved to `gke/fault-trigger-ui/models/*_rul_v2.ubj` and embedded in the container.

---

### Task 3: MLOps "Drift & Retrain" Demo Flow (`app.py` + `index.html`)
**Backend:**
- Dual model registry: `RUL_MODELS_V1` (V1 `.ubj`) + `RUL_MODELS_V2` (V2 `_v2.ubj`)
- `GET /api/model/version` — returns active version + loaded asset classes
- `POST /api/model/version` — swaps active registry, clears smoothing buffers
- Startup default: V1 (drifted, for the demo narrative)

**Frontend:**
- "☁ Sync & Retrain via Vertex AI" button — appears in plot header when active fault exists AND model is V1
- 3-step pipeline toast sequence (1.5s + 2.5s + 1.5s): BigQuery export → Vertex AI training → GDC Edge Registry deploy
- After successful swap: button changes to "✅ Model v2.0 Active" (green), plot auto-refreshes
- `resetModelToV1()` called by "Reset Demo Data" button to return to demo start state

**Demo narrative:**  
*"This is Training-Serving Skew. Our cloud-trained model wasn't calibrated for the noise of this edge device. Watch — I'm going to trigger a retrain using the actual edge telemetry that's been accumulating in AlloyDB. Vertex AI is ingesting it to BigQuery... and now that new model is deployed to this edge node. Notice how the RUL line just snapped from chaotic to perfectly stable."*

---

### Task 4: Edge vs Cloud Chart Upgrade (`app.py` — `plot_forecast()`)
Replaced the shaded "Cloud Detection Window" rectangle with two stark vertical lines:

- **PNR Line:** Solid red (#f44336, width=3) — labeled `⛔ PNR T+Xm`
- **Cloud Alert Line:** Solid purple (#ce93d8, width=2.5) — labeled `☁ Cloud Alert T+20m`

Added horizontal "Time to React" arrows using Plotly `axref/ayref="x"/"paper"`:
- **Edge Arrow:** fault_onset → PNR (green, y=0.88 paper) — `⚡ Edge: Xm to act`
- **Cloud Arrow:** cloud_detect_time → PNR (purple, y=0.80 paper) — `☁ Cloud: Ym to act`
- If `cloud_window_min = 0`: shows `☁ NO WINDOW — Alert after PNR` label

Summary callout box moved from y=0.98 to y=0.72 to avoid collision with arrows.

---

### Task 5: PNR Exceeded / Asset Failed States (`app.py` — `plot_forecast()`)
Three-state detection computed once per chart request and shared across overlays:

**State A (Active Fault, PNR not reached):** Existing behavior, no change.

**State B (PNR Exceeded):**
- Detection: `(datetime.utcnow() - fault_onset).total_seconds()/60 > PNR_MINUTES[fault_type]`
- Chart title: `⚠ INTERVENTION WINDOW CLOSED — {FAULT_TYPE}`
- Chart annotation: `⛔ PNR PASSED — Damage Irreversible` at the PNR time position

**State C (Asset Failed — sensors past critical threshold):**
- Detection: any of last 5 readings crossing `crit_psi/crit_temp/crit_vib`
- Plot background: `rgba(50,10,10,0.8)` red tint
- Chart title: `🔴 ASSET FAILURE — {asset_id} Offline`
- Flat red line at `y_crit` extending to future
- Center annotation: `🔴 ASSET OFFLINE`

Incident panel already had `💥 FAILED` badge (Phase 2 feature). States B and C deepen the narrative for the "What if you missed it?" demo moment.

---

### Task 6: RUL-Tiered Resolution Actions (`app.py` + `index.html`)
**Backend:** `REMEDIATION_TIERED` dict — 11 fault types × 4 tiers (early/urgent/critical/post_pnr). All actions are physics-grounded O&G interventions.

**Tier logic:**
- `early`: RUL ≥ PNR × 1.5 → Software/SCADA command preferred
- `urgent`: PNR × 0.5 ≤ RUL < PNR × 1.5 → Field notification required
- `critical`: RUL < PNR × 0.5 → Emergency procedure only
- `post_pnr`: PNR exceeded → Recovery/workover dispatch

**`GET /api/resolution-actions/{fault_type}?rul_minutes=X&is_pnr_exceeded=Y`** returns:
- Active tier determination
- All 4 tiers with viability scores (VIABLE/MARGINAL/NOT VIABLE based on `time_to_execute` vs `rul_minutes`)
- `dim=true` for NOT VIABLE options (rendered at 0.38 opacity with warning)

**Dispatch modal:**
- Shows tiered summary bar (Active Tier + RUL + PNR)
- 4 radio options (all tiers visible, recommended highlighted)
- Viability badge per option
- "RECOVERY DISPATCH" header when `is_pnr_exceeded` or `is_failed`
- Reads `activeDegrades[asset].fault_onset_utc` for elapsed time computation

---

## Bug Fixes Applied This Session

### Fix 1: Historical Telemetry Tab (Grafana)
**Root cause:** UI was constructing Grafana URL as `${hostname}:3000`, but Grafana has its own LoadBalancer at `136.115.220.48:80`. The fallback was also hidden by default, so a blank iframe showed instead of the helper message.

**Fix:**
- Server injects `<meta name="grafana-url" content="http://136.115.220.48">` into HTML at request time via `GRAFANA_URL` env var (defaults to `http://136.115.220.48`)
- Grafana fallback div changed from `display:none` to `display:flex` by default
- `switchMainTab('telemetry')` always shows the fallback first, then `onload` hides it when Grafana responds

### Fix 2: Fleet Financials Empty Ledger
**Root cause:** `renderLedger()` was filtering from `recentEvents` (limit=40 newest rows). With an active cluster generating 12 telemetry readings/minute, acknowledged events from past sessions were outside the 40-row window.

**Fix:**
- Added `GET /api/ledger` backend endpoint — queries acknowledged events directly (up to 200), ordered by `ack_time DESC`, independent of the telemetry event stream
- Added separate `ledgerEvents` JS state variable
- Added `refreshLedger()` function called on tab switch, polling loop, and after every acknowledge/clear action
- `renderLedger()` now uses `ledgerEvents` and filters for `cost_avoided > 0` (hidden after reset)

### Fix 3: Fleet Financials Reset
**Fix:** Added "♻ Reset Demo Data" button in the Fleet Financials tab header:
- Calls `/api/clear-dispatch` (sets all `cost_avoided=0, cost_incurred=0`)
- Resets MLOps model back to V1 via `resetModelToV1()` (clean demo restart)
- Refreshes ledger (now shows empty because `cost_avoided=0` entries are filtered)
- Confirmed with `confirm()` dialog to prevent accidental reset

---

## Current Cluster State (Phase 3 Complete)

```
Cluster:     gdc-edge-simulation (GKE Autopilot, us-central1)
Project:     gdc-pm-v2
Namespace:   gdc-pm
UI URL:      http://35.188.3.97
Grafana:     http://136.115.220.48

RUNNING (all healthy):
  alloydb-omni           1/1 Running
  event-processor        1/1 Running
  fault-trigger-ui       1/1 Running  (Phase 3 — all tasks deployed)
  gdc-pm-rabbitmq        1/1 Running
  grafana                1/1 Running  (LoadBalancer: 136.115.220.48:80)
  inference-api          1/1 Running
  ollama                 1/1 Running  (Gemma 2B)
  telemetry-simulator    1/1 Running

RUL MODE:      XGBoost V1 (drifted) — fault-only feature extraction
MODELS LIVE:   V1 (all 4 classes) + V2 (all 4 classes, 5s noise calibrated)
MODEL ACTIVE:  V1 (default — supports MLOps retrain demo)
```

---

## Files Changed in Phase 3

```
MODIFIED:
  gke/fault-trigger-ui/app.py         # All 7 tasks + /api/ledger + Grafana meta injection
  gke/fault-trigger-ui/index.html     # Tasks 3, 4, 5, 6 + ledger + Grafana + reset

CREATED:
  gke/fault-trigger-ui/models/esp_rul_v2.ubj         # V2 model (1413 KB, RMSE 0.204m)
  gke/fault-trigger-ui/models/gas_lift_rul_v2.ubj    # V2 model (1424 KB, RMSE 0.227m)
  gke/fault-trigger-ui/models/mud_pump_rul_v2.ubj    # V2 model (1406 KB, RMSE 0.166m)
  gke/fault-trigger-ui/models/top_drive_rul_v2.ubj   # V2 model (1430 KB, RMSE 0.176m)
  scripts/retrain_edge_models.py                      # Task 2: V2 training script
  docs/PHASE_3_PLAN.md                                # Planning doc (written prior session)
  docs/PHASE_3_DEPLOYMENT_STATUS.md                  # This file

UNCHANGED (Phase 2, already deployed):
  gke/event-processor/processor.py                   # RAG pipeline (Phase 2)
  gke/inference-api/app.py                            # Inference API (Phase 2)
  gke/alloydb-omni/k8s/init-schema.yaml              # DB schema (Phase 2)
```

---

## Key Engineering Decisions

1. **V1 instability is preserved (intentional):** The fault-only filter fixes the "arc" artifact but not V1's variance vs. 5-second noise. This is the demo's opening act for the MLOps narrative.

2. **V2 models embedded in container, not streamed from GCS at runtime.** The `inference-api` supports GCS streaming (Phase 2), but `fault-trigger-ui` loads from `/app/models/` at startup. V2 files (`*_rul_v2.ubj`) are embedded alongside V1 (`*_rul.ubj`) and selected at runtime via `_active_model_version`.

3. **Grafana URL hardcoded to LB IP.** The `GRAFANA_URL` env var can override it if the LB IP changes. In GDC Software-Only deployments, set `GRAFANA_URL` to the appropriate internal service URL.

4. **Ledger decoupled from event log.** `/api/recent-events` (limit=40) is optimized for the live event feed; `/api/ledger` (limit=200, acknowledged only) is optimized for the financials table. These will diverge further as telemetry volume grows.

5. **No run-to-failure real data required.** All V2 training data is synthetically generated to match the exact noise profile of `_run_degrade_thread`. Industry-standard practice for O&G demo software.

---

## Demo Script (Phase 3 Complete)

1. **Start:** All assets normal. Explain fleet overview (4 sites, 20 assets, live telemetry from AlloyDB).
2. **Inject:** ESP-ALPHA-1 → Gas Lock → Gradual. RUL appears — noisy but counting down from ~45m.
3. **"This is training-serving skew..."** Click "☁ Sync & Retrain via Vertex AI". Watch the 3-step pipeline toast sequence. RUL snaps to stable line.
4. **Cloud Comparison:** Toggle "☁ Cloud-Based Prediction". Two vertical lines appear. Show 25m Edge window vs "NO WINDOW" for Cloud (gas_lock PNR=25m < cloud_detect=20m → 5m window).
5. **Dispatch Modal:** Click "Diagnose ▶". Show tiered actions: Early=VIABLE ($2,500 SCADA command) vs Post-PNR=$150,000 workover. Select Early. Acknowledge.
6. **Fleet Financials:** Show $150,000 saved for $2,500 cost.
7. **Optional — "What if you missed it?"** Reset, inject again, wait >25 minutes. Chart title changes to `⚠ INTERVENTION WINDOW CLOSED`. Then sensors cross threshold → `🔴 ASSET FAILURE — Offline`. Show modal in Recovery Dispatch mode ($150,000 workover).

---

## Known Limitations / Watch Points

1. **V1 RUL variance:** The exponential smoothing (window=10, α=0.75) damps single-reading spikes but V1 predictions still show ±15-30m variance on 5-second noise. This is expected and supports the demo. After retrain to V2, variance drops to ±2-3m.

2. **Plotly `axref/ayref` arrows:** Task 4 arrows use `axref="x", ayref="paper"` for data-coordinate arrow tails. If the fault onset is outside the visible x-range (e.g., burst injections from >10 min ago), the arrow may not render. This is a known Plotly limitation.

3. **PNR state detection polling:** State B/C are computed on every `/api/plot/forecast` call (every 10s polling cycle). There is a <10s detection lag between PNR being crossed and the chart title changing. Acceptable for demo.

4. **Model hot-swap clears smoothing buffers:** `POST /api/model/version` calls `RUL_HISTORY.clear()` — all assets need 2-3 refreshes (20-30s) after the swap before the V2 prediction stabilizes. The plot auto-refreshes at 1.2s after swap, so the first post-swap RUL may show only 1-2 readings in the buffer.

5. **`fin-uptime` metric:** Still hardcoded to `100.0%`. Not wired to real data.

---

## Phase 4 Vision

The Ollama/Gemma integration in the dispatch modal is the seed for Phase 4 closed-loop control:
- **AI Agent:** Gemma queries parts inventory, evaluates intervention options, and (with sufficient confidence) issues SCADA commands autonomously
- **Autonomous Dispatch:** Agent proposes action, operator approves with single click ("Execute VFD reduction — confirm?")
- **Multi-asset correlation:** Agent identifies patterns across fleet (e.g., thermal runaway on 3 gas lift compressors → shared cooling system fault)
- **Proactive PNR alerts:** Agent sends proactive notification at T+10m (halfway to PNR) if no operator acknowledgement detected
