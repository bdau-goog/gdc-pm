# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session R end — Phase 1 frontend modularization complete)
**Git Head:** `0d18533` — clean working tree
**fault-trigger-ui image digest:** `sha256:85738e70` (live, has static file split)
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
- All pods 1/1 Running · fault-trigger-ui pod name starts with `74559b58dc`
- ollama_online: True · model: gemma4:latest
- field_intel: 80–120 rows · rag_documents: 18 rows

**Also verify static assets are served:**
```bash
curl -s -o /dev/null -w "%{http_code}" http://gdc-pm.bdau.io/static/styles.css  # expect 200
curl -s -o /dev/null -w "%{http_code}" http://gdc-pm.bdau.io/static/app.js      # expect 200
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: What Was Done This Session (Session R)

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

## STEP 4: Next Implementation Task — Phase 2 (app.py Truth Layer)

**Goal:** Make the backend data honest and non-converging so the UI has clean signals.

**Four surgical `app.py` changes (one batched `replace_in_file` call):**

### 2A — `thermal_lead_time_minutes` in `/api/plot/forecast-data`
Add to the response dict after the slopes block:
```python
# Thermal lead-time: how long until motor winding temp reaches Class H limit
# dtemp_dt is in °F/min (from polyfit × READINGS_PER_MIN)
# This varies per run because _run_degrade_thread randomizes _temp_target and _k
_thermal_lead = None
if dtemp_dt > 0.05 and last_temp < 280.0:
    _thermal_lead = round((280.0 - last_temp) / dtemp_dt, 1)
```
Add `"thermal_lead_time_minutes": _thermal_lead` to the return dict.

### 2B — `class_probs` derived from recent telemetry labels
In the same endpoint, after computing health_score, add:
```python
# Multi-class probability distribution from recent model labels
# Derived from predicted_label + confidence in last 10-min DB window
from collections import Counter, defaultdict
_label_conf = defaultdict(list)
for r in rows[-20:]:
    lbl = (r.get("predicted_label") or "normal").lower()
    conf = float(r.get("confidence") or 0.0)
    _label_conf[lbl].append(conf if lbl not in ("normal","") else 1.0 - conf)
_class_probs = {}
_total_weight = max(sum(sum(v) for v in _label_conf.values()), 1.0)
for lbl, confs in _label_conf.items():
    _class_probs[lbl] = round(sum(confs) / _total_weight, 3)
```
Add `"class_probs": _class_probs` to return dict.

### 2C — Protect RAG seed doc from 100-row prune
In `_intel_generator`, the prune query deletes all but 100 rows. The GVF seed doc (inserted at inject time) gets pruned when the generator writes ~10+ docs. Fix: add a `WHERE lbl_type != 'ai' OR id IN (SELECT id FROM field_intel WHERE lbl = 'AI' ORDER BY created_at ASC LIMIT 5)` guard to protect the seed.

Simpler fix — just re-insert the seed doc on each forecast-data poll while fault is active (already done on inject, do it in `/api/plot/forecast-data` if `fault_active` and no GVF doc in recent window).

### 2D — Advisor 20s timeout + template fallback
In `agent_chat` endpoint, change `timeout=20` (from current 20) and add:
```python
return {"response": (
    f"Gas lock confirmed. PIP declining at {req.context[:80] if req.context else 'rate visible on chart'}. "
    f"Your $0 option (VFD 52→44 Hz) is available now. "
    f"Waiting increases risk — act within the viable window."
)}
```
Return this template if Ollama call fails instead of the current "Unable to reach AI model" message.

**Verify with:** `curl -s http://gdc-pm.bdau.io/api/plot/forecast-data/ESP-ALPHA-1 | python3 -c "import sys,json;d=json.load(sys.stdin);print('thermal_lead:',d.get('thermal_lead_time_minutes'),'class_probs:',d.get('class_probs'))"`

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
