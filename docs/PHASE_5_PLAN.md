# GDC-PM Phase 5 — Core Physics Engine & UI Structural Rebuild

**Status:** ✅ COMPLETE — 2026-05-13  
**Preceded by:** `PHASE_4_2_DEPLOYMENT_STATUS.md`  
**Followed by:** `PHASE_6_PLAN.md` (chart physics fixes, time slider, agent UX)  
**Decision context:** This plan was developed through an in-depth architectural review session that identified three critical structural failures in how the demo conveys its value proposition. Everything documented here must be implemented as a coherent, end-to-end rebuild — incremental patches will not fix the fundamental alignment problem.

---

## Why This Rebuild Is Necessary

### Problem 1: The Timeline Is Backwards
The current ML Forecast chart shows the following sequence:

```
ML Detection → PNR → SCADA Alarm ≈ Failure
```

This is **physically wrong**. The correct sequence must be:

```
ML Detection → SCADA Alarm → PNR → Failure
```

A SCADA alarm is an operational setpoint, not a failure event. By drawing the PNR *before* the SCADA alarm, the current chart implies that SCADA only warns you after irreversible damage — making SCADA look completely incompetent rather than merely reactive. The demo must make SCADA look *good but too late*, not useless.

**Root cause:** The XGBoost models were trained with `RUL = 0` at the exact moment the sensor crosses the SCADA threshold. RUL=0 should represent actual physical destruction of the asset, which occurs *after* the SCADA alarm fires.

### Problem 2: All Faults Run on a 60-Minute Clock
All fault injections currently degrade the asset in 60 minutes. Sand Ingress on an ESP in reality takes 14 days. Connecting a 14-day supply chain resolution ("ordering a $145,000 pump that takes 12 days to arrive") to a 60-minute failure window makes the agentic value proposition physically impossible and narratively absurd.

**Root cause:** `STEPS = 720` is hardcoded in `retrain_edge_models.py`, treating all fault types identically.

### Problem 3: The User Cannot Explore "What If I Acted Earlier?"
The Dispatch Modal pops up and the user has ~30 seconds of real time to react before the chart ticks forward. There is no way to explore: "What happens if I intervene on Day 2 vs. Day 12?" The LLM response is also static (reading from a script, not reacting to context).

---

## The Core Architectural Decisions

### Decision 1: Health Score Replaces RUL Minutes
The XGBoost models will be retrained to predict a **`Health_Score`** (1.0 = Perfect, 0.0 = Destroyed) rather than `RUL_Minutes`. 

- The model remains agnostic to physical time.
- It learns to score the *state of equipment health* from the multivariate sensor signatures.
- The UI layer maps Health Score to physical time via the `FAULT_PHYSICS` configuration.
- This enables one model architecture to correctly serve both a 45-minute Gas Lock and a 14-day Sand Ingress fault.

### Decision 2: Per-Fault Time Horizons via `FAULT_PHYSICS` Config
We introduce a `FAULT_PHYSICS` configuration block in `app.py` that defines the physical reality for each fault mode:

```python
FAULT_PHYSICS = {
    # Long Horizon (Days) — Supply Chain / Workover
    "sand_ingress": {
        "horizon_label": "Days",
        "total_hours": 336,          # 14 days
        "scada_alarm_health": 0.15,  # Fires at 85% degraded (Day 11.9)
        "pnr_health": 0.05,          # Irreversible at 95% degraded (Day 13.3)
        "intervention_type": "supply_chain",
    },
    "piston_seal_wear": {
        "horizon_label": "Days",
        "total_hours": 96,           # 4 days
        "scada_alarm_health": 0.20,
        "pnr_health": 0.08,
        "intervention_type": "maintenance_scheduling",
    },
    "gearbox_bearing_spalling": {
        "horizon_label": "Hours",
        "total_hours": 10,
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "intervention_type": "maintenance_scheduling",
    },
    # Medium Horizon (Hours) — Crew Dispatch
    "motor_overheat": {
        "horizon_label": "Hours",
        "total_hours": 4,
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "intervention_type": "operational_control",
    },
    "thermal_runaway": {
        "horizon_label": "Hours",
        "total_hours": 72,
        "scada_alarm_health": 0.20,
        "pnr_health": 0.07,
        "intervention_type": "maintenance_scheduling",
    },
    "valve_washout": {
        "horizon_label": "Hours",
        "total_hours": 10,
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "intervention_type": "maintenance_scheduling",
    },
    "hydraulic_leak": {
        "horizon_label": "Hours",
        "total_hours": 6,
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "intervention_type": "operational_control",
    },
    # Short Horizon (Minutes) — Automated/SCADA Control
    "gas_lock": {
        "horizon_label": "Minutes",
        "total_hours": 0.75,         # 45 min
        "scada_alarm_health": 0.30,
        "pnr_health": 0.12,
        "intervention_type": "operational_control",
    },
    "bearing_wear": {
        "horizon_label": "Hours",
        "total_hours": 16,
        "scada_alarm_health": 0.20,
        "pnr_health": 0.08,
        "intervention_type": "maintenance_scheduling",
    },
    "pulsation_dampener_failure": {
        "horizon_label": "Minutes",
        "total_hours": 0.083,        # 5 min — catastrophic / emergency
        "scada_alarm_health": 0.50,
        "pnr_health": 0.25,
        "intervention_type": "emergency_shutdown",
    },
    "valve_failure": {
        "horizon_label": "Minutes",
        "total_hours": 0.25,         # 15 min
        "scada_alarm_health": 0.40,
        "pnr_health": 0.15,
        "intervention_type": "operational_control",
    },
}
```

### Decision 3: Exponential Failure Curves (Not Linear)
The sequence generator in `retrain_edge_models.py` currently uses `np.linspace` to linearly degrade sensors. Real equipment failure is exponential: starts slow, accelerates rapidly near end-of-life. We will replace the linear ramp with an exponential decay curve:
```python
# Instead of: t_frac = np.linspace(0, 1, STEPS)
# Use:         t_frac = (np.exp(k * t) - 1) / (np.exp(k) - 1)  where k ≈ 3-4
```
This makes early-stage degradation subtle (harder for SCADA, but the ML model catches it) and late-stage degradation rapid (urgent PNR + Failure sequence).

### Decision 4: Remove MLOps V1/V2 Drift Narrative
The "V1 cloud-drifted vs. V2 edge-calibrated model" comparison is removed. It distracts from the core value proposition and introduces doubt about whether the AI model being shown is the "good" or "bad" one. We will have a single, high-quality edge-calibrated model per asset class. The "Retrain via Vertex AI" button is deleted.

### Decision 5: Flatten the Site Hierarchy (Optional/Phase 5.5)
The three-site hierarchy (Pad Alpha, Pad Bravo, Rig 42) can remain in the backend but the main UX story will be driven by fault injection on individual assets. Removing it entirely is a UI preference for future polish, not a blocker for Phase 5.

---

## The New UI Architecture (Frontend Rebuild)

### Delete
- The Dispatch Queue popup modal (`#dispatch-modal` and all JS).
- The Retrain via Vertex AI button and all V1/V2 toggle logic.

### New: The Copilot Workspace (Bottom Panel)
Replace the modal with a persistent bottom workspace split into two halves:

**Left: Dynamic Physics & Economics Calculator**  
Updates in real-time as the Intervention Slider is dragged. Shows:
- Time to Failure (in the correct unit: Days / Hours / Minutes)
- Intervention Tier badge (🟢 EARLY / 🟡 URGENT / 🔴 CRITICAL / 🛠 RECOVERY)
- Required Action category
- Estimated Cost Incurred
- Production Value at Risk
- Cost Avoided

**Right: GDC Agentic Chat Interface**  
A conversational chat window (NOT a static block of text). When the user places the Intervention Slider and clicks "Consult Agent":
1. The agent is initialized with the fault context (fault type, Health Score, time remaining from slider position).
2. The LLM asks a specific question relevant to the intervention type (e.g., "Should I generate a parts order?" for Supply Chain, "Should I reduce VFD frequency now?" for Operational Control).
3. The user responds (type or click quick-reply buttons).
4. The conversation continues until the user executes an intervention or acknowledges the recommendation.
5. The Financial Ledger is updated based on the slider position at acknowledgement.

### New: The Intervention Slider
An HTML range slider displayed directly below the Plotly chart. 
- Left end = `t=0` (the moment ML detection begins).
- Right end = `t=Failure` (Health Score = 0.0).
- As the user drags, three vertical lines update on the chart: `SCADA Alarm` (red), `PNR` (orange), and `Current Intervention Point` (white/green).
- The Copilot Workspace (left side) updates instantly based on slider position.

### New: The Forecast Chart Timeline (Correct Sequence)
The Plotly chart `x-axis` will now show the *physical* time unit (Days, Hours, or Minutes) based on `FAULT_PHYSICS[fault_type].horizon_label`. The order of elements on the chart from left to right:
1. **Blue solid line:** Live telemetry (past — nominal).
2. **Gray dashed vertical:** Present moment / detection.
3. **Orange dotted line + confidence band:** ML Health Score projection.
4. **Red dashed horizontal:** SCADA Alarm threshold level.
5. **Red vertical line:** Time when projection crosses SCADA threshold.
6. **Orange vertical line:** PNR — irreversible damage point.
7. **Black `X`:** RUL = 0 / Failure point.

**Intervention Slider annotation:**  
A white/green vertical line showing *where on this timeline the user has chosen to respond*, with a dynamic text label: "Intervening at T+2 Days — EARLY" or "Intervening at T+13.5 Days — POST-PNR".

---

## Three Agentic Intervention Types

These must be implemented in the Agent backend (`app.py`) with distinct LLM prompts and conversation flows:

### Type 1: Supply Chain (Long Horizon — Days)
*Applicable faults: sand_ingress, piston_seal_wear, gearbox_bearing_spalling, bearing_wear*

LLM persona: Inventory & Logistics Coordinator.
- Queries SAP MM (simulated) for local stock.
- Checks lead time from specific suppliers.
- Proposes PO generation if Early, emergency expedite if Critical, recovery dispatch if Post-PNR.
- Outcome: "PO #XXXXX created. Delivery in 10 days."

### Type 2: Maintenance Scheduling (Medium Horizon — Hours)
*Applicable faults: thermal_runaway, valve_washout, hydraulic_leak, motor_overheat*

LLM persona: Maintenance Dispatch Coordinator.
- Queries IBM Maximo (simulated) for available crews in the vicinity.
- Checks if any crew is already scheduled nearby (zero-cost piggyback).
- Proposes adding to existing work order if Early, dedicated emergency truck roll if Critical.
- Outcome: "Task appended to Crew B's existing WO for tomorrow. Zero additional travel cost."

### Type 3: Operational Control (Short Horizon — Minutes/Immediate)
*Applicable faults: gas_lock, pulsation_dampener_failure, valve_failure*

LLM persona: Automation Engineer / Control System.
- Proposes specific SCADA parameter adjustments (VFD frequency reduction, valve position changes).
- For emergency faults (dampener rupture), forces emergency shutdown logic.
- Displays simulated SCADA command confirmation: "VFD setpoint reduced to 42 Hz. Intake pressure recovering."
- Outcome: "SCADA Command Executed. Monitoring for 10 minutes."

---

## Implementation Execution Steps

### Phase 5.1 — ML Foundation Rebuild (Run first, retrain models)
1. Modify `scripts/retrain_edge_models.py`:
   - Change target variable from `rul_min` → `health_score` (inverted, 1.0 to 0.0).
   - Replace `np.linspace` with exponential curve for degradation trajectory.
   - Ensure all fault profiles degrade correctly to health=0.0 at `STEPS=720`.
2. Retrain all models: `python scripts/retrain_edge_models.py --n-samples 300 --rounds 300`
3. Verify output `.ubj` files contain health scores not minutes.

### Phase 5.2 — Backend Application Logic (`app.py`)
1. Add `FAULT_PHYSICS` dictionary (as defined above).
2. Update `/api/plot/forecast/{asset_id}`:
   - Scale x-axis to physical time using `FAULT_PHYSICS[fault].total_hours`.
   - Draw SCADA alarm line at `scada_alarm_health` (mapped to physical time).
   - Draw PNR line at `pnr_health` (mapped to physical time, always *after* SCADA alarm).
   - Use `horizon_label` (Days/Hours/Minutes) for axis title.
3. Update `/api/agent/recommend`:
   - Accept `slider_health_score` parameter (0.0 to 1.0 from the UI slider).
   - Determine Intervention Tier from `slider_health_score` vs FAULT_PHYSICS thresholds.
   - Branch LLM prompt by `intervention_type` (supply_chain, maintenance_scheduling, operational_control, emergency_shutdown).
   - Support conversation continuity (multi-turn — accept `chat_history` parameter).
4. Update Financial Ledger:
   - Scale cost_avoided by Health Score at time of intervention (Early = 100%, Post-PNR = 20%).
5. Delete V1/V2 model switching logic, `_active_model_version`, and related endpoints.

### Phase 5.3 — Frontend Rebuild (`index.html`)
1. Delete `#dispatch-modal` and all related JS.
2. Delete `#btn-retrain` (Vertex AI Retrain button) and all related JS.
3. Delete `#incidents-panel` (Dispatch Queue).
4. Add `#copilot-workspace` bottom panel:
   - Left: Dynamic calculator section (Health, Tier, Cost, Time).
   - Right: Chat interface (`#agent-chat-log`, `#agent-input`, `#agent-send-btn`).
5. Add `#intervention-slider` below `#plot-iframe`.
6. Wire slider to:
   - Update chart annotation via iframe message OR re-fetch the plot with `?intervention_health={X}`.
   - Update the left-side calculator in real-time.
   - Pre-populate the agent context when the user starts the chat.

### Phase 5.4 — Docker Rebuild & Deploy
1. Rebuild `fault-trigger-ui` Docker image.
2. Push to `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`.
3. `kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm`.
4. Verify at `http://35.188.3.97`.

---

## Things to NOT Change in Phase 5
- The AlloyDB schema — no changes to `telemetry_events` columns needed.
- The event-processor pipeline — it will continue populating the DB normally.
- The Grafana dashboard — just fixed in Phase 4.2, leave it alone.
- The simulator — leave it running its existing 60-minute injection sequence; the UI's Health Score mapping will handle the timeline presentation.

---

## Next Session Prompt

```
Read docs/PHASE_5_PLAN.md before doing anything else.

This is a major structural rebuild of the GDC-PM demo's physics engine.
We are NOT patching the existing system — we are replacing the core of it.

Start with Phase 5.1: Modify scripts/retrain_edge_models.py to produce
health_score (1.0→0.0) instead of rul_min, with an exponential degradation
curve. Then retrain all models. Do not touch app.py or index.html yet —
verify the models first.

Key constraints:
1. The physical timeline on the chart MUST be: ML Detection → SCADA Alarm → PNR → Failure
2. Each fault mode has its own time horizon (gas_lock=45min, sand_ingress=14days)
3. No V1/V2 model switching — single high-quality model per asset class
4. No dispatch modal — the Copilot Workspace replaces it entirely
5. The LLM must respond conversationally based on where the slider is set
```
