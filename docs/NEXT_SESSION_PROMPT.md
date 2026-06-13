# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** Session BP — June 13, 2026  
**git head:** `2e016a6` — chore(autopilot): finish companion changes (scheduler + runbook)  
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Commands First

```bash
# 1. GPU pool at 0 (no billing)
kubectl get nodes -l cloud.google.com/gke-accelerator=nvidia-l4 --no-headers | wc -l
# Expected: 0

# 2. Cluster health
kubectl get pods -n gdc-pm --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c
# Expected: 6 Running

# 3. API status
curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))" \
  2>/dev/null || echo "API offline"
# Expected: ollama_online: False (correct dev default)
```

If anything is unexpected, **stop and ask** before writing any code.

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Task — Autopilot + T4 Rebuild

### The plan (decided Session BP)

1. **Pre-flight (before teardown):**
   - `gcloud compute accelerator-types list --filter="zone:us-central1* AND name=nvidia-tesla-t4"` — confirm T4 available
   - ~~Apply companion code changes~~ ✅ ALL DONE — `4e7e09c` + `2e016a6` committed

2. **Companion code changes to YAML/scripts (do this first):**
   | File | Change |
   |---|---|
   | `gke/ollama/k8s/ollama.yaml` | nodeSelector `nvidia-tesla-t4`, no taint/toleration, limits.memory 16Gi, fix 27b header |
   | `gke/fault-trigger-ui/k8s/fault-trigger-ui.yaml` | `OLLAMA_MODEL: "gemma4:latest"` (was "gemma:27b") |
   | `scripts/gpu-start.sh` | Replace node-pool resize with `kubectl scale deployment ollama -n gdc-pm --replicas=1` |
   | `scripts/gpu-stop.sh` | Replace node-pool resize with `kubectl scale deployment ollama -n gdc-pm --replicas=0` |

3. **Teardown + Rebuild:** Follow `docs/runbooks/deploy-from-scratch.md` start to finish.  
   Region: `us-central1` · Cluster type: Autopilot · GPU: T4 (~$0.35/hr, scale-to-zero)

4. **Post-rebuild — verify then continue Sprint L4 GPU validation:**
   - Run verification checklist (Step 13 in runbook)
   - Announce "$0.35/hr T4 GPU cost" → get confirmation → `./scripts/gpu-start.sh`
   - Verify `gemma_modulated=True`, `bayes_pct` varies from 93.1 (confirms Gemma Path A is live)
   - `./scripts/gpu-stop.sh` immediately after

5. **After L4 GPU validated — Product task (first after rebuild):**
   Reconcile DEMO_MASTER §3 two-tier APM concession (Session BF) vs the Session AS/AT decision to reclaim L2 as genuine differentiator alongside L3. The target is: **L2 (fleet-trained edge ML) + L3 (document fusion) = the sovereign AI stack**, not L3-only. Requires hostile-engineer pass before any §3 wording changes.

---

## Current Dev State

| Item | Status |
|---|---|
| H1 Discern (Scenario Replay + Bayesian) | ✅ DEPLOYED |
| H2 Classify (Paraffin scenario) | ✅ DEPLOYED |
| H3 Optimize (Pad Alpha 6-well + Vizier) | ✅ DEPLOYED |
| Sprint L1–L3 (weight metadata, pgvector, corpus) | ✅ COMPLETE |
| Sprint L4 Gemma extraction + Path A modulation | ✅ CODE DEPLOYED — CPU fallback verified (bayes_pct=93.1) — **GPU path pending** |
| H3-F (selectable constraint + RAG provenance) | ⏸ QUEUED — after rebuild |
| H1_METHODOLOGY.md LR values | ⚠️ STALE DOC — code is correct (3/2/1.6/1.4→93%); doc says 8/5/3/2→99.6% |
| DEMO_MASTER §3 L2/APM-concession reconciliation | ⏸ QUEUED — post-rebuild product task |

---

## Known Integrity State

| Item | Status | Note |
|---|---|---|
| H1–H3 all horizons | ✅ DEPLOYED | Paraffin, pad-level dashboard, Vizier |
| Sprint L4 Gemma extraction | ✅ CPU FALLBACK VERIFIED | GPU path pending T4 rebuild |
| H1/H2 pgvector retrieval | ✅ REAL + DISCRIMINATING | Sprint L3 |
| `OLLAMA_MODEL: "gemma:27b"` in manifest | ✅ FIXED `4e7e09c` | fault-trigger-ui.yaml now has gemma4:latest |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended |
| H1_METHODOLOGY.md LR values | ⚠️ STALE DOC | Fix post-rebuild |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied (would destroy live cluster)
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- **No GPU start without announcing cost (~$0.35/hr T4) and getting confirmation**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status`
- Artifact Registry only — NOT gcr.io
