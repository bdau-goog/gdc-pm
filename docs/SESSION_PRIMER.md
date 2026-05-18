# GDC-PM — Session Primer

**Live URL:** http://35.188.3.97  
**Cluster:** `gdc-edge-simulation` / namespace `gdc-pm`  
**Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**LLM:** `gemma:2b` (live cluster still using gemma:2b — `OLLAMA_MODEL=gemma:2b` patched on deployment. The YAML is updated for `gemma4:27b` on L4 GPU but that upgrade requires a new L4 node pool to be provisioned.)

---

## What the app is

GDC Predictive Maintenance demo — Edge AI for upstream O&G.  
14 assets across 3 sites (Pad Alpha ESPs, Pad Bravo Gas Lift, Rig 42 Drilling).  
Detects faults from multi-modal data fusion (sensor telemetry + lab reports + shift logs + Maximo PM records) before SCADA alarms.

Stack: FastAPI backend + Vue 3 (CDN, Options API) + Plotly.js + XGBoost health models + Ollama/gemma:2b.  
Only edit `gke/fault-trigger-ui/app.py` and `gke/fault-trigger-ui/index.html`.  
**Never apply `terraform/gke.tf`** — it destroys the live cluster.

---

## Current state (as of Phase 14 / Session 4)

### Main Application (`index.html` + `app.py`)
- **Tab order:** Fleet Telemetry (default, loads first) → Fleet Operations → Fleet Financials
- **Fleet Telemetry tab:** Grafana iframe loads immediately on app open (`loadGrafana()` in `mounted()`). Kiosk mode: `?kiosk=tv` (stable chart rendering — do NOT change to `?kiosk`).
- **↺ All Assets button:** Floating button in bottom-right of Fleet Telemetry tab reloads iframe to reset legend isolation
- **Fleet Operations tab (formerly "Operations"):** 3-column layout — Fleet (360px) | Field Intelligence (310px) | Predictive Horizon (flex)
- **Field Intelligence panel:** 10 routine O&G reports, all clickable → opens feed-detail modal with full document text + AI relevance annotation
- **6 demo scenarios:** 3 ESP + 2 Gas Lift + 1 Mud Pump; all auto-inject and stream Intelligence Feed on click
- **Deep Dive:** Fault injection + ML forecast chart + Intelligence Feed + Gemma findings
- **Copilot panel:** 250px narrow chat + wide HITL panel showing all 4 remediation tiers (Early/Urgent/Critical/Post-PNR)
- **Craft Fault button:** in Deep Dive header, opens modal to inject any fault type/duration on any asset
- **ⓘ Cost Basis button:** in HITL panel, opens Financial Justification Modal with OEM-sourced itemized cost breakdown
- **LLM display:** Shows `gemma4:27b` in UI (pending actual L4 upgrade); live cluster still uses `gemma:2b`

### Grafana Dashboard (`gke/grafana/k8s/grafana-configmap.yaml`)
- **Narrative purpose:** "Well-designed SCADA monitoring is still blind to precursors"
- **Default time range:** `now-2h` — enough to see recent activity, queries complete in <1s
- **SQL bucketing:** All 6 timeseries panels use `date_trunc('minute', event_time)` (native TIMESTAMPTZ, renders correctly in Grafana 10.4.2)
- **Layout:** Fleet Status KPIs → Pressure → Vibration & Temperature → Electrical & Mechanical → **⚡ Edge AI vs SCADA**
- **Edge AI Detection Timeline (Panel 9):** Tooltip `single` mode (no PSI bleed), `showValue: auto` (state labels in blocks), `h:10` (comfortable labels)
- **SCADA Hard-Threshold Breach Log:** Fires ONLY on hard physics thresholds (PSI < 800, temp > 230°F, etc.) — empty in normal state, which is the demo point
- **Asset legend isolation:** Click a legend item to isolate one asset; click again to restore all

---

## Key APIs

| Endpoint | Purpose |
|---|---|
| `GET /api/horizon` | Active AI predictions (dashboard) |
| `GET /api/kpis` | Live site KPIs with fault degradation |
| `GET /api/intelligence-feed/{asset_id}` | Unstructured data feed per fault |
| `GET /api/resolution-actions/{fault_type}` | 4-tier remediation options with viability |
| `GET /api/financial-justification/{fault_type}` | Itemized cost breakdown for objection handling |
| `GET /api/agent/recommend-stream` | SSE streaming agent (rule-based + Gemma tokens) |
| `GET /api/plot/forecast-data/{asset_id}` | JSON Plotly traces for all sensor tabs |

---

## Rebuild & deploy

```bash
cd /home/brian
docker build --quiet -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gdc-pm/gke/fault-trigger-ui/
docker push --quiet us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=180s
```

## Grafana deploy (dashboard JSON only — no app rebuild needed)

```bash
kubectl apply -f gdc-pm/gke/grafana/k8s/grafana-configmap.yaml
kubectl rollout restart deployment/grafana -n gdc-pm
kubectl rollout status deployment/grafana -n gdc-pm --timeout=90s
```

## Ollama stand-up/stand-down (cost management)

```bash
# Manual:
./gdc-pm/scripts/ollama-stand-up.sh    # scale to 1 replica (starts L4 billing)
./gdc-pm/scripts/ollama-stand-down.sh  # scale to 0 replicas (stops L4 billing)

# Automated CronJobs (6 AM UTC up, 6 PM UTC down) — requires RBAC Role to be applied:
# See gke/ollama/k8s/ollama-scheduler.yaml comments for prerequisite IAM grant
```

---

## What's next — refinements for Session 5

See `docs/NEXT_SESSION_PROMPT.md` for the full handoff.  
See `docs/CHANGELOG.md` for full history of decisions and changes.
