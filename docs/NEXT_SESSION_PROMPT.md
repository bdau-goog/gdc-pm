# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** Session BP — June 13, 2026  
**git head:** `cc104b1` — docs(runbook): fix Step 13 field names  
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Commands First

```bash
# 1. GPU pool at 0 (no billing)
kubectl get nodes -l cloud.google.com/gke-accelerator=nvidia-tesla-t4 --no-headers | wc -l
# Expected: 0

# 2. Cluster health
kubectl get pods -n gdc-pm --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c
# Expected: 1 Completed + 7 Running

# 3. API status
curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))" \
  2>/dev/null || echo "API offline"
# Expected: ollama_online: False (correct dev default)
# NOTE: DNS may need update — if API offline, hit 34.72.142.23 directly
```

If anything is unexpected, **stop and ask** before writing any code.

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Tasks

### 3a — DNS update (if not done)
Update `gdc-pm.bdau.io` A-record → **`34.72.142.23`** (new fault-trigger-ui LoadBalancer IP)  
Grafana: **`34.45.194.92`**

### 3b — Sprint L4 GPU validation (first code task)

The rebuild is complete. CPU fallback verified (`bayes_pct=93.1`, `gemma_modulated=False`).  
GPU path validation is the remaining Sprint L4 item:

```bash
# Announce cost first (~$0.35/hr T4), then:
./scripts/gpu-start.sh   # waits until model ready (~5-15 min first time)

# Verify GPU path:
curl -s "http://34.72.142.23/api/h1/scenario-replay?fault=gas_lock" | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print('gemma_modulated:',d['gemma_modulated'],'bayes_pct:',d['bayes_pct'])"
# Expected: gemma_modulated: True, bayes_pct varies from 93.1

./scripts/gpu-stop.sh   # ALWAYS pair immediately after test
```

### 3c — Product task (after GPU validated)
Reconcile DEMO_MASTER §3 two-tier APM concession (Session BF) vs Session AS/AT decision to reclaim L2 as genuine differentiator alongside L3. Target: **L2 (fleet-trained edge ML) + L3 (document fusion) = the sovereign AI stack**, not L3-only. Requires hostile-engineer pass before any §3 wording changes.

---

## Current Dev State

| Item | Status |
|---|---|
| H1 Discern (Scenario Replay + Bayesian) | ✅ DEPLOYED + VERIFIED (bayes_pct=93.1, gdc_detect_idx=33 < alarm_idx=60) |
| H2 Classify (Paraffin scenario) | ✅ DEPLOYED + VERIFIED (paraffin_wax_restriction, 3 docs) |
| H3 Optimize (Pad Alpha 6-well + Vizier) | ✅ DEPLOYED + VERIFIED (uplift_bbl_d=189.6, $725K/90d) |
| Sprint L1–L3 (weight metadata, pgvector, corpus) | ✅ COMPLETE |
| Sprint L4 Gemma extraction + Path A modulation | ✅ CPU FALLBACK VERIFIED — **GPU path pending** (3b above) |
| Autopilot rebuild (us-central1, T4) | ✅ COMPLETE — 7/7 pods Running |
| H3-F (selectable constraint + RAG provenance) | ⏸ QUEUED |
| H1_METHODOLOGY.md LR values | ⚠️ STALE DOC — code is correct (3/2/1.6/1.4→93%); doc says 8/5/3/2→99.6% |
| DEMO_MASTER §3 L2/APM-concession reconciliation | ⏸ QUEUED — post GPU-validation product task |

---

## Known Integrity State

| Item | Status | Note |
|---|---|---|
| H1–H3 all horizons | ✅ DEPLOYED + VERIFIED | Live on Autopilot cluster |
| Sprint L4 Gemma extraction | ✅ CPU FALLBACK VERIFIED | GPU path pending (task 3b) |
| H1/H2 pgvector retrieval | ✅ REAL + DISCRIMINATING | Sprint L3 |
| `OLLAMA_MODEL` manifest | ✅ FIXED `4e7e09c` | `gemma4:latest` in fault-trigger-ui.yaml |
| GRAFANA_URL | ✅ FIXED `8e9bca3` | `34.45.194.92` (new Autopilot cluster) |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended |
| H1_METHODOLOGY.md LR values | ⚠️ STALE DOC | Fix post-rebuild |

---

## Cluster State

| Resource | Value |
|---|---|
| Cluster | `gdc-edge-simulation` — GKE Autopilot, us-central1 |
| fault-trigger-ui LoadBalancer | `34.72.142.23` |
| grafana LoadBalancer | `34.45.194.92` |
| Ollama replicas | `0` (no GPU billing) |
| AlloyDB | `alloydb-omni.gdc-pm.svc.cluster.local:5432` |
| Seeds | 20 rag_documents, 11 field_intel |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied (would destroy live cluster)
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- **No GPU start without announcing cost (~$0.35/hr T4) and getting confirmation**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status`
- Artifact Registry only — NOT gcr.io
