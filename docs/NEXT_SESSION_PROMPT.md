# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `e4504ec`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `e4504ec` ⚠ Uncommitted changes in working directory (4 files: app.py, index.html, requirements.txt, NEXT_SESSION_PROMPT.md)
**Image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
**Image Digest:** `sha256:4b120c0473787bb56ca43de88d457978e86f7d6834daa63fe81214f55674a64e` (deployed June 3, 2026 — Fixes 1-4)
**Image Size:** 3.3 GB (includes sentence-transformers 2.7.0)

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

# 5. Check sentence_transformers (Fix 1 — should print OK)
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "from sentence_transformers import SentenceTransformer; print('sentence_transformers: OK')" 2>&1

# 6. Check slug_flow is registered
curl -s http://gdc-pm.bdau.io/api/fault-physics/slug_flow | python3 -c "import sys,json;d=json.load(sys.stdin);p=d['physics'];print('slug_flow:',p['horizon_label'],p['total_hours'],'h')"

# 7. Check Fleet Operations nav tab exists in live HTML
curl -s http://gdc-pm.bdau.io/ | grep -o "Fleet Operations"

# 8. Commit pending changes (FIRST ACTION)
cd ~/gdc-pm && git add -A && git commit -m "fix: Fixes 1-4 — sentence-transformers, Fleet Operations tab, motor_amps live binding, slug_flow registry"
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows** ✅
- field_intel: **~100 rows** ✅
- fault_sessions: **≥4 rows** ✅
- sentence_transformers: **OK** ✅ (Fix 1 deployed)
- slug_flow: **Hours 2.0 h** ✅ (Fix 4 deployed)
- Fleet Operations: **Fleet Operations** ✅ (Fix 2 deployed)

---

## ⚠️ Known Integrity State (VERIFIED June 3, 2026 — Post Fixes 1-4)

| Item | Display Says | Reality | Status |
|------|-------------|---------|--------|
| Gemma model | "gemma4:latest" | `gemma4:latest` running | ✅ CLEAN |
| Architecture Pane 4 | "Static O&G Corpus: 18 chunks retrieved" | `sentence_transformers==2.7.0` NOW installed in fault-trigger-ui | ✅ **FIXED (Fix 1)** |
| Fleet Operations nav tab | Accessible from header | Tab now has nav button → `mainTab='operations'` | ✅ **FIXED (Fix 2)** |
| H1 Motor Amps card | Live declining value | `motor_amps` now in `current_sensors` dict AND bound in H1 polling | ✅ **FIXED (Fix 3)** |
| slug_flow registry | Registered in all 4 dicts | FAULTS_BY_CLASS, FAULT_PHYSICS, INTELLIGENCE_FEED, GEMMA_FINDINGS all populated | ✅ **FIXED (Fix 4)** |
| H2 Truck Roll savings | Fleet Financials shows $148,500 | DB write never happens — frontend never calls `/api/agent/truck-roll` | ❌ FIX-5 |
| Vizier "Bayesian" trials | 15 Bayesian exploration trials | Hardcoded `trial_hz_values` list — deterministic, not adaptive | ⚠️ Demo-acceptable |
| `last_cloud_sync` in MLOps | Live sync timestamp | Hardcoded `"2026-05-13T14:30:00Z"` | ⚠️ Low priority |
| Grafana URL | `35.190.137.145` | Live Grafana LB IP | ✅ Fixed |
| GPU CronJobs | SUSPENDED ✅ | Manual only | ✅ |

---

## Ollama PVC Model Inventory

```
gemma4:latest    9.6 GB   ← ACTIVE (running)  Gemma 4 8B, 128K ctx
gemma3:27b       17 GB    ← fallback           Gemma 3 27B
gemma4:31b       19 GB    ← READY (downloaded) Gemma 4 31B, 128K ctx (upgrade candidate)
```

---

## NEXT SESSION PLAN — Session B (1 fix + git commit)

**First action: commit the 4 changed files** (they are deployed but uncommitted):
```bash
git add -A && git commit -m "fix: Fixes 1-4 — sentence-transformers, Fleet Operations tab, motor_amps live binding, slug_flow registry"
```

| Fix | Exact change | Verification | Complexity |
|-----|-------------|--------------|------------|
| **Commit pending** | `git add -A && git commit -m "fix: Fixes 1-4..."` | `git log --oneline -1` shows new commit | Trivial |
| **Fix 5** | `index.html` `dispatchTruckRoll()`: before starting countdown, call `fetch('/api/recent-events?limit=5')`, find the most recent event for `ESP-ALPHA-3` with `failure_type='slug_flow'`, capture its `id`, then call `fetch('/api/agent/truck-roll', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({asset_id:'ESP-ALPHA-3', event_id: <captured_id>})})`. If no event found, pass `event_id: 0` (backend handles gracefully). | Inject Slug Flow → dispatch truck roll → wait 5s → Fleet Financials ledger shows `ESP-ALPHA-3 / slug_flow / $148,500` entry | Medium |

**Where Fix 5 is in index.html:**
- Search for `async dispatchTruckRoll()` in the JS section
- The function currently only starts a countdown timer without calling the backend
- The `/api/agent/truck-roll` endpoint already exists in app.py (PID-ready with `event_id: int` parameter)
- Pattern: `fetch('/api/recent-events?limit=50')` → filter `.failure_type === 'slug_flow'` and `.asset_id === 'ESP-ALPHA-3'` → take `[0].id` → POST to truck-roll

---

## What Was Done This Session (June 3, 2026 — Fixes 1-4)

*   **Fix 1 (sentence-transformers)** — Added `sentence-transformers==2.7.0` to `gke/fault-trigger-ui/requirements.txt`. Rebuilt and deployed. Verified: `kubectl exec ... python3 -c "from sentence_transformers import SentenceTransformer; print('OK')"` → `sentence_transformers: OK`. Static RAG corpus (18 OEM manual chunks) now actually retrieved during agent queries.

*   **Fix 2 (Fleet Operations nav tab)** — Added `<div class="hdr-tab" :class="{active: mainTab==='operations'}" @click="mainTab='operations';fetchHorizonAlerts()">Fleet Operations</div>` to header in `index.html` (after "Horizon 3: Optimization" tab, before "Fleet Financials"). The full HITL deep dive workflow is now reachable from the UI.

*   **Fix 3 (H1 Motor Amps live binding)** — Two-part fix: (a) Added `"motor_amps": reading.get("motor_amps")` to `current_sensors` dict in `_run_degrade_thread` in `app.py`; (b) Added `if(cs.motor_amps !== undefined && cs.motor_amps !== null) this.h1SensorAmps = cs.motor_amps.toFixed(1)+' A';` to the H1 polling block in `index.html`. Motor Amps card on H1 now shows live declining value during gas lock injection.

*   **Fix 4 (slug_flow registry)** — Added `slug_flow` to 4 dictionaries in `app.py`:
    - `FAULTS_BY_CLASS["esp"]`: `["gas_lock", "slug_flow", "sand_ingress", "motor_overheat"]`
    - `FAULT_PHYSICS["slug_flow"]`: `{horizon_label:"Hours", total_hours:2.0, scada_sensor:"vib", pnr_sensor:"vib", primary_sensor:"vib", intervention_type:"field_notification"}`
    - `INTELLIGENCE_FEED["slug_flow"]`: 3 items (choke log, separator test, shift note — all physically accurate for slug flow)
    - `GEMMA_FINDINGS["slug_flow"]`: vibration drift + flat motor temp discriminator statement

*   **Deployed** — docker build (took ~5 min for sentence-transformers) → docker push (3.3GB image, took ~8 min) → kubectl rollout restart → `deployment "fault-trigger-ui" successfully rolled out` in 2m19s.

---

## Current Cluster State (VERIFIED June 3, 2026 11:56)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   0   5d15h
event-processor-7d9b594b6b-j5jp8        1/1   Running   0   5d15h
fault-trigger-ui-859787b97c-xmg8m       1/1   Running   0   ~4m    ← NEW pod (Fixes 1-4)
gdc-pm-rabbitmq-server-0                1/1   Running   0   5d15h
grafana-655b6f5c7c-w2h84                1/1   Running   0   5d15h
inference-api-5697b79566-zqdpl          1/1   Running   0   5d15h
ollama-5bc5db749b-n6tb8                 1/1   Running   0   5d12h
telemetry-simulator-867677f784-h55wd    1/1   Running   0   ~40m
```

DB counts: field_intel: 100, rag_documents: 18, fault_sessions: 4

---

## Outstanding Development Items (Backlog)

**High Priority — Integrity Violations**
1. **[Fix 5] H2 Truck Roll DB write** — Frontend `dispatchTruckRoll()` never calls `/api/agent/truck-roll`. Truck roll resolution is invisible in Fleet Financials. Fix: fetch latest event_id from `/api/recent-events`, then POST to `/api/agent/truck-roll`. (See Session B plan above.)

**Medium Priority**
2. **Pareto chart tooltip** — Add `hovertemplate` with Hz, Cash Flow ($M), RUL (d) labels.
3. **Deploy VFD feedback (H3)** — After "Deploy Recommendation", show which Hz was applied.
4. **Polling timer leaks (H1/H2)** — `h1DegPollTimer` and `h2DegPollTimer` not cleared on tab navigation. Add cleanup to `beforeUnmount()`.
5. **Merge `feature-trio-scenarios` → `main`** — Once Fix 5 deployed and verified.

**Low Priority**
6. **`last_cloud_sync` hardcoded stale** — Either compute from a real AlloyDB timestamp or remove the field.
7. **`processor.py` default `OLLAMA_MODEL`** — Change default from `"gemma:2b"` to `"gemma4:latest"` (line 52).
8. **Frontend `FAULT_META` / `ASSET_META`** — Only Pad Alpha ESP assets defined. Gas lift, mud pump, top drive invisible to frontend JS.
9. **Upgrade to gemma4:31b** — Change `OLLAMA_MODEL=gemma4:31b` env var to test higher quality reasoning.
10. **Horizon 3 — RAG constraint** — Add pgvector retrieval of max motor temperature limits to Vizier prompt.

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

**Note:** Image is now 3.3GB (sentence-transformers adds ~2.3GB). Build takes ~5 min, push takes ~8 min, rollout pull takes ~2 min. Total deploy time: ~15 min.

---

## Key Lessons Learned (June 3, 2026 — Fixes 1-4 Session)

- **sentence-transformers adds 2.3GB to image**: Build time increased from ~2min to ~5min, push from ~1min to ~8min, GKE pull from ~30s to ~2min. Budget 15min for a full deploy cycle with this dependency.
- **`docker push ... | tail -10` buffers output**: The log file stays 0 bytes until the push completes. Better to check `ps aux | grep "docker push"` or `gcloud artifacts docker images list` to monitor push progress.
- **All 4 slug_flow dicts needed**: A fault type is only fully functional when it appears in FAULTS_BY_CLASS, FAULT_PHYSICS, INTELLIGENCE_FEED, and GEMMA_FINDINGS. Missing any one causes silent failures in different parts of the UI.
- **motor_amps needs BOTH app.py and index.html changes**: Backend must populate `current_sensors["motor_amps"]` AND frontend must read it. Either change alone does nothing.
