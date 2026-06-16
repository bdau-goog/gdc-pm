# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-16 / git head: 0691e4a / branch: feature-trio-clean
Image: sha256:077a5209f1d4c8d6fd3a9b6dc97a02f20f19f5dd75ecf591ea59001460cb9177

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

### Sprint BS+17 — Priority 1 (First thing next session)
**Live review of all three decks end-to-end on the actual BenQ display:**
| Deck | URL | Check |
|---|---|---|
| H1 Discern | gdc-pm.bdau.io/slides/h1.html | 4-slide arc, clocks, `.detail-element` toggle, wellbore SVGs |
| H2 Classify | gdc-pm.bdau.io/slides/h2.html | 3-slide arc, hot-oil truck SVG, workover rig SVG, detail toggle |
| H3 Optimize | gdc-pm.bdau.io/slides/h3.html | 3-slide arc, SCADA/GDC comparison bars, +77.9 bbl/d badge |

After walk-through: note any copyediting, layout, or sizing issues. Make a list and batch into a single `replace_in_file` call per file before rebuilding.

---

### Sprint BS+18 — Priority 2 (after P1 live review sign-off)
**BenQ screen flicker investigation:**
- Hypothesis: Plotly poller (background `setInterval`) conflicts with VRR / adaptive-sync on BenQ PD2725U
- Fix candidate: throttle Plotly relayout calls to ≤ 4 Hz; suppress relayout when tab is not active (`document.visibilityState`)
- Files: `gke/fault-trigger-ui/static/app.js` (`_updateH1ReplayCursor`, `_renderH1ReplayChart`)
- Verify: open slides deck AND the live replay tab simultaneously and confirm no flicker

---

### Sprint BS+19 — Priority 3 (after P2 verified)
**Terminology & authored-$ cleanup pass (app.js / app.py / templates):**

| Item | Count | Location | Fix |
|---|---|---|---|
| `PIP` bare abbreviation | 61 | app.js / app.py / tab templates | → `Pump Inlet Pressure` (or `PIP` used once, spelled out on first use) |
| `~$2,500` authored figure | 7 | app.py narrative / tab_h1.html | → comparative language: `a low-cost control-room adjustment` |
| `~$150k` / `$150,000` authored figure | 10+ | app.py / tab_h1.html / tab_architecture.html | → `a six-figure workover` where on demo path; Architecture tab deferred |

Atomic fix rule: do all PIP in one batched call, all $ in a second batched call. Verify with grep before building.

---

### Sprint BS+20 — Priority 4 (deferred — do not start before P1–P3 done)
**Demo video recording prep:**
- GPU pre-flight: `./scripts/gpu-start.sh` (announce cost ~$0.35/hr before running)
- Verify live Gemma path: `gemma_modulated: True` in `/api/h1/scenario-replay`
- Walk through `docs/VIDEO_SCRIPT.md` narration scripts
- Record four videos (Overview ~60s, H1/H2/H3 ~90–120s each)
- GPU stop immediately after: `./scripts/gpu-stop.sh`

### What was completed in BS+16 (commit a434a0e)
**H2 (Classify) `h2.html`:**
- Kickers realigned: `THE SCENARIO` / `AMBIGUOUS TELEMETRY` / `ADDING CONTEXT`
- `.detail-element` on 4 sensor tile subs, 2 SCADA/APM sub-paragraphs, verdict quote, doc sub-rows ×3, action card footnote
- Slide 3 action cards: custom inline desaturated SVG thumbnails
  - Green card: Chemical hot-oil truck pumping down casing annulus (`rgba(74,222,128,0.45)` stroke)
  - Red card: Workover derrick extracting ESP completion string (`rgba(239,68,68,0.38)` stroke)

**H3 (Optimize) `h3.html`:**
- Kickers realigned: `THE SCENARIO` / `DECISION SUPPORT` / `PAD OPTIMIZATION`
- `.detail-element` on GOR character column descriptions, all 3 constraint row explanations, results card ceiling note
- Slide 3: compact side-by-side production comparison track
  - SCADA Uniform Throttle (slate bar: `rgba(148,163,184,0.1)`, `1px solid rgba(148,163,184,0.3)`)
  - GDC Joint Optimal (mint bar: `rgba(74,222,128,0.08)`, `1px solid rgba(74,222,128,0.4)`)
  - `+77.9 bbl/d uplift` callout badge between bars

**Deployment:** sha256:077a5209 — verify_templates 20/20, 971/971 — pod rollout clean.
Includes in-session RT fixes (`0691e4a`): H2 "eliminates" → "reduces bearing-wear probability"; H3 "GOR-RANKED" → "JOINT OPTIMAL SETPOINT ALLOCATION".

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
