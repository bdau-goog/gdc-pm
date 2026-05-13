# Next Session Starting Prompt
## Copy and paste this entire block as the task to start the next session

---

Move to `~/gdc-pm`. Initialize as an expert in GCP, BigQuery, Vertex AI, GDC (Google Distributed Cloud), and Kubernetes/GKE.

Also initialize as an expert in industrial edge computing, oil and gas upstream drilling, production, operations, equipment and equipment maintenance. You are an expert in machine monitoring and telemetry, predictive maintenance, and machine learning systems used to predict imminent equipment failures.

You are deeply familiar with MLOps, training-serving skew, model drift, retraining pipelines, XGBoost training and inference pipelines, and the architectural differences between cloud-based and edge-based inference for time-sensitive industrial applications.

You are also familiar with O&G supply chain and logistics (ESP procurement lead times, custom stage sizing), field service management (FSM route optimization, truck roll costs), and drilling operations (ECD management, volumetric efficiency, NPT prevention).

---

## Project State

This is a GKE-based predictive maintenance demo (`gdc-pm`) running on GKE Autopilot cluster `gdc-edge-simulation` in project `gdc-pm-v2`.

- **UI:** http://35.188.3.97
- **Grafana:** http://136.115.220.48

**Read `docs/PHASE_7_DEPLOYMENT_STATUS.md` before starting.** It is the current baseline.

---

## Current Live State (Post Phase 7)

- 14 assets across 3 sites: Pad Alpha (6 ESPs), Pad Bravo (4 Gas Lift), Rig 42 (3 Mud Pumps + 1 Top Drive)
- **Phase 5:** 4 XGBoost health-score models deployed (`esp_health.ubj`, `gas_lift_health.ubj`, `mud_pump_health.ubj`, `top_drive_health.ubj`), exponential decay training (k=3.5), RMSE <0.002
- **Phase 6:** Bug-fix and UX pass (forecast curve physics, sensor routing, inline Plotly, SSE agent streaming, gemma3:12b)
- **Phase 7:** Bug-fix and feature pass — all items below now live:
  - ✅ Pad Charlie removed from simulator (was generating phantom events)
  - ✅ Duplicate `injectFault()` and `updateIncidents()` consolidated
  - ✅ `_currentForecastData` cleared on asset switch (no chart flicker)
  - ✅ `/api/model/version` endpoint added (MLOps retrain button fixed)
  - ✅ Ollama `gemma3:12b` keepalive background thread (no cold starts)
  - ✅ `scripts/hard_reset_db.sh` added (hard reset tool)
  - ✅ Intervention Slider now shows physical time units (min/hrs/days) with 5s live animation
  - ✅ Plotly chart resizes automatically when Operations Workspace opens/closes
  - ✅ AlloyDB truncated and reset — clean slate post-Pad Charlie

### ⚠️ Known Gaps (Deferred to Phase 8)

1. **`sendAgentMessage()` not streaming:** Follow-up chat messages use blocking HTTP. Backend `/api/agent/recommend-stream` needs `message` + `chat_history` params. Frontend `sendAgentMessage()` needs to consume SSE.

2. **XGBoost models trained on old health-% ground truth:** Models were trained before the time-based slider was added. Ground truth labels are still in health-score space. Consider retraining with time-normalized labels in Phase 8 if the slider-to-health conversion introduces drift.

---

## Cluster Access

```bash
gcloud container clusters get-credentials gdc-edge-simulation \
  --region us-central1 --project gdc-pm-v2
```

## Build + Deploy Pattern (fault-trigger-ui only)

```bash
cd /home/brian/gdc-pm/gke/fault-trigger-ui
docker build --platform linux/amd64 \
  -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest . && \
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest && \
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm && \
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=120s
```

## Hard Reset (clears all events, resets ID sequence)

```bash
bash scripts/hard_reset_db.sh --confirm
```

**Important:** Ask for explicit approval before running any build + deploy sequence.

---

## Doc Set (Current)

```
docs/
├── ARCHITECTURE.md
├── LESSONS_LEARNED.md
├── NEXT_SESSION_PROMPT.md           ← This file
├── PHASE_3_DEPLOYMENT_STATUS.md
├── PHASE_3_1_DEPLOYMENT_STATUS.md
├── PHASE_4_PLAN.md
├── PHASE_4_1_DEPLOYMENT_STATUS.md
├── PHASE_4_1_SENSOR_RETRAIN.md
├── PHASE_4_2_DEPLOYMENT_STATUS.md
├── PHASE_5_PLAN.md
├── PHASE_6_PLAN.md
├── PHASE_6_DEPLOYMENT_STATUS.md
├── PHASE_7_DEPLOYMENT_STATUS.md     ← CURRENT BASELINE (read first)
├── README.md
├── VALUE_PROPOSITION.md
├── WHY_GDC.md
├── WHY_THESE_SCENARIOS.md
├── rag_source/
└── runbooks/DEPLOY_FROM_SCRATCH.md
```

Wait for instructions before proceeding.
