# Next Session Prompt — ESP v2 Redesign (Sprint 5: Digital Twin Polish & Activity Stream)

## Header
**Date:** May 21, 2026
**Live URL:** http://gdc-pm.bdau.io
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation
**Namespace:** gdc-pm
**Current Image Tag:** latest (Sprint 4, commit 617c611)
✅ Working tree clean.

## What Was Done This Session

### Sprint 3 (Committed)
- **SCADA Blind Spot Watermark**: Orange-shaded SCADA BLIND SPOT annotation on the future timeframe of the SCADA chart.
- **Base vs Adjusted RUL**: Deep-dive header now shows both Base RUL and AI Fusion-adjusted RUL side-by-side.
- **SCADA Chart X-axis sync**: SCADA chart X-axis locked to match GDC AI forecast chart.

### Sprint 4 — Pad Alpha 2D Digital Twin Mockups (Completed)
Three selectable digital twin background variations added to the Pad Alpha zone on the main dashboard landing page. Toggle with the **V1 · SVG / V2 · API / V3 · Grid** pill buttons:

1. **V1 · SVG (Inline Schematic)**: Pure HTML/CSS inline SVG. Pad boundary, 6 ESP well circles (A-1 through A-6) connected to a production header/manifold, GDC Edge AI box (top-center, blue tinted), SCADA RTU (top-right), Generator (top-left), Starlink dish (far-right). Dashed data/power connecting lines. SMIL animation on the GDC LED status dot. Legend. "Pad Alpha · 2D Schematic · V1" watermark.

2. **V2 · API (Dynamic SVG from `/api/pad-mockup`)**: GET endpoint in FastAPI serving a dynamically-generated SVG. Blueprint-style, dark navy + cyan palette (vs V1's dark blue-gray). Live well health colours derived from `active_degrades` (teal=healthy, amber=warning, red=critical). Well depth annotations. SVG linear gradients on GDC box. Separator box at manifold end. Engineering title block (bottom-right, standard drawing format). Served with `image/svg+xml` and `no-cache`.

3. **V3 · Grid (CSS Grid with Live Vue Nodes)**: Infrastructure row (Generator, GDC Edge AI, SCADA RTU, Starlink) as styled HTML boxes connected by dashed CSS borders, over a subtle repeating-linear-gradient dot grid background. The 6 ESP Vue asset nodes (fully interactive) are arranged in a spatial row below with health-state colour coding. GDC box has a live-blinking blue LED dot (blink keyframe).

- **`scripts/gen_pad_mockup.py`**: Standalone matplotlib-based PNG generator. Run `pip install matplotlib numpy && python scripts/gen_pad_mockup.py` to produce `gke/fault-trigger-ui/static/pad_alpha_mockup.png`.
- **Bug fix**: Duplicate `const rul` JS SyntaxError in `fetchRemediationTiers` resolved.

## Current Cluster State
- `alloydb-omni` (1/1): Running stable.
- `event-processor` (1/1): Running.
- `fault-trigger-ui` (1/1): Running. Serves Sprint 4 digital twin mockup UI. `GET /api/pad-mockup` → HTTP 200.
- `inference-api` (1/1): Running.
- `grafana` (1/1): Running.
- `telemetry-simulator` (1/1): Running.
- `ollama` (0/1): Pending GPU node provisioning (Autopilot scaling).

## Outstanding Development Items (To-Do)

**High Priority**
1. **Sprint 5 — Digital Twin Polish**: Now that we have 3 working mockup variations, evaluate and pick the strongest one for a production-quality polish pass:
   - Consider making the SVG wells in V1 **dynamically reflect health state** (bind `stroke` colour to `getAssetHealthClass(assetId)` directly in the SVG, matching the Vue node colours).
   - For V3, add a subtle horizontal "pipeline" line connecting the infra icons to each other.
   - Optionally add a **V4 variant** that renders the SVG *behind* the asset nodes as a spatial background layer (absolute positioning overlay).

2. **Activity Stream**: The right-side Activity Stream panel is currently empty (no data feeds from the fleet canvas). Wire it to surface real-time events from the `active_degrades` map — each new fault injection or health state change should push an entry.

3. **Ollama / Gemma4 GPU node**: The `ollama` pod is still pending GPU node provisioning. Once the Autopilot L4 node provisions, pull `gemma4:27b` and verify the chatbot responses are streaming correctly.

4. **Standalone PNG deployment**: To serve the `gen_pad_mockup.py` output via the V2 endpoint as a true PNG (vs the dynamic SVG), update the Dockerfile to:
   ```
   COPY static/ ./static/
   ```
   and update `app.py` to mount `StaticFiles` and redirect `/api/pad-mockup` to the static PNG. Then run `gen_pad_mockup.py` as part of the build.

## Constraints
- `terraform/gke.tf` must NOT be applied — it would destroy the live cluster.
- All demo UI changes go into `gke/fault-trigger-ui/index.html` and logic into `gke/fault-trigger-ui/app.py`.
- Preserve the existing XGBoost health score models (`*.ubj` files).
- The existing `/api/*` endpoints must remain backward-compatible unless explicitly agreed to break them.
- Do NOT commit to `main`.
- O&G scenarios and physics must remain authentic.
- **Note: The SSH remote does not have a browser**, so the `browser_action` tool should not be used for visual verification.

## Rebuild & Deploy Commands
```bash
# General Docker Build & Push (example for UI)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest

# Restart Deployments
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout restart deployment/event-processor -n gdc-pm
kubectl rollout restart deployment/inference-api -n gdc-pm
```

## Key Lessons Learned
- When emphasizing predictive AI value in the UI, highlighting what legacy systems *cannot* see (e.g., the "SCADA Blind Spot") is often more impactful than just showing what the AI *can* see.
- Careful attention must be paid to Plotly chart axis synchronization and layout manipulation to ensure annotations and shapes render correctly across dynamic data updates.
- SVG inside Vue templates works cleanly as inline HTML — SMIL `<animate>` elements are fully supported by modern browsers and work in the Vue template compiler without special handling.
- FastAPI can serve dynamically-generated SVG responses with `image/svg+xml` content type, making `<img src="...">` tags render the server-generated SVG directly without any JavaScript.
- For dark-theme UI mockups, using two distinct colour palettes for different mockup variations (e.g., V1: blue-gray; V2: navy/cyan) makes each variation clearly differentiated during demos.
