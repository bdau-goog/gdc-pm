#!/bin/bash
# =============================================================================
# GDC-PM — Deploy AlloyDB Omni to GKE
# =============================================================================
# Deploys AlloyDB Omni (containerized AlloyDB for edge/GDC) to GKE,
# creates the Kubernetes Secret for credentials, and initializes the schema.
#
# Usage:
#   bash gke/alloydb-omni/start-alloydb-omni.sh
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../../terraform"
K8S_DIR="${SCRIPT_DIR}/k8s"

PROJECT_ID="${PROJECT_ID:-$(grep 'project_id' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || true)}"
REGION="${REGION:-$(grep 'region' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || echo "us-east4")}"
CLUSTER_NAME="${CLUSTER_NAME:-gdc-edge-simulation}"
NAMESPACE="gdc-pm"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — AlloyDB Omni Deployment${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}  Cluster: ${CYAN}${CLUSTER_NAME}${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""

# ── Step 1: Configure kubectl ─────────────────────────────────────────────────
echo -e "${BOLD}🔑 Step 1: Configuring kubectl for cluster '${CLUSTER_NAME}'...${RESET}"
gcloud container clusters get-credentials "${CLUSTER_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}"
echo -e "${GREEN}  ✅ kubectl configured.${RESET}"
echo ""

# ── Step 2: Create Namespace ──────────────────────────────────────────────────
echo -e "${BOLD}📁 Step 2: Creating namespace '${NAMESPACE}'...${RESET}"
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}  ✅ Namespace ready.${RESET}"
echo ""

# ── Step 3: Create AlloyDB Credentials Secret ─────────────────────────────────
echo -e "${BOLD}🔒 Step 3: Creating AlloyDB credentials secret...${RESET}"

# Generate a strong random password if none exists
DB_PASSWORD="${ALLOYDB_PASSWORD:-$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)}"

kubectl create secret generic alloydb-secret \
  --namespace="${NAMESPACE}" \
  --from-literal=username=postgres \
  --from-literal=password="${DB_PASSWORD}" \
  --dry-run=client -o yaml | kubectl apply -f -

# Save password locally for other services to read
mkdir -p "${SCRIPT_DIR}/../../.secrets"
echo "${DB_PASSWORD}" > "${SCRIPT_DIR}/../../.secrets/alloydb-password.txt"
chmod 600 "${SCRIPT_DIR}/../../.secrets/alloydb-password.txt"
echo -e "${GREEN}  ✅ Secret created. Password saved to .secrets/alloydb-password.txt${RESET}"
echo ""

# ── Step 4: Deploy AlloyDB Omni ───────────────────────────────────────────────
echo -e "${BOLD}🚀 Step 4: Deploying AlloyDB Omni...${RESET}"
kubectl apply -f "${K8S_DIR}/alloydb-omni.yaml"
echo ""

# ── Step 5: Wait for AlloyDB to be ready ─────────────────────────────────────
echo -e "${BOLD}⏳ Step 5: Waiting for AlloyDB Omni to become ready...${RESET}"
kubectl rollout status deployment/alloydb-omni -n "${NAMESPACE}" --timeout=120s
echo -e "${GREEN}  ✅ AlloyDB Omni is running.${RESET}"
echo ""

# ── Step 6: Initialize Schema ─────────────────────────────────────────────────
echo -e "${BOLD}🗄️  Step 6: Initializing database schema...${RESET}"
# Delete any previous init job to allow re-runs
kubectl delete job alloydb-init-schema -n "${NAMESPACE}" --ignore-not-found=true
kubectl apply -f "${K8S_DIR}/init-schema.yaml"

echo -e "${DIM}  Waiting for schema init job to complete...${RESET}"
kubectl wait --for=condition=complete job/alloydb-init-schema \
  -n "${NAMESPACE}" --timeout=120s
echo -e "${GREEN}  ✅ Schema initialized.${RESET}"
echo ""

echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ AlloyDB Omni deployed and ready.${RESET}"
echo -e "${DIM}  Host: alloydb-omni.${NAMESPACE}.svc.cluster.local:5432${RESET}"
echo -e "${DIM}  DB:   grid_reliability${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""
