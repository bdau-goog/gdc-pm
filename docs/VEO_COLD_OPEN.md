# GDC ESP Ops Video — Veo Story Intro → Demo Hand-off (PER-BEAT VO)
**Pattern:** Modeled on the prior GDC CCS/DAS demo (narrated Veo B-roll intro that tells the whole story, then "Let's dive into the demo"). Cinema is **front-loaded**; the demo itself is live screen recording with voiceover (V3/V4 scripts).
**Structure:** **One Veo clip = one Vids scene = one short VO line.** Seven beats ≈ **~60s**, then cut to the live demo (~4–4.5 min). Total **< 6:00**.
**Perspective:** Google Cloud, third-party. **Persona:** ESP operations / maintenance / asset-longevity leadership (CxO-safe). **No exact numbers spoken** (panel carries them).

---

## ⚠️ DEFEATING VEO'S PUMPJACK BIAS (read first — negative prompts DON'T work)
Veo (like most video models) **ignores "no pump jacks"** — naming the token and saying "oil field" both summon the nodding-donkey schema. Stop fighting it with negatives; **starve the schema instead:**
1. **Never say "oil field," "oil well," "oil pad," "pumpjack," or "nodding donkey."** Even in a negative, those words bias the output.
2. **Describe only the specific object + its setting**, using non-oil framing: *"a low, finned valve-tree wellhead on a gravel industrial pad,"* *"an industrial wellsite,"* *"a remote energy facility."*
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

### MOVEMENT 1 — Industry context

**🎬 Beat 1 — the wellsite (aerial, schema-starved)**  ·  *~8s*
```
Photorealistic top-down cinematic drone shot slowly descending over a flat gravel industrial pad in remote West Texas at golden hour. On the pad: a cluster of low, compact finned valve-tree assemblies (steel valve stacks about waist-to-chest height), each linked by small-diameter steel gathering pipes to a central manifold, with a separate electrical control skid holding a tall metal cabinet and a boxy transformer set a few meters apart. Flat caliche gravel, long warm shadows, distant horizon. Smooth slow aerial motion, 35mm film look. Industrial precision, clean and quiet.
```
> **🎙️ VO — Beat 1:** *"Upstream oil and gas runs on engineering discipline — lifting every barrel as efficiently and safely as possible."*  ·  *(~17 words / ~8s)*
> **🛠 If a pumpjack appears:** remove "industrial pad/wellsite" entirely → *"a gravel equipment yard with a cluster of finned steel valve-stack assemblies and a control skid."* Top-down framing helps most.

**🎬 Beat 2 — the wellhead + control skid (tight, schema-starved)**  ·  *~8s*
```
Photorealistic tight close detail of a single low, compact finned steel valve-tree assembly (a stack of flanged valves and gauges about chest height) on flat gravel, with a separate electrical control skid a few meters behind it — a tall louvered metal cabinet and a boxy step-up transformer. Slow push-in, shallow depth of field, golden-hour light, 35mm film look. Precision industrial hardware, clean and quiet.
```
> **🎙️ VO — Beat 2:** *"Electric submersible pumps do that lifting. Keep them running, and lifting costs stay down and production stays online."*  ·  *(~18 words / ~8s)*
> **🛠 Note:** the pump itself is downhole (invisible); this beat shows the surface valve tree + VFD/transformer skid. Tight framing leaves no room for a jack.


---

### MOVEMENT 2 — The problem

**🎬 Beat 3 — the night alarm**  ·  *~8s*
```
Photorealistic interior of a dim Real-Time Operations Center at night, one operator at a wall of monitors showing trending industrial sensor graphs, a single amber alarm banner active. Slow dolly-in on the operator. Cool monitor-blue light, quiet night-shift tension, 35mm, shallow depth of field. No readable on-screen text, no logos.
```
> **🎙️ VO — Beat 3:** *"But when an alarm fires at night, the sensors say a pump is in trouble — not why."*  ·  *(~17 words / ~8s)*

**🎬 Beat 4 — the context that isn't on the screen**  ·  *~9s*
```
Photorealistic close-up rack-focus from a glowing monitor to a thick manila well-file folder on the desk beside the keyboard — handwritten notes and a lab report just visible inside. The paper is in sharp focus, the screen soft behind it. Warm desk-lamp amber against cool screen-blue. No readable text, no logos, no UI.
```
> **🎙️ VO — Beat 4:** *"The deciding context lives in documents — shift notes, lab results, service histories — siloed, far from the live signal."*  ·  *(~19 words / ~9s)*

---

### MOVEMENT 3 — The GDC solution

**🎬 Beat 5 — bring the cloud to the edge**  ·  *~8s*
```
Photorealistic macro slow push-in on a small rack-mounted server inside a field equipment enclosure at night, status LEDs breathing steady green, neat fiber and copper cabling, a dark gravel yard faintly visible through a window behind it. Compact, quiet, on-premise. Cool blue key light with one warm practical. No text overlays, no readable labels, no logos.

```
> **🎙️ VO — Beat 5:** *"Google Distributed Cloud brings Google's AI on-premise, inside the operator's perimeter — where the data already lives."*  ·  *(~16 words / ~8s)*

**🎬 Beat 6 — fusion (telemetry meets documents)**  ·  *~8s*
```
Photorealistic abstract-but-grounded shot: a clean stream of light representing live sensor data and a stack of physical field documents drawing together into a single bright point on the edge server, conveying fusion of data and documents. Cinematic, dark background, cool blue and warm amber light merging. No text, no labels, no UI, no logos.
```
> **🎙️ VO — Beat 6:** *"It reads the live sensors and the well's own documents together — a cited, reviewable diagnosis in seconds."*  ·  *(~17 words / ~8s)*

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

1. **One scene per beat.** You'll have 7 intro scenes; drop each beat's Veo clip on its scene.
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
| A — Veo intro | Beats 1–7 (per-beat VO) | 7 scenes × ~8s | ~0:55–1:00 |
| B — Live demo | How It Works + H1 + H2 + H3 + close | ~430 words | ~4:00 |
| | **Total** | | **~5:00–5:15** | (comfortably under 6:00) |

---

## NOTES
- **I can author but not watch Veo output.** Generate each beat, eyeball it yourself (or via a vision-capable tool), regenerate as needed. Tell me which beats fight you and I'll retune those prompts.
- **Continuity:** beats 1–7 play **back-to-back**. Aim for similar grade/color across clips so the cut feels continuous even though each carries its own VO line.
- **Minimum viable intro** if short on time: beats **1, 3, 4, 5, 7** still tell the whole story (context → problem → solution → demo) in ~40s.
