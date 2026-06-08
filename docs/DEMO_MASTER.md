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

## 4. H1 SPECIFICATION — ESP UNLOADING (THE DISCERNING OPERATOR & INTERACTIVE CHOICE GAME)

### The Core Story (The Competing Views Dilemma)
When an ESP's PIP and Motor Amps decline, the raw telemetry signature is **physically ambiguous**. It represents a state of **fluid unloading** — the pump is losing its liquid head. This is identical for two completely different root causes:
1. **Gas Lock (GVF rising):** The casing fluid level is high, but gas has entered the pump. Slowing the pump down by trimming VFD frequency safely clears the gas void. The well stays online. **(Correct choice: [APPROVE VFD TRIM])**
2. **Fluid Drawdown (Reservoir depletion):** The reservoir fluid level is actually low. Slowing the pump down drops the fluid velocity below "critical lift", causing sand/debris to settle and bridge the downhole string. **(Correct choice: [EMERGENCY SHUTDOWN]; wrong choice: trim VFD → $150k stuck pump)**

**SCADA's Dilemma:** SCADA sees the declining PSI and Amps but is **structurally blind to context** (no unstructured document access). The penalty for misdiagnosis (executing a VFD trim during fluid drawdown) is a seized $150k downhole pump. The penalty for conservative inaction (letting SCADA trip a true gas lock) is $3k–$8k. Under these asymmetric risks, the operator's **only rational choice is the conservative, inactive path**: wait for the protective underload trip. The well shuts in.

**The GDC Resolution:** GDC's RAG pipeline retrieves the **06:15 Operator Shift Note** (High GVF documented) or **06:00 Lab fluid-level log** (Annulus low). This L3 context **excludes the wrong hypothesis** on the operating envelope itself, giving the operator the high-confidence safety permit to act.

---

### The Interactive Trade-Show Choice Game (How it runs)
To draw traffic at the trade-show booth, H1 runs as an **interactive game with consequences**:
- The screen starts on the **Pad Alpha Map** (14 wells nominal, all gray status dots).
- **The Presenter Prompt:** The presenter clicks either **`⚡ Inject Gas Lock`** OR **`⚡ Inject Fluid Drawdown`** (and tells the visitor: *"You are the operator. Both look identical. Do you trim the speed to stay online, or shut down?"*).
- **The Symptom:** Well A-1 pulses amber. The operating point `YOU ARE HERE` drifts into the ambiguous lower-left quadrant of the **Operating Envelope Chart**.
- **The Climax (GDC RAG reveals the truth):**
  - **In Gas Lock:** GDC retrieves the shift note. The `Fluid Drawdown` zone grays out. GDC flags: *"Gas Lock Confirmed (92%). Safe to trim Hz."* The user clicks `[APPROVE VFD TRIM]`. The well recovers smoothly. **(Savings: ~$150k preserved, well online).**
  - **In Fluid Drawdown:** GDC retrieves the low annulus log. The `Gas Lock` zone grays out. GDC flags: *"⚠ DANGER: FLUID DRAWDOWN (94%). Stuck pump risk. Do NOT speed down."* The user must click `[EMERGENCY SHUTDOWN]`.
- **The Trap (Making the wrong choice):** If the user ignores the GDC warning during Fluid Drawdown and clicks `[APPROVE VFD TRIM]` anyway, the wellbore SVG animates sand falling backward and bridging the pump. The motor housing flashes red, and a critical error screen pops up: *"❌ FAILURE: STUCK PUMP SEIZURE. Motor amperage spiked on startup. String bridged. Pull rig required (~$150k, 5 days downtime)."* This spectacularly proves that GDC's context is what prevents the $150k mistake.

---

### H1 UI Layout: The Three-Act Screen (Detailed Implementation Spec)

#### ACT 1: The Pad Alpha Map (Entry Point & Scale Story)
When the "Detect" tab is opened, the viewer sees a **dark-mode well-field overview map**, not a single well dashboard. This is the scale entry point.

- **Layout:** Dark HP-HMI style map showing 14 wellheads (labeled A-1 through A-14) connected to a central pad manifold (simple geometric layout, no geographic projection required).
- **Nominal State:** All well-pads are calm gray dots/icons with no alarm annotation.
- **On Fault Injection:** `ESP-ALPHA-1` pulses amber. A sliding GDC Advisor Alert banner appears: *"⚠ GDC ADVISOR: Anomaly detected on A-1 · SCADA: All Limits Green · GDC Confidence: 87% Gas Lock"*.
- **Scale Story:** With 14 wells visible and only 1 highlighted, the audience immediately understands the triage value. GDC silently monitors all wells, and surfaces the one that needs attention.
- **Drill-Down Interaction:** Clicking the flashing `ESP-ALPHA-1` icon on the map transitions (collapses) to reveal the **Single-Well Diagnostic Screen** (Acts 2 + 3).

**Implementation note:** The well map is a Vue-driven HTML/CSS component (not an SVG library). Each well is a simple div/circle styled with CSS. This avoids rendering complexity while being fully on-brand for an operator console.

---

#### ACT 2: The Single-Well Diagnostic Screen (3-Column Layout)
After drill-down, the screen shows the full well diagnostic context.

```
╔═══════════════════════════════════════════════════════════════════════════╗
║ STATUS BANNER (full width):                                                ║
║  Pre-inject: [✓ A-1: NOMINAL — GDC monitoring · SCADA green]              ║
║  Post-inject: [⚠ GAS LOCK ACTIVE · T+02:14 · Decision window closing]     ║
╠════════════════════════════╦══════════════════════════════╦════════════════╣
║ COL 1 — Sensors (~25%)      ║ COL 2 — Operating Envelope   ║ COL 3 Advisor  ║
║                             ║   (~40%)                     ║   (~35%)       ║
║ ISA-101 Sensor Bars:        ║ [OPERATING ENVELOPE CHART]   ║ GDC Advisor    ║
║ PIP  ███████░░ 1,180 PSI    ║                              ║ Streaming text ║
║  ↓ Worse · Alarm <800       ║ Y-axis: Intake Pressure      ║ with superscript ║
║  ✓ SCADA Green              ║ X-axis: Motor Current        ║ doc citations  ║
║                             ║                              ║ [¹][²][³]      ║
║ AMPS ████░░░░ 62A           ║ ZONES (shaded background):   ║                ║
║  ↓ Worse · Alarm <50A       ║ [Green] Nominal              ║ INTEL FEED     ║
║  ✓ SCADA Green              ║ [Blue]  Gas Lock             ║                ║
║                             ║ [Red]   Pump-Off Risk        ║ File-styled    ║
║ TEMP ████░░░░ 199°F         ║                              ║ document cards ║
║  ↑ Worse · Alarm >280°F     ║ ●  YOU ARE HERE dot          ║ pulse glow as  ║
║  ✓ SCADA Green              ║ (migrates live as fault      ║ new AI docs    ║
║                             ║  progresses toward risk)     ║ are generated  ║
║ VIB  ██░░░░░ 2.1 mm/s       ║                              ║                ║
║  ↑ Worse · Alarm >8.0       ║ ON RAG RETRIEVAL:            ║                ║
║  ✓ SCADA Green              ║ Pump-Off zone turns to       ║                ║
║                             ║ dark gray + strikethrough:   ║                ║
╠════════════════════════════╬══════════════════════════════╬════════════════╣
║ ACT 3 — THE DECISION SPLIT CARD (full width below 3 columns)               ║
║                                                                             ║
║  ┌─────────────────────────────────────┬────────────────────────────────┐  ║
║  │ 🟡 SCADA VIEW (Conservative Path)   │ 🟢 GDC ADVISOR (Safe Path)      │  ║
║  │                                     │                                │  ║
║  │ "PIP & Amps declining.              │ "Gas Lock Confirmed (92%).     │  ║
║  │  Could be Gas Lock OR Pump-Off.     │  Pump-Off EXCLUDED (L3 fused): │  ║
║  │  Risk of misdiagnosis: ~$150k       │   📄 06:15 Shift Note          │  ║
║  │  stuck pump.                        │   📊 Annulus Level (stable)    │  ║
║  │                                     │                                │  ║
║  │  ACTION: Must wait for trip.        │  ACTION: [APPROVE VFD TRIM ✓] │  ║
║  │  (Well goes offline)"               │  (Well stays online)"          │  ║
║  └─────────────────────────────────────┴────────────────────────────────┘  ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

---

#### ACT 3: The Operating Envelope — The Decision-Supporting Visual

This is the physical explanation of **why the operating point migration matters.** It is the most engineeringly credible visual in the entire demo.

**The Chart (Plotly scatter chart, Plotly.js via CDN):**
- **Y-Axis:** Intake Pressure (PSI), 0–1,600 PSI
- **X-Axis:** Motor Current (Amps), 0–120A
- **Background Zones (colored rectangles rendered as Plotly shape objects):**
  - `Nominal Zone` — green, upper right quadrant
  - `Gas Lock Zone` — amber, mid-left (low amps, moderate pressure)
  - `Pump-Off Risk Zone` — red, lower left (low amps, low pressure)
- **SCADA Alarm Lines:**
  - Horizontal dashed line at 800 PSI (PIP underload limit)
  - Vertical dashed line at 50A (current underload limit)
- **The Live Dot:** A bright orange dot (`YOU ARE HERE`) trails a history of the last 20 operating points. As gas lock develops, the trail migrates from the green Nominal zone into the amber Gas Lock region, approaching the SCADA alarm lines—but crucially **not crossing them** yet.
- **The L3 Exclusion Transition:** When the RAG pipeline retrieves the 06:15 shift note, the `Pump-Off Risk Zone` background **visually fades to dark gray**, and a label appears: *"❌ EXCLUDED: L3 Context — Annulus fluid level confirmed high (Pump-Off ruled out)"*. This happens live, as a dynamic visual update.
- **The SCADA Label:** A text annotation near the alarm lines reads: *"SCADA alarms not triggered (A: >800 PSI · B: >50A)"*. This makes it explicit and visual that SCADA is currently silent.

**What this proves:**
1. The operating point is in danger—visible to anyone watching.
2. SCADA's red lines haven't been crossed—also visible.
3. The ambiguity (Gas Lock vs Pump-Off) is visible as two competing zones.
4. GDC's L3 context physically removes one of those zones from the chart.
5. The safe path becomes literally the only remaining visible path.

---

#### R4 — ISA-101 Directional Sensor Bars
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
