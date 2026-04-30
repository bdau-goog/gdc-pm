#!/bin/bash
# =============================================================================
# GDC-PM — Import Pre-Existing Resources into Terraform State
# =============================================================================
# Run this when deploying into a GCP project that was partially provisioned
# by the old standalone gdc-pm/terraform/ before integrating with bdau-basic-vpc.
#
# It attempts to import each known resource into the appropriate Terraform
# state file. Errors on "resource not found" are silently skipped.
#
# Usage:
#   From ~/bdau-basic-vpc/scenarios/gdc-pm (for foundation imports):
#     bash ~/gdc-pm/scripts/terraform-import-existing.sh foundation
#
#   From ~/gdc-pm/terraform (for workload layer imports):
#     bash ~/gdc-pm/scripts/terraform-import-existing.sh workload
#
# =============================================================================

set -uo pipefail

MODE="${1:-foundation}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../terraform"

PROJECT_ID="${PROJECT_ID:-$(grep 'project_id' "${TF_DIR}/terraform.tfvars" 2>/dev/null | awk -F'"' '{print $2}' || grep 'project_id' "${PWD}/terraform.tfvars" 2>/dev/null | awk -F'=' '{print $2}' | tr -d ' "' || true)}"
REGION="${REGION:-us-east4}"

if [ -z "${PROJECT_ID:-}" ]; then
    echo "❌ Could not determine project_id. Set PROJECT_ID env var or ensure terraform.tfvars is present."
    exit 1
fi

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

echo ""
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo -e "${BOLD}  GDC-PM — Terraform Import (${MODE} layer)${RESET}"
echo -e "${BOLD}  Project: ${CYAN}${PROJECT_ID}${RESET}  Region: ${CYAN}${REGION}${RESET}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
echo ""

# Helper: run import, skip if resource not found or already in state
do_import() {
    local tf_addr="$1"
    local import_id="$2"
    local label="${3:-}"

    echo -e "${BOLD}▶ Importing${RESET} ${label:-${tf_addr}}"
    echo -e "${DIM}  Address: ${tf_addr}${RESET}"
    echo -e "${DIM}  ID:      ${import_id}${RESET}"

    OUT=$(terraform import "${tf_addr}" "${import_id}" 2>&1)
    STATUS=$?

    if [ $STATUS -eq 0 ]; then
        echo -e "${GREEN}  ✅ Imported successfully.${RESET}"
    elif echo "$OUT" | grep -q -i "already managed\|already exists in state"; then
        echo -e "${GREEN}  ✅ Already in state — skipping.${RESET}"
    elif echo "$OUT" | grep -q -i "not found\|404\|does not exist"; then
        echo -e "${YELLOW}  ⚠️  Resource not found in GCP — skipping (may not have been created yet).${RESET}"
    else
        echo -e "${YELLOW}  ⚠️  Import returned non-zero status. Output:${RESET}"
        echo -e "${DIM}${OUT}${RESET}"
        echo -e "${DIM}  Continuing anyway...${RESET}"
    fi
    echo ""
}

# ── FOUNDATION LAYER IMPORTS ──────────────────────────────────────────────────
if [ "${MODE}" == "foundation" ]; then
    echo -e "${BOLD}Importing resources into: bdau-basic-vpc/scenarios/gdc-pm${RESET}"
    echo ""

    # 1. GCP Project
    do_import \
        "module.vpc_foundation.google_project.project" \
        "${PROJECT_ID}" \
        "GCP Project (${PROJECT_ID})"

    # 2. Artifact Registry — gdc-models
    do_import \
        'module.vpc_foundation.google_artifact_registry_repository.repo["gdc-models"]' \
        "projects/${PROJECT_ID}/locations/${REGION}/repositories/gdc-models" \
        "Artifact Registry: gdc-models"

    # 3. Service Account — ml-pipeline-sa
    do_import \
        'module.vpc_foundation.google_service_account.sa["ml-pipeline-sa"]' \
        "projects/${PROJECT_ID}/serviceAccounts/ml-pipeline-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        "Service Account: ml-pipeline-sa"

    # 4. Service Account — gdc-edge-sa (may not exist yet)
    do_import \
        'module.vpc_foundation.google_service_account.sa["gdc-edge-sa"]' \
        "projects/${PROJECT_ID}/serviceAccounts/gdc-edge-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
        "Service Account: gdc-edge-sa"

    echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
    echo -e "${GREEN}${BOLD}  ✅ Foundation imports complete. Run: terraform apply${RESET}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
    echo ""
fi

# ── WORKLOAD LAYER IMPORTS ────────────────────────────────────────────────────
if [ "${MODE}" == "workload" ]; then
    echo -e "${BOLD}Importing resources into: gdc-pm/terraform${RESET}"
    echo ""

    # 1. BigQuery Dataset
    do_import \
        "google_bigquery_dataset.grid_reliability" \
        "${PROJECT_ID}:grid_reliability_gold" \
        "BigQuery Dataset: grid_reliability_gold"

    # 2. BigQuery Table (correct format: project/dataset/table)
    do_import \
        "google_bigquery_table.telemetry_raw" \
        "${PROJECT_ID}/grid_reliability_gold/telemetry_raw" \
        "BigQuery Table: telemetry_raw"

    # 3. GCS Model Bucket
    do_import \
        "google_storage_bucket.model_artifacts" \
        "${PROJECT_ID}-models" \
        "GCS Bucket: ${PROJECT_ID}-models"

    # 4. GKE Autopilot Cluster (if it already exists from an interrupted apply)
    do_import \
        "google_container_cluster.gdc_edge_sim" \
        "${REGION}/gdc-edge-simulation" \
        "GKE Cluster: gdc-edge-simulation"

    # ── Remove orphaned state entries from old standalone terraform ───────────
    # These resources were managed by the old gdc-pm/terraform/ before integrating
    # with bdau-basic-vpc. They are now managed by the foundation layer and must
    # be removed from the workload state (NOT from GCP) to prevent accidental
    # deletion of APIs, IAM bindings, and service accounts.
    echo -e "${BOLD}🧹 Removing orphaned state entries from old standalone Terraform...${RESET}"
    ORPHANS=(
        "google_service_account.ml_pipeline_sa"
        "google_artifact_registry_repository.model_repo"
        'google_project_iam_member.ml_sa_roles["roles/aiplatform.user"]'
        'google_project_iam_member.ml_sa_roles["roles/bigquery.dataEditor"]'
        'google_project_iam_member.ml_sa_roles["roles/bigquery.jobUser"]'
        'google_project_iam_member.ml_sa_roles["roles/storage.admin"]'
        'google_project_service.apis["aiplatform.googleapis.com"]'
        'google_project_service.apis["artifactregistry.googleapis.com"]'
        'google_project_service.apis["bigquery.googleapis.com"]'
        'google_project_service.apis["bigqueryconnection.googleapis.com"]'
        'google_project_service.apis["cloudresourcemanager.googleapis.com"]'
        'google_project_service.apis["compute.googleapis.com"]'
        'google_project_service.apis["container.googleapis.com"]'
        'google_project_service.apis["iam.googleapis.com"]'
        'google_project_service.apis["storage.googleapis.com"]'
    )
    for orphan in "${ORPHANS[@]}"; do
        OUT=$(terraform state rm "$orphan" 2>&1)
        if echo "$OUT" | grep -q "Successfully removed"; then
            echo -e "${GREEN}  ✅ Removed: ${orphan}${RESET}"
        elif echo "$OUT" | grep -q "not found\|No matching"; then
            : # already gone — silent skip
        else
            echo -e "${DIM}  (skipped: ${orphan})${RESET}"
        fi
    done
    echo ""

    echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
    echo -e "${GREEN}${BOLD}  ✅ Workload imports complete. Run: terraform apply${RESET}"
    echo -e "${DIM}  Expected plan: 3 to add, 0 to change, 0 to destroy${RESET}"
    echo -e "${BOLD}═══════════════════════════════════════════════════════════════════${RESET}"
    echo ""
fi
