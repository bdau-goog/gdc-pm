#!/usr/bin/env bash
# =============================================================================
# scripts/hard_reset_db.sh
#
# Hard reset the AlloyDB telemetry_events table in the GDC-PM cluster.
# This is a DESTRUCTIVE operation — all telemetry history will be deleted.
#
# Use cases:
#   - Clearing Pad Charlie phantom data from before the fleet was trimmed
#   - Starting a completely clean demo with zero historical events
#   - Resetting after a test run that polluted the event log
#
# Soft reset (clears ledger/savings but keeps history):
#   Use the "♻ Reset Demo Data" button in the Fleet Financials tab instead.
#
# Usage:
#   bash scripts/hard_reset_db.sh              # truncate telemetry_events
#   bash scripts/hard_reset_db.sh --confirm    # skip confirmation prompt
# =============================================================================

set -euo pipefail

NAMESPACE="gdc-pm"
ALLOYDB_SVC="alloydb-omni"
DB_NAME="grid_reliability"
DB_USER="postgres"

# ── Colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'; NC='\033[0m'

echo ""
echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║              GDC-PM DATABASE HARD RESET                 ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}This will TRUNCATE the telemetry_events table.${NC}"
echo -e "${YELLOW}ALL telemetry history, events, and ledger entries will be deleted.${NC}"
echo ""

# ── Confirmation ──────────────────────────────────────────────────────────────
if [[ "${1:-}" != "--confirm" ]]; then
  read -rp "  Type 'RESET' to continue: " CONFIRM
  if [[ "$CONFIRM" != "RESET" ]]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 0
  fi
fi

# ── Verify kubectl context ────────────────────────────────────────────────────
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "none")
echo ""
echo -e "  Kubernetes context: ${YELLOW}${CURRENT_CONTEXT}${NC}"
echo ""

# ── Find the AlloyDB Omni pod ─────────────────────────────────────────────────
echo "  Finding AlloyDB pod in namespace '${NAMESPACE}'..."
ALLOYDB_POD=$(kubectl get pod -n "${NAMESPACE}" \
  -l "app=${ALLOYDB_SVC}" \
  --no-headers \
  -o custom-columns=":metadata.name" 2>/dev/null | head -1)

if [[ -z "${ALLOYDB_POD}" ]]; then
  # Try alternate label selector used in some deploys
  ALLOYDB_POD=$(kubectl get pod -n "${NAMESPACE}" \
    --no-headers \
    -o custom-columns=":metadata.name" 2>/dev/null \
    | grep -i alloydb | head -1 || true)
fi

if [[ -z "${ALLOYDB_POD}" ]]; then
  echo -e "${RED}  ERROR: Could not find an AlloyDB pod in namespace '${NAMESPACE}'.${NC}"
  echo "  Check with: kubectl get pods -n ${NAMESPACE}"
  exit 1
fi

echo -e "  Found pod: ${GREEN}${ALLOYDB_POD}${NC}"
echo ""

# ── Step 1: Truncate telemetry_events ────────────────────────────────────────
echo "  Step 1/3 — Truncating telemetry_events..."
kubectl exec -n "${NAMESPACE}" "${ALLOYDB_POD}" -- \
  psql -U "${DB_USER}" -d "${DB_NAME}" \
  -c "TRUNCATE TABLE telemetry_events RESTART IDENTITY;" \
  2>&1

echo -e "  ${GREEN}✓ telemetry_events truncated${NC}"

# ── Step 2: Reset the AlloyDB sequence (if using SERIAL / BIGSERIAL IDs) ─────
echo "  Step 2/3 — Resetting event ID sequence..."
kubectl exec -n "${NAMESPACE}" "${ALLOYDB_POD}" -- \
  psql -U "${DB_USER}" -d "${DB_NAME}" \
  -c "SELECT setval(pg_get_serial_sequence('telemetry_events','id'), 1, false);" \
  2>&1 || true   # non-fatal: RESTART IDENTITY above should handle this

echo -e "  ${GREEN}✓ Sequence reset${NC}"

# ── Step 3: Verify row count ──────────────────────────────────────────────────
echo "  Step 3/3 — Verifying row count..."
ROW_COUNT=$(kubectl exec -n "${NAMESPACE}" "${ALLOYDB_POD}" -- \
  psql -U "${DB_USER}" -d "${DB_NAME}" \
  -t -c "SELECT COUNT(*) FROM telemetry_events;" \
  2>/dev/null | tr -d ' ')

echo -e "  telemetry_events row count: ${GREEN}${ROW_COUNT}${NC}"
echo ""

if [[ "${ROW_COUNT}" == "0" ]]; then
  echo -e "${GREEN}  ✅ Hard reset complete. Database is clean.${NC}"
else
  echo -e "${RED}  ⚠  Unexpected row count after truncate. Check manually.${NC}"
  exit 1
fi

echo ""
echo -e "  ${YELLOW}Next steps:${NC}"
echo "    • The live feed will show 'No events yet…' until telemetry flows in (~10s)"
echo "    • Any active fault injections should be reset via the UI ↺ Reset button"
echo "    • The Fleet Financials ledger will be empty (as expected)"
echo ""
