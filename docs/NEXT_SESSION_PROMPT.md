# GDC-PM — Handoff & Primer for UI Reassessment

**Date:** 2026-05-13  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2` | Cluster: `gdc-edge-simulation` | Namespace: `gdc-pm`  
**Current image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Image digest:** `sha256:7496cf230650d0d2ec6fa07302520c741752c92b9ed236bf3f69ac10638b8579`

---

## What This Is

A GKE-hosted demo of **predictive maintenance on Google Distributed Cloud (GDC)**.
The application simulates an oil & gas operating company running AI/ML inference
at the edge — on an asset fleet spread across drilling rigs and production pads —
predicting equipment failures before any SCADA threshold is crossed.

The **target audience** is a GCP customer or prospect who manages remote industrial
assets and is evaluating whether GDC (Google Distributed Cloud) makes sense for
their edge AI workloads.

The **one-sentence pitch:**  
*"GDC doesn't just alarm faster. It tells you weeks or days early, checks what you
need to fix it, and tells you exactly what to do — while everything on your SCADA
dashboard still looks green."*

---

## The Story Being Told — Three Scenarios

The three demo scenarios were deliberately selected to represent three **distinct types
of value** that an edge AI system delivers. Each one answers a different objection to
the question *"Why couldn't you just configure a better SCADA setpoint?"*

| Scenario | Site | Asset | Fault | Primary Value | Time Horizon |
|---|---|---|---|---|---|
| 1 | Pad Alpha | ESP-ALPHA-2 | Sand Ingress | **Supply chain lead time** — 14-day warning, 12-day part lead time | Days |
| 2 | Pad Bravo | GLIFT-BRAVO-1 | Thermal Runaway | **Workforce route optimization** — crew already en route tomorrow | Hours |
| 3 | Rig 42 | MUD-RIG42-1 | Valve Washout | **Active operational control** — the driller is masking the failure from SCADA | Hours |

Each fault is also physically validated: SCADA genuinely cannot detect these patterns
because they require multivariate analysis — not just a higher setpoint. See
`docs/WHY_THESE_SCENARIOS.md` for the full engineering narrative per scenario.

The **four pillars of why this runs on GDC specifically** (not cloud):  
Security/air-gap, data gravity (200GB/day of 50Hz vibration), latency (some faults
have <10min response windows), survivability (rig keeps drilling when WAN is down).
See `docs/WHY_GDC.md` for the full argument.

---

## What Is Currently Running in the Cluster

```
gdc-edge-simulation / gdc-pm namespace
────────────────────────────────────────
fault-trigger-ui       1/1 Running   ← Primary demo UI + FastAPI backend (Phase 10)
telemetry-simulator    1/1 Running   ← Generates synthetic sensor telemetry, 12 readings/min
event-processor        1/1 Running   ← RabbitMQ consumer → inference → AlloyDB writer
alloydb-omni           1/1 Running   ← PostgreSQL-compatible edge DB (telemetry_events table)
gdc-pm-rabbitmq        1/1 Running   ← AMQP message broker
grafana                1/1 Running   ← Live telemetry dashboard (http://136.115.220.48)
ollama                 1/1 Running   ← Gemma3:12b local LLM (keeps warm via 5min keepalive)
inference-api          1/1 Running   ← Legacy BQML inference (not used by current UI flow)
```

**Asset Fleet (14 assets, 3 sites):**
- Pad Alpha: ESP-ALPHA-1…6 (Electric Submersible Pumps — ESP class)
- Pad Bravo: GLIFT-BRAVO-1…4 (Gas Lift Compressors — gas_lift class)
- Rig 42: MUD-RIG42-1,2,3 (Mud Pumps) + TOPDRIVE-RIG42-1 (Top Drive)

---

## The Application Architecture (What `fault-trigger-ui` Does)

The entire demo experience lives in two files:
- `gke/fault-trigger-ui/app.py` — FastAPI backend (Python)
- `gke/fault-trigger-ui/index.html` — Single-page frontend (vanilla JS, Plotly.js)

### How a fault demonstration flows end to end

```
1. Operator clicks asset card (e.g., ESP-ALPHA-2)
   → UI calls GET /api/health-status/ESP-ALPHA-2
   → Shows asset detail: sensor tabs (PSI / Temp / Vib / Motor Current), normal baseline chart

2. Operator selects fault type (e.g., "Sand Ingress") and clicks "Inject"
   → POST /api/fault/inject {asset_id, fault_type}
   → Backend starts _run_degrade_thread: synthetic degradation ramp injected into AlloyDB
     at 5-second intervals alongside the normal simulator telemetry

3. UI polls GET /api/degrade-status/ESP-ALPHA-2 every 5s
   → Returns: health_score (0→1), time_to_scada_minutes, time_to_pnr_minutes,
     time_to_failure_minutes, horizon_label (Days/Hours/Minutes)
   → Intervention slider max shrinks in real time

4. UI polls GET /api/plot/forecast-data/ESP-ALPHA-2 (returns all 4 sensor tabs at once)
   → Plotly.react() updates chart inline (no iframe reload)

5. Operator sets intervention slider ("Intervening in 9h 30m")
   → Left panel updates: Tier badge (EARLY/URGENT/CRITICAL), cost estimates, time math

6. Operator clicks "Consult Operations Agent"
   → POST /api/agent/recommend-stream (SSE)
   → Rule-based recommendation fires immediately (zero LLM latency)
   → Gemma3:12b via Ollama streams a 2–3 sentence narrative after
   → Right panel shows: enterprise system queried (SAP MM / IBM Maximo / Pason EDR),
     specific recommendation with reasoning

7. Operator interacts via chat (follow-up questions)
   → POST /api/agent/recommend-stream with chat_history
   → Streams into conversation thread

8. Operator clicks Reset → back to normal baseline
```

### Key API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health-status/{asset_id}` | GET | Current asset health + sensor values |
| `/api/fault/inject` | POST | Start degradation ramp |
| `/api/degrade-status/{asset_id}` | GET | Live health + time-to-X values for slider |
| `/api/plot/forecast-data/{asset_id}` | GET | All 4 sensor tabs as Plotly JSON (one call) |
| `/api/fault-physics/{fault_type}` | GET | Physics config for a fault (horizons, sensors) |
| `/api/agent/recommend-stream` | POST | SSE streaming agent recommendation |
| `/api/model/version` | POST | Swap XGBoost health models (v1/v2) |
| `/api/model/status` | GET | Loaded model inventory |

---

## The ML Architecture (What the Models Are and How They Work)

### Health Score Models (the core ML, 4 models)

Files: `gke/fault-trigger-ui/models/esp_health.ubj`, `gas_lift_health.ubj`,
`mud_pump_health.ubj`, `top_drive_health.ubj`

- **Type:** XGBoost regressors
- **Target:** `health_score` — a continuous value from 1.0 (perfect) to 0.0 (destroyed)
- **Input features (6):** `[psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]`  
  (plus `motor_amps/damps_dt` for ESP, `spm/dspm_dt` for Mud Pump = 8 features)
- **Training:** Synthetic sequences with exponential decay curve (k=3.5), 300 samples
  per fault × 300 XGBoost rounds. RMSE ~0.002. Phase 10 retrain included partial
  intervention plateaus (15% probability) to make models robust to non-monotonic
  health trajectories.
- **These models are correct and should NOT be retrained without a specific reason.**

### FAULT_PHYSICS Config (in `app.py`)

The health models are asset-class-agnostic — they score health state, not time.
The `FAULT_PHYSICS` dictionary in `app.py` maps health scores to physical reality:

```python
FAULT_PHYSICS = {
    "sand_ingress":  { total_hours: 336,  # 14 days
                       scada_alarm_health: 0.15,
                       pnr_health: 0.05,
                       horizon_label: "Days",
                       scada_sensor: "vib", pnr_sensor: "vib", primary_sensor: "vib",
                       intervention_type: "supply_chain" },
    "thermal_runaway": { total_hours: 72,  # 3 days
                         scada_alarm_health: 0.20, ... },
    "gas_lock":      { total_hours: 0.75,  # 45 min
                       scada_alarm_health: 0.30,
                       pnr_health: 0.12,
                       scada_sensor: "psi", pnr_sensor: "temp", primary_sensor: "psi",
                       intervention_type: "operational_control" },
    # ... 11 fault types total
}
```

This is what allows one model architecture to correctly serve both a 45-minute
gas lock and a 14-day sand ingress fault.

### Correct Chart Timeline (hard-won — do not revert)

The forecast chart renders this sequence left-to-right:
```
Now / ML Detection → [Orange projection] → SCADA Alarm threshold → PNR → Failure
```

This was backwards in earlier phases (PNR appeared before SCADA alarm). The fix was
structural: SCADA alarm is an *operational setpoint*, not a failure event. The PNR
is the *physical* point of no return. The chart must show SCADA → PNR → Failure in
that order to make SCADA look "good but too late" rather than "useless."

### Sensor Routing (per-fault, do not generalize)

Each fault type has exactly one sensor that triggers the SCADA alarm, one that
determines the PNR, and one "primary" sensor that is the most diagnostically
meaningful to an operator. These are specified in `FAULT_PHYSICS` and used to:
- Draw the SCADA threshold line only on the correct sensor tab
- Draw the PNR vertical line only on the correct sensor tab
- Auto-select the primary sensor tab when a fault is injected
- Direct Plotly forecast curve parameterization

**The gas_lock case is a known complexity:** The current SCADA sensor for gas_lock
is `psi` (intake pressure drops as gas void rises). The original implementation
erroneously used `amps` (motor current). This was corrected in Phase 10.

---

## Key Design Decisions and Why They Were Made

### Decision 1: Health Score instead of RUL Minutes
**Why:** RUL in minutes requires the model to understand the *scale* of each fault
(45 minutes for gas lock, 14 days for sand ingress). A health score (0→1) is
scale-agnostic — the model scores equipment state, and the UI layer maps that to
physical time via `FAULT_PHYSICS`. This means one model architecture serves all
fault types correctly.

**Consequence:** The models are now more portable and interpretable. Health = 0.85
means "15% degraded" for any fault type, which is intuitive for operators.

### Decision 2: Remove V1/V2 Cloud Drift Narrative
**Why:** The "V1 cloud-drifted vs V2 edge-calibrated" MLOps story was a distraction
from the core value proposition and introduced confusion about whether the model on
screen was the "good" or "bad" one. The demo narrative is now cleaner: one
high-quality edge model per asset class.

**Consequence:** The `☁ Retrain via Vertex AI` button and dual-model registry were
removed in Phase 5. The model retrain in Phase 10 (`retrain_edge_models.py`) now
maintains a single production model per asset class.

### Decision 3: Three Intervention Types
**Why:** The scenarios needed structurally different agent responses to avoid feeling
repetitive. The three types (supply_chain → ERP/SAP, maintenance_scheduling →
FSM/Maximo, operational_control → Rig Control/Pason) each have distinct enterprise
system integrations and resolution timeframes, making each scenario feel like a
different use case.

**Consequence:** The agent prompting, mock enterprise API responses, and cost
calculations are all branched by `intervention_type` in `app.py`.

### Decision 4: Time-Based Slider (not Health %)
**Why:** Operators don't think in health percentages. They think in "how many days
do I have before I need to act?" The slider operates in physical units (Minutes /
Hours / Days) determined by `horizon_label` in `FAULT_PHYSICS`. The slider's max
value shrinks in real time as the fault progresses (via the degrade-status poller).

**Consequence:** `_wsTTFMinutes` drives slider range; `_wsSliderHealth` is computed
from `slider_value / ttf_minutes` as a derived value. The slider counts DOWN (right
= more time, left = imminent failure / now).

### Decision 5: `_wsCurrentHealth` vs `_wsSliderHealth` Separation (Phase 10)
**Why:** The tier badge (🟢 EARLY / 🟡 URGENT / 🔴 CRITICAL) must reflect the asset's
health *right now*, not the health at the operator's chosen future intervention time.
Previously, these were the same variable, so dragging the slider to "intervene
sooner" (when the asset would be healthier) would flip the badge to CRITICAL — the
opposite of intuitive.

**Fix:** `_wsCurrentHealth` is always updated by the poller from the server's current
health. The tier badge is computed from `_wsCurrentHealth`. The slider only controls
`_wsSliderHealth`, which drives the physics/cost calculator.

### Decision 6: Inline Plotly.js (not iframe)
**Why:** The iframe-based forecast chart required a full server round-trip and
chart regeneration on every tab switch (2–4 seconds each). Replacing it with a
`<div id="forecast-chart">` + Plotly.js CDN means the backend returns all 4 sensor
tabs' data in one JSON call, and `Plotly.react()` switches tabs at animation speed.

**Consequence:** `refreshPlot()` calls `GET /api/plot/forecast-data/{asset_id}`
once; `selectTab()` calls `Plotly.react()` with no server request.

### Decision 7: Two-Segment Exponential for SCADA Alarm Curve (Phase 10)
**Why:** A single-segment exponential over the full failure horizon does not
guarantee that the projection curve crosses the SCADA threshold *exactly* at the
`rul_minutes` time point. The marker appeared to the right of where the curve
crossed the line. Fix: parameterize the curve as two segments — segment 1 goes from
`y_start → y_crit` over exactly `rul_minutes`, segment 2 continues `y_crit → y_failure`
over the remaining horizon. The SCADA alarm marker now aligns precisely.

### Decision 8: Gemma3:12b via Ollama (not Vertex AI Gemma)
**Why:** Vertex AI Gemma had cold-start latency of 10+ seconds when the endpoint
was idle. Ollama runs Gemma3:12b in-cluster (on the same GKE node), and a keepalive
thread pings it every 5 minutes to prevent model unloading. Combined with SSE
streaming, the agent response feels instant (rule-based text appears immediately,
then LLM tokens stream in).

### Decision 9: Rule-Based Recommendation Fires Before LLM
**Why:** The structured recommendation (tier badge, enterprise system query result,
specific action) is computed deterministically in Python from `FAULT_PHYSICS` and
mock enterprise APIs. This fires instantly with zero LLM latency. The LLM then
streams a 2–3 sentence narrative that provides human-readable context and nuance.
This pattern ensures the demo never "hangs" waiting for LLM generation.

---

## The Current Interface Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  Header: GDC-PM Predictive Maintenance                Fleet KPI bar  │
├──────────┬───────────────────────────────────────────────────────────┤
│  Site    │  [Pad Alpha] [Pad Bravo] [Rig 42]          Main tabs:     │
│  Sidebar │                                            Fleet Overview │
│          │  Asset cards (14) with health dot + fault  Historical Tel │
│  (asset  │  badge + RUL countdown                     Fleet Finance  │
│  list)   │                                                           │
│          ├───────────────────────────────────────────────────────────┤
│          │  SELECTED ASSET PANEL                                     │
│          │  ┌── Sensor tabs ──────────────────────────────────────┐  │
│          │  │  [PSI] [Temp] [Vib] [Motor Current*]               │  │
│          │  │                                                      │  │
│          │  │         Plotly forecast chart                       │  │
│          │  │  (live telemetry + ML projection + SCADA/PNR marks) │  │
│          │  └─────────────────────────────────────────────────────┘  │
│          │                                                           │
│          │  ┌── Intervention Slider ─────────────────────────────┐  │
│          │  │  ◄────────────────────────────── [●] ──────────►   │  │
│          │  │  Intervening in 9h 30m           14 days to failure │  │
│          │  └─────────────────────────────────────────────────────┘  │
│          │                                                           │
│          │  [resize handle]  (drag to expand/collapse below)        │
│          │                                                           │
│          │  ┌── Operations Workspace ────────────────────────────┐  │
│          │  │  LEFT: Physics/Economics      RIGHT: Agent Chat    │  │
│          │  │  ─────────────────────        ──────────────────   │  │
│          │  │  Tier: 🟢 EARLY               [Consult Agent]     │  │
│          │  │  Time to SCADA: 9h 30m                            │  │
│          │  │  Time to PNR:   12h 15m        💬 Agent: "Based   │  │
│          │  │  Time to Fail:  14d 0h          on sand ingress... │  │
│          │  │  Cost Avoided:  $120,000        Order part now..." │  │
│          │  │  Cost Incurred: $2,500                             │  │
│          │  │                                [chat input] [Send] │  │
│          │  └─────────────────────────────────────────────────────┘  │
└──────────┴───────────────────────────────────────────────────────────┘
```

(*) 4th sensor tab is conditional: Motor Current for ESP, Stroke Rate for Mud Pump,
absent for Gas Lift and Top Drive.

---

## What Is NOT Working Well (The Reason for This Reassessment)

The interface has been built incrementally over 10 phases. Each phase solved a
specific technical problem. The cumulative result is a working system with
**structural storytelling problems** that make it hard to run a smooth demo:

1. **The story doesn't have a natural beginning.** A new viewer sees 14 asset cards
   and a generic fleet dashboard. There is no narrative entry point that says "here's
   what SCADA sees, here's what GDC sees, and here's why that matters." The demo
   relies entirely on a live presenter walking through it.

2. **The forecast chart is technically correct but visually dense.** It has six
   types of overlaid information (live telemetry, ML projection, confidence cone,
   SCADA threshold line, SCADA alarm marker, PNR marker, Intervening marker). An
   audience member who hasn't seen it before needs 30–60 seconds to parse it —
   during a live demo, that's the whole attention budget.

3. **The intervention slider adds cognitive complexity before the value proposition
   is established.** A first-time viewer doesn't yet understand *why* the slider
   matters. The "intervening earlier vs. later" comparison only makes sense after the
   viewer understands the cost of waiting. The slider is currently the second thing
   you see after injecting a fault.

4. **The three scenarios aren't differentiated in the UI.** The gas lock on an ESP
   (45-minute operational emergency), the thermal runaway on a gas lift compressor
   (3-day workforce scheduling), and the valve washout on a mud pump (2-hour
   operational control) all use the same chart, slider, and agent panel. The UI
   doesn't visually reflect the very different nature of each scenario.

5. **The Operations Workspace feels cramped.** The physics calculator (left) and
   agent chat (right) compete for space in a panel that is already below the chart
   and slider. In practice, the presenter has to scroll down to show the agent
   conversation, which breaks the demo flow.

6. **The agentic value is the climax, but it's buried.** The three enterprise
   system integrations (SAP MM procurement, IBM Maximo scheduling, Pason EDR pump
   swap) are the most compelling part of the demo — but they appear at the bottom of
   the screen after the operator has already understood the fault and set the slider.
   The agent conclusion feels like a footnote rather than the headline.

7. **Grafana is on a separate URL.** The historical telemetry dashboard is at
   `http://136.115.220.48` and opens in a separate tab. This is fine for showing
   "what's in the database," but it means the demo requires two browser tabs and
   the presenter must context-switch.

---

## What IS Working and Should Be Preserved

- **The physics engine is correct.** The `FAULT_PHYSICS` config, health score models,
  exponential decay curves, SCADA/PNR/Failure sequence, and sensor routing by fault
  are all validated and correct. Do not touch the ML or physics layer.

- **The three scenarios are the right scenarios.** The failure physics, industry
  validation, and enterprise system integrations documented in `WHY_THESE_SCENARIOS.md`
  are solid. This is not the thing to reassess.

- **The core value proposition is the right one.** The four pillars in `WHY_GDC.md`
  (security, data gravity, latency, survivability) and the "SCADA vs ML" differentiation
  in `VALUE_PROPOSITION.md` are well-grounded. The *message* is right; the *medium*
  needs work.

- **The agent backend is functional.** SSE streaming, rule-based + LLM hybrid,
  chat history, three intervention types — the agent works well. The presentation
  of the agent output is the problem, not the agent itself.

- **The asset fleet and simulator are correct.** 14 assets, 3 sites, 11 fault types,
  all sensor channels generating realistic ranges.

---

## Critical Constraint for Reassessment

The **cluster and infrastructure are running and should be left intact.** Any UI
reassessment work is in `gke/fault-trigger-ui/index.html` and (if backend changes
are needed) `gke/fault-trigger-ui/app.py`. After changes:

```bash
# Rebuild and redeploy (fast, ~90s total):
docker build --quiet -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest \
  gdc-pm/gke/fault-trigger-ui/

docker push --quiet us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest

kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=180s
```

The `terraform/gke.tf` must NOT be applied (would destroy the live cluster).

---

## Document Map (what's still relevant)

| Document | Status | Purpose |
|---|---|---|
| `docs/NEXT_SESSION_PROMPT.md` | ✅ Current | This file |
| `docs/PHASE_10_DEPLOYMENT_STATUS.md` | ✅ Current | Full technical state, Phase 10 changes |
| `docs/WHY_GDC.md` | ✅ Current | The four pillars — why edge, not cloud |
| `docs/WHY_THESE_SCENARIOS.md` | ✅ Current | Scenario physics, industry validation |
| `docs/VALUE_PROPOSITION.md` | ✅ Current | SCADA vs ML differentiation narrative |
| `docs/ARCHITECTURE.md` | ✅ Current | Two-repo model (bdau-basic-vpc + gdc-pm) |
| `docs/LESSONS_LEARNED.md` | ✅ Current | Infrastructure lessons (GKE, Grafana, AlloyDB) |
| `docs/README.md` | ⚠️ Outdated | Describes old stator/PRD failure architecture |
| `docs/runbooks/DEPLOY_FROM_SCRATCH.md` | ⚠️ Outdated | Describes old 3-model factory, not current O&G scenarios |

---

## Wait for Instructions

Read this document, examine `http://35.188.3.97` in a browser, and **wait for the
user to describe what they want to change before touching any code.** The goal of
the reassessment is to redesign the presentation layer — how the story is told
visually — not to add features or fix bugs. Start by understanding what the user
wants to achieve with the new interface before proposing solutions.
