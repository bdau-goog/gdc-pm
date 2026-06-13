# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date: June 13, 2026 (Session BO — Sprint L4 deployed; GPU fixed; cluster rebuild decision pending)**
**git head:** `9572fa6` — fix(gpu): restrict gpu-pool to us-east1-b — single node $1.09/hr
**fault-trigger-ui image:** `sha256:2d7f4c0349e34216c81b4ecb2b0c0905b706382d09252843b46d44b7cac98d05`
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## ⚠️ TOP PRIORITY NEXT SESSION — Two Decisions Required Before Development Continues

### Decision 1: Deploy-from-Scratch Process
Review `docs/runbooks/deploy-from-scratch.md` and verify it is complete and correct.
If not: rewrite it so it covers the full stack (AlloyDB, RabbitMQ, inference-api, fault-trigger-ui, Ollama GPU pool).
**Goal:** A new engineer (or a new session) can rebuild this cluster from zero using only this runbook.

### Decision 2: Autopilot Migration
Analyze whether GKE Autopilot can replace the current standard cluster. Key questions:
1. Can Autopilot handle GPU requests for Ollama (gemma4:latest, ~6GB VRAM)? Which GPU types?
2. Does Autopilot auto-scale-to-zero GPU when replicas=0? (This eliminates the billing problem completely)
3. What must be migrated? AlloyDB PVC (data), ollama-models PVC (model cache), all k8s YAML
4. What breaks? Any incompatible configs in current k8s YAML?
5. Cost comparison: current standard cluster vs Autopilot at same workload
6. Time estimate: how long to tear down and rebuild?

**If Autopilot answers are favorable:** Tear down the current cluster and rebuild in Autopilot. Continue Sprint L4 GPU validation + Sprint L5+ on the new cluster.
**If Autopilot has blocking issues:** Stay on standard GKE. Apply the L4→T4 migration (wider availability, $0.50/hr).

---

## STEP 1: Run These Commands First

```bash
# 1. Verify GPU pool is at 0 (no billing)
source .env && kubectl get nodes -l cloud.google.com/gke-accelerator=nvidia-l4 --no-headers | wc -l
# Expected: 0

# 2. Cluster health
source .env && kubectl get pods -n gdc-pm --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c

# 3. Quick status check
source .env && curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | jq '{ollama_online, ollama_model}' 2>/dev/null || echo "API offline"
```

**Expected:** 6 pods Running, 0 GPU nodes, ollama_online: false

---

## STEP 2: Read DEMO_MASTER.md and deploy-from-scratch runbook

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
cat /home/brian/gdc-pm/docs/runbooks/deploy-from-scratch.md
```

---

## STEP 3: Sprint Work (after cluster decision)

### ✅ SPRINT L1 — COMPLETE (Session BL)
### ✅ SPRINT L2 — COMPLETE (Session BM)
### ✅ SPRINT L3 — COMPLETE (Session BN)
### ✅ SPRINT L4 — CODE DEPLOYED, GPU VALIDATION PENDING

**Sprint L4 still needs (once cluster is sorted):**
1. Run `./scripts/gpu-start.sh` — now provisions exactly 1 L4 node in us-east1-b at ~$1.09/hr
2. Scale Ollama, wait for model load
3. Call `/api/h1/scenario-replay`, verify `gemma_modulated=True`, `bayes_pct` varies from 93.1
4. Run `./scripts/gpu-stop.sh` immediately when done

---

## GPU State

| Item | State |
|---|---|
| GPU pool | **0 nodes** — at rest, no billing |
| gpu-pool zone | **us-east1-b only** (single-zone fix applied Session BO) |
| gpu-start.sh | **Fixed** — provisions 1 node at $1.09/hr, no zone mismatch |
| ollama-models-pvc | Bound, zone us-east1-b — matches node pool |
| Ollama replicas | 0 |

---

## Known Integrity State

| Item | Status | Note |
|---|---|---|
| H1–H3 all horizons | ✅ DEPLOYED | Paraffin, pad-level dashboard, Vizier |
| Sprint L4 Gemma extraction | ✅ DEPLOYED — CPU FALLBACK VERIFIED | GPU path pending |
| H1/H2 pgvector retrieval | ✅ REAL + DISCRIMINATING | Sprint L3 |
| H1_METHODOLOGY.md LRs | ⚠️ STALE DOC | Code 3/2/1.6/1.4→93%; doc says 8/5/3/2→99.6% |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended |
| SPE papers cited | ⚠️ UNVERIFIED | Do not cite as hard facts |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied (would destroy live cluster)
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- **No GPU start without announcing cost and getting confirmation**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status`
- Artifact Registry only — NOT gcr.io
