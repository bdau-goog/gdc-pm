# GDC Demo — Per-Panel / Per-Scenario Voiceover (live screen recording)
**Pairs with:** `VEO_COLD_OPEN.md` (intro) → this file (the demo). Same persona/voice as V3/V4: **Google Cloud third-party, operator-grounded, CxO-safe, NO exact numbers spoken** (panels carry the figures).
**Structure:** one **Vids scene per panel / per scenario beat**, each with its own VO line and an **action note** (zoom / Play / toggle). Verified against the live slides + replay templates (h1/h2/h3.html, tab_h1/h2/h3.html).

## Conventions
- **[ACTION]** = what you do on screen for that scene (advance slide / click Play / toggle view / zoom in post).
- **[VO]** = the line to read for that scene (≈ matches the on-screen dwell time).
- **Zoom** notes are for post (1.15–1.2× crop on the named element). "Play" = click the panel's ▶ Play.
- **Scenario pattern you specified:** start the run → VO while it animates → explain **SCADA View** → toggle to **GDC Advisor** view. Verified the toggle is literally labeled **"SCADA View" / "GDC Advisor."**
- **Numbers stay on screen.** Read meaning, not figures.

---

# SECTION 0 — "WHAT IS GDC" (How It Works tab)  ·  ~25s

**Scene 0.1 — three-tier diagram**
[ACTION] Open *How It Works*; cursor glides Tier 1 → Tier 2 → Tier 3; **zoom 1.15× on Tier 3 (Document Context)** and hold.
[VO] *"GDC works alongside your existing control system. It scores the live sensor pattern locally — and adds the layer no monitoring platform has: your own field documents."*  ·  *(~8–9s)*

---

# SECTION 1 — H1 DISCERN
**Slides (verified):** 1 THE SCENARIO "Same Signal. Two Causes." · 2 AMBIGUOUS TELEMETRY "One Signature, Two Physical Realities" (has a **Play** mini-sim — "THE EVENT") · 3 DECISION SUPPORT "Motor Burnout vs. Sand Bridging" · 4 ADDING CONTEXT "Fusing Telemetry and Unstructured Well History" · 5 INDUSTRIAL APPLICATION "Solving the Edge Context Gap — At Scale."
**Scenario replay (verified):** **SCADA View / GDC Advisor** toggle · verdict card · **Approve** (HITL) · pgvector similarity score shown.

### Panel VO

**Scene H1-P1 — THE SCENARIO**
[ACTION] Show Slide 1.
[VO] *"Well A-3 is on a standard intake-only string. One signal is about to appear — with two possible causes that call for opposite actions."*  ·  *(~8s)*

**Scene H1-P2 — AMBIGUOUS TELEMETRY (Play)**
[ACTION] Slide 2; **click ▶ Play** on the mini-sim; let pressure & current fall while temp & vibration hold flat.
[VO] *"Watch it develop: intake pressure and motor current slide down together, while winding temperature and vibration stay flat. They lag — so they can't break the tie."*  ·  *(~10s — let Play finish under the line)*

**Scene H1-P3 — DECISION SUPPORT**
[ACTION] Slide 3; **zoom on the two-outcome contrast** (Motor Burnout vs. Sand Bridging).
[VO] *"Same signature, two physical realities. One is cleared by easing the pump; the other is made catastrophic by it. The sensor alone cannot tell you which."*  ·  *(~9s)*

**Scene H1-P4 — ADDING CONTEXT**
[ACTION] Slide 4; cursor across the document types being fused.
[VO] *"The tie-breaker isn't another sensor — it's the well's own documents, read against the live signal."*  ·  *(~7s)*

**Scene H1-P5 — INDUSTRIAL APPLICATION**
[ACTION] Slide 5; brief hold on the three-industry cards.
[VO] *"And this same gap — state on the sensor, context in the documents — exists across every industry that runs physical assets."*  ·  *(~8s)*

### Scenario VO (your pattern: run → narrate → SCADA view → GDC view)

**Scene H1-S1 — start the run**
[ACTION] Click **▶ Run the Scenario** (a fresh scenario; verdict is randomly Gas Lock *or* Drawdown — you'll read the matching branch in S3).
[VO] *"Let's run it live. GDC is scoring every channel as the event unfolds — before any single hard limit is crossed."*  ·  *(~7s)*

**Scene H1-S2 — SCADA View**
[ACTION] Ensure **SCADA View** is selected; point to the underload trip.
[VO] *"This is what the control system sees. It protects the pump — it trips on its hard limit, as it should — but it offers no cause, and no read on sand risk."*  ·  *(~10s)*

**Scene H1-S3 — toggle to GDC Advisor (read the on-screen verdict)**
[ACTION] Click **GDC Advisor**; let the documents + **verdict** + **pgvector similarity** render; **zoom on the verdict card.**
[VO — if verdict = GAS LOCK] *"GDC retrieves the well's documents — annulus submerged, gas rising, sand history clean — and returns a cited verdict: gas lock. Ease the speed; keep the well online."*  ·  *(~11s)*
[VO — if verdict = FLUID DRAWDOWN] *"GDC retrieves the well's documents — fluid level below the intake, a known sand producer — and returns a cited verdict: drawdown. Shut it in; easing the speed here would seize the pump."*  ·  *(~11s)*

**Scene H1-S4 — HITL approve**
[ACTION] Show the **Approve** action; zoom the cited-evidence/similarity line.
[VO] *"Every recommendation is cited and reviewable. The engineer approves the action — GDC advises, the human decides."*  ·  *(~8s)*

---

# SECTION 2 — H2 CLASSIFY
**Slides (verified):** 1 THE SCENARIO "Waxy Crude. Routine PM. Then Nothing." · 2 AMBIGUOUS TELEMETRY "Fifty-Two Days Late. Bearings or Wax?" · 3 ADDING CONTEXT "Three Documents. One Truck. No Pull."
**Scenario replay (verified):** **SCADA / APM** vs **GDC Advisor** toggle · **Verdict** cards · three document reveals.

### Panel VO

**Scene H2-P1 — THE SCENARIO**
[ACTION] Slide 1; brief hold on the waxy-crude / PM-interval setup.
[VO] *"A different well, a slower problem. Waxy crude, on a routine treatment schedule — until a treatment is missed."*  ·  *(~7s)*

**Scene H2-P2 — AMBIGUOUS TELEMETRY**
[ACTION] Slide 2; **zoom on the four sensor tiles** (current up, efficiency down, vibration through its high-alarm line, pressure holding).
[VO] *"Weeks of drift — rising current, falling efficiency, vibration climbing through its high alarm. To a best-in-class platform, that pattern reads as bearing wear: pull the pump."*  ·  *(~11s)*

**Scene H2-P3 — ADDING CONTEXT**
[ACTION] Slide 3; hold on the three-document / one-truck framing.
[VO] *"But the bearings aren't the cause — and the proof is in three documents the platform never sees."*  ·  *(~7s)*

### Scenario VO (run → SCADA/APM view → GDC view)

**Scene H2-S1 — start the run**
[ACTION] Click **▶ Run the Scenario**; let efficiency fall and vibration climb past the missed-treatment point.
[VO] *"Run it. The degradation accumulates exactly the way mechanical wear would."*  ·  *(~5s)*

**Scene H2-S2 — SCADA / APM View**
[ACTION] Ensure **SCADA / APM** view; point to the bearing-wear conclusion.
[VO] *"The monitoring platform identifies the symptom correctly — and routes to the standard, expensive response: a pump pull."*  ·  *(~8s)*

**Scene H2-S3 — toggle to GDC Advisor (three documents → verdict)**
[ACTION] Click **GDC Advisor**; let the **three documents** reveal in sequence; **zoom each** (vendor service log → fluid PVT report → prior pull record); land on the green **Verdict**.
[VO] *"GDC fuses three documents: an overdue paraffin treatment, a fluid report showing this crude lays down wax, and a recent inspection with healthy bearings. The verdict flips — paraffin restriction, not bearing wear."*  ·  *(~13s — pace to the reveals)*

**Scene H2-S4 — the action contrast**
[ACTION] Show the two action cards (surface treatment vs. pull — AVERTED); zoom the AVERTED card.
[VO] *"The fix is a surface treatment, not a workover. The pull is averted — symptom versus cause, decided by the documents."*  ·  *(~8s)*

---

# SECTION 3 — H3 OPTIMIZE
**Slides (verified):** 1 THE SCENARIO "Maximum Production. Maximum Care." · 2 DECISION SUPPORT "Three Ceilings You Cannot Ignore." · 3 PAD OPTIMIZATION "Cloud Searches. Edge Enforces."
**Optimization (verified):** **SCADA Uniform** vs **GDC Optimal** · per-well setpoints · uplift card.
**Your note — explain what we're optimizing for** is built into S0/S1 below.

### Panel VO

**Scene H3-P1 — THE SCENARIO**
[ACTION] Slide 1; **zoom the GOR table** (cursor the lowest-gas wells, then the gassiest).
[VO] *"Now the whole pad. Six wells share one gas-handling limit — and every barrel carries gas, but some wells carry far more than others."*  ·  *(~9s)*

**Scene H3-P2 — DECISION SUPPORT (what we optimize for)**
[ACTION] Slide 2; point to each of the three ceilings (gas / motor temperature / run-life).
[VO] *"Here's the goal: the most oil the pad can produce while staying under the gas contract and never crossing any motor's temperature limit. Three ceilings, held at once."*  ·  *(~10s)*

**Scene H3-P3 — PAD OPTIMIZATION**
[ACTION] Slide 3; hold on the cloud-searches / edge-enforces split.
[VO] *"The division of labor: the cloud searches for the best setpoints; the edge enforces the safety limit on every candidate, locally."*  ·  *(~8s)*

### Scenario VO (run → explain SCADA Uniform → GDC Optimal)

**Scene H3-S1 — start the optimization**
[ACTION] Click **▶ Run the Optimization**; let the trial points populate and converge.
[VO] *"Run it. The optimizer explores the setpoint space — and only setpoints and scores ever leave the site."*  ·  *(~7s)*

**Scene H3-S2 — SCADA Uniform (the baseline)**
[ACTION] Show **SCADA Uniform**; point to every well at the same conservative speed.
[VO] *"The safe baseline throttles every well the same — which strands production on the wells that are most gas-efficient."*  ·  *(~8s)*

**Scene H3-S3 — GDC Optimal (read the table)**
[ACTION] Toggle to **GDC Optimal**; **zoom the per-well setpoint table** (lowest-gas wells run highest; the gassiest backs off); then the **uplift card**.
[VO] *"GDC's allocation runs the low-gas wells wide open and backs off the gassiest — more daily production, with gas held just under the ceiling."*  ·  *(~10s)*

**Scene H3-S4 — edge-safety / offline**
[ACTION] Show the edge-safety callout; zoom it.
[VO] *"And the temperature limit is enforced on the edge — so if the link drops mid-search, safety never drops with it."*  ·  *(~8s)*

---

# CLOSE  ·  ~12s
**Scene CLOSE — Operations / Financials**
[ACTION] Toggle to *Operations* then *Financials*; rest on cumulative savings (no zoom; calm).
[VO] *"Diagnose the ambiguous, catch the wrong fix, and push every safe barrel — one sovereign stack, cited and reviewable, inside your perimeter. Lower lifting cost, longer asset life, higher runtime."*  ·  *(~12s)*

---

## TIMING / SYNC NOTES
- **Aligning Play to VO:** for H1-P2 and the three scenario runs, start the line a beat after you click ▶ so the motion and the words land together. If a run finishes before the line, hold the last frame; if the line finishes first, let the animation breathe before cutting.
- **Per-scene recording:** capture each scene's screen action as its own clip (QuickTime), then attach that scene's [VO] in Vids (same per-scene Voiceover method as the intro). One action ↔ one line = automatic sync.
- **Total estimate:** Section 0 (~25s) + H1 (~1:30) + H2 (~1:10) + H3 (~1:20) + close (~12s) ≈ **~4:30 demo**. With the ~60s Veo intro → **~5:30 total**, under 6:00.
- **Realism check (verified against code):** view toggles are literally "SCADA View"/"GDC Advisor" (H1, H2) and "SCADA Uniform"/"GDC Optimal" (H3); H1 verdict is randomly gas-lock or drawdown (two branches provided); H2 reveals exactly three documents; pgvector similarity + Approve/HITL exist on H1. No spoken numbers, so randomized replay values can't desync the narration.
