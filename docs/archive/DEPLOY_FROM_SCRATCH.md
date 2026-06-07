# GDC-PM: Zero-to-Edge Deployment Runbook

This runbook walks you through deploying the entire GDC-PM Predictive Maintenance
architecture — from a blank GCP account to a running edge simulation — step by step.

The deployment is split into two Terraform layers, a multi-model ML pipeline,
and the GKE service deployments:

```
Layer 1: bdau-basic-vpc/scenarios/gdc-pm/   (Foundation)
         ↳ Creates: GCP project, VPC, Cloud NAT, APIs, Org Policies, IAM, Artifact Registry

Layer 2: gdc-pm/terraform/                  (Workloads)
         ↳ Creates: GKE Autopilot cluster, BigQuery dataset + 3 training tables, GCS model bucket

ML Factory: gdc-pm/scripts/               (Model Pipeline — one per asset class)
         ↳ Compressor:   seed → train → export  (stator_classifier)
         ↳ Turbine:      seed → train → export  (turbine_classifier)
         ↳ Transformer:  seed → train → export  (transformer_classifier)

GKE Services: gdc-pm/gke/*/start-*.sh     (Edge Services)
         ↳ Deploys: AlloyDB, RabbitMQ, Inference API (3 models), Simulator, Processor, UI, Grafana
```

---

## 🔐 Phase 0: Authentication

```bash
gcloud auth login
gcloud auth application-default login
```

Verify you are targeting the correct account:
```bash
gcloud config get-value account
gcloud config get-value project
```

---

## 🏗️ Phase 1: Foundation Layer (bdau-basic-vpc)

This layer creates the GCP project, VPC networking, Cloud NAT, org policy
overrides, IAM service accounts, and Artifact Registry.

> **Why two layers?** GKE Autopilot nodes are private. Without a VPC and
> Cloud NAT, they cannot reach Artifact Registry to pull Docker images.
> The `vpc-foundation` module handles all of this in a single `terraform apply`.

### 1.1 Configure Foundation Variables
```bash
cd ~/bdau-basic-vpc/scenarios/gdc-pm
cp terraform.tfvars.example terraform.tfvars
```

Open `terraform.tfvars` and fill in:
- `billing_account_id` — your GCP billing account (format: `XXXXXX-XXXXXX-XXXXXX`)
- `folder_id` — GCP folder to create the project under (or use `org_id`)
- Verify `region = "us-central1"` is correct for your deployment

### 1.2 Apply Foundation Terraform
```bash
terraform init
terraform apply
```

> **⚠️ If any resources already exist (Error 409):**
> ```bash
> PROJECT_ID=gdc-pm REGION=us-central1 \
>   bash ~/gdc-pm/scripts/terraform-import-existing.sh foundation
> terraform apply
> ```
>
> **⚠️ If Terraform fails with org policy errors:**
> ```bash
> bash ~/bdau-basic-vpc/scripts/set-org-policies.sh gdc-pm
> terraform apply
> ```

*Expected output:*
- Project `gdc-pm` created (or adopted via import)
- VPC `gdc-pm-vpc` created with subnet `subnet-gke` (10.30.0.0/20)
- Cloud NAT `gdc-pm-vpc-nat` provisioned
- `ml-pipeline-sa` and `gdc-edge-sa` Service Account keys downloaded to `~/gdc-keys/gdc-pm/`
- Artifact Registry `gdc-models` created at `us-central1-docker.pkg.dev/gdc-pm/gdc-models`

```bash
cd ~/gdc-pm
```

---

## 🏗️ Phase 2: Workload Layer (gdc-pm/terraform)

This layer creates the GKE Autopilot cluster, BigQuery dataset with three
training tables (compressor, turbine, transformer), and GCS model bucket.

### 2.1 Configure Workload Variables
```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Defaults match the foundation layer. Edit only if you changed vpc_name.
```

### 2.2 Apply Workload Terraform
```bash
cd terraform
terraform init
terraform apply
cd ..
```

*Expected output:*
- GKE Autopilot cluster `gdc-edge-simulation` created
- BigQuery dataset `grid_reliability_gold` with tables:
  - `telemetry_raw` (compressor training data)
  - `turbine_telemetry_raw` (turbine training data)
  - `transformer_telemetry_raw` (transformer training data)
- GCS bucket `gdc-pm-models` created
- Workload Identity configured for the Inference API

### 2.3 Configure kubectl
```bash
gcloud container clusters get-credentials gdc-edge-simulation \
  --region us-central1 --project gdc-pm

kubectl get nodes
```

---

## 🧠 Phase 3: BigQuery ML Model Factory

### 3.1 Install Python Dependencies
```bash
pip install google-cloud-bigquery pandas numpy pyarrow
```

### 3.2a — Compressor Model (Stator/PRD Classifier)

```bash
# Seed 3,000 rows: normal + prd_failure + thermal_runaway + bearing_wear
python3 scripts/seed-training-data.py --project gdc-pm

# Train stator_failure_classifier (5–10 min)
bash scripts/train-model.sh --project gdc-pm
```

*Expected evaluation output:*
```json
{ "precision": 0.97, "recall": 0.96, "f1_score": 0.96, "accuracy": 0.98, "roc_auc": 0.99 }
```

> **Note:** `train-model.sh` also exports the model to GCS at
> `gs://gdc-pm-models/stator_classifier/latest/` automatically.

### 3.2b — Gas Turbine Generator Model

```bash
# Seed 4,000 rows: normal + combustion_instability + blade_fouling + rotor_imbalance
python3 scripts/seed-turbine-data.py --project gdc-pm

# Train turbine_failure_classifier + export to GCS (5–10 min)
bash scripts/train-turbine-model.sh --project gdc-pm
```

*Expected GCS output:*
```
gs://gdc-pm-models/turbine_classifier/latest/model.bst
```

### 3.2c — High-Voltage Transformer Model

```bash
# Seed 4,000 rows: normal + winding_overheat + dielectric_breakdown + core_loosening
# NOTE: 'psi' column stores line voltage (kV) for transformer assets
python3 scripts/seed-transformer-data.py --project gdc-pm

# Train transformer_failure_classifier + export to GCS (5–10 min)
bash scripts/train-transformer-model.sh --project gdc-pm
```

*Expected GCS output:*
```
gs://gdc-pm-models/transformer_classifier/latest/model.bst
```

*After all three models are trained, verify GCS contents:*
```bash
gcloud storage ls gs://gdc-pm-models/ --project gdc-pm
# Expected:
# gs://gdc-pm-models/stator_classifier/latest/
# gs://gdc-pm-models/turbine_classifier/latest/
# gs://gdc-pm-models/transformer_classifier/latest/
```

---

## 🌩️ Phase 4: Edge Services Deployment

### 4.1 Configure kubectl & Artifact Registry Credentials
```bash
gcloud container clusters get-credentials gdc-edge-simulation \
  --region us-central1 --project gdc-pm

# Create pull secret so isolated pods can pull from Artifact Registry
bash ~/bdau-basic-vpc/scripts/setup-edge-auth.sh gdc-pm gdc-edge-sa gdc-pm us-central1
```

### 4.2 Deploy Data Infrastructure
```bash
# Deploy in order — AlloyDB first (schema init job runs automatically)
bash gke/alloydb-omni/start-alloydb-omni.sh
bash gke/rabbitmq/start-rabbitmq.sh
```

*Wait for both to report ✅ before continuing.*

The AlloyDB schema init job creates:
- `telemetry_events` table with all columns (including `ai_narrative`, `acknowledged`, etc.)
- `asset_registry` table seeded with all 10 assets (5 compressors + 2 turbines + 3 transformers)
- Pruning CronJob (runs nightly at 03:00 UTC)

### 4.3 Deploy Application Microservices
```bash
# Inference API loads all 3 models from gs://gdc-pm-models/{model_name}/latest/
bash gke/inference-api/start-inference-api.sh

# Event processor — generates AI narrative for all detected failures (rule_based mode)
bash gke/event-processor/start-event-processor.sh

# Telemetry simulator — now generates telemetry for 10 assets (3 asset types)
bash gke/telemetry-simulator/start-telemetry-simulator.sh
```

### 4.4 Deploy UIs & Monitoring
```bash
bash gke/fault-trigger-ui/start-fault-trigger-ui.sh
bash gke/grafana/start-grafana.sh
```

*Both scripts will print the external LoadBalancer IP at the end.*

---

## 🧪 Phase 5: Verify the System

### 5.1 Check all pods are running
```bash
kubectl get pods -n gdc-pm
```

*All pods should show `Running` or `Completed` (the init-schema job).*

### 5.2 Verify the Inference API loaded all models
```bash
kubectl exec -n gdc-pm deploy/inference-api -- \
  curl -s http://localhost:8080/model-info | jq .
```

*Expected: all three models show `"loaded": true`.*

### 5.3 Verify the Pipeline is Flowing
```bash
# Watch the event processor — should show all 10 assets with their types
kubectl logs -n gdc-pm deployment/event-processor -f
```

*Expected log lines (10 assets × all types):*
```
[✓] COMP-TX-VALLEY-01 (compressor) | sent=normal | predicted=normal (conf=0.98)
[✓] GTG-VALLEY-01 (turbine)        | sent=normal | predicted=normal (conf=0.97)
[✓] XFR-VALLEY-01 (transformer)    | sent=normal | predicted=normal (conf=0.96)
```

### 5.4 Open the Fault Trigger UI
Navigate to `http://<FAULT_TRIGGER_UI_IP>` in your browser.

The UI now shows all 10 assets with:
- Live status dots (green/yellow/orange/red) driven by the latest ML prediction
- ⓘ info buttons with full asset metadata, nominal ranges, and operations notes
- 3 demo scenarios available: Cascade Failure, Cooling System Failure, Fleet Stress Test

Test a basic compressor fault:
- Select `COMP-TX-VALLEY-01` → Burst: 5 → Click **PRD Failure**
- The events table should show 5 `prd_failure` rows with AI narrative text
- Click **▸ details** on any fault row to expand the narrative + recommended action

### 5.5 Test a Turbine Fault via API
```bash
# Inject a combustion instability event on GTG-VALLEY-01
curl -X POST http://<FAULT_TRIGGER_UI_IP>/api/inject-fault \
  -H 'Content-Type: application/json' \
  -d '{"fault_type": "combustion_instability", "asset_id": "GTG-VALLEY-01", "count": 5}'
```

> **Note:** Turbine faults require the `turbine_classifier` model to be loaded.
> If you skipped Phase 3.2b, the inference API will return 503 for turbine predictions.

### 5.6 Open Grafana
Navigate to `http://<GRAFANA_IP>` — Login: `admin` / `gdc-pm-admin`

Open **"GDC-PM — Stator Failure Detection"** dashboard. New panels include:
- **Fleet Health Timeline** (State Timeline) — health of all 10 assets over time
- **ML Confidence Trend** — model certainty on detected failures
- **Anomaly Rate % (24h)** — hourly failure detection rate KPI
- **Recent ML Detections** table now includes `ai_narrative` column

---

## 🔧 Useful Commands

```bash
# Get all service IPs
kubectl get svc -n gdc-pm

# Inject a PRD fault (compressor)
curl -X POST http://<TRIGGER_IP>/api/inject-fault \
  -H 'Content-Type: application/json' \
  -d '{"fault_type":"prd_failure","asset_id":"COMP-TX-VALLEY-01","count":5}'

# Inject a turbine fault
curl -X POST http://<TRIGGER_IP>/api/inject-fault \
  -H 'Content-Type: application/json' \
  -d '{"fault_type":"rotor_imbalance","asset_id":"GTG-RIDGE-01","count":5}'

# Inject a transformer fault
curl -X POST http://<TRIGGER_IP>/api/inject-fault \
  -H 'Content-Type: application/json' \
  -d '{"fault_type":"winding_overheat","asset_id":"XFR-VALLEY-01","count":5}'

# Run the Cascade Failure demo scenario (automated multi-step)
curl -X POST http://<TRIGGER_IP>/api/run-scenario \
  -H 'Content-Type: application/json' \
  -d '{"scenario_id":"cascade_failure"}'

# Check inference API model status
kubectl exec -n gdc-pm deploy/inference-api -- \
  curl -s http://localhost:8080/health | jq .

# Check inference API model registry
kubectl exec -n gdc-pm deploy/inference-api -- \
  curl -s http://localhost:8080/model-info | jq '.models | keys'

# Enable Gemini AI narrative (when Vertex AI API access is available)
kubectl set env deployment/event-processor \
  AI_NARRATIVE_ENABLED=gemini \
  GCP_PROJECT=gdc-pm \
  -n gdc-pm

# Retrain a specific model after data changes
bash scripts/train-model.sh          # compressor
bash scripts/train-turbine-model.sh  # turbine
bash scripts/train-transformer-model.sh  # transformer
kubectl rollout restart deployment/inference-api -n gdc-pm

# Tail the telemetry simulator (now shows all 10 assets)
kubectl logs -n gdc-pm deployment/telemetry-simulator -f

# Inject a fault via kubectl env vars (compressor example)
kubectl set env deployment/telemetry-simulator \
  INJECT_FAULT=prd_failure \
  INJECT_ASSET=COMP-TX-VALLEY-01 \
  -n gdc-pm

# Inject a turbine fault via kubectl
kubectl set env deployment/telemetry-simulator \
  INJECT_FAULT=combustion_instability \
  INJECT_ASSET=GTG-VALLEY-01 \
  -n gdc-pm
```

---

## 🔄 Rebuilding Services After Code Changes

After modifying any service, rebuild only the affected container(s):

```bash
# Example: rebuild inference-api after model or code changes
bash gke/inference-api/start-inference-api.sh

# Or using the shared push script from the foundation layer:
bash ~/bdau-basic-vpc/scripts/push-image.sh fault-trigger-ui
bash ~/bdau-basic-vpc/scripts/push-image.sh event-processor
bash ~/bdau-basic-vpc/scripts/push-image.sh inference-api
bash ~/bdau-basic-vpc/scripts/push-image.sh telemetry-simulator

# Then restart the deployments:
kubectl rollout restart deployment/fault-trigger-ui    -n gdc-pm
kubectl rollout restart deployment/event-processor     -n gdc-pm
kubectl rollout restart deployment/inference-api       -n gdc-pm
kubectl rollout restart deployment/telemetry-simulator -n gdc-pm
```

---

## 🗑️ Teardown

### Option A: Full teardown (delete the project entirely)
```bash
# Deletes the GCP project + clears all foundation Terraform state.
# ⚠️ The project ID will be blocked for 30 days.
cd ~/bdau-basic-vpc
bash scripts/teardown.sh gdc-pm

# Also clear the workload layer state
rm -f ~/gdc-pm/terraform/terraform.tfstate*
rm -rf ~/gdc-pm/terraform/.terraform
```

### Option B: Soft teardown (keep the project, remove resources)
```bash
# 1. Remove GKE edge services
kubectl delete namespace gdc-pm --wait

# 2. Destroy workload infrastructure (GKE, BQ, GCS)
cd ~/gdc-pm/terraform && terraform destroy

# 3. Destroy foundation infrastructure (VPC, NAT, SAs, AR)
cd ~/bdau-basic-vpc/scenarios/gdc-pm && terraform destroy
```

---

## 📋 Asset Reference

| Asset ID | Type | Asset Class | Failure Modes | ML Model |
|---|---|---|---|---|
| `COMP-TX-VALLEY-01` | Reciprocating Compressor | compressor | prd_failure, thermal_runaway, bearing_wear | stator_classifier |
| `COMP-TX-VALLEY-02` | Reciprocating Compressor | compressor | prd_failure, thermal_runaway, bearing_wear | stator_classifier |
| `COMP-TX-RIDGE-01`  | Centrifugal Compressor   | compressor | prd_failure, thermal_runaway, bearing_wear | stator_classifier |
| `COMP-TX-RIDGE-02`  | Centrifugal Compressor   | compressor | prd_failure, thermal_runaway, bearing_wear | stator_classifier |
| `COMP-TX-BASIN-01`  | Screw Compressor         | compressor | prd_failure, thermal_runaway, bearing_wear | stator_classifier |
| `GTG-VALLEY-01`     | Gas Turbine Generator    | turbine    | combustion_instability, blade_fouling, rotor_imbalance | turbine_classifier |
| `GTG-RIDGE-01`      | Gas Turbine Generator    | turbine    | combustion_instability, blade_fouling, rotor_imbalance | turbine_classifier |
| `XFR-VALLEY-01`     | HV Transformer (115kV)   | transformer | winding_overheat, dielectric_breakdown, core_loosening | transformer_classifier |
| `XFR-RIDGE-01`      | HV Transformer (115kV)   | transformer | winding_overheat, dielectric_breakdown, core_loosening | transformer_classifier |
| `XFR-BASIN-01`      | HV Transformer (115kV)   | transformer | winding_overheat, dielectric_breakdown, core_loosening | transformer_classifier |
