# GDC Edge AI Demo — Video Narration Scripts
**Created:** Session AU (June 11, 2026)  
**Format:** Four narrations. Each ~90–120s for H1/H2/H3; ~60s for Overview.  
**Structure per scenario:** Open (the situation) → Tension (the problem) → Reveal (GDC) → Resolution (the outcome) → Bridge to next horizon.

---

## Overview / Value Proposition (~60s)

> *"Industrial operations generate two kinds of intelligence: sensor data — which every SCADA and APM platform reads — and operational documents: shift notes, workover reports, OEM manuals, lab results. Documents that no sensor-based system can read in real time.*
>
> *GDC changes that. A local LLM reads your documents. Local ML models read your sensors. Together they generate a cited differential diagnosis — not just an anomaly score, but a ranked explanation of what's happening and what to do — inside your sovereign boundary, on open weights, in seconds.*
>
> *The whole APM industry is building this capability for the cloud. GDC delivers it where your data already lives."*

---

## H1 Narration — DISCERN (~90–120s)

### The Situation

> *"In a Permian Basin Real-Time Operations Center, an unloading alarm just fired on Well A-3. PIP down. Motor amps down. Standard response: shut it in to be safe. That call costs three to eight thousand dollars in deferred production and restart."*

### The Problem

> *"But this well has two possible causes — and the correct action is the opposite for each.*
>
> *Gas lock: the casing annulus is fully submerged. A gas pocket entered the pump stages. The fix — trim the VFD from 52 to 44 hertz. The well stays online. Twenty-five hundred dollars.*
>
> *Fluid drawdown: the dynamic fluid level has depleted. The pump is running dry. In a moderate-sand well, applying that same trim drops fluid velocity below the critical sand-transport threshold. Solids compact around the rotating impeller. Pump seizure. One hundred and fifty thousand dollar workover.*
>
> *Same alarm. Same four sensors. Opposite actions. The sensor cannot tell you which."*

### The Reveal

> *"GDC has already retrieved the 06:15 shift note, the GOR lab report, and the sonic survey.*
>
> *Casing annulus: fully submerged. GOR: rising. Sand history: stable. That's gas lock.*
>
> *The context was never in the telemetry. It was in three documents the sensor cannot read."*

### The Resolution

> *"The operator reviews the cited verdict and approves the VFD trim. The well stays online. The differential diagnosis took eight seconds. The audit trail cites three documents.*
>
> *At 2am, across 200 wells, operators default to reflexive shut-in — the safe choice. GDC makes the better choice automatic."*

### Bridge

> *"That's the ambiguity problem. H2 shows the provenance problem — when the cause was never in any sensor, and it's written down in a document from eight weeks ago."*

---

## H2 Narration — CLASSIFY (~90–120s)

### The Situation

> *"Well A-3 has been declining for three weeks. Efficiency down. Vibration up. Amps elevated. Slow, progressive — textbook early bearing wear.*
>
> *Every APM platform on the market would route this to a pump-pull investigation. That's a workover — three days offline, spot rig at fourteen thousand a day, plus motor inspection, plus deferred production. Seventy to a hundred thousand dollars."*

### The Problem

> *"Except the pump bearings are fine.*
>
> *This is a Permian carbonate producer. High-wax crude — Wax Appearance Temperature confirmed at one-thirteen Fahrenheit by the PVT report. As production fluid rises up the tubing and cools, paraffin crystals deposit on the tubing wall.*
>
> *The ninety-day hot-oil treatment that clears that wax? Fifty-two days overdue. The chemical vendor had a scheduling conflict — their unit was committed to another pad. That delay is documented in the vendor service portal. It is not in SCADA.*
>
> *Here's what paraffin restriction does on a four-sensor string: the tubing narrows, the pump works harder against backpressure — amps up, vibration up, intake pressure rising, efficiency down. The motor stays cool. It is hydraulic, not mechanical.*
>
> *On the data you have, that pattern is indistinguishable from bearing wear. The sensor cannot tell you that a vendor missed a truck roll."*

### The Reveal

> *"GDC read the chemical vendor service log. PM fifty-two days past due. Vendor delay documented.*
>
> *Read the PVT report. WAT one-thirteen Fahrenheit. Eight-point-three percent wax content. High deposition risk. Ninety-day treatment cycle required.*
>
> *Read the prior pull record. Bearings were normal eighteen months ago. Bearing-age hypothesis eliminated.*
>
> *The recommendation: dispatch hot-oil truck. Three to six thousand dollars. Surface-only. No downhole access required. No pull."*

### The Resolution

> *"The pump stays in the ground. The wax is flushed. The well returns to nominal in hours.*
>
> *The cause was in a vendor portal log that no SCADA historian, no APM platform, and no threshold alarm ever touches. GDC connected it to the sensor pattern in seconds.*
>
> *Fifty-one percent of ESP failures are attributed to human factors and operational errors — including missed preventive maintenance. This is the common case, not the edge case. GDC generates the non-obvious provenance hypothesis automatically — at fleet scale, every time."*

### Bridge

> *"Now: what if you could also optimize production within that safety envelope — and hold the safety line even when the cloud goes dark?"*

---

## H3 Narration — OPTIMIZE (~90–120s)

### The Situation

> *"Oil price just spiked. The operator wants to run Well A-3 faster — fifty to fifty-eight hertz — to capture the production window. Standard economics. Push when the price is right."*

### The Problem

> *"Faster means hotter. Motor winding temperature is the constraint. Exceed two hundred and eighty degrees Fahrenheit — the field derated operating setpoint — and the motor burns out. One hundred and fifty thousand dollar failure.*
>
> *Bayesian optimization can search the setpoint space efficiently. But the cloud doesn't know the asset. And the cloud link is not guaranteed."*

### The Reveal

> *"Vertex AI Vizier searches the optimization space using Gaussian process math. Only parameter-level data goes to the cloud — never raw operational telemetry.*
>
> *Every candidate setpoint is evaluated by the local XGBoost thermal model — running inside the RTOC, inside the perimeter. The edge model enforces the two-eighty limit at every step.*
>
> *If the satellite link drops mid-search — storm, outage, process upset at precisely the wrong moment — the edge model holds the constraint. The optimization stops where the safety line is. No further."*

### The Resolution

> *"The operator runs at fifty-four hertz. Within limits. Capturing the upside.*
>
> *The novel piece is not the cloud optimization — Bayesian search is well understood. The novel piece is the edge safety constraint that holds when the link dies. At precisely the wrong moment. The edge is the safety system."*

### Bridge

> *"Diagnose the cause. Prevent the wrong fix. Optimize within limits.*
>
> *Three problems. One sovereign AI stack. Running inside your perimeter, on open weights, where the data already lives."*

---

## Production Notes

### Recording guidance
- **Pace:** slower than you think. Technical content at conversational pace. Target 120 words/minute.
- **Pauses:** pause after each sentence in the Tension section — let the problem land.
- **Emphasis:** bold = emphasis in the scripts above. Resist the urge to rush the numbers.
- **No filler words.** The scripts are written to land without "um," "so," "basically."

### Screen flow for each recording

**H1:** Open on H1 Briefing Panel 1 → advance to Panel 6 CTA → click "Run the Scenario" → play to GDC detect cursor → pause → reveal L3 documents one by one → HITL approve action card

**H2:** Open on H2 Briefing Panel 1 → advance to Panel 3 CTA → click "Run the Scenario" → play to detection → reveal workover completion report → OEM matrix → pull record → verdict card

**H3:** Open on H3 Optimize tab → walk Vizier hybrid diagram → click "Run the Optimization" → watch setpoint converge → show edge constraint hold

**Overview:** No scenario — walk "How It Works" tab only. Tags → tag-patterns → documents. One screenshot each tier. Close on the three-gap frame.

### Runtime targets
| Narration | Target | Hard limit |
|---|---|---|
| Overview / value prop | 55s | 75s |
| H1 Discern | 100s | 130s |
| H2 Classify | 100s | 130s |
| H3 Optimize | 90s | 120s |
