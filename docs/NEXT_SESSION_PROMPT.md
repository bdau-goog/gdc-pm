# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-16 / git head: 8fa7d0f (pre-commit) / branch: feature-trio-clean
Image: sha256:7cb896cbd996fb9a2771168b02ae9a3c74c9a3883d27caef71142663d5950a77

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
  - ⚠️ ollama-scheduler CronJobs were DELETED this session (BS+9). If you see ollamaCronJobs re-appearing, they were re-applied from a stale manifest — delete them again.
  - If ollama replicas=1 on startup: flag immediately (was it left running accidentally? GPU charges ~$0.35/hr)
- ollama_online: False, model: offline (expected dev default)
- field_intel=11, rag_documents=20

## STEP 2: Read DEMO_MASTER.md
```bash
cat docs/DEMO_MASTER.md
```
**ESPECIALLY read the new §7.5 BRIEFING ARCHITECTURE — this is the primary task for this session.**

## STEP 3: Next Implementation Task — Build Slides Foundation + All Four Decks

### Context (from Session BS+9)
All architectural decisions are LOCKED in DEMO_MASTER §7.5. The decisions are universal — no per-deck decisions to make. Build the foundation ONCE, port all four decks.

### Task Order
```
1. Build slides/_shared/ foundation (tokens.css + slide.css + slide.js + terms.js)
2. Build slides/h1.html (5 panels — proves every lever)
3. Wire iframe in tab_h1.html + postMessage handler + /slides/ route in app.py
4. Remove H1 briefing block + scale machinery from tab_h1.html + app.js
5. VERIFY LIVE: H1 renders, split drags, P3 animates, ▶ Run hands off to replay, app unchanged
6. Port slides/intro.html (3 panels — port from docs/slides/gdc-intro-slides.html)
7. Port slides/h2.html (3 panels — port from tab_h2.html briefing block)
8. Port slides/h3.html (3 panels — port from tab_h3.html briefing block)
9. Wire iframes for intro/h2/h3; remove their Vue briefing blocks + scale machinery
10. VERIFY ALL FOUR LIVE; commit
```

### Foundation spec (from DEMO_MASTER §7.5)
```
gke/fault-trigger-ui/slides/
  _shared/
    tokens.css    ← :root design tokens (migrate app styles.css :root here too)
    slide.css     ← fixed 1440×810 canvas + §4.5 card anatomy + graphic scale
    slide.js      ← fit-to-viewport + ←→/dot nav + scrubber/▶Play (applyState)
                    + CSS-grid split handles + localStorage + author-mode Copy-layout
                    + terms.js dictionary injection
    terms.js      ← content dictionary (pip, cost_trim, cost_pull, etc.)
  intro.html, h1.html, h2.html, h3.html
```

### Key reference panels to build in h1.html
- **P1 "Same Signal. Two Causes."** → demonstrates resizable Scenario↔Event split handle
- **P3 "The Hook"** → demonstrates scrub/▶Play applyState(t) animation (wellbore + metric tiles)
- Other panels: static with correct content + comparative-only copy

### App wiring
```python
# app.py: add static mount for /slides/
app.mount("/slides", StaticFiles(directory="slides"), name="slides")
```
```html
<!-- tab_h1.html: replace briefing block with: -->
<div v-if="h1BriefingMode" style="flex:1;min-height:0;overflow:hidden">
  <iframe src="/slides/h1.html" style="width:100%;height:100%;border:none"
    @load="$el.contentWindow.addEventListener('message', e => {
      if(e.data==='run-h1'){h1BriefingMode=false;loadH1Scenario();}
    })">
  </iframe>
</div>
```
- Remove `h1BriefingScale`, `h1BriefingScaleManual`, `_h1ComputeFit`, `_h1KeyZoom` from app.js
- Remove the `ResizeObserver`/`Cmd±0` block for H1 from mounted() in app.js
- Verify app renders identically after token migration before deploying

### Content policy (LOCKED in DEMO_MASTER §7.5)
- No authored hard $ in narrative copy → comparative phrases via terms.js
- `pip` → `Pump Inlet Pressure` in all deck copy (61 old occurrences in app stay for deferred cleanup)
- Live model outputs (health score, lead-time minutes, H3 bbl/d) retain real labeled numbers

### Build / deploy commands
```bash
cd gke/fault-trigger-ui
python3 ../../scripts/verify_templates.py   # must pass before build
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=90s
```

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| `PIP` (61 occurrences) → `Pump Inlet Pressure` in app.js/app.py/templates | ⏸ Deferred — decks use terms.js; app gets a separate cleanup pass after decks verified |
| Authored `~$2,500` / `~$150k` → comparative language in app templates | ⏸ Deferred — same pass as PIP cleanup |
| Ledger rows C1/C3 (authored display costs) | ⏸ Retired as display values; constants remain in app.py as traceable source |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` ONLY for explicit LLM test; ALWAYS pair with gpu-stop.sh
- **NO ollama-scheduler CronJobs** — both deleted Session BS+9 (conflict with GPU discipline)
- No Jinja2 in templates
- Branch is 10+ commits ahead of origin — commit + push this session
