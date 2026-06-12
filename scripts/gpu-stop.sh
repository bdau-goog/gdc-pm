#!/usr/bin/env bash
# =============================================================================
# gpu-stop.sh — Stop Ollama AND scale GPU node pool to 0 (stops all billing)
#
# Usage: ./scripts/gpu-stop.sh
#
# What this does:
#   1. Scales the Ollama deployment to 0 replicas
#   2. Resizes the GKE gpu-pool to 0 nodes (terminates the L4 VMs — stops billing)
#   3. The PVC (gemma model cache) is RETAINED for faster next startup
#
# NOTE: This is a standard GKE cluster (NOT Autopilot). Scaling the deployment
# to 0 does NOT automatically remove the GPU nodes — you must explicitly resize
# the node pool. This script does both.
#
# Billing stops when node pool reaches 0 nodes (~2-3 min after this script).
# =============================================================================
set -e

NAMESPACE="gdc-pm"
DEPLOYMENT="ollama"
CLUSTER="gdc-edge-simulation"
NODE_POOL="gpu-pool"
REGION="us-east1"
PROJECT="${GOOGLE_CLOUD_PROJECT:-gdc-pm-v2}"

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  🛑 GDC-PM GPU Stop — shutting down Ollama + GPU nodes     │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

# ── Step 1: Scale Ollama deployment to 0 ─────────────────────────────────────
CURRENT=$(kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
if [ "${CURRENT}" == "0" ]; then
    echo "✅ Ollama deployment already at 0 replicas."
else
    echo "📥 Scaling Ollama deployment to 0..."
    kubectl scale deployment ${DEPLOYMENT} -n ${NAMESPACE} --replicas=0
    kubectl wait --for=delete pod -l app=${DEPLOYMENT} -n ${NAMESPACE} --timeout=120s 2>/dev/null || true
    echo "✅ Ollama pod terminated."
fi

# ── Step 2: Check current GPU node count ─────────────────────────────────────
GPU_NODES=$(kubectl get nodes --no-headers 2>/dev/null | grep -c "g2-standard" || echo "0")
if [ "${GPU_NODES}" -eq "0" ]; then
    echo "✅ GPU node pool already at 0 nodes. No billing to stop."
    exit 0
fi

echo ""
echo "📥 Resizing ${NODE_POOL} to 0 nodes (terminates ${GPU_NODES} GPU VM(s))..."
echo "   This stops all GPU billing. Takes ~2-3 minutes."
gcloud container clusters resize ${CLUSTER} \
    --node-pool ${NODE_POOL} \
    --num-nodes 0 \
    --region ${REGION} \
    --project ${PROJECT} \
    --quiet

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  ✅ GPU nodes terminated. Billing stopped.                  │"
echo "│     PVC (model cache) retained for faster next startup.     │"
echo "│  To restart: ./scripts/gpu-start.sh                        │"
echo "└─────────────────────────────────────────────────────────────┘"
