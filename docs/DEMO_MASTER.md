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

### 4.2 The Comparative Detection Scenario: Screen Architecture

The H1 "Discern" tab is structured as an interactive **Pad Alpha well surveillance grid** (A-1 to A-6), a **persistent telemetry column** with live sparkline trend cards, and a **switchable Decision Console** with SCADA View and GDC Advisor sub-tabs. All panels are horizontally and vertically resizable via drag handles.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DISCERN — ESP FLUID UNLOADING   [⚡ Ingest Pad Anomalies] [Std|Accel] [↺]  │
├─────────────────── Pad Alpha ─────────────────────────────────────────────  │
│  [ A-1: ⚠ Alerting ] [ A-2: ✓ ] [ A-3: ⚠ Suppressed ] [ A-4: ✓ ] ...     │
├──────────────────────────────────────┬──────────────────────────────────────┤
│  📡 SHARED TELEMETRY (resizable L)   │  ⚖ DECISION CONSOLE (resizable R)    │
│                                      │   ┌────────────────┬───────────────┐  │
│  PIP:  [ 📈 Sparkline · 1,180 PSI ] │   │ 🟡 SCADA VIEW   │ 🟢 GDC ADVISOR│  │
│  AMPS: [ 📈 Sparkline · 62A      ] │   └────────────────┴───────────────┘  │
│  TEMP: [ 📈 Sparkline · 198°F    ] │                                        │
│  VIB:  [ 📈 Sparkline · 1.3mm/s  ] │   SCADA: Manual intervention warning   │
│  ↕ Drag handle (chart height)        │   GDC: RAG card + wellbore twin       │
│                                      │       + informed action buttons       │
└──────────────────────────────────────┴──────────────────────────────────────┘
                 ↔ Drag splitter (column width)
```

Clicking `⚡ Ingest Pad Anomalies`:
1. **Randomly selects a target well** from A-1 to A-6 to receive the unloading anomaly.
2. **Randomly selects** Gas Lock or Fluid Drawdown (50/50, fault type hidden until GDC reveals it).
3. **Sets departure rate** based on `h1RampSpeed`: Standard (900s) or Accelerated (300s).
4. **Initiates benign transient disturbances** (gas venting) on two adjacent wells, triggering SCADA nuisance alarms which GDC suppresses via retrieved Daily Well Test logs.

Clicking any well in the surveillance grid dynamically loads that well's telemetry and GDC assessment.

---

### 4.3 Component A: Shared Telemetry Column (Left 40%, resizable)

**Always visible.** Proves that SCADA and GDC are reading the **same physical sensors**.

- **Pad Alpha 6-Well Surveillance Grid**: Interactive well cards at the top of the column. Each card displays the well label, a pulsing status dot (✓ nominal / ⚠ alerting / ⚠ suppressed), and real-time health. Clicking a card loads that well's telemetry into the sparkline cards below.
- **Four Stacked Plotly Sparkline Cards** (replaces horizontal progress bars):
  - `#h1-spark-psi`: Pump Intake Pressure (PSI) — declining trend for target well
  - `#h1-spark-amps`: Motor Current (Amps) — declining trend for target well
  - `#h1-spark-temp`: Winding Temperature (°F) — stable for both fault types
  - `#h1-spark-vib`: Motor Vibration (mm/s) — slightly elevated for gas lock
  - Each card renders a live Plotly trend line with a **large bold live digital readout** via annotation in the top-right corner.
  - Each card includes a **subtle horizontal dashed red line** at the SCADA alarm threshold.
- **Drag Handles**:
  - `.h1-splitter`: vertical drag handle (between Left and Right columns) controlling `h1SplitPercent` (25%–75%). Double-click resets to 38%.
  - `.h1-v-splitter`: horizontal drag handle (inside Left column, below sparklines) controlling `h1ChartH` (80px–320px). Double-click resets to 140px.

---

### 4.4 Component B: Sub-Tab 1 — 🟡 Traditional SCADA View (Reactive Manual Intervention)

**The Operator's Dilemma Without Document Context.**

- **SCADA Alarm State**: `⚠ AMBIGUOUS STATE — Fluid Unloading Detected`
- **The Dilemma Text**: *"PIP and Amps declining simultaneously. Physical telemetry signature is identical for Gas Lock (VFD trim is safe) and Reservoir Fluid Drawdown (VFD trim seizes pump). SCADA has no document access. Misdiagnosis risk: representative $150k stuck-pump cost. Conservative path: wait for underload trip (well shuts in; ~$3k–$8k restart estimate)."*
- **Action Buttons (Reactive Manual Intervention)**:
  - **`[Execute VFD Speed-Down: 52 → 44 Hz]` (Standard Response)**:
    - *If Gas Lock (hidden)*: Well stabilizes. GDC log: *"SCADA operator intervened manually — successful on Gas Lock. Without GDC, this had ~50% downside risk."*
    - *If Drawdown (hidden)*: Pump seizes. `h1Seized = true`. Screen: `❌ PUMP SEIZED — Sand bridged downhole. Motor unresponsive on restart.` Plus representative Capex breakdown (~$150k).
  - **`[Execute Conservative Shutdown]` (Safe Inaction)**:
    - Well shuts in. Avoids damage. `h1Resolved = true`. Log: *"SCADA conservative shutdown. Well offline. Representative deferred oil restart: ~$3k–$8k."*

---

### 4.5 Component C: Sub-Tab 2 — 🟢 GDC Edge AI Advisor View (Informed Clarity)

**The GDC Digital Twin — Unlocked by Document Context Fusion.**

- **pgvector RAG Card** (prominent, clickable):
  - *If Gas Lock*: `📄 Retrieved: Operator Shift Handover Note · 06:15 Tour 2 · GVF elevated (78%) at pump intake`
  - *If Drawdown*: `📄 Retrieved: Dynamic Acoustic Sonic Log · 06:00 · Dynamic fluid level 150 ft above intake`
  - **Click-Through Modal**: Clicking the card opens a professional, form-styled pop-up that displays the full field record (Baker Hughes Acoustic Survey form or central-battery shift handover template), making the source document real and verifiable.

- **GDC-Only Downhole Wellbore Digital Twin** (CSS/HTML schematic, never visible on SCADA tab):
  - Renders the casing cross-section, pump, and dynamic fluid column.
  - *Gas Lock State*: Casing fluid level HIGH and stable (blue column full). Animated **gold gas bubbles** rising past the perforations and entering the pump stages. Label: `Pump unloading on gas — fluid column stable. Safe to trim.`
  - *Drawdown State*: Casing fluid level **depletes downward** on screen (blue column falls, exposing pump intake). **Brown sand particles** settle down the tubing string. Label: `Dynamic fluid level at 150 ft (critical minimum: 120 ft). Velocity will drop below 4.2 ft/s on trim. Sand bridge risk. Shutdown.`

- **GDC Verdict** (high-confidence):
  - *Gas Lock*: `✅ GAS LOCK CONFIRMED (92%) — L3 Context Fused: Shift Note + GOR trend. Safe to VFD trim.`
  - *Drawdown*: `⚠ FLUID DRAWDOWN CONFIRMED (94%) — L3 Context Fused: Sonic Log + Casing GOR. VFD trim CONTRAINDICATED.`

- **Action Buttons (Informed)**:
  - **`[✔ Approve Proactive VFD Trim — 52 → 44 Hz]`**:
    - *Gas Lock*: Correct action. Well stabilizes and stays online with $0 downtime.
    - *Drawdown (Override Prompt)*: GDC blocks with a warning modal:
      - *"⚠ CRITICAL GDC WARNING: Dynamic fluid level confirmed critically low (Sonic Log: 150 ft above intake). Reducing pump speed drops fluid velocity below critical lift (4.2 ft/s), causing sand bridging and pump seizure. Override GDC and trim anyway?"*
      - Buttons: `[Override & Trim (Bypass GDC Warning)]` and `[Cancel Action]`.
      - If overridden: Pump seizes (`h1Seized = true`). Consequence shown.
  - **`[⛔ Approve Emergency Shutdown]`** (correct for Drawdown):
    - Well safely shut-in. Sand bridge prevented. `h1Resolved = true`. GDC log: *"Emergency shutdown executed per GDC sonic log evidence. Dynamic fluid level preserved above intake. Pump integrity confirmed."*

---

### 4.6 Injection & Workload Scaling Mechanics

- **Single Trigger**: `⚡ Ingest Pad Anomalies` button. Randomly selects a target well (A-1 to A-6) and fault type (gas_lock or fluid_drawdown, 50/50). The fault type is hidden until GDC reveals it.
- **Departure Rate**: `h1RampSpeed` toggle in banner — `Standard` (900s duration, 15–30 min window) or `Accelerated` (300s duration, 5–10 min window).
- **Nuisance Well Suppression**: Two adjacent wells receive benign transient disturbances triggering SCADA nuisance alarms. GDC suppresses them via Daily Well Test RAG retrieval. SCADA floods the operator with 3 concurrent alerts; GDC filters to 1 critical alert.
- **VFD Trim vs. Shutdown**: Both actions available on BOTH SCADA and GDC sides. Difference is informed vs. uninformed, not gated vs. ungated.
- **Outcome Mapping**:
  - Gas Lock + VFD Trim → Recovery (correct)
  - Gas Lock + Emergency Shutdown → Safe shut-in (conservative but acceptable)
  - Drawdown + VFD Trim → `h1Seized` (catastrophic — shows the $150k consequence)
  - Drawdown + Emergency Shutdown → Safe shut-in (correct)
  - Suppressed nuisance well viewed → GDC shows nominal wellbore twin + Daily Well Test RAG card

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
