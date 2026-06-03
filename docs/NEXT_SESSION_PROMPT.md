# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `6db9d01`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `6db9d01` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:0a6c7c7c2a5528936e0b4286ec53bafb0ef589922ec5c74034e264ee8822c786` (Fix 14/15 rewrite, June 3)
**event-processor Digest:** `sha256:c63678dd5aec44569f3419f0cc3d2f96d9e93a5501cab0da929e1eaa635d3d83` (EP-1: startup model pre-load, June 3) — pinned in YAML
**Branch Policy:** `feature-trio-scenarios` stays **separate from main** — do NOT merge.

---

## ⚠️ MANDATORY SESSION OPENER — Run this BEFORE writing any code

```bash
# 1. Verify cluster truth
kubectl get pods -n gdc-pm --no-headers

# 2. Verify event-processor (restarts should be 0)
kubectl get pod -n gdc-pm -l app=event-processor -o jsonpath='{.items[0].metadata.name} restarts={.items[0].status.containerStatuses[0].restartCount}'; echo ""

# 3. API truth
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'),'last_cloud_sync:',d.get('last_cloud_sync'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"

# 5. Verify Fix 15 Vizier endpoint responds quickly (<5s)
time curl -s "http://gdc-pm.bdau.io/api/vizier/optimize?oil_price=112&horizon_days=90" --max-time 10 | python3 -c "import sys,json;d=json.load(sys.stdin);print('trials:',len(d['trials']),'optimal_hz:',d['optimal_hz'])"

# 6. Verify Fix 14 assets live in frontend
curl -s http://gdc-pm.bdau.io/ | grep -c "well_bravo\|GLIFT-BRAVO\|MUD-RIG42\|valve_failure\|pulsation_dampener"

# 7. Verify event-processor OLLAMA_MODEL
kubectl exec -n gdc-pm deployment/event-processor -- env | grep OLLAMA_MODEL

# 8. Check what models Ollama actually has loaded
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('UI model (fault-trigger-ui):',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/ollama -- ollama list 2>/dev/null || echo "check ollama pod name"

# 9. Verify git state
cd ~/gdc-pm && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running` — all 8 services
- event-processor: **restarts=0**
- Ollama: `ollama_online: True`, `model: gemma4:latest`
- rag_documents: **18 rows**, field_intel: **~100 rows**
- Vizier endpoint: **<1s response** (was >60s timeout before Fix 15)
- Fix 14 assets grep: **≥14 matches**
- event-processor OLLAMA_MODEL: **gemma4:31b**
- git head: `6db9d01`

---

## ⚠️ Known Integrity State

| Item | Status |
|------|--------|
| `mlops/status` shows `gemma4:latest` | ⚠️ This is fault-trigger-ui's own OLLAMA_MODEL (gemma4:latest default). The event-processor has OLLAMA_MODEL=gemma4:31b but Ollama may only have gemma4:latest pulled. If Ollama doesn't have 31b, event-processor RAG narratives silently fall back to rule_based. Verify with `ollama list` on the Ollama pod. |
| `last_cloud_sync` | ✅ Live from AlloyDB MAX(event_time) |
| `slug_flow` in FAULT_META | ✅ Added with color `#ffb300` |
| H1/H2/H3 Physics panels | ✅ Deployed |
| All prior fixes (1-12) | ✅ Verified and deployed |
| Fix 14 new assets | ✅ 14 live matches in frontend JS constants |
| Fix 15 Vizier RAG | ✅ 148ms response (SQL ILIKE, no model loading) |

---

## NEXT SESSION PLAN — Session G

| Fix | Change (one sentence) | Verification test | Est. complexity |
|-----|----------------------|-------------------|-----------------|
| Fix 13 verify | Confirm Ollama actually has gemma4:31b pulled (not just env var set) | `ollama list` on the pod shows `gemma4:31b` | Small (check only) |
| Fix 13b (if 31b not pulled) | Pull gemma4:31b on the Ollama pod: `kubectl exec -n gdc-pm deployment/ollama -- ollama pull gemma4:31b` | mlops/status shows gemma4:31b after 5min GPU warm-up | Small (10-15 min GPU warm-up) |
| Fix 10b | H2 physics panel: add explicit "1 production engineer manages 300–500 wells" as a standalone callout box (currently inline in body text — make it the visual anchor) | Visual check in browser | Trivial (HTML-only) |
| EP-2 | Bake all-MiniLM-L6-v2 weights into event-processor Dockerfile so cold-start model download never happens again | After deploy, logs show model loaded from cache, not HuggingFace | Small (1 Dockerfile line) |

### Recommended Batching for Session G
- **Verify A:** Fix 13 — check if gemma4:31b is actually in Ollama (1 command, no deploy)
- **If needed:** Pull gemma4:31b (one kubectl exec, wait 10-15 min)
- **Deploy A:** Fix 10b (HTML-only, ~1 min rebuild)
- **Deploy B:** EP-2 (event-processor Dockerfile, ~9 min build)

---

## What Was Done This Session (Session F — June 3, 2026)

**EP-1 — event-processor crash loop eliminated:**
- Root cause: `_get_embed_model()` lazy-loaded inside `handle_message()`. Model load blocked pika heartbeat → `StreamLostError` on `basic_ack` → exit 1 → crash loop (10+ restarts/90 min).
- Fix: `_get_embed_model()` called in `main()` BEFORE `connect_rabbitmq()`. Model warms before any RabbitMQ connection opens.
- **Critical lesson**: the YAML had `image: ...event-processor:latest`. When `kubectl apply` was run for Fix 13, it reverted the image from the digest-pinned EP-1 to the old cached `:latest` on the node, re-introducing the crash loop. Fix: YAML now pins `image: ...event-processor@sha256:c63678dd5aec...` so `kubectl apply` always uses the correct image.
- Deployed: `sha256:c63678dd5aec...` | Committed: `24c7913`

**Fix 13 — OLLAMA_MODEL=gemma4:31b in event-processor:**
- Added env var to `gke/event-processor/k8s/event-processor.yaml`
- Verified: `kubectl exec ... env | grep OLLAMA_MODEL` → `gemma4:31b`
- NOTE: Whether Ollama pod has gemma4:31b actually pulled is unverified — see Known Integrity State

**Fix 14 — Expanded fleet: 3 new sites, 8 new assets, 4 asset classes:**
- Added to frontend JS constants: `well_bravo` (GLIFT-BRAVO-1..4), `rig_42` (MUD-RIG42-1..3, TOPDRIVE-RIG42-1)
- FAULT_META: 8 new faults (valve_failure, thermal_runaway, bearing_wear_glift, pulsation_dampener_failure, valve_washout, piston_seal_wear, gearbox_bearing_spalling, hydraulic_leak)
- SENSOR_LABELS: gas_lift, mud_pump, top_drive sensor label sets
- Verified live: 14 grep matches in deployed HTML
- Also added these asset classes/faults to app.py ASSET_REGISTRY, FAULT_PROFILES, FAULTS_BY_CLASS, FAULT_PHYSICS, PNR_MINUTES, REMEDIATION_TIERED, REMEDIATION_COSTS, FINANCIAL_JUSTIFICATIONS, AGENT_CONTEXTS, INTELLIGENCE_FEED (already existed)

**Fix 15 — Vizier RAG constraint (SQL ILIKE, not embedding model):**
- First implementation used `get_rag_context_and_adjusted_rul()` which loads sentence_transformers — caused 60-90s latency, GKE gateway timeout, endpoint appeared broken.
- Rewritten to direct SQL: `SELECT content FROM rag_documents WHERE asset_class='esp' AND content ILIKE '%insulation%'` + regex parse for temperature.
- Result: 148ms response (was >60s timeout). Constraint still comes from OEM manual in rag_documents.
- Committed: `6db9d01`

**Fix 10b — Already live:**
- Line 1217 of index.html already has "One engineer manages 300–500 wells" explicitly. No code change needed.

---

## Current Cluster State (VERIFIED June 3, 2026 17:57)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   — AlloyDB Omni + pgvector
event-processor-bc5dbd8f-p4sdp          1/1   Running   ← EP-1 (startup model pre-load) + Fix 13 (gemma4:31b env)
fault-trigger-ui-85585dcc55-lspbt       1/1   Running   ← Fix 14 (assets) + Fix 15 SQL rewrite
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running
telemetry-simulator-867677f784-h55wd    1/1   Running
```

DB: field_intel: ~100, rag_documents: 18
event-processor: restarts=0 (pod age 10m at verification)
Vizier endpoint: 148ms ✅

---

## Outstanding Development Items (Backlog)

**HIGH PRIORITY:**
- **Fix 13 verify + Fix 13b** — Confirm `ollama list` shows gemma4:31b on the Ollama pod. If not, pull it (`kubectl exec -n gdc-pm deployment/ollama -- ollama pull gemma4:31b`). GPU warm-up ~5-15 min. Then verify event-processor narrates with 31b.

**MEDIUM PRIORITY:**
- **EP-2** — Bake `all-MiniLM-L6-v2` into event-processor Dockerfile. Add one line: `RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"` before the COPY processor.py step. This eliminates the 60-90s HuggingFace download on pod cold-start. Required to make EP-1 fix instantaneous rather than just survivable.

**LOW PRIORITY:**
- Fix 10b — H2 physics panel visual improvement (already functionally present, optional polish)
- Fix 13b — Model quality toggle in UI if 31b proves too slow for live demo

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

# event-processor Python changes — MUST use digest (YAML now pinned)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
NEW_DIGEST=$(gcloud artifacts docker images describe ${REGISTRY}/event-processor:latest --format='value(image_summary.digest)' 2>/dev/null)
# Update YAML image line to new digest, then:
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm

# Pull gemma4:31b on Ollama pod (if not already present)
kubectl exec -n gdc-pm deployment/ollama -- ollama pull gemma4:31b
# Wait 10-15 minutes for download + GPU warm-up, then verify:
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('ollama_model'))"
```

**Deploy timing:** fault-trigger-ui HTML-only: ~1 min. event-processor (only processor.py changed): ~3 min build + pull.

---

## Key Lessons (Session F)

- **Always diagnose before implementing**: The Fix 15 original implementation (embedding model) was the wrong tool for a fact retrieval task. A specific known fact (Class H temp limit) in a text document is better retrieved by SQL ILIKE than by semantic similarity. Use semantic search for "find content relevant to X"; use text search for "find the exact fact Y".
- **`kubectl apply` reverts `kubectl set image @sha256`**: The YAML stores the image as `:latest`. When `kubectl apply` is run (e.g., to add an env var), it reverts the image spec from the digest-pinned version back to `:latest`, which resolves to whatever the node has cached — potentially the old broken image. Solution: pin the digest in the YAML itself so `kubectl apply` always uses the correct image.
- **OLLAMA_MODEL env var ≠ model pulled**: Setting `OLLAMA_MODEL=gemma4:31b` in the deployment YAML tells the application what model to request. It does NOT pull that model onto the Ollama pod. Always verify with `ollama list` that the requested model is available.
- **Blocking functions in synchronous FastAPI endpoints timeout at the GKE gateway**: Any operation >60s in a sync endpoint will be cut by nginx. Either make it async, add a timeout/fallback, or choose a fast implementation (SQL vs model loading).
