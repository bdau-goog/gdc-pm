# GDC Ops Video — Veo Prompt Sheet (copy-paste ready)
**Use with:** Google Vids → right rail → **Veo**. Paste one prompt, generate, regenerate until you like it, then drop the clip on the slide.
**Pairs with:** `VIDEO_SCRIPT_OPS_VIDS_V3_NUMBERFREE.md` / `V4_GROUNDED.md` (the narration sits over these B-roll shots).

## ⚠️ REALISM GUARDRAILS (validated against docs/rag_source/esp_manual.md)
- **ESP wells = LOW-PROFILE CHRISTMAS-TREE WELLHEADS, never beam pump jacks.** Always add *"NO beam pump jacks, no nodding donkeys"* to outdoor shots (Veo's default oil field is rod-pump jacks — wrong lift method).
- **VFD is a SEPARATE surface cabinet + step-up transformer on a skid set back from the wellhead** — NOT bolted to the christmas tree. Don't fuse them.
- **Hot-oil treatment** connects a **service truck at the wellhead** (down tubing/annulus), not the chemical-injection port.

---

## How to use (Veo-in-Vids practicalities)

- Veo makes **~8-second** clips. Keep one **single camera move** per prompt (these are written that way).
- Set the clip's **aspect ratio to 16:9** in Veo before generating.
- Veo tends to **invent text/labels** — every prompt below already says *"no text overlays, no on-screen text, no UI."* Keep that line.
- If a result adds captions or looks cartoonish, **regenerate** (same prompt) — outputs vary run to run.
- These are **B-roll** (establishing/atmosphere). The actual product = your screen recording; Veo just opens and bridges sections.

---

## SCENE 1 — COLD OPEN  *(Section 1 of the script)*
```
Photorealistic cinematic drone shot slowly descending toward a single LOW-PROFILE electric submersible pump wellhead (a christmas tree) on a Permian Basin oil pad at night, West Texas, summer, with a SEPARATE electrical control skid set back a few meters — a variable frequency drive cabinet and a step-up transformer — lit by one amber sodium work-light. A row of identical low-profile wellheads fades into the dark toward the horizon. Clear star-filled sky, calm and quiet. Dark industrial aesthetic, deep blue-black sky with warm amber pools of light, 35mm film look, shallow depth of field. IMPORTANT: NO beam pump jacks, NO nodding donkeys, NO derricks. No text overlays, no on-screen text, no UI, no logos.
```


## SCENE 1b — INTERIOR (optional pair for the cold open)
```
Photorealistic cinematic slow dolly-in toward the back of a single operator sitting alone in a dim Real-Time Operations Center, face lit blue-white by a wall of monitors showing trending industrial sensor graphs, one amber alarm banner glowing. On the desk beside the keyboard, a thick manila well file folder and a cold cup of coffee. Quiet night-shift mood. Cool monitor-blue light against warm desk-lamp amber, 35mm, shallow depth of field, rack focus from the screens to the folder. No text overlays, no readable on-screen text, no logos.
```

---

## SCENE 2 — THE EDGE SERVER  *(Section 2 — "What GDC is")*
```
Photorealistic macro shot with a gentle slow push-in on a small rack-mounted server inside a field equipment skid, status LEDs breathing steady green, neat fiber and copper cabling. Through a window behind it, a dark oil pad at night. Compact, quiet, on-premise hardware at the edge of the field. Cool blue key light with one warm practical light, cinematic, shallow depth of field. No text overlays, no readable labels, no logos.
```

---

## SCENE 3 — SAME SIGNAL, OPPOSITE CAUSES  *(Section 3 — H1 Discern)*
```
Photorealistic split-screen cross-section of a steel oil well, X-ray-clarity diagnostic style, slow simultaneous push-in on both halves. LEFT: an electric submersible pump intake submerged in fluid with a small pocket of gas bubbles drifting into the spinning impeller. RIGHT: the same pump with the fluid level dropped below the intake, the impeller turning in sandy partial fluid with fine sand grains settling on the metal faces. Mechanically precise, cool blue clinical lighting. Only motion is the bubbles on the left and drifting sand on the right. No text overlays, no labels, no UI.
```

---

## SCENE 4 — THE TREATMENT THAT WAS MISSED  *(Section 4 — H2 Classify)*
```
Photorealistic macro time-lapse inside an oil production tubing pipe: warm golden crude rising while pale crystalline paraffin wax slowly builds along the steel inner wall, gradually narrowing the bore. Locked-off camera, no movement, let the wax visibly close in. Warm amber crude against cold pale steel, clinical and precise. No text overlays, no labels, no UI.
```

## SCENE 4b — THE TRUCK AT THE WRONG WELL (optional pair)
```
Photorealistic slow lateral dolly across a cold Permian Basin morning revealing a hot-oil service truck connected at a distant low-profile wellhead — orange-jacketed hoses running to the christmas tree, steam rising from the heated oil — while in the foreground a nearer identical ESP wellhead stands alone with no truck and no hoses attached. Pale winter palette, low golden sun, dust in the air. The absence of service at the near well is the focus. NO beam pump jacks, no nodding donkeys. No text overlays, no labels, no logos.
```


---

## SCENE 5 — ONE PAD, ONE GAS LIMIT  *(Section 5 — H3 Optimize)*
```
Photorealistic high aerial quarter-arc orbit over a Permian Basin well pad at golden hour: six identical electric submersible pump wellheads in two rows of three, gathering lines converging to a central manifold, a midstream gas-compressor station with a metering skid in the distance. Warm late-afternoon light, long shadows across caliche gravel. Smooth cinematic drone motion. No text overlays, no on-screen numbers, no labels, no logos.
```

## SCENE 5b — EDGE HOLDS IN THE STORM (optional pair)
```
Photorealistic shot of a Starlink satellite dish on the roof of a field operations trailer, beaded with rain, distant lightning on the horizon at dusk. Handheld subtle camera shake conveying the storm. Cut feeling of tension. Cold storm-blue exterior light. No text overlays, no labels, no logos.
```

---

## SCENE 6 — FIRST LIGHT (CLOSE)  *(Section 6 — bookend to Scene 1)*
```
Photorealistic cinematic slow crane-up at dawn over the same Permian Basin well pad from the opening shot, work-lights now off, the electric submersible pump wellheads operating steadily against a pale gold sunrise sky. Calm, resolved, hopeful mood. Warm soft sunrise palette, long gentle shadows, smooth crane motion rising to a wide shot of the running field. No text overlays, no on-screen text, no logos.
```

---

## SUGGESTED MINIMUM SET (if you only generate a few)
1. **Scene 1** (cold open) — essential opener.
2. **Scene 3** (split-screen well) — strongest visual for the H1 story.
3. **Scene 5** (pad aerial) — establishes the "whole field" for H3.
4. **Scene 6** (dawn close) — clean ending.
The 1b / 4b / 5b pairs are nice-to-have bridges; add them if you have time.

## Prompt-tuning tips
- If Veo adds **captions/watermarks/UI**: regenerate; if persistent, append *"absolutely no text, no captions, no watermark."*
- If it looks **too CGI/game-like**: append *"shot on 35mm film, photojournalistic realism, natural lighting."*
- If **equipment looks wrong**: keep the exact nouns (christmas tree, VFD cabinet, impeller, intake, tubing wall, metering skid, gathering lines, hot-oil truck) — Veo renders O&G hardware far better with correct terms.
- Keep prompts **short**; overly long prompts get truncated and drift.
