# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date: June 12, 2026 (Session BO — Sprint L4 deployed, GPU test deferred)
**git head:** `5492e32` — feat(sprint-l4): Gemma extraction + Path A evidence-strength modulation
**fault-trigger-ui image:** `sha256:2d7f4c0349e34216c81b4ecb2b0c0905b706382d09252843b46d44b7cac98d05`
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## ⚠️ GPU CLUSTER ISSUE — READ BEFORE DOING ANY GPU WORK

The cluster `gdc-edge-simulation` is in **us-east1** — a region with essentially no L4 GPU availability.
- The `ollama-models-pvc` PV is zone-locked to **us-east1-b**
- The GPU node pool only provisioned a node in **us-east1-d** (wrong zone → PVC mismatch → Ollama Pending forever)
- Session BO ran `gpu-start.sh` which left a us-east1-d GPU node running. **Run `./scripts/gpu-stop.sh` manually** once the cluster finishes RECONCILING before starting any new session.
- Future GPU tests require either: (a) a different cluster region (east4/east5), or (b) re-creating the ollama-models-pvc in us-east1-d and updating the deployment.
- Do NOT run `gpu-start.sh` again in this cluster without resolving the zone mismatch first.

---

## STEP 1: Run These Commands First

```bash
# 1. Stop GPU if still running (cluster may still be RECONCILING from Session BO)
source .env && gcloud container clusters describe gdc-edge-simulation --region us-east1 --format="value(status)" && ./scripts/gpu-stop.sh

# 2. Cluster health
source .env && kubectl get pods -n gdc-pm --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c

# 3. Quick status check
source .env && curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | jq '{ollama_online, ollama_model}' 2>/dev/null || echo "MLOps status API offline/starting"
```

**Expected (dev default — GPU OFF):**
- 6 pods 1/1 Running + 3 prune CronJob Completed (ollama pod ABSENT — correct)
- `ollama_online: False` — NOT a problem. Do NOT scale up without resolving zone mismatch.

---

## STEP 2: Read These Two Docs

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Task

### ✅ SPRINT L1 — Weight Metadata Migration — COMPLETE (Session BL)
### ✅ SPRINT L2 — Readable Docs + Discoverable Weights — COMPLETE (Session BM)
### ✅ SPRINT L3 — Corpus Expansion — COMPLETE (Session BN)
### ✅ SPRINT L4 — Gemma Extraction + Path A Evidence-Strength Modulation — CODE DEPLOYED, GPU TEST DEFERRED

**What L4 delivered (Session BO):**
- `_gemma_extract_findings()`: reads 3 retrieved L3 docs, calls Gemma 4, returns `{F1-F4: emphatic/qualified/absent}`
- `_bayes_discriminate(gemma_mod=None)`: Path A — emphatic→lr_max, qualified→lr_base, absent→lr_min
- `h1_scenario_replay`: fetch RAG → Gemma extract → Bayes, returns `gemma_modulated` bool
- `index.html`: evidence table has Gemma status header + per-finding strength badge
- **CPU fallback verified live**: `gemma_modulated=False`, `bayes_pct=93.1` unchanged
- **GPU test deferred**: cluster in us-east1 has no L4 quota; Ollama never scheduled

**Remaining for GPU validation test (next session with working GPU):**
1. Confirm Ollama pod schedules and is 1/1 Running
2. Call `/api/h1/scenario-replay` with Ollama online
3. Verify: `gemma_modulated=True`, `bayes_pct` varies from 93.1 (LRs adjusted), `gemma_strength` = real classifications

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED — PARAFFIN | Session BG |
| H2 Scenario Replay | ✅ DEPLOYED — PARAFFIN | Session BJ |
| Sprint H3-E: pad-level dashboard | ✅ DEPLOYED | Session BH |
| Sprint H3-F: selectable constraints + RAG | ✅ DEPLOYED | Session BI |
| H3 briefing panel Hz values (66.0, 65.5, 59.7) | ⚠️ HARDCODED | From live API 2026-06-11 |
| H1/H2 pgvector retrieval | ✅ REAL + DISCRIMINATING | Sprint L3 |
| H1 Bayesian provenance band | ✅ DEPLOYED | Sprint L2 |
| H2 doc modals (click to read) | ✅ DEPLOYED | Sprint L2 |
| Sprint L4 Gemma extraction (app.py + index.html) | ✅ DEPLOYED — CPU FALLBACK VERIFIED | GPU path untested (us-east1 quota issue) |
| H1_METHODOLOGY.md LRs 8/5/3/2→99.6% | ⚠️ STALE DOC | Code uses 3/2/1.6/1.4→93% |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended |
| Pad Alpha RAG corpus (38 total rows) | ✅ SEEDED | Session BN |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Do not cite as hard facts |
| **GPU cluster region** | ⛔ WRONG REGION | Cluster in us-east1 — no L4 GPU quota. GPU pool node (us-east1-d) left running by Session BO — run gpu-stop.sh |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~7,750 lines · `index.html` ~3,660 lines · `app.js` ~2,310 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (always)
- **No build/push/deploy without user walkthrough and verification**
- MCP gdc-second-opinion: ⛔ DISABLED
- **Ask inline questions — no option lists**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status`
- **GPU:** Do NOT run `gpu-start.sh` until the us-east1 zone mismatch is resolved. The ollama-models-pvc is zone-locked to us-east1-b; GPU nodes come up in us-east1-d.
