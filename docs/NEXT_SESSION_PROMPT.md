# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-17 / git head: ab428f3 / branch: feature-trio-clean
Image: sha256:f7c8218f0c4643863818f93615d910daedc5f28ff76b00b97b52637aac78a77e

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

### PRIORITY 1 — Live review of H1 scenario replay + slides on BenQ ✅ FLICKER RESOLVED
BS+21–BS+23 flicker fix confirmed. **Three chart bugs also fixed (commit `ab428f3`):**
- Temp now 197→~225°F (not 250°F) — matches BS+20 physics ruling (API RP 11S §4.2)
- Vib now 1.4→~3.2 mm/s (not 5+ mm/s) — sub-ISA HI, sub-trip as required
- Legend box removed (`showlegend:false`)
- Duplicate "Threshold SCADA▲" scrubber label removed

Review on BenQ: H1 → load scenario → ▶ Play — confirm temp/vib stay sub-threshold.

- `gdc-pm.bdau.io/slides/h1.html` — Slide 1 scrub NOMINAL→FAULT:
  - PIP + Amps decline (amber at threshold)
  - Temp rises gently 197→225°F (green, sub-trip, ↗ arrow, "Rising but lagging")
  - Vib rises gently 1.4→3.2 mm/s (green, sub-trip, ↗ arrow, "Rising but lagging")
- Slide 2: CASING GAS label (right wellbore, drawdown) brightens as fluid drops
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

## Physics Rulings Locked (BS+20)
- **Temp + Vib BOTH rise in the H1 decision window** for BOTH gas lock and drawdown.
  - Temp: 197 → ~225°F (lagging, sub-trip; thermal mass, API RP 11S §4.2)
  - Vib: 1.4 → ~3.2 mm/s (lagging, sub-trip; cavitation, non-specific)
  - Both stay GREEN throughout — only PIP/Amps cross alarm thresholds
  - Confirmed by: Gemini hostile RT (FAILS on flat claim), internal XGBoost probe
    (flat temp/vib delays detection by 8 min), fault_signatures.py training data
- **No retrain of XGBoost models** — rising temp/vib is training-consistent
- **"Identical"** softened to **"indistinguishable on an intake-only string"** throughout

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
