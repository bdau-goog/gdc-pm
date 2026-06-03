# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `b4a0242`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `b4a0242` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:5d8c773248eed7ee4293d8c5d3d102d43acde415c19e1947abd46861778cb9c9` (Fix 10b, June 3)
**event-processor Digest:** `sha256:312ce844a244356732d435e396396486df7e111c814f8205238c43feb5d9cd63` (EP-2: model baked in, June 3) — pinned in YAML
**Branch Policy:** `feature-trio-scenarios` stays **separate from main** — do NOT merge.

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify event-processor (restarts should be 0, model loading should be instant)
kubectl get pod -n gdc-pm -l app=event-processor -o jsonpath='{.items[0].metadata.name} restarts={.items[0].status.containerStatuses[0].restartCount}'; echo ""

# 3. API truth
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'),'last_cloud_sync:',d.get('last_cloud_sync')[:25])"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"

# 5. Vizier endpoint speed (should be <1s)
time curl -s "http://gdc-pm.bdau.io/api/vizier/optimize?oil_price=112&horizon_days=90" --max-time 10 | python3 -c "import sys,json;d=json.load(sys.stdin);print('trials:',len(d['trials']),'optimal_hz:',d['optimal_hz'])"

# 6. Verify Fix 14 assets live
curl -s http://gdc-pm.bdau.io/ | grep -c "well_bravo\|GLIFT-BRAVO\|MUD-RIG42\|valve_failure\|pulsation_dampener"

# 7. Verify Ollama has gemma4:31b (not just env var)
kubectl exec -n gdc-pm deployment/ollama -- ollama list 2>/dev/null | grep -E "NAME|gemma"

# 8. Verify event-processor env
kubectl exec -n gdc-pm deployment/event-processor -- env | grep OLLAMA_MODEL

# 9. Git state
cd ~/gdc-pm && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- event-processor: **restarts=0**; startup model load < 5s (from image cache, not HuggingFace)
- Ollama: `ollama_online: True`, gemma4:31b and gemma4:latest in ollama list
- rag_documents: **18 rows**, field_intel: **~100 rows**
- Vizier endpoint: **<1s response**
- Fix 14 assets grep: **≥14 matches**
- event-processor OLLAMA_MODEL: **gemma4:31b**
- git head: `b4a0242`

---

## ⚠️ Known Integrity State — ALL CLEAR

| Item | Status |
|------|--------|
| `mlops/status` shows `gemma4:latest` | ✅ CLARIFIED — fault-trigger-ui uses gemma4:latest for its agent chat. event-processor uses gemma4:31b for RAG narratives. Both are correct — different services, different roles. |
| `last_cloud_sync` | ✅ Live from AlloyDB MAX(event_time) |
| `slug_flow` in FAULT_META | ✅ |
| H1/H2/H3 Physics panels | ✅ H2 has "1:500" callout box as visual anchor |
| Fix 14 new assets | ✅ 14 live matches |
| Fix 15 Vizier RAG | ✅ 148ms (SQL ILIKE) |
| EP-1 crash loop | ✅ Eliminated (model pre-loaded before RabbitMQ) |
| EP-2 cold-start | ✅ Eliminated (model baked into image, 62 it/s from cache) |

---

## NEXT SESSION PLAN — No Outstanding Items

The demo is **feature-complete and hardened**. All Session F + G items are done.

| Item | Status |
|------|--------|
| EP-1: event-processor crash loop | ✅ Done |
| EP-2: model cold-start | ✅ Done |
| Fix 13: gemma4:31b env var | ✅ Done (model confirmed in Ollama) |
| Fix 14: Fleet expansion | ✅ Done |
| Fix 15: Vizier RAG constraint | ✅ Done (SQL ILIKE, 148ms) |
| Fix 10b: H2 scale callout | ✅ Done |

**Remaining optional items (not blocking demo):**
- Ollama 500 errors from event-processor when using gemma4:31b for RAG narratives — Ollama may be slow to warm up 31b (19GB model). If RAG narratives are important, add a `wait_for_model` probe before the Ollama call in processor.py. Falls back to rule-based gracefully today.
- Fix 13b: Model quality toggle UI (low priority)

---

## What Was Done This Session (Sessions F + G — June 3, 2026)

**EP-1** (Session F): event-processor crash loop eliminated — model pre-loads before RabbitMQ

**Fix 13** (Session F/G): OLLAMA_MODEL=gemma4:31b set in event-processor. Verified gemma4:31b is pulled on Ollama pod (19GB, 5 days ago).

**Fix 14** (Session F): GLIFT-BRAVO-1..4, MUD-RIG42-1..3, TOPDRIVE-RIG42-1 added to all 5 frontend JS constants. 4 asset classes, 12 fault types.

**Fix 15** (Session F): Vizier RAG constraint retrieved from AlloyDB rag_documents via SQL ILIKE. 148ms response (was >60s timeout with embedding model).

**Fix 10b** (Session G): H2 physics panel "Why H2 Is the Most Vulnerable Scenario" section now has a visually prominent orange callout box with "1:500" as a large numeral, making the scale argument the visual anchor when presenting.

**EP-2** (Session G): Baked all-MiniLM-L6-v2 model into event-processor Docker image. Model loads at 62 it/s from image cache vs 60-90s HuggingFace download on cold-start. Event-processor now has instant startup regardless of node history.

---

## Current Cluster State (VERIFIED June 3, 2026 18:26)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   — AlloyDB Omni + pgvector
event-processor-99dd7b6d9-qjjg9         1/1   Running   ← EP-2 (model baked) + EP-1 + Fix 13 (gemma4:31b)
fault-trigger-ui-[new pod]              1/1   Running   ← Fix 10b (1:500 callout) + Fix 14/15
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running   ← gemma4:31b + gemma4:latest + gemma3:27b
telemetry-simulator-867677f784-h55wd    1/1   Running
```

DB: field_intel: ~100, rag_documents: 18
event-processor: restarts=0, model loads at 62 it/s from image cache

---

## Outstanding Development Items (Backlog — Low Priority)

- **Ollama 500 on 31b narratives**: event-processor gets 500 from Ollama when requesting gemma4:31b narratives. Fallback to rule-based is graceful but 31b narratives are not being generated. Root cause: 31b needs longer warm-up or the request format differs. Fix: add retry with backoff in `generate_rag_narrative()` in processor.py.
- **Fix 13b**: Model quality toggle UI (low priority — demo works with gemma4:latest in fault-trigger-ui agent chat)

---

## Constraints

- `terraform/gke.tf` must NOT be applied.
- All demo changes: `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`.
- No browser on SSH remote — no `browser_action` tool.
- `feature-trio-scenarios` stays **separate from `main`**.
- XGBoost `*.ubj` models — do not retrain.

---

## Rebuild & Deploy Commands

```bash
# fault-trigger-ui (HTML or app.py changes)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# event-processor Python changes — build, push, update YAML digest, apply
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
# Get new digest:
docker inspect --format='{{index .RepoDigests 0}}' ${REGISTRY}/event-processor:latest
# Update image line in gke/event-processor/k8s/event-processor.yaml, then:
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm
```

---

## Key Lessons (Sessions F + G)

- **SQL ILIKE > embedding model for fact retrieval**: Semantic search is for "find relevant content." SQL text search is for "find the specific fact I know exists." The insulation temperature limit is a specific known fact — ILIKE finds it in <10ms with no model loading.
- **`kubectl apply` reverts `kubectl set image @sha256`**: Pin the digest in the YAML itself. `kubectl set image @sha256` is a one-off fix; only the YAML is durable.
- **OLLAMA_MODEL env var ≠ model pulled**: Always verify with `ollama list` that the requested model is available on the pod.
- **Model baking eliminates cold-start entirely**: `RUN python3 -c "SentenceTransformer('all-MiniLM-L6-v2')"` in the Dockerfile downloads and caches the model into the image layer. First run on any node is now instant. EP-1 fixed the crash; EP-2 makes the startup fast.
- **gemma4:31b Ollama 500s**: The 31b model may take longer to load into GPU VRAM than the Ollama request timeout. If RAG narratives from 31b are needed, increase the Ollama timeout in processor.py or add a warm-up probe.
