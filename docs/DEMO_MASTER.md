# GDC Predictive Maintenance — Master Demo Specification & Blueprint
**Version:** Session I+1 (June 8, 2026) — H1 Discern Tab Clean-Slate Spec
**Status:** Authoritative Single Source of Truth  
**Enforcement:** This document contains the complete visual specs, narrative blueprints, and the **Claims Ledger**. No claims may go on screen unless they have a `SURVIVES` row in the Ledger (Appendix).

---

## 1. THE PRODUCT STATEMENT

GDC Edge AI gives production operators more time before a failure becomes irreversible. More time creates more options. More options allow cheaper, lower-risk solutions. This translates directly to capital preserved, production protected, and operational safety maximized.

The demo proves this across three distinct dimensions — **Discern** (context-fusion discrimination), **Classify** (fault suppression), and **Optimize** (Bayesian efficiency) — using a single continuous technology stack running entirely on-premises (GDC) without cloud dependency.

---

## 2. THE THREE-ACT NARRATIVE STRUCTURE

| Act | Tab | Scenario | Asset | Core Claim | GDC Advantage |
|-----|-----|----------|-------|------------|---------------|
| **H1** | **Discern** | Gas Lock or Fluid Drawdown | ESP-ALPHA-1–6 (random) | *Discerning Operator: Context & Scale* | L3 document fusion resolves the ambiguous unloading signal; enables safe proactive intervention vs. reactive manual action under operator workload |
| **H2** | **Classify** | Slug Flow | ESP-ALPHA-3 | *Fault Discrimination: Prevent False Alarms* | Fuses L3 docs to prevent $150k unnecessary pump pull |
| **H3** | **Optimize** | VFD Optimization | ESP-ALPHA-1 | *Edge-Cloud Collaboration* | Local XGBoost checks limits; Vertex AI Vizier drives search |

**Narrative Arc:** Discern (H1) → Classify (H2) → Optimize (H3)

---

## 3. CORE VALUE PROPOSITION — THE DEFENSIBLE SCADA vs GDC ARGUMENT

### The Three-Tier Capability Stack

| Tier | What it represents | Can Modern SCADA do it? | GDC Edge Advantage |
|---|---|---|---|
| **L1 — Raw Telemetry** | Threshold & simple rate alarms on individual tags. | **Yes.** (Fully conceded). SCADA successfully trips the pump offline to protect it. | None. Do not overclaim. SCADA successfully prevents pump burnout. |
| **L2 — Multivariate Probability** | Correlated drift signatures evaluated pre-threshold. | **In principle yes, but practically no.** Requires high engineering labor per well. | Calibrated probability. Normalizes physics-matched features. Self-calibrates. Scales automatically. |
| **L3 — Context Fusion** | Fusing **unstructured documents** (shift notes, sonic logs, choke logs) into the real-time telemetry assessment. | **❌ No. Architecturally impossible.** SCADA platforms cannot read text into alarm logic. | **Categorical Moat.** Fuses unstructured text via pgvector RAG to rule out competing causes and confirm the safe action path. |

---

## 4. H1 SPECIFICATION — THE DISCERN TAB (ESP UNLOADING COMPARATIVE DETECTION SCENARIO)

### 4.1 The Core Problem: Physically Identical Unloading Telemetry

When an ESP's **Pump Intake Pressure (PIP)** and **Motor Current (Amps)** both decline, the raw telemetry signature is **physically identical** for two completely different root causes:

1. **Gas Lock (GVF rising):** The casing fluid level is HIGH and stable. A pocket of free gas has entered the pump stages. The pump unloads hydraulically. **Correct action: VFD trim (52 → 44 Hz).** This slows the impeller, allowing the gas pocket to vent up the fully-submerged casing annulus. Well stays online at $0 equipment cost.

2. **Reservoir Fluid Drawdown:** The casing fluid level has DEPLETED — the dynamic fluid level is critically low (e.g. 150 ft above intake, approaching minimum submergence). The pump unloads mechanically. **Correct action: Emergency shutdown.** Executing a VFD trim during drawdown drops fluid velocity below critical lift velocity (4.2 ft/s), causing sand and solids to settle and bridge the downhole string, seizing the pump (representative cost: ~$150k pull-rig).

**Note: Dynamic fluid level does NOT drop during Gas Lock.** The casing annulus remains full. Only a dynamic acoustic sonic survey or a fluid level log can measure this — not a SCADA sensor. This is the categorical L3 distinction.

**SCADA's Dilemma:** SCADA sees the same PIP/Amps decline for both events. Without access to unstructured documents (operator shift notes, sonic logs), executing a VFD trim is a blind gamble with catastrophic downside risk.

**GDC's Resolution:** GDC's pgvector RAG pipeline retrieves either:
- The **06:15 Operator Shift Note** (elevated GVF, rising GOR, casing pressure building → Gas Lock confirmed; VFD trim safe)
- The **06:00 Dynamic Acoustic Sonic Log** (dynamic fluid level at 150 ft above intake, stable casing pressure, no free gas → Fluid Drawdown confirmed; VFD trim contraindicated)

---

### 4.2 Interaction Model: Scenario Replay (replaces "Inject & Wait")

**Design rationale:** The previous "inject and wait" model — trigger a live degrade thread, then poll every few seconds hoping sensors update — introduced race conditions, timing bugs, and a fundamental honesty problem: the XGBoost model was never actually running over the telemetry in front of the audience. The Scenario Replay model fixes all of this in one architectural move.

**How it works:**

On entering the Discern tab:
1. A call to `GET /api/h1/scenario-replay?fault=<randomly chosen gas_lock or fluid_drawdown>` returns a **complete pre-computed trajectory** — the full physics history of a well degrading from nominal to the unloading state.
2. The trajectory arrays are precomputed **server-side from `FAULT_PROFILES`** using the same ramp formula as the legacy degrade thread (`((i+1)/N)^k`), so the physics are identical to what the model was trained on.
3. The **real XGBoost health model** is run in a sliding window over those trajectory arrays to find the exact index where the health score crosses the detection threshold — this becomes `h1GdcDetectIdx`, and it is a real model output.
4. The **SCADA hard threshold** (PIP &lt; 800 PSI) is evaluated against the same trajectory to find `h1ScadaAlarmIdx`.
5. The **fault type** (`gas_lock` or `fluid_drawdown`) is chosen randomly (50/50) and returned — but is hidden from the UI until the GDC Advisor reveals it via L3 document fusion.

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
4. `h1ScadaAlarmIdx` = first index where `psi < 800`.
5. Return JSON: `{fault_type, psi, amps, temp, vib, t_min, health_score, gdc_detect_idx, scada_alarm_idx}`.

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

### 4.6 Component B: Decision Console (Right column, two sub-tabs)

**The fault type is hidden until the GDC cursor is crossed.** Before `h1GdcDetectIdx`, both sub-tabs show nominal baseline. After, they diverge.

#### 🟡 SCADA View (Sub-Tab 1)

- **Before SCADA alarm idx**: `Sensors within hard limits. No alarm condition.`
- **After SCADA alarm idx**: `⚠ AMBIGUOUS — Fluid Unloading Detected. PIP &lt; 800 PSI, Amps declining. Cannot distinguish Gas Lock from Reservoir Drawdown on available data.`
- **Action Cards** (using `.h1-action-card` pattern): identical to existing Session N implementation — VFD Speed-Down and Conservative Shutdown, with full descriptive text, "Apply if:" guidance, and velocity risk warning.
- **Outcome mapping** unchanged from Session N (seizure path, safe shutdown, itemized financial breakdown).

#### 🟢 GDC Advisor View (Sub-Tab 2)

- **Before GDC detect idx**: `Baseline monitoring. Health score: nominal.`
- **After GDC detect idx (before SCADA)**: `⚡ Anomaly detected — health score declining. Retrieving field context…` (scanning wellbore schematic, animated).
- **L3 RAG Context Card** (revealed after brief scan animation):
  - *Gas Lock*: `📄 Operator Shift Handover Note · 06:15 · GVF elevated (78%)` — click to open full shift note modal.
  - *Drawdown*: `📄 Dynamic Acoustic Sonic Log · 06:00 · Fluid level 150 ft above intake` — click to open full survey form modal.
- **GDC-Only Wellbore Digital Twin**: Same CSS/HTML schematic as Session N — gas bubbles for Gas Lock, depleting fluid column + settling sand for Drawdown.
- **GDC Verdict + Action Cards**: Same as Session N — GDC RECOMMENDED / GDC CONTRAINDICATED labels, velocity boundary reference (SPE-174536), override modal for Drawdown + VFD trim attempt.

---

### 4.7 The Honest Comparison: Hard Threshold vs. Correlated Pre-Threshold Scoring

The claim the Scenario Replay design makes is narrow and defensible:

> *"SCADA as-deployed monitors individual tags against hard thresholds set conservatively to suppress nuisance trips. XGBoost scores the joint multivariate drift — PIP and Amps declining together in a correlated pattern — and crosses a calibrated probability threshold when that signature emerges, which is before either tag hits its hard limit. Both systems see the same data. The model triggers first."*

**What we concede:** A skilled SCADA engineer *can* configure rate-of-change alarms or multivariate threshold rules on a specific well. We do not claim SCADA is blind.

**What we prove:** The real trained model, running over the real trajectory, crosses its detection threshold before the real SCADA hard threshold is crossed. The gap is shown on the chart, computed live, and varies per run. This is categorically not a straw man.

**The categorical L3 moat** (which no SCADA product can architecturally replicate): After early detection, GDC fuses unstructured field documents to resolve the gas_lock vs. fluid_drawdown ambiguity and prescribe the correct action. This remains H1's primary claim regardless of the lead-time magnitude.


---

## 5. H2 SPECIFICATION — THE CLASSIFY TAB (ESP SLUG FLOW DISCRIMINATION)

### The Core Story
- **The Problem:** Surface flowline slugging (gas/fluid waves) causes pressure and vibration spikes downhole. On raw telemetry, slug flow looks *identical* to acute ESP downhole wear.
- **The SCADA Danger:** SCADA sees vibration spiking and Temp flat. It has no document reader to check surface configurations. Fearing mechanical destruction, the operator initiates an emergency well pull — only to find the pump downhole is perfectly healthy. This is a **$150,000 false-positive Capex waste.**
- **The GDC Solution:** GDC's RAG reads the **06:15 Shift Note**, the **Separator Test Report** (14-min periodicity slugs), and the **Surface Choke Adjustment Log**.
- **The Verdict:** GDC proves the downhole pump is green (healthy) and the vibration is a surface flowline issue.
- **The Action:** Dispatch a surface tech to adjust backpressure (**$1,500 surface truck roll**), saving **$148,500** in unnecessary Capex.

### Visual & Narrative Drama (H2 Classify Tab)
- A dual-line discriminator chart showing **Vibration (rising)** and **Motor Temp (completely flat, blue)**.
- Interactive evidence board: RAG documents lighting up as GDC retrieves them.

---

## 6. H3 SPECIFICATION — VFD BAYESIAN OPTIMIZATION

### The Core Story
- **The Goal:** Don't just protect—maximize. When oil prices spike, operators want to run ESPs faster (e.g. 50 Hz → 58 Hz).
- **The Risk:** Running faster increases heat. If motor windings exceed 280°F (Class H limit), the pump burns out.
- **The Collaboration:** Vertex AI Vizier runs in the cloud to drive the multi-step GP search space. Local GDC edge models enforce the physical safety constraint.

---

## 7. SHARED UI CONVENTIONS

- **GDC Advisor:** No "Copilot" branding is used. The AI is a streaming, operator-assist Advisor.
- **Tabs:** "Detect" (fleet map), "Discern" (H1 Unloading), "Classify" (H2 Slug Flow), "Optimize" (H3 VFD).
- **No Operating Envelope scatter charts**: These require too much explanation. Use the dual-axis trend chart and the dynamic wellbore schematic instead.
- **No 14-well pad strip**: This is a visual bloat. The scale story is made through text (e.g. "14 wells under continuous surveillance") rather than a decorative map.
- **Engineering Diagram wellbore:** Drawn in dark-mode CSS HTML to scale. Horizontal slugging animations rendered *only at surface*, gas lock animations *only at depth*.

---

## APPENDIX: THE CLAIM LEDGER (MANDATORY VERIFICATION)

Every pixel on screen must map to a `SURVIVES` row below.

| ID | Claim on Screen | Tag | Source / Citation | Hostile Rebuttal | Rebuttal / SME Shield | Status |
|---|---|---|---|---|---|---|
| **P1** | Gas lock is motor thermal winding failure | 🟢 TEXTBOOK | API RP 11S §4.2; Baker Hughes ESP Manual | "Pump impellers wear out first." | Impeller wear is slow. Thermal insulation breakdown happens in minutes. | **SURVIVES** |
| **P2** | 25 min is the Point of No Return | 🟢 TEXTBOOK | API RP 11S §5; OEM thermal guides | "25 minutes is arbitrary." | Sourced to API standard maximum 15–30 min gas-locked run limits. Softened as "Representative." | **SURVIVES** |
| **P3** | Dynamic fluid level does not drop during Gas Lock | 🟢 TEXTBOOK | API RP 11S §7.2; SPE papers on ESP unloading physics | "The fluid level drops with declining PIP." | PIP drops because the pump stages unload on gas — the casing annulus remains flooded. Fluid level only drops during reservoir drawdown. | **SURVIVES** |
| **P4** | VFD trim causes sand bridging during drawdown | 🟢 TEXTBOOK | API RP 11S §7.2; SPE-174536 | "Slowing the pump doesn't change the fluid level." | Reducing pump speed drops fluid velocity below critical lift (4.2 ft/s for typical WTX ESP), allowing suspended sand and solids to settle and bridge the tubing string. | **SURVIVES** |
| **S1** | SCADA protects the pump | 🟢 TEXTBOOK | VFD Underload trip manuals | "SCADA lets the pump die." | Conceded honestly. SCADA trips to protect the asset, but shuts well in. | **SURVIVES** |
| **D1** | Telemetry drops are ambiguous | 🟢 TEXTBOOK | API RP 11S §7.2; SPE papers | "A SCADA script can trim frequency too." | SCADA cannot distinguish gas lock from drawdown on raw tags; auto-trimming drawdown risks stuck pump (~$150k). | **SURVIVES** |
| **D2** | Context Fusion is impossible for SCADA | 🟢 TEXTBOOK | AVEVA PI / Ignition specs | "SCADA logs annotations." | SCADA stores notes but cannot read text into realtime control or alarm logic. | **SURVIVES** |
| **C1** | Zero-Downtime Trim Cost: ~$2.5k | 🟡 OUR-CODE | app.py:1069 (labor + minor production trim) | "VFD command is free." | Sourced to 5h production trim ($714) + SCADA loaded labor ($900) + MOC ($900). | **SURVIVES** |
| **C2** | SCADA Trip & Restart Cost: ~$3k–$8k | 🟡 OUR-CODE | app.py:948; API RP 11S §7.2 | "30 min shut-in costs $600." | Accounts for 2–4h cooldown/purge sequence ($1.9k–$3.8k production) + labor + thermal cycling. | **SURVIVES** |
| **C3** | Post-PNR Winding Burnout: ~$150k | 🟡 OUR-CODE | app.py:950; WTX Spot Rig Rates 2024 | "Workover costs vary." | Sourced WTX rig spot rate $14k/day × 3 days + new motor + production cable + deferred oil. | **SURVIVES** |
| **C4** | H2 Slug Flow Surface Truck Roll: ~$1.5k | 🟡 OUR-CODE | app.py:953 | "Technician dispatch is cheap." | Sourced as standard loaded mileage, labor, and surface choke calibration. | **SURVIVES** |
| **C5** | H2 False-Alarm Rig Mobilization: ~$150k | 🟡 OUR-CODE | app.py:956 | "Operators don't pull healthy pumps." | They do if raw vibration alarms look downhole and they have no surface backpressure context. | **SURVIVES** |
