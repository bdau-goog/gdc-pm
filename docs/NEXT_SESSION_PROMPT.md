# GDC-PM — Session 9 Handoff

**Date:** 2026-05-20  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2` | Cluster: `gdc-edge-simulation` | Namespace: `gdc-pm`  
**Current image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Git head:** `1d0b2cc` (master — working tree clean, all changes committed)

---

## What Was Done in Session 8

### 1. Deep Dive Panel — Full Redesign (deployed, live)

The Deep Dive event detail panel was completely restructured into a 2-row layout that makes the SCADA vs. GDC AI contrast visually self-explanatory without any narration.

**Row 1 — The Contrast (265px fixed):**
- **Left — "Traditional SCADA":** Renders only the historical blue line, X-axis capped at NOW. Flat red alarm threshold shown far below the sensor. Title hard-codes to "✓ STATUS NORMAL — No Alarms Active." SCADA has no idea anything is wrong.
- **Center — Delta Bridge:** When a fault is active, shows the GDC AI Lead Time in large monospace (e.g., "14.2 days"). The single number that wins the demo.
- **Right — "GDC Edge AI Forecast":** Same historical data but orange RUL projection continues into the future with confidence cone, "⚡ SCADA Alarm in [X]" vertical marker, and PNR marker.

**Row 2 — Evidence & Action (flex):**
- Col 1 (295px): Evidence & Intelligence — sensor grid, live AI document feed, Gemma synthesis
- Col 2 (255px): GDC Ops Agent chat
- Col 3 (flex): Resolution & Action — HITL remediation tiers + approve/reject

**JS change:** `renderChart()` now renders both Plotly charts simultaneously. SCADA chart filters to `traces[0]` (historical) + SCADA Alarm Threshold trace only, strips all annotations and shapes, caps x-axis at last real timestamp.

### 2. Phase 16 Dynamic Intelligence Feed (deployed, live)

`get_intelligence_feed()` in `app.py` now queries the `field_intel` AlloyDB table for the active fault context and prepends up to 10 live LLM-generated documents (prefixed `gi_*`) before the pre-canned `INTELLIGENCE_FEED` items. The Deep Dive "Evidence & Intelligence" column now shows real AI-generated field documents.

### 3. Grafana Improvements (deployed, live)

- Default time range: `now-2h` → `now-8h`
- Vibration panels split into 3 sub-panels: ESP / Gas Lift / Rig 42 (each `w:8`)
- Temperature panels split into 3 sub-panels: ESP / Gas Lift / Rig 42 (each `w:8`)
- Grid y-positions updated throughout (Electrical → y:34, Edge AI → y:44, SCADA log → y:55)

### 4. Operational Honesty

- `OLLAMA_DISPLAY_MODEL=gemma:2b` applied to `fault-trigger-ui` deployment — UI now honestly shows `gemma:2b` as the running model

### 5. Documentation

- `docs/DEMO_NARRATIVE.md` — new unified demo walk-through guide with 5-phase presenter script, narrator lines, 12-step quick-reference flow, and objection-handling talking points
- `.clinerules` — Pre-Handoff Checklist added: enforces `git status` check before writing handoff, Feature Completeness Gate (Partially Complete label for undeployed work), cross-check of To-Do vs. What Was Done sections

---

## Current Cluster State

```
gdc-edge-simulation / gdc-pm namespace
────────────────────────────────────────
fault-trigger-ui       1/1 Running   ← Primary demo UI + FastAPI backend (Session 8 image)
telemetry-simulator    1/1 Running   ← Generates 12 readings/min
event-processor        1/1 Running   ← RabbitMQ → inference → AlloyDB
alloydb-omni           1/1 Running   ← PostgreSQL edge DB (has field_intel table)
gdc-pm-rabbitmq        1/1 Running   ← AMQP message broker
grafana                1/1 Running   ← SCADA dashboard (http://136.115.220.48) — 8h range, split vib/temp panels
ollama                 1/1 Running   ← gemma:2b actual model (OLLAMA_DISPLAY_MODEL=gemma:2b, honest)
inference-api          1/1 Running   ← Legacy BQML inference (not used by current UI)
```

**IMPORTANT:** Ollama is running `gemma:2b`. The YAML targets `gemma4:27b` on L4 but NOT applied — requires L4 node pool and project-admin IAM. `OLLAMA_DISPLAY_MODEL` is now set to `gemma:2b` (honest).

---

## Outstanding Development Items (To-Do)

### High Priority

**1. Grafana Fleet Telemetry — Site-Zone Grouping**
- Current: Panels grouped by sensor type (all Pressures, all Vibrations). This is a data-scientist view, not an operator view.
- Goal: Restructure the Grafana dashboard to group by operational site — three rows:
  - **Pad Alpha (ESP Production):** Intake PSI, Motor Winding Temp, Motor Current, Vibration — filtered to `ESP-%` assets
  - **Pad Bravo (Gas Lift):** Discharge PSI, Discharge Temp, Vibration — filtered to `GLIFT-%`
  - **Rig 42 (Drilling):** Mud Pump PSI + SPM, Top Drive Vib + Temp — filtered to `MUD-%` and `TOPDRIVE-%`
- The spaghetti-line problem for Vib and Temp was reduced by splitting into 3 sub-panels, but the page still leads with a wall-of-sensors view
- File: `gke/grafana/k8s/grafana-configmap.yaml`
- After: `kubectl apply -f ... && kubectl rollout restart deployment/grafana -n gdc-pm`

**2. Gemma 4 / L4 GPU Upgrade** *(requires project admin IAM)*
- YAML files ready for `gemma4:27b` on L4
- Pending: Project admin grants `roles/container.developer` to `dev-workstation-sa@gdc-pm-v2.iam.gserviceaccount.com`, provision L4 node pool, apply `gke/ollama/k8s/ollama-scheduler.yaml` then `gke/ollama/k8s/ollama.yaml`
- After upgrade: `kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_MODEL=gemma4:27b OLLAMA_DISPLAY_MODEL=gemma4:27b`

### Medium Priority

**3. Demo Flow Polish**
- Recommended demo script: Fleet Telemetry tab (SCADA all green) → Fleet Operations tab → click ESP-ALPHA-2 → inject Sand Ingress → show AI Detection Timeline populating in Grafana while SCADA log remains empty → open Deep Dive → side-by-side comparison (SCADA normal / GDC: 14 days lead time) → Consult Agent → Approve
- Consider whether the Grafana "⚡ GDC Edge AI Detection Timeline" needs annotation arrows for the demo moment

### Low Priority

**4. Chart Y-Axis Note**
- Single exponential forecast (k=3.5/1.8) means SCADA alarm marker may not align exactly where curve crosses `y_crit` — this is intentional and physically correct. Both are independent estimates. No fix needed.

---

## Constraints — Do Not Violate

- **Never apply `terraform/gke.tf`** — destroys the live cluster
- **Never change iframe to `?kiosk`** — must stay `?kiosk=tv`
- **Only edit:** `gke/fault-trigger-ui/app.py`, `gke/fault-trigger-ui/index.html`, `gke/grafana/k8s/grafana-configmap.yaml`
- Gemma keepalive thread is in `app.py` — prevents cold starts during demos
- XGBoost health models (`*.ubj`) are validated — do not retrain without specific reason
- `_ensure_field_intel_table()` creates `field_intel` idempotently on startup

---

## Rebuild & Deploy Commands

```bash
# UI (after editing app.py or index.html):
cd /home/brian
docker build --quiet -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gdc-pm/gke/fault-trigger-ui/
docker push --quiet us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=180s
```

```bash
# Grafana only (no app rebuild needed):
kubectl apply -f gdc-pm/gke/grafana/k8s/grafana-configmap.yaml
kubectl rollout restart deployment/grafana -n gdc-pm
kubectl rollout status deployment/grafana -n gdc-pm --timeout=90s
```

---

## Key Lessons Learned (Session 8)

**Side-by-side chart rendering via trace filtering:** The SCADA chart is derived from the same `chartData.sensors[tab]` object as the GDC chart. Filter `traces` to `name === 'Live Telemetry' || name === 'SCADA Alarm Threshold'`, deep-clone the layout, strip `annotations` and `shapes`, cap `xaxis.range` to the last historical timestamp. This produces a correct SCADA historian view with zero additional backend calls.

**Demo timing for maximum contrast:** For sand ingress (14-day horizon), the most powerful demo moment is the first 15–20 minutes of the fault ramp, when GDC has already detected the multi-variate signature but all sensors are still well within SCADA alarm limits. The delta bridge will show ~14 days. Waiting too long into the ramp reduces the visual gap as the sensor approaches the threshold.

**Fault-type honesty for the narrative:** Not all fault modes have SCADA-invisible profiles. Gas lock, sand ingress, and piston seal wear are "SCADA completely blind" scenarios. Bearing wear, thermal runaway, and motor overheat are "SCADA catches it late" scenarios. Both are valid demo points: the first proves SCADA can't see it at all; the second proves GDC gives hours/days of advance warning vs. an emergency response. The delta bridge quantifies this correctly for all fault types.
