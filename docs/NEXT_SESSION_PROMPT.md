# Next Session Starting Prompt
## Copy and paste this entire block as the task to start the next session

---

Move to `~/gdc-pm`. Initialize as an expert in GCP, BigQuery, Vertex AI, GDC (Google Distributed Cloud), and Kubernetes/GKE.

Also initialize as an expert in industrial edge computing, oil and gas upstream drilling, production, operations, equipment and equipment maintenance. You are an expert in machine monitoring and telemetry, predictive maintenance, and machine learning systems used to predict imminent equipment failures.

You are deeply familiar with MLOps, training-serving skew, model drift, retraining pipelines, and the architectural differences between cloud-based and edge-based inference for time-sensitive industrial applications.

You are also familiar with O&G supply chain and logistics (ESP procurement lead times, custom stage sizing), field service management (FSM route optimization, truck roll costs), and drilling operations (ECD management, volumetric efficiency, NPT prevention).

---

## Project State

This is a GKE-based predictive maintenance demo (`gdc-pm`) running on GKE Autopilot cluster `gdc-edge-simulation` in project `gdc-pm-v2`.

- **UI:** http://35.188.3.97
- **Grafana:** http://136.115.220.48

**Read `docs/PHASE_4_PLAN.md` first.** It contains the full Phase 4 strategy, validated scenarios, and implementation plan.

**Current live state (Phase 4 deployed):**
- 14 assets across 3 sites: Pad Alpha (6 ESPs), Pad Bravo (4 Gas Lift), Rig 42 (3 Mud Pumps + 1 Top Drive)
- `fault-trigger-ui` pod: Phase 4 deployed — agentic predictive maintenance overhaul live
- Cloud latency narrative fully removed (no more purple line, VSAT countdown, or ☁ compare button)
- New: `/api/agent/context/{fault_type}` and `/api/agent/recommend` endpoints live
- New: Dispatch modal shows 🤖 GDC AGENT RECOMMENDATION section with enterprise source badge
- New: SENSOR4_CONFIG (motor_amps for ESP, spm for Mud Pump) in data model
- RAG documents fully expanded with industry-accurate O&G engineering detail
- RUL: XGBoost V2 (default) with fault-only feature extraction
- Both V1 and V2 models loaded on startup; active version controlled via `/api/model/version`

---

## Phase 4 Approved Direction

Phase 4 is an **Agentic Predictive Maintenance** overhaul. The full strategic rationale, O&G industry validation, and implementation plan are in `docs/PHASE_4_PLAN.md`.

**Core narrative shift:**
- **OLD:** "Edge AI detects faults 20 minutes before cloud analytics — beating VSAT latency."
- **NEW:** "GDC predicts failures days/weeks before SCADA thresholds are crossed, then uses local AI agents to check enterprise systems and recommend exactly what to do."

### Three Core Demo Scenarios (Validated Against O&G Industry Practice)

**Scenario 1 — Pad Alpha (ESP): Sand Ingress → Supply Chain / Procurement**
- GDC detects sub-harmonic impeller erosion signature 14 days before gross failure
- SCADA sees nothing (vibration amplitude still below alarm threshold)
- Agent queries Enterprise ERP: custom sand-handler ESP not in local stock, 12-day lead time from Baker Hughes
- Recommendation: Order now. Parts arrive 2 days before predicted failure.

**Scenario 2 — Pad Bravo (Gas Lift): Thermal Runaway → Workforce Scheduling**
- GDC detects growing delta-T divergence (temperature relative to ambient) indicating fouled aerial cooler
- SCADA sees nothing (discharge temperature still below alarm limit)
- Agent queries Field Service Management (Maximo): a crew is already scheduled at Pad Bravo tomorrow
- Recommendation: Append cooler flush to existing work order. Zero truck roll cost.

**Scenario 3 — Rig 42 (Mud Pump): Valve Washout → Active Operational Control**
- GDC detects declining volumetric efficiency — driller's SPM compensation is masking it from SCADA
- Agent queries Rig Control System: MUD-RIG42-3 is standby and ready
- Recommendation: Bring MUD-RIG42-3 online first, then reduce MUD-RIG42-1 to maintain ECD
- Demo "wow moment": Operator clicks "🤖 Execute via Rig Control" — simulated pump transition command

### What Gets Removed
- All "Cloud latency" UI: purple vertical line, VSAT countdown, "☁ Show Arrows" toggle, cloud alert time logic in `app.py`
- The VSAT/latency comparison narrative

### Why Edge (The Correct Narrative)
- **Security/Air Gap:** Telemetry never leaves the site by default
- **Data Gravity:** 50Hz vibration data — too much to backhaul continuously  
- **Survivability:** Core inference runs offline; enterprise connectivity is additive
- **Enterprise Connectivity:** Agent reaches ERP/FSM/SCADA on enterprise WAN — not cloud dependency

---

## Files to Read Before Starting Phase 4 Implementation

```
docs/PHASE_4_PLAN.md                 # Full strategy, scenarios, implementation plan — READ FIRST
docs/PHASE_3_1_DEPLOYMENT_STATUS.md  # Current chart/terminology state
gke/fault-trigger-ui/app.py          # Current backend
gke/fault-trigger-ui/index.html      # Current frontend
gke/event-processor/processor.py     # RAG pipeline + Gemma integration
docs/rag_source/esp_manual.md        # To be expanded
docs/rag_source/gas_lift_manual.md   # To be expanded
docs/rag_source/mud_pump_manual.md   # To be expanded
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

**Important:** Ask for explicit approval before running the build + deploy sequence.

---

## Open Questions (From Phase 4 Planning Session)

1. **Retain the MLOps "Retrain via Vertex AI" demo?** Currently the "☁ Sync & Retrain via Vertex AI" button triggers a simulated V1→V2 model swap. This is orthogonal to the new narrative but still technically interesting. Keep as secondary demo or remove?

2. **SCADA command simulation depth?** For Scenario 3, should we simulate an actual pump RPM/GPM command being acknowledged by the rig control system, or just a visual toast notification?

3. **Connectivity architecture diagram?** Should the UI include a small architecture callout showing "Local GDC ↔ Enterprise WAN ↔ ERP/FSM" to visually reinforce the enterprise (not cloud) connectivity narrative?

Wait for instructions before proceeding.
