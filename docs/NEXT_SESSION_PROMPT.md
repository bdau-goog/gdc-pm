# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-23 (Session BS+42) / branch: feature-trio-clean
Git HEAD: 40bf93e / Image: sha256:06a56c0d393c28f6

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
cat docs/VIDS_PRODUCTION_MASTER.md   # PRIMARY REFERENCE — shot bible
# Last 3 SESSION_LOG entries for context
```

## STEP 3: Next Implementation Task — READY TO RECORD B2 + B3

### Slide fixes are DONE and deployed — clear to record:
- ✅ H2 Slide 2 kicker: "THE SIGNAL SAYS PULL" (was: AMBIGUOUS TELEMETRY)
- ✅ H2 Slide 2 sub: "Every best-in-class platform reads this as bearing wear..." (dropped "indistinguishable")
- ✅ H3 Slide 2: Bayesian optimizer sentence added
- ✅ H3 Slide 3: Vizier explanation paragraph added
- ✅ Deployed: sha256:06a56c0d, pod fault-trigger-ui-6b7f9b68b6-bwrbn Running

### Recording order (pick up here):
1. FINISH H1: B1-P5 → B1-S1 → S2 → S3 → S4 (A/B) → S5 → S6 (OPTIONAL)
2. Record B2: B2-P1 → P2 → P3 → S1 → S2 → S3 → S4  (skip B2-S5 — CUT)
3. BBRIDGE (VO: "all AI local, no cloud required")
4. Record B3: B3-P1 → P2 → P3 → S1 → S2 → S3 → S4 (CONDITIONAL) → S5
5. BCLOSE

## Deploy Command (for reference — registry was missing from previous doc, caused startup confusion)
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
- B1-P5 VO locked at 52w/~21s
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
