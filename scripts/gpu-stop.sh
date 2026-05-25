#!/usr/bin/env bash
# =============================================================================
# gpu-stop.sh — Stop the Ollama LLM GPU node (saves ~$0.65/hr)
#
# Usage: ./scripts/gpu-stop.sh
#
# What this does:
#   1. Scales the Ollama deployment to 0 replicas
#   2. GKE Autopilot deprovisions the L4 GPU node (~5 min)
#   3. The PVC (50Gi, contains the gemma:27b model) is RETAINED
#      — next gpu-start.sh will reuse the cached model (faster startup)
#
# NOTE: The GDC-PM UI will show "⛔ LLM offline — rule-based mode"
# in the agent panel header automatically when Ollama is down.
# =============================================================================
set -e

NAMESPACE="gdc-pm"
DEPLOYMENT="ollama"

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│  🛑 GDC-PM GPU Stop — shutting down Ollama / L4 node   │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

# Check current state
CURRENT=$(kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
if [ "${CURRENT}" == "0" ]; then
    echo "✅ Ollama is already stopped (replicas=0). Nothing to do."
    exit 0
fi

echo "📥 Scaling Ollama deployment to 0..."
kubectl scale deployment ${DEPLOYMENT} -n ${NAMESPACE} --replicas=0
echo "✅ Scale command sent."
echo ""
echo "⏳ Waiting for pod to terminate..."
kubectl wait --for=delete pod -l app=${DEPLOYMENT} -n ${NAMESPACE} --timeout=120s 2>/dev/null || true

# Verify
PODS=$(kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} --no-headers 2>/dev/null | wc -l)
if [ "${PODS}" -eq "0" ]; then
    echo ""
    echo "┌─────────────────────────────────────────────────────────┐"
    echo "│  ✅ Ollama stopped. L4 GPU node deprovisioning now.     │"
    echo "│     PVC (model cache) retained for faster next startup. │"
    echo "│     Savings: ~\$0.65/hr while stopped.                  │"
    echo "└─────────────────────────────────────────────────────────┘"
else
    echo "⚠️  Pod still showing. Check manually:"
    kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT}
fi
echo ""
echo "To restart: ./scripts/gpu-start.sh"
