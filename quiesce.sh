#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"
source "${SCRIPT_DIR}/.env"

echo "=================================================="
echo "🛑 Quiescing GDC-PM Demo Cluster (gdc-edge-simulation)"
echo "• Project   : ${GOOGLE_CLOUD_PROJECT}"
echo "• Namespace : gdc-pm"
echo "=================================================="

# 1. Scale down deployments to 0
echo "📦 [1/2] Scaling down deployments to 0..."
kubectl scale deployment -n gdc-pm --all --replicas=0

# 2. Patch RabbitMQ cluster to 0 replicas
echo "🐇 [2/2] Scaling down RabbitMQ cluster to 0..."
kubectl patch rabbitmqcluster gdc-pm-rabbitmq -n gdc-pm --type merge -p '{"spec":{"replicas":0}}'

echo "=================================================="
echo "✅ GDC-PM Quiesced to $0.00 compute charges."
echo "=================================================="
