# H1 Slide Deck — Design Reset Document
**Status: IMMUTABLE — Do not modify without explicit session discussion.**
**Session: BS+14 — June 16, 2026**
**Branch: feature-trio-clean**

---

## Purpose

This document captures the full set of design decisions, narrative directions, physics decisions, and layout approaches agreed upon for the H1 Slide Deck (`gke/fault-trigger-ui/slides/h1.html`) during Session BS+14. It serves as the authoritative reference before any code is written. No implementation shall deviate from this specification without explicit review.

---

## Section 1 — Scenario Setup (Physics Foundation)

### What is happening
*   A Permian Basin ESP well on **Pad Alpha** enters **hydraulic unloading**.
*   The correct SCADA term is **hydraulic unloading** (the ESP pump is starved of sufficient fluid load to maintain design operating point).
*   Two physically distinct causes produce this unloading:
    1.  **Gas Entrainment** (also called: high Gas Void Fraction / GVF): Free gas from the reservoir enters the pump intake. The pump stages move aerated fluid with reduced hydraulic head. No fluid level depletion.
    2.  **Fluid Drawdown**: The dynamic fluid level in the wellbore casing falls below the pump intake depth. The pump is starved of liquid. The reservoir cannot supply fluid at the pumping rate.

### The sensor ambiguity (physically exact — NOT approximation)
*   On an **intake-only PDG string** (no discharge gauge), both Gas Entrainment and Fluid Drawdown produce the **identical sensor trajectory**:
    *   **Pump Inlet Pressure (PIP):** Declining
    *   **Motor Amps:** Declining
    *   **Winding Temperature:** Flat (early phase; thermally lagging)
    *   **Vibration:** Flat
*   The sensor decline is physically identical because the hydraulic load on the impeller drops in both cases — the mechanism differs, but the electrical and pressure signatures are indistinguishable in the early decision window.
*   **Source:** API RP 11S §4.2 (gas lock thermal and pressure behaviour), API RP 11S §7.2 (underload trip parameters), ISA-18.2 §5.3 (rate-of-change alarm logic).

### Wellbore Configuration
| Parameter | Value |
|---|---|
| Pad Name | Pad Alpha · Permian Basin (mature unconventional) |
| Well Label | ESP-ALPHA-N (randomized at demo run) |
| Formation | Mature Permian unconventional · moderate-sand |
| Pump Type | ESP · AR-trim impellers (abrasion-resistant) |
| Sensor String | Intake-only PDG — Pump Inlet Pressure (PIP), Motor Amps, Winding Temp, Vibration |
| No discharge gauge | — *this is the structural constraint that makes sensor disambiguation impossible* |
| VFD Frequency (nominal) | 52 Hz · 3,120 RPM · ~1,245 PSI |
| Well completion | Moderate-sand formation · hydraulically fractured |

---

## Section 2 — Slide Structure (5 Slides)

Slides go from the physical observation → the control room problem → the solution.

| # | Beat Name | Physics / Narrative Focus |
|---|---|---|
| 1 | **THE SCENARIO** | Pad setup + sensor tiles (PIP and Amps declining, Temp/Vib flat). Sets up the unloading event. |
| 2 | **AMBIGUOUS TELEMETRY** | Side-by-side animated wellbore SVGs: Gas Entrainment vs. Fluid Drawdown. Same sensor decline shown at bottom. Makes ambiguity visceral. |
| 3 | **DECISION SUPPORT** | The two control room levers and their physical risks. Why both options carry hidden catastrophic failure modes. |
| 4 | **ADDING CONTEXT** | How GDC resolves the ambiguity using edge-resident RAG (AlloyDB + Gemma) on unstructured well documents. SCADA fires the alarm correctly. GDC reads the file. |
| 5 | **INDUSTRIAL APPLICATION** | Three cross-industry State vs. Context examples proving the pattern is universal. Data Gravity + Sovereignty framing included. |

---

## Section 3 — Approved Slide Headings

Each slide has three text elements: **Kicker** (small, monospace, colored), **Title** (large, `slide-title`), **Sub-title** (`slide-sub`).

### Slide 1: THE SCENARIO
*   **Kicker:** `THE SCENARIO`
*   **Title:** Same Signal. Two Causes. One Right Decision.
*   **Sub-title:** A Permian ESP well enters hydraulic unloading. The same Pump Inlet Pressure and Motor Amps decline — two root causes, opposite correct actions.

### Slide 2: AMBIGUOUS TELEMETRY
*   **Kicker:** `AMBIGUOUS TELEMETRY`
*   **Title:** One Signature, Two Physical Realities
*   **Sub-title:** Gas Entrainment and Fluid Drawdown produce identical Pump Inlet Pressure and Amps decline on an intake-only sensor string. The cause — and the safe action — are not in these numbers.

### Slide 3: DECISION SUPPORT
*   **Kicker:** `DECISION SUPPORT`
*   **Title:** Motor Burnout vs. Sand Bridging
    *(Correction BS+14: "Gas Burnout" is not standard field terminology. "Motor burnout" = winding failure from loss of cooling flow, per API RP 11S §4.2. "Sand bridging" = sand settling and packing in tubing string, standard Permian term.)*
*   **Sub-title:** An unloading well forces a blind trade-off: slow down to clear gas and risk sand settling, or shut-in and risk sand fallback. Neither is safe without knowing the well's history.

### Slide 4: ADDING CONTEXT
*   **Kicker:** `ADDING CONTEXT`
*   **Title:** Fusing Telemetry and Unstructured Well History
*   **Sub-title:** The deciding context isn't hidden — it's scattered across the well file, the frac report, and the shift log. GDC reads the documents. The confident call replaces the cautious default.

### Slide 5: INDUSTRIAL APPLICATION
*   **Kicker:** `INDUSTRIAL APPLICATION`
*   **Title:** Solving the Edge Context Gap — At Scale
*   **Sub-title:** Every industry that runs physical assets faces the same pattern: telemetry reports state; unstructured documents hold context. GDC brings AI/ML to the data — on-premises.

---

## Section 4 — Slide 2 Wellbore Animation Specification (AMBIGUOUS TELEMETRY)

The two SVG wellbore animations share a single scrubber. Both begin **nominal** and progress to **fault onset** as the scrubber advances from 0→1.

### Left Wellbore: Gas Entrainment (High GVF)
*   **Nominal state (t=0):** Wellbore fully flooded with fluid. No bubbles visible at pump intake.
*   **Fault onset (t=1):** Wellbore remains **fully flooded** (fluid level is stable and HIGH — critical distinguishing fact vs. Fluid Drawdown). Free gas bubbles begin to appear and rise from the formation through the fluid column. The pump intake shows an increasing density of bubbles entering the pump stages.
*   **Key visual truth:** The fluid level does NOT drop. The annulus stays flooded. Gas migrates upward through the liquid column and enters at the pump intake. This is the physical mechanism per API RP 11S §4.2.
*   **Bottom callout (blue):** ✔ VFD trim 52→44 Hz — lowers intake draw, gas vents up the annulus. Well stays online. Zero-cost SCADA command.

### Right Wellbore: Fluid Drawdown (Reservoir Depletion)
*   **Nominal state (t=0):** Wellbore fully flooded. Dynamic fluid level well above pump intake.
*   **Fault onset (t=1):** Fluid level **visibly drains downward**. As the scrubber advances, the fluid column drops progressively toward the pump intake. 
*   **Sand behavior:** As fluid velocity increases at the intake (high drawdown rate), sand particles appear **floating/hovering** at the pump intake — suspended by what remains of the upward flow velocity. They are NOT falling; they are being carried up by intake suction. As the scrubber passes ~0.65, sand particles begin accumulating and entering the pump visually.
*   **Physical note:** The sand is NOT falling yet — it is being drawn upward by the suction velocity. This is the correct physics: sand is mobilized when the drawdown velocity pulls it off the formation face and into the tubing.
*   **Bottom callout (orange):** ✘ VFD trim drops tubing velocity below transport limit; sand bridges above pump. ✔ Step down in stages; verify fluid level from last sonic survey before any further reduction.
*   **Bottom sensor bars:** Both wellbores show identical PIP ↓ and Amps ↓ bars below, reinforcing the "same sensor, different physics" message.

---

## Section 5 — Slide 3 Decision Support Layout Specification

Side-by-side decision cards showing two control room levers and their physical outcomes.

### Option 1: VFD Speed-Down (52→44 Hz)
*   **Header:** VFD SPEED-DOWN · 52→44 Hz
*   **For Gas Entrainment:** ✔ Safe — lowers intake rate, gas vents up annulus, stays online. Zero incremental cost.
*   **For Fluid Drawdown (light-sand well):** ✔ Acceptable if kept above minimum lift velocity AND sand cut confirmed low from completion record.
*   **For Fluid Drawdown (moderate/high-sand well — our scenario):** ✘ Dangerous. Reducing speed below ~48 Hz drops fluid velocity below the **critical sand-transport limit** (API RP 11S). Sand settles in tubing, bridges the string, and seizes the pump assembly. A zero-dollar command triggers a six-figure workover pull.

### Option 2: Emergency Shut-In (Stop Pump)
*   **Header:** EMERGENCY SHUT-IN
*   **For Gas Entrainment:** ✘ Overkill. Unnecessary production deferral. Restart risk (electrical, hydraulic). No asset is threatened by Gas Entrainment if monitored correctly.
*   **For Fluid Drawdown (low-sand, standing valve confirmed):** ✔ Acceptable as last resort when completion record confirms low sand cut.
*   **For Fluid Drawdown (sand present):** ✘ Dangerous. Without lift velocity, suspended sand falls back through the tubing onto the pump assembly. Sand bridges in place. Pump seizes. Six-figure pull required.

### Bottom hero callout for Slide 3:
*   *"To make the safe call, the operator needs to know the sand history of the well. SCADA cannot provide it. The answer is in the completion record."*

---

## Section 6 — Slide 4 (ADDING CONTEXT) — Replacing Current Slides 3+4

The current Slides 3 (THE MOAT — STATE vs. CONTEXT) and 4 (THE DECISION — How Operators Decide Today) will be **merged into a single high-impact Slide 4** that uses a two-column layout:

### Left Column: The Manual Context Search
*   An operator under alarm receives the SCADA underload alert.
*   They must manually locate and cross-reference:
    1.  Wellbore Completion File (to check sand screen mesh and historical sand cut)
    2.  Last Acoustic Fluid-Level Survey (to verify dynamic submergence headroom)
    3.  Last Shift Tour Log (to check recent operator notes on GVF or fluid slugging)
    4.  Separator GOR Trend Report (to check if GOR is rising, indicating gas migration)
*   These files may be in SCADA historians, SharePoint folders, field supervisor emails, or paper binders.
*   **The narrative:** Under a live alarm, assembling this correctly in time to act in the early window is the gap. It's not that engineers don't know what to look for — it's that finding and integrating these four sources correctly before the window closes is what gets missed.

### Right Column: GDC Edge RAG
*   GDC's on-site AlloyDB (pgvector) holds all field documents as searchable vector embeddings.
*   When the unloading anomaly is detected, GDC's Gemma model automatically retrieves and fuses the relevant documents.
*   In under 2 seconds: cited differential diagnosis, confidence-weighted recommendation, auditable evidence chain.
*   **HITL:** The operator reviews the cited evidence and approves the action. GDC advised. The operator decided.

---

## Section 7 — Slide 5 (INDUSTRIAL APPLICATION) — Example Overhaul

### Three New Cross-Industry Examples

| Industry | STATE (Sensor) | CONTEXT (Document) | What GDC Resolves |
|---|---|---|---|
| **O&G · ESP Well** | Pump Inlet Pressure ↓ · Motor Amps ↓ | Acoustic fluid-level survey · Sand-cut completion record · Shift note on GOR | Gas Entrainment vs. Fluid Drawdown — opposite correct actions |
| **Power & Utilities · Grid Transformer** | Winding Temperature ↑ · Load Current ↑ | Maintenance log (dielectric oil condition / overdue flush) · Regional loading plan · Feeder schedule | Thermal overload from legitimate grid demand spike vs. incipient insulation breakdown requiring isolation |
| **Maritime / Offshore · Engine Crankshaft** | Cylinder vibration ↑ · RPM flat · Fuel consumption rising | Fuel analysis lab report (asphaltene/sulfur content) · Sea-state log (high-swell strain in last 12 hrs) · OEM maintenance bulletin | Detonation knock from bad fuel batch vs. mechanical bearing wear — one requires fuel switchover, the other a hard shutdown |

### Intro / Data Gravity / Sovereignty framing (added to Slide 5 bottom banner or sub-header):
*   *"Every one of these decisions requires data that cannot economically move to the cloud — and must not. Data gravity, data sovereignty, and sub-second response time mean the AI must come to the data. That is GDC."*

---

## Section 8 — Integrity Issues to Address Globally

These integrity issues exist in the live app and will be corrected as part of this implementation pass:

### 8.1 PIP Abbreviation (Priority: Address in slide kickers and headings; accept in chart labels and technical code comments)
*   **In Slide 1 sensor tiles:** Change `PIP` header label → `PUMP INLET PRESSURE` (spelled out, as it is visible to the audience).
*   **In Slide 2 bottom sensor bars:** Labels remain abbreviated `PRESSURE` / `AMPS` since they are small descriptors in a visual context.
*   **In app.js / app.py technical strings:** Retain `PIP` in internal Gemma prompt strings and technical code comments (these are not displayed to audience).
*   **In app.js sparkline labels:** Retain `PIP` only in the chart legend (audience-visible short labels are acceptable as chart annotations).
*   **Critical:** Any slide heading, kicker, or large-text callout must not contain `PIP` — use **"Pump Inlet Pressure"**.

### 8.2 Authored Dollar Figures in Slide Decks
*   Slide decks (`h1.html`) must NOT contain authored hard dollar figures in narrative copy.
*   All comparative cost language in slides must go through `terms.js` `data-term` dictionary.
*   **Exception:** The `methodology` field in `app.py` (internal backend, never displayed in slide iframes) may retain soft estimates tagged 🔴 NEEDS-EXPERT.

### 8.3 Authored Dollar Figures in app.py GEMMA_FINDING_TEMPLATES
*   Current `GEMMA_FINDING_TEMPLATES` in `app.py` contain authored `$150,000` figures in advisory strings displayed in the live replay.
*   These are in the **interactive demo area** (tab_h1.html live replay), not in the slides.
*   These are **deferred** (tracked in NEXT_SESSION_PROMPT.md) — the slides are the priority. Live replay cleanup is a separate pass.

---

## Section 9 — Global Typography: Content Scale

*   **Current:** `--content-scale: 1.2` in `tokens.css`
*   **Target:** `--content-scale: 1.3` (increase body text size across all four decks simultaneously by changing this single value)
*   **Pinned elements:** `slide-title` class must remain pinned at `1.75rem` (no `--content-scale` multiplier on title) to prevent headline overflow.
*   **Validation:** After change, manually verify Slide 2 (most content-dense) does not overflow vertical bounds on 2560×1440 display.

---

## Section 10 — Intro Deck Addition (Sovereignty & Data Gravity)

A **brief explicit mention** of data sovereignty and data gravity will be added to `intro.html` Slide 2 (currently lists Compliance, Survivability, Latency, Data Gravity).

*   The current **Data Gravity** pillar copy (`"Process data too massive to economically move to cloud — petabyte-scale, field-resident workloads."`) will be expanded to explicitly name the O&G and P&E context:
    *   *"Acoustic logs, seismic surveys, completion records, shift notes, and realtime historian streams are generated at the field. Processing them at the edge eliminates cloud egress cost and network dependency — and keeps sensitive operational data sovereign."*
*   A **Sovereignty** dimension will be woven into the **Compliance** pillar to make data sovereignty explicit:
    *   *"Regulatory requirements, contractual obligations, and national data residency laws require that operational data — including well histories and production records — never leave the operator's physical infrastructure."*

---

## Decisions NOT in scope for this pass

*   H2 slide redesign (paraffin/wax scenario) — this will proceed AFTER H1 is implemented and verified.
*   `$150,000` × 3 in `tab_architecture.html` — deferred (Architecture tab, not H1 demo path).
*   `PIP` cleanup in `app.js` and `app.py` internal advisory strings — deferred per NEXT_SESSION_PROMPT.md (decks are the audience-facing surface, not live replay text).
*   H2 hostile-engineer RT pass (gdc-second-opinion MCP) — still queued after H1 deployment.

---

## Atomic Implementation Sequence

1.  **Write this document** (`docs/H1_RESET.md`) → mark immutable. *(this step)*
2.  **Update `tokens.css`** — `--content-scale: 1.2` → `1.3`
3.  **Rewrite `h1.html`** — 5-slide redesign per sections 2-7 of this spec (single batched `replace_in_file` call)
4.  **Update `intro.html`** — Sovereignty and Data Gravity copy expansions
5.  **Run `verify_templates.py`** — confirm 20/20 templates, div balance intact
6.  **Docker build → push → rollout restart** → verify live

---

*End of H1_RESET.md — Do not modify without explicit session agreement.*
