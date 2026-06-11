# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session BG — H2 paraffin scenario, docs + briefing deployed · Session BF: §3 APM calibration + Lift IQ hostile-pass)
**git head:** `f5f30b6` (feat(h2-briefing): paraffin scenario — 3-panel rewrite + v-else layout fix)
**fault-trigger-ui image:** `sha256:1be9477f39daa975bc8a320c9e7164d9962d669666e54e950dce28c75cff6569`
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected (dev default — GPU OFF):**
- 6 pods 1/1 Running + 3 prune CronJob Completed (ollama pod ABSENT — correct)
- ollama replicas: **0** · `ollama_online: False` — NOT a problem. Do NOT scale up.
- field_intel: **9–12** · rag_docs: **18**

**Actual at session-BG close:** cluster healthy · new pod `fault-trigger-ui-f698b6955-j7rmx` 1/1 Running · API responding 200 OK

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

### ✅ SPRINT H2-REFRAME — COMPLETE (Session BG)

H2 physics error is now fixed on screen. What was done:
- DEMO_MASTER §5 rewritten to paraffin/wax deposition scenario (5-gate pass, gdc-second-opinion hostile pass)
- CLAIM_LEDGER: old workover-fluid rows retired (ARCHIVED); H2-PAR-1 through H2-PAR-7 added (incl. PIP rebuttal)
- STAKEHOLDER_BRIEF §H2: physics-error paragraph and table row corrected
- index.html: 3 briefing panels rewritten + `<template v-else>` layout fix deployed
- Commits: `dad8c71` (docs) + `f5f30b6` (HTML) · Image: `sha256:1be9477f`

**Remaining H2 work (lower priority):**
- H2 scenario replay verdict banner still says "Elastomer seal degradation" (old scenario) — backend `/api/h2/scenario-replay` not yet updated to paraffin scenario. Briefing (default view) is correct. Replay is secondary.

---

### SPRINT H3-E — Pad-level dashboard (medium priority)

**The gap:** H3 briefing (3 panels) correctly tells the 6-well Pad Alpha story. When CTA fires `runVizierOptimize()` and drops out of `h3BriefingMode`, the user lands on the **legacy single-well dashboard** — 3 scalar VFD Hz cards, avg-Hz pareto chart x-axis, single-Hz trial table. This is incoherent with the 6-well briefing.

**The fix:** Replace 3 scalar Hz cards with:
1. **Field uplift card** (+77.9 bbl/d · +$369,225/90d · gas 7.9999/8.0 MMscfd) from `joint_optimal` + `constraint_stack`
2. **6-well per-well allocation table** (Well · GOR · SCADA Hz · GDC optimal Hz · Δ · Role) sourced from `wells[]` + `joint_optimal`

Data is already in the API response — frontend-only work. Vizier pareto chart stays.

---

### SPRINT H3-F — Selectable binding constraint + RAG provenance (new, medium priority)

**User request (Session BG):** Want ability to select which of the 3 constraints is binding, and show constraint-setting documents (RAG provenance) for each.

**Backend change:** Add `?constraint=gas|thermal|rul` param to `/api/vizier/optimize`. Each limiter produces a different optimal allocation (proving the solver is real):
- `gas` (current default): lowest-GOR wells get Hz priority
- `thermal`: wells with best cooling (high water cut, low intake temp) run harder
- `rul`: wells with highest RUL base push hardest; aging pumps protected

**Frontend change:** Constraint selector UI (3 toggle buttons in Panel 2 / dashboard) that re-runs Vizier with selected constraint. Each selection shows the document that SETS the constraint number (RAG provenance — pgvector retrieval, no GPU needed).

**Document corpus:** Seed ~10-12 doc Pad Alpha corpus (3 constraint-setting docs + ~7-9 supporting/distractor docs). All must pass G1-G6 gate — draft for user sign-off before seeding.

---

### SPRINT H2-REPLAY — Update scenario replay to paraffin scenario (lower priority)

Backend `/api/h2/scenario-replay` still returns workover-fluid data. Need to:
1. Update trajectory generation (efficiency+vib signature for paraffin restriction)
2. Update verdict banner text and doc reveals (vendor log, PVT, pull record)
3. Remove Gemma dependency for static docs (2 of 3 are static seeds)

---

### SPRINT P4 — H1 Batch B date-templating (small, code change — lower priority)
- Sonic log / shift note / GOR lab report in `field_intel` have hardcoded 2025 dates
- Template to `today − offset` at startup (same pattern as H2 docs)
- Find affected rows: `grep -n "2025" gke/fault-trigger-ui/app.py | grep -i "field_intel\|sonic\|shift\|gor\|lab"`

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 backend endpoint | ✅ DEPLOYED | `sha256:cd46caa8` — session AX (old scenario — needs H2-REPLAY sprint) |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED — PARAFFIN | `sha256:1be9477f` — session BG · paraffin scenario, v-else layout fix |
| H2 Scenario Replay verdict | ⚠️ STALE | Still shows "Elastomer seal degradation" — old scenario. Briefing is primary view (default). |
| Sprint F0: "GDC Operations Intelligence" header | ✅ DEPLOYED | `e85f9b9`+`81c3a5b` — session BB |
| Sprint H3-A: thermal model 4-feature fix | ✅ DEPLOYED | `81c3a5b` — session BB |
| Sprint H3-B: N-well field Vizier optimization | ✅ DEPLOYED | `84e1b5f` — session BC · 6-well LP-optimal, gas ceiling 8.0 MMscfd |
| Sprint H3-C: 3-panel H3 briefing | ✅ DEPLOYED | `662166c` — session BD |
| Sprint H3-D: DEMO_MASTER §6 + STAKEHOLDER_BRIEF.md | ✅ COMMITTED | Session BE — docs only |
| §3 APM two-tier calibration + Lift IQ hostile-pass | ✅ COMMITTED | Session BF — docs only, `d000c52` |
| H2-REFRAME docs + briefing | ✅ DEPLOYED | Session BG — `dad8c71` (docs) + `f5f30b6` (HTML) · `sha256:1be9477f` |
| H3 briefing panel Hz values (66.0, 65.5, 59.7) | ⚠️ HARDCODED | From live API 2026-06-11 — update if _PAD_ALPHA_WELL_PARAMS changes |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| STAKEHOLDER_BRIEF.md user review | ⚠️ PENDING | Sprint STAKEHOLDER-REVIEW — H2 physics error now fixed |
| esp_thermal.ubj — XGBoost version mismatch | ✅ RESOLVED | Session BB: physics polynomial used directly |
| H2 SCENARIO — PHYSICS ERROR | ✅ FIXED IN BRIEFING | Briefing rewritten to paraffin. Scenario replay backend still old (lower priority). |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,900 lines · `index.html` ~3,590 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (always)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
