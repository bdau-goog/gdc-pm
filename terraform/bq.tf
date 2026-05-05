# ============================================================================
# BIGQUERY DATASET — grid_reliability_gold
# ============================================================================

resource "google_bigquery_dataset" "grid_reliability" {
  dataset_id  = "grid_reliability_gold"
  project     = var.project_id
  location    = var.region
  description = "Dataset for grid reliability predictive maintenance (BQML & Vertex AI)"
}

# ── Stator / Compressor Training Table ────────────────────────────────────────
resource "google_bigquery_table" "telemetry_raw" {
  dataset_id          = google_bigquery_dataset.grid_reliability.dataset_id
  table_id            = "telemetry_raw"
  project             = var.project_id
  description         = "Raw telemetry for stator/PRD compressor ML model training"
  deletion_protection = false

  schema = <<EOF
[
  { "name": "timestamp",    "type": "STRING",  "mode": "NULLABLE" },
  { "name": "asset_id",     "type": "STRING",  "mode": "NULLABLE" },
  { "name": "psi",          "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Pressure (PSI) — nominal ~855" },
  { "name": "temp_f",       "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Temperature (°F) — nominal ~112" },
  { "name": "vibration",    "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Vibration amplitude (mm) — nominal ~0.02" },
  { "name": "is_failure",   "type": "INTEGER", "mode": "NULLABLE",
    "description": "Failure class: 0=normal 1=prd_failure 2=thermal_runaway 3=bearing_wear" },
  { "name": "failure_type", "type": "STRING",  "mode": "NULLABLE",
    "description": "Human-readable failure label" }
]
EOF
}

# ── Gas Turbine Generator Training Table ──────────────────────────────────────
resource "google_bigquery_table" "turbine_telemetry_raw" {
  dataset_id          = google_bigquery_dataset.grid_reliability.dataset_id
  table_id            = "turbine_telemetry_raw"
  project             = var.project_id
  description         = "Raw telemetry for gas turbine generator ML model training"
  deletion_protection = false

  schema = <<EOF
[
  { "name": "timestamp",    "type": "STRING",  "mode": "NULLABLE" },
  { "name": "asset_id",     "type": "STRING",  "mode": "NULLABLE" },
  { "name": "psi",          "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Combustion pressure (PSI) — nominal ~2200" },
  { "name": "temp_f",       "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Exhaust temperature (°F) — nominal ~1050" },
  { "name": "vibration",    "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Rotor vibration (mm) — nominal ~0.05" },
  { "name": "is_failure",   "type": "INTEGER", "mode": "NULLABLE",
    "description": "Failure class: 0=normal 1=combustion_instability 2=blade_fouling 3=rotor_imbalance" },
  { "name": "failure_type", "type": "STRING",  "mode": "NULLABLE",
    "description": "Human-readable failure label" }
]
EOF
}

# ── High-Voltage Transformer Training Table ───────────────────────────────────
resource "google_bigquery_table" "transformer_telemetry_raw" {
  dataset_id          = google_bigquery_dataset.grid_reliability.dataset_id
  table_id            = "transformer_telemetry_raw"
  project             = var.project_id
  description         = "Raw telemetry for HV transformer ML model training (psi column stores kV)"
  deletion_protection = false

  schema = <<EOF
[
  { "name": "timestamp",    "type": "STRING",  "mode": "NULLABLE" },
  { "name": "asset_id",     "type": "STRING",  "mode": "NULLABLE" },
  { "name": "psi",          "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Line voltage (kV) stored in PSI column — nominal ~115 kV" },
  { "name": "temp_f",       "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Oil temperature (°F) — nominal ~185" },
  { "name": "vibration",    "type": "FLOAT",   "mode": "NULLABLE",
    "description": "Core/frame vibration (mm) — nominal ~0.01" },
  { "name": "is_failure",   "type": "INTEGER", "mode": "NULLABLE",
    "description": "Failure class: 0=normal 1=winding_overheat 2=dielectric_breakdown 3=core_loosening" },
  { "name": "failure_type", "type": "STRING",  "mode": "NULLABLE",
    "description": "Human-readable failure label" }
]
EOF
}
