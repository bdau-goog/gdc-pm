#!/usr/bin/env bash
# =============================================================================
# gpu-start.sh — Start GPU node pool + Ollama LLM (gemma4:latest on NVIDIA L4)
#
# Usage: ./scripts/gpu-start.sh
#
# What this does:
#   1. Resizes the GKE gpu-pool from 0 → 1 node in us-east1-b ONLY
#      gpu-pool is single-zone (us-east1-b) — provisions exactly 1 L4 VM
#      This is the same zone as the ollama-models-pvc PV — no zone mismatch.
#   2. Scales the Ollama deployment to 1 replica
#   3. Waits until the pod is Running and the model is responding (~15-20 min)
#
# NOTE: This is a standard GKE cluster (NOT Autopilot). The GPU node pool must
# be explicitly resized before the pod can schedule. This script does both.
#
# Cost: ~$1.09/hr (1 × g2-standard-8 L4 node in us-east1-b) while running.
#
# When done: ./scripts/gpu-stop.sh (ALWAYS pair — stops billing)
# =============================================================================
set -e

NAMESPACE="gdc-pm"
DEPLOYMENT="ollama"
CLUSTER="gdc-edge-simulation"
NODE_POOL="gpu-pool"
REGION="us-east1"
PROJECT="${GOOGLE_CLOUD_PROJECT:-gdc-pm-v2}"
TIMEOUT=1800   # 30 minutes max wait

echo ""
echo "┌─────────────────────────────────────────────────────────────┐"
echo "│  🚀 GDC-PM GPU Start — Ollama on NVIDIA L4 (us-east1-b)    │"
echo "│  Cost: ~\$1.09/hr (1 node) · ALWAYS run gpu-stop.sh when done  │"
echo "└─────────────────────────────────────────────────────────────┘"
echo ""

# ── Step 1: Resize GPU node pool if at 0 ────────────────────────────────────
GPU_NODES=$(kubectl get nodes --no-headers 2>/dev/null | grep -c "g2-standard" || echo "0")
if [ "${GPU_NODES}" -gt "0" ]; then
    echo "✅ GPU nodes already running (${GPU_NODES} node(s)). Skipping resize."
else
    echo "📤 Resizing ${NODE_POOL} to 1 node in us-east1-b (~$1.09/hr)..."
    echo "   This provisions 1 NVIDIA L4 VM. Takes ~2-3 min."
    gcloud container clusters resize ${CLUSTER} \
        --node-pool ${NODE_POOL} \
        --num-nodes 1 \
        --region ${REGION} \
        --project ${PROJECT} \
        --quiet
    echo "✅ Node pool resize requested. Waiting for nodes to be Ready..."

    # Wait for GPU nodes to join the cluster
    WAIT_START=$(date +%s)
    while true; do
        ELAPSED=$(( $(date +%s) - WAIT_START ))
        if [ ${ELAPSED} -gt 300 ]; then
            echo "⚠️  Nodes taking >5 min to be Ready. Continuing anyway..."
            break
        fi
        READY=$(kubectl get nodes --no-headers 2>/dev/null | grep "g2-standard" | grep "Ready" | wc -l || echo "0")
        if [ "${READY}" -gt "0" ]; then
            echo "✅ ${READY} GPU node(s) Ready."
            break
        fi
        echo "   Waiting for GPU nodes... (${ELAPSED}s)"
        sleep 15
    done
fi

echo ""

# ── Step 2: Scale Ollama deployment ─────────────────────────────────────────
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
