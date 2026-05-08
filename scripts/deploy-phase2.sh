#!/bin/bash
# =============================================================================
# GDC-PM — Phase 2 Deployment Script
# Autonomous Edge Command Center (RAG + 3-Tab UI + Financial Ledger)
#
# Usage:
#   cd /home/brian/gdc-pm
#   bash scripts/deploy-phase2.sh
#
# Prerequisites:
#   - gcloud auth login && gcloud auth configure-docker us-central1-docker.pkg.dev
#   - kubectl context set to gdc-edge-simulation
#   - docker daemon running
#
# Token-conservation design:
#   - docker build --quiet (SHA only, not layer logs)
#   - docker push --quiet (no progress bars)
#   - All output redirected to /tmp/deploy-phase2-*.log
#   - Only tails on failure; prints ✅/❌ summary table at end
# =============================================================================

set -uo pipefail

PROJECT_ID="gdc-pm-v2"
REGION="us-central1"
REGISTRY="${REGION}-docker.pkg.dev/${PROJECT_ID}/gdc-models"
NAMESPACE="gdc-pm"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="/tmp/deploy-phase2-logs"
mkdir -p "${LOG_DIR}"

# ── Status tracking ────────────────────────────────────────────────────────────
declare -A STEP_STATUS
STEP_STATUS=(
  [db_migrate]="pending"
  [build_ui]="pending"
  [build_processor]="pending"
  [build_inference]="pending"
  [apply_manifests]="pending"
  [ollama]="pending"
  [rag_ingest]="pending"
)

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
BOLD='\033[1m'; RESET='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${RESET}"; }
fail() { echo -e "${RED}❌ $1${RESET}"; }
info() { echo -e "${BOLD}── $1${RESET}"; }
warn() { echo -e "${YELLOW}⚠️  $1${RESET}"; }

# ── Helper: build + push with quiet flags ─────────────────────────────────────
build_and_push() {
  local name="$1"
  local dir="${ROOT_DIR}/gke/${name}"
  local image="${REGISTRY}/${name}:latest"
  local log="${LOG_DIR}/build-${name}.log"

  info "Building ${name}..."
  docker build --quiet -t "${image}" "${dir}" > "${log}" 2>&1 \
    && ok "Build OK: ${name}" \
    || { fail "Build FAILED: ${name}"; tail -25 "${log}"; return 1; }

  info "Pushing ${name}..."
  docker push --quiet "${image}" >> "${log}" 2>&1 \
    && ok "Push OK: ${name}" \
    || { fail "Push FAILED: ${name}"; tail -10 "${log}"; return 1; }
}

# ── Step 1: AlloyDB Schema Migration ─────────────────────────────────────────
info "Step 1: AlloyDB schema migration"
ALLOYDB_POD=$(kubectl get pod -n "${NAMESPACE}" -l app=alloydb-omni \
  --no-headers -o custom-columns=':metadata.name' 2>/dev/null | head -1)

if [[ -z "${ALLOYDB_POD}" ]]; then
  fail "AlloyDB pod not found — is the cluster accessible?"
  STEP_STATUS[db_migrate]="FAILED"
else
  kubectl exec -n "${NAMESPACE}" "${ALLOYDB_POD}" -- \
    psql -U postgres -d grid_reliability -q -c "
      CREATE EXTENSION IF NOT EXISTS vector;
      CREATE TABLE IF NOT EXISTS rag_documents (
        id SERIAL PRIMARY KEY,
        asset_class TEXT NOT NULL,
        doc_title TEXT NOT NULL,
        content TEXT NOT NULL,
        embedding vector(384)
      );
      CREATE INDEX IF NOT EXISTS idx_rag_embedding
        ON rag_documents USING hnsw (embedding vector_cosine_ops);
      ALTER TABLE telemetry_events
        ADD COLUMN IF NOT EXISTS cost_incurred NUMERIC DEFAULT 0;
      SELECT 'migration_complete' AS status;
    " 2>&1 | tail -3 \
    && { ok "AlloyDB migration applied"; STEP_STATUS[db_migrate]="OK"; } \
    || { fail "AlloyDB migration failed"; STEP_STATUS[db_migrate]="FAILED"; }
fi

# ── Step 2: Build & Push fault-trigger-ui ─────────────────────────────────────
info "Step 2: fault-trigger-ui"
if build_and_push "fault-trigger-ui"; then
  STEP_STATUS[build_ui]="OK"
else
  STEP_STATUS[build_ui]="FAILED"
fi

# ── Step 3: Build & Push event-processor ──────────────────────────────────────
info "Step 3: event-processor"
if build_and_push "event-processor"; then
  STEP_STATUS[build_processor]="OK"
else
  STEP_STATUS[build_processor]="FAILED"
fi

# ── Step 4: Build & Push inference-api ────────────────────────────────────────
info "Step 4: inference-api"
if build_and_push "inference-api"; then
  STEP_STATUS[build_inference]="OK"
else
  STEP_STATUS[build_inference]="FAILED"
fi

# ── Step 5: Apply updated manifests ───────────────────────────────────────────
info "Step 5: Apply Kubernetes manifests"
MANIFEST_LOG="${LOG_DIR}/manifests.log"

# Restart pods to pick up new :latest images (imagePullPolicy: Always assumed)
for svc in fault-trigger-ui event-processor inference-api; do
  IMAGE="${REGISTRY}/${svc}:latest"
  MANIFEST="${ROOT_DIR}/gke/${svc}/k8s/${svc}.yaml"
  if [[ -f "${MANIFEST}" ]]; then
    # Substitute placeholder and apply
    sed "s|GCR_IMAGE_PLACEHOLDER|${IMAGE}|g" "${MANIFEST}" \
      | kubectl apply -f - --output=name >> "${MANIFEST_LOG}" 2>&1
  fi
  kubectl rollout restart deployment/"${svc}" -n "${NAMESPACE}" >> "${MANIFEST_LOG}" 2>&1
done

# Wait for rollouts
ALL_ROLLED=true
for svc in fault-trigger-ui event-processor inference-api; do
  if kubectl rollout status deployment/"${svc}" -n "${NAMESPACE}" --timeout=120s \
       >> "${MANIFEST_LOG}" 2>&1; then
    ok "Rollout OK: ${svc}"
  else
    fail "Rollout FAILED: ${svc}"; tail -10 "${MANIFEST_LOG}"; ALL_ROLLED=false
  fi
done
$ALL_ROLLED && STEP_STATUS[apply_manifests]="OK" || STEP_STATUS[apply_manifests]="FAILED"

# ── Step 6: Deploy Ollama ──────────────────────────────────────────────────────
info "Step 6: Deploy Ollama (GPU — Autopilot will provision GPU node, ~5 min)"
OLLAMA_LOG="${LOG_DIR}/ollama.log"
kubectl apply -f "${ROOT_DIR}/gke/ollama/k8s/ollama.yaml" --output=name \
  >> "${OLLAMA_LOG}" 2>&1 \
  && { ok "Ollama manifest applied — GPU node provisioning in background"; STEP_STATUS[ollama]="OK"; } \
  || { fail "Ollama apply failed"; tail -10 "${OLLAMA_LOG}"; STEP_STATUS[ollama]="FAILED"; }
warn "Ollama readiness takes ~5-10 min (GPU node provision + gemma:2b download on first run)"

# ── Step 7: RAG Document Ingestion ────────────────────────────────────────────
info "Step 7: RAG document ingestion"
if [[ "${STEP_STATUS[db_migrate]}" != "OK" ]]; then
  warn "Skipping RAG ingestion — DB migration must succeed first"
  STEP_STATUS[rag_ingest]="SKIPPED"
else
  RAG_LOG="${LOG_DIR}/rag-ingest.log"
  # Apply as a Kubernetes Job so no local sentence-transformers install needed
  cat <<EOF | kubectl apply -f - --output=name >> "${RAG_LOG}" 2>&1
apiVersion: batch/v1
kind: Job
metadata:
  name: rag-ingest-$(date +%s)
  namespace: ${NAMESPACE}
spec:
  ttlSecondsAfterFinished: 600
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: ingest
          image: python:3.11-slim
          command:
            - sh
            - -c
            - |
              pip install --quiet psycopg2-binary sentence-transformers > /dev/null 2>&1
              echo "Ingesting manuals..."
              python /scripts/ingest_manuals.py && echo "✅ Ingestion complete"
          env:
            - name: PGHOST
              value: alloydb-omni.${NAMESPACE}.svc.cluster.local
            - name: PGUSER
              valueFrom:
                secretKeyRef:
                  name: alloydb-secret
                  key: username
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: alloydb-secret
                  key: password
            - name: PGDATABASE
              value: grid_reliability
          volumeMounts:
            - name: scripts
              mountPath: /scripts
            - name: docs
              mountPath: /docs
      volumes:
        - name: scripts
          configMap:
            name: rag-ingest-script
        - name: docs
          configMap:
            name: rag-source-docs
EOF
  warn "RAG Job submitted — requires ConfigMaps for script + docs."
  warn "Preferred alternative: kubectl port-forward svc/alloydb-omni 5432:5432 and run locally."
  STEP_STATUS[rag_ingest]="SUBMITTED_JOB"
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}════════ Phase 2 Deployment Summary ════════${RESET}"
printf "  %-25s %s\n" "Step" "Status"
printf "  %-25s %s\n" "─────────────────────────" "──────"
for step in db_migrate build_ui build_processor build_inference apply_manifests ollama rag_ingest; do
  status="${STEP_STATUS[$step]}"
  if   [[ "$status" == "OK" ]];      then icon="${GREEN}✅${RESET}"
  elif [[ "$status" == "FAILED" ]];  then icon="${RED}❌${RESET}"
  elif [[ "$status" == "SKIPPED" ]]; then icon="${YELLOW}⏭️${RESET}"
  else                                    icon="${YELLOW}⚠️${RESET}"
  fi
  printf "  %-25s " "$step"
  echo -e "${icon} ${status}"
done
echo ""
echo -e "Build logs: ${LOG_DIR}/"
echo ""
echo -e "${BOLD}Verify deployment:${RESET}"
echo "  kubectl get pods -n gdc-pm"
echo "  kubectl logs -n gdc-pm -l app=fault-trigger-ui --tail=10"
echo "  kubectl logs -n gdc-pm -l app=event-processor --tail=10"
echo "  kubectl logs -n gdc-pm -l app=ollama --tail=5 2>/dev/null || echo 'Ollama: provisioning'"
