# GDC-PM Phase 3 — Implementation Plan
**Status:** Plan Complete — Ready for Implementation  
**Date:** 2026-05-08  
**Preceded by:** `PHASE_2_DEPLOYMENT_STATUS.md` (all Phase 2 changes built, deployed, and live at http://35.188.3.97)

---

## Context: What Phase 2 Delivered (Current Live State)

All Phase 2 code changes are deployed and running on the GKE cluster (`gdc-edge-simulation`, `gdc-pm` namespace):

- **3-Tab UI:** Operations | Fleet Financials | Historical Telemetry (with Grafana fallback)
- **Tab UI improvements:** Physical tab styling, visible active/inactive states
- **Fleet Savings removed from header** — now lives in Fleet Financials tab only
- **Resizable live detection feed:** Draggable splitter between event log and fault injection panel
- **Event lifecycle:** No duration input — gradual faults hold until operator resolves
- **Resolve as Intermittent:** Yellow button in dispatch modal; auto-cancels fault injection
- **Auto-cancel on acknowledge:** Resolving any incident stops the fault simulation cleanly
- **Failed state detection:** `is_failed` flag on events where sensors crossed critical thresholds; 💥 badge in incidents panel
- **Edge vs Cloud Visualization:** PNR line + Cloud Detection zone + summary callout box (see Phase 3 upgrades below)
- **Geometric RUL (TEMPORARY):** Current live code uses pure physics projection (gap ÷ slope) instead of XGBoost. This must be replaced in Phase 3. See rationale below.

---

## Phase 3 Problem Statement

### RUL Instability Root Cause (Training-Serving Skew)
The original XGBoost RUL models were trained on perfectly clean, 5-minute interval synthetic data. The edge runs 5-second noisy telemetry. This is a classic **Training-Serving Skew** problem.

When a fault is injected, the 10-minute query window contains a mix of pre-fault normal readings and post-fault fault readings. The slope computed over this mixed window is distorted: it starts artificially shallow (too many normal readings → slope near zero → RUL inflated to 3.5H), then dramatically steepens as the window fills with fault readings (RUL crashes to 41m). This created the "arc" effect the user observed.

The temporary fix (geometric projection from fault-only readings) is stable but **removes the ML model from the RUL calculation**, which undermines the entire GDC/Vertex AI value proposition.

### The Correct Fix: Retrain on Realistic Edge Data
The XGBoost model must be restored, but fed **clean features computed from fault-only readings**. Additionally, better training data must be generated that accurately reproduces the 5-second noise profile of our edge simulator.

---

## Phase 3 Implementation Scope

### Task 1: Restore XGBoost RUL + Clean Feature Extraction
**File:** `gke/fault-trigger-ui/app.py`  
**What:** Revert RUL computation from geometric back to `rul_model.predict()`, but fix the feature extraction to use **fault-labeled readings only** before computing slope.

**Implementation:**
1. Filter `rows` to only include entries where `failure_type != 'normal'`
2. If ≥ 6 fault readings: compute linear regression slope over those readings only
3. If < 6 fault readings (early in injection): use full window as fallback
4. Feed `last_psi`, `last_temp`, `last_vib`, `dpsi`, `dtemp`, `dvib` computed from fault-only data into `rul_model.predict()`
5. Keep the 10-reading exponential-weighted smoothing buffer on the XGBoost output

**Why this works:** By filtering to fault readings only, the slope estimation is no longer polluted by the pre-fault flat portion of the window. The model sees a clean, consistent degradation signal from the first moment the fault is detected.

---

### Task 2: Retrain Models on Realistic Edge Data (V1 → V2)
**New file:** `scripts/retrain_edge_models.py`  
**What:** Generate new training data that accurately reproduces the statistical properties of our 5-second edge telemetry, retrain the XGBoost RUL regressors, and push the new `.ubj` artifacts to GCS.

**Training Data Generation (for all 4 asset classes):**
- Each sample: 720 steps × 5-second intervals = 60 minutes of degradation
- **Noise profile:** Gaussian noise at ±0.2% of current value (matching the `_run_degrade_thread` noise parameters: `psi * 0.002`, `temp * 0.001`, `vib * 0.005`)
- **Start state:** Normal range midpoint (matching `NORMAL_RANGES` in app.py)
- **End state:** Target fault range endpoint (matching `FAULT_PROFILES` psi_range/temp_range/vib_range)
- **RUL label:** Decrements from 720 down to 0 at each step
- **Features per sample:** `psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt`
- **Slope feature calculation:** Linear regression over a 60-reading (5-minute) window at each point in the sequence, converted to PSI/min to match the training scale

**Deployment:**
- Upload `.ubj` files to `gs://gdc-pm-v2-models/{asset_class}_rul/latest/model.bst`
- The existing `inference-api` pulls from GCS automatically on startup
- **Alternatively:** Embed in the `fault-trigger-ui` container as local model files

---

### Task 3: MLOps "Drift & Retrain" Demo Flow
**Files:** `gke/fault-trigger-ui/index.html`, `gke/fault-trigger-ui/app.py`  
**What:** Interactive demo showing the full GDC→BigQuery→Vertex AI→Edge retraining loop.

**Backend:**
- `app.py` maintains two model registries: `RUL_MODELS_V1` (original noisy models) and `RUL_MODELS_V2` (retrained edge-calibrated models)
- New endpoint: `POST /api/model/version` — switches active model between v1 and v2
- New endpoint: `GET /api/model/version` — returns current active version
- On startup: defaults to V1

**Frontend (`index.html`):**
- When an active fault is detected (incident panel visible), show a new button in the plot header area:  
  `"☁ Sync Data & Retrain via Vertex AI"`
- Button click triggers a simulated pipeline sequence via toast notifications:
  1. *"Exporting AlloyDB edge telemetry → BigQuery..."* (1.5s delay)
  2. *"Vertex AI training XGBoost v2.0 on high-fidelity 5s data..."* (2.5s delay)
  3. *"Model v2.0 validated — deploying to GDC Edge Registry..."* (1.5s delay)
  4. *"✅ Model v2.0 active — RUL predictions improved"* (calls `/api/model/version` to swap)
- After the swap, the next plot refresh will use V2 model and the RUL should visibly stabilize

**Demo Narrative:**  
*"This is Training-Serving Skew. Our cloud-trained model wasn't calibrated for the noise of this edge device. Watch — I'm going to trigger a retrain using the actual edge telemetry that's been accumulating in AlloyDB. Vertex AI is ingesting it to BigQuery, training a new model... and now that new model is deployed to this edge node. Notice how the RUL line just snapped from chaotic to perfectly stable."*

---

### Task 4: Upgrade Edge vs Cloud Chart Visualization
**File:** `gke/fault-trigger-ui/app.py` (`plot_forecast()`)  
**What:** Replace the shaded Cloud Detection box with stark vertical lines for both PNR and Cloud Detection, and add horizontal "Time to React" span arrows.

**Changes:**
1. **PNR Line:** Keep as a solid red vertical line (already exists, may need thickness increase)
2. **Cloud Detection Line:** Replace the shaded purple rectangle with a **solid purple vertical line** at `fault_onset + 20m`, labeled *"☁ Cloud Alert: T+20m"*. Remove the shaded box entirely.
3. **Time to React — Edge Arrow:** Horizontal green arrow from `fault_onset` (T+0) to `pnr_time`. Label: *"Edge Reaction Window: Xm"*. Use `go.layout.Shape` with `type="line"` or an annotation with arrows (`ax`/`ay`).
4. **Time to React — Cloud Arrow:** Horizontal purple arrow from `cloud_detect_time` to `pnr_time`. Label: *"Cloud Reaction Window: Ym"* (or *"NO WINDOW — Alert Arrives After PNR"* if `cloud_detect_time > pnr_time`). 
5. Both arrows should span at a fixed `y_paper` height (e.g., y=0.92 and y=0.85) to avoid overlapping the telemetry data.

---

### Task 5: Implement "Past PNR / Asset Lost" Failure State
**Files:** `gke/fault-trigger-ui/app.py`, `gke/fault-trigger-ui/index.html`

**Three State Model:**

**State A: Active Fault, PNR Not Yet Reached**  
*(Current behavior — no change)*
- Chart: Orange dotted RUL projection, "Failure in Xm" annotation
- Incident: ⚠ or 🔴 badge, "Diagnose ▶" button
- Callout: "Edge SAVED — Xm response window"

**State B: PNR Passed — Sensor Still Degrading**  
Detection: `time.utcnow() > fault_onset + PNR_MINUTES[fault_type]` (computed server-side)
- Chart: 
  - Add annotation at PNR line: *"⛔ PNR PASSED — Damage Irreversible"* in bold red
  - Title changes to: *"⚠ INTERVENTION WINDOW CLOSED — {fault_type.upper()}"*
- Incident panel: Badge changes to `💥 PNR EXCEEDED`
- Callout: "Edge: ✅ Window was Xm — MISSED" in dim orange
- Dispatch modal: `cost_avoided = 0`, cost shown as full failure cost under "Projected Loss"

**State C: Sensor Crossed Failure Threshold**  
Detection: `is_failed = True` (already computed in `/api/recent-events`)
- Chart:
  - Background hint red tint via `plot_bgcolor="rgba(50,10,10,0.8)"`
  - Title: *"🔴 ASSET FAILURE — {asset_id} Offline"*
  - Forecast cone removed; a flat red line at `y_crit` extends to the right
- Incident panel: `💥 FAILED — UNADDRESSED` in deep red, full failure cost displayed
- Dispatch modal: Resolution options change to "Recovery Dispatch" tier (see Task 6)

**Backend change:** Expose `fault_onset_time` and `is_pnr_exceeded` in the plot endpoint so the frontend can reflect these states correctly.

---

### Task 6: RUL-Tiered Resolution Actions
**File:** `gke/fault-trigger-ui/app.py`  
**What:** Replace the single flat `REMEDIATION` dictionary with a three-tier structure (`early`, `urgent`, `critical`) per fault type. The dispatch modal shows only the contextually appropriate tier based on current RUL.

**Tier Logic:**
- `early`: RUL ≥ PNR_MINUTES × 1.5 → Low urgency, planned approach
- `urgent`: RUL between PNR_MINUTES × 0.5 and PNR_MINUTES × 1.5 → Must act now, software commands preferred
- `critical`: RUL < PNR_MINUTES × 0.5 → Emergency only
- `post_pnr`: PNR exceeded → Recovery/damage assessment

**Example — Gas Lock (ESP), PNR = 25m:**
```
early (>37m remaining):
  action: "Reduce VFD frequency 10-15% via SCADA — software command from control room"
  type: software_command
  time_to_execute: "<5 minutes"
  cost_incurred: $2,500

urgent (12-37m remaining):
  action: "Immediate VFD cutback to 60% + notify on-call field engineer"
  type: field_notification  
  time_to_execute: "15-20 minutes"
  cost_incurred: $8,000

critical (<12m remaining):
  action: "Emergency VFD shutdown + staged pump restart protocol"
  type: emergency_procedure
  time_to_execute: "<5 minutes"
  cost_incurred: $15,000

post_pnr (PNR exceeded):
  action: "Pull and replace ESP string — order workover rig"
  type: workover
  time_to_execute: "3-5 days"
  cost_incurred: $150,000  (full failure cost)
```

**Modal UI changes:**
- Each resolution option shows a colored badge: 🟢 VIABLE | 🟡 MARGINAL | 🔴 NOT VIABLE
- Viability based on `time_to_execute` vs current `rul_minutes`
- "Not Viable" options are shown with `opacity: 0.4` and a tooltip explaining why
- For `post_pnr` tier, modal header changes to *"RECOVERY DISPATCH — Asset Already Failed"*

---

### Task 7: Consistent Fault Onset Time Tracking
**File:** `gke/fault-trigger-ui/app.py`  
**What:** The server needs to know when a fault truly began to calculate PNR elapsed time correctly.

**Implementation:**
- In `_run_degrade_thread`, record `fault_onset_utc` in the `active_degrades` dict when the ramp starts
- For burst injections, record onset when the first fault reading is published
- Expose this via `/api/degrade-status` so the plot endpoint can compute `is_pnr_exceeded` accurately
- This also feeds the Cloud Detection vertical line placement (`fault_onset + 20m`)

---

## Demo Script (Phase 3 Complete)

1. **Start:** All assets normal. Explain fleet overview, site structure.
2. **Inject fault:** Select ESP-ALPHA-1, Gas Lock, Gradual. The RUL appears — stable, counting down from ~60m.
3. **Toggle Cloud Comparison:** Two vertical lines appear. Show the Edge reaction window (25m green arrow) vs Cloud reaction window (5m purple arrow).
4. **Explain PNR:** "Gas Lock has a 25-minute PNR. The pump impeller stalls when gas fraction exceeds 70%. After that, only a workover rig can fix it. With Edge AI you have 25 minutes for a SCADA command. Cloud AI gives you 5 minutes — not enough time."
5. **Wait for dispatch modal:** RUL at ~40m. Open modal. Show "Reduce VFD frequency via SCADA" as the VIABLE option. Point out the cost: $2,500 vs $150,000.
6. **Trigger Retrain:** Click "Sync to BigQuery & Retrain". Show the toast sequence. Point out V2 model snaps the RUL to a perfectly stable line.
7. **Acknowledge & Dispatch:** Select VFD reduction option. Close incident. Show Fleet Financials — $150,000 saved for $2,500 cost.
8. **Optional — "What if you missed it?"** Reset, inject again, let it run past PNR. Show the UI flip to "⛔ PNR PASSED" and then "🔴 ASSET FAILURE". Show how the resolution cost jumped from $2,500 to $150,000. This is the whole point of the demo.

---

## Current Live Cluster State at Phase 3 Start

```
Cluster:     gdc-edge-simulation (GKE Autopilot, us-central1)
Project:     gdc-pm-v2
Namespace:   gdc-pm
UI URL:      http://35.188.3.97

RUNNING (all healthy):
  alloydb-omni       1/1 Running  7d
  event-processor    1/1 Running  ~2h  (Phase 2 image)
  fault-trigger-ui   1/1 Running  ~2h  (Phase 3 TEMP image — geometric RUL, must be replaced)
  gdc-pm-rabbitmq    1/1 Running
  grafana            1/1 Running
  inference-api      1/1 Running  (Phase 2 image)
  ollama             1/1 Running  (Gemma 2B)
  telemetry-simulator 1/1 Running

CURRENT RUL MODE: Geometric projection (TEMPORARY — must restore XGBoost + clean features)
MODELS LIVE:      V1 (noisy — trained on 5-min clean synthetic data)
MODELS NEEDED:    V2 (calibrated — trained on 5-second noise-profile synthetic data)
```

---

## Files to Create/Modify in Phase 3

```
MODIFY:
  gke/fault-trigger-ui/app.py         # Tasks 1, 3, 4, 5, 6, 7
  gke/fault-trigger-ui/index.html     # Tasks 3, 6

CREATE:
  scripts/retrain_edge_models.py       # Task 2: Generate V2 training data + train models
  docs/PHASE_3_PLAN.md                 # This file

POSSIBLY MODIFY:
  gke/inference-api/app.py            # Only if model swap requires inference-api involvement
```

---

## Key Engineering Decisions Made This Session

1. **No Pure Geometry for RUL:** The geometric approach is accurate and stable, but it removes the ML element from the demo. XGBoost must be restored. The fix is clean feature extraction, not model replacement.

2. **Training-Serving Skew is the Story:** We are intentionally keeping a "V1 drifting model" as the demo starting state so we can demonstrate the retraining loop live. This is the most compelling MLOps narrative for GCP/GDC customers.

3. **No Run-to-Failure on Real Data:** We do not have (and don't need) the Volve ESP dataset or similar. Physically-informed synthetic data is industry standard for enterprise O&G demo software. The key is matching the noise profile of the actual edge simulator.

4. **Resolution Actions Must Be Physics-Grounded:** The dispatch modal must show contextually appropriate interventions. "Send a truck" is never valid when RUL < 2 hours. Software SCADA commands (VFD frequency reduction) are the correct early-intervention option for most ESP faults.

5. **PNR Exceeded = Full Demo Impact:** The "ASSET FAILED" state should be demonstrable on demand (inject fault, ignore it, watch the UI show the consequences). This is the key emotional moment of the demo.

6. **Phase 4 Vision (AI Agent):** The Ollama/Gemma integration in the dispatch modal is the seed for Phase 4 closed-loop control — where the agent queries parts inventory, evaluates intervention options, and (with sufficient confidence) issues SCADA commands autonomously.
