# Google Cloud GDC Edge AI — ESP Operations Video Script (VERSION 2 — for comparison)
**Target Persona:** ESP Field Operations, Maintenance & Asset-Longevity Managers (Persona #2)
**Perspective:** Google Cloud — third-party technology advisor explaining GDC's value to upstream operators
**Target Duration:** 5:30–6:00 (spoken word budget ≈ 660 words at a deliberate 120 WPM, with pauses for figures to land)
**Compliance:** 100% sourced to `docs/DEMO_MASTER.md`, `docs/CLAIM_LEDGER.md`, and live code values. No claim ships without a SURVIVES ledger row.

> **This is an ALTERNATIVE narrative to `VIDEO_SCRIPT_OPS_VIDS.md`.** Same facts, same physics, same locked numbers — but a different storytelling spine ("follow one engineer, one night, one fleet"), a tighter VO, and full cinematography + screen-choreography direction. Read both and pick the one that lands.

---

## HOW THIS SCRIPT IS ORGANIZED
Each section gives you four synchronized layers:
1. **🎬 VEO PROMPT** — the generative-video text prompt (photoreal, no text overlays).
2. **🎥 CINEMATOGRAPHY** — explicit camera language for the Veo B-roll (lens, move, speed, palette).
3. **🖱️ SCREEN CHOREOGRAPHY** — how to drive the *live UI* capture: cursor path, zoom, pan, highlight, dwell. (This is "digital cinematography" for the screen recording.)
4. **🎙️ NARRATION** — the exact voiceover. Branch markers included where the app is random.

### Resiliency rules (because the demo is live & partly random)
- **H1 is 50/50 random** between **Gas Lock** and **Fluid Drawdown** (`Math.random()` in `app.js`). Two narration branches are provided — read the one matching the on-screen verdict.
- **No hard timestamps.** Cues are tied to **visual events** ("when the amber marker fires"), so any scrub speed stays in sync.
- **Numbers are spoken as defensible ranges** where the backend randomizes baselines; exact locked values (66.0 Hz, 59.7 Hz, 280°F, 8.0 MMscfd, +77.9 bbl/d, $369,225) are spoken precisely because they are static.

---

## ░░ SECTION 1 — COLD OPEN (Veo) ░░  *(~35s · ~70 words)*

### 🎬 VEO PROMPT
```
SCENE 1 — "2 A.M., Two Hundred Wells"
Photorealistic. A Permian Basin pad at night, summer, West Texas. A single electric
submersible pump wellhead (christmas tree + VFD control cabinet) stands under a sodium
work-light, casting a long amber cone across caliche gravel. Beyond it, a row of identical
wellheads fades into the dark to the horizon — implied scale, dozens of wells. Stars above.
No wind. Then: interior, a dim Real-Time Operations Center. One operator, alone, face lit
blue-white by a wall of SCADA trend screens; a single amber alarm banner pulses on one panel.
On the desk beside the keyboard, a thick manila well file labeled "WELL A-3 — COMPLETION &
PVT HISTORY", a coffee gone cold. Photorealistic, cinematic, 35mm, shallow depth of field.
No text overlays. No synthetic UI. Palette: sodium amber + cold monitor blue.
```

### 🎥 CINEMATOGRAPHY
- Open on a **slow 8-second aerial push-in** (drone, descending) toward the lone lit wellhead — establishes isolation and scale.
- **Hard match-cut** to interior: a **slow dolly-in** on the operator's back, rack-focus from the blurred alarm banner to the sharp manila folder on the desk (the folder is the thesis of the whole film).
- Keep it **quiet and unhurried** — no whip-pans. Let the silence imply the stakes.
- Palette discipline: amber exterior, blue interior. The two color worlds = "sensors vs. documents," set up visually before a word is said.

### 🎙️ NARRATION
> *"Two in the morning. One operator. Two hundred wells.*
>
> *An alarm fires on Well A-3. The sensors say the pump is struggling — but not why. The answer isn't on the screen. It's in that file on the desk.*
>
> *This is the gap that costs the industry millions. And it's the gap Google Cloud built GDC to close."*

---

## ░░ SECTION 2 — WHAT GDC IS ░░  *(~45s · ~95 words)*

### 🎬 VEO PROMPT *(optional 6–8s bridge B-roll; can also stay on the live UI)*
```
SCENE 2 — "The Stack at the Edge"
Photorealistic close-up inside a field equipment skid: a small rack-mounted server with a
discreet "GDC" label, status LEDs breathing steady green, fiber and copper neatly dressed.
Behind it, a window onto the dark pad. The machine is small, quiet, on-premise. No data center,
no cloud — just a box at the edge of the field. Cool blue key light, single warm practical.
No text overlays.
```

### 🎥 CINEMATOGRAPHY
- A **single locked-off macro shot** with a **gentle 3% push-in** on the green LEDs — "alive, local, always on."
- Then **dissolve to the live screen capture** of the *How It Works* tab.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *How It Works* tab)
- Enter the tab already scrolled to the **three-tier diagram**.
- **Cursor choreography:** glide top-to-bottom, dwell ~1.5s on each tier as it's named:
  1. **Tier 1 — Telemetry Tags** (SCADA real-time stream)
  2. **Tier 2 — Tag Patterns** (local XGBoost scoring on edge CPU)
  3. **Tier 3 — Document Context** (pgvector RAG over AlloyDB Omni)
- **Zoom (digital): 1.15× ease-in on Tier 3** and hold — this is the moat; let it linger longest.
- Do **not** click away until the word "perimeter" is spoken.

### 🎙️ NARRATION
> *"This is Google Distributed Cloud. It puts Google's AI and data stack inside your operations-technology perimeter — your firewall, your hardware, your control.*
>
> *Three layers, all on-premise. Your SCADA tags stream in. Local machine-learning models score the multivariate pattern continuously. And the layer no SCADA or monitoring platform has — semantic search across your private well files: shift notes, lab reports, workover histories, vendor logs.*
>
> *When something moves, GDC fuses live sensors with those documents — and returns a cited, auditable diagnosis. On open-weight models. Inside your perimeter. In seconds."*

---

## ░░ SECTION 3 — HORIZON 1: DISCERN ░░  *(~80s · ~165 words)*
*One signal. Two opposite causes. The sensor can't tell you which.*

### 🎬 VEO PROMPT
```
SCENE 3 — "Same Four Numbers, Opposite Fates"
Photorealistic cutaway of a steel wellbore, X-ray clarity. LEFT: a healthy ESP pump intake
submerged in fluid; a pocket of gas bubbles drifts into the impeller — gas lock. RIGHT: the
dynamic fluid level has dropped below the intake; the impeller spins in sandy, partial fluid;
fine sand grains settle against the rotating faces — drawdown. Two diagnostic diagrams brought
to life, side by side, mechanically precise. Cool blue clinical light. No text, no labels.
```

### 🎥 CINEMATOGRAPHY
- **Split-screen** held static for 3s, then a **slow simultaneous push-in** on both halves — the audience should feel the two failures are *visually distinct but sensor-identical*.
- Subtle **particle motion** (bubbles left, sand right) is the only movement — everything else still.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 1* tab)
- **Briefing pass:** advance Slides 1→5. On **Slide 2 (Ambiguous Telemetry)**, **zoom 1.2× onto the four sensor tiles** and trace the cursor across PIP and Amps (falling) then Temp and Vib (flat) — physically point out the lead/lag split.
- Click **▶ Run the Scenario**.
- **Milestone A:** scrub slowly into the pre-detection zone — narrate over the declining PIP/Amps while Temp/Vib hold flat.
- **Milestone B (the beat):** scrub until the **amber GDC-detect marker** appears; **stop**. Let the three RAG documents reveal. **Zoom 1.15× on the GDC Advisor card** as each citation lands.
- **READ THE VERDICT ON SCREEN → choose Path A or Path B below.**
- **Milestone C:** scrub to the **red SCADA alarm marker**; gesture the **gap** between amber and red with the cursor as you say "four to nine minutes."

### 🎙️ NARRATION — shared opening
> *"Well A-3. Intake pressure and motor amps slide down together. On a standard intake-only string, that exact signature has two opposite causes.*
>
> *Watch what doesn't move: winding temperature and vibration stay near-nominal — they're lagging indicators. SCADA's thermal and vibration trips won't help you here, not in time.*
>
> *GDC's local model crosses its confidence threshold first — its amber marker fires four to nine minutes before SCADA's hard-limit alarm. And in that window, it pulls three documents the sensors can't see."*

### 🟧 PATH A — on-screen verdict is **GAS LOCK**
> *"The shift note says the casing annulus is fully submerged. The lab shows gas-oil ratio rising. The sand history is clean.*
>
> *Verdict: gas lock. The fix is to trim the VFD speed and clear the gas — a couple thousand dollars, and the well never stops producing. GDC turned an ambiguous 2 A.M. alarm into a confident, low-cost call."*

### 🟦 PATH B — on-screen verdict is **FLUID DRAWDOWN**
> *"The sonic survey says the fluid level has fallen below the intake. The wellbore history flags sand. This well is drawing down.*
>
> *Verdict: drawdown — and here, trimming the pump is exactly wrong. Slow the fluid and sand compacts around the impeller. GDC calls for an immediate shut-in, protecting the operator from a hundred-and-fifty-thousand-dollar seizure. Same signal — opposite, correct action."*

---

## ░░ SECTION 4 — HORIZON 2: CLASSIFY ░░  *(~90s · ~185 words)*
*The right symptom. The wrong cause. A very expensive fix.*

### 🎬 VEO PROMPT
```
SCENE 4 — "The Truck That Never Came"
Photorealistic. Macro time-lapse inside production tubing: warm golden crude rising; over days,
pale crystalline paraffin wax creeps inward along the steel wall, narrowing the bore. Cut to
surface: an ESP wellhead on a cold Permian morning, a disconnected chemical-injection port —
no hot-oil truck, no hose, nothing flowing. In the distance, a hot-oil service truck works a
DIFFERENT well, hoses connected, steam rising. The absence is the story. Pale winter palette,
long low sun, dust.
```

### 🎥 CINEMATOGRAPHY
- The wax growth is a **locked macro time-lapse** — no camera move, let the bore visibly close.
- At surface, a **slow lateral truck-left dolly** reveals the working truck at the wrong well — the **pull-away** literalizes "the truck went somewhere else."
- Hold one extra beat on the **empty injection port**.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 2* tab)
- **Briefing pass:** Slides 1→3. On **Slide 2**, **zoom 1.2× on the sensor tiles**: amps **+14%**, efficiency **−10%**, vibration climbing **~1.0 → 4.5 mm/s** (call out the **4.0 mm/s ISA High** line), PIP stable/slightly rising. Trace each with the cursor.
- Click **▶ Run the Scenario**.
- **Milestone A:** scrub **past Day 90** — narrate the missed treatment; point at the gentle divergence beginning ~Day 106.
- **Milestone B:** scrub to where **GDC triggers retrieval**; **stop**. As the **three documents reveal in sequence**, **zoom 1.15×** and dwell on each: vendor log (**52 days overdue**), PVT (**WAT 118°F**), prior pull (**bearings normal, 18 months**).
- **Milestone C:** settle on the **green Verdict card** + the two action cards (**hot-oil $3k–$6k** vs **pump pull $70k–$100k AVERTED**). Let it hold.

### 🎙️ NARRATION
> *"Different problem. Over three weeks, A-3 degrades slowly — amps up about fourteen percent, efficiency down about ten, vibration climbing from one to four-and-a-half millimeters per second, right through the ISA High alarm at four-point-zero.*
>
> *To a best-in-class monitoring platform, that pattern is textbook bearing wear. The recommendation: pull the pump. Seventy to a hundred thousand dollars.*
>
> *But the bearings aren't the cause. GDC reads three documents the platform can't. A vendor service log: the ninety-day paraffin treatment is fifty-two days overdue — the truck went to another pad. A fluid report: this crude lays down wax below one-eighteen Fahrenheit. And the last pull record: bearings inspected normal, eighteen months ago.*
>
> *Fused together, the verdict flips: paraffin restriction, not bearing wear. Send a hot-oil truck — a few thousand dollars at surface — and the pull is averted entirely. The platform found the symptom. GDC found the cause."*

---

## ░░ SECTION 5 — HORIZON 3: OPTIMIZE ░░  *(~85s · ~175 words)*
*Maximum production. No motor burned. The edge holds the line.*

### 🎬 VEO PROMPT
```
SCENE 5 — "Six Wells, One Budget, One Storm"
Photorealistic aerial of Pad Alpha at golden hour: six identical ESP wellheads, two rows of
three, gathering lines converging to a manifold; a midstream gas-compressor station with a
metering skid sits beyond. Push toward a flow-computer readout glowing near a limit. Then
cut to a Starlink dish on a field-trailer roof, rain-beaded, lightning in the distance; inside,
a network indicator flips green→amber, yet the on-prem server LEDs stay steady green and the
setpoints hold. Warm field gold vs. cold storm blue. No text overlays.
```

### 🎥 CINEMATOGRAPHY
- Open on a **smooth high aerial orbit** (quarter-arc) around the pad — communicates "fleet, not one well."
- **Push-in** on the metering skid number nearing its ceiling = tension.
- For the storm beat, **handheld micro-shake** on the exterior, but **locked-off steady** on the green server LEDs — the camera language itself says *"cloud wobbles, edge is rock-steady."*

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Horizon 3* tab)
- **Briefing pass:** Slides 1→3. On **Slide 1**, **zoom on the GOR table** — cursor-tap A-3/A-6 (**450**) and A-5 (**1,350**) to show the 3× spread. On **Slide 2**, point at the **280°F** thermal line.
- Click **▶ Run the Optimization**.
- **Milestone A:** let the **Vizier trial dots (1→15)** populate the Pareto chart — narrate the search exploring, then converging.
- **Milestone B:** **zoom 1.15× on the per-well setpoint table** as it locks: **A-3/A-6 → 66.0 Hz**, **A-5 → 59.7 Hz**, A-1/A-2 → 65.5 Hz.
- **Milestone C:** settle on the **uplift card (+77.9 bbl/d · +$369,225/90d · gas 7.9999/8.0)** and the **edge-safety callout**; cursor-circle the gas figure to show the ceiling is respected.

### 🎙️ NARRATION
> *"Now run the whole pad. Six wells share one gas-takeaway ceiling — eight million cubic feet a day. Every barrel carries gas, but some wells carry three times more than others. Throttle them all equally and you strand production on your most gas-efficient wells.*
>
> *So the cloud searches and the edge enforces. Vertex AI Vizier explores the six-well setpoint space — but only setpoints and scores ever leave the site. Every candidate is checked on-premise against each motor's two-hundred-eighty-degree winding limit before it counts.*
>
> *The result: the lowest-gas wells, A-3 and A-6, run wide open at sixty-six hertz; the gassiest, A-5, backs to fifty-nine-point-seven. Seventy-seven-point-nine more barrels a day — three hundred sixty-nine thousand dollars a quarter — with gas pinned just under the ceiling.*
>
> *And if the storm takes your satellite link mid-search? The edge already holds the safety line. The motor limit never depended on the cloud."*

---

## ░░ SECTION 6 — CLOSE ░░  *(~35s · ~75 words)*

### 🎬 VEO PROMPT *(bookend to the cold open)*
```
SCENE 6 — "First Light"
Photorealistic. The same Permian pad as Scene 1, now at dawn. The work-lights are off; the
wellheads pump steadily against a pale gold sky. The same operator walks out of the RTOC trailer
with a fresh coffee, calm — the night is over, the wells are running. Warm sunrise palette,
soft and resolved. No text overlays.
```

### 🎥 CINEMATOGRAPHY
- A **slow crane-up** from the operator to a **wide of the running pad at sunrise** — visually "the fleet kept producing through the night."
- End on a **held wide**, let it breathe, then a gentle fade.

### 🖱️ SCREEN CHOREOGRAPHY (live UI — *Operations* / *Financials*)
- Briefly toggle to the **Operations** fleet view, then **Financials** — cursor-rest on the cumulative savings figure. No zoom; calm, settled framing to match the dawn.

### 🎙️ NARRATION
> *"Diagnose the ambiguous. Catch the wrong fix before it's ordered. Push every barrel that's safe to push.*
>
> *Three problems, one sovereign stack — every verdict cited, every action approved by your engineer, every byte inside your perimeter.*
>
> *Lower lifting cost. Longer asset life. Maximum runtime. That's GDC, from Google Cloud — where your data already lives."*

---

## APPENDIX A — SHOT LIST & RUNTIME LEDGER

| # | Section | Veo? | Live UI tab | Key camera/screen move | Words | Budget |
|---|---|---|---|---|---|---|
| 1 | Cold Open | ✅ | — | Aerial push-in → interior dolly + rack-focus to folder | 70 | 0:35 |
| 2 | What GDC Is | ◐ bridge | How It Works | Macro LED push → tier glide, 1.15× hold on Tier 3 | 95 | 0:45 |
| 3 | H1 Discern | ✅ | Horizon 1 | Split-screen push-in; amber→red gap gesture; **A/B branch** | 165 | 1:20 |
| 4 | H2 Classify | ✅ | Horizon 2 | Wax time-lapse; truck pull-away; doc-reveal zooms | 185 | 1:30 |
| 5 | H3 Optimize | ✅ | Horizon 3 | Aerial orbit; storm steady-LED; setpoint-table zoom | 175 | 1:25 |
| 6 | Close | ✅ | Ops/Financials | Crane-up to sunrise wide; calm settle | 75 | 0:35 |
| | **TOTAL** | | | | **≈765** | **≈6:10** |

> **Trim note:** if you need a hard 6:00, the Section-2 Veo bridge (Scene 2) and ~15 words from H2 are the safe cuts. Spoken-only (no Veo dwell) lands ≈5:25.

---

## APPENDIX B — VEO PROMPTING DISCIPLINE
- Always include **"photorealistic, no text overlays, no synthetic UI"** — Veo tends to invent labels.
- Always state **time of day + palette** (night sodium/blue, winter pale, golden hour, dawn).
- Use **correct equipment nouns** (christmas tree, VFD cabinet, impeller, intake, tubing wall, metering skid, hot-oil truck) — Veo renders O&G hardware far more accurately with precise terms.
- For **"absence" shots** (the truck that didn't come, the link that dropped), film the **contrast** (truck working a *different* well; LEDs steady *while* the network indicator goes amber) — generative video can't show a negative directly.
- Camera language Veo responds to well: *slow push-in, dolly, crane-up, rack focus, locked-off macro, quarter-arc aerial orbit*. Avoid asking for more than one move per shot.

---

## APPENDIX C — SPOKEN-FIGURES INTEGRITY GATE *(must match live code)*
| Spoken claim | Source | Locked value |
|---|---|---|
| GDC leads SCADA by "4–9 minutes" | `HEALTH_THRESHOLD=0.87`; detect idx 35–46 vs alarm idx 55–73 | run-dependent, range holds |
| H1 is Gas Lock **or** Drawdown | `app.js`: `Math.random()<0.5` | 50/50 — use A/B branch |
| H2 amps +14% / eff −10% | app.py H2 scenario | +14% / −10% |
| H2 vibration 1.0→4.5 mm/s; HI at 4.0 | app.py `vib_*`; ISA-18.2 | mm/s (NOT in/s) |
| H2 paraffin overdue | dynamic doc | 52 days (Day 142) |
| H2 WAT | seed PVT doc | 118°F |
| H2 hot-oil vs pull | ledger H2-PAR-5/6 | $3k–$6k vs $70k–$100k |
| H3 gas ceiling | `_GAS_CEILING_MMSCFD` | 8.0 MMscfd |
| H3 winding limit | `_WINDING_TEMP_LIMIT_F` | 280°F |
| H3 setpoints | live Vizier 2026-06-11 | A-3/A-6 66.0 · A-5 59.7 · A-1/A-2 65.5 |
| H3 uplift / revenue | live Vizier result | +77.9 bbl/d · $369,225/90d · gas 7.9999 |

> ⚠️ If `_GAS_CEILING_MMSCFD`, `_WINDING_TEMP_LIMIT_F`, `_PAD_ALPHA_WELL_PARAMS`, or the H2 vib/WAT/PM values change in `app.py`, update Sections 4–5 and this table **before** recording.
