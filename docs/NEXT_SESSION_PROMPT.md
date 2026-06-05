# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 5, 2026 (Session T end — Model Foundations + Injection Log)
**Git Head:** `89040f9` — clean working tree
**fault-trigger-ui image:** `sha256:34c0c8fe` (live — has injection_events + popup)
**inference-api image:** `sha256:560e4ab3` (live — has 5-class ESP classifier)
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

**Also verify injection log is working:**
```bash
curl -s http://gdc-pm.bdau.io/api/injection-log | python3 -c "import sys,json;d=json.load(sys.stdin);print('injection_events count:',d.get('count'))"
# expect: count ≥ 1 (at least 1 from Session T verification)
```

---

## STEP 2: Read DEMO_MASTER.md + MODEL_FOUNDATIONS.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
cat ~/gdc-pm/docs/MODEL_FOUNDATIONS.md  # NEW — canonical model spec
```

---

## STEP 3: What Was Done This Session (Session T)

### Model Foundations complete

**Session S classifiers are deployed but NOT trusted** — training distributions were
invented, not derived from `FAULT_PROFILES`. The injection event log now exists to
provide the non-circular verification dataset needed before the clean retrain.

**Commits:**
- `92dc9be` — Session S: ESP classifier 5-class (invented ranges, known-bad)
- `89040f9` — Session T: injection_events table + popup + MODEL_FOUNDATIONS.md

**docs/MODEL_FOUNDATIONS.md (new):**
- Canonical ESP fault-signature table (gas_lock PSI 875–1100 from live DB, not 350–800)
- Per-horizon model inventory: H1 (classifier+health), H2 (classifier), H3 (esp_thermal — not built yet)
- 4 open integrity violations documented
- Clean-run verification protocol (replay injection log → confusion matrix)
- Next-retrain-session runbook (exact commands, pass/fail thresholds)

**Injection event log (live + verified):**
- `injection_events` table in AlloyDB — persists actual drawn values + bounds every inject
- `GET /api/injection-log` — returns events for non-circular verification replay
- `showInjectionPopup()` in app.js — 5s popup on every inject showing drawn params vs bounds
- Verified: `gas_lock point psi_target: 882.9 [875–1100] amps_target: 23.5`

### Known integrity violations (open)
| Violation | Status |
|---|---|
| `esp_classifier.ubj` trained on invented ranges, not live FAULT_PROFILES | ❌ Deployed but not trusted |
| `esp_health.ubj` endpoint values disagree with live injection | ❌ Needs replay verification |
| `vizier_optimize()` uses hardcoded polynomial, not XGBoost | ❌ H3 silent-lie |
| `FAULT_PROFILES["slug_flow"]["vib_range"]` = (2.2, 3.2) — too narrow | ❌ Needs widening to (4.0, 6.5) |

---

## STEP 4: Next Implementation Task — CLEAN MODEL RETRAIN

**Prerequisite:** Run ≥3 demo injections (gas_lock + slug_flow + normal) to populate
`injection_events` with real drawn-value samples. These rows ARE the non-circular test set.

### The 5-step clean retrain (from MODEL_FOUNDATIONS.md §7)

**Step 1:** Update `FAULT_PROFILES["slug_flow"]["vib_range"]` → `(4.0, 6.5)` in `app.py` (one line)

**Step 2:** Create `gke/shared/fault_signatures.py` — derives from live `FAULT_PROFILES` +
event-processor's `get_slopes()` logic. This becomes the single source of truth.

**Step 3:** Rewrite `scripts/train_classifiers.py` to use trajectory-based approach:
- Simulate the degrade ramp (same `((i+1)/steps)^k` formula as `_run_degrade_thread`)
- Compute slopes using the same first-last difference as `processor.py:get_slopes()`
- 600 trajectories × ~60 steps per fault, 6,000 normal readings
- All distributions sourced from `FAULT_PROFILES` — never invented

**Step 4:** Train + verify non-circularly:
```sql
-- Pull real gas_lock rows time-matched to injection_events
SELECT te.psi, te.temp_f, te.vibration, te.motor_amps, te.failure_type
FROM telemetry_events te
JOIN injection_events ie ON te.asset_id = ie.asset_id
  AND te.event_time BETWEEN ie.inject_time AND ie.inject_time + INTERVAL '10 minutes'
WHERE ie.fault_type = 'gas_lock' LIMIT 500;
```
Replay these rows through `/predict`. Pass = gas_lock ≥ 0.92, slug_flow ≥ 0.90.

**Step 5:** Build `esp_thermal.ubj` + wire into `vizier_optimize()` (closes H3 silent-lie).

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- **Batch all edits to same file in ONE `replace_in_file` call**
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- "Copilot" is a Microsoft product name — do NOT use it
- Future `index.html` edits: ~1947 lines. `app.js` edits: ~1633 lines. `app.py` edits: ~5600 lines. Always grep -n first.
