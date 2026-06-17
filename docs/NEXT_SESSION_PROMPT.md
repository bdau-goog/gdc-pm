# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-17 / git head: aefc4fb / branch: feature-trio-clean
Image: sha256:373f76abb8f6440bf0b361993f1d26442dcc363ce698b09ab9cda87d75188adb

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

### PRIORITY 1 — Live review of H1 scenario replay and H2/H3 slides on BenQ ✅ ALL DEPLOYED
BS+26 changes deployed and verified:
- **HEALTH_THRESHOLD raised 0.65 → 0.87** in `h1_scenario_replay()`.
  3-run live verification: gdc_detect_idx 4.8m–9.5m BEFORE scada_alarm_idx. ✅
  GDC (XGBoost multivariate model) now consistently detects BEFORE threshold SCADA.
- **H2/H3 slide readability pass** deployed:
  - `slides/h2.html`: tile-val 0.85→1.05rem, tile-sub 0.52→0.68rem, doc-row 0.58→0.70rem,
    tile labels 0.50→0.65rem, subtitles split with second line yellow #fbbf24.
  - `slides/h3.html`: well-table 0.62→0.76rem, opt-table 0.60→0.72rem,
    subtitles split with second line yellow #fbbf24.

Review on BenQ after deploy: H1 → load scenario → ▶ Play → confirm GDC line fires before SCADA line.
Then H2 → all 3 slides, H3 → all 3 slides for readability.

### PRIORITY 2 — H2 and H3 live scenario tabs (tab_h2.html / tab_h3.html)
No changes yet to these tabs. If live review reveals readability issues at BenQ scale, apply
equivalent treatment: font floors, subtitle splits. The structural patterns are now proven in the slides.

---

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| `PIP` (61 occurrences) → `Pump Inlet Pressure` in app.js/app.py/templates | ⏸ Deferred |
| Authored `~$2,500` / `~$150k` → comparative language in app replay sections | ⏸ Deferred |
| `$150,000` × 3 in tab_architecture.html (ROI Equation + Fleet Financials) | ⏸ Deferred |

## Physics Rulings Locked (BS+20 + BS+25 retrain + BS+26 threshold tune)
- **PIP/Amps are LEADING indicators** — decline from T+0 on the power-law curve.
- **Temp/Vib are LAGGING indicators** — near-nominal through the decision window (~55% of replay),
  then gentle sub-trip rise. Temp: 197 → ~225°F. Vib: 1.4 → ~3.2 mm/s. Both GREEN throughout.
  - Only PIP/Amps cross SCADA alarm thresholds.
  - API RP 11S §4.2: thermal mass delays winding-temp rise; cavitation onset mild until high GVF.
  - RT-hardened: gdc-second-opinion SURVIVES-IF-REWORDED (absolute language softened).
- **esp_health.ubj retrained (BS+25)** on lag_onset=0.55 trajectory in xgboost==2.0.3 venv.
  RMSE=0.00185. Health < 0.30 at 90.1% of sequence (SCADA alarm zone correctly placed).
- **HEALTH_THRESHOLD = 0.87 (BS+26)** — empirically tuned so gdc_detect_idx fires 4.8–9.5m before
  SCADA alarm. hs_at_alarm ≈ 0.83 across runs; threshold 0.04-point margin above alarm zone.
  H2 HEALTH_THRESHOLD = 0.65 (untouched — H2 paraffin scenario gdc_detect_idx=23 < alarm_idx=78 ✅).
- **"Identical"** softened to **"indistinguishable on an intake-only string"** throughout.

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
