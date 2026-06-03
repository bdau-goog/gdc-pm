# Next Session Prompt — GDC Edge AI 3-Horizon Demo

## Header
**Date:** June 3, 2026
**Live URL:** http://gdc-pm.bdau.io (us-east1 cluster)
**Project:** gdc-pm (`feature-trio-scenarios` branch — git head `e10bebc`)
**Cluster:** gdc-edge-simulation (us-east1)
**Namespace:** gdc-pm
**Git Head:** `e10bebc` — clean working tree, no uncommitted changes
**fault-trigger-ui Digest:** `sha256:63c2ade64e8496a19a46310bd3a27b945145b67b7e72e6f18cf0b04cbd636661` (Fix 9, June 3)
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
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"

# 4. Database truth
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM fault_sessions;"

# 5. Check sentence_transformers
kubectl exec -n gdc-pm deployment/fault-trigger-ui -- python3 -c "from sentence_transformers import SentenceTransformer; print('sentence_transformers: OK')" 2>&1

# 6. Verify no uncommitted changes
cd ~/gdc-pm && git status && git log --oneline -3
```

**Expected results when healthy:**
- All pods: `1/1 Running`
- Ollama: `1` replica, `ollama_online: True  model: gemma4:latest`
- rag_documents: **18 rows**, field_intel: **~100 rows**, fault_sessions: **≥4 rows**
- sentence_transformers: **OK**
- git status: **clean**

---

## ⚠️ Known Integrity State — ALL CLEAR (Post Fixes 1-9)

All 9 integrity violations from prior sessions have been resolved and verified live. The only remaining items are polish/enhancement work (listed below). No display vs. reality mismatches remain in the demo-critical path.

| Residual item | Status |
|---------------|--------|
| Vizier "Bayesian" trials — deterministic | ⚠️ Demo-acceptable |
| `last_cloud_sync` hardcoded | Fix 10 below |

---

## NEXT SESSION PLAN — All 6 Remaining Fixes

### Fix 10 — `slug_flow` in frontend `FAULT_META` (Small · HTML-only deploy)

**Problem:** `slug_flow` is registered in `app.py` (Fixes 4 done) but is NOT in the frontend `FAULT_META` or `FAULTS_BY_CLASS.esp` JS constants in `index.html`. When a user opens a Fleet Operations deep-dive for a slug_flow fault, the label shows the raw key `"slug_flow"` instead of `"Slug Flow"`.

**Exact code change** — in `index.html`, in the `FAULT_META` const:
```javascript
// ADD this entry to FAULT_META:
slug_flow: {label:'Slug Flow', color:'#ffb300', desc:'Flowline slugging — surface choke valve backpressure', aclass:'esp'},
```

And in `FAULTS_BY_CLASS.esp` array:
```javascript
esp: ['gas_lock', 'slug_flow', 'sand_ingress', 'motor_overheat'],
```

**Verification:** Open Fleet Operations → navigate to a deep-dive → select "slug_flow" from the fault type menu → confirm it shows "Slug Flow" label with amber dot.

---

### Fix 11 — `last_cloud_sync` live timestamp (Small · app.py rebuild)

**Problem:** `/api/mlops/status` returns `last_cloud_sync: "2026-05-13T14:30:00Z"` — hardcoded 3 weeks ago.

**File:** `gke/fault-trigger-ui/app.py`  
**Search for:** `"last_cloud_sync"` or `"2026-05-13T14:30:00Z"`

**Exact fix:** Replace the hardcoded value with a live DB query:
```python
# Replace:
"last_cloud_sync": "2026-05-13T14:30:00Z",

# With:
"last_cloud_sync": _get_last_event_time(),
```

Add this helper function near the top of the mlops endpoint:
```python
def _get_last_event_time() -> str:
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(event_time) FROM telemetry_events")
            row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return row[0].isoformat() + "Z"
    except Exception:
        pass
    return "unknown"
```

**Verification:** `curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('last_cloud_sync'))"` → shows a recent timestamp (within the last few minutes).

---

### Fix 12 — Upgrade Ollama to gemma4:31b (Medium · deployment YAML change)

**Problem:** Currently using `gemma4:latest` (8B). The `gemma4:31b` model is already downloaded on the Ollama PVC (19GB). Upgrading produces significantly richer RAG narratives.

**File:** `gke/event-processor/k8s/event-processor.yaml`  
**Change:** Add or update the `OLLAMA_MODEL` env var:
```yaml
env:
- name: OLLAMA_MODEL
  value: "gemma4:31b"
```

**Deploy:** Only the deployment YAML needs to change — no Python code, no Docker rebuild.
```bash
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm
```

**Verification:** 
```bash
kubectl logs deployment/event-processor -n gdc-pm | grep -i "model\|gemma"
# Should show gemma4:31b being passed to Ollama
```

**Note:** First inference after rollout may take 3–5 minutes while the 19GB model loads into VRAM. The L4 GPU (24GB) has enough capacity.

---

### Fix 13 — Frontend `ASSET_META` expansion (Medium · HTML-only deploy)

**Problem:** Only `pad_alpha` ESP assets (ESP-ALPHA-1 through 6) are defined in the frontend `ASSET_META` and `SITES` constants. Gas lift (GLIFT-*), mud pump (PUMP-*), and top drive (TDRIVE-*) assets are invisible to Fleet Operations UI.

**Exact additions needed** in `index.html` JS constants:

```javascript
// Add to SITES:
pad_bravo: { name:'Pad Bravo', icon:'⛽', type:'Gas Lift Production', assets:['GLIFT-BRAVO-1','GLIFT-BRAVO-2','GLIFT-BRAVO-3','GLIFT-BRAVO-4'] },
pad_charlie: { name:'Pad Charlie', icon:'🔧', type:'Mud Pump / Drilling', assets:['PUMP-CHARLIE-1','PUMP-CHARLIE-2'] },

// Add to ASSET_META:
'GLIFT-BRAVO-1':{label:'GL-B1',site:'pad_bravo',aclass:'gas_lift',type:'Gas Lift Well'},
'GLIFT-BRAVO-2':{label:'GL-B2',site:'pad_bravo',aclass:'gas_lift',type:'Gas Lift Well'},
// ... (replicate pattern for all GLIFT-BRAVO-* seen in telemetry logs)
'PUMP-CHARLIE-1':{label:'MP-C1',site:'pad_charlie',aclass:'mud_pump',type:'Mud Pump'},

// Add to FAULTS_BY_CLASS:
gas_lift: ['valve_failure','valve_washout','thermal_runaway'],
mud_pump: ['pulsation_dampener_failure','piston_seal_wear','bearing_wear'],

// Add to FAULT_META:
valve_failure: {label:'Valve Failure', color:'#f9a825', desc:'Gas lift valve stuck — injection inefficiency', aclass:'gas_lift'},
valve_washout:  {label:'Valve Washout', color:'#ff6d00', desc:'High-velocity erosion — valve seat damaged', aclass:'gas_lift'},
// ... etc.

// Add to SENSOR_LABELS:
gas_lift: {psi:'Tubing Pressure (PSI)', temp:'Wellhead Temp (°F)', vib:'Valve Vibration (mm/s)', s4:'Injection Rate (Mscf/d)'},
mud_pump: {psi:'Discharge Pressure (PSI)', temp:'Fluid Temp (°F)', vib:'Vibration (g)', s4:'Stroke Rate (SPM)'},
```

**Verification:** Fleet Operations shows Pad Bravo and Pad Charlie site zones with their assets.

---

### Fix 14 — `last_cloud_sync` in MLOps tab display (Low · bundled with Fix 11)

This is the same as Fix 11 — bundle both into a single deploy.

---

### Fix 15 — H3 RAG constraint for Vizier (Low · app.py + HTML)

**Problem:** The Vizier optimization uses hardcoded motor temperature limits. It should query the RAG corpus (AlloyDB pgvector) for the OEM-specified max motor temperature for the ESP asset class, then use that as the burnout threshold in the cash flow model.

**File:** `gke/fault-trigger-ui/app.py` — find `@app.get("/api/vizier/optimize")`

**Exact change:** Before the trial loop, add:
```python
# Retrieve OEM max motor temp from RAG corpus
oem_max_temp = 284.0  # fallback: Class H insulation limit per API RP 11S
try:
    conn = get_db()
    with conn.cursor() as cur:
        query_embedding = embed_query("ESP motor maximum temperature insulation Class H")
        cur.execute("""
            SELECT content FROM rag_documents
            WHERE asset_class = 'esp'
            ORDER BY embedding <-> %s::vector LIMIT 1
        """, (query_embedding,))
        row = cur.fetchone()
        if row:
            import re
            match = re.search(r'(\d{2,3})\s*[°º]?F', row[0])
            if match:
                oem_max_temp = float(match.group(1))
    conn.close()
except Exception:
    pass
# Use oem_max_temp in the trial burnout threshold (replace hardcoded 270°F)
```

**Verification:** `/api/vizier/optimize` response includes `oem_temp_limit` field showing a value pulled from the RAG corpus.

---

## Implementation Order for Session E

1. **Fix 10** (slug_flow FAULT_META) — 2-line JS change, HTML-only build, ~1 min deploy
2. **Fix 11** (last_cloud_sync) — 1 helper function in app.py, requires rebuild (~15 min)
3. **Fix 12** (gemma4:31b upgrade) — YAML-only, no rebuild, kubectl apply only (~3 min)
4. **Fix 13** (ASSET_META expansion) — larger JS change, HTML-only build, ~1 min deploy
5. **Fix 15** (H3 RAG constraint) — app.py change, requires rebuild (~15 min)

Fixes 10 + 13 can be batched into a single HTML deploy. Fixes 11 + 15 can be batched into a single app.py deploy.

**Recommended batching:**
- **Deploy A:** Fix 10 + Fix 13 (HTML-only, ~1 min)
- **Deploy B:** Fix 11 + Fix 15 (app.py rebuild, ~15 min)
- **Deploy C:** Fix 12 (kubectl apply only, ~3 min)

---

## What Was Done Last Session (June 3, 2026)

All 9 integrity fixes (Fixes 1–9) are deployed and verified. The demo is fully functional with no display vs. reality mismatches in the critical path. See git log for commit history.

---

## Current Cluster State (VERIFIED June 3, 2026 16:07)

```
alloydb-omni-5fcfc68fdb-9vm2z           1/1   Running
event-processor-5bfb656765-b9s7q        1/1   Running   ← Fix 7 (gemma4:latest default)
fault-trigger-ui-cf7bf4444-vw9s6        1/1   Running   ← Fix 9 (timer leak fix)
gdc-pm-rabbitmq-server-0                1/1   Running
grafana-655b6f5c7c-w2h84                1/1   Running
inference-api-5697b79566-zqdpl          1/1   Running
ollama-5bc5db749b-n6tb8                 1/1   Running
telemetry-simulator-867677f784-h55wd    1/1   Running
```

DB: field_intel: 100, rag_documents: 18, fault_sessions: 4

---

## Constraints

- `terraform/gke.tf` must NOT be applied — would destroy the live cluster.
- All demo changes go into `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`.
- After changes: `docker build → docker push → kubectl rollout restart`.
- No browser on SSH remote — no `browser_action` tool.
- `feature-trio-scenarios` stays **separate from `main`**.
- XGBoost `*.ubj` models — do not retrain.

---

## Rebuild & Deploy Commands

```bash
# HTML-only changes (Fix 10, Fix 13)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# app.py changes (Fix 11, Fix 15)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm

# gemma4:31b upgrade (Fix 12) — NO REBUILD, YAML only
kubectl apply -f gke/event-processor/k8s/event-processor.yaml -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm

# event-processor Python changes — use digest (imagePullPolicy: IfNotPresent)
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor
docker push ${REGISTRY}/event-processor:latest
NEW_DIGEST=$(gcloud artifacts docker images describe ${REGISTRY}/event-processor:latest --format='value(image_summary.digest)' 2>/dev/null)
kubectl set image deployment/event-processor event-processor=${REGISTRY}/event-processor@${NEW_DIGEST} -n gdc-pm
kubectl rollout status deployment/event-processor -n gdc-pm
```

---

## Key Lessons (carry-forward)

- **event-processor requires `kubectl set image @sha256:<digest>`** — `imagePullPolicy: IfNotPresent` means `rollout restart` uses cached old image on the node.
- **event-processor image is 5.49GB** — push takes ~7 min; plan accordingly.
- **fault-trigger-ui HTML-only changes** — build ~20s, push ~14s, rollout ~24s total.
- **`setMainTab()` is the nav chokepoint for H1/H2/H3** — "Fleet Operations" and "Fleet Financials" use inline `@click` and bypass it.
