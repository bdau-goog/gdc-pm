#!/bin/bash
# =============================================================================
# GDC-PM — Train BigQuery ML Model: HV Transformer Failure Classifier
# =============================================================================
# Trains a BOOSTED_TREE_CLASSIFIER on transformer_telemetry_raw to classify:
#   0 = normal
#   1 = winding_overheat
#   2 = dielectric_breakdown
#   3 = core_loosening
#
# NOTE: The 'psi' feature column stores line voltage (kV) for transformer assets.
#       The model learns from the feature value distributions, not the column name.
#
# Prerequisites:
#   - Transformer data seeded: python3 scripts/seed-transformer-data.py --project gdc-pm
#   - gcloud auth application-default login
#
# Usage:
#   bash scripts/train-transformer-model.sh
#   bash scripts/train-transformer-model.sh --project gdc-pm
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../terraform"

# Determine Project ID
if [ -n "${1:-}" ] && [[ "$1" == "--project" ]]; then
    PROJECT_ID="$2"
elif [ -n "${PROJECT_ID:-}" ]; then
    PROJECT_ID="${PROJECT_ID}"
else
    PROJECT_ID=$(grep 'project_id' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || true)
fi

if [ -z "${PROJECT_ID:-}" ]; then
    echo "❌ Could not determine project_id."
    echo "   Usage: bash scripts/train-transformer-model.sh --project YOUR_PROJECT_ID"
    exit 1
fi

DATASET_ID="grid_reliability_gold"
MODEL_ID="transformer_failure_classifier"
GCS_BUCKET="${PROJECT_ID}-models"
EXPORT_PATH="gs://${GCS_BUCKET}/transformer_classifier/$(date +%Y%m%d_%H%M%S)/"
LATEST_PATH="gs://${GCS_BUCKET}/transformer_classifier/latest/"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — Transformer BQML Model Training & Export${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""

# ── Step 1: Train ─────────────────────────────────────────────────────────────
echo -e "${BOLD}🚀 Step 1: Training transformer_failure_classifier (5–10 minutes)...${RESET}"

bq query \
  --use_legacy_sql=false \
  --project_id="${PROJECT_ID}" \
  "
CREATE OR REPLACE MODEL \`${DATASET_ID}.${MODEL_ID}\`
OPTIONS(
  MODEL_TYPE           = 'BOOSTED_TREE_CLASSIFIER',
  INPUT_LABEL_COLS     = ['is_failure'],
  BOOSTER_TYPE         = 'GBTREE',
  NUM_PARALLEL_TREE    = 5,
  MAX_ITERATIONS       = 50,
  DATA_SPLIT_METHOD    = 'AUTO_SPLIT'
) AS
SELECT
  psi, temp_f, vibration, is_failure
FROM
  \`${DATASET_ID}.transformer_telemetry_raw\`
WHERE is_failure IS NOT NULL;
"

echo -e "${GREEN}  ✅ Model training complete.${RESET}"
echo ""

# ── Step 2: Evaluation Metrics ────────────────────────────────────────────────
echo -e "${BOLD}📊 Step 2: Evaluation Metrics...${RESET}"
bq query \
  --use_legacy_sql=false \
  --project_id="${PROJECT_ID}" \
  --format=prettyjson \
  "
SELECT precision, recall, f1_score, accuracy, log_loss, roc_auc
FROM ML.EVALUATE(MODEL \`${DATASET_ID}.${MODEL_ID}\`,
  (SELECT psi, temp_f, vibration, is_failure FROM \`${DATASET_ID}.transformer_telemetry_raw\`)
)
ORDER BY roc_auc DESC
LIMIT 5;
"

echo ""

# ── Step 3: Grant BQ service agent GCS access ────────────────────────────────
echo -e "${BOLD}🔒 Granting BQ service agent GCS access...${RESET}"
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
BQ_SA="bq-${PROJECT_NUMBER}@bigquery-encryption.iam.gserviceaccount.com"
gcloud storage buckets add-iam-policy-binding "gs://${GCS_BUCKET}" \
  --member="serviceAccount:${BQ_SA}" \
  --role="roles/storage.objectAdmin" \
  --project="${PROJECT_ID}" \
  --quiet 2>/dev/null && \
  echo -e "${GREEN}  ✅ BQ service agent granted GCS access.${RESET}" || \
  echo -e "${DIM}  (Grant skipped — may already exist)${RESET}"
echo ""

# ── Step 4: Export Model ──────────────────────────────────────────────────────
echo -e "${BOLD}📦 Step 3: Exporting transformer model to GCS...${RESET}"
bq query \
  --use_legacy_sql=false \
  --project_id="${PROJECT_ID}" \
  "EXPORT MODEL \`${DATASET_ID}.${MODEL_ID}\` OPTIONS(URI = '${EXPORT_PATH}');"

echo -e "${GREEN}  ✅ Exported to: ${EXPORT_PATH}${RESET}"

# ── Step 5: Sync to /latest/ ─────────────────────────────────────────────────
echo -e "${BOLD}🔗 Step 4: Syncing to 'latest' path...${RESET}"
gcloud storage rsync "${EXPORT_PATH}" "${LATEST_PATH}" \
  --project="${PROJECT_ID}" --recursive --quiet

echo -e "${GREEN}  ✅ Synced to: ${LATEST_PATH}${RESET}"

# Write path for inference API
echo "${LATEST_PATH}" > "${SCRIPT_DIR}/../gke/inference-api/.transformer-model-gcs-path"

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ transformer_classifier trained and exported.${RESET}"
echo -e "${DIM}  Rebuild and redeploy the inference-api to load the new model.${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""
