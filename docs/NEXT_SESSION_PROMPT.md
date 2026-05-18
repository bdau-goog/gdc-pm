# GDC-PM — Session 5 Handoff

**Date:** 2026-05-15  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2` | Cluster: `gdc-edge-simulation` | Namespace: `gdc-pm`  
**Current image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`

---

## What Was Done in Session 4 (Phase 13–14)

### Grafana SCADA Dashboard — Full Redesign + Debugging

A complete redesign of the Grafana dashboard (`gke/grafana/k8s/grafana-configmap.yaml`) was completed to support the core narrative: *"Even a well-designed, functional SCADA monitoring dashboard is reactive by nature — it cannot detect multi-variable fault precursors before SCADA alarm thresholds are breached."*

**Final working state:**
- **Time range:** `now-2h` default
- **SQL:** All 6 timeseries panels use `date_trunc('minute', event_time) AS time` + `GROUP BY 1, asset_id` — native TIMESTAMPTZ output that renders correctly in Grafana 10.4.2
- **Layout:** Fleet Status KPIs → Pressure → Vibration & Temperature → Electrical & Mechanical → ⚡ Edge AI vs SCADA
- **Edge AI Detection Timeline (Panel 9):** tooltip `single` mode (no PSI bleed), `showValue: auto` (state labels visible in blocks), `h:10` (spacious y-axis labels)
- **SCADA Hard-Threshold Breach Log:** Hard physics thresholds only — empty during normal / early-degradation state (this emptiness is the demo point)

**Key lesson learned — DO NOT change:**
- Grafana iframe URL MUST use `?kiosk=tv` (NOT `?kiosk`). Using basic kiosk mode breaks the Vue iframe integration and the timeseries chart renderer silently fails. This caused several hours of debugging.

### UI Improvements
- **Tab reorder:** Fleet Telemetry is now tab 1 and the default view. Demo starts with SCADA view.
- **Field Intelligence panel:** All 10 routine reports are now clickable — opens full-text modal with authentic O&G document content (Maximo WOs, spectroscopic oil analysis, EDR driller's notes, BS&W analysis, directional surveys, VFD calibration logs)
- **↺ All Assets button:** Floating button on Fleet Telemetry tab reloads iframe to reset legend isolation
- **LLM strings updated** to `gemma4:27b` throughout the UI

### Infrastructure Planning
- `gke/ollama/k8s/ollama.yaml`: Updated to target L4 GPU (24GB VRAM), `gemma4:27b` model, 50Gi PVC — **NOT YET APPLIED** to live cluster (requires L4 node pool provisioning)
- `gke/ollama/k8s/ollama-scheduler.yaml`: CronJobs for 6 AM / 6 PM UTC auto-scale — ServiceAccount + CronJobs applied; RBAC Role/RoleBinding needs project admin with `container.roles.create` IAM permission
- `scripts/ollama-stand-up.sh` / `stand-down.sh`: Manual alternatives, work immediately

---

## Cluster State (as of end of Session 4)

```
gdc-edge-simulation / gdc-pm namespace
────────────────────────────────────────
fault-trigger-ui       1/1 Running   ← Primary demo UI + FastAPI backend
telemetry-simulator    1/1 Running   ← Generates 12 readings/min
event-processor        1/1 Running   ← RabbitMQ → inference → AlloyDB
alloydb-omni           1/1 Running   ← PostgreSQL edge DB
gdc-pm-rabbitmq        1/1 Running   ← AMQP message broker
grafana                1/1 Running   ← SCADA telemetry dashboard (http://136.115.220.48)
ollama                 1/1 Running   ← gemma:2b local LLM (deployment env var: gemma:2b)
inference-api          1/1 Running   ← Legacy BQML inference (not used by current UI)
```

**Important:** The live Ollama deployment still has `OLLAMA_MODEL=gemma:2b` patched. The app and YAML show `gemma4:27b` but the actual loaded model is `gemma:2b`. The L4/gemma4 upgrade is YAML-ready but not applied.

---

## What Needs Refinement in Session 5

### 1. Grafana — Time Range Extends Backwards
The current `now-2h` window is a pragmatic working solution. The original design intent was `now-12h` (one full operator shift) to make slow-developing faults like sand ingress (14-day horizon) visible as a very gentle slope over the course of a shift.

**Options to explore:**
- Increase time range to `now-4h` or `now-6h` — test if `date_trunc` queries remain fast
- Or add `WHERE event_time > NOW() - INTERVAL '4 hours'` explicitly in each query as a belt-and-suspenders approach to avoid relying solely on `$__timeFilter`

### 2. Grafana — Spaghetti Lines on Multi-Asset Charts
With all 14 assets visible simultaneously on Vibration and Temperature charts, it's still somewhat cluttered. The legend items work for isolation (click to select) but the initial view is busy.

**Options:**
- Default the `$asset` variable to a specific site (e.g., `ESP-ALPHA-1`) and let users expand
- OR add separate panels per site type (ESP-only pressure, Gas Lift-only pressure, etc.) instead of all-in-one
- The `?kiosk=tv` constraint means the `$asset` variable dropdown is inaccessible from the embedded iframe — the only filter mechanism is the chart legend

### 3. Gemma 4 / L4 GPU Upgrade
The YAML files are ready. Pending:
1. Project admin runs: `gcloud projects add-iam-policy-binding gdc-pm-v2 --member="serviceAccount:dev-workstation-sa@gdc-pm-v2.iam.gserviceaccount.com" --role="roles/container.developer"`
2. Then: `kubectl apply -f gke/ollama/k8s/ollama-scheduler.yaml` (for RBAC)
3. Provision an L4 GPU node pool in the GKE cluster
4. Apply the updated `ollama.yaml` — first startup will pull `gemma4:27b` (~15GB, 5–15 min)
5. Patch the deployment: `kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_MODEL=gemma4:27b`

### 4. Field Intelligence Panel — Dynamic Integration
Currently the 10 routine report cards are hardcoded in `FIELD_INTEL_ITEMS` in `index.html`. They are realistic and clickable, but static.

**Future enhancement:** Serve these from a new API endpoint `/api/field-intelligence` that could pull from AlloyDB (pre-seeded unstructured documents) or from the RAG pipeline. This would make the Field Intelligence panel update dynamically when a fault is detected — showing only the documents relevant to the active asset's fault type.

### 5. Demo Flow Polish
A few UX refinements observed during Session 4 testing:
- The `Fleet Telemetry` tab shows all assets — a presenter tip would be to **click a specific legend item** (e.g., `GLIFT-BRAVO-1`) right before launching the Sand Ingress demo to isolate that asset, making the "clean/green" baseline obvious before the fault is injected
- The `⚡ GDC Edge AI Detection Timeline` is the "reveal" panel — the orange block appearing while the SCADA Log stays empty is the visual proof point. Consider whether this needs a title update or annotation arrow.

---

## Demo Script (Current Working Flow)

1. Open http://35.188.3.97 → opens on **Fleet Telemetry** tab (Grafana SCADA view)
2. Point out: "This is what a real operator sees. Active Assets: 14. SCADA Hard-Limit Alarms: 0. Everything green."
3. Scroll down to **⚡ Edge AI vs SCADA** section
4. Point out: "Two panels here. The top one shows what the AI has already detected. The bottom is the traditional SCADA alarm log. Notice the SCADA log may already be empty while the AI timeline shows orange bars."
5. Click **Fleet Operations** tab → Dashboard loads
6. Click a Demo Scenario card (e.g., **Sand Ingress — Supply Chain Lead Time**)
7. Deep Dive opens, fault injection auto-starts, Intelligence Feed populates
8. Chart auto-switches to Vibration tab (primary sensor), shows rising projection curve
9. Switch back to **Fleet Telemetry** — sensors still look normal on the charts
10. Scroll to Edge AI vs SCADA section — orange bar appeared, SCADA log still empty
11. Back to **Fleet Operations** → "💬 Consult Operations Agent" → rule-based recommendation fires, Gemma streams
12. Click "✔ Approve & Execute" → outcome card, net savings shown
13. Click **Fleet Financials** → ledger entry appears

---

## Constraints — Do Not Violate
- **Never apply `terraform/gke.tf`** — destroys the live cluster
- **Never change iframe to `?kiosk`** — must stay `?kiosk=tv` for chart rendering stability
- **Only edit:** `gke/fault-trigger-ui/app.py`, `gke/fault-trigger-ui/index.html`, `gke/grafana/k8s/grafana-configmap.yaml`
- Gemma keepalive thread is in `app.py` — this prevents cold starts during demos
- XGBoost health models (`*.ubj`) are validated — do not retrain without specific reason
