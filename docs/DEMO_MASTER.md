# GDC Predictive Maintenance — Master Demo Specification & Blueprint
**Version:** Session AU (June 11, 2026) — Sovereign-Edge of Industry-Validated Capability; H2 Maintenance-Provenance; Locked Strategy
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
| **H2** | **Classify** | Workover Fluid Incompatibility | ESP-ALPHA-3 | *Provenance Diagnosis: Prevent Wrong Fix* | Reads workover completion report + OEM matrix → reclassifies from bearing wear to seal degradation → averts $70k–$100k unnecessary pull |
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

#### The Competitive Claim (use exact wording — Gemini neutral-search verified, Session AT)

> *"No native, production-ready commercial product combines real-time ML anomaly detection with LLM-based differential diagnosis over unstructured maintenance documents — as of 2025–2026, this is where all major APM platforms are heading. GDC delivers it now, inside the sovereign perimeter, on open weights."*

#### Three Gaps That Drive the Value Proposition

**1. The Diagnostic Gap**
SCADA says *that* something is wrong. APM says the *pattern* is anomalous. Neither says *why* — because "why" lives in unstructured documents: shift notes, workover reports, OEM manuals, lab results, completion records. No sensor-based system reads them in real time. GDC reads the documents.

**2. The Scale Gap**
A senior engineer can diagnose one well. They cannot diagnose 200 wells at 2am. GDC gives every operator senior-level differential diagnosis on every asset at once — automatic, cited, with an audit trail.

**3. The Sovereignty Gap**
Cloud APM requires data egress — precluded for NOCs, IEC 62443 OT-compliance operators, and jurisdictions with data-residency law. GDC is the only complete path for those operators. The decision and the safety constraint both remain on-premise.

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
| **L2 — Learned detection** | Threshold-based SCADA: hand-authored rules. Advanced predictive platforms (GE SmartSignal, AVEVA PRiSM, Aspen Mtell): adaptive ML, retraining workflows. | **Tag patterns** (multivariate sensor correlations) | **Contested ground — concede gracefully.** Threshold SCADA hand-authors rules per well; advanced APM platforms do adaptive ML. GDC's modest L2 edge (calibrated probability, learned-not-hand-set, decoupled from control layer) is supporting context, **not the headline**. Against best-of-breed APM, detection converges — L3 is still the moat. |
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

## 5. H2 SPECIFICATION — THE CLASSIFY TAB (ESP MAINTENANCE PROVENANCE — WORKOVER FLUID INCOMPATIBILITY)

**Version:** Session AU (June 11, 2026) — **Maintenance-provenance scenario. Passes all 4 survival tests. Approved. Build per this spec.**

> **Design history:** The original slug-flow H2 scenario was invalidated in Session AR (dual-AI red-team: 4 FAILs — deciding signal is telemetric, false cost dichotomy, temperature discriminator runs backwards, APM understated). A frac-hit replacement was rejected in Session AS (fails Test 1 — experienced operators recognize signatures). The maintenance-provenance scenario was proposed in Session AS, validated via Gemini search (API RP 11S3/11S5 confirms elastomer/bearing ambiguity on 4-sensor string), confirmed in Session AT. **All 4 survival tests pass — see §D of DEMO_STORY_AND_PATH.md.**

### Scenario Survival Tests (all 4 pass)

| Test | Result | Evidence |
|---|---|---|
| **1. Discrete past event** | ✅ PASS | Wrong-fluid fill is a specific event at a specific time (workover date), not slow drift |
| **2. Categorically off-sensor** | ✅ PASS | No online sensor on a running ESP can measure historical hydraulic-fluid fill provenance. Physically impossible. |
| **3. APM mis-routes** | ✅ PASS | Standard 4-sensor string: elastomer seal degradation and bearing wear genuinely ambiguous (API RP 11S3/11S5). APM routes to bearing wear → expensive pump-pull investigation. |
| **4. Common and material** | ✅ PASS | 51% of ESP failures attributed to human factors/operational problems (SPE 185275-MS, 194398-MS, 144562-MS). Fleet-scale automation has defensible ROI. |

### The Core Story

- **Asset:** Permian ESP producer, 8 weeks post-workover. Standard 4-sensor string: PIP, motor amps, winding temp, single-axis vibration accelerometer.
- **Symptom pattern:** Motor efficiency declining + vibration rising slowly over 3–4 weeks. On the standard 4-sensor string, this pattern matches early **bearing wear** — the most common cause, and the cause any APM platform routes to.
- **Hidden cause:** During the workover 8 weeks ago, the crew used a **non-OEM-spec hydraulic fluid incompatible with the Buna-N elastomer shaft seals**. Documented only in the workover completion report (fluid type, vendor, date). No online sensor on the running ESP carries this information — it is physically impossible for one to do so.
- **Why APM gets it wrong:** APM correctly identifies the bearing wear signature (amps elevated, vibration rising) — the bearing wear is **real**. It is caused by well fluid contaminating the bearing assembly through the degraded protector seal. But APM cannot determine **why** the bearings are wearing. Without the workover completion report and OEM fluid compatibility matrix, APM routes to the statistically common hypothesis (normal bearing wear) and recommends a pump pull. GDC fuses the documents, identifies the root cause (incompatible fill fluid → Buna-N seal degradation → well fluid ingress → bearing contamination pathway), and recommends the correct lower-cost fix: flush + reseal to stop the ingress. *(Physics: Gemini search confirmed Session AV — seal degrades → pressure barrier lost → well fluid ingress → bearing contamination. API RP 11S1 teardown classification. Session AV red-team: all 4 survival tests pass with strengthened Test 3.)*
- **GDC resolution:** L2 classifier (`esp_health.ubj`) flags mechanical degradation → routes to L3 fusion. Gemma reads: (1) workover completion report (fluid type — observations only, no diagnosis); (2) OEM fluid compatibility matrix (fluid class → Buna-N: INCOMPATIBLE); (3) timing correlation (3-week onset = expected elastomer swell timeline); (4) last pull record (bearings normal → bearing-wear hypothesis eliminated). GDC verdict: "Elastomer seal degradation from workover fluid incompatibility — NOT bearing wear. Correct action: controlled flush + reseal (~$8k–$15k)."
- **Why the operator misses it:** At 2am with a vibration alarm firing on Well #47 of 200, no operator checks the 8-week-old workover completion report. GDC generates the non-obvious provenance hypothesis automatically.
- **Cost claims (🔴 NEEDS-EXPERT for reseal; 🟡 OUR-CODE-consistent for pull):**
  - Flush + reseal: ~$8k–$15k (stated as estimate — no hard public source found via Gemini search; confirmed "substantially less than full workover"; requires SME verification before hard display)
  - Pump-pull investigation: ~$70k–$100k (consistent with $140k AFE for full ESP workover, Andrews County WTX, July 2023, per Gemini search — our range is the investigation subset before repair/replace decision)
- **SPE citation:** 51% of ESP failures = human factors/operational problems — 2014 SPE AI Conference survey; SPE 185275-MS, 194398-MS, 144562-MS.

### Synthetic Documents Required (G1–G6 Gate — sign off before any pixel)

**Five documents** for L3 RAG retrieval. Two are **dynamically generated by Gemma per scenario run** (so each demo run looks like a different well/workover — varying vendor, date, technician). Three are **static seeds** (factual reference data, same every run). All must pass all 6 gates before seeding or display.

#### Dynamic Generation Architecture

On each call to `GET /api/h2/scenario-replay`:
1. The endpoint draws randomized scenario parameters (workover date offset, fictional fluid vendor, fill volume, technician initials, well production rate baseline).
2. It calls the local Gemma model to generate the **workover completion report** and **shift note** texts, injecting the randomized parameters into a Gemma prompt template.
3. The generated texts are returned in the `doc_reveals[]` payload — they are NOT static seeds. Each run produces unique document text.
4. The static documents (OEM matrix, pull record, well history) are pre-seeded in `field_intel` and retrieved via pgvector RAG in the normal way.

This proves to a technical audience that Gemma is synthesizing content per-run, not retrieving pre-written text.

| Document | Generation | Content (measurements/observations only — no diagnosis) | G-gate notes |
|---|---|---|---|
| **Workover completion report** | 🔄 DYNAMIC — Gemma generates per run | Date, crew, procedure, fictional fluid vendor and product code, fill volume, hydraulic system capacity. No diagnosis. Parameters randomized per run. | G1: fictional vendor (e.g. "TexPlex Industrial Fluids — SynFlow 460E"). G2: observations only. G3: nothing alarming in isolation. G4: decisive only when crossed with OEM matrix. |
| **OEM fluid compatibility matrix** | 📌 STATIC SEED | Factual table: fluid class vs. elastomer type (Buna-N, Viton, HNBR) → Compatible / Conditionally Compatible / INCOMPATIBLE. Sourced from fictional OEM manual. | G1: fictional OEM name (e.g. "PermPump Systems — ESP Series 4000 Service Manual"). G2: pure facts. G5: chemistry accurate (Buna-N + petroleum-based: compatible; Buna-N + synthetic ester/phosphate ester: INCOMPATIBLE — Gemini confirmed). |
| **Prior pull record** | 📌 STATIC SEED | Last workover summary: pull date (18 months prior), motor condition (normal), bearing condition (NORMAL — no unusual wear), protector condition (normal). No anomalies. | G4: decisive only in combination with the workover completion report (eliminates bearing-wear hypothesis when crossed with the "normal bearings" finding). G6: post-pull inspection report from ESP service company. |
| **Shift note (recent tour)** | 🔄 DYNAMIC — Gemma generates per run | Operator observation: rough pumping noted, vibration uptick, flagged for monitoring. No diagnosis, no alarm escalation. Timestamps and operator initials randomized per run. | G3: concerning-in-hindsight, not alarming-in-isolation. G6: operator tour note, 12-hour cadence. |
| **Well history extract** | 📌 STATIC SEED | Workover dates and procedure list for past 24 months: two prior workovers (both normal), plus current workover 8 weeks ago. No anomalies pre-current-workover. | G5: timeline must be internally consistent (current workover date = T-8wk from alarm; prior workovers at realistic intervals). G6: SCADA historian or well file extract. |

### Screen Architecture (same H1 pattern)

```
CLASSIFY tab
├── H2 Briefing (3 panels, per §4.5 Briefing Pattern Spec)
│   ├── Panel 1: The Equipment (ESP + sensor string + workover context callout)
│   ├── Panel 2: The Provenance Hook (timeline: workover → onset → alarm today; 4 sensor tiles; doc stack)
│   └── Panel 3: The Decision (GDC verdict card; action cards; universal pattern close)
│       └── CTA: ▶ Run the Scenario
└── H2 Scenario Replay (same mechanics as H1)
    ├── Shared sensor chart: efficiency trend + vibration rise (the "bearing wear" signature)
    ├── SCADA View: degradation flagged, recommends investigation (no root-cause hypothesis)
    └── GDC Advisor: reads 3 docs → reclassifies → flush+reseal recommendation
```

**Backend endpoint:** `GET /api/h2/scenario-replay?asset=ESP-ALPHA-3`

Returns: efficiency[], vib[], t_min[], health_score[], gdc_detect_idx, scada_alarm_idx, gdc_verdict, doc_reveals[]

### Visual & Narrative Drama (H2 Classify Tab) — TO BUILD

- Dual-sensor Plotly chart: **Motor efficiency (declining, amber)** + **Vibration (rising, purple)** — the "bearing wear" visual signature.
- Transport controls: ◀◀ ▶ ▶▶ + scrubber with GDC detect▲ / Investigation trigger▲ markers.
- ISA-101 SCADA View: quiet pre-alarm slate → degradation banner ("Mechanical degradation detected — investigation recommended") → no root-cause hypothesis — action cards: (A) Pump-pull investigation / (B) Continue monitoring.
- GDC Advisor View: 3-zone layout. Zone 1: "Elastomer seal degradation — NOT bearing wear." Zone 2: action card (flush+reseal ~$8k–$15k, soft estimate) vs. averted action (pump pull ~$70k–$100k). Zone 2 right: sequential doc reveals — Workover completion report [DYNAMIC] (fires with RAG) → OEM matrix (+2s) → Pull record (+3.5s) → Shift note [DYNAMIC] (+5s) → Well history (+6.5s). Five documents total; two generated by Gemma per run.
- Universal pattern close (Panel 3): O&G (wrong fluid) / P&E (wrong coolant) / MRO (wrong lubricant).

---

## 6. H3 SPECIFICATION — VFD BAYESIAN OPTIMIZATION

### The Core Story
- **The Goal:** Don't just protect—maximize. When oil prices spike, operators want to run ESPs faster (e.g. 50 Hz → 58 Hz).
- **The Risk:** Running faster increases heat. If motor windings exceed **280°F (derated operating setpoint; Class H insulation limit = 356°F / 180°C per IEC 60085)**, the pump burns out. *(Note: 280°F is the field operating threshold applied in the demo — not the insulation class limit. See RT-NEW-2 in RED_TEAM_LEDGER.)*
- **The Collaboration (honest hybrid — NOT air-gap):** Vertex AI Vizier runs in the cloud to drive the multi-step GP search space using Gaussian process math — only parameter-level data goes to cloud, never raw operational telemetry. The local XGBoost thermal model (`esp_thermal.ubj`) evaluates every candidate setpoint against the 280°F derated safety constraint and holds it — **even if the WAN link drops mid-search**. The decision and the safety constraint both remain on-premise. This is the novel piece: not the cloud optimization (Bayesian search is common), but the edge safety constraint that holds at precisely the wrong moment (process upset, storm, satellite outage during a price spike). The edge is the safety system.
  - ❌ **Retired language:** "no cloud dependency for the decision" — too absolute. Replace with: "no public-cloud dependency for the decision — the safety constraint and the final approved setpoint both run on-premise."

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
| **3 — Governance & IP** | Open-weight **Gemma on GDC** means proprietary prompts (telemetry + field documents) never transit a third-party model API and are never externally logged or exposed. | Operator IP/security policy |

**Honest counter (NO-STRAW-MAN):** Cloud-first US independents with cloud historians (AVEVA CONNECT, Cognite Data Fusion) and no residency constraint can run this in Vertex — often simpler and cheaper. GDC's market is operators and workloads where public cloud is **precluded**. The demo dramatizes that workload; do not claim "everyone needs GDC."

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
