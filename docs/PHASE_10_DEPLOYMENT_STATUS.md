# Phase 10 Deployment Status

**Date:** 2026-05-13  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2`  
**Cluster:** `gdc-edge-simulation`  
**Namespace:** `gdc-pm`  

## Image Digest

```
us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:7496cf230650d0d2ec6fa07302520c741752c92b9ed236bf3f69ac10638b8579
```

## Changes Deployed

### Critical Design Flaw: Tier Badge Semantic Bug (Fixed)

**Root cause:** `_wsSliderHealth` was used for both intervention timing AND tier badge urgency display.

**Fix:** Added `_wsCurrentHealth` variable in `index.html`:
- The `_startDegradePoller()` always updates `_wsCurrentHealth` from server, independent of slider position
- `updateWorkspace()` now computes `tierDisp = getTier(_wsCurrentHealth ?? hs, fp)` for badge display
- Slider health (`hs`) still drives physics calculations and cost estimates
- Badge now reflects actual current asset health — not the operator's chosen future intervention time

**Verification:** `grep -c "_wsCurrentHealth" index.html` → 7 occurrences (state var, poller, showWorkspace reset, resetNormal, updateWorkspace)

---

### Bug 1: Stale Intervening Marker on Reset (Fixed)

**Symptom:** After clicking ↺ Reset, green "Intervening" line remained on ML Forecast chart.

**Fix in `index.html`:**
- `resetNormal()` now calls `hideWorkspace()` and clears `_wsCurrentHealth = null`
- `showWorkspace()` resets `_wsCurrentHealth = null` and `_primaryTabSelected = false` on new fault
- `_renderForecastTab()` already guards Intervening shape with `if (_wsActiveFault && ...)`

---

### Bug 2: Poller Overwrites Manual Slider (Fixed)

**Symptom:** Operator drags slider → badge changes to CRITICAL. After ~60s poller reverts badge.

**Fix in `index.html`:**
- `_startDegradePoller()` now ALWAYS updates `_wsCurrentHealth` (current health from server)
- `_wsSliderHealth` updated ONLY when `!_sliderManuallySet`
- `updateWorkspace()` always called so badge reflects `_wsCurrentHealth` even when slider is held

---

### Bug 3: Gas-Lock Primary Sensor (Fixed)

**Symptom:** On gas-lock injection, "Motor Current ⚡" tab was auto-selected as primary sensor.

**Fix in `app.py` FAULT_PHYSICS:**
```python
"gas_lock": {
    "scada_sensor": "psi",    # PSI drops below 800 psi critical threshold
    "pnr_sensor": "temp",     # Winding temperature burnout at PNR
    "primary_sensor": "psi",  # Intake Pressure is the causal leading sensor
}
```

**Fix in `index.html`:** `_updateSensorTabBadges()` now auto-selects primary tab once per fault injection (`_primaryTabSelected` flag), and `selectAsset()`/`showWorkspace()` reset this flag.

**Verification:** `curl http://35.188.3.97/api/fault-physics/gas_lock` → `primary_sensor: psi, scada_sensor: psi` ✅

---

### Bug 4: SCADA Alarm Marker Curve Alignment (Fixed)

**Symptom:** Red "SCADA Alarm in Xm" vertical line appeared to the right of where the dotted projection curve crossed the SCADA threshold.

**Root cause:** The single-segment exponential `f(t) = y_start + (y_failure - y_start) * (1 - exp(-k*t/T))` does NOT reach `y_crit` at `t = rul_minutes` — it only reaches ~97% there.

**Fix in `app.py`** (both `plot_forecast()` and `_build_sensor()` in `get_forecast_data()`):
Two-segment exponential parameterisation:
- Segment 1 `[0 → rul_minutes]`: `y_start → y_crit` using `(exp(k*t/T1)-1)/(exp(k)-1)` — equals exactly `y_crit` at `t = rul_minutes`
- Segment 2 `[rul_minutes → ttf_total_min]`: `y_crit → y_failure`

The SCADA alarm marker now aligns precisely where the dotted curve crosses the alarm threshold.

---

### Feature: `sendAgentMessage()` SSE Streaming (Added)

**Previous state:** `sendAgentMessage()` used blocking `POST /api/agent/recommend` endpoint.

**Fix in `app.py`:**
- Added `chat_history: str = None` parameter to `get_agent_recommend_stream()`
- Parse JSON chat history array and inject last 4 turns into LLM prompt as `CONVERSATION:` block

**Fix in `index.html`:**
- `sendAgentMessage()` now uses SSE streaming via `POST /api/agent/recommend-stream`
- Sends `chat_history=JSON.stringify(_agentChatHistory.slice(-6))` in URLSearchParams
- Shows animated `● ● ●` typing indicator while streaming
- Rule-based response appears immediately; LLM tokens stream character-by-character into teal-bordered bubble
- Full streamed content pushed to `_agentChatHistory` on `type === 'done'`

---

### Feature: Retrain XGBoost Models with Slider Data (Completed)

**Script:** `scripts/retrain_edge_models.py`

**Change:** Added partial-intervention plateau to `generate_sequence()`:
- With probability 15%, inserts a 5–15 step plateau where health_score and sensor values are held constant at the intervention level
- Plateau applied when health is between 0.30 and 0.70 (meaningful degradation zone)
- Makes models robust to non-monotonic health trajectories seen in real deployments

**Training results (Phase 10 models):**
| Asset Class | RMSE | File Size |
|------------|------|-----------|
| esp | ~0.002 | 1355 KB |
| gas_lift | ~0.002 | 1280 KB |
| mud_pump | ~0.002 | 1347 KB |
| top_drive | 0.00176 | 1330 KB |

All models trained in 108s on CPU with 300 samples/fault × 300 XGBoost rounds.

---

## Files Changed

| File | Changes |
|------|---------|
| `gke/fault-trigger-ui/app.py` | gas_lock FAULT_PHYSICS (psi), two-segment exponential curve, chat_history in recommend-stream |
| `gke/fault-trigger-ui/index.html` | `_wsCurrentHealth`, tier badge decouple, Bug 1/2/3 fixes, primary tab auto-select, sendAgentMessage SSE streaming |
| `scripts/retrain_edge_models.py` | Partial-intervention plateau in generate_sequence() |

## Deployment Commands Run

```bash
# Retrain models
python3 scripts/retrain_edge_models.py --n-samples 300 --rounds 300

# Docker build
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/

# Docker push
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
# digest: sha256:7496cf230650d0d2ec6fa07302520c741752c92b9ed236bf3f69ac10638b8579

# Rollout
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=180s
# → deployment "fault-trigger-ui" successfully rolled out
```

## Live Verification

| Check | Result |
|-------|--------|
| UI serving at http://35.188.3.97 | ✅ |
| All 4 health models loaded | ✅ `['esp', 'gas_lift', 'mud_pump', 'top_drive']` |
| gas_lock primary_sensor = psi | ✅ |
| gas_lock scada_sensor = psi | ✅ |
| `_wsCurrentHealth` in index.html | ✅ 7 occurrences |
