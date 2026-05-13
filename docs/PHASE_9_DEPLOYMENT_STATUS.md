# Phase 9 Deployment Status

## Summary
Phase 9 addressed three UI bugs observed at http://35.188.3.97 (GKE Autopilot, `gdc-edge-simulation` / `gdc-pm-v2`).

## Docker Image
- **Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- **Digest:** `sha256:a552d5470fe8f5d41120f0cb505c251a9d3b384b231f2c05489c03d436bb3fab`

## Fixes Applied

### 1. Timezone Parsing Bug (`_renderForecastTab`)
- **Problem:** `nowISO` from Python's `datetime.isoformat()` lacked a `Z` suffix. JS treated it as local time, placing the "Intervening" green vertical line 5+ hours off.
- **Fix:** Appended `'Z'` in `_renderForecastTab()` before parsing: `new Date(nowISO + 'Z')`.

### 2. Intervention Slider Reset Bug (`_sliderManuallySet` flag)
- **Problem:** The 5s polling loop was overwriting the slider position after the operator dragged it.
- **Fix:** Added `_sliderManuallySet` boolean. Latches `true` on `mousedown`/`touchstart`, reset to `false` in `showWorkspace()`. Poller respects the flag.

### 3. Small Ops Workspace Plot
- **Problem:** The prediction plot was visually cramped.
- **Fix:** Increased Ops workspace height from `232px` to `300px`.

## Pending Items (Deferred to Phase 10)

### Bug Fixes Identified During Post-Deploy Testing
1. **Chart reset shows stale Intervening line and ML Detection data** — after a hard reset the Intervening marker and detection badge persist. Should be cleared when there is no active fault.
2. **Gas-lock SCADA alarm marker appears AFTER the predicted curve crosses the threshold** — `ttf_time` is being computed from `rul_minutes` (SCADA alarm health), but the marker renders right of where the dotted line crosses the dashed SCADA threshold.
3. **Gas-lock shows Motor Current as "major factor"** — the Motor Current tab is auto-selected because `primary_sensor: "amps"` in FAULT_PHYSICS. Should probably lead with Intake Pressure instead.
4. **Intervention tier badge does not update reactively with slider position** — `getTier()` uses `hs <= scada_alarm_health * 1.5` for "urgent" threshold. When the slider sits just left of the SCADA alarm line the badge reads "EARLY" instead of "URGENT". Moving the slider further left (SCADA: "Past alarm") flips to "CRITICAL", which is also wrong — "CRITICAL" should reflect the health score itself being near PNR, not the slider timestamp.
5. **After one minute the CRITICAL badge reverts to EARLY** — the poller overwrites `_wsSliderHealth` even when `_sliderManuallySet` is true if there is no active fault.

### Other Deferred Items
- `sendAgentMessage()` SSE streaming — currently calls `/api/agent/recommend` (blocking). Should be updated to use `/api/agent/recommend-stream` with `chat_history` support, mirroring the `consultOperationsAgent()` streaming loop already implemented.
- Retrain Phase 5 XGBoost models with Phase 7.1 slider interaction data.
