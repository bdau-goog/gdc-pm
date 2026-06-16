# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-16 / git head: e80fc4b / branch: feature-trio-clean
Image: sha256:24ed283b66283e3907be368ae7a031ccf12fb174f4eded393de06d0206d01b93

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

## STEP 3: Next Implementation Task — Briefing Deck Polish

### Context (from Session BS+10)
All four briefing decks are **built, wired, deployed, and verified live**. The iframe
architecture is working. This session's 10-step task order is fully complete.

### What was verified live (commit 31f3908)
- All 7 slide endpoints return 200: h1.html, h2.html, h3.html, intro.html,
  _shared/slide.js, _shared/terms.js, _shared/slide.css
- **BUG FIXED (bae1dd9):** All 4 slide decks had `../_shared/` paths → 404 → serif font + all panels stacked.
  Fixed to `_shared/` (relative to /slides/ mount). slide.css: 200, slide.js: 200, terms.js: 200 confirmed live.
  NOTE: "No docker build needed for slides" in prior doc was WRONG — slides/ is baked into the image. Always rebuild.
- **BUG FIXED (31f3908):** Inter font not downloading in iframe context (no Google Fonts link in slide pages).
  Added `@import url('https://fonts.googleapis.com/css2?family=Inter...')` to slide.css — one change covers all 4 decks.
  Also: pump SVG max-height on H1 P2 increased 260px → 340px for better visibility.
- **FEATURE (9ecb2d6):** Keyboard zoom in slides. `+`/`=` zoom in, `-` zoom out, `0` reset to fit.
  Persists to localStorage — survives page reload. No rebuild needed to adjust zoom after this point.
  Range: 25%–300% of fit scale. Small toast shows current zoom % for 1.8s.
- **FIX (1cbfc06):** GDC Advisor activates at `gdc_detect_idx`; red marker renamed "Threshold SCADA ▲".
- **FEAT (72a332a):** H1 Decision Console legibility pass. App-level +/- zoom (body font-size, localStorage).
- **FEAT (e80fc4b):** H1 slide deck overhaul:
  - Global `--content-scale: 1.25` bumps all body text ~25% across all 4 decks; `.slide-title` pinned at 1.75rem.
  - P3 redesign: left=4 animated SVG dial gauges (PIP+Amps sweep to alarm zone, Temp+Vib stay nominal);
    right=document stream cards → GDC core callout. Replaces static two-column text layout.
  - P5 redesign: three illustrated industry cards (O&G derrick, P&E transformer, MFG motor+gear SVGs),
    each with STATE/CONTEXT columns. Replaces 3 text rows. Animated blinking sensor dots.
  - P2: wellbore SVG max-height 340→460px (taller = proportionally wider casing display).
- All 4 iframes present in assembled app (0 unresolved @@INCLUDE markers)
- 0 authored hard-$ in h1.html or h2.html (content policy passed)
- P1 split handle in h1 (data-ls-key=h1.p1.split)
- 4 data-term injections in h1.html (comparative language via terms.js)
- postMessage handler wired in app.js (run-h1 / run-h2 / run-h3 / go-horizon1)

### Remaining polish items (next session priority order)
1. **Live review of all four decks** — open each at gdc-pm.bdau.io and verify:
   - H1 P1: drag split handle, scrub sensor tiles, ▶ Play → hands off to replay
   - H1 P2: scrub wellbore animation (gas bubbles + fluid level drop), ▶ Play
   - H2 P2: check sensor tiles + timeline strip render correctly
   - Intro: verify 3 slides navigate, "▶ View Demo →" fires go-horizon1
2. **Review content in context** — any copy adjustments after seeing panels on display
3. **PIP cleanup pass** (deferred since Session BS+9) — 61 occurrences of bare `PIP`
   in app.js/app.py/templates. Low priority vs visual verification.
4. **Authored $2,500 / $150k cleanup** in live app narrative (tab_h1.html scenario
   replay sections) — also deferred. The decks are clean; the live app still has these.

### Build / deploy commands
```bash
cd gke/fault-trigger-ui
python3 ../../scripts/verify_templates.py   # must pass before build
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=90s
```

### Slide URLs for live review
| Purpose | URL |
|---|---|
| H1 deck | gdc-pm.bdau.io/slides/h1.html |
| H2 deck | gdc-pm.bdau.io/slides/h2.html |
| H3 deck | gdc-pm.bdau.io/slides/h3.html |
| Intro deck | gdc-pm.bdau.io/slides/intro.html |
| Full demo | gdc-pm.bdau.io |
| Author mode (split debug) | gdc-pm.bdau.io/slides/h1.html?author |

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| `PIP` (61 occurrences) → `Pump Inlet Pressure` in app.js/app.py/templates | ⏸ Deferred — decks use terms.js; app gets a separate cleanup pass |
| Authored `~$2,500` / `~$150k` → comparative language in app replay sections | ⏸ Deferred — decks are clean; live replay narrative still has authored $ |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Slides: `gke/fault-trigger-ui/slides/` — slides/ is **baked into the image** (COPY slides/ in Dockerfile). Always docker build + push + rollout restart after slide edits.
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` ONLY for explicit LLM test; ALWAYS pair with gpu-stop.sh
- **NO ollama-scheduler CronJobs** — both deleted Session BS+9 (conflict with GPU discipline)
- No Jinja2 in templates
- **Vizier:** 3 billing auto-triggers removed (Session BS+9). One call per explicit ▶ Run click.
