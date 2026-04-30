# ============================================================================
# CLOUD STORAGE — Model Artifact Bucket
# ============================================================================

resource "google_storage_bucket" "model_artifacts" {
  name          = "${var.project_id}-models"
  location      = var.region
  project       = var.project_id
  force_destroy = true  # Allow terraform destroy to empty the bucket

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# Grant ml-pipeline-sa write access for EXPORT MODEL
resource "google_storage_bucket_iam_member" "ml_sa_gcs_writer" {
  bucket = google_storage_bucket.model_artifacts.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${data.google_service_account.ml_pipeline_sa.email}"
}

# NOTE: The BigQuery service agent (bq-<project-number>@bigquery-encryption.iam.gserviceaccount.com)
# is auto-created by GCP the first time any BigQuery job runs. We cannot grant it IAM
# permissions here because it doesn't exist yet. The train-model.sh script grants this
# permission automatically after the first BQ job activates the service agent.
