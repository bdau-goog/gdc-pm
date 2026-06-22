# GDC ESP Ops Video — Veo Story Intro → Demo Hand-off (PER-BEAT VO)
**Pattern:** Modeled on the prior GDC CCS/DAS demo (narrated Veo B-roll intro that tells the whole story, then "Let's dive into the demo"). Cinema is **front-loaded**; the demo itself is live screen recording with voiceover (V3/V4 scripts).
**Structure:** **One Veo clip = one Vids scene = one short VO line.** ✅ **STATUS (Session BS+35):** the cold open is a **9-scene** structure (Scenes 1-9), all scenes designed and approved. **Scenes 1-6 are RENDERED** (Movement 1-2 problem half + the GDC-platform/sled bridge = Scene 6). **Scenes 7-9 remain to render**: pre-threshold scoring (Scene 7), operator-resolved fusion + cited diagnosis + HITL (Scene 8), and the dissolve hand-off (Scene 9). Movement 3 redesign is **APPROVED** (not void). The old "12 scenes / Beats 4A-4C, 5A-5B, 6A-6B" plan is **retired** — the problem half collapsed old Beat 3+4A into one Scene 3, and the solution half is now three literal scenes (Beats 5/6/7) plus the hand-off.
**Perspective:** Google Cloud, third-party. **Persona:** ESP operations / maintenance / asset-longevity leadership (CxO-safe). **No exact numbers spoken** (panel carries them).

> **⚠️ PRODUCTION TOOL — REVERTED TO VIDS/VEO FOR THE REMAINING BEATS (Session BS+35).** We have shifted the remaining solution-half beats (Scenes 7-9) **back to Vids/Veo to use the EXTEND capability**, which is now working there. This supersedes the BS+32 "Flow + Omni Flash + reference images" decision *for these beats only*. Plan: render Scene 7 (Mark's eyes), then **Extend** that clip into Scene 8 (Mark resolved, same desk/face/wardrobe) for automatic character continuity; Scene 9 (dissolve) is a separate short push-in. Scene 6's sled clip is already rendered and reused as-is. The Flow process notes below are retained as history for the already-rendered Scenes 1-6.

### SCENE ↔ BEAT MAP (the canonical 9-scene order)
| Scene | Beat | Subject | Render status |
|---|---|---|---|
| 1 | Beat 1 | Aerial field of blue christmas-tree wellheads | ✅ rendered |
| 2 | Beat 2 | Push-in: one wellhead + control/VFD skid | ✅ rendered |
| 3 | Beat 3 (merges old 3 + 4A) | Night alarm + "often easily diagnosed" concession | ✅ rendered |
| 4 | Beat 4B | The ambiguous alarm (operator hesitates) | ✅ rendered |
| 5 | Beat 4C | Scattered context (digital fragmentation, overhead) | ✅ rendered |
| 6 | Beat 5 | GDC edge platform — the three compute sleds (bridge) | ✅ rendered |
| 7 | Beat 6 | Pre-threshold scoring (Mark's focused eyes) — MORE TIME | ⬜ to render |
| 8 | Beat 7 | Operator resolved — fusion + cited Dx + HITL | ⬜ to render |
| 9 | Beat 8 | Dissolve toward the live dashboard (hand-off) | ⬜ to render |


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

> **⚠️ CONTINUITY IS DONE WITH A REFERENCE IMAGE OR EXTEND, NOT WITH WORDS.** Veo has **no memory between cold generations** — phrases like "the same desk/operator as Beat 3" in these prompts are only loose hints and will NOT reliably reproduce the prior shot. To make beats actually match, either (a) **feed a still frame from the prior clip as a reference/ingredient image**, or (b) **use Vids/Veo EXTEND** to continue the prior clip (the BS+35 method for Scenes 7→8). Then use the prompt to describe only the change (new angle, new action). Treat all "same as Beat N" prose below as intent for the human, not as something Veo enforces.

### MOVEMENT 1 — Industry context

**🎬 Beat 1 (Scene 1) — the field of wellheads (aerial, schema-starved)**  ·  *~8s*
```
Photorealistic elevated cinematic drone shot slowly descending over a vast flat caliche-gravel field in remote West Texas at golden hour. Spread across the field in a loose grid, dozens of identical christmas-tree wellheads recede toward the horizon — each one a vertical stack of flanged steel valves and spools about a man's height, painted glossy industrial blue, fitted with several bright red round handwheels projecting from the sides and small round pressure gauges. Short horizontal flowlines link each wellhead to slim steel gathering pipes that run in straight lines across the tan gravel. Long warm shadows, flat distant horizon, dust-free clean hardware. Smooth slow descending aerial motion, 35mm film look. Industrial precision, repetition, quiet scale.
```
> **🎙️ VO — Beat 1 (Scene 1):** *"Upstream oil and gas runs on engineering discipline — lifting every barrel as efficiently and safely as possible."*  ·  *(~17 words / ~8s)*
> **🛠 If a pumpjack appears:** keep the elevated/top-down framing (a nodding-donkey silhouette can't form from above) and lean harder on the color + repetition — *"rows of glossy blue valve stacks with bright red handwheels, identical and evenly spaced across a gravel field."* Pumpjacks are never painted blue-and-red valve stacks, so the color detail starves the schema.

**🎬 Beat 2 (Scene 2) — the wellhead + control skid (tight, schema-starved)**  ·  *~8s*  ·  *(same field as Beat 1, pushed in)*
```
Photorealistic slow push-in on a single christmas-tree wellhead firmly bolted to a low concrete base in the same gravel field as the wide aerial — a vertical stack of heavy flanged steel valves and spools about a man's height, painted glossy industrial blue, with several bright red round handwheels projecting from the sides. The framing favors the blue valve body and the red handwheels; any small fittings stay soft and out of focus. From the base, a horizontal steel flowline runs along the gravel and ties into a slim gathering pipe. A short distance behind sits a separate electrical control skid: a tall louvered stainless cabinet and a small boxy transformer, linked by conduit. Every piece of equipment is solidly connected — nothing floating or detached. The rest of the identical blue wellheads recede softly out of focus toward the golden-hour horizon. Shallow depth of field, warm low-sun grade matching the field shot, 35mm film look. Precision industrial hardware, clean and quiet.
```
> **🎙️ VO — Beat 2 (Scene 2):** *"Electric submersible pumps - ESPs - do that lifting. Maintaining them well keeps costs down and optimizes production."*  ·  *(FINALIZED wording, Session BS+33 — verbatim)*
> **🛠 Note:** this is the **same scene as Beat 1, just closer** — one wellhead sharp in front, the field soft behind. The pump itself is downhole (invisible); the surface story is the blue valve tree + the control/VFD skid beside it. Same hardware and grade as Beat 1 keep the wide→tight cut continuous; the tight framing leaves no room for a jack.
> **🛠 GAUGES — DON'T specify what Veo can't count (BS+32, the durable lesson).** Two successive prompts tried to pin the gauges ("exactly two… needle at mid-dial") and **both failed** — Veo rendered the wrong count/positions every time. Root cause: **video diffusion models cannot count discrete objects or place fine details on command** (same blind spot as six-fingered hands and garbled text). Every word you add about "gauges" *summons more gauge tokens* and makes it worse, not better. **Fix = stop specifying them entirely. Frame them out and blur them out:** push the composition to the **blue valve body + red handwheels** (the on-message part) and let any small fittings sit **soft / out of focus**. Gauge realism is a detail no viewer parses in a 7s clip — do not spend renders fighting it. **General rule for all hardware beats: describe the dominant silhouette + color, never a countable/precise small detail.**
> **🛠 GROUNDING — "pump connected to nothing" fix (BS+32 render):** an earlier render produced a **floating, disconnected pump-like object**. Two causes: (1) the word **"pump"** summons a surface skid-pump schema → **keep "pump" OUT of the visual prompt** (the ESP is downhole/invisible; "pump" lives only in the VO); (2) nothing forced the hardware to be plumbed in. **Fix = ground everything:** tree **"bolted to a low concrete base,"** an explicit **flowline → gathering-pipe tie-in**, skid **"linked by conduit,"** and a hard clause: **"Every piece of equipment is solidly connected — nothing floating or detached."**





---

### MOVEMENT 2 — The problem

**🎬 Beat 3 (Scene 3) — the night alarm (operator profile, no screen content)**  ·  *~8s*
```
Photorealistic medium shot of a single industrial control-room operator seen in three-quarter side profile at night, looking to the side at screens out of frame. They are a professional in a neat dark work shirt, expression calm and focused; they do NOT look at the camera. The soft cool blue glow of monitors washes across their face from the side, joined by a gentle, rhythmic pulsing amber light that casts slow warm flashes on their profile. The background is dark and soft, with banks of distant unreadable screens pushed completely out of focus into neat blue bokeh. Cinematic side-profile composition, shallow depth of field, 35mm film look, quiet night-shift focus. No screen content is visible in frame, no text, no letters, no logos, no graphics.
```
> **🎙️ VO — Beat 3 (Scene 3 — MERGES old Beat 3 + old Beat 4A):** *"Occasionally, monitoring systems trigger alarms, telling you a well is in trouble. Often, these are easily diagnosed."*  ·  *(FINALIZED wording, Session BS+33 — verbatim)*
> **🛠 SCENE 3 = the alarm + the concession in ONE shot (BS+33 restructure).** This single scene now carries both ideas the old Beat 3 and Beat 4A held separately: an alarm fires (old Beat 3 visual — operator at the monitors) AND most are routinely handled ("often easily diagnosed" = old Beat 4A's concession). The already-rendered Beat 3 operator footage covers it; the calm demeanor sells "easily diagnosed." **Old Beat 4A is now ABSORBED here — do not render it as a separate scene.**
> **🛠 Why side profile:** we tried an close-up, but Veo rendered a creepy head-on mugshot staring straight at the camera. The side profile or three-quarter view forces the subject to look off-camera at their work screens, keeping the illusion of a working RTOC.
> **🛠 Why no screen content:** we tried showing the alarm on a SCADA wall and on a single on-screen pump symbol — Veo fakes garbled toolbars/labels ("SCADA MIIPLUPUO", "CdNet") and renders unpredictable junk icons every time a UI is in frame. **The fix: never show the screen directly.** Convey the alarm purely through the **pulsing amber light on the operator's side profile**. No UI = no garbled text, and a focused side profile sells the operational moment cleanly.
> **🛠 If the operator looks at the camera:** hard-specify *"the operator looks off-camera to the side, three-quarter side profile, eyes focused on screens out of frame, they do NOT look at the camera lens."*
> **🛠 The "pump" is carried by the VO, not the visual** — this beat is about the human moment; the pump hardware already lives in Beats 1–2.

**🎬 Beat 4A — the clear-cut alarm (the easy majority) — ❌ MERGED INTO SCENE 3, DO NOT RENDER**  ·  *(reference only)*
```
Photorealistic medium shot of the same control-room operator from Beat 3, at the same desk, seen in three-quarter side profile, looking off-camera at their screens — they do NOT look at the camera. With calm, practiced confidence they reach forward and tap a key to acknowledge a routine alert, giving a small assured nod as the moment is handled in seconds. The pulsing amber accent from the previous beat steadies and cools back to calm blue. Banks of monitors stay softly out of focus as blue bokeh behind them. Same night-shift lighting, cool blue with a fading warm accent. Shallow depth of field, 35mm film look, quiet competence. No screen content visible, no text, no letters, no logos, no graphics.
```
> **🎙️ VO — Beat 4A:** ❌ **MERGED into Scene 3 (BS+33).** The "easily diagnosed" concession now lives in Scene 3's second sentence ("Often, these are easily diagnosed"). Do NOT render 4A separately. (Visual notes below retained only for reference if the concession is ever re-split.)
> **🛠 Why this beat exists (TRUTH / no straw man):** most alarms ARE routine and self-evident — a clean underload trip, an obvious overpressure, a comms fault. Conceding this up front is a **credibility signal** to the engineer audience and scopes our claim honestly: GDC's value is the *ambiguous* subset (Beat 4B), not every alarm. Without this concession, a production engineer dismisses the whole open as overclaiming.
> **🛠 Visual = confident & fast.** This beat should feel quick and assured (a few seconds, handled). The contrast with Beat 4B's slower "hunt" is what carries the meaning — pacing does the work.
> **🛠 Keep it screen-free** (same lesson as Beat 3): convey "resolved" through the operator's confident action + amber settling to calm blue, not through any rendered UI.
> **🛠 Continuity (do this, not the prose):** to match Beat 3's operator/desk, **feed a still frame of the Beat 3 clip as a reference ingredient** — the "same operator/desk" wording alone won't reproduce it.

**🎬 Beat 4B (Scene 4) — the ambiguous alarm (operator hesitates, no quick resolve)**  ·  *~6s*  ·  *(same operator/desk as Beat 3)*
```
Photorealistic medium shot of the same control-room operator from Beat 3, at the same desk, in three-quarter side profile, looking off-camera at their screens — they do NOT look at the camera. This time there is no quick resolution: the operator leans in slightly, brow tightening, one hand hovering near the keyboard but not acting, studying an unclear signal with quiet concern. The amber warning accent keeps pulsing, unresolved, rather than settling to calm blue. Banks of monitors stay softly out of focus as blue bokeh behind them. Same night-shift lighting, cool blue with a persistent warm amber accent. Shallow depth of field, 35mm film look, quiet uncertainty. No screen content visible, no text, no letters, no logos, no graphics.
```
> **🎙️ VO — Beat 4B (Scene 4):** *"But some alarms are ambiguous — the signals alone can't tell you the cause."*  ·  *(FINALIZED wording, Session BS+33 — verbatim)*
> **🛠 The contrast that carries the meaning:** 4A was fast/confident (amber settles to calm). 4B is the **inverse** — the operator hesitates, doesn't act, amber stays unresolved. Pacing + body language do the work; no screen needed.
> **🛠 Flow (3-beat concede→pivot→friction):** Scene 3 *"often easily diagnosed"* → Scene 4 (4B) *"But some are ambiguous — the signal alone can't tell you the cause"* → Scene 5 (4C) *"The context that **can** sits scattered…"*. The word **"can"** links Scene 4→5 (signal *can't* / context that *can* is scattered). Record each line on its own scene.
> **🛠 Screen-free** (same lesson as Beat 3): convey "stuck" through the lean-in + hovering hand + unresolved amber, not through any rendered UI.
> **🛠 Continuity (do this, not the prose):** feed a still frame of the Beat 3 clip as a **reference ingredient** — the "same operator/desk" wording alone won't reproduce it.

**🎬 Beat 4C (Scene 5) — the scattered context (FRAGMENTATION is the subject)**  ·  *~8s+ (use EXTEND if VO runs long)*  ·  *(same desk; slower, heavier)*
```
Photorealistic overhead top-down shot looking straight down onto the same dark industrial control desk from Beat 3, lit by cool blue screen glow with a warm amber desk-lamp spill from one side. Scattered across the desk are several DISCONNECTED digital devices showing incompatible siloed applications: a rugged tablet displaying a generic database entry form, a laptop showing an email inbox with an uncooperative document attachment, and a phone showing a separate system alert dashboard. The operator's two hands move rapidly between the devices—tapping the tablet screen, dragging a mouse on the laptop, typing on the keyboard—conveying the slow effort of manually cross-referencing and transcribing context between completely separate digital platforms. Everything is kept slightly soft so no text is legible. Slow, deliberate, slightly tense pacing, heavier than the previous beat. Shallow depth of field, 35mm film look. No physical paper, no printed sheets, no notebooks, no handwriting. No logos, no recognizable UI chrome, no audio-waveform or seismic-nebula imagery.
```
> **🎙️ VO — Beat 4C (Scene 5):** *"The context that can help is scattered across distributed systems — slow to assemble when the decision can't wait."*  ·  *(FINALIZED wording, Session BS+33 — verbatim)*
> **🛠 The fix vs. the old render:** a single tidy tablet reads as *normal work* and contradicts the VO. Make **fragmentation the subject** — MULTIPLE disconnected digital devices and windows (tablet, laptop, phone, separate app screens) the operator must physically interact with and reconcile. The **hands moving between separate screens and devices** + the **overhead angle** are what convey "scattered across disconnected systems, slow to assemble." That friction IS the story.
> **🛠 VO intent (the real friction):** the deciding context **exists** — but it's **fragmented across disconnected digital systems** (CMMS, lab portal, handover log, file shares) and **slow to find, combine, and decide from** under a live-event clock. Convey *fragmentation + retrieval/assembly friction*, not *distance* or *absence*. This is exactly the H1/H2 demo subset (look-alike telemetry: gas-interference-vs-drawdown, paraffin-mimicking-bearing-wear) and what GDC collapses into a cited diagnosis in seconds.
> **🛠 If the VO runs longer than the clip:** use the Veo/Vids **EXTEND** feature to lengthen this clip to match the line (validated as working), or let the scene hold a beat longer on the scattered desk. Don't rush the read — the slow "hunt" pacing is the point.
> **🛠 Why digital-only fragmentation (TRUTH gate):** a modern RTOC engineer's sources are entirely digital (PDFs, CMMS like Maximo/SAP, a digital handover log, shared files). Having paper or printed sheets on an RTOC desk is unrealistic. The fragmentation is purely digital: the data lives in **different, incompatible systems** that don't talk to each other. The multi-device and multi-window spread (tablet + laptop + phone) makes "disconnected systems" literal.
> **🛠 Veo garble dodge:** every screen risks fake text. Keep **all on-screen applications slightly soft / out of crisp focus** so they read as software layouts (headers, tables, loading spinners) without legible words. Reinforce *"no readable text, no recognizable UI chrome."* Overhead framing also reduces how much screen detail Veo tries to invent.
> **🛠 Continuity (do this, not the prose):** feed a still frame from Beat 3/4B as a **reference ingredient** so the desk/grade match — prompt prose like "same desk" won't reproduce it on its own. Use the prompt only to specify the *change* (overhead angle, scattered items). Keep the color/lighting identical so the cut reads as the same room.

---

### MOVEMENT 3 — The GDC solution (REDESIGN APPROVED — Session BS+34)

In this movement, we land the **operator benefit** as one affirmative, high-value spine that resolves the Diagnostic Gap:
1. **MORE TIME** — GDC's pre-threshold XGBoost multivariate models flag anomalous trends early, before failure is irreversible.
2. **MORE CONTEXT** — GDC automatically ingests and parses the well's own scattered, unstructured documents (shift notes, lab results, PVT reports, completion records) that no sensor system can read.
3. **MORE INSIGHT** — GDC evaluates the evidence to deliver a cited, reviewable differential diagnosis and proactive recommended action in seconds.
4. **HUMAN-IN-THE-LOOP CONTROL & SOVEREIGNTY** — The decision is handed off on-premise for final operator approval, keeping data fully secure inside the sovereign boundary.

To eliminate the Veo abstraction trap (which previously caused server room "fusion" and "data perimeter" visual failures), we **keep all abstract concepts in the Voiceover** and use only **highly realistic, concrete nouns** for our visuals: GDC hardware sleds and the operator resolved.

> **🛡️ NARRATIVE GUARDRAIL (PRIME DIRECTIVE / no straw man):** the pre-threshold detection edge in Scene 7 is claimed **only against threshold-only SCADA** (Tier 1: a single tag crossing a hard limit), **never against best-of-breed APM** (SmartSignal/PRiSM/Mtell — against which detection quality *converges*, per DEMO_MASTER §3 and NARRATIVE_GUIDANCE Tier table). "Before SCADA can alarm" = before the hard-limit trip, consistent with the 4–9-minute lead time on the H1 fluid-unloading scenario. The **categorical** moat is Scene 8's document-context fusion, which no sensor-based system can architecturally replicate.

---

**🎬 Beat 5 (Scene 6) — Bring GDC to the Operations Center (The Edge Platform)**  ·  *~8s*  ·  *✅ RENDERED*

```
Photorealistic cinematic macro shot inside a bright, spotless, climate-controlled enterprise data clean-room with perfectly clear, cold, dry, still air. The camera performs a slow, smooth tracking glide from left to right along the front edges of a small stack of three identical slim silver-white enterprise compute sleds mounted one above another, the focus racking gently from the near sled to the far one. Across the clean front faces, dozens of tiny status LEDs blink in green and amber, while a single steady green power LED glows on each unit. A crisp specular highlight travels slowly across the brushed-metal surfaces as the camera moves. A few blue and orange fiber patch cables catch the moving light. The dense ports stay soft and out of focus so they read as fine texture, never text. Bright, even, cool white lighting; clean dry air; immaculate surfaces. Only the three stacked sleds are in frame — no surrounding rack frame, no power strips, no outlets. Crisp, controlled, enterprise-grade, on-premise.
```

> **🎙️ VO — Beat 5 (Scene 6):** *"This is where Google Distributed Cloud comes in — it brings Google's AI to your data, instead of your data to the cloud."*  ·  *(RENDERED wording — verbatim to the delivered clip, BS+35)*
> **🛠 Value Point:** Physical on-premise edge hardware (Sovereignty) & the GDC inversion ("AI to the data"). This is the loved sled hardware clip, already successfully rendered; the VO is the BS+30 bridge line locked to the delivered take. Reuse the clip as-is.
> **🛠 STEAM FIX — starve the schema, don't negate it (BS+32 durable lesson):** The prior version said "no steam..." and still rendered steam. Fix = positive incompatible framing: "bright, spotless, climate-controlled clean-room" with "perfectly clear, cold, dry, still air" — a cold dry clean-room cannot have steam. No moody "dark room / cool blue" grade.
> **🛠 ADD MOTION:** Two motion layers drive the shot: (1) camera slow tracking glide + rack focus; (2) LEDs blinking (data traffic), specular highlights traveling, fiber cables catching light. No "heat-shimmer" (which triggers steam).
> **🛠 Siting:** GDC sits in the regional or corporate Real-Time Operations Center (RTOC), beside SCADA, inside the operator's security perimeter.

---

**🎬 Beat 6 (Scene 7) — Scoring the Combined Pattern (Pre-Threshold Faster Detection)**  ·  *~8s*  ·  *⬜ TO RENDER (Vids/Veo — base clip for the Extend chain)*

```
Photorealistic cinematic macro shot of the operator "Mark"'s eyes, focused and calm, reflecting the cool blue and green light of the workstation monitors. The camera performs a slow track across his profile as he monitors the system. Deep, quiet concentration; the blue-green light is steady and smooth, with no pulsing alarm amber. Shallow depth of field, 35mm film look, quiet night-shift focus. No screen content is visible in frame, no text, no letters, no logos, no graphics.
```

> **🎙️ VO — Beat 6 (Scene 7):** *"At the edge, GDC scores the combined pattern across all channels simultaneously — identifying the drift before SCADA can alarm."*  ·  *(~18 words / ~8s — trimmed to fit 8s, BS+34)*
> **🛠 Value Point:** Faster Detection (multivariate pattern matching without buzzwords) + More Time (identifying pre-threshold). See the NARRATIVE GUARDRAIL above — this edge is vs. threshold-only SCADA, not vs. elite APM.
> **🛠 Screen-free:** Convey "monitoring the pattern" purely through the steady blue-green reflections in the operator's focused eyes, avoiding any unrenderable screens.
> **🛠 Continuity / PRODUCTION (BS+35):** Render this in Vids/Veo as the **base clip of the Extend chain**. Feed a still frame of Mark from Scene 3/4 as the reference; this clip then **Extends into Scene 8** so Mark's face/wardrobe stay identical without re-stitching.

---

**🎬 Beat 7 (Scene 8) — Fusing the Unstructured Context (The Context Problem Resolved + HITL)**  ·  *~8s*  ·  *⬜ TO RENDER (Vids/Veo — EXTEND from Scene 7)*

```
Photorealistic medium shot of the same control-room operator "Mark" from Beat 3, at the same desk, seen in three-quarter side profile, looking off-camera at his screens. The tension from Beat 4B is gone: his brow is relaxed, and he has a calm, confident expression of quiet certainty. Across his face is a soft, steady, cool green and blue screen-glow, with no pulsing amber warning lights. Studying a clear recommendation, he gives a single, slow, assured nod of approval, and with simple deliberate motion, reaches forward and types a final key to authorize the proactive action. The background remains dark and soft, with distant unreadable screens pushed completely out of focus into neat blue bokeh. Cinematic side-profile composition, shallow depth of field, 35mm film look, quiet resolution. No readable text, no logos, no recognizable UI chrome.
```

> **🎙️ VO — Beat 7 (Scene 8):** *"Then, it automatically reads and fuses the well's complete document history — delivering a cited recommendation for operator approval."*  ·  *(~18 words / ~8s — trimmed to fit 8s, BS+34)*
> **🛠 Value Point:** More Context Ingested (sensors + documents) + More AI-Driven Insight (cited, reviewable recommendation) + Human-In-The-Loop Approval (nod of approval / operator action) + Sovereignty (runs on-premise).
> **🛠 How this resolves the narrative arc:** This beat is the **mirror image** of Beat 4B / Scene 4 (the ambiguous alarm / operator hesitates). Scene 4 showed hesitation, amber pulsing warning, and hovering hands. Scene 8 shows quiet confidence, cool green/blue steady glow, a single slow nod of approval, and a decisive action (HITL).
> **🛠 Screen-free:** Avoids garbled text. Convey "resolution" purely through Mark's relaxed body language, green-glow lighting, and decisive nod.
> **🛠 Continuity / PRODUCTION (BS+35):** **EXTEND from the Scene 7 clip** (Mark's eyes → pull back to the resolved nod + authorize keystroke). Extend keeps Mark's face/wardrobe/desk identical automatically — the reason we reverted to Vids/Veo. If Extend drifts on the tail, trim in Vids or re-run with a Scene 7 last-frame reference.

---

### HAND-OFF — Roll into the Demo

**🎬 Beat 8 (Scene 9) — Dissolve toward the screen**  ·  *~6s*  ·  *⬜ TO RENDER*

```
Photorealistic slow push-in toward a clean operations dashboard glowing on a monitor in the dark RTOC, the screen brightening to fill the frame, inviting the viewer in. Cool screen light. No readable text, no logos.
```

> **🎙️ VO — Beat 8 (Scene 9):** *"Let's dive into the live system, and see GDC analyze a struggling well at the source."*  ·  *(~17 words / ~7s)*
> **🛠 Handoff:** Dissolve from the cinematic intro directly into the actual live web-browser UI of the GDC Advisor kiosk. A short separate push-in (not part of the Extend chain) — Veo never needs to render a legible dashboard because the cut lands on the real app.

➡️ **Cut to live screen recording.** From here, follow **V3 (cinematic)** or **V4 (operator-grounded)** for the demo voiceover, starting at the **"What is GDC / How It Works"** beat, then **Discern → Classify → Optimize**, and the close.

---

## PRODUCTION PROCESS — TOOLING (BS+35 update at top; Flow history retained below)

> **✅ CURRENT METHOD (Session BS+35) for the remaining solution-half beats (Scenes 7-9):** generate in **Vids/Veo using EXTEND.** Extend is now working in our Vids/Veo path and is the cleanest way to hold the operator "Mark" consistent across Scene 7 → Scene 8 (render Scene 7, Extend it into Scene 8). Scene 6's sled clip is already rendered (reuse as-is); Scene 9 is a short standalone dissolve. Scenes 1-6 are done. This supersedes the Flow/Omni-Flash approach below **for the remaining beats** — that approach is retained only as the record of how Scenes 1-6 were produced.

**Why Flow was used for Scenes 1-6 (history):** every failure in the original Vids-embedded Veo workflow traced to **no cross-shot context** — Veo regenerated cold each time (re-inventing servers), and the only way to steer it was retyping the whole prompt. That produced the explosion → liquid → laser-beam churn on the abstract "fusion" beat. Flow's Characters + Ingredients gave the cross-shot consistency the per-beat prompts assume, and was the right tool for the problem-half operator beats and the sled macro.

**What is settled regardless of tool:** the abstract "fusion" effect is **concept-hostile to Veo**, not tool-hostile — it failed 4x because "data merging" over-literalizes into hazards/sci-fi. The **EFFECT CUT** decision (solution beats = calm literal nouns — sleds, the operator resolved — with the VO carrying the abstract idea) stands in any tool. Don't reopen it.

**Per-beat prompts in this doc are tool-agnostic** — paste them into Vids/Veo or Flow as-is. The "ingredient image" and "Extend" notes map onto either tool's continuity features.

### Flow mechanics — recorded BS+32 (history for Scenes 1-6; Extend now works in our Vids/Veo path per BS+35)
- **Clip length is ~8–10s, NOT hard-locked at 8s.** Veo 3.1 treats the "8s" selector as a target and may render up to ~10s. This is fine — our VO lines are written to ~7–8s, so the extra 1–2s lets the visual breathe (trim head/tail in Vids). At 10s, glance at the final ~2s of operator (Mark) and hardware shots for coherence drift; trim the tail in Vids if a face/server morphs.
- **Ingredients use Nano Banana Pro (the image model), NOT Nano Banana 2.** Nano Banana = Google's still-image model; it generates/edits the reference Ingredients (well-field, sled stack, Mark portrait) that Veo then animates. Use **Pro** — better text suppression + detail/negative adherence, which matters for fighting garbled hardware labels and pumpjack bias. Credits aren't a constraint.
- **Veo's video-output count is set on the VIDEO generation bar, NOT in the Agent-settings "Image generation default" panel.** The x4 in the image-default panel only makes 4 *image* variations (Ingredients). To get the x4 "best-of-4 against the steam/spark/pumpjack lottery," set outputs on the Veo bar itself, or simply re-run the same prompt 3–4 times.
- **Flow-specific caveat (why we left Flow for the remaining beats):** in Flow, **Extend returned blank video** on every model tried, and **Veo 3.1 Quality could not use reference images** (it silently rendered text-only). In Flow the only working continuity mechanism was therefore still-frame **reference images** on **Omni Flash**. BS+35 reverted Scenes 7-9 to our Vids/Veo path specifically because **Extend works there**, removing the need to re-stitch Mark via reference frames.
- **CONTINUITY methods:** (a) **Extend** (BS+35, Scenes 7→8 — preferred where it works); (b) **still-frame reference image** (the fallback used for Scenes 1-6 — each beat that must match a prior one takes a still frame from the prior clip and the prompt describes only the change). Win condition is **clips that cut together under per-scene VO**, NOT frame-perfect continuity — the per-scene VO structure forgives minor grade drift.
- **If grade drifts between a beat and its reference:** add a one-line grade-lock to the prompt, e.g. *"warm golden-hour light, low sun, long shadows, identical color grade to the reference image."*

**Guardrails (unchanged, any tool):** no readable screens/UI (garble); no Dell branding + never feed the Dell photo as an ingredient; hard-negate steam/sparks/fire/liquid/beams; operator three-quarter side profile, never to camera; schema-starve outdoor beats (blue valve-tree, never "oil field/pumpjack").




---

---

## HOW TO RECORD PER-SCENE VOICEOVER IN GOOGLE VIDS
The point of per-beat VO: **each scene carries its own narration**, so sync is automatic.

1. **One scene per beat.** You'll have **9 intro scenes** (Scenes 1-9 per the SCENE ↔ BEAT MAP at the top); drop each beat's Veo clip on its scene.
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
| A — Veo intro | Scenes 1–9 (5 problem-half + sled bridge + 2 solution + hand-off) | 9 scenes × ~7s | ~1:00–1:10 |
| B — Live demo | How It Works + H1 + H2 + H3 + close | ~430 words | ~4:00 |
| | **Total** | | **~5:00–5:10** | (comfortably under 6:00) |

---

## NOTES
- **I can author but not watch Veo output.** Generate each beat, eyeball it yourself (or via a vision-capable tool), regenerate as needed. Tell me which beats fight you and I'll retune those prompts.
- **Continuity:** all 9 scenes play **back-to-back**. Aim for similar grade/color across clips so the cut feels continuous even though each carries its own VO line. **Veo has no cross-generation memory** — to actually match a prior shot (operator, desk, wellhead, server), use **Extend** (Scenes 7→8) or **feed a still frame of that clip as a reference/ingredient image**, and let the prompt describe only the change. "Same as Beat N" prose is a hint for you, not an instruction Veo can follow.
- **Minimum viable intro** if short on time: Scenes **1, 3, 5, 6, 8** still tell the whole story (context → problem → solution → demo) in ~40s. (Scene 2 ESP detail and Scene 4 hesitation are the first to trim; Scene 5 carries the core "scattered context" value point and Scene 8 carries the resolution.)
