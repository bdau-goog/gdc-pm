# GDC Edge AI Demo — Video Production Scripts
**Version:** Session BR (June 13, 2026)  
**Status:** PRODUCTION-READY — full Veo prompts, panel-by-panel narration, interactive replay directions  
**Based on:** `docs/DEMO_MASTER.md` (master spec), `gke/fault-trigger-ui/index.html` (live UI panels), `docs/DEMO_STORY_AND_PATH.md` (locked value proposition)

---

## READING GUIDE

### Script Structure
Each demo video has four sections:
1. **`VEO INTRO`** — Detailed scene prompts for Google Veo cinematic B-roll (photorealistic, ~60–90s total)
2. **`PANEL BRIEFINGS`** — Panel-by-panel presenter narration, synchronized to the live UI briefing panels
3. **`SCENARIO REPLAY`** — Dashboard walkthrough narration synchronized to interactive chart playback
4. **`BRIDGE / CTA`** — Closing line and bridge to the next demo video

### Voice Discipline (PRIME DIRECTIVE)
Every sentence in these scripts has been reviewed against the claim-survival tests in `docs/DEMO_MASTER.md`. Numbers shown are exactly the values held in the live deployed code. No claim appears here that cannot survive a hostile-engineer rebuttal.

- **Pace target**: 110–125 words per minute. Pause fully on each numbered fact.
- **Emphasis**: capitals in the text mark vocal stress — do not rush them
- **No straw men**: "SCADA trips the well in to protect the pump" — that is the correct framing; say it that way
- **Concede, then win**: always state what the baseline system does correctly; win only on what the document provides

### Runtime Targets
| Video | Target | Hard Limit |
|---|---|---|
| Overview / Value Prop | 60s | 80s |
| H1 Discern | 105s | 130s |
| H2 Classify | 110s | 135s |
| H3 Optimize | 100s | 125s |

---

## ─────────────────────────────────────────
## VIDEO 0 — OVERVIEW / VALUE PROPOSITION
## ─────────────────────────────────────────

### VEO INTRO — Overview (1 scene, ~40s)

```
SCENE O-1 — "Two Kinds of Intelligence" (~40s)

Veo prompt:
Cinematic drone pull-back from a glowing RTOC (Real-Time Operations Center) at 3am.
Dozens of SCADA screens show trending sensor values — orange and red alarm banners flashing.
An engineer leans forward studying a screen showing flat pump curves and declining efficiency.
On an adjacent desk, a thick stack of paper field documents: handwritten shift notes, a folder
labeled "PVT Analysis Report," a service log printout. The paper stack is in soft focus.
The engineer's face is lit blue-white by the screen — focused, uncertain.
Camera pulls back further to reveal through the window a dark Permian Basin oil field — 
twelve pump jacks and wellhead christmas trees silhouetted against a star-filled sky, 
red warning lights blinking on two of them.
B-roll cuts: close-up of handwritten shift note with wellbore diagram; 
close-up of GOR lab report stamped "Permian Basin Fluid Analysis LLC"; 
close-up of a SCADA historian flat-lining — no root-cause insight visible.
Photorealistic. Dark cinematic industrial aesthetic. No motion graphics. No text overlays.
Color palette: deep blue-black, amber monitor glow, cool white LED overheads.
Subject: upstream oil & gas operations. 2-camera cuts, smooth transitions.
```

---

### OVERVIEW NARRATION (~60s)

> *"Industrial operations generate two kinds of intelligence.*
>
> *Sensor data — which every SCADA and APM platform reads in real time.*
>
> *And operational documents: shift notes, workover reports, OEM manuals, lab results. Documents that every sensor-based system misses entirely.*
>
> *GDC changes that. A local LLM reads your documents. Local ML models read your sensors. Together, they surface a cited differential diagnosis — every alert backed by evidence from your own field documents, every verdict auditable, running inside your sovereign boundary, on open weights, in seconds.*
>
> *GDC is a decision-support advisor, not an autonomous controller. The evidence is cited. The audit trail is complete. The engineer makes the call.*
>
> *The cloud APM industry is building exactly this capability — for the cloud. GDC delivers it where your data already lives."*

---

### SCREEN FLOW — Overview
**Open on:** How It Works tab → Tags tier (real-time sensor tag stream) → tag-patterns tier (multivariate correlated ML scores) → Documents tier (pgvector RAG document retrieval with cited excerpts)  
**Close on:** The three-gap summary frame (Ambiguity / Provenance / Optimization)  
**No interaction needed.** Walk the three-tier diagram. One pause at each tier.

---

## ─────────────────────────────────────────
## VIDEO 1 — H1 DISCERN (The Ambiguity Problem)
## ─────────────────────────────────────────

### VEO INTRO — H1 Discern (3 scenes, ~70s)

```
SCENE H1-1 — "3am, 200 Wells" (~25s)

Veo prompt:
Overhead aerial establishing shot of a Permian Basin oil field at night, 
West Texas, summer. Dense pad development — dozens of beam pump jacks,
electric submersible pump wellheads (simple christmas tree with VFD control box), 
gathering lines lit every hundred meters by small yellow flames from instrument pilots.
Stars overhead. No wind. Absolute silence implied.
Cut to: interior RTOC. Large bank of monitors. A lone operator, 30s, in a hard-hat-free
office environment, monitoring dozens of real-time well channels. Alarm banner fires on
Well A-3: yellow banner — "A-3 UNLOADING — PIP LO-LO". Operator sits forward.
Hard cut to: close-up of the screen. A SCADA historian trending four channels:
PIP declining, motor amps declining, VFD frequency flat at 52 Hz, winding temp steady.
Color: dark blue-black. Screen glow amber-white. Tension.
Photorealistic. No text overlays. Industrial tone.
```

```
SCENE H1-2 — "Same Four Numbers, Two Opposite Calls" (~25s)

Veo prompt:
Split-image concept. Left half: ESP well producing normally, cross-section schematic
style but photorealistic — fluid flowing up the production tubing inside a steel wellbore casing.
A small pocket of gas enters the intake below the ESP pump. Bubbles. Impeller running in froth.
Right half: Same well cross-section, but the dynamic fluid level has fallen. 
The pump intake is now above the fluid surface. Pump running in air. Dry. 
Close-up of rotating metal impeller in wet sand and partial fluid. Sand grains visible.
Camera pushes in to show the micro-scale: sand particles settling onto pump impeller faces.
These two images should feel like diagnostic diagrams brought to life — photorealistic but
clearly showing internal wellbore mechanics.
Lighting: cool blue-tinted industrial X-ray-like clarity. 
No text. No overlays. Precise mechanical realism.
```

```
SCENE H1-3 — "The Document the Sensor Cannot Read" (~20s)

Veo prompt:
Close-up: A hand-written field shift note on standard field engineering paper.
Partially legible: mentions "A-3 casing pressure," "annulus submerged," "GOR rising 3 days."
Corner of a printed lab report is visible: "Gas-Oil Ratio Analysis — Well Pad Alpha."
The documents are in focus. Behind them, soft-focus: the SCADA screens still flashing.
The gap between physical paper and digital sensor data is the visual narrative.
Cut to: time-lapse of the RTOC operator's hand setting down the paper and reaching for a keyboard.
Warm paper-tone vs. cool blue screen-tone color contrast. 35mm film aesthetic. No overlays.
```

---

### H1 PANEL BRIEFINGS — Panel-by-Panel Narration

**PRE-PANEL / OPENING:**
> *"DISCERN. The ambiguity problem. One alarm. Same four sensors. Opposite actions. The sensor alone cannot tell you which."*

---

**PANEL 1 of 6 — "The Setup"**
*Screen shows: Well A-3 specs, ESP string diagram, Permian Basin context card, intake-only sensor string callout*

> *"Well A-3 is a Permian Basin ESP producer. Standard four-sensor string: pump intake pressure, motor amps, VFD frequency, and winding temperature. No discharge-pressure gauge — that's roughly ninety percent of Permian ESP installations.*
>
> *This is not a unique well. This is the common case."*

---

**PANEL 2 of 6 — "What is an Unloading Event?"**
*Screen shows: animated PIP trace, amps trace, explanation of pump unloading mechanics*

> *"An unloading event: the pump intake pressure drops. Amps follow it down. The VFD frequency holds. At its simplest — the pump is no longer moving fluid as efficiently as it was.*
>
> *That pattern fires an unloading alarm on every SCADA historian in the field. Every platform sees it. No platform knows what caused it."*

---

**PANEL 3 of 6 — "One Signature, Two Causes"**
*Screen shows: split comparison — Gas Lock vs. Fluid Drawdown, identical sensor traces, diverging action cards*

> *"Gas lock: a gas pocket entered the pump stages. The casing annulus is fully submerged. The impellers are churning froth instead of fluid.*
>
> *Fix: trim the VFD from fifty-two to forty-four hertz. The well stays online. Approximately twenty-five hundred dollars.*
>
> *Fluid drawdown: the dynamic fluid level has fallen. The pump is running in air — or worse, in partial fluid and sand. In a moderate-sand well, the trim that fixes gas lock would drop fluid velocity below the critical sand-transport threshold. Solids compact around the rotating impeller. Pump seizure. One hundred and fifty thousand dollar workover.*
>
> *Same alarm. Same four sensors. Opposite actions.*
>
> *The sensor cannot tell you which."*

---

**PANEL 4 of 6 — "STATE vs. CONTEXT"**
*Screen shows: STATE column (blue) — sensor values; CONTEXT column (amber) — documents not in sensor data*

> *"STATE is everything the gauge reports. PIP. Amps. Hertz. Winding temperature.*
>
> *CONTEXT is what caused those numbers. Is the casing annulus submerged? What is the current Gas-Oil Ratio? Is this well a known sand producer?*
>
> *None of those questions have answers in the telemetry. They have answers in three documents the sensor cannot read:*
>
> *The 06:15 shift note. The GOR lab report. The sonic fluid level survey.*
>
> *CONTEXT decides. GDC reads CONTEXT."*

---

**PANEL 5 of 6 — "How Operators Decide Today"**
*Screen shows: decision timeline, operator default flowchart — SCADA alarm fires → shut-in to be safe, cost comparison table*

> *"When that alarm fires at two in the morning, on well one-of-two-hundred, the safe default is: shut it in. Protect the pump. Restart during the day shift.*
>
> *That call costs three to eight thousand dollars in deferred production and restart. It is the correct call under uncertainty. SCADA trips to protect the equipment — that is the right design.*
>
> *But if an operator had the three documents in thirty seconds, the probability of gas lock is overwhelming. The confident call is: trim the VFD. Don't shut in.*
>
> *The problem is not operator competence. It is that the document evidence is never assembled — at two in the morning, across two hundred wells — automatically."*

---

**PANEL 6 of 6 — "This Pattern Is Universal"**
*Screen shows: four-industry comparison table — Oil & Gas / Power / Water / Mining — all with the same STATE-CONTEXT gap*

> *"The same gap exists in every industry that runs physical assets.*
>
> *A substation protection engineer knows the transformer temperature. The maintenance backlog that loaded it beyond its thermal rating is in a work order. Not in the sensor.*
>
> *The pattern is universal. GDC closes it inside the sovereign boundary — one stack, any vertical.*
>
> *Click Run the Scenario to see it live."*

---

### H1 SCENARIO REPLAY — Dashboard Walkthrough Narration

**SETUP DIRECTION:**
Click "▶ Run the Scenario" on Panel 6. The dashboard loads. Sensor chart is live — dual-trace Plotly chart: PIP (blue, declining) and motor amps (amber, declining). Playback is paused at t=0.

---

**INTERACTIVE PLAYBACK:**
*Advance scrubber slowly to t=30 (pre-detection zone)*

> *"The unloading signature is developing. PIP trending down. Amps following. No alarm has fired yet. GDC's multivariate Bayesian model is already scoring this correlation across all four channels.*
>
> *This is the pre-threshold zone. SCADA is quiet. GDC is not."*

*Advance scrubber to GDC detection cursor (index 33)*

> *"GDC detects the anomaly here — at index thirty-three. Correlation scoring exceeds the threshold. RAG retrieval fires automatically.*
>
> *Three documents. Eight seconds."*

**SWITCH TO GDC ADVISOR VIEW — document reveals appear sequentially:**

*Watch first document reveal: shift note*

> *"Shift note, 06:15. Casing annulus: FULLY SUBMERGED. Fluid level above pump. That eliminates fluid drawdown."*

*Watch second document reveal: GOR lab report*

> *"GOR lab report. Current Gas-Oil Ratio: RISING. Consistent with gas entering the annulus and finding the pump intake. Confirms gas-lock hypothesis."*

*Watch third document reveal: sand log*

> *"Sand history: STABLE. No elevated particulate production over the past ninety days. Sand-seizure risk is LOW — the aggressive VFD trim is safe for this well."*

**GDC verdict card appears:**

> *"Verdict: GAS LOCK. Trim VFD from fifty-two to forty-four hertz. Risk: LOW.*
>
> *The context was never in the telemetry. It was in three documents the sensor cannot read."*

*Advance scrubber to SCADA alarm index (index 60)*

> *"SCADA fires its alarm here — at index sixty. Twenty-seven data points after GDC.*
>
> *By this point, GDC's recommendation has already been reviewed and approved. The operator acted on evidence, not reflexive caution."*

**SWITCH TO HUMAN-IN-THE-LOOP card:**

> *"The operator reviews the cited verdict. Three sources, two sentences, eight seconds. Approves the VFD trim. The well stays online. The audit trail is complete.*
>
> *That's the ambiguity problem. H2 shows the provenance problem — when the cause was never in any sensor and it is written in a document from eight weeks ago."*

---

## ─────────────────────────────────────────
## VIDEO 2 — H2 CLASSIFY (The Provenance Problem)
## ─────────────────────────────────────────

### VEO INTRO — H2 Classify (3 scenes, ~75s)

```
SCENE H2-1 — "Fifty-Two Days of Silence" (~25s)

Veo prompt:
Extreme close-up: inside a steel production tube, photorealistic microscopic view.
Crude oil rising, golden-amber in warm lighting. The tubing walls are clean at first.
Time-lapse progression: white crystalline paraffin wax begins depositing on the tube wall,
slowly narrowing the bore. The deposition is gradual, almost imperceptible day-by-day.
By the end of the shot, the bore is visibly restricted — a partial occlusion of waxy material.
Above-ground exterior: a Permian Basin ESP wellhead on a cold winter morning, steam rising
from the wellhead insulation wrap, the chemical injection port on the surface tree clearly
visible but disconnected — no truck hose attached, no chemical flowing.
Calendar visual: not a graphic but implied — a field maintenance board on a trailer wall, 
showing a dry-erase calendar with a circled date crossed out. No truck has arrived.
Photorealistic. Subdued winter morning palette — pale blue sky, dusty beige caliche.
```

```
SCENE H2-2 — "The Diagnostic Trap" (~25s)

Veo prompt:
Split-frame diagnostic: on the left, a vibration signature — a printed chart showing 
gradually rising vibration amplitude over 21 days on smooth engineering paper.
On the right, a worn ESP pump bearing assembly — grease-stained, showing early wear marks
on a thrust disc, machined steel surfaces. This is what a bearing-wear diagnosis looks like.
The visual question is implicit: same vibration chart, two possible explanations.
APM screen insert: a software dashboard (generic, non-branded) showing "MECHANICAL DEGRADATION — 
PROBABLE BEARING WEAR — RECOMMEND PULL INVESTIGATION" in bold amber.
Close-up of the pull cost estimate form: circled figure, five digits.
The trap closes: what looks like one thing is something else entirely.
Photorealistic. No motion graphics. Clean industrial diagnostic aesthetic.
```

```
SCENE H2-3 — "The Truck That Should Have Come" (~25s)

Veo prompt:
Dust road in the Permian Basin. A hot-oil service truck — a specialized pump-and-heat trailer
on a heavy flatbed — is parked at a different well location, connected with orange-jacketed
hoses. A technician in PPE is monitoring a pressure gauge on the truck's control panel.
Caption feel: this truck is doing the job somewhere else. 
Cut to: a different wellhead, same design, identical ESP installation. No truck. No hoses. 
The wellhead stands alone in the flat West Texas scrubland. A faded maintenance schedule
printout is pinned to the wellhead enclosure — the PM date has passed.
The absence of the truck is the story. No truck = no hot-oil treatment = paraffin builds.
Warm afternoon light, long shadows, Permian dust. Photorealistic. No overlays.
```

---

### H2 PANEL BRIEFINGS — Panel-by-Panel Narration

**PRE-PANEL / OPENING:**
> *"CLASSIFY. The provenance problem. The pump bearings are fine. The cause is in a vendor service portal that no SCADA historian, no APM platform, and no threshold alarm ever touches."*

---

**PANEL 1 of 3 — "Waxy Crude. Routine PM. Then Nothing."**
*Screen shows: Well A-3 spec card, production chemistry card (WAT 118°F, 90-day hot-oil interval), callout on paraffin being endemic to Permian carbonates*

> *"Well A-3 is a Permian carbonate producer. High-wax crude — Wax Appearance Temperature confirmed at one-eighteen Fahrenheit by the PVT analysis for this well.*
>
> *As produced fluid rises up the production tubing and cools below that temperature, paraffin crystals nucleate on the pipe wall. The restriction builds.*
>
> *The standard countermeasure: hot-oil treatment every ninety days. Circulate heated oil down the annulus, melt the wax, restore the bore. Three to six thousand dollars. A truck roll. No downhole access required.*
>
> *This well has a ninety-day hot-oil schedule. Routine. Standard. Until the vendor missed the truck roll."*

---

**PANEL 2 of 3 — "Fifty-Two Days Late. Bearings or Wax?"**
*Screen shows: four sensor tiles (Amps +14%, Vib 0.38 in/s, Eff -10%, PIP stable), Day 0→90→106→142 timeline strip, SCADA/APM two-tier framing callout*

> *"Three weeks of progressive deterioration. Motor amps up fourteen percent above nominal. Vibration rising — from 0.15 to 0.38 inches per second RMS. Motor efficiency down ten percent. Intake pressure stable, slightly rising.*
>
> *Against threshold SCADA — the kind running eighty-five to ninety-five percent of Permian independent operations — the vibration HI alarm fires with no root-cause hypothesis. Action cards: pull investigation, or continue monitoring. Neither names paraffin.*
>
> *Against best-of-breed APM — multivariate ML, trained on thousands of ESP events — this pattern routes to mechanical degradation. Probable bearing wear. Recommend pull investigation.*
>
> *The symptom identification is CORRECT. The root cause is WRONG. The recommended fix costs seventy to one hundred thousand dollars.*
>
> *Here is what paraffin restriction actually does: the tubing narrows. The pump works harder against backpressure — amps up, vibration up, efficiency down. The motor stays cool because this is hydraulic, not mechanical. And intake pressure rises slightly as the operating point shifts.*
>
> *On a four-sensor string, that pattern is indistinguishable from bearing wear — unless you know the wax chemistry and the PM record.*
>
> *That chemistry is in the PVT report. That record is in the vendor portal. Neither is in SCADA."*

---

**PANEL 3 of 3 — "Three Documents. One Truck. No Pull."**
*Screen shows: GDC verdict card (green), action cards — Hot-oil truck ~$3k–$6k [GDC RECOMMENDED] vs Pull ~$70k–$100k [AVERTED], document stack (vendor log, PVT report, prior pull record)*

> *"GDC retrieved three documents.*
>
> *Chemical vendor service log: last hot-oil treatment Day zero. Ninety-day schedule. Today is Day one-forty-two — fifty-two days overdue. Delay reason: vendor truck committed to another pad.*
>
> *Fluid PVT report: Wax Appearance Temperature one-eighteen Fahrenheit. Moderate-to-high wax content. Ninety-day hot-oil interval required for this well at current flowing conditions.*
>
> *Prior pull record, eighteen months prior: bearings inspected — NORMAL. No unusual wear. Pump returned to service in good condition.*
>
> *GDC verdict: paraffin wax deposition — NOT bearing wear. Hot-oil treatment overdue fifty-two days. Bearing-wear hypothesis eliminated. Dispatch hot-oil truck. Do NOT pull.*
>
> *The cause was in a vendor portal log that no SCADA historian, no APM platform, and no threshold alarm ever touches. GDC connected it to the sensor pattern in two seconds. GDC advised. The engineer decided.*
>
> *Click Run the Scenario."*

---

### H2 SCENARIO REPLAY — Dashboard Walkthrough Narration

**SETUP DIRECTION:**
Click "▶ Run the Scenario" on Panel 3. Dashboard loads. Dual-trace Plotly chart: motor efficiency (amber, declining from Day 90) and vibration (purple, rising from Day 90). X-axis: days since last hot-oil treatment (0–142). Playback paused at Day 0.

---

**INTERACTIVE PLAYBACK:**
*Advance scrubber to Day 90 zone*

> *"The well runs normally for ninety days after the last treatment. Efficiency holds. Vibration baseline. The hot-oil PM window has now passed — the vendor truck did not come."*

*Advance slowly to Day 106*

> *"Day one-oh-six. The restriction onset. Efficiency begins its slow decline. Vibration begins its slow climb. On any given day, the change is imperceptible. Over twenty-one days, the pattern accumulates into a textbook-looking degradation signature."*

*Advance to GDC detection cursor*

> *"GDC flags the anomaly here — at Day one-thirty-six. The correlated multivariate pattern — efficiency declining while vibration rises — triggers the RAG retrieval. Not a single threshold. A correlated pre-threshold signature."*

**SWITCH TO GDC ADVISOR VIEW — document reveals appear sequentially:**

*Watch first document reveal: vendor service log*

> *"Vendor service log retrieved. Treatment Day zero. Schedule: ninety days. Current day: one-forty-two. Overdue: fifty-two days. Delay cause: truck availability — vendor unit committed to another pad.*
>
> *By itself, a missed PM is a maintenance flag, not a diagnosis. The model needs the chemistry."*

*Watch second document reveal: PVT report (+2s)*

> *"PVT lab report retrieved. WAT: one-eighteen Fahrenheit. Moderate-to-high wax content. Ninety-day treatment interval required for this well. The overdue PM is now crossed with confirmed high-wax crude — paraffin restriction is the most probable explanation for this sensor pattern."*

*Watch third document reveal: prior pull record (+3.5s)*

> *"Prior pull record retrieved. Last workover eighteen months ago. Bearing condition at inspection: NORMAL. No unusual wear. Bearing-age hypothesis is now eliminated.*
>
> *Three documents. Two seconds per reveal. The hypothesis space has collapsed."*

**GDC verdict card fully rendered:**

> *"Verdict: PARAFFIN WAX DEPOSITION — NOT BEARING WEAR. Confidence: high. Dispatch hot-oil truck. Do NOT authorize pull.*
>
> *The engineer reviews the cited evidence. The call is clear: send the truck, not the rig. The pump stays in the ground. The wax is flushed. The well returns to nominal within hours.*
>
> *Fifty-one percent of ESP failures are attributed to human factors and operational errors — including missed preventive maintenance. This is the common case, not the edge case.*
>
> *GDC generates the non-obvious provenance hypothesis automatically — at fleet scale, every time."*

---

### H2 BRIDGE

> *"Now: what if you could also optimize production within that safety envelope — and hold the safety line even when the cloud goes dark?"*

---

## ─────────────────────────────────────────
## VIDEO 3 — H3 OPTIMIZE (The Optimization Problem)
## ─────────────────────────────────────────

### VEO INTRO — H3 Optimize (3 scenes, ~70s)

```
SCENE H3-1 — "Six Wells. One Gas Budget." (~25s)

Veo prompt:
Aerial establishing shot: Pad Alpha. Six identical ESP wellheads arranged in two rows of three,
all active, VFD control enclosures humming beside each christmas tree, gathering lines
converging to a central production manifold.
A midstream gas compressor station is visible four hundred meters away — two large reciprocating
compressor buildings with inlet separator vessels and metering skid. A flow computer board 
is visible through a glass panel: a large digital readout showing "7.9 MMscfd / 8.0 MMscfd MAX."
The number is approaching the limit. The operator watching the board has his hand on his radio.
Pull back further: six wells, one gas processing limit, one decision-maker.
Photorealistic. Late afternoon Permian Basin light — golden-hour shadows across the caliche.
No motion graphics. No text overlays. Compositional tension.
```

```
SCENE H3-2 — "The Search the Spreadsheet Cannot Run" (~25s)

Veo prompt:
Close-up montage: six VFD control panels, one per well, each displaying a current frequency 
setpoint in large LED digits — all reading 63.0 Hz. Identical. Conservative. Uniform.
The camera pans across all six, then cuts to: a laptop screen in an engineering trailer showing 
a dense Excel spreadsheet — 47 columns, 6 wells, three constraint sheets. 
An engineer is drawing a circle around a single cell with a pen.
Cut to: abstract visualization of the optimization search space — not a screen graphic, but a 
physical analog: a sand table or scale model with six moving levers, each influencing the others.
The interplay between variables — raising one lever lowers another — is made physical.
This is not a software problem. It is a physical constraint problem with six coupled variables.
Industrial design aesthetic. Clean. No typography. No UI mockups. Pure concept.
```

```
SCENE H3-3 — "Edge Holds When the Link Drops" (~20s)

Veo prompt:
A Starlink dish mounted on the roof of a Permian Basin field operations trailer — the 
phased-array form factor, wet with rain from a passing thunderstorm. Lightning in the middle distance.
Interior: the RTOC operator is watching a network status indicator flip from green to amber.
The satellite link has dropped. He turns to a second monitor — the local optimization results 
are still displayed. The setpoints are holding. The constraint stack shows green.
The edge machine is still running. The safety line is intact.
A small indicator light on a rack-mounted server (labeled GDC EDGE) blinks steadily green.
The storm continues outside. The system has not moved.
Cinematic tension. Warm amber interior vs. cold blue-white storm exterior. Photorealistic.
```

---

### H3 PANEL BRIEFINGS — Panel-by-Panel Narration

**PRE-PANEL / OPENING:**
> *"OPTIMIZE. Six wells. One gas-compression takeaway contract. Every barrel of oil is accompanied by associated gas — but the wells differ in how much gas comes with each barrel. When the gas budget is tight, not all barrels cost the same."*

---

**PANEL 1 of 3 — "Maximum Production. Maximum Care."**
*Screen shows: 6-well GOR table (A-1: 520, A-2: 680, A-3: 450, A-4: 890, A-5: 1350, A-6: 450 scf/bbl), associated gas explanation, gas ceiling card*

> *"Pad Alpha. Six active ESP producers. One binding constraint: a midstream gas-compression takeaway contract — eight-million standard cubic feet per day maximum. That is an RRC of Texas-class production limit. Exceed it and you face curtailment or flaring violations.*
>
> *Every well produces oil and associated gas. But the ratio differs dramatically. A-3 and A-6 produce four hundred and fifty cubic feet of gas per barrel of oil. A-5 produces thirteen-fifty.*
>
> *Three times the gas per barrel. When the gas ceiling is binding, the low-GOR wells are three times more valuable to run at full speed.*
>
> *SCADA's safe default: uniform throttle. Scale every well back proportionally. Conservative. Safe. Leaves approximately seventy-eight barrels per day of production potential unrealized — oil the pad is physically capable of delivering."*

---

**PANEL 2 of 3 — "Three Ceilings You Cannot Ignore."**
*Screen shows: constraint stack (gas ceiling AMBER/BINDING · thermal SLATE/not binding · RUL SLATE), SCADA honest framing callout*

> *"Three real constraints per well — not policy, physics.*
>
> *Gas ceiling: field-level and binding this run. Eight-million-scfd. Every setpoint decision is bounded by it.*
>
> *Motor winding temperature: per well, evaluated by a four-feature thermal polynomial — VFD hertz, motor amps, intake fluid temperature, water cut. The derated operating setpoint for this installation: two-hundred-eighty Fahrenheit. Per API RP 11S3. Exceed it and you burn a motor — one hundred and fifty thousand dollar failure.*
>
> *Remaining useful life: tracked per well, not binding this run, but monitored at every candidate setpoint.*
>
> *SCADA uniform throttle is conservative and safe. GDC asks: given these three constraints, what is the highest-production allocation that respects all of them — simultaneously, across all six wells?"*

---

**PANEL 3 of 3 — "Cloud Searches. Edge Enforces."**
*Screen shows: optimal Hz table (A-3: 66.0, A-6: 66.0, A-5: 59.7), uplift card (+77.9 bbl/d, +$369,225/90d), Vizier hybrid diagram, edge-constraint description*

> *"Vertex AI Vizier runs a Gaussian Process Bandit across the six-dimensional search space — one hertz setpoint per well. Fifteen trials. Each candidate setpoint vector is evaluated locally by the physics thermal polynomial before any score returns to Vizier.*
>
> *Only parameter-level data travels to the cloud: hertz vectors and their objective scores. Raw operational telemetry, production rates, and well identities never leave the sovereign boundary.*
>
> *The result: A-3 and A-6 run at sixty-six hertz — full speed, lowest GOR. A-5 trims to fifty-nine-point-seven — highest GOR, gives way. A-2 and A-1 push to sixty-five-point-five.*
>
> *Uplift: plus seventy-seven-point-nine barrels per day. Plus three-hundred-sixty-nine thousand dollars over ninety days. Gas consumed: seven-point-nine-nine-nine-nine — inside the eight-million ceiling.*
>
> *And if the satellite link drops mid-search — storm, outage — the local LP-optimal result is the approved output. The thermal constraint holds. The edge is the safety system.*
>
> *Click Run the Optimization."*

---

### H3 SCENARIO REPLAY — Dashboard Walkthrough Narration

**SETUP DIRECTION:**
Click "▶ Run the Optimization" on Panel 3. The optimization fires. Vizier Pareto chart begins populating. 15 GP-Bandit trial iterations. Each trial dot plots at its objective score.

---

**INTERACTIVE PLAYBACK:**
*Watch first 5 Vizier trials populate*

> *"Vizier is exploring the search space. Early trials are spread — the Gaussian Process is building its model of the objective landscape. Each trial vector is a valid proposal — no constraint violations — because the local physics polynomial has already screened every candidate."*

*Watch trials 6–12 converge*

> *"The exploration focus is narrowing. The GP model has learned which region of the space is productive: low-GOR wells at high frequency, high-GOR wells trimmed back. The objective surface is becoming clear."*

*Trials 13–15 converge to optimal*

> *"Trials thirteen, fourteen, fifteen — converging. The search is done."*

**Per-well setpoint table locks in:**

> *"The optimal allocation. A-3 and A-6 at sixty-six hertz — lowest GOR, maximum speed. A-5 at fifty-nine-point-seven — highest GOR, throttled back. A-1 and A-2 at sixty-five-point-five.*
>
> *SCADA uniform throttle would have run all six at sixty-three hertz — conservative, safe, suboptimal.*
>
> *The difference is seventy-seven-point-nine barrels per day. At fifty-dollar oil — and oil is not fifty dollars today — that is three-hundred-sixty-nine thousand dollars over ninety days.*
>
> *More importantly: no pump was destroyed. No thermal constraint was violated. No gas ceiling was breached. Maximum production, inside every limit."*

**Edge constraint callout:**

> *"Note the edge constraint: the local thermal model evaluated every single trial setpoint before the score was returned to Vizier. The constraint was never advisory — it was enforced at every step.*
>
> *The optimization runs with the cloud. The safety runs on the edge. If the link drops — storm, outage, precisely the wrong moment — the local LP result is the fallback. The constraint holds.*
>
> *That is the novel piece. Not the cloud optimization — Bayesian search is well understood. The novel piece is the edge safety constraint that holds when the link dies."*

---

### H3 BRIDGE / CLOSE

> *"Diagnose the cause. Prevent the wrong fix. Optimize within limits.*
>
> *Three problems. One sovereign AI stack. Every verdict cited. Every engineer in control. Running inside your perimeter, on open weights, where the data already lives."*

---

## ─────────────────────────────────────────
## PRODUCTION NOTES
## ─────────────────────────────────────────

### Veo Prompt Engineering Notes

**Scene specifications that produce the best results:**
- Always specify **photorealistic**, **no motion graphics**, **no text overlays** — Veo defaults to adding labels
- Specify the **time of day and lighting palette** explicitly (night RTOC, golden-hour Permian, winter morning)
- For interior RTOC scenes: specify **blue-white screen glow**, **amber monitor glow**, and one **focused operator**
- For well cross-section / mechanical scenes: specify **precise component names** (thrust disc, impeller, intake, tubing wall) — Veo renders O&G equipment accurately when you use the correct terminology
- The **absence narrative** (truck that didn't come, satellite link that dropped) is harder for generative video; specify it as a **contrast shot** (truck connected to other well / truck absent from this well)

### Recording Guidance

- **Pace**: Slower than you think. Technical content lands at 110–120 words per minute.
- **Pauses**: Full 1.5-second pause after every number. Let it land.
- **Emphasis capitals**: Maintain vocal stress on ALL-CAPS words in the scripts above.
- **No filler words.** These scripts are written to land clean. No "basically," "so," "kind of."
- **Cost framing**: State both sides: "X avoids Y" — not just "saves Y." 

### Screen Flow Summary

| Video | Open on | Navigate through | Close on |
|---|---|---|---|
| Overview | How It Works tab | Tags → tag-patterns → Documents | Three-gap summary frame |
| H1 | H1 Briefing P1 | P1→P2→P3→P4→P5→P6 → Run → Replay | HITL approval card |
| H2 | H2 Briefing P1 | P1→P2→P3 → Run → Replay | Doc reveals + verdict card |
| H3 | H3 Briefing P1 | P1→P2→P3 → Run Optimization | Vizier Pareto + per-well table |

### Integrity Gate — Spoken Figures vs Live Code Values

These are the safety-critical number correspondences. Script must match code exactly.

| Spoken Claim | Code Location | Value |
|---|---|---|
| GDC detection index 33 | `app.py gdc_detect_idx` | 33 |
| SCADA alarm index 60 | `app.py alarm_idx` | 60 |
| WAT 118°F | `docs/rag_source/` seed PVT doc | 118°F |
| Hot-oil overdue 52 days | Dynamic Gemma doc context | 52 days (randomized ±0–7d, script says "fifty-two days" as representative) |
| Motor eff -10%, vib +14% | `app.py H2 scenario data` | -10%, +14% |
| A-3 optimal Hz 66.0 | `app.py vizier result 2026-06-11` | 66.0 Hz |
| A-5 optimal Hz 59.7 | `app.py vizier result 2026-06-11` | 59.7 Hz |
| Uplift +77.9 bbl/d | `app.py vizier result 2026-06-11` | 77.9 bbl/d |
| Uplift +$369,225/90d | `app.py vizier result 2026-06-11` | $369,225 |
| Gas ceiling 8.0 MMscfd | `app.py _GAS_CEILING_MMSCFD=8.0` | 8.0 |
| Gas consumed 7.9999 | live Vizier result | 7.9999 |
| Winding temp limit 280°F | `app.py _WINDING_TEMP_LIMIT_F=280` | 280°F |

**⚠️ If any `_PAD_ALPHA_WELL_PARAMS`, `_GAS_CEILING_MMSCFD`, or `_PUMP_FLOW_COEFF` values change in `app.py`, the H3 narration MUST be updated before recording.** Update the values in Panel 3, Scenario Replay, and the integrity gate table above.

### GPU Pre-Flight for Recording

If recording H1 live with Gemma L3 extraction active:
1. Run `./scripts/gpu-start.sh` (~10 min before camera rolls — T4 provisioning ~5–6 min, Ollama startup ~1–2 min, model cached on PVC)
2. Confirm `ollama_online: True` via `curl http://gdc-pm.bdau.io/api/mlops/status`
3. Run `./scripts/gpu-stop.sh` immediately after recording ends (~$0.35/hr T4 billing)

For H2 recording: vendor log Document 1 is Gemma-generated per run. Documents 2–3 are static. GPU not required for briefing panels — only for the live document generation in the scenario replay.

For H3 recording: No Gemma dependency. Vizier optimization requires WAN connectivity to GCP. Confirm `vizier_algorithm: GAUSSIAN_PROCESS_BANDIT` in API status before recording.
