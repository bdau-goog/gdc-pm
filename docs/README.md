# GDC-PM — Predictive Maintenance on GKE/GDC
## Stator & PRD Failure Classification with BigQuery ML + Edge Inference

This repository contains a complete, automated edge ML architecture for
predictive maintenance on power grid assets. It trains a BQML XGBoost
classifier in Google Cloud, exports it to GCS, and deploys it as a real-time
inference microservice on GKE (Google Kubernetes Engine). The architecture is
designed to be migrated to **Google Distributed Cloud (GDC)** edge appliances
for offline / near-real-time inference at the grid edge.

---

## Architecture

```
┌────────────────────── Google Cloud ──────────────────────────────┐
│                                                                   │
│  BigQuery ML ──→ EXPORT MODEL ──→ GCS (model artifact)           │
│  (training data: grid_reliability_gold.telemetry_raw)            │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
          │
          │ model.bst downloaded at startup
          ▼
┌────────────────────── GKE / GDC Cluster (gdc-pm namespace) ──────┐
│                                                                   │
│  Telemetry Simulator ──→ RabbitMQ ──→ Event Processor            │
│  (synthetic PSI/Temp/Vib)              │        │                │
│                                        │        ▼                │
│                              Inference API    AlloyDB Omni        │
│                              (XGBoost model)  (telemetry_events) │
│                                                    │              │
│  Fault Trigger UI ────────────────────────────────►│              │
│  (HTML operator panel)                             │              │
│                                                    ▼              │
│  Grafana ──────────────────────── AlloyDB Omni ──► Dashboard      │
│  (live telemetry + ML alerts)                                     │
└───────────────────────────────────────────────────────────────────┘
```

### Failure Classes Detected
| Class | Label | PSI | Temp °F | Vibration |
|---|---|---|---|---|
| 0 | normal | ~855 | ~112 | ~0.02mm |
| 1 | prd_failure | ~645 | ~162 | ~0.90mm |
| 2 | thermal_runaway | ~845 | ~188 | ~0.12mm |
| 3 | bearing_wear | ~850 | ~124 | ~0.45mm |

---

## Deployment Sequence

### Prerequisites
- `gcloud` authenticated: `gcloud auth login && gcloud auth application-default login`
- `terraform`, `kubectl`, `docker` installed
- Project `gdc-pm` created and billing enabled

### Step 1 — Configure Environment
```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars with your project_id, region, project_number
```

### Step 2 — Remove Org Policy Constraints
```bash
bash scripts/set-org-policies.sh
```

### Step 3 — Provision GCP Infrastructure (APIs, GKE, BQ, GCS, IAM)
```bash
cd terraform && terraform init && terraform apply
cd ..
```

### Step 4 — Seed Training Data & Train Model
```bash
pip install google-cloud-bigquery pandas numpy pyarrow
python3 scripts/seed-training-data.py --project gdc-pm --rows 3000
bash scripts/train-model.sh --project gdc-pm
```

### Step 5 — Export Model to GCS
```bash
bash scripts/export-bqml-model.sh --project gdc-pm
```

### Step 6 — Deploy Data Layer (AlloyDB + RabbitMQ)
```bash
# Deploy in order — data services first
bash gke/alloydb-omni/start-alloydb-omni.sh
bash gke/rabbitmq/start-rabbitmq.sh
```

### Step 7 — Deploy Application Services
```bash
bash gke/inference-api/start-inference-api.sh
bash gke/event-processor/start-event-processor.sh
bash gke/telemetry-simulator/start-telemetry-simulator.sh
```

### Step 8 — Deploy UI & Monitoring
```bash
bash gke/fault-trigger-ui/start-fault-trigger-ui.sh
bash gke/grafana/start-grafana.sh
```

---

## Services

| Service | Description | Port |
|---|---|---|
| `inference-api` | XGBoost model server (FastAPI) | 8080 (internal) |
| `telemetry-simulator` | Continuous sensor data generator | — |
| `event-processor` | RabbitMQ consumer → Inference → AlloyDB | — |
| `fault-trigger-ui` | Operator fault injection panel (HTML) | 80 (LoadBalancer) |
| `grafana` | Live telemetry + ML alert dashboards | 80 (LoadBalancer) |
| `alloydb-omni` | PostgreSQL-compatible edge database | 5432 (internal) |
| `gdc-pm-rabbitmq` | AMQP message broker | 5672 (internal) |

---

## Injecting a Fault (Demo)

**Via UI:** Open the Fault Trigger UI at the external LoadBalancer IP, select an
asset, choose a fault type, and click the button.

**Via kubectl:**
```bash
kubectl set env deployment/telemetry-simulator \
  INJECT_FAULT=prd_failure \
  INJECT_ASSET=COMP-TX-VALLEY-01 \
  -n gdc-pm
```

**Via API:**
```bash
curl -X POST http://<fault-trigger-ui-ip>/api/inject-fault \
  -H 'Content-Type: application/json' \
  -d '{"fault_type": "prd_failure", "asset_id": "COMP-TX-VALLEY-01", "count": 3}'
```

---

## Grafana Dashboard

Access at `http://<grafana-ip>` — Username: `admin` / Password: `gdc-pm-admin`

Dashboard panels:
- **Stat panels**: Alert counts for last 30min (PRD, Thermal, Bearing)
- **Time-series**: PSI, Temperature, Vibration trends per asset
- **Table**: Last 50 ML detections with confidence scores

---

## GDC Migration Path

1. **Train in cloud** (BigQuery ML) — no changes needed.
2. **Export** the trained `model.bst` to GCS via `scripts/export-bqml-model.sh`.
3. **Package** the Inference API container and push to Artifact Registry.
4. On the GDC appliance, run `kubectl apply -f gke/inference-api/k8s/`
   followed by `kubectl apply -f gke/alloydb-omni/k8s/` etc.
5. GDC's GKE on Bare Metal runs the same Kubernetes manifests unchanged.
6. The Inference API downloads `model.bst` from GCS at startup, or can be
   pre-loaded into the container image for fully air-gapped operation.
