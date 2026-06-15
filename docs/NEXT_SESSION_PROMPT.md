# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-15 / git head: see `git log --oneline -1` / branch: feature-trio-clean

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

The app is restored and working (2026-06-15). Session priority order is fixed:

### Priority 1 — Tab Modularization (DO FIRST — prevents recurrence)
Split `index.html` into per-tab template files to eliminate the unclosed-template trap permanently. The 3,700-line monolith is the root cause of this class of failures.

**Approach (no build pipeline needed):**
- Extract H1, H2, H3, Architecture, Financials, Operations each into `gke/fault-trigger-ui/templates/tab_h1.html`, `tab_h2.html`, etc.
- Modify `app.py`'s home route to assemble them at request time via marker-based string substitution (NOT Jinja2 — Vue's `{{ }}` collides with Jinja2)
- Marker convention: `<!-- @@INCLUDE:tab_h1@@ -->` in shell `index.html`
- Add `COPY templates/ ./templates/` to Dockerfile
- Add `scripts/verify_templates.py` gate: per-file `<template>`/`</template>` and `<div>`/`</div>` balance check + Playwright `hasCloak=false` assertion
- Each tab file is now ~500 lines — manageable, readable, independently verifiable
- **Assembled output must be byte-identical to current `index.html`** (minus grafana meta inject) — prove with local diff before building

**Tab boundary map (verified line numbers before modularization):**
```
Shell HEAD:        lines 1–34     (doctype, head, header nav, app-body open)
tab_operations:    lines 35–337   (303 lines — legacy tab, no header button)
tab_h1:            lines 338–1617 (1,280 lines — DISCERN)
tab_h2:            lines 1618–2281 (664 lines — CLASSIFY)
tab_h3:            lines 2282–2692 (411 lines — OPTIMIZE)
tab_financials:    lines 2695–2832 (138 lines)
tab_architecture:  lines 2836–3603 (768 lines — REFERENCE)
Shell TAIL:        lines 3605–3716 (feed modal, justify modal, #app close, toast, body close)
```

**Note:** Lines shifted by 1 after dead `app.js` removal (was 3717 lines, now 3716). Re-verify with `grep -n` before extracting.

### Priority 2 — UI Review
After modularization, do a full tab-by-tab visual review of the live app:
- Confirm H1 Discern briefing + scenario replay render correctly
- Confirm H2 Classify briefing + paraffin/wax scenario render correctly
- Confirm H3 Optimize dashboard is functional
- Note any visual regressions to fix

### Priority 3 — Narrative / Scenario Issues
After UI review, fix any issues identified in the H1/H2/H3 narratives or scenario content.

### What was fixed this session (for reference):
1. **Blank page fix (DONE, Session BS+3):** `app.js` moved to `<head defer>` — immune to template trapping. Verified: `hasCloak=false`, `display=block`, `height=720`, 6 tab panels in DOM. Committed `7150b0e`.
2. **Image pinning (DONE):** k8s deployment was SHA-pinned; fixed with `kubectl set image ... :latest`.
3. **Dead duplicate `app.js` removed (DONE, this session):** Line 3715 `<script src="/static/app.js"></script>` was dead (trapped in inert `<template>`) — removed. Only the `<head defer>` copy at line 11 remains.

## Known Integrity Issues
| Issue | Status |
|-------|---------|
| H2 GDC Zone 1 div not closed — `<template v-if="h2VerdictRevealed">` nested inside Zone 1 without close | ✅ RESOLVED — `<template>` count verified 20/20 balanced (Session BS+3 fix `5702859`) |
| Unclosed outer `<template v-else>` — verify comment-tagged closes balance | ✅ RESOLVED — 20/20 balanced (verified this session) |
| Dead duplicate `app.js` at line 3715 | ✅ RESOLVED — removed this session |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — it would destroy the live cluster
- All demo changes go into `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`
- After changes: docker build → docker push → kubectl set image (DO NOT use sha-pinned deployment)
- Source env: `source /home/brian/gdc-pm/.env` for correct project/kubeconfig
- GPU: ollama is scale-to-zero; only start via `./scripts/gpu-start.sh` when needed
- No Jinja2 in templates — Vue's `{{ }}` collides with Jinja2 template syntax
