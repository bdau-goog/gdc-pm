# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-16 / git head: 047c607 / branch: feature-trio-clean
Image: sha256:a44ba16ba01dd8d0112d03ff76d938a4c4b128969cee459e2b9096c3bf48b6b7

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

### H1 slide deck readability pass complete (BS+15). Next priorities:

**Priority 1 — Live review of updated H1 deck**
Open `gdc-pm.bdau.io/slides/h1.html` on actual display and walk through all 5 slides:
- Slide 2: Wellbore SVGs now 420px (larger), two bottom info boxes removed, new amber/red PUMP legend
- Slide 3: Detail Toggle ON — see all outcome text; Details OFF — only bold headlines visible
- Slide 4: Clock (ticking, red) left + Stopwatch (snaps 2s, blue) right; clock/stopwatch symmetric
- Nav-bar: `[Details: ON/OFF]` button (green=ON, grey=OFF) — persists via localStorage
Test: click Details OFF, confirm slide 3 shows only the 3 outcome headlines per card (not the sub-text)

**Priority 2 — H2 hostile-engineer RT pass (gdc-second-opinion MCP)**
Before any H2 UI work, run the paraffin/wax scenario through one hostile-engineer RT pass.
Then write an H2_RESET.md (same format as H1_RESET.md) before touching h2.html.

**Priority 3 — BenQ screen flicker (back-burner)**
Hypothesis: Plotly 1s pollers trigger rapid window repaints which interact with BenQ VRR/G-Sync.
Fix sprint: throttle/clamp pollers and limit Plotly redraws to only necessary repaints.
DO NOT tackle this before H2 work — it is explicitly back-burnered.

**Priority 4 — Authored $ cleanup in live replay (deferred)**
61 occurrences of bare `PIP` and authored `~$2,500 / ~$150k` in app.js / app.py narrative sections.
Low urgency — decks clean via terms.js; app narrative is secondary.

### What was completed this session (commit 047c607)
BS+15 readability pass on H1 slide deck:
- tokens.css: --content-scale 1.3→1.4 (all 4 decks updated simultaneously)
- slide.css: `.detail-element`/`.hide-details` toggle CSS; analog clock + stopwatch keyframes
- slide.js: `initDetailsToggle()` — [Details: ON/OFF] nav-bar button (localStorage persistence)
- h1.html Slide 2: wellbore SVGs 340→420px; two bottom info boxes removed; amber/red PUMP legend added
- h1.html Slide 3: 6 outcome descriptions wrapped in `.detail-element` — toggled by Details button
- h1.html Slide 4: analog clock (ticking, red, "MINUTES TO HOURS") + stopwatch (snaps 2s, blue, "< 2 SECONDS") added as symmetric column headers
- h1.html: CSS readability lifts on outcome/doc/step title font sizes (0.60→0.70rem, 0.58→0.66rem)

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| `PIP` (61 occurrences) → `Pump Inlet Pressure` in app.js/app.py/templates | ⏸ Deferred — decks use terms.js; slides use full name; app gets a separate cleanup pass |
| Authored `~$2,500` / `~$150k` → comparative language in app replay sections | ⏸ Deferred — decks are clean; live replay narrative still has authored $ |
| `$150,000` × 3 in tab_architecture.html (ROI Equation + Fleet Financials Ledger) | ⏸ Deferred — Architecture tab, not H1 demo path |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Slides: `gke/fault-trigger-ui/slides/` — **baked into the image** (COPY slides/ in Dockerfile). Always docker build + push + rollout restart after slide edits.
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` ONLY for explicit LLM test; ALWAYS pair with gpu-stop.sh
- **NO ollama-scheduler CronJobs** — both deleted Session BS+9 (conflict with GPU discipline)
- No Jinja2 in templates
- **Vizier:** 3 billing auto-triggers removed (Session BS+9). One call per explicit ▶ Run click.

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
