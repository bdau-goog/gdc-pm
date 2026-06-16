# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-16 / git head: bd9b234 / branch: feature-trio-clean
Image: sha256:6f79a6a5929860ff2e5c1f61202c9ea87517bee0fd749b556379c2b3769c2413

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

## STEP 3: Next Implementation Task — H1 Live-Scenario Harmonization (Option A)

### Context
The H1 slide deck (bd9b234) now uses the RT-hardened graduated-response framing for
drawdown. The **live replay scenario** (`tab_h1.html` + `app.py` RAG docs) still runs
the old "Emergency Shut-In = safe for both" framing, which the RT named as the
WEAKEST LINK. These must be harmonized before any demo.

### The conflict to resolve
**DEMO_MASTER rows P5-B/P5-C** say shut-in is safe on mature moderate-sand Permian well
(≤0.05% cut — June 10 Gemini+Claude reviews). **Session RT pass 3 (June 16)** says
shut-in sand-locks the pump 9/10 times. Ruling: graduated step-down framing reconciles
both — shut-in remains available but only after documents confirm the well's sand-cut
and standing-valve regime support it. P5-B/P5-C become scoped, not retired.

### Files to change (all in one session, then RT, then deploy)

**1. `gke/fault-trigger-ui/templates/tab_h1.html`** (large file — batch all edits):
- **L59**: soften "No sensor can distinguish these" → "ambiguous in the early decision
  window on an intake-only string — the documents resolve the cause and the safe action"
- **L204/L256**: SCADA drawdown card header → "🔒 Protective Default — Hold + Alert RTOC"
  (matches slide P4); drop "Emergency Shut-In"
- **L336**: REMOVE "drops velocity to 3.1 ft/s < 4.2 ft/s critical lift (SPE-174536)"
  → replace with "VFD trim CONTRAINDICATED — drops velocity below this well's sand-
  transport floor (per completion file). Step down toward minimum flush Hz."
  SPE-174536 is flagged UNVERIFIED in the ledger and must NOT appear on screen.
- **L394-402**: Rewrite drawdown action card entirely:
  OLD: `✔ GDC RECOMMENDED: Emergency Shut-In`
  NEW: `✔ GDC RECOMMENDED: Step-Down + Hold · Verify from Sonic Survey`
  Card desc: "Acoustic survey confirms fluid level 150 ft above intake — critical but
  above dry-run threshold. Reduce VFD in steps toward minimum sand-transport Hz.
  Do NOT trim below transport floor. Verify headroom from last sonic before full shut-in."
- **L402**: DELETE the line "GDC confirms this is the safe action for both fault types"
- **L407-412**: Outcome text after action taken → "STEP-DOWN COMMAND SENT — GDC
  Recommendation. VFD reducing to minimum flush Hz. Sonic survey check ordered.
  Production partially preserved pending fluid-level verification."

**2. `gke/fault-trigger-ui/app.py`** (large file — batch all edits):
- **L1272**: OEM doc guidance → "If fluid level is declining, do not trim below the
  sand-transport velocity floor. Reduce VFD in steps and verify fluid-level headroom
  from the most recent acoustic fluid-level survey before any further reduction or
  shut-in. Shut-in is appropriate only if the well's completion history and standing-
  valve configuration support it."

**3. `docs/DEMO_MASTER.md`** — ledger + §4.6:
- **§4.6 action-card spec**: Update Card B label from "Emergency Shut-In" to
  "Step-Down + Hold · Verify from Sonic" for drawdown scenario; update action text.
- **Row P5-B**: Reframe from "shut-in = safe default" to "shut-in is appropriate when
  completion file confirms low cut + standing-valve seal — GDC prescribes the graduated
  step-down and surfaces the sonic survey; shut-in is the endpoint if documents confirm."
- **Row P5-C**: Keep (the "never shut in a sandy well" rule scoping is still correct).
- **Add row P5-D**: "VFD step-down toward minimum sand-transport floor + sonic-survey
  verification is the RT-hardened graduated response for drawdown on a moderate-sand
  well where documents are available. Graduated response requires the sonic survey —
  confirming GDC's document moat." Tag: 🟡 OUR-CODE. Status: SURVIVES.

### RT pass before coding
Before touching tab_h1.html or app.py, run ONE Gemini hostile-engineer pass on the
harmonized live-scenario action text (L394 equivalent). If it comes back clean: code.
If not: adjust text first.

### Build sequence (after RT confirms)
```bash
# tab_h1.html is assembled — run verify before building
python3 scripts/verify_templates.py
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=90s
```

### Other deferred items (lower priority than the above)

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
- **REVERTED (01fec04):** e80fc4b H1 slide deck overhaul reverted.
- **STYLE (85b6813):** Legibility pass — body 13→14px; `--muted` #475569→#94a3b8; slide content-scale 1.0→1.2; slide-title pinned at 1.75rem.
- **FEAT (bd9b234):** H1 P2/P3/P4 narrative overhaul — 3-pass RT-hardened (3 hostile-engineer Gemini passes):
  - P2 Left: "GAS INTERFERENCE · HIGH GVF"; 12 bubbles distributed full column; wider pump/motor rects
  - P2 Right: "RESERVOIR DRAWDOWN · SAND RISK"; fluid starts CRITICALLY LOW (pump submerged, barely); "SAND▶INTAKE" label; drawdown action = reduce speed in steps, hold above min cooling-flow Hz, verify from last sonic survey
  - P2 banner: "Both produce the same polled-trend decline. The safe move is in the documents."
  - P3 context footer: "Assembling them correctly, fast enough, under alarm load — that's what gets missed."
  - P4 right card: "PROTECTIVE DEFAULT · Hold + Alert RTOC" — drops "Pump always protected"
  - P4 banner: "SCADA fires the alarm correctly. GDC reads the file."
  - DEMO_MASTER §4 line 190: "Emergency shutdown" → controlled step-down with sonic verification
- All 4 iframes present in assembled app (0 unresolved @@INCLUDE markers)
- 0 authored hard-$ in h1.html or h2.html (content policy passed)
- P1 split handle in h1 (data-ls-key=h1.p1.split)
- 4 data-term injections in h1.html (comparative language via terms.js)
- postMessage handler wired in app.js (run-h1 / run-h2 / run-h3 / go-horizon1)

1. **Live review of all four decks** — open each at gdc-pm.bdau.io after harmonization.
2. **PIP cleanup pass** (deferred since Session BS+9) — 61 occurrences of bare `PIP`.
3. **Authored $2,500 / $150k cleanup** in live app narrative — decks clean; app deferred.

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
