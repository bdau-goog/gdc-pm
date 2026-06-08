# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** Session F end — June 8, 2026  
**git head:** `1518b5e` (docs: Claim Ledger C2 resolved, Phase 3 unblocked)  
**fault-trigger-ui image:** `sha256:ec5b0306` (1/1 Running — unchanged since Session E)  
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)  
**Branch:** `feature-trio-scenarios` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
source .env && kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
source .env && kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

Also check RabbitMQ every session start:
```bash
source .env && kubectl exec -n gdc-pm gdc-pm-rabbitmq-server-0 -- rabbitmqctl list_queues --vhost gdc-pm name messages consumers
```

**⚠️ NOTE: Session F bootstrapped workspace isolation. All kubectl/gcloud commands MUST now be prefixed with `source .env &&`**

**Expected healthy (Session G start):**
- All 8 pods: 1/1 Running (2 completed cronjobs are normal)
- ollama_online: True · model: gemma4:latest
- field_intel: 0–5 rows (only grows during active fault)
- rag_documents: 18 rows
- RabbitMQ: **< 500 messages** (P0 fix from Session D holding)

---

## STEP 2: Read These Two Documents

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
cat ~/gdc-pm/docs/CLAIM_LEDGER.md
```

---

## STEP 3: Session F State Summary

### What was done Session F:
1. **Workspace isolation bootstrapped** (`39da363`): `scripts/setup-workspace.sh`, `terraform/terraform.tfvars` (gdc-pm-v2/us-east1), `.env`, `.envrc`, `.kubeconfig` seeded from live cluster. `.gitignore` updated. All `source .env && kubectl` commands now use isolated kubeconfig.
2. **Claim Ledger C2 resolved** (`1518b5e`): Was 🔴 NEEDS-EXPERT blocking Phase 3. Now 🟡 SURVIVES via independent math: 300 BPD @ $76/bbl × 2–4h restart (API RP 11S §7.2) + labor + thermal cycling = **$3,000–$8,000** defensible range. All 10 claims now SURVIVES or SURVIVES-with-qualification. No 🔴 rows remain.

### PHASE 3 IS UNBLOCKED — Next task:

**H1 Decision Clock UI Redesign** (index.html only, single batched `replace_in_file`)

The honest H1 story per CLAIM_LEDGER.md Section 5:
> *"GDC detected gas lock at minute 2 — while all 4 SCADA thresholds still green — $2,500 VFD trim kept well producing. SCADA trip would fire ~15–21 min later costing $3k–$8k. Past ~25 min: ~$150k pump pull."*

**3 integrity bugs to fix IN THE SAME PASS** (all independent of C2, in current live deployment):
1. **Motor CRITICAL state** driven by `h1ElapsedMin > 15` timer (integrity violation) — must derive from `h1SensorTemp` value
2. **Pre-injection sensor bars** showing hardcoded fallback values instead of live-telemetry
3. **RAG seed doc collapses to 0** after ~5 min (100-row prune job rotates it out)

**Phase 3 Decision Clock additions** (NEW — build the cost-ladder visual):
- Decision timeline with YOU ARE HERE moving marker
- Cost ladder nodes: $2,500 (GDC, VIABLE) → $3k–$8k (SCADA reactive, footnoted range) → $150k (post-PNR)
- Footnote on C2: "2–4h production loss + restart labor + thermal cycling risk (300 BPD @ $76/bbl). Varies by well."
- Motor state badge from actual `h1SensorTemp` vs 280°F threshold, not elapsed time

**Do NOT start Phase 3 code until reviewing DEMO_MASTER.md §12 wireframe (lines 488–528)**

---

## Known Integrity State — Session F end

| Item | File | Status |
|---|---|---|
| "$0 direct cost" → "$2,500" | index.html | ✅ Fixed Session E (a493549) |
| Missing Vibration sensor bar | index.html | ✅ Fixed Session E (a493549) |
| Thermal countdown "993 min" at onset | index.html | ✅ Fixed Session E (a493549) |
| Sensor source unified (DB trace) | app.js | ✅ Fixed Session E (a493549) |
| Motor CRITICAL state from elapsed time | index.html | ❌ Phase 3 fix (integrity violation) |
| Pre-injection sensor bars hardcoded | index.html | ❌ Phase 3 fix |
| RAG seed doc collapses after ~5 min | app.py | ❌ Phase 3 fix |
| FAULT_PHYSICS 45min vs PNR 25min comment | app.py | ⚠ Comment update deferred |
| H3 Vizier hardcoded polynomial | app.py:~5293 | ❌ Phase 5+ — not blocking H1/H2 |
| esp_classifier trained on invented ranges | inference-api/models | ⚠ Phase 5 retrain |
| CLAIM_LEDGER C2 | docs/CLAIM_LEDGER.md | ✅ Resolved Session F — $3k–$8k math-derived range |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote
- `feature-trio-scenarios` stays separate from `main`
- Batch all edits to same file in ONE `replace_in_file` call
- **ALL kubectl/gcloud commands now require `source .env &&` prefix** (workspace isolation active)
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- inference-api registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest`
- Do NOT use "Copilot" anywhere in H1/H2/H3
- Failing model `.ubj` files are NEVER committed
- All claims on screen must have a SURVIVES row in CLAIM_LEDGER.md before code is written
