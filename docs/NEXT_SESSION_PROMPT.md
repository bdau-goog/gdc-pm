# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 5, 2026 (Session U end)  
**Git Head:** `55beab3` — integrity audit + fault_signatures.py + trajectory classifier v1  
**fault-trigger-ui image:** `sha256:34c0c8fe` (scaled to 0)  
**inference-api image:** `sha256:560e4ab3` (scaled to 0, still has Session S classifiers)  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected healthy (Session V start):**
- fault-trigger-ui, inference-api, telemetry-simulator: 0/0 replicas (intentional)
- AlloyDB, RabbitMQ, Grafana, event-processor, Ollama: 1/1 Running
- ollama_online: True · model: gemma4:latest
- mlops/status: connection refused (expected — fault-trigger-ui is at 0)
- field_intel: 80–120 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md + INTEGRITY_AUDIT.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
cat ~/gdc-pm/docs/INTEGRITY_AUDIT.md   # NEW Session U — read before writing any code
```

**INTEGRITY_AUDIT.md is mandatory reading before Session V.** It contains the complete classified table of violations to fix.

---

## STEP 3: Known Integrity State — Fix in Session V

All 9 items below are 🔴 VIOLATION per `docs/INTEGRITY_AUDIT.md` (Session U). Session V fixes them all before any feature work.

| ID | File | Line(s) | Problem | Fix |
|---|---|---|---|---|
| V-01 | index.html | 377 | `"94% confidence"` claim — model not yet verified | Replace with `"≥92% once confirmed"` + ⓘ citation |
| V-02 | index.html | 429 | `'GAS LOCK - 94% confidence'` static badge text | Bind to `h1TopClass` + `h1TopClassProb` from `class_probs` |
| V-03 | index.html | 440–456 | `h1ElapsedMin > 15` drives CRITICAL motor state | Bind to `h1SensorTemp >= 260` threshold |
| V-04 | index.html | 464 | GVF `'68%' : '22%'` hardcoded | Bind `h1GvfPct` from inject params / degrade-status API |
| V-05 | index.html | 647,681 | `"52%"` in H2 Physics text — no model backing | Replace with `"initially low, building to ≥90% once confirmed"` |
| V-06 | index.html | 731 | H2 AI Confidence card `52% (Ambiguous)` — H2 not built | Add `"PREVIEW — not yet live"` badge to H2 tab |
| V-07 | app.js | 1413 | `'Gas lock diagnosis confirmed at 94% confidence'` advisor pre-load | Remove hardcoded %; use `"pattern detected · confidence building"` |
| V-08 | app.py | 60-63, 4870 | `OLLAMA_DISPLAY_MODEL` — designed to show wrong model name | Delete OLLAMA_DISPLAY_MODEL; report `OLLAMA_MODEL` |
| V-09 | index.html | 1459–1724, 1800 | Architecture tab chips look live; `$1,200` amount wrong | Add `"Walkthrough Example — not live data"` banner; fix `$1,200` |

**Additional Session V task:** Wire `h1TopClass` / `h1TopClassProb` / `h1TopClassAll` from the existing `class_probs` field in `/api/plot/forecast-data` into the H1 tab Vue data. The backend already returns this dict; the frontend never consumes it.

**Approach for all V-02 / V-03 / V-04 fixes:** One batched `replace_in_file` call to `index.html` + one batched call to `app.js`. Verify after with grep that no hardcoded values remain. Do NOT make sequential single-block edits.

---

## STEP 4: Session W — Model Recreate (after Session V is deployed + verified)

See `docs/MODEL_FOUNDATIONS.md §9` for the full Session W runbook. Summary:

1. **Fix `train_classifiers.py` slope window** (Step 3b): match 60-reading deque + `dt_minutes = (n−1)/12` to `processor.py:get_slopes()` exactly
2. **Tag ramp-progress `t`** per training row (Step 3c): enables stage-stratified verification (overall + developed precision)
3. **Scale up fault-trigger-ui + inference-api + telemetry-simulator:**
   ```bash
   kubectl scale deployment/fault-trigger-ui --replicas=1 -n gdc-pm
   kubectl scale deployment/inference-api --replicas=1 -n gdc-pm
   kubectl scale deployment/telemetry-simulator --replicas=1 -n gdc-pm
   ```
4. **Run ≥3 injections** (gas_lock + slug_flow + normal) to populate `injection_events`
5. **Retrain**: `python3 scripts/train_classifiers.py --asset-class esp --n-trajectories 600 --n-normal 6000 --rounds 300`
6. **Verify non-circular**: replay `injection_events` rows through `/predict` → confusion matrix → pass = gas_lock ≥ 0.92 developed, slug_flow ≥ 0.90 developed
7. **Build `esp_thermal.ubj`** + wire into `vizier_optimize()` (closes M-03 / V3 in MODEL_FOUNDATIONS)
8. **Rebuild + deploy inference-api** with exact digest

---

## STEP 5: After Session W — Confidence Widget

Build the "Live Diagnostic Confidence" widget in H1 tab (approved Session U):
- Live `class_probs` bars for all 5 classes, sorted descending, color by stage
- Stage badge: Emerging (<60%) / Developing (60–85%) / Confirmed (≥85%)
- Static chip: "Overall precision: 81% · Confirmed-stage: 92%" (both numbers, with ⓘ explaining the distinction)
- Binds dual-reality bar string (V-02) to live top class + prob

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- "Copilot" is a Microsoft product name — do NOT use it anywhere
- No static values that imitate live output — global `.clinerules §6` now enforces this
- Failing model `.ubj` files are NEVER committed — only passing models (per ML Integrity rule)
