# GDC-PM Phase 2 — Deployment Status & Handoff
**Status:** Code Complete — Not Yet Deployed  
**Date:** 2026-05-07  
**Next Task Brief:** Execute `bash scripts/deploy-phase2.sh` from `/home/brian/gdc-pm`, verify all steps succeed, then test the 3-tab UI and RUL projections against the live cluster.

---

## What Was Built (Code Changes Summary)

All changes are committed to working tree but **not yet pushed to Artifact Registry or applied to the cluster**.

### 1. 3-Tab UI Architecture (`gke/fault-trigger-ui/index.html`)
- **Tab 1 (Operations):** Existing fleet bar, event log, and Plotly RUL forecast — unchanged behavior
- **Tab 2 (Fleet Financials):** New full-page ledger table of resolved incidents showing Timestamp, Asset, Fault Type, Resolution Taken, Cost Incurred (from operator's selected option), Savings Realized. Summary cards: Aggregate Capital Saved, Total Incidents, Uptime Protected.
- **Tab 3 (Historical Telemetry):** Grafana iframe. URL auto-derived from `window.location.hostname:3000`. Override via `<meta name="grafana-url">`.
- **Dispatch Modal upgrade:** Now parses Gemma-generated JSON from `ai_narrative` and renders radio-button resolution options (Action, Cost, Time). Selected option's cost flows through to the ledger.
- **Default ramp duration:** Changed from 600s → **3600s** (matches training data trajectory length).

### 2. RUL Stability Fix (`gke/fault-trigger-ui/app.py`)
- **Root cause fixed:** Training used 5-min steps; old inference used 8-reading (40-sec) window → 6–30× slope magnitude mismatch causing constant near-zero RUL predictions.
- **Fix:** Lookback window changed from `min(8, n-1)` to `min(60, n-1)` readings (~5 min at 5-sec intervals). Rate-of-change now divided by `TRAINING_STEP_MIN = 5.0` (matching training denominator).
- **Held-phase detection:** `is_degrading` now catches `held: True` state, keeping RUL active after ramp completes.
- **Smoothing:** Changed current-value from mean→median of last 5 readings; past-value from mean→median of 5 readings centered around `window_size` ago.

### 3. Financial Ledger Fixes (`gke/fault-trigger-ui/app.py` + `index.html`)
- `clear-dispatch` now resets both `cost_avoided=0` AND `cost_incurred=0` (was missing the latter; caused savings ticker to go negative after reset).
- `renderLedger()` now reads `ev.cost_incurred` from the API response (was ignoring it and using a hardcoded 10% heuristic).
- `GET /api/savings` computes `SUM(cost_avoided - cost_incurred)` (was only summing `cost_avoided`).

### 4. RAG Pipeline (`gke/event-processor/processor.py`)
- `SentenceTransformer` is now a module-level lazy singleton (was reloading 90MB model on every fault event).
- pgvector query now filters by `asset_class = %s` first, with a fallback to global search if no class-specific docs exist.
- `AI_NARRATIVE_ENABLED` default changed from `rule_based` → `rag`.
- Prompt structured to output JSON `{assessment, options: [{action, cost, time}]}` for the multi-option modal.

### 5. RAG Knowledge Base (new files)
- `docs/rag_source/esp_manual.md` — ESP: gas_lock, sand_ingress, motor_overheat
- `docs/rag_source/gas_lift_manual.md` — Gas Lift: valve_failure, thermal_runaway, bearing_wear
- `docs/rag_source/mud_pump_manual.md` — Mud Pump: pulsation_dampener_failure, valve_washout, piston_seal_wear
- `docs/rag_source/top_drive_manual.md` — Top Drive: gearbox_bearing_spalling, hydraulic_leak

### 6. Ingestion Script (`scripts/ingest_manuals.py`)
- Asset class derived by stripping `_manual.md` suffix (fixes `gas_lift_manual.md` → `"gas_lift"` not `"gas"`)
- Uses explicit `[x,y,z]` embedding string format for pgvector
- Creates HNSW index on first run

### 7. Ollama LLM Deployment (new file: `gke/ollama/k8s/ollama.yaml`)
- `PersistentVolumeClaim` (10Gi, no storageClassName = cluster default)
- Init container: `ollama pull gemma:2b` with skip-if-present check
- Main container: `ollama/ollama:0.3.12` (pinned), readiness + liveness probes
- GPU scheduling via `nvidia.com/gpu: 1` resource request only (no GKE-specific nodeSelector)
- Image: `ollama/ollama:0.3.12`

### 8. AlloyDB Schema (`gke/alloydb-omni/k8s/init-schema.yaml`)
- `cost_incurred NUMERIC DEFAULT 0` column added to `telemetry_events`
- `pgvector` extension + `rag_documents` table + HNSW index
- `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` migration is safe to re-run

### 9. Inference API — GDC Software-Only Mode (`gke/inference-api/app.py` + `k8s/inference-api.yaml`)
- `LOCAL_MODELS_DIR` env var: when set, loads `.ubj`/`.bst`/`.json` files from that path instead of GCS
- GKE Workload Identity annotation commented out (portable to GDC Software-Only)
- Startup logs which mode it's in (`air-gapped / GDC Software-Only` or `cloud / GKE`)

### 10. Portability Fixes (GDC Software-Only)
- `ollama.yaml`: removed `cloud.google.com/gke-accelerator: nvidia-l4` nodeSelector
- `rabbitmq-cluster.yaml`: removed `storageClassName: standard`
- `terraform/gke.tf`: marked as GKE simulation only; added GDC Software-Only deployment guide in header

---

## Current Live Cluster State

```
Cluster:     gdc-edge-simulation (GKE Autopilot, us-central1)
Project:     gdc-pm-v2
Registry:    us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/
Namespace:   gdc-pm

RUNNING PODS (stale — pre-Phase 2 images):
  alloydb-omni          Running  6d8h  google/alloydbomni:latest
  event-processor       Running  5d7h  .../event-processor:latest
  fault-trigger-ui      Running  2h    .../fault-trigger-ui:latest
  gdc-pm-rabbitmq       Running  14h   rabbitmq:3.12-management
  grafana               Running  5d    grafana/grafana:10.4.2
  inference-api         Running  29h   .../inference-api:latest
  telemetry-simulator   Running  2h    .../telemetry-simulator:latest

MISSING FROM CLUSTER:
  - Ollama pod (not yet deployed)
  - rag_documents table (not yet migrated)
  - cost_incurred column (not yet migrated)
  - pgvector extension (not yet installed)
```

---

## Deployment Commands

### Prerequisites
```bash
cd /home/brian/gdc-pm
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
gcloud container clusters get-credentials gdc-edge-simulation \
  --region us-central1 --project gdc-pm-v2
```

### Full Automated Deployment (Preferred)
```bash
bash scripts/deploy-phase2.sh
```
Uses `docker build --quiet`, `docker push --quiet`, output to `/tmp/deploy-phase2-logs/`. Tails only on failure. Prints summary table.

### Manual Steps (if needed individually)

**1. AlloyDB migration (30 sec, no downtime):**
```bash
ALLOYDB_POD=$(kubectl get pod -n gdc-pm -l app=alloydb-omni --no-headers -o custom-columns=':metadata.name')
kubectl exec -n gdc-pm "$ALLOYDB_POD" -- psql -U postgres -d grid_reliability -q -c "
  CREATE EXTENSION IF NOT EXISTS vector;
  CREATE TABLE IF NOT EXISTS rag_documents (id SERIAL PRIMARY KEY, asset_class TEXT NOT NULL, doc_title TEXT NOT NULL, content TEXT NOT NULL, embedding vector(384));
  CREATE INDEX IF NOT EXISTS idx_rag_embedding ON rag_documents USING hnsw (embedding vector_cosine_ops);
  ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS cost_incurred NUMERIC DEFAULT 0;
  SELECT 'done' AS status;
" 2>&1 | tail -3
```

**2. Rebuild container images (8–12 min each):**
```bash
# All use --quiet to suppress layer output
PROJECT="gdc-pm-v2"; REGION="us-central1"
REG="${REGION}-docker.pkg.dev/${PROJECT}/gdc-models"

docker build --quiet -t "${REG}/fault-trigger-ui:latest" gke/fault-trigger-ui/ \
  && docker push --quiet "${REG}/fault-trigger-ui:latest" && echo "✅ UI done"

docker build --quiet -t "${REG}/event-processor:latest" gke/event-processor/ \
  && docker push --quiet "${REG}/event-processor:latest" && echo "✅ Processor done"

docker build --quiet -t "${REG}/inference-api:latest" gke/inference-api/ \
  && docker push --quiet "${REG}/inference-api:latest" && echo "✅ Inference done"
```

**3. Apply manifests and restart pods:**
```bash
REG="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
for svc in fault-trigger-ui event-processor; do
  kubectl rollout restart deployment/$svc -n gdc-pm --output=name
done
sed "s|GCR_IMAGE_PLACEHOLDER|${REG}/inference-api:latest|g" \
  gke/inference-api/k8s/inference-api.yaml | kubectl apply -f - --output=name
kubectl rollout restart deployment/inference-api -n gdc-pm --output=name
for svc in fault-trigger-ui event-processor inference-api; do
  kubectl rollout status deployment/$svc -n gdc-pm --timeout=120s
done
```

**4. Deploy Ollama (GPU auto-provisioned by Autopilot, ~5-10 min):**
```bash
kubectl apply -f gke/ollama/k8s/ollama.yaml --output=name
# Wait for model pull (~5 min first time):
kubectl wait pod -n gdc-pm -l app=ollama --for=condition=ready --timeout=600s
```

**5. RAG document ingestion (requires AlloyDB migration first):**
```bash
# Port-forward AlloyDB, then run locally:
kubectl port-forward -n gdc-pm svc/alloydb-omni 5432:5432 &

# Get the DB password:
kubectl get secret -n gdc-pm alloydb-secret -o jsonpath='{.data.password}' | base64 -d

PGHOST=localhost PGUSER=postgres PGPASSWORD=<password> PGDATABASE=grid_reliability \
  python scripts/ingest_manuals.py
```

---

## Verification Checklist

After deployment, verify each Phase 2 feature:

### ✅ 3-Tab UI
1. Open the fault-trigger-ui external IP
2. Confirm 3 tabs visible: Operations | Fleet Financials | Historical Telemetry
3. Click "Fleet Financials" → should show empty ledger with `$0` savings
4. Click "Historical Telemetry" → should show Grafana iframe (may need port-forward at `:3000`)

### ✅ Financial Ledger + Dispatch Modal
1. Inject a fault on any ESP asset (gas_lock, gradual, 3600s)
2. Wait ~2 min for fault label to appear in incidents panel
3. Click "Diagnose ▶" → modal should open
4. If Ollama is ready: AI Assessment section + 2 resolution option radio buttons should appear
5. If Ollama not ready: plain narrative text appears (graceful fallback)
6. Select an option, click "Acknowledge & Dispatch"
7. Click "Fleet Financials" tab → should show 1 row in ledger with actual cost_incurred from selected option

### ✅ RUL Stability
1. Inject gradual ramp on `ESP-ALPHA-1` (sand_ingress, 3600s)
2. Select the asset in Operations tab
3. Watch the Plotly forecast — RUL should start high (~300-400m) and decline smoothly
4. Should NOT flip wildly between 0m and 600m
5. After ramp completes (held phase), RUL should stabilize at ~0-30m and remain there

### ✅ Savings Ticker
1. After acknowledging a dispatch, savings ticker should show positive number
2. Click "Clear All Work Orders" → ticker should reset to $0 (not go negative)

### ✅ RAG / LLM (requires Ollama + ingested docs)
1. Check Ollama is ready: `kubectl logs -n gdc-pm -l app=ollama --tail=5`
2. Check RAG docs ingested: `SELECT COUNT(*), asset_class FROM rag_documents GROUP BY 2;`
3. Inject fault, wait for event-processor to generate narrative
4. Open dispatch modal → AI assessment should be a coherent 2-sentence description with 2 specific resolution options

### ✅ Savings Math (clear-dispatch fix)
1. Acknowledge several dispatches with different resolution options
2. Note the total savings
3. Click "Clear All Work Orders"
4. Savings should immediately reset to $0 (not show a negative number)

---

## Known Limitations / Watch Points

1. **Ollama first-start latency:** The gemma:2b model (~1.5GB) downloads on first pod start. Event-processor will fall back to `rule_based` narratives until Ollama is ready (logged as `RAG narrative generation failed: Connection refused`). No action needed — it self-recovers.

2. **RUL still slightly pessimistic on 10-min ramps:** The 5-min lookback window needs 5 minutes of data to calculate a valid slope. For ramps shorter than 10 minutes, the RUL will still predict low (but stable) values early in the ramp. Use ≥3600s duration for best results.

3. **`fin-uptime` metric:** Hardcoded to `100.0%` — not yet wired to real data. Cosmetic placeholder.

4. **GKE Autopilot GPU provisioning:** Applying `ollama.yaml` triggers Autopilot to provision a new GPU node. This takes 3–7 minutes and is visible via `kubectl get nodes`. The `nvidia.com/gpu` nodeSelector-less approach works on Autopilot but will provisioned the cheapest available L4/T4 in the region.

5. **Terraform:** Do NOT run `terraform apply` — the current `gke.tf` defines a Standard cluster with explicit GPU node pools that would destroy the running Autopilot cluster if applied.

---

## Files Changed (git status)
```
M gke/alloydb-omni/k8s/init-schema.yaml   # pgvector + cost_incurred migration
M gke/event-processor/processor.py         # Singleton embedder, asset_class filter
M gke/event-processor/requirements.txt     # +sentence-transformers
M gke/fault-trigger-ui/app.py              # RUL fix, clear-dispatch fix, cost math
M gke/fault-trigger-ui/index.html          # 3-tab UI, ledger, dispatch modal, 3600s
M gke/inference-api/app.py                 # LOCAL_MODELS_DIR fallback
M gke/inference-api/k8s/inference-api.yaml # LOCAL_MODELS_DIR env, WorkloadIdent comment
M gke/rabbitmq/k8s/rabbitmq-cluster.yaml  # StorageClass portability
M terraform/gke.tf                          # GKE-only header annotation + GPU pool

?? docs/PHASE_2_COMMAND_CENTER.md           # Phase 2 spec (pre-existing)
?? docs/PHASE_2_DEPLOYMENT_STATUS.md        # This file
?? docs/rag_source/                         # 4 OEM manual markdown files
?? gke/ollama/                              # New: Ollama Deployment + PVC + Service
?? scripts/deploy-phase2.sh                 # New: Phase 2 deployment automation
?? scripts/ingest_manuals.py                # New: RAG ingestion script
?? .clinerules                              # New: Token conservation + project rules
```
