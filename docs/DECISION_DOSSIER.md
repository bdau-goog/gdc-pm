# GDC Demo — Decision Dossier (Sessions BS+48 + BS+49)
**Date:** 2026-06-25 · **Branch:** feature-trio-clean · **Commit range:** 94f99e6 → (current)
**Status:** Architecture and strategy locked for H1, H2, H3, and the "Why GDC" platform tab. Build plan documented.

**⚠ READ THIS FILE BEFORE ANY H1/H2/H3/PLATFORM CODE OR RECORDING.**

This dossier is the single source of truth for every strategic, architectural, and physics decision made in Sessions BS+48 and BS+49. Every option that was considered and eliminated is recorded here with its reason, so no future session re-opens it. The H3 content from the previous `H3_DECISION_DOSSIER.md` is incorporated verbatim below and should not be read separately.

---

## §0 — HOW TO USE THIS DOSSIER

1. Read the **Shared Premises** (§1) first — they apply to every horizon and the platform tab.
2. For any horizon you're about to work on, read its **Decision Record** (§2, §3) before touching code.
3. For the platform tab, read **§4**.
4. Before writing any on-screen claim, verify it against the **Must-NOT-Say lists** in the relevant section.
5. If a hostile RT returns a FAILS on something in this dossier, write the rebuttal here before acting on it. Do not delete locked decisions based on a single RT pass.

---

## §1 — SHARED PREMISES (cited, apply to H1 + H2 + H3)

These are first-class cited foundations. Reference them from every horizon's framing rather than re-asserting them locally.

### Premise 1 — RTOC Span-of-Attention (wells per engineer)
**Claim:** A single surveillance engineer in an upstream RTOC monitors *hundreds* of artificial-lift/ESP wells simultaneously. This is why proactive per-well research is architecturally impossible without automated tooling — not negligence.

**Citations (Gemini Search, 2026-06-25):**
- **YPF Decision Support Center:** 2 optimization engineers monitor **560+ artificial-lift wells** (~280 wells/engineer) — source: industry conference paper via onepetro.org/esss.com
- **SLB Artificial Lift Surveillance Center (ALSC):** **847 wells** monitored over an 8-day surveillance window — source: drillingcontractor.org/SLB materials
- **Conservative display figure (defensible range):** "hundreds of artificial-lift wells per surveillance engineer" — YPF/SLB figures support 280–500+ range. Do NOT cite a hard floor below 200 without confirming it with a production-engineer SME.

**What this defeats:** "Why can't the engineer just check the PM log?" — The engineer cannot proactively check the PM log for 280+ wells on every shift. GDC's fleet-scale automation is what makes the possible-in-principle diagnosis happen automatically in practice.

### Premise 2 — APM/ML Penetration (industry reality)
**Claim:** Advanced predictive maintenance (SmartSignal/PRiSM/Mtell tier) is the *minority*, not the default. Most wells run on threshold SCADA.

**Citations (Gemini Search via uptimeai.com, reliamag.com, 2023):**
- Only **~24% of O&G companies** run any predictive maintenance strategy
- Only **~11%** reach ML-maturity (the full SmartSignal/PRiSM/Mtell tier)
- Even super-majors are **mixed** — advanced APM does NOT blanket every well

**Two-tier implication (use this framing, NOT "APM is dumb"):**
- **Tier 1 (~76–89% of wells): Threshold SCADA only.** GDC's XGBoost pre-threshold multivariate scoring is a *genuine* detection advantage here. No APM incumbent to defeat — pure greenfield.
- **Tier 2 (~11–24% with some APM): Best-of-breed APM.** GDC's detection edge narrows. GDC wins here on **L3 document fusion** (APM is sensor-only; it cannot read the vendor PM portal, PVT lab report, or workover record). This is the CATEGORICAL moat — not a speed claim.

**MUST-NOT-SAY:**
- ❌ "GDC detects faster than SmartSignal/PRiSM/Mtell" — not proven
- ❌ "APM systems are unsophisticated / can't do ML" — they can and do
- ✅ "APM classifies sensor *patterns* correctly but cannot read the documents that carry the *cause*" — survives

### Premise 3 — RTOC Structure (regional, not monolithic)
**Claim:** A major upstream operator runs a **handful of regional RTOCs/IOCCs** (typically 2–10+), each governing thousands of wells across a geographic basin. No single giant RTOC and no pad-per-RTOC.

**Citations (Gemini Search via Chevron/Exxon/Shell/BP/Aramco sources, 2026-06-25):**
- **ExxonMobil:** "Vantage" centralized hub for Permian/Bakken/Denbury + prior regional drilling centers
- **Chevron:** Multiple IOCCs — Midland TX (Permian), N. Colorado, Kazakhstan (Tengiz), Houston Wells DSC, Houston pipeline center
- **Shell:** New Orleans deepwater + Gulf of Mexico IOC + global WRFM network
- **BP:** "Hub-and-satellite" architecture (Houston RCC + multiple satellite locations); originated 1997
- **Saudi Aramco:** 4IR Center (Dhahran), Drilling/Workover RTOC (2008), Geosteering Center (2005, 75 rigs)

**What this means for GDC scale story:** The right deployment shape is **one GDC cluster per regional RTOC** (handful per major), each governing the basin's thousands of wells. This is the "fleet-management" pitch — not "one global instance" and not "one per pad." The scale revenue for Google comes from data-gravity × AlloyDB × continuous inference × the training loop on many wells per instance.

**MUST-NOT-SAY:**
- ❌ Hard RTOC count claims without qualification (varies by operator)
- ❌ "One RTOC per well pad" (pads are typically unmanned)
- ✅ "A handful of regional operations centers, each governing thousands of wells"

---

## §2 — H2 DECISION RECORD (Classify — Maintenance Provenance)

### 2.1 The Problem We Found (Sessions BS+48/BS+49)
H2 as originally filmed/planned was **too close to H1 in framing**, and its treatment was too thin to survive the "why not just check the PM log?" challenge. Specifically:
1. Both H1 and H2 were framed as "ambiguous sensor signal → documents resolve it." H2 is *not* ambiguous — the signal is clear. The framing was wrong.
2. H2 had no explicit answer to "why GDC, not the engineer?", whereas H1 and H3 both have more obvious answers.
3. The H2 recording used an 8-week slow-motion transport playback — conceptually wrong for an alarm-triage story.
4. The cost-dichotomy was fragile: if the bearings are already damaged by the time vib crosses ISA-HI, "avert the pull" is an overstatement.

### 2.2 The Sharpened Thesis (LOCKED)
> **H2 is the opposite of H1. H1 has an AMBIGUOUS signal where neither cause can be confirmed from sensors alone. H2 has a CLEAR, CONFIDENT signal — and the machine routes to the wrong, expensive action because the cause lives off-sensor in a document it cannot read.**
>
> *"Clear signal. Confident APM verdict. Wrong action."*

**The core structural insight:** APM is RIGHT about the *symptom* (bearing wear pattern — rising vib + amps + declining efficiency = textbook mechanical degradation). APM is WRONG about the *cause* (paraffin restriction, not mechanical failure). The provenance lives in three documents no sensor carries. That's the categorical moat.

### 2.3 The L2→L3 Earliness Engine (the actual "why GDC" mechanism for H2)
This is the mechanism that resolves the physics risk and the "why not the engineer" challenge simultaneously.

**The engine:**
1. **L2 (XGBoost multivariate):** scores the *joint* drift — efficiency softening + amps creeping + vib rising TOGETHER in a correlated pattern — and crosses a **probability threshold BEFORE any single tag crosses its hard SCADA limit.**
2. **L3 (router to document research):** that early L2 anomaly is the trigger that sends GDC to the document corpus for *this specific well, automatically, fleet-wide.* The engineer (280 wells) cannot proactively do this for every quiet-but-anomalous well. GDC can.
3. **The verdict:** pulls overdue PM log + PVT report + prior-pull healthy-bearings record → names paraffin restriction → "surface treatment, NOT pull."

**Why earliness is the key to honest physics:** The hot-oil/surface treatment *genuinely averts the pull* when caught BEFORE the vibration reaches the hard ISA-18.2 HI alarm (4.0 mm/s). By that point, bearing damage may already be developing (see §2.6 Physics). GDC's L2 model catches the pattern while still in the pre-alarm developing phase — the window where the cheap surface fix works and bearing damage is not yet inevitable.

**The honest claim (survives the physics):** "GDC's model notices the off-nominal pattern early — before the hard alarm — and automatically researches the well's own documents to name the real cause: paraffin restriction, not mechanical wear. Caught at fleet scale and automated speed, a low-cost surface treatment averts the pump pull while the intervention is still effective."

**MUST-NOT-SAY (H2 — physics-grounded):**
- ❌ "The vibration crossed the ISA-HI alarm and the pump is pristine — hot-oil was all it needed" (once vib crosses HI, bearing damage may exist; this overclaims)
- ❌ "Hot-oil perfectly removes all paraffin" (can be incomplete; formation damage risk if poorly executed)
- ✅ "Low-cost surface remediation" / "surface treatment" (not "hot-oil guarantees full removal")
- ✅ "Catches it early enough that the surface fix is still effective" (honest, physics-grounded)

**Honesty boundary on detection tier (same as H1, now explicit for H2):**
- ✅ "Earlier than threshold SCADA" — the L2 pre-threshold edge is genuine
- ❌ "Detects faster/earlier than best-of-breed APM" — not proven; APM may also detect the anomaly
- ✅ "Resolves the CAUSE (paraffin vs bearings) that even APM cannot — by reading the documents APM cannot access" — this is the categorical moat APM cannot replicate

### 2.4 Three-Act Treatment

**Act 1 — The Confident Wrong Answer (the hook):**
Clear signal: vib climbing over weeks through ISA alarm, efficiency down, amps up. Best-in-class APM classifies **bearing wear** with high confidence → routes to pump pull (~$70k–$100k). Frame explicitly: **APM is RIGHT about the symptom. Wrong about the cause. The cause is off-sensor.**

**Act 2 — The Provenance (where GDC plays — demonstrable):**
GDC's L2 model detects the joint-drift anomaly pre-alarm. Routes to L3: retrieves three siloed documents:
- **Doc 1:** Chemical vendor service log — hot-oil PM **52 days overdue**, third-party logistics delay documented (vendor portal, NOT in SCADA)
- **Doc 2:** Fluid PVT report — WAT ~118°F confirmed, 8.3% wax content, 90-day treatment interval required (lab report PDF)
- **Doc 3:** Prior pull record — bearings **NORMAL** 18 months ago → bearing-age hypothesis eliminated (workover completion report)

Synthesis: *"Paraffin restriction from missed PM — NOT bearing wear. Dispatch surface remediation. Do NOT pull."*

**Act 3 — The Fleet-Scale Moat (Premise 1 + 2):**
One engineer, 280+ wells. The engineer opens a well's page when it alarms — which by then may be too late for the cheap fix. GDC flags it automatically, proactively, fleet-wide, from the first anomalous murmur. Scale is what makes "caught early" real, not aspirational.

### 2.5 H2 Scenario Differentiation from H1 (critical — must not blur)

| | **H1 — Discern** | **H2 — Classify** |
|---|---|---|
| The signal | **AMBIGUOUS** — PIP+Amps decline; two causes, sensor can't distinguish | **CLEAR** — vib+amps+eff pattern = bearing wear with confidence |
| The machine's state | "Cannot determine — both causes possible" | **"Certain — and wrong"** |
| The danger | Acting on wrong cause in a live event (drawdown + trim seizes the pump) | Acting on a confident-but-wrong expensive action (pull instead of surface treat) |
| The deciding context | Ambiguity-resolution (which cause?) | Provenance-resolution (why this symptom? what event caused it?) |
| Time character | **Live event unfolding over minutes** (playback needed to show lead-time gap) | **History-already-happened alarm** (load at alarm state; no slow playback) |

### 2.6 Physics Grounding (wax → bearing timeline, cited)

**Source:** Gemini Search via osti.gov, swpshortcourse.org, researchgate.net, onepetro.org, worldoil.com (2026-06-25)

Key findings:
- Early hot-oil treatment **CAN restore normal operation and avoid a pull IF prompt and effective**
- Once vib rises significantly, bearings **may already be experiencing damage** — excessive shaft movement → lubrication loss → metal-to-metal → accelerated wear
- Failure conditions can develop **within hours or days** under severe restriction (motor parameter deviations observed 0.6–1.8 days before failure in some datasets)
- **Removing the restriction is MITIGATION, not full reversal** — if significant wear has occurred, vibration may not return to pre-damage levels
- **Early intervention is the key** — the longer the restriction continues, the less effective the surface treatment becomes

**H2 build-in safeguard:** The scenario explicitly fires the GDC alert at `gdc_detect_idx` (pre-alarm), not at `scada_alarm_idx` (hard alarm crossed). This is the honest state: GDC flags it early, while the remediation is still fully effective. The UI must load at the alarm-triage state (instant-triage), but the story must emphasize *when* GDC acted relative to the alarm.

### 2.7 H2 UI Changes Required (build tasks)

**Task H2-1 (one-line code change):** Load scenario at active alarm
- File: `static/app.js` function `loadH2Scenario()` ~L2057
- After `this.h2ReplayData = data;` add: `this.h2CursorIdx = data.scada_alarm_idx || 0;`
- Effect: tab opens with 90-day static history plotted, VIB-HI alarm already active, doc cascade fires
- Verify: `curl http://gdc-pm.bdau.io/api/h2/scenario-replay` → confirm `scada_alarm_idx` present in JSON

**Task H2-2 (VO/slide reframe):** Update `slides/h2.html` kickers/subs and VIDS_PRODUCTION_MASTER.md B2 scene cards to reflect sharpened thesis
- Slide 2 must NOT say "ambiguous" — it should say "clear signal, wrong action" or equivalent
- Slide 2 kicker: "THE SIGNAL SAYS PULL" (already in place — CONFIRM no regression)
- Scene cards B2-P1→B2-S4 VOs must carry the fleet-scale "caught early across hundreds of wells" framing
- Verify against VIDS_PRODUCTION_MASTER.md §SECTION 2 current VO text

**Task H2-3 (recording prep):** Once H2-1 and H2-2 verified live, record B2-P1 through B2-S4

### 2.8 Eliminated Options for H2

| Option | Why eliminated |
|---|---|
| Keep 8-week slow playback | Wrong register for a history/alarm story; makes it look like the operator was asleep for 8 weeks |
| "APM is dumb / missed it" framing | Strawman — APM correctly identifies bearing-wear pattern; it misses the *cause*, not the symptom |
| "Hot-oil guarantees full recovery" | Overclaims — bearing damage may already exist once vib crosses HI; repair is mitigation not reversal |
| "GDC detects before APM" | Not proven; APM may also flag the anomaly; L3 provenance is the categorical win, not detection speed |
| Emphasize single-well economics alone | Leaves "why not the engineer?" unanswered; fleet-scale (Premise 1) is the necessary second half |

---

## §3 — H3 DECISION RECORD (Optimize — FINAL LOCKED Session BS+51)

**⚠ This section supersedes H3_DECISION_DOSSIER.md entirely. Do not read that file separately.**
**Session BS+51 replaced the A-5 thermal-trim edge beat with a curtailment re-allocation edge beat after two independent hostile passes both returned FAILs on the original approach.**

### 3.1 Eliminated Options (do NOT reopen)
- ❌ Edge does the fleet optimization — shared gas ceiling requires global view
- ❌ Edge "corrects" gas overrun — gas ceiling is central, already IN Vizier objective; evaluate_field() IS Vizier's oracle
- ❌ Single-batch Vizier as "learns per trial" — suggest_trials(count=15) is one batch; silent lie
- ❌ "Operators don't trust control vendors with data" — FUD, RT FAILS
- ❌ **Edge trims A-5 down to protect motor from overtemp** — VFD's own overtemp derate/trip already does this, locally and faster; edge layer is redundant (RT FAILS, Session BS+51 RT Pass 1, Attack 2)
- ❌ **Two-timescale split where edge only protects single motors** — "architecture theater"; a single local controller does the same job (RT FAILS, Session BS+51 RT Pass 1, Attack 5)
- ❌ **Slug flow as trigger** — telemetric signature (cyclic amps + PIP) is in the data; permanently eliminated by .clinerules Scenario Validation Gate

### 3.2 Locked Thesis — Two-Timescale RTO-over-MPC with Curtailment Re-Allocation (BS+51 FINAL)

> **Cloud (Vizier, slow/global/periodic):** divides shared gas budget across the fleet of wells for max revenue. Plans on a nominal, periodically-refreshed snapshot. Output: per-well Hz setpoints pushed down to each pad.
>
> **Edge (GDC, fast/local/continuous):** receives the cloud's plan as a target. When a LIVE, LOCAL constraint changes AFTER the plan was made — specifically a midstream gas-takeaway curtailment (8.0 → 6.0 MMscfd, off-sensor) — the edge re-solves the intra-pad allocation in real time, trimming gassy wells and preserving/lifting oil-rich wells to maximize revenue within the new ceiling. Does NOT round-trip to cloud. Runs offline.
>
> **SCADA + VFD:** execute setpoints; own hard trips and regulatory control. VFD owns per-motor thermal protection. GDC does NOT claim to protect motors (that's the VFD's job — conceded explicitly in VO/copy).
>
> **The defended number:** revenue delta of GDC smart re-allocation vs. dumb-SCADA baseline (uniform throttle or shut-in-gassiest-well). Must be computed live from `evaluate_field()` — never hardcoded.

### 3.3 Physics Hole #3 — REFINED (BS+51)

**Original rule (BS+48):** Edge trims DOWN only; up-reallocation breaches shared gas ceiling.
**Refined rule (BS+51):** The original rule was written assuming the binding ceiling was fleet-wide (the edge has no view of other pads). For the curtailment scenario, the binding ceiling is the **pad's own gathering tie-in**, which the pad edge node fully observes. Therefore:
- **Intra-pad re-allocation (trimming one well DOWN + lifting another UP within the same pad's lower curtailed ceiling) is SAFE** — the edge has complete visibility and authority over its own tie-in.
- **Inter-pad re-allocation STILL requires the cloud** — the edge cannot move gas budget between pads.
- **The curtailed ceiling is still respected at all times** — the edge never exceeds the midstream limit, and any up-move on an oil-rich well is bounded by the new, lower ceiling.

This is more physically accurate (gathering/compression limits bind at the pad/CTB, not basin-wide) and eliminates the "trim-down-only = SCADA bluntness" attack.

### 3.4 Five-Angle Moat (unchanged from BS+48)
1. Greenfield ~76% no ML APM (cited Premise 2)
2. Horizontal platform vs point product
3. Unstructured fusion — CATEGORICAL STRONGEST (APM can't read documents); **H3 curtailment notice is off-sensor, carrying this same moat into H3**
4. Sovereign fleet Model-Ops
5. Data-gravity / outage-tolerance

### 3.5 H3 Build Plan (FINAL, app.py L6701–6900)
1. **Iterative Vizier loop** — 3 rounds of 5 → score → re-suggest (fixes 14/15 infeasible root cause; makes "searches and learns" literally true)
2. **Curtailment re-allocation** — new `curtailment_path` in `vizier_optimize()`:
   - Input: `curtailed_ceiling` (default 6.0 MMscfd, parameterizable)
   - Re-runs existing joint-LP allocator at curtailed ceiling → `curtailed_hz_vec`
   - Runs dumb-SCADA baseline (uniform throttle to new ceiling) → `scada_baseline_hz_vec`
   - Returns `revenue_delta = curtailed_cf - scada_baseline_cf` (must be live-computed, not hardcoded)
   - Returns curtailment constraint doc from AlloyDB pgvector (reuses existing `constraint_doc` machinery)
3. **Presentation (`tab_h3.html`)** — cloud plan panel + curtailment event card + edge re-allocation panel + revenue delta vs. dumb-SCADA + "⏺ Architecture view — system-to-system flow" honesty tag + ✗/✓ iterative trial stamps
4. **Slides/VO reframe** — cloud = fleet optimizer (revenue + conserve equipment); edge = re-allocates under live curtailment; concede VFD/SCADA own protection explicitly; lead with revenue delta
5. **Verify H3-S4 constraintDoc.found=True** — confirm before recording B3-S4

### 3.6 H3 Role — Proof #3, Not Standalone Justification
H3 is the third proof of the off-sensor-context-fusion spine:
- H1: ambiguity-resolution (shift note + sonic log)
- H2: provenance-correction (vendor PM portal + PVT report + prior pull record)
- **H3: constraint-reallocation (midstream curtailment notice)**

Three different decision modes, one fusion primitive = platform argument. H3 alone cannot justify GDC platform adoption. The buy-case is the **Why-GDC platform tab (TASK 5, 5-angle moat)**. Do NOT over-claim H3 as the standalone justification.

### 3.7 H3 Must-NOT-Say (RT-confirmed, BS+51 updated)
1. ❌ "Operators don't trust control vendors" (FUD)
2. ❌ "GDC invented hierarchical control" (it's textbook RTO/MPC)
3. ❌ "Edge does global optimization"
4. ❌ "14 of 15 rejected" as hero stat
5. ❌ "Vendor-neutral" unscoped
6. ❌ GitOps manages PLC/SCADA/Level-1/2
7. ❌ **"GDC saved A-5 from motor burnout / the edge trimmed A-5"** — VFD's job; edge thermal-trim beat is BLOCKED
8. ❌ **"GDC prevents a motor trip"** — VFD and SCADA trip to protect; do not claim to displace this
9. ❌ Revenue delta as a hardcoded number — must be live-computed from `evaluate_field()`

### 3.8 Verified Cloud Facts (live, 2026-06-25)
- Project: gdc-pm-v2 / us-central1; 10 real studies gdc_pad_alpha_field_opt_*
- Latest study 593258648990: 14 INFEASIBLE, 1 feasible (root cause: wide bounds + batch + shared ceiling → fixed by iterative loop)
- suggest_trials(count=15) at app.py L6734 = single batch, NOT iterative → fix before claiming "learns"
- Cost: 100 free trials/mo, $1/trial Bayesian; dev/test safe; no GPU

---

## §4 — "WHY GDC" PLATFORM TAB (new nav tab — RT-hardened)

### 4.1 What We're Answering
The three scenarios prove "why edge AI" and "why context fusion." They do NOT prove "why Google Distributed Cloud specifically." A procurement-level CTO will ask this. The Why-GDC tab answers it, once, for all three horizons, with no competitive mentions.

**The three "why" questions:**
1. Why edge? → Answered by the scenarios + sovereignty
2. **Why GDC specifically?** → Answered by this tab
3. Why Google AI? → Implied by Gemini/Vertex/BQ depth; not belabored

### 4.2 Platform RT Results (gdc-second-opinion, 2026-06-25)
- **Claim 1 (form factor):** SURVIVES-IF-REWORDED — say "validated/certified hardware"; name what's lighter (central patching, remote infra management)
- **Claim 2 (fleet governance):** SURVIVES-IF-REWORDED — must explicitly scope ACM/Config-Sync to "the GDC platform and applications on it, NOT the underlying OT/PLC/SCADA"
- **Claim 3 (Model-Ops "deploy identically"):** ❌ FAILS — "deploy identically" contradicts ESP analytics reality (site-specific conditions, sensor drift → models need local adaptation). Fix: **"deploy BASE models centrally; enable local fine-tuning for site-specific conditions; govern centrally"**
- **Claim 4 ("tens of thousands of locations"):** SURVIVES-IF-REWORDED — needs context; qualify as "proven fleet control-plane lineage" or cite analogous industrial deployments; do not lead with raw number

### 4.3 Locked Three-Reason "Why GDC" Thesis (no competitive mentions)
> **You've decided sovereign edge AI is the answer. Why Google?**
>
> **1. Form factor fit** — GDC runs on validated hardware across connected, software-on-your-hardware, and air-gapped deployments; the right footprint for whatever edge topology your operations require.
>
> **2. Fleet governance** — Anthos Config Management + Fleet Management give you one declarative policy for security, configuration, and version consistency across every GDC site — the platform and the applications on it. Company-wide consistency from one control plane, extending the same tooling you use to govern your cloud GKE fleet.
>
> **3. Sovereign AI platform + Model-Ops depth** — the same Google stack on-prem (GKE, AlloyDB Omni, Vertex AI / Gemini Enterprise): train centrally on your fleet data, deploy **base models** to each edge node with **local fine-tuning for site-specific conditions**, govern rollouts and rollbacks centrally, propagate findings fleet-wide. Backed by Google's enterprise AI + data-services depth.

### 4.4 RTOC Scale Shape for the Tab
Do NOT claim GDC lands at every pad (unmanned; too many). The honest, cited deployment shape:
- **A handful of regional RTOCs/IOCCs per major** (Chevron: Midland + N. Colorado + Kazakhstan + Houston DSC; ExxonMobil: Vantage + regional; etc.)
- **Each RTOC governs thousands of wells** (Premise 2 + 3 above)
- **One GDC cluster per regional RTOC** → fleet governance across that basin's wells
- Scale revenue = data-gravity × AlloyDB × continuous inference × training loop across thousands of wells per instance

### 4.5 Why-GDC Tab Must-NOT-Say (RT-confirmed + principle)
1. ❌ Any competitive mentions (AWS Outposts, Azure Local, DIY) — 100% GDC value-props only
2. ❌ "Deploy models identically" — FAILS, per RT; use "base models + local fine-tuning"
3. ❌ "Config-Sync manages your PLCs/SCADA" — apps+infra only
4. ❌ "Zero OT integration work" — OT integration still required; GDC simplifies the IT/app layer above it
5. ❌ Raw "tens of thousands of locations" as hero number — qualify or demote
6. ❌ "Vendor-neutral" without scoping — scope to "neutral relative to equipment/OEM vendors"

### 4.6 Tab Build Scope
- **New nav tab** (not strengthening existing ⓘ Reference)
- **Content:** three-pillar layout (form factor / fleet governance / sovereign AI platform); RTOC scale shape; "one control plane, N sovereign edge nodes" diagram
- **Architecture reference:** RTOC → GDC cluster → many wells in basin → AlloyDB + models + ACM/FM
- **Connections to scenarios:** "The same platform stack that ran H1/H2/H3 manages your entire fleet identically — except each GDC node retunes its models to its basin's wells."
- **No demo-runnable content** — this is an architecture/procurement beat, not a live interactive scenario

### 4.7 Open Items Before Pixels
- **Branding source-check:** confirm current naming of "Vertex AI / Gemini Enterprise Agent Platform" — what is the correct 2026 product name? Do a grounded search before the tab text is finalized.
- **Analogous industrial deployments citation:** if we cite GDC scale, we need at least one public reference to an industrial/edge deployment (manufacturing, grid, mining) analogous to O&G remote sites.

---

## §5 — H1 CONSISTENCY-AUDIT (read-only, next session)

### H1 does NOT need a redo. The recorded scenes (B1-P1→S4) are untouched.
The three scenarios are now more coherent with H2's sharpened framing and the shared premises made explicit. However, run the following three read-only checks before recording B1-S5/S6:

1. **APM-tier honesty audit:** Confirm no H1 slide/VO claims "GDC detects faster than SmartSignal/PRiSM/Mtell." Should be clean — this rule originated in DEMO_MASTER §3.
2. **Ambiguity-vs-provenance distinction:** Confirm H1 still reads as "genuinely AMBIGUOUS" (not "confident wrong answer") — this is the defining contrast with H2. If any H1 text has drifted toward H2's "clear signal" framing, fix the slide text.
3. **"Why not the engineer?" coverage:** Confirm H1-P4 (MINUTES TO HOURS vs <10 SECONDS) still carries the fleet-scale under-time-pressure argument. With Premise 1 now explicit and cited, H1-P4's claim may benefit from a one-sentence reinforcement ("across hundreds of wells per shift, automatically") — but this is a slide-text brush-up, NOT a re-record of done scenes.

---

## §6 — RT HISTORY (all passes, with file references)

| Pass | Session | Claim area | Result | File |
|---|---|---|---|---|
| RT Pass 1 (framing) | BS+49 | H2 "14/15 rejected + batch as search" | Claims A1/A2/A4 FAILS; H2 proactive-attacks NOISE | /tmp/mcp-results/second_opinion_1782344096.txt |
| RT Pass 2 (validation) | BS+48 | H3 two-timescale + moat | Thesis SURVIVES; vendor-FUD FAILS; "vendor-neutral" SURVIVES-IF-REWORDED | /tmp/mcp-results/second_opinion_1782352813.txt |
| RT Pass 3 (platform) | BS+49 | "Why GDC" 4-reason thesis | 3 SURVIVES-IF-REWORDED, 1 FAILS ("deploy identically") | /tmp/mcp-results/second_opinion_1782385012.txt |

---

## §7 — CITATIONS (all grounded searches, BS+49)

### Search 1 — RTOC Count / Structure
**Query:** How many RTOCs does a typical large upstream O&G operator run?
**Finding:** Multi-tiered hybrid — handful of regional RTOCs per major. Examples: Exxon Vantage (centralized + regional), Chevron multi-IOCC (Midland/N.Colorado/Kazakhstan/Houston), Shell (New Orleans + GoM IOC), BP hub-satellite, Aramco 4IR Center + drilling/geosteering RTOCs.
**Sources:** onepetro.org, chevron.com, exxonmobil.com, drillingcontractor.org, bp.com, aramco.com
**File:** /tmp/mcp-results/search_1782385411.txt

### Search 2 — Wells per Surveillance Engineer
**Query:** Span of control / well-to-engineer ratio in artificial lift / ESP surveillance RTOCs.
**Finding:** YPF Decision Support Center: ~280 wells/engineer (2 engineers, 560+ wells). SLB ALSC: 847 wells monitored over 8-day window. Technologies enabling "many more wells" per engineer by prioritizing critical issues.
**Sources:** onepetro.org, esss.com, drillingcontractor.org, various SPE/industry sources
**File:** /tmp/mcp-results/search_1782385451.txt

### Search 3 — Wax→Bearing Damage Timeline
**Query:** Does early hot-oil treatment avert an ESP pull? Timeline of bearing damage from wax-induced restriction.
**Finding:** Early treatment CAN restore normal operation IF prompt and effective. Once vib rises significantly, bearing damage may already be developing (hours-to-days progression). Removing restriction = mitigation, not full reversal. **Intervention before the hard alarm is the physics-honest framing.**
**Sources:** osti.gov, swpshortcourse.org, parc400.com, nih.gov, researchgate.net, onepetro.org, worldoil.com
**File:** /tmp/mcp-results/search_1782385480.txt

### Earlier Searches (BS+48)
- APM penetration: ~24% any PdM, ~11% ML-maturity — uptimeai.com, reliamag.com (2023)
- Vizier cost: 100 free trials/mo, $1/trial — finout.io
- Paraffin WAT / hot-oil physics — various (Session BG baseline)

---

## §8 — OPEN ITEMS (confirmed before pixels)

| # | Item | Priority | Owner |
|---|---|---|---|
| 1 | **Branding:** Verify current product name "Vertex AI / Gemini Enterprise Agent Platform" (2026) | Before Why-GDC tab text | Next session grounded search |
| 2 | **H3 feasible-rate fix:** iterative Vizier loop — must deploy before H3 recording | Blocking H3 recording | Next session build |
| 3 | **H1 consistency-audit:** 3 read-only checks (§5 above) | Before B1-S5/S6 recording | Next session quick check |
| 4 | **Wax-bearing SME gut-check:** confirm "caught pre-alarm → bearing damage not yet inevitable" framing with Bill Barna or equivalent Permian engineer | Before H2 recording | SME contact |
| 5 | **Wells/engineer figure:** confirm 150–300 range is defensible (YPF/SLB suggest 280–500+; is the lower bound credible?) | Before Premise 1 display | SME or soften to "hundreds" |
