# GDC-PM Phase 7 — Deployment Status

**Completed:** 2026-05-13
**Live URL:** http://35.188.3.97
**Grafana:** http://136.115.220.48
**GKE Cluster:** `gdc-edge-simulation` — `gdc-pm-v2` — `us-central1`

---

## Images Deployed

| Service | Image | Digest |
|---|---|---|
| `fault-trigger-ui` | `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest` | `sha256:9dabc2f2ca204bfe2de6799a0460e63cc679bbcd45f354904bcd276bba737635` |
| `telemetry-simulator` | `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/telemetry-simulator:latest` | `sha256:96347e4be505bca29763fd1e69ad2d448912f223b6fdcad3a423274e8cb1a525` |

---

## What Was Fixed and Built

### Bug Fixes (Phase 7.0)

#### BUG 1: Pad Charlie Phantom Events — `simulator.py`
- **Root cause:** `ASSET_REGISTRY` in `gke/telemetry-simulator/simulator.py` still contained `ESP-CHARLIE-1` through `ESP-CHARLIE-6` (6 assets) after the site was removed from the UI.
- **Fix:** Removed all 6 Pad Charlie entries. Fleet is now 14 assets: Pad Alpha (6 ESPs), Pad Bravo (4 Gas Lift), Rig 42 (4).
- **Also fixed:** Stale docstring, log line, and `ASSET_FLEET` comment.

#### BUG 2: Duplicate `injectFault()` — `index.html`
- **Root cause:** Two `async function injectFault()` declarations in the same script scope. The second (at end of file) overwrote the first but both were dead code in the original sense. The second had auto-open workspace logic; the first did not.
- **Fix:** Replaced the first (dead) definition with a comment. The second definition remains as the single canonical implementation.

#### BUG 3: Duplicate `updateIncidents()` — `index.html`
- **Root cause:** First (simplified) definition at line 1310 was overridden by second (full, with FAILED badges) definition at line 2181.
- **Fix:** Replaced first definition with a comment stub.

#### BUG 4: `_currentForecastData` not cleared on asset switch — `index.html`
- **Root cause:** When switching assets, the cached forecast from the previous asset remained in `_currentForecastData` and was briefly rendered on the new asset before the fetch completed.
- **Fix:** Added `_currentForecastData = null` at the end of `selectAsset()` before `refreshPlot()`.

#### BUG 5: `/api/model/version` endpoint missing — `app.py`
- **Root cause:** The MLOps retrain demo button in `index.html` called `POST /api/model/version` which did not exist in `app.py`. Every retrain demo would fail silently with a 404.
- **Fix:** Added `POST /api/model/version` endpoint. Accepts `{"version": "v1"|"v2"}`, clears `HEALTH_HISTORY` (the EWA smoothing buffer), returns status message.

---

### Phase 7.1 — Intervention Slider: Time-Based Units

**Files changed:** `gke/fault-trigger-ui/index.html`

The slider previously showed Health % (0–100). It now moves in physical time units (minutes, matching the fault's `horizon_label`).

**Changes:**
- Added `_wsTTFMinutes`, `_wsHorizonLabel`, `_wsDegradePoller` state variables
- Added `fmtSliderVal(minutes, hlabel)` helper to format minutes as "15 min", "3h 30m", "2.4 days"
- Added `_startDegradePoller(assetId)` — polls `/api/degrade-status/{asset_id}` every 5s:
  - Updates `slider.max = Math.ceil(ttf_minutes)` (shrinks as fault progresses)
  - Animates `slider.value` leftward when `!_sliderUserHeld`
  - Updates `_wsSliderHealth` from `d.health_score`
- Updated `showWorkspace()`:
  - Sets `slider.min=0, slider.max=initTTF, slider.value=0.75*initTTF`
  - Calls `_startDegradePoller(assetId)`
- Updated `hideWorkspace()` to `clearInterval(_wsDegradePoller)`
- Updated `onSliderInput(rawVal)` to convert minutes → health score via `rawVal / _wsTTFMinutes`
- Updated `updateWorkspace()` to show `"Intervening in X [units]"` instead of `"Health X%"` in `calc-intervene-at`
- Updated `refreshPlot()` auto-follow to NOT set `sliderEl.value` (poller owns that now — just updates `_wsSliderHealth`)

---

### Phase 7.2 — Plotly Resize on Workspace Toggle

**Files changed:** `gke/fault-trigger-ui/index.html`

Added `Plotly.relayout(chartDiv, {autosize: true})` in:
- `showWorkspace()` — 100ms after `ops-workspace` becomes visible
- `hideWorkspace()` — 100ms after `ops-workspace` is hidden

This ensures the chart correctly fills the new available height when the workspace panel opens/closes.

---

### Phase 7.4 — Ollama Model Warm-Up

**Files changed:** `gke/fault-trigger-ui/app.py`

Added `_ollama_keepalive()` background thread:
- Starts 15s after container init (avoids startup race)
- Sends a minimal `{"prompt": "ping", "num_predict": 1}` to Ollama every 5 minutes
- Runs as daemon thread — does not block FastAPI startup
- Prevents `gemma3:12b` from cold-starting on GKE after 10+ minutes of idle

---

### Hard Reset Script

**New file:** `scripts/hard_reset_db.sh`

Truncates `telemetry_events` and resets the ID sequence. Run with:
```bash
bash scripts/hard_reset_db.sh              # prompts for RESET
bash scripts/hard_reset_db.sh --confirm    # skips prompt
```

Database was reset on 2026-05-13 to purge Pad Charlie events.

---

## Database State

- **AlloyDB `telemetry_events`:** TRUNCATED — 0 rows, ID sequence reset to 1.
- Pad Charlie events have been cleared.
- Fresh telemetry started flowing immediately after reset.

---

## Current Fleet (14 assets, 3 sites)

| Site | Assets | Fault Types |
|---|---|---|
| Pad Alpha | ESP-ALPHA-1 … 6 (ESP) | gas_lock, sand_ingress, motor_overheat |
| Pad Bravo | GLIFT-BRAVO-1 … 4 (Gas Lift) | valve_failure, thermal_runaway, bearing_wear |
| Rig 42 | MUD-RIG42-1,2,3 + TOPDRIVE-RIG42-1 | pulsation_dampener_failure, valve_washout, piston_seal_wear, gearbox_bearing_spalling, hydraulic_leak |

---

## Known Gaps (Deferred to Phase 8)

| # | Description | Status |
|---|---|---|
| 8.1 | `sendAgentMessage()` SSE streaming | Backend SSE endpoint needs `message` + `chat_history` params |
| 8.2 | Phase 5 XGBoost model retrain with Phase 7.1 slider data | Model still trained on health-% ground truth |

---

## Key Files Changed This Phase

| File | Changes |
|---|---|
| `gke/telemetry-simulator/simulator.py` | Removed Pad Charlie (6 assets), updated docstring/log/comment |
| `gke/fault-trigger-ui/app.py` | Added `/api/model/version`, added `_ollama_keepalive` thread |
| `gke/fault-trigger-ui/index.html` | Phase 7.0 bug fixes, Phase 7.1 time slider, Phase 7.2 Plotly resize |
| `scripts/hard_reset_db.sh` | New: DB hard reset script |
| `docs/PHASE_7_DEPLOYMENT_STATUS.md` | This file |
