#!/bin/bash
# =============================================================================
# GDC-PM — Build & Deploy Inference API to GKE
# =============================================================================
# Builds the XGBoost inference container, pushes it to Artifact Registry,
# and deploys it to GKE with the correct GCS model path.
#
# Prerequisites:
#   - Model exported: bash scripts/export-bqml-model.sh
#   - AlloyDB running: bash gke/alloydb-omni/start-alloydb-omni.sh
#   - RabbitMQ running: bash gke/rabbitmq/start-rabbitmq.sh
#
# Usage:
#   bash gke/inference-api/start-inference-api.sh
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../../terraform"
K8S_DIR="${SCRIPT_DIR}/k8s"

PROJECT_ID="${PROJECT_ID:-$(grep 'project_id' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || true)}"
REGION="${REGION:-$(grep 'region' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || echo "us-east4")}"
CLUSTER_NAME="${CLUSTER_NAME:-gdc-edge-simulation}"
NAMESPACE="gdc-pm"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/gdc-models/inference-api:latest"
GCS_MODEL_PATH="gs://${PROJECT_ID}-models/stator_classifier/latest/"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — Inference API Deployment${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}  Image: ${CYAN}${IMAGE_NAME}${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""

# ── Step 1: Configure Docker + kubectl ───────────────────────────────────────
echo -e "${BOLD}🔑 Step 1: Configuring Docker auth and kubectl...${RESET}"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
gcloud container clusters get-credentials "${CLUSTER_NAME}" \
  --region "${REGION}" --project "${PROJECT_ID}"
echo -e "${GREEN}  ✅ Auth configured.${RESET}"
echo ""

# ── Step 2: Build Docker Image ────────────────────────────────────────────────
echo -e "${BOLD}🐳 Step 2: Building inference-api Docker image...${RESET}"
docker build -t "${IMAGE_NAME}" "${SCRIPT_DIR}"
echo -e "${GREEN}  ✅ Image built: ${IMAGE_NAME}${RESET}"
echo ""

# ── Step 3: Push to Artifact Registry ────────────────────────────────────────
echo -e "${BOLD}📤 Step 3: Pushing image to Artifact Registry...${RESET}"
docker push "${IMAGE_NAME}"
echo -e "${GREEN}  ✅ Image pushed.${RESET}"
echo ""

# ── Step 4: Bind Workload Identity ────────────────────────────────────────────
echo -e "${BOLD}🔒 Step 4: Binding Workload Identity for GCS access...${RESET}"
gcloud iam service-accounts add-iam-policy-binding \
  "ml-pipeline-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${NAMESPACE}/ml-inference-ksa]" \
  --project "${PROJECT_ID}" \
  --quiet 2>/dev/null || echo -e "${DIM}  (Binding already exists — skipping)${RESET}"
echo -e "${GREEN}  ✅ Workload Identity bound.${RESET}"
echo ""

# ── Step 5: Deploy to GKE ─────────────────────────────────────────────────────
echo -e "${BOLD}🚀 Step 5: Deploying inference-api to GKE...${RESET}"
sed \
  -e "s|GCR_IMAGE_PLACEHOLDER|${IMAGE_NAME}|g" \
  -e "s|GCS_MODEL_PATH_PLACEHOLDER|${GCS_MODEL_PATH}|g" \
  -e "s|PROJECT_ID_PLACEHOLDER|${PROJECT_ID}|g" \
  "${K8S_DIR}/inference-api.yaml" | kubectl apply -f -
echo ""

# ── Step 6: Wait for rollout ──────────────────────────────────────────────────
echo -e "${BOLD}⏳ Step 6: Waiting for inference-api rollout...${RESET}"
kubectl rollout status deployment/inference-api -n "${NAMESPACE}" --timeout=180s
echo -e "${GREEN}  ✅ Inference API is running.${RESET}"
echo ""

echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ Inference API deployed.${RESET}"
echo -e "${DIM}  Endpoint: http://inference-api.${NAMESPACE}.svc.cluster.local:8080/predict${RESET}"
echo -e "${DIM}  Health:   http://inference-api.${NAMESPACE}.svc.cluster.local:8080/health${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""
