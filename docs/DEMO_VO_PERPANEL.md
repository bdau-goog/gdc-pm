# GDC Demo — Per-Panel / Per-Scenario Voiceover (live screen recording)
**Pairs with:** `VEO_COLD_OPEN.md` (intro) → this file (the demo). Same persona/voice as V3/V4: **Google Cloud third-party, operator-grounded, CxO-safe, NO exact numbers spoken** (panels carry the figures).
**Structure:** one **Vids scene per panel / per scenario beat**, each with its own VO line and an **action note** (zoom / Play / toggle). Verified against the live slides + replay templates (h1/h2/h3.html, tab_h1/h2/h3.html).

## Conventions
- **[ACTION]** = what you do on screen for that scene (advance slide / click Play / toggle view / zoom in post).
- **[VO]** = the line to read for that scene (≈ matches the on-screen dwell time).
- **Zoom** notes are for post (1.15–1.2× crop on the named element). "Play" = click the panel's ▶ Play.
- **Scenario pattern you specified:** start the run → VO while it animates → explain **SCADA View** → toggle to **GDC Advisor** view. Verified the toggle is literally labeled **"🟡 SCADA View" / "🟢 GDC Advisor"** (H1/H2).
- **Numbers stay on screen.** Read meaning, not figures.

---

## PART A↔B ALIGNMENT — VERIFIED (BS+37 check against live app)
| Item | Script | Live app | Status |
|---|---|---|---|
| H1/H2 view toggle labels | SCADA View / GDC Advisor | `🟡 SCADA View` / `🟢 GDC Advisor` | ✅ |
| H1 verdict cards | GAS LOCK / FLUID DRAWDOWN | `✔ GAS LOCK CONFIRMED` / `⚠ FLUID DRAWDOWN CONFIRMED` | ✅ |
| H1 HITL | "Awaiting RTOC approval / Approve & Execute" | `GDC Agent · Action package ready · Awaiting RTOC approval` + `✔ Approve & Execute` | ✅ |
| pgvector / RAG | present | `AlloyDB pgvector < 2s`, cosine similarity shown | ✅ |
| Slide titles (H1×5, H2×3, H3×3) | all named | all match verbatim | ✅ |
| Nav tabs | Intro / Discern / Classify / Optimize / ⓘ Reference | **exact** (no "How It Works", no "Operations", no "Financials") | ✅ (§0 updated below) |
| H3 view toggle | "SCADA Uniform / GDC Optimal" | **No toggle** — table has cols `Baseline Hz / GDC Optimal / Δ Hz` | ✅ (H3 block updated below) |
| Run buttons | "▶ Run the Scenario / Optimization" | H1/H2: `↺ New Scenario` + ▶ scrub; H3: `⚡ Run Vizier Optimization` | ✅ (labels updated below) |
| Close tabs | Operations → Financials | **Orphaned** (not in nav — BS+27 known) | ✅ (close updated; tabs = Known Integrity item) |

---

# SECTION 0 — "MEET GDC" (Intro tab — 3 slides)  ·  ~33s

*Grounded in the actual Intro deck (3 slides: "What is GDC?" · "When Should You Consider GDC?" · "GDC — Flexible Deployment Models"). The cold-open (Scenes 6–8) already told the "what GDC does for ESPs" story; this section tells "what GDC is" at the platform level before the live scenarios.*

**Scene 0.1 — "What is GDC?" (Slide 1)**
[ACTION] Open **Intro** tab (lands on Slide 1 "What is GDC?"); cursor the GKE→GDC arrow; hold on the glass card ("Google-Managed · AI/ML Enabled").
[VO] *"At its core, GDC is a fully supported version of Google Kubernetes Engine — Google-managed, AI-enabled — deployed at the edge, on hardware that sits inside your own facility."*  ·  *(~10s)*

**Scene 0.2 — "When Should You Consider GDC?" (Slide 2)**
[ACTION] Advance to Slide 2; cursor across the four pillars.
[VO] *"It's built for four realities of field operations: data that must stay sovereign, operations that must survive a network outage, decisions that can't wait on a round-trip to the cloud, and the sheer gravity of data generated at the wellsite."*  ·  *(~12s)*

**Scene 0.3 — "Flexible Deployment Models" (Slide 3)**
[ACTION] Advance to Slide 3; cursor the three model cards (Connected · Software-Only · Air-Gapped); click **▶ View Demo →** to enter the live scenarios.
[VO] *"And it deploys the way your site allows — a managed connected rack, software on your own hardware, or a fully air-gapped appliance for the most remote sites. Let's see it work."*  ·  *(~11s)*

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
[ACTION] Click **↺ New Scenario** to load a fresh scenario (verdict is randomly Gas Lock *or* Drawdown — you'll read the matching branch in S3); the scenario loads and the ▶ play transport begins.
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
[ACTION] Click **↺ New Scenario** to load a fresh run; let efficiency fall and vibration climb past the missed-treatment point.
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
**Optimization (verified):** **⚡ Run Vizier Optimization** → trial scatter converges → per-well table (`Baseline Hz` / `GDC Optimal` / `Δ Hz`) → uplift card → optional **✔ Deploy Recommendation**. No "SCADA Uniform / GDC Optimal" toggle exists — the contrast is between the **Baseline Hz column** (equal throttle) and the **GDC Optimal column** (differentiated by GOR).
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

### Scenario VO (run → baseline vs GDC-optimal table → uplift → edge safety)

**Scene H3-S1 — start the optimization**
[ACTION] Click **⚡ Run Vizier Optimization**; let the trial scatter populate and converge toward the optimum.
[VO] *"Run it. The optimizer explores the setpoint space — and only setpoints and scores ever leave the site."*  ·  *(~7s)*

**Scene H3-S2 — the baseline (Baseline Hz column)**
[ACTION] When trials settle, **zoom 1.15× on the per-well setpoint table**; cursor the **Baseline Hz column** — every well near the same conservative speed.
[VO] *"The safe baseline throttles every well the same — which strands production on the wells that are most gas-efficient."*  ·  *(~8s)*

**Scene H3-S3 — GDC Optimal (read the table and uplift card)**
[ACTION] Cursor across the **GDC Optimal column** (lowest-gas wells run highest; the gassiest backs off); then pan to the **uplift card** (+bbl/d · cash uplift).
[VO] *"GDC's allocation runs the low-gas wells wide open and backs off the gassiest — more daily production, with gas held just under the ceiling."*  ·  *(~10s)*

**Scene H3-S4 — edge-safety / offline**
[ACTION] Cursor the **Binding Constraint selector** (GAS TAKEAWAY active); hold on the thermal-limit provenance note below the table.
[VO] *"And the temperature limit is enforced on the edge — so if the link drops mid-search, safety never drops with it."*  ·  *(~8s)*

---

# CLOSE  ·  ~12s
**Scene CLOSE — H3 uplift + ⓘ Reference (sovereign deployment)**
[ACTION] Rest on the **H3 uplift card** (+bbl/d, cash uplift) — let the numbers sit; then navigate to **ⓘ Reference** tab; cursor the "Operator RTOC / Sovereign Data Center" deployment panel. Calm, settled framing. *(Note: Operations and Financials templates exist in the codebase but are not currently wired into the nav — do not attempt to navigate there. Known Integrity item: wire tabs into nav = future code task.)*
[VO] *"Diagnose the ambiguous, catch the wrong fix, and push every safe barrel — one sovereign stack, cited and reviewable, inside your perimeter. Lower lifting cost, longer asset life, higher runtime."*  ·  *(~12s)*

---

## TIMING / SYNC NOTES
- **Aligning Play to VO:** for H1-P2 and the three scenario runs, start the line a beat after you click ▶ so the motion and the words land together. If a run finishes before the line, hold the last frame; if the line finishes first, let the animation breathe before cutting.
- **Per-scene recording:** capture each scene's screen action as its own clip (QuickTime), then attach that scene's [VO] in Vids (same per-scene Voiceover method as the intro). One action ↔ one line = automatic sync.
- **Total estimate:** Section 0 (~33s) + H1 (~1:30) + H2 (~1:10) + H3 (~1:20) + close (~12s) ≈ **~4:45 demo**. With the ~65s Veo intro → **~5:50 total**, under 6:00 (tight — if a test cut runs long, trim ~10 words from H2 narration, per V4 Appendix C).
- **Realism check (verified against live app, BS+37):** H1/H2 toggles are literally "🟡 SCADA View"/"🟢 GDC Advisor"; H3 has no toggle — differentiation is **Baseline Hz** vs **GDC Optimal** columns in the table; H1 verdict is randomly gas-lock or drawdown (two branches provided); H2 reveals exactly three documents; pgvector similarity + Approve/HITL exist on H1; run buttons are `↺ New Scenario` (H1/H2) and `⚡ Run Vizier Optimization` (H3). No spoken numbers, so randomized replay values can't desync the narration.
