# ============================================================================
# GKE CLUSTER — SIMULATION ENVIRONMENT ONLY
#
# This Terraform file provisions the GKE-based cloud simulation cluster used
# to develop and test the GDC Predictive Maintenance demo before deploying
# to a real GDC cluster. It is NOT used in production GDC deployments.
#
# ── Target Environment: GKE (Google Kubernetes Engine) ─────────────────────
#   Used for: CI/CD, feature development, demo live environment on GCP
#   Cluster type: Standard (was Autopilot — switching enables GPU node pools)
#   Infrastructure: Managed by Terraform via google_container_cluster
#
# ── NOT for: GDC Software-Only or GDC Connected ─────────────────────────────
#   GDC clusters are provisioned by the GDC Platform itself (via the GDC
#   Console or bmctl for on-prem bare metal). This Terraform file should NOT
#   be applied to a GDC target.
#
#   For GDC Software-Only deployment:
#     1. The GDC cluster is pre-provisioned — no Terraform needed
#     2. Deploy the app manifests directly: kubectl apply -f gke/
#     3. Set LOCAL_MODELS_DIR=/app/models in the inference-api Deployment
#     4. Install the NVIDIA GPU Operator on the cluster for Ollama GPU support
#     5. No GCS bucket, no Workload Identity, no GCE-specific StorageClasses
#
# Cloud NAT is already provisioned by the vpc-foundation layer — GKE private
# nodes use it to reach Artifact Registry and GCP APIs without public IPs.
# ============================================================================

resource "google_container_cluster" "gdc_edge_sim" {
  name     = "gdc-edge-simulation"
  location = var.region
  project  = var.project_id

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = data.google_compute_network.vpc.self_link
  subnetwork = data.google_compute_subnetwork.gke_subnet.self_link

  release_channel {
    channel = "REGULAR"
  }

  # Workload Identity — allows GKE pods to use GCP Service Accounts
  # without downloading JSON keys. The Inference API uses this to pull
  # model artifacts from GCS.
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Allow terraform destroy in demo environments
  deletion_protection = false
}

resource "google_container_node_pool" "default_pool" {
  name       = "default-pool"
  cluster    = google_container_cluster.gdc_edge_sim.name
  location   = var.region
  node_count = 1

  node_config {
    machine_type = "e2-standard-4"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_container_node_pool" "gpu_pool" {
  name       = "gpu-pool"
  cluster    = google_container_cluster.gdc_edge_sim.name
  location   = var.region
  node_count = 1

  node_config {
    machine_type = "g2-standard-8"
    
    guest_accelerator {
      type  = "nvidia-l4"
      count = 1
      gpu_driver_installation_config {
        gpu_driver_version = "LATEST"
      }
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }
  }
}
