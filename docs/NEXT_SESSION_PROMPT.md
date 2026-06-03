# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `098afa0`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `098afa0` (Clean working tree)
**Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest` (deployed June 3, 2026 — 3-Horizon Overhaul)

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""

# 3. API truth
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"

# 5. Check new Vizier endpoint works
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize?oil_price=112&horizon_days=90" | python3 -c "import sys,json;d=json.load(sys.stdin);print('trials:',len(d.get('trials',[])), 'optimal_hz:',d.get('optimal_hz'))"
```

**Expected results when healthy:**
- All pods: `1/1 Running` (fault-trigger-ui ~fresh from today's deploy)
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows** ✅
- field_intel: **100 rows** ✅
- fault_sessions: **4 rows** ✅
- Vizier: `trials: 15 optimal_hz: 54.5` ✅

---

## ⚠️ Known Integrity State (VERIFIED June 3, 2026)

| Item | Display Says | Reality | Status |
|------|-------------|---------|--------|
| Gemma model | "Gemma 4 8B" | `gemma4:latest` (8B, 128K context) | ✅ CLEAN |
| Architecture tab | v5 live | Full-width panes, ⓘ popups | ✅ |
| Grafana URL | 35.190.137.145 | Live Grafana LB IP | ✅ Fixed |
| Horizon 1 tab | Gas Lock UI | ESP-ALPHA-1, PNR 25min | ✅ Live |
| Horizon 2 tab | Slug Flow UI | ESP-ALPHA-3, truck roll timer | ✅ Live |
| Horizon 3 tab | Vizier UI | 15 Bayesian trials, Pareto chart | ✅ Live |
| slug_flow fault | In simulator | vibration drift, nominal motor temp | ✅ |
| Vizier optimal_hz | 54.5 Hz | Bayesian converged result at $112/bbl, 90d | ✅ |
| GPU CronJobs | SUSPENDED ✅ | Manual only | ✅ |

---

## Ollama PVC Model Inventory

```
gemma4:latest    9.6 GB   ← ACTIVE (running)  Gemma 4 8B, 128K ctx
gemma3:27b       17 GB    ← fallback           Gemma 3 27B
gemma4:31b       19 GB    ← READY (downloaded) Gemma 4 31B, 128K ctx (upgrade candidate)
```

---

## NEXT SESSION PLAN — Horizon UI Polish & Integration Testing

| Fix | Change | Verification | Est. complexity |
|-----|--------|--------------|-----------------|
| H1 Live Charts | Verify h1-gdc-chart and h1-scada-chart render correctly when fault is injected | Click "Inject Gas Lock" → chart appears within 10s | Small |
| H2 Truck Roll Timer | Test 5-second countdown completes and vibration resets | Click "Dispatch Truck Roll" → resolved in 5s | Small |
| H3 Slider Reactivity | Test Oil Price and Horizon sliders re-trigger Vizier optimization | Drag slider → trial table updates | Small |
| H1 Motor Amps Card | Wire live motor_amps value to h1SensorAmps card in Horizon 1 | h1SensorAmps shows declining value when gas lock active | Small |
| slug_flow Intelligence Feed | Add canned feed items for slug_flow to INTELLIGENCE_FEED dict in app.py | Horizon 2 shows 3+ feed items with RAG context | Medium |
| RAG Prompt for slug_flow | Confirm Gemma finding for slug_flow is meaningful | h2GemmaFinding contains vibration + motor temp reference | Small |
| Pareto Chart Clickthrough | Add hover tooltip showing VFD Hz, Cash Flow, RUL on Pareto | Hover over scatter point → tooltip appears | Small |

---

## What Was Done This Session (June 3, 2026)

*   **3-Horizon Architecture** — Replaced old Fleet Operations + Fleet Telemetry tabs with 3 dedicated Horizon tabs (Horizon 1: Gas Lock, Horizon 2: Slug Flow, Horizon 3: Vizier Optimization).

*   **Horizon 1 (Gas Lock)** — SCADA vs GDC value cards, live GDC AI forecast chart + SCADA historical chart, VFD approval button with $147,500 savings, live RAG feed from AlloyDB, polling loop.

*   **Horizon 2 (Slug Flow)** — Slug flow vibration drift scenario (1.1→2.4 mm/s), motor temp remains nominal (O&G defensible physics), 5-second truck roll countdown timer, RAG troubleshooting guide text, $148,500 savings narrative.

*   **Horizon 3 (Vizier Optimization)** — Bayesian optimization over 15 trials, real Net Cash Flow model (Revenue − Power Costs − $150k ESP burnout penalty), interactive sliders (oil price, horizon), Pareto scatter plot via Plotly, trials log table.

*   **Backend APIs** — `/api/vizier/optimize`, `/api/vizier/deploy`, `/api/agent/truck-roll`, `/api/agent/truck-roll-status`.

*   **Simulator** — Added `slug_flow_reading()` fault generator with physically correct sensor profile (vibration rises, motor temp flat, motor amps nominal).

*   **Deployed & Verified** — Both `fault-trigger-ui` and `telemetry-simulator` pods rebuilt, pushed, and rolled out. Vizier API confirmed working: 15 trials, optimal_hz=54.5.

---

## Current Cluster State (VERIFIED June 3, 2026)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   0   5d15h
event-processor-7d9b594b6b-j5jp8        1/1   Running   0   5d15h
fault-trigger-ui-846895c64d-j7zmt       1/1   Running   0   <2m  ← NEW (3-Horizon)
gdc-pm-rabbitmq-server-0                1/1   Running   0   5d15h
grafana-655b6f5c7c-w2h84                1/1   Running   0   5d15h
inference-api-5697b79566-zqdpl          1/1   Running   0   5d15h
ollama-5bc5db749b-n6tb8                 1/1   Running   0   5d12h
telemetry-simulator-867677f784-h55wd    1/1   Running   0   <2m  ← NEW (slug_flow)
```

---

## Outstanding Development Items (Backlog)

**High Priority**
1. **slug_flow Intelligence Feed** — INTELLIGENCE_FEED dict in app.py has no `slug_flow` key; the RAG feed pane shows empty in H2. Add 2–3 realistic field docs referencing flowline slugging, choke adjustment, and motor temp sentinel. One-liner: add `"slug_flow": [...]` block matching existing feed format.
2. **H1 Motor Amps live binding** — `h1SensorAmps` is not wired to current_sensors polling; shows static "64.1 A". Wire in `launchHorizon1` polling interval.

**Medium Priority**
3. **Pareto chart tooltip** — Currently hover shows raw coordinates. Add `hovertemplate` with Hz, Cash Flow ($M), RUL (d) labels.
4. **Deploy VFD feedback** — After clicking "Deploy Recommendation", show what Hz will be applied and a brief confirmation dialog.
5. **Gemma Horizon 1 narrative** — The h1GemmaFinding is pulled from existing gas_lock GEMMA_FINDINGS. May need to trigger the agent streaming endpoint to generate something richer.
6. **Merge `feature-trio-scenarios` → `main`** — Once UI polish is complete, create PR and merge.

**Low Priority**
7. **Upgrade to gemma4:31b** — Change `OLLAMA_MODEL=gemma4:31b` env var to test higher quality reasoning on Horizon scenarios.
8. **Horizon 3 — RAG constraint** — Add a block to the Vizier prompt that retrieves max motor temperature limits from OEM manuals via pgvector, constraining the Bayesian search space.

---

## Constraints

- `terraform/gke.tf` must NOT be applied — would destroy the live cluster.
- All demo changes go into `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`.
- After changes: `docker build → docker push → kubectl rollout restart`.
- No browser available on SSH remote — no `browser_action` tool.
- XGBoost `*.ubj` models are correct and validated. Do not retrain without explicit reason.
- Existing `/api/*` endpoints remain backward-compatible.

---

## Rebuild & Deploy Commands

```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

If simulator.py changed:
```bash
docker build -t ${REGISTRY}/telemetry-simulator:latest gke/telemetry-simulator
docker push ${REGISTRY}/telemetry-simulator:latest
kubectl rollout restart deployment/telemetry-simulator -n gdc-pm
kubectl rollout status deployment/telemetry-simulator -n gdc-pm
```

---

## Key Lessons Learned

- **O&G Domain Realism enforced**: "loose wellhead bolts" scenario was rejected (sensor placement on downhole motor block means surface mechanical looseness doesn't show in downhole vibration). Replaced with flowline slug flow hydraulics — physically sound and defensible to any production engineer.
- **Three-horizon architecture** cleanly maps to near-term (gas lock emergency), mid-term (ambiguous inconclusive telemetry requiring field dispatch), and long-term (capital allocation optimization under market conditions). This is the correct framing for a predictive maintenance ROI story.
- **Vizier Bayesian economic model**: net cash flow = Revenue − Power Costs − $150k CAPEX penalty if RUL < horizon. At $112/bbl and 90-day horizon, optimal_hz = 54.5 (vs 50.0 SCADA nominal). Higher Hz → more barrels but exponentially shorter RUL. The $150k penalty correctly punishes aggressive run-to-failure strategies.
- **Tab architecture**: Removing Fleet Telemetry (Grafana iframe) reduced UI complexity without losing any capability (Grafana accessible separately). Three focused Horizon tabs > one generic operations tab for demo storytelling.
