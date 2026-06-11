# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 11, 2026 (Session BD — Sprint H3-C 3-panel briefing deployed)
**git head:** `662166c` (feat(h3-briefing): Sprint H3-C — 3-panel H3 briefing + field optimization display)
**fault-trigger-ui image:** `sha256:a1c534d5c38b0dddda191a3627e5090466a2aedb621c6a897b14dfd2cf0c398b`
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

**Actual at session-BD close:** 6 pods Running · ollama=0 · ollama_online=False · field_intel=11 · rag_docs=18 ✅

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

### SPRINT H3-D: DEMO_MASTER §6 field-level spec rewrite
- Update §6 to reflect 6-well Pad Alpha joint optimization (N-well, gas ceiling, LP uplift)
- Replace single-pump VFD story with field-level story: Discern→Classify→Optimize arc lands at the field
- No code changes — docs only

### SPRINT P4 — H1 Batch B date-templating (small)
- Sonic log / shift note / GOR lab report in `field_intel` have hardcoded 2025 dates
- Template to `today − offset` at startup (same pattern as H2 docs)

---

## H3-C Technical Notes (Session BD)

**What was built:**
3-panel H3 briefing replacing the old "ⓘ Physics & Logic" toggle panel. All panels follow §4.5 Briefing Pattern Spec exactly.

**Panel 1 — The Opportunity:**
- 6-well GOR table (A-3 green/450 → A-5 amber/1350)
- Associated gas explanation: "every oil well produces gas whether you want it or not"
- Closing quote: "Not all barrels cost the same gas. A-3 produces 3× more oil per unit of gas budget than A-5."

**Panel 2 — The Tradeoff:**
- Constraint stack: gas ceiling (amber/BINDING, 8.0 MMscfd), motor winding temp (slate/not binding, 280°F from AlloyDB RAG), RUL horizon (slate/not binding, 90d)
- SCADA honest framing: "Without a cross-well optimizer, the safe default is uniform throttle — conservative, safe, but leaves 9,238 bbl/d short of what gas-efficient wells could carry."

**Panel 3 — The Optimization:**
- GOR-ranked setpoint table: A-3/A-6 run at 66.0 Hz, A-5 (highest GOR) gives way at 59.7 Hz (+9.7 from SCADA vs +16 for low-GOR wells)
- Uplift card: +77.9 bbl/d / +$369,225/90d / gas 7.9999/8.0 MMscfd ✓
- Closing: "Maximum production from the pad. No pump destroyed." / "Cloud searches. Edge enforces."
- CTA: ▶ Run the Optimization → sets h3BriefingMode=false, fires runVizierOptimize()

**Red-team (Gemini gdc-second-opinion, Session BD):**
- "Vizier as optimizer for LP-trivial problem" → FAILS (engineer attack: "use a spreadsheet")
- Fix: Vizier justified for FULL multi-constraint problem (gas+thermal+RUL non-linear). LP analytical handles gas-only subproblem; Vizier handles the full search where LP doesn't apply.
- All 7 revised claims SURVIVE

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
| **Sprint H3-C: 3-panel H3 briefing** | **✅ DEPLOYED** | **`662166c` — session BD · "Maximum Production. Maximum Care." / "Cloud Searches. Edge Enforces."** |
| DEMO_MASTER §6 field-level spec | ❌ NOT UPDATED | Sprint H3-D |
| H1 static seed date-templating | ⚠️ NEEDS FIX | Sprint P4 — hardcoded 2025 dates |
| **esp_thermal.ubj — XGBoost version mismatch** | **✅ RESOLVED** | **Session BB: physics polynomial used directly** |
| H2-C1 flush+reseal ~$8k–$15k | ⚠️ 🔴 NEEDS-EXPERT | Soft range only — labeled as estimate on screen |
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
