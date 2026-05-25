# Next Session Prompt — ESP v2 Redesign (Sprint 5 v8 — Stage 2 COMPLETE)

## Header
**Date:** May 22, 2026
**Live URL:** http://34.138.32.109  ← NEW IP (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation  ← NOW IN us-east1 (was us-central1)
**Namespace:** gdc-pm
**Current Image:** fault-trigger-ui:latest (sha256:d12a1a8e059d) — includes all Sprint 5 v8 Stage 2 fixes
**Session ended at:** ~835K tokens

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state (is it truly running and serving Gemma?)
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
kubectl get pods -n gdc-pm -l app=ollama --no-headers

# 3. API truth (does the UI tell the truth about Gemma?)
curl -s http://34.138.32.109/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected results when healthy:**
- Ollama pod: `ollama-XXXXX  1/1  Running` on a GPU node (gpu-pool in us-east1)
- API: `ollama_online: True  model: gemma:27b`
- field_intel: some rows (0 if no fault has been injected since pod restart)
- rag_documents: 11 rows

---

## ⚠️ CLUSTER MIGRATION — us-central1 → us-east1

**Why:** L4 GPU capacity exhausted in all 3 us-central1 zones (a, b, c). us-east1 has capacity.

**New cluster details:**
- Region: `us-east1`
- Cluster: `gdc-edge-simulation`
- Live IP: `34.138.32.109`
- Terraform: `gdc-pm/terraform/terraform.tfvars` → `region=us-east1`, `gke_subnet_name=subnet-us-east1`
- Subnet: `subnet-us-east1` (10.31.0.0/20) in `gdc-pm-vpc`

**GPU node pool:** `gpu-pool` with `g2-standard-8` + `nvidia-l4` in us-east1

---

## ⚠️ Known Integrity State (as of May 22, 2026)

| Item | Actual State | Notes |
|------|-------------|-------|
| Ollama / Gemma4:27b | **PENDING** (init container pulling gemma:27b ~15GB) | Started ~12:49 UTC. Will take 15-20 min. |
| GPU CronJobs | **SUSPENDED** (both ollama-stand-up and ollama-stand-down) | Replaced by manual scripts. Do NOT unsuspend. |
| GPU control | **Manual scripts only** | `./scripts/gpu-start.sh` and `./scripts/gpu-stop.sh` |
| AI Informed RUL | **Fixed** (GVF guaranteed > 70) | Was only firing ~60% of runs before fix |
| UI Gemma status | **Honest** | Shows `⛔ offline` when Ollama down, real model name when up |
| ChromaDB | **Removed** | Replaced by AlloyDB field_intel dynamic RAG |
| sentence-transformers | **Not installed** (reverted — was 6GB image) | Static rag_documents pgvector query skipped gracefully |
| k8s yamls | **PATCHED** | GCR_IMAGE_PLACEHOLDER replaced with real registry URLs |
| Secrets | **RECREATED** | alloydb-secret + rabbitmq-secret from .secrets/ files |

---

## GPU Management (Manual — No CronJobs)

### Start the GPU (run this at start of work day):
```bash
cd /home/brian/gdc-pm
./scripts/gpu-start.sh
```
- Scales Ollama to 1 replica
- GKE Standard provisions L4 GPU node in **us-east1** (~10-15 min)
- PVC `ollama-models-pvc` is in us-east1 ✅ (zone-matched)
- Init container skips pull if `gemma:27b` already on PVC (faster restart)
- Watches until `gemma:27b` is responding (~15-20 min total first time, ~15 min with cached model)

### Stop the GPU (run when done for the day):
```bash
cd /home/brian/gdc-pm
./scripts/gpu-stop.sh
```
- Scales Ollama to 0
- L4 node deprovisioned by GKE (~5 min)
- PVC retained (model cache preserved for faster next startup)
- Cost: ~$0.65/hr while running

### Verify Gemma is actually serving (after gpu-start.sh completes):
```bash
kubectl exec -n gdc-pm deployment/ollama -- curl -sf http://localhost:11434/api/tags | python3 -c "import sys,json;d=json.load(sys.stdin);print([m['name'] for m in d.get('models',[])])"
# Must return: ['gemma:27b']
```

---

## Sprint 5 v7 Layout (DO NOT REVERT)
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

## What IS Working (verified)

| Feature | Status | Verified by |
|---------|--------|-------------|
| GDC AI Forecast (XGBoost) | ✅ | All 4 health models loaded at startup |
| GDC vs SCADA bridge bar countdown | ✅ | Elapsed-time fallback (Fix 3) |
| Sensor highlighting (per-sensor) | ✅ | Fix 4 |
| SCADA chart purge on reset/approve | ✅ | Fix 5 |
| Intelligence Feed (gas_lock) | ✅ | 5-item pool; live field_intel docs after ~30s |
| AI Informed RUL divergence | ✅ | GVF guaranteed >70, 0.6x multiplier always fires |
| HITL flow (approve, savings) | ✅ | Full end-to-end works |
| Honest Gemma status | ✅ | `⛔ offline` shown when Ollama down |
| `gpu-start.sh` / `gpu-stop.sh` | ✅ | Scripts created, CronJobs suspended |
| **Fix 8b: Intel feed randomization** | ✅ | `random.sample` + `random.shuffle` — verified live |
| **Fix 10: Dynamic Gemma finding** | ✅ | Interpolates live PSI/amps/GVF/conf — verified live |
| **Fix 9: valve_failure docs** | ✅ | 3 randomized templates (process_historian, maximo_service, shift_note) |
| **Fix 9: thermal_runaway docs** | ✅ | 3 randomized templates (process_historian, maximo_pm, shift_note) |
| **Fix 11b: fault_sessions table** | ✅ | Table created, `/api/fault-sessions` returns 0 count, no error |

## What IS NOT Working Yet

| Feature | Status | Fix |
|---------|--------|-----|
| Gemma LLM streaming | ❌ Ollama PENDING (L4 provisioning in us-east1) | Will auto-resolve when L4 node provisions |
| Dynamic docs for non-ESP faults (5 remaining) | ❌ Generic "Shift Note" fallback | Fix 9 (remaining 5 branches) |
| Dynamic Gemma finding for non-gas_lock faults | ❌ Static string for other fault types | Fix 10 (extend templates) |
| Fault sessions audit log (write path) | ❌ Table exists, no writes yet | Fix 11b (write on inject/resolve) |
| Deploy-from-scratch runbook | ❌ Not documented | **TODO: Next session** |

---

## 🚧 TODO: Deploy-from-Scratch Runbook

**MARKER: This needs to be created next session.**

Similar to `~/gdc-das-life` runbook. Should cover:
1. Terraform apply (creates cluster + node pools + BigQuery + GCS)
2. Namespace creation (`kubectl create namespace gdc-pm`)
3. Secret creation (alloydb-secret, rabbitmq-secret from .secrets/ files)
4. Service deployment order (alloydb-omni first, then rabbitmq, then everything else)
5. k8s yaml image URL patching (GCR_IMAGE_PLACEHOLDER → real registry)
6. IAM: grant `roles/artifactregistry.reader` to compute SA
7. Ollama deployment + gpu-start.sh
8. Verification checklist

**Also needed: Architecture diagram overview** covering:
- GKE cluster (us-east1) with node pools (default + gpu-pool)
- AlloyDB Omni (PostgreSQL) — telemetry_events, field_intel, rag_documents, fault_sessions
- RabbitMQ — telemetry exchange, sensor.reading routing key
- Telemetry Simulator → RabbitMQ → Event Processor → AlloyDB
- Fault Trigger UI (FastAPI) — serves frontend + all /api/* endpoints
- Inference API — XGBoost health models
- Ollama (GPU pod) — gemma:27b LLM
- Grafana — dashboards
- Artifact Registry (us-central1) — Docker images
- VPC: gdc-pm-vpc, subnet-gke (us-central1), subnet-us-east1 (us-east1)

---

## NEXT SESSION PLAN

| # | Fix | Change | Verification Test | Complexity |
|---|-----|--------|-------------------|------------|
| 1 | 9 (remaining) | 5 more fault type branches in `generate_dynamic_documents` | Inject valve_washout → check field_intel for non-generic content | Medium |
| 2 | 10 (extend) | Add templates for thermal_runaway, valve_failure, bearing_wear_glift | Inject thermal_runaway, check gemma_finding contains live temp value | Small |
| 3 | 11b (write path) | Write to fault_sessions on inject + resolve | Inject gas_lock, approve → check `/api/fault-sessions` has 1 row | Small |
| 4 | Runbook | Create deploy-from-scratch runbook | Follow runbook on fresh namespace | Medium |

---

## Current Cluster State (as of May 22, 2026 ~12:50 UTC)

```bash
# VERIFIED cluster state:
kubectl get pods -n gdc-pm  # actual output at session end:
# alloydb-omni      ✅ 1/1 Running
# event-processor   ✅ 1/1 Running
# fault-trigger-ui  ✅ 1/1 Running  (sha256:d12a1a8e059d — includes all Stage 2 fixes)
# gdc-pm-rabbitmq   ✅ 1/1 Running
# grafana           ✅ 1/1 Running
# inference-api     ✅ 1/1 Running
# telemetry-sim     ✅ 1/1 Running
# ollama            ⏳ Init:0/1 — pulling gemma:27b (~15 min from 12:49 UTC)

# AlloyDB:
# rag_documents: 11 rows (esp:3, gas_lift:3, mud_pump:3, top_drive:2)
# field_intel: cleared on next fault injection
# fault_sessions: 0 rows (table created, write path not yet implemented)

# CronJobs:
# ollama-stand-up:   SUSPENDED ✅
# ollama-stand-down: SUSPENDED ✅

# Secrets:
# alloydb-secret:  ✅ (from .secrets/alloydb-password.txt)
# rabbitmq-secret: ✅ (from .secrets/rabbitmq-password.txt)
```

---

## Constraints (unchanged)
- `terraform/gke.tf` must NOT be applied without review
- All UI changes → `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`
- Preserve XGBoost health score models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- O&G physics must remain authentic
- **No browser on SSH remote** — `browser_action` must NOT be used
- **No inline high-res screenshots** — token budget
- **`classifier_active = (fault_fraction > 0.20) or is_degrading`** — DO NOT REVERT

---

## Rebuild & Deploy Commands
```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```

---

## Fix Specs for Stage 2 (COMPLETED)

### Fix 8b — ✅ DONE
`random.sample(pool, min(3, len(pool)))` + `random.shuffle(canned_items)` in `get_intelligence_feed`

### Fix 10 — ✅ DONE
`GEMMA_FINDING_TEMPLATES` dict + `get_gemma_finding(fault_type, asset_id)` function.
Interpolates: `psi`, `amps`, `gvf`, `conf`, `pnr` from `active_degrades[asset_id]["current_sensors"]`.
Currently only gas_lock has templates; other fault types fall back to static GEMMA_FINDINGS.

### Fix 9 — ✅ PARTIAL (valve_failure + thermal_runaway done; 5 more remaining)
Added `elif fault_type == "valve_failure"` and `elif fault_type == "thermal_runaway"` branches
in `generate_dynamic_documents`. Each has 3 doc types with 3 randomized content variants.

### Fix 11b — ✅ PARTIAL (table + GET endpoint done; write path not yet implemented)
`fault_sessions` table created in `_ensure_field_intel_table()`.
`GET /api/fault-sessions` endpoint added.
Write path (INSERT on inject/resolve) not yet implemented.
