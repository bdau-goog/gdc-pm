#!/usr/bin/env bash
# =============================================================================
# gpu-start.sh — Start Ollama LLM (gemma4:latest on NVIDIA T4, Autopilot)
#
# Usage: ./scripts/gpu-start.sh
#
# What this does:
#   1. Scales the Ollama deployment to 1 replica
#   2. Autopilot automatically provisions a T4 GPU node to satisfy the request
#   3. Waits until the pod is Running and the model is responding (~15-20 min)
#
# NOTE: This is a GKE Autopilot cluster. Node provisioning is automatic —
# no explicit node-pool resize needed. Billing starts when the GPU pod schedules.
#
# Cost: ~$0.35/hr (1 × T4 GPU node via Autopilot) while running.
#
# When done: ./scripts/gpu-stop.sh (ALWAYS pair — stops billing)
# =============================================================================
set -e

NAMESPACE="gdc-pm"
DEPLOYMENT="ollama"
TIMEOUT=1800   # 30 minutes max wait

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  🚀 GDC-PM GPU Start — Ollama on NVIDIA T4 (Autopilot)     │"
echo "│  Cost: ~\$0.35/hr · ALWAYS run gpu-stop.sh when done        │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

# ── Step 1: Scale Ollama deployment ─────────────────────────────────────────
# Autopilot provisions the T4 GPU node automatically when the pod is scheduled.
CURRENT=$(kubectl get deployment ${DEPLOYMENT} -n ${NAMESPACE} -o jsonpath='{.spec.replicas}' 2>/dev/null || echo "0")
if [ "${CURRENT}" == "1" ]; then
    STATUS=$(kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} --no-headers 2>/dev/null | awk '{print $3}' | head -1)
    if [ "${STATUS}" == "Running" ]; then
        echo "✅ Ollama is already running."
        kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} --no-headers
        exit 0
    fi
    echo "⏳ Ollama already at replicas=1 (status: ${STATUS}). Watching..."
else
    echo "📤 Scaling Ollama deployment to 1..."
    kubectl scale deployment ${DEPLOYMENT} -n ${NAMESPACE} --replicas=1
    echo "✅ Scale command sent."
fi

echo ""
echo "⏳ Waiting for Ollama pod to start (model load takes ~15-20 min total)..."
echo ""

START=$(date +%s)
LAST_STATUS=""
while true; do
    ELAPSED=$(( $(date +%s) - START ))
    if [ ${ELAPSED} -gt ${TIMEOUT} ]; then
        echo ""
        echo "❌ Timeout after ${TIMEOUT}s."
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
        POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
        MODEL_OK=$(kubectl exec -n ${NAMESPACE} ${POD_NAME} -- curl -sf http://localhost:11434/api/tags 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('models',[])))" 2>/dev/null || echo "0")
        if [ "${MODEL_OK}" -gt "0" ]; then
            echo ""
            echo "┌─────────────────────────────────────────────────────────────┐"
            echo "│  ✅ Ollama is READY — model loaded and responding           │"
            echo "│  ⚠️  Remember: run ./scripts/gpu-stop.sh when finished     │"
            echo "└─────────────────────────────────────────────────────────────┘"
            kubectl get pods -n ${NAMESPACE} -l app=${DEPLOYMENT} --no-headers
            exit 0
        else
            if [ "${LAST_STATUS}" != "Running-loading" ]; then
                echo "   Pod Running, waiting for model to load..."
                LAST_STATUS="Running-loading"
            fi
        fi
    fi

    sleep 15
done
