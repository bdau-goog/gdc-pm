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

## STEP 3: Next Implementation Task
The app is restored and verified working (2026-06-15).

### Critical issues resolved this session:
1. **Blank page fix (DONE):** `app.js` was trapped in an inert `<template>` element because `<template v-if="h2VerdictRevealed">` at line ~2143 in the H2 scenario replay section was never properly closed, causing Chrome to treat all following content (including `</div><!-- #app -->` and `<script src="/static/app.js">`) as template content. **Fix:** moved `<script src="/static/app.js" defer></script>` to `<head>`. Defer scripts are immune to template trapping. Deployed and verified: `hasCloak=false`, `display=block`, `height=720` — Vue mounts.
2. **Image pinning (DONE):** The running k8s deployment was pinned to a specific SHA digest. Fixed with `kubectl set image deployment/fault-trigger-ui ... :latest`.

### Next tasks (from DEMO_MASTER.md §12):
- The H2 GDC Advisor view has structural HTML issues (unclosed `<template>` blocks in Zone 1 section). The app works but the H2 advisor view likely doesn't render correctly. Address in next session.
- Review if a file split (index.html → separate tab files) should be prioritized to prevent recurrence.

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
