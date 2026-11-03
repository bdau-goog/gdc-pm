#!/bin/bash
# =============================================================================
# GDC-PM — Deploy Grafana to GKE (Hardened: ClusterIP + Secret-Backed Password)
# =============================================================================
# Deploys Grafana with a pre-provisioned AlloyDB Omni datasource and the
# GDC-PM predictive maintenance dashboard without exposing a public LoadBalancer
# or hardcoded default credentials.
#
# Usage: bash gke/grafana/start-grafana.sh
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../../terraform"
K8S_DIR="${SCRIPT_DIR}/k8s"

PROJECT_ID="${PROJECT_ID:-$(grep 'project_id' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || true)}"
REGION="${REGION:-$(grep 'region' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || echo "us-east4")}"
CLUSTER_NAME="${CLUSTER_NAME:-gdc-edge-simulation}"
NAMESPACE="gdc-pm"

GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

echo -e "\n${BOLD}════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — Grafana Deployment (ClusterIP + Secret Auth)${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}"
echo -e "${BOLD}════════════════════════════════════════════════════════════════${RESET}\n"

gcloud container clusters get-credentials "${CLUSTER_NAME}" --region "${REGION}" --project "${PROJECT_ID}"

kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f - >/dev/null

if ! kubectl get secret grafana-admin-secret -n "${NAMESPACE}" >/dev/null 2>&1; then
    echo -e "${BOLD}🔐 Generating Kubernetes secret 'grafana-admin-secret'...${RESET}"
    GEN_PASS="${GRAFANA_ADMIN_PASSWORD:-$(python3 -c 'import secrets; print(secrets.token_urlsafe(18))')}"
    kubectl create secret generic grafana-admin-secret \
        --namespace="${NAMESPACE}" \
        --from-literal=password="${GEN_PASS}" >/dev/null
    echo -e "${GREEN}  ✅ Created grafana-admin-secret.${RESET}\n"
fi

echo -e "${BOLD}🗂️  Applying ConfigMaps (datasource + dashboard)...${RESET}"
kubectl apply -f "${K8S_DIR}/grafana-configmap.yaml"
echo -e "${GREEN}  ✅ ConfigMaps applied.${RESET}\n"

echo -e "${BOLD}🚀 Deploying Grafana (ClusterIP)...${RESET}"
kubectl apply -f "${K8S_DIR}/grafana.yaml"

kubectl rollout status deployment/grafana -n "${NAMESPACE}" --timeout=180s
echo -e "${GREEN}  ✅ Grafana is running (internal ClusterIP).${RESET}\n"

echo -e "\n${BOLD}════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ Grafana deployed privately (ClusterIP — zero public LB).${RESET}"
echo -e "${BOLD}  Port-Forward: ${CYAN}kubectl port-forward svc/grafana -n ${NAMESPACE} 3000:80${RESET}"
echo -e "${BOLD}  Local URL:    ${CYAN}http://localhost:3000/d/gdc-pm-main${RESET}"
echo -e "${BOLD}  Username:     ${CYAN}admin${RESET}"
echo -e "${BOLD}  Password Cmd: ${CYAN}kubectl get secret grafana-admin-secret -n ${NAMESPACE} -o jsonpath='{.data.password}' | base64 -d; echo${RESET}"
echo -e "${BOLD}════════════════════════════════════════════════════════════════${RESET}\n"
