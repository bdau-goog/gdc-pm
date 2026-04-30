# ============================================================================
# GKE AUTOPILOT CLUSTER
# Deployed into the VPC and subnet created by the vpc-foundation layer.
# Cloud NAT is already provisioned by the foundation — GKE private nodes
# use it to reach Artifact Registry and GCP APIs without public IPs.
# ============================================================================

resource "google_container_cluster" "gdc_edge_sim" {
  name     = "gdc-edge-simulation"
  location = var.region
  project  = var.project_id

  enable_autopilot = true

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
