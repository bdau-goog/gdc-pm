# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session BF — §3 APM calibration + Lift IQ hostile-pass · Session BE: Sprint H3-D docs + Panel 1 layout fixes + H2 physics invalidation)
**git head:** `d000c52` (docs(session-bf): §3 APM two-tier calibration; Lift IQ/sovereignty hostile-pass rewording)
**fault-trigger-ui image:** `sha256:0aca289c78726f784fb8384e5866c18065c0ade08981b5b56300901e19c8693e`
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

**Actual at session-BF close:** cluster unchanged (docs-only session, no deploy) · field_intel=11 · rag_docs=18 ✅

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

### ⚠️ SPRINT H2-REFRAME — Full H2 scenario replacement (TOP PRIORITY — blocking)

**H2 is currently on screen with a fatal physics error that must be corrected before any demo.**

**The defect:** The current H2 scenario claims GDC recommends a "~$8k–$15k flush + reseal" as an alternative to a "~$70k–$100k pump pull." This is physically impossible — **an ESP protector/seal section cannot be resealed in place.** It is integral to the downhole string at depth. Any correction to a protector seal **requires pulling the completion with a workover rig.** Gemini search confirmed this unambiguously (Session BE). The "$8k–$15k" cost number is fictitious; the economic comparison is incoherent.

**The approved replacement scenario (H2-NEW): Paraffin/Wax deposition mimicking bearing wear**

- **Asset:** Same ESP on a waxy Permian carbonate producer (Permian Basin crude is paraffin-rich; WAT ≈ 110–122°F; Gemini-confirmed)
- **Telemetry signature:** Gradually rising vibration + Amps, declining motor efficiency — indistinguishable from mechanical bearing wear on a 4-sensor string (physically correct: restricted tubing increases backpressure and torque)
- **APM routes to:** Mechanical bearing wear → pump pull → full investigation (~$70k–$100k)
- **The real cause:** Well A-3's 90-day hot-oil paraffin treatment (a routine surface chemical truck job) is 52 days overdue. It is NOT forgotten by the operator — it was delayed by the chemical vendor (billing dispute, truck shortage). The delay is in a vendor portal/email thread, not in SCADA. Combined with alarm fatigue (RTOC is seeing false positives on 14 other wells that week; nobody is chasing the hot-oil PM).
- **GDC context fusion:** Retrieves (1) Chemical vendor service log (T−142 days, 90-day schedule overdue by 52 days); (2) Fluid lab PVT report (confirms high WAT crude chemistry); (3) Prior pull record (bearings were normal 18 months ago — eliminates mechanical wear hypothesis)
- **Verdict:** "Paraffin wax deposition — NOT bearing wear. Dispatch hot-oiler, do NOT pull."
- **Correct action:** Surface hot-oil truck or chemical solvent flush down the annulus. ~$3k–$6k. Well returns to nominal. **Pull averted completely. No workover required.**
- **5-gate survival check:** Discrete event ✅ (treatment date/delay) · Off-sensor ✅ (wax thickness downhole unmeasured) · APM mis-routes ✅ (bearing wear hypothesis) · Common/material ✅ (endemic Permian problem) · Remedy feasible ✅ (surface truck, no pull)

**SME context from Bill Barna (production engineer with extensive Permian experience):**
> *"Many operators have poor programs. Often, there are so many false positives, nobody believes the system. All of the problems you listed happen."*
This validates both the alarm-fatigue angle AND the missed/deferred PM angle as real, common O&G realities. Not a straw man — the operator's processes can be solid and this still happens.

**Key design principle (NO STRAW MAN rule preserved):** The operator did not negligently forget. A third-party vendor delay + alarm fatigue created a data gap between the CMMS service record and the live RTOC decision-maker. GDC closes that silo. The operator looks operationally competent; the gap is structural, not behavioral.

**Session BF completed (docs-only):** §3 APM two-tier calibration done. Alarm fatigue confirmed as H2 named pain point. Buyer = NOC-leaning (sovereignty is load-bearing). Lift IQ rebuttals corrected in §3 rejected-claims + §9. **H2 code still blocking.**

**What this session needs:**
1. Run `gdc-second-opinion` hostile-engineer pass on the paraffin scenario (full 5-gate + remedy feasibility)
2. If passes: rewrite DEMO_MASTER §5 with new scenario spec
3. Rewrite H2 briefing (3 panels), scenario-replay GDC verdict copy, and STAKEHOLDER_BRIEF §H2
4. Update CLAIM_LEDGER (retire old H2 rows; add new ones)
5. Deploy new UI — backend endpoint is a lower priority for now (briefing + verdict copy first)

---

### SPRINT H3-E — Pad-level dashboard (post-briefing, medium priority)

**The gap:** The H3 briefing (3 panels, Session H3-C) correctly tells the 6-well Pad Alpha story (gas ceiling, GOR-ranked allocation, +77.9 bbl/d uplift). But when the CTA fires `runVizierOptimize()` and drops out of `h3BriefingMode`, the user lands on the **legacy single-well dashboard** — three scalar VFD Hz cards, a scalar Pareto chart (avg_Hz x-axis), and a trial table with one Hz column. This is incoherent with the briefing.

**The fix:** Replace the 3 backward-compat value cards with (1) a **6-well per-well allocation table** (Well · GOR · SCADA 50 Hz · GDC optimal Hz · Δ) sourced from `wells[]` + `joint_optimal`; (2) a **field uplift card** (+77.9 bbl/d · +$369,225/90d · gas 7.9999/8.0 MMscfd) from `joint_optimal` + `constraint_stack`. Data is already in the API response — this is frontend-only work. Vizier pareto chart can stay.

---

### SPRINT P4 — H1 Batch B date-templating (small, code change — lower priority)
- Sonic log / shift note / GOR lab report in `field_intel` have hardcoded 2025 dates
- Template to `today − offset` at startup (same pattern as H2 docs)
- Find affected rows: `grep -n "2025" gke/fault-trigger-ui/app.py | grep -i "field_intel\|sonic\|shift\|gor\|lab"`

---

### SPRINT STAKEHOLDER-REVIEW — user review of STAKEHOLDER_BRIEF.md
- `docs/STAKEHOLDER_BRIEF.md` is written and committed (Session BE)
- **NOTE:** The H2 paragraph in this brief also contains the physics error ("flush and reseal") — it must be updated as part of the H2-REFRAME sprint before this brief is shared with any customer

---

## H3-D Technical Notes (Session BE)

**What was written (docs only — no code, no deploy):**

**DEMO_MASTER §6 rewrite:** Complete field-level spec replacing the old single-pump VFD story. Now covers:
- 6-well Pad Alpha joint optimization narrative arc (Discern→Classify→Optimize lands at the field)
- Three binding/tracked constraints per well (gas ceiling, thermal polynomial, RUL horizon)
- Live Vizier result table (A-3/A-6 at 66.0 Hz, A-5 at 59.7 Hz, +77.9 bbl/d, +$369,225/90d)
- LP-optimal vs. GP-Bandit role distinction (both shown, roles honest)
- Edge-enforces safety explanation (outage-immune, no public-cloud dependency for decision)
- 7 H3 Claim Ledger rows (all SURVIVES per Session BD red-team)

**STAKEHOLDER_BRIEF.md (new file):** ~1,800-word non-technical executive document. Sections:
1. What we built (H1/H2/H3 — plain English, one paragraph each)
2. The Problem Each Horizon Solves (table: problem / delivery / avoids)
3. Honest relationship with SCADA (three tiers in plain language, no overclaiming)
4. Same capability in other industries (P&E / Manufacturing / Mining table)
5. Why "inside the perimeter" matters (IEC 62443 / data residency / governance & IP)
- All cost figures from CLAIM_LEDGER; estimates labeled; no 🔴 NEEDS-EXPERT items displayed as hard facts
- No LP/Bayesian/GP/pgvector terminology on screen
- Closing quote from DEMO_MASTER §9 spine sentence (locked wording)

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Briefing — all 6 panels | ✅ DEPLOYED | Session AQ |
| H1 Scenario replay | ✅ DEPLOYED | Session AP |
| H2 backend endpoint | ✅ DEPLOYED | `sha256:cd46caa8` — session AX |
| H2 Briefing panels (3 panels) | ✅ DEPLOYED | `7673efd` — session AY |
| H2 Scenario Replay UI | ✅ DEPLOYED | `866522f` — session BA |
| Sprint F0: "GDC Operations Intelligence" header | ✅ DEPLOYED | `e85f9b9`+`81c3a5b` — session BB |
| Sprint H3-A: thermal model 4-feature fix | ✅ DEPLOYED | `81c3a5b` — session BB |
| Sprint H3-B: N-well field Vizier optimization | ✅ DEPLOYED | `84e1b5f` — session BC · 6-well LP-optimal, gas ceiling 8.0 MMscfd |
| Sprint H3-C: 3-panel H3 briefing | ✅ DEPLOYED | `662166c` — session BD |
| **Sprint H3-D: DEMO_MASTER §6 + STAKEHOLDER_BRIEF.md** | **✅ COMMITTED** | **Session BE — docs only, no deploy needed** |
| **§3 APM two-tier calibration + Lift IQ hostile-pass** | **✅ COMMITTED** | **Session BF — docs only, `d000c52` · 5–15% adoption range · Lift IQ rebuttals corrected** |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| STAKEHOLDER_BRIEF.md user review | ⚠️ PENDING | Sprint STAKEHOLDER-REVIEW — confirm tone/claims |
| **esp_thermal.ubj — XGBoost version mismatch** | **✅ RESOLVED** | **Session BB: physics polynomial used directly** |
| **H2 SCENARIO — PHYSICS ERROR (blocking)** | **❌ MUST FIX** | **"Flush + reseal in-place" is physically impossible for a downhole ESP protector — always requires a pull. Full H2 scenario replacement required. See Sprint H2-REFRAME above.** |
| SPE papers cited (SPE-174536, SPE-170776) | ⚠️ UNVERIFIED | Not yet pulled — do not cite as hard facts |
| 51% ESP failures = operational factors | ✅ ATTRIBUTED | 2014 SPE Artificial Lift Conference survey (Gemini-verified) |
| MCP gdc-second-opinion | ✅ WORKING | gemini-2.5-flash, Vertex AI ADC, gdc-pm-v2 |
| H3 briefing panel Hz values (66.0, 65.5, 59.7) | ⚠️ HARDCODED | From live API 2026-06-11 — update if _PAD_ALPHA_WELL_PARAMS changes |

---

## Constraints (Permanent)

- `terraform/gke.tf` must NOT be applied
- No `browser_action` (SSH remote, no browser)
- **Batch all edits to same file in ONE `replace_in_file` call**
- `feature-trio-clean` branch — do NOT merge to main
- `app.py` ~6,900 lines · `index.html` ~3,400 lines · `app.js` ~2,300 lines — grep first, targeted reads only
- **Wireframes → sign-off → HTML** (always)
- **No build/push/deploy without user walkthrough and verification**
- Gemini tools (gemini_search, gemini_second_opinion) on autoApprove — use freely for fact-checking
- **Ask inline questions — no option lists** (ask_followup_question options array causes display issues)
- **Keep text before tool calls short**
- **Deploy sequence:** `docker build` → `docker push` → `kubectl set image ... @sha256:<digest>` → `kubectl rollout status` (Artifact Registry, NOT gcr.io)
