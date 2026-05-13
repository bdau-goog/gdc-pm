# GDC-PM Phase 8 — Deployment Status

**Completed:** 2026-05-13
**Live URL:** http://35.188.3.97
**Grafana:** http://136.115.220.48
**GKE Cluster:** `gdc-edge-simulation` — `gdc-pm-v2` — `us-central1`

---

## Images Deployed

| Service | Image | Digest |
|---|---|---|
| `fault-trigger-ui` | `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest` | `sha256:d487b32bde1cfb44cc5e28e1b5588a8d932acd26fe30766ef43204a7f0d705ab` |

---

## What Was Fixed and Built

### Bug Fix: ML Confidence Cone Restored — `app.py`

**Root cause:** In Phase 6.3, the forecast rendering was migrated from the full Plotly HTML iframe endpoint (`/api/plot/forecast`) to a lightweight JSON endpoint (`/api/plot/forecast-data/`) that the frontend renders inline via `Plotly.react()`. The confidence cone (uncertainty band) was present in the old iframe endpoint but was **accidentally omitted** from the new `_build_sensor()` function in `get_forecast_data()`.

**Fix:** Ported the cone logic into `_build_sensor()` inside `get_forecast_data()`:
- Computes `_proj_range` = absolute difference between the last projected value and the start value
- Expands a noise band from 4% → 18% of the projected range across the forecast horizon
- Appends a `fill: "toself"` polygon scatter trace (Confidence Band) matching the same color as the ML RUL projection (orange if degrading, green if nominal)
- Matches the exact Phase 5 Plotly iframe cone logic

### Feature: Ops Workspace Panel Adjuster — `index.html`

**Problem:** When the Operations Workspace opened in full-screen width scenarios, the "Consult Operations Agent" button was hidden below the viewport with no way to scroll or resize.

**Fix:** Added a draggable resize handle `#ops-resize-handle` between the intervention slider and the Operations Workspace:

**CSS:** New `#ops-resize-handle` style block — 7px tall, `ns-resize` cursor, blue highlight on hover/drag, dot indicator glyph via `::before`. Hidden by default, shown only when workspace is visible.

**HTML:** New `<div id="ops-resize-handle">` inserted between `#intervention-slider-wrap` and `#ops-workspace` in the DOM.

**JS — `showWorkspace()` / `hideWorkspace()`:** Handle element gets `.visible` class added/removed alongside the workspace element.

**JS — `initOpsResizeHandle()` IIFE:** Self-initialising function that attaches mousedown/mousemove/mouseup handlers:
- `mousedown`: captures `clientY` and current `ws.offsetHeight`
- `mousemove`: computes `delta = startY - clientY` (drag up = positive = expand), clamps height to 100px–560px
- `mouseup`: clears drag state, triggers `Plotly.relayout({autosize: true})` so the chart cleanly fills the newly available space

---

## Known Gaps (Deferred to Phase 9)

| # | Description | Status |
|---|---|---|
| 9.1 | `sendAgentMessage()` SSE streaming | Backend SSE endpoint needs `message` + `chat_history` params |
| 9.2 | Phase 5 XGBoost model retrain with Phase 7.1 slider data | Model still trained on health-% ground truth |

---

## Key Files Changed This Phase

| File | Changes |
|---|---|
| `gke/fault-trigger-ui/app.py` | Restored confidence cone in `get_forecast_data()._build_sensor()` |
| `gke/fault-trigger-ui/index.html` | Added `#ops-resize-handle` CSS, HTML div, showWorkspace/hideWorkspace updates, drag IIFE |
| `docs/PHASE_8_DEPLOYMENT_STATUS.md` | This file |
