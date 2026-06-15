# Next Session Prompt — GDC Edge AI Demo (Operational State)
Session BS+2 — June 15, 2026 / git head: `5702859` / image: `sha256:5f0d34d48695eca397a72decb324186d6ae5e3bba36f2cf78abc8936c538e553` / branch: `feature-trio-clean`

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'))" 2>/dev/null || echo "API offline"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

## STEP 3: Next Implementation Tasks

### Blank Page — RESOLVED ✅
**Root cause (final):** Session BS+1 added two spurious `</div>` tags as "div balance fixes". But the self-hosting commit (3a74460) only changed script src attributes — it added ZERO new unclosed divs. The spurious closers broke Vue's template compilation even though the div count balanced.

**Two fixes applied (both needed):**
1. `c416068` — CDN URLs restored (Plotly + Vue)
2. `5702859` — 2 spurious `</div>` tags removed from H2 GDC Advisor section

**Deployed:** `sha256:5f0d34d...` — CDN URLs live, 0 spurious divs confirmed.

### Remaining Work (from DEMO_MASTER.md §12)
- H2 paraffin/wax scenario: hostile red-team pass ("gdc-second-opinion") before any pixel changes
- H3 Optimize tab: verify Vizier optimization runs end-to-end
- Architecture tab: verify all 6 panes render correctly

### Known Integrity Issues
| Item | Issue | Status |
|------|-------|--------|
| blank page | RESOLVED — CDN URLs restored | ✅ Fixed session BS+2 |

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied (would destroy live cluster)
- No `browser_action` (SSH remote, no browser)
- Batch all edits to same file in ONE `replace_in_file` call
- `feature-trio-clean` branch — do NOT merge to main
- No GPU start without announcing cost (~$0.35/hr T4) and getting confirmation
- Deploy sequence: `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status`
- Artifact Registry only — NOT gcr.io
- All Ollama API calls MUST include `"think": False` — do not omit this
