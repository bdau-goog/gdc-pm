# Next Session Starting Prompt
## Copy and paste this entire block as the task to start the next session

---

Move to `~/gdc-pm`. Initialize as an expert in GCP, BigQuery, AI/ML, Vertex AI, GDC (Google Distributed Cloud), and Kubernetes/GKE.

Also initialize as an expert in industrial edge computing, oil and gas upstream drilling, production, operations, equipment and equipment maintenance. You are an expert in machine monitoring and telemetry, predictive maintenance, and machine learning systems used to predict imminent equipment failures.

You are deeply familiar with MLOps, training-serving skew, model drift, retraining pipelines, and the architectural differences between cloud-based and edge-based inference for time-sensitive industrial applications.

---

## Project State

This is a GKE-based predictive maintenance demo (`gdc-pm`) running on GKE Autopilot cluster `gdc-edge-simulation` in project `gdc-pm-v2`. The UI is live at **http://35.188.3.97**.

**Read `docs/PHASE_3_PLAN.md` first.** It contains the complete Phase 3 implementation plan including:
- What Phase 2 built (currently live)
- The root cause of RUL instability (training-serving skew)
- All 7 Phase 3 tasks with precise implementation details
- The complete demo script
- Key engineering decisions made in the planning session

**Critical context you must understand before writing any code:**
1. The current live `fault-trigger-ui` pod is using a **TEMPORARY** geometric RUL calculation (pure physics, no ML model). This was a stopgap. It must be replaced with the XGBoost model using the clean feature extraction approach described in Task 1 of PHASE_3_PLAN.md.
2. The XGBoost RUL models in GCS are V1 — trained on clean 5-minute synthetic data. They will still be noisy at first because of training-serving skew. This is **intentional** — it sets up the MLOps retraining demo in Task 3.
3. Do NOT attempt to stabilize the RUL by reverting to geometry. The instability is the demo's opening act.

**Also read:**
- `docs/PHASE_2_DEPLOYMENT_STATUS.md` — Phase 2 architecture reference
- `gke/fault-trigger-ui/app.py` — current backend (especially `plot_forecast()` and `_run_degrade_thread()`)
- `gke/fault-trigger-ui/index.html` — current frontend

---

## What to Implement This Session (Phase 3)

Work through `docs/PHASE_3_PLAN.md` tasks in order:

1. **Task 1:** Restore XGBoost RUL model with fault-only clean feature extraction (`app.py`)
2. **Task 7:** Add fault onset time tracking to `active_degrades` (needed by Tasks 4 and 5)
3. **Task 2:** Write `scripts/retrain_edge_models.py` — generate V2 training data, train models, upload to GCS
4. **Task 3:** MLOps "Drift & Retrain" UI flow — button + toast sequence + model swap endpoints
5. **Task 4:** Upgrade Edge vs Cloud chart — vertical lines for PNR and Cloud Detection, horizontal Time to React arrows
6. **Task 5:** PNR Exceeded / Asset Failed states in chart and incident panel
7. **Task 6:** RUL-tiered resolution actions in dispatch modal

After each task, rebuild and push the `fault-trigger-ui` image:
```bash
cd /home/brian/gdc-pm
REG="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build --quiet -t "${REG}/fault-trigger-ui:latest" gke/fault-trigger-ui/ && \
  docker push --quiet "${REG}/fault-trigger-ui:latest" && \
  kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```

Wait for instructions before proceeding.
