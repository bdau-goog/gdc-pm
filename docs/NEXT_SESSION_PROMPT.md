# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-15 / git head: f336220 / branch: feature-trio-clean
Image: sha256:b2971a3fa40ad2eb9e8eafe54397547c561c6645c5032c698642d9b2338d972f

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```
Expected when healthy:
- fault-trigger-ui: 1/1 Running
- ollama replicas=0 (GPU off by default — DO NOT scale up)
- ollama_online: False, model: gemma4:latest
- field_intel/rag_documents: non-zero counts

## STEP 2: Read DEMO_MASTER.md
```bash
cat docs/DEMO_MASTER.md
```

## STEP 3: Session Priority — H1 Briefing 16:9 Scale-to-Fit + Content Polish

**Root cause of all Panel 1–6 complaints (user live-review, Session BS+7):** The briefing panels use fixed `rem`/`px` sizing that renders at laptop size and does not grow. On a large display, the 660px text column and 148px wellbore SVG leave ~1700px of dead space (P1), pumps are postage-stamp size (P3), and P4/P5/P6 have huge empty areas. The "16:9 slide-native" spec was implemented per-element but never applied a **scale-to-fit stage**.

### Phase 1 — Scale-to-fit canvas (do first, deploy, review before Phase 2)

Wrap all 6 briefing panels in a fixed **1440×810** slide stage. A `ResizeObserver` in `static/app.js` computes:

```js
scale = Math.min(frameW / 1440, frameH / 810)
```

and applies `transform: scale(${scale}); transform-origin: top center` to the stage element, centered in the parent. The stage content is authored at 1440×810 and scales uniformly to any monitor — the "slide that scales but keeps Vue animation" pattern (same as reveal.js / Google Slides). Scoped to `v-if="h1BriefingMode"` only — the live Scenario Replay already fills the frame correctly via flex-grow charts and is untouched.

**Implementation checklist:**
1. In `tab_h1.html`: replace the briefing outer div's `flex:1;overflow:hidden` with a fixed `width:1440px;height:810px` stage div, wrapped in a centering/scaling parent div.
2. In `static/app.js`: add `h1BriefingScale: 1` data prop + `ResizeObserver` on `mounted()` that watches the briefing container and sets `h1BriefingScale = Math.min(w/1440, h/810)`.
3. Bind `:style="{transform:'scale('+h1BriefingScale+')', transformOrigin:'top center'}"` to the stage div.
4. Remove all `overflow:hidden` from the stage — content is authored to fit 1440×810, no clipping needed.
5. Run `verify_templates.py` → build → deploy → user reviews.

### Phase 2 — Per-panel content fixes (after Phase 1 review)

| Panel | Fix |
|---|---|
| P1 | Raise body-text contrast (muted gray is illegible at distance); fix truncated "no dit gauge" → "no discharge gauge"; enlarge PIP/PDG callouts in the wellbore SVG |
| P2 | Add pump/intake SVG visualization showing the unloading event; remove redundant bottom "key insight" box (user: "unnecessary") |
| P3 | Replace the sand block with dispersed settling sand particles at intake (consistent with gas bubbles); auto-play nominal→fault transition on panel entry (scrubber becomes replay control) — make auto-play a P2/P3 pattern |
| P4 | Rename "PIP" → "Intake Pressure" everywhere non-engineers read it; replace 4-row STATE tag-list with a visual live gauge cluster (circular/arc gauges) vs document-card CONTEXT; dense not sparse |
| P5 | Shorten the two action cards; add a decision-fork / cost-contrast graphic (e.g. $2,500 ↔ $150,000 fork) to fill the frame |
| P6 | Add industry icons/graphics for the three rows (O&G / Power & Energy / Manufacturing) |

**Open question to confirm at session start:** "stop using PIP" — (a) spell out the acronym globally for non-engineer audiences, or (b) specifically P4's tag-list is too jargon-heavy? Current plan assumes both.

### Phase 3 — Scenario fetch latency (independent of Phases 1–2)

User observed: "Scenario — failed to fetch after 20s. Finally did fetch after 30s." Root cause: cold-model load (XGBoost + embedding model first-call JIT) races a ~20s client-side fetch timeout. Fix:
1. In `static/app.js`: raise `h1ScenarioFetchTimeout` from default (~20s) to **60s**
2. In `tab_h1.html`: on Panel 6 entry (`v-if="h1BriefingPanel===6"`), fire a lightweight warmup call (`/api/h1/scenario-replay?warm=true` or the real call with a flag that pre-loads models without returning full payload)

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
| ⓘ Physics panel: "physically identical / no sensor can disambiguate" | ✅ RESOLVED — `6e42e35` |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- Tab content: `gke/fault-trigger-ui/templates/*.html` + `app.py` (index.html = shell only)
- Run `verify_templates.py` before any template build
- Source env: `source /home/brian/gdc-pm/.env`
- GPU: ollama scale-to-zero; `./scripts/gpu-start.sh` only for explicit LLM test
- No Jinja2 in templates
