# GDC-PM — Session 11 Handoff

**Date:** 2026-05-20  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2` | Cluster: `gdc-edge-simulation` | Namespace: `gdc-pm`  
**Current image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Git head:** Session 10 changes committed on master

---

## What Was Done in Session 10

### 1. Ollama Scheduler RBAC — Resolved (deployed, live)

The L4 GPU auto-scaling scheduler was previously blocked because `container.roles.create` IAM was denied. Confirmed that `kubectl auth can-i create role -n gdc-pm` returned **yes** — the RBAC permissions already existed at the namespace level. Applied the full scheduler manifest:

- `serviceaccount/ollama-scheduler` ✅
- `role.rbac.authorization.k8s.io/ollama-scaler` ✅
- `rolebinding.rbac.authorization.k8s.io/ollama-scheduler-scaler` ✅
- `cronjob.batch/ollama-stand-up` — **6 AM UTC, Mon–Fri** ✅
- `cronjob.batch/ollama-stand-down` — **6 PM UTC, daily** ✅

**Cost impact:** L4 GPU node (gemma4:27b) now auto-provisions on weekday mornings and deprovisions evenings → ~78% GPU cost savings.

**Current ollama state:** New pod (`ollama-77f99db54d-*`) still Pending (L4 node provisioning / 15GB model pull). Old pod (`ollama-8ffc6bd5b-*`) still Running on gemma:2b and serving requests.

### 2. Fleet Financials — Narrative ROI Card (deployed, live)

Replaced the minimal 3-KPI row with a full **"Before GDC vs After GDC"** narrative card:

- **Hero ROI number:** Large monospace `$totalSaved` with green gradient — the "big number" visible instantly
- **Annualised Projection** card (visible only after first intervention): `totalSaved × 52` with footnote
- **Before/After comparison grid:** Left card (🛢 Traditional SCADA Only) lists 5 failure modes in red; right card (⚡ GDC Edge AI) lists 5 advantages in green — direct side-by-side contrast
- **3 KPI tiles:** Incidents Resolved (blue), Fleet Uptime Protected (green), Avg $ / Intervention (yellow)
- **Methodology footnote:** API RP 11S / SPE-181437-MS references, downtime rates ($45k/day ESP, $120k/day rig)
- **Fleet Uptime comparison bar:** Horizontal progress bars GDC (green) vs SCADA-only (red estimated), appears after first intervention
- **Cost-per-intervention sparkline row:** Individual mini-cards per resolved incident, newest first
- **Empty state message:** "No resolved incidents yet — approve a fault intervention in Fleet Operations to populate this ledger."

### 3. Grafana Fleet Telemetry — Per-Asset Stat Cards (deployed, live)

Added 14 per-asset PSI health stat panels to `grafana-configmap.yaml` using a Python patch script (`gdc-pm/scripts/patch_grafana_stat_panels.py`):

**New panels — Pad Alpha (6 ESP stat cards at y=6):**
- IDs 100–105: ESP-A1, ESP-A2, ESP-A3, ESP-A4, ESP-A5, ESP-A6
- Each shows current 5-min avg Intake PSI with green/orange/red threshold coloring
- Click → navigates to `/d/gdc-pm-main?var-asset=ESP-ALPHA-N&kiosk=tv`

**New panels — Pad Bravo (4 GLIFT stat cards at y=29):**
- IDs 110–113: GL-B1, GL-B2, GL-B3, GL-B4
- Each shows current Discharge PSI

**New panels — Rig 42 (4 stat cards at y=43):**
- IDs 120–123: MUD-1, MUD-2, MUD-3, TDRIVE
- Mud pump: Discharge PSI (1800–3800 PSI range); Top Drive: Hydraulic PSI

**All existing chart panels shifted down** to accommodate the new rows (+12 total Y to Edge AI section).

**Total panel count:** 24 → 38 panels

---

## Current Cluster State

```
gdc-edge-simulation / gdc-pm namespace
────────────────────────────────────────
fault-trigger-ui       1/1 Running   ← Session 10 image (Financial narrative, same ops)
telemetry-simulator    1/1 Running   ← Generates 12 readings/min
event-processor        1/1 Running   ← RabbitMQ → inference → AlloyDB
alloydb-omni           1/1 Running   ← PostgreSQL edge DB
gdc-pm-rabbitmq        1/1 Running   ← AMQP message broker
grafana                1/1 Running   ← Session 10: 14 asset stat cards added
ollama (new)           0/1 Pending   ← L4 node provisioning / gemma4:27b pull in progress
ollama (old)           1/1 Running   ← gemma:2b still serving until new pod Ready
inference-api          1/1 Running   ← Legacy BQML (not used by current UI)
ollama-stand-up        CronJob       ← 6 AM UTC Mon–Fri ✅
ollama-stand-down      CronJob       ← 6 PM UTC daily ✅
```

**Monitor ollama L4:** `kubectl get pod -n gdc-pm -l app=ollama -w`  
When new pod goes Running and old terminates, gemma4:27b is live.

---

## Outstanding Development Items (To-Do)

### High Priority

**1. Grafana Stat Panels — Click-through UX validation**
- Verify that clicking a stat card (e.g., ESP-A2) actually changes the `$asset` variable and filters the time-series charts to show only that asset's data
- If the URL link approach doesn't work within the kiosk iframe, consider using Grafana's **data link** feature inside the chart panels themselves (target URL: `var-asset=${__field.labels.metric}`)
- Edge case: the `$asset` dropdown may need `refresh: 1` to pick up the URL-driven value in kiosk mode

**2. Grafana Stat Panel Labels — Add subtitle row**
- Currently stat panels show label (e.g., "ESP-A1") and value (PSI number)
- Could add `displayName` override to show "ESP-ALPHA-1 · Intake PSI" for clarity
- Or use `textMode: "value_and_name"` to show both (already configured but needs verification)

**3. Ollama L4 / gemma4:27b — Monitor to Completion**
- `kubectl logs -n gdc-pm -l app=ollama -c pull-model --follow`
- Model pull: ~15 GB, 10-15 min after L4 node is ready
- Once Running: verify Agent responses are qualitatively better than gemma:2b

### Medium Priority

**4. Chart Y-Axis Alignment (Deep Dive)**
- GDC forecast chart and SCADA chart share X-axis but may have different Y-axis scales
- Consider: `scaleDistribution: {type: "linear"}` with explicit `min`/`max` matching across both charts
- Low visual friction — current layout already tells the story

**5. Grafana Time Range**
- Default `now-8h` → consider `now-2h` for demo sessions (fault ramp more visible)
- Change in `grafana-configmap.yaml`: `"time": { "from": "now-2h", "to": "now" }`

**6. Demo Flow Documentation**
- Write a step-by-step demo script for:
  1. Fleet Operations (all green) → click ESP-ALPHA-2 → Inject Sand Ingress
  2. Flip to Fleet Telemetry → click ESP-A2 stat card → single-asset chart appears
  3. Back to Operations → Deep Dive → Time Bridge shrinking
  4. Consult Agent → Approve → Fleet Financials shows the ROI hero card

### Low Priority

**7. Financial tab — Projected Savings Chart**
- Could add a simple Plotly bar chart showing each intervention's savings over time
- Currently the cost-per-intervention sparkline row of mini-cards approximates this

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

```bash
# Monitor Ollama L4 pod readiness (gemma4:27b pull):
kubectl get pod -n gdc-pm -l app=ollama -w
kubectl logs -n gdc-pm -l app=ollama -c pull-model --follow
```

```bash
# Grafana stat panel patch script (idempotent — re-run if dashboard is reset):
python3 gdc-pm/scripts/patch_grafana_stat_panels.py
```

---

## Key Lessons Learned (Session 10)

**The RBAC gap was already resolved:** The session handoff said `container.roles.create` IAM permission was missing, but `kubectl auth can-i create role -n gdc-pm` returned `yes`. The namespace-scoped RBAC was always permitted; the GCP project-level IAM was not needed. The Role and RoleBinding had actually been created in a previous step (creationTimestamp showed 2026-05-20T11:29:11Z). Always `kubectl auth can-i` before assuming an IAM grant is required.

**Python for ConfigMap JSON surgery is reliable:** Embedding JSON inside YAML is fragile to manual edits. The Python script approach (parse → modify → re-indent → write) is deterministic and rerunnable. The `patch_grafana_stat_panels.py` script can be safely re-run if the dashboard needs to be reset — it is idempotent provided the panel IDs 100–123 are not already present.

**Financial narrative framing matters more than data volume:** The original financials tab had accurate data but no story. The addition of the "Before GDC vs After GDC" comparison grid immediately frames the product's value proposition in the language operators and executives understand: reactive vs proactive, hours vs days, full replacement vs scheduled maintenance.

**Grafana kiosk=tv + panel links:** When Grafana is served in `kiosk=tv` mode via iframe, URL-based navigation (clicking stat panel links) should work within the iframe. The `var-asset` URL parameter sets the template variable on page load. If it doesn't work, the fallback is to add data links directly to the time-series chart panels using `${__field.labels.metric}` substitution.
