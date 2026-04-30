#!/bin/bash
# =============================================================================
# GDC-PM — Deploy Grafana to GKE
# =============================================================================
# Deploys Grafana with a pre-provisioned AlloyDB Omni datasource and the
# GDC-PM predictive maintenance dashboard. No manual configuration required.
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
echo -e "${BOLD}  GDC-PM — Grafana Deployment${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}"
echo -e "${BOLD}════════════════════════════════════════════════════════════════${RESET}\n"

gcloud container clusters get-credentials "${CLUSTER_NAME}" --region "${REGION}" --project "${PROJECT_ID}"

echo -e "${BOLD}🗂️  Applying ConfigMaps (datasource + dashboard)...${RESET}"
kubectl apply -f "${K8S_DIR}/grafana-configmap.yaml"
echo -e "${GREEN}  ✅ ConfigMaps applied.${RESET}\n"

echo -e "${BOLD}🚀 Deploying Grafana...${RESET}"
kubectl apply -f "${K8S_DIR}/grafana.yaml"

kubectl rollout status deployment/grafana -n "${NAMESPACE}" --timeout=180s
echo -e "${GREEN}  ✅ Grafana is running.${RESET}\n"

echo -e "${BOLD}⏳ Waiting for LoadBalancer IP...${RESET}"
GRAFANA_IP=""
for i in $(seq 1 18); do
    GRAFANA_IP=$(kubectl get svc grafana -n "${NAMESPACE}" \
        -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
    if [ -n "${GRAFANA_IP}" ]; then break; fi
    echo -e "${DIM}  Waiting... (${i}/18)${RESET}"
    sleep 10
done

echo -e "\n${BOLD}════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD}  ✅ Grafana deployed.${RESET}"
if [ -n "${GRAFANA_IP}" ]; then
    echo -e "${BOLD}  URL:      ${CYAN}http://${GRAFANA_IP}${RESET}"
    echo -e "${BOLD}  Username: ${CYAN}admin${RESET}"
    echo -e "${BOLD}  Password: ${CYAN}gdc-pm-admin${RESET}"
    echo -e "${DIM}  Dashboard: http://${GRAFANA_IP}/d/gdc-pm-main${RESET}"
fi
echo -e "${BOLD}════════════════════════════════════════════════════════════════${RESET}\n"
