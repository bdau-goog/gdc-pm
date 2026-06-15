# Next Session Prompt — GDC Edge AI Demo (Operational State)
Date: 2026-06-15 / git head: 04fd9dd / branch: feature-trio-clean

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

## STEP 3: Session Priority Order (next session)

The app is restored and working (2026-06-15). Session priority order is fixed:

### Priority 1 — Tab Modularization (DO FIRST — prevents recurrence)
Split `index.html` into per-tab template files to eliminate the unclosed-template trap permanently. The 3,700-line monolith is the root cause of this class of failures — a missing `</template>` on line 2143 of 3,700 silenced the entire app for 4 days.

**Approach (no build pipeline needed):**
- Extract H1, H2, H3, Architecture, Financials each into `gke/fault-trigger-ui/templates/tab_h1.html`, `tab_h2.html`, etc.
- Modify `app.py`'s home route to assemble them at request time (Jinja2 includes or simple string concatenation)
- Each tab file is now ~500 lines — manageable, readable, and independently verifiable
- Add a `npm run verify` gate that uses Playwright to assert `hasCloak=false` after load — blocks any bad build

### Priority 2 — UI Review
After modularization, do a full tab-by-tab visual review of the live app:
- Confirm H1 Discern briefing + scenario replay render correctly
- Confirm H2 Classify briefing + paraffin/wax scenario render correctly (H2 GDC Advisor Zone 1 had a structural div issue — may not render perfectly)
- Confirm H3 Optimize dashboard is functional
- Note any visual regressions to fix

### Priority 3 — Narrative Issues
After UI review, fix any issues identified in the H1/H2/H3 narratives or scenario content.

### What was fixed this session (for reference):
1. **Blank page fix (DONE):** `app.js` moved to `<head defer>` — immune to template trapping. Verified: `hasCloak=false`, `display=block`, `height=720`, 6 tab panels in DOM.
2. **Image pinning (DONE):** k8s deployment was SHA-pinned; fixed with `kubectl set image ... :latest`.

## Known Integrity Issues
| Issue | Fix Deadline |
|-------|-------------|
| H2 GDC Zone 1 div not closed — `<template v-if="h2VerdictRevealed">` nested inside Zone 1 without close | Next session |
| Unclosed outer `<template v-else>` at 1856 — `</template><!-- /h2-verdict-revealed -->` at 2167 closes the inner template, `</template><!-- /h2-scenario-replay -->` at 2279 should close the outer — verify this works correctly | Next session |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied — it would destroy the live cluster
- All demo changes go into `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`
- After changes: docker build → docker push → kubectl set image (DO NOT use sha-pinned deployment)
- Source env: `source /home/brian/gdc-pm/.env` for correct project/kubeconfig
- GPU: ollama is scale-to-zero; only start via `./scripts/gpu-start.sh` when needed
