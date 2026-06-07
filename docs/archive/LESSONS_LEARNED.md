# Lessons Learned & Technical Retrospective

During the deployment of the GDC-PM architecture, several technical challenges were encountered when adapting local development patterns to GKE Autopilot and GCP organization constraints.

This document details the issues, the applied fixes, and the design patterns established to prevent them in the future.

## 1. Resource Exhaustion & Quota Limitations

**The Problem:**
GKE Autopilot cluster creation appeared to succeed, but all system pods (e.g., `kube-dns`, `metrics-server`) remained in a `Pending` state indefinitely. The cluster events showed `no nodes available to schedule pods`.

**The Root Cause:**
The GCP project (`gdc-pm`) had a Compute Engine `CPUs` quota limit of `0.0` in the `us-central1` region. Autopilot requires underlying Compute Engine CPU quota to dynamically provision its worker nodes.

**The Fix:**
Tore down the broken project and started fresh in a new project (`gdc-pm-v2`) with a verified CPU quota of `200.0`. 

**Future Prevention:**
A pre-flight quota check has been conceptualized. Before deploying GKE Autopilot, teams should verify their regional CPU quota using:
`gcloud compute project-info describe --format="table(quotas[].metric,quotas[].limit)" | grep "CPUS"`

## 2. Artifact Registry Authentication (GKE Pull Secrets)

**The Problem:**
Custom microservices (like `inference-api`) failed with `ImagePullBackOff` and `403 Forbidden` errors when attempting to pull their Docker images from the private Artifact Registry.

**The Root Cause:**
GDC Edge and GKE Autopilot isolated pods do not have implicit permission to pull from Artifact Registry without workload identity or explicit pull secrets. The `inference-api` pod was using a custom Kubernetes ServiceAccount (`ml-inference-ksa`) which lacked the `imagePullSecrets` configuration that was applied only to the `default` namespace account.

**The Fix:**
Patched the `ml-inference-ksa` ServiceAccount to include the `gcr-json-key` secret, enabling it to authenticate via the `gdc-edge-sa` identity.

**Future Prevention:**
The `setup-edge-auth.sh` script from the foundation layer is now a mandatory step in the deployment runbook (Phase 4). Future manifests must explicitly map `imagePullSecrets` if they bypass the `default` service account.

## 3. Stateful Workload Permissions (Grafana PVC)

**The Problem:**
The Grafana pod crashed constantly with `GF_PATHS_DATA='/var/lib/grafana' is not writable. Permission denied`.

**The Root Cause:**
GKE dynamically provisions PersistentVolumes (PVCs) with `root` ownership. The Grafana Docker image runs as a non-root user (ID 472). Therefore, Grafana could not write its internal SQLite database to the mounted volume.

**The Fix:**
Added a `securityContext` block to `grafana.yaml` specifying `fsGroup: 472`. This instructs the Kubelet to change the volume permissions to match the Grafana user before mounting it.

**Future Prevention:**
Any stateful container running as a non-root user requires an explicit `fsGroup` declaration in its deployment manifest. This pattern is now standardized in our yaml templates.

## 4. PostgreSQL Data Directory Initialization (AlloyDB Omni)

**The Problem:**
AlloyDB Omni crashed with `initdb: error: directory "/var/lib/postgresql/data" exists but is not empty` and `lost+found directory`.

**The Root Cause:**
Similar to the Grafana issue, standard Kubernetes PVCs often contain a root-level `lost+found` directory. PostgreSQL refuses to initialize a new database in a non-empty directory.

**The Fix:**
Added the `PGDATA` environment variable to `alloydb-omni.yaml`, pointing it to a subdirectory (`/var/lib/postgresql/data/pgdata`). This forces Postgres to create a fresh, empty directory inside the mount point.

**Future Prevention:**
All Postgres-based deployments (including AlloyDB Omni) must explicitly set the `PGDATA` environment variable to a subdirectory path.

## 5. Terraform State Management and Project Teardown

**The Problem:**
After an interrupted `terraform apply`, subsequent `apply` or `destroy` commands failed with `409 Already Exists` or `Cannot destroy cluster because deletion_protection is set to true`.

**The Fix:**
1. Explicitly set `deletion_protection = false` on BigQuery tables and GKE clusters.
2. Created a `terraform-import-existing.sh` script to recover state cleanly.
3. Created a master `teardown.sh` script that deletes the entire GCP project to ensure a guaranteed clean slate when environments get corrupted.

**Future Prevention:**
The two-tier repository architecture isolates the foundation (VPC, IAM) from the workloads. This prevents workload crashes from corrupting core networking state.
