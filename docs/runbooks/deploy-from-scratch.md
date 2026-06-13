# GDC-PM Deploy-from-Scratch Runbook
**Version:** Session BP (June 13, 2026) — Autopilot + T4 rebuild  
**Replaces:** Old Standard GKE + L4 runbook (incorrect Step 1 terraform, missing schema/seed, wrong model refs)

This runbook is the **single authoritative procedure** for rebuilding the GDC-PM demo cluster from zero. A new engineer following it from the top should end with a fully operational cluster serving the H1/H2/H3 demo at `gdc-pm.bdau.io` with all data seeded.

> ⚠️ **Do NOT run `terraform apply` on `terraform/gke.tf`** — it is barred by project rules and would destroy a live cluster. The cluster is provisioned via `gcloud` commands below, not Terraform.

---

## Architecture (post-migration)

```
GKE Autopilot Cluster (us-central1)
├── Default node pools — managed by Autopilot (no user configuration)
│   ├── fault-trigger-ui (FastAPI / Vue.js)  — LoadBalancer → gdc-pm.bdau.io
│   ├── inference-api (XGBoost models)
│   ├── event-processor (RabbitMQ consumer)
│   ├── telemetry-simulator
│   ├── grafana
│   ├── alloydb-omni (AlloyDB on-cluster, PostgreSQL + pgvector)
│   └── rabbitmq (RabbitMQ cluster via operator)
└── GPU node — Autopilot-managed, NVIDIA T4 (16GB VRAM)
    └── ollama (gemma4 / gemma3:12b, scale-to-zero when replicas=0)

Artifact Registry: us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/
```

**Key Autopilot GPU benefit:** When Ollama replicas=0, Autopilot provisions zero GPU nodes → zero GPU billing. No manual node-pool resize required.

---

## Prerequisites

- `gcloud`, `kubectl`, `docker` installed and authenticated
- `gcloud auth login && gcloud auth application-default login`
- Project: `gdc-pm-v2`
- Artifact Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models` (must already exist)
- Git repo cloned to `~/gdc-pm`, branch `feature-trio-clean`

---

## Step 0 — Environment variables

Set these once in your shell before starting. All steps below use them.

```bash
export PROJECT_ID="gdc-pm-v2"
export REGION="us-central1"
export CLUSTER="gdc-edge-simulation"
export NAMESPACE="gdc-pm"
export REGISTRY="us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models"
```

---

## Step 0.5 — Delete the old Standard GKE cluster (migration only)

**Skip this step if no prior cluster exists.**

The old cluster (`gdc-edge-simulation`, region `us-east1`) must be deleted before the new Autopilot cluster of the same name is created in `us-central1`. The new cluster reuses the same name and Artifact Registry — only the region and cluster type change.

```bash
# Confirm you are about to delete the right cluster:
gcloud container clusters describe gdc-edge-simulation \
  --region us-east1 --project ${PROJECT_ID} \
  --format="value(location,currentNodeCount)"

# Delete it (irreversible — all cluster workloads and PVCs are gone):
gcloud container clusters delete gdc-edge-simulation \
  --region us-east1 \
  --project ${PROJECT_ID} \
  --quiet
```

> **Expected data loss (all intentional):**
> - AlloyDB PVC data lost — re-seeded automatically by `fault-trigger-ui` startup threads (Step 9)
> - ollama-models PVC lost — gemma4:latest re-pulled on first `gpu-start.sh` (~5-15 min, cached for subsequent starts)
> - `gdc-pm.bdau.io` DNS record will be stale until Step 11 updates it with the new LoadBalancer IP

---

## Step 1 — Create GKE Autopilot Cluster

```bash
gcloud container clusters create-auto ${CLUSTER} \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --release-channel regular \
  --workload-pool "${PROJECT_ID}.svc.id.goog"
```

**Wait ~5–10 minutes.** When complete:

```bash
gcloud container clusters get-credentials ${CLUSTER} \
  --region ${REGION} \
  --project ${PROJECT_ID}

kubectl get nodes  # should show Autopilot-managed nodes appearing
```

---

## Step 2 — Namespace

```bash
kubectl create namespace ${NAMESPACE}
```

---

## Step 3 — IAM: Artifact Registry Reader

The GKE compute SA needs to pull images:

```bash
PROJECT_NUM=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${PROJECT_NUM}-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.reader"
```

---

## Step 4 — AlloyDB Omni (database + schema)

The start script generates a password, saves it to `.secrets/`, creates the k8s secret, deploys AlloyDB, and runs `init-schema.yaml` (creates all tables + pgvector extension).

```bash
cd ~/gdc-pm
export PROJECT_ID=${PROJECT_ID}
export REGION=${REGION}
export CLUSTER_NAME=${CLUSTER}
bash gke/alloydb-omni/start-alloydb-omni.sh
```

**Verify:**
```bash
kubectl exec -n ${NAMESPACE} deployment/alloydb-omni -- \
  psql -U postgres -d grid_reliability -c "\dt"
# Should show: telemetry_events, field_intel, rag_documents, asset_registry
```

> The `init-schema.yaml` Job also installs the pgvector extension and creates the HNSW index on `rag_documents.embedding`. If the Job is still Running, wait for Completed before proceeding.

---

## Step 5 — RabbitMQ

The start script installs the RabbitMQ Cluster Operator, generates credentials, saves them to `.secrets/`, and deploys the cluster:

```bash
cd ~/gdc-pm
export PROJECT_ID=${PROJECT_ID}
export REGION=${REGION}
export CLUSTER_NAME=${CLUSTER}
bash gke/rabbitmq/start-rabbitmq.sh
```

**Verify:**
```bash
kubectl get rabbitmqcluster gdc-pm-rabbitmq -n ${NAMESPACE}
# STATUS.CONDITIONS[AllReplicasReady] should be True
```

---

## Step 6 — Build and push application images

If images are already up to date in Artifact Registry (check digests), skip this step. Otherwise, for each service that needs a new image:

```bash
cd ~/gdc-pm

# fault-trigger-ui (the main app — most frequently rebuilt)
docker build -t ${REGISTRY}/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push ${REGISTRY}/fault-trigger-ui:latest
DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' ${REGISTRY}/fault-trigger-ui:latest | cut -d@ -f2)
echo "fault-trigger-ui digest: ${DIGEST}"

# inference-api (rarely changes)
docker build -t ${REGISTRY}/inference-api:latest gke/inference-api/
docker push ${REGISTRY}/inference-api:latest

# event-processor (rarely changes)
docker build -t ${REGISTRY}/event-processor:latest gke/event-processor/
docker push ${REGISTRY}/event-processor:latest

# telemetry-simulator (rarely changes)
docker build -t ${REGISTRY}/telemetry-simulator:latest gke/telemetry-simulator/
docker push ${REGISTRY}/telemetry-simulator:latest
```

> **Deploy rule (from clinerules):** Always deploy by digest, not `:latest` tag:
> `kubectl set image deployment/fault-trigger-ui fault-trigger-ui=${REGISTRY}/fault-trigger-ui@${DIGEST} -n ${NAMESPACE}`

---

## Step 7 — Fix the OLLAMA_MODEL integrity mismatch (before first deploy)

> ✅ **Already fixed in commit `4e7e09c`** — if you cloned `feature-trio-clean` after Session BP, `fault-trigger-ui.yaml` already has `OLLAMA_MODEL: "gemma4:latest"`. The `sed` command below is a no-op on a current checkout; it is retained here as a safeguard only.

```bash
# No-op on current feature-trio-clean — value already correct:
grep 'OLLAMA_MODEL' gke/fault-trigger-ui/k8s/fault-trigger-ui.yaml
# Should show: value: "gemma4:latest"
```

Update `GRAFANA_URL` to match the current Grafana IP once it's assigned (Step 8 will give you the IP):
```bash
# After Step 8, get the Grafana LoadBalancer IP and patch:
# GRAFANA_IP=$(kubectl get svc grafana -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
# sed -i "s|value: \"http://.*\"|value: \"http://${GRAFANA_IP}\"|" gke/fault-trigger-ui/k8s/fault-trigger-ui.yaml
```

---

## Step 8 — Deploy application tier

Order matters: inference-api first (event-processor depends on it), then event-processor, then the rest.

```bash
cd ~/gdc-pm

kubectl apply -f gke/inference-api/k8s/
kubectl rollout status deployment/inference-api -n ${NAMESPACE} --timeout=120s

kubectl apply -f gke/event-processor/k8s/
kubectl apply -f gke/telemetry-simulator/k8s/
kubectl apply -f gke/fault-trigger-ui/k8s/
kubectl apply -f gke/grafana/k8s/
```

**Verify all pods:**
```bash
kubectl get pods -n ${NAMESPACE}
# Expected: inference-api, event-processor, telemetry-simulator, fault-trigger-ui, grafana, alloydb-omni, rabbitmq pod(s) — all Running
```

> **Troubleshooting: event-processor CrashLoopBackOff** — RabbitMQ wasn't fully ready when the pod started. Fix:
> `kubectl delete pod -l app=event-processor -n ${NAMESPACE}`

---

## Step 9 — Data seeding (automatic)

**No external seed script is needed for the O&G demo.** The `fault-trigger-ui` pod seeds everything automatically via background threads when it starts:

| Thread | What it seeds | Table | Wait (from startup) |
|---|---|---|---|
| `h2-seed` | H2 paraffin docs (vendor log, PVT, pull record) | `rag_documents` | ~10s |
| `h1-bayes-seed` | H1 Bayesian findings with LR metadata | `field_intel` | ~20s |
| `pad-alpha-rag-seed` | H3 Pad Alpha docs | `rag_documents` | ~30s |
| `l3-scenario-rag-seed` | 10 scenario RAG docs (H1 + H2, with noise mix) | `rag_documents` | ~55s |
| `intel-generator` | Live field intel documents | `field_intel` | continuous |

> **The `scripts/seed-*.py` files are legacy power-grid seeders (transformer/turbine/compressor).** Do NOT run them for the O&G demo.

**Verify seeding (wait ~2 min after fault-trigger-ui is Running):**
```bash
kubectl exec -n ${NAMESPACE} deployment/alloydb-omni -- \
  psql -U postgres -d grid_reliability \
  -c "SELECT COUNT(*) FROM rag_documents; SELECT COUNT(*) FROM field_intel;"
# rag_documents: ~18+ rows (grows as seeders run)
# field_intel: ~8+ rows (grows as intel-generator runs)
```

---

## Step 10 — Ingest OEM manuals into RAG corpus (optional but recommended)

This adds the ESP, gas lift, mud pump, and top drive manuals to `rag_documents` for deeper H1/H2 retrieval. Takes ~5 min.

```bash
cd ~/gdc-pm
# Get AlloyDB password from secrets
ALLOYDB_PASS=$(cat .secrets/alloydb-password.txt)

# Port-forward AlloyDB for local script access
kubectl port-forward -n ${NAMESPACE} deployment/alloydb-omni 5432:5432 &
PF_PID=$!
sleep 3

ALLOYDB_HOST=localhost ALLOYDB_PORT=5432 \
  ALLOYDB_DB=grid_reliability ALLOYDB_USER=postgres \
  ALLOYDB_PASS=${ALLOYDB_PASS} \
  python3 scripts/ingest_manuals.py

kill ${PF_PID}
```

---

## Step 11 — DNS: wire gdc-pm.bdau.io

The `fault-trigger-ui` Service is a LoadBalancer. Get its external IP:

```bash
kubectl get svc fault-trigger-ui -n ${NAMESPACE}
# Copy the EXTERNAL-IP value
```

Update the `gdc-pm.bdau.io` A-record in your DNS provider to point to this IP. Propagation takes 1–5 minutes.

**Verify:**
```bash
curl -s http://gdc-pm.bdau.io/api/assets | python3 -m json.tool | head -10
```

---

## Step 12 — Ollama / GPU (on-demand only, not always-on)

Ollama runs on a T4 GPU via Autopilot. It is **off by default (replicas=0, zero billing).** Only bring it up for showcase/record sessions.

**Before starting:** GPU costs ~$0.35/hr on T4 Autopilot. Always run stop when done.

```bash
# Start (announce cost first — about $0.35/hr):
./scripts/gpu-start.sh

# Stop (always pair — stops billing):
./scripts/gpu-stop.sh
```

> On Autopilot, `gpu-start.sh` simply scales the Deployment to 1. Autopilot provisions the T4 node automatically. `gpu-stop.sh` scales back to 0 — the T4 node disappears and billing stops. No manual node-pool resize needed.

**First-time GPU start:** Autopilot provisions a T4 node (~2–3 min), then Ollama's init container pulls `gemma4:latest` (~6GB, ~5–15 min). The model is cached on the PVC for subsequent starts.

**Verify Ollama ready:**
```bash
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print('online:',d['ollama_online'],'model:',d['ollama_model'])"
# Expected: online: True  model: gemma4:latest
```

---

## Step 13 — Verification checklist

```bash
# 1. All pods running
kubectl get pods -n ${NAMESPACE} --no-headers | awk '{print $3}' | sort | uniq -c
# Expected: all Running (or Completed for init jobs)

# 2. API health
curl -s http://gdc-pm.bdau.io/api/assets | jq 'keys'
# Expected: ["ESP-ALPHA-1", "ESP-ALPHA-2", ..., "ESP-ALPHA-6"]

# 3. H1 scenario replay
curl -s "http://gdc-pm.bdau.io/api/h1/scenario-replay?fault=gas_lock" | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print('bayes_pct:',d['bayes_pct'],'gdc_detect_idx:',d['gdc_detect_idx'])"
# Expected: bayes_pct ~93.1, gdc_detect_idx < scada_alarm_idx

# 4. H2 scenario replay
curl -s "http://gdc-pm.bdau.io/api/h2/scenario-replay?asset=ESP-ALPHA-3" | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print('scenario:',d.get('scenario'),'docs:',len(d.get('doc_reveals',[])))"
# Expected: scenario: paraffin_wax_restriction, docs: 3

# 5. H3 Vizier
curl -s -X POST "http://gdc-pm.bdau.io/api/vizier/optimize" | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print('uplift_bpd:',d.get('uplift_bpd'))"
# Expected: uplift_bpd ~77.9

# 6. mlops/status
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c \
  "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d['ollama_online'])"
# Expected: ollama_online: False (correct default — GPU is off)
```

---

## Troubleshooting

**event-processor CrashLoopBackOff:** RabbitMQ not yet ready.
```bash
kubectl delete pod -l app=event-processor -n ${NAMESPACE}
```

**inference-api 503:** Model not yet loaded, or pod crashed.
```bash
kubectl rollout restart deployment/inference-api -n ${NAMESPACE}
```

**Ollama Pending (GPU not scheduling):** Autopilot may be provisioning the T4 node. Check events:
```bash
kubectl describe pod -l app=ollama -n ${NAMESPACE} | grep -A5 Events
# If "no nodes available with nvidia.com/gpu", wait 3–5 min for Autopilot to provision
```

**Data not seeded after 3 min:** Check fault-trigger-ui logs for seed thread output:
```bash
kubectl logs -n ${NAMESPACE} deployment/fault-trigger-ui | grep -i "seed\|Sprint"
```

---

## Companion code changes needed in the same session as the rebuild

The following YAML/script changes were identified during Session BO/BP audit. Apply them *before* deploying to the new cluster:

| File | Change | Why |
|---|---|---|
| `gke/ollama/k8s/ollama.yaml` | ✅ DONE `4e7e09c` | nodeSelector T4, limits 16Gi, no tolerations, header updated |
| `gke/fault-trigger-ui/k8s/fault-trigger-ui.yaml` | ✅ DONE `4e7e09c` | `OLLAMA_MODEL: "gemma4:latest"` |
| `scripts/gpu-start.sh` | ✅ DONE `4e7e09c` | kubectl scale only, no gcloud resize |
| `scripts/gpu-stop.sh` | ✅ DONE `4e7e09c` | kubectl scale only, no gcloud resize |
| `gke/ollama/k8s/ollama-scheduler.yaml` | ✅ DONE (Session BP) | T4 cost/Autopilot language throughout |
