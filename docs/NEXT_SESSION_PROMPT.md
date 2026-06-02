# Next Session Prompt — GDC Edge AI 3-Horizon Demo Overhaul Blueprint

## Header
**Date:** June 2, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch — *Note: Next session should checkout new branch `feature-trio-scenarios`*)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `0ecb1e76f9ae852ebd3d514ead5d90f08578a77e` (Clean working tree)
**Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest` (deployed June 2, 2026 — Gemma 4 8B)

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 0. Checkout new feature branch
cd ~/gdc-pm && git checkout -b feature-trio-scenarios

# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""

# 3. API truth
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"

# 5. Check Ollama PVC models
kubectl exec -n gdc-pm deployment/ollama -- ollama list
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest` (Note: we will upgrade OLLAMA_MODEL to `gemma4:31b` env var during Scenario 3 implementation)
- rag_documents: **18 rows** ✅
- field_intel: **100 rows** ✅
- fault_sessions: **4 rows** ✅

---

## ⚠️ Known Integrity State (VERIFIED June 2, 2026)

| Item | Display Says | Reality | Status |
|------|-------------|---------|--------|
| Gemma model | "Gemma 4 8B" | `gemma4:latest` (8B, 128K context) | ✅ CLEAN |
| Architecture tab | v5 live | Full-width panes, ⓘ popups, SCADA subscriber | ✅ |
| Grafana URL | 35.190.137.145 | Live Grafana LB IP | ✅ Fixed |
| Field Link badge | "Field Link" | WAN state indicator | ✅ |
| Guided Tour values | Static (Health: 0.34) | Illustrative | Acceptable |
| rag_documents | 18 rows ✅ | Healthy | ✅ |
| field_intel | 100 rows ✅ | Active | ✅ |
| fault_sessions | 4 rows ✅ | Working | ✅ |
| GPU CronJobs | SUSPENDED ✅ | Manual only | ✅ |

---

## Ollama PVC Model Inventory

```
gemma4:latest    9.6 GB   ← ACTIVE (running)  Gemma 4 8B, 128K ctx
gemma3:27b       17 GB    ← fallback           Gemma 3 27B
gemma4:31b       19 GB    ← READY (downloaded) Gemma 4 31B, 128K ctx (upgrade candidate)
```

Disk: 49GB PVC, all 3 models fully downloaded and ready. Free space is tight (~5.1GB free) but stable.

---

## 📈 THE 3-HORIZON DEMO OVERHAUL BLUEPRINT

We are restructuring the GDC Predictive Maintenance demo to address three distinct business and physical event horizons, maintaining a progressive-disclosure UX ("Executive View" vs. "Engineer Console") and full "Data-Informed" RAG synthesis.

### 1. Near-Term Horizon (ESP Gas Lock Emergency)
*   **Narrative**: Immediate, high-severity gas entrainment on `ESP-ALPHA-1`. PNR = 25 minutes.
*   **Executive Mode**: Pulsing red alert. SCADA says Green (Nominal). GDC warns 25 mins early. "Approve Autonomous VFD Tuning" button saves **$150,000**.
*   **Engineer Mode**: Plotly PIP decline curve. XGBoost feature table. RAG manuals + Lab reports showing 8.4% free gas void fraction.

### 2. Mid-Term Horizon (Ambiguous Vibration Drift & Truck Roll)
*   **Narrative**: Gradual vibration drift (1.1 → 2.4 mm/s) on `ESP-ALPHA-3` with low AI confidence (52%). Telemetry alone is inconclusive.
*   **Executive Mode**: Amber alert. "Inconclusive Telemetry — Avoid Premature Well Pull ($150k mistake)." Action card: **"Dispatch Truck Roll"**. Clicking triggers "Tech en-route" loader. Tech reports back: loose wellhead bolts retorqued; vibration drops to 1.1 mm/s.
*   **Engineer Mode**: Vibration drift line. RAG Troubleshooting Guide (stating vibration without temp spikes = mounting issues, not downhole wear) + Contractor platform service notes from 2 days ago.

### 3. Long-Term Horizon (Oil Price Jump & Vizier Optimization Game)
*   **Narrative**: Oil prices jump 40%. Operator wants to maximize production but prevent pump burnout.
*   **Executive Mode**: Sliders for **Oil Price Target ($/bbl)** and **Horizon (Days)**. Dynamic Value cards (SCADA Nominal vs. Vizier Optimal vs. Aggressive Run-to-Failure) showing calculated revenues, RUL, and repair costs. Action: "Apply Vizier Recommendation".
*   **Engineer Mode**: Live Bayesian optimization trials log. Pareto frontier scatter plot. RAG historical records of well temperature failure limits constraining the search space.

---

## NEXT SESSION PLAN (Implementing the Trio Scenarios)

| Fix | Change | Verification | Est. complexity |
|-----|--------|--------------|-----------------|
| Branch Setup | Check out `feature-trio-scenarios` branch | `git status` reports new branch | Small |
| Telemetry Drift | Add `vibration_drift_reading` to `simulator.py` | Run simulator locally; verify output | Medium |
| Optimize API | Write `/api/vizier/optimize` (Bayesian model math) and `/api/vizier/deploy` in `app.py` | HTTP GET curl returns trials | Medium |
| UI Overhaul | Refactor `index.html` to build the progressive disclosure accordion & sliders | UI displays sliders and layout | Large |
| Dispatch API | Implement `/api/agent/truck-roll` logging and timer logic | Approved truck roll completes | Medium |
| Gemma Prompts | Synthesize prompt instructions with Vizier trials and vibration drift RAG | Agent outputs accurate narrative | Medium |
| Rebuild & Deploy | Docker build, push, and kubectl rollout restart | http://34.138.32.109 loads live | Medium |

---

## What Was Done This Session (June 2, 2026)

*   **Environmental Check**: Corrected VM kubectl context to us-east1, restoring cluster health.
*   **Cleanup**: Removed legacy scratch Python files from root.
*   **O&G Terminology**: Aligned `Intake PSI` to `Pump Intake Pressure (PIP)` in the UI Pane 2 info popup.
*   **Deployment**: Fully rebuilt, pushed, and rolled out the updated GKE web server.
*   **Blueprint Design**: Collaboratively designed the entire 3-horizon progressive-disclosure demo architecture, outlining the exact mathematical, physical, and business layers.

---

## Rebuild & Deploy Commands
```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```
