# ============================================================================
# BIGQUERY DATASET
# ============================================================================

resource "google_bigquery_dataset" "grid_reliability" {
  dataset_id  = "grid_reliability_gold"
  project     = var.project_id
  location    = var.region
  description = "Dataset for grid reliability predictive maintenance (BQML & Vertex AI)"

}

resource "google_bigquery_table" "telemetry_raw" {
  dataset_id = google_bigquery_dataset.grid_reliability.dataset_id
  table_id   = "telemetry_raw"
  project    = var.project_id
  
  description        = "Raw telemetry data for stator/PRD ML model training"
  deletion_protection = false

  schema = <<EOF
[
  {
    "name": "timestamp",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "asset_id",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "psi",
    "type": "FLOAT",
    "mode": "NULLABLE"
  },
  {
    "name": "temp_f",
    "type": "FLOAT",
    "mode": "NULLABLE"
  },
  {
    "name": "vibration",
    "type": "FLOAT",
    "mode": "NULLABLE"
  },
  {
    "name": "is_failure",
    "type": "INTEGER",
    "mode": "NULLABLE"
  }
]
EOF

}
