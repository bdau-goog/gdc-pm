# Next Session Prompt — GDC Edge AI Demo (Operational State)

**Date:** June 4, 2026  
**Git Head:** `9951199` — clean working tree  
**fault-trigger-ui Digest:** `sha256:c8dfa4c39282aef43011df1bef010e406653c7bb5700f77c88aa11bc2646a98b`  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected when healthy:** All pods 1/1 Running · ollama_online: True · gemma4:latest · rag_documents: 18 · field_intel: ~100

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

Also read the last entry in SESSION_LOG.md for recent decision context.

---

## STEP 3: Next Implementation Task — H1 Verification + H2 Redesign

### H1 is DEPLOYED — verify the demo flow first:
1. Open `http://gdc-pm.bdau.io` → Horizon 1: Gas Lock tab
2. Charts tick live (nominal DB data from `telemetry_events`)
3. Click "Inject Gas Lock Fault" → evidence wall activates in sequence (5 rows, ~7s total)
4. LLM copilot auto-streams after 3s with superscript citations [¹][³][⁵]
5. Window of Options shows 3 cards; click "✔ Execute Now" on VFD option
6. Recovery message appears from `_post_approval_monitor` after ~30s
7. Chat input: ask a follow-up question → Gemma responds via `/api/agent/chat`

### If H1 is verified clean → implement H2 redesign:

H2 redesign from `DEMO_MASTER.md` §5:
- **Primary visual:** two-line superimposed chart: Vibration (rising, orange) + Motor Temperature (flat, blue)
- **Well SVG:** pump body GREEN (healthy) while surface flowline shows slug animation (orange slugs)
- **Evidence Wall:** 6 source categories (vibration alarming, temp exonerating, shift note, separator test, choke log, OEM guide)
- **LLM copilot:** auto-streams on inject: "$1,500 vs $150,000" decision outcome
- **No RUL / no Window of Options** for H2 (slug flow = surface dispatch, not time-critical PNR)
- Reuse all H1 CSS classes (`.evidence-wall`, `.h1-copilot`, `.scada-compare`, etc.)

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
