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
> **🎙️ VO — Beat 2:** *"Electric submersible pumps do that lifting. Keep them running, and lifting costs stay down and production stays online."*  ·  *(~18 words / ~8s)*
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

**🎬 Beat 5A — bring the cloud to the edge (the hardware)**  ·  *~6s*
```
Photorealistic macro slow push-in on a small rack-mounted server inside a field equipment enclosure at night, status LEDs breathing steady green, neat fiber and copper cabling, a dark gravel yard faintly visible through a window behind it. Compact, quiet, on-premise. Cool blue key light with one warm practical. No text overlays, no readable labels, no logos.
```
> **🎙️ VO — Beat 5A:** *"Google Distributed Cloud brings Google's AI on-premise."*  ·  *(~8 words / ~5s)*
> **🛠 One idea per beat:** 5A = the *what* (Google's AI, on a box at the edge). The *where/why* (sovereign, inside the perimeter) is 5B. Visual is the hardware itself — the green LEDs + cabling sell "real on-prem compute."

**🎬 Beat 5B — inside the operator's perimeter (sovereign)**  ·  *~6s*  ·  *(same site; pull back / wider)*
```
Photorealistic wider night shot of the same compact field equipment enclosure on a gravel wellsite, a soft warm glow spilling from its open door, a security fence and the faint silhouettes of christmas-tree wellheads visible beyond it under a dark sky. The small building sits quietly inside the fenced site — self-contained, secure, on-premise. Cool blue night grade with one warm practical light. Slow, steady, reassuring. No text, no readable labels, no logos.
```
> **🎙️ VO — Beat 5B:** *"It runs inside the operator's own perimeter — where the data already lives."*  ·  *(~13 words / ~6s)*
> **🛠 One idea per beat:** 5B = the *where/why* — data sovereignty + locality. The fence + wellheads-beyond visual makes "inside the perimeter / where the data lives" literal. Continuity: feed a frame of 5A (or Beat 1/2's wellheads) as a reference ingredient so the site matches.

**🎬 Beat 6A — fusion (telemetry meets documents)**  ·  *~8s*
```
Photorealistic abstract-but-grounded shot: a clean stream of light representing live sensor data and a stack of physical field documents drawing together into a single bright point on the edge server, conveying fusion of data and documents. Cinematic, dark background, cool blue and warm amber light merging. No text, no labels, no UI, no logos.
```
> **🎙️ VO — Beat 6A:** *"On the edge, it merges and compares the live sensor data with the well's own scattered documents."*  ·  *(~17 words / ~8s)*
> **🛠 Closes the 4C loop:** 4C ended on *"scattered… slow to assemble."* 6A answers the *"scattered"* directly — *"merges and compares… the scattered documents."* The data-stream + documents drawing together IS that answer on screen.
> **🛠 Detection wording (TRUTH / NO STRAW MAN):** *"merges and compares the live sensor data"* credits the **multivariate** nature of our scoring (🟡 OUR-CODE — true to our models) **without** claiming we detect earlier/better than advanced APM (SmartSignal/Mtell already do multivariate early detection — a superiority claim gets dismantled). Do NOT escalate this to "detects sooner" or "catches what others miss." The fuller pre-threshold-vs-threshold-SCADA detection story belongs in the **live demo's How It Works (tiers 1–2)**, where the models actually show it — not the cinematic intro.

**🎬 Beat 6B — the cited answer**  ·  *~5s*  ·  *(the convergence resolves)*
```
Photorealistic continuation of the fusion shot: the single bright converged point on the edge server settles and steadies into one calm, clear, glowing focus — the moment of resolution. Cinematic, dark background, cool blue and warm amber light now unified and steady rather than merging. Quiet confidence. No text, no labels, no UI, no logos.
```
> **🎙️ VO — Beat 6B:** *"The result: one cited, reviewable diagnosis — in seconds."*  ·  *(~9 words / ~5s)*
> **🛠 Closes the 4C loop (part 2):** 4C ended on *"slow to assemble when the decision can't wait."* 6B is the counter-punch — *"in seconds."* The visual settling from "merging" (6A) to "steady/resolved" (6B) mirrors chaos→clarity.
> **🛠 "Cited, reviewable" is load-bearing (TRUTH):** the diagnosis is **evidence-backed and human-checkable**, not a black-box guess — this is the trust hook that sets up the live demo's cited verdicts. Keep both words.
> **🛠 Continuity:** feed a frame of 6A as a reference ingredient so 6A→6B reads as the same converging light resolving.

---

### HAND-OFF — roll into the demo

**🎬 Beat 7 — dissolve toward the screen**  ·  *~6s*  *(optional; or just cut to the app)*
```
Photorealistic slow push-in toward a clean operations dashboard glowing on a monitor in the dark RTOC, the screen brightening to fill the frame, inviting the viewer in. Cool screen light. No readable text, no logos.
```
> **🎙️ VO — Beat 7:** *"Let's dive into the demo — and see GDC analyze a struggling well at the source."*  ·  *(~15 words / ~7s)*

➡️ **Cut to live screen recording.** From here, follow **V3 (cinematic)** or **V4 (operator-grounded)** for the demo voiceover, starting at the **"What is GDC / How It Works"** beat, then **Discern → Classify → Optimize**, and the close.

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
