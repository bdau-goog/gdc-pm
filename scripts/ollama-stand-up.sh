#!/bin/bash
# ============================================================================
# Ollama Stand-Up — manually scale Ollama deployment to 1 replica.
# Run this at the start of your day to enable Gemma 4:27b LLM inference.
#
# GKE Cluster Autoscaler will provision a new L4 GPU node (~2-3 minutes).
# Ollama will pull gemma4:27b from the PVC (instant if already cached) and
# become ready once the readiness probe passes.
#
# Usage:
#   ./scripts/ollama-stand-up.sh
#
# AUTOMATED ALTERNATIVE:
#   The CronJobs in gke/ollama/k8s/ollama-scheduler.yaml (already applied to
#   the cluster) will run this automatically at 6 AM UTC Mon-Fri.
#   However, they require the RBAC Role/RoleBinding to be applied first by a
#   project admin with container.roles.create IAM permission:
#
#     kubectl apply -f gke/ollama/k8s/ollama-scheduler.yaml
#
#   To grant the required IAM permission (run as project owner):
#     gcloud projects add-iam-policy-binding gdc-pm-v2 \
#       --member="serviceAccount:dev-workstation-sa@gdc-pm-v2.iam.gserviceaccount.com" \
#       --role="roles/container.developer"
# ============================================================================
set -e

NAMESPACE="gdc-pm"
DEPLOYMENT="ollama"

echo "$(date -u '+%Y-%m-%d %H:%M:%S UTC') — Standing UP ollama deployment"

kubectl scale deployment "${DEPLOYMENT}" -n "${NAMESPACE}" --replicas=1

echo "✅ ollama scaled to 1 replica."
echo "   GKE Autoscaler will provision an L4 GPU node in ~2-3 minutes."
echo "   gemma4:27b will be ready once the readiness probe passes."
echo ""
echo "   Monitor progress:"
echo "   kubectl get pods -n ${NAMESPACE} -l app=ollama -w"
