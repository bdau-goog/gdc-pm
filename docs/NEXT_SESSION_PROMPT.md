# GDC-PM — Session 10 Handoff

**Date:** 2026-05-20  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2` | Cluster: `gdc-edge-simulation` | Namespace: `gdc-pm`  
**Current image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Git head:** `de7477d` (master — working tree clean, all changes committed)

---

## What Was Done in Session 9

### 1. Deep Dive Layout — Vertical Stacked Redesign (deployed, live)

The Deep Dive event detail panel Row 1 was restructured from a horizontal side-by-side layout to a vertical stack that aligns X-axes for maximum narrative impact.

**New vertical order (430px total height):**
- **Top (flex:1) — GDC Edge AI Forecast:** Orange forecast with RUL projection, PNR marker, SCADA alarm marker, confidence cone. Includes new **ⓘ info button** in the header.
- **Middle (46px fixed) — Horizontal Time Advantage Bridge:** When fault is active shows `⚡ GDC Detected → [progress bar shrinking] → ⛔ SCADA Alarm` with the lead time remaining in monospace. Bar width is calculated from `initialRulMinutes` (captured on first detection) and shrinks live as time elapses.
- **Bottom (flex:1) — Traditional SCADA:** Historical-only chart, X-axis capped at "Now", all shapes/annotations stripped, title hard-coded to "✓ STATUS NORMAL."

**Key implementation notes:**
- `showAiFactors: false` + `initialRulMinutes: null` added to Vue data
- `aiFactors` computed: reads `SENSOR_LABELS[aclass]` for the current fault type — lists PSI, Temp, Vib, and optionally Amps/SPM depending on asset class
- `bridgeBarPct` computed: `(time_to_scada_minutes / initialRulMinutes) * 100` — starts at 100%, shrinks on every poll
- `fetchDegradeStatus()` now captures `initialRulMinutes` on first non-null active reading
- `resetAsset()` now clears `initialRulMinutes = null` and `showAiFactors = false`

### 2. AI Factor ⓘ Decoration (deployed, live)

Orange circle button in the GDC Edge AI chart header. Clicking shows a popover listing:
- The exact numerical sensor features the XGBoost RUL model reads (asset-class specific)
- Footer copy: *"Deterministic ML: multivariate sensor correlation, not single-threshold rules. The Agent chat additionally reasons over field documents and maintenance records."*
- Dismisses on click-away to the compare row
- Uses `CSS classes: .ai-factors-btn, .ai-factors-popover, .afp-title, .afp-row, .afp-footer`

### 3. Tab Reordering (deployed, live)

- Default tab changed to **Fleet Operations** (was Fleet Telemetry)
- Tab order: **Fleet Operations** | **Fleet Financials** | Fleet Telemetry (dimmed, opacity 0.7)
- `mainTab: 'operations'` in Vue data (was `'telemetry'`)

### 4. Grafana Fleet Telemetry — Site-Zone Grouping (deployed, live)

Dashboard restructured from sensor-type rows to operator-centric site rows:
- **🛢 Pad Alpha — ESP Production** (y=5): Intake PSI, Motor Winding Temp, Motor Current (A), Vibration
- **🛢 Pad Bravo — Gas Lift Production** (y=24): Discharge PSI, Discharge Temp, Vibration
- **🏗 Rig 42 — Drilling** (y=34): Mud Pump Discharge PSI (**new panel ID 32**), Stroke Rate SPM, Rig 42 Vibration, Rig 42 Temperature
- **⚡ Edge AI vs SCADA** (y=53): unchanged — AI Detection Timeline + SCADA Breach Log

New Mud Pump PSI panel queries `MUD-%` assets with correct thresholds (LOW: 1,800 PSI, HIGH: 3,800 PSI).

### 5. Gemma 4 / L4 GPU Upgrade (applied, L4 provisioning in progress)

- Applied `ollama.yaml`: PVC expanded to 50Gi, Deployment updated to target `cloud.google.com/gke-accelerator: nvidia-l4` with `gemma4:27b` init-container model pull
- Applied `ollama-scheduler.yaml`: CronJobs for stand-up (6 AM UTC weekdays) and stand-down (6 PM UTC daily) configured. **Note:** RBAC Role + RoleBinding creation failed — `container.roles.create` IAM permission not granted. ServiceAccount and CronJobs exist; admin needs to grant `roles.create` and `roleBindings.create` for the scheduler to function.
- Set UI env vars: `OLLAMA_MODEL=gemma4:27b OLLAMA_DISPLAY_MODEL=gemma4:27b`
- **Current state:** New ollama pod (`ollama-77f99db54d-*`) is Pending while GKE Autopilot provisions the L4 node (~3-5 min provisioning, then 10-15 min for init container to pull 15GB model). Old gemma:2b pod (`ollama-8ffc6bd5b-*`) is still Running and serving requests until the new one is Ready.

---

## Current Cluster State

```
gdc-edge-simulation / gdc-pm namespace
────────────────────────────────────────
fault-trigger-ui       1/1 Running   ← Session 9 image (vertical Deep Dive, gemma4:27b env)
telemetry-simulator    1/1 Running   ← Generates 12 readings/min
event-processor        1/1 Running   ← RabbitMQ → inference → AlloyDB
alloydb-omni           1/1 Running   ← PostgreSQL edge DB
gdc-pm-rabbitmq        1/1 Running   ← AMQP message broker
grafana                1/1 Running   ← Session 9 site-zone dashboard
ollama (new)           0/1 Pending   ← L4 node provisioning / gemma4:27b pull in progress
ollama (old)           1/1 Running   ← gemma:2b still serving until new pod Ready
inference-api          1/1 Running   ← Legacy BQML (not used by current UI)
```

**IMPORTANT:** Monitor ollama pod: `kubectl get pod -n gdc-pm -l app=ollama -w` — when new pod goes Running AND passes readiness probe, old pod will terminate. Model pull takes 10-15 min on first run (15GB download). Once L4 pod is stable, set `OLLAMA_DISPLAY_MODEL=gemma4:27b` is already done.

**RBAC gap:** The Ollama scheduler's Role + RoleBinding could not be created due to missing `container.roles.create` IAM permission on `dev-workstation-sa`. An admin needs to either:
1. Grant `roles/container.developer` → `container.roles.create` or run `kubectl create role/rolebinding` directly with a privileged account
2. Or: The CronJobs exist but will fail on execution until this is resolved

---

## Outstanding Development Items (To-Do)

### High Priority

**1. Grafana Fleet Telemetry — Match Fleet Operations Look & Feel (pure Grafana, no HTML wrapper)**
- **Goal:** The Grafana dashboard (which fills the Fleet Telemetry tab via iframe) should itself replicate the operator-centric layout of the Fleet Operations tab. No HTML/Vue in front of it — all changes inside `grafana-configmap.yaml`.
- **Target experience:** Site zone "cards" (Pad Alpha / Pad Bravo / Rig 42), per-asset stat panels showing current sensor values and health, and click-through to that asset's time-series charts using the existing `$asset` variable.
- **Grafana features to use:**
  - **Stat panels per asset** (e.g., a row of 6 stat panels for ESP-ALPHA-1 through ESP-ALPHA-6 showing current PSI/health — green = nominal, orange = AI alert, red = SCADA breach)
  - **Row panels** as site-zone section headers (already in place)
  - **`$asset` variable** pre-set to "All" by default; operator clicks a stat panel that links to a filtered URL to drill into one asset's charts
  - **Text panels** for site-zone descriptions if needed
  - **Panel links:** stat panels can be configured with a `dashboardUID` link that sets `var-asset=ESP-ALPHA-2` — simulating the "click asset → see its telemetry" behaviour entirely within Grafana
- **The spaghetti problem:** Current charts show all assets as overlapping lines. When `$asset` is set to a specific asset via URL or dropdown, each chart shows only one clean line. The refactoring should make the dropdown selection the primary interaction.
- File: `gke/grafana/k8s/grafana-configmap.yaml`
- Deploy: `kubectl apply -f ... && kubectl rollout restart deployment/grafana -n gdc-pm`

**2. Financial Story — Tighten the Narrative**
- The Fleet Financials tab shows a ledger but the story is currently "loose"
- Consider: a front-page summary card with a single ROI number, and a clear "before GDC vs. after GDC" framing
- Ideas: projected annual savings extrapolation, fleet-level uptime bar chart, cost-per-intervention trend
- The session owner wants a cleaner, more persuasive financial narrative
- File: `gke/fault-trigger-ui/index.html` (financials tab)

**3. Ollama Scheduler RBAC (requires admin)**
- Grant `container.roles.create` / `container.roleBindings.create` to `dev-workstation-sa@gdc-pm-v2.iam.gserviceaccount.com`
- Then re-apply: `kubectl apply -f gke/ollama/k8s/ollama-scheduler.yaml`
- This enables automated L4 stand-up/stand-down to save ~78% GPU costs

### Medium Priority

**4. Demo Flow Review**
- With the new vertical layout, verify the Deep Dive demo flow at http://35.188.3.97:
  1. Fleet Operations (all green) → Click ESP-ALPHA-2 → Inject Sand Ingress
  2. Watch the Time Bridge bar populate and shrink in real time
  3. Note the ⓘ popover lists the exact XGBoost input features
  4. Both charts share the same Y-axis range and X-axis scale — the gap is visually undeniable
  5. Consult Agent → Approve
- Check that `bridgeBarPct` renders the full bar at injection and shrinks over the 1-hour session

**5. Chart Y-Axis Alignment (optional enhancement)**
- Currently the GDC forecast chart and SCADA chart may have different Y-axis scales
- Consider: shared Y-axis scaling so the two charts are directly comparable at a glance
- Lower priority — the current layout already tells the story clearly

### Low Priority

**6. Grafana Time Range Tweak**
- Consider using `now-2h` for the default view during live demos (fault ramp is more visible in 2h window)
- Currently set to `now-8h`

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

---

## Key Lessons Learned (Session 9)

**Vertical chart stacking eliminates interpretation friction:** When SCADA and AI charts share the X-axis (time axis) and are stacked top-to-bottom rather than side-by-side, the audience can immediately compare "what AI sees" vs "what SCADA sees" at exactly the same point in time. The old horizontal layout required horizontal eye movement; the vertical layout requires only a straight down glance.

**The Time Bridge bar is the "money shot" for the demo:** Having a concrete, animated visual showing the shrinking lead time is far more persuasive than a number in a header badge. The bar going from 100% → 60% → 20% over the course of a demo tells the story that time is genuinely being consumed — and that without GDC, all of that lead time would be lost.

**ⓘ Data Fusion Transparency builds credibility:** The ⓘ popover addresses the most common skeptical question in predictive maintenance demos: "How does the AI actually know?" Listing the exact sensor inputs (Intake Pres., Winding Temp., Vibration, Motor Current) and explicitly stating "deterministic ML, not LLM" distinguishes GDC from AI-washing and positions the product honestly.

**GKE Autopilot + L4 GPU provisioning:** Unlike standard GKE, Autopilot creates nodes on-demand when pods request specific accelerator resources. The `cloud.google.com/gke-accelerator: nvidia-l4` nodeSelector triggers this. First provisioning takes 3-5 min; model pull adds another 10-15 min. Subsequent restarts skip the pull (PVC caches the model).
