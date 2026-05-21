# Next Session Prompt — ESP v2 Redesign (Sprint 2 Continuation & Sprint 3)

## Header
**Date:** May 21, 2026
**Live URL:** http://gdc-pm.bdau.io
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation
**Namespace:** gdc-pm
**Current Image Tag:** latest
**⚠ Uncommitted changes in working directory.**

## What Was Done This Session
- **ESP Classifier Upgraded**: Retrained the XGBoost classifier for ESP assets to use 8 features (`psi`, `temp_f`, `vibration`, `motor_amps`, plus their rolling slopes).
- **Event Processor History Buffer**: Implemented a 60-reading rolling window buffer in `gke/event-processor/processor.py` to calculate per-minute rate-of-change features for ESP assets.
- **Inference API Updated**: Modified `gke/inference-api/app.py` to expect and route 8 features to the `esp_classifier`.
- **Models Deployed**: Generated new `esp_classifier.bst`, uploaded to GCS, and successfully restarted backend deployments. End-to-end verified via API.
- **Sprint 2 — Main Page UI Redesign (Partially Complete)**:
  - Cleaned up legacy CSS styles.
  - Implemented dynamic **green/amber/red health indicators** for all asset nodes based on the backend ML `health_score`.
  - Added **right-click context menus** (`@contextmenu.prevent`) to the asset nodes to seamlessly trigger the fault-injection menu.
  - Implemented a **high-level alert banner** that appears whenever `horizonAlerts.length > 0`.
  - Added an Ingress routing `gdc-pm.bdau.io` to the `fault-trigger-ui` Service.

## Current Cluster State
- `alloydb-omni` (1/1): Running stable.
- `event-processor` (1/1): Running, computes 60-window slopes and routes 8 features to inference API.
- `fault-trigger-ui` (1/1): Running behind `gdc-pm.bdau.io` ingress. Serves updated Pad overview UI with live health indicators and context menus.
- `inference-api` (1/1): Running, loaded all 7 models including new 8-feature `esp_classifier`.
- `grafana` (1/1): Running.
- `telemetry-simulator` (1/1): Running.
- `ollama` (0/1): Pending GPU node provisioning (Autopilot scaling). Will serve `gemma` for RAG responses once up.

## Outstanding Development Items (To-Do)

**High Priority**
1. **Commit pending changes** in the `esp-v2-redesign` branch (`gke/event-processor/processor.py`, `gke/inference-api/app.py`, `gke/fault-trigger-ui/index.html`, etc.).
2. **Sprint 2 — Finishing Touches:** The UI currently still shows Pad Bravo, Rig 42, and the Field Intelligence stream (leftovers from the v1 demo). Strip these out so the UI exclusively focuses on ESPs / Pad Alpha. Also, ensure the field intelligence stream is fully removed from the main dashboard to clean up markdown rendering issues.

**Medium Priority**
3. **Sprint 3 — Detail Page UI Redesign:** Implement the remaining frontend components for the deep dive view:
   - Base RUL vs Adjusted RUL panels.
   - Document feed (expandable cards).
   - SCADA comparison chart (fix X-Axis sync bug).
   - Gemma assessment panel & Operator Chatbot interface.
   - Remediation Actions.

## Constraints
- `terraform/gke.tf` must NOT be applied — it would destroy the live cluster.
- All demo UI changes go into `gke/fault-trigger-ui/index.html` and logic into `gke/fault-trigger-ui/app.py`.
- Preserve the existing XGBoost health score models (`*.ubj` files).
- The existing `/api/*` endpoints must remain backward-compatible unless explicitly agreed to break them.
- Do NOT commit to `main`.
- O&G scenarios and physics must remain authentic.

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
- `inference-api` dynamically pulls models from GCS. When updating model shapes (e.g. from 3 to 8 features), the `.bst` file must be successfully uploaded to the exact GCS path `inference-api` uses (`gs://gdc-pm-v2-models/esp_classifier/latest/model.bst`) before restarting the pod, otherwise feature mismatch errors will crash the pod on predict.
- The Python slim container doesn't have `curl`, so `kubectl port-forward` from the host is required for API tests.
- Vue `@click.stop` maps to left click, while `@contextmenu.prevent` properly maps to right-click for implementing context menus natively without third-party plugins.