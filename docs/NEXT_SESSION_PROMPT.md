# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-17 / git head: (commit pending) / branch: feature-trio-clean
Image: sha256:fb9a214912c2b8d523af2750ed747239a3310a7e99363f15faefb92780dd3553

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```
Expected when healthy:
- fault-trigger-ui: 1/1 Running
- **ollama replicas=0 (GPU OFF — DO NOT scale up)**
- ollama_online: False, model: offline (expected dev default)
- field_intel=11, rag_documents=20

## STEP 2: Read DEMO_MASTER.md
```bash
cat docs/DEMO_MASTER.md
```

## STEP 3: Next Implementation Tasks

### PRIORITY 1 — Live review of H1 scenario replay on BenQ ✅ LEAD/LAG PHYSICS DEPLOYED
BS+25: `esp_health.ubj` retrained on lag_onset=0.55 trajectory. H1 replay trajectory also aligned.
- Temp at lag onset (step 66): +0.8°F — essentially flat ✅
- Vib at lag onset (step 66): +0.235 mm/s — essentially flat ✅
- Temp end: 220.2°F / Vib end: 2.936 mm/s — sub-trip, green ✅
- PIP leading: 1237→959 PSI / Amps leading: 83.8→69.3 A ✅
- model_used: esp_health.ubj / Bayes: 93.1% ✅
- **🔴 OPEN BUG:** GDC dashed marker fires AFTER "Threshold SCADA ▲" in the replay chart.
  The agreed contract: GDC (XGBoost multivariate model) ALWAYS detects before threshold SCADA.
  We conceded Advanced APM *might* match GDC. We never conceded threshold SCADA beats GDC.

  Root cause: HEALTH_THRESHOLD=0.65 is too low. With lag_onset=0.55, SCADA fires at ~step 63
  (52.5% of window, just before lag onset at 55%). The XGBoost health score at step 63 is ~0.84
  (healthy by training standards — full feature set hasn't contributed yet). Threshold 0.65
  isn't crossed until step ~76 → gdc_detect_idx > alarm_idx.

  Fix (ONE line in h1_scenario_replay): raise HEALTH_THRESHOLD from 0.65 → 0.82 so detection
  fires at ~step 50 on PIP/Amps slope features alone, before the SCADA alarm at step 63.
  Also verify on fluid_drawdown fault type.

Review on BenQ after fix: H1 → load scenario → ▶ Play — confirm:
  - GDC dashed line fires BEFORE Threshold SCADA line
  - Temp/Vib flat through decision window, then gentle sub-trip rise
- App landing opens on `Intro` tab ✓

### PRIORITY 2 — H2/H3 readability pass
Apply equivalent improvements to `slides/h2.html` and `slides/h3.html` (same structural treatment as H1 slide pass).

---

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| `PIP` (61 occurrences) → `Pump Inlet Pressure` in app.js/app.py/templates | ⏸ Deferred |
| Authored `~$2,500` / `~$150k` → comparative language in app replay sections | ⏸ Deferred |
| `$150,000` × 3 in tab_architecture.html (ROI Equation + Fleet Financials) | ⏸ Deferred |

## Physics Rulings Locked (BS+20 + BS+25 retrain)
- **PIP/Amps are LEADING indicators** — decline from T+0 on the power-law curve.
- **Temp/Vib are LAGGING indicators** — near-nominal through the decision window (~55% of replay),
  then gentle sub-trip rise. Temp: 197 → ~225°F. Vib: 1.4 → ~3.2 mm/s. Both GREEN throughout.
  - Only PIP/Amps cross SCADA alarm thresholds.
  - API RP 11S §4.2: thermal mass delays winding-temp rise; cavitation onset mild until high GVF.
  - RT-hardened: gdc-second-opinion SURVIVES-IF-REWORDED (absolute language softened).
- **esp_health.ubj retrained (BS+25)** on lag_onset=0.55 trajectory in xgboost==2.0.3 venv.
  RMSE=0.00185. Health < 0.30 at 90.1% of sequence (SCADA alarm zone correctly placed).
  H2 unaffected: paraffin scenario gdc_detect_idx=23 < alarm_idx=78 ✅.
- **"Identical"** softened to **"indistinguishable on an intake-only string"** throughout.
- **BS+20 "no retrain" ruling superseded** by BS+25 — retrain was necessary to align model with
  lead/lag physics (old model keyed on concurrent temp/vib rise).

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Slides: `gke/fault-trigger-ui/slides/` — **baked into the image** (COPY slides/ in Dockerfile)
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` ONLY for explicit LLM test; ALWAYS pair with gpu-stop.sh
- **NO ollama-scheduler CronJobs**
- No Jinja2 in templates
- **Vizier:** One call per explicit ▶ Run click only

## Build / deploy commands
```bash
cd gke/fault-trigger-ui
python3 ../../scripts/verify_templates.py   # must pass before build
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=90s
```

## Slide URLs for live review
| Purpose | URL |
|---|---|
| H1 deck | gdc-pm.bdau.io/slides/h1.html |
| H2 deck | gdc-pm.bdau.io/slides/h2.html |
| H3 deck | gdc-pm.bdau.io/slides/h3.html |
| Intro deck | gdc-pm.bdau.io/slides/intro.html |
| Full demo | gdc-pm.bdau.io |
| Author mode (split debug) | gdc-pm.bdau.io/slides/h1.html?author |
