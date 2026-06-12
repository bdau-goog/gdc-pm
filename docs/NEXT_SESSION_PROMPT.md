# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 12, 2026 (Session BK — cost controls + LLM/RAG architecture assessment)
**git head:** see `git log` (Session BK docs commit)
**fault-trigger-ui image:** `sha256:0da67ee966fa7f5cfa540c2f101d1d673ba62d57a9fb8f8d2b93d6e1cece8e7f`
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

## STEP 3: Next Implementation Task

### ⚠️ TOP PRIORITY (Session BL) — L3 / LLM Architecture Impact Exploration

Read `docs/LLM_RAG_ARCHITECTURE_ASSESSMENT.md` FIRST. Key decisions pending:
1. Demo narrative: live-inject Gemma feed vs Briefing+Replay canonical path
2. INTEGRITY: H1/H2 replay show "cosine sim · pgvector" labels but do NOT run live
   retrieval (hardcoded HTML / static templates). Resolve: wire real retrieval OR
   soften labels. (No Silent Lies rule.)
3. DEMO_MASTER §3: make System A (retrieval/CPU/real) vs System B (Gemma/GPU/generation)
   distinction explicit.

### ✅ SESSION BK — Cost controls deployed (no app code change)
- MCP gdc-second-opinion DISABLED (Vertex AI billing). Toggle: `~/mcp-enable.sh` / `~/mcp-disable.sh`
- GPU node pool resized 3→0 (was idle ~$78/day). gpu-start.sh/gpu-stop.sh now resize node pool
  (root cause: standard GKE, not Autopilot — deployment scale-down never removed the VMs)
- LLM/RAG architecture assessment written (docs/LLM_RAG_ARCHITECTURE_ASSESSMENT.md)

### ✅ SPRINT H3-F — Selectable Binding Constraint + RAG Provenance — COMPLETE (Session BI)

### ✅ SPRINT H2-REPLAY — Paraffin/Wax Deposition Scenario — COMPLETE (Session BJ)

What was done:
- Backend `/api/h2/scenario-replay` rewritten for paraffin_wax_restriction scenario
  - Physics: PIP rises (1183→1577 PSI) — hydraulic restriction (API RP 11S system curve)
  - Temp stays flat (+5°F over 8 weeks) — confirms hydraulic, not thermal/mechanical
  - VIB + AMPS rise → ISA-18.2 HI alarm (same observable pattern as old scenario)
  - EFF declines (pump off BEP)
  - 3 static docs: vendor_service_log + pvt_report + pull_record (no Gemma dependency)
  - Returns `psi[]` + `temp[]` arrays (previously missing from payload)
- Frontend: 8 blocks updated (physics panel, verdict banner, GDC Zone 1, action cards, doc stack, SCADA outcomes)
- VIDEO_SCRIPT.md H2 narration updated to paraffin story
- Verified live: scenario=paraffin_wax_restriction, PIP 1183→1577 PSI, temp flat, health_ok=True

---

### ✅ SPRINT P4 — H1 Batch B date-templating — ALREADY COMPLETE (verified Session BJ)
All 3 H1 document modals already use `{{ new Date().toLocaleDateString(...) }}` (dynamic):
- Shift Note modal (index.html line 1487) — ✅ new Date()
- Sonic Log modal (index.html line 1511) — ✅ new Date()
- GOR Lab modal (index.html line 1544) — ✅ new Date()
Inject-time field_intel docs use relative language only (no hardcoded calendar dates).
This was fixed in Session X (Batch B). NEXT_SESSION_PROMPT entry was stale.

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED — PARAFFIN | `sha256:1be9477f` — session BG |
| H2 Scenario Replay | ✅ DEPLOYED — PARAFFIN | `sha256:0da67ee9` — session BJ |
| H2 VIDEO_SCRIPT narration | ✅ UPDATED — PARAFFIN | `d58073d` — session BJ |
| Sprint H3-E: pad-level dashboard | ✅ DEPLOYED | `sha256:42b044d2` — session BH |
| Sprint H3-F: selectable constraints + RAG | ✅ DEPLOYED | `sha256:6d79a17d` — session BI |
| H3 briefing panel Hz values (66.0, 65.5, 59.7) | ⚠️ HARDCODED | From live API 2026-06-11 — update if _PAD_ALPHA_WELL_PARAMS changes |
| H3 Panel 3 cash figure | ✅ FIXED | Was hardcoded $369,225 — now live `optJointOptimal.uplift_cash_90d` |
| H1 static seed date-templating | ✅ ALREADY DONE | new Date() in all 3 modals — verified Session BJ |
| STAKEHOLDER_BRIEF.md user review | ⚠️ PENDING | H2 physics error now fixed in all UIs |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |
| MCP gdc-second-opinion | ⛔ DISABLED | Billing suspended 2026-06-12 · toggle: ~/mcp-disable.sh / ~/mcp-enable.sh |
| Pad Alpha RAG corpus (10 docs) | ✅ SEEDED | Session BI — 3 constraint-setting + 7 background in rag_documents |
| H2 endpoint response time | ⚠️ SLOW | ~35s for 80-step XGBoost loop — acceptable (spinner shown); no action needed |

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
  - Do NOT call gemini_search or gemini_second_opinion while disabled
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
- **Token-efficient edits:** Use Python splice scripts for large function replacements (avoids returning 7K-line files to context)
