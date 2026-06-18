# Google Cloud GDC Edge AI — ESP Operations Video Script (VERSION 4 — OPERATOR-GROUNDED REGISTER)
**Target Persona:** ESP Field Operations, Maintenance & Asset-Longevity leadership (Persona #2), reviewed-friendly for CxO
**Perspective:** Google Cloud — third-party technology advisor
**Distribution:** Public (YouTube). **Must pass Google marketing review:** on-brand, professional, plain-spoken — never folksy, never slangy.
**Target Duration:** ~6:00 finished (spoken ≈ 620 words at ~120 wpm ≈ 5:10 of voice + B-roll/panel dwell)
**Compliance:** 100% sourced to `docs/DEMO_MASTER.md` / `docs/CLAIM_LEDGER.md`. **No exact numbers in the spoken track** — every precise figure is read off the fixed on-screen panel.

---

## REGISTER NOTE (what makes V4 different from V3)
Same facts, same structure, same camera and screen direction. The **only** change is the spoken register:
- **V3** is brand-film/cinematic ("the gap between the signal and the story behind it").
- **V4** is **operator-grounded and direct** — it names the work as an operations leader would frame it (nuisance shut-ins, unnecessary workovers, deferred barrels, runtime through an outage) — but stays **corporate-clean and executive-safe.** No colloquialisms, no "folksy" phrasing, no hype.

> **Brand-safety guardrails honored throughout:** concede what SCADA/APM genuinely do; no straw men; no "SCADA lets the pump die"; advisor-not-autonomous (human approves); claims qualitative so nothing can be falsified on screen.

---

## ░░ SECTION 1 — COLD OPEN (Veo) ░░  *(~35s)*

### 🎬 VEO PROMPT
```
SCENE 1 — "Night Shift in the Field"
Photorealistic. A Permian Basin pad at night, summer, West Texas. A single electric submersible
pump wellhead (christmas tree + VFD control cabinet) under a sodium work-light, a long amber cone
across caliche gravel. Beyond it, a row of identical wellheads fades into the dark to the horizon —
implied scale. Stars above, no wind. Cut to interior: a calm Real-Time Operations Center, one
operator at a wall of SCADA trend screens; a single amber alarm banner is active. On the desk, a
thick well file labeled "WELL A-3 — COMPLETION & PVT HISTORY". 35mm, shallow depth of field.
No text overlays, no synthetic UI. Palette: sodium amber + cold monitor blue.
```

### 🎥 CINEMATOGRAPHY
- **Slow descending aerial push-in** (~8s) toward the lit wellhead — establish scale and isolation.
- **Match-cut** to interior; **slow dolly-in** on the operator, **rack-focus** from the alarm banner to the well file on the desk.
- Measured, professional pacing. Amber exterior vs. blue interior frames the film's thesis: sensors versus documents.

### 🎙️ NARRATION
> *"Across a producing field, a control room watches hundreds of wells at once.*
>
> *When an alarm fires, the sensors tell the operator that a pump is in trouble — but not why. The deciding context usually isn't on the screen. It's in the well file: the shift notes, the lab work, the service history.*
>
> *Closing that gap — automatically, on every well — is what Google Cloud designed GDC to do."*

---

## ░░ SECTION 2 — WHAT GDC IS ░░  *(~45s)*

### 🎬 VEO PROMPT *(optional 6–8s bridge)*
```
SCENE 2 — "On-Premise at the Edge"
Photorealistic macro inside a field equipment skid: a small rack-mounted server with a discreet
"GDC" label, status LEDs steady green, fiber and copper neatly dressed. Behind it, a window onto
the dark pad. Compact, quiet, on-premise. Cool blue key light, one warm practical. No text overlays.
```

### 🎥 CINEMATOGRAPHY
- **Locked-off macro**, gentle **3% push-in** on the green LEDs.
- **Dissolve** to the live *How It Works* tab.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *How It Works* tab)
- Enter on the **three-tier diagram**. Cursor glides top→bottom, ~1.5s dwell per tier:
  **Tier 1 Telemetry Tags → Tier 2 Tag Patterns (local ML) → Tier 3 Document Context (pgvector / AlloyDB Omni).**
- **Digital zoom 1.15× on Tier 3** and hold until "perimeter" is spoken.

### 🎙️ NARRATION
> *"This is Google Distributed Cloud. It runs Google's AI and data stack inside the operator's own perimeter — on their hardware, behind their firewall.*
>
> *It works alongside the existing control system. Sensor tags stream in. Local models score the combined pattern across every channel, continuously. And it adds the layer no control system or monitoring platform has today: search across the operator's own well documents — shift notes, lab reports, workover records, vendor service logs.*
>
> *When a well moves off-pattern, GDC reads the sensors and those documents together, and returns a cited, reviewable diagnosis. On open models. On-premise. In seconds."*

---

## ░░ SECTION 3 — HORIZON 1: DISCERN ░░  *(~75s)*
*One signal. Two opposite causes. The sensor alone can't separate them.*

### 🎬 VEO PROMPT
```
SCENE 3 — "Same Signal, Opposite Causes"
Photorealistic wellbore cutaway, X-ray clarity. LEFT: a healthy ESP intake submerged in fluid;
a pocket of gas drifts into the impeller — gas lock. RIGHT: the dynamic fluid level has dropped
below the intake; the impeller turns in sandy, partial fluid; fine sand settles on the rotating
faces — drawdown. Two diagnostic diagrams brought to life, side by side, mechanically precise.
Cool blue clinical light. No text, no labels.
```

### 🎥 CINEMATOGRAPHY
- **Split-screen** static 3s, then **slow simultaneous push-in** — visually distinct, sensor-identical.
- Only motion: bubbles left, sand right.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 1* tab)
- **Briefing pass:** Slides 1→5. On **Slide 2**, **zoom 1.2× on the four sensor tiles**; cursor across the two that fall (pressure, amps), then the two that hold flat (temperature, vibration). *(Panel prints the values; do not speak them.)*
- Click **▶ Run the Scenario**.
- **Milestone A:** scrub into the pre-detection zone — pressure and amps falling, temperature and vibration holding.
- **Milestone B:** scrub to the **amber GDC-detect marker** → stop; let the three documents reveal; **zoom 1.15× on the GDC Advisor card.**
- **READ THE ON-SCREEN VERDICT → deliver Path A or Path B.**
- **Milestone C:** scrub to the **red SCADA alarm marker**; cursor-gesture the gap.

### 🎙️ NARRATION — shared opening
> *"Well A-3. Intake pressure and motor current fall together. On a standard intake-only string, that one signature has two opposite causes — and they call for opposite actions.*
>
> *Note what stays flat: winding temperature and vibration. They lag this kind of event, so the thermal and vibration trips won't resolve it in the window that matters.*
>
> *The control system protects the pump — it trips on its hard limits, as it should. GDC adds the diagnosis: its model flags the well ahead of that trip, and pulls the documents the sensors can't carry."*

### 🟧 PATH A — on-screen verdict is **GAS LOCK**
> *"The shift note shows the casing annulus fully submerged. The lab shows gas-oil ratio rising. The sand history is clean.*
>
> *The diagnosis is gas lock. The corrective action is to ease pump speed and clear the gas — the well keeps producing, and an ambiguous alarm becomes a confident, low-cost decision."*

### 🟦 PATH B — on-screen verdict is **FLUID DRAWDOWN**
> *"The sonic survey shows the fluid level below the intake. The well's history flags sand production. This is drawdown.*
>
> *Here, easing pump speed would be the wrong action — slowing flow lets sand settle around the impeller. GDC calls for a controlled shut-in and avoids a major workover. Same signal — the opposite, correct action."*

---

## ░░ SECTION 4 — HORIZON 2: CLASSIFY ░░  *(~85s)*
*The right symptom. The wrong cause. An avoidable workover.*

### 🎬 VEO PROMPT
```
SCENE 4 — "The Treatment That Was Missed"
Photorealistic macro time-lapse inside production tubing: warm golden crude rising; over days,
pale crystalline paraffin wax builds along the steel wall, narrowing the bore. Cut to surface:
an ESP wellhead on a cold Permian morning, the chemical-injection port disconnected — no truck,
no hose. In the distance, a hot-oil service truck works a DIFFERENT well, hoses connected, steam
rising. Pale winter palette, low sun, dust. No text overlays.
```

### 🎥 CINEMATOGRAPHY
- Wax growth = **locked macro time-lapse**; let the bore close.
- Surface: **slow lateral dolly** reveals the truck working the wrong well.
- Hold a beat on the disconnected injection port.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 2* tab)
- **Briefing pass:** Slides 1→3. On **Slide 2**, **zoom 1.2× on the sensor tiles** — current rising, efficiency falling, vibration climbing **through the printed high-alarm line**, pressure holding. *(Let the panel figures be read.)*
- Click **▶ Run the Scenario**.
- **Milestone A:** scrub past the missed-treatment point — the slow divergence begins.
- **Milestone B:** scrub to where **GDC retrieves documents** → stop; **zoom 1.15×** and dwell on each: vendor service log → fluid PVT report → prior pull record.
- **Milestone C:** settle on the **green Verdict card** and the two action cards (surface treatment vs. pump pull — AVERTED).

### 🎙️ NARRATION
> *"A second well, a slower problem — weeks of gradual change. Motor current climbs, efficiency drops, and vibration rises through its high-alarm threshold.*
>
> *A best-in-class monitoring platform reads that combination as bearing wear, and recommends the standard response: pull the pump. That is a six-figure intervention.*
>
> *The symptom is real — but the cause is not the bearings. GDC reads three documents the platform does not see. A vendor service log shows the routine paraffin treatment is well overdue; the service unit was committed to another pad. A fluid report confirms this crude deposits wax as it cools. And the last pull record shows the bearings were inspected and normal not long ago.*
>
> *Together, those sources change the diagnosis: a paraffin restriction, not bearing wear. The corrective action is a surface treatment at a fraction of the cost — and the pull is avoided. The platform identified the symptom. GDC identified the cause."*

---

## ░░ SECTION 5 — HORIZON 3: OPTIMIZE ░░  *(~80s)*
*More production within the limits. Safety enforced on-premise.*

### 🎬 VEO PROMPT
```
SCENE 5 — "One Pad, One Gas Limit"
Photorealistic aerial of Pad Alpha at golden hour: six identical ESP wellheads in two rows of
three, gathering lines converging to a manifold; a midstream gas-compressor station with a
metering skid beyond. Push toward a flow-computer readout near its limit. Cut to a Starlink dish
on a field-trailer roof, rain-beaded, distant lightning; inside, a network indicator shifts
green→amber while the on-prem server LEDs stay steady green and the setpoints hold. Warm field
gold vs. cold storm blue. No text overlays.
```

### 🎥 CINEMATOGRAPHY
- **High aerial quarter-arc orbit** — fleet, not one well.
- **Push-in** on the metering readout near its ceiling.
- Storm beat: **handheld micro-shake** outside, **locked-off steady** on the green LEDs.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 3* tab)
- **Briefing pass:** Slides 1→3. On **Slide 1**, **zoom on the GOR table** — cursor-tap the two lowest-gas wells, then the gassiest. On **Slide 2**, point to the **printed thermal-limit line**.
- Click **▶ Run the Optimization**.
- **Milestone A:** trial dots populate the chart — searching, then converging.
- **Milestone B:** **zoom 1.15× on the per-well setpoint table** as it locks (lowest-gas wells highest; gassiest backs off).
- **Milestone C:** settle on the **uplift card** and **edge-safety callout**; cursor-circle the gas figure to show the ceiling is respected.

### 🎙️ NARRATION
> *"The third case is the whole pad. These wells share one gas-handling limit set by the midstream contract. Every barrel brings associated gas — but some wells bring far more than others. Throttle them all equally and the field leaves production on the table on its most gas-efficient wells.*
>
> *So the work is divided: the cloud searches, the edge enforces. Vertex AI Vizier explores the setpoint combinations, but only setpoints and scores leave the site. Every candidate is checked on-premise against each motor's temperature limit before it is allowed to count.*
>
> *The result is on the panel: the lowest-gas wells run at full speed, the gassiest is throttled back — more daily production, real quarterly value, with gas held just under the ceiling.*
>
> *And if the network link drops during the search, the temperature limit is already enforced locally. Safety never depends on the connection."*

---

## ░░ SECTION 6 — CLOSE ░░  *(~35s)*

### 🎬 VEO PROMPT *(bookend)*
```
SCENE 6 — "First Light"
Photorealistic. The same Permian pad as Scene 1, now at dawn. Work-lights off; the wellheads
pump steadily against a pale gold sky. The operator steps out of the RTOC trailer — the shift is
over, the wells are running. Warm sunrise palette, resolved. No text overlays.
```

### 🎥 CINEMATOGRAPHY
- **Slow crane-up** from the operator to a **wide of the running pad at sunrise.**
- Hold the wide; gentle fade.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Operations* / *Financials*)
- Toggle **Operations** then **Financials**; cursor-rest on the cumulative-savings figure. Calm, settled framing.

### 🎙️ NARRATION
> *"Three problems an ESP operation faces every day: an ambiguous alarm, a misread cause, and production left within the limits.*
>
> *One platform addresses all three — every diagnosis cited, every action reviewed by the operator, and all of it inside the operator's own perimeter.*
>
> *Lower lifting cost. Longer asset life. Higher runtime. That is GDC, from Google Cloud — where the data already lives."*

---

## APPENDIX A — "LET THE PANEL SAY IT" CHEAT SHEET
When a precise figure matters, **frame it, don't speak it.** Zoom/dwell so the audience reads the fixed panel value while the voice gives the meaning.

| Moment | Voice says (qualitative) | Panel shows (fixed, on screen) |
|---|---|---|
| H1 telemetry split | "pressure and current fall; temp and vibration hold flat" | live tiles + lead/lag note |
| H1 lead time | "ahead of that trip" | amber marker vs. red marker |
| H2 vibration | "through its high-alarm threshold" | printed high-alarm line (4.0 mm/s) |
| H2 overdue PM | "well overdue; the unit was on another pad" | vendor-log doc (52 days) |
| H2 cost contrast | "a fraction of the cost … pull avoided" | action cards (surface vs pull AVERTED) |
| H3 limit | "one gas-handling limit" | gas card (8.0 MMscfd) |
| H3 setpoints | "lowest-gas wells full speed; gassiest throttled" | per-well Hz table (66.0 / 59.7 …) |
| H3 uplift | "more daily production, real quarterly value" | uplift card (+77.9 bbl/d · revenue) |
| H3 safety | "against each motor's temperature limit" | thermal-limit line (280°F) |

---

## APPENDIX B — WHAT'S FIXED vs. RANDOM
- **FIXED (safe to show; identical every record):** everything printed in the **briefing slides** — H1 nominal Hz / PSI floor / thermal limit; H2 WAT / interval / overdue days / high-alarm / current & efficiency deltas; H3 gas ceiling / thermal limit / all setpoints / uplift / barrels.
- **RANDOM (never speak; trend only):** the **replay scrubber tiles** (PIP/Amps/Temp/Vib/health) re-seed each run; the **GDC-detect and SCADA-alarm marker positions** shift each run; **H1 verdict is 50/50 Gas Lock vs Drawdown** (use the A/B branch).

> Because the voice never states a value, no run can desync the narration — and every precise figure on screen is the fixed, correct one.

---

## APPENDIX C — RUNTIME LEDGER
| # | Section | Words | Spoken | Notes |
|---|---|---|---|---|
| 1 | Cold Open | ~60 | ~0:30 | + ~10s B-roll dwell |
| 2 | What GDC Is | ~95 | ~0:48 | tier glide |
| 3 | H1 Discern | ~150 (shared + one branch) | ~1:15 | A/B branch, one read |
| 4 | H2 Classify | ~140 | ~1:10 | doc reveals |
| 5 | H3 Optimize | ~130 | ~1:05 | Vizier run animates |
| 6 | Close | ~70 | ~0:35 | crane-up |
| | **TOTAL spoken** | **≈620** | **≈5:10** | **finished ≈6:00** with B-roll/panel/run dwell |

> To trim toward a hard 6:00 if B-roll runs long: drop the Section-2 Veo bridge first, then ~10 words from H2.

---

## APPENDIX D — BRAND / MARKETING-REVIEW CHECKLIST (pre-publish)
- [ ] **Third-party Google Cloud voice** — describes the operator's world; never claims to *be* the operator.
- [ ] **No exact numbers spoken** — all precise figures read off the panel.
- [ ] **SCADA/APM conceded honestly** — "protects the pump … as it should"; "best-in-class platform reads it as bearing wear." No straw men.
- [ ] **Advisor, not autopilot** — "reviewed by the operator" stated in the close.
- [ ] **Sovereignty** — "inside the operator's own perimeter," "on open models," "data already lives" — consistent with brand language.
- [ ] **Tone** — plain and direct, but corporate-clean: no slang, no idioms, no "folksy" phrasing; safe for a CxO viewer.
- [ ] **Product names correct** — "Google Distributed Cloud," "Vertex AI Vizier," "AlloyDB Omni," "pgvector."
