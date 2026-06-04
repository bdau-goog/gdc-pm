# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session R end — Phase 1 + Phase 2 + Fix A complete)
**Git Head:** `0d85220` — clean working tree
**fault-trigger-ui image digest:** `sha256:565ec44a` (live, has Phase 1 + Phase 2 + Fix A)
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected healthy:**
- All pods 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 80–120 rows · rag_documents: 18 rows

**Also verify static assets + Phase 2 API fields:**
```bash
curl -s -o /dev/null -w "%{http_code}" http://gdc-pm.bdau.io/static/styles.css  # expect 200
curl -s -o /dev/null -w "%{http_code}" http://gdc-pm.bdau.io/static/app.js      # expect 200
curl -s http://gdc-pm.bdau.io/api/plot/forecast-data/ESP-ALPHA-1 | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print('thermal_lead:',d.get('thermal_lead_time_minutes'),'class_probs:',d.get('class_probs'))"
# expect: thermal_lead: <non-null float> class_probs: {dict}
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: What Was Done This Session (Session R)

### Phase 2 COMPLETE — app.py Truth Layer

**What changed in `app.py` (commit faebd9f):**
- `thermal_lead_time_minutes` added to `/api/plot/forecast-data` response
  - Computed: `(280 - temp_v[-1]) / dtemp_dt` (°F/min from polyfit)
  - Varies per run — defeats "always 25m" convergence problem
  - Verified live: returned 8.9 min (dtemp_dt=9.335 °F/min)
- `class_probs` dict added — genuine model label distribution from last 20 DB rows
  - Currently shows `{'inference_error': 0.0}` — honest (ESP classifier not in inference-api pod)
  - Will show `{'gas_lock': 0.94, ...}` when inference-api has ESP classifier loaded
- RAG seed doc protection: prune query now preserves 5 oldest AI shift-notes
  - Fixes: GVF seed doc was pruned after ~10 intel cycles, collapsing RAG gap to 0
- Advisor fallback: replaces "Unable to reach AI model" with physically grounded template

### Phase 1 COMPLETE — Frontend Modularization (behavior-preserving)

**What changed:**
- `index.html`: 4347 → 1947 lines (slim shell: head + template only)
- `static/styles.css`: 829 lines (all CSS, served by FastAPI StaticFiles at /static/)
- `static/app.js`: 1569 lines (entire Vue app, loaded before `</body>`)
- `app.py`: `StaticFiles` mount added; `aiofiles` import added
- `Dockerfile`: `COPY static/ ./static/`
- `requirements.txt`: `aiofiles==23.2.1` added

**Why it matters:** Future HTML edits return ~1947 lines not 4347 (~2.2× cheaper). CSS/JS edits target individual ~800-1600 line files. Next step: split `app.js` into `core.js + h1.js + h2.js + h3.js` WHEN rebuilding each horizon tab.

**Verified live:** `/static/styles.css` HTTP 200 (76KB), `/static/app.js` HTTP 200 (87KB), page loads correctly.

---

## STEP 4: Next Implementation Task — MODEL PREP (MUST DO BEFORE ANY UI WORK)

**Why this is first:** H2's entire value proposition ("right diagnosis = right action") is 100% classifier-dependent — the demo is literally "model says slug_flow, not bearing wear → $1,500 truck roll instead of $150,000 pump pull." No working classifier = no H2. Also: H1's classification hero panel needs real `predicted_label` output from the inference-api, not `inference_error`. Phase 3 UI can be built in parallel but the classification panel component will show garbage until models are in place.

### Critical discovery (Session R): two orphaned model pipelines

| Component | Model type | Status |
|---|---|---|
| `inference-api` | XGBoost **classifier** (`esp_classifier.ubj`) — outputs fault TYPE label | **NEVER LOADED**: GCS bucket `gdc-pm-v2-models` is **completely empty**. All predictions return `inference_error`. |
| `fault-trigger-ui` | XGBoost **health regressor** (`esp_health.ubj`) — outputs health 0→1 | ✅ Working — baked into container at `models/*.ubj` |

The project pivoted from BQML classifiers → XGBoost health regressors in Phase 5.1. The health regressors were built (`retrain_edge_models.py`) and deployed. **No one created or uploaded ESP classifier models.** The inference-api has been running with an empty GCS bucket the entire project.

### Critical gap: `slug_flow` missing from `esp_classifier` label map

Current `esp_classifier` label map: `{0: normal, 1: gas_lock, 2: sand_ingress, 3: motor_overheat}` — **slug_flow is absent.**
H2 requires a classifier that distinguishes slug_flow (rising vibration + FLAT temperature) from sand_ingress/bearing_wear (rising vibration + RISING temperature). Temperature is the discriminating feature. This must be encoded in training data, not just the label map.

### Model dependency per horizon

| Horizon | Classifier needed | Health regressor needed | Cloud |
|---|---|---|---|
| **H1** Gas Lock | ✅ "gas_lock 94%" panel | ✅ early detection + health score | edge only |
| **H2** Slug Flow | ✅✅ **THE ENTIRE STORY** (slug_flow must be class 4) | — | edge only |
| **H3** VFD Optimize | — | ✅ thermal-safety evaluator for Vizier | Vizier = one cloud dep |

### Model-prep task sequence (5 steps, next session)

**Step 1 — Audit training scripts.**
Read `scripts/seed-and-train-og-models.py` and `scripts/retrain_edge_models.py`.
Determine: do they produce classifiers, regressors, or both?
Expected finding: `retrain_edge_models.py` produces health regressors only. Need to add a classifier-training path.

**Step 2 — Extend classifier training to include slug_flow as class 4.**
Update `retrain_edge_models.py` or create `train_classifiers.py`:
- `esp_classifier`: classes 0=normal, 1=gas_lock, 2=sand_ingress, 3=motor_overheat, 4=slug_flow
- Training data for slug_flow: rising vibration + **flat temperature** (temp_range overlaps nominal)
- This temperature signature is what makes H2's discrimination story true and testable
- Output: `esp_classifier.ubj`, `gas_lift_classifier.ubj`, `mud_pump_classifier.ubj`, `top_drive_classifier.ubj`

**Step 3 — Deploy classifiers via LOCAL_MODELS_DIR (recommended over GCS).**
Rationale: fully edge-native, no cloud dependency, matches the "runs entirely on-prem" value prop, consistent with how health models are deployed.
```
kubectl set env deployment/inference-api -n gdc-pm \
  LOCAL_MODELS_DIR=/app/models
```
Then bake the classifier `.ubj` files into the inference-api container alongside the Dockerfile.

**Step 4 — Verify end-to-end.**
```bash
# Inject gas_lock fault on ESP-ALPHA-1
# Wait 60s for event-processor to classify
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c \
  "SELECT predicted_label, confidence FROM telemetry_events WHERE failure_type='gas_lock' ORDER BY event_time DESC LIMIT 5;"
# Expected: predicted_label='gas_lock', confidence>0.85
# NOT: predicted_label='inference_error'
```

**Step 5 — Then resume Phase 3 UI.**
With real `predicted_label = "gas_lock"` in the DB, `class_probs` will show `{gas_lock: 0.9x}` automatically (already wired in Phase 2). The classification panel hero becomes genuine.

### Known integrity state going into next session

| Issue | Status |
|---|---|
| `predicted_label = "inference_error"` for all events | Known/documented. Fix A prevents this from corrupting `classifier_active` gate. Fix B = train + deploy classifiers. |
| `class_probs = {}` in nominal, `{inference_error: 0.0}` during faults | Honest display. Will show real probabilities once classifier is deployed. |
| temperature reframe = INCREASES model dependence | Correct. Temperature is the lagging deadline. ML classifier is the PRIMARY hero. |

### Phase 3 (HP-HMI design system) — deferred to after model-prep

Once classifiers are verified, these files are ready to receive the components:
- `static/styles.css` (~829 lines) — add `.mai`, `.classify-panel`, `.status-banner`
- `static/app.js` (~1569 lines) — add Vue components wired to `class_probs` + `thermal_lead_time_minutes`

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain without explicit verification step
- No npm/webpack/React — vanilla HTML/JS + Vue.js CDN only
- **Batch all edits to same file in ONE `replace_in_file` call** — each call returns full file
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- "Copilot" is a Microsoft product name — do NOT use it
- Future `index.html` edits: ~1947 lines (≈75K tokens). `app.js` edits: ~1569 lines. `app.py` edits: ~5510 lines. Always grep -n to locate lines before reading.
