# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-24 (Session BS+44) / branch: feature-trio-clean
Git HEAD: 9a0afeb / Image: sha256:8b8b62c7fcc15409c6474a59e4dfbb7a2ac73841538d490fe22be3e43594343c

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
# Expected: all 1/1 Running (7 pods)

kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0

curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
# Expected: ollama_online: False model: offline

kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
# Expected: field_intel = 11, rag_documents = 20
```

## STEP 2: Read These Documents
```bash
cat docs/SESSION_LOG.md | head -80   # last 3 entries for context
```

## STEP 3: B3-S4 Pre-Recording Verification (next task)

Before recording B3-S4 (H3 constraint provenance), verify constraintDoc renders reliably:
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print('constraintDoc.found:', d.get('constraint_doc', {}).get('found'))"
# Expected: constraintDoc.found: True
# If False: check app.py pgvector query at L6530-6545 — seed doc may be missing
```

## STEP 4: Continue Recording

All slides are clear. Recording order per VIDS_PRODUCTION_MASTER.md:
- B1-S1 through B1-S6 (H1 DISCERN) — app record-ready per BS+40 audit ✅
- BBRIDGE (sovereignty bridge) — standalone scene
- B2-S1 through B2-S4 (H2 CLASSIFY) — slides clear per BS+42 ✅
- B3-S1 through B3-S4 (H3 OPTIMIZE) — B3-S4 conditional on constraintDoc.found=True

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io — that's the old project)

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file not replace_in_file
- B1-P5 VO locked: recorded, matches bible verbatim ✅
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
- Reference tab integrity scrub COMPLETE (BS+44) — tab_architecture.html all panes SURVIVES
