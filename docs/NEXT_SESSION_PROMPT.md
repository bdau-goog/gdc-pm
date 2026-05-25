# Next Session Prompt — ESP v2 Redesign (Stage 2 COMPLETE)

## Header
**Date:** May 25, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `08b590a` — "feat: finalize stage 2 fixes and runbooks" ✅ clean working tree
**Session ended at:** ~10:00 AM EDT May 25, 2026

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
kubectl get pods -n gdc-pm -l app=ollama --no-headers

# 3. API truth
curl -s http://34.138.32.109/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, pod on gpu-pool node
- API: `ollama_online: True  model: gemma:27b`
- field_intel: ≥ 0 rows (clears on pod restart)
- rag_documents: **11 rows** (esp:3, gas_lift:3, mud_pump:3, top_drive:2) ⚠️ was 0 at last check — must be restored
- fault_sessions: ≥ 2 rows (write path verified working)

---

## ⚠️ Known Integrity State (as of May 25, 2026 ~10:00 EDT)

| Item | Actual State | Action Required |
|------|-------------|-----------------|
| **rag_documents** | **0 rows** (expected 11) | ⚠️ HIGH — investigate and restore before any demo |
| fault_sessions | 2 rows ✅ | Write path working (Fix 11b complete) |
| field_intel | 100 rows ✅ | Active, populates on fault injection |
| Ollama / gemma:27b | `ollama_online: True` ✅ | Running on GPU node (us-east1) |
| UI Gemma status | Honest ✅ | Shows `⛔ offline` when Ollama down |
| GPU CronJobs | SUSPENDED ✅ | Use manual scripts only |
| ChromaDB | Removed ✅ | Replaced by AlloyDB field_intel dynamic RAG |
| sentence-transformers | Not installed ✅ | Static rag_documents pgvector query skipped gracefully |

---

## ⚠️ CLUSTER MIGRATION NOTE — us-central1 → us-east1

- Region: `us-east1`
- Cluster: `gdc-edge-simulation`
- Live IP: `34.138.32.109`
- Terraform: `gdc-pm/terraform/terraform.tfvars` → `region=us-east1`, `gke_subnet_name=subnet-us-east1`
- GPU node pool: `gpu-pool` with `g2-standard-8` + `nvidia-l4` in us-east1

---

## GPU Management (Manual — No CronJobs)

### Start the GPU (run at start of work day):
```bash
cd /home/brian/gdc-pm
./scripts/gpu-start.sh
```
- Scales Ollama to 1 replica
- GKE Standard provisions L4 GPU node in us-east1 (~10-15 min)
- PVC `ollama-models-pvc` in us-east1 ✅ (zone-matched)
- Init container skips pull if `gemma:27b` already on PVC (~15 min with cached model)

### Stop the GPU (run when done for the day):
```bash
cd /home/brian/gdc-pm
./scripts/gpu-stop.sh
```
- Scales Ollama to 0; L4 node deprovisioned (~5 min); PVC retained
- Cost: ~$0.65/hr while running

### Verify Gemma is serving:
```bash
kubectl exec -n gdc-pm deployment/ollama -- curl -sf http://localhost:11434/api/tags | python3 -c "import sys,json;d=json.load(sys.stdin);print([m['name'] for m in d.get('models',[])])"
# Must return: ['gemma:27b']
```

---

## Sprint 5 Layout (DO NOT REVERT)
```
┌────────────────────────────┬───┬──────────────────┐
│  dd-compare-col (charts)   │ ║ │  Intelligence    │  ← 260px default
│   GDC AI forecast          │ ║ ├··················┤
│   gdc-scada-handle (amber) │ ║ │  Agent Chat      │  ← 280px default
│   SCADA chart              │ ║ ├··················┤
│                            │ ║ │  Resolution      │  ← flex:1 remainder
└────────────────────────────┴───┴──────────────────┘
```

---

## What IS Working (verified as of May 25, 2026 ~10:00 EDT)

| Feature | Status | Verified by |
|---------|--------|-------------|
| GDC AI Forecast (XGBoost) | ✅ | All 4 health models loaded at startup |
| GDC vs SCADA bridge bar countdown | ✅ | Elapsed-time fallback (Fix 3) |
| Sensor highlighting (per-sensor) | ✅ | Fix 4 |
| SCADA chart purge on reset/approve | ✅ | Fix 5 |
| Intelligence Feed randomization | ✅ | Fix 8b — `random.sample` + `random.shuffle` |
| AI Informed RUL divergence | ✅ | GVF guaranteed >70, 0.6x multiplier always fires |
| HITL flow (approve, savings) | ✅ | Full end-to-end works |
| Honest Gemma status | ✅ | `⛔ offline` shown when Ollama down |
| `gpu-start.sh` / `gpu-stop.sh` | ✅ | Manual GPU scripts, CronJobs suspended |
| **Fix 9: ALL fault type dynamic docs** | ✅ | valve_failure, thermal_runaway + 5 remaining branches — all done |
| **Fix 10: Dynamic Gemma finding** | ✅ | Templates for all fault types, interpolates live PSI/amps/GVF/conf |
| **Fix 11b: fault_sessions audit log** | ✅ | Table + GET endpoint + write on inject/resolve (2 rows confirmed) |
| **Deploy-from-scratch runbook** | ✅ | `docs/runbooks/DEPLOY_FROM_SCRATCH.md` |
| **DEVELOPMENT_DECISIONS.md** | ✅ | Created in `docs/` |
| **gemma:27b typo fix** | ✅ | Was `gemma4:27b` — corrected, GPU LLM inference restored |

---

## NEXT SESSION PLAN

| # | Item | Change | Verification Test | Complexity |
|---|------|--------|-------------------|------------|
| 1 | **Restore rag_documents** | Investigate why 11 rows went to 0; re-seed if needed | `SELECT COUNT(*) FROM rag_documents` = 11 | Small |
| 2 | **Architecture tab in UI** | Add an Architecture tab to `index.html` with SVG data-flow diagram (all tiers: SCADA → sensors → AlloyDB → XGBoost + Gemma → dashboards) | Tab renders in live app without duplicate HTML | Medium |
| 3 | **Demo narrative** | Review and implement improvements from `docs/DEMO_NARRATIVE_UPDATE.md` | Live walkthrough matches narrative | Medium |

---

## Current Cluster State (VERIFIED May 25, 2026 ~22:28 UTC)

```
kubectl get pods -n gdc-pm --no-headers:
alloydb-omni-5fcfc68fdb-x9xc8          1/1  Running    3d9h
event-processor-7d9b594b6b-wjlkc       1/1  Running    3d8h
fault-trigger-ui-7df579f6c5-qmwdn      1/1  Running    39m
gdc-pm-rabbitmq-server-0               1/1  Running    3d8h
grafana-655b6f5c7c-mtmtw               1/1  Running    3d9h
inference-api-5697b79566-4q8tm         1/1  Running    3d8h
ollama-5bc5db749b-jf997                1/1  Running    10h   ← GPU pod
telemetry-simulator-6b9668648b-ddc66   1/1  Running    3d9h

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ✅

AlloyDB:
  field_intel:    100 rows
  rag_documents:  0 rows  ⚠️ REGRESSION — was 11 rows
  fault_sessions: 2 rows  ✅ (write path confirmed working)

CronJobs:
  ollama-stand-up:   SUSPENDED ✅
  ollama-stand-down: SUSPENDED ✅
```

---

## Constraints (unchanged — never violate)
- `terraform/gke.tf` must NOT be applied without review
- All UI changes → `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`
- Preserve XGBoost health score models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- O&G physics must remain authentic
- **No browser on SSH remote** — `browser_action` must NOT be used
- **No inline high-res screenshots** — token budget
- **`classifier_active = (fault_fraction > 0.20) or is_degrading`** — DO NOT REVERT
- Commit after every verified deployment (not just at session end)

---

## Rebuild & Deploy Commands
```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

---

## Key Lessons Learned (May 25 session)
- **Always commit after deployment** — the afternoon session made code changes and deployed them without committing; git history had a 10-hour gap that required manual reconstruction
- **`gemma4:27b` vs `gemma:27b`** — the model name typo was silently causing Ollama inference to fail; always verify `ollama_online: True` AND the model name in the API response
- **rag_documents can drain unexpectedly** — went from 11 to 0 between sessions; cause unknown; add to session opener verification and investigate
