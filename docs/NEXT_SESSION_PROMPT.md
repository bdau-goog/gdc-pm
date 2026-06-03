# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `4a50823`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `4a50823` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:7bd9c7b8b47db3e8b6d428ffaeeb068a5b427040db9f0786cab9073dc832c672` (Fix 10/11/12, June 3)
**event-processor Digest:** `sha256:7de3fab05e65530524137ae944cc871ca6f4baab6d709898a530298a6d7b48d1` (Fix 7, June 3)
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

# 7. Check Fix 11 live (slug_flow should appear in FAULT_META)
curl -s http://gdc-pm.bdau.io/ | grep -c "slug_flow"

# 8. Check Fix 10 live (Physics & Logic panels present)
curl -s http://gdc-pm.bdau.io/ | grep -c "Physics.*Logic"

# 9. Verify git state
cd ~/gdc-pm && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows**, field_intel: **~100 rows**, fault_sessions: **≥4 rows**
- sentence_transformers: **OK**
- last_cloud_sync: **recent timestamp** (2026-06-03T...), NOT `2026-05-13`
- slug_flow grep: **≥7** (in FAULT_META, banner, and functions)
- Physics & Logic grep: **≥8** (3 buttons + 3 panel titles + other)
- git head: `4a50823`

---

## ⚠️ Known Integrity State — ALL CLEAR (Post Fixes 1-12)

All integrity violations from prior sessions are resolved and verified live. No display vs. reality mismatches remain.

| Item | Status |
|------|--------|
| `last_cloud_sync` | ✅ Live from AlloyDB MAX(event_time) — was hardcoded 2026-05-13 |
| `slug_flow` in FAULT_META | ✅ Added with color `#ffb300`, label "Slug Flow" |
| H1/H2/H3 Physics panels | ✅ Deployed — ⓘ button toggles collapsible panel |
| All prior fixes (1-9) | ✅ Verified and deployed in previous sessions |

---

## NEXT SESSION PLAN — Session F: 4 Remaining Items

| Fix | Change (one sentence) | Verification test | Est. complexity |
|-----|----------------------|-------------------|-----------------|
| 13  | Upgrade Ollama to gemma4:31b — add OLLAMA_MODEL env var to event-processor deployment YAML | `curl -s http://gdc-pm.bdau.io/api/mlops/status \| python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('ollama_model'))"` → shows gemma4:31b | Small (YAML only) |
| 14  | Add gas lift (GLIFT-BRAVO-*) and mud pump (PUMP-CHARLIE-*) assets to frontend SITES/ASSET_META/FAULTS_BY_CLASS/FAULT_META/SENSOR_LABELS JS constants | Fleet Operations → verify 4 GLIFT-BRAVO and 3 PUMP-CHARLIE assets visible | Medium (HTML-only) |
| 15  | H3 Vizier RAG Constraint — retrieve Class H insulation temp limit from pgvector before trial loop instead of hardcoded 270°F | Check Vizier trials use pgvector-retrieved constraint; temp limit changes between runs | Low (app.py rebuild) |
| Fix 10b | H2 banner: note already has the key discriminator point, but the ⓘ panel doesn't show the scale argument — add "1 engineer: 300–500 wells" explicitly | Visual check in browser | Trivial (HTML-only) |

### Recommended Batching for Session F

- **Deploy A:** Fix 13 (kubectl apply to event-processor YAML, no rebuild, ~3 min + 5 min GPU warm-up)
- **Deploy B:** Fix 14 + Fix 10b (HTML-only, ~1 min rebuild)
- **Deploy C:** Fix 15 (app.py rebuild, ~9 min)

---

## What Was Done This Session (Session E — June 3, 2026)

**Fix 11 — `slug_flow` in frontend `FAULT_META`** (HTML-only):
- Added `slug_flow: {label:'Slug Flow', color:'#ffb300', desc:'Flowline slugging — surface choke valve backpressure', aclass:'esp'}` to `FAULT_META`
- Updated `FAULTS_BY_CLASS.esp` to `['gas_lock','slug_flow','sand_ingress','motor_overheat']`
- Fleet Operations Craft Fault Modal now shows Slug Flow as a selectable option

**Fix 12 — Live `last_cloud_sync` timestamp** (app.py):
- Added `_get_last_event_time()` helper that queries `MAX(event_time) FROM telemetry_events` from AlloyDB
- Replaced hardcoded `"2026-05-13T14:30:00Z"` with `_get_last_event_time()` in `/api/mlops/status`
- Verified live: returns `2026-06-03T16:55:19.396022+00:00Z`

**Fix 10 — H1/H2/H3 Physics & Logic Info Panels** (HTML-only):
- Added `showH1Info`, `showH2Info`, `showH3Info: false` to Vue `data()`
- Added `ⓘ Physics & Logic` toggle button (`.hb-btn.btn-info`) to each Horizon banner's `hb-actions` div
- Added collapsible `.physics-panel` div between each `horizon-banner` and `h3-dashboard`
- H1 panel: Gas Lock failure physics, why engineers miss it, how GDC catches it, cost table ($147,500)
- H2 panel: Slug flow surface-vs-downhole discrimination, scale argument (1 engineer × 300-500 wells), cost table ($148,500) + "why H2 is the most vulnerable" note
- H3 panel: VFD thermal tradeoff, why manual optimization fails, how Vizier works, financial model formula, strategy comparison table

All three fixes deployed to live cluster at digest `sha256:7bd9c7b8b47db3e8b6d428ffaeeb068a5b427040db9f0786cab9073dc832c672`.

---

## Current Cluster State (VERIFIED June 3, 2026 17:07)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running   — AlloyDB Omni + pgvector
event-processor-5bfb656765-b9s7q        1/1   Running   ← Fix 7 (gemma4:latest default)
fault-trigger-ui-68dd6db7b4-nccdq       1/1   Running   ← Fix 10/11/12 (June 3)
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running
telemetry-simulator-867677f784-h55wd    1/1   Running
```

DB: field_intel: ~100, rag_documents: 18, fault_sessions: 4+

---

## Outstanding Development Items (Backlog)

**HIGH PRIORITY:**
- **Fix 13** — gemma4:31b upgrade: add `OLLAMA_MODEL: "gemma4:31b"` env var to `gke/event-processor/k8s/event-processor.yaml`. YAML-only, no rebuild. Allow 5 min GPU warm-up.
- **Fix 14** — ASSET_META expansion: Add GLIFT-BRAVO-1..4 and MUD-RIG42-1..3 and TOPDRIVE-RIG42-1 to frontend `SITES`, `ASSET_META`, `FAULTS_BY_CLASS`, `FAULT_META`, `SENSOR_LABELS`. Gas lift faults: valve_failure, thermal_runaway, bearing_wear_glift. Mud pump faults: pulsation_dampener_failure, valve_washout, piston_seal_wear. Top drive: gearbox_bearing_spalling, hydraulic_leak.

**MEDIUM PRIORITY:**
- **Fix 15** — H3 Vizier RAG constraint: In `/api/vizier/optimize`, call `get_rag_context_and_adjusted_rul('ESP-ALPHA-5', 'motor_overheat', 60)` to retrieve the Class H insulation limit from pgvector, then use it as the burnout threshold (replacing hardcoded 270°F). The retrieved limit is stored in `rag_context`; parse it with regex.

**LOW PRIORITY:**
- Fix 10b — H2 physics panel scale argument: explicitly state "1 production engineer manages 300–500 wells" in the panel text (already implied, but should be made explicit as the anchor counter-argument).
- Fix 13b — if gemma4:31b is too slow for demo, add a "model quality" toggle in the MLOps panel to switch between 8b (fast) and 31b (quality) at demo time.

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

# event-processor Python changes — use digest (imagePullPolicy: IfNotPresent)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
NEW_DIGEST=$(gcloud artifacts docker images describe ${REGISTRY}/event-processor:latest --format='value(image_summary.digest)' 2>/dev/null)
kubectl set image deployment/event-processor event-processor=${REGISTRY}/event-processor@${NEW_DIGEST} -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm
```

**Deploy timing:** fault-trigger-ui HTML-only: ~1 min. event-processor (5.49GB): ~9 min. event-processor YAML only: ~3 min + 5 min GPU warm-up.

---

## Key Lessons (Session E)

- **Parallel `replace_in_file` writes to the same file CAN succeed**: Both the CSS addition and FAULT_META addition ran in parallel and both applied correctly. Verify with grep after, not just from final_file_content display.
- **Physics & Logic panels are commercially critical**: The H2 panel's "Yes — for one well" counter-argument to "an engineer can see this" is the most important sentence in the entire demo for handling technical pushback.
- **`_get_last_event_time()` helper pattern**: AlloyDB helper functions should use `get_db()` and close the connection explicitly, not rely on context managers, to avoid psycopg2 connection leak in FastAPI sync functions.
- **event-processor requires `kubectl set image @sha256:<digest>`** — `imagePullPolicy: IfNotPresent` means `rollout restart` uses cached old image on the node.
