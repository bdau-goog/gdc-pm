# Next Session Prompt — GDC ESP Ops Video (Operational State)
Date: 2026-06-23 (Session BS+41) / branch: feature-trio-clean
Git HEAD: 0ae3980 / Image: sha256:f3c6f77a (fault-trigger-ui, full Gemma de-claim sweep)

## STEP 1: Run These Four Commands First
```bash
kubectl get pods -n gdc-pm --no-headers
# Expected: all 1/1 Running (7 pods)

kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
# Expected: 0

curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))" 2>/dev/null || echo "API unreachable"
# Expected: ollama_online: False model: offline

kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
# Expected: field_intel = 11, rag_documents = 20
```

## STEP 2: Read These Documents
```bash
cat docs/VIDS_PRODUCTION_MASTER.md   # PRIMARY REFERENCE — shot bible
# Last 3 SESSION_LOG entries for context
```

## STEP 3: FINISH H1 RECORDING — then NARRATIVE/PANEL FIXES BEFORE RECORDING H2/H3

### BLOCKER: H2 and H3 have narrative gaps that must be fixed before recording those scenes.
### Record H1 (finish B1-P5 + B1-S1→S6) first. Then fix H2+H3 slides. Then record B2/B3.

---

## ⚠ H2 NARRATIVE GAP — "Signal Leads Wrong Direction" (not same as H1)

**SH feedback:** H2 "feels like the same scenario" as H1 — both seem to be about ambiguous signals.
**Root cause:** h2.html Slide 2 says "AMBIGUOUS TELEMETRY" and "indistinguishable" — WRONG framing.

**The actual H2 distinction (must be made explicit in slides):**
- H1: Signal is ambiguous. Sensors cannot name the cause. Two causes, identical signature. "We don't know what it is."
- H2: Signal is CLEAR and POINTS DEFINITIVELY at bearing wear. The APM correctly reads the symptom. The trap is that bearing wear and paraffin restriction produce the SAME symptom pattern — but paraffin is the root cause. "The sensors are right about what they see. They're wrong about why."

**Required slide changes in h2.html (Slide 2, "AMBIGUOUS TELEMETRY" panel):**
- Line 73 kicker: "AMBIGUOUS TELEMETRY" → **"THE SIGNAL SAYS PULL"** (or "CLEAR SIGNAL. WRONG ANSWER.")
- Line 74 title: "Fifty-Two Days Late. Bearings or Wax?" — OK to keep or change to "Weeks of Drift. One Clear Pattern. One Wrong Conclusion."
- Line 75 sub: Drop "indistinguishable" → **"Vibration rising steadily for weeks. Current up. Efficiency down. Every best-in-class platform reads this as bearing wear — and routes straight to a pump pull. That diagnosis is correct for the sensors. Wrong for this well."**

**VO impact (B2-P2):** The VO already has the right framing ("To a best-in-class platform, that pattern reads as bearing wear: pull the pump.") — this is a SLIDE TEXT fix, not a VO re-record.

**Also revisit H2 Slide 1 sub-text** to plant the distinction upfront: add something like "Here, the monitoring system sees the right symptom and makes the wrong call."

---

## ⚠ H3 NARRATIVE GAP — Vizier not explained; optimization problem not clear

**SH feedback:** Why are we using Vizier? What are we trying to optimize? Not explained clearly enough.

**Two specific gaps:**

**Gap 1 — What is Vizier?** Never explained on screen. Need a brief in h3.html Slide 3:
> "Vertex AI Vizier is Google's Bayesian optimizer. Rather than brute-forcing the setpoint space, it learns from each trial — focusing the search on promising regions and converging on the near-optimal allocation in ~15 trials. Without it: hours of manual calculation or crude uniform throttle."

**Gap 2 — Why can't the engineer just calculate it manually / why can't SCADA do it?**
The H3 Slide 1 or 2 needs to make explicit WHY this is hard:
- 6 wells × many Hz options = large search space
- 3 simultaneous ceilings (gas contract + individual motor temp limits + run-life) that interact
- The interaction matters: backing off the gassiest well 2 Hz gives headroom to push the efficient wells harder — but the optimal trade-off is not obvious
- Conditions change daily; a manual calculation goes stale overnight; Vizier can re-run on demand

**Required slide additions:**
- h3.html Slide 2 (THREE CEILINGS): Add a sentence: "An engineer could compute a setpoint table manually — but the gas-efficient wells interact with the gassier ones. The optimal trade-off across all three ceilings and all 6 wells is a problem for a Bayesian optimizer, not a spreadsheet."
- h3.html Slide 3 (CLOUD SEARCHES · EDGE ENFORCES): Add a Vizier explanation paragraph. Current sub only says "Vertex AI Vizier explores the 6-well setpoint space" — needs to say WHAT Vizier is.

**VO impact (B3-P3):** B3-P3 VO says "The division of labor: the cloud searches for the best setpoints; the edge enforces the safety limit." Needs one additional sentence explaining Vizier. Update bible VO.

---

## STEP 4: RECORDING ORDER (after H2/H3 fixes)

**H1-P5 card fix: ✅ DONE** · **Tier 1 bible trims: ✅ DONE (beb066f)**

Trim summary (docs only — no app change, no re-record needed for done scenes):
- B1-P5 VO: 52w / ~21s (locked)
- B1-S3 VO: tightened 31w → 28w
- B2-S5: ❌ CUT — redundant VO; saves ~4s
- BBRIDGE VO: "air-gap capable" → "all AI local" (BS+39 accuracy fix applied to VO)

**Recording order:**
1. FINISH H1: B1-P5 (in progress) → B1-S1 → B1-S2 → B1-S3 → B1-S4 (A/B) → B1-S5 → B1-S6 (OPTIONAL)
2. FIX H2 SLIDE TEXT (h2.html P2 kicker/sub) — deploy before recording any B2 scenes
3. FIX H3 SLIDE TEXT (h3.html P2/P3 add Vizier explanation) — deploy before recording any B3 scenes
4. Record B2-P1 → B2-P2 → B2-P3 → B2-S1 → B2-S2 → B2-S3 → B2-S4 (skip B2-S5 — CUT)
5. BBRIDGE (use updated VO — "all AI local, no cloud required")
6. Record B3-P1 → B3-P2 → B3-P3 → B3-S1 → B3-S2 → B3-S3 → B3-S4 (CONDITIONAL) → B3-S5
7. BCLOSE

## STEP 5: Pre-B2 RT gate — H2-C1 (vib units)

All B1-Sx VOs are in the bible and have not changed this session — safe to proceed.

## STEP 5: Update Runtime Ledger

Actual runtime with updated VOs (~145 wpm pace):
| Section | Real est |
|---|---|
| Part A cold open | ~68s |
| Intro B0.1–B0.4 | ~55s |
| H1 Discern B1-P1→S5 | ~2:46 (core) |
| H2 Classify B2-P1→S4 | ~1:05 |
| BBRIDGE | ~19s |
| H3 Optimize B3-P1→S5 | ~1:06 |
| BCLOSE | ~13s |
| **TOTAL core VO** | **~7:32** |
| Finished (add 10–15% overhead) | **~8:00–8:30** |

The bible runtime ledger still shows the old ~5:45 estimate — update it.

## Current Deployed State
- App: http://gdc-pm.bdau.io
- Image: sha256:f3c6f77a (fault-trigger-ui, Gemma de-claim sweep + H1-P5 doc pills + outcome chips)
- Slides committed: h1.html P4 (Bayesian Context Fusion), P5 doc pills; intro.html Gemma chip removed
- VIDS_PRODUCTION_MASTER.md: B1-P1→P4 marked DONE; B1-P5 redesigned + VO updated — ready to record
- Gemma de-claimed: all user-facing surfaces reframed to XGBoost + pgvector + Bayesian

## Key Decisions This Session (do NOT revert)
| Decision | Detail |
|---|---|
| B1-P3 3-card redesign | VFD Speed-Down / Managed Step-Down + Hold / Emergency Shut-In; closes false-binary hole for sandy drawdown |
| B1-P3 title | "All Three Responses Have a Trap." |
| LAST RESORT removed | Replaced with "SAFE · DEFERS PRODUCTION" on clean-drawdown / shut-in row |
| "Indistinguishable" dropped from B1-P2 VO | Replaced with "the cause and the safe action are not in these numbers" |
| "Needless for gas" replaced in B1-P3 VO | "for gas, the simple speed-down already worked" |
| P5 labels | "Oil & Gas" / "Power & Utilities" / "MARITIME" (full names) |
| P5 text sizes bumped | badges 0.82, headlines 0.85, descriptions 0.70, resolution 0.76rem |
| P5 analogies: BOTH FAIL RT | "identical signature" framing is false; fix before recording B1-P5 |

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- GPU scale-to-zero; `gpu-start.sh` ONLY for explicit LLM test
- VEO_COLD_OPEN.md has hidden-character lines — use write_to_file not replace_in_file
