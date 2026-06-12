# GDC Operations Intelligence — Master Demo Specification & Blueprint
**Version:** Session BF (June 11, 2026) — §3 APM two-tier calibration; Lift IQ/sovereignty hostile-pass rewording; 5–15% deployment reality; rejected-claims updated · Session BE: §6 field-level rewrite (Sprint H3-D); STAKEHOLDER_BRIEF.md added; H2 Maintenance-Provenance; Locked Strategy
**Status:** Authoritative Single Source of Truth  
**Enforcement:** This document contains the complete visual specs, narrative blueprints, and the **Claims Ledger**. No claims may go on screen unless they have a `SURVIVES` row in the Ledger (Appendix).

---

## 1. THE PRODUCT STATEMENT

GDC Edge AI gives production operators more time before a failure becomes irreversible. More time creates more options. More options allow cheaper, lower-risk solutions. This translates directly to capital preserved, production protected, and operational safety maximized.

The demo proves this across three distinct dimensions — **Discern** (context-fusion discrimination), **Classify** (fault suppression), and **Optimize** (Bayesian efficiency) — using a single continuous technology stack running inside the operator's sovereign boundary on GDC, without public-cloud dependency for the decision.

**Horizontal positioning:** The H1/H2/H3 scenario structure is asset-agnostic. The O&G upstream instance is the worked example; the platform claim generalizes to any industrial vertical where unstructured operational knowledge is the missing tier (Power & Energy, manufacturing, mining, process industries). See §3 for the 4-industry mapping.

---

## 2. THE THREE-ACT NARRATIVE STRUCTURE

| Act | Tab | Scenario | Asset | Core Claim | GDC Advantage |
|-----|-----|----------|-------|------------|---------------|
| **H1** | **Discern** | Gas Lock or Fluid Drawdown | ESP-ALPHA-1–6 (random) | *Discerning Operator: Context & Scale* | L3 document fusion resolves the ambiguous unloading signal; enables safe proactive intervention vs. reactive manual action under operator workload |
| **H2** | **Classify** | Paraffin/Wax Deposition Mimicking Bearing Wear | ESP-ALPHA-3 | *Provenance Diagnosis: Prevent Wrong Pull* | Retrieves vendor service log + PVT report + prior pull record → identifies overdue hot-oil PM as root cause → averts $70k–$100k unnecessary pump pull |
| **H3** | **Optimize** | VFD Optimization | ESP-ALPHA-1 | *Edge-Cloud Collaboration* | Local XGBoost checks limits; Vertex AI Vizier drives search |

**Narrative Arc:** Discern (H1) → Classify (H2) → Optimize (H3)

---

## 3. CORE VALUE PROPOSITION — SOVEREIGN EDGE OF AN INDUSTRY-VALIDATED CAPABILITY

**Version:** Session AU (June 11, 2026) — **LOCKED. Do not re-open.** See `docs/DEMO_STORY_AND_PATH.md §B` for the full stakeholder narrative.

**The PRIME DIRECTIVE for this section:** Concede sensors and L1/L2 completely and honestly. Win on WHERE the capability runs — not just what it does.

#### The Locked Thesis — The Industry Is Building This. GDC Delivers It Inside the Perimeter.

The AI-powered diagnostic advisor — the capability the entire APM industry (GE Vernova, AVEVA, Aspen Mtell, Cognite, C3.ai) is building for cloud deployment in 2025–2026 — GDC delivers inside the operator's sovereign boundary, on open-weight Gemma, at the edge, where the data already lives.

**This is a WHERE claim, not a WHAT claim.** The capability class (real-time ML anomaly detection + LLM-based differential diagnosis over unstructured documents) is industry-validated. GDC's differentiator is WHERE it runs. The demo demonstrates that capability running inside a sovereign perimeter.

**Market validation (Gemini neutral-search confirmed, Session AT — no hostile priming):**
- C3.ai 2026 roadmap: "virtual subject matter expert… full context — all sensor data, structured, unstructured, past work performed on the machine"
- GE Vernova, AVEVA, Aspen Mtell, Cognite: all have 2025–2026 GenAI roadmap items for document-aware diagnosis
- The direction is industry-validated. GDC's differentiator is sovereign-edge deployment, not the AI capability class.

#### The Two-System Architecture — System A (CPU) + System B (Gemma/GPU)

> **Session BL decision — do not conflate these two systems under the word "the LLM."**

| System | What it is | Hardware | Status |
|---|---|---|---|
| **System A — Retrieval** | SentenceTransformer `all-MiniLM-L6-v2` embeddings + AlloyDB pgvector semantic search. Finds the relevant unstructured documents. | **CPU-only** | Always live. Unaffected by GPU off. |
| **System B — Generation** | Gemma 4 via Ollama. Reads retrieved documents → extracts structured findings, modulates evidence strength, writes advisory prose, powers conversational chat. | **GPU (NVIDIA L4)** | Off by default (cost). On for showcase/record sessions only. |

**The L3 competitive moat is System A** — semantic retrieval of unstructured documents fused with live telemetry. This is architecturally impossible for any current SCADA/APM product and runs on CPU regardless of GPU state.

**System B is the GenAI showcase layer.** Its defensible roles (per Session BL architecture review):
1. **Extraction** — reads genuinely-unstructured retrieved documents and emits a structured finding ("free gas: none detected → F1"). Replaces hardcoded finding lists.
2. **Evidence-strength modulation** — classifies assertion strength (emphatic / qualified / absent) and adjusts the LR *within physics-anchored bounds* stored in `field_intel` metadata. Gemma never invents a weight; it moves within a range a domain engineer set and cited.
3. **Advisory summarization** — writes the operator-language synthesis of the retrieved evidence (the "L3 Context Fused" one-liner).
4. **Conversational chat** — RAG-grounded "Ask the Advisor": operator interrogates the verdict in natural language.

**The trap to avoid:** Gemma must never *assign* safety-critical probability weights. LR values live in `field_intel` metadata with physics citations (`lr_base`, `lr_min`, `lr_max`, `lr_source` columns), not in code. Weights are adaptable without recompile. The Bayesian arithmetic is always CPU, always auditable.

**H1 vs H2 asymmetry (Session BL):**
- **H1 (Discern):** Bayesian posterior is the contested artifact — the weight-metadata architecture defends the number. Gemma's role is extraction + evidence-strength modulation + chat. The diagnostic *verdict* stays Bayesian math (never LLM) — that is a feature: an engineer can check the arithmetic.
- **H2 (Classify):** No posterior to defend. The contested artifact is the *causal chain* (paraffin, not bearing wear). Gemma's role is document summarization + causal synthesis. Rigor is physics-cited discriminators (PIP rises = hydraulic restriction; temp flat = rules out thermal/mechanical), not LR weights.

**The honest demo claim (replace "the LLM diagnoses your pump"):**
> *"GDC turns a pile of unstructured field documents into structured findings (Gemma, GPU), fuses them with auditable probability math (CPU), and lets the operator interrogate the result in plain language (Gemma, GPU) — all inside the sovereign perimeter on open weights."*

#### The Competitive Claim (use exact wording — Gemini neutral-search verified, Session AT)

> *"No native, production-ready commercial product combines real-time ML anomaly detection with LLM-based differential diagnosis over unstructured maintenance documents — as of 2025–2026, this is where all major APM platforms are heading. GDC delivers it now, inside the sovereign perimeter, on open weights."*

#### Three Gaps That Drive the Value Proposition

**1. The Diagnostic Gap**
SCADA says *that* something is wrong. APM says the *pattern* is anomalous. Neither says *why* — because "why" lives in unstructured documents: shift notes, workover reports, OEM manuals, lab results, completion records. No sensor-based system reads them in real time. GDC reads the documents.

**2. The Scale Gap**
A senior engineer can diagnose one well. They cannot diagnose 200 wells at 2am. GDC gives every operator senior-level differential diagnosis on every asset at once — automatic, cited, with an audit trail.

**3. The Sovereignty Gap**
Cloud APM requires data egress — precluded for NOCs, IEC 62443 OT-compliance operators, and jurisdictions with data-residency law. GDC delivers this capability inside the sovereign boundary — architecturally designed for on-prem inference from the ground up. The decision and the safety constraint both remain on-premise. *(Do not claim "only complete path" — on-prem alternatives exist including SLB Lift IQ Edge. Win on architectural design, not exclusivity — see Rejected claims below.)*

#### The Honest-Footing Rule (use when challenged with "but a human could figure this out")

> *"Yes — a skilled engineer could reach this conclusion with the right documents and time, on a single well. What GDC does is make it automatic, fleet-scale, instant, cited, and inside your perimeter — turning a diagnosis that's possible in principle into one that happens every time in practice."*

#### The Universal Pattern — One Platform, Four Verticals

| Vertical | Ambiguous Signal | Deciding Context (in documents — not sensors) |
|---|---|---|
| **O&G upstream (demo)** | ESP intake pressure + amps decline (gas lock or drawdown?) | Sand/completion history · offset-frac report · GOR trend · shift note |
| **Power & Energy** | Transformer DGA gas rise / turbine vibration anomaly | LTC maintenance log · loading plan · prior fault record · service record |
| **Manufacturing / Process** | Motor or pump vibration / bearing temp rise | Lubrication log · production schedule · prior rebuild record · OEM bulletin |
| **Mining / Heavy Industry** | Haul-truck driveline signal / crusher vibration | Service history · haul-road condition report · OEM TSB · shift note |

This is not an oilfield trick. It is the structural gap in every industrial AI deployment where unstructured operational knowledge is the missing tier.

#### The Three-Tier Stack — Honest and Concessive (no overclaiming)

| Tier | Architecture | What each tier reads | The honest GDC position |
|---|---|---|---|
| **L1 — Threshold alarms** | SCADA control layer — hard setpoints, rate rules | **Tags** (individual sensor values) | **Fully conceded.** SCADA trips the pump to protect it. GDC wins nothing here. Never imply SCADA lets the pump die. |
| **L2 — Learned detection** | Threshold-based SCADA: hand-authored rules per well. Advanced predictive platforms (GE SmartSignal, AVEVA PRiSM, Aspen Mtell, SLB Lift IQ): adaptive ML, retraining workflows. | **Tag patterns** (multivariate sensor correlations) | **Contested ground — two distinct sub-tiers (calibrate by audience):** **(1) Against threshold-only SCADA** — the realistic baseline for ~85–95% of mid/small Permian independents (true ML PdM penetration ~5–15% per SPE maturity-matrix / GlobalData analysis; practitioner SME confirmed): XGBoost pre-threshold multivariate scoring is a **genuine, honest detection edge** — give it full credit. **(2) Against best-of-breed APM** (SmartSignal/PRiSM/Mtell/Lift IQ — ~5–15% with real ML): detection converges — **L3 document fusion remains the categorical moat.** ⚠ Never claim GDC out-detects best-of-breed APM on model quality. |
| **L3 — Context fusion** | No SCADA product, control-layer or APM, reads unstructured text into real-time fault diagnosis | **Documents** (shift notes, acoustic sonic logs, GOR reports, work orders) | **Categorical Moat.** GDC fuses unstructured field documents via pgvector RAG and chains them into the live diagnosis. The operator has the same documents — GDC's advantage is reading and correlating the entire corpus in seconds during a live process upset. Architecturally impossible for any current SCADA/APM product. |

#### "Tags vs. Tag-Patterns vs. Documents" (centerpiece for How It Works)

- **Threshold SCADA:** monitors tags against fixed setpoints → alarms when crossed.
- **Advanced predictive ML (APM):** monitors tag *patterns* across sensors → scores risk against calibrated models.
- **GDC:** monitors tags *and* patterns *and* **reads the documents** — the only tier that supplies the context the action depends on.

#### Retraining & Drift — Settled Position (Session AF)

- ❌ "SCADA/APM can't retrain" → **dead** (SmartSignal/PRiSM/Mtell do adaptive retraining — false claim).
- ✅ **Sovereign MLOps lifecycle**: train on the operator's own fleet-failure history via Vertex AI → deploy to GDC edge → run on-prem. Data never leaves the operator's boundary. This is a *platform* claim (where and whose data), not a feature comparison.
- ❌ Active **drift detection** → **not claimed** (not implemented; silent).

#### Rejected claims — do not ship (Session AC / AF, permanently blocked)

- ❌ "SCADA can't retrain its models" — False (SmartSignal/PRiSM/Mtell retrain).
- ❌ "SCADA can't do multivariate detection" — False (advanced APM does this).
- ❌ Any market-share percentage — 🔴 NEEDS-EXPERT, fabrication risk.
- ❌ **"No sensor now or future can distinguish gas lock from drawdown"** — **False** (discharge gauge resolves state; PIP is a submergence proxy). Retired Session AF. Win on CONTEXT, not an overstated sensor impossibility.
- ❌ "The decision stays at the pad" — decision-maker is in the RTOC. Retired.
- ❌ "No cloud dependency for the decision" → replace with: "runs inside the operator's sovereign boundary; local inference is outage-immune."
- ❌ **"GDC is the only complete path for sovereign operators"** — False (SLB Lift IQ Edge, on-prem historian vendors, private cloud options all exist). Replace with: *"GDC is architecturally designed for on-prem AI from the ground up — not adapted from cloud."* (gdc-second-opinion Test A FAILS, Session BF)
- ❌ **"Lift IQ is cloud-only / sends your data to SLB's cloud"** — False as a categorical claim. SLB has on-prem/hybrid Lift IQ Edge deployments. Reframe: *"Lift IQ was architected cloud-first and adapted for edge; GDC is sovereign-first by design."* (gdc-second-opinion Test B Axis 1 FAILS, Session BF)
- ❌ **"Lift IQ covers SLB-contracted ESPs only"** — False. SLB Agora/Lift IQ can ingest non-SLB ESP data. Reframe: *"Lift IQ's core model depth concentrates in the SLB ecosystem; GDC is a native multi-OEM, multi-lift platform with no equipment bias."* (gdc-second-opinion Test B Axis 3 FAILS, Session BF)

**Conceding sensors makes the L3 context-moat more credible, not less.**

---

## 3.5 SURVEILLANCE TAB — ❌ REMOVED (Session AC decision)

### Why the Surveillance tab was cut

The Surveillance tab argued *scale and workload* ("156 ESPs, 14 alarms, 8,412 documents") to pre-empt the "why can't the operator just read the PDF?" question. It was cut in Session AC for the following reasons — **do not restore without addressing all of them:**

1. **Fabricated precision (integrity violation):** "8,412 documents" and "14 alarms" and "156 ESPs" were hardcoded display values not backed by real data. The PRIME DIRECTIVE NO-SILENT-LIE gate blocks them.
2. **Implicit straw man:** 14 SCADA alarms listed as simultaneously active implies operator negligence — "someone isn't doing their job." That violates the NO-STRAW-MAN rule.
3. **Self-contradicting H1:** Listing Well A-3 *inside* the active SCADA alarm feed directly undercuts the H1 claim that GDC detects it *before* SCADA alarms.
4. **Wrong argument for the wrong audience:** The "operator can't read the PDF because they're swamped" frame is workload-based, not capability-based. It's straw-man-adjacent (implies SCADA/operators are negligent rather than architecturally limited).

### What replaced it

The real answer to "why can't the operator just read the PDF?" is **cognitive + architectural, not workload:**

> *The operator has access to the same documents. GDC's advantage is not exclusive access — it is reading and correlating the entire corpus in seconds, against the live telemetry signature, in the middle of a process upset. No human can do this completely or fast enough, regardless of how busy they are.*

This argument lives in two places in the revised demo:

- **How It Works** (Pane 4 — Context Fusion, and the "tags vs. tag-patterns vs. documents" comparison): explains the architectural argument before the scenarios.
- **H1 Discern — GDC Advisor document-reveal beat (Zone 2 Right):** the L3 synthesis payload is shown *live* at the moment the documents appear and the fault is resolved. The synthesis framing at that beat makes the argument *demonstrated*, not *asserted*.

### Default opening tab (replaces Surveillance)

**`How It Works`** is now the default landing tab. The narrative flow becomes:

1. **Open on How It Works** → conceptual framing: tags vs. tag-patterns vs. documents; the physics-impossibility premise; what L3 fusion is.
2. **Navigate to Discern (H1)** → live proof: documents are retrieved, fault is resolved in real time. The concept is demonstrated, not just explained.
3. **Classify (H2) → Optimize (H3)** → full progression.

---

## 4. H1 SPECIFICATION — THE DISCERN TAB (ESP UNLOADING COMPARATIVE DETECTION SCENARIO)

> **✅ RULING LOCKED — Session AO (June 10, 2026):** H1 narrative reframe deployed and verified at `7e7af08`. The detection-race framing is **retired**. The new H1 spine:
> 1. **Even with advanced SCADA, certain fault pairs produce ambiguous symptoms — the safe default is a production-deferring shut-in** (shown honestly in SCADA view as "standard protective policy").
> 2. **GDC's L3 document fusion hands the operator an auditable cited verdict in seconds** — turning the policy default into a confident, production-preserving action.
> 3. **This is a class of problems, not a one-off** (Panel 6: O&G / Power & Energy / Manufacturing — Mining row removed).
>
> **Removed from UI:** lead-time banner, "Smart SCADA" label, "PUMP SEIZED" strawman. **Replaced:** "GDC: context fused" marker, "standard protective policy" card copy, "UNPLANNED OUTCOME" for override path. **Tab order:** Discern (default) / Classify / Optimize / ⓘ Reference. The detection speed story is demoted to background context (XGBoost = the router that aims L3 fusion pre-threshold); L3 document fusion is the headline.

### 4.1 The Core Problem: Ambiguous Unloading Telemetry on an Intake-Only String

**Well context (H1 scope — state explicitly in Briefing Panel 1):** A mature Permian ESP well, moderate-sand formation, AR-trim (abrasion-resistant) pump, standard **intake-only** PDG sensor string (no downhole discharge-pressure gauge — the configuration of ~90% of Permian ESPs). The operator's RTOC has PIP, Amps, Temp, and Vibration from this well.

When an ESP's **Pump Intake Pressure (PIP)** and **Motor Current (Amps)** both decline together on an intake-only string, the early-window signature is genuinely ambiguous between two root causes with opposite correct actions:

1. **Gas Lock (GVF rising):** The casing fluid level is HIGH and stable. A pocket of free gas has entered the pump stages. The pump unloads hydraulically. **Correct action: VFD trim (52 → 44 Hz).** This slows the impeller, allowing the gas pocket to vent up the fully-submerged casing annulus. Well stays online at near-zero cost.

2. **Reservoir Fluid Drawdown:** The casing fluid level has DEPLETED — the dynamic fluid level is critically low, approaching minimum submergence. The pump unloads mechanically. **Correct action: Emergency shutdown.** Executing a VFD trim during drawdown in a **moderate-sand well** drops fluid velocity toward or below the critical sand-transport threshold, causing solids to settle and compact around the still-rotating impeller assembly, seizing the pump. Representative workover cost: ~$150k.

**Why the sensor is ambiguous in the decision window (not "physically identical forever"):**
The clean physical discriminators are either absent or slow on this well:
- A downhole **discharge-pressure gauge** would resolve state (developed head collapses in gas lock, holds in drawdown) — but this well does not have one.
- An **acoustic fluid-level shot (Echometer)** is the independent ground-truth measurement — but it requires dispatching a crew (hours), far exceeding the ~25-min thermal window.
- **PIP itself is a submergence proxy** — but with gas breaking out, the annulus gradient is uncertain, degrading the inference.

In the early decision window, on the data the RTOC has, the signal is genuinely ambiguous.

**Why sand makes the stakes asymmetric:** In a moderate-sand well, VFD trim during drawdown is not merely "suboptimal" — it is catastrophically destructive. A clean well can be stabilized with a trim-down; this well cannot. Sand is the stakes-setter. The Briefing must establish the well's character before the live scenario plays.

**The deciding CONTEXT lives in documents, not sensors:** Whether trim is safe — and what's at stake — depends on the well's **sand/completion history** (workover records), the **GOR trend** (separator/lab report), any **offset-well frac activity** (frac report), and the most recent **shift note**. None of these are sensor signals. They are field events recorded only in unstructured documents.

**GDC's Resolution:** GDC's pgvector RAG pipeline retrieves:
- The **06:15 Operator Shift Note** (elevated GVF, rising GOR, casing pressure building → Gas Lock in a well with stable sand history → VFD trim is safe)
- The **06:00 Sonic-Survey Summary** (fluid level near intake, flat casing pressure, no free-gas indicators → Drawdown in progress → VFD trim contraindicated; shut-in and recover)

The context the documents supply — in seconds — is what the RTOC operator cannot assemble in time from the sensor screen alone.

---

### 4.2 Interaction Model: Scenario Replay (replaces "Inject & Wait")

**Design rationale:** The previous "inject and wait" model — trigger a live degrade thread, then poll every few seconds hoping sensors update — introduced race conditions, timing bugs, and a fundamental honesty problem: the XGBoost model was never actually running over the telemetry in front of the audience. The Scenario Replay model fixes all of this in one architectural move.

**How it works:**

On entering the Discern tab:
1. A call to `GET /api/h1/scenario-replay?fault=<randomly chosen gas_lock or fluid_drawdown>` returns a **complete pre-computed trajectory** — the full physics history of a well degrading from nominal to the unloading state.
2. The trajectory arrays are precomputed **server-side from `FAULT_PROFILES`** using the same ramp formula as the legacy degrade thread (`((i+1)/N)^k`). **Every run is randomized** — the backend samples a new ramp exponent `k ∈ [1.2, 2.5]`, a new starting PIP baseline `∈ [1180–1250 PSI]`, and new fault endpoint targets from the fault profile ranges. No two demo runs are identical. This proves to technical audiences that a live, stochastic model is running — not a prerecorded replay.
3. The **real XGBoost health model** is run in a sliding window over those trajectory arrays to find the exact index where the health score crosses the detection threshold — this becomes `h1GdcDetectIdx`, and it is a real model output.
4. The **SCADA underload alarm rules** (evaluated at every step, fire at the earliest crossing):
   - **Rule A (Rate):** dPIP/dt < −35 PSI/min sustained over rolling 2.5-min window (ISA-18.2 §5.3)
   - **Rule B (Pressure floor):** rolling-avg PIP < 1020 PSI (API RP 11S §7.2 underload setpoint) — fires at ~T=10 min under corrected physics
   - **Rule C (Undercurrent trip):** Motor Amps < 50 A (API RP 11S §7.2 motor underload protection) — fires at ~T=18 min under corrected physics
   This gives SCADA a fully competent, non-straw-manned alarm that fires at ~T=10 min, with GDC detecting at ~T=6 min via pre-threshold multivariate correlation.
5. The **fault type** (`gas_lock` or `fluid_drawdown`) is chosen randomly (50/50) and returned — but is hidden from the UI until the GDC Advisor reveals it via L3 document fusion.

**Real-World Failure Timelines (API RP 11S §4.2, OEM guidelines):**
- **Gas Lock → Thermal Burnout:** An ESP motor running gas-locked, with zero cooling fluid flow, enters thermal runaway. IEEE 117 / API RP 11S limits Class H insulation at 356°F / 180°C. The motor reaches this winding temperature limit in **15–30 minutes** of gas-locked operation. Our 30-minute simulation window precisely matches this real-world failure timeline.
- **Drawdown → Sand Bridging:** Running a dry ESP drops transport velocity below the critical sand-lift threshold (4.2 ft/s at 52 Hz for typical WTX conditions). Sand and solids settle and bridge the tubing string within **minutes** if VFD trim is incorrectly applied. Spontaneous mechanical failure from dry-running alone occurs in **15–45 minutes** (SPE-174536).

The frontend stores the full trajectory arrays and renders them via a **▶ Play / scrub control**. No live degrade thread, no RabbitMQ, no polling — the chart is a deterministic function of one dataset.

---

### 4.3 Screen Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DISCERN — ESP FLUID UNLOADING   Well: A-[N] · [↺ New Scenario]            │
├──────────────────────────────────────────────────────────────────────────── │
│  [◀◀ Reset] [▶ Play] [▶▶ Fast]  ●━━━━━━━━━━━━━━━━━━━━━○━━━━━━━━━━━━━○━━━  │
│                    time scrubber    GDC detect ▲         SCADA alarm ▲      │
├──────────────────────────────────┬─────────────────────────────────────────┤
│  📡 SHARED SENSOR HISTORY (L)    │  ⚖ DECISION CONSOLE (R)                 │
│                                  │   ┌─────────────────┬─────────────────┐  │
│  ── Single Plotly chart ──       │   │ 🟡 SCADA VIEW    │ 🟢 GDC ADVISOR  │  │
│  PIP (blue) + Amps (green)       │   └─────────────────┴─────────────────┘  │
│  on dual Y-axes.                 │                                           │
│  Vertical markers:               │   Pre-cursor: both tabs show baseline    │
│  • Dashed amber: GDC detect      │   Post-GDC-cursor: GDC Advisor activates │
│  • Dashed red:   SCADA alarm     │   Post-SCADA-cursor: SCADA alarm fires   │
│  • Moving cursor: time position  │                                           │
└──────────────────────────────────┴─────────────────────────────────────────┘
```

**Scrubber states:**
- **Before `h1GdcDetectIdx`**: Both SCADA and GDC tabs show nominal state ("Sensors within limits").
- **At `h1GdcDetectIdx`** (GDC amber dashed line): GDC Advisor activates — health score displayed, scanning state begins, L3 RAG retrieve fires. SCADA tab: *"No alarm. Both sensors still within hard limits."*
- **At `h1ScadaAlarmIdx`** (SCADA red dashed line): SCADA alarm fires. Both tabs show alert. GDC has already completed L3 fusion and shows verdict + action cards. The gap between the two markers is the lead-time — shown, not asserted.
- **After `h1ScadaAlarmIdx`**: Both systems see the event. GDC has the informed action path. SCADA has the dilemma.

---

### 4.4 Backend Endpoint: `GET /api/h1/scenario-replay`

**Request:** `GET /api/h1/scenario-replay?fault=gas_lock` (or `fluid_drawdown`)

**Server-side logic (app.py):**
1. Draw trajectory arrays (`psi[]`, `amps[]`, `temp[]`, `vib[]`, `t_min[]`) using `FAULT_PROFILES` ramp formula — N=120 steps, same `k` distribution as degrade thread.
2. Load `esp_health.ubj` (the real trained XGBoost health model). For each sliding window of width W=20 in the trajectory, construct the 8 features the model expects (slopes `dpsi_dt`, `dtemp_dt`, etc.) and call `model.predict()`. Record `health_score[]`.
3. `h1GdcDetectIdx` = first index where `health_score < 0.65` (the detection threshold).
4. `h1ScadaAlarmIdx` = earliest index satisfying any of: rate alarm (Rule A dPIP/dt), PIP floor (Rule B: rolling-avg PIP < 1020 PSI), or undercurrent (Rule C: Amps < 50 A). See §4.2 for rule definitions.
5. Return JSON: `{fault_type, psi, amps, temp, vib, t_min, health_score, gdc_detect_idx, scada_alarm_idx, scada_rule_fired, lead_time_minutes, model_used}`.

**No `fault_type` in the response until the GDC L3 card activates** — the field `fault_type` is omitted from the initial response payload; it arrives only when `GET /api/h1/rag-context?asset=...` is called (see §4.5).

---

### 4.5 Component A: Shared Sensor History Chart (Left column, resizable)

**Single Plotly dual-axis chart** (`#h1-replay-chart`). Renders the full trajectory from the replay response. X-axis: time (minutes). Left Y-axis: PIP (PSI, blue). Right Y-axis: Motor Amps (A, green). Both sensors visible simultaneously — proves they are declining *together* (the correlated signature SCADA sees as ambiguous).

**Three vertical marker lines** drawn as Plotly shapes:
- Amber dashed: at `t_min[h1GdcDetectIdx]` — labelled `GDC Detects (T−Nm)`
- Red dashed: at `t_min[h1ScadaAlarmIdx]` — labelled `SCADA Alarm (T+0)`
- Grey solid (moving): the scrubber cursor position

**Lead-time callout banner** above chart (appears once cursor passes SCADA alarm):
> `⚡ GDC detected {N} minutes before SCADA alarm — on identical sensor data`

This is computed from `t_min[h1ScadaAlarmIdx] - t_min[h1GdcDetectIdx]`. If the model only wins by 2–4 minutes on a given run, that is displayed honestly. The lead-time varies per run because `FAULT_PROFILES` ramp parameters are sampled with variance — this is correct and defensible.

**Below the chart:** four small read-only sensor tiles (PIP / Amps / Temp / Vib) showing the value at the current cursor position.

---

### 4.6 Component B: Decision Console (Right column) — ISA-101 / HP-HMI Design

**ISA-101 principle:** Saturated color is reserved for active anomalies and alarms only. Nominal state is quiet. Maximum information is placed in the operator's field of view with minimum visual noise. The Level-2 detail panel is structured as a clear operational hierarchy: HEADLINE → EVIDENCE → INTERVENTION.

**The fault type is hidden until the GDC cursor is crossed.** Before `h1GdcDetectIdx`, both sub-tabs show quiet nominal baseline. After, they diverge.

#### 🟡 SCADA View (Sub-Tab 1) — HP-HMI Bare-Metal Telemetry

- **Before SCADA alarm idx**: Quiet slate background. Single line: `WELL A-3 — SURVEILLANCE ACTIVE · ALL SENSORS WITHIN LIMITS`. No color.
- **After SCADA alarm idx**: Narrow, discrete amber/red alarm banner + 2×2 industrial tag grid (large monospace readouts for PIP, Amps, Temp, Vib with their SCADA setpoints and status indicators). No diagnosis — SCADA only knows that an underload alarm fired.
  - `⚠ UNDERLOAD ALARM — Unloading condition detected. Gas Lock and Reservoir Drawdown produce identical sensor signatures. Cause unknown without document context.`
- **Action Cards:** Two equally sized, clean slate-bordered cards (not color-saturated — ISA-101 Level-2 style):
  - **Card A: VFD Speed-Down** — labeled `Reactive Operator Intervention` with annotation `(Safe if Gas Lock · Catastrophic if Drawdown — cause unknown)`
  - **Card B: Emergency Shut-In** — labeled `Conservative Protective Response` with annotation `(Safe for both causes · ~$3k–$8k deferred restart)`
  - Both cards are clickable and functional. Card B (Conservative Shut-In) is now a real, functional selectable option that resolves safely. This removes the false appearance that operators are "forced" to take the risky path.
  - Clicking Card A during Drawdown triggers the seizure path (requires no modal on SCADA side — SCADA doesn't know better).

#### 🟢 GDC Advisor View (Sub-Tab 2) — Three-Zone HP-HMI Layout

The GDC Advisor view is structured as three vertical zones using ISA-101 Level-2 detail hierarchy:

**Zone 1 — Standalone Assessment Headline (top, full width):**
- Clean monochrome box (dark-border, no heavy saturation) with a single colour-coded status tag.
- Contains the GDC diagnostic statement + health score + confidence level, in clean monospace:
  ```
  ✔  GAS LOCK CONFIRMED                                      hs = 0.42 · 92% confidence
  L3 Context Fused: Shift Note (06:15 Tour 2) + GOR trend
  Casing annulus fully submerged. Gas pocket in pump stages.
  VFD trim (52→44 Hz) is safe. Motor cooling intact.
  ```
- This zone exists ONLY on the GDC tab. It reveals after `h1GdcDetectIdx` is passed.
- Before detection, this zone shows a scanning placeholder: `Retrieving field context via pgvector RAG…`

**Zone 2 — Two-Column Middle Layout:**
- **Left ~60%:** Two equally-sized, ISA-101-compliant Action Cards:
  - **Card A (Gas Lock → VFD Trim):** `VFD Speed-Down · 52→44 Hz · ~$2,500`  
    Label: `[✔ GDC RECOMMENDED: Proactive Intervention]` (thin green outline, not saturated)
  - **Card B (Emergency Shut-In):** `Emergency Shut-In · ~$3k–$8k deferred restart`  
    Label: `[○ Conservative Fallback — Available]` (thin neutral outline — also clickable and functional)
  - **For Drawdown scenarios, labels flip:** Card B becomes `[✔ GDC RECOMMENDED: Safe Shut-In]` and Card A becomes `[❌ GDC CONTRAINDICATED — sand bridging risk]` (triggers override modal if clicked).
- **Right ~40%:** Vertical Supporting Document Stack (ISA-101 Evidence Panel):
  - A clean vertical list of retrieved context documents, each rendered as a compact card:
    - `📄 Operator Shift Note · 06:15 Tour 2` (click → field form modal)
    - `📄 GOR Lab Test · Well A-3 Separator` (click → separator test results modal)
    - `📄 OEM Troubleshooting Guide · Gas Void Handling` (click → OEM PDF excerpt modal)
  - The documents are revealed one-by-one as the RAG pipeline retrieves them, timing their appearance for dramatic effect.
  - Label above the stack: `RETRIEVED CONTEXT — AlloyDB pgvector (< 2s)`
  - This is the categorical L3 moat — SCADA has no architecture to assemble this evidence list.

**Zone 3 — Downhole Digital Twin strip (far right 12%, GDC only, full height):**
- SVG wellbore schematic, visible only on GDC Advisor tab.
- Completely hidden (collapsed to zero width) on SCADA View tab — visually reinforcing that SCADA has no downhole visibility.
- Scrubber-reactive: fluid column drains with PIP, gas bubbles or sand particles bind to `h1CursorIdx` past `gdc_detect_idx`.

**Fleet Scale Card:** **REMOVED.** The Surveillance tab was removed in Session AC. No fleet-scale card in the Discern tab.

---

### 4.7 The Honest Comparison: Hard Threshold vs. Correlated Pre-Threshold Scoring

The claim the Scenario Replay design makes is narrow and defensible:

> *"SCADA as-deployed monitors individual tags against hard thresholds set conservatively to suppress nuisance trips. XGBoost scores the joint multivariate drift — PIP and Amps declining together in a correlated pattern — and crosses a calibrated probability threshold when that signature emerges, which is before either tag hits its hard limit. Both systems see the same data. The model triggers first."*

**What we concede:** A skilled SCADA engineer *can* configure rate-of-change alarms or multivariate threshold rules on a specific well. We do not claim SCADA is blind.

**What we prove:** The real trained model, running over the real trajectory, crosses its detection threshold before the real SCADA hard threshold is crossed. The gap is shown on the chart, computed live, and varies per run. This is categorically not a straw man.

**The categorical L3 moat** (which no SCADA product can architecturally replicate): After early detection, GDC fuses unstructured field documents to resolve the gas_lock vs. fluid_drawdown ambiguity and prescribe the correct action. This remains H1's primary claim regardless of the lead-time magnitude.


---

## 4.5 BRIEFING PATTERN SPEC — Canonical for All Three Tabs

**This section is the authoritative look-and-feel reference.** Every briefing panel (H1/H2/H3) must conform before code is written. Do not drift from it.

### Chrome — identical on all three tabs
```
┌─ PROGRESS STRIP (var(--surf2), border-bottom) ──────────────────────┐
│ {Tab} — {Asset}   Background Briefing    ● ● ○ …   M / N   Skip →   │
├─ PANEL BODY (flex:1, padding 16–20px 28px, gap 8–14px) ─────────────┤
│   KICKER  (0.58rem · 700 · UPPERCASE · 0.12em · color #3b82f6)      │
│   Panel N of M — {Beat Name}                                        │
│   TITLE   (1.5–1.7rem · 800 · var(--text2))   ← the claim, ≤6 words │
│   subtitle (0.65rem · var(--muted))            ← the tension, 1 line │
│   …panel content…                                                   │
├─ NAV FOOTER (var(--surf2), border-top, justify-content:space-between)│
│   ← Back   │  {hint, 0.52rem italic muted}  │  Next →  /  ▶ Run …  │
└─────────────────────────────────────────────────────────────────────┘
```

### Color discipline (ISA-101 HP-HMI)
- **Blue** = STATE / sensors / system data (border `rgba(59,130,246,0.20)`, fill `rgba(59,130,246,0.05)`)
- **Amber** = CONTEXT / documents / caution (border `rgba(251,191,36,0.22)`, fill `rgba(251,191,36,0.05)`)
- **Green** = safe / healthy / recommended (border `rgba(74,222,128,0.22)`, fill `rgba(16,185,129,0.06)`)
- **Red/orange** = risk / contraindicated (border `rgba(239,68,68,0.22)`, fill `rgba(239,68,68,0.05)`)
- **Slate** = structure / secondary (border `rgba(100,116,139,0.22)`)

**Toned-down palette rule (locked Session AQ-continued):** All briefing chrome (borders, fills, badges, section headers) uses the lower-opacity values above. Saturated `#4ade80 / #f87171 / #fbbf24` reserved for status-indicator-only (ISA-101: saturated color = status, not decoration). Large text (titles, quotes) stays high-contrast `var(--text2) / #e2e8f0`.

### Card anatomy
```html
<!-- Standard panel info-box card -->
<div style="background:rgba(15,23,42,0.65);border:1px solid rgba(59,130,246,0.20);border-radius:8px;padding:16px 20px">

<!-- Blue left-rule callout -->
<div style="padding:10px 14px;border-left:3px solid rgba(59,130,246,0.35);background:rgba(59,130,246,0.05);border-radius:0 5px 5px 0;font-size:0.62rem;color:var(--text2);line-height:1.7">

<!-- Bottom closing quote -->
<div style="padding:10px 16px;background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.07);border-radius:7px;text-align:center">
  <div style="font-size:0.72rem;font-weight:800;color:#e2e8f0">…main quote…</div>
  <div style="font-size:0.58rem;color:var(--muted);margin-top:4px;font-style:italic">…secondary…</div>
</div>

<!-- Two-column action card (reuse for decision panels) -->
<div class="h1-p5-cell" style="animation-delay:Xs;border:1px solid rgba(C,0.22);border-radius:8px;padding:14px 16px;...">
```

### Animation — reuse these classes, do not add new ones
- `.h1-p4-state-row` — staggered fade-in (STATE tiles, left column rows)
- `.h1-p4-ctx-card` — staggered fade-in (CONTEXT cards, right column)
- `.h1-p5-cell` — scale/opacity in (action cards, decision grids)
- `.h1-p6-row` — opacity in (industry/table rows)
- `.h1-bar-scrub` — width transition (scrubber-driven bars)
- **No new keyframe loops.** No CSS transforms that cause repaints. Opacity-only for all build animations.

### HTML entity discipline (Vue template safety)
`&#x2714;` ✔ · `&#x2718;` ✘ · `&#x2192;` → · `&#x2191;` ↑ · `&#x2193;` ↓ · `&#x2014;` — · `&middot;` · · `&#x26A0;` ⚠ · `&#x2013;` –
Never raw `<digit` in template text. Never raw `{{ }}` in static strings.

### Copy voice rules
| Element | Rule |
|---|---|
| Kicker | Role label only: "Panel N of M — {Beat Name}" |
| Title | Plain-English claim, ≤6 words, present tense |
| Subtitle | One sentence: the tension that this panel resolves |
| Callout body | First person of the RTOC operator's reality |
| Quote | The one line they'll repeat leaving the room |
| SCADA framing | SCADA *trips to protect* — never "lets the pump die." |
| Cost language | State both sides: "X avoids Y" not just "saves Y" |
| Never | "Copilot" · "revolutionary" · vague "AI-powered" |

### Unified 3-beat arc across all three tabs
| Beat | H1 Discern (6 panels) | H2 Classify (3) | H3 Optimize (3) |
|---|---|---|---|
| **Setup** | This Well / The Event | The Equipment | The Opportunity |
| **Hook** | The Hook | The Hook | The Tradeoff |
| **Decision** | The Moat / The Decision | The Decision | The Optimization |

**Closing spine sentence** (same on every final panel): the scenario CTA button. Label honest to the action: `▶ Run the Scenario` (H1/H2) · `▶ Run the Optimization` (H3).

---

## 5. H2 SPECIFICATION — THE CLASSIFY TAB (ESP PARAFFIN/WAX DEPOSITION MIMICKING BEARING WEAR)

**Version:** Session BG (June 11, 2026) — **Paraffin/wax deposition scenario. Passes all 5 survival gates (including Gate 5 — Remedy Feasibility, added Session BE). Hostile-engineer pass: gdc-second-opinion Session BG — three FAILS verdicts overturned (hostile engineer inverted PIP hydraulics; PIP rise confirmed correct by Gemini search + API RP 11S); 4 SURVIVES-IF-REWORDED fixes applied. Replaces workover-fluid-incompatibility scenario (Session BE physics invalidation: "flush + reseal in place" is impossible for a downhole ESP protector).**

> **Design history:** Slug-flow (Session AR, 4 FAILs), frac-hit (Session AS, Gate 1 FAIL), workover-fluid-incompatibility (Session AT–AY, deployed to screen) → Session BE: user exposed fatal physics error ("how do you reseal a pump without pulling it?"). Flush+reseal in-place is physically impossible for a downhole ESP protector — correction always requires pulling the completion. Session BE added Gate 5 (Remedy Feasibility) to `.clinerules`. Paraffin/wax deposition is the approved replacement: Session BG gdc-second-opinion hostile-engineer pass complete — all FAILS overturned, 4 rewording fixes applied.

### Scenario Survival Tests — All 5 Pass

| Gate | Test | Result | Evidence |
|---|---|---|---|
| **1. Discrete past event** | Cause is a specific thing that happened at a specific time, not slow drift | ✅ PASS | 90-day hot-oil treatment due on Day 90; delayed by third-party vendor (truck availability logistics dispute). Specific calendar date, specific reason. Documented in vendor service portal — NOT in SCADA. |
| **2. Categorically off-sensor** | Cause cannot be measured by any sensor on the monitored asset | ✅ PASS | Wax deposition thickness inside production tubing: physically unmeasurable by any sensor on a running ESP string. PIP/amps/temp/vib measure pump and motor behavior — not tubing wall state. |
| **3. APM mis-routes** | Best-of-breed APM routes to the wrong, expensive action | ✅ PASS | Rising amps + rising vibration + declining efficiency on a 4-sensor string is **highly similar to** early bearing wear — APM's most common ESP failure class. APM often classifies this pattern as bearing wear (a common failure mode). Without document context, bearing wear is the most probable diagnosis. APM routes to pump-pull investigation (~$70k–$100k). |
| **4. Common and material** | Failure class occurs often enough for fleet-scale automation to have defensible ROI | ✅ PASS | Paraffin deposition endemic to Permian carbonate producers (WAT ~110–122°F per PVT analysis — Gemini-confirmed range). Missed/deferred hot-oil treatments confirmed as common operational reality by SME Bill Barna (Permian production engineer): *"Many operators have poor programs. Often, there are so many false positives, nobody believes the system. All of the problems you listed happen."* |
| **5. Remedy feasibility** | GDC-prescribed corrective action physically executable without workover or downhole access | ✅ PASS | Hot-oil truck roll + annulus flush: surface-only operation. Truck circulates heated oil down the casing-tubing annulus to melt/dissolve paraffin deposits. ~$3k–$6k (🔴 NEEDS-EXPERT — soft estimate; SME-confirmed directionally correct). No workover rig. No wireline. No downhole access. Well returns to nominal within hours. **Pull completely averted.** |

### The Core Story

- **Asset:** Permian ESP producer on a waxy carbonate formation. Standard 4-sensor string: PIP, motor amps, winding temperature, single-axis vibration. No downhole discharge-pressure gauge (~90% of Permian ESP wells).
- **Telemetry signature over ~3–4 weeks:** Motor amps gradually rising (+12–18% above nominal); vibration gradually rising (0.15 → 0.38 in/s RMS); motor efficiency declining (~8–12% below nominal); PIP stable or slightly rising. *(PIP rises because: restriction above pump steepens system curve → operating point shifts to lower flow rate → less reservoir drawdown → PIP builds. Confirmed by Gemini search, API RP 11S, ResearchGate, production-technology.org. Session BG hostile-engineer attack ["pump pulls harder → PIP decreases"] inverts centrifugal pump hydraulics — overturned.)*
- **Why the signature is highly similar to bearing wear on a 4-sensor string:** Both paraffin restriction and bearing wear produce rising amps + rising vibration + declining efficiency. Against threshold-only SCADA (~85–95% of Permian independents): vibration HI alarm fires with no root-cause hypothesis. Against best-of-breed APM: APM often classifies this pattern as bearing wear and recommends pump-pull investigation — correct symptom identification, wrong root cause, wrong fix.
- **Hidden root cause:** Well A-3's 90-day hot-oil paraffin treatment is 52 days overdue (Day 142). Crude WAT ≈ 118°F (per PVT analysis for this well — Document 2). As produced fluid cools below WAT rising up the tubing, paraffin deposits on tubing walls. Restriction builds backpressure on the pump, driving the telemetry signature. The delay is documented in a vendor service portal — NOT in SCADA. The RTOC is experiencing alarm fatigue from 14 other false-positive vibration events on the pad that week.
- **NO STRAW MAN:** The operator is NOT negligent. A third-party vendor logistics dispute caused the delay. The gap is structural (vendor portal not integrated with SCADA), not behavioral. GDC closes the data silo; it does not expose operator incompetence. Confirmed by SME Bill Barna.
- **GDC context fusion (L3 RAG):** pgvector RAG retrieves three siloed documents:
  1. **Chemical vendor service log** (last hot-oil treatment Day 0, 90-day schedule, Day 142 = 52 days overdue; delay reason: vendor truck availability). 🔄 DYNAMIC — Gemma generates per run with randomized vendor, dates, technician.
  2. **Fluid PVT / lab report** (crude WAT = 118°F, moderate-to-high wax content, 90-day hot-oil interval confirmed per production engineering recommendation for this well). 📌 STATIC SEED.
  3. **Prior pull record** (last workover 18 months ago: bearings inspected — NORMAL, no unusual wear, pump returned to service in good condition). 📌 STATIC SEED.
- **GDC verdict:** "Paraffin wax deposition — NOT bearing wear. Hot-oil treatment overdue by 52 days — consistent with restriction onset at Day ~106. Bearings normal at last inspection 18 months ago — bearing-wear hypothesis eliminated. Dispatch hot-oil truck. Do NOT pull."
- **Cost claims:**
  - Hot-oil truck roll + annulus flush: ~$3k–$6k (🔴 NEEDS-EXPERT — soft estimate; SME-confirmed directionally correct; display with caveat. Alternatively: chemical solvent squeeze ~$4k–$8k.)
  - Pump-pull investigation averted: ~$70k–$100k (🟡 OUR-CODE — consistent with $140k AFE for full ESP workover, Andrews County WTX, July 2023, Gemini search; our range is the investigation subset)
- **Why the operator misses it:** At 2am with a vibration alarm on Well A-3 among 200 wells, compounded by alarm-fatigue from 14 other false-positive vibration events on the pad that week, no operator checks a vendor service portal entry for an overdue PM. GDC generates the non-obvious provenance hypothesis automatically, across every asset, in < 2 seconds.

### Two-Tier SCADA/APM Framing (per §3 calibration — Session BF)

| Tier | What it does | H2 result |
|---|---|---|
| **Threshold SCADA** (~85–95% of Permian independents) | Fires vibration HI alarm when single tag crosses setpoint. No root-cause hypothesis. | Fires alarm. Action cards: (A) pull investigation / (B) continue monitoring. Neither names paraffin. GDC XGBoost detection edge is genuine here (pre-threshold multivariate scoring). |
| **Best-of-breed APM** (SmartSignal/PRiSM/Mtell/Lift IQ — ~5–15%) | Multivariate ML classifies symptom pattern → most-probable failure class. | Classifies as "mechanical degradation / likely bearing wear." CORRECT symptom. WRONG root cause. WRONG fix. L3 document fusion is the categorical moat APM cannot reach. |
| **GDC L3 context fusion** | Fuses unstructured field documents into real-time root-cause diagnosis | Vendor log (overdue PM 52d) + PVT (WAT 118°F, high wax) + pull record (bearings normal 18mo ago) → "Paraffin deposition. Dispatch hot-oiler. Do NOT pull." **CATEGORICAL MOAT.** |

### Synthetic Documents Required (G1–G6 Gate — sign off before any pixel)

Three documents for L3 RAG retrieval. One is dynamically generated by Gemma per run. Two are static seeds with Python date-templating at startup. All must pass all 6 gates before seeding or display.

| Document | Generation | Content (measurements/observations only — no diagnosis) | G-gate notes |
|---|---|---|---|
| **Chemical vendor service log** | 🔄 DYNAMIC — Gemma generates per run | Last hot-oil treatment date (Day 0 offset), 90-day schedule, current day overdue count, delay reason (vendor logistics). No diagnosis. Parameters randomized per run (vendor name, technician, dates). | G1: fictional vendor (e.g. "Permian ChemTreat Services — HeatFlow 400"). G2: observations only. G3: "52 days overdue" is concerning-in-hindsight, not alarming-in-isolation (PM delays are common, not emergency triggers). G4: decisive only when crossed with PVT (high WAT crude + overdue treatment = paraffin likely). |
| **Fluid PVT / lab report** | 📌 STATIC SEED | Crude characterization: WAT = 118°F (measured by DSC or cooling curve), moderate-to-high wax content (wt%), 90-day hot-oil treatment interval recommended for this well at current flowing conditions. No diagnosis. | G1: fictional lab (e.g. "Permian Basin Fluid Analysis LLC — PVT Report #PAL-2024-047"). G2: measurements only. G5: WAT 118°F physically consistent (Gemini-confirmed 110–122°F range for Permian carbonate crude). G6: routine reservoir fluid study. |
| **Prior pull record** | 📌 STATIC SEED | Last workover summary (18 months prior): pull date, pump condition — normal, bearing condition — NORMAL (no unusual wear noted), motor condition — normal. No anomalies. | G4: decisive only in combination with vendor log (cross-referencing "normal bearings 18mo ago" + "overdue paraffin PM" eliminates bearing-wear hypothesis). G6: ESP service company post-pull inspection report. |

### Screen Architecture (per §4.5 Briefing Pattern Spec)

```
CLASSIFY tab
├── H2 Briefing (3 panels — h2BriefingMode: true) [same §4.5 chrome as H1/H3]
│   ├── Panel 1: The Well (setup beat)
│   │   (Well spec card: 4-sensor string, no discharge gauge, waxy carbonate)
│   │   (Production chemistry card: WAT 118°F, 90-day hot-oil interval)
│   │   (Callout: "Paraffin is endemic to Permian carbonate producers — the fix is cheap if caught early")
│   ├── Panel 2: The Signature (hook beat)
│   │   (Timeline strip: Day 0 ✔ → Day 90 ⚠ DUE → Day 106 ↑ onset → Day 142 🔴 TODAY)
│   │   (4 sensor tiles: Amps +14% · Vib 0.38 in/s · Eff -10% · PIP stable)
│   │   (Two-tier SCADA/APM callout: threshold fires alarm / APM routes to bearing wear)
│   └── Panel 3: The Decision (decision beat)
│       (GDC verdict card [green outline]: "Paraffin wax deposition — NOT bearing wear")
│       (Action cards: Hot-oil truck ~$3k–$6k [GDC RECOMMENDED] vs Pump pull ~$70k–$100k [AVERTED])
│       (Doc stack: vendor log [DYNAMIC] + PVT report + pull record)
│       CTA: ▶ Run the Scenario → sets h2BriefingMode=false
└── H2 Scenario Replay (h2BriefingMode: false)
    ├── Dual-sensor Plotly chart: motor efficiency (amber, declining) + vibration (purple, rising)
    │   X-axis: days post last hot-oil treatment
    │   Markers: GDC detect▲ (amber dashed) · SCADA vib HI▲ (red dashed)
    ├── Transport controls: ◀◀ ▶ ▶▶ + scrubber
    ├── SCADA View: quiet slate → vibration HI banner → action cards (pull investigation / monitor)
    └── GDC Advisor View: 3-zone layout
        Zone 1: "PARAFFIN WAX DEPOSITION — NOT BEARING WEAR · health score · confidence"
        Zone 2L: action cards — Hot-oil truck [GDC RECOMMENDED] vs Pull [AVERTED]
        Zone 2R: sequential doc reveals — vendor log [DYNAMIC] → PVT report (+2s) → pull record (+3.5s)
        Zone 3: wellbore schematic (paraffin deposit buildup animation in tubing above pump)
    [← Briefing] button returns to h2BriefingMode=true, h2BriefingPanel=1
```

**Backend endpoint:** `GET /api/h2/scenario-replay?asset=ESP-ALPHA-3`

Returns: `efficiency[], vib[], t_min[], health_score[], gdc_detect_idx, scada_alarm_idx, gdc_verdict, doc_reveals[]`

**Note on GPU dependency:** Document 1 (vendor log) is generated by Gemma per run. Documents 2–3 are static seeds. GPU is NOT required for the briefing panels — Gemma generation is live during scenario replay only (and can fall back to a static template if GPU is off).

---

## 6. H3 SPECIFICATION — THE OPTIMIZE TAB (PAD-LEVEL FIELD OPTIMIZATION)

**Version:** Session BE (June 11, 2026) — Full field-level rewrite (Sprint H3-D). Replaces single-pump VFD story from Session BB.

### The Narrative Arc: Discern → Classify → Optimize

H1 and H2 each resolve a crisis on a single well. H3 asks the natural next question: *now that the system knows which wells are healthy, what is the most valuable way to run them?* The Optimize act takes the same GDC stack — edge models, sovereign boundary, cloud collaboration — and applies it to the **field as a whole**, not one pump at a time. The scale gap that §3 claims becomes literal: the decision is not about one asset; it is about the entire pad.

---

### The Core Story

**The Problem:** Pad Alpha has 6 active ESP producers (A-1 through A-6) running inside a single gas-compression takeaway contract. The binding constraint is the **gas ceiling: 8.0 MMscfd** — a hard midstream contract limit that, if exceeded, triggers curtailment or flaring violations (RRC of Texas). Every barrel of oil produced is accompanied by associated gas. Wells differ in their Gas-Oil Ratio (GOR): A-3 produces 450 scf per barrel; A-5 produces 1,350 scf/bbl. When the gas budget is scarce, **not all barrels cost the same gas.**

**Without GDC:** The safe SCADA default is **uniform throttle** — scale every well back proportionally to stay below the ceiling. Conservative, safe, but it wastes gas budget on high-GOR wells that could be partially throttled while low-GOR wells run at full speed. That inefficiency costs approximately **78 bbl/d** — production the pad is physically capable of delivering, left deferred by the absence of a cross-well optimizer.

**With GDC:** A joint optimizer runs across all 6 wells simultaneously, respecting three real constraints per well:

1. **Gas ceiling** (field-level, binding this run): 8.0 MMscfd. Tagged 🟡 OUR-CODE — representative of real Permian midstream contract constraints; scenario parameter, not a measured field value.
2. **Motor winding temperature** (per-well, 280°F derated operating setpoint): evaluated on-premise by the 4-feature physics polynomial `T = f(vfd_hz, motor_amps, intake_fluid_temp, water_cut_pct)` per API RP 11S3/S5 and IEEE 112. The 280°F threshold is the derated field operating limit — not the Class H insulation limit of 356°F / 180°C (IEC 60085). See RT-NEW-2 in RED_TEAM_LEDGER.
3. **RUL horizon** (per-well, tracked but not binding this run): modeled as `rul_base × exp(−0.11 × max(0, hz−50))`. Decay begins above 50 Hz (SCADA nominal). RUL bases 590–820 days reflect realistic Permian ESP lifecycle.

**The Result (live Vizier API verification, 2026-06-11):**

| Well | GOR (scf/bbl) | SCADA uniform (Hz) | GDC optimal (Hz) | Role |
|------|--------------|-------------------|-----------------|------|
| A-1 | 520 | ~63.0 | 65.5 | Low-GOR — run near max |
| A-2 | 680 | ~63.0 | 65.5 | Low-GOR — run near max |
| A-3 | 450 | ~63.0 | **66.0** | Lowest GOR — full speed |
| A-4 | 890 | ~63.0 | 64.2 | Mid-GOR — modest trim |
| A-5 | 1,350 | ~63.0 | **59.7** | Highest GOR — throttled |
| A-6 | 450 | ~63.0 | **66.0** | Lowest GOR — full speed |

**Uplift: +77.9 bbl/d · +$369,225 over 90 days · gas 7.9999 / 8.0 MMscfd ✓**

A-5 gives way so A-3 and A-6 can run at maximum. Maximum production from the pad. No constraint violated. No pump destroyed.

⚠️ **Integrity note:** Hz values and uplift figures are hardcoded in the H3 briefing panels from the live API call of 2026-06-11. If `_PAD_ALPHA_WELL_PARAMS`, `_GAS_CEILING_MMSCFD`, or `_PUMP_FLOW_COEFF` in app.py change, the briefing table must be updated to match.

---

### The Collaboration: Cloud Searches, Edge Enforces

This is an **honest hybrid** — not an air-gap and not cloud-dependent for the safety decision:

- **Vertex AI Vizier** (cloud) runs as a **Gaussian Process Bandit** — 6-dimensional search (one Hz setpoint per well). It drives the multi-step Bayesian exploration. Only parameter-level data (Hz vectors and their objective scores) goes to cloud. **Raw operational telemetry, production rates, and well identities never leave the sovereign boundary.**

- **The edge** (local Python, physics polynomial) evaluates every candidate Hz vector from Vizier against all three constraints and rejects any violation before the setpoint reaches the control layer. The LP-optimal analytical allocation — the correct closed-form solution for the gas-only linear sub-problem — is also computed locally as both the initialization and the fallback.

- **Edge is the safety system:** If the WAN link drops mid-search during a price spike, storm, or process upset, the LP-optimal local result is the approved output. The constraint holds. The decision does not require a cloud round-trip.

❌ **Retired language:** *"no cloud dependency for the decision"* — too absolute.
✅ **Use:** *"No public-cloud dependency for the decision — the safety constraint and the final approved setpoint both run on-premise."*

---

### Vizier Justification (red-teamed and SURVIVES — Session BD Gemini gdc-second-opinion)

**Attack:** *"A GP Bandit for a problem you can solve with a spreadsheet — that's credentialing theater."*

**Defense — SURVIVES:** The gas-only sub-problem IS LP-solvable (linear objective, linear constraint → bang-bang: allocate to lowest-GOR wells first). We solve it analytically and show it as the LP-optimal baseline — transparent, auditable, no black box. Vizier's role is the **full multi-constraint problem**: gas ceiling + 4-feature nonlinear thermal polynomial + per-well exponential RUL decay, simultaneously, over 6 continuous variables. That is not LP-solvable. That is the search space where GP Bandit adds value over grid enumeration. The demo shows both solvers, distinguishes their roles, and explains why the non-linear full problem is Vizier's domain. An engineer watching this demo sees two honest solvers, not one over-engineered one.

---

### Screen Architecture

```
OPTIMIZE tab
├── H3 Briefing (3 panels — §4.5 Briefing Pattern Spec) — h3BriefingMode: true
│   ├── Panel 1: The Opportunity
│   │   (6-well GOR table · associated gas explanation · "3× more oil per unit of gas budget")
│   ├── Panel 2: The Tradeoff
│   │   (constraint stack: gas ceiling AMBER/BINDING · thermal SLATE/not binding · RUL SLATE)
│   │   (SCADA honest framing: "uniform throttle — conservative, safe, leaves 9,238 bbl/d short")
│   └── Panel 3: The Optimization
│       (GOR-ranked Hz table · uplift card · "Maximum production. No pump destroyed.")
│       (closing: "Cloud searches. Edge enforces.")
│       CTA: ▶ Run the Optimization → sets h3BriefingMode=false, fires runVizierOptimize()
└── H3 Dashboard — h3BriefingMode: false
    ├── Vizier Pareto chart (trials[] — 15 GP-Bandit iterations, exploration progress)
    ├── Per-well setpoint table (SCADA baseline vs GDC optimal Hz + gas consumed per well)
    ├── Field uplift card (+77.9 bbl/d / +$369,225/90d / gas ✓ 7.9999/8.0 MMscfd)
    └── ← Briefing button (returns to h3BriefingMode=true, h3BriefingPanel=1)
```

**Backend endpoint:** `POST /api/vizier/optimize` (or existing GET with asset param — see app.py).

Returns: `trials[]`, `scada_nominal`, `vizier_optimal`, `optimal_hz`, per-well breakdown (gas_consumed, thermal_ok, rul_remaining), `lp_baseline`, `gas_ceiling_mmscfd`, `constraint_binding`.

---

### Claim Ledger Rows — H3 (all SURVIVES, Session BD Gemini red-team)

| ID | Claim | Tag | Source | Status |
|---|---|---|---|---|
| H3-P1 | Gas ceiling 8.0 MMscfd is a real class of binding Permian production constraint | 🟡 OUR-CODE | `_GAS_CEILING_MMSCFD=8.0` in app.py; scenario parameter representative of RRC/midstream contract limits (Gemini-confirmed); labeled as scenario parameter | SURVIVES |
| H3-P2 | GOR heterogeneity across wells makes joint optimization > sum of independent optimizations | 🟢 TEXTBOOK | Standard reservoir engineering; Permian GOR variation well-documented; "classic resource-allocation problem" (Gemini Session AZ) | SURVIVES |
| H3-P3 | Motor winding temp evaluated by 4-feature polynomial T = f(hz, amps, fluid_temp, water_cut) | 🟢 TEXTBOOK | API RP 11S3/S5 §5; IEEE 112; physics polynomial is PRIMARY evaluator since Session BB — esp_thermal.ubj intentionally not loaded | SURVIVES |
| H3-P4 | 280°F is the derated operating setpoint (not the Class H insulation limit of 356°F / 180°C per IEC 60085) | 🟡 OUR-CODE | `_WINDING_TEMP_LIMIT_F=280` in app.py; labeled as derated operating threshold on screen; IEC 60085 Class H cited for context only | SURVIVES (scoped) |
| H3-P5 | Vizier GP Bandit justified for full multi-constraint non-linear search; LP analytical handles gas-only sub-problem | 🟡 OUR-CODE | LP-optimal baseline computed locally and shown; Vizier handles (gas + thermal polynomial + RUL) non-linear joint search; both roles shown transparently | SURVIVES |
| H3-P6 | +77.9 bbl/d / +$369,225/90d at gas ceiling 7.9999/8.0 MMscfd | 🟡 OUR-CODE | Live Vizier API result 2026-06-11; `_PAD_ALPHA_WELL_PARAMS`, `_GAS_CEILING_MMSCFD`, `_PUMP_FLOW_COEFF=24.0` in app.py — grep-verifiable. Update if params change. | SURVIVES (update if params change) |
| H3-P7 | Edge enforces safety constraint even when WAN drops (outage-immune) | 🟡 OUR-CODE | Physics polynomial runs on-premise; LP-optimal fallback computed locally; WAN only carries Hz vectors and scores | SURVIVES |

---

## 7. SHARED UI CONVENTIONS

- **GDC Advisor:** No "Copilot" branding is used. The AI is a streaming, operator-assist Advisor.
- **Tabs (L→R):** `How It Works` · `Discern` (H1 Unloading) · `Classify` (H2 Maintenance Provenance) · `Optimize` (H3 VFD). **Surveillance tab removed (Session AC).**
- **No Operating Envelope scatter charts**: These require too much explanation. Use the dual-axis trend chart and the dynamic wellbore schematic instead.
- **No 14-well pad strip**: This is a visual bloat. The scale story is made through text (e.g. "14 wells under continuous surveillance") rather than a decorative map.
- **Engineering Diagram wellbore:** Drawn in dark-mode CSS HTML to scale. Horizontal slugging animations rendered *only at surface*, gas lock animations *only at depth*.

---

## 8. DOCUMENT REALISM GATE — SYNTHETIC FIELD DOCUMENTS

**Added: Session W (June 9, 2026). Enforcement: blocking — same level as PRIME DIRECTIVE.**

Every synthetic field document (modal, RAG card, seeded `field_intel` row, app.py seed doc) must pass **all 6 gates** before it goes on screen. If it fails any gate, it is reworded or cut.

| Gate | Rule | Failure example (pre-Session W) |
|---|---|---|
| **G1 — No third-party identity** | No real company, product, or trademark. Invent fictional vendors (e.g. *"Permian Acoustic Services"*, *"SONiX-2 well analyzer"*). | "Baker Hughes SONiK™" in sonic log modal |
| **G2 — Measurements, not verdicts** | A raw field doc records **observations/readings only**. It must NOT state the diagnosis or prescribe the action. Diagnosis and action belong to the GDC synthesis layer (`ai_relevance` / verdict). | Sonic log saying "Emergency shutdown is the correct action" |
| **G3 — No premature-action trigger ("no smoking gun")** | At its timestamp, the doc must NOT contain information so alarming that a competent operator would already have acted before our demo window. Values must be *concerning-in-hindsight*, not *alarming-in-isolation*. Test: *"Would a competent operator act on this document ALONE at its timestamp? If yes, soften the measurement or move the decisive value to the live telemetry signal."* | Sonic log showing fluid level within 30 ft of minimum — an operator sees that at 06:00 and acts immediately. Demo window starts 15 min later. |
| **G4 — Decisive only in fusion** | The doc earns its value only when combined with the live telemetry + the other docs. Alone, it is ambiguous or routine. This is what proves the L3 moat. | A single doc that already solves the diagnostic case without the telemetry |
| **G5 — Physically consistent** | Every number obeys the scenario physics (FAULT_PROFILES, submergence limits, GOR ranges, ISA-18.2/API RP 11S setpoints). Units correct. Internally consistent (deltas add up). | Drawdown doc showing rising casing pressure (gas lock sign, not drawdown) |
| **G6 — Provenance plausible** | The doc type, author role, timestamp, and cadence match how that artifact is actually produced in the field (who logs it, when, why, how often). | Echometer acoustic survey "streaming automatically every 30s" — these are ad-hoc surveys, not continuous streams |

**Workflow:** Before writing or editing any synthetic document text, run the G1–G6 gate check in the session. Log each document and its gate results in CLAIM_LEDGER.md before it appears in the UI. Domain owner (user) reviews document copy before pixels are drawn — same model as the Claim Ledger.

**Documents currently requiring Batch B remediation (Session W open items):**
- H1 Sonic Log modal: fails G1 (Baker Hughes), G2 (diagnosis in body), G3 (smoking gun — 150 ft near-critical at 06:00)
- H1 Shift Note: review against G3 (GVF "estimated at 78%" is inferred, not a direct sensor reading — verify wording)
- H1 OEM Guide doc card: review G4 (does it independently solve the case?)
- H2 Workover completion report, OEM compatibility matrix, shift note: sign off against G1–G6 gate before seeding (new H2 scenario — not yet built)

---

## 9. DEPLOYMENT & DATA ARCHITECTURE — SOVEREIGN INDUSTRIAL AI

### The Placement Spectrum

GDC deployment follows one invariant: **compute goes where the data cannot leave.** There are two distinct reasons data cannot move:

| Driver | What constrains the data | Where GDC deploys | Reference project |
|---|---|---|---|
| **Data gravity** | Physical firehose — GB/min too large to backhaul (e.g., DAS fiber at 6,000 msg/s, 160,000:1 reduction needed) | At the wellhead / pad-cluster compute shack | `gdc-das-physics-detection` (CCS) |
| **Sovereignty** | Policy/regulatory boundary — data cannot or will not cross to public cloud | Inside the operator's RTOC / sovereign data center | **This project (gdc-pm)** |

For a standard ESP PdM workload (4 scalar SCADA tags at 5 s cadence ≈ ~0.3–0.5 GB/day for a 38-well fleet — confirmed arithmetic), there is **no data-gravity reason** to place compute at the pad. Our workload is **sovereignty-constrained**, not bandwidth-constrained.

### Canonical Deployment: RTOC-Sovereign

The decision-maker who watches SCADA and authorizes a well shut-in or VFD trim is **not at the pad** (shale pads are typically unmanned; lease operators run drive-by routes). They sit in a centralized **Real-Time Operations Center (RTOC)** — regional or corporate (e.g., Midland or Houston for Permian operations). VFD adjustments are executed remotely from the RTOC, or by dispatched field personnel.

GDC co-locates at the **operator's RTOC or corporate data center**, inside the IT/OT security perimeter, serving multiple assets over the existing production network. This is economically realistic (data-center/colo-grade hardware), operationally accurate (the decision-maker is there), and the natural convergence point for the full document corpus.

**Note on pad-level compute:** Compute shacks at pad-cluster level exist for control-layer (PLC/VFD) and ESD functions — not for AI advisory. The advisory and L3 fusion runs in the RTOC tier.

### The Three Sovereignty Pillars (why GDC, not public Vertex)

| Pillar | Plain statement | Regulatory regime |
|---|---|---|
| **1 — Isolation + self-sufficiency** | OT/production data must not cross the public internet under the operator's OT-security policy (IEC 62443 zones & conduits), AND the AI must keep functioning when the outside link is severed (Starlink/WAN drop during a process upset is a real scenario). The AI runs **inside**, no external dependency for the decision. | **IEC 62443 / Purdue** (O&G, manufacturing); **NERC-CIP CIP-005/007** (Power & Energy BES assets — *not applicable to upstream O&G*); **API 1164** (O&G pipeline) |
| **2 — Sovereignty / residency** | Reservoir and production data is commercially sensitive; many NOCs and regulated jurisdictions require it to remain in-country / off public multi-tenant cloud. | National data-residency law; operator policy (e.g., Saudi Arabia NCA ECC-1:2018) |
| **3 — Governance & IP** | Open-weight **Gemma on GDC** deployed on-prem gives operators **full control over inference data** — proprietary prompts (telemetry + field documents) never transit a third-party model API during inference and are never externally logged. Operators can audit the model weights directly. *(Scope: inference-sovereignty claim. GDC is a Google-supplied platform — Gemma's training-data provenance is Google's responsibility, separate from the operator's inference IP. If challenged on platform dependency, position as "inference sovereignty" not "full IP isolation from all third-party components".)* | Operator IP/security policy |

**Honest counter (NO-STRAW-MAN):** Cloud-first US independents with cloud historians (AVEVA CONNECT, Cognite Data Fusion) and no residency constraint can run this in Vertex — often simpler and cheaper. GDC's market is operators and workloads where public cloud is **precluded**. The demo dramatizes that workload; do not claim "everyone needs GDC."

**Lift IQ honest counter (Session BF — gdc-second-opinion verified):** SLB offers Lift IQ Edge on-prem/hybrid deployments. Do NOT claim "Lift IQ sends your data to SLB's cloud" — that may be false for a given deployment. The honest four-axis reframe (Ledger LIFTIQ rows): (1) **Architectural design** — GDC is sovereign-first by design, not adapted from cloud; (2) **Perceived conflict of interest** — SLB recommends and sells pulls; GDC is vendor-neutral (soften to "perceived/potential"); (3) **Multi-OEM native** — GDC has no SLB-ecosystem bias; (4) **L3 automated fusion** — Lift IQ's *automated* system cannot fuse unstructured vendor emails, overdue-PM logs, and field documents into the live real-time diagnosis at fleet scale in seconds; human SLB experts may incorporate context manually, but not automatically across 200 wells at 2am. **For cost-driven US independents with no residency constraint:** Lift IQ may be the better commercial answer — do not claim GDC is superior for this buyer.

**One-sentence spine:** *"The data can't come to the AI, so the AI goes to the data — GDC puts Google's AI stack inside the operator's sovereign boundary."*

### Backhaul Reality: Starlink / LEO

Starlink (LEO): ~25–60 ms latency, 50–250 Mbps down, **best-effort — no enterprise SLA, public network, OT-trust concern.** Ideal for KB-scale corpus sync *down* and insights *up*. **Never in the decision path.**

GDC's sovereign value rests on **reliability of the decision + sovereignty**, not on latency (Starlink is fast enough) and not on bandwidth (scalar SCADA is trivially small). The argument: the satellite link can drop during a process upset — at precisely the wrong moment. Local corpus + local inference is **outage-immune by design.**

### ⚠️ Integrity Fixes — Retired Claims (Session AF, confirmed by independent expert review)

| Retired claim | Why | Replacement |
|---|---|---|
| "~200 GB/day for 38 wells" | Wrong by ~1,000× for scalar SCADA (4 tags × 5 s ≈ 0.3–0.5 GB/day total fleet). 200 GB/day requires DAS-class waveform data. | Omit or explicitly scope to waveform/DAS only. |
| "VSAT round-trip latency: 15–25 minutes" | Physically wrong. GEO VSAT RTT ≈ 500–650 ms. The "15–25 min" likely conflated poll cadence with latency. | Delete from all UI copy. |
| "The decision stays at the pad" | Decision-maker is in the RTOC; pad is unmanned. | "Decision support runs inside the operator's sovereign boundary, beside SCADA in the RTOC." |
| "No cloud dependency for the decision" | Too absolute; framing that doesn't acknowledge the real reason. | "No public-cloud dependency for the decision — runs sovereign, outage-immune." |
| "NERC-CIP" cited for upstream O&G | NERC-CIP has **zero jurisdiction** over upstream O&G (governs BES only). Citing it to an O&G audience signals regulatory confusion. | Use **IEC 62443 / Purdue** for O&G; NERC-CIP **only** when explicitly addressing the P&E vertical. |
| "GDC is the only complete path for sovereign operators" | False — SLB Lift IQ Edge, private-cloud historians, and other on-prem analytics exist. (gdc-second-opinion Test A FAILS, Session BF) | "GDC is architecturally designed for on-prem AI from the ground up — not adapted from cloud. It brings cloud-native AI services inside the sovereign boundary." |
| "Lift IQ is cloud-only / sends data to SLB's cloud" | False as a categorical claim — SLB has Lift IQ Edge on-prem/hybrid deployments. (gdc-second-opinion Test B Axis 1 FAILS, Session BF) | "Lift IQ was architected cloud-first and adapted for edge. GDC is sovereign-first by design." Verify specific deployment model before asserting. |
| "Lift IQ covers SLB-contracted ESPs only" | False — SLB Agora/Lift IQ can ingest non-SLB ESP data. (gdc-second-opinion Test B Axis 3 FAILS, Session BF) | "Lift IQ's core model depth concentrates in the SLB equipment ecosystem; GDC is native multi-OEM with no equipment bias." |

---

## APPENDIX: THE CLAIM LEDGER (MANDATORY VERIFICATION)

Every pixel on screen must map to a `SURVIVES` row below.

| ID | Claim on Screen | Tag | Source / Citation | Hostile Rebuttal | Rebuttal / SME Shield | Status |
|---|---|---|---|---|---|---|
| **P1** | Gas lock is motor thermal winding failure | 🟢 TEXTBOOK | API RP 11S §4.2; Baker Hughes ESP Manual | "Pump impellers wear out first." | Impeller wear is slow. Thermal insulation breakdown happens in minutes. | **SURVIVES** |
| **P2** | 25 min is the Point of No Return | 🟢 TEXTBOOK | API RP 11S §5; OEM thermal guides | "25 minutes is arbitrary." | Sourced to API standard maximum 15–30 min gas-locked run limits. Softened as "Representative." | **SURVIVES** |
| **P3** | Dynamic fluid level does not drop during Gas Lock | 🟢 TEXTBOOK | API RP 11S §7.2; SPE papers on ESP unloading physics | "The fluid level drops with declining PIP." | PIP drops because the pump stages unload on gas — the casing annulus remains flooded. Fluid level only drops during reservoir drawdown. | **SURVIVES** |
| **P4** | VFD trim during drawdown in a moderate-sand well drops fluid velocity toward/below critical sand-transport velocity → solids compact around rotating impeller assembly → pump seizure (~$150k) | 🟡 FIELD-PRACTICE | API RP 11S §7.2; SPE-170776 (Soepyan et al. 2014 — confirms velocity is model-dependent, not a constant); SPE-174536 **UNVERIFIED** — do not cite until text pulled | "Slowing down is how you stabilize a pumping-off well." | True for CLEAN wells. In a moderate-sand well, velocity below critical transport threshold allows solids to compact around the still-rotating shaft. Must scope: "moderate-sand well." Not catastrophic in a clean-well drawdown. | **SURVIVES (scoped to moderate-sand well)** |
| **S1** | SCADA protects the pump | 🟢 TEXTBOOK | VFD Underload trip manuals | "SCADA lets the pump die." | Conceded honestly. SCADA trips to protect the asset, but shuts well in. | **SURVIVES** |
| **D1** | Telemetry drops are ambiguous | 🟢 TEXTBOOK | API RP 11S §7.2; SPE papers | "A SCADA script can trim frequency too." | SCADA cannot distinguish gas lock from drawdown on raw tags; auto-trimming drawdown risks stuck pump (~$150k). | **SURVIVES** |
| **D2** | Context Fusion is impossible for SCADA | 🟢 TEXTBOOK | AVEVA PI / Ignition specs | "SCADA logs annotations." | SCADA stores notes but cannot read text into realtime control or alarm logic. | **SURVIVES** |
| **C1** | Zero-Downtime Trim Cost: ~$2.5k | 🟡 OUR-CODE | app.py:1069 (labor + minor production trim) | "VFD command is free." | Sourced to 5h production trim ($714) + SCADA loaded labor ($900) + MOC ($900). | **SURVIVES** |
| **C2** | SCADA Trip & Restart Cost: ~$3k–$8k | 🟡 OUR-CODE | app.py:948; API RP 11S §7.2 | "30 min shut-in costs $600." | Accounts for 2–4h cooldown/purge sequence ($1.9k–$3.8k production) + labor + thermal cycling. | **SURVIVES** |
| **C3** | Post-PNR Winding Burnout: ~$150k | 🟡 OUR-CODE | app.py:950; WTX Spot Rig Rates 2024 | "Workover costs vary." | Sourced WTX rig spot rate $14k/day × 3 days + new motor + production cable + deferred oil. | **SURVIVES** |
| **C4** | H2 Slug Flow Surface Truck Roll: ~$1.5k | 🟡 OUR-CODE | app.py:953 | "Technician dispatch is cheap." | Sourced as standard loaded mileage, labor, and surface choke calibration. | **SURVIVES** |
| **C5** | H2 False-Alarm Rig Mobilization: ~$150k | 🟡 OUR-CODE | app.py:956 | "Operators don't pull healthy pumps." | They do if raw vibration alarms look downhole and they have no surface backpressure context. | **SURVIVES** |
| **PREMISE** | On an intake-only gauge (standard Permian ESP — no downhole discharge sensor, ~90% of wells), the PIP/Amps decline is genuinely ambiguous between gas lock and drawdown in the early decision window. Clean discriminators (discharge gauge, acoustic fluid-level shot) are absent or truck-roll-gated (hours). The deciding context — sand history, GOR trend, offset-frac activity — is not in any sensor; it is in documents. | 🟢 TEXTBOOK / 🟡 FIELD-PRACTICE | API RP 11S §7.2; Gemini + Claude independent expert reviews (June 10, 2026); ~90% intake-only prevalence = FIELD-PRACTICE | "Just add a discharge gauge." | Correct for new wells; impractical for legacy fleet (per-well workover). Even with a gauge: discharge pressure confirms STATE — it does not report the well's sand completion history, a recent offset frac, or the GOR trend. Context is not a sensor reading. | **SURVIVES** |
| **P5-A** | In a moderate-sand Permian ESP well, VFD trim during drawdown drops tubing velocity toward or below critical sand-transport velocity → rotating-impeller seizure | 🟡 FIELD-PRACTICE | API RP 11S §7.2; SPE-170776 (Soepyan 2014 — velocity model-dependence); 4.2 ft/s is *representative*, not a constant — do NOT display as a hard number on screen | "Slowing down is how you stabilize a pumping-off well." | True for CLEAN wells. For moderate-sand wells, below critical transport velocity, solids compact around the rotating shaft. Scope must be stated: moderate-sand well. | **SURVIVES (scoped)** |
| **P5-B** | Emergency shut-in is the safe default for a moderate-sand drawdown well (not high-sand/flowback): pump stops → reservoir pressure recovers fluid level → controlled restart clears loose sand bed | 🟡 FIELD-PRACTICE | Independent expert review (June 10, 2026) — both Gemini and Claude confirm; operator ESP restart SOPs (internal) | "Never shut in a sandy well." | That rule governs unconsolidated/high-cut/flowback wells (heavy oil, post-frac with proppant backflow). For mature Permian moderate-sand, shut-in halts active destruction; level recovers; AR-trim pump designed for controlled restart through minor sand bed. Scope caveat must appear on screen. | **SURVIVES (scoped + caveat)** |
| **P5-C** | "Never shut in a sandy well" governs only unconsolidated formations, heavy oil, post-frac flowback with high sand cut — not mature Permian moderate-sand wells | 🟢 FIELD-PRACTICE | SPE 181228 (ESP in heavy oil / high-sand environments); both expert reviews | "Then why do operators always say that?" | Right rule, wrong well type. Mature Permian unconventional sand cut typically < 0.05% by volume — not the heavy-oil/flowback regime. The rule is correct in its domain. | **SURVIVES** |
