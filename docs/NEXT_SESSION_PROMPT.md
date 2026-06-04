# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026  
**Git Head:** `862d674` — clean working tree  
**fault-trigger-ui Digest:** `sha256:7da84c2480ccd3c821c00f99fe720e6fe6243910da22ac08fefcd39bea07fd49`  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
cd ~/gdc-pm && git log --oneline -3
```

**Expected when healthy:** All pods 1/1 Running · ollama_online: True · gemma4:latest · rag_documents: 18 · field_intel: ~100

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

This is the authoritative spec for what we're building. Do not write any code until you have read it. It contains the complete H1/H2/H3 design, UI patterns, physics, agentic elements, and implementation order.

Also read the last entry in SESSION_LOG.md for recent decision context:
```bash
tail -50 ~/gdc-pm/docs/SESSION_LOG.md
```

---

## STEP 3: Next Implementation Task — H1 Full Redesign

Implement the H1 tab from `DEMO_MASTER.md` §4 spec. All of the following in **one session**:

### app.py changes (single replace_in_file call):
- Add `slopes` dict to `/api/plot/forecast-data/{asset_id}` JSON response (`dpsi_dt`, `dtemp_dt`, `dvib_dt`, `ds4_dt`)
- Update `_intel_generator` document type weights: ~55% supporting, ~30% neutral, ~15% counterargument (see DEMO_MASTER.md §10)
- Add `_post_approval_monitor(asset_id)` function: polls recovery, streams "Recovery on track" or escalates
- Wire `hitl_approve()` for gas_lock to launch `_post_approval_monitor` in addition to `_run_recovery_thread`

### index.html changes (single replace_in_file call):
- H1 tab full layout redesign (see DEMO_MASTER.md §4 wireframe)
- 2D SVG animated well schematic (blue/yellow particles, motor temp color gradient)
- Evidence Convergence Wall (5 category rows, activate in sequence on inject)
- SCADA access comparison (always visible, not animated)
- Cited LLM Copilot (auto-starts streaming on inject, superscript citations [¹][²], chat input)
- Window of Options timeline replacing RUL (3 option cards with live viability tickers)
- Live document feed (shows `_intel_generator` output with "⚡ GDC AI — just now" badge)
- Remove Fleet Operations tab link from header
- Remove static financial cards entirely

### Verification:
1. Open H1 tab → charts tick live (nominal DB data), copilot says "Monitoring..."
2. Inject gas lock → evidence wall activates in sequence, LLM streams with citations
3. Window of Options shows 3 viable options, viability ticking down
4. Approve VFD → recovery animation, copilot confirms "Recovery on track"

### Deploy:
```bash
REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui
docker push ${REGISTRY}/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — no `browser_action` tool
- `feature-trio-scenarios` stays separate from `main`
- XGBoost `*.ubj` models — do not retrain
- Fleet Operations tab: do NOT re-add (removed by user request)
- Financial case: LLM only, no static financial cards
