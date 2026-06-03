# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `1fdb394`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `1fdb394` — clean working tree, no uncommitted changes
**fault-trigger-ui Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
**fault-trigger-ui Digest:** `sha256:0bb289082920aa5518f3612fe033ff2d4b7e564525fe5b2c0be0b7e4fbeb304a` (Fixes 6+8, June 3)
**event-processor Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/event-processor:latest`
**event-processor Digest:** `sha256:7de3fab05e65530524137ae944cc871ca6f4baab6d709898a530298a6d7b48d1` (Fix 7, June 3)

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

# 5. Check sentence_transformers (Fix 1)
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "from sentence_transformers import SentenceTransformer; print('sentence_transformers: OK')" 2>&1

# 6. Check Fix 7 live (event-processor model default)
kubectl exec -n gdc-pm deployment/event-processor -- grep "OLLAMA_MODEL" /app/processor.py | head -1

# 7. Check Fix 6 live (Pareto hovertemplate)
curl -s http://gdc-pm.bdau.io/ | grep -c "hovertemplate"

# 8. Check Fix 8 live (VFD deploy badge)
curl -s http://gdc-pm.bdau.io/ | grep -c "Applied:"

# 9. Verify no uncommitted changes
cd ~/gdc-pm && git status && git log --oneline -4
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows** ✅
- field_intel: **~100 rows** ✅
- fault_sessions: **≥4 rows** ✅
- sentence_transformers: **OK** ✅
- Fix 7 — event-processor: `OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:latest")` ✅
- Fix 6 — hovertemplate count: **4** ✅ (one per scatter trace)
- Fix 8 — Applied badge count: **1** ✅
- git status: **clean** ✅

---

## ⚠️ Known Integrity State (VERIFIED June 3, 2026 — Post Fixes 1-8)

| Item | Display Says | Reality | Status |
|------|-------------|---------|--------|
| Gemma model | "gemma4:latest" | `gemma4:latest` running | ✅ CLEAN |
| Architecture Pane 4 | "Static O&G Corpus: 18 chunks retrieved" | `sentence_transformers==2.7.0` installed | ✅ **FIXED (Fix 1)** |
| Fleet Operations nav tab | Accessible from header | Tab exists → `mainTab='operations'` | ✅ **FIXED (Fix 2)** |
| H1 Motor Amps card | Live declining value | `motor_amps` in `current_sensors` + H1 polling | ✅ **FIXED (Fix 3)** |
| slug_flow registry | Registered in all 4 dicts | FAULTS_BY_CLASS, FAULT_PHYSICS, INTELLIGENCE_FEED, GEMMA_FINDINGS | ✅ **FIXED (Fix 4)** |
| H2 Truck Roll DB write | Fleet Financials shows $148,500 | `dispatchTruckRoll()` calls `/api/agent/truck-roll` with real event_id | ✅ **FIXED (Fix 5)** |
| Pareto chart tooltip | Blank on hover | `hovertemplate` with Hz, Cash Flow, RUL per trace | ✅ **FIXED (Fix 6)** |
| event-processor model default | Unknown | `OLLAMA_MODEL` default is now `gemma4:latest` | ✅ **FIXED (Fix 7)** |
| VFD deploy badge | No feedback after "Deploy Recommendation" | `✅ Applied: XX Hz` badge appears in Vizier Optimal card | ✅ **FIXED (Fix 8)** |
| Vizier "Bayesian" trials | 15 Bayesian exploration trials | Hardcoded `trial_hz_values` list — deterministic, not adaptive | ⚠️ Demo-acceptable |
| `last_cloud_sync` in MLOps | Live sync timestamp | Hardcoded `"2026-05-13T14:30:00Z"` | ⚠️ Low priority |
| event-processor Ollama RAG | narrative generated via gemma4 | `/api/generate` returns 404 — falls back to rule-based silently | ⚠️ Pre-existing bug |

---

## Ollama PVC Model Inventory

```
gemma4:latest    9.6 GB   ← ACTIVE (running)  Gemma 4 8B, 128K ctx
gemma3:27b       17 GB    ← fallback           Gemma 3 27B
gemma4:31b       19 GB    ← READY (downloaded) Gemma 4 31B, 128K ctx (upgrade candidate)
```

---

## NEXT SESSION PLAN — Session D

**All demo integrity violations resolved. Next session focuses on merge and polish.**

| Fix | Exact change | Verification | Complexity |
|-----|-------------|--------------|------------|
| **Merge** | `git checkout main && git merge feature-trio-scenarios` | `git log main --oneline -1` shows `1fdb394` ancestry | Trivial |
| **Fix 9** | Polling timer leaks: `h1DegPollTimer` and `h2DegPollTimer` not cleared on tab navigation. Add `if(this.h1DegPollTimer){clearInterval(this.h1DegPollTimer);}` to `setMainTab()` when switching away from horizon1/2 | Switch H1 tab after inject → navigate to Architecture → back → inject again. No duplicate polls. | Small |
| **Fix 10** | event-processor Ollama RAG 404: check if it's `format:"json"` param causing issues or model not ready. Try removing `format:"json"` and catch malformed JSON gracefully | `kubectl logs deployment/event-processor` — no more 404 errors | Small |

**Sequencing:** Merge first (trivial, no conflicts expected). Then Fix 9 (index.html only, fast deploy). Fix 10 only if time permits.

---

## What Was Done This Session (June 3, 2026 — Fixes 5-8 + Commits)

- **Git commit of Fixes 1-4** (`e3af61f`) — 4 files deployed but uncommitted. Committed.

- **Fix 5 (H2 Truck Roll DB write)** (`a96f41a`) — `dispatchTruckRoll()` now fetches `/api/recent-events?limit=50`, finds the unacknowledged `slug_flow` event for `ESP-ALPHA-3`, and POSTs `{asset_id, event_id}` to `/api/agent/truck-roll`. Backend writes acknowledged DB entry. Fleet Financials ledger now shows the resolution. Verified: `status: dispatched` from live API.

- **Fix 6 (Pareto hovertemplate)** (`1fdb394`) — Added `customdata` (RUL days) and `hovertemplate` to all 4 scatter traces in `_renderVizierPareto()`. Hovering shows `XX Hz / Cash Flow: $X,XXX,XXX / RUL: Xd`. Verified: 4 `hovertemplate` in deployed HTML.

- **Fix 7 (event-processor OLLAMA_MODEL default)** (`1fdb394`) — Changed line 52 of `processor.py` from `"gemma:2b"` to `"gemma4:latest"`. No env var was set in the k8s deployment, so this was the actual model name used. **Important deploy note:** `imagePullPolicy: IfNotPresent` on event-processor required using `kubectl set image ... @sha256:<digest>` to force the new image to be pulled. `kubectl rollout restart` alone used the cached old image. Verified: `OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:latest")` in running pod.

- **Fix 8 (VFD deploy badge)** (`1fdb394`) — After clicking "Deploy Recommendation" in H3, the Vizier Optimal card title now shows `✅ Applied: XX Hz` inline badge (green). Uses existing reactive `vizierDeployed` and `optOptimalHz` state. Verified: 1 `Applied:` in deployed HTML.

---

## Current Cluster State (VERIFIED June 3, 2026 15:56)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   0   5d19h
event-processor-5bfb656765-b9s7q        1/1   Running   0   ~2m    ← Fix 7 pod (new digest)
fault-trigger-ui-565b6d8544-9xjkm       1/1   Running   0   ~9m    ← Fixes 6+8 pod
gdc-pm-rabbitmq-server-0                1/1   Running   0   5d19h
grafana-655b6f5c7c-w2h84                1/1   Running   0   5d19h
inference-api-5697b79566-zqdpl          1/1   Running   0   5d19h
ollama-5bc5db749b-n6tb8                 1/1   Running   0   5d16h
telemetry-simulator-867677f784-h55wd    1/1   Running   0   4h41m
```

DB counts: field_intel: 100, rag_documents: 18, fault_sessions: 4  
Git: clean, head `1fdb394`

---

## Outstanding Development Items (Backlog)

**High Priority — Demo Polish**
1. **[Fix 9] Polling timer leaks (H1/H2)** — `h1DegPollTimer` and `h2DegPollTimer` not cleared when navigating away from those tabs. Add cleanup in `setMainTab()`. One function, 4 lines.
2. **[Fix 10] event-processor Ollama RAG 404** — `/api/generate` returns 404 on every call. Likely the `format:"json"` param or model-loading timing. Removing `format:"json"` or adding retry logic may fix it.

**Medium Priority**
3. **Merge `feature-trio-scenarios` → `main`** — All 8 integrity fixes deployed and verified. Ready to merge.
4. **Frontend `FAULT_META` / `ASSET_META`** — Only Pad Alpha ESP assets defined. Gas lift, mud pump, top drive invisible to frontend JS. Medium effort.

**Low Priority**
5. **`last_cloud_sync` hardcoded** — Either compute from a real AlloyDB timestamp or remove.
6. **H3 — RAG constraint** — Add pgvector retrieval of max motor temperature limits to Vizier prompt.
7. **Upgrade to gemma4:31b** — Change `OLLAMA_MODEL=gemma4:31b` env var.

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
# fault-trigger-ui (HTML/Python changes)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# event-processor (Python changes) — IMPORTANT: use set image with digest
# because imagePullPolicy: IfNotPresent will NOT pull new :latest on rollout restart
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
NEW_DIGEST=$(gcloud artifacts docker images describe ${REGISTRY}/event-processor:latest --format='value(image_summary.digest)' 2>/dev/null)
kubectl set image deployment/event-processor event-processor=${REGISTRY}/event-processor@${NEW_DIGEST} -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm
```

**Note:** fault-trigger-ui image is 3.3GB (sentence-transformers). HTML-only changes use layer cache: build ~15s, push ~14s, rollout ~22s. event-processor image is 5.49GB — push takes ~7 min. Deploy total ~9 min.

---

## Key Lessons Learned (June 3, 2026 — Fixes 5-8 Session)

- **`imagePullPolicy: IfNotPresent` on event-processor is a trap:** `kubectl rollout restart` uses the already-cached image on the node. To force a new image, use `kubectl set image deployment/... container=<registry>@sha256:<digest>` with the explicit digest. The fault-trigger-ui also has `IfNotPresent` but its node didn't have the old image cached — different nodes may behave differently.
- **event-processor image is 5.49GB:** Push takes ~7 min. Budget accordingly. Most of the size is ML/Python dependencies that rarely change.
- **Plotly `hovertemplate` needs `customdata` array:** You can't reference non-x/y data in a Plotly hovertemplate without first passing it as `customdata`. Map it with `.map(t=>t.rul_days)` and reference as `%{customdata}`.
- **VFD deploy badge uses existing reactive state:** No new data needed — `vizierDeployed` (bool) and `optOptimalHz` (string) are already reactive. The badge is a pure Vue template addition, no JS changes.
