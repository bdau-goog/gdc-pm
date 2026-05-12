# GDC-PM Phase 4 — Agentic Predictive Maintenance
**Status:** Deployed — commit `304bc60`  
**Date:** 2026-05-12  
**Preceded by:** `PHASE_3_1_DEPLOYMENT_STATUS.md`  
**UI:** http://35.188.3.97

## ⚠️ Known Gap — Phase 4.1 Required

Phase 4 added `motor_amps` (ESP) and `spm` (Mud Pump) to the UI data model (`SENSOR4_CONFIG` in `app.py`) and the demo narrative, but did **not** update the telemetry simulator, event processor, AlloyDB schema, or XGBoost models. The new sensors are defined in the frontend but not generated or predicted in the pipeline.

**See `PHASE_4_1_SENSOR_RETRAIN.md` for the full implementation plan to resolve this.**

Until Phase 4.1 is complete:
- The 4th sensor tab will appear in the UI but show no data
- The Agent recommendation narratives reference `motor_amps` and `spm` but these are not persisted in AlloyDB
- The XGBoost RUL models continue to use the 6-feature vector (psi, temp, vib + slopes)


---

## Executive Summary

Phase 4 shifts the GDC-PM demo from a "fault detection & dispatch" tool to a fully agentic predictive maintenance platform. The core narrative pivot is:

> **From "react to alarms faster" → "predict failures before they happen and get ahead of them."**

This document captures the strategic decisions made in the Phase 4 planning session, the industry validation of the selected demo scenarios, and the full implementation plan. **No code changes are to be made without explicit approval after this document is reviewed.**

---

## Narrative Pivot: Why We Are Changing the Story

### The Old Narrative (Phase 1–3): "Edge AI vs. Cloud Latency"
The previous demo compared GDC edge detection time against a simulated cloud analytics round-trip (20-minute VSAT latency). The argument was: "GDC detects gas lock NOW. Cloud would tell you in 20 minutes — when you only have 5 minutes before the PNR."

**Why we are retiring this narrative:**
1. **It is a partial strawman.** Modern SCADA systems with rate-of-change alarms, multi-parameter logic, and local PLCs can catch many acute failure events independently. An operator wouldn't rely on a cloud round-trip for emergency shutdowns.
2. **The "Why Edge" argument is understated.** The real justifications for edge computing are stronger and more accurate:
   - **Security / Air Gap:** Operational telemetry (production rates, wellbore parameters) is commercially sensitive. It never leaves the site by default.
   - **Data Gravity:** 50Hz vibration data from 14 assets generates gigabytes per day. Backhaul is expensive and unnecessary when the compute runs locally.
   - **Survivability:** The rig and pad continue to operate and optimize even when the WAN link is degraded or offline.
   - **Enterprise Connectivity (not Cloud Dependency):** The agent *can* reach back to enterprise systems (ERP, FSM, procurement) for context, but core detection and inference is fully local.
3. **The "Cloud vs Edge timing" UI elements feel contrived.** The purple cloud line and VSAT countdown are visually busy and raise more questions than they answer.

**Action:** Remove all "Cloud latency" UI elements, chart overlays, and backend logic.

### The New Narrative (Phase 4): "Predict. Get Ahead. Close the Loop."
GDC Edge AI sees failure patterns developing **weeks or days before any SCADA threshold is crossed**, because it uses multivariate ML — not single-sensor setpoints. This advance warning creates a fundamentally different operational posture:

- A 14-day early warning on an ESP lets you **order a replacement pump before the failure**, not wait weeks for a delivery after the failure.
- A 3-day early warning on a gas lift compressor lets you **append a flush to an existing crew route**, not dispatch an emergency truck roll.
- A 45-minute early warning on a mud pump lets you **bring the standby pump online gradually**, maintaining drilling operations instead of making an emergency stop.

**The one-sentence pitch:** *"GDC doesn't just alarm faster. It tells you weeks or days early, checks what you need to fix it, and tells you exactly what to do — while everything on your SCADA dashboard still looks green."*

---

## "Why Can't SCADA See This?" — The Honest Differentiation

For each scenario, the honest answer to "couldn't SCADA catch this?" is documented below. We do NOT use scenarios where simple threshold monitoring would work.

| Fault | What SCADA Sees | What GDC Sees | Why SCADA Fails |
|---|---|---|---|
| ESP Sand Ingress | Intake pressure NORMAL, vibration below alarm | Subtle sub-harmonic vibration + slowly degrading pump performance curve | SCADA has a vibration HH alarm. The signature GDC detects is in the frequency spectrum and the pump's hydraulic efficiency — not in gross vibration amplitude. |
| Gas Lift Thermal Runaway | Discharge temp below alarm limit, pressure NORMAL | Discharge temp trending upward relative to ambient temperature (delta-T analysis) | SCADA alarms on absolute temperature. GDC detects the *rate of change* of the temperature differential — which indicates fouling, not just a hot day. |
| Mud Pump Valve Washout | Standpipe pressure holding — driller bumped SPM to compensate | Declining volumetric efficiency (flow output per stroke) + high-frequency fluid-end vibration signature | SCADA measures standpipe pressure. Drillers routinely adjust SPM, masking the washout. GDC detects efficiency degradation independent of SPM. |

---

## Validated Demo Scenarios

### Scenario 1: Pad Alpha (ESP) — Supply Chain / Long-Lead Procurement

**Fault:** Sand Ingress on ESP-ALPHA-2 (gradual, 14-day RUL)

**Industry Validation:**
- Sand erosion of ESP impeller stages is a primary failure mode in formations with unconsolidated sand (e.g., Gulf Coast, Colombia, Permian). This is extensively documented in SPE literature (SPE-184399, SPE-196199).
- The earliest detectable signature is sub-harmonic vibration at 0.38–0.47× running frequency, caused by impeller stage vane erosion creating hydraulic imbalance. This precedes overall vibration amplitude alarms by days to weeks.
- A degrading pump's performance curve (head vs. flow rate) shifts downward as stages erode — detectable via the relationship between motor current, intake pressure, and flow rate.
- **Why SCADA misses it:** SCADA alarms are on absolute vibration (e.g., >8 mm/s HH alarm). The predictive signature is in the frequency spectrum and pump efficiency, not the overall amplitude. By the time the vibration HH alarm fires, the impeller is already severely damaged.
- **Supply chain reality:** ESP stages are sized to the well's Inflow Performance Relationship (IPR) and fluid properties. A standard pump from local stock may not fit the well. Sand-handler configurations (tungsten carbide radial bearings, hardened stages) often require custom orders from the manufacturer (Schlumberger/Centrilift, Baker Hughes ESP, Borets). Lead times from manufacturing facilities in Claremore, OK or Houston, TX run 10–21 days.

**Agentic Action:**
1. GDC XGBoost detects impeller erosion signature. RUL: ~14 days.
2. Gemma Agent queries ERP (SAP/Oracle): "Well A-1 ESP requires 400-series sand-handler, 100-stage, 2,000 BPD design."
3. ERP returns: "Local inventory: 0 matching units. Vendor (Baker Hughes): 12-day lead time. Air freight option: 7-day lead time (+$8,000)."
4. Agent recommendation: "Order now (standard shipping). Pump arrives day 12, failure predicted day 14. Two-day buffer. If air freight is available, recommend if well produces >300 BPD to offset $8,000 premium."

**Value Delivered:** Avoids 9+ days of deferred production waiting for a pump after an unplanned failure. Industry typically values ESP production at $5,000–$15,000 per day per well (varies widely by oil price and well rate).

---

### Scenario 2: Pad Bravo (Gas Lift) — Workforce Scheduling / Route Optimization

**Fault:** Thermal Runaway (Cooling Jacket Fouling) on GLIFT-BRAVO-1 (gradual, 72-hour RUL)

**Industry Validation:**
- Reciprocating gas lift compressors (Ariel, Gemini, Exterran) require active cooling — either an aerial fin-fan cooler or a water jacket heat exchanger. Both are prone to fouling.
- Aerial fin-fan coolers foul with cottonwood seeds (common in many US basins), insects, and debris. In Permian or Bakken operations, dust fouling is a major issue. A fouled cooler reduces heat rejection capacity by 15–40%.
- Water jacket / inter-stage coolers scale over time with produced water chemistry.
- **The multivariate signature GDC detects:** If compressor RPM and suction/discharge pressures are held constant but discharge temperature and jacket water outlet temperature are slowly diverging from ambient temperature (the delta-T is growing), this indicates decreasing cooling system efficiency — not just a hot ambient day.
- **Why SCADA misses it:** SCADA has a discharge temperature high alarm (e.g., 250°F HH). Operators see the temperature and think "it's summer, the compressor runs hot." GDC's delta-T trending (temperature relative to ambient) identifies the cause as a fouled cooler, not ambient conditions.
- **Workforce scheduling reality:** Unmanned gas lift pad compressors are typically visited on a service route (every 2–4 weeks for routine checks, or on-demand for alarms). An emergency truck roll to an unmanned pad typically costs $800–$2,500 in direct labor and travel, and more importantly, it pulls a mechanic off a planned work order, cascading disruption into the schedule.
- **FSM reality:** Field Service Management (FSM) systems like Maximo, SAP PM, or Salesforce Field Service track technician locations, certifications, and scheduled routes. If a crew is already dispatched to a pad for one task, appending additional work costs almost nothing.

**Agentic Action:**
1. GDC XGBoost detects delta-T divergence on GLIFT-BRAVO-1. RUL: ~72 hours.
2. Gemma Agent queries Field Service Management (Maximo API): "Upcoming dispatches to Pad Bravo."
3. FSM returns: "Crew B (2 mechanics) scheduled at Pad Bravo tomorrow at 14:00 for transmitter calibration on Well B-3. Est. duration: 2 hours."
4. Agent checks: "Aerial fin-fan flush requires 45 min, 1 mechanic, no special parts."
5. Agent recommendation: "Append aerial cooler flush to Crew B's existing Pad Bravo work order. Zero additional travel cost. Prevents emergency dispatch in 72 hours (est. $1,800 emergency callout + 4-hour compressor trip = 4 wells offline)."

**Value Delivered:** Elimination of unplanned truck rolls and prevention of compressor trips on unmanned pads. Each gas lift pad compressor outage affects all wells on that injection system simultaneously — production impact can be significant.

---

### Scenario 3: Rig 42 (Drilling) — Active Operational Control / NPT Prevention

**Fault:** Valve Seat Washout on MUD-RIG42-1 (acute, 45-minute window)

**Industry Validation:**
- Triplex mud pump fluid end failures are the leading cause of Non-Productive Time (NPT) in land and offshore drilling operations. Valve seat/insert failure is the most common failure mode (SPE-170638, SPE-199694).
- A polyurethane or rubber valve insert erodes over time due to abrasive drilling fluid (high sand content, barite, etc.). The erosion creates a small channel, then progressively washes out.
- **The multivariate signature GDC detects:** As a valve washes out, the pump loses *volumetric efficiency* — it takes more strokes (SPM) to move the same volume of fluid. The driller on a rig floor naturally compensates by increasing SPM or pump pressure, which masks the loss of efficiency on SCADA trend displays. GDC tracks the relationship between SPM, liner size, and actual flow rate to detect this divergence before it becomes gross.
- **Why SCADA misses it:** The driller continuously adjusts the pump to maintain the required flow rate. SCADA sees a "normal" standpipe pressure (because the driller compensated), not the underlying efficiency loss. By the time gross efficiency loss becomes apparent on SCADA, the valve is about to fail catastrophically.
- **Operational consequence of stopping drilling:** If mud circulation stops during a critical drilling phase (e.g., while sliding directionally, or while in a reactive shale formation), drill cuttings fall back onto the bit, the wellbore walls can swell, and the drill string can become stuck. Stuck pipe is one of the most expensive events in drilling — typically $1–5M per occurrence.
- **ECD management reality:** Equivalent Circulating Density (ECD) must be maintained within a narrow window between formation pore pressure (too low = influx) and fracture gradient (too high = lost circulation). When shifting between pumps, the flow rate must remain constant to keep ECD stable. This is why the procedure is to bring the standby pump up first, then reduce the failing pump — never stop and start, always synchronize.

**Agentic Action:**
1. GDC XGBoost detects declining volumetric efficiency and fluid-end vibration signature on MUD-RIG42-1. RUL at current SPM: 45 minutes.
2. Gemma Agent queries Rig Control System (local API): "Current pump status, rig state, hole parameters."
3. Rig State returns: "MUD-RIG42-2 online at 350 GPM. MUD-RIG42-3 standby (ready). Current total flow: 700 GPM. Min required for hole cleaning at current depth/inclination: 650 GPM."
4. Agent queries RAG manual: "Procedure for pump swap during active drilling."
5. RAG returns: "Bring standby pump online to 50% of required flow rate, verify stable standpipe pressure, then reduce primary pump proportionally. Never reduce primary before standby is confirmed stable."
6. Agent recommendation: "Bring MUD-RIG42-3 online to 300 GPM. Once stable, reduce MUD-RIG42-1 to 100 GPM (maintenance mode for valve inspection). Total flow maintained at 700 GPM. MUD-RIG42-1 can be rebuilt during next planned connection stop (est. 22 minutes at current ROP)."

**Value Delivered:** Prevention of unplanned pump stoppage during drilling. An unplanned pump stop risking stuck pipe is typically $50,000–$500,000 in NPT, depending on depth and formation.

---

## What the Agent is NOT Doing (LLM Scope Guardrails)

The Gemma 2B model running on T4/L4 GPUs is used for **narrative synthesis**, not **heavy reasoning**. The agent workflow is structured so Gemma is doing the minimum viable LLM task:

1. **XGBoost does the prediction** (fault type, RUL, confidence).
2. **Rule-based Python code selects** the correct context API to call.
3. **The Context API (mock ERP/FSM/Rig State) returns structured JSON** with the relevant data.
4. **RAG retrieves relevant manual excerpts** using sentence embeddings.
5. **Gemma synthesizes** a 2–3 sentence natural language recommendation from structured inputs.

This is well within the capability of Gemma 2B on a T4. The LLM is not reasoning about physics or O&G engineering — it is narrating a pre-computed result. This is an appropriate use of local LLMs.

---

## Sensor Model Additions

Two sensors are being added to the simulation. Both are universal industry standards — not embellishments.

### ESP: Motor Current (Amps)
Every ESP installation with a Variable Frequency Drive (VFD) logs motor current continuously. It is the primary pump health indicator. As impeller stages erode from sand ingress, the pump does progressively less hydraulic work for the same input speed — current falls. This current-vs-speed-vs-pressure relationship is multivariate and genuinely not detectable by a single SCADA setpoint.

| Asset Class | New Sensor | Label | Normal Range | Critical Threshold |
|---|---|---|---|---|
| ESP (Pad Alpha) | `motor_amps` | Motor Current (A) | 60–90 A | < 40 A (underload) or > 100 A (overcurrent) |

**Fault signatures for motor_amps:**
- `sand_ingress`: 45–65 A (declining as impeller stages erode)
- `gas_lock`: 20–45 A (pump unloads as gas fraction rises)
- `motor_overheat`: 88–105 A (overcurrent driving heat buildup)

### Mud Pump: Stroke Rate (SPM)
The stroke counter is the most fundamental measurement in drilling operations. SPM × liner displacement = theoretical flow rate. If SPM trends upward over hours while standpipe pressure holds constant, the driller is compensating for declining pump volumetric efficiency — the definitive washout signature that SCADA cannot see because pressure appears normal.

| Asset Class | New Sensor | Label | Normal Range | Critical Threshold |
|---|---|---|---|---|
| Mud Pump (Rig 42) | `spm` | Pump Stroke Rate (SPM) | 75–100 SPM | > 115 SPM (over-stroking) |

**Fault signatures for spm:**
- `valve_washout`: 95–120 SPM (rising as driller compensates)
- `piston_seal_wear`: 90–110 SPM (moderate compensation)
- `pulsation_dampener_failure`: 60–130 SPM (erratic — extreme pressure hammer)

### Gas Lift: No New Sensor Required
The discharge temperature trend *rate* (not absolute value) is sufficient for the delta-T fouling narrative with existing sensors. Frame: "GDC analyzes the rate of change of discharge temperature under constant load conditions — not just the current value."

### Model Retraining Note
The current deployed XGBoost models use features `[psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]`. The new sensors (`motor_amps`, `spm`) will be displayed in the UI and included in the agent context narrative. Retraining the models with the extended feature set (`+motor_amps, +amps_dt` for ESP; `+spm, +dspm_dt` for mud pump) is a natural next step for the MLOps demo — the "☁ Retrain via Vertex AI" button can be retained and repositioned as "train the model on the full extended sensor set."

---

## Enterprise API Mock Specification

A single `/api/agent/context/{fault_type}` backend endpoint handles all three scenarios. Python routes internally to the appropriate mock data source. The frontend receives a unified `context` block tagged with the source system name. This keeps the frontend clean (one API call) while displaying authentic enterprise system branding.

### Scenario 1 — ERP Procurement API (Fault: sand_ingress)
*Modeled after SAP MM (Materials Management) / Oracle Procurement*

```json
{
  "enterprise_source": "ERP_SAP_MM",
  "query_type": "procurement_inventory",
  "well_bom": {
    "part_description": "ESP Sand-Handler Assembly",
    "series": "400",
    "stages": 100,
    "design_rate_bpd": 2000,
    "material_spec": "Tungsten Carbide Radial Bearings",
    "manufacturer": "Baker Hughes Centrilift",
    "mat_doc_number": "MAT-4002-TC-100"
  },
  "inventory": {
    "storage_location_local": 0,
    "storage_location_midland_hub": 0,
    "manufacturer_available_stock": 1,
    "manufacturer_location": "Claremore, OK"
  },
  "lead_times": {
    "standard_freight_days": 12,
    "air_freight_days": 7,
    "air_freight_premium_usd": 8500
  },
  "last_workover_date": "2025-03-14",
  "replacement_cost_usd": 145000
}
```

### Scenario 2 — FSM Scheduling API (Fault: thermal_runaway)
*Modeled after IBM Maximo / SAP Plant Maintenance*

```json
{
  "enterprise_source": "FSM_MAXIMO",
  "query_type": "field_service_schedule",
  "site": "pad_bravo",
  "upcoming_dispatches": [
    {
      "work_order_id": "WO-2026-0847",
      "crew_id": "CREW-BRAVO-B",
      "headcount": 2,
      "scheduled_date": "tomorrow",
      "scheduled_time_local": "14:00",
      "primary_task": "Transmitter calibration — Well B-3",
      "estimated_duration_hours": 2.0,
      "certifications": ["compressor_operator", "h2s_safety"],
      "available_capacity_hours": 2.5
    }
  ],
  "appended_task": {
    "description": "Aerial fin-fan cooler flush — GLIFT-BRAVO-1",
    "estimated_duration_hours": 0.75,
    "required_certifications": ["compressor_operator"],
    "parts_required": false,
    "parts_cost_usd": 0,
    "labor_cost_usd": 0,
    "emergency_dispatch_cost_usd": 1800
  }
}
```

### Scenario 3 — Rig Control API (Fault: valve_washout)
*Modeled after Pason EDR / NOV NOVOS. This query is LOCAL — rig control network, no WAN required.*

```json
{
  "enterprise_source": "DRILLSYS_PASON_EDR",
  "query_type": "rig_state",
  "local_query": true,
  "rig_id": "RIG-42",
  "hole_depth_ft": 12450,
  "inclination_deg": 38.5,
  "next_connection_min": 22,
  "ecd_constraints": {
    "min_flow_gpm_hole_cleaning": 650,
    "current_total_flow_gpm": 700
  },
  "pump_status": {
    "MUD-RIG42-1": {
      "status": "active",
      "current_spm": 89,
      "output_gpm": 350,
      "volumetric_efficiency_pct": 81,
      "ve_trend": "declining"
    },
    "MUD-RIG42-2": {
      "status": "active",
      "current_spm": 89,
      "output_gpm": 350,
      "volumetric_efficiency_pct": 95,
      "ve_trend": "stable"
    },
    "MUD-RIG42-3": {
      "status": "standby",
      "ready": true,
      "output_gpm": 0
    }
  },
  "recommended_action": {
    "step_1": "Bring MUD-RIG42-3 online to 300 GPM",
    "step_2": "Confirm stable standpipe pressure",
    "step_3": "Reduce MUD-RIG42-1 to 50 GPM (maintenance mode)",
    "result": "Total flow maintained at 700 GPM. ECD stable."
  }
}
```

---

## Implementation Plan

### Phase 0: Git Commit Baseline
Create a clean commit of the current Phase 3.1 state before any Phase 4 changes.

### Phase 1: Update RAG Documents
Expand all four source documents in `docs/rag_source/` with the scenario-specific engineering detail that grounds the Agent's narrative:
- `esp_manual.md` — motor current monitoring, sand-handler BOM, pump performance curve degradation
- `gas_lift_manual.md` — aerial cooler fouling, delta-T analysis, flush procedures
- `mud_pump_manual.md` — SPM monitoring, volumetric efficiency, ECD management, pump transition procedure
- `top_drive_manual.md` — bearing spall frequency signatures and inspection intervals

### Phase 2: Sensor Model Extension (`app.py`, `asset_metadata.json`)
- Add `motor_amps` to all ESP asset entries (normal range, crit threshold, fault ranges)
- Add `spm` to all Mud Pump asset entries (normal range, crit threshold, fault ranges)
- Update `NORMAL_RANGES`, `FAULT_PROFILES`, `ASSET_REGISTRY`
- Extend `plot_forecast()` to support `amps` and `spm` as plottable metrics

### Phase 3: Remove Cloud Comparison (`app.py`, `index.html`)
- Remove `cloud_alert_t` computation from `plot_forecast()`
- Remove purple cloud vertical line and VSAT callout box from chart output
- Remove "☁ Show Arrows" toggle button from the UI
- Remove `compare_cloud` parameter from the forecast URL

### Phase 4: Agent Context API (`app.py`)
- Add `/api/agent/context/{fault_type}` endpoint returning scenario-specific JSON
- Add `/api/agent/recommend` endpoint: passes context + RAG + RUL to Gemma, returns narrative

### Phase 5: "Predictive Insights" UI Overhaul (`index.html`)
- Revise incident panel: show RUL in hours/days for gradual faults, show "planned cost vs failure cost"
- Add 4th sensor tab (conditionally visible for ESP → "Current", Mud Pump → "Strokes")
- Add Agent recommendation section to Dispatch Modal
- Add "enterprise system queried" badge (ERP/FSM/Rig Control)
- Add simulated "🤖 Execute via Rig Control" button for Scenario 3

### Phase 6: Ask before deploying

---

## Open Questions (Resolved)

| Question | Decision |
|---|---|
| Retain MLOps Retrain button? | YES — reposition as "retrain with extended sensor set" to keep the MLOps story |
| How rich is the mock ERP? | SAP MM-style schema fields, scenario-specific data per fault type |
| SCADA command simulation? | YES — "🤖 Execute via Rig Control" for Scenario 3, visual simulation |
| Connectivity diagram? | NO for now — the enterprise_source badge on the API response is sufficient |
