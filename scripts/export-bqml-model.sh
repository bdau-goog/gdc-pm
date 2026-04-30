#!/bin/bash
# =============================================================================
# GDC-PM — Export BQML Model to GCS
# =============================================================================
# Exports the trained stator_failure_classifier XGBoost model artifact
# from BigQuery to a GCS bucket so it can be loaded by the Inference API
# container running on GKE/GDC.
#
# Prerequisites:
#   - Model must be trained first: bash scripts/train-model.sh
#   - GCS bucket must exist: gs://${PROJECT_ID}-models/
#   - ml-pipeline-sa must have storage.objectAdmin on the bucket
#
# Usage:
#   bash scripts/export-bqml-model.sh
#   bash scripts/export-bqml-model.sh --project gdc-pm
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
    echo "   Usage: bash scripts/export-bqml-model.sh --project YOUR_PROJECT_ID"
    exit 1
fi

DATASET_ID="grid_reliability_gold"
MODEL_ID="stator_failure_classifier"
GCS_BUCKET="${PROJECT_ID}-models"
EXPORT_PATH="gs://${GCS_BUCKET}/stator_classifier/$(date +%Y%m%d_%H%M%S)/"
LATEST_PATH="gs://${GCS_BUCKET}/stator_classifier/latest/"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — BQML Model Export${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}"
echo -e "${BOLD}  Destination: ${CYAN}${EXPORT_PATH}${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""

# ── Step 1: Export model to GCS ───────────────────────────────────────────────
echo -e "${BOLD}📦 Step 1: Exporting BQML model to GCS...${RESET}"
echo -e "${DIM}(This exports the XGBoost model.bst artifact used by the Inference API)${RESET}"

bq query \
  --use_legacy_sql=false \
  --project_id="${PROJECT_ID}" \
  "
EXPORT MODEL \`${DATASET_ID}.${MODEL_ID}\`
OPTIONS(URI = '${EXPORT_PATH}');
"

echo -e "${GREEN}  ✅ Model exported to: ${EXPORT_PATH}${RESET}"
echo ""

# ── Step 2: Copy to /latest/ for easy container reference ─────────────────────
echo -e "${BOLD}🔗 Step 2: Syncing to 'latest' path for container startup...${RESET}"

gcloud storage rsync "${EXPORT_PATH}" "${LATEST_PATH}" \
  --project="${PROJECT_ID}" \
  --recursive \
  --quiet

echo -e "${GREEN}  ✅ Synced to: ${LATEST_PATH}${RESET}"
echo ""

# ── Step 3: List exported artifacts ──────────────────────────────────────────
echo -e "${BOLD}📋 Step 3: Exported artifacts:${RESET}"
gcloud storage ls "${LATEST_PATH}" --project="${PROJECT_ID}" 2>/dev/null || \
    echo -e "${YELLOW}  ⚠️  Could not list artifacts (check bucket permissions).${RESET}"
echo ""

# ── Write latest GCS path to a local file for the Inference API startup ───────
mkdir -p "$(dirname "${SCRIPT_DIR}")/gke/inference-api"
echo "${LATEST_PATH}" > "${SCRIPT_DIR}/../gke/inference-api/.model-gcs-path"
echo -e "${DIM}  Model path written to gke/inference-api/.model-gcs-path${RESET}"

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ Model exported. You can now build and deploy the Inference API.${RESET}"
echo -e "${DIM}  Run: bash gke/inference-api/start-inference-api.sh${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""
