# ============================================================================
# IAM — Workload Identity Binding
# The ml-pipeline-sa is created by the vpc-foundation layer.
# Here we reference it and bind Workload Identity so that GKE pods
# using the ml-inference-ksa Kubernetes Service Account can impersonate
# it for GCS access (downloading the exported XGBoost model).
# ============================================================================

data "google_service_account" "ml_pipeline_sa" {
  account_id = "ml-pipeline-sa"
  project    = var.project_id
}

# Allow the GKE Kubernetes Service Account (ml-inference-ksa) in the gdc-pm
# namespace to impersonate the ml-pipeline-sa GCP Service Account.
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = data.google_service_account.ml_pipeline_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[gdc-pm/ml-inference-ksa]"

  depends_on = [google_container_cluster.gdc_edge_sim]
}
