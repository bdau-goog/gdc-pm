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

## STEP 4: Next Implementation Task — Phase 3 (HP-HMI Design System)

**Goal:** Build the shared reusable visual components in `static/styles.css` and `static/app.js` that H1/H2/H3 all use.

### Components to build (in Phase 3):
1. **Moving-analog-indicator** — HP-HMI bar with live pointer, gray normal band, alarm limit on the indicator itself. CSS class `.mai` + Vue component. Split into LEADING group (PIP, Amps) and LAGGING group (Temp).
2. **Fault classification panel** — Probability bar chart from `class_probs` API field. The "this is categorically ML not threshold" visual.
3. **Status banner** — Full-width, gray when nominal → amber/red on fault. Uses `thermal_lead_time_minutes` and `class_probs.gas_lock` to drive state.
4. **Gray/color discipline** — Nominal state: almost entirely gray/desaturated. Fault state: color blooms.

### API fields now available (Phase 2 ✅):
- `thermal_lead_time_minutes` — the per-run-varying lead-time number
- `class_probs` — multi-class probability distribution
- `adjusted_rul_minutes` — RAG context-adjusted estimate
- `slopes.dtemp_dt` — temperature rate of change (°F/min)

### Phase 3 target files:
- `static/styles.css` — add `.mai`, `.classify-panel`, `.status-banner` CSS
- `static/app.js` — add Vue component definitions; wire to `class_probs` + `thermal_lead_time_minutes`

Both files are now modular (~829 and ~1569 lines) — edits are ~6× cheaper than before Phase 1.

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
