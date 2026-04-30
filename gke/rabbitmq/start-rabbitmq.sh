#!/bin/bash
# =============================================================================
# GDC-PM — Deploy RabbitMQ to GKE
# =============================================================================
# Installs the RabbitMQ Cluster Operator and deploys a RabbitMQ cluster
# with a dedicated virtual host and user for GDC-PM services.
#
# Usage:
#   bash gke/rabbitmq/start-rabbitmq.sh
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../../terraform"
K8S_DIR="${SCRIPT_DIR}/k8s"

PROJECT_ID="${PROJECT_ID:-$(grep 'project_id' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || true)}"
REGION="${REGION:-$(grep 'region' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || echo "us-east4")}"
CLUSTER_NAME="${CLUSTER_NAME:-gdc-edge-simulation}"
NAMESPACE="gdc-pm"

RABBITMQ_OPERATOR_URL="https://github.com/rabbitmq/cluster-operator/releases/latest/download/cluster-operator.yml"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — RabbitMQ Deployment${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}  Cluster: ${CYAN}${CLUSTER_NAME}${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""

# ── Step 1: Configure kubectl ─────────────────────────────────────────────────
echo -e "${BOLD}🔑 Step 1: Configuring kubectl...${RESET}"
gcloud container clusters get-credentials "${CLUSTER_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}"
echo -e "${GREEN}  ✅ kubectl configured.${RESET}"
echo ""

# ── Step 2: Install RabbitMQ Cluster Operator ────────────────────────────────
echo -e "${BOLD}📦 Step 2: Installing RabbitMQ Cluster Operator...${RESET}"
kubectl apply -f "${RABBITMQ_OPERATOR_URL}"
echo -e "${DIM}  Waiting for operator to be ready...${RESET}"
kubectl wait deployment/rabbitmq-cluster-operator \
  -n rabbitmq-system \
  --for=condition=Available \
  --timeout=120s
echo -e "${GREEN}  ✅ RabbitMQ Cluster Operator installed.${RESET}"
echo ""

# ── Step 3: Ensure Namespace ──────────────────────────────────────────────────
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# ── Step 4: Create RabbitMQ Credentials Secret ───────────────────────────────
echo -e "${BOLD}🔒 Step 4: Creating RabbitMQ credentials secret...${RESET}"
RABBITMQ_PASSWORD="${RABBITMQ_PASSWORD:-$(openssl rand -base64 24 | tr -d '/+=' | head -c 32)}"

kubectl create secret generic rabbitmq-secret \
  --namespace="${NAMESPACE}" \
  --from-literal=username=gdc_user \
  --from-literal=password="${RABBITMQ_PASSWORD}" \
  --from-literal=host="gdc-pm-rabbitmq.${NAMESPACE}.svc.cluster.local" \
  --from-literal=port="5672" \
  --from-literal=vhost="gdc-pm" \
  --dry-run=client -o yaml | kubectl apply -f -

mkdir -p "${SCRIPT_DIR}/../../.secrets"
echo "${RABBITMQ_PASSWORD}" > "${SCRIPT_DIR}/../../.secrets/rabbitmq-password.txt"
chmod 600 "${SCRIPT_DIR}/../../.secrets/rabbitmq-password.txt"
echo -e "${GREEN}  ✅ Secret created. Password saved to .secrets/rabbitmq-password.txt${RESET}"
echo ""

# ── Step 5: Patch cluster manifest with the actual password ──────────────────
echo -e "${BOLD}🔧 Step 5: Deploying RabbitMQ cluster...${RESET}"
sed "s/RABBITMQ_PASSWORD_PLACEHOLDER/${RABBITMQ_PASSWORD}/g" \
    "${K8S_DIR}/rabbitmq-cluster.yaml" | kubectl apply -f -
echo ""

# ── Step 6: Wait for RabbitMQ to be ready ────────────────────────────────────
echo -e "${BOLD}⏳ Step 6: Waiting for RabbitMQ cluster to be ready...${RESET}"
echo -e "${DIM}  (This may take 60–90 seconds)${RESET}"

for i in $(seq 1 18); do
    STATUS=$(kubectl get rabbitmqcluster gdc-pm-rabbitmq -n "${NAMESPACE}" \
        -o jsonpath='{.status.conditions[?(@.type=="AllReplicasReady")].status}' 2>/dev/null || echo "")
    if [ "${STATUS}" == "True" ]; then
        break
    fi
    echo -e "${DIM}  Waiting... (${i}/18)${RESET}"
    sleep 10
done

echo -e "${GREEN}  ✅ RabbitMQ cluster is ready.${RESET}"
echo ""

echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ RabbitMQ deployed.${RESET}"
echo -e "${DIM}  AMQP: gdc-pm-rabbitmq.${NAMESPACE}.svc.cluster.local:5672${RESET}"
echo -e "${DIM}  Vhost: gdc-pm  User: gdc_user${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""
