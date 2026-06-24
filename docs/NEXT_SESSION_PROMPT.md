# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-24 (Session BS+43) / branch: feature-trio-clean
Git HEAD: 49bf672 / Image: sha256:d127b3f9ccc5f1dfc19fda00946bde3fc32419f8891e536ab589c06edaaad6ac

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

## STEP 3: Next Tasks (priority order)

### 3A — RECORDING: Resume B1-S1 (all slide fixes and Reference tab are done)
Slides clear, Reference tab new Pane 3 deployed. Recording order:
1. B1-S1 → S2 → S3 → S4 (A/B) → S5 → S6 (optional)
2. B2-P1 → P2 → P3 → S1 → S2 → S3 → S4  (skip B2-S5 — CUT)
3. BBRIDGE (VO: "all AI local, no cloud required")
4. B3-P1 → P2 → P3 → S1 → S2 → S3 → S4 (CONDITIONAL — verify constraintDoc.found=True first) → S5
5. BCLOSE

Pre-B3-S4 check:
```bash
curl -s "http://gdc-pm.bdau.io/api/vizier/optimize" | python3 -c "import sys,json; d=json.load(sys.stdin); print('constraintDoc.found:', d.get('constraint_doc', {}).get('found'))"
```

### 3B — Reference Tab integrity scrub (new session, separate from recording)
The Reference tab has 7 panes. Several have hardcoded display values (e.g., Pane 6 ROI
numbers, Pane 5 RUL estimates) that were written before integrity discipline was tightened.
A scoped scrub pass is needed — read each pane, build a brief claim ledger, fix OPEN items.
See SESSION_LOG BS+43 for context on what was changed this session.

### 3C — SESSION_LOG append (needed before wrap)
Append BS+43 entry to docs/SESSION_LOG.md.

## Deploy Command (permanent reference)
```bash
cd gke/fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest .
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```
**Registry:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/` (NOT gcr.io — that's the old project)

## Deployed This Session (BS+43)
- **Reference tab Pane 2** renamed "Telemetry Ingestion" (was "Data Ingestion")
- **Reference tab Pane 3** added: "Unstructured Data Ingestion" — honest two-layer content
  (IN THIS DEMO: seed corpus + pgvector; IN PRODUCTION: connector pipeline pattern)
- **B1-P5 slides/h1.html** sparklines added: 7 inline SVG polylines across 3 industry cards
  (O&G: 2 declining blue; P&U: 2 rising purple; Maritime: 2 rising + 1 flat-dashed orange)

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test (~$0.65/hr)
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file not replace_in_file
- B1-P5 VO locked: recorded, matches bible verbatim ✅
- B2-S5: ❌ CUT — do not record
- BBRIDGE VO: "all AI local, no cloud required" (not "air-gap capable")
