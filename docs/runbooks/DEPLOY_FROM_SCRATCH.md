# GDC-PM: Zero-to-Edge Deployment Runbook

This runbook walks you through deploying the entire GDC-PM Predictive Maintenance
architecture — from a blank GCP account to a running edge simulation — step by step.

The deployment is split into two Terraform layers followed by the GKE service deployments:

```
Layer 1: bdau-basic-vpc/scenarios/gdc-pm/  (Foundation)
         ↳ Creates: GCP project, VPC, Cloud NAT, APIs, Org Policies, IAM, Artifact Registry

Layer 2: gdc-pm/terraform/                 (Workloads)
         ↳ Creates: GKE Autopilot cluster, BigQuery dataset, GCS model bucket

GKE Services: gdc-pm/gke/*/start-*.sh     (Edge Services)
              ↳ Deploys: AlloyDB, RabbitMQ, Inference API, Simulator, Processor, Grafana, UI
```

---

## 🔐 Phase 0: Authentication

```bash
# Log in to GCP
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
> Resources such as the project, Artifact Registry, or Service Accounts may
> have been created by a previous `terraform apply`. Import them all into
> Terraform state using the provided import script, then re-apply:
> ```bash
> # Run from ~/bdau-basic-vpc/scenarios/gdc-pm
> PROJECT_ID=gdc-pm REGION=us-central1 \
>   bash ~/gdc-pm/scripts/terraform-import-existing.sh foundation
> terraform apply
> ```
> The script gracefully skips any resources that don't exist yet.
>
> **⚠️ If Terraform fails with org policy errors before creating APIs:**
> Run the pre-flight org policy script first, then retry:
> ```bash
> bash ~/bdau-basic-vpc/scripts/set-org-policies.sh gdc-pm
> terraform apply
> ```

*Expected output:*
- Project `gdc-pm` created (or adopted via import)
- VPC `gdc-pm-vpc` created with subnet `subnet-gke` (10.30.0.0/20)
- Cloud NAT `gdc-pm-vpc-nat` provisioned (enables GKE private nodes to reach GCPs APIs)
- Org policy overrides applied gracefully
- `ml-pipeline-sa` and `gdc-edge-sa` Service Account keys downloaded to `~/gdc-keys/gdc-pm/`
- Artifact Registry `gdc-models` created at `us-central1-docker.pkg.dev/gdc-pm/gdc-models`

```bash
cd ~/gdc-pm
```

---

## 🏗️ Phase 2: Workload Layer (gdc-pm/terraform)

This layer creates the GKE Autopilot cluster, BigQuery dataset, and GCS model
bucket. It references the VPC created in Phase 1 via data sources.

### 2.1 Configure Workload Variables
```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

The defaults match the foundation layer. Edit only if you changed `vpc_name`
or `gke_subnet_name` in Phase 1.

### 2.2 Apply Workload Terraform
```bash
cd terraform
terraform init
terraform apply
cd ..
```

*Expected output:*
- GKE Autopilot cluster `gdc-edge-simulation` created in `gdc-pm-vpc/subnet-gke`
- Workload Identity configured (GKE pods can access GCS without JSON keys)
- BigQuery dataset `grid_reliability_gold` and `telemetry_raw` table created
- GCS bucket `gdc-pm-models` created with versioning enabled
- Workload Identity binding created for the Inference API

### 2.3 Configure kubectl
Pull credentials so `kubectl` is ready before the edge service deployments:
```bash
gcloud container clusters get-credentials gdc-edge-simulation \
  --region us-central1 --project gdc-pm

# Verify
kubectl get nodes
```

---

## 🧠 Phase 3: BigQuery ML Model Factory

### 3.1 Install Python Dependencies
```bash
pip install google-cloud-bigquery pandas numpy pyarrow
```

### 3.2 Seed Training Data
Generates 3,000 rows across 5 assets with 4 failure classes (PRD Failure,
Thermal Runaway, Bearing Wear, Normal) at ~12% failure rate.
```bash
python3 scripts/seed-training-data.py --project gdc-pm
```

*Expected output:*
```
✅ Loaded 3000 rows into gdc-pm.grid_reliability_gold.telemetry_raw
   Total Failure Rate: 12.1%
```

### 3.3 Train the BQML Model
```bash
bash scripts/train-model.sh
```

*Takes 5–10 minutes. Expected output includes evaluation metrics:*
```json
{ "precision": 0.97, "recall": 0.96, "f1_score": 0.96,
  "accuracy": 0.98, "roc_auc": 0.99 }
```

### 3.4 Export Model Artifacts to GCS
```bash
bash scripts/export-bqml-model.sh
```

*Expected output:*
```
✅ Model exported to: gs://gdc-pm-models/stator_classifier/<timestamp>/
✅ Synced to: gs://gdc-pm-models/stator_classifier/latest/
```

---

## 🌩️ Phase 4: Edge Services Deployment

### 4.1 Configure kubectl & Artifact Registry Credentials
Because GDC edge nodes (or GKE Autopilot testing nodes) run isolated pods, they need explicit
permission to pull container images from your Artifact Registry. We configure a Kubernetes
secret using the `gdc-edge-sa` JSON key that Terraform downloaded in Phase 1.

```bash
gcloud container clusters get-credentials gdc-edge-simulation \
  --region us-central1 --project gdc-pm

bash ~/bdau-basic-vpc/scripts/setup-edge-auth.sh gdc-pm gdc-edge-sa gdc-pm us-central1
```

### 4.2 Deploy Data Infrastructure
```bash
bash gke/alloydb-omni/start-alloydb-omni.sh
bash gke/rabbitmq/start-rabbitmq.sh
```

*Wait for both to report ✅ before continuing.*

### 4.3 Deploy Application Microservices
```bash
bash gke/inference-api/start-inference-api.sh
bash gke/event-processor/start-event-processor.sh
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

### 5.2 Verify the Pipeline is Flowing
```bash
# Watch the event processor logs — should show messages processing every 5s
kubectl logs -n gdc-pm deployment/event-processor -f
```

*Expected log lines:*
```
[✓] COMP-TX-VALLEY-01 | sent=normal | predicted=normal (conf=0.98)
[✓] COMP-TX-RIDGE-01  | sent=normal | predicted=normal (conf=0.97)
```

### 5.3 Open the Fault Trigger UI
Navigate to `http://<FAULT_TRIGGER_UI_IP>` in your browser.

- Select asset `COMP-TX-VALLEY-01`
- Set Burst Count to `5`
- Click **"PRD Failure"** (red button)

*The "Recent Detections" table should show 5 `prd_failure` rows within seconds.*

### 5.4 Open Grafana
Navigate to `http://<GRAFANA_IP>` in your browser.
- Login: `admin` / `gdc-pm-admin`
- Open the **"GDC-PM — Stator Failure Detection"** dashboard

*Within 5 seconds of injecting a fault, the "PRD Failures" stat panel should
increment and the sensor graphs should show the characteristic anomaly signature.*

---

## 🔧 Useful Commands

```bash
# Get all service IPs
kubectl get svc -n gdc-pm

# Inject a PRD fault via command line
curl -X POST http://<TRIGGER_IP>/api/inject-fault \
  -H 'Content-Type: application/json' \
  -d '{"fault_type":"prd_failure","asset_id":"COMP-TX-VALLEY-01","count":5}'

# Check inference API health
kubectl exec -n gdc-pm deploy/inference-api -- \
  curl -s http://localhost:8080/health | jq .

# Tail the telemetry simulator
kubectl logs -n gdc-pm deployment/telemetry-simulator -f

# Retrain the model (after data changes)
bash scripts/train-model.sh
bash scripts/export-bqml-model.sh
kubectl rollout restart deployment/inference-api -n gdc-pm
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
