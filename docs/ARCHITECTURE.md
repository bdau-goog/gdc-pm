# GDC-PM Architecture & Repository Structure

## Overview

The GDC-PM deployment uses a **two-repository model** that cleanly separates
infrastructure provisioning from application code. This pattern is designed to
be reusable across multiple demo projects (gdc-pm, gdc-das-life, etc.) without
modification.

---

## The Two-Repo Model

```
~/bdau-basic-vpc/                  ← GCP Foundation Platform Library
│                                     "How to stand up a GCP project"
│   modules/vpc-foundation/        ← Reusable Terraform module (never edit directly)
│   scenarios/<project-name>/      ← One folder per project = one terraform apply
│   scripts/                       ← Shared infrastructure scripts for ALL projects
│       setup-edge-auth.sh
│       push-image.sh
│       teardown.sh
│       set-org-policies.sh        ← Pre-flight alternative to Terraform org policy mgmt
│
└── README.md                      ← How to use the platform library

~/gdc-pm/                          ← GDC-PM Application Repository
│                                     "What to run on the GCP project"
│   gke/                           ← Edge microservices (one directory per service)
│       alloydb-omni/
│       rabbitmq/
│       inference-api/
│       telemetry-simulator/
│       event-processor/
│       fault-trigger-ui/
│       grafana/
│
│   scripts/                       ← Application-specific scripts ONLY
│       seed-training-data.py      ← Generate & load BQML training data
│       train-model.sh             ← Execute CREATE MODEL in BigQuery
│       export-bqml-model.sh       ← EXPORT MODEL → GCS
│       terraform-import-existing.sh  ← Import pre-existing GCP resources into TF state
│
│   terraform/                     ← Workload Layer (depends on vpc-foundation output)
│       main.tf                    ← VPC data sources (references bdau-basic-vpc VPC)
│       gke.tf                     ← GKE Autopilot cluster
│       bq.tf                      ← BigQuery dataset & table
│       gcs.tf                     ← GCS model artifact bucket
│       iam.tf                     ← Workload Identity binding
│
│   docs/
│       ARCHITECTURE.md            ← This file
│       runbooks/
│           DEPLOY_FROM_SCRATCH.md ← Step-by-step deployment guide
│
└── README.md                      ← Quick start
```

---

## Separation of Concerns

| Concern | Owned by | Why |
|---|---|---|
| GCP project creation | `bdau-basic-vpc` | Single source of truth for project lifecycle |
| VPC, subnets, Cloud NAT | `bdau-basic-vpc` | Network topology is environment infrastructure |
| Org policy overrides | `bdau-basic-vpc` | Applies to the project as a whole |
| Artifact Registry repo | `bdau-basic-vpc` | Shared across all workloads in the project |
| IAM Service Accounts | `bdau-basic-vpc` | SA lifecycle managed at project level |
| GKE Autopilot cluster | `gdc-pm/terraform` | Workload-specific infrastructure |
| BigQuery dataset/table | `gdc-pm/terraform` | Application data layer |
| GCS model bucket | `gdc-pm/terraform` | Application artifact storage |
| Workload Identity binding | `gdc-pm/terraform` | Ties KSA → GSA, requires GKE to exist first |
| Application containers | `gdc-pm/gke/*` | Application code |
| ML model pipeline | `gdc-pm/scripts/*` | Application logic |

---

## Scripts Ownership

### `~/bdau-basic-vpc/scripts/` — Shared infrastructure scripts
These work for **any project** that uses the `vpc-foundation` module.

| Script | Purpose |
|---|---|
| `setup-edge-auth.sh` | Configure `kubectl` with GDC SA keys for Artifact Registry pulls |
| `push-image.sh` | Authenticate Docker and push an image to any Artifact Registry |
| `teardown.sh` | Delete a project and clear Terraform state (any scenario) |
| `set-org-policies.sh` | Pre-flight org policy override (alternative to Terraform when needed) |

### `~/gdc-pm/scripts/` — Application-specific scripts
These are **specific to the predictive maintenance use case**.

| Script | Purpose |
|---|---|
| `seed-training-data.py` | Generate and load 3,000-row training dataset into BigQuery |
| `train-model.sh` | Run BQML `CREATE OR REPLACE MODEL` |
| `export-bqml-model.sh` | Run BQML `EXPORT MODEL` → GCS |
| `terraform-import-existing.sh` | Import gdc-pm-specific pre-existing resources into Terraform state |

---

## Extending to Another Project (e.g. gdc-das-life)

Adding `gdc-das-life` to this pattern is a single `cp`:

```bash
# 1. Create the foundation scenario
cp -r ~/bdau-basic-vpc/scenarios/gdc-pm ~/bdau-basic-vpc/scenarios/gdc-das-life
# Edit scenarios/gdc-das-life/terraform.tfvars (project_id, subnets, SAs, etc.)

# 2. The gdc-das-life application repo already exists at ~/gdc-das-life
#    Add a gdc-das-life/terraform/ workload layer that references the VPC
#    (same pattern as gdc-pm/terraform/)
```

No changes to the `vpc-foundation` module are needed.

---

## Deployment Sequence (Any Project)

```
Phase 1: ~/bdau-basic-vpc/scenarios/<project>/
         terraform init && terraform apply
         ↳ Provisions: project, VPC, Cloud NAT, APIs, org policies, SAs, AR

Phase 2: ~/<project-name>/terraform/
         terraform init && terraform apply
         ↳ Provisions: GKE, application-specific databases, storage

Phase 3: ~/<project-name>/gke/*/start-*.sh
         ↳ Builds + deploys application microservices

Phase 4: ~/<project-name>/scripts/<ml-pipeline>.sh
         ↳ Trains and exports ML models (if applicable)
```
