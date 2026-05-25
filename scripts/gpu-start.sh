#!/usr/bin/env bash
# =============================================================================
# gpu-start.sh — Start the Ollama LLM (gemma:27b) GPU node
#
# Usage: ./scripts/gpu-start.sh
#
# What this does:
#   1. Scales the Ollama deployment to 1 replica
#   2. GKE Autopilot provisions an NVIDIA L4 GPU node in us-central1-b (~10-15 min)
#   3. The init container checks if gemma:27b is on the PVC — if not, pulls it (~10 min)
#   4. Watches until the pod is Running and the model is responding
#
# Estimated startup time:
#   - If model already on PVC: ~15 min (node provisioning)
#   - First time or after PVC delete: ~25 min (node + model pull)
#
# Cost: ~$0.65/hr while the L4 GPU node is running
# =============================================================================
set -e

NAMESPACE="gdc-pm"
DEPLOYMENT="ollama"
TIMEOUT=1800   # 30 minutes max wait

echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│  🚀 GDC-PM GPU Start — gemma:27b on NVIDIA L4          │"
echo "│  Zone: us-central1-b  ·  Cost: ~\$0.65/hr              │"
echo "└─────────────────────────────────────────────────────────┘"
echo ""

# Check current state
CURRENT=$(kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
if [ "${CURRENT}" == "1" ]; then
    # Already scaled up — check if running
    STATUS=$(kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} --no-headers 2>/dev/null | awk '{print $3}' | head -1)
    if [ "${STATUS}" == "Running" ]; then
        echo "✅ Ollama is already running."
        kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} --no-headers
        echo ""
        echo "Test: curl -s http://ollama.${NAMESPACE}.svc.cluster.local:11434/api/tags"
        exit 0
    fi
    echo "⏳ Ollama is already at replicas=1 but not yet Running (status: ${STATUS})."
    echo "   Watching for it to come up..."
else
    echo "📤 Scaling Ollama deployment to 1..."
    kubectl scale deployment ${DEPLOYMENT} -n ${NAMESPACE} --replicas=1
    echo "✅ Scale command sent."
fi

echo ""
echo "⏳ Waiting for L4 GPU node provisioning and pod startup..."
echo "   (This takes 10-20 minutes. GKE Autopilot is provisioning the node now.)"
echo ""

START=$(date +%s)
LAST_STATUS=""
while true; do
    ELAPSED=$(( $(date +%s) - START ))
    if [ ${ELAPSED} -gt ${TIMEOUT} ]; then
        echo ""
        echo "❌ Timeout after ${TIMEOUT}s. Check events:"
        kubectl get events -n ${NAMESPACE} --sort-by=.lastTimestamp | grep -i "ollama" | tail -10
        exit 1
    fi

    POD=$(kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} --no-headers 2>/dev/null | head -1)
    STATUS=$(echo "${POD}" | awk '{print $3}')
    NODE=$(echo "${POD}" | awk '{print $7}')

    if [ "${STATUS}" != "${LAST_STATUS}" ]; then
        MINS=$(( ELAPSED / 60 ))
        SECS=$(( ELAPSED % 60 ))
        echo "[${MINS}m${SECS}s] Pod status: ${STATUS} | Node: ${NODE:-pending}"
        LAST_STATUS="${STATUS}"
    fi

    if [ "${STATUS}" == "Running" ]; then
        # Verify model is actually loaded
        POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
        MODEL_OK=$(kubectl exec -n ${NAMESPACE} ${POD_NAME} -- curl -sf http://localhost:11434/api/tags 2>/dev/null | grep -c "gemma4" || echo "0")
        if [ "${MODEL_OK}" -gt "0" ]; then
            echo ""
            echo "┌─────────────────────────────────────────────────────────┐"
            echo "│  ✅ Ollama is READY — gemma:27b loaded and responding  │"
            echo "└─────────────────────────────────────────────────────────┘"
            echo ""
            kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} --no-headers
            echo ""
            echo "The GDC-PM UI agent chat will now use real Gemma responses."
            exit 0
        else
            if [ "${LAST_STATUS}" != "Running-loading" ]; then
                echo "   Pod is Running, waiting for model to load..."
                LAST_STATUS="Running-loading"
            fi
        fi
    fi

    sleep 15
done
