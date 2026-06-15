# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-15 / git head: e5381f6 / branch: feature-trio-clean
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
- ollama replicas=0 (GPU off by default — DO NOT scale up)
- ollama_online: False, model: offline (expected dev default)
- field_intel=11, rag_documents=20

## STEP 2: Read DEMO_MASTER.md
```bash
cat docs/DEMO_MASTER.md
```

## STEP 3: Session Priority — H1 Briefing Panel Polish (Phase 2)

**What shipped this session (Session BS+8):**
- H1 briefing panels wrapped in a fixed **1440×810 slide stage** with `ResizeObserver` scale-to-fit — fills BenQ 5K at ~1.67× scale (reveal.js pattern). git f5d5c16.
- **P1 redesigned as combined P1+P2**: left=well context (headline + well card, no metric tiles, no wellbore SVG), right=THE EVENT (scrubber + 2×2 sensor tiles showing nominal→fault transition). Old P2 removed. 5 progress dots. git e5381f6.
- `docs/H1_BRIEFING_COPY.md` — verbatim archive of all verbose P1–P6 copy (reference before condensation).

**Recording guidance confirmed:**
- Record on BenQ PD2725U (5120×2880 native, 2560×1440 logical at 2× Retina). Scale-to-fit renders at ~1.67× — ideal for both video and live projection.
- Delivery = video + live presentation. Type floor: body ≥ 1.0rem authored, labels ≥ 0.85rem.

### Next: Phase 2 — Per-Panel Content Fixes (P3–P6)

**CONFIRM P1 FIRST:** User had not yet confirmed P1 looks correct at session end. Hard-refresh BenQ and review P1 before starting P3.

| Panel | Priority fix |
|---|---|
| P3 (THE HOOK) | Body text 0.65rem→0.90rem; auto-play nominal→fault transition on panel entry (scrubber starts at 0, animates to 100 over ~2s) |
| P4 (THE MOAT) | "PIP" → "Intake Pressure" in tag-list labels; replace 4-row tag-list with visual arc-gauge cluster |
| P5 (THE DECISION) | Shorten action card bullets; add $2,500 ↔ $150,000 decision-fork graphic to fill the frame |
| P6 (THE PLATFORM) | Add industry icons for O&G / P&E / MFG rows |

**Phase 3 (independent — do any time):**
- In `app.js`: raise h1ScenarioFetchTimeout from ~20s to 60s
- On Panel 6 entry: fire warmup call so scenario loads before user clicks ▶

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
- Branch is 9 commits ahead of origin — push before session end next time
