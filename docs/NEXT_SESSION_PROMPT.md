# Next Session Prompt — ESP v2 Redesign (Sprint 4: Landing Zone Mockups)

## Header
**Date:** May 21, 2026
**Live URL:** http://gdc-pm.bdau.io
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation
**Namespace:** gdc-pm
**Current Image Tag:** latest
⚠ Uncommitted changes in working directory.

## What Was Done This Session
- **Stripped Legacy Assets**: Completely removed Pad Bravo, Rig 42, and associated faults from both `index.html` and `app.py`. The UI now focuses exclusively on Pad Alpha and its ESPs.
- **Dashboard Clean-up**: Removed the Field Intelligence stream from the main dashboard to fix markdown rendering issues and declutter the landing page.
- **Sprint 3 — Detail Page UI Redesign (Completed)**:
  - **SCADA Comparison Chart**: Synced the X-axis of the traditional SCADA chart with the GDC AI forecast chart. Added a prominent orange-shaded **"SCADA BLIND SPOT"** watermark to the empty future timeframe on the SCADA chart to visually emphasize the AI's predictive lead time.
  - **Base vs. Adjusted RUL Panels**: The detail page header now dynamically displays both the Base RUL and the AI Fusion-adjusted RUL side-by-side, highlighting the difference in red.
  - Verified the Document Feed, Chatbot interface, and Remediation Actions components are fully functional and styled correctly.
- **Deployment**: Rebuilt the `fault-trigger-ui` Docker image and restarted the deployments.

## Current Cluster State
- `alloydb-omni` (1/1): Running stable.
- `event-processor` (1/1): Running.
- `fault-trigger-ui` (1/1): Running behind `gdc-pm.bdau.io` ingress. Serves updated Pad Alpha exclusive UI with SCADA Blind Spot visualizations.
- `inference-api` (1/1): Running.
- `grafana` (1/1): Running.
- `telemetry-simulator` (1/1): Running.
- `ollama` (0/1): Pending GPU node provisioning (Autopilot scaling). Will serve `gemma` for RAG responses once up.

## Outstanding Development Items (To-Do)

**High Priority**
1. **Commit pending changes** in the `esp-v2-redesign` branch (specifically the `index.html` changes for the SCADA blind spot).
2. **Sprint 4 — Pad Alpha 2D Landing Zone Mockups**: The main dashboard landing page is currently empty after removing the Field Intelligence stream. We need to create mockups for a subtle 2D diagram of a drilling pad (Pad Alpha) to serve as a "digital twin" background. 
   - **Plan**: Create 3 different mockup variations of this digital twin background:
     1. An SVG/Canvas layout using CSS shapes directly in Vue/HTML.
     2. A custom script to generate a static PNG mockup.
     3. A stylized CSS grid background with Vue asset nodes positioned dynamically over it.
   - **Elements to include**: ESP wells (in a realistic line/arrangement), a SCADA hut, GDC equipment (in a distinct color), power generator, starlink uplink, and light gray connecting lines. 
   - **Style**: Subtle, light gray lines/background, non-AI-generated 2D mockup style.

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