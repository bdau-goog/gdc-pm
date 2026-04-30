#!/bin/bash
# =============================================================================
# GDC-PM — Build & Deploy Event Processor to GKE
# =============================================================================
# Usage: bash gke/event-processor/start-event-processor.sh
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../../terraform"
K8S_DIR="${SCRIPT_DIR}/k8s"

PROJECT_ID="${PROJECT_ID:-$(grep 'project_id' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || true)}"
REGION="${REGION:-$(grep 'region' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || echo "us-east4")}"
CLUSTER_NAME="${CLUSTER_NAME:-gdc-edge-simulation}"
NAMESPACE="gdc-pm"
IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/gdc-models/event-processor:latest"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

echo -e "\n${BOLD}════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — Event Processor Deployment${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}"
echo -e "${BOLD}════════════════════════════════════════════════════════════════${RESET}\n"

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
gcloud container clusters get-credentials "${CLUSTER_NAME}" --region "${REGION}" --project "${PROJECT_ID}"

echo -e "${BOLD}🐳 Building image...${RESET}"
docker build -t "${IMAGE_NAME}" "${SCRIPT_DIR}"
echo -e "${BOLD}📤 Pushing image...${RESET}"
docker push "${IMAGE_NAME}"

echo -e "${BOLD}🚀 Deploying to GKE...${RESET}"
sed "s|GCR_IMAGE_PLACEHOLDER|${IMAGE_NAME}|g" \
    "${K8S_DIR}/event-processor.yaml" | kubectl apply -f -

kubectl rollout status deployment/event-processor -n "${NAMESPACE}" --timeout=120s

echo -e "\n${BOLD}════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ Event Processor deployed.${RESET}"
echo -e "${DIM}  Pipeline: RabbitMQ → Event Processor → Inference API → AlloyDB${RESET}"
echo -e "${BOLD}════════════════════════════════════════════════════════════════${RESET}\n"
