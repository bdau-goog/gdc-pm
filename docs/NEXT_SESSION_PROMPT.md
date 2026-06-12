# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date: June 12, 2026 (Session BN — Sprint L3 deployed)
**git head:** `e4349b8` — feat(sprint-l3): corpus expansion — 10 scenario RAG docs with noise mix
**fault-trigger-ui image:** `sha256:916bdc216a8a49be6766adc56dfa7ac76c2f3df7a2e8fe407e8545180e87032f`
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

**Actual at session-BN close:** fault-trigger-ui pod 1/1 Running · HTTP 200 · Sprint L3 verified live

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
### ✅ SPRINT L3 — Corpus Expansion — COMPLETE (Session BN)

**What L3 delivered:**
- `_L3_SCENARIO_RAG_DOCS` — 10 new docs in `rag_documents` with SentenceTransformer embeddings
- H1 set: Tour 2 Shift Note (GVF), Separator GOR Test, OEM GVF Bulletin (HIGH) + Megger Test, Water Disposal (NOISE)
- H2 set: Chemical Service Log (hot-oil 52d overdue), Fluid PVT (WAT 118°F), ESP Pull Record (bearings NORMAL) (HIGH) + VFD Config, Rig Schedule (NOISE)
- H1 retrieval: OEM GVF bulletin now #2 at **0.5351** (vs generic ESP manual at 0.4096) — clear discrimination
- H2 retrieval: Chemical Treatment Log now **#1 at 0.3790** (was thermal memo at 0.3556)
- Noise docs not appearing in top-3 for either scenario query — verified live

---

### ⚠️ TOP PRIORITY (Session BO) — Sprint L4: Gemma Extraction + Path A Evidence-Strength Modulation

**Goal:** GPU showcase — Gemma 4 reads the retrieved L3 documents and:
1. **Extraction:** Emits structured findings (F1/F2/F3/F4) from retrieved doc text — replacing hardcoded _H1_BAYES_SEED_DOCS labels with Gemma-generated extraction
2. **Evidence-strength modulation (Path A):** Classifies assertion strength (emphatic/qualified/absent) from doc text → adjusts LR within physics-anchored `lr_min`/`lr_max` bands in `field_intel`
3. Gemma never assigns a weight; it moves within a range a domain engineer set and cited

**Requires:** `./scripts/gpu-start.sh` (announces ~$1.09/hr before running). Single L4 node sufficient for Gemma 4.

**Sprint sequence:**
| Sprint | Deliverable | GPU? |
|---|---|---|
| **L1** | Weight-metadata migration + `_bayes_discriminate` DB refactor | No ✅ |
| **L2** | Readable-doc modal + discoverable weight provenance panel (H1 + H2) | No ✅ |
| **L3** | Corpus expansion — 10 H1/H2 `rag_documents` (3 HIGH + 2 NOISE per scenario) | No ✅ |
| **L4** | Gemma extraction + Path A evidence-strength modulation (GPU showcase only) | Single L4 ~$1.09/hr |

**Atomic-fix discipline:** Deploy and verify L4 before starting any other sprint.

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
| H1/H2 pgvector retrieval | ✅ REAL + DISCRIMINATING | Sprint L3 — GVF bulletin #2 (0.535) for H1; paraffin log #1 (0.379) for H2 |
| H1 Bayesian provenance band | ✅ DEPLOYED | Sprint L2 — Band lr_min–lr_max · lr_source shown |
| H2 doc modals (click to read) | ✅ DEPLOYED | Sprint L2 — full text in modal |
| H1_METHODOLOGY.md LRs 8/5/3/2→99.6% | ⚠️ STALE DOC | Code uses 3/2/1.6/1.4→93% — fix after L4 |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended 2026-06-12 · toggle: ~/mcp-disable.sh / ~/mcp-enable.sh |
| Pad Alpha RAG corpus (10 Pad Alpha + 10 L3 scenario docs) | ✅ SEEDED | Session BN — 38 total rag_documents rows |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call** (or use Python splice for large functions)
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~7,680 lines · `index.html` ~3,660 lines · `app.js` ~2,310 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (always)
- **No build/push/deploy without user walkthrough and verification**
- MCP gdc-second-opinion: ⛔ DISABLED (billing suspended 2026-06-12)
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
- **GPU:** Single L4 node (~$1.09/hr) sufficient for Gemma 4 showcase. Never scale up without announcing cost.
