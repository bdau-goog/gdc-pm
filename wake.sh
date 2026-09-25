#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"
source "${SCRIPT_DIR}/.env"

echo "=================================================="
echo "🚀 Waking GDC-PM Demo Cluster (gdc-edge-simulation)"
echo "• Project   : ${GOOGLE_CLOUD_PROJECT}"
echo "• Namespace : gdc-pm"
echo "=================================================="

# 1. Scale up core deployments only (leaves ollama at 0 to avoid $0.35/hr GPU billing)
echo "📦 [1/3] Scaling up core deployments..."
kubectl scale deployment alloydb-omni event-processor fault-trigger-ui inference-api telemetry-simulator -n gdc-pm --replicas=1

# 2. Restore RabbitMQ StatefulSet to 1 replica
echo "🐇 [2/3] Restoring RabbitMQ cluster to 1 replica..."
kubectl patch rabbitmqcluster gdc-pm-rabbitmq -n gdc-pm --type merge -p '{"spec":{"replicas":1}}'

# 3. Wait for core workloads in gdc-pm to become Ready
echo "⏳ [3/3] Waiting for workloads to roll out..."
kubectl -n gdc-pm rollout status deploy/alloydb-omni --timeout=300s
kubectl -n gdc-pm rollout status deploy/event-processor --timeout=300s
kubectl -n gdc-pm rollout status deploy/fault-trigger-ui --timeout=300s
kubectl -n gdc-pm rollout status deploy/inference-api --timeout=300s
kubectl -n gdc-pm rollout status deploy/telemetry-simulator --timeout=300s

echo "=== Workloads Ready ==="
kubectl get pods -n gdc-pm -o wide

echo "=================================================="
echo "🎉 GDC-PM DEMO IS AWAKE & READY!"
echo "• Public LoadBalancer IP : http://34.72.142.23/"
echo "• Demo DNS Hostname     : http://gdc-pm.bdau.io/"
echo "=================================================="
