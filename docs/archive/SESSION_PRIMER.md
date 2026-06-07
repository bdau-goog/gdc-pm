# GDC-PM — Session Primer

**Live URL:** http://35.188.3.97  
**Cluster:** `gdc-edge-simulation` / namespace `gdc-pm` / region `us-central1`  
**Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**LLM:** `gemma:2b` running on existing node. `gemma:27b` is configured in the Ollama deployment YAML; the NAP is actively provisioning an L4 GPU node in `us-central1-c` (old PVC was zone-locked to `us-central1-f` which does not support L4 — fixed in this sprint). Once the node provisions, the init container will auto-pull the 15 GB model.

---

## What the app is

GDC Predictive Maintenance demo — Edge AI for upstream O&G.  
14 assets across 3 sites (Pad Alpha ESPs, Pad Bravo Gas Lift, Rig 42 Drilling).  
Detects faults from multi-modal data fusion (sensor telemetry + lab reports + shift logs + Maximo PM records) **before** SCADA alarms fire.

Stack: FastAPI backend + Vue 3 (CDN, Options API) + Plotly.js + XGBoost health models + Ollama/gemma.  
Only edit `gke/fault-trigger-ui/app.py` and `gke/fault-trigger-ui/index.html`.  
**Never apply `terraform/gke.tf`** — it destroys the live cluster.

---

## Current state (Phase 16 — as of 2026-05-20)

### Application Architecture

**Tab order:** Fleet Operations (default) → Fleet Financials → Fleet Telemetry

**Fleet Operations:**
- **Phase 15 Dual-Reality Fleet Canvas:** 3 site zones (Pad Alpha, Pad Bravo, Rig 42) with distinct asset node shapes (ESP=circle, Gas Lift=oval, Mud Pump=squircle, Top Drive=lobe). Click asset → context menu with fault injection + mini sensor grid.
- **Activity Stream** (right side, resizable via drag splitter): Live AI alerts at top + rotating field intel documents (10 hardcoded + LLM-generated via `/api/field-intelligence`).
- **Deep Dive view:** Vertical stack → GDC AI Forecast chart (top) → Time Advantage Bridge bar (middle) → Traditional SCADA chart (bottom). Then 3-column bottom panels: Evidence & Intelligence | GDC Ops Agent | Resolution & Action.

**Deep Dive specifics:**
- **Sensor selector tabs** are on the **GDC AI chart header** (right side, after flex spacer). Selecting a tab re-renders BOTH charts simultaneously.
- **Compare row resize handle:** Drag to resize chart area vs. bottom panels. Double-click to toggle between 430px split and 88% full-screen. Persisted in `sessionStorage`.
- **Column resizers** between bottom panels (Evidence ↔ Agent ↔ Resolution). Drag to resize, double-click to reset defaults. Persisted in `sessionStorage`.
- **initialRulMap:** Per-asset dictionary preserving the original GDC advance notice. Navigating to fleet and back does NOT reset the "X advance notice given by GDC" value.
- **SCADA chart:** Shows Live Telemetry + SCADA Alarm Threshold traces only (no AI projections). X-axis capped at NOW; Y-axis mirrors GDC chart scale for direct visual comparison. Fixed: `gdcLayout` is now hoisted to outer scope in `renderChart()`.
- **Bridge bar label:** `"X until SCADA detection — Y advance notice given by GDC"` where Y is the original captured advance notice (from `initialRulMap`).

### Grafana (`gke/grafana/k8s/grafana-configmap.yaml`)
- **Default time range:** `now-2h`
- **Pressure units:** All pressure stat panels (ESP-A1–A6, Avg ESP Intake) use `"unit": "psi"` — prevents Grafana auto-scaling from ksi to PSI. Display names set to `"ESP Intake Pressure (PSI)"`.
- **Timeseries panels** (ESP panel 5, Gas Lift 31, Mud Pump 32): also use `"unit": "psi"` (not `pressurepsi` which auto-scales to ksi).

### Ollama / gemma:27b
- **Status:** Deployment YAML configured for `gemma:27b` on L4 GPU (`g2-standard-4`).
- **Previous issue:** PVC `ollama-models-pvc` was zone-locked to `us-central1-f` which does NOT support NVIDIA L4. Fixed by deleting the PVC and letting GKE NAP provision a fresh one in `us-central1-c`.
- **Current:** NAP is actively trying to provision in `us-central1-c` (L4-capable). Once the node is available, init container pulls `gemma:27b` (~15 GB, ~10 min). `gemma:2b` is NOT available anymore (old PVC deleted). Until gemma:27b pulls, agent responses use the rule-based fallback.
- **Cost:** L4 GPU node ~$0.65/hr. The `ollama-scheduler` CronJobs manage stand-up (6 AM UTC Mon–Fri) / stand-down (6 PM UTC daily).

---

## Key APIs

| Endpoint | Purpose |
|---|---|
| `GET /api/horizon` | Active AI predictions (dashboard) |
| `GET /api/kpis` | Live site KPIs with fault degradation |
| `GET /api/degrade-status/{asset_id}` | Per-asset fault health + time_to_scada |
| `GET /api/intelligence-feed/{asset_id}?fault_type=X` | Unstructured data feed per fault |
| `GET /api/resolution-actions/{fault_type}?rul_minutes=N` | 4-tier remediation options |
| `GET /api/financial-justification/{fault_type}` | Itemized cost breakdown |
| `GET /api/agent/recommend-stream` | SSE streaming agent (rule-based + Gemma tokens) |
| `GET /api/plot/forecast-data/{asset_id}` | JSON Plotly traces for all sensor tabs |
| `GET /api/field-intelligence?limit=N` | LLM-generated rotating field intel documents |
| `POST /api/inject/degrade` | Start fault injection simulation |
| `POST /api/cancel-degrade/{asset_id}` | Reset/clear active fault |
| `POST /api/agent/hitl-approve` | Record intervention approval + cost savings |

---

## Rebuild & deploy

```bash
cd /home/brian/gdc-pm
bash gke/fault-trigger-ui/start-fault-trigger-ui.sh
# OR manually:
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=180s
```

## Grafana deploy (no app rebuild needed)

```bash
kubectl apply -f gdc-pm/gke/grafana/k8s/grafana-configmap.yaml
kubectl rollout restart deployment/grafana -n gdc-pm
kubectl rollout status deployment/grafana -n gdc-pm --timeout=90s
```

## Check gemma:27b status

```bash
kubectl get pods -n gdc-pm -l app=ollama -o wide
kubectl get events -n gdc-pm --sort-by='.lastTimestamp' | grep -E "ollama|ScaleUp|TriggeredScale" | tail -10
kubectl logs -n gdc-pm -l app=ollama -c pull-model --tail=20
# Once running:
kubectl exec -n gdc-pm deployment/ollama -- ollama list
```

---

## What's next — Session 6 (UI Testing & Refinement)

See `docs/NEXT_SESSION_PROMPT.md` for the full handoff.  
See `docs/CHANGELOG.md` for full history of decisions and changes.
