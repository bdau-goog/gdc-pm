# Next Session Prompt — ESP v2 Redesign (Sprint 5 v2: Digital Twin Refinement Continued)

## Header
**Date:** May 21, 2026
**Live URL:** http://gdc-pm.bdau.io
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation
**Namespace:** gdc-pm
**Current Image Tag:** latest (Sprint 5 v1, commit c8c0b54)
✅ Working tree clean.

## What Was Done This Session

### Sprint 5 v1 (committed `c8c0b54`)
**Replaced the SVG + HTML overlay Digital Twin diagram with a pure CSS Flexbox layout.**

Key architectural changes:

1. **Landing Page Digital Twin — CSS Flexbox (replaces SVG overlay)**
   - The old `<div class="pad-svg-bg">` SVG + `.pad-well-overlay` absolute positioning approach has been **fully removed**.
   - Replaced with a `.twin-diagram` container using a tiered Flexbox layout:
     - **Tier 1 (Top Row)**: External Left (Generator + A/C) | Site Structure (Broker + GDC AI + SCADA + Network Bar) | External Right (Starlink)
     - The "site structure" has a **dashed light-grey border** (`#5a6a7a`) indicating the wellsite equipment boundary
     - Generator, A/C, and Starlink sit **outside** the structure boundary (by design — not connected to the data network)
     - Edge Broker, GDC Edge AI, and SCADA RTU sit **inside** the structure
     - A shared **Network Segment Bar** at the bottom of the structure represents the Pub/Sub data bus
     - **Tier 2**: Network lines (blue/grey) from network bar down to wells — uses `v-for="n in 6"` loops
     - **Tier 3**: 6 ESP well nodes — **larger (72×72px), fully opaque** with **A-1 through A-6 labels** below
     - **Tier 4**: Google Blue (`#8ab4f8`) gas/fluid lines from wells down to pipeline
     - **Tier 5**: Production manifold pipeline with separator arrow
   - Includes a legend strip with clear color coding
   - The currently selected asset (after Deep Dive navigation) gets a `selected` highlight class
   - All right-click (fault injection) and left-click (deep dive) interactions preserved

2. **Deep Dive Header — RUL Terminology Updated**
   - "Base RUL" → **"Initial RUL"** (time_to_scada_minutes badge)
   - "Adjusted RUL (AI Fusion)" → **"AI Informed RUL"** (adjusted_rul_minutes badge)

3. **Evidence Panel — RAG Context Label Updated**
   - "Live Intelligence Feed" renamed to **"📄 RAG Context Documents"**
   - This accurately describes what these items are: dynamically generated enterprise documents (lab reports, shift notes, PM records, VFD logs) that are inserted into ChromaDB and used as RAG context for the Gemma4 LLM and for the `adjust_rul_with_documents()` multiplier
   - The "All ▾" drill-down modal still works; modal title still reads "All Intelligence Feed Items"

## Current Cluster State
- `alloydb-omni` (1/1): Running stable.
- `event-processor` (1/1): Running.
- `fault-trigger-ui` (1/1): Running — Sprint 5 v1 flexbox twin. HTTP 200 ✅
- `inference-api` (1/1): Running.
- `grafana` (1/1): Running.
- `telemetry-simulator` (1/1): Running.
- `ollama` (0/1): Pending GPU node provisioning (Autopilot scaling).

## Design Decisions Made This Session (Source of Truth)

### Digital Twin Architecture
- **DO use pure CSS Flexbox**, NOT SVG + HTML overlay. The overlay approach had line-through and alignment issues.
- The `.twin-diagram` class and all `.twin-*` CSS classes are the canonical implementation.
- The tiered structure (top-row → network-lines → wells → gas-lines → pipeline) is the agreed layout.
- Wells are **always at the bottom**, **large (72×72px)**, **fully opaque** with individual health colour fills.
- **No Activity Stream on the landing page** — this was explicitly agreed and removed from scope.

### Terminology
- **"Initial RUL"** = `time_to_scada_minutes` (the base XGBoost RUL before document fusion)
- **"AI Informed RUL"** = `adjusted_rul_minutes` (after `adjust_rul_with_documents()` multiplier applied)
- **"RAG Context Documents"** = the dynamically generated enterprise documents (lab reports, shift notes, PM records, VFD logs) that feed ChromaDB and inform both the LLM and the RUL adjustment

### Data Flow Architecture (Immutable Demo Talking Point)
- GDC Edge AI does **NOT** receive data from SCADA
- Both GDC Edge AI and SCADA RTU **independently subscribe** to the same Pub/Sub topics on the Edge Broker (RabbitMQ/MQTT)
- This is why GDC catches sub-threshold faults SCADA misses — it reads the raw sensor stream, not a filtered SCADA feed

## Outstanding Development Items (To-Do)

**High Priority — Sprint 5 Continued**

1. **Digital Twin Layout Refinement** (visual alignment, spacing still needs review):
   - The network lines (Tier 2) spacers (`width:80px` left, `width:56px` right) may need tuning if the external left/right panels change width
   - The network lines should line up approximately with the wells below them
   - May want to add subtle visual connection from equipment boxes (Broker, GDC, SCADA) down to the network bar
   - Consider adding a very subtle horizontal line from each equipment box to the network bar to show the "subscription" relationship (currently implied by the shared bus)

2. **RAG Context Documents — improve drill-down modal title** (minor):
   - The "All Intelligence Feed Items" modal title should be updated to "All RAG Context Documents"
   - The "Ingesting unstructured data sources…" placeholder text is fine as-is

3. **Ollama / Gemma4 GPU node**: `ollama` pod still pending L4 GPU provisioning.

4. **Health state binding to well colours** (✅ already implemented via `getAssetHealthClass()`):
   - Green/Amber/Red health states are correctly applied to well nodes via `.twin-wells-row .health-*` CSS

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
- SVG inline + absolute HTML overlay (the Sprint 4 approach) is NOT suitable for resizable interactive diagrams.
- **Pure CSS Flexbox tiered layout** (`twin-*` classes) is the correct solution. It scales naturally with the browser window and never has line-through issues.
- For the well nodes: `background` on `.twin-wells-row .health-green` etc. must use `!important` to override the global `.health-green` which only has a semi-transparent background.
- **GDC data flow architecture**: GDC does NOT receive data from SCADA — both independently subscribe to the same edge Pub/Sub bus (RabbitMQ). Critical demo talking point.
- The `adjust_rul_with_documents()` function in `app.py` uses regex to extract variables from dynamically generated documents and applies RUL multipliers. The UI now correctly labels this as "AI Informed RUL".
- RAG context documents are generated by `generate_dynamic_documents()` and pushed to ChromaDB. The UI's "📄 RAG Context Documents" section surfaces these for demo transparency.
