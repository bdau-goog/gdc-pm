# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-16 / git head: 6f5bbf4 / branch: feature-trio-clean
Image: sha256:c7ba64ebf11b7af9ca60bdd2bcc09213b9b67bce71ffceff0044077b6d8138bc

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

### H1 scenario is now fully harmonized and deployed. Next priorities:

**Priority 1 — CxO narrative validation (discuss first, don't code)**
The RT pass (Session BS+13) returned SCENARIO VERDICT: KEEP but flagged two CxO narrative
weaknesses:
1. "HITL/Agentic" framing is now on screen (GDC Agent badge + Approve & Execute buttons) ✅
2. The "same sensor signal, two opposite correct actions, documents resolve which" story needs
   live review on a display — ask user to pull up gdc-pm.bdau.io H1 tab and confirm the
   narrative lands before proceeding to H2/H3.

**Priority 2 — Live deck + live replay review**
Open all 4 slides + the H1 live replay on the actual display. Verify:
- H1 slide deck P4 "PROTECTIVE DEFAULT · Hold + Alert RTOC" matches the live replay card
- H1 live replay shows "GDC Agent · Action package ready · Awaiting RTOC approval" badge
- Drawdown action card shows "Approve & Execute — Step-Down + Hold"
- Override modal shows "step-down to minimum flush Hz, not an aggressive trim"
- Sonic log modal shows "150 ft above intake" (not 240 ft)

**Priority 3 — H2 second-opinion hostile pass (gdc-second-opinion MCP)**
Before any H2 UI work, run the paraffin/wax scenario through one hostile-engineer RT pass.
The paraffin scenario passed gates 1-5 but has not been RT-tested on the current live
scenario text (tab_h2.html). Run pass, then code.

**Priority 4 — Authored $ cleanup in live replay (deferred twice)**
61 occurrences of bare `PIP` and authored `~$2,500 / ~$150k` remain in:
- `gke/fault-trigger-ui/static/app.js` and `app.py` narrative sections
- These are NOT in the slide decks (decks clean via terms.js)
Low urgency — decks are what the audience sees; app narrative is secondary.

### What was verified live (commit 6f5bbf4)
- 19 new H1 strings live: GDC Agent, Step-Down + Hold, Approve & Execute, six-figure, etc.
- Emergency Shut-In: 0 in H1 drawdown decision path
- SPE-174536: 0 on any live screen
- "$150,000" in override modal: 0 (→ "six-figure")
- Sonic log modal: 150 ft (was 240 ft — integrity fix)
- Remaining 3 × "$150,000": Architecture tab (pre-existing deferred, not H1)
- verify_templates.py: 20/20 templates, 971/971 divs ✅

## Known Integrity Issues
| Issue | Status |
|-------|--------|
| `PIP` (61 occurrences) → `Pump Inlet Pressure` in app.js/app.py/templates | ⏸ Deferred — decks use terms.js; app gets a separate cleanup pass |
| Authored `~$2,500` / `~$150k` → comparative language in app replay sections | ⏸ Deferred — decks are clean; live replay narrative still has authored $ |
| `$150,000` × 3 in tab_architecture.html (ROI Equation + Fleet Financials Ledger) | ⏸ Deferred — Architecture tab, not H1 demo path |

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
