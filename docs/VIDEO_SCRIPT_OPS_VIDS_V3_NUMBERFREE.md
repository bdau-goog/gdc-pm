# Google Cloud GDC Edge AI — ESP Operations Video Script (VERSION 3 — NUMBER-FREE NARRATION)
**Target Persona:** ESP Field Operations, Maintenance & Asset-Longevity Managers (Persona #2)
**Perspective:** Google Cloud — third-party technology advisor explaining GDC's value to upstream operators
**Target Duration:** 5:30–6:00
**Compliance:** 100% sourced to `docs/DEMO_MASTER.md` / `docs/CLAIM_LEDGER.md`. **The spoken track contains NO exact numbers** — every precise figure lives on the on-screen panel, which is fixed and correct.

---

## THE GOVERNING PRINCIPLE OF THIS VERSION
**The screen carries the numbers. The voice carries the meaning.**

The voiceover never speaks a specific value (no Hz, no °F, no dollar figure, no day count). It speaks only **direction and significance** — "pressure and amps slide together," "the gassiest well backs off," "a surface truck-roll instead of a six-figure pull." This makes the narration **immune** to the app's run-to-run randomness: nothing you say can ever contradict a number that moved on screen.

### Why this is safe — what is fixed vs. random in the live app
| Surface | Behavior | Use in narration |
|---|---|---|
| **Briefing panels / slides** (static HTML) | **Fixed** — same every record (e.g., 118°F WAT, 8.0 MMscfd ceiling, 280°F limit, 66.0/59.7 Hz, +77.9 bbl/d) | Let them be **read on screen**; do not speak them. Zoom the camera so the viewer reads them. |
| **Replay scrubber tiles** (PIP / Amps / Temp / Vib / health) | **Randomized per run** — seeds & curve shape change; marker positions shift | **Never speak.** Describe trend only ("falling," "holding flat," "crossing the alarm line"). |
| **H1 verdict** (Gas Lock vs Drawdown) | **Random 50/50** each run | Use the **A/B branch** — read the one on screen. |

> **Production tip:** Because the numbers are on the panels, **let the camera do the quoting**. When a precise figure matters, *zoom and dwell* on the panel tile so the audience reads it themselves while your voice gives the "so what."

---

## ░░ SECTION 1 — COLD OPEN (Veo) ░░  *(~35s)*

### 🎬 VEO PROMPT
```
SCENE 1 — "2 A.M., Two Hundred Wells"
Photorealistic. A Permian Basin pad at night, summer, West Texas. A single electric
submersible pump wellhead (christmas tree + VFD control cabinet) under a sodium work-light,
a long amber cone across caliche gravel. Beyond it, a row of identical wellheads fades into
the dark to the horizon — implied scale. Stars above, no wind. Cut to interior: a dim
Real-Time Operations Center, one operator alone, face lit blue-white by a wall of SCADA trend
screens; a single amber alarm banner pulses. On the desk, a thick manila well file labeled
"WELL A-3 — COMPLETION & PVT HISTORY", coffee gone cold. 35mm, shallow depth of field.
No text overlays, no synthetic UI. Palette: sodium amber + cold monitor blue.
```

### 🎥 CINEMATOGRAPHY
- **Slow descending aerial push-in** (~8s) toward the lone lit wellhead — isolation + scale.
- **Hard match-cut** to interior; **slow dolly-in** on the operator's back, **rack-focus** from the blurred alarm banner to the sharp manila folder. The folder is the thesis.
- Quiet, unhurried. Amber exterior vs. blue interior = "sensors vs. documents," stated visually before a word.

### 🎙️ NARRATION
> *"Two in the morning. One operator. A field full of wells.*
>
> *An alarm fires. The sensors say a pump is struggling — but not why. The answer isn't on the screen. It's in the file on the desk.*
>
> *That gap — between the signal and the story behind it — is what Google Cloud built GDC to close."*

---

## ░░ SECTION 2 — WHAT GDC IS ░░  *(~45s)*

### 🎬 VEO PROMPT *(optional 6–8s bridge)*
```
SCENE 2 — "The Stack at the Edge"
Photorealistic macro inside a field equipment skid: a small rack-mounted server, discreet
"GDC" label, status LEDs breathing steady green, fiber and copper neatly dressed. Behind it,
a window onto the dark pad. Small, quiet, on-premise — a box at the edge of the field.
Cool blue key light, one warm practical. No text overlays.
```

### 🎥 CINEMATOGRAPHY
- **Locked-off macro**, gentle **3% push-in** on the green LEDs — "alive, local, always on."
- **Dissolve** to the live *How It Works* tab.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *How It Works* tab)
- Enter scrolled to the **three-tier diagram**. Cursor glides top→bottom, dwell ~1.5s per tier:
  **Tier 1 Telemetry Tags → Tier 2 Tag Patterns (local ML) → Tier 3 Document Context (pgvector / AlloyDB Omni).**
- **Digital zoom 1.15× on Tier 3** and hold — the moat lingers longest. Don't click away until "perimeter" is spoken.

### 🎙️ NARRATION
> *"This is Google Distributed Cloud. It puts Google's AI and data stack inside your operations-technology perimeter — your firewall, your hardware, your control.*
>
> *Three layers, all on-premise. Your sensor tags stream in. Local models score the pattern across every channel, continuously. And the layer no SCADA or monitoring platform has — semantic search across your own well files: shift notes, lab reports, workover histories, vendor logs.*
>
> *When something moves, GDC fuses the live sensors with those documents and returns a cited, auditable diagnosis. On open-weight models. Inside your perimeter. In seconds."*

---

## ░░ SECTION 3 — HORIZON 1: DISCERN ░░  *(~80s)*
*One signal. Two opposite causes. The sensor can't tell you which.*

### 🎬 VEO PROMPT
```
SCENE 3 — "Same Signal, Opposite Fates"
Photorealistic wellbore cutaway, X-ray clarity. LEFT: a healthy ESP intake submerged in fluid;
a pocket of gas bubbles drifts into the impeller — gas lock. RIGHT: the dynamic fluid level
has dropped below the intake; the impeller spins in sandy, partial fluid; fine sand grains
settle on the rotating faces — drawdown. Two diagnostic diagrams brought to life, side by side,
mechanically precise. Cool blue clinical light. No text, no labels.
```

### 🎥 CINEMATOGRAPHY
- **Split-screen** static 3s, then **slow simultaneous push-in** on both halves — visually distinct, sensor-identical.
- Only motion: **bubbles left, sand right.** Everything else still.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 1* tab)
- **Briefing pass:** Slides 1→5. On **Slide 2 (Ambiguous Telemetry)**, **zoom 1.2× on the four sensor tiles**; trace the cursor across the two that fall (pressure, amps) then the two that hold flat (temperature, vibration). *(Let the panel's printed values be read; don't speak them.)*
- Click **▶ Run the Scenario**.
- **Milestone A:** scrub into the pre-detection zone — narrate over the falling pressure/amps while temp/vib hold.
- **Milestone B (the beat):** scrub until the **amber GDC-detect marker** appears → **stop**; let the three documents reveal; **zoom 1.15× on the GDC Advisor card** as each citation lands.
- **READ THE ON-SCREEN VERDICT → deliver Path A or Path B.**
- **Milestone C:** scrub to the **red SCADA alarm marker**; cursor-gesture the **gap** between amber and red.

### 🎙️ NARRATION — shared opening
> *"Well A-3. Intake pressure and motor amps slide down together. On a standard intake-only string, that exact signature has two opposite causes.*
>
> *Watch what doesn't move — winding temperature and vibration hold near-nominal. They're lagging indicators; the thermal and vibration trips won't save you here, not in time.*
>
> *GDC's local model crosses its confidence line first — its amber marker fires well before SCADA's hard-limit alarm. And in that lead, it pulls the documents the sensors can't see."*

### 🟧 PATH A — on-screen verdict is **GAS LOCK**
> *"The shift note: the casing annulus is fully submerged. The lab: gas-oil ratio rising. The sand history: clean.*
>
> *Verdict — gas lock. The fix is to ease the pump speed and clear the gas. The well never stops producing. An ambiguous alarm becomes a confident, low-cost call."*

### 🟦 PATH B — on-screen verdict is **FLUID DRAWDOWN**
> *"The sonic survey: the fluid level has fallen below the intake. The wellbore history: a known sand producer. This well is drawing down.*
>
> *Verdict — drawdown, and here easing the pump is exactly the wrong move; slow the fluid and sand compacts around the impeller. GDC calls for a shut-in, and spares the operator a major workover. Same signal — opposite, correct action."*

---

## ░░ SECTION 4 — HORIZON 2: CLASSIFY ░░  *(~90s)*
*The right symptom. The wrong cause. A very expensive fix.*

### 🎬 VEO PROMPT
```
SCENE 4 — "The Truck That Never Came"
Photorealistic macro time-lapse inside production tubing: warm golden crude rising; over days,
pale crystalline paraffin wax creeps inward along the steel wall, narrowing the bore. Cut to
surface: an ESP wellhead on a cold Permian morning, a disconnected chemical-injection port —
no truck, no hose, nothing flowing. In the distance, a hot-oil service truck works a DIFFERENT
well, hoses connected, steam rising. The absence is the story. Pale winter palette, low sun, dust.
```

### 🎥 CINEMATOGRAPHY
- Wax growth = **locked macro time-lapse**, no camera move; let the bore visibly close.
- Surface: **slow lateral dolly** reveals the truck working the *wrong* well — the pull-away literalizes "it went somewhere else."
- Hold an extra beat on the **empty injection port**.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 2* tab)
- **Briefing pass:** Slides 1→3. On **Slide 2**, **zoom 1.2× on the sensor tiles** — cursor-trace amps rising, efficiency falling, vibration climbing **through the printed ISA High line**, pressure holding. *(Panel prints the exact figures; let them be read.)*
- Click **▶ Run the Scenario**.
- **Milestone A:** scrub past the missed-treatment point — narrate the slow divergence beginning.
- **Milestone B:** scrub to where **GDC triggers retrieval** → **stop**; as the **three documents reveal in sequence**, **zoom 1.15×** and dwell: vendor service log → fluid PVT report → prior pull record.
- **Milestone C:** settle on the **green Verdict card** and the two action cards (**hot-oil truck-roll** vs **pump pull — AVERTED**). Let it hold.

### 🎙️ NARRATION
> *"A different problem, weeks in the making. The pump draws more current, runs less efficiently, and vibrates harder — climbing right through its high-vibration alarm.*
>
> *To a best-in-class monitoring platform, that pattern is textbook bearing wear. The recommendation: pull the pump — a six-figure intervention.*
>
> *But the bearings aren't the cause. GDC reads three documents the platform can't. A vendor service log shows the routine paraffin treatment is badly overdue — the truck went to another pad. A fluid report shows this crude lays down wax as it cools. And the last pull record shows the bearings were inspected healthy not long ago.*
>
> *Fused together, the verdict flips: paraffin restriction, not bearing wear. Send a hot-oil truck at surface — a fraction of the cost — and the pull is averted entirely. The platform found the symptom. GDC found the cause."*

---

## ░░ SECTION 5 — HORIZON 3: OPTIMIZE ░░  *(~85s)*
*Maximum production. No motor burned. The edge holds the line.*

### 🎬 VEO PROMPT
```
SCENE 5 — "Six Wells, One Budget, One Storm"
Photorealistic aerial of Pad Alpha at golden hour: six identical ESP wellheads in two rows of
three, gathering lines converging to a manifold; a midstream gas-compressor station with a
metering skid beyond. Push toward a flow-computer readout glowing near a limit. Cut to a
Starlink dish on a field-trailer roof, rain-beaded, lightning in the distance; inside, a network
indicator flips green→amber, yet the on-prem server LEDs stay steady green and the setpoints
hold. Warm field gold vs. cold storm blue. No text overlays.
```

### 🎥 CINEMATOGRAPHY
- **High aerial quarter-arc orbit** of the pad — "fleet, not one well."
- **Push-in** on the metering-skid number nearing its ceiling = tension.
- Storm beat: **handheld micro-shake** on the exterior, **locked-off steady** on the green LEDs — the camera says *"cloud wobbles, edge is rock-steady."*

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 3* tab)
- **Briefing pass:** Slides 1→3. On **Slide 1**, **zoom on the GOR table** — cursor-tap the two lowest-gas wells, then the gassiest, to show the spread. On **Slide 2**, point at the **printed thermal limit line**.
- Click **▶ Run the Optimization**.
- **Milestone A:** let the **trial dots populate** the Pareto chart — narrate the search exploring, then converging.
- **Milestone B:** **zoom 1.15× on the per-well setpoint table** as it locks (lowest-gas wells run highest; gassiest backs off). *(Panel prints exact Hz; let it be read.)*
- **Milestone C:** settle on the **uplift card** and **edge-safety callout**; cursor-circle the gas figure to show the ceiling is respected.

### 🎙️ NARRATION
> *"Now run the whole pad. These wells share a single gas-takeaway ceiling. Every barrel carries gas — but some wells carry far more than others. Throttle them all equally and you strand production on your most gas-efficient wells.*
>
> *So the cloud searches and the edge enforces. Vertex AI Vizier explores the setpoint space — but only setpoints and scores ever leave the site. Every candidate is checked on-premise against each motor's winding-temperature limit before it counts.*
>
> *The result writes itself on the panel: the lowest-gas wells run wide open; the gassiest backs off. More barrels a day, real dollars a quarter — with gas pinned just under the ceiling.*
>
> *And if a storm takes your satellite link mid-search? The edge already holds the safety line. The motor limit never depended on the cloud."*

---

## ░░ SECTION 6 — CLOSE ░░  *(~35s)*

### 🎬 VEO PROMPT *(bookend)*
```
SCENE 6 — "First Light"
Photorealistic. The same Permian pad as Scene 1, now at dawn. Work-lights off; the wellheads
pump steadily against a pale gold sky. The same operator walks out of the RTOC trailer with a
fresh coffee, calm — the night is over, the wells are running. Warm sunrise palette, resolved.
No text overlays.
```

### 🎥 CINEMATOGRAPHY
- **Slow crane-up** from the operator to a **wide of the running pad at sunrise.**
- End on a **held wide**, let it breathe, gentle fade.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Operations* / *Financials*)
- Briefly toggle **Operations** then **Financials**; cursor-rest on the cumulative-savings figure. No zoom; calm, settled framing to match the dawn.

### 🎙️ NARRATION
> *"Diagnose the ambiguous. Catch the wrong fix before it's ordered. Push every barrel that's safe to push.*
>
> *Three problems, one sovereign stack — every verdict cited, every action approved by your engineer, every byte inside your perimeter.*
>
> *Lower lifting cost. Longer asset life. Maximum runtime. That's GDC, from Google Cloud — where your data already lives."*

---

## APPENDIX A — "LET THE PANEL SAY IT" CHEAT SHEET
When a precise figure matters, **do not speak it — frame it.** Zoom/dwell so the audience reads the fixed panel value while your voice gives the meaning.

| Moment | Voice says (qualitative) | Panel shows (fixed, on screen) |
|---|---|---|
| H1 telemetry split | "pressure and amps slide; temp and vib hold flat" | the live tiles + the lead/lag note |
| H1 lead time | "well before SCADA's hard-limit alarm" | amber marker vs. red marker on the chart |
| H2 vibration | "climbing through its high-vibration alarm" | the printed ISA High line (4.0 mm/s) |
| H2 overdue PM | "badly overdue — the truck went to another pad" | the vendor-log doc (52 days) |
| H2 cost contrast | "a fraction of the cost of a pull" | action cards (hot-oil vs pull AVERTED) |
| H3 ceiling | "a single gas-takeaway ceiling" | the gas card (8.0 MMscfd) |
| H3 setpoints | "lowest-gas wells run wide open; gassiest backs off" | per-well Hz table (66.0 / 59.7 …) |
| H3 uplift | "more barrels a day, real dollars a quarter" | uplift card (+77.9 bbl/d · revenue) |
| H3 safety | "checked against each motor's winding limit" | the thermal-limit line (280°F) |

---

## APPENDIX B — WHAT'S FIXED vs. RANDOM (so you trust the cheat sheet)
- **FIXED (safe to show on panel, identical every record):** everything printed in the **briefing slides** — H1: nominal Hz, PSI floor, thermal limit; H2: WAT, interval, overdue days, ISA High, amps/efficiency deltas; H3: gas ceiling, thermal limit, all setpoints, uplift, barrels.
- **RANDOM (never speak; describe trend only):** the **replay scrubber tiles** (PIP/Amps/Temp/Vib/health) re-seed each run; the **GDC-detect and SCADA-alarm marker positions** shift each run; **H1 verdict is 50/50 Gas Lock vs Drawdown** (use the A/B branch).

> Result: because the voice never speaks a value, **no run can ever desync your narration** — and every precise number the audience sees is the fixed, correct one on the panel.

---

## APPENDIX C — VEO PROMPTING DISCIPLINE
- Always include **"photorealistic, no text overlays, no synthetic UI."** Veo invents labels otherwise.
- Always state **time of day + palette** (night sodium/blue, winter pale, golden hour, dawn).
- Use **correct equipment nouns** (christmas tree, VFD cabinet, impeller, intake, tubing wall, metering skid, hot-oil truck) — far more accurate renders.
- For **"absence" shots** (truck that didn't come, link that dropped), shoot the **contrast** (truck at a *different* well; LEDs steady *while* the indicator goes amber). Generative video can't show a negative directly.
- One camera move per shot: *slow push-in, dolly, crane-up, rack focus, locked-off macro, quarter-arc aerial orbit.*
