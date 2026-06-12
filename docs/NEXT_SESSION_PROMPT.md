# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date: June 12, 2026 (Session BL — architecture review + Sprint L1 deployed)
**git head:** see `git log` (Session BL docs commit)
**fault-trigger-ui image:** `sha256:07cef48e2de814a3c6e184c7be71e43c0c03acda9aea18ee73afa0e9e5f34ce9`
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Three Commands First

```bash
# 1. Verify isolation & context
source .env && echo "PROJECT=$GOOGLE_CLOUD_PROJECT KUBECONFIG=$KUBECONFIG" && kubectl config current-context

# 2. Token-efficient cluster health summary
source .env && kubectl get pods -n gdc-pm --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c

# 3. Quick status check
source .env && curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | jq '{ollama_online, ollama_model}' 2>/dev/null || echo "MLOps status API offline/starting"
```

**Expected (dev default — GPU OFF):**
- 6 pods 1/1 Running + 3 prune CronJob Completed (ollama pod ABSENT — correct)
- ollama replicas: **0** · `ollama_online: False` — NOT a problem. Do NOT scale up.

**Actual at session-BJ close:** fault-trigger-ui pod 1/1 Running · HTTP 200 · H2-REPLAY paraffin verified live

**GPU discipline:** OFF by default. `./scripts/gpu-start.sh` only at explicit LLM-test step (~$1.09/hr single node). Always paired with `./scripts/gpu-stop.sh`.

**⚠️ REGISTRY NOTE:** Artifact Registry only — NOT gcr.io.
```bash
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

---

## STEP 2: Read These Two Docs

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
cat /home/brian/gdc-pm/docs/SESSION_BL_ARCHITECTURE_REVIEW.md
```

`SESSION_BL_ARCHITECTURE_REVIEW.md` is the full record of Session BL decisions — read it before writing any code.

---

## STEP 3: Next Implementation Task

### ✅ SESSION BL — Architecture decisions made (June 12, 2026) — no code written

Key decisions (full record in `docs/SESSION_BL_ARCHITECTURE_REVIEW.md`):
1. **System A/B distinction** written into DEMO_MASTER §3 — do NOT conflate "the LLM" with retrieval.
2. **4-sprint Gemma re-elevation plan** approved — L1 → L2 → L3 → L4 (GPU last, showcase-only).
3. **Honest demo claim** locked: *"GDC turns unstructured documents into structured findings (Gemma/GPU), fuses them with auditable math (CPU), and lets operators interrogate the result (Gemma/GPU) — sovereign, on open weights."*

---

### ✅ SPRINT L1 — Weight Metadata Migration — COMPLETE (Session BL)

**Prerequisite reading:** `docs/SESSION_BL_ARCHITECTURE_REVIEW.md` + `docs/LLM_RAG_ARCHITECTURE_ASSESSMENT.md` §Session BL

**Sprint L1 deliverable — no behavior change, pure refactor:**

1. **AlloyDB schema migration** — add columns to `field_intel` (additive, backward-compatible):
   ```sql
   ALTER TABLE field_intel ADD COLUMN finding_code  TEXT;   -- 'F1'..'F4' (NULL = not evidence doc)
   ALTER TABLE field_intel ADD COLUMN lr_base       REAL;   -- physics-anchored LR e.g. 3.0
   ALTER TABLE field_intel ADD COLUMN lr_min        REAL;   -- floor of physics band e.g. 2.0
   ALTER TABLE field_intel ADD COLUMN lr_max        REAL;   -- ceiling e.g. 4.5
   ALTER TABLE field_intel ADD COLUMN lr_source     TEXT;   -- 'API RP 11S §4.2'
   ALTER TABLE field_intel ADD COLUMN finding_dir   TEXT;   -- 'drawdown' | 'gas_lock'
   ```

2. **Seed the H1 evidence docs** with `finding_code` + LR metadata into `field_intel` at startup (moves `_BAYES_FINDINGS` dict out of code → data).

3. **Refactor `_bayes_discriminate()`** to query `field_intel` for `finding_code` rows matching active `fault_context`, read `lr_base`, compute posterior. Posterior must equal current ~93% — this is a refactor, not a physics change.

4. **Verify:** `GET /api/h1/scenario-replay?fault=fluid_drawdown` and `?fault=gas_lock` — posterior must match pre-L1 values within rounding tolerance.

**Sprint sequence:**
| Sprint | Deliverable | GPU? |
|---|---|---|
| **L1** | Weight-metadata migration + `_bayes_discriminate` DB refactor | No |
| **L2** | Readable-doc modal + discoverable weight provenance panel (H1 + H2) | No |
| **L3** | Corpus expansion — more H1/H2 `field_intel` docs (some noise) | No |
| **L4** | Gemma extraction + Path A evidence-strength modulation (GPU showcase only) | Single L4 ~$1.09/hr |

**Atomic-fix discipline:** Deploy and verify L1 before starting L2. Do not combine sprints.

---

### ⚠️ TOP PRIORITY (Session BM) — Sprint L2: Readable Docs + Discoverable Weights

Wire real pgvector retrieval into H1/H2 replay path. Add document modal (click evidence card → full doc text). Add weight provenance panel (lr_base + physics band + citation + effective LR). Closes the cosine-sim·pgvector integrity-label violation. See SESSION_BL_ARCHITECTURE_REVIEW.md §UI Requirements.

**Verification:** After deploy, H1/H2 scenario replay should show evidence cards that open a modal with readable document text and the LR provenance panel.

---

### ✅ SESSION BK — Cost controls deployed (no app code change)
- MCP gdc-second-opinion DISABLED (Vertex AI billing). Toggle: `~/mcp-enable.sh` / `~/mcp-disable.sh`
- GPU node pool resized 3→0 (was idle ~$78/day). gpu-start.sh/gpu-stop.sh now resize node pool
  (root cause: standard GKE, not Autopilot — deployment scale-down never removed the VMs)
- LLM/RAG architecture assessment written (docs/LLM_RAG_ARCHITECTURE_ASSESSMENT.md)

### ✅ SPRINT H2-REPLAY — Paraffin/Wax Deposition Scenario — COMPLETE (Session BJ)
- Backend `/api/h2/scenario-replay` rewritten; 3 static docs; PIP 1183→1577 PSI verified live

### ✅ SPRINT H3-F — Selectable Binding Constraint + RAG Provenance — COMPLETE (Session BI)

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED — PARAFFIN | `sha256:1be9477f` — session BG |
| H2 Scenario Replay | ✅ DEPLOYED — PARAFFIN | `sha256:0da67ee9` — session BJ |
| Sprint H3-E: pad-level dashboard | ✅ DEPLOYED | `sha256:42b044d2` — session BH |
| Sprint H3-F: selectable constraints + RAG | ✅ DEPLOYED | `sha256:6d79a17d` — session BI |
| H3 briefing panel Hz values (66.0, 65.5, 59.7) | ⚠️ HARDCODED | From live API 2026-06-11 — update if _PAD_ALPHA_WELL_PARAMS changes |
| H1/H2 "cosine sim · pgvector (< 2s)" labels | ⚠️ INTEGRITY VIOLATION | Retrieval not executing in replay path — closed by Sprint L1+L2 |
| H1 `_BAYES_FINDINGS` LRs in code | ✅ RESOLVED | Sprint L1 — weights in field_intel DB, get_db() read path live · sha256:07cef48e |
| H1_METHODOLOGY.md LRs 8/5/3/2→99.6% | ⚠️ STALE DOC | Code uses 3/2/1.6/1.4→93% — fix after L1 |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended 2026-06-12 · toggle: ~/mcp-disable.sh / ~/mcp-enable.sh |
| Pad Alpha RAG corpus (10 docs) | ✅ SEEDED | Session BI — 3 constraint-setting + 7 background in rag_documents |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call** (or use Python splice for large functions)
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,977 lines · `index.html` ~3,640 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (always)
- **No build/push/deploy without user walkthrough and verification**
- MCP gdc-second-opinion: ⛔ DISABLED (billing suspended 2026-06-12)
  - To re-enable: `~/mcp-enable.sh` → reconnect in Cline MCP sidebar
  - To disable again: `~/mcp-disable.sh` (run immediately after use)
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
- **Token-efficient edits:** Use Python splice scripts for large function replacements
- **GPU:** Single L4 node (~$1.09/hr) sufficient for Gemma 4 showcase. Resize `gpu-start.sh` `--num-nodes 1` per zone → 1 total. Never scale up without announcing cost.
