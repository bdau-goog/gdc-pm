# GDC Demo — Scenario Defense Dossier
**For:** Presenter / stakeholder briefings  
**Date:** 2026-06-25 · Session BS+50  
**Sources:** DECISION_DOSSIER.md · DEMO_MASTER.md · RED_TEAM_LEDGER.md · CLAIM_LEDGER.md  
**Relation to other docs:**
- `STAKEHOLDER_BRIEF.md` = exec-facing prose; business value language
- `DECISION_DOSSIER.md` = internal build/strategy record; session history
- `DEMO_MASTER.md` = full engineering spec and physics
- **This file** = presenter's defense brief — what to say, how to defend it, what never to say

---

## §0 — How to Use This Doc

**Read this before any stakeholder or customer conversation.** The demo can be dismantled in five minutes by a senior production or ESP engineer if any claim overreaches. Every number you say in the room should trace to one of three tags:

| Tag | Meaning | Can you say it as a hard fact? |
|---|---|---|
| 🟢 TEXTBOOK | Grounded in a citeable standard (API RP, SPE, IEC, IEEE, OEM manual) | Yes |
| 🟡 OUR-CODE | Number comes directly from our system (`FAULT_PROFILES`, `RESOLUTION_OPTIONS`, `app.py` constants); grep-verifiable | Yes, as "in our scenario" |
| 🔴 NEEDS-EXPERT | Plausible but not authoritatively sourced; soft estimate | **No.** Caveat as estimate, soften to a range, or cut it |

**The PRIME DIRECTIVE:** A slower, honest demo beats a fast demo that an engineer dismantles in the first five minutes. Concede what SCADA/APM genuinely does well. Win only on what is real and defensible.

---

## §1 — The One-Sentence Spine

> **GDC delivers — inside the operator's sovereign boundary, on open-weight AI, at the edge where the data already lives — the AI-powered diagnostic advisor the entire APM industry is building for cloud deployment in 2025–2026.**

This is a **WHERE claim, not a WHAT claim.** The capability class (real-time ML anomaly detection + document-fused differential diagnosis) is industry-validated. GDC's differentiator is sovereign-edge deployment: the decision, the safety constraint, and the AI inference all run inside the operator's perimeter.

**Three acts, escalating scope:**
- **H1 (Discern):** One well, one live event, two possible causes — GDC names the right one from documents, in seconds
- **H2 (Classify):** One well, a weeks-long developing pattern — the confident AI verdict is right about the symptom and wrong about the cause; GDC finds the provenance from documents and averts an expensive wrong action
- **H3 (Optimize):** The whole pad, simultaneously — GDC allocates the shared gas budget across 6 wells to maximize production without violating any constraint

---

## §2 — Three Shared Premises (cite these when challenged)

These underpin every scenario and the Why-GDC tab. Always reference them rather than re-asserting locally.

### Premise 1 — RTOC Span-of-Attention (Wells Per Engineer)
**Claim:** A single surveillance engineer in an RTOC monitors *hundreds* of artificial-lift/ESP wells simultaneously. Proactive per-well document research is architecturally impossible without automated tooling — not negligence.

| Source | Figure |
|---|---|
| YPF Decision Support Center (onepetro.org / esss.com) | ~280 wells per engineer (2 engineers, 560+ artificial-lift wells) |
| SLB Artificial Lift Surveillance Center (drillingcontractor.org) | 847 wells monitored over an 8-day surveillance window |

**Display figure:** "hundreds of artificial-lift wells per surveillance engineer" — the cited range (280–500+) supports this. Do NOT state a hard floor below 200 without SME confirmation.

**What this defeats:** "Why can't the engineer just check the PM log?" — At 280+ wells per shift, checking a vendor service portal entry for every quiet-but-anomalous well is architecturally impossible. GDC's fleet-scale automation is what makes the possible-in-principle diagnosis happen automatically in practice.

### Premise 2 — APM Penetration (Two-Tier Honest Framing)
**Claim:** Advanced predictive maintenance (SmartSignal/PRiSM/Mtell tier) is the minority, not the default.

| Tier | Proportion | What this means for GDC |
|---|---|---|
| **Threshold SCADA only** | ~76–89% of O&G companies (uptimeai.com / reliamag.com, 2023 — only ~24% run any PdM strategy, only ~11% reach ML-maturity) | GDC's XGBoost pre-threshold multivariate scoring is a **genuine detection advantage** — no APM incumbent to defeat |
| **Best-of-breed APM** (SmartSignal/PRiSM/Mtell/Lift IQ) | ~11–24% | Detection quality converges. GDC wins on **L3 document fusion** — APM is sensor-only and cannot read the documents that carry the cause. This is the CATEGORICAL moat |

**MUST-NOT-SAY:** "GDC detects faster/better than SmartSignal/PRiSM/Mtell" — not proven; against best-of-breed APM, detection edges converge.

### Premise 3 — RTOC Structure (Deployment Scale Shape)
**Claim:** A major upstream operator runs a handful of regional RTOCs/IOCCs (typically 2–10+), each governing thousands of wells across a geographic basin.

| Operator | RTOC Structure |
|---|---|
| ExxonMobil | "Vantage" centralized hub + regional drilling centers |
| Chevron | Multi-IOCC: Midland TX (Permian), N. Colorado, Kazakhstan (Tengiz), Houston Wells DSC |
| Shell | New Orleans deepwater + Gulf of Mexico IOC + global WRFM network |
| BP | Hub-and-satellite (Houston RCC + satellite locations, since 1997) |
| Saudi Aramco | 4IR Center (Dhahran), Drilling/Workover RTOC (2008), Geosteering Center (75 rigs) |

**GDC deployment shape:** One GDC cluster per regional RTOC → fleet governance across the basin's thousands of wells. This is the scale revenue story: data-gravity × AlloyDB × continuous inference × training loop across thousands of wells per instance.

**MUST-NOT-SAY:** Hard RTOC count claims without qualification (varies by operator). "One RTOC per well pad" (pads are typically unmanned).

---

## §3 — H1: DISCERN · ESP Fluid Unloading · Ambiguity Resolution

### 3.1 What We Show

A Permian ESP well (Well A-3, Pad Alpha, mature carbonate producer, AR-trim pump, **intake-only sensor string** — the configuration of ~90% of Permian ESPs) experiences a developing event. Pump Intake Pressure (PIP) and Motor Current (Amps) both decline together — the classic early-unloading signature.

GDC scores the developing event against its XGBoost health model **before any single SCADA hard limit fires** and routes to L3 document retrieval. The SCADA view shows the standard protective response (equipment-safe, but production-deferring). The GDC Advisor view reveals the three retrieved documents and delivers a plain-language cited verdict. The operator approves the recommended VFD setpoint dispatch via a human-in-the-loop action panel. SCADA retains regulatory control.

**The three documents GDC retrieves:**
1. **06:15 Operator Shift Note** — elevated GOR, casing pressure building, well behaving with stable sand history → gas interference likely safe for VFD trim
2. **06:00 Sonic-Survey Summary** — fluid level 150 ft above intake, flat casing pressure, no free-gas indicators → if drawdown branch: step VFD down toward minimum flush Hz, verify headroom from this survey before any further reduction
3. **OEM/Well Operational Manual** — defines failure thresholds and operating constraints specific to this pump configuration

### 3.2 Why It Matters

**The physics:** When PIP and Amps decline together on an intake-only string, the early signature is **genuinely ambiguous** between two root causes with opposite correct actions:

| Cause | Correct Action | Cost if Wrong |
|---|---|---|
| **Gas Interference → Gas Lock** (GVF ~18% at intake — early interference window) | VFD trim 52 → 44 Hz. Slows impeller, gas vents up the fully-submerged casing annulus. Well stays online. ~$2,500. | If misdiagnosed as drawdown and pump is shut in: restart after sand bridges = workover |
| **Reservoir Fluid Drawdown** (dynamic fluid level critically low) | Reduce VFD in controlled steps above minimum sand-transport velocity; verify fluid-level headroom from last sonic survey before any reduction. Hard shut-in contraindicated on sand-laden column. | VFD trim during actual drawdown drops fluid velocity below critical sand-transport threshold → sand bridges in tubing above pump → ~$150k 🟡 workover |

**Why no sensor resolves it:** A discharge-pressure gauge would resolve state — but this well doesn't have one (~90% of Permian ESPs are intake-only). An acoustic fluid-level shot is the ground-truth measurement — but it takes hours to dispatch a crew, far exceeding the ~25-minute thermal failure window. PIP itself is a submergence proxy, but with gas breaking out, the annulus gradient is uncertain.

**The thermal failure timeline:** An ESP motor running gas-locked enters thermal runaway. IEEE 117 / API RP 11S limits Class H insulation at 356°F / 180°C. Thermal failure: **15–30 minutes** of gas-locked operation. 🟢 TEXTBOOK.

**The scale reality:** This event happens across hundreds of wells in the RTOC at once, including at 2am. The documents exist. The engineer cannot read them proactively for every quiet-but-anomalous well. GDC can.

### 3.3 How It Works

1. **L2 (XGBoost multivariate):** The `esp_health.ubj` model runs a sliding window over the trajectory arrays and computes a health score at every step. It crosses the detection threshold at index ~27 (~T=6 min) — before the SCADA pressure-floor alarm fires at ~T=10 min. The model is real; the detection index is a real model output. 🟡 OUR-CODE.

2. **SCADA rules evaluated honestly:** Three alarm rules (rate-of-change dPIP/dt, rolling-avg PIP floor, motor undercurrent — ISA-18.2 §5.3 / API RP 11S §7.2). The SCADA alarm fires competently. GDC is never shown making SCADA look broken or asleep.

3. **L3 (pgvector RAG):** The XGBoost detection event triggers automatic document retrieval. `all-MiniLM-L6-v2` embeddings + AlloyDB pgvector cosine similarity. The relevant documents surface in < 2 seconds. The Bayesian discriminator fuses the retrieved evidence (log-odds over API RP 11S §7.2 physics-anchored likelihood ratios) and outputs a posterior probability for each fault branch. 🟡 OUR-CODE (LR weights are conservative, physics-grounded, labeled on-screen as not empirically calibrated).

4. **HITL:** Operator approves the recommended action. GDC dispatches a supervisory setpoint (52 → 44 Hz) to SCADA. SCADA retains regulatory control and hard trip authority. Action label: "Approve & Dispatch to SCADA — VFD Trim · Supervisory setpoint · SCADA retains regulatory control."

### 3.4 The Defense (top hostile challenges)

| Challenge | Honest Answer |
|---|---|
| "A good engineer at the SCADA screen could figure this out from the sensor pattern" | Yes — on a single well with time. What GDC does is make it automatic, fleet-scale, instant, cited, and inside your perimeter. One engineer, 280 wells, 2am: the research doesn't happen. GDC makes it happen every time. |
| "Your lead-time advantage — GDC before SCADA — isn't real. SCADA alarms fast." | SCADA does alarm (we show it correctly). The lead-time against threshold-only SCADA is real and code-derived (gdc_detect_idx=27 vs. alarm_idx=48 — ~21 steps / 5.25 min). Against best-of-breed APM, detection converges — the L3 document fusion is the categorical win there, not the detection speed. We don't overclaim detection speed vs. APM. |
| "The two failure modes aren't really indistinguishable — a discharge gauge would resolve it" | Correct, and we say so. This well doesn't have one — the configuration of ~90% of Permian ESPs. The scenario explicitly states the intake-only limitation. The deciding context lives in documents, not sensors. |
| "Can't SCADA multi-variate rules distinguish the two causes?" | No numeric combination of PIP/Amps/Temp/Vib on an intake-only string can discriminate in the early decision window. Both branches lose cooling flow; both branches show PIP and Amps declining together. The FAULT_PROFILES are identical arrays for a reason. |
| "GDC's Bayesian weights are made up" | They're conservative, transparent, physics-grounded (API RP 11S §7.2 cited), and labeled as not empirically calibrated — on screen. An engineer can check the arithmetic. The weaker claim (transparent conservative weights) is the honest one and more defensible than a black-box confidence percentage. |
| "GDC makes the wrong call if the documents are wrong" | Correct. GDC is an operator-assist tool, not autonomous control. The operator reviews the evidence chain and approves every action. If the shift note is wrong, the operator sees the source. SCADA retains regulatory control and hard trip authority. |

### 3.5 Must-NOT-Say (H1)

- ❌ "GDC detects faster than SmartSignal/PRiSM/Mtell" — not proven; detection converges against best-of-breed APM
- ❌ "SCADA lets the pump die" — SCADA trips and shuts the well in to protect the pump; it alarms correctly and we say so
- ❌ "No sensor can ever distinguish gas lock from drawdown" — FALSE; a discharge gauge resolves state; win on the intake-only context, not an overstated sensor impossibility
- ❌ "GDC is the only path for sovereign operators" — SLB Lift IQ Edge, on-prem historian vendors, private cloud options exist; say "architecturally designed for on-prem AI from the ground up — not adapted from cloud"
- ❌ "VFD SETPOINT DISPATCHED · RECOVERING" — GDC does not know the well is recovering at the moment of dispatch; correct label is "VFD SETPOINT DISPATCHED — awaiting wellbore response"

---

## §4 — H2: CLASSIFY · Paraffin/Wax Deposition Mimicking Bearing Wear · Provenance Resolution

### 4.1 What We Show

The **opposite of H1.** H1 has an ambiguous signal where neither cause can be confirmed from sensors alone. H2 has a **clear, confident signal** — every best-in-class platform reads it correctly as a symptom — and the machine routes to the wrong, expensive action because the *cause* lives off-sensor in three documents it cannot read.

> **"Clear signal. Confident APM verdict. Wrong action."**

The tab opens with 90 days of degradation history already plotted. The VIB-HI alarm is already active. The SCADA view shows the standard bearing-wear action card: pull the pump. The GDC Advisor view shows three documents appearing in sequence, then the verdict flipping: "Paraffin/wax deposition — NOT bearing wear. Dispatch hot-oil truck. Do NOT pull."

**The three documents GDC retrieves:**
1. **Chemical vendor service log** — hot-oil PM 52 days overdue; third-party vendor logistics delay documented; NOT in SCADA
2. **Fluid PVT lab report** — crude WAT ~118°F 🟢, 8.3% wax content, 90-day treatment interval required for this well
3. **Prior pull record** — bearings inspected NORMAL 18 months ago → bearing-age hypothesis eliminated

### 4.2 Why It Matters

**The five survival gates (all pass):**

| Gate | Test | Result |
|---|---|---|
| **1. Discrete past event** | Specific thing that happened at a specific time | ✅ 90-day hot-oil PM due Day 90; delayed by third-party vendor. Calendar date, documented reason, in vendor portal — NOT SCADA |
| **2. Categorically off-sensor** | Cause impossible to measure with any sensor on this asset | ✅ Wax deposition thickness inside production tubing: physically unmeasurable by any sensor on a running ESP string |
| **3. APM mis-routes** | Best-of-breed APM routes to wrong, expensive action | ✅ Rising amps + rising vibration + declining efficiency on a 4-sensor string = textbook bearing wear signature. APM classifies correctly on the symptom; cannot read the cause |
| **4. Common and material** | Failure class frequent enough for fleet-scale automation to have ROI | ✅ Paraffin endemic to Permian carbonate producers (WAT 110–122°F 🟢). SME Bill Barna (Permian production engineer): *"Many operators have poor programs. Often there are so many false positives, nobody believes the system. All of the problems you listed happen."* |
| **5. Remedy feasibility** | GDC-prescribed fix physically executable without workover or downhole access | ✅ Hot-oil truck roll + annulus flush: surface-only. No workover rig. No wireline. No downhole access. ~$3k–$6k 🔴 soft estimate, SME-confirmed directionally correct |

**Cost dichotomy:**
- Hot-oil truck roll: ~$3k–$6k 🔴 (soft estimate — caveat explicitly)
- Pump-pull investigation averted: ~$70k–$100k 🟡 (consistent with $140k AFE for full ESP workover, Andrews County WTX, July 2023, Gemini search)

**The L2→L3 Earliness Engine (the honest physics):** GDC's L2 XGBoost model detects the joint-drift anomaly — efficiency softening + amps creeping + vib rising TOGETHER — **before the VIB-HI hard alarm fires.** That pre-alarm window is when the surface treatment genuinely averts the pull. Once vibration crosses the ISA HI alarm (4.0 mm/s), bearing damage may already be developing (bearing damage timeline: hours-to-days under severe restriction — osti.gov / researchgate.net). GDC catches it early. The RTOC engineer — with 280 wells — cannot proactively research the vendor portal for every quiet-but-anomalous well. GDC can, fleet-wide, automatically.

**The scale reality (fleet-wide, at alarm speed):** Across hundreds of wells per surveillance shift, this overdue-PM event happens repeatedly. Some get caught; most don't because the data silo between the vendor portal and the SCADA historian is structural, not behavioral. GDC closes that silo automatically.

### 4.3 How It Works

1. **L2 (XGBoost multivariate):** Pre-threshold multivariate scoring detects the joint-drift anomaly — all four sensor channels drifting in a correlated pattern — before the VIB-HI alarm fires. This is the trigger that routes GDC to the L3 document corpus for this specific well, automatically.

2. **L3 (pgvector RAG):** Three documents retrieved. The determining insight requires cross-referencing all three:
   - Vendor log alone: a PM delay is common; not an alarm trigger in isolation
   - PVT report alone: high-wax crude; context, not diagnosis
   - Pull record alone: bearings normal 18mo ago; reduces probability, not eliminates it
   - **All three together:** Overdue paraffin PM + confirmed high-wax crude + healthy bearings 18 months ago = bearing-wear hypothesis eliminated; paraffin restriction is the mechanistically consistent and documented cause

3. **Instant-triage load:** The tab opens at the alarm state (h2CursorIdx = scada_alarm_idx), not at Day 0 of the replay. This reflects the realistic alarm-triage register: the event has developed; the operator opens the well page when it alarms and needs an immediate answer.

4. **Two-tier framing:** The SCADA view honestly shows what threshold SCADA does: fires the VIB-HI alarm, presents "pull investigation" as the action card. The GDC view shows the document cascade and the flipped verdict. The distinction is NOT "SCADA is dumb" — it is "APM is right about the symptom, wrong about the cause, because the cause is architecturally off-sensor."

### 4.4 The Defense (top hostile challenges)

| Challenge | Honest Answer |
|---|---|
| "If the bearings are already past the HI alarm, they might already be damaged — pulling was right" | This is why the earliness engine matters. GDC's L2 model detects the pattern pre-alarm, when the surface treatment is still fully effective. The scenario explicitly fires the GDC alert before the hard alarm. Caught early: treatment works, pull averted. Caught at the hard alarm: mitigation, not full reversal — honest physics, acknowledged in our framing. |
| "Paraffin vs. bearing wear — can't the engineer tell from the sensor trend shape?" | Both paraffin restriction and bearing wear produce rising amps + rising vibration + declining efficiency on a 4-sensor string. Against threshold SCADA: no root-cause hypothesis at all. Against best-of-breed APM: APM classifies this pattern as bearing wear (correct symptom, wrong cause) — it cannot read the vendor portal to discover the overdue PM. The off-sensor cause is the categorical moat. |
| "A smart APM system could learn to cross-reference scheduled PM dates" | Scheduled PM dates are in the vendor service portal, not the SCADA historian. Integration of third-party vendor portals with SCADA is non-standard. Even where integrated, the system would need to cross-reference: overdue date + PVT WAT + bearing history + current vib trend simultaneously. That cross-document synthesis is GDC's architecture. |
| "Hot-oil doesn't always work — what if the bearings are already damaged?" | Acknowledged. We say "low-cost surface remediation" or "surface treatment" — not "hot-oil guarantees full removal." The honest framing is: caught pre-alarm, the surface treatment is still effective and the pull is genuinely averted. Caught post-HI, it's mitigation. Our demo catches it pre-alarm. |
| "Why didn't someone check the PM log?" | 280 wells per engineer. 14 other false-positive vibration events on the pad that week. 2am. The PM log is in a third-party vendor portal, not in the SCADA historian. The structural data silo is the problem — not operator negligence. A third-party vendor logistics dispute caused the delay. GDC closes the silo automatically. |
| "The documents are seeded for the demo" | Yes — seeded for the demo. In deployment, the RAG pipeline reads from live field data integrations (polling, event-subscribe, file-watcher — all inside the perimeter). The pgvector retrieval and Bayesian fusion mechanisms are identical. |

### 4.5 Must-NOT-Say (H2)

- ❌ "Vibration crossed ISA-HI and the pump is pristine — hot-oil was all it needed" — once VIB-HI crossed, bearing damage may already exist; overclaims
- ❌ "Hot-oil guarantees full removal" — use "low-cost surface remediation" or "surface treatment"
- ❌ "GDC detects before APM" — L3 provenance is the win, not detection speed
- ❌ "APM missed this" — APM correctly identified the bearing-wear pattern; it missed the CAUSE (off-sensor); this distinction matters
- ❌ "The signal is ambiguous" — H2 is the OPPOSITE of H1; the signal is clear and confident; the machine is certain and wrong; never blur H1 and H2

---

## §5 — H3: OPTIMIZE · Pad-Level Gas-Budget Allocation · Field Optimization

### 5.1 What We Show

Six ESP producers (A-1 through A-6) on Pad Alpha share a hard gas-handling ceiling: **8.0 MMscfd** — a midstream contract limit. Exceeding it triggers curtailment or flaring violations (RRC of Texas). Each well has a different Gas-Oil Ratio (GOR): A-3 produces 450 scf/bbl; A-5 produces 1,350 scf/bbl. Not all barrels cost the same gas.

**Without GDC:** The safe SCADA default is uniform throttle — scale every well back proportionally. Conservative, safe, but it wastes the gas budget on high-GOR wells while low-GOR wells are needlessly throttled.

**With GDC:** Vertex AI Vizier (cloud Gaussian Process Bandit) searches the 6-dimensional Hz setpoint space in 3 iterative rounds of 5 trials each (→ learns the gas-ceiling boundary). The edge evaluates every candidate against all three constraints. The result: A-5 (highest GOR) gives way so A-3 and A-6 (lowest GOR) run at maximum speed. Maximum production from the pad. No constraint violated.

**Result:** +77.9 bbl/d · +$369,225 over 90 days · gas 7.9999/8.0 MMscfd ✓ 🟡 OUR-CODE (live Vizier API result, June 11, 2026; will update if scenario params change)

### 5.2 Why It Matters

**The binding constraint:** The gas ceiling is a hard midstream contract limit — not a model assumption. Representative of real RRC of Texas and Permian midstream contract constraints. 🟡 OUR-CODE (scenario parameter).

**Three constraints evaluated simultaneously per well:**

| Constraint | Level | How Evaluated |
|---|---|---|
| **Gas ceiling** | 8.0 MMscfd, field-level | Cloud Vizier objective (Hz vectors + scores only cross the wire — raw telemetry never leaves) |
| **Motor winding temp** | 280°F derated operating setpoint (NOT the Class H insulation limit of 356°F/180°C per IEC 60085) 🟢 | **On-premise only:** 4-feature physics polynomial T = f(hz, amps, fluid_temp, water_cut) per API RP 11S3/S5 + IEEE 112 |
| **RUL horizon** | Per-well, tracked but not binding this run | On-premise: `rul_base × exp(−0.11 × max(0, hz−50))` |

**Why Vizier for a problem an engineer might solve with a spreadsheet:** The gas-only sub-problem IS LP-solvable (linear objective, linear constraint → allocate to lowest-GOR wells first). We solve it analytically and show it as the LP-optimal baseline — transparent, auditable, no black box. Vizier's role is the **full multi-constraint problem**: gas ceiling + 4-feature nonlinear thermal polynomial + per-well exponential RUL decay, simultaneously, over 6 continuous variables. That is not LP-solvable. The demo shows both solvers, distinguishes their roles, and explains why the non-linear full problem is Vizier's domain. 🟡 RT-SURVIVES (gdc-second-opinion Session BD).

**The two-timescale architecture (textbook RTO-over-MPC):**
- **Cloud (Vizier, slow/global/periodic):** divides the shared gas budget across all wells for maximum revenue — global view required for the shared constraint
- **Edge (GDC, fast/local/continuous):** takes cloud plan as target; reconciles against LIVE per-asset reality (motor temp hot, slugging, tripped); trims DOWN only — never reallocates UP (that would breach the shared gas ceiling); data never leaves the site
- **SCADA:** executes; owns regulatory control and hard trips

**The sovereignty is honest:** Only Hz vectors (6 numbers) and their objective scores cross the wire to Vizier. Raw operational telemetry, production rates, and well identities never leave the sovereign boundary. If the WAN link drops, the LP-optimal local result is the approved output. The constraint holds.

### 5.3 How It Works

1. **Iterative Vizier loop:** 3 rounds × 5 trials. Round 1 establishes the feasible boundary. Round 2 focuses on promising regions. Round 3 converges. The optimizer literally learns from trial rejections — the "searches and learns" claim is made literally true, not just asserted.

2. **Edge reconciliation (reconcile_live()):** After cloud optimization, the edge reconciles against real-time per-well conditions. Well A-5 has a motor temp +12°F above the cloud plan's assumption (degrading seal). Edge enforces `hz_live[i] ≤ hz_plan[i]` — trims A-5 down, returns a `trims[]` list explaining the adjustment. Never reallocates UP (that would breach the shared gas ceiling — only cloud can do that safely on the next cycle).

3. **Constraint provenance (H3-S4):** The midstream contract constraint traces to an AlloyDB RAG document — "Pad Alpha — Gas Gathering Agreement PA-2024-GG-047." `constraintDoc.found=True` must be verified before recording B3-S4.

4. **Presentation:** Two panels — "GDC-plan Hz" (what Vizier computed) and "GDC-live Hz" (what edge enforced after A-5 hot). ✗/✓ stamps on trial log. "⏺ Architecture view — system-to-system flow" honesty tag.

### 5.4 The Defense (top hostile challenges)

| Challenge | Honest Answer |
|---|---|
| "A GP Bandit for a problem you can solve with a spreadsheet — that's credentialing theater" | The gas-only sub-problem IS LP-solvable, and we show it as the LP-optimal baseline — transparently, auditably. Vizier handles the full non-linear problem: gas ceiling + 4-feature thermal polynomial + per-well exponential RUL decay simultaneously over 6 continuous variables. That is not LP-solvable. We show both solvers and explain both roles. |
| "Operators don't trust control vendors with their data" | Nothing operational crosses the wire. Only Hz setpoint vectors and their scores go to Vizier. Raw telemetry, production rates, and well identities stay on-premise. The safety constraint evaluates locally. |
| "GDC invented hierarchical control" | No — two-timescale RTO-over-MPC is textbook industrial control architecture (standard in refinery and compressor station optimization for decades). GDC implements it for the ESP gas-allocation problem using cloud-native tooling (Vizier) for the search layer and edge computing for the enforcement layer. |
| "What if the gas ceiling changes mid-shift?" | The edge trims DOWN against the current plan. If conditions change materially, the operator initiates a new cloud optimization cycle. This is intentional: the cloud re-optimizes periodically with global visibility; the edge enforces continuously with local visibility. Two different timescales, two different roles. |
| "14 of 15 Vizier trials were infeasible — that's a broken optimizer" | It's not broken — it's the shared gas ceiling doing its job. A wide initial search space + shared constraint + single-batch trials produces mostly infeasible results. The iterative loop (3 rounds of 5) fixes this: round-1 rejections teach Vizier the feasible boundary, rounds 2–3 concentrate the search there. The fix is to make the claim literally true by making the loop iterative. |

### 5.5 Must-NOT-Say (H3)

- ❌ "Operators don't trust control vendors" — FUD; RT FAILS
- ❌ "GDC invented hierarchical control" — it's textbook RTO/MPC
- ❌ "Edge does global optimization" — edge trims DOWN only; global optimization requires the cloud (shared constraint)
- ❌ "14 of 15 rejected" as a hero stat — frame as "learning the boundary," not as the optimizer failing
- ❌ "No public-cloud dependency for the decision" → use "No public-cloud dependency for the safety constraint — the thermal limit and the final approved setpoint both evaluate on-premise"

---

## §6 — Why GDC / Why GCP

### 6.1 The Challenge Being Answered

H1, H2, and H3 prove "why edge AI" and "why document fusion." They do NOT automatically answer "why Google Distributed Cloud specifically." A procurement-level CTO will ask this. Here is the three-pillar answer, RT-hardened.

### 6.2 The Three-Pillar Answer (no competitive mentions)

> **You've decided sovereign edge AI is the answer. Why Google?**

**1. Form Factor Fit**
GDC runs on validated, certified hardware across connected, software-on-your-hardware, and air-gapped deployments. One platform; the right footprint for whatever edge topology your operations require — from an RTOC rack to a remote facility with intermittent connectivity.

**2. Fleet Governance**
Anthos Config Management + Fleet Management give you one declarative policy plane for security, configuration, and version consistency across every GDC site — the platform and the applications on it. Company-wide consistency from one control plane. The same tooling that governs your cloud GKE fleet governs your sovereign edge nodes. **Scope this correctly:** ACM/Config-Sync governs the GDC platform and the applications on it, NOT the underlying OT/PLC/SCADA systems.

**3. Sovereign AI Platform + Model-Ops Depth**
The same Google stack on-prem: GKE, AlloyDB Omni, Vertex AI / Gemini Enterprise. Train centrally on your fleet data; deploy **base models** to each edge node with **local fine-tuning** for site-specific conditions (sensor drift, formation character, lift efficiency curves); govern rollouts and rollbacks centrally; propagate findings fleet-wide. Backed by Google's enterprise AI + data-services depth.

**⚠ Do NOT say "deploy models identically"** — ESP analytics are site-specific; models need local adaptation. "Base models + local fine-tuning" is the honest and defensible claim. RT FAILS on "identically." 🔴 (gdc-second-opinion Session BS+49)

### 6.3 RTOC Scale Shape (the revenue story for Google)

- "A handful of regional RTOCs per major, each governing thousands of wells" (Premise 3)
- One GDC cluster per regional RTOC → fleet governance across that basin's thousands of wells
- Scale revenue = data-gravity × AlloyDB × continuous inference × training loop across thousands of wells per instance
- Do NOT claim GDC lands at every pad (unmanned; too many)

### 6.4 The Competitive Claim (exact wording — Gemini neutral-search verified, Session AT)

> *"No native, production-ready commercial product combines real-time ML anomaly detection with LLM-based differential diagnosis over unstructured maintenance documents — as of 2025–2026, this is where all major APM platforms are heading. GDC delivers it now, inside the sovereign perimeter, on open weights."*

### 6.5 The Honest-Footing Rule (for "but a human could figure this out")

> *"Yes — a skilled engineer could reach this conclusion with the right documents and time, on a single well. What GDC does is make it automatic, fleet-scale, instant, cited, and inside your perimeter — turning a diagnosis that's possible in principle into one that happens every time in practice."*

### 6.6 Why-GDC Must-NOT-Say

- ❌ Any competitive mentions (AWS Outposts, Azure Local, DIY) — 100% GDC value-props only
- ❌ "Deploy models identically" → use "base models + local fine-tuning"
- ❌ "Config-Sync manages your PLCs/SCADA" — apps + infra on GDC only
- ❌ "Zero OT integration work" — OT integration still required; GDC simplifies the IT/app layer above it
- ❌ "Vendor-neutral" unscoped → scope to "neutral relative to equipment/OEM vendors"
- ❌ "The only complete sovereign path" → "architecturally designed for on-prem AI from the ground up — not adapted from cloud" (SLB Lift IQ Edge and on-prem historian vendors also exist)
- ❌ "Air-gap capable" for the demo deployment — the demo cluster is network-connected; honest claim is "all AI on-prem, fully sovereign (no cloud dependency for the AI decisions)"

---

## §7 — Key Findings from Red-Team & Research Actions

This is the list of what the hostile-engineer passes and grounded searches changed. Understanding WHY each change was made lets you defend the current framing.

### RT Findings — Scenario Physics

**1. The thermal-path kill shot (H2 slug-flow scenario, Session AR — FAILS)**
The original H2 used flat winding temperature as the discriminator between slug-flow and bearing wear. A hostile-engineer red-team (Gemini + Claude Opus) independently identified: the motor RTD is in the motor; bearings are in the pump/protector (thermally separated). Early mechanical wear doesn't move the winding RTD. In a high-GOR well, gas at the intake *reduces* cooling → temp trends UP, not flat. The discriminator ran backwards. **Cut. Scenario replaced.**

**2. The off-sensor test (H2 slug-flow, Session AR — FAILS)**
The cyclic amps-with-recovery + cyclic PIP pattern that distinguishes slug flow is IN the telemetry. APM already reads it. Documents only corroborate. The L3 moat was efficiency-only, not categorical. **Same failure class as H1 pre-reframe. Scenario must be replaced if the deciding variable is reachable from telemetry.**

**3. Gate 5 — Remedy Feasibility (elastomer-seal scenario, Session BE — FAILS)**
The H2 workover-fluid-incompatibility scenario passed all four scenario gates but was never asked: is the fix physically executable without pulling the pump? "Flush + reseal in place" sounds like a maintenance action — but an ESP protector is integral to the downhole string. It cannot be resealed in place. The fix always requires pulling the completion. The "$8k–$15k vs $70k–$100k" cost dichotomy was incoherent — both required a pull. **Gate 5 permanently added to `.clinerules`.**

**4. PIP-rise hydraulics confirmed (H2 paraffin scenario, Session BG)**
Hostile engineer attack: "The pump pulls harder against restriction → PIP decreases." This inverts centrifugal pump hydraulics. The correct physics: restriction above the pump steepens the system curve → operating point shifts to lower flow rate → less reservoir drawdown → PIP builds. Confirmed by Gemini search, API RP 11S, ResearchGate, production-technology.org. **Attack overturned. PIP-rise is correct.**

**5. Wax-to-bearing damage timeline (H2, Session BS+49)**
Physics grounding via Gemini search (osti.gov, swpshortcourse.org, researchgate.net): Early hot-oil treatment CAN restore normal operation IF prompt and effective. Once vibration rises significantly, bearing damage MAY already be developing (hours-to-days progression under severe restriction). Removing the restriction is mitigation, not full reversal, once damage has begun. **Implication: the earliness engine (pre-alarm detection) is the mechanism that makes the honest claim "surface treatment averts the pull" true. The scenario explicitly fires GDC at pre-alarm. The physics is locked on this framing.**

**6. Vizier GP Bandit justified (H3, Session BD — SURVIVES)**
Attack: "A GP Bandit for a problem you can solve with a spreadsheet." The gas-only sub-problem IS LP-solvable. We solve it analytically and show it. Vizier handles the full multi-constraint non-linear problem. Both roles shown transparently. **SURVIVES with this explanation.**

**7. 14/15 infeasible root cause (H3, Session BS+48)**
The root cause of 14 infeasible trials was not a broken optimizer — it was shared gas ceiling + wide initial bounds + single-batch `suggest_trials(count=15)` (one batch, no iteration). A single batch cannot learn the feasible boundary. Fix: 3 rounds of 5 trials → Vizier learns the boundary from round-1 rejections. **Makes "searches and learns" literally true, not just claimed.**

### RT Findings — Competitive Claims

**8. L2 detection quality is contested ground vs. best-of-breed APM (Session BQ — FAILS)**
Three L2 claims failed hostile scrutiny: "L2 detection quality vs. APM," "sovereignty-at-L2 as a unique differentiator," and "trained on YOUR data" as an L2 differentiator. All APMs (especially Mtell) train on operator-specific data. SmartSignal/PRiSM/Mtell have hardened on-prem deployments (Chevron/Oxy historically mandated them). **GDC wins L2 against threshold-only SCADA (genuine edge). Against best-of-breed APM, detection converges. Win on deployment simplicity + L3 categorical moat.**

**9. "Most of your unstructured data isn't unstructured" (Session AR)**
A critical narrowing: choke position = SCADA tag. GOR = production database (structured). Only some operator knowledge is genuinely unstructured. The defensible moat is specifically the documents that are architecturally out-of-reach of SCADA/APM: vendor service portals, PVT lab reports, workover completion records, shift notes not in the historian. Scope the claim precisely.

**10. "Deploy models identically" FAILS (Platform RT, Session BS+49)**
ESP analytics are site-specific. Sensor drift, formation character, and lift efficiency curves vary. "Deploy identically" contradicts operational reality. Fix: "Deploy base models centrally; enable local fine-tuning for site-specific conditions; govern centrally." **Model-Ops depth story survives with this reword.**

**11. "ACM/Config-Sync manages your PLCs" FAILS (Platform RT, Session BS+49)**
ACM/Config-Sync governs the GDC platform and the applications on it. It does NOT govern OT/PLC/SCADA systems. This scope clarification is mandatory — any O&G engineer will immediately push back on the idea that GitOps manages their control systems.

**12. The IEC 61511 autonomy kill (Session BS+46)**
A numeric autonomy knob (auto-execute above a confidence threshold) was proposed. gdc-second-opinion returned 4 FAILS: IEC 61511 (functional safety for process industries), not PHA-grounded, cherry-picked numbers, automation bias. The autonomy story survives as a governance display: "⛭ Autonomy Policy: VFD setpoint → ALWAYS REQUIRE APPROVAL (operator-set)." The numeric knob is permanently blocked.

### Research Findings (Gemini Search, June 2026)

**13. APM penetration (uptimeai.com / reliamag.com, 2023):** ~24% of O&G companies run any PdM strategy; ~11% reach ML-maturity. This grounds the two-tier framing — threshold SCADA is the realistic baseline for most operators.

**14. Wells-per-engineer (YPF / SLB, onepetro.org / drillingcontractor.org):** YPF ~280 wells/engineer. SLB ALSC 847 wells in 8-day window. Grounds "hundreds of wells per shift."

**15. WAT range for Permian carbonate crudes:** 110–122°F confirmed range for Permian carbonate producers. Our scenario (WAT ~118°F) falls squarely in this range. 🟢 TEXTBOOK.

**16. Vizier cost:** 100 free trials/month, $1/trial Bayesian after. Dev/test safe. No GPU.

---

## §8 — Quick-Reference Claim Table

| Claim | Tag | Source | Caveat Required? |
|---|---|---|---|
| 15–30 min ESP gas-lock thermal failure window | 🟢 TEXTBOOK | IEEE 117 / API RP 11S — Class H insulation limit 356°F/180°C | No |
| 280°F derated operating setpoint (H3 thermal constraint) | 🟡 OUR-CODE | `_WINDING_TEMP_LIMIT_F=280` in app.py; labeled as derated, not Class H insulation limit | Label on-screen as "derated operating setpoint" |
| GVF ~18% at intake (H1 gas interference) | 🟡 OUR-CODE | API RP 11S / SLB: early interference 15–20%; onset 20–25%; gas lock 25–35% — 18% is in the early-interference window | "Estimated from surface evidence (casing pressure + separator GOR)" — inferred, not directly sensed |
| 52→44 Hz VFD trim (H1 GDC action) | 🟡 OUR-CODE | `RESOLUTION_OPTIONS` in app.py | "Scenario parameter — actual setpoints are field-specific" |
| ~$150k workover cost (H1 wrong-action stakes) | 🟡 OUR-CODE | Consistent with $140k AFE for full ESP workover, Andrews County WTX, July 2023 | "Representative range; varies by depth, market conditions, well complexity" |
| ~$70k–$100k pump-pull investigation (H2) | 🟡 OUR-CODE | $140k full ESP workover AFE — our range is the investigation subset | "Representative range" |
| ~$3k–$6k hot-oil truck roll (H2 GDC action) | 🔴 NEEDS-EXPERT | SME-confirmed directionally correct; no authoritative citation | Must caveat: "soft estimate — verify with field service vendor" |
| WAT ~118°F (H2 PVT lab report) | 🟢 TEXTBOOK | Gemini-confirmed 110–122°F range for Permian carbonate crude (osti.gov, swpshortcourse.org) | No — within grounded range |
| 90-day hot-oil treatment interval (H2) | 🟡 OUR-CODE | Scenario parameter; representative of Permian production practice | "This well's PVT-recommended interval; varies by crude and GOR" |
| 8.0 MMscfd gas ceiling (H3) | 🟡 OUR-CODE | `_GAS_CEILING_MMSCFD=8.0` in app.py; representative of RRC/midstream contract limits | "Scenario parameter representative of Permian midstream contracts" |
| +77.9 bbl/d / +$369,225 / 90 days (H3 uplift) | 🟡 OUR-CODE | Live Vizier API result, June 11, 2026; `_PAD_ALPHA_WELL_PARAMS` + `_PUMP_FLOW_COEFF=24.0` in app.py | "Figure from current scenario parameters — will vary by field" |
| ~280 wells/engineer (RTOC span) | 🟢 TEXTBOOK | YPF Decision Support Center (onepetro.org / esss.com); SLB ALSC 847 wells | Use "hundreds" as display figure; do not hard-floor below 200 without SME |
| ~24% any PdM / ~11% ML-maturity (APM penetration) | 🟢 TEXTBOOK | uptimeai.com / reliamag.com, 2023 | "2023 survey data; varies by operator size and basin" |
| Paraffin endemic to Permian carbonate producers | 🟢 TEXTBOOK | WAT 110–122°F range confirmed (osti.gov, swpshortcourse.org, onepetro.org) | No |
| SME confirmation (Bill Barna, Permian production engineer) | 🔴 NEEDS-EXPERT | Direct stakeholder conversation; not a published citation | Quote as SME perspective, not authoritative study |

---

*For full engineering spec and physics derivations: `docs/DEMO_MASTER.md`*  
*For internal build/strategy record and session history: `docs/DECISION_DOSSIER.md`*  
*For full hostile-challenge register: `docs/RED_TEAM_LEDGER.md`*  
*For business-value prose (exec audience): `docs/STAKEHOLDER_BRIEF.md`*
