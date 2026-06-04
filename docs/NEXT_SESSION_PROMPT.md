# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026 (Session S end — Model Prep complete)
**Git Head:** `92dc9be` — clean working tree
**inference-api image digest:** `sha256:560e4ab3` (live, has 4 classifiers + slug_flow)
**fault-trigger-ui image digest:** `sha256:565ec44a` (unchanged this session)
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
- All pods 1/1 Running (inference-api pod: `6f8c85857f-*`)
- ollama_online: True · model: gemma4:latest
- field_intel: 80–120 rows · rag_documents: 18 rows

**Also verify classifiers working:**
```bash
kubectl exec -n gdc-pm deployment/inference-api -- python3 -c "
import urllib.request, json
data = json.dumps({'psi':520,'temp_f':230,'vibration':9.5,'motor_amps':30,'dpsi_dt':-45.0,'dtemp_dt':3.5,'dvib_dt':1.2,'damps_dt':-4.0,'asset_type':'esp'}).encode()
req = urllib.request.Request('http://localhost:8080/predict', data=data, headers={'Content-Type':'application/json'}, method='POST')
d = json.loads(urllib.request.urlopen(req).read())
print('gas_lock test:', d['predicted_label'], d['confidence'])
"
# expect: gas_lock 0.94
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: What Was Done This Session (Session S)

### Model Prep COMPLETE

**Classifiers trained and deployed** (`92dc9be`):
- `scripts/train_classifiers.py`: new script, all 4 asset classifiers
- ESP: 5 classes — normal, gas_lock, sand_ingress, motor_overheat, **slug_flow (class 4)**
- `slug_flow` training signature: vibration elevated + `dtemp_dt` ≈ 0 (flat temp = H2 discriminator)
- Test accuracy: ESP 99.92% · all classes 100/200 correct in holdout
- Deploy method: `LOCAL_MODELS_DIR=/app/models` (edge-native, no GCS dependency)
- Verified live: gas_lock 94.41% · slug_flow 93.8% · sand_ingress 94.47%
- DB: `predicted_label` now shows real values (no more `inference_error`)

**Known calibration issue (non-blocking):** ESP nominal state sometimes classified as `sand_ingress` at 50-63% confidence. Cause: simulator nominal amps (~88A) overlap with sand_ingress training range (42-72A). The H1 demo uses gas_lock injection (psi <800, amps <50, dpsi_dt <-8) which is unambiguous. Fix later by retraining with corrected nominal amps range if needed.

---

## STEP 4: Next Implementation Task — H1 V2 UI INTEGRITY FIXES

**All 7 known violations from DEMO_MASTER §12 — batch into ONE `replace_in_file` on `static/app.js`:**

### Fix 1 (INTEGRITY): Motor state from actual temperature, not timer
Current: `h1ElapsedMin > 15` triggers "MOTOR CRITICAL". A hardcoded lie.
Fix: motor state must derive from `h1SensorTemp` numeric value:
- `h1SensorTemp < 220` → `motor-ok` (green)
- `220 ≤ h1SensorTemp < 250` → `motor-warn` (amber)
- `h1SensorTemp ≥ 250` → `motor-crit` (red)

### Fix 2 (INTEGRITY): GAS LOCK confidence from live model, not static text
Current: `"GAS LOCK — 94%"` is hardcoded string in dual-reality bar.
Fix: `class_probs.gas_lock` from `/api/plot/forecast-data` response already contains live confidence. Display as `{{ (classProbs.gas_lock * 100).toFixed(0) }}%` when `h1Injected`.

### Fix 3 (INTEGRITY): SCADA gauge bars from live telemetry, not fallback
Current: bars show hardcoded "1,400 PSI / 75.3 A" pre-injection.
Fix: populate `h1RawPsi/Amps/Temp` from `setMainTab` baseline call to `/api/live-telemetry`.

### Fix 4 (UX): "YOU ARE HERE" moving marker on Window of Options timeline
Current: fixed T+10m/T+18m/PNR markers with no current-position indicator.
Fix: compute `h1ElapsedMin` from `h1InjectTime` timestamp every tick. Show dot/arrow on timeline.

### Fix 5 (UX): Event-active status banner with ticking timer
Current: only signal fault is running = Reset button appears.
Fix: full-width banner: pre-inject = green "✓ WELL A-1 NOMINAL"; post-inject = amber "⚠ GAS LOCK ACTIVE · T+MM:SS · N min remaining".

### Fix 6 (UX): SCADA gauge directional labels
Current: "Alarm at 800" — no direction indication.
Fix: add "↓ Lower = worse" (PIP, Amps) or "↑ Higher = worse" (Temp) below each bar.

### Fix 7 (TECHNICAL): Drop phase-plane chart
DEMO_MASTER §15 anti-pattern. Replace with the SCADA vs GDC plain-sentence comparison block.

**Implementation approach:** All 7 fixes are in `static/app.js` (~1569 lines). Grep line numbers first, then ONE batched `replace_in_file` call. Also check `static/styles.css` for motor state CSS classes.

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain without explicit verification step
- No npm/webpack/React — vanilla HTML/JS + Vue.js CDN only
- **Batch all edits to same file in ONE `replace_in_file` call**
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- "Copilot" is a Microsoft product name — do NOT use it
- Future `index.html` edits: ~1947 lines. `app.js` edits: ~1569 lines. `app.py` edits: ~5510 lines. Always grep -n first.
