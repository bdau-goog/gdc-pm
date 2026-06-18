# Google Cloud GDC Edge AI — ESP Operations & Maintenance Video Script
**Target Persona:** ESP Field Operations, Maintenance, and Asset Longevity Managers (Persona #2)  
**Perspective:** Google Cloud (3rd-party technology advisor explaining GDC's value to O&G operators)  
**Target Duration:** Under 6 minutes (spoken narration designed with visual milestones and branching paths to be 100% robust against playback speeds and dynamic random runs)  
**Sourced to Live Code & Physical Laws:** Yes (100% compliant with `docs/DEMO_MASTER.md` and `docs/CLAIM_LEDGER.md`)  

---

## REPLAY RESILIENCY GUIDE (READ BEFORE RECORDING)
1. **No Timestamp Hardcoding:** This script uses **Visual Milestones** (e.g., "As the curves begin to slope downward...", "When the amber GDC marker fires...") instead of fixed timestamps (like "at thirty seconds"). Drag the scrubber at whatever pace is natural for your commentary.
2. **Dynamic Horizon 1 Branching:** When you click "▶ Run the Scenario" in Horizon 1, the application randomly selects *either* **Gas Lock (Gas Entrainment)** or **Fluid Drawdown** (50/50 probability). This script provides **Path A** and **Path B** narration options. Simply read the branch that matches the verdict shown on your screen.
3. **Robust Numeric Ranges:** For Horizon 2 and Horizon 3, spoken numbers use approximate but accurate language (e.g., "over seventy-five barrels per day," "nominally around one point zero to over four millimeters per second"). This ensures that minor dynamic sensor baselines or Vizier seed variations always sound 100% correct.

---

## SECTION 1: VEO AI GENERATED INTRO
### Visuals (Google Veo Scene Prompt)
```
SCENE INTRO-1 — "The Operational Boundary" (~40s)

Veo prompt:
Cinematic, slow-panning shot of a vast Permian Basin oil field at dusk, summer. 
Warm golden-hour orange light glinting off several electric submersible pump (ESP) wellheads and adjacent VFD control enclosures. 
The flat West Texas scrubland stretches to the horizon with long shadows. 
Cut to: Inside a quiet, dimly lit Real-Time Operations Center (RTOC). A solitary operations engineer sits in front of a wide array of SCADA monitoring screens. The screens show active, trending sensor data plots with yellow and green status indicators. 
On an adjacent desk sits a physical, thick manila folder labeled "Well A-3: PVT Analysis & Completion History" with handwritten engineering notes visible. The folder is lit by the blue-white glow of the monitors. 
Photorealistic, cinematic industrial aesthetic. 35mm film feel, 2-camera cuts. No text overlays or synthetic graphics. 
```

### Narrator (Google Cloud Voiceover)
> *"For upstream oil and gas operators, keeping Electric Submersible Pumps running is the difference between profitable production and soaring lifting costs.*
>
> *Yet, ESP operators face a recurring wall: eighty-five percent of failures are preceded by ambiguous sensor patterns. SCADA trips to protect the equipment, but it cannot tell you why the pump is struggling.*
>
> *To protect both your P&L and asset longevity, you need the context that lives in field documents, not just sensors."*

---

## SECTION 2: GDC SOVEREIGN PLATFORM INTRO
### Visuals (Screen Flow — How It Works Tab)
* **Show:** How It Works tab on the main dashboard.
* **Navigate:** Highlight the three-tier architecture diagram:
  1. **Tier 1 (Telemetry Tags)** — SCADA real-time ingestion.
  2. **Tier 2 (Tag Patterns)** — Continuous local ML scoring (XGBoost running on edge CPU).
  3. **Tier 3 (Document Context)** — Local pgvector RAG document retrieval (AlloyDB Omni).
* **Presenter Action:** Mouse over the three tiers, pausing briefly on the pgvector RAG / Document Context tier.

### Narrator (Google Cloud Voiceover)
> *"This is Google Distributed Cloud—or GDC. It brings Google's advanced AI and data stack directly into your secure on-premise operations technology perimeter.*
>
> *GDC works alongside your existing SCADA. Continuous local machine learning models evaluate real-time telemetry, while AlloyDB Omni runs pgvector semantic search over your private well dossier.*
>
> *When an anomaly occurs, GDC fuses these two streams. It reads your shift notes, lab reports, and prior workover logs to deliver an auditable, cited differential diagnosis in seconds."*

---

## SECTION 3: HORIZON 1 — DISCERN (Resolving Telemetry Ambiguity)
### Visuals (Screen Flow — Horizon 1 Tab)
* **Show:** Navigate to the H1 Briefing Panels (Slides 1–5).
* **Briefing Panel Walkthrough:**
  * **Slide 1: THE SCENARIO** — Same sensor signal, two opposite causes.
  * **Slide 2: AMBIGUOUS TELEMETRY** — PIP and Motor Amps declining; Winding Temperature and Vibration staying near-nominal (lagging indicators).
  * **Slide 3: DECISION SUPPORT** — Gas Lock (VFD trim: cost $2,500) vs. Fluid Drawdown (critical depletion, sand-seizure risk, cost if wrong is a $150k pump pull).
  * **Slide 4: ADDING CONTEXT** — Fusing telemetry with shift notes, GOR report, and sonic surveys.
  * **Slide 5: INDUSTRIAL APPLICATION** — Fleet-scale decision support.
* **Presenter Action:** Click **"▶ Run the Scenario"**. 
* **Scrubbing Milestone 1:** Advance the scrubber slowly into the pre-detection zone. Note the declining pressure and current, while temp and vib remain flat.
* **Scrubbing Milestone 2:** Move the scrubber past the **amber GDC detect marker**. Pause as the RAG documents begin revealing in the GDC Advisor view.
* **Narrator Branching Decision:** Deliver *either* **Path A** or **Path B** based on the verdict card shown on screen.
* **Scrubbing Milestone 3:** Advance the scrubber to the **red SCADA alarm marker**. Pause and highlight the 4-to-9 minute gap between GDC's context and SCADA's hard-limit trip.

### Path A: If the Random Verdict is "GAS LOCK (GAS ENTRAINMENT)"
> *"On Well A-3, Pump Intake Pressure and Motor Amps decline together. This unloading pattern is physically ambiguous. Winding temperature and vibration are lagging indicators—they remain green and near-nominal through this entire decision window. SCADA thresholds won't cross in time.*
>
> *GDC's local XGBoost model detects the anomaly, firing its amber indicator four to nine minutes before the SCADA hard-limit alarm. Instantly, GDC searches local files. It retrieves the morning shift note, the fluid lab report, and the sand history.*
>
> *The verdict is Gas Lock: the casing annulus is fully submerged, gas-oil ratio is rising, and sand risk is low. GDC confirms Gas Lock, and the operator confidently trims the VFD speed. The well stays online, saving thousands in deferred production."*

### Path B: If the Random Verdict is "FLUID DRAWDOWN (DEPLETION)"
> *"On Well A-3, Pump Intake Pressure and Motor Amps decline together. This unloading pattern is physically ambiguous. Winding temperature and vibration are lagging indicators—they remain green and near-nominal through this entire decision window. SCADA thresholds won't cross in time.*
>
> *GDC's local XGBoost model detects the anomaly, firing its amber indicator four to nine minutes before the SCADA hard-limit alarm. Instantly, GDC searches local files. It retrieves the morning shift note, the fluid lab report, and the sand history.*
>
> *The verdict is Fluid Drawdown: the sonic survey shows the dynamic fluid level has fallen below the pump, and wellbore history flags a high sand-ingress risk. Slowing down would drop fluid velocity and compact solids around the impeller. GDC confirms Drawdown, recommending an immediate emergency shut-in. GDC protects the pump from a catastrophic hundred and fifty thousand dollar sand-seizure."*

---

## SECTION 4: HORIZON 2 — CLASSIFY (Averting Unnecessary Pump Pulls)
### Visuals (Screen Flow — Horizon 2 Tab)
* **Show:** Navigate to H2 Briefing Panels (Slides 1–3).
* **Briefing Panel Walkthrough:**
  * **Slide 1: THE SCENARIO** — Well A-3 waxy crude PVT specs (Wax Appearance Temperature of 118°F) and 90-day hot-oil interval.
  * **Slide 2: AMBIGUOUS TELEMETRY** — Motor amps up 14%, motor efficiency down 10%, vibration rising nominally from 1.0 to 4.5 mm/s RMS (crossing the ISA-18.2 High alarm threshold at 4.0 mm/s).
  * **Slide 3: THREE DOCUMENTS. ONE TRUCK. NO PULL.** — Explaining the chemical vendor log, PVT report, and 18-month prior pull record (bearings normal).
* **Presenter Action:** Click **"▶ Run the Scenario"**.
* **Scrubbing Milestone 1:** Advance the scrubber past Day 90 (the missed hot-oil treatment date). Note the gradual, creeping decline in efficiency and rise in vibration starting around Day 106.
* **Scrubbing Milestone 2:** Move the scrubber past Day 136 where GDC's pre-threshold anomaly scoring triggers pgvector RAG.
* **Scrubbing Milestone 3:** Pause on the final Day 142. GDC Advisor retrieves and sequentially reveals the chemical log (52 days late), PVT report (WAT 118°F), and prior pull record (bearings normal 18 months ago). High-level the green GDC Verdict Card.

### Narrator (Google Cloud Voiceover)
> *"Over three weeks, Well A-3 shows rising amps, declining efficiency, and vibration climbing from one point zero to four point five millimeters per second, crossing the ISA High alarm at four point zero.*
>
> *To standard APM, this pattern looks exactly like mechanical bearing wear—recommending a seventy to one hundred thousand dollar pump-pull investigation.*
>
> *But GDC looks outside the sensors. It queries three siloed data sources. It finds the fluid PVT report confirming a waxy crude with a Wax Appearance Temperature of one-eighteen Fahrenheit. It retrieves the third-party chemical vendor log showing the ninety-day paraffin treatment is fifty-two days overdue.*
>
> *Finally, GDC verifies the prior pull record: bearings were normal eighteen months ago.*
>
> *The diagnostic verdict: Paraffin restriction—NOT bearing wear. By dispatching a surface hot-oil truck for around six thousand dollars instead of a pulling rig, the operator averts a massive capital expense, resuming nominal flow within hours."*

---

## SECTION 5: HORIZON 3 — OPTIMIZE (Constraint-Bounded Edge Optimization)
### Visuals (Screen Flow — Horizon 3 Tab)
* **Show:** Navigate to H3 Briefing Panels (Slides 1–3).
* **Briefing Panel Walkthrough:**
  * **Slide 1: MAXIMUM PRODUCTION. MAXIMUM CARE.** — 6-well Pad Alpha. Associated Gas-Oil Ratios (A-3/A-6: 450, A-5: 1,350 scf/bbl). Shared gas takeaway contract limit of 8.0 MMscfd.
  * **Slide 2: THREE CEILINGS** — Binding gas ceiling, 280°F winding temperature safety limit (API RP 11S3), and RUL limits.
  * **Slide 3: CLOUD SEARCHES. EDGE ENFORCES.** — Vertex AI Vizier GP Bandit (cloud) vs. Local XGBoost thermal model (`esp_thermal.ubj`) enforcing the 280°F safety limit locally.
* **Presenter Action:** Click **"▶ Run the Optimization"**.
* **Visual Milestone 1:** Watch the Vertex AI Vizier trial dots (1 to 15) populate the Pareto chart.
* **Visual Milestone 2:** Pause once the optimal setpoints adjust in the per-well table (A-3/A-6 running at 66.0 Hz, A-5 throttled to 59.7 Hz).
* **Visual Milestone 3:** Highlight the overall production uplift card and note that the edge-safety constraint handles any Starlink network drop.

### Narrator (Google Cloud Voiceover)
> *"Now: how do we optimize production across your fleet while protecting individual assets?*
>
> *On Pad Alpha, six active ESP wells share a midstream gas takeaway ceiling of eight point zero million cubic feet per day. Since GOR varies across wells, a standard SCADA uniform throttle leaves over seventy-five barrels per day of high-value, gas-efficient production deferred.*
>
> *GDC solves this. Vertex AI Vizier runs a multi-dimensional search in the cloud, while GDC's local physics polynomial evaluates every candidate setpoint on-premises against each motor's two-hundred-and-eighty-degree winding temperature limit.*
>
> *The result is a joint optimal setpoint allocation: low-GOR wells A-3 and A-6 are accelerated to sixty-six hertz, while high-GOR well A-5 is throttled back to fifty-nine point seven hertz.*
>
> *This captures an extra seventy-seven point nine barrels per day—generating over three hundred and sixty-nine thousand dollars over ninety days. And if your satellite link drops mid-search, GDC enforces these thermal safety limits locally on the edge, offline and uninterrupted."*

---

## SECTION 6: WRAP-UP / OPERATIONAL SUMMARY
### Visuals (Screen Flow — Operations & Financials Tabs)
* **Show:** Move to the Operations and Financials tabs on the dashboard.
* **Highlight:** The combined fleet-wide savings, reduced workover frequencies, and lower lifting costs achieved.
* **Narrator Focus:** Summary of Google's unique GDC offering.

### Narrator (Google Cloud Voiceover)
> *"By fusing real-time sensor streams with unstructured document context, GDC eliminates diagnostic blind spots, protects downhole assets, and maximizes production within strict physical limits.*
>
> *You get the computational power of Google Cloud AI, deployed inside your secure OT boundary, on open-weight models where your data already lives.*
>
> *Sovereign edge intelligence. Lower lifting costs. Maximum runtime. That is GDC for oil and gas operations."*

---

## SCREEN FLOW & ACTION REFERENCE

| Video Section | Tab / View | Screen Actions & Clicks | Spoken Keywords to Sync |
|---|---|---|---|
| **SECTION 1** | None (Veo Intro) | Video B-roll plays on full screen | *ESP operations, lifting costs, field documents* |
| **SECTION 2** | `How It Works` | Highlight Tier 1, 2, and 3 tiers sequentially | *Google Distributed Cloud, pgvector, AlloyDB Omni* |
| **SECTION 3** | `Horizon 1` | Walk through Briefing Slides 1–5 → Click **"▶ Run the Scenario"** → Scrub slowly to pre-detection → Scrub past amber marker → Note document reveals → **Deliver Path A (Gas Lock) or Path B (Drawdown)** → Scrub past red SCADA marker | *unloading pattern, lagging indicators, amber indicator, shift note, fluid lab, verdict* |
| **SECTION 4** | `Horizon 2` | Walk through Briefing Slides 1–3 → Click **"▶ Run the Scenario"** → Scrub past Day 90 → At Day 136 show document reveals → Show green Verdict Card | *millimeters per second, bearing wear, chemical vendor log, fifty-two days overdue* |
| **SECTION 5** | `Horizon 3` | Walk through Briefing Slides 1–3 → Click **"▶ Run the Optimization"** → Watch trials 1–15 populate → Highlight setpoint table and uplift card | *gas takeaway, uniform throttle, winding temperature, seventy-seven point nine, offline* |
| **SECTION 6** | `Operations` / `Financials` | Toggle tabs to show fleet dashboard and ROI metrics | *fusing, sovereign edge intelligence, lower lifting costs* |

---

## SPOKEN FIGURES INTEGRITY GATE
To maintain 100% compliance with the actual running codebase, the speaker MUST NOT deviate from these locked numerical values:
* **H1 GDC Detect Index:** Fired dynamically via `HEALTH_THRESHOLD=0.87` (typically `35–46`). Script specifies "four to nine minutes before the SCADA hard-limit alarm."
* **H1 SCADA Alarm Index:** Fired dynamically via rolling-average PIP < 1,020 PSI (typically `55–73`).
* **H2 Vibration Units & Readings:** Nominally `1.0 mm/s`, rising to `4.5 mm/s` RMS, crossing the High alarm at `4.0 mm/s`. (Units: millimeters per second).
* **H2 Overdue PM Status:** `52 days` past due (Day 142).
* **H2 Wax Appearance Temperature (WAT):** `118°F`.
* **H2 Surface Hot-oil Cost:** `six thousand dollars` (representing the range `$3,000–$6,000`).
* **H2 Pump Pull Investigation Cost:** `seventy to one hundred thousand dollars`.
* **H3 Gas Takeaway Contract Ceiling:** `eight point zero million standard cubic feet per day` (8.0 MMscfd).
* **H3 Motor Winding Temp Limit:** `two hundred and eighty degrees Fahrenheit` (280°F).
* **H3 Optimal Setpoints:** A-3/A-6 at `sixty-six hertz` (66.0 Hz); A-5 throttled to `fifty-nine point seven hertz` (59.7 Hz).
* **H3 Production Uplift & Revenue:** `plus seventy-seven point nine barrels per day` (+77.9 bbl/d); `three hundred and sixty-nine thousand dollars` over 90 days ($369,225).
