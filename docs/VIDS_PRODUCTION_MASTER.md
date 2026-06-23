# GDC ESP Ops Video — Vids Production Master (Shot Bible)
**Version:** BS+38 · **Branch:** feature-trio-clean · **Date:** 2026-06-22
**Purpose:** Single reproducible bible for every scene in the GDC ESP Operations video. Anyone with access to the GDC app, the Vids project, and this document can rebuild or update the video from scratch.
**Structure:** Part A (9 Veo cold-open scenes, all DONE) → Part B (31 live-capture demo scenes, record-ready). Both sides map to the same three value points.

---

## DOCUMENT MAP
| File | Role |
|---|---|
| **This file** | Shot bible — Direction Cards for every scene; sovereignty spine; alignment table |
| `docs/VEO_COLD_OPEN.md` | Full Veo prompts + production notes for Part A (Scenes 1–9) |
| `docs/DEMO_VO_PERPANEL.md` | Canonical per-panel VO reference + verified app-label alignment table |
| `docs/RECORDING_GUIDE.md` | MacBook capture setup (window size, crop, export spec) |
| `docs/VIDEO_SCRIPT_OPS_VIDS_V4_GROUNDED.md` | Extended V4 narration + brand/marketing checklist |

---

## PART A ↔ PART B ↔ APP ALIGNMENT SPINE
Every demo section maps to a value point first stated in the cold open and echoed by a real app state.

| Value Point | Cold Open (Part A) | Demo section (Part B) | Real app state |
|---|---|---|---|
| **MORE TIME** — pre-threshold scoring | Scene 7 (GDC amber marker before SCADA red marker in GDC Advisor screenshot) | H1-S2 (new) | `gdc_detect_idx` (~27) fires before `alarm_idx` (~48) in `h1ReplayData` |
| **MORE CONTEXT** — document fusion | Scene 8 (Mark authorizes; amber lamp out) | H1-S4 / H2-S3 (3-doc cascade) | `h1RagRevealed` / `h2VerdictRevealed` → doc cards appear sequentially |
| **HITL / SOVEREIGNTY — on-prem** | Scene 8 (nod + authorize) | H1-S5 / H2-S4 | `GDC Agent · Action package ready · Awaiting RTOC approval` → `✔ Approve & Execute` |
| **SOVEREIGNTY SPECTRUM** — H1/H2 air-gap, H3 connected | Intro Slide 3 plant (Deployment Models) | H2→H3 Bridge scene (new) + H3 Slide 3 payoff | Intro `s3` slide; H3 `Cloud Searches. Edge Enforces.`; Vizier sends only Hz + score |

---

## SOVEREIGNTY SPINE (three explicit moments)

### PLANT — Intro Scene 0.3 (Slide 3 — Deployment Models)
Extend the existing VO to bridge forward:
> *"…a managed connected rack, software on your own hardware, or a fully air-gapped appliance for the most remote sites. **You'll see both ends of that spectrum today.** Let's see it work."*

### BRIDGE — new scene between H2 Close and H3 (see §BRIDGE below)
> *"The first two cases ran entirely on-prem — air-gap capable, no cloud required. The third case is the connected model: it reaches GCP for Bayesian search — but only candidate setpoints and scores leave the site. Your data never follows. And safety stays local."*

### PAYOFF — H3-S3 + H3-S5 (existing lines, now carry the sovereignty resolution)
H3-S3: *"…more daily production, with gas held just under the ceiling."*
H3-S5: *"The temperature limit is enforced on the edge — so if the link drops mid-search, safety never drops with it."*

---

## SCENE DIRECTION CARD SCHEMA
Each card below uses this structure:
```
### [ID] — [Title]   ·  [duration]  ·  [STATUS]
SOURCE      : Veo render | Live screen capture | Still image | Hybrid
APP STATE   : (live only) tab · toggle · trigger/marker — exact preconditions for capture
VISUAL      : what is on screen / what to frame
CAMERA/MOVE : recording-time action + post-production move (zoom/crop)
VO          : "verbatim line"  (number-free)
PANEL QUOTE : fixed on-screen value the camera move "quotes" (panels carry the numbers)
ASSET REF   : source Veo prompt section / screenshot filename / clip name
CONTINUITY  : Extend base / ingredient image / grade-lock (Veo only) / echo in Part B
```

---

# PART A — VEO COLD OPEN · ~65s · STATUS: ALL DONE

> Full Veo prompts and production notes live in `docs/VEO_COLD_OPEN.md`. Cards below capture the final VO and status; **do not re-render** unless explicitly noted.

---

### A1 — The Field of Wellheads   ·  ~8s  ·  ✅ DONE
```
SOURCE      : Veo render
VISUAL      : Aerial drone descending over Permian gravel field; grid of blue christmas-tree
              wellheads with red handwheels; gathering lines running to horizon
CAMERA/MOVE : Slow descending drone; 35mm grade; golden hour
VO          : "Upstream oil and gas runs on engineering discipline — lifting every barrel
              as efficiently and safely as possible."
PANEL QUOTE : (none — establishing)
ASSET REF   : VEO_COLD_OPEN.md Beat 1
CONTINUITY  : Grade and hardware color lock the field identity for A2
```

### A2 — Wellhead + Control Skid (push-in)   ·  ~8s  ·  ✅ DONE
```
SOURCE      : Veo render
VISUAL      : Tight push-in on single blue valve-tree wellhead; VFD skid in background;
              flowline grounded to concrete base
CAMERA/MOVE : Slow push-in; shallow DOF; wellheads soft in background
VO          : "Electric submersible pumps - ESPs - do that lifting. Maintaining them well
              keeps costs down and optimizes production."
PANEL QUOTE : (none — hardware context)
ASSET REF   : VEO_COLD_OPEN.md Beat 2
CONTINUITY  : Same grade/field as A1; starve pumpjack schema (blue+red only)
```

### A3 — Night Alarm (operator profile, concession)   ·  ~8s  ·  ✅ DONE
```
SOURCE      : Veo render
VISUAL      : Operator three-quarter side profile; cool blue monitor glow; pulsing amber
              accent; screens out of frame; no screen content
CAMERA/MOVE : Static medium shot; 35mm night-shift grade; amber pulsing
VO          : "Occasionally, monitoring systems trigger alarms, telling you a well is in
              trouble. Often, these are easily diagnosed."
PANEL QUOTE : (none — human moment; concession delivers credibility)
ASSET REF   : VEO_COLD_OPEN.md Beat 3 (merges old 3 + 4A)
CONTINUITY  : Mark's three-quarter profile / navy shirt establish operator identity for A4, A5, A7A, A8
```

### A4 — Ambiguous Alarm (operator hesitates)   ·  ~6s  ·  ✅ DONE
```
SOURCE      : Veo render
VISUAL      : Same operator, same desk; leans in; hand hovering near keyboard; amber
              stays unresolved; no screen content
CAMERA/MOVE : Same grade as A3; amber unresolved — does NOT settle to blue
VO          : "But some alarms are ambiguous — the signals alone can't tell you the cause."
PANEL QUOTE : (none — body language carries meaning)
ASSET REF   : VEO_COLD_OPEN.md Beat 4B
CONTINUITY  : Continuity from A3 via reference ingredient
```

### A5 — Scattered Context (fragmentation)   ·  ~8s  ·  ✅ DONE
```
SOURCE      : Veo render (over-the-shoulder approved take — BS+35)
VISUAL      : Mark at console; eyes hunting across several incompatible monitors + rugged
              tablet; all screens slightly soft; no paper, no legible text
CAMERA/MOVE : Over-the-shoulder; slow deliberate pacing
VO          : "The context that can help is scattered across distributed systems — slow to
              assemble when the decision can't wait."
PANEL QUOTE : (none — fragmentation is shown through operator action + incompatible screens)
ASSET REF   : VEO_COLD_OPEN.md Beat 4C
CONTINUITY  : Continuity from A3/A4 via reference ingredient
```

### A6 — GDC Edge Platform (sled hardware)   ·  ~8s  ·  ✅ DONE (LOVED CLIP — DO NOT RE-RENDER)
```
SOURCE      : Veo render
VISUAL      : Three slim silver-white enterprise compute sleds; LEDs blinking; fiber cables;
              clean bright climate-controlled room; no surrounding rack
CAMERA/MOVE : Slow tracking glide L→R; rack-focus near-to-far; specular highlight traveling
VO          : "This is where Google Distributed Cloud comes in — it brings Google's AI to your
              data, instead of your data to the cloud."
PANEL QUOTE : (none — hardware sovereignty)
ASSET REF   : VEO_COLD_OPEN.md Beat 5 (Scene 6)
CONTINUITY  : Reuse as-is; also candidate for BRIDGE visual (A6 clip can back sovereignty bridge VO)
```

### A7A — Pre-Threshold Detect (Mark's down-left focus)   ·  ~3s  ·  ✅ DONE
```
SOURCE      : Veo render
VISUAL      : Mark seated at RTOC; strong hard down-left head movement to desk monitor;
              multi-channel screen-light palette; cool blue + teal + amber; no spoken dialogue
CAMERA/MOVE : Medium shot; shallow DOF; Mark never faces camera; 35mm
VO          : "Using your secured networks and data..."
PANEL QUOTE : (none — short sovereignty/human setup over operator)
ASSET REF   : VEO_COLD_OPEN.md Beat 6 (7A)
CONTINUITY  : 7A is the Extend base for A8 — do NOT re-render this clip
AUDIO       : MUTE Veo audio in Vids; VO recorded in Vids per-scene
```

### A7B — Pre-Threshold Detect (GDC Advisor screenshot reveal)   ·  ~6-7s  ·  ✅ DONE
```
SOURCE      : Hybrid — fade from A7A into REAL GDC Advisor screenshot (no Veo)
APP STATE   : H1 tab · GDC Advisor view · scrubber at gdc_detect_idx (~27)
              → DETECTION MOMENT: amber GDC marker (~9 min left) + red SCADA marker (~18 min left);
              docs loading, NO verdict yet. "WELL A-3 — BASELINE MONITORING · hs=0.9029 ·
              XGBoost routing score" + "RETRIEVED CONTEXT — ALLOYDB PGVECTOR (< 2S)" header visible
VISUAL      : Both markers in frame; hold ~1.5s on the gap; then drift push-in + pan up-right
CAMERA/MOVE : [START] both markers; [DRIFT] slow push-in + pan up-right along declining PIP/Current;
              [SETTLE] land on Decision Console / pgvector header (no doc cards, no recommendation)
VO          : "...GDC combines and evaluates multiple sensor streams in real time —
              identifying the developing issue."
PANEL QUOTE : Amber GDC marker LEFT of red SCADA marker = the lead-time gap = the evidence
ASSET REF   : Screenshot built BS+36; VEO_COLD_OPEN.md Beat 6 (7B)
CONTINUITY  : Same screenshot/recording as H1-S2 (Part B) — they echo each other
AUDIO       : Record A7A + A7B VO as one continuous take; pause falls on the fade
```

### A8 — Operator Authorized (lamp out)   ·  ~7s  ·  ⚠ TO RENDER (fresh cold render — NOT Extend)
```
SOURCE      : Veo render — FRESH COLD RENDER (Extend kept the lamp on — wrong)
VISUAL      : Mark at desk; same navy shirt; same RTOC grade. Four-beat sequence:
              (1) calm satisfied certainty; (2) one hand taps authorize key; (3) amber
              desk-lamp dims and goes completely dark; (4) Mark settles to cool blue light.
              Lamp-out is the DOMINANT visual event — unmistakable.
CAMERA/MOVE : Medium three-quarter side profile; shallow DOF; 35mm
VO          : "GDC then fuses your live documents with that data — diagnoses the fault,
              prepares the fix, and awaits your authorization."
PANEL QUOTE : Lamp-out = warm-amber warning-state → cool-blue resolved-state
ASSET REF   : VEO_COLD_OPEN.md Beat 7 (Scene 8); use A7A still-frame as ingredient for face/wardrobe
AUDIO       : MUTE Veo audio in Vids; include no-dialogue suppression clause in prompt
CONTINUITY  : Use still from A7A as ingredient (NOT Extend); same wardrobe/desk
```

### A9 — Hand-Off to Live App   ·  ~8s  ·  ⚠ BUILD IN VIDS (live screen-recording)
```
SOURCE      : Real screen-recording — NOT Veo (Veo cannot render legible UI; retired)
APP STATE   : GDC Advisor app, Intro tab, Slide 1 "What is GDC?" opening
VISUAL      : Slow push-in / gentle brighten as cold open dissolves into the live app on
              the Intro tab. Real UI = zero garbled-text risk
CAMERA/MOVE : [IN VIDS] apply slow push-in + brighten dissolve from the cold-open last frame
              into the live app; the Intro deck's ▶ View Demo → button on Slide 3 is the
              next click that advances into H1
VO          : "The decision — and the control — are always yours. First, a closer look at
              GDC itself — then we'll step through a realistic production scenario."
PANEL QUOTE : The live app opening (integrity note: labeled ⏺ Scenario Replay — not a live well)
ASSET REF   : Built BS+37; record Intro tab opening as clip A9_handoff.mov
CONTINUITY  : This clip's opening frame should match A8's final frame (RTOC → screen transition)
```

---

# PART B — LIVE DEMO SCREEN RECORDING · ~4:45 · RECORD-READY

**Recording setup:** `docs/RECORDING_GUIDE.md` · MacBook · Chrome DevTools 1280×720 CSS · QuickTime record-then-import · Vids crop 16:9 · export 1440p Rec.709
**Rule:** VO never speaks a number — panels carry every figure. Random replay values can't desync.

---

## SECTION 0 — MEET GDC · Intro tab, 4 slides · ~43s

### B0.1 — What is GDC? (Intro Slide 1)   ·  ~10s  ·  ✅ DONE
```
SOURCE      : Live screen capture
APP STATE   : Intro tab · Slide 1 "What is GDC?" (opens when tab is clicked)
VISUAL      : GKE→GDC architecture diagram; glass card "Google-Managed · AI/ML Enabled"
CAMERA/MOVE : [LIVE] cursor the GKE→GDC arrow; dwell on glass card
              [POST] static — no zoom needed on this slide
VO          : "At its core, GDC is a fully supported version of Google Kubernetes Engine —
              Google-managed, AI-enabled — deployed at the edge, on hardware that sits inside
              your own facility."
PANEL QUOTE : "Google-Managed · AI/ML Enabled" glass card label
ASSET REF   : slides/intro.html #s1
CONTINUITY  : (none — first app scene)
```

### B0.2 — When to Consider GDC (Intro Slide 2)   ·  ~12s  ·  ✅ DONE
```
SOURCE      : Live screen capture
APP STATE   : Intro tab · Slide 2 "When Should You Consider Using GDC?"
VISUAL      : 4-pillar grid: Compliance & Sovereignty · Survivability · Latency · Data Gravity
CAMERA/MOVE : [LIVE] advance slide; cursor across the four pillars left-to-right
              [POST] static
VO          : "It's built for four realities of field operations: data that must stay
              sovereign, operations that must survive a network outage, decisions that can't
              wait on a round-trip to the cloud, and the sheer gravity of data generated
              at the wellsite."
PANEL QUOTE : Four pillar labels (cursor gesture quotes them)
ASSET REF   : slides/intro.html #s2
CONTINUITY  : (none)
```

### B0.3 — Deployment Models (Intro Slide 3)   ·  ~9s  ·  ✅ DONE
```
SOURCE      : Live screen capture
APP STATE   : Intro tab · Slide 3 "GDC — Flexible Deployment Models"
VISUAL      : Three model cards: Connected · Software-Only · Air-Gapped
CAMERA/MOVE : [LIVE] advance slide; cursor the three model cards
              [POST] static (no View Demo click here — that moved to B0.4)
VO          : "There are three deployment models to match your use-cases — Google managed
              connected rack servers, GDC software on your own hardware, or a fully
              air-gapped appliance for the most sensitive workloads."
PANEL QUOTE : Three deployment model cards
ASSET REF   : slides/intro.html #s3
CONTINUITY  : (none — sovereignty plant was cut; topology framing is in B0.4)
NOTE (SESSION BS+39 decision): Original VO included "You'll see both ends of that spectrum
              today" as a sovereignty plant. CUT FOR ACCURACY — overclaimed two hardware SKUs
              (the demo uses one Connected deployment, not both Connected and Air-Gapped hardware).
              B0.4 replaces this as the honest topology plant.
```

### B0.4 — Two Edge Architectures (Intro Slide 4)   ·  ~10s  ·  ✅ DONE ⭐ NEW
```
SOURCE      : Live screen capture — NEW SLIDE (slides/intro.html #s4, committed 115ed31)
APP STATE   : Intro tab · Slide 4 "Two Edge Architectures — Fully On-Prem and Hybrid"
              · Two-column layout: RTOC icon (left) | Google Cloud icon (right)
              · Row 1: DISCERN · CLASSIFY (green) — chip box left only, right column empty
              · Row 2: OPTIMIZE (blue) — chip box left + dashed connector → AI Optimizer cloud box
VISUAL      : Both rows visible; connector + AI Optimizer box in right column (Optimize row)
CAMERA/MOVE : [LIVE] advance slide; cursor Discern·Classify row (left) → trace dashed connector
              → AI Optimizer box; click ▶ View Demo →
              [POST] gentle zoom to AI Optimizer box as VO says "Vizier, Google's powerful AI optimizer"
VO          : "Three scenarios — two where all AI runs on-prem against local data, fully
              sovereign. The third reaches the cloud for one service: Vizier, Google's
              powerful AI optimizer."
PANEL QUOTE : "AI Optimizer · Vertex AI Vizier" cloud box (right column, Optimize row)
ASSET REF   : slides/intro.html #s4
CONTINUITY  : TOPOLOGY PLANT — pays off in BBRIDGE (callback) and H3-S3/S5 (payoff).
              "Air-gap capable" deliberately NOT used — demo runs on Connected GDC.
              Sovereignty framing: "all AI on-prem, fully sovereign" (accurate);
              "data never follows" implied by the cloud box showing only setpoints+scores.
NOTE        : View Demo → click moves to this slide (B0.4 is now the last Intro slide).
              B0.3 advances normally to B0.4 via Next →.
```

---

## SECTION 1 — H1 DISCERN · Discern tab · ~1:45 · RECORD

**Tab header:** `Discern — ESP Fluid Unloading · Well A-3 · Pad Alpha · ⏺ Scenario Replay`
**Toggle labels (live):** `🟡 SCADA View` / `🟢 GDC Advisor`
**Run button:** `↺ New Scenario`
**Verdict (random):** `✔ GAS LOCK CONFIRMED` OR `⚠ FLUID DRAWDOWN CONFIRMED`

### B1-P1 — THE SCENARIO (H1 Slide 1)   ·  ~30s  ·  ✅ DONE
```
SOURCE      : Live screen capture (briefing slides iframe)
APP STATE   : H1 tab · briefing mode · Slide 1 "Same Signal. Two Causes. One Right Decision."
VISUAL      : Scenario kicker + title + sub-text: ESP unloading / two root causes / opposite actions
CAMERA/MOVE : [LIVE] tab opens in briefing mode on Slide 1
              [POST] static
VO          : "A moment ago, we described the ambiguous alarm — where the signals alone can't tell
              you the cause. This is one. Well A-3: a mature ESP well on Pad Alpha, out in the
              Permian. As it begins to lose lift, the sensors show a textbook decline — but that
              same signature can come from two very different downhole problems, and the fix that
              saves the well in one case would destroy it in the other."
PANEL QUOTE : Slide kicker "THE SCENARIO"
ASSET REF   : slides/h1.html #p1
CONTINUITY  : CALLBACKS Part A A4 ("the signals alone can't tell you the cause") — direct echo
```

### B1-P2 — AMBIGUOUS TELEMETRY + Play (H1 Slide 2)   ·  ~14s  ·  ✅ DONE
```
SOURCE      : Live screen capture
APP STATE   : H1 tab · Slide 2 "One Signature, Two Physical Realities" · click ▶ Play on
              the shared scrubber
VISUAL      : Two animated wellbore diagrams side by side — GAS ENTRAINMENT (blue, left)
              and FLUID DRAWDOWN · RESERVOIR DEPLETION (amber, right). Shared scrubber
              drives both simultaneously. Bottom bar "SAME SENSOR OUTPUT ↓" shows identical
              pressure + amps decline for both causes.
CAMERA/MOVE : [LIVE] advance to Slide 2; click ▶ Play; let both animations run
              [POST] zoom 1.2× on the two side-by-side wellbore panels
VO          : "Two culprits: gas entrainment — free gas reaching the pump — or fluid
              drawdown, where the fluid level falls toward the intake. Different downhole
              causes — and on this sensor string, the cause and the safe action are not
              in these numbers."
PANEL QUOTE : Bottom bar "SAME SENSOR OUTPUT ↓" + identical pressure/amps bars for both
              causes (zoom quotes the identical declining bars)
ASSET REF   : slides/h1.html #p2 — shared ▶ Play scrubber button
CONTINUITY  : (none)
NOTE (BS+40): "Indistinguishable" dropped from VO — invites "slug-texture" rebuttal from
              experienced ESP engineers. Anchor shifted to slide's own unarguable line:
              "the cause and the safe action are not in these numbers."
```

### B1-P3 — DECISION SUPPORT (H1 Slide 3)   ·  ~27s  ·  ✅ DONE
```
SOURCE      : Live screen capture
APP STATE   : H1 tab · Slide 3 "All Three Responses Have a Trap."
              (REDESIGNED BS+40 — 3 cards: VFD Speed-Down | Managed Step-Down + Hold | Emergency Shut-In)
VISUAL      : Three choice cards in a row (1fr 1fr 1fr grid). Each shows 2 outcome rows.
              KEY VISUAL: the Speed-Down card has ✔ Gas / ✘ Drawdown+Sand — same action,
              opposite fate. The Managed Step-Down card has ✘ Gas (unnecessary) / ✔ Drawdown
              (correct). The Shut-In card has ✘ Gas (overkill) / ✔ Drawdown clean (safe-defers)
              / ✘ Drawdown+Sand (dangerous).
CAMERA/MOVE : [LIVE] advance to Slide 3; cursor starts wide (all 3 cards visible)
              [POST] Screen Studio — sweep L→R across all three cards, one beat per card.
              Use ZOOM (~1.3×) or MASK (highlight one card, others dimmed) — both work:
              (1) Card 1 (VFD Speed-Down): flick ✔ Gas row → ✘ Drawdown+Sand row (vertical)
              (2) Card 2 (Managed Step-Down): settle on ✔ Fluid Drawdown row (hold ~2s)
              (3) Card 3 (Emergency Shut-In): settle on ✘ Gas (overkill) + ✔ clean (holds)
              (4) Pull back to all three + bottom callout for the closing line
VO          : "There are three responses — and each one is a trap in the wrong case. Ease the
              speed — clears the gas, but seizes a sandy well. Step down and hold — correct for
              drawdown; for gas, the simple speed-down already worked. Shut in — safe only if
              the well is confirmed clean, but overkill if it isn't. The sensors can't tell you
              which is right. That answer is in the well documents."
PANEL QUOTE : Card 1 ✔/✘ flip → Card 2 ✔ Drawdown → Card 3 ✘ Gas + ✔ clean → bottom callout

ASSET REF   : slides/h1.html #p3
CONTINUITY  : (none)
NOTE (BS+40): Slide redesigned from 2-card to 3-card to close the "both dangerous for sandy
              drawdown" false-binary hole. Managed Step-Down + Hold is the complete answer
              GDC's drawdown verdict delivers. "LAST RESORT" label removed — replaced with
              "SAFE · DEFERS PRODUCTION" on the Shut-In / clean-drawdown row.
```

### B1-P4 — ADDING CONTEXT (H1 Slide 4)   ·  ~12s  ·  ✅ DONE
```
SOURCE      : Live screen capture
APP STATE   : H1 tab · Slide 4 "Fusing Telemetry and Unstructured Well History"
              · Left panel: WITHOUT GDC — clock (MINUTES TO HOURS), 4 scattered sources
              · Right panel: WITH GDC — stopwatch (< 10 SECONDS), 4 automated steps
VISUAL      : Two-column contrast — MINUTES TO HOURS (left) vs < 10 SECONDS (right).
              The stopwatch-vs-clock is the dominant visual; the source names fill the detail.
CAMERA/MOVE : [LIVE] advance to Slide 4
              [POST] zoom on WITHOUT column (clock + document list) during "minutes to hours";
              pan RIGHT to WITH column (stopwatch + GDC steps) during "GDC does it in seconds";
              settle on the < 10 SECONDS readout for the closing line
VO          : "Those records exist. The problem is assembling them under pressure. GDC
              retrieves, fuses, and diagnoses automatically — in seconds. A cited
              recommendation is in the engineer's hands before any hard limit is crossed."
PANEL QUOTE : WITHOUT column "MINUTES TO HOURS" → WITH column "< 10 SECONDS" · GDC 4-step
              (auto-retrieve → Gemma fusion → cited verdict → HITL)
ASSET REF   : slides/h1.html #p4
CONTINUITY  : ECHOES Part A (A5 — scattered context is now collected)
```

### B1-P5 — INDUSTRIAL APPLICATION (H1 Slide 5)   ·  ~10s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H1 tab · Slide 5 "Solving the Edge Context Gap — At Scale"
VISUAL      : Three-industry cards
CAMERA/MOVE : [LIVE] advance to Slide 5; brief hold on the three-industry cards
              [POST] static
VO          : "And this gap — live state on the sensors, the deciding context locked in
              documents — shows up in every industry that runs critical equipment."
PANEL QUOTE : Industry card labels
ASSET REF   : slides/h1.html #p5
CONTINUITY  : (none)
```

### B1-S1 — Start the Run   ·  ~7s  ·  RECORD
```
SOURCE      : Live screen capture (tab transitions from briefing to replay)
APP STATE   : H1 tab · click ↺ New Scenario → replay loads → ▶ transport begins
              · GDC Advisor view · h1ReplayData loaded · idx=0
              · GDC panel shows: "WELL A-3 — BASELINE MONITORING · hs=… · XGBoost routing score"
VISUAL      : Replay loads; sensors begin animating; GDC baseline monitoring panel visible
CAMERA/MOVE : [LIVE] click ↺ New Scenario; show transport running
              [POST] static
VO          : "Let's run it live. GDC is scoring every channel as the event unfolds — before
              any single hard limit is crossed."
PANEL QUOTE : "BASELINE MONITORING · XGBoost routing score" in GDC Advisor panel
ASSET REF   : templates/tab_h1.html — `↺ New Scenario` button
CONTINUITY  : Verdict is random (Gas Lock or Drawdown); record whichever fires; VO branches at B1-S4
```

### B1-S2 — Pre-Threshold Detect ⭐ NEW   ·  ~7s  ·  RECORD
```
SOURCE      : Live screen capture — NEW SCENE
APP STATE   : H1 tab · GDC Advisor view · scrub to gdc_detect_idx (~27)
              · h1FaultTypeRevealed=true; h1RagRevealed=false
              · GDC panel shows: amber "RETRIEVING CONTEXT — ALLOYDB PGVECTOR (<2S)" scanning state
              · NO SCADA alarm yet (alarm_idx ~48 not yet reached)
              · Chart: PIP + Amps declining; Temp + Vib still flat
VISUAL      : GDC flags the drift; SCADA is still silent; the gap between the two markers
              is the evidence for the MORE TIME value point
CAMERA/MOVE : [LIVE] scrub replay to ~gdc_detect_idx; hold on the GDC Advisor panel
              [POST] zoom 1.15× on the GDC-detect amber state; hold ~2s
VO          : "GDC flags the developing drift here — ahead of any single hard limit being
              crossed."
PANEL QUOTE : GDC amber retrieving state at idx≈27; SCADA still quiet
ASSET REF   : templates/tab_h1.html — v-if="h1FaultTypeRevealed && !h1RagRevealed"
CONTINUITY  : ECHOES Part A Scene A7B (same detection moment — "identifying the developing
              issue" = this moment in the live app)
INTEGRITY   : This is the Part B proof of the Part A claim. Do not skip this scene.
```

### B1-S3 — SCADA View (alarm, no cause)   ·  ~10s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H1 tab · 🟡 SCADA View selected · scrub to alarm_idx (~48)
              · Red banner: "⚠ SCADA alarm — ambiguous underload — gas lock and fluid
              drawdown produce indistinguishable telemetry on an intake-only string — cause
              cannot be determined from sensor data alone"
              · SCADA action cards: two grey slate cards (cause unknown — not color-saturated)
VISUAL      : SCADA view shows alarm banner; no cause; grey action cards (not green)
CAMERA/MOVE : [LIVE] switch to 🟡 SCADA View; scrub to alarm; point to the amber banner
              and the un-colored action cards
              [POST] static
VO          : "This is what the control system sees. It protects the pump — it trips on its
              hard limit, as it should — but it offers no cause, and no read on sand risk."
PANEL QUOTE : "ambiguous underload" + grey (not green) action cards
ASSET REF   : templates/tab_h1.html — `h1CursorIdx >= h1ReplayData.alarm_idx` + SCADA view
CONTINUITY  : (none)
```

### B1-S4 — GDC Advisor verdict + 3 documents   ·  ~11s  ·  RECORD (A/B BRANCH)
```
SOURCE      : Live screen capture
APP STATE   : H1 tab · 🟢 GDC Advisor view · h1RagRevealed=true
              · GAS LOCK: "✔ GAS LOCK CONFIRMED" green panel; 3 docs: Shift Note + Separator
                GOR Lab + OEM Troubleshooting Guide
              · DRAWDOWN: "⚠ FLUID DRAWDOWN CONFIRMED" amber panel; 3 docs: Sonic Log +
                GOR Lab + OEM Troubleshooting Guide
VISUAL      : Verdict card + 3 doc cascade (each doc card appears ~2s apart)
CAMERA/MOVE : [LIVE] click 🟢 GDC Advisor; let docs + verdict render; zoom each doc card
              briefly as it appears
              [POST] zoom 1.15× on the verdict card; hold ~2s
VO — GAS LOCK : "GDC retrieves the well's documents — annulus submerged, gas rising, sand
              history clean — and returns a cited verdict: gas lock. Ease the speed;
              keep the well online."
VO — DRAWDOWN : "GDC retrieves the well's documents — fluid level below the intake, a known
              sand producer — and returns a cited verdict: drawdown. Shut it in; easing the
              speed here would seize the pump."
PANEL QUOTE : "✔ GAS LOCK CONFIRMED" / "⚠ FLUID DRAWDOWN CONFIRMED" + pgvector cosine
              similarity score visible
ASSET REF   : templates/tab_h1.html — `h1RagRevealed && h1FaultType==='gas_lock'` /
              `h1FaultType==='fluid_drawdown'` verdict panels
CONTINUITY  : ECHOES Part A A8 (document fusion resolved the problem)
NOTE        : Record whichever verdict fires. Both VO branches are provided. Do not re-run
              to force a specific branch — the random branch is the honest demo.
```

### B1-S5 — HITL Approve   ·  ~8s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H1 tab · 🟢 GDC Advisor · h1RagRevealed=true · before approval
              · "GDC Agent · Action package ready · Awaiting RTOC approval" streaming label
              · Action card: "✔ Approve & Execute — VFD Trim 52→44 Hz" (gas lock)
                or "✔ Approve & Execute — Step-Down + Hold" (drawdown)
              · pgvector similarity score visible in evidence line
VISUAL      : HITL panel; approve the action
CAMERA/MOVE : [LIVE] show the HITL awaiting state; zoom the evidence/similarity line;
              click ✔ Approve & Execute
              [POST] zoom 1.15× on "Awaiting RTOC approval" + the approve button
VO          : "Every recommendation is cited and reviewable. The engineer approves the
              action — GDC advises, the human decides."
PANEL QUOTE : "Awaiting RTOC approval" label + ✔ Approve & Execute button label
ASSET REF   : templates/tab_h1.html — `GDC Agent · Action package ready · Awaiting RTOC approval`
CONTINUITY  : ECHOES Part A A8 (the nod + authorize moment)
```

### B1-S6 — Outcome (OPTIONAL / TRIM)   ·  ~5s  ·  RECORD-IF-BUDGET
```
SOURCE      : Live screen capture
APP STATE   : H1 tab · GDC Advisor · h1Resolved=true
              · GAS LOCK: "✅ RECOVERING — VFD at 44 Hz · monitoring wellbore response"
              · DRAWDOWN: Step-down outcome card
VISUAL      : Resolved outcome card; well stays online (gas lock) or safe shut-in (drawdown)
CAMERA/MOVE : [LIVE] hold on the resolved state
              [POST] static
VO          : "The well stays online — an ambiguous alarm became a confident, low-cost decision."
              (gas lock branch; omit or adapt for drawdown)
PANEL QUOTE : "✅ RECOVERING" status label
ASSET REF   : templates/tab_h1.html — `h1Resolved && !h1Seized`
NOTE        : OPTIONAL — cut this scene if total runtime exceeds 5:55. The close narration
              already wraps H1. Remove if tight.
```

---

## SECTION 2 — H2 CLASSIFY · Classify tab · ~1:10 · RECORD

**Tab header:** `Classify — Maintenance Provenance · Well A-3 · Pad Alpha · ⏺ Scenario Replay`
**Toggle labels (live):** `🟡 SCADA View` / `🟢 GDC Advisor`
**Run button:** `↺ New Scenario`
**Verdict (fixed):** `⚡ GDC verdict: Paraffin/wax deposition — PM Xd overdue · dispatch hot-oil truck · do NOT pull`

### B2-P1 — THE SCENARIO (H2 Slide 1)   ·  ~7s  ·  RECORD
```
SOURCE      : Live screen capture (briefing iframe)
APP STATE   : H2 tab · Slide 1 "Waxy Crude. Routine PM. Then Nothing."
VISUAL      : Scenario kicker + title + sub: paraffin problem / 52-day overdue treatment /
              vendor delay logged but not in SCADA
CAMERA/MOVE : [LIVE] tab opens in briefing mode on Slide 1
              [POST] static
VO          : "A different well, a slower problem. Waxy crude, on a routine treatment
              schedule — until a treatment is missed."
PANEL QUOTE : Slide kicker "THE SCENARIO"
ASSET REF   : slides/h2.html #p1
CONTINUITY  : (none — new scenario)
```

### B2-P2 — AMBIGUOUS TELEMETRY (H2 Slide 2)   ·  ~11s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H2 tab · Slide 2 "Fifty-Two Days Late. Bearings or Wax?"
VISUAL      : Four sensor tiles: current rising, efficiency falling, vibration climbing
              THROUGH the printed high-alarm line, pressure holding
CAMERA/MOVE : [LIVE] advance to Slide 2
              [POST] zoom 1.2× on the four sensor tiles; hold on vibration tile crossing
              the high-alarm line
VO          : "Weeks of drift — rising current, falling efficiency, vibration climbing
              through its high alarm. To a best-in-class platform, that pattern reads as
              bearing wear: pull the pump."
PANEL QUOTE : Vibration tile value vs printed high-alarm line (4.0 mm/s) — zoom quotes the cross
ASSET REF   : slides/h2.html #p2
CONTINUITY  : (none)
```

### B2-P3 — ADDING CONTEXT (H2 Slide 3)   ·  ~7s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H2 tab · Slide 3 "Three Documents. One Truck. No Pull."
VISUAL      : Three-document / one-truck framing; kicker "ADDING CONTEXT"
CAMERA/MOVE : [LIVE] advance to Slide 3; hold on the framing
              [POST] static
VO          : "But the bearings aren't the cause — and the proof is in three documents the
              platform never sees."
PANEL QUOTE : "GDC adds three documents" (slide sub-text)
ASSET REF   : slides/h2.html #p3
CONTINUITY  : (none)
```

### B2-S1 — Start the Run   ·  ~5s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H2 tab · click ↺ New Scenario → degradation replay begins
              · efficiency falls; vibration climbs past missed-treatment point
VISUAL      : Replay starts; degradation begins accumulating
CAMERA/MOVE : [LIVE] click ↺ New Scenario; show replay animating
              [POST] static
VO          : "Run it. The degradation accumulates exactly the way mechanical wear would."
PANEL QUOTE : Slowly rising vibration / falling efficiency curves
ASSET REF   : templates/tab_h2.html — `↺ New Scenario` button
CONTINUITY  : (none)
```

### B2-S2 — SCADA/APM View → Bearing Wear   ·  ~8s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H2 tab · 🟡 SCADA View · h2CursorIdx >= h2ReplayData.scada_alarm_idx
              · Red ISA-18.2 VIB-HI banner visible
              · SCADA action cards: "pump pull" option (bearing wear assumption)
VISUAL      : SCADA view; VIB-HI alarm; pump-pull card showing
CAMERA/MOVE : [LIVE] ensure SCADA View; let replay reach scada_alarm_idx; point to the
              bearing-wear conclusion / pump pull card
              [POST] static
VO          : "The monitoring platform identifies the symptom correctly — and routes to the
              standard, expensive response: a pump pull."
PANEL QUOTE : VIB-HI alarm banner text + pump-pull action card
ASSET REF   : templates/tab_h2.html — `h2CursorIdx >= h2ReplayData.scada_alarm_idx` SCADA view
CONTINUITY  : (none)
```

### B2-S3 — GDC Advisor: 3-Doc Cascade + Verdict   ·  ~13s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H2 tab · 🟢 GDC Advisor · h2VerdictRevealed=true
              · Doc 1: 📋 Chemical Vendor Service Log (fires with RAG verdict)
              · Doc 2: 🧪 Fluid PVT Report (+2s)
              · Doc 3: 📁 Prior Pull Record (+3.5s)
              · Blue banner: "⚡ GDC verdict: Paraffin/wax deposition — PM Xd overdue ·
                dispatch hot-oil truck · do NOT pull"
VISUAL      : Three doc cards appear in sequence; blue verdict banner above
CAMERA/MOVE : [LIVE] click 🟢 GDC Advisor; pace the VO to the reveals
              [POST] zoom 1.15× on each doc card as it appears (~2s each);
              then zoom 1.2× on the blue verdict banner; hold ~2s
VO          : "GDC fuses three documents: an overdue paraffin treatment, a fluid report
              showing this crude lays down wax, and a recent inspection with healthy bearings.
              The verdict flips — paraffin restriction, not bearing wear."
PANEL QUOTE : Doc 1 title "Chemical Vendor Service Log"; Doc 2 🧪 "Fluid PVT Report";
              Doc 3 📁 "Prior Pull Record"; verdict banner "do NOT pull"
ASSET REF   : templates/tab_h2.html — `h2VerdictRevealed` + three doc v-if blocks
CONTINUITY  : ECHOES Part A A8 (document fusion payoff)
NOTE        : Pace the read to the doc reveals. Start the VO line a beat after clicking
              GDC Advisor so the first doc is already appearing when words begin.
```

### B2-S4 — Action Contrast (surface vs pull AVERTED)   ·  ~8s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H2 tab · 🟢 GDC Advisor · h2VerdictRevealed=true · before action choice
              · Two action cards: (green) hot-oil truck dispatch · (grey/averted) pump pull
VISUAL      : Hot-oil dispatch action card (green) vs pump pull AVERTED card
CAMERA/MOVE : [LIVE] show both action cards
              [POST] zoom 1.15× on the AVERTED label on the pull card; hold ~2s
VO          : "The fix is a surface treatment, not a workover. The pull is averted —
              symptom versus cause, decided by the documents."
PANEL QUOTE : "✅ HOT-OIL TRUCK DISPATCHED" / AVERTED label on pull card
ASSET REF   : templates/tab_h2.html — two-card layout before h2Resolved / h2PullOutcome
CONTINUITY  : (none)
```

### B2-S5 — Outcome (OPTIONAL / TRIM)   ·  ~4s  ·  RECORD-IF-BUDGET
```
SOURCE      : Live screen capture
APP STATE   : H2 tab · GDC Advisor · h2Resolved=true · !h2PullOutcome
              · "✅ HOT-OIL TRUCK DISPATCHED — PARAFFIN RESTRICTION CLEARED"
VISUAL      : Resolved outcome card; pull explicitly avoided
CAMERA/MOVE : [LIVE] click dispatch; hold on outcome card
              [POST] static
VO          : "Symptom versus cause — decided by the documents."
PANEL QUOTE : "✅ HOT-OIL TRUCK DISPATCHED — PARAFFIN RESTRICTION CLEARED"
ASSET REF   : templates/tab_h2.html — `h2Resolved && !h2PullOutcome` outcome card
NOTE        : OPTIONAL — cut if runtime tight. The action contrast card (B2-S4) already
              carries the payoff if this scene is dropped.
```

---

## SOVEREIGNTY BRIDGE · Between H2 and H3 · ~8s · RECORD

### BBRIDGE — H2→H3 Sovereignty Bridge   ·  ~8s  ·  RECORD ⭐ NEW
```
SOURCE      : Live screen capture — CALLBACK to Intro Slide 3 (Deployment Models)
APP STATE   : Navigate to Intro tab · Slide 3 "GDC — Flexible Deployment Models"
              (the same slide shown in B0.3 — the sovereignty plant)
              Three model cards: Connected · Software-Only · Air-Gapped
VISUAL      : Return to the three Deployment Model cards; cursor the Air-Gapped card (H1/H2),
              then cursor the Connected card (H3)
CAMERA/MOVE : [LIVE] navigate Intro tab → Slide 3; cursor Air-Gapped card (hold ~2s) then
              pan cursor to Connected card (hold ~2s)
              [POST] zoom 1.15× on the Air-Gapped and Connected cards to make labels readable
VO          : "The first two cases ran entirely on-prem — air-gap capable, no cloud required.
              The third case is the connected model: it reaches GCP for Bayesian search —
              but only candidate setpoints and scores leave the site. Your data never follows.
              And safety stays local."
PANEL QUOTE : "Air-Gapped" model card label (H1/H2) + "Connected" model card label (H3)
ASSET REF   : slides/intro.html #s3 (same as B0.3 — callback not re-record)
CONTINUITY  : TOPOLOGY SPINE: Plant (B0.4) → Bridge (this) → Payoff (H3-S5).
              B0.3 plant line was cut for accuracy (Session BS+39). B0.4 is the honest plant.
INTEGRITY   : Sovereignty claim is true to code: Vizier receives only Hz vectors + scalar
              cash_flow (app.py L6741–6763). evaluate_field() — physics, temps, GOR —
              runs on-prem before any value crosses the wire. Fallback is fully deterministic
              (no cloud at all). Both states are honest.
```

---

## SECTION 3 — H3 OPTIMIZE · Optimize tab · ~1:20 · RECORD

**Tab header:** `Optimize — Pad Alpha VFD Optimization`
**Run button:** `⚡ Run Vizier Optimization`
**Deploy button:** `✔ Deploy Recommendation` (appears after trials)
**Table columns:** `Baseline Hz` · `GDC Optimal` · `Δ Hz`
**No toggle** — contrast lives in the two table columns.

### B3-P1 — THE SCENARIO (H3 Slide 1)   ·  ~9s  ·  RECORD
```
SOURCE      : Live screen capture (briefing iframe)
APP STATE   : H3 tab · Slide 1 "Maximum Production. Maximum Care."
              · GOR table visible: 6 wells with differing GOR values
VISUAL      : GOR table; Slide 1 kicker "THE SCENARIO"
CAMERA/MOVE : [LIVE] tab opens in briefing mode on Slide 1
              [POST] zoom 1.2× on the GOR table; cursor the lowest-GOR wells
              (priority rows — "Priority · runs max ↑"), then cursor the highest-GOR well
              (marginal row — "Marginal · gives way ↓")
VO          : "Now the whole pad. Six wells share one gas-handling limit — and every barrel
              carries gas, but some wells carry far more than others."
PANEL QUOTE : GOR table values; priority vs marginal labels
ASSET REF   : slides/h3.html #p1
CONTINUITY  : (none — new scenario; sovereignty is covered in BBRIDGE)
```

### B3-P2 — DECISION SUPPORT / Three Ceilings (H3 Slide 2)   ·  ~10s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H3 tab · Slide 2 "Three Ceilings You Cannot Ignore."
              · Three constraints: gas takeaway contract / motor temperature / run-life
VISUAL      : Three ceiling constraints; printed thermal-limit line visible
CAMERA/MOVE : [LIVE] advance to Slide 2; point to each of the three ceiling items
              [POST] zoom 1.15× on the printed thermal-limit line/value
VO          : "Here's the goal: the most oil the pad can produce while staying under the gas
              contract and never crossing any motor's temperature limit. Three ceilings,
              held at once."
PANEL QUOTE : Thermal-limit value (printed on slide — panels carry the number)
ASSET REF   : slides/h3.html #p2
CONTINUITY  : (none)
```

### B3-P3 — PAD OPTIMIZATION: Cloud Searches. Edge Enforces. (H3 Slide 3)   ·  ~8s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H3 tab · Slide 3 "Cloud Searches. Edge Enforces."
              · Cloud-search / edge-enforce split diagram
VISUAL      : Division-of-labor diagram; cloud side vs edge side
CAMERA/MOVE : [LIVE] advance to Slide 3; hold on cloud-searches / edge-enforces split
              [POST] static
VO          : "The division of labor: the cloud searches for the best setpoints; the edge
              enforces the safety limit on every candidate, locally."
PANEL QUOTE : "Cloud Searches. Edge Enforces." slide title
ASSET REF   : slides/h3.html #p3
CONTINUITY  : SOVEREIGNTY PAYOFF begins here (continues B3-S5)
```

### B3-S1 — Run Vizier Optimization   ·  ~7s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H3 tab · briefing dismissed (h3BriefingMode=false) · click ⚡ Run Vizier Optimization
              · Trial scatter populates Pareto chart (15 Bayesian trials converging)
VISUAL      : Trial dots populating chart; optimization converges toward optimum
CAMERA/MOVE : [LIVE] click ⚡ Run Vizier Optimization; show trial scatter populating
              [POST] static — let the animation be the visual
VO          : "Run it. The optimizer explores the setpoint space — and only setpoints and
              scores ever leave the site."
PANEL QUOTE : Trial scatter chart (each dot = one Hz proposal + one cash score)
ASSET REF   : templates/tab_h3.html — `⚡ Run Vizier Optimization` button
CONTINUITY  : SOVEREIGNTY SPINE: the phrase "only setpoints and scores" echoes BBRIDGE exactly
```

### B3-S2 — Baseline Hz Column (uniform throttle)   ·  ~8s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H3 tab · optTrials.length > 0 · per-well setpoint table visible
              · Cursor on Baseline Hz column: all 6 wells near same conservative speed
VISUAL      : Per-well table with Baseline Hz column highlighted; uniform values
CAMERA/MOVE : [LIVE] when trials settle, zoom on the per-well table; cursor the Baseline Hz column
              [POST] zoom 1.15× on the Baseline Hz column
VO          : "The safe baseline throttles every well the same — which strands production
              on the wells that are most gas-efficient."
PANEL QUOTE : Baseline Hz column values (uniform; printed on screen)
ASSET REF   : templates/tab_h3.html — per-well table `Baseline Hz` column
CONTINUITY  : (none)
```

### B3-S3 — GDC Optimal Column + Uplift Card   ·  ~10s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H3 tab · per-well table + uplift card visible
              · GDC Optimal column: lowest-GOR wells highest Hz; gassiest backed off
              · Δ Hz column: shows differentiation
              · Uplift card: +bbl/d · cash uplift values
VISUAL      : GDC Optimal column differentiation vs Baseline; uplift card
CAMERA/MOVE : [LIVE] cursor across GDC Optimal column; then pan to uplift card
              [POST] zoom 1.15× on GDC Optimal column; hold ~2s; then zoom 1.15× on
              uplift card; hold ~2s
VO          : "GDC's allocation runs the low-gas wells wide open and backs off the gassiest —
              more daily production, with gas held just under the ceiling."
PANEL QUOTE : GDC Optimal Hz values (differentiated) + uplift card (+bbl/d · cash figure)
ASSET REF   : templates/tab_h3.html — GDC Optimal + Δ Hz columns + uplift card
CONTINUITY  : (none)
```

### B3-S4 — Constraint Provenance Document ⭐ NEW   ·  ~7s  ·  RECORD (CONDITIONAL)
```
SOURCE      : Live screen capture — NEW SCENE
APP STATE   : H3 tab · optTrials.length > 0 · Binding Constraint selector visible
              · GAS TAKEAWAY active (v-if="optTrials.length > 0")
              · constraintDoc.found=true → constraint provenance doc card visible
              · Provenance card: midstream contract reference (AlloyDB RAG result)
VISUAL      : Binding Constraint selector (GAS TAKEAWAY active) + constraint provenance
              doc card below — showing the limit is cited to a real document
CAMERA/MOVE : [LIVE] cursor the Binding Constraint selector (GAS TAKEAWAY active);
              then cursor the constraint provenance card below it
              [POST] zoom 1.15× on the provenance doc card
VO          : "And the limit itself is cited — it traces to the midstream contract,
              not a guess."
PANEL QUOTE : Constraint provenance doc card text (midstream contract reference from AlloyDB)
ASSET REF   : templates/tab_h3.html — v-if="constraintDoc && constraintDoc.found" block
              · RAG lookup: /api/vizier/optimize → app.py L6538 (constraintDoc query)
CONTINUITY  : This is H3's "MORE CONTEXT" beat — mirrors H1-S4 and H2-S3 in the doc-fusion
              spine. H3 now has a document beat too.
NOTE (CONDITIONAL): This scene renders ONLY when constraintDoc.found=true. 
              ⚠ CODE TASK: Verify the RAG constraint query (app.py L6530-6540) reliably
              returns a found=true result before recording. If constraintDoc.found is
              intermittent, a code fix is needed to ensure the AlloyDB midstream contract
              document is in the rag_documents table and the lookup succeeds consistently.
              Do not record this scene until confirmed reliable. If it fails to render,
              fold this VO into B3-S5.
```

### B3-S5 — Edge Safety / Offline   ·  ~8s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H3 tab · thermal-limit provenance note visible below the per-well table
              · Binding Constraint selector visible
VISUAL      : Thermal-limit note; constraint selector (GAS TAKEAWAY active)
CAMERA/MOVE : [LIVE] cursor the Binding Constraint selector; hold on the thermal-limit
              provenance note below the table
              [POST] zoom 1.15× on the thermal-limit note
VO          : "And the temperature limit is enforced on the edge — so if the link drops
              mid-search, safety never drops with it."
PANEL QUOTE : Thermal-limit value in provenance note (printed: 280°F)
ASSET REF   : templates/tab_h3.html — thermal-limit provenance note + constraint selector
CONTINUITY  : SOVEREIGNTY PAYOFF: this is the third leg of the sovereignty spine
              (Plant B0.3 → Bridge BBRIDGE → Payoff B3-S3/S5)
```

---

## CLOSE · ~12s · RECORD

### BCLOSE — H3 Uplift + ⓘ Reference tab   ·  ~12s  ·  RECORD
```
SOURCE      : Live screen capture
APP STATE   : H3 tab · uplift card in frame; then navigate to ⓘ Reference tab
              · ⓘ Reference tab: "Operator RTOC / Sovereign Data Center" deployment panel
              ⚠ DO NOT navigate to Operations or Financials — those tabs are orphaned
              (not in nav header — Known Integrity item)
VISUAL      : Uplift card (+bbl/d, cash uplift); then ⓘ Reference sovereign-deployment panel
CAMERA/MOVE : [LIVE] rest on H3 uplift card (let numbers sit ~3s); navigate to ⓘ Reference;
              cursor the sovereign-deployment panel
              [POST] zoom 1.1× on uplift card (+bbl/d figure); then static on Reference panel
VO          : "Diagnose the ambiguous, catch the wrong fix, and push every safe barrel —
              one sovereign stack, cited and reviewable, inside your perimeter.
              Lower lifting cost, longer asset life, higher runtime."
PANEL QUOTE : Uplift card values (+bbl/d · cash uplift); ⓘ Reference "Sovereign Data Center" label
ASSET REF   : templates/tab_h3.html uplift card; tab_operations orphan note above
CONTINUITY  : Final sovereign-data-center framing resolves the sovereignty spine cleanly.
```

---

## RUNTIME LEDGER
| Section | Scenes | Est. time |
|---|---|---|
| Part A — Cold open (Veo, 9 scenes) | A1–A9 | ~65s |
| Part B — Intro (4 slides) | B0.1–B0.4 | ~43s |
| Part B — H1 Discern (5 slides + 5+1 scenario) | B1-P1 to B1-S6 | ~55s+15s opt |
| Part B — H2 Classify (3 slides + 4+1 scenario) | B2-P1 to B2-S5 | ~27s+13s opt |
| Part B — Sovereignty Bridge | BBRIDGE | ~8s |
| Part B — H3 Optimize (3 slides + 5 scenario) | B3-P1 to B3-S5 | ~34s+7s cond |
| Part B — Close | BCLOSE | ~12s |
| **TOTAL (core, excl. optionals)** | | **~5:45** |
| **With optionals B1-S6 + B2-S5** | | **~6:00** ← trim lever |

> **Trim lever:** drop B1-S6 and B2-S5 (both marked OPTIONAL) for ~5:45. Drop B3-S4 (CONDITIONAL) if constraintDoc.found unreliable. Stay under 6:00.

---

## OPEN CODE TASKS (do not record until these are confirmed)

| Task | File | Notes |
|---|---|---|
| **H3-S4 foundation: verify constraintDoc reliably renders** | `app.py` L6530–6545 | RAG query for midstream contract doc. Confirm `rag_documents` table has the constraint document and the pgvector lookup returns `found=true` consistently. Fix if intermittent before recording B3-S4. |
| **Operations / Financials orphaned tabs** | `index.html` / `app.js` | Wire `tab_operations` + `tab_financials` into nav header and `mainTab` state. Known Integrity item from BS+27/BS+37. No urgency for video — close is on ⓘ Reference. |

---

## RECORDING CHECKLIST (pre-recording)
- [ ] Cluster healthy: all pods Running, Ollama=0
- [ ] App open at `http://gdc-pm.bdau.io` (or local port-forward) in Chrome, clean profile, no bookmarks bar
- [ ] DevTools → Device → 1280×720 CSS (or record full-screen + crop 16:9 in Vids)
- [ ] Do Not Disturb ON; Dock auto-hidden
- [ ] H3-S4 constraintDoc confirmed renders (or fallback note added to B3-S4)
- [ ] QuickTime record-then-import OR Vids Insert→Recording→Chrome Tab
- [ ] Export 1440p Rec.709 for crisp text
- [ ] Part A: all 9 scenes assembled in Vids with per-scene VO attached
- [ ] Part B: one clip per scene card; attach scene's VO in Vids per-scene microphone
- [ ] A8 (operator authorized): render when ready — fresh cold render, NOT Extend, use A7A still as ingredient
