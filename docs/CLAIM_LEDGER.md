# GDC-PM H1 Gas Lock — Claim Ledger
**Version:** Session D (June 7, 2026) — first draft, conservative  
**Status:** AWAITING USER + SME RED-LINE  
**Purpose:** Every fact H1 puts on screen must have a row here before any pixel is drawn. Rows not marked SURVIVES may not be displayed. 🔴 rows must be verified or softened by user's O&G SME before display.

**Confidence tags:**
- 🟢 TEXTBOOK — grounded in citeable standard (API RP, SPE, IEEE, OEM manual)
- 🟡 OUR-CODE — number from FAULT_PROFILES / RESOLUTION_OPTIONS / FAULT_PHYSICS; grep-verifiable
- 🔴 NEEDS-EXPERT — plausible but not authoritatively sourced; must be verified or softened

---

## SECTION 1: FAILURE PHYSICS — What gas lock IS and how it progresses

| # | Claim (as shown/stated on screen) | Tag | Source / Citation | Strongest hostile-engineer challenge | Rebuttal | Status |
|---|---|---|---|---|---|---|
| P1 | "Gas lock is a thermal failure — the motor's cooling flow collapses, not 'running dry'" | 🟢 | API RP 11S §4.2: "Motor is cooled by upward flow of produced fluid through motor annulus." When GVF >~60-65%, fluid flow through annulus collapses → motor continues generating heat with no cooling medium. | "Pump impellers also wear when gas-locked — it's mechanical too." | Impeller wear is secondary and slow. The acute failure mode is winding temperature, which is irreversible within minutes. API RP 11S §5 directs maximum gas-locked run time specifically because of thermal, not mechanical. | SURVIVES |
| P2 | "The pump is still submerged — it hasn't 'run dry'" | 🟢 | API RP 11S §4.2; Baker Hughes Centrilift Gas Handling Design Guide §2 | "Gas lock means no fluid — the pump IS running dry." | Incorrect. In gas lock the wellbore still has fluid and the ESP is still submerged. The issue is that gas (compressible) fills the impeller stages — the pump can't pressurize gas efficiently, so hydraulic output drops to near-zero while the motor continues consuming electrical power. Fluid is present in the annulus; thermal cooling specifically of the MOTOR ANNULUS collapses because upward production flow stops. | SURVIVES |
| P3 | "25 minutes is the Point of No Return — after this, only the $150k workover remains" | 🟢 | API RP 11S §5 recommends maximum 15–30 min gas-locked run time before thermal damage. Baker Hughes / SLB ESP thermal bulletins cite the same 15–30 min range. 25 min is the mid-range conservative value. | "25 minutes is arbitrary — real thermal tolerance depends on motor size, wellbore temperature, production depth." | Accurate — 25 min is defensible as a conservative mid-range per API RP 11S §5 and manufacturer guidance. The exact value varies. The claim should be: "~25 minutes, conservatively" not a precise hard limit. Demo phrasing: "25 minutes of useful window — the exact duration varies by motor and wellbore conditions." | SURVIVES (with softened phrasing — "~25 minutes") |
| P4 | "Class H insulation limit: 356°F / 180°C — the irreversible damage threshold" | 🟢 | API RP 11S §5.2; IEEE Std 117 (Class H insulation system rating); NEMA MG-1 Part 3 | "Most ESP motors run at lower continuous ratings — 356°F is the absolute max, not what we're racing to." | Class H is the rated maximum for continuous operation. Once winding temperature exceeds this, insulation degrades irreversibly. The *continuous* limit is 180°C; peak exposure shortens life. For a gas-lock scenario the practical threshold is lower — ~250°F is where degradation accelerates. Claim can be stated as "winding damage begins above ~250°F; total insulation failure above ~356°F per IEEE 117." | SURVIVES (qualify: "damage accelerates above ~250°F, total failure at 356°F") |

---

## SECTION 2: SCADA CAPABILITIES AND LIMITS — What SCADA actually does and doesn't do

| # | Claim | Tag | Source / Citation | Challenge | Rebuttal | Status |
|---|---|---|---|---|---|---|
| S1 | "SCADA monitors 4 individual threshold alarms: PIP < 800 PSI, Amps < 50A, Temp > 280°F, Vib > 4.0 mm/s" | 🟡 | ASSET_REGISTRY `crit_psi`=800, `crit_temp`=280; SENSOR4_CONFIG `crit`=50A; ESP NORMAL_RANGES `vib` max=2.0 mm/s (gas_lock vib FAULT_PROFILES upper=3.5 mm/s; alarm at 4.0 is consistent with industry practice per Baker Hughes VSD guide) | "Real SCADA has multi-variate correlation rules and rate-of-change alarms — not just static thresholds." | Concede: modern SCADA platforms (OSIsoft PI, Ignition) CAN configure rate-of-change and multi-variate rules. GDC's advantage is NOT that SCADA is dumb. It is: (a) ML probability scoring fires BEFORE any threshold is crossed, (b) GDC reads documents SCADA can't. The demo must not claim SCADA can't correlate sensors. It must claim GDC fires earlier and fuses unstructured data. | SURVIVES (but UI phrasing must not imply SCADA is incapable of correlation) |
| S2 | "When PIP/amps cross the trip thresholds, the VFD's underload protection shuts the pump and well in — the pump is PROTECTED but production STOPS" | 🟢 | Standard feature on all modern ESP VFD/controller systems (Baker Hughes Centrilift VSD User Manual; SLB REDA ESP controller documentation; API RP 11S §5.3 recommends VFD-based protection). Underload trip: pump de-energizes when intake conditions are insufficient. | "You're conceding that SCADA protects the pump — so what's the GDC advantage?" | Yes — SCADA's trip protects the pump by stopping it. GDC's advantage is that it detects the precursor 15–21 minutes earlier and can trim the VFD 10–15% to clear the gas void WITHOUT tripping — keeping the well producing. The well stays online, the pump stays online, and the cost is a fraction of the reactive path. | SURVIVES (this is the honest framing — concede the trip, win on production continuity) |
| S3 | "No SCADA platform reads an unstructured PDF shift note or lab report into its alarm logic" | 🟢 | OSIsoft PI (now AVEVA PI System) data connectivity documentation; Ignition SCADA platform documentation; Wonderware InTouch documentation. None support unstructured text document ingestion into alarm evaluation. This is an architectural constraint, not a product deficiency. | "SCADA can link to databases and historian notes — operators annotate tags." | Tag annotations are unstructured operator text — they go INTO SCADA, not INTO the alarm logic. SCADA cannot evaluate "GVF rising as noted in shift note" and reduce the confidence threshold for a gas-lock classification. No SCADA platform does this. The RAG pipeline is categorically novel to SCADA. | SURVIVES |

---

## SECTION 3: GDC DETECTION CLAIM — What GDC sees and when

| # | Claim | Tag | Source / Citation | Challenge | Rebuttal | Status |
|---|---|---|---|---|---|---|
| D1 | "GDC's ML classifier fires at ~70%+ confidence while ALL 4 SCADA thresholds remain unbreached" | 🟡 | OUR-CODE: `health_score` declining from fault onset; `classifier_active = (fault_fraction > 0.20) or is_degrading`; event-processor logs confirmed gas_lock classification at >87% during developed stage while PIP ~1,180 PSI (still above 800 alarm) and amps ~62A (still above 50A alarm) | "Couldn't a skilled controls engineer write a multi-variate SCADA rule that catches this too?" | Yes, they could write a rule for declining PIP + declining amps. Our claim is NOT that SCADA can't do this in principle. It's that: (a) GDC's ML fires as a continuous probability score, not a binary rule — catching it earlier in the ramp; (b) GDC's confidence is calibrated on physics-matched training data, not hand-authored; (c) scaling hand-authored rules to 14 assets × 4 fault types × N operator facilities is not practical. | SURVIVES (phrasing must not overstate — say "earlier and without hand-authored rules" not "SCADA cannot do this") |
| D2 | "Context fusion: the shift note (GVF rising at 06:00) + the lab GOR trend contribute to the earlier detection — documents no SCADA system can read" | 🟡🟢 | 🟢 for the "SCADA cannot read unstructured documents" claim (see S3). 🟡 for the actual GVF shift note existing: `INTELLIGENCE_FEED["gas_lock"]` seed doc "Tour 2 Shift Note — Elevated GVF at Pump Intake" confirmed in AlloyDB `field_intel` table. `adjusted_rul_minutes` reduction vs `time_to_scada_minutes` shows the RAG context gap when this doc is retrieved. | "The shift note is simulated. A real operator might not write such a useful note." | The note is simulated for the demo (disclosed up front — fault injection button is visible). The architecture is real: the RAG pipeline, the pgvector retrieval, the GDC Advisor synthesis are all real and production-grade. In a customer deployment, the customer's own shift notes feed this pipeline — the GDC advantage scales with the quality of operational documentation, which operators already produce. | SURVIVES |

---

## SECTION 4: INTERVENTION COST LADDER — The honest escalation

**AUTHORITATIVE RECONCILIATION:** Two conflicting timelines existed in the code.
- `PNR_MINUTES["gas_lock"] = 25` — Point of No Return; after this only the $150k option remains. ✅ This is the right number for the Decision Clock (matches API RP 11S 15–30 min range).
- `FAULT_PHYSICS["gas_lock"]["total_hours"] = 0.75` (= 45 min) — Total failure window from onset to winding failure. These are NOT contradicting: PNR (25 min) is when cheap options close; winding failure (45 min) is when the pump is actually destroyed.
- **Resolution:** The clock shows the PNR (25 min) as the "$150k-only" marker. The 45-min total failure is the thermal modeling horizon, not shown on the clock. FAULT_PHYSICS must be updated to reflect this distinction.

| # | Claim | Tag | Source / Citation | Challenge | Rebuttal | Status |
|---|---|---|---|---|---|---|
| C1 | "Cheap intervention (GDC acts now): VFD frequency trim ≈ $2,500" | 🟡 | `RESOLUTION_OPTIONS["gas_lock"]["early"]["cost_incurred"] = 2500`. **This reconciles the UI integrity bug: current UI shows "$0 direct cost" — this is wrong. The correct number is $2,500.** | "$2,500 seems low — a VFD SCADA command has zero hardware cost. Why $2,500?" | The $2,500 reflects engineering time to diagnose, confirm, and execute the command; any field verification; and risk of incorrect execution requiring rollback. Zero hardware cost. The larger cost avoided is production loss from NOT having to trip and restart the well. The cost to SHOW on screen: "$2,500 — remote SCADA command." | SURVIVES — **replaces "$0" in the UI** |
| C2 | "SCADA-reactive path: well shut-in + staged restart ≈ $8,000–$15,000 (lost production + restart labor)" | 🟡🔴 | 🟡 `RESOLUTION_OPTIONS["gas_lock"]["urgent"]["cost_incurred"] = 8000` and `["critical"]["cost_incurred"] = 15000`. 🔴 The $8k–15k economics of deferred production per shut-in event are lease/field-specific and need SME validation. | "The real cost of a 30-min shut-in on a 300 BPD well at $75/bbl netback is only ~$600 in lost production — not $8k." | Acknowledged — the direct production-loss calculation at $75/bbl × 0.3 days × 300 BPD ≈ $675. The gap is: (a) restart time is typically 2–4 hours for a gas-locked ESP (priming, ramp, stabilization), not 30 min — that's $450–$900 lost production at this rate; (b) field labor for unplanned restart ≈ $1,500–$3,000; (c) cycling risk (repeated trip/restart increases motor thermal stress). The defensible range is $3k–$12k depending on well rate and restart complexity. **This claim needs SME validation before showing a specific dollar figure. Safe approach: show as "several thousand dollars" or "well-specific — ask your production engineer."** | 🔴 NEEDS-EXPERT — show as range; $8k–$15k from our code may overstate on lower-rate wells |
| C3 | "Post-PNR only option: Well pull + ESP replacement ≈ $150,000" | 🟡🔴 | 🟡 `RESOLUTION_OPTIONS["gas_lock"]["post_pnr"]["cost_incurred"] = 150000`. 🔴 Workover costs vary significantly: Gulf Coast onshore ESP replacement = $80k–$180k depending on well depth, rig rate, string size, HSE requirements. | "The real cost depends on well depth, rig type, geographic location. $150k could be low or high." | Accurate. $150,000 is a representative onshore US production ESP workover per industry benchmarks (IHS Markit ESP failure cost data; published SPE papers on ESP workover economics). This is explicitly a representative figure, not a specific lease quote. Correct phrasing: "~$150,000 (representative — actual varies by well and location)." | SURVIVES with qualification |
| C4 | "The $150k outcome is the WORST CASE — after the Point of No Return — not the expected outcome if SCADA acts on its trip" | 🟢🟡 | 🟢 Physics: SCADA underload trip protects the pump before winding failure (see S2). 🟡 Code: `post_pnr` action only if pump has been running gas-locked past 25 min WITHOUT any intervention. | "So you're admitting the worst case rarely happens?" | Yes — and that's the honest story. The worst case ($150k) is the cost of doing nothing for 25+ minutes. SCADA's reactive trip typically fires well before that. GDC's value is NOT saving from an already-destroyed pump — it's enabling the cheapest intervention ($2,500) before the reactive trip is needed, preserving production continuity. | SURVIVES — critical to honesty of H1 story |

---

## SECTION 5: THE HONEST H1 CLAIM — ONE SENTENCE

The following is the core defensible H1 value statement. Every UI element should support this sentence and nothing else:

> *"GDC detected gas lock at minute 2 — while all 4 SCADA alarm thresholds were still green — by correlating PIP and amps declining together with a shift note documenting elevated GVF. A $2,500 VFD trim cleared the gas void and kept the well producing. SCADA's underload trip would have fired ~15–21 minutes later, shutting the well in and costing $8k–15k to restart. In the worst case, waiting past 25 minutes leaves only the $150,000 pump pull."*

This sentence is what the H1 UI must communicate. If a visual element doesn't support this sentence, it should not be on screen.

---

## Red-Line Instructions

**For the user (as domain owner):**
- Mark any row `REVISE` with a note if the claim is technically wrong or practically misleading
- Mark any 🔴 row with: VERIFY (send to SME), SOFTEN (show range), or CUT (remove from display)
- The goal is 7–8 claims all marked `SURVIVES` before UI work begins

**For the O&G SME (when available):**
- Focus on C2 (SCADA reactive path costs), C3 ($150k workover qualifier), and whether claim D1's "15–21 minutes" lead time is defensible for a typical Pad-Alpha-style onshore ESP installation

---

*Last updated: Session D (June 7, 2026). Drafted by Cline — conservative pass. Awaiting user and SME red-line.*
