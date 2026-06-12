# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 12, 2026 (Session BH — Sprint H3-E pad-level dashboard deployed)
**git head:** `840afe1` (feat(h3-e): pad-level dashboard — field uplift card + 6-well allocation table)
**fault-trigger-ui image:** `sha256:42b044d2bf16c32f7f6edd10fcd03ff7de60c06d1901d2cc3d693305dab67f01`
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Three Commands First

```bash
# 1. Verify isolation & context
source .env && echo "PROJECT=$GOOGLE_CLOUD_PROJECT KUBECONFIG=$KUBECONFIG" && kubectl config current-context

# 2. Token-efficient cluster health summary (prevents massive pod table clutter!)
source .env && kubectl get pods -n gdc-pm --no-headers 2>/dev/null | awk '{print $3}' | sort | uniq -c

# 3. Quick, non-blocking status check (2s max)
source .env && curl -s --max-time 2 http://gdc-pm.bdau.io/api/mlops/status | jq '{ollama_online, ollama_model}' 2>/dev/null || echo "MLOps status API offline/starting"
```

**Expected (dev default — GPU OFF):**
- 6 pods 1/1 Running + 3 prune CronJob Completed (ollama pod ABSENT — correct)
- ollama replicas: **0** · `ollama_online: False` — NOT a problem. Do NOT scale up.
- field_intel: **9–12** · rag_docs: **18**

**Actual at session-BH close:** pod `fault-trigger-ui-d8fd4bb6f-mghms` 1/1 Running · API HTTP 200 · 6 wells returning from `/api/vizier/optimize`

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

### ✅ SPRINT H3-E — Pad-Level Dashboard — COMPLETE (Session BH)

What was done:
- Replaced 3 old single-well scalar cards (SCADA Nominal/Vizier Optimal/Run-to-Failure) with:
  1. **PAD ALPHA · JOINT FIELD UPLIFT card** — 3-column: +77.9 bbl/d · +$179,928/90d · 7.9999/8.0 MMscfd (all live from API)
  2. **PAD ALPHA · 6-WELL OPTIMAL ALLOCATION table** — sorted by GOR asc, Baseline Hz vs GDC Optimal Hz vs Δ vs Role
- `app.js`: added `optWells`, `optJointOptimal`, `optIndependentBaseline`, `optConstraintStack` data props; `wellsSortedByGor` computed; populated in `runVizierOptimize()`
- **Integrity fix**: Panel 3 hardcoded `+$369,225` → live `optJointOptimal.uplift_cash_90d` expression
- Pareto chart and trial log table unchanged (still below the new cards)
- Commit: `840afe1` · Image: `sha256:42b044d2`

---

### SPRINT H3-F — Selectable Binding Constraint + RAG Provenance (next priority)

**User request (Session BG):** Select which of the 3 constraints is binding; show the constraint-setting document via RAG provenance for each.

**Backend change:** Add `?constraint=gas|thermal|rul` param to `/api/vizier/optimize`. Each produces distinct optimal allocation:
- `gas` (current default): lowest-GOR wells get Hz priority
- `thermal`: wells with best cooling (high water cut, low intake temp) run harder
- `rul`: wells with highest RUL base push hardest; aging pumps protected

**Frontend change:** 3 toggle buttons on dashboard (above the uplift card) that re-run Vizier with selected constraint. Show constraint-setting document retrieved from pgvector for each selection (no GPU needed).

**Document corpus:** Seed ~10-12 doc Pad Alpha corpus (3 constraint-setting docs + ~7-9 supporting/distractor docs). Draft for user sign-off before seeding.

---

### SPRINT H2-REPLAY — Update scenario replay to paraffin scenario (lower priority)

Backend `/api/h2/scenario-replay` still returns workover-fluid data. Need to:
1. Update trajectory generation (efficiency+vib signature for paraffin restriction)
2. Update verdict banner text and doc reveals (vendor log, PVT, pull record)
3. Remove Gemma dependency for static docs

---

### SPRINT P4 — H1 Batch B date-templating (small, lower priority)
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
| H2 Briefing panels (3 panels) | ✅ DEPLOYED — PARAFFIN | `sha256:1be9477f` — session BG |
| H2 Scenario Replay verdict | ⚠️ STALE | Still shows "Elastomer seal degradation" — old scenario. Briefing is primary view. |
| Sprint H3-E: pad-level dashboard | ✅ DEPLOYED | `sha256:42b044d2` — session BH · uplift card + 6-well table |
| Sprint H3-F: selectable constraints + RAG | ⏳ NEXT | Backend + frontend — see above |
| H3 briefing panel Hz values (66.0, 65.5, 59.7) | ⚠️ HARDCODED | From live API 2026-06-11 — update if _PAD_ALPHA_WELL_PARAMS changes |
| H3 Panel 3 cash figure | ✅ FIXED | Was hardcoded $369,225 — now live `optJointOptimal.uplift_cash_90d` · `840afe1` |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| STAKEHOLDER_BRIEF.md user review | ⚠️ PENDING | H2 physics error now fixed |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,834 lines · `index.html` ~3,613 lines · `app.js` ~2,295 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (always)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
