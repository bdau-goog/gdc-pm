# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-15 / git head: f011030 / branch: feature-trio-clean

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

Expected when healthy:
- fault-trigger-ui: 1/1 Running
- ollama replicas=0 (GPU off by default — DO NOT scale up unless running LLM test)
- ollama_online: False, model: gemma4:latest (expected — GPU is off)
- field_intel/rag_documents: non-zero counts

## STEP 2: Read DEMO_MASTER.md
```bash
cat docs/DEMO_MASTER.md
```

## STEP 3: Session Priority Order

### Priority 1 — UI Review (DO FIRST)
Tab modularization is COMPLETE and deployed. Do a full tab-by-tab visual review:
- Confirm H1 Discern briefing (6 panels) + scenario replay render correctly
- Confirm H2 Classify briefing (3 panels) + paraffin/wax scenario render correctly
  - Zone 1 headline and Zone 2 action cards + doc stack should now display properly
  - Two previously unclosed divs were fixed in this session
- Confirm H3 Optimize dashboard is functional
- Note any visual regressions

### Priority 2 — Narrative / Scenario Issues
After UI review, fix any issues identified in H1/H2/H3 narratives or scenario content.

### What was done this session (for reference):
1. **Dead duplicate `app.js` removed:** Line 3715 `<script>` was dead (trapped in inert template) — removed. Only `<head defer>` copy at line 11 remains.
2. **Tab modularization (DONE, deployed, verified live):**
   - `index.html` slimmed to 159-line shell with 6 `<!-- @@INCLUDE:tabname@@ -->` markers
   - 6 tab files extracted to `gke/fault-trigger-ui/templates/` (tab_operations, tab_h1, tab_h2, tab_h3, tab_financials, tab_architecture)
   - `app.py` `index()` now assembles tabs at request time via plain string substitution (no Jinja2 — avoids `{{ }}` collision with Vue)
   - `Dockerfile` updated with `COPY templates/ ./templates/`
   - `scripts/verify_templates.py` gate: per-file `<template>` and `<div>` balance check + assembled output check
   - **verify gate caught and fixed 2 unclosed `<div>` tags in tab_h2.html** (Zone 1 headline and Zone 2 LEFT) — these were the Known Integrity Issues from prior sessions
   - **Live verification:** 1 script tag, v-cloak=1, 6 tab panels in DOM, 0 unresolved markers
3. **NEXT_SESSION_PROMPT.md:** Updated to reflect completed work.

### Build / deploy commands (for reference):
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
|-------|---------|
| H2 GDC Zone 1 div not closed | ✅ RESOLVED — fixed this session (verify gate caught it) |
| Unclosed outer `<template v-else>` | ✅ RESOLVED — `<template>` 20/20 balanced (verified) |
| Dead duplicate `app.js` at old line 3715 | ✅ RESOLVED — removed this session |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — it would destroy the live cluster
- All demo changes go into `gke/fault-trigger-ui/templates/*.html` (tabs) + `gke/fault-trigger-ui/app.py`
  - The shell `index.html` (159 lines) rarely needs editing — only for head/footer/modal changes
- After changes: run `verify_templates.py` first → then docker build → docker push → kubectl rollout restart
- Source env: `source /home/brian/gdc-pm/.env` for correct project/kubeconfig
- GPU: ollama is scale-to-zero; only start via `./scripts/gpu-start.sh` when needed
- No Jinja2 in templates — Vue's `{{ }}` collides with Jinja2 template syntax
- The 3700-line monolith is now modularized — never edit `index.html` directly for tab content again
