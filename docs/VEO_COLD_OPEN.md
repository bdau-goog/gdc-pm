# GDC ESP Ops Video — Veo Story Intro → Demo Hand-off (PER-BEAT VO)
**Pattern:** Modeled on the prior GDC CCS/DAS demo (narrated Veo B-roll intro that tells the whole story, then "Let's dive into the demo"). Cinema is **front-loaded**; the demo itself is live screen recording with voiceover (V3/V4 scripts).
**Structure:** **One Veo clip = one Vids scene = one short VO line.** Seven beats — several split into sub-scenes (4A/B/C, 5A/B, 6A/B) for **12 scenes total** ≈ **~70–80s**, then cut to the live demo (~4–4.5 min). Total **< 6:00**.
**Perspective:** Google Cloud, third-party. **Persona:** ESP operations / maintenance / asset-longevity leadership (CxO-safe). **No exact numbers spoken** (panel carries them).

---

## ⚠️ DEFEATING VEO'S PUMPJACK BIAS (read first — negative prompts DON'T work)
Veo (like most video models) **ignores "no pump jacks"** — naming the token and saying "oil field" both summon the nodding-donkey schema. Stop fighting it with negatives; **starve the schema instead:**
1. **Never say "oil field," "oil well," "oil pad," "pumpjack," or "nodding donkey."** Even in a negative, those words bias the output.
2. **Describe only the specific object + its setting**, using non-oil framing: *"a low christmas-tree wellhead — a glossy blue flanged valve stack with bright red round handwheels — on flat gravel,"* *"an industrial wellsite,"* *"a remote energy facility."* (The blue-body / red-handwheel color detail is the strongest schema-starve we've found — VALIDATED on the Beat 1 render: a pumpjack is never a blue-and-red valve stack. Do **not** say "finned" — real ESP trees are smooth flanged bodies, and the word steers Veo toward a heat-exchanger look.)
3. **Pick framings where a pumpjack can't intrude:** tight close-ups, macro, interiors, night shots lit to a small pool, the gas-compressor station, the VFD skid, gathering-line manifolds, top-down aerials of just the tree.
4. **If a jack still appears, change the noun, not the negative** — try *"Christmas-tree valve assembly,"* *"wellhead valve stack,"* *"subsea-style valve tree on the surface."*
5. **Last resort:** generate the clip you can get, then crop/frame in Vids to exclude any stray jack, or pick a different beat angle.

### Realism facts (validated against docs/rag_source/esp_manual.md)
- **ESP = low-profile christmas-tree (valve-stack) wellhead**, NOT a beam pump. (Don't *say* "not a beam pump" — just describe the valve tree.)
- **VFD = separate surface cabinet + step-up transformer on a skid**, set back from the wellhead — not part of the tree.
- **Hot-oil treatment** = a service truck **connected at the wellhead** (down tubing/annulus), not the chemical-injection port.
- Safe nouns: christmas tree / valve-tree wellhead, VFD cabinet, step-up transformer, skid, gathering lines, manifold, metering skid, tubing, impeller, intake.


---

## PART A — VEO STORY INTRO (per-beat: one clip = one scene = one VO line)

**How to use this section:** Each beat is **ONE Vids scene**. Drop that beat's Veo clip on the scene, then attach **only that beat's VO line** to the same scene. One clip ↔ one line keeps sync automatic — you never spread a paragraph across clips. *(Step-by-step for attaching per-scene VO is at the bottom: "HOW TO RECORD PER-SCENE VOICEOVER IN GOOGLE VIDS.")*

> **⚠️ CONTINUITY IS DONE WITH A REFERENCE IMAGE, NOT WITH WORDS.** Veo has **no memory between generations** — phrases like "the same desk/operator as Beat 3" in these prompts are only loose hints and will NOT reliably reproduce the prior shot. To make beats actually match (e.g. 3 → 4A → 4B share a desk/operator/grade), **feed a still frame from the prior clip as a reference/ingredient image** in the Veo generation, then use the prompt to describe the change (new angle, new action). Treat all "same as Beat N" prose below as intent for the human, not as something Veo enforces.

### MOVEMENT 1 — Industry context

**🎬 Beat 1 — the field of wellheads (aerial, schema-starved)**  ·  *~8s*
```
Photorealistic elevated cinematic drone shot slowly descending over a vast flat caliche-gravel field in remote West Texas at golden hour. Spread across the field in a loose grid, dozens of identical christmas-tree wellheads recede toward the horizon — each one a vertical stack of flanged steel valves and spools about a man's height, painted glossy industrial blue, fitted with several bright red round handwheels projecting from the sides and small round pressure gauges. Short horizontal flowlines link each wellhead to slim steel gathering pipes that run in straight lines across the tan gravel. Long warm shadows, flat distant horizon, dust-free clean hardware. Smooth slow descending aerial motion, 35mm film look. Industrial precision, repetition, quiet scale.
```
> **🎙️ VO — Beat 1:** *"Upstream oil and gas runs on engineering discipline — lifting every barrel as efficiently and safely as possible."*  ·  *(~17 words / ~8s)*
> **🛠 If a pumpjack appears:** keep the elevated/top-down framing (a nodding-donkey silhouette can't form from above) and lean harder on the color + repetition — *"rows of glossy blue valve stacks with bright red handwheels, identical and evenly spaced across a gravel field."* Pumpjacks are never painted blue-and-red valve stacks, so the color detail starves the schema.

**🎬 Beat 2 — the wellhead + control skid (tight, schema-starved)**  ·  *~8s*  ·  *(same field as Beat 1, pushed in)*
```
Photorealistic slow push-in on a single christmas-tree wellhead in the same gravel field as the wide aerial — a vertical stack of flanged steel valves and spools about a man's height, painted glossy industrial blue, with several bright red round handwheels projecting from the sides and small round pressure gauges. A short distance behind it sits a separate electrical control skid: a tall louvered stainless cabinet and a small boxy transformer. The rest of the identical blue wellheads recede softly out of focus toward the golden-hour horizon. Shallow depth of field, same warm low-sun grade as the field shot, 35mm film look. Precision industrial hardware, clean and quiet.
```
> **🎙️ VO — Beat 2:** *"Electric submersible pumps do that lifting. Maintaining them well keeps costs down and optimizes production."*  ·  *(~15 words / ~7s)*
> **🛠 Note:** this is the **same scene as Beat 1, just closer** — one wellhead sharp in front, the field soft behind. The pump itself is downhole (invisible); the surface story is the blue valve tree + the control/VFD skid beside it. Same hardware and grade as Beat 1 keep the wide→tight cut continuous; the tight framing leaves no room for a jack.


---

### MOVEMENT 2 — The problem

**🎬 Beat 3 — the night alarm (operator profile, no screen content)**  ·  *~8s*
```
Photorealistic medium shot of a single industrial control-room operator seen in three-quarter side profile at night, looking to the side at screens out of frame. They are a professional in a neat dark work shirt, expression calm and focused; they do NOT look at the camera. The soft cool blue glow of monitors washes across their face from the side, joined by a gentle, rhythmic pulsing amber light that casts slow warm flashes on their profile. The background is dark and soft, with banks of distant unreadable screens pushed completely out of focus into neat blue bokeh. Cinematic side-profile composition, shallow depth of field, 35mm film look, quiet night-shift focus. No screen content is visible in frame, no text, no letters, no logos, no graphics.
```
> **🎙️ VO — Beat 3:** *"But when an alarm fires at night, the sensors say a pump is in trouble — not why."*  ·  *(~17 words / ~8s)*
> **🛠 Why side profile:** we tried an close-up, but Veo rendered a creepy head-on mugshot staring straight at the camera. The side profile or three-quarter view forces the subject to look off-camera at their work screens, keeping the illusion of a working RTOC.
> **🛠 Why no screen content:** we tried showing the alarm on a SCADA wall and on a single on-screen pump symbol — Veo fakes garbled toolbars/labels ("SCADA MIIPLUPUO", "CdNet") and renders unpredictable junk icons every time a UI is in frame. **The fix: never show the screen directly.** Convey the alarm purely through the **pulsing amber light on the operator's side profile**. No UI = no garbled text, and a focused side profile sells the operational moment cleanly.
> **🛠 If the operator looks at the camera:** hard-specify *"the operator looks off-camera to the side, three-quarter side profile, eyes focused on screens out of frame, they do NOT look at the camera lens."*
> **🛠 The "pump" is carried by the VO, not the visual** — this beat is about the human moment; the pump hardware already lives in Beats 1–2.

**🎬 Beat 4A — the clear-cut alarm (the easy majority)**  ·  *~7s*  ·  *(same operator/desk as Beat 3)*
```
Photorealistic medium shot of the same control-room operator from Beat 3, at the same desk, seen in three-quarter side profile, looking off-camera at their screens — they do NOT look at the camera. With calm, practiced confidence they reach forward and tap a key to acknowledge a routine alert, giving a small assured nod as the moment is handled in seconds. The pulsing amber accent from the previous beat steadies and cools back to calm blue. Banks of monitors stay softly out of focus as blue bokeh behind them. Same night-shift lighting, cool blue with a fading warm accent. Shallow depth of field, 35mm film look, quiet competence. No screen content visible, no text, no letters, no logos, no graphics.
```
> **🎙️ VO — Beat 4A:** *"The resolution to some alarms can be identified quickly."*  ·  *(~9 words / ~5s)*  ·  *(prior alt: "Most alarms are clear-cut — the signal is obvious, and the operator clears it in seconds.")*
> **🛠 Why this beat exists (TRUTH / no straw man):** most alarms ARE routine and self-evident — a clean underload trip, an obvious overpressure, a comms fault. Conceding this up front is a **credibility signal** to the engineer audience and scopes our claim honestly: GDC's value is the *ambiguous* subset (Beat 4B), not every alarm. Without this concession, a production engineer dismisses the whole open as overclaiming.
> **🛠 Visual = confident & fast.** This beat should feel quick and assured (a few seconds, handled). The contrast with Beat 4B's slower "hunt" is what carries the meaning — pacing does the work.
> **🛠 Keep it screen-free** (same lesson as Beat 3): convey "resolved" through the operator's confident action + amber settling to calm blue, not through any rendered UI.
> **🛠 Continuity (do this, not the prose):** to match Beat 3's operator/desk, **feed a still frame of the Beat 3 clip as a reference ingredient** — the "same operator/desk" wording alone won't reproduce it.

**🎬 Beat 4B — the ambiguous alarm (operator hesitates, no quick resolve)**  ·  *~6s*  ·  *(same operator/desk as Beat 3/4A)*
```
Photorealistic medium shot of the same control-room operator from Beat 3, at the same desk, in three-quarter side profile, looking off-camera at their screens — they do NOT look at the camera. This time there is no quick resolution: the operator leans in slightly, brow tightening, one hand hovering near the keyboard but not acting, studying an unclear signal with quiet concern. The amber warning accent keeps pulsing, unresolved, rather than settling to calm blue. Banks of monitors stay softly out of focus as blue bokeh behind them. Same night-shift lighting, cool blue with a persistent warm amber accent. Shallow depth of field, 35mm film look, quiet uncertainty. No screen content visible, no text, no letters, no logos, no graphics.
```
> **🎙️ VO — Beat 4B:** *"But some are ambiguous — the signal alone can't tell you the cause."*  ·  *(~12 words / ~6s)*
> **🛠 The contrast that carries the meaning:** 4A was fast/confident (amber settles to calm). 4B is the **inverse** — the operator hesitates, doesn't act, amber stays unresolved. Pacing + body language do the work; no screen needed.
> **🛠 Flow (3-beat concede→pivot→friction):** 4A *"identified quickly"* → 4B *"But some are ambiguous — the signal alone can't tell you the cause"* → 4C *"The context that **can** sits scattered…"*. The word **"can"** links 4B→4C (signal *can't* / context that *can* is scattered). Record 4B and 4C as separate lines on separate scenes.
> **🛠 Screen-free** (same lesson as Beat 3): convey "stuck" through the lean-in + hovering hand + unresolved amber, not through any rendered UI.
> **🛠 Continuity (do this, not the prose):** feed a still frame of the Beat 3/4A clip as a **reference ingredient** — the "same operator/desk" wording alone won't reproduce it.

**🎬 Beat 4C — the scattered context (FRAGMENTATION is the subject)**  ·  *~8s+ (use EXTEND if VO runs long)*  ·  *(same desk; slower, heavier)*
```
Photorealistic overhead top-down shot looking straight down onto the same dark industrial control desk from Beat 3, lit by cool blue screen glow with a warm amber desk-lamp spill from one side. Scattered across the desk are several DISCONNECTED sources of information that don't belong together: a rugged tablet showing a generic scanned report (header block + small data table), a separate laptop turned at an angle showing a different generic document, a printed lab-report sheet, a spiral notebook with handwriting, and a phone displaying yet another small screen. The operator's two hands move between the scattered items — sliding the paper aside, reaching for the tablet, comparing — conveying the slow effort of gathering context from many separate places. Everything is kept slightly soft so no text is legible. Slow, deliberate, slightly tense pacing, heavier than the previous beat. Shallow depth of field, 35mm film look. No readable text anywhere, no logos, no recognizable UI chrome, no audio-waveform or seismic-nebula imagery.
```
> **🎙️ VO — Beat 4C:** *"The context that can sits scattered across disconnected systems — slow to assemble when the decision can't wait."*  ·  *(~17 words / ~8s)*
> **🛠 The fix vs. the old render:** a single tidy tablet reads as *normal work* and contradicts the VO. Make **fragmentation the subject** — MULTIPLE disconnected sources (tablet, laptop, paper, notebook, phone) the operator must physically gather and reconcile. The **hands moving between scattered items** + the **overhead angle** are what convey "scattered across disconnected systems, slow to assemble." That friction IS the story.
> **🛠 VO intent (the real friction):** the deciding context **exists** — but it's **fragmented across disconnected systems** (CMMS, lab portal, handover log, file shares) and **slow to find, combine, and decide from** under a live-event clock. Convey *fragmentation + retrieval/assembly friction*, not *distance* or *absence*. This is exactly the H1/H2 demo subset (look-alike telemetry: gas-interference-vs-drawdown, paraffin-mimicking-bearing-wear) and what GDC collapses into a cited diagnosis in seconds.
> **🛠 If the VO runs longer than the clip:** use the Veo/Vids **EXTEND** feature to lengthen this clip to match the line (validated as working), or let the scene hold a beat longer on the scattered desk. Don't rush the read — the slow "hunt" pacing is the point.
> **🛠 Why digital + paper mix (TRUTH gate):** a modern engineer's sources are mostly digital (PDFs, CMMS like Maximo/SAP, a digital handover log) with some printed sheets — the point isn't paper-vs-screen, it's that the sources live in **different systems** and don't talk to each other. The multi-device spread (tablet + laptop + phone + paper) makes "disconnected systems" literal.
> **🛠 Veo garble dodge:** every screen/paper risks fake text. Keep **all items slightly soft / out of crisp focus** so they read as documents by layout (headers, tables, handwriting texture) without legible words. Reinforce *"no readable text, no recognizable UI chrome."* Overhead framing also reduces how much screen detail Veo tries to invent.
> **🛠 Continuity (do this, not the prose):** feed a still frame from Beat 3/4A/4B as a **reference ingredient** so the desk/grade match — prompt prose like "same desk" won't reproduce it on its own. Use the prompt only to specify the *change* (overhead angle, scattered items). Keep the color/lighting identical so the cut reads as the same room.

---

### MOVEMENT 3 — The GDC solution

**🎬 Beat 5A — bring the cloud to the operations center (the hardware)**  ·  *~6s*
```
Photorealistic cinematic macro shot in a dark operations-center equipment room, with continuous motion throughout. The camera performs a slow, smooth tracking glide from left to right along the front edges of a small stack of three identical slim silver-white enterprise compute sleds mounted one above another, the focus racking gently from the near sled to the far one as it moves. Across the dark front faces, dozens of tiny status LEDs flicker and blink rapidly in green and amber, alive with data-traffic activity, while a single steady green power LED glows on each unit. A soft specular highlight travels slowly across the brushed-metal surfaces as the camera moves. A few blue and orange fiber patch cables sway almost imperceptibly and catch the moving light. The dense ports stay soft and out of crisp focus so they read as fine texture, never text. Cool blue key light with one warm practical reflection. Only the three stacked sleds are in frame — no surrounding rack frame, no power strips, no outlets. Energetic but controlled, enterprise-grade, on-premise. No text, no readable labels, no logos, no brand markings, no nameplates, no printed port names, no steam, no smoke, no vapor, no haze, no mist, no fog.
```
> **🎙️ VO — Beat 5A:** *"This is where Google Distributed Cloud comes in — it brings Google's AI to your data, instead of your data to the cloud."*  ·  *(~23 words / ~8s)*  ·  *(prior alts: "Google Distributed Cloud brings Google's AI on-premise." → too abrupt; then "…to make sense of that scattered context." → good bridge, but missed the core GDC inversion.)*
> **🛠 BRIDGE + INVERSION (your note — do better in 5A: lead with the "AI to your data, not data to AI" idea + sovereignty):** *"This is where Google Distributed Cloud comes in"* is the bridge phrase — it answers 4C's just-posed problem (*"the context… sits scattered… slow to assemble"*) by naming the thing that solves it, so the M2→M3 cut reads as **problem → answer**. The substance of 5A is now the **GDC inversion**: *"brings Google's AI to your data, instead of your data to the cloud."* That single line is the differentiated, memorable GDC concept **and** the mechanism of sovereignty (the data never has to travel), which sets up 5B to land the sovereignty payoff explicitly. *Honesty gate:* the inversion is literally true of GDC (on-prem inference), not a competitive-detection claim — safe.
> **🛠 Scene 5 = ARCHITECTURE (5A) then SECURITY POSTURE (5B) (your notes — "are they saying the same thing?" + "5B is about secure access without leaving the corporate data perimeter"):** the split is **5A = the architecture / the move** (GDC brings the AI *to your data* instead of shipping your data to a public cloud) and **5B = the security & governance payoff** (because it works *inside your own corporate perimeter*, the data stays secure and governed, and only what you approve ever leaves). NOTE the deliberate framing difference so they don't just restate locality: 5A = *where the compute runs*; 5B = *the trust/compliance posture* (access-controlled, governed, nothing exposed to a third party). Full M3 arc: **5A architecture (AI→data) → 5B security (governed, inside your perimeter) → 6A mechanism (fusion) → 6B result (cited diagnosis, in seconds).** "Scattered context" is still closed downstream by 6A/6B. *(Latency/"keep pace" was considered for 5B and cut — the value here is sovereignty/security, not speed.)*
> **🛠 Length note:** ~8s line vs the ~6s clip — let the 5A scene run a touch longer or use EXTEND. Tight trim (~7s): *"This is where Google Distributed Cloud comes in — bringing Google's AI to your data, not your data to the cloud."* (~20 words).

> **🛠 ADD MOTION (your note — "zero motion, bland"):** Veo renders a *still life* unless you script movement explicitly. Two motion layers now drive the shot: (1) **camera** — a slow left-to-right **tracking glide** with a gentle **rack-focus** from near sled to far (a static hero shot of hardware always reads as a product photo); (2) **in-frame life** — LEDs **flickering/blinking rapidly** (data traffic), a **specular highlight traveling** across the metal as the camera moves, fiber cables that **sway and catch the light**. **Do NOT use heat-shimmer / “warm exhaust air” as a motion layer** — Veo renders it as visible **steam/smoke**, which in an O&G setting reads as venting/leaking/overheating (off-message); it's now negated in the prompt (no steam/smoke/vapor/haze/mist/fog). If still too static, escalate the camera to a slow **push-in toward the blinking LED bank** and add *"LEDs pulsing in sequence, a wave of light running along the row."*
> **🛠 SITING (why this changed):** in this scenario GDC is **not** deployed in the field next to the wells — it sits in the operator's **Real-Time Operations Center (RTOC)**, placed there for **data sovereignty** and **latency / data-gravity** reasons (the SCADA historian + documents already live at the RTOC). So 5A/5B are an indoor ops-center, not a gravel-yard field box. *"On-premise"* in the VO = the operator's own RTOC, which is exactly right.
> **🛠 Match to the real gear (brand-free):** actual GDC Connected hardware is a **stack of three slim silver-white sleds** — so the prompt describes that silhouette for authenticity. The real unit is **Dell**, but we do NOT show Dell: the sleds carry readable labels ("iDRAC", "SFP28", "Dry Input") and a logo'd top cover. **Do NOT feed the Dell product photo as an ingredient** — Veo would copy those labels (→ garbled fake text) and the branding. Reproduce only the *form factor* in words, and keep the dense port face **soft/out of focus** so it reads as texture, never text.
> **🛠 Why the earlier render broke (Tripp-Lite screenshot):** the words **"rack-mounted server"** summoned the whole rack — Veo added a **PDU / power strip** (the Tripp-Lite bar + outlets) and invented **garbled brand labels**. **Fix = starve the rack schema:** never say "rack," "rack-mounted," "PDU," or "power strip"; say **"stacked compute sleds."** Negate outlets/power strips/nameplates/printed port names explicitly, and keep the front face soft so there's nothing for Veo to letter.
> **🛠 If labels/outlets/branding still appear:** tighten to just the **moving light across the blinking LED bank + one swaying fiber cable** (front-face ports cropped out). Swap nouns to *"compute sleds" / "compute appliances,"* never "rack" or "server" (which both pull in racks/logos). Last resort: generate it and crop the offending element out in Vids.
> **🛠 INGREDIENT: none — prompt only.** 5A is the first Movement-3 shot (nothing to match), and the only candidate reference (the Dell photo) would *reintroduce* branding + garbled labels. Generate from text alone, iterate until clean. *(For 5B, prefer **Extend** rather than a still-frame ingredient — see the 5B note.)*
> **🛠 One idea per beat:** 5A = the *what* (Google's AI, on stacked boxes at the edge). The *where/why* (sovereign, inside the RTOC perimeter) is 5B.

**🎬 Beat 5B — inside the operator's perimeter (sovereign)**  ·  *~6s*  ·  *(same RTOC; pull back / wider)*
```
Photorealistic slow wider pull-back inside a clean, cool operations-center equipment room at night: rows of dark, quiet equipment cabinets with soft breathing green and blue status lights, neatly managed overhead cabling, a polished floor catching the cool glow. In the foreground a secure glass door with a small access-card reader implies a controlled, private facility. The space feels self-contained, enterprise-grade, on-premise — the operator's own secured operations center, not a public cloud. Cool blue night grade with one warm practical light. Slow, steady, reassuring. No text, no readable labels, no logos, no screen content.
```
> **🎙️ VO — Beat 5B:** *"And it works inside your own corporate perimeter — so your data stays secure and governed, and only what you approve ever leaves."*  ·  *(~21 words / ~8s)*  ·  *(prior alts: "…where the data already lives." / "…so your data never leaves, and never has to." / "…it keeps pace with the event as it unfolds." — latency was cut; the value is secure, governed access. "Never has to leave" was also cut — it contradicts H3 (Vizier: cloud searches, edge enforces), so the claim is now governed egress: "only what you approve ever leaves.")*
> **🛠 5B = SECURITY / GOVERNANCE, distinct from 5A's architecture (your note — "secure access without leaving the corporate data perimeter"):** 5A states the *move* (AI comes to your data); 5B states the *trust posture* it buys — the analysis happens **inside your own corporate security perimeter**, so the data stays **secure, governed, and under your access controls**, never exposed to a third party. The angles differ on purpose (5A = architecture / where the compute runs · 5B = security & compliance), so this isn't just locality said twice. 5B's *"And…"* still flows straight out of 5A. *Honesty gate (H3-aware):* the claim is **governed egress**, NOT "data never leaves." H1/H2 run fully on the edge, but **H3 (Vizier/Optimize) is hybrid — cloud searches, edge enforces** — so *some* optimization data does leave. "Only what you approve ever leaves" is true across all three horizons and ties to the real **HITL approval gate**. An absolute "never leaves" would be a silent lie vs the H3 architecture — do not restore it.
> **🛠 One idea per beat:** 5B = **secure, governed access inside the perimeter**. The **secure glass door + access-card reader** visual is doing exactly this work — it reads as *controlled, private, access-restricted facility*, which is the literal picture of "inside your corporate perimeter, under your access controls."
> **🛠 Why the wellheads are gone (corrected with 5A):** the old 5B showed "christmas-tree wellheads visible beyond a fence," which placed the hardware at the wellsite — that contradicts the RTOC siting. The wells are miles away; their data is what travels to the RTOC. Convey "perimeter" through the **secured facility** (badge reader, controlled room), not through visible wellheads. *(If you'd rather keep a field tie, tell me and I'll restore a softened version — flagging this since you only asked about 5A.)*
> **🛠 USE EXTEND for 5A→5B (your question — better than the still-frame ingredient for THIS pair):** 5A is an extreme macro on the sleds; 5B is a **wider pull-back** revealing the room — a pull-back reveal is a natural *continuation* of a macro, so **Extend** continues the same shot/room/grade with zero "does it match?" risk (Extend matches the whole motion; a still-frame ingredient only matches one starting frame). The two lines already read as one breath (*"…not your data to the cloud. **And** it works entirely inside your own corporate perimeter…"*), so continuous picture under continuous narration reinforces the "one thought" goal. **Workflow caveat (preserve VO sync):** keep the per-scene rule — generate 5A → Extend into the pull-back → then **split the extended clip at the macro→wide transition into two Vids scenes**, one line on each half. Do NOT merge both lines onto one ~16s scene. (For 6A→6B, the still-frame ingredient is still fine — that pair is the same framing resolving, not a camera move.)
> **🛠 Screen-free** (Beat 3 lesson): do NOT show the SCADA video wall here — Veo garbles on-screen dashboards into fake text. Convey "operations center" through the equipment cabinets + secured room, not monitors.

**🎬 Beat 6A — fusion (telemetry meets documents)**  ·  *~8s*
```
Photorealistic, calm and premium continuation of the SAME operations-center equipment room from the previous shot (same cabinets, same grade, same hardware — do not introduce new or different servers): a slow, smooth, steady push-in glides down the quiet server aisle toward one softly glowing server, its rows of small status LEDs breathing gently in green and blue. The room is calm, ordered, and powerful — quiet on-premise compute doing its work. Subtle, restrained, cinematic; cool blue with one warm practical light; shallow depth of field, slow controlled motion. Absolutely NO glowing light beams, no laser lines, no light streaks, no light trails, no neon, no holograms, no flashy effects, no paper, no documents, no liquid, no pool, no sparks, no fire, no smoke, no steam, no new servers. No readable text, no labels, no UI, no logos.
```
> **🎙️ VO — Beat 6A:** *"On the edge, it merges and compares the live sensor data with the well's own scattered documents."*  ·  *(~17 words / ~8s)*
> **🛠 CONTINUE 6A FROM 5B (your note — "it's rendering new servers"):** generated cold, 6A invents fresh/different hardware. Fix = **continue it from 5B** — either **Extend** the 5B clip, or feed a **5B still frame as the ingredient** — so 6A is the **same room and the same server**, not a new one. This also **starves the liquid/spark hallucinations**: with a real established server to anchor on, Veo stops free-associating “fusion” into a substance. Chain reads as one move: 5A macro → 5B pull back to the room → 6A push back in down the aisle onto one glowing server (NO beams, NO paper — see EFFECT CUT below). (Coupling caveat: Extend re-couples re-renders, so if 6A needs tweaks, the ingredient method keeps it independent.)
> **🛠 EFFECT CUT — the abstract “fusion” visual is abandoned (your renders: explosion → liquid puddle → laser beams + stray paper).** Veo over-literalizes EVERY data-merge metaphor into a hazard or a flashy sci-fi effect, and kept rendering the paper stack out of place on a server. **Decision: 6A/6B carry NO bespoke effect and NO paper** — they are calm, literal, premium shots of the real on-prem server room, and the **VO owns the “merges and compares” idea** (the Beat-3 rule: voice carries the abstract, the picture stays literal and safe). Hard-negate beams/lasers/streaks/holograms/paper/liquid/sparks/steam. If you later want a hint of “data moving,” the ONLY safe version is the existing LED activity on the servers — never light-beams across the room.
> **🛠 Closes the 4C loop:** 4C ended on *"scattered… slow to assemble."* 6A answers the *"scattered"* directly — but in the **VO, not the visual**: *"merges and compares… the well's own scattered documents."* The picture stays a calm, literal server room (effect cut — see above); the spoken line carries the *scattered → assembled* payoff of the 4C shot. This is the Beat-3 rule again: let the voice own the abstract.
> **🛠 Detection wording (TRUTH / NO STRAW MAN):** *"merges and compares the live sensor data"* credits the **multivariate** nature of our scoring (🟡 OUR-CODE — true to our models) **without** claiming we detect earlier/better than advanced APM (SmartSignal/Mtell already do multivariate early detection — a superiority claim gets dismantled). Do NOT escalate this to "detects sooner" or "catches what others miss." The fuller pre-threshold-vs-threshold-SCADA detection story belongs in the **live demo's How It Works (tiers 1–2)**, where the models actually show it — not the cinematic intro.

**🎬 Beat 6B — the cited answer**  ·  *~5s*  ·  *(the convergence resolves)*
```
Photorealistic calm continuation of the previous shot in the SAME room on the SAME server (do not introduce new or different servers): the slow push-in settles and holds on the one softly glowing server as its steady glow brightens just slightly into one calm, clear, even light — the quiet moment of resolution. Slow, smooth, controlled, still. Cool blue with one warm practical light; quiet confidence. Absolutely NO glowing light beams, no laser lines, no light streaks, no neon, no holograms, no flashy effects, no paper, no documents, no liquid, no sparks, no fire, no smoke, no steam, no new servers. No readable text, no labels, no UI, no logos.
```
> **🎙️ VO — Beat 6B:** *"The result: one cited, reviewable diagnosis — in seconds."*  ·  *(~9 words / ~5s)*
> **🛠 Closes the 4C loop (part 2):** 4C ended on *"slow to assemble when the decision can't wait."* 6B is the counter-punch — *"in seconds."* The visual flow from "push-in down the aisle" (6A) to "settle and hold on one steady, brightening server glow" (6B) carries scattered→answered — calmly, with the VO doing the narrative work; never a spark/flash/liquid/beam.
> **🛠 "Cited, reviewable" is load-bearing (TRUTH):** the diagnosis is **evidence-backed and human-checkable**, not a black-box guess — this is the trust hook that sets up the live demo's cited verdicts. Keep both words.
> **🛠 Continuity:** feed a frame of 6A as a reference ingredient (or Extend) so 6B holds on the SAME server, its glow just steadying — no new shot, no effect.

---

### HAND-OFF — roll into the demo

**🎬 Beat 7 — dissolve toward the screen**  ·  *~6s*  *(optional; or just cut to the app)*
```
Photorealistic slow push-in toward a clean operations dashboard glowing on a monitor in the dark RTOC, the screen brightening to fill the frame, inviting the viewer in. Cool screen light. No readable text, no logos.
```
> **🎙️ VO — Beat 7:** *"Let's dive into the demo — and see GDC analyze a struggling well at the source."*  ·  *(~15 words / ~7s)*

➡️ **Cut to live screen recording.** From here, follow **V3 (cinematic)** or **V4 (operator-grounded)** for the demo voiceover, starting at the **"What is GDC / How It Works"** beat, then **Discern → Classify → Optimize**, and the close.

---

## GENERATION TOOLING — USE GOOGLE FLOW, NOT VEO-INSIDE-VIDS (decided Session BS+30)

**Why we switched:** every failure in the Vids-embedded Veo workflow traced to **no cross-shot context** — Veo regenerated cold each time (re-inventing servers), and the only way to steer it was retyping the whole prompt. That produced the explosion → liquid → laser-beam churn on Beat 6.

**The workflow going forward:**
1. **Generate in Google Flow** (`labs.google/flow`) — Google's dedicated Veo filmmaking tool, purpose-built for multi-shot continuity:
   - **Ingredients:** save a subject/asset (the operator, the desk, the 3-sled stack, the server room) once and **reuse it across shots** so the hardware/person stays consistent — this is the real fix for "it keeps rendering new servers."
   - **Scene extension / "jump to":** continue a shot into the next beat (our 5A→5B macro→pull-back, 5B→6A push-back-in) inside one project.
   - **Iterate conversationally** instead of retyping: "same shot, less flashy, keep the room."
2. **Assemble in Google Vids** — import the finished Flow clips, one clip per scene, and attach the **per-scene VO** exactly as described below. Vids remains the edit/VO/timeline tool; it is NOT where you generate.

**What Flow does NOT fix:** the abstract "fusion" effect is **concept-hostile to Veo**, not tool-hostile — it failed 4x because "data merging" over-literalizes into hazards/sci-fi. The **EFFECT CUT** decision (Beat 6 = calm literal server room, VO carries the merge) stands in Flow too. Don't reopen it.

**Per-beat prompts in this doc are tool-agnostic** — paste them into Flow as-is. The "ingredient image" and "Extend" notes map directly onto Flow's Ingredients and scene-extension features. *(Fallback if Flow is unavailable to you: the general Gemini app is better than Vids for iterative prompting, but still has no true cross-shot video memory — you'll lean on ingredient images for continuity.)*

---

## HOW TO RECORD PER-SCENE VOICEOVER IN GOOGLE VIDS
The point of per-beat VO: **each scene carries its own narration**, so sync is automatic.

1. **One scene per beat (sub-scene).** You'll have **12 intro scenes** (Beats 1, 2, 3, 4A, 4B, 4C, 5A, 5B, 6A, 6B, 7); drop each beat's Veo clip on its scene.
2. **Select a scene**, then in the right rail click **Voiceover** (the mic icon). Vids records audio **for the selected scene only** and pins it to that scene.
3. **Read just that beat's VO line**, stop, accept. The audio is now attached to that scene.
4. **Match scene length to the line.** If the line runs ~8s, set that scene's duration to ~8s (drag the scene edge / set duration). The Veo clip is ~8s, so they line up naturally.
5. **Repeat per scene.** Because each line lives on its own scene, reordering or re-recording one beat never desyncs the others.
6. **Prefer to narrate elsewhere?** Record each line as its own audio file (phone/QuickTime) and **Insert → Audio → Upload** onto the matching scene. Same one-line-per-scene principle.

> **Tips:** leave ~0.3s of silence at the head of each take so cuts don't clip the first word. If a clip is shorter than its line, extend the scene or slow the clip slightly; if longer, let the visual breathe before cutting.

---

## PART B — LIVE DEMO (screen recording + VO)
Use the existing script for the demo walkthrough — **do not** add more B-roll (protects the 6-min budget):
- **How It Works** tab — three tiers (telemetry → patterns → documents).
- **Discern (H1)** — ambiguous signal; read the on-screen verdict (Gas Lock *or* Drawdown branch).
- **Classify (H2)** — bearing-wear look-alike → paraffin; three documents; surface fix vs. pull.
- **Optimize (H3)** — six wells, one gas limit; cloud searches, edge enforces; offline safety.
- **Close** — lower lifting cost, longer asset life, higher runtime; sovereign edge.

> For the demo, you can narrate **per tab/scene** the same way (one VO line per scene), or record continuously while you click. The V3/V4 scripts already break the demo VO into short per-section passages that map cleanly to scenes.

---

## RUNTIME MATH
| Part | Content | Beats / sections | Time |
|---|---|---|---|
| A — Veo intro | Beats 1–7 (4→4A/B/C, 5→5A/B, 6→6A/B → 12 scenes) | 12 scenes × ~6s | ~1:10–1:20 |
| B — Live demo | How It Works + H1 + H2 + H3 + close | ~430 words | ~4:00 |
| | **Total** | | **~5:00–5:15** | (comfortably under 6:00) |

---

## NOTES
- **I can author but not watch Veo output.** Generate each beat, eyeball it yourself (or via a vision-capable tool), regenerate as needed. Tell me which beats fight you and I'll retune those prompts.
- **Continuity:** all 12 scenes (Beats 1–7 incl. sub-scenes) play **back-to-back**. Aim for similar grade/color across clips so the cut feels continuous even though each carries its own VO line. **Veo has no cross-generation memory** — to actually match a prior shot (operator, desk, wellhead, server), **feed a still frame of that clip as a reference/ingredient image** and let the prompt describe only the change. "Same as Beat N" prose is a hint for you, not an instruction Veo can follow.
- **Minimum viable intro** if short on time: beats **1, 3, 4C, 5, 7** still tell the whole story (context → problem → solution → demo) in ~40s. (4A + 4B are the optional concession/hesitation beats — cut those first if trimming; 4C carries the core "scattered context" value point.)
