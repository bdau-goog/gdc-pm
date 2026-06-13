#!/usr/bin/env bash
# =============================================================================
# gpu-stop.sh — Stop Ollama LLM (scales to 0; Autopilot deprovisions T4 node)
#
# Usage: ./scripts/gpu-stop.sh
#
# What this does:
#   1. Scales the Ollama deployment to 0 replicas
#   2. Autopilot automatically deprovisions the T4 GPU node (~2-3 min)
#   3. The PVC (model cache) is RETAINED for faster next startup
#
# NOTE: This is a GKE Autopilot cluster. No explicit node-pool resize needed —
# Autopilot terminates the GPU node automatically once the pod is gone.
#
# Billing stops when Autopilot removes the T4 node (~2-3 min after this script).
# =============================================================================
set -e

NAMESPACE="gdc-pm"
DEPLOYMENT="ollama"

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  🛑 GDC-PM GPU Stop — scaling Ollama to 0 (Autopilot)      │"
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

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  ✅ Ollama scaled to 0. Autopilot will deprovision the T4   │"
echo "│     GPU node automatically (~2-3 min) — billing stops then. │"
echo "│     PVC (model cache) retained for faster next startup.     │"
echo "│  To restart: ./scripts/gpu-start.sh                        │"
echo "└─────────────────────────────────────────────────────────────┘"
