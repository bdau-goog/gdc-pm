# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 5, 2026 (Session V end)  
**Git Head:** `bd28fdf` — all 9 integrity violations resolved (V-01 through V-09)  
**fault-trigger-ui image:** `sha256:b57066d4` (scaled to 1, **running**)  
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

**Expected healthy (Session W start):**
- fault-trigger-ui: 1/1 Running (scaled up Session V)
- inference-api, telemetry-simulator: 0/0 replicas (intentional)
- AlloyDB, RabbitMQ, Grafana, event-processor, Ollama: 1/1 Running
- ollama_online: True · model: gemma4:latest
- field_intel: 80–120 rows · rag_documents: 18 rows

---

## STEP 2: Read DEMO_MASTER.md + INTEGRITY_AUDIT.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
cat ~/gdc-pm/docs/INTEGRITY_AUDIT.md
```

**Session V completed all 9 🔴 violations from INTEGRITY_AUDIT.md.** The audit is now clean for all display violations. Remaining model integrity issues (M-01 through M-04) are tracked in MODEL_FOUNDATIONS.md.

---

## STEP 3: Known Integrity State — Session W

All 9 display violations from Session U are **resolved and deployed** as of `bd28fdf`:

| ID | Status | Notes |
|---|---|---|
| V-01 | ✅ Fixed | `≥92% once confirmed` |
| V-02 | ✅ Fixed | Bound to `h1TopClass`/`h1TopClassProb` from `class_probs` |
| V-03 | ✅ Fixed | Motor state from `parseInt(h1SensorTemp)` thresholds |
| V-04 | ✅ Fixed | GVF from intel feed parse; `'—'` pre-inject |
| V-05 | ✅ Fixed | `builds to ≥90% as slug pattern confirms` |
| V-06 | ✅ Fixed | `PREVIEW — not yet live` badge |
| V-07 | ✅ Fixed | `pattern detected · confidence building` |
| V-08 | ✅ Fixed | `OLLAMA_DISPLAY_MODEL` deleted; reports `OLLAMA_MODEL` |
| V-09 | ✅ Fixed | Arch tab banner + `$1,200 → ~$2,000` |

**One note on V-04 (GVF):** `h1GvfPct` is populated by parsing the `_intel_generator` GVF shift note from `h1FeedItems`. This populates ~20s after injection when the first GVF doc arrives. Pre-inject shows `'—'` (honest). This is intentional and correct.

---

## STEP 4: Session W — Model Recreate

See `docs/MODEL_FOUNDATIONS.md §9` for the full Session W runbook. Summary:

1. **Fix `train_classifiers.py` slope window** (Step 3b): match 60-reading deque + `dt_minutes = (n−1)/12`
2. **Tag ramp-progress `t`** per training row (Step 3c)
3. **Scale up inference-api + telemetry-simulator:**
   ```bash
   kubectl scale deployment/inference-api --replicas=1 -n gdc-pm
   kubectl scale deployment/telemetry-simulator --replicas=1 -n gdc-pm
   ```
4. **Run ≥3 injections** (gas_lock + slug_flow + normal) to populate `injection_events`
5. **Retrain**: `python3 scripts/train_classifiers.py --asset-class esp --n-trajectories 600 --n-normal 6000 --rounds 300`
6. **Verify non-circular**: replay `injection_events` through `/predict` → confusion matrix → gas_lock ≥ 0.92, slug_flow ≥ 0.90
7. **Build `esp_thermal.ubj`** + wire into `vizier_optimize()`
8. **Rebuild + deploy inference-api**

---

## STEP 5: After Session W — Confidence Widget

Build the "Live Diagnostic Confidence" widget in H1 tab (approved Session U):
- Live `class_probs` bars for all 5 classes, sorted descending
- Stage badge: Emerging (<60%) / Developing (60–85%) / Confirmed (≥85%)
- `h1TopClass`/`h1TopClassProb` are now wired — the widget just needs the HTML/CSS

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- "Copilot" is a Microsoft product name — do NOT use it anywhere
- No static values that imitate live output — global `.clinerules §6` enforces this
- Failing model `.ubj` files are NEVER committed
