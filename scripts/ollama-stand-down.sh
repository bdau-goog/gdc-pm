#!/bin/bash
# ============================================================================
# Ollama Stand-Down — manually scale Ollama deployment to 0 replicas.
# Run this at the end of your day to stop L4 GPU billing.
#
# GKE Cluster Autoscaler will delete the L4 GPU node ~10 minutes after
# no pods are requesting nvidia.com/gpu resources (billing stops then).
#
# COST IMPACT: L4 GPU node costs ~$0.60-$0.70/hr on GKE.
#   Running only during working hours (Mon-Fri, ~9h/day) vs 24/7 reduces
#   monthly GPU cost from ~$500 to ~$110 (~78% savings).
#
# Usage:
#   ./scripts/ollama-stand-down.sh
#
# AUTOMATED ALTERNATIVE:
#   The CronJob ollama-stand-down in gke/ollama/k8s/ollama-scheduler.yaml
#   runs this automatically at 6 PM UTC every day.
#   See ollama-stand-up.sh for instructions on enabling automated scheduling.
# ============================================================================
set -e

NAMESPACE="gdc-pm"
DEPLOYMENT="ollama"

echo "$(date -u '+%Y-%m-%d %H:%M:%S UTC') — Standing DOWN ollama deployment"

kubectl scale deployment "${DEPLOYMENT}" -n "${NAMESPACE}" --replicas=0

echo "✅ ollama scaled to 0 replicas."
echo "   GKE Autoscaler will remove the L4 GPU node in ~10 minutes."
echo "   L4 GPU billing stops when the node is deleted."
echo ""
echo "   Note: The model weights remain on the PVC and will be available"
echo "   instantly when the deployment is scaled back up."
