# The H1 and H2 Journey — How We Challenged Our Way to Where We Are

**Date written:** June 11, 2026 (Session AR)  
**Audience:** Stakeholder-readable; every beat cross-referenced to the technical record.  
**Purpose:** The demo's credibility comes from surviving challenge, not from being right the first time. This is the honest record of where each scenario started, what dismantled it, what survived, and why what survived is defensible.

---

## §0 — The One Idea That Survived Every Pivot

**STATE vs. CONTEXT.** `DEMO_MASTER.md §3`

Sensors report the *current value* of a physical measurement — PIP, amps, vibration, temperature. They report STATE. They are excellent at this. Advanced APM platforms (GE SmartSignal, AVEVA PRiSM, Aspen Mtell) score STATE signals with calibrated ML models across multiple sensors simultaneously. We concede both tiers honestly.

What sensors and APM platforms structurally cannot report is **CONTEXT**: equipment history, recent human interventions, GOR trends, adjacent-asset events, regulatory constraints. Context originates from human activity and field events, and is recorded only in unstructured documents — shift notes, sonic logs, lab reports, work orders, maintenance records.

**GDC's only claimed moat:** fuses unstructured field documents via vector-RAG against the live signal and synthesizes the action-determining context in seconds. No SCADA/APM product does this — architecturally impossible for them, not because they are unsophisticated, but because their data model is sensor-tag-based.

Every change described below was us arriving at this idea more honestly. Detection speed was repeatedly conceded. The document-fusion moat is what each pivot converged toward.

---

## §1 — H1 DISCERN: The Ambiguous Unloading Event

### Where we started — *detection-speed and supply-chain lead time*

**Circa Session H / `archive/WHY_THESE_SCENARIOS.md`**

The original H1 scenario was **ESP sand ingress** — an impeller erosion failure with a 14-day predictive window vs SCADA's 24-hour alarm. The headline was: *"GDC predicted this 14 days out. SCADA would have told you 24 hours out — too late to avoid the 12-day parts lead time."* The value proposition was almost entirely **detection speed** and the supply-chain buffer it creates.

The scenario was later replaced with **ESP gas-lock vs. fluid-drawdown** — a more vivid unloading event — but kept the same detection-speed thesis: GDC detects multivariate decline before SCADA thresholds fire, and that lead time lets operators act before the failure window closes.

This framing dominated from Sessions H through AN.

---

### Challenge 1 — *Advanced APM ties detection* (Session AN)

> *Hostile rebuttal: "A best-of-breed APM (SmartSignal, Mtell) does adaptive multivariate ML across all four sensors. It would fire before your SCADA threshold too — your 'lead time' is only against threshold SCADA, not against best-in-class."*

**Honest answer:** Correct. `DEMO_MASTER.md §3 L2` explicitly concedes: threshold SCADA hand-authors per-well rules; advanced APM does adaptive ML. Against best-of-breed APM, GDC's L2 detection advantage converges. The "8-minute lead time" story was honest only against threshold SCADA as deployed on most legacy fleets — a real and significant market segment, but not a categorical claim.

`SESSION_LOG.md — Session AN: "detection-speed is conceded — advanced APM ties us on multivariate ML."` Rated: our L2 edge is supporting context, never the headline.

---

### Challenge 2 — *Shut-in is the safe default anyway* (Session AN)

> *Hostile rebuttal: "On an ambiguous unloading alarm, any competent engineer shuts in. Shut-in is safe for both gas lock and drawdown. The rational default doesn't need GDC — it just defers production temporarily."*

**Honest answer:** Also correct. The shut-in path is genuinely safe for both faults. If an operator shuts in without GDC, no pump dies. The loss is deferred production, not catastrophic failure. This meant the H1 scenario's headline — "GDC saves you from the expensive wrong action" — was overstated.

`SESSION_LOG.md — Session AN: "shut-in is the rational safe default... the 'contrived and weak' feeling traces precisely to framing an efficiency claim as a SCADA-competition victory."` This was the deeper honest finding that forced the reframe.

---

### The turn — *L3 document-fusion as the sole moat* (Sessions AO → AP)

**Ruling locked at `7e7af08` (Session AO). `DEMO_MASTER.md §4 — RULING LOCKED`.**

After applying both concessions, what survived:

1. **A class of fault pairs produces genuinely ambiguous telemetry** (PIP+amps declining together on an intake-only string can't be discriminated by any sensor the well has). The ambiguity is a physical measurement constraint, not a model limitation.
2. **The rational safe default (shut-in) is production-deferring.** GDC's L3 document fusion turns the policy default into a confident, production-preserving action — in seconds.
3. **This scales at fleet level across 200–500 wells** where no engineer has time to hand-correlate a sonic log + separator test + shift note for every ambiguous alarm.

What was removed: the lead-time race framing, "Smart SCADA" language, the pump-seizure strawman. `SESSION_LOG.md — Session AO.`

Bayes posterior further softened from 99.6% → 93.1% at Session AP (naive-Bayes inflates correlated findings; conservative correlation haircut applied). `RED_TEAM_LEDGER.md RT-10; SESSION_LOG.md — Session AP.`

---

### Where we landed — *Cited-evidence analyst*

**H1 deployed state: production (all 6 briefing panels, Bayes 93.1%).** `DEMO_MASTER.md §4.`

The H1 story in one sentence: *SCADA alarm fires — cause unknown — standard policy is a production-deferring shut-in; GDC fuses three field documents in seconds and hands the operator a cited verdict that turns the policy default into a confident, production-preserving action.*

The moat is **L3 document fusion → cited actionable verdict**, not detection speed, not sensor accuracy, not SCADA blindness. XGBoost is the router that aims L3 fusion pre-threshold. The document retrieval is the claim.

---

## §2 — H2 CLASSIFY: Three Scenarios, Not One

### Origin A — *Mud-pump valve washout* (original deck)

**`archive/WHY_THESE_SCENARIOS.md — Scenario 3`**

The original H2 analog was a **mud-pump valve washout** on a drilling rig. The mechanism: the driller manually increases SPM to maintain standpipe pressure as efficiency drops, inadvertently hiding the fault from SCADA. GDC detects the compensation behavior (rising SPM against flat pressure = declining volumetric efficiency). The value: a controlled pump swap instead of a stuck-pipe event ($500k+).

The scenario was a detection-efficiency play — same thesis as H1's original arc: GDC sees what SCADA misses because SCADA sees compensated tags, not underlying efficiency.

This scenario was left behind when the project pivoted to a production-focused ESP demo.

---

### Origin B — *Slug flow introduced; physics corrected* (Session V)

**`SESSION_LOG.md — Session V; RED_TEAM_LEDGER H2-1`**

Slug flow replaced the mud-pump scenario as H2's story: cyclic vibration + flat motor temperature = surface gas/liquid slugs, not a failing bearing. The discriminator: bearing wear raises vib AND temp; slug flow raises vib while temp stays flat (pump hydraulically healthy, cooling nominal). Cost contrast: $1,500 surface truck roll vs $150k pump pull.

This required a physics correction at Session V: the original framing claimed "surface slugs mechanically shock the gauge 2 miles down the tubing string." That failed basic mechanical engineering scrutiny (2 miles of damped clamped pipe). Corrected to: in-string multiphase slug loading at the pump *intake*, where the gauge physically sits. `RED_TEAM_LEDGER H2-1 — CRITICAL, FIXED Session V.`

---

### Challenge — *Dual-AI red-team; scenario invalidated* (Session AR)

**`RED_TEAM_LEDGER H2-9 through H2-12, H2-C1 through H2-C3; SESSION_LOG Session AR`**

Both Gemini (web-enabled) and Claude Opus (web-enabled) independently rated four H2 claims as **FAILS**:

| # | Claim | Verdict | Why |
|---|---|---|---|
| H2-9 | Flat winding temperature = categorical bearing/slug discriminator | **FAILS** | RTD is in the *motor*; bearings are in the *pump/protector*, thermally separated. Early mechanical wear doesn't move the motor RTD. In a high-GOR well, gas at the intake *reduces cooling* → temp trends **up, not flat** — the discriminator runs backwards. |
| H2-10 | $150k pull vs $1,500 truck roll | **FAILS (false dichotomy)** | The real operator baseline for cyclic amps/vib is **choke/VFD adjustment first** — the same $1,500 action, reached from the amp chart without GDC. No competent engineer jumps to a rig on a sub-HH vibration trend. |
| H2-11 | L3 moat on slug flow | **FAILS** | Cyclic amps-with-recovery + cyclic PIP is a **telemetric signature** — APM reads it. Documents only corroborate. Same failure class as H1 pre-reframe: deciding variable reachable without L3. |
| H2-12 | "APM stops at anomaly score" | **FAILS (over-concession)** | Mtell can classify a *trained* failure mode and attach a canned SOP. We were conceding less than what APM actually does. |

Additional cross-cutting integrity findings (`RED_TEAM_LEDGER H2-C1..C3`):
- Downhole ESP gauges report vibration in **g** (0–5 g range), not mm/s (surface ISO 10816 convention). Showing mm/s signals the scenario was written by a surface-PdM engineer, not an ESP specialist.
- ISA-18.2 governs **alarm management and rationalization**, not trip levels. Numeric trip levels come from the OEM. Misattributing them signals a standards-compliance gap.
- A single softmax confidence percentage is "overfit theater" to an APM-literate audience. Replace with the evidence chain.

**The root failure was the same as H1's pre-reframe:** the deciding signal (cyclic amps+PIP) is in the telemetry. The documents confirm what the sensors already show. L3 fusion is adding latency reduction and fleet-scale automation, not a categorical capability the sensor can't carry.

---

### The turn — *Scenario invalidated; 4-survival-test gate created*

**No code was written for the slug-flow briefing — correctly. The scenario was invalid before build.**

The dual-red-team also surfaced the meta-lesson that stopped the cycle: **the "categorically off-sensor" test.** A scenario is only a categorical L3 moat if the deciding variable is *architecturally impossible* to put on a sensor — not just "currently not integrated."

Four survival tests now locked in `.clinerules`:
1. **Discrete past event** — a specific thing that happened, not a slow drift.
2. **Categorically off-sensor** — no sensor on this machine can ever carry this variable.
3. **APM mis-routes** — best-of-breed APM would route to the wrong, expensive action.
4. **Common and material** — frequent enough that fleet-scale automation has defensible ROI.

Slug flow fails tests 2 and 3. The test doesn't ask "do they have the document integrated?" — it asks "could a sensor ever carry this?" The telemetry carries it. Scenario out.

---

### Where we landed — *Frac-hit candidate; pending validation*

**`DEMO_MASTER.md §5 — Status: INVALIDATED, under reframe.`**

Committed reframe: **offset-well frac-hit interference.** A neighbor operator fracs a nearby well; your ESP well's pressure/rate shifts and the telemetry looks like a downhole problem. The deciding variable — *which neighbor well was fracked, on what date, at what stage count* — exists **only** in the neighbor's frac schedule, state regulatory filings, or a partner completion notice. It is categorically not on any sensor on your well. APM mis-attributes the interference signature to downhole pump trouble. Frac hits are a well-documented, economically significant Permian production problem.

This scenario passes all 4 survival tests structurally. It must still be validated via in-session hostile-engineer red-team + dual-AI pass **before any wireframe or code is written.** `DEMO_MASTER.md §5; .clinerules — Scenario Gate.`

---

## §3 — What the Challenges Taught Us

### The recurring trap: deciding variable reachable from telemetry

Both H1 (original) and H2 (slug flow) fell into the same failure class. In each case, the scenario looked compelling on first read — vivid fault, clear cost delta, sensor evidence you could show. But under adversarial scrutiny, the deciding variable turned out to be *in the telemetry* or reconstructable from it, which means L3 document fusion adds efficiency (latency, scale, automation) but not a *categorical* capability gap. An experienced APM engineer or a sharp SCADA engineer can reach the same answer from the sensor data alone.

The test that would have caught both, stated plainly: *"If GDC's documents were missing, could a best-of-breed APM platform — or a 20-year ESP engineer at 2 AM — still make the right call from the sensor screen?"* For slug flow, the answer is yes (cyclic amps+PIP is unambiguous once you've seen it before, and Mtell classifies it if trained). For the original H1 detection story, the answer is also yes (the rational call is shut-in, which is safe regardless). In both cases, the documents were adding evidence to a conclusion the data already supported.

The categorical moat is only real when the document contains a variable that **no sensor on the asset can ever carry** — a third-party event, a supply/service history, an adjacent-asset action — and when that variable is what **changes the action and the cost**.

### The fix: scenario gate + in-session red-team persona

Two structural changes now in `.clinerules`:

**The Scenario Validation Gate** requires every new H2/H3 scenario to pass 4 explicit survival tests before a wireframe is drawn. This stops the "looks good, build it" pattern that produced both the original H1 and the slug-flow H2.

**In-Session Red-Team Discipline** requires adopting the hostile-engineer persona ("I am a 20-year production/ESP engineer who has run SmartSignal and Mtell") and writing the one-sentence attack on every claim *before* defending it. The Gemini and Opus passes in Session AR caught the thermal-path kill shot and the false-dichotomy cost structure — findings I missed in the coding-agent deference stance. The fix is persona, not capability.

### Same-model variance: context and stance, not inherent ability

The quality gap between in-Cline reasoning and the Gemini/Opus external passes came from **framing and context load**, not from a different model. The external passes had: (a) a hostile-engineer adversarial persona, (b) a clean focused context window, (c) web access for citations. The in-Cline pass had: (a) coding-agent deference bias, (b) a context window carrying large file scaffolding and tool infrastructure, (c) no web access.

The MCP `gemini_second_opinion` tool being set up next session closes gap (c). The in-session red-team discipline closes gap (a). Gap (b) is partially mitigated by batching editorial work (like this document) outside of large-file editing sessions.

---

## §4 — Cross-Reference Index

| Claim / event | Source |
|---|---|
| Original H1: ESP sand-ingress, 14-day detection | `archive/WHY_THESE_SCENARIOS.md — Scenario 1` |
| H1 reframed to gas-lock vs drawdown | `SESSION_LOG.md — Session H / J` |
| Detection-speed thesis dominant | `SESSION_LOG.md — Sessions H through AM` |
| H1 Challenge 1: APM ties multivariate ML | `SESSION_LOG.md — Session AN; DEMO_MASTER §3 L2` |
| H1 Challenge 2: shut-in is safe default | `SESSION_LOG.md — Session AN` |
| H1 turn: cut detection race; L3 as sole moat | `SESSION_LOG.md — Session AO; DEMO_MASTER §4 RULING LOCKED` |
| Bayes 99.6% → 93.1% (correlation haircut) | `SESSION_LOG.md — Session AP; RED_TEAM_LEDGER RT-10` |
| Original H2: mud-pump valve washout | `archive/WHY_THESE_SCENARIOS.md — Scenario 3` |
| H2 Origin B: slug flow introduced | `SESSION_LOG.md — Session V` |
| H2 slug-flow physics correction (H2-1) | `RED_TEAM_LEDGER H2-1; SESSION_LOG Session V` |
| H2 Challenge: dual-AI red-team 4×FAIL | `RED_TEAM_LEDGER H2-9..H2-12; SESSION_LOG Session AR` |
| Cross-cutting integrity (vib units, ISA-18.2, confidence) | `RED_TEAM_LEDGER H2-C1..C3` |
| Scenario invalidated; survival gate created | `DEMO_MASTER §5; .clinerules — Scenario Gate` |
| Frac-hit candidate committed | `DEMO_MASTER §5; SESSION_LOG Session AR` |
| STATE-vs-CONTEXT thesis (settled) | `DEMO_MASTER §3` |
| L1/L2/L3 three-tier concession stack | `DEMO_MASTER §3 — Three-Tier Stack table` |

---

*Last updated: Session AR, June 11, 2026. Update when H2 frac-hit scenario is validated and locked.*
