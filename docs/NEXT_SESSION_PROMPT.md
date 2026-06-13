# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** Session BQ — June 13, 2026  
**git head:** `b3fd9cb` — fix(sprint-l4): think:False + timeout 60s for Gemma4 extraction  
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

### 3a — DNS update (if not done)
Update `gdc-pm.bdau.io` A-record → **`34.72.142.23`** (new fault-trigger-ui LoadBalancer IP)  
Grafana: **`34.45.194.92`**

### 3b — Sprint L4 COMPLETE ✅
GPU path fully validated this session. `gemma_modulated: True`, `bayes_pct: 96.6`.  
**No further L4 work needed.**

### 3c — Product task ✅ COMPLETE (Session BQ)
DEMO_MASTER §3 L2/APM-concession reconciliation done. Hostile-engineer pass run via Gemini API (ADC). Verdict: L2 reclaim FAILS on detection quality, sovereignty-at-L2, and "your data" claims. L2 contribution reframed as **deployment simplicity** (zero legacy footprint). PRIME DIRECTIVE patched; 2 new rejected-claim rows added. See SESSION_LOG for full decision record.

### 3d — H3-F (selectable constraint + RAG provenance) — queued

---

## Current Dev State

| Item | Status |
|---|---|
| H1 Discern (Scenario Replay + Bayesian) | ✅ DEPLOYED + VERIFIED (bayes_pct=93.1 CPU / 96.6 GPU, gdc_detect_idx=33 < alarm_idx=60) |
| H2 Classify (Paraffin scenario) | ✅ DEPLOYED + VERIFIED (paraffin_wax_restriction, 3 docs) |
| H3 Optimize (Pad Alpha 6-well + Vizier) | ✅ DEPLOYED + VERIFIED (uplift_bbl_d=189.6, $725K/90d) |
| Sprint L1–L3 (weight metadata, pgvector, corpus) | ✅ COMPLETE |
| Sprint L4 Gemma extraction + Path A modulation | ✅ **FULLY VERIFIED** — GPU path `gemma_modulated: True`, 1.6s T4 |
| Autopilot rebuild (us-central1, T4) | ✅ COMPLETE — 7/7 pods Running |
| H3-F (selectable constraint + RAG provenance) | ⏸ QUEUED |
| H1_METHODOLOGY.md LR values | ⚠️ STALE DOC — code is correct (3/2/1.6/1.4→93%); doc says 8/5/3/2→99.6% |
| DEMO_MASTER §3 L2/APM-concession reconciliation | ✅ COMPLETE (Session BQ) — hostile-pass run; PRIME DIRECTIVE patched |

---

## Known Integrity State

| Item | Status | Note |
|---|---|---|
| H1–H3 all horizons | ✅ DEPLOYED + VERIFIED | Live on Autopilot cluster |
| Sprint L4 Gemma extraction | ✅ **GPU PATH VERIFIED** | `gemma_modulated: True`, `bayes_pct: 96.6`, 1.6s |
| Sprint L4 fix: `think: False` | ✅ DEPLOYED `b3fd9cb` | Disables Gemma4 chain-of-thought; classification ~1.6s |
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
