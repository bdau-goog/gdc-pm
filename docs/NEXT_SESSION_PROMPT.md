# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-16 / git head: 1c19e31 / branch: feature-trio-clean
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

### H2/H3 Consistency Refinement Plan (BS+16). Next priorities:

**Priority 1 — Implement H2 (Classify) static slide improvements in `h2.html`**

*Kicker/Title Alignment (matches H1 three-beat arc):*
- Slide 1: `THE WELL` → **`THE SCENARIO`** (sub: unchanged)
- Slide 2: `THE SIGNATURE` → **`AMBIGUOUS TELEMETRY`** (sub: unchanged)
- Slide 3: `THE DECISION` → **`ADDING CONTEXT`** (sub: unchanged)

*Details Toggle Integration:*
- Slide 2: Wrap sensor tile sub-text (e.g., `↓ declining (pump off best-efficiency-point)`) and full APM response sub-paragraphs in `.detail-element` tags.
- Slide 3: Wrap document excerpt detail text and action card footnote in `.detail-element` tags.

*Symmetrical Visual Anchors (desaturated, match H1 aesthetic):*
- Slide 2: Enlarge wellbore SVGs to `max-height:420px` to match H1.
- Slide 3: Replace text-heavy action cards with two custom inline desaturated SVG thumbnails:
  - **Green card**: Chemical service hot-oil truck pumping down the casing annulus
  - **Red card**: Workover derrick/rig extracting the entire completion string
  - *Color palette*: Desaturated strokes only — no filled saturated color blocks. Truck: `rgba(74,222,128,0.45)` stroke. Rig: `rgba(239,68,68,0.38)` stroke.

**Priority 2 — Implement H3 (Optimize) static slide improvements in `h3.html`**

*Kicker/Title Alignment:*
- Slide 1: `THE OPPORTUNITY` → **`THE SCENARIO`** (sub: unchanged)
- Slide 2: `THE TRADEOFF` → **`DECISION SUPPORT`** (sub: unchanged)
- Slide 3: `THE OPTIMIZATION` → **`PAD OPTIMIZATION`** (sub: unchanged)

*Details Toggle Integration:*
- Slide 1: Wrap GOR table Character column descriptions in `.detail-element`.
- Slide 2: Wrap all constraint-row explanatory sub-text in `.detail-element` — leaving only the bold headers (e.g., `GAS TAKEAWAY CEILING — 8.0 MMscfd`) visible when toggled OFF.
- Slide 3: Wrap the detailed setpoint values and constraint provenance in `.detail-element`.

*Symmetrical Visual Anchor (desaturated horizontal comparison bars):*
- Slide 3: Add a compact side-by-side comparison track between the setpoint table and the results card:
  - **SCADA Uniform Throttle** (slate bar): `background:rgba(148,163,184,0.1); border:1px solid rgba(148,163,184,0.3)`
  - **GDC Joint Optimal** (mint bar): `background:rgba(74,222,128,0.08); border:1px solid rgba(74,222,128,0.4)`
  - Label above the gap: **+77.9 bbl/d uplift**

**Priority 3 — Verify, Build, and Deploy the Whole Suite**
- `python3 scripts/verify_templates.py` (must pass 20/20)
- Docker build + push + rollout restart
- Walk through h1.html, h2.html, and h3.html on actual display to confirm consistency

**Priority 4 — Deferred tasks (do not start before P1–P3 done)**
- BenQ screen flicker (Plotly poller throttle/VRR hypothesis)
- Authored `PIP` / `$2,500` / `$150k` cleanup in app.js / app.py narrative sections

### Red-Team Results (in-session hostile-engineer check, Session BS+15+plan)
*H2 Rig Pull claim attack:* "An operator won't automatically pull; they'll try hot-oil first." → SURVIVES: Best-of-breed APM (SmartSignal/Mtell) pattern-classifies the EFF+VIB signature as **bearing wear** and generates a high-severity work order for a downhole pull. GDC's L3 fusion (vendor log 52d overdue + PVT WAT 118°F + prior pull record bearings NORMAL) reclassifies to paraffin restriction, preventing the expensive pull. The RT pass found no flaw in the causal chain.
*H3 "Spreadsheet is enough" attack:* "Gas ceiling alone is an LP problem." → SURVIVES: Gas + thermal polynomial + RUL exponential decay = non-convex, non-linear joint search. GP Bandit is mathematically required.

### What was completed in BS+15 (commits 047c607 + 1c19e31)
- tokens.css: `--content-scale` 1.3→1.4 (all 4 decks)
- slide.css: `.detail-element`/`.hide-details` toggle; analog clock + stopwatch keyframes
- slide.js: `initDetailsToggle()` — `[Details: ON/OFF]` nav-bar button (localStorage)
- h1.html Slide 2: SVGs 340→420px; info boxes removed; amber/red PUMP legend
- h1.html Slide 3: 6 outcome descriptions wrapped in `.detail-element`
- h1.html Slide 4: Analog clock (red, ticking) + Stopwatch (blue, 2s snap) symmetric column headers
- h1.html: CSS readability lifts (0.60→0.70rem outcomes, 0.58→0.66rem docs/steps)

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
