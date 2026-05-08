# Next Session Starting Prompt
## Copy and paste this entire block as the task to start the next session

---

Move to `~/gdc-pm`. Initialize as an expert in GCP, BigQuery, Vertex AI, GDC (Google Distributed Cloud), and Kubernetes/GKE.

Also initialize as an expert in industrial edge computing, oil and gas upstream drilling, production, operations, equipment and equipment maintenance. You are an expert in machine monitoring and telemetry, predictive maintenance, and machine learning systems used to predict imminent equipment failures.

You are deeply familiar with MLOps, training-serving skew, model drift, retraining pipelines, and the architectural differences between cloud-based and edge-based inference for time-sensitive industrial applications.

---

## Project State

This is a GKE-based predictive maintenance demo (`gdc-pm`) running on GKE Autopilot cluster `gdc-edge-simulation` in project `gdc-pm-v2`.

- **UI:** http://35.188.3.97
- **Grafana:** http://136.115.220.48

**Read `docs/PHASE_3_DEPLOYMENT_STATUS.md` first.** It contains the complete Phase 3 implementation summary including:
- All 7 tasks delivered (XGBoost RUL restore, V2 model training, MLOps retrain flow, chart upgrades, PNR/Failed states, tiered resolution actions, fault onset tracking)
- 3 bug fixes applied (Grafana URL, ledger truncation, reset button)
- Current cluster state and demo script
- Known limitations
- Phase 4 vision

**Current live state:**
- `fault-trigger-ui` pod: Phase 3 complete — all features deployed
- RUL: XGBoost V1 (drifted, intentional) with fault-only feature extraction
- Both V1 and V2 models loaded on startup; active version controlled via `/api/model/version`
- MLOps retrain demo: click "☁ Sync & Retrain via Vertex AI" → 3-step pipeline toast → V2 model swap → stable RUL
- Edge vs Cloud chart: solid vertical lines (PNR + Cloud Alert), horizontal Time-to-React arrows
- Dispatch modal: 4-tier resolution actions with VIABLE/MARGINAL/NOT VIABLE scoring
- Fleet Financials: separate `/api/ledger` endpoint (not limited by event log truncation), "♻ Reset Demo Data" button

---

## Phase 4 Scope (Proposed — Not Yet Started)

Phase 4 is the "AI Agent closes the loop" milestone. The Gemma 2B model running via Ollama is already deployed in the cluster and connected via the event-processor RAG pipeline.

### Proposed Phase 4 Tasks

**Task 1: Autonomous Dispatch Proposal (Gemma → dispatch modal)**
- When operator opens the dispatch modal, Gemma evaluates the active fault, current RUL, and the tiered resolution actions already computed by `/api/resolution-actions`
- Gemma outputs a JSON recommendation: `{recommended_tier, justification, confidence, proposed_action}`
- Modal shows "🤖 AI Recommends: [action]" with a confidence bar above the tier options
- Operator can accept (one click) or override (manually select different tier)

**Task 2: Parts Inventory Query (mock API)**
- Create a mock `/api/inventory/{part_type}` endpoint returning availability + lead time for common O&G parts (impellers, seals, bearings, valve discs, etc.)
- Gemma queries this before making a recommendation: "Is an ESP impeller string available on-site? Lead time 3 days → recommend early intervention, not emergency order."
- Show inventory status in the dispatch modal alongside the resolution action

**Task 3: Proactive PNR Alert (server-sent events or polling)**
- When a fault is active and 50% of PNR time has elapsed with no acknowledgement, auto-generate a push notification / high-visibility toast: `⚠ T+12m — HALF OF PNR WINDOW ELAPSED — {asset_id} unacknowledged`
- Implemented as a background thread checking `active_degrades` every 30s

**Task 4: Multi-asset Correlation (fleet-level pattern detection)**
- When 2+ assets on the same site trigger faults within 5 minutes, generate a fleet-level alert: `🔴 MULTI-ASSET EVENT — Pad Alpha: 2 ESPs degrading simultaneously`
- Possible shared-cause hypotheses shown (shared cooling loop, formation breakthrough, etc.)
- This sets up the AI agent's "why" narrative

**Task 5: SCADA Command Simulation (closed-loop demo)**
- Add a "🤖 Execute via SCADA" button to the dispatch modal for software_command tier actions
- Clicking it triggers a simulated SCADA command toast: "Issuing VFD frequency reduction to ALPHA-1... confirmed at 14:32:07 UTC"
- No real SCADA connection — purely visual simulation for demo impact
- This is the "Phase 4 close" moment: AI detected, AI diagnosed, AI remediated, human approved

---

## Files to Read Before Starting Phase 4

```
docs/PHASE_3_DEPLOYMENT_STATUS.md   # Full Phase 3 summary
gke/fault-trigger-ui/app.py         # Current backend (Phase 3 complete)
gke/fault-trigger-ui/index.html     # Current frontend (Phase 3 complete)
gke/event-processor/processor.py    # RAG pipeline + Gemma integration
```

---

## Cluster Access

```bash
gcloud container clusters get-credentials gdc-edge-simulation \
  --region us-central1 --project gdc-pm-v2
```

## Build + Deploy Pattern

```bash
cd /home/brian/gdc-pm
REG="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build --quiet -t "${REG}/fault-trigger-ui:latest" gke/fault-trigger-ui/ && \
  docker push --quiet "${REG}/fault-trigger-ui:latest" && \
  kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm && \
  kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=120s
```

Wait for instructions before proceeding.
