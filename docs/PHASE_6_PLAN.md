# GDC-PM Phase 6 — Forecast Chart Physics, Time Slider & Agent UX

**Status:** Planned — 2026-05-13  
**Preceded by:** `PHASE_5_PLAN.md`  
**Live URL:** `http://35.188.3.97`  
**GKE Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Deployment:** `kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm`  

---

## What Phase 5 Built (Completed — Do Not Redo)

- **4 XGBoost health-score models** (`esp_health.ubj`, `gas_lift_health.ubj`, `mud_pump_health.ubj`, `top_drive_health.ubj`) trained with exponential decay curve, health 1.0→0.0, RMSE <0.002.
- **`FAULT_PHYSICS` config** in `app.py` — 11 fault modes with physical time horizons (gas_lock=45min, sand_ingress=14 days, etc.).
- **`/api/model/status`** and **`/api/fault-physics/{fault_type}`** endpoints.
- **Operations Workspace** bottom panel with Intervention Slider, Physics/Economics Calculator (left), and Ops Agent Chat (right).
- **`/api/agent/recommend`** accepts `slider_health_score` parameter.
- Docker image pushed, GKE deployment live.

---

## Phase 6 Issues Found During Live Testing

### Bug 1: ML Prediction Line Flattens at the SCADA Alarm Threshold

**Observed:** The dotted ML projection line drops along a curve, hits the red SCADA alarm threshold, then goes **completely flat** for a long stretch before resuming its drop toward failure. This plateau is physically wrong — the asset does not stabilize when a SCADA alarm fires; it continues degrading.

**Root cause:** In `app.py`'s `/api/plot/forecast/...` endpoint, the projection logic clips or holds the value at the `scada_alarm_health` level after the threshold is crossed.

**Fix:** Remove this clamping behavior. The ML projection trace must be a smooth, continuous exponential curve from detection all the way to `health=0.0` (Failure), crossing the SCADA and PNR thresholds cleanly as it goes.

---

### Bug 2: Every Sensor Tab Shows the Same SCADA and PNR Threshold Lines

**Observed:** Switching between Intake Pressure, Winding Temp, Vibration, and Motor Current — all four tabs show identical SCADA and PNR threshold annotation lines at identical times.

**Physics problem:** Only one (or at most two) sensors actually *drive* the SCADA alarm and the PNR for any given fault. For Gas Lock specifically:

| Sensor | Physical reality during Gas Lock | SCADA alarm? | PNR? |
|---|---|---|---|
| Motor Current | Drops immediately — pump unloads (less fluid = less torque) | ✅ YES — underload alarm | ❌ No — low current doesn't damage |
| Winding Temperature | Rises slowly — loss of fluid cooling | ❌ No early alarm | ✅ YES — insulation burnout |
| Intake Pressure | Drops — gas void in first stage | Supporting indicator | Supporting indicator |
| Vibration | Increases slightly — cavitation | Supporting indicator only | — |

Showing a "PNR" vertical line on the Motor Current tab is **physically nonsensical** and will confuse any petroleum engineer. Showing an early SCADA alarm on the Temperature tab is also wrong (temp is a lagging indicator).

**Fix:** Add `scada_sensor` and `pnr_sensor` to each fault in `FAULT_PHYSICS`. The `/api/plot/forecast/...` endpoint must check which tab is being rendered and only draw threshold lines that apply to that specific sensor.

Updated `FAULT_PHYSICS` entries for Phase 6 (examples):

```python
"gas_lock": {
    "horizon_label": "Minutes",
    "total_hours": 0.75,
    "scada_alarm_health": 0.30,
    "pnr_health": 0.12,
    "scada_sensor": "amps",       # SCADA fires on Motor Current underload
    "pnr_sensor": "temp",         # PNR is winding temperature burnout
    "primary_sensor": "amps",     # Most important tab to look at first
    "intervention_type": "operational_control",
},
"sand_ingress": {
    "horizon_label": "Days",
    "total_hours": 336,
    "scada_alarm_health": 0.15,
    "pnr_health": 0.05,
    "scada_sensor": "vib",        # Vibration high alarm from impeller erosion
    "pnr_sensor": "vib",          # Vibration also drives PNR (impellers destroyed)
    "primary_sensor": "vib",
    "intervention_type": "supply_chain",
},
"bearing_wear": {
    "horizon_label": "Hours",
    "total_hours": 16,
    "scada_alarm_health": 0.20,
    "pnr_health": 0.08,
    "scada_sensor": "vib",        # Vibration high alarm (bearing roughness)
    "pnr_sensor": "temp",         # Thermal runaway as bearing seizes
    "primary_sensor": "vib",
    "intervention_type": "maintenance_scheduling",
},
"motor_overheat": {
    "horizon_label": "Hours",
    "total_hours": 4,
    "scada_alarm_health": 0.25,
    "pnr_health": 0.10,
    "scada_sensor": "temp",       # Temperature high alarm
    "pnr_sensor": "temp",         # Temperature drives insulation failure
    "primary_sensor": "temp",
    "intervention_type": "operational_control",
},
"piston_seal_wear": {
    "horizon_label": "Days",
    "total_hours": 96,
    "scada_alarm_health": 0.20,
    "pnr_health": 0.08,
    "scada_sensor": "pressure",   # Pressure drop (leaking past seal)
    "pnr_sensor": "vib",          # Vibration as piston wipes
    "primary_sensor": "pressure",
    "intervention_type": "maintenance_scheduling",
},
```

For remaining faults (fill in similarly by fault type physics):
- `gearbox_bearing_spalling` → vib (SCADA) / temp (PNR)
- `thermal_runaway` → temp (SCADA + PNR)
- `valve_washout` → pressure (SCADA + PNR)
- `hydraulic_leak` → pressure (SCADA + PNR)
- `pulsation_dampener_failure` → pressure (SCADA + PNR)
- `valve_failure` → pressure (SCADA + PNR)

**Tab badge UI change:** The sensor tab that is the `primary_sensor` for the active fault must be visually highlighted — bold text or a small "⚡ PRIMARY" badge — so the operator is immediately directed to the most important indicator.

---

### Bug 3: Slow Tab Switching (Full Chart Reload)

**Observed:** Switching between sensor tabs (Intake Pressure, Winding Temp, Vibration, Motor Current) triggers a full `<iframe>` src reload, which takes 2-4 seconds each time.

**Root cause:** Each tab change re-requests `/api/plot/forecast/...` from the server, which re-runs the ML inference and regenerates the full Plotly HTML.

**Fix:** Return all 4 sensor traces as JSON in a single API call. The frontend JavaScript will keep a single Plotly chart in-DOM and switch between traces using `Plotly.react()`, which is near-instantaneous.

**Architecture change:** Remove the `<iframe>` for the forecast chart. Replace with a `<div id="forecast-chart">` and use Plotly's JavaScript library directly in `index.html`. The backend `/api/plot/forecast/...` endpoint should return a `application/json` response (Plotly `data` and `layout` arrays) rather than a full HTML page.

---

### Bug 4: Intervention Slider is Health-Based, Not Time-Based

**Observed:** The slider position is expressed as "Health 75%" — the Operations Workspace calculator says "Intervening at Health 75%". This is abstract and not how operators think.

**Fix:** Convert the slider to a **Time Remaining** axis. The slider range is defined by the current ML prediction of time-to-failure:
- **Right edge (max):** Current ML prediction of minutes/hours/days to failure.
- **Left edge (0):** Failure (T=0 remaining).
- As the operator drags the slider left, they are saying: *"I am choosing to wait X [minutes/hours/days] before acting."*
- The calculator will display: **"Intervening in 5 hours — 9 hours before PNR"** instead of the abstract "Health 75%".

The slider should tick/animate automatically as the live telemetry clock ticks down the time-to-failure prediction. The operator can grab and move it at any time to explore "what if I wait longer?".

---

### Bug 5: Operations Workspace Does Not Update Live

**Observed:** The Intervention Slider and the Physics/Economics Calculator in the Operations Workspace only update when the user physically drags the slider. They do not animate automatically as the live ML prediction changes.

**Fix:** The existing `/api/recent-events` or a new `/api/degrade-status/{asset_id}` polling endpoint should return the current live `health_score`. The `setInterval` loop in `index.html` should feed this live score into the slider's `max` value, causing the calculator to tick down in sync with the forecast chart.

---

### Bug 6: Operations Agent CSS Overlap / "Consulting..." State Looks Broken

**Observed:** On the right side of the Operations Workspace, the "Consulting Operations Agent..." text and the "Consulting at Health 75% — 🟢 EARLY" buttons overlap and look visually broken, especially before the agent has responded.

**Fix:** Clean up the CSS for the agent panel. The initial state before the user clicks "Consult Agent" should show a clean, inviting chat interface:
```
[ 🤖 Ops Agent ]

  Gas Lock detected on ESP-ALPHA-2.
  Set the slider to your intended intervention time,
  then press 'Consult Operations Agent'.

  [ Ask the Operations Agent... ]        [ Send ]
```

When the agent is thinking, show a subtle animated typing indicator (three dots) rather than a full-width "Consulting..." button that blocks interaction.

The "Consulting at Health X%" quick-reply buttons should be removed from the initial state — they appear to be partially-formed action buttons that confuse the user. Instead, quick-reply buttons should only appear AFTER the agent provides a response with specific options.

---

### Bug 7: Ops Agent Response Latency (Too Slow)

**Observed:** After clicking "Consult Operations Agent", the user waited a very long time before receiving a response. This is unacceptable during a live demo.

**Diagnosis options (check in this order):**
1. **Vertex AI Gemma endpoint cold start** — If the GKE endpoint is not receiving enough traffic, it may scale to 0 and need to warm up. Check if there is a minimum replica count of 1 set.
2. **Prompt size** — If the `chat_history` + `context_summary` + system prompt being sent to the LLM is very large, reduce the context. The agent prompt should be <1,500 tokens total.
3. **Model selection** — `gemma-3-27b-it` is much slower than `gemma-3-12b-it` or `gemma-3-4b-it`. For a demo, a smaller model with a tightly constrained prompt will feel far more responsive.
4. **Streaming** — Instead of waiting for the full response, stream the LLM output token-by-token and append to the chat window as it arrives.

**Fix recommendations (in priority order):**
- **Short-term:** Replace the blocking LLM call with a streaming call using `stream=True` on the Vertex AI SDK. Update the `/api/agent/recommend` endpoint to return a `StreamingResponse` (FastAPI). The JavaScript will consume the SSE stream and update the chat window in real-time.
- **Mid-term:** Reduce model to `gemma-3-12b-it` for demo use. Tighten the system prompt to under 200 words.
- **Long-term:** Implement a `keep-alive` ping to the Vertex AI endpoint every 5 minutes to prevent cold starts.

---

## Implementation Execution Steps

### Phase 6.1 — Backend: Physics Fix + Chart Data API (app.py)
1. Add `scada_sensor` and `pnr_sensor` to all 11 `FAULT_PHYSICS` entries.
2. Fix the prediction flattening bug — remove any clamping of health score at SCADA threshold.
3. Change `/api/plot/forecast/{asset_id}` to return JSON Plotly traces for all 4 sensors in one call, including `scada_sensor` and `pnr_sensor` metadata so the frontend knows where to draw threshold lines.
4. Add `/api/degrade-status/{asset_id}` endpoint returning `{ health_score, time_to_failure_minutes, fault_type, is_active }` for the frontend polling loop.

### Phase 6.2 — Backend: Agent Streaming (app.py)
1. Reduce LLM model size to `gemma-3-12b-it` (or `gemma-3-4b-it` for demo responsiveness).
2. Enable streaming response from Vertex AI SDK.
3. Change `/api/agent/recommend` to return a `StreamingResponse` with SSE (Server-Sent Events) format.
4. Tighten system prompt to <200 words. The agent should ask exactly ONE question per turn.

### Phase 6.3 — Frontend: Chart + Tab Switching Overhaul (index.html)
1. Replace forecast `<iframe>` with `<div id="forecast-chart">` + Plotly.js loaded inline.
2. On fault injection, call the new JSON forecast endpoint and use `Plotly.newPlot()`.
3. Tab switching → `Plotly.react()` to update trace visibility — no server call.
4. Highlight `primary_sensor` tab with a `⚡` badge when a fault is active.
5. Only draw SCADA threshold line on the tab matching `scada_sensor`; only draw PNR line on tab matching `pnr_sensor`.

### Phase 6.4 — Frontend: Time-Based Slider + Live Workspace (index.html)
1. Replace `slider_health_score` (0–1) with `slider_time_remaining` (0 to `time_to_failure_minutes`).
2. The slider label should read: **"Intervening in [X] [min/hrs/days]"** not "Health X%".
3. Wire the existing `setInterval` poll loop to update the slider's `max` value from `/api/degrade-status/`.
4. The slider thumb should animate leftward automatically each poll cycle.
5. If the user grabs the slider, pause the auto-animation until they release.

### Phase 6.5 — Frontend: Agent UI Cleanup (index.html)
1. Remove the "Consulting at Health X% — 🟢 EARLY" pre-populated quick-reply buttons from the initial state.
2. Clean initial state: show clean invite text and the chat input only.
3. Replace "Consulting..." full-width button with a subtle animated `…` typing indicator inside the chat log.
4. Consume SSE stream from the new `/api/agent/recommend` endpoint and append tokens to the chat log in real-time.

### Phase 6.6 — Docker Rebuild & Deploy
1. `docker build --platform linux/amd64 -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .`
2. `docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
3. `kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm`
4. Verify at `http://35.188.3.97`

---

## Sensor-to-Fault Physics Reference

This mapping governs which sensor tab gets threshold annotations. Use this as the authoritative reference.

| Fault | Primary Sensor | SCADA Trigger | PNR Trigger |
|---|---|---|---|
| `gas_lock` | Motor Current | Current underload (amps ↓) | Winding temp (temp ↑) |
| `sand_ingress` | Vibration | Vibration high (vib ↑) | Vibration / impeller destroyed (vib ↑) |
| `bearing_wear` | Vibration | Vibration high (vib ↑) | Winding temp seize (temp ↑) |
| `piston_seal_wear` | Intake Pressure | Pressure drop (pressure ↓) | Vibration / piston wipes (vib ↑) |
| `motor_overheat` | Winding Temp | Temp high alarm (temp ↑) | Winding temp burnout (temp ↑) |
| `thermal_runaway` | Winding Temp | Temp high alarm (temp ↑) | Winding temp burnout (temp ↑) |
| `gearbox_bearing_spalling` | Vibration | Vibration high (vib ↑) | Temp seize (temp ↑) |
| `valve_washout` | Intake Pressure | Pressure drop (pressure ↓) | Pressure / valve destroyed (pressure ↓) |
| `hydraulic_leak` | Intake Pressure | Pressure drop (pressure ↓) | Pressure / loss of prime (pressure ↓) |
| `valve_failure` | Intake Pressure | Pressure drop (pressure ↓) | Pressure (pressure ↓) |
| `pulsation_dampener_failure` | Intake Pressure | Pressure spike (pressure ↑) | Pressure / rupture (pressure ↑) |

---

## Things NOT to Change in Phase 6
- The 4 `*_health.ubj` model files — they are correct.
- The AlloyDB schema or event-processor pipeline.
- The Grafana dashboard.
- The Fault Trigger injection logic (`/api/fault/inject`).
- The `FAULT_PHYSICS` time horizons (total_hours, scada_alarm_health, pnr_health) — only ADD the sensor fields.
- The site hierarchy (Pad Alpha / Bravo) — leave as-is.

---

## Restart Prompt for New Session

```
Read docs/PHASE_6_PLAN.md carefully before touching any code.

The GDC-PM demo is live at http://35.188.3.97.
All files are at /home/brian/gdc-pm/gke/fault-trigger-ui/.
Primary files to edit: app.py and index.html.
Docker image: us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest

Phase 5 is fully deployed and working. Phase 6 fixes a set of chart physics
bugs and UX problems discovered during live testing. Do not retrain any models
(the *_health.ubj files in models/ are correct and must not be changed).

Start with Phase 6.1: Fix the two app.py bugs (prediction flattening + sensor
routing). Add scada_sensor and pnr_sensor to all 11 FAULT_PHYSICS entries using
the Sensor-to-Fault Physics Reference table in the plan. Remove the prediction
trace clamping that causes the dotted ML projection to go flat at the alarm
threshold.

Key facts:
- The forecast chart uses an <iframe> today — the plan is to replace it with
  inline Plotly.js for instant tab switching (Phase 6.3).
- The Intervention Slider currently uses health_score (0-1). Phase 6.4 converts
  it to time_remaining in physical units (Days/Hours/Minutes).
- The Ops Agent response is too slow. Phase 6.2 is to switch to SSE streaming
  and reduce the model to gemma-3-12b-it.
- The "Consulting..." CSS state in the agent panel right side looks broken and
  needs cleanup (Phase 6.5).

Work through Phases 6.1→6.6 in order. After each phase, confirm what was
changed before moving to the next.
```
