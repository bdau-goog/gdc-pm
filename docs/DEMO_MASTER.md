# GDC Predictive Maintenance — Master Demo Specification & Blueprint
**Version:** Session H (Consolidated - June 8, 2026)  
**Status:** Authoritative Single Source of Truth  
**Enforcement:** This document contains the complete visual specs, narrative blueprints, and the **Claims Ledger**. No claims may go on screen unless they have a `SURVIVES` row in the Ledger (Appendix).

---

## 1. THE PRODUCT STATEMENT

GDC Edge AI gives production operators more time before a failure becomes irreversible. More time creates more options. More options allow cheaper, lower-risk solutions. This translates directly to capital preserved, production protected, and operational safety maximized.

The demo proves this across three distinct dimensions — protection, discrimination, and optimization — using a single continuous technology stack running entirely on-premises (GDC) without cloud dependency.

---

## 2. THE THREE-ACT NARRATIVE STRUCTURE

| Act | Scenario | Asset | Core Claim | GDC Advantage |
|-----|----------|-------|------------|---------------|
| **H1** | Gas Lock | ESP-ALPHA-1 | *Discerning Operator: Context & Scale* | Safe, early VFD trim (well stays online) vs. blind SCADA trip |
| **H2** | Slug Flow | ESP-ALPHA-3 | *Fault Discrimination: Prevent False Alarms* | Fuses L3 docs to prevent $150k unnecessary pump pull |
| **H3** | VFD Optimization | ESP-ALPHA-1 | *Edge-Cloud Collaboration* | Local XGBoost checks limits; Vertex AI Vizier drives search |

**Narrative Arc:** Protect (H1) → Discriminate (H2) → Optimize (H3)

---

## 3. CORE VALUE PROPOSITION — THE DEFENSIBLE SCADA vs GDC ARGUMENT

The core argument is framed as a **three-tier capability stack** (L1, L2, L3) that maps directly against the real-world operational constraints and risks of upstream operations.

### The Three-Tier Capability Stack

| Tier | What it represents | Can Modern SCADA do it? | GDC Edge Advantage |
|---|---|---|---|
| **L1 — Raw Telemetry** | Threshold & simple rate alarms on individual tags (e.g., PIP < 800 PSI, Amps < 50A). | **Yes.** (Fully conceded). SCADA successfully trips the pump offline to protect it. | None. Do not overclaim. SCADA successfully prevents pump burnout. |
| **L2 — Multivariate Probability** | Correlated drift signatures evaluated pre-threshold to score a continuous probability of fault. | **In principle yes, but practically no.** Requires high engineering labor to configure and maintain separate static rules per well. | ** cal_prob.** Normalizes physics-matched features. Self-calibrates. Scales to 1,000s of unique wells automatically. |
| **L3 — Context Fusion** | Fusing **unstructured documents** (shift notes, lab GOR reports, choke valve logs) into the real-time telemetry assessment. | **❌ No. Architecturally impossible.** SCADA platforms (PI, Ignition) cannot read text into alarm logic. | **Categorical Moat.** Fuses unstructured text via pgvector RAG to rule out competing causes (Pump-Off) and confirm the safe action path. |

---

## 4. H1 SPECIFICATION — ESP GAS LOCK (THE DISCERNING OPERATOR)

### The Core Story
- **SCADA's Dilemma:** PIP and Amps are declining. This symptom is highly ambiguous—it could be **Gas Lock** (where slowing the pump is the safe, correct recovery) or **Reservoir Pump-Off** (where slowing the pump risks critical lift failure, sand-bridging, and a stuck downhole pump costing ~$150k to pull). Because raw SCADA is blind to context, the operator *cannot* risk an automatic frequency reduction. SCADA must trip the pump offline to protect it. The well goes black.
- **The GDC Solution:** GDC's RAG pipeline instantly fuses live telemetry with the **06:15 Operator Shift Note** (documenting elevated Pad GVF) and **Annulus fluid level logs** (proving the wellbore fluid is high, ruling out reservoir drawdown/pump-off). 
- **The Decision:** With GDC's **92% GVF-confirmed confidence**, the operator has the safety permit to execute a **Zero-Downtime VFD Trim (HITL)**. The well stays online at a lower frequency (44 Hz) for 4–6 hours until the gas void clears.

### Visual & Narrative Drama (H1 Detect Tab)

#### R1 — Active/Inactive State is Immediately Obvious (The Status Banner)
- **Pre-inject:** Large green header: `[ ✓ ESP-ALPHA-1: NOMINAL — 4 sensors monitoring · no alarms ]`
- **Post-inject:** Pulsing amber header: `[ ⚠ GAS LOCK ACTIVE · T+02:14 · Zero-Downtime Trim Window Closing ]`

#### R2 — The Decision Timeline (YOU ARE HERE)
A horizontal visual strip showing the progression of time and the closing of choices.
- Marks elapsed time with a sliding `YOU ARE HERE` marker.
- Explicitly aligns option cards spatially below the timeline:
  - **Rung 1 (GDC):** `Zero-Downtime VFD Trim` (Preserves production; Soft Cost: ~$2.5k) — *MARGINAL after 18 min, EXPIRED at 25 min.*
  - **Rung 2 (SCADA):** `Reactive Trip & Shut-In` (2–4h zero production; Restart Cost: ~$3k–$8k) — *EXPIRED at 25 min.*
  - **Rung 3 (PNR Cliff):** `Winding Burnout / Motor Melt` (Emergency Pump Pull; Representative Cost: ~$150k) — *Available ONLY after 25 min.*

#### R3 — The Split SCADA vs. GDC Advisor Card
A clear visual split below the timeline exposing the exact contrast in capability:
- **LEFT Box (SCADA):** Displays `STATUS: 🟡 Low Current / Low Pressure`. Flags `AMBIGUITY: 50% Gas Lock / 50% Pump-Off`. Shows `ACTION: Wait for underload trip (shut-in)`.
- **RIGHT Box (GDC Advisor):** Displays `STATUS: 🟢 Gas Lock Confirmed (92% Prob)`. Lists `EVIDENCE: 📄 06:15 Shift Note (High GVF) | 📊 Annulus Level (Stable)`. Highlights `ACTION: [APPROVE VFD TRIM]` (Human-in-the-Loop button).

#### R4 — Directional Sensor Bars
Every sensor bar includes its threshold and direct physical direction context:
- `PIP: 1,340 PSI` — `↓ Lower = worse · SCADA underload alarm: <800 PSI`
- `AMPS: 69.6 A` — `↓ Lower = worse · SCADA underload alarm: <50A`
- `TEMP: 199°F` — `↑ Higher = worse · SCADA thermal alarm: >280°F`
- `VIB: 2.1 mm/s` — `↑ Higher = worse · SCADA vibration alarm: >8.0 mm/s`

---

## 5. H2 SPECIFICATION — ESP SLUG FLOW DISCRIMINATION (THE FALSE ALARM)

### The Core Story
- **The Problem:** Surface flowline slugging (gas/fluid coming in large waves) causes pressure and vibration spikes downhole. On raw telemetry, slug flow looks *identical* to acute ESP downhole wear.
- **The SCADA Danger:** SCADA sees vibration spiking and Temp flat. It has no document reader to check surface configurations. Fearing mechanical destruction, the operator initiates an emergency well pull (mobilizing a workover rig) to pull the pump—only to find the pump downhole is perfectly healthy. This is a **$150,000 false-positive Capex waste.**
- **The GDC Solution:** GDC's RAG reads the **06:15 Shift Note**, the **Separator Test Report** (14-min periodicity slugs), and the **Surface Choke Adjustment Log**.
- **The Verdict:** GDC proves the downhole pump is green (healthy) and the vibration is a surface flowline issue.
- **The Action:** Dispatch a surface tech to adjust backpressure (**$1,500 surface truck roll**), saving **$148,500** in unnecessary Capex.

### Visual & Narrative Drama (H2 Discern Tab)

#### The Two-Line Discriminator Chart
- A single dual-axis chart superimposing **Vibration (rising, orange)** and **Motor Temp (completely flat, blue)**.
- The visual is intuitive in 3 seconds: if temperature is flat, there is no downhole friction—it's a surface issue!

#### The Evidence Board
Interactive documents that light up as the RAG pipeline pulls them:
- `📋 06:15 Shift Note` (surface rough pumping observed)
- `🧪 Separator Slug Test` (periodic gas pockets)
- `⚡ Choke Adjustment Log` (surface restrictions)
- `📖 OEM Troubleshooting Guide` (*"Vibration with flat winding temp = surface slugging, DO NOT pull well."*)

---

## 6. H3 SPECIFICATION — VFD BAYESIAN OPTIMIZATION

### The Core Story
- **The Goal:** Don't just protect—maximize. When oil prices spike, operators want to run ESPs faster (e.g., 50 Hz → 58 Hz) to extract more volume. 
- **The Risk:** Running faster increases heat. If motor windings exceed 280°F (Class H limit), the pump burns out.
- **The Collaboration:** Vertex AI Vizier runs in the cloud to drive the multi-step GP search space. Local GDC edge models enforce the physical safety constraint (predicting winding temperature/RUL locally at millisecond latency). 
- **The Value:** +143 BBL/day × $112/bbl × 90 days = **$1.2M in optimized revenue** safely within thermal limits.

---

## 7. SHARED UI CONVENTIONS

- **GDC Advisor:** No "Copilot" branding is used. The AI is a streaming, operator-assist Advisor.
- **Citations:** Every claim in the Advisor text uses superscript citations `[¹]`, `[²]` that open specific documentation modals.
- **Engineering Diagram wellbore:** Drawn in dark-mode SVG to scale, showing correct downhole cross-section (SLB Oilfield Review style). Horizontal slugging animations rendered *only at surface*, gas lock animations *only at depth*.

---

## APPENDIX: THE CLAIM LEDGER (MANDATORY VERIFICATION)

Every pixel on screen must map to a `SURVIVES` row below. 

| ID | Claim on Screen | Tag | Source / Citation | Hostile Rebuttal | Rebuttal / SME Shield | Status |
|---|---|---|---|---|---|---|
| **P1** | Gas lock is motor thermal winding failure | 🟢 TEXTBOOK | API RP 11S §4.2; Baker Hughes ESP Manual | "Pump impellers wear out first." | Impeller wear is slow. Thermal insulation breakdown happens in minutes. | **SURVIVES** |
| **P2** | 25 min is the Point of No Return | 🟢 TEXTBOOK | API RP 11S §5; OEM thermal guides | "25 minutes is arbitrary." | Sourced to API standard maximum 15–30 min gas-locked run limits. Softened as "Representative." | **SURVIVES** |
| **S1** | SCADA protects the pump | 🟢 TEXTBOOK | VFD Underload trip manuals | "SCADA lets the pump die." | Conceded honestly. SCADA trips to protect the asset, but shuts well in. | **SURVIVES** |
| **D1** | Telemetry drops are ambiguous | 🟢 TEXTBOOK | API RP 11S §7.2; SPE papers | "A SCADA script can trim frequency too." | SCADA cannot distinguish gas lock from pump-off on raw tags; auto-trimming pump-off risks stuck pump (~$150k). | **SURVIVES** |
| **D2** | Context Fusion is impossible for SCADA | 🟢 TEXTBOOK | AVEVA PI / Ignition specs | "SCADA logs annotations." | SCADA stores notes but cannot read text into realtime control or alarm logic. | **SURVIVES** |
| **C1** | Zero-Downtime Trim Cost: ~$2.5k | 🟡 OUR-CODE | app.py:1069 (labor + minor production trim) | "VFD command is free." | Sourced to 5h production trim ($714) + SCADA loaded labor ($900) + MOC ($900). | **SURVIVES** |
| **C2** | SCADA Trip & Restart Cost: ~$3k–$8k | 🟡 OUR-CODE | app.py:948; API RP 11S §7.2 | "30 min shut-in costs $600." | Accounts for 2–4h cooldown/purge sequence ($1.9k–$3.8k production) + labor + thermal cycling. | **SURVIVES** |
| **C3** | Post-PNR Winding Burnout: ~$150k | 🟡 OUR-CODE | app.py:950; WTX Spot Rig Rates 2024 | "Workover costs vary." | Sourced WTX rig spot rate $14k/day × 3 days + new motor + production cable + deferred oil. | **SURVIVES** |
| **C4** | H2 Slug Flow Surface Truck Roll: ~$1.5k | 🟡 OUR-CODE | app.py:953 | "Technician dispatch is cheap." | Sourced as standard loaded mileage, labor, and surface choke calibration. | **SURVIVES** |
| **C5** | H2 False-Alarm Rig Mobilization: ~$150k | 🟡 OUR-CODE | app.py:956 | "Operators don't pull healthy pumps." | They do if raw vibration alarms look downhole and they have no surface backpressure context. | **SURVIVES** |
