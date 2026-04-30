#!/bin/bash
# =============================================================================
# GDC-PM — Train BigQuery ML Model
# =============================================================================
# Triggers a BQML BOOSTED_TREE_CLASSIFIER training job on the telemetry_raw
# dataset, registers the trained model in Vertex AI Model Registry, and
# prints evaluation metrics.
#
# Prerequisites:
#   - Dataset & table seeded with: python3 scripts/seed-training-data.py
#   - gcloud auth application-default login
#
# Usage:
#   bash scripts/train-model.sh
#   bash scripts/train-model.sh --project gdc-pm
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
    echo "   Usage: bash scripts/train-model.sh --project YOUR_PROJECT_ID"
    exit 1
fi

DATASET_ID="grid_reliability_gold"
MODEL_ID="stator_failure_classifier"
VERTEX_MODEL_ID="stator_failure_classifier_v1"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — BQML Model Training${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""

# ── Step 1: Train the Model ───────────────────────────────────────────────────
echo -e "${BOLD}🚀 Step 1: Creating/replacing BQML model (this may take 5–10 minutes)...${RESET}"

bq query \
  --use_legacy_sql=false \
  --project_id="${PROJECT_ID}" \
  "
CREATE OR REPLACE MODEL \`${DATASET_ID}.${MODEL_ID}\`
OPTIONS(
  MODEL_TYPE = 'BOOSTED_TREE_CLASSIFIER',
  INPUT_LABEL_COLS = ['is_failure'],
  BOOSTER_TYPE = 'GBTREE',
  NUM_PARALLEL_TREE = 5,
  MAX_ITERATIONS = 50,
  DATA_SPLIT_METHOD = 'AUTO_SPLIT',
  MODEL_REGISTRY = 'VERTEX_AI',
  VERTEX_AI_MODEL_ID = '${VERTEX_MODEL_ID}',
  VERTEX_AI_MODEL_VERSION_ALIASES = ['production', 'gdc_poc']
) AS
SELECT
  psi, temp_f, vibration, is_failure
FROM
  \`${DATASET_ID}.telemetry_raw\`
WHERE is_failure IS NOT NULL;
"

echo -e "${GREEN}  ✅ Model training complete.${RESET}"
echo ""

# ── Grant BQ service agent access to GCS ─────────────────────────────────────
# The BigQuery service agent is auto-created on the first BQ job.
# It needs storage.objectAdmin on the model bucket for EXPORT MODEL to work.
echo -e "${BOLD}🔒 Granting BQ service agent access to GCS model bucket...${RESET}"
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")
BQ_SA="bq-${PROJECT_NUMBER}@bigquery-encryption.iam.gserviceaccount.com"
gcloud storage buckets add-iam-policy-binding "gs://${PROJECT_ID}-models" \
  --member="serviceAccount:${BQ_SA}" \
  --role="roles/storage.objectAdmin" \
  --project="${PROJECT_ID}" \
  --quiet 2>/dev/null && \
  echo -e "${GREEN}  ✅ BQ service agent granted GCS access.${RESET}" || \
  echo -e "${DIM}  (BQ service agent grant skipped — may already exist)${RESET}"
echo ""

# ── Step 2: Print Evaluation Metrics ─────────────────────────────────────────
echo -e "${BOLD}📊 Step 2: Model Evaluation Metrics...${RESET}"

bq query \
  --use_legacy_sql=false \
  --project_id="${PROJECT_ID}" \
  --format=prettyjson \
  "
SELECT
  precision, recall, f1_score, accuracy, log_loss, roc_auc
FROM
  ML.EVALUATE(MODEL \`${DATASET_ID}.${MODEL_ID}\`,
    (SELECT psi, temp_f, vibration, is_failure FROM \`${DATASET_ID}.telemetry_raw\`)
  )
ORDER BY roc_auc DESC
LIMIT 5;
"

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ Training complete. Run scripts/export-bqml-model.sh next.${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""
