# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session BE — Sprint H3-D: DEMO_MASTER §6 field-level rewrite + STAKEHOLDER_BRIEF.md)
**git head:** `[commit after session-be wrap]`
**fault-trigger-ui image:** `sha256:a1c534d5c38b0dddda191a3627e5090466a2aedb621c6a897b14dfd2cf0c398b` (UNCHANGED — docs-only session)
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

**Actual at session-BE close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=11 · rag_docs=18 ✅

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

### SPRINT P4 — H1 Batch B date-templating (small, code change)
- Sonic log / shift note / GOR lab report in `field_intel` have hardcoded 2025 dates
- Template to `today − offset` at startup (same pattern as H2 docs — `_H2_SCENARIO_DATE` pattern in app.py)
- Find affected rows: `grep -n "2025" gke/fault-trigger-ui/app.py | grep -i "field_intel\|sonic\|shift\|gor\|lab"`
- Scope: app.py only — no HTML change needed
- Deploy after: docker build → push → rollout → smoke test H1 scenario

### SPRINT STAKEHOLDER-REVIEW — user review of STAKEHOLDER_BRIEF.md
- `docs/STAKEHOLDER_BRIEF.md` is written and committed (Session BE)
- Read it with the user, confirm tone and claims are correct
- Check any 🔴 NEEDS-EXPERT items against what's labeled on screen

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
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| STAKEHOLDER_BRIEF.md user review | ⚠️ PENDING | Sprint STAKEHOLDER-REVIEW — confirm tone/claims |
| **esp_thermal.ubj — XGBoost version mismatch** | **✅ RESOLVED** | **Session BB: physics polynomial used directly** |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — labeled as estimate on screen and in STAKEHOLDER_BRIEF.md |
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
