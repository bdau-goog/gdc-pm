# Next Session Prompt — ESP v2 Redesign (Architecture Polish & rag_documents Fix)

## Header
**Date:** May 26, 2026
**Live URL:** http://34.138.32.109 (us-east1 cluster)
**Project:** gdc-pm (esp-v2-redesign branch)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `d63a4e1` — clean working tree ✅
**Note:** Pushed to origin/esp-v2-redesign.
**Image:** `sha256:d58e3a7bb4364c7256e68cc25cc6108ec02be183f974944237cc79a217831bfc` (deployed May 26 — includes Architecture tab fixes)

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 0. Push uncommitted commits to origin
cd ~/gdc-pm && git push

# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""

# 3. API truth
curl -s http://34.138.32.109/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma:27b`
- rag_documents: **18 rows** ✅ (Was 0, fixed)
- fault_sessions: ≥ 3 rows ✅

---

## ⚠️ Known Integrity State (VERIFIED May 26, 2026)

| Item | Actual State | Action Required |
|------|-------------|-----------------|
| **RUL Detection Flow** | UI shows AI-enhanced RUL logic, but backend (`event-processor` / `inference-api`) still records un-enhanced RUL first. | Needs logic refactor: enforce synchronous RAG synthesis before saving RUL (never show un-enhanced RUL). |
| Architecture tab | **Visually confirmed ✅** | Flow updated to match: Telemetry -> XGBoost ML -> AlloyDB -> Gemma -> UI. |
| fault_sessions | 3 rows ✅ | Working |
| field_intel | 100 rows ✅ | Active |
| Ollama / gemma:27b | `ollama_online: True` ✅ | Running on GPU |
| GPU CronJobs | SUSPENDED ✅ | Use manual scripts only |

---

## GPU Management (Manual — No CronJobs)

```bash
cd /home/brian/gdc-pm && ./scripts/gpu-start.sh   # start of day
cd /home/brian/gdc-pm && ./scripts/gpu-stop.sh    # end of day
```

---

## NEXT SESSION OBJECTIVES

### Priority 1 — Backend Flow Change (Never Show Un-Enhanced RUL)

**Current Logic:**
- `event-processor` subscribes to RabbitMQ.
- `event-processor` calls `inference-api` for `health_score` (XGBoost).
- `event-processor` saves `health_score` and `Initial RUL` to AlloyDB `telemetry_events`.
- UI polls `telemetry_events` and shows the un-enhanced RUL.
- Later, the AI agent endpoint enhances the RUL with doc context.

**Requested Logic (from User):**
- "Never show the RUL until it has been enhanced with the docs that pertain."
- Modify `inference-api` (or `event-processor`) to block the final save of the RUL until the RAG synthesis/Gemma LLM step is completed. 
- Ensure `telemetry_events` (or a dedicated table) stores the combined RUL, so the UI only ever displays the enhanced version.

**File surgery approach:**
- Inspect `gke/event-processor/processor.py` and `gke/inference-api/app.py`.
- Adjust the detection flow to trigger RAG synthesis synchronously.
- Verify `rag_documents` are being queried at detection time.

---

## What Was Done This Session

| Feature | Status |
|---------|--------|
| `rag_documents` table | ✅ 18 rows restored via `ingest_manuals.py` |
| Architecture tab visuals | ✅ Perfected flow: RabbitMQ -> XGBoost -> AlloyDB -> Gemma -> UI |

---

## Constraints (never violate)
- `terraform/gke.tf` must NOT be applied without review
- Preserve XGBoost models (`*.ubj` files)
- `/api/*` endpoints must remain backward-compatible
- Do NOT commit to `main`
- **No browser on SSH remote** — `browser_action` must NOT be used
- **Commit after every verified deployment**
- **CSS goes in `<head>` — never in a `<style>` tag inside `#app`**

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

## Current Cluster State (VERIFIED May 26, 2026)

```
fault-trigger-ui-84dd4cbc6c-2lwtf   1/1  Running  (Architecture fix deployed)
alloydb-omni-5fcfc68fdb-x9xc8       1/1  Running  
event-processor-7d9b594b6b-wjlkc    1/1  Running  
gdc-pm-rabbitmq-server-0            1/1  Running  
grafana-655b6f5c7c-mtmtw            1/1  Running  
inference-api-5697b79566-4q8tm      1/1  Running  
ollama-5bc5db749b-jf997             1/1  Running   ← GPU
telemetry-simulator-6b9668648b-ddc66 1/1 Running  

Ollama replicas: 1
API: ollama_online: True  model: gemma:27b ✅
AlloyDB: field_intel=100, rag_documents=18 ✅, fault_sessions=3
git: working tree clean (d63a4e1 pushed to origin)
```

---

## Outstanding Development Items (Backlog)

1. Enforce synchronous RAG synthesis on RUL generation.
2. Demo narrative improvements (`docs/DEMO_NARRATIVE_UPDATE.md`).

---

## Key Lessons Learned (May 26 session)

- `python3 scripts/ingest_manuals.py` must be run with a venv that contains `psycopg2-binary` and `sentence-transformers`, with `AlloyDB` port-forwarded locally if executed from the SSH host. 
- Python string-replacement (`re.sub`) is safer than `replace_in_file` for large HTML block edits where spacing/formatting is complex, preventing matching errors.
- Visual flow logic correctly places XGBoost inference before the DB and LLM enhancement, representing realistic edge telemetry paths.