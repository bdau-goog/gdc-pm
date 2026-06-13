# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** Session BQ+1 wrap — June 13, 2026  
**git head:** `5ed18cb` — docs(h1-methodology): correct stale LR values 8/5/3/2→99.6% to live code values 3/2/1.6/1.4→93.1%  
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Commands First

```bash
# 1. GPU pool at 0 (no billing)
kubectl get nodes -l cloud.google.com/gke-accelerator=nvidia-tesla-t4 --no-headers | wc -l
# Expected: 0 (Autopilot deprovisions ~2-3 min after gpu-stop.sh)

# 2. Cluster health
kubectl get pods -n gdc-pm --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c
# Expected: 1 Completed + 7 Running (Ollama at 0 replicas — correct dev default)

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

### 3a — DNS ✅ DONE
`/etc/hosts` updated by user. `gdc-pm.bdau.io` → `34.72.142.23`. Grafana: `34.45.194.92`.

### 3b — Sprint L4 COMPLETE ✅
GPU path fully validated. `gemma_modulated: True`, `bayes_pct: 96.6`.  
**No further L4 work needed.**

### 3c — DEMO_MASTER §3 L2/APM reconciliation ✅ COMPLETE (Session BQ)
Hostile-engineer pass run via Gemini API. L2 framing reworded to deployment simplicity. PRIME DIRECTIVE patched.

### 3d — H3-F (selectable constraint + RAG provenance) ✅ VERIFIED LIVE (Session BQ+1)
**Already deployed and working.** Constraint toggles (gas/thermal/rul) in UI, API passes constraint,
pgvector returns real docs for all 3 constraints:
- `gas` → "Pad Alpha — Gas Gathering Agreement (Ref. PA-2024-GG-047)"
- `thermal` → "Pad Alpha — ESP Motor Thermal Limit Memo (PE-2025-NOV-047)"
- `rul` → "Pad Alpha — Q2 2026 ESP Fleet RUL Assessment"
No code changes were needed. The feature was already implemented.

### 3e — H1_METHODOLOGY.md LR values ✅ FIXED (Session BQ+1)
Corrected stale values: `8/5/3/2 → 99.6%` → live code values `3/2/1.6/1.4 → 93.1%`.
Committed `5ed18cb`.

### 3f — NEXT: What is actually left?
All known backlog items are now complete. Read DEMO_MASTER.md §12 Implementation Order
to identify any remaining H3 or polish tasks. Candidates to investigate:
- Is there a Vizier Pareto chart that needs implementation?
- Is the `?` on `vizier_used` in the API response a display bug worth fixing?
- VIDEO_SCRIPT.md — any remaining gaps before a full demo run?

---

## Current Dev State

| Item | Status |
|---|---|
| H1 Discern (Scenario Replay + Bayesian) | ✅ DEPLOYED + VERIFIED (bayes_pct=93.1 CPU / 96.6 GPU, gdc_detect_idx=33 < alarm_idx=60) |
| H2 Classify (Paraffin scenario) | ✅ DEPLOYED + VERIFIED (paraffin_wax_restriction, 3 docs) |
| H3 Optimize (Pad Alpha 6-well + Vizier) | ✅ DEPLOYED + VERIFIED (uplift_bbl_d=189.6, $725K/90d) |
| Sprint L1–L3 (weight metadata, pgvector, corpus) | ✅ COMPLETE |
| Sprint L4 Gemma extraction + Path A modulation | ✅ FULLY VERIFIED — GPU path `gemma_modulated: True`, 1.6s T4 |
| Autopilot rebuild (us-central1, T4) | ✅ COMPLETE — 7/7 pods Running |
| H3-F (selectable constraint + RAG provenance) | ✅ VERIFIED LIVE (Session BQ+1) — was already deployed |
| H1_METHODOLOGY.md LR values | ✅ FIXED (Session BQ+1) `5ed18cb` — 3/2/1.6/1.4→93.1% |
| DEMO_MASTER §3 L2/APM-concession reconciliation | ✅ COMPLETE (Session BQ) |
| VIDEO_SCRIPT.md decision-support language | ✅ COMPLETE (Session BQ) |

---

## Known Integrity State

| Item | Status | Note |
|---|---|---|
| H1–H3 all horizons | ✅ DEPLOYED + VERIFIED | Live on Autopilot cluster |
| Sprint L4 Gemma extraction | ✅ GPU PATH VERIFIED | `gemma_modulated: True`, `bayes_pct: 96.6`, 1.6s |
| Sprint L4 fix: `think: False` | ✅ DEPLOYED `b3fd9cb` | Disables Gemma4 chain-of-thought; classification ~1.6s |
| H1/H2 pgvector retrieval | ✅ REAL + DISCRIMINATING | Sprint L3 |
| `OLLAMA_MODEL` manifest | ✅ FIXED `4e7e09c` | `gemma4:latest` in fault-trigger-ui.yaml |
| GRAFANA_URL | ✅ FIXED `8e9bca3` | `34.45.194.92` (new Autopilot cluster) |
| H1_METHODOLOGY.md LR values | ✅ FIXED `5ed18cb` | 3/2/1.6/1.4→93.1% (was 8/5/3/2→99.6%) |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended |

---

## Cluster State

| Resource | Value |
|---|---|
| Cluster | `gdc-edge-simulation` — GKE Autopilot, us-central1 |
| fault-trigger-ui LoadBalancer | `34.72.142.23` |
| fault-trigger-ui image | `sha256:2bb22017af8eaa8ee9dba9a8c227921ee6656eb61827d8abb223017179e6e6e4` |
| grafana LoadBalancer | `34.45.194.92` |
| Ollama replicas | `0` (no GPU billing) |
| AlloyDB | `alloydb-omni.gdc-pm.svc.cluster.local:5432` |
| Seeds | 20 rag_documents, 11 field_intel |

### Gemma4 model notes
- Model: `gemma4:latest` (9.6GB, cached on PVC — next startup skips download)
- **Must always use `"think": False`** in all Ollama API calls — Gemma4 thinking mode adds 180s+ latency
- With `think: False`: 1.6s inference on T4 (1,185 tok/s prefill, 40 tok/s eval)
- No stronger GPU needed — T4 is sufficient for this classification task

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied (would destroy live cluster)
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- **No GPU start without announcing cost (~$0.35/hr T4) and getting confirmation**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status`
- Artifact Registry only — NOT gcr.io
- **All Ollama API calls MUST include `"think": False`** — do not omit this
