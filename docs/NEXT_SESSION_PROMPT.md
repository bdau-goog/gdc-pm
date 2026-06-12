# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date: June 12, 2026 (Session BM — Sprint L2 deployed)
**git head:** `e554977` — feat: Sprint L2 — real pgvector retrieval + doc modals + LR provenance bands
**fault-trigger-ui image:** `sha256:e1b4ed84e7d1bdedc8e6ec657f5b5acda2e2ea7a057a79173cbaeb8cfc30644e`
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

**Actual at session-BM close:** fault-trigger-ui pod 1/1 Running · HTTP 200 · Sprint L2 verified live

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

---

## STEP 3: Next Implementation Task

### ✅ SPRINT L1 — Weight Metadata Migration — COMPLETE (Session BL)
### ✅ SPRINT L2 — Readable Docs + Discoverable Weights — COMPLETE (Session BM)

**What L2 delivered:**
- `_fetch_rag_sections()` — real pgvector cosine similarity search on `rag_documents`
- H1 `rag_sections[2].similarity` = **0.3794** (was hardcoded "cosine sim 0.82")
- H2 `rag_sections` = real scores 0.3556 / 0.3155 / 0.2994
- H2 doc cards: click → full text modal (Chemical Service Log, PVT Report, Prior Pull Record)
- H1 OEM doc 3: click → modal showing retrieved rag_documents content + real similarity
- H1 Bayesian evidence table: provenance band under each row: `Band lr_min–lr_max · lr_source · ⓘ weight in field_intel DB`
- H2 label: "FIELD DOCUMENT CORPUS — AlloyDB on-cluster" (honest; not "pgvector (< 2s)")

---

### ⚠️ TOP PRIORITY (Session BN) — Sprint L3: Corpus Expansion

**Goal:** Add more H1/H2 `field_intel` documents (including some noise/neutral docs) so retrieval visibly discriminates. Makes the "pgvector searches and finds relevant docs" claim more compelling.

**L3 scope:**
1. Seed 6–10 additional `field_intel` docs for `__h1_bayes_corpus__` (mix of supporting + noise)
2. Seed additional H2 paraffin scenario docs into `field_intel` (e.g., well history, shift notes pre-onset)
3. Verify pgvector retrieval now returns a discriminating mix (relevant docs score higher than noise)
4. Update H1 header: since `rag_sections` now returns real docs, "RETRIEVED CONTEXT — AlloyDB pgvector (< 2s)" label on H1 is now **honest** — no change needed.

**Sprint sequence:**
| Sprint | Deliverable | GPU? |
|---|---|---|
| **L1** | Weight-metadata migration + `_bayes_discriminate` DB refactor | No ✅ |
| **L2** | Readable-doc modal + discoverable weight provenance panel (H1 + H2) | No ✅ |
| **L3** | Corpus expansion — more H1/H2 `field_intel` docs (some noise) | No |
| **L4** | Gemma extraction + Path A evidence-strength modulation (GPU showcase only) | Single L4 ~$1.09/hr |

**Atomic-fix discipline:** Deploy and verify L3 before starting L4. Do not combine sprints.

---

### ✅ SESSION BK — Cost controls deployed (no app code change)
### ✅ SPRINT H2-REPLAY — Paraffin/Wax Deposition Scenario — COMPLETE (Session BJ)
### ✅ SPRINT H3-F — Selectable Binding Constraint + RAG Provenance — COMPLETE (Session BI)

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
| H3 briefing panel Hz values (66.0, 65.5, 59.7) | ⚠️ HARDCODED | From live API 2026-06-11 — update if _PAD_ALPHA_WELL_PARAMS changes |
| H1/H2 "cosine sim · pgvector (< 2s)" labels | ✅ RESOLVED | Sprint L2 — real pgvector retrieval active · sha256:e1b4ed84 |
| H1 `_BAYES_FINDINGS` LRs in code | ✅ RESOLVED | Sprint L1 — weights in field_intel DB |
| H1 Bayesian provenance band | ✅ DEPLOYED | Sprint L2 — Band lr_min–lr_max · lr_source shown |
| H2 doc modals (click to read) | ✅ DEPLOYED | Sprint L2 — full text in modal |
| H1_METHODOLOGY.md LRs 8/5/3/2→99.6% | ⚠️ STALE DOC | Code uses 3/2/1.6/1.4→93% — fix after L3 |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended 2026-06-12 · toggle: ~/mcp-disable.sh / ~/mcp-enable.sh |
| Pad Alpha RAG corpus (10 docs) | ✅ SEEDED | Session BI — 3 constraint-setting + 7 background in rag_documents |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call** (or use Python splice for large functions)
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~7,320 lines · `index.html` ~3,660 lines · `app.js` ~2,310 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (always)
- **No build/push/deploy without user walkthrough and verification**
- MCP gdc-second-opinion: ⛔ DISABLED (billing suspended 2026-06-12)
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
- **GPU:** Single L4 node (~$1.09/hr) sufficient for Gemma 4 showcase. Never scale up without announcing cost.
