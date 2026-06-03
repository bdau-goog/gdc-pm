# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `24c7913`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `24c7913` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:7bd9c7b8b47db3e8b6d428ffaeeb068a5b427040db9f0786cab9073dc832c672` (Fix 10/11/12, June 3)
**event-processor Digest:** `sha256:c63678dd5aec44569f3419f0cc3d2f96d9e93a5501cab0da929e1eaa635d3d83` (Fix EP-1: startup model pre-load, June 3)
**Branch Policy:** `feature-trio-scenarios` stays **separate from main** — do NOT merge.

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify Ollama state
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""

# 3. API truth
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'),'last_cloud_sync:',d.get('last_cloud_sync'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"

# 5. Check sentence_transformers
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "from sentence_transformers import SentenceTransformer; print('sentence_transformers: OK')" 2>&1

# 6. Check Fix 12 live (last_cloud_sync should be recent, NOT 2026-05-13)
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('last_cloud_sync:',d.get('last_cloud_sync'))"

# 7. Check event-processor stability (restarts should be 0)
kubectl get pod -n gdc-pm -l app=event-processor -o jsonpath='{.items[0].metadata.name} restarts={.items[0].status.containerStatuses[0].restartCount}'; echo ""

# 8. Verify git state
cd ~/gdc-pm && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running` — including event-processor (was crash-looping before Fix EP-1)
- event-processor: **restarts=0** (was 10+ restarts/90 min before fix)
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows**, field_intel: **~100 rows**, fault_sessions: **≥4 rows**
- sentence_transformers: **OK**
- last_cloud_sync: **recent timestamp** (2026-06-03T...), NOT `2026-05-13`
- git head: `24c7913`

---

## ⚠️ Known Integrity State — ALL CLEAR (Post Fixes 1-12 + EP-1)

All integrity violations from prior sessions are resolved and verified live. No display vs. reality mismatches remain.

| Item | Status |
|------|--------|
| `last_cloud_sync` | ✅ Live from AlloyDB MAX(event_time) — was hardcoded 2026-05-13 |
| `slug_flow` in FAULT_META | ✅ Added with color `#ffb300`, label "Slug Flow" |
| H1/H2/H3 Physics panels | ✅ Deployed — ⓘ button toggles collapsible panel |
| event-processor crash loop | ✅ Fixed (EP-1) — pre-load model at startup before RabbitMQ |
| All prior fixes (1-9) | ✅ Verified and deployed in previous sessions |

---

## NEXT SESSION PLAN — Session F: 4 Remaining Items

| Fix | Change (one sentence) | Verification test | Est. complexity |
|-----|----------------------|-------------------|-----------------|
| 13  | Upgrade Ollama to gemma4:31b — add OLLAMA_MODEL env var to event-processor deployment YAML | `curl -s http://gdc-pm.bdau.io/api/mlops/status \| python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('ollama_model'))"` → shows gemma4:31b | Small (YAML only) |
| 14  | Add gas lift (GLIFT-BRAVO-*) and mud pump (PUMP-CHARLIE-*) assets to frontend SITES/ASSET_META/FAULTS_BY_CLASS/FAULT_META/SENSOR_LABELS JS constants | Fleet Operations → verify 4 GLIFT-BRAVO and 3 PUMP-CHARLIE assets visible | Medium (HTML-only) |
| 15  | H3 Vizier RAG Constraint — retrieve Class H insulation temp limit from pgvector before trial loop instead of hardcoded 270°F | Check Vizier trials use pgvector-retrieved constraint; temp limit changes between runs | Low (app.py rebuild) |
| Fix 10b | H2 banner: add "1 engineer: 300–500 wells" explicitly to the ⓘ physics panel | Visual check in browser | Trivial (HTML-only) |

### Recommended Batching for Session F

- **Deploy A:** Fix 13 (kubectl apply to event-processor YAML, no rebuild, ~3 min + 5 min GPU warm-up)
- **Deploy B:** Fix 14 + Fix 10b (HTML-only, ~1 min rebuild)
- **Deploy C:** Fix 15 (app.py rebuild, ~9 min)

---

## What Was Done This Session (Session F startup / June 3, 2026)

**Fix EP-1 — event-processor crash loop eliminated:**

Root cause: `_get_embed_model()` was lazy-loaded inside `handle_message()` on the first fault message. Loading `all-MiniLM-L6-v2` blocks the Python thread for 15–90s. During this block, no heartbeat is sent to RabbitMQ (pika `BlockingConnection` is single-threaded). RabbitMQ times out the connection → `ConnectionResetError(104)` → `StreamLostError` on `basic_ack` → exit code 1 → crash loop (10+ restarts in 90 min).

Fix: added `_get_embed_model()` call in `main()` **before** `connect_rabbitmq()`. Model loads at startup; RabbitMQ connection only opens after the model is warm. Heartbeat timeout is physically impossible with this ordering.

- Committed: `24c7913` on `feature-trio-scenarios`
- Deployed: `sha256:c63678dd5aec44569f3419f0cc3d2f96d9e93a5501cab0da929e1eaa635d3d83`
- Verified: pod running 4m36s+ with 0 restarts (previously crashed every ~3 min)

**Fixes 10/11/12 (Session E — already deployed, listed for completeness):**
- Fix 11: `slug_flow` added to frontend `FAULT_META`
- Fix 12: Live `last_cloud_sync` from AlloyDB `MAX(event_time)`
- Fix 10: H1/H2/H3 Physics & Logic collapsible info panels

---

## Current Cluster State (VERIFIED June 3, 2026 17:34)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   — AlloyDB Omni + pgvector
event-processor-c486c89f-crlkn          1/1   Running   ← Fix EP-1 (pre-load model at startup)
fault-trigger-ui-68dd6db7b4-nccdq       1/1   Running   ← Fix 10/11/12 (June 3)
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running
telemetry-simulator-867677f784-h55wd    1/1   Running
```

DB: field_intel: ~100, rag_documents: 18, fault_sessions: 4+
event-processor: restarts=0 (pod age ~5 min at time of handoff write)

---

## Outstanding Development Items (Backlog)

**HIGH PRIORITY:**
- **Fix 13** — gemma4:31b upgrade: add `OLLAMA_MODEL: "gemma4:31b"` env var to `gke/event-processor/k8s/event-processor.yaml`. YAML-only, no rebuild. Allow 5 min GPU warm-up after deploy.
- **Fix 14** — ASSET_META expansion: Add GLIFT-BRAVO-1..4 and MUD-RIG42-1..3 and TOPDRIVE-RIG42-1 to frontend `SITES`, `ASSET_META`, `FAULTS_BY_CLASS`, `FAULT_META`, `SENSOR_LABELS`. Gas lift faults: valve_failure, thermal_runaway, bearing_wear_glift. Mud pump faults: pulsation_dampener_failure, valve_washout, piston_seal_wear. Top drive: gearbox_bearing_spalling, hydraulic_leak.

**MEDIUM PRIORITY:**
- **Fix 15** — H3 Vizier RAG constraint: In `/api/vizier/optimize`, call `get_rag_context_and_adjusted_rul('ESP-ALPHA-5', 'motor_overheat', 60)` to retrieve the Class H insulation limit from pgvector, then use it as the burnout threshold (replacing hardcoded 270°F). The retrieved limit is stored in `rag_context`; parse it with regex.

**LOW PRIORITY:**
- Fix 10b — H2 physics panel scale argument: explicitly state "1 production engineer manages 300–500 wells" in the panel text (already implied, but should be made explicit as the anchor counter-argument).
- Fix 13b — if gemma4:31b is too slow for demo, add a "model quality" toggle in the MLOps panel to switch between 8b (fast) and 31b (quality) at demo time.
- **EP-2 (future hardening)** — Bake `all-MiniLM-L6-v2` weights into the event-processor Docker image so the first startup doesn't need to download from HuggingFace (currently ~90s download on fresh container). Add `RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"` to the Dockerfile.

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
# HTML-only changes (Fix 10b, Fix 14)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# app.py changes (Fix 15) — same commands as above

# gemma4:31b upgrade (Fix 13) — YAML only, NO REBUILD
# Add env var to gke/event-processor/k8s/event-processor.yaml:
#   - name: OLLAMA_MODEL
#     value: "gemma4:31b"
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm
# Wait 5 minutes for GPU warm-up, then verify:
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('ollama_model'))"

# event-processor Python changes — MUST use digest (imagePullPolicy: IfNotPresent)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
NEW_DIGEST=$(gcloud artifacts docker images describe ${REGISTRY}/event-processor:latest --format='value(image_summary.digest)' 2>/dev/null)
kubectl set image deployment/event-processor event-processor=${REGISTRY}/event-processor@${NEW_DIGEST} -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm
```

**Deploy timing:** fault-trigger-ui HTML-only: ~1 min. event-processor (only processor.py changed): ~3 min build + pull. event-processor YAML only: ~3 min + 5 min GPU warm-up.

---

## Key Lessons (Session F startup)

- **event-processor crash root cause**: pika `BlockingConnection` is single-threaded — any blocking operation inside `handle_message()` starves the heartbeat. The fix is always to do slow init (model loads, DB migrations, cache warming) **before** `connect_rabbitmq()`, not lazily inside the message handler.
- **`imagePullPolicy: IfNotPresent` + digest deploy**: `kubectl rollout restart` reuses the cached old image. Must use `kubectl set image deployment/... @sha256:<new_digest>` to force the new image. Always retrieve the digest with `gcloud artifacts docker images describe`.
- **HuggingFace model download in GKE**: First-run download of `all-MiniLM-L6-v2` takes 60–90s from within a GKE node. Bake it into the Dockerfile (EP-2) to eliminate this delay — add to backlog, not urgent.
- **Crash diagnosis pattern**: `kubectl logs --previous` shows the actual exception; `kubectl get pod -o jsonpath='.containerStatuses[0].lastState'` shows exit code and duration. exitCode=137 → OOM, exitCode=1 → Python exception.
