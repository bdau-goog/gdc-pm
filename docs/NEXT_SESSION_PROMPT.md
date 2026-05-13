# Next Session Prompt — Phase 10

## Context
GDC Predictive Maintenance demo running on GKE Autopilot.
- Live URL: http://35.188.3.97
- Project: `gdc-pm-v2`, cluster: `gdc-edge-simulation`, namespace: `default`
- Image: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Files to edit: `gdc-pm/gke/fault-trigger-ui/index.html` and `gdc-pm/gke/fault-trigger-ui/app.py`
- After any change: `docker build`, `docker push`, `kubectl rollout restart deployment/fault-trigger-ui`

## Go Directly to Act Mode

Do NOT spend time in Plan Mode re-investigating. All bugs and their root causes are documented below. Implement all fixes, rebuild the image, redeploy, verify at the live URL, and document a new deployment status doc.

---

## Critical Design Flaw (Fix First)

### The Tier Badge Semantic Bug

**Root cause:** `_wsSliderHealth` is used for two purposes that must be separated:
1. The health score projected at the slider's chosen intervention time (used to tell the agent "how healthy will the asset be when I intervene")
2. The *current* health score used to determine intervention urgency (EARLY / URGENT / CRITICAL)

The tier badge must reflect urgency *right now* based on the asset's current health, not the projected health at the operator's chosen future intervention time.

**Fix in `index.html`:**
- Add a new variable `_wsCurrentHealth` (initialized to `null`). The poller sets this to the latest `health_score` returned from `/api/health-status/{asset_id}` on every poll, regardless of slider position.
- `_wsSliderHealth` continues to represent health at the slider time (used for the Intervening marker position and as context for the agent recommendation).
- Change every call to `getTier(_wsSliderHealth, fp)` that feeds the **tier badge display** to `getTier(_wsCurrentHealth ?? _wsSliderHealth, fp)`.
- The agent `sendAgentMessage()` and `consultOperationsAgent()` should continue passing `_wsSliderHealth` (slider health) as `slider_health_score` to the backend — that is correct.

**Why this fixes the observed symptoms:**
- Moving slider left (intervening sooner when asset is still healthier in the future) no longer flips badge to CRITICAL — the badge reflects current health, which hasn't changed.
- After one minute when poller fires, it updates `_wsCurrentHealth` from the server, which is correct.
- Tier badge correctly shows EARLY → URGENT → CRITICAL as the fault degrades in real time, independent of where the operator positions the slider.

---

## Bug 1 — Stale Intervening Marker on Reset

**Symptom:** After clicking Reset (no active fault), the green "Intervening" vertical line still appears on the ML Forecast chart, and the ML Detection panel still shows a tier badge (EARLY) with timing values.

**Root cause:** `showWorkspace()` / `_renderForecastTab()` does not clear the Intervening shape and the tier badge when `_wsActiveFault` is null.

**Fix in `index.html`:**
- In `showWorkspace()` (called on reset / fault clear): set `_sliderManuallySet = false`, clear `_wsCurrentHealth = null`, clear `_wsSliderHealth` to a sensible default (e.g. 1.0), and hide / remove the intervention slider panel.
- In `_renderForecastTab()`: before adding the Intervening shape to `shapes[]`, guard with `if (_wsActiveFault && nowISO)`. If no active fault, skip the shape entirely.
- Also guard the tier badge update: only update it if `_wsActiveFault` is set.

---

## Bug 2 — Poller Overwrites Manual Slider Even with _sliderManuallySet=true

**Symptom:** Operator drags the slider → badge changes to CRITICAL. After ~60s the poller fires and badge reverts to EARLY.

**Root cause:** The poller's health-status fetch calls code that sets `_wsSliderHealth` unconditionally when there is no active fault (the guard `if (!_sliderManuallySet)` is either absent or in the wrong branch).

**Fix in `index.html`:**
- The poller should ALWAYS update `_wsCurrentHealth` (current health from server) — this drives the tier badge.
- The poller should update `_wsSliderHealth` ONLY when `!_sliderManuallySet` (slider not manually positioned).
- The poller should also only update the slider DOM element's value when `!_sliderManuallySet`.
- Confirm the `_sliderManuallySet` flag is reset to `false` in `showWorkspace()` when a new fault workspace opens (so that fresh fault injections start with auto-tracking).

---

## Bug 3 — Gas-Lock: Motor Current Selected as Primary Sensor Tab

**Symptom:** On gas-lock fault injection, the "Motor Current ⚡" tab is auto-selected and shown as the primary sensor. Gas lock is driven by rising gas void fraction reducing intake *pressure* — the physically correct leading sensor is Intake Pressure (PSI drops toward 800 psi critical threshold).

**Root cause:** In `app.py` FAULT_PHYSICS, `"primary_sensor": "amps"` for gas_lock.

**Fix in `app.py`:**
```python
"gas_lock": {
    "horizon_label": "Minutes",
    "total_hours": 0.75,
    "scada_alarm_health": 0.30,
    "pnr_health": 0.12,
    "scada_sensor": "psi",        # PSI drops below 800 psi critical threshold
    "pnr_sensor": "temp",         # Winding temperature burnout at PNR
    "primary_sensor": "psi",      # Intake Pressure is the causal leading sensor
    "intervention_type": "operational_control",
},
```
Also update the matching entry in `FAULT_PHYSICS_JS` in `index.html`.

**Note on amps:** Motor Current (amps) does drop as gas void fraction rises (pump unloads), but it is a *lagging* secondary indicator. PSI is the causal first-mover for gas lock.

---

## Bug 4 — Gas-Lock SCADA Alarm Marker Renders After Curve Crosses Threshold

**Symptom:** The red "SCADA Alarm in Xm" vertical line appears to the right of where the orange dotted projection curve actually crosses the red dashed SCADA threshold.

**Root cause:** `ttf_time = now + timedelta(minutes=rul_minutes)` where `rul_minutes` = time until SCADA alarm from current health score. This is physically correct. However, the projection curve is drawn using an exponential decay that is anchored to `y_start` (current sensor value) and `y_failure` (full failure endpoint), with `y_crit` as the SCADA threshold *en route*. Because the exponential decay is computed over `ttf_total_min` (the full failure horizon), the curve visually crosses `y_crit` later than `rul_minutes` because the curve endpoint is `y_failure`, not `y_crit`.

**Fix in `app.py` and the `_build_sensor` equivalent in `get_forecast_data`:**
The exponential projection curve should be parameterized so that it crosses `y_crit` exactly at `t = rul_minutes`. Currently the curve uses:
```python
t_norm = t_arr / ttf_total_min  # normalized over FULL failure horizon
```
This means at `t = rul_minutes`, `t_norm = rul_minutes / ttf_total_min < 1.0`, and the exponential hasn't reached `y_crit` yet at that point on the curve.

The fix: derive the curve so that `y_crit` is hit exactly at `t = rul_minutes`. Use a two-segment approach:
- From `t=0` to `t=rul_minutes`: exponential decay from `y_start` to `y_crit`
- From `t=rul_minutes` to `t=x_end`: continued exponential decay from `y_crit` to `y_failure`

Or alternatively, re-scale the exponential so that `exp(k * rul_minutes/ttf_total_min) - 1) / (exp(k) - 1)` equals the normalized distance from `y_start` to `y_crit`.

---

## Feature: sendAgentMessage() SSE Streaming

**Current state:** `sendAgentMessage()` calls `POST /api/agent/recommend` (blocking JSON response). `consultOperationsAgent()` already uses `POST /api/agent/recommend-stream` (SSE streaming, working).

**Problem:** The agent chat messages entered by the operator (after the initial recommendation) use the blocking endpoint and don't support streaming, and don't pass `chat_history` to the streaming endpoint.

**Fix in `app.py`:**
Add `chat_history: str = None` parameter to `get_agent_recommend_stream()`. Parse it with `json.loads(chat_history)` if present. Pass the parsed history into the LLM prompt (same as the blocking endpoint does).

**Fix in `index.html`:**
Replace `sendAgentMessage()`'s fetch of `/api/agent/recommend` with the same SSE streaming loop already used in `consultOperationsAgent()`. Key differences from `consultOperationsAgent()`:
- Pass `chat_history: JSON.stringify(_agentChatHistory.slice(-6))` in URLSearchParams
- On `type === 'recommendation'`: append to chat log (same as now)
- On `type === 'token'`: stream tokens into a teal-bordered streaming bubble (same pattern as `consultOperationsAgent()`)
- On `type === 'done'`: push full streamed content to `_agentChatHistory`, re-enable send button

---

## Feature: Retrain Phase 5 XGBoost Models with Phase 7.1 Slider Data

**Background:** The current models (`model_pump.json`, `model_esp.json`, `model_transformer.json`) are trained on synthetic health scores that follow a purely deterministic `1.0 - t_frac` curve. Phase 7.1 introduced the intervention slider which means operators can see and adjust perceived health. The models should be retrained to reflect that the health score progression can be modified by operator actions (intervention at a given health level).

**What "slider data" means for training:** The training sequences should include examples where the health score is artificially held higher for some steps (simulating a partial recovery / intervention) then resumes degradation. This makes the model more robust to non-monotonic health score trajectories in real deployments.

**Script:** `gdc-pm/scripts/retrain_edge_models.py`

**Change needed in `generate_sequence()`:**
With probability `p_intervention = 0.15`, after the sequence reaches a random health score between 0.3 and 0.7, insert a "partial intervention" plateau (health held constant for 5–15 steps with small noise) then resume degradation from that health level. This does NOT change the physics — it adds training diversity so the model doesn't assume strictly monotonic descent.

After retraining, replace the `.json` model files and rebuild/redeploy the Docker image.

---

## Deployment Checklist for Next Session

1. Make all code changes above in `index.html` and `app.py`
2. Run a quick sanity check: `grep -n "_wsCurrentHealth" gdc-pm/gke/fault-trigger-ui/index.html` (should appear in poller, tier badge display, and showWorkspace)
3. Build: `docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gdc-pm/gke/fault-trigger-ui/`
4. Push: `docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
5. Rollout: `kubectl rollout restart deployment/fault-trigger-ui -n default`
6. Wait: `kubectl rollout status deployment/fault-trigger-ui -n default`
7. Verify at http://35.188.3.97:
   - Reset → no Intervening line, no tier badge
   - Inject gas-lock → "Intake Pres." tab selected as primary
   - SCADA alarm marker aligns with dotted curve crossing threshold
   - Tier badge shows EARLY initially, transitions naturally as health degrades (not driven by slider position)
   - Drag slider left/right → Intervening marker moves, tier badge does NOT change
   - Agent chat messages stream character-by-character
8. Create `docs/PHASE_10_DEPLOYMENT_STATUS.md` with the new image digest

---

## Files Changed Summary
| File | Changes |
|------|---------|
| `gke/fault-trigger-ui/index.html` | Add `_wsCurrentHealth`, decouple tier from slider, fix reset clear, fix poller guard, update gas_lock in FAULT_PHYSICS_JS, refactor sendAgentMessage to SSE |
| `gke/fault-trigger-ui/app.py` | Fix gas_lock FAULT_PHYSICS primary/scada sensor, fix alarm curve alignment, add chat_history to recommend-stream |
| `scripts/retrain_edge_models.py` | Add partial-intervention plateau to generate_sequence(), retrain models |
