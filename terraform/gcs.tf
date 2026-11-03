# ============================================================================
# CLOUD STORAGE — Model Artifact Bucket (Least-Privilege Bucket IAM)
# ============================================================================

resource "google_storage_bucket" "model_artifacts" {
  name                     = "${var.project_id}-models"
  location                 = var.region
  project                  = var.project_id
  force_destroy            = true  # Allow terraform destroy to empty the bucket
  public_access_prevention = "enforced"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# Grant ml-pipeline-sa bucket-scoped read + create access (never project-wide storage.admin/objectAdmin)
resource "google_storage_bucket_iam_member" "ml_sa_gcs_viewer" {
  bucket = google_storage_bucket.model_artifacts.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${data.google_service_account.ml_pipeline_sa.email}"
}

resource "google_storage_bucket_iam_member" "ml_sa_gcs_creator" {
  bucket = google_storage_bucket.model_artifacts.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${data.google_service_account.ml_pipeline_sa.email}"
}

# NOTE: The BigQuery service agent (bq-<project-number>@bigquery-encryption.iam.gserviceaccount.com)
# is auto-created by GCP the first time any BigQuery job runs. The train-*.sh scripts grant it
# bucket-scoped roles/storage.objectViewer + roles/storage.objectCreator after the first BQ job.
