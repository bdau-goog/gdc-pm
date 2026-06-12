# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 12, 2026 (Session BI — Sprint H3-F: selectable constraint + RAG provenance deployed)
**git head:** `073cc1a` (feat(h3-f): selectable binding constraint + RAG provenance)
**fault-trigger-ui image:** `sha256:6d79a17d9e1edc014b60eb1cf04faba749db72d9a4d4146d75da490a09a92688`
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
- rag_docs: **28** (18 original + 10 Pad Alpha constraint docs seeded at startup)

**Actual at session-BI close:** pod `fault-trigger-ui` 1/1 Running · HTTP 200 · all 3 constraint modes verified live · 10 Pad Alpha docs in rag_documents

**GPU discipline:** OFF by default. `./scripts/gpu-start.sh` only at explicit LLM-test step (~$0.65/hr). Always paired with `./scripts/gpu-stop.sh`.

**⚠️ REGISTRY NOTE:** Artifact Registry only — NOT gcr.io.
```bash
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl set image deployment/fault-trigger-ui -n gdc-pm \
  fault-trigger-ui=us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui@sha256:<digest>
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm
```

---

## STEP 2: Read DEMO_MASTER.md

```bash
cat /home/brian/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Next Implementation Tasks (in order)

### ✅ SPRINT H3-F — Selectable Binding Constraint + RAG Provenance — COMPLETE (Session BI)

What was done:
- Backend `?constraint=gas|thermal|rul` param added to `/api/vizier/optimize`
  - **gas**: lowest-GOR wells get Hz priority (oil/gas efficiency maximized)
  - **thermal**: highest thermal margin first (wells furthest from burnout run hardest)
  - **rul**: highest RUL first (aging pumps protected; fresh pumps absorb load)
- `constraint_doc` returned: AlloyDB pgvector semantic search retrieves the constraint-setting document per mode
- `_PAD_ALPHA_CONSTRAINT_DOCS`: 10 docs seeded idempotently at startup (3 constraint-setting + 7 background)
- Frontend: 3 toggle buttons (color-coded per mode), dynamic BINDING label, RAG provenance card below uplift card
- Verified live: all 3 modes return correct RAG doc, correct binding flag, allocation reorders visibly

---

### SPRINT H2-REPLAY — Update scenario replay to paraffin scenario (next priority)

Backend `/api/h2/scenario-replay` still returns workover-fluid-incompatibility data. Need to:
1. Update trajectory generation (efficiency+vib signature for paraffin restriction)
2. Update verdict banner text and doc reveals (vendor log, PVT, pull record)
3. Remove Gemma dependency for static docs

---

### SPRINT P4 — H1 Batch B date-templating (low priority)
- Sonic log / shift note in `field_intel` seeded at inject time have static text dates
- Template to `today − offset` at startup (same pattern as H2 docs)

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 backend endpoint | ⚠️ STALE | Still workover-fluid scenario — needs H2-REPLAY sprint |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED — PARAFFIN | `sha256:1be9477f` — session BG |
| H2 Scenario Replay verdict | ⚠️ STALE | Still shows "Elastomer seal degradation" — old scenario |
| Sprint H3-E: pad-level dashboard | ✅ DEPLOYED | `sha256:42b044d2` — session BH |
| Sprint H3-F: selectable constraints + RAG | ✅ DEPLOYED | `sha256:6d79a17d` — session BI |
| H3 briefing panel Hz values (66.0, 65.5, 59.7) | ⚠️ HARDCODED | From live API 2026-06-11 — update if _PAD_ALPHA_WELL_PARAMS changes |
| H3 Panel 3 cash figure | ✅ FIXED | Was hardcoded $369,225 — now live `optJointOptimal.uplift_cash_90d` |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| STAKEHOLDER_BRIEF.md user review | ⚠️ PENDING | H2 physics error now fixed |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |
| Pad Alpha RAG corpus (10 docs) | ✅ SEEDED | Session BI — 3 constraint-setting + 7 background in rag_documents |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,840 lines · `index.html` ~3,640 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (always)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
