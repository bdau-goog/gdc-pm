# Next Session Prompt — ESP v2 Redesign (Sprint 5: Digital Twin Diagram Refinement)

## Header
**Date:** May 21, 2026
**Live URL:** http://gdc-pm.bdau.io
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation
**Namespace:** gdc-pm
**Current Image Tag:** latest (Sprint 4 v2, commit de7667a)
✅ Working tree clean.

## What Was Done This Session

### Sprint 3 (Committed earlier)
- SCADA Blind Spot watermark, Base vs Adjusted RUL header panels, SCADA chart X-axis sync.

### Sprint 4 v1 — Three Mockup Variations (committed `617c611`)
Three selectable V1/V2/V3 digital twin variations + standalone `scripts/gen_pad_mockup.py`.

### Sprint 4 v2 — Integrated Interactive Diagram (committed `de7667a`)
Simplified to a single integrated diagram design. Key changes:

**Layout (top → bottom):**
1. **Equipment row** at top: GEN, A/C UNIT (both non-connected), EDGE BROKER (RabbitMQ/MQTT), GDC EDGE AI (blue accent, animated LED), SCADA RTU, STARLINK
2. **Shared Edge Network Bar** (horizontal Pub/Sub bus): all subscribing equipment + all 6 wells connect here with junction dots
3. **6 ESP wells** in the middle: Vue interactive nodes (right-click fault injection, left-click deep dive) overlaid directly on the SVG via `padWellStyle(idx)` absolute positioning
4. **Production Manifold** at the bottom: horizontal pipeline → separator, with wellbore stubs below

**Architectural accuracy encoded:**
- The Edge Broker publishes raw sensor telemetry
- GDC Edge AI and SCADA RTU both **independently subscribe** to the same Pub/Sub topics
- Neither is downstream of the other — this is why GDC catches sub-threshold faults SCADA misses

**Removed:** V2 API variant, V3 Grid variant, selector buttons, padMockupVar/padPngLoaded/padPngErr state.

## Current Cluster State
- `alloydb-omni` (1/1): Running stable.
- `event-processor` (1/1): Running.
- `fault-trigger-ui` (1/1): Running — serves Sprint 4 v2 integrated diagram. HTTP 200 ✅
- `inference-api` (1/1): Running.
- `grafana` (1/1): Running.
- `telemetry-simulator` (1/1): Running.
- `ollama` (0/1): Pending GPU node provisioning (Autopilot scaling).

## Outstanding Development Items (To-Do)

**High Priority — Sprint 5**
1. **Digital Twin Diagram Refinement** (main discussion next session):
   - Review the layout, spacing, and proportions of the current diagram
   - Consider adjustments to well node positioning, line routing, label placement
   - Possible: make the SVG wells dynamically reflect health state (bind stroke colour to Vue health data)
   - Possible: add well A-1 through A-6 labels below the interactive nodes in the diagram
   - Possible: show a subtle "currently selected/active" highlight on the well that matches the deep-dive tab

2. **Activity Stream**: The right-side Activity Stream panel is still empty. Wire it to surface real-time events from `active_degrades` — each fault injection or health state change should push an entry.

3. **Ollama / Gemma4 GPU node**: `ollama` pod still pending L4 GPU provisioning.

## Constraints
- `terraform/gke.tf` must NOT be applied.
- All demo UI changes go into `gke/fault-trigger-ui/index.html` and logic into `gke/fault-trigger-ui/app.py`.
- Preserve XGBoost health score models (`*.ubj` files).
- `/api/*` endpoints must remain backward-compatible.
- Do NOT commit to `main`.
- O&G scenarios and physics must remain authentic.
- **Note: The SSH remote does not have a browser** — `browser_action` tool should not be used.

## Rebuild & Deploy Commands
```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```

## Key Lessons Learned
- SCADA Blind Spot emphasis is more impactful than showing what AI *can* see.
- SVG inline in Vue templates works cleanly — SMIL `<animate>` is fully supported.
- Absolute-positioning Vue nodes over an SVG schematic (via `padWellStyle`) is the cleanest way to integrate live interactive components with a static technical diagram.
- **GDC data flow architecture**: GDC does NOT receive data from SCADA — both independently subscribe to the same edge Pub/Sub bus (RabbitMQ). This is a critical demo talking point: GDC gets the raw stream, not a filtered SCADA feed.
