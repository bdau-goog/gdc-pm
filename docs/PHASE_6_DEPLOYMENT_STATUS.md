# GDC-PM Phase 6 — Deployment Status

**Completed:** 2026-05-13  
**Live URL:** http://35.188.3.97  
**GKE Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Image Digest:** `sha256:6245577334062549ed70756c5365f6edc523be2f58b707d6d5d02f91a3e14a42`

---

## What Was Fixed

Phase 6 was a bug-fix and UX polish pass discovered during live testing of Phase 5.

### Phase 6.1 — Backend: Physics Fix + Chart Data API (`app.py`)

#### Bug 1 Fixed: ML Prediction Line Flatline at SCADA Threshold
**Root cause:** The forecast projection used `np.clip(t_arr / max(rul_minutes, 0.5), 0.0, 1.0)` which clamped the interpolation fraction to 1.0 once `t > rul_minutes`. This held the dotted ML projection flat at `y_end` (just below the SCADA alarm threshold) for the remainder of the x-axis.

**Fix:** Replaced with a smooth exponential decay curve matching the Phase 5 training curve:
```python
frac       = t_arr / max(ttf_total_min, 1.0)
forecast_y = y_start + (y_failure - y_start) * (1.0 - np.exp(-3.5 * frac))
```
- `ttf_total_min` = `FAULT_PHYSICS[fault_type].total_hours * 60` (full failure horizon, always >> rul_minutes)
- `y_failure` = 45% of alarm threshold for "below" sensors, 180% for "above" sensors
- No `np.clip` → curve smoothly passes through SCADA threshold and continues to full failure

#### Bug 2 Fixed: SCADA/PNR Threshold Lines on Wrong Sensor Tabs
**Root cause:** The forecast endpoint drew the SCADA alarm threshold line and PNR vertical marker on every sensor tab regardless of which sensor physically triggers the alarm.

**Fix:** Added `scada_sensor`, `pnr_sensor`, `primary_sensor` fields to all 11 `FAULT_PHYSICS` entries using the authoritative Sensor-to-Fault Physics Reference table:

| Fault | SCADA Sensor | PNR Sensor | Primary Sensor |
|---|---|---|---|
| `gas_lock` | amps | temp | amps |
| `sand_ingress` | vib | vib | vib |
| `bearing_wear` | vib | temp | vib |
| `gearbox_bearing_spalling` | vib | temp | vib |
| `motor_overheat` | temp | temp | temp |
| `thermal_runaway` | temp | temp | temp |
| `piston_seal_wear` | psi | vib | psi |
| `valve_washout` | psi | psi | psi |
| `hydraulic_leak` | psi | psi | psi |
| `valve_failure` | psi | psi | psi |
| `pulsation_dampener_failure` | psi | psi | psi |

Threshold line and vertical markers are now conditionally drawn:
```python
_show_scada_annotations = (not _fp_scada_sensor) or (metric == _fp_scada_sensor)
_show_pnr_annotation    = (not _fp_pnr_sensor)   or (metric == _fp_pnr_sensor)
```

#### New Endpoints Added

**`GET /api/degrade-status/{asset_id}`** — Per-asset live health status for Phase 6.4 slider:
```json
{
  "asset_id": "ESP-ALPHA-2", "is_active": true, "fault_type": "gas_lock",
  "health_score": 0.7412, "time_to_scada_minutes": 9.2, "time_to_pnr_minutes": 4.5,
  "time_to_failure_minutes": 33.4, "horizon_label": "Minutes",
  "scada_sensor": "amps", "pnr_sensor": "temp", "primary_sensor": "amps"
}
```

**`GET /api/plot/forecast-data/{asset_id}`** — Single-call JSON with all 4 sensor tabs' Plotly traces for Phase 6.3 instant tab switching:
```json
{
  "asset_id": "ESP-ALPHA-2", "fault_type": "gas_lock", "health_score": 0.74,
  "scada_sensor": "amps", "pnr_sensor": "temp", "primary_sensor": "amps",
  "sensors": {
    "psi":  {"traces": [...], "layout": {...}, "is_scada": false, "is_pnr": false},
    "temp": {"traces": [...], "layout": {...}, "is_scada": false, "is_pnr": true},
    "vib":  {"traces": [...], "layout": {...}, "is_scada": false, "is_pnr": false},
    "amps": {"traces": [...], "layout": {...}, "is_scada": true,  "is_pnr": false}
  }
}
```

---

### Phase 6.2 — Backend: Agent Streaming (`app.py`)

- `OLLAMA_MODEL` default changed from `gemma:2b` → `gemma3:12b` (faster, better quality for demos)
- New `POST /api/agent/recommend-stream` endpoint returns SSE:
  ```
  data: {"type":"recommendation","text":"...","tier":"EARLY","rul_minutes":9.2}
  data: {"type":"token","text":"Reduce"}
  data: {"type":"token","text":" VFD"}
  ...
  data: {"type":"done"}
  ```
- Rule-based recommendation fires immediately (zero LLM latency), LLM tokens stream in afterward
- System prompt tightened to <150 words, `num_predict:100`, `temperature:0.2`
- SSE headers set: `Cache-Control: no-cache`, `X-Accel-Buffering: no`

---

### Phase 6.3 — Frontend: Inline Plotly.js Chart (`index.html`)

**Removed:** `<iframe id="plot-iframe">` (was causing 2-4s reload on every tab switch)

**Added:** `<div id="forecast-chart">` + Plotly.js 2.35.2 CDN in `<head>`

**New architecture:**
- `refreshPlot()` fetches `/api/plot/forecast-data/{asset_id}` **once**, stores all 4 sensor traces in `_currentForecastData`
- `selectTab()` calls `Plotly.react(chartDiv, sd.traces, sd.layout)` — **zero server round-trip**, instant
- `_updateSensorTabBadges()` adds ⚡ badge to `primary_sensor` tab when fault is active
- Fullscreen (`expandPlot`) still uses the HTML iframe endpoint for simplicity
- Slider auto-follows live `health_score` from `_currentForecastData` on each poll cycle (respects `_sliderUserHeld` guard)

---

### Phase 6.5 — Frontend: Agent UI Cleanup (`index.html`)

**Problem:** Clicking "Consult Operations Agent" set the button text to "⏳ Consulting…" (a full-width blocking state that looked broken) and left the chat panel empty while waiting.

**Fix:** SSE streaming with animated typing indicator:
1. Button immediately disables (no text change)
2. `● ● ●` animated typing indicator appears in chat log
3. On first `data: {"type":"recommendation"}` event: indicator removes, rule-based text appears instantly
4. LLM tokens stream into a second teal-bordered bubble as they arrive
5. Quick-reply buttons appear only after agent responds

**Also cleaned up:**
- Initial workspace chat shows clean invite text (no pre-populated "Consulting at Health X% — 🟢 EARLY" action buttons)
- `consultAgent()` uses `/api/agent/recommend-stream` via `fetch().body.getReader()` (SSE from POST)
- `sendAgentMessage()` still uses blocking `/api/agent/recommend` (text messages with chat history)

---

## Files Changed

| File | Changes |
|---|---|
| `gke/fault-trigger-ui/app.py` | FAULT_PHYSICS sensor routing (11 entries), exponential forecast curve, sensor routing conditionals, `/api/degrade-status/{asset_id}`, `/api/plot/forecast-data/{asset_id}`, `/api/agent/recommend-stream`, `OLLAMA_MODEL=gemma3:12b`, `StreamingResponse` import |
| `gke/fault-trigger-ui/index.html` | Plotly.js CDN, `<div id="forecast-chart">` replaces iframe, `refreshPlot()` → JSON+Plotly, `selectTab()` → `Plotly.react()`, `_currentForecastData` cache, ⚡ primary badge, `consultAgent()` → SSE streaming, `● ● ●` typing indicator |

**Not changed:** `*_health.ubj` model files, AlloyDB schema, Grafana dashboard, simulator, event-processor, site hierarchy.

---

## Key Technical Decisions

### Why exponential k=3.5 instead of linear for the forecast curve?
The Phase 5 XGBoost health models were trained on data generated with exponential decay (k=3.5). Using a matching exponential curve for the projection ensures the visual behavior matches the model's output domain. A linear projection would over-estimate remaining time for early-stage faults and under-estimate for late-stage.

### Why draw SCADA/PNR markers on only one tab each?
The SCADA alarm system in an O&G installation fires based on a specific sensor threshold crossing a specific setpoint. Showing a SCADA alarm threshold on a sensor that doesn't trigger the alarm (e.g., showing the motor current SCADA underload alarm on the vibration chart) is physically wrong and would confuse a petroleum engineer. Each fault has exactly one sensor that determines the SCADA trigger and one that determines the PNR (which may be different — e.g. gas_lock SCADA fires on motor current but PNR is determined by winding temperature).

### Why one JSON endpoint for all 4 sensor tabs?
The old architecture made one `/api/plot/forecast/{asset_id}?metric=X` request per tab switch, each running the full ML inference + Plotly chart generation. With 4 tabs and the user clicking through them, this was 4× the latency. The new `/api/plot/forecast-data/{asset_id}` endpoint runs ML inference once and returns all 4 sensor traces as JSON. The frontend switches tabs at animation speed using `Plotly.react()`.

### Why keep blocking `/api/agent/recommend` for `sendAgentMessage()`?
The SSE streaming endpoint `/api/agent/recommend-stream` is optimized for the initial consult (slider position → enterprise data → rule-based + LLM). Follow-up text messages in `sendAgentMessage()` use the blocking endpoint because they include `chat_history` context. Adding chat_history SSE streaming would require adding a `message` parameter to the SSE endpoint — a future improvement for Phase 7.

---

## Known Limitations (Backlog for Phase 7)

- **Phase 6.4 (Intervention Slider):** The slider still uses health % (0-100) instead of physical time units (Days/Hours/Minutes). The backend `/api/degrade-status/{asset_id}` endpoint now returns the time values — the frontend just needs to update the slider range and labels. The infrastructure is in place.
- **`sendAgentMessage()` not streaming:** Follow-up chat messages still use blocking HTTP. Could be migrated to SSE if the streaming endpoint is extended to accept `chat_history`.
- **Slider auto-tick animation:** The slider thumb moves left as time ticks down (via `_sliderUserHeld` guard + health score from `_currentForecastData`), but the tick rate is 10s (same as the main poll interval). Could be made smoother with a separate 5s degrade-status poll.
- **Plotly resize on workspace toggle:** When the Operations Workspace opens/closes (changing the chart's available height), Plotly may not auto-resize. A `Plotly.relayout(chartDiv, {autosize: true})` call on workspace visibility change would fix this.
