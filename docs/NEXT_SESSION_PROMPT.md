# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-16 / git head: 4ed1c8c / branch: feature-trio-clean
Image: sha256:7b4158a347ac131eec07c34befbd5aff97d64a859968498cee87a0d5cde4dd9f

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

### H1 slide deck now fully redesigned and deployed. Next priorities:

**Priority 1 — Live review of H1 deck (5 slides)**
Open `gdc-pm.bdau.io/slides/h1.html` on actual display and walk through all 5 slides:
- Slide 1: THE SCENARIO — sensor tiles + resizable split
- Slide 2: AMBIGUOUS TELEMETRY — wellbore SVG animation (scrubber: gas bubbles vs fluid drain + sand)
- Slide 3: DECISION SUPPORT — Motor Burnout vs. Sand Bridging decision matrix
- Slide 4: ADDING CONTEXT — Without GDC / With GDC two-column
- Slide 5: INDUSTRIAL APPLICATION — O&G / P&U / Maritime + Data Gravity banner
Also verify intro.html Slide 2 shows "Compliance & Sovereignty" and expanded Data Gravity copy.

**Priority 2 — H2 hostile-engineer RT pass (gdc-second-opinion MCP)**
Before any H2 UI work, run the paraffin/wax scenario through one hostile-engineer RT pass.
Then write an H2_RESET.md (same format as H1_RESET.md) before touching h2.html.

**Priority 3 — Authored $ cleanup in live replay (deferred twice)**
61 occurrences of bare `PIP` and authored `~$2,500 / ~$150k` remain in:
- `gke/fault-trigger-ui/static/app.js` and `app.py` narrative sections
- These are NOT in the slide decks (decks clean via terms.js)
Low urgency — decks are what the audience sees; app narrative is secondary.

### What was completed this session (commits 2864d0a + 4ed1c8c)
H1 slide deck 5-slide redesign per H1_RESET.md:
- --content-scale 1.2 → 1.3 (global legibility lift)
- Slide 2: AMBIGUOUS TELEMETRY (was THE HOOK) — correct gas-bubble physics (distributed column, fluid level stays HIGH/STABLE)
- Slide 3 NEW: DECISION SUPPORT — **Motor Burnout vs. Sand Bridging** (2×2 matrix; terminology corrected in-session: "Gas Burnout" → "Motor Burnout" per API RP 11S §4.2; "Sand Bridging" = standard Permian field term)
- Slide 4: ADDING CONTEXT (merged old slides 3+4) — Manual context search vs GDC 4-step RAG
- Slide 5: INDUSTRIAL APPLICATION (was THE PLATFORM) — new O&G/P&U/Maritime examples
- intro.html: Compliance & Sovereignty + expanded Data Gravity copy
- docs/H1_RESET.md: immutable design spec for H1 (with terminology correction note)

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
