# GDC Demo — Build Sprint Plan
**Created:** Session AF (June 10, 2026) | **Spec basis:** DEMO_MASTER.md Session AF

This plan sequences all remaining build work to get the demo to "see it all" — including the animated explanatory briefings, the How It Works reconciliation, and the Vids deliverable.

---

## SPRINT 0 — Strategy Lock ✅ COMPLETE (Session AF)

**Deliverable:** `docs/DEMO_MASTER.md` — Session AF full rewrite. Committed `0c35a8f`.

Changes locked:
- §3 STATE-vs-CONTEXT universal moat (replaces "physics-impossibility" premise)
- §3 4-industry mapping (O&G / P&E / Manufacturing / Mining)
- §3 Retraining & Drift settled position
- §4.1 premise corrected: intake-only scoping + sand-as-stakes (replaces "physically identical forever")
- §9 NEW: Deployment & Data Architecture (RTOC-sovereign canonical, placement spectrum, 3 sovereignty pillars, Starlink reality, 5 retired claims with replacements)
- Claim Ledger: P4 updated citation; PREMISE + P5-A + P5-B + P5-C added
- Version bumped to Session AF

---

## SPRINT 1 — How It Works Reconciliation
**File:** `gke/fault-trigger-ui/index.html` (one batched edit)
**Estimate:** 1 Act session

### Changes (all batched into ONE replace_in_file call):

| # | What | Why |
|---|---|---|
| 1 | Rewrite `ⓘ "Why Not Cloud?"` panel (info panel lines ~1809–1817) | Fix 2 integrity violations: delete "200 GB/day" + "VSAT 15–25 min"; replace with 3 sovereignty pillars + IEC 62443 / Purdue / NERC-CIP scoping |
| 2 | Retitle deployment: "E-House on the well pad" → "Operator RTOC / sovereign data center (inside the security perimeter)" | Matches DEMO_MASTER §9 RTOC-sovereign canonical |
| 3 | Add one muted anchor line below GDC pipeline diagram | "Runs inside the operator's security perimeter — IEC 62443 / NERC-CIP (P&E) · sovereign, outage-immune" |
| 4 | Retire "no cloud dependency for the decision" tagline | → "No public-cloud dependency — runs sovereign, outage-immune" |
| 5 | Reframe SCADA path label | "alarm-based, threshold-driven" → "control-layer telemetry path" + one-liner noting APM platforms add ML in the historian/cloud |
| 6 | Add one "generalizes across industrial verticals" line in How It Works | Below the 3-column TAGS / TAG-PATTERNS / DOCUMENTS centerpiece — references the 4 verticals |

**Integrity fixes confirmed in this sprint:** 200 GB/day ✅ deleted, VSAT 15–25 min ✅ deleted, "decision at the pad" ✅ retired, NERC-CIP for O&G ✅ scoped.

**Verification:** `grep -n` against deployed HTML for the old claim strings.

---

## SPRINT 2 — H1 Briefing (6 Panels, Animated)
**File:** `gke/fault-trigger-ui/index.html` + minor `app.js` (separate batched calls per sub-sprint)
**Estimate:** 2–3 Act sessions (large new HTML)

### Design spec (from DEMO_MASTER §4 + Session AF discussion):

H1 now loads in **Briefing mode** by default (instead of auto-starting the scenario). The Briefing is a 6-panel stepped explainer that ends with `▶ Run the Scenario`.

#### Panel 1 — This Well (the setup)
- **Scope declaration (static card):** "Well ESP-ALPHA-N · Mature Permian Basin · Moderate-sand formation · AR-trim pump · **Intake-only PDG** (no discharge gauge) · Operating at 52 Hz"
- Animation: wellbore SVG showing pump running nominal — fluid column high, green amps/PIP tiles
- Purpose: establish the well character and sand stakes before anything happens

#### Panel 2 — What is an Unload?
- Animation: PIP + Amps tiles decline together; wellbore SVG shows fluid/gas boundary shifting
- Text: "The pump stops moving fluid effectively — Pump Intake Pressure and Motor Load fall together"
- Reuses existing wellbore SVG + dual-axis chart

#### Panel 3 — One Signature, Two Causes (the hook)
- **Full-screen split:** LEFT = Gas Lock wellbore (annulus full, bubbles entering pump) | RIGHT = Drawdown wellbore (fluid level falling)
- **Below both:** the SAME PIP/Amps trace
- "On this well's sensor, the live decline looks the same."
- Animated: bubbles rising left, fluid level dropping right — both produce identical chart below

#### Panel 4 — STATE vs. CONTEXT (the moat)
- **Full-screen two-column animated reveal:**
  - LEFT (STATE): PIP, Amps, Temp, Vib readouts. Pulse in. "Even a perfect gauge sharpens the STATE. It cannot report what happened last week."
  - RIGHT (CONTEXT): Document cards appear one by one — workover record · GOR trend · offset-frac report · shift note. "The deciding context lives here. Not on any sensor."
- "You cannot instrument your way out of a context gap."

#### Panel 5 — Why Sand Makes the Stakes Asymmetric
- **Scope badge visible:** "moderate-sand well · AR-trim"
- **2×2 animated decision matrix:**
  - Cell by cell reveals: Trim + Gas Lock (✅) → Trim + Drawdown (❌ $150k seizure, animated sand packing) → Shut-in + Gas Lock (⚠️ deferred production) → Shut-in + Drawdown (✅ recoverable)
- "Blind to the cause, trim risks seizure. Shut-in is safe in both — the rational default."
- "The context that removes the blindness is in the documents. GDC reads them in seconds."

#### Panel 6 — This Pattern Is Universal (the platform claim)
- **4-row animated table** (appears row by row):
  - O&G ESP · Power transformer · Factory motor · Haul truck
  - Each: sensor STATE → document CONTEXT arrow
- "This is not an oilfield trick. It is the structural gap in every industrial AI deployment."
- `[▶ Run the Scenario]` CTA — hands off to existing H1 Scenario Replay

#### Visual requirements (user-stated):
- **Animations must be strong, fill the screen, perfect for the narrative**
- CSS transitions + SVG animations preferred (no external deps)
- Each panel is full-width, full-height of the briefing viewport
- Panel navigation: prev/next stepper (not tabs) — linear guided flow

#### Sub-sprint sequence:
- **2a:** Briefing container + Panel 1 + Panel 2 (wellbore SVG reuse)
- **2b:** Panel 3 (split-screen two-cause animation — most complex)
- **2c:** Panel 4 (STATE vs. CONTEXT two-column reveal)
- **2d:** Panel 5 (2×2 decision matrix animation)
- **2e:** Panel 6 (4-row table + CTA handoff)

---

## SPRINT 3 — H2 Briefing (3 Panels, Animated)
**File:** `gke/fault-trigger-ui/index.html`
**Estimate:** 1 Act session

Same Briefing-mode pattern. Aligns to the state-vs-context thesis.

#### Panel 1 — What is Slug Flow?
- Surface slugs → cyclic vibration at pump intake
- Animated: slug pulses in production tubing, PDG gauge showing cyclic PIP

#### Panel 2 — Why It Looks Like a Failing Pump
- Vibration rising (alarming STATE) — SCADA HI fires
- "The sensor shows the pattern. It doesn't tell you what's driving it."

#### Panel 3 — STATE vs. CONTEXT (the exoneration)
- STATE: vibration rising + **flat motor temp** → "something changed, but not at the motor"
- CONTEXT cards reveal: choke log (3 adjustments) · separator test (1.8 bbl slugs) · shift note ("pumping rough but temp normal")
- "The documents say: do NOT pull. $1,500 surface adjustment vs. $150k false alarm."
- `[▶ Run the Scenario]` CTA

---

## SPRINT 4 — Vids Narrative + Presenter Script
**File:** `docs/VIDEO_SCRIPT.md` (new file)
**Estimate:** 1 Act session (docs only, no code)

**Structure (6 segments, ~5 minutes):**

| Segment | Duration | Content | Maps to Briefing panels |
|---|---|---|---|
| **1 — The Pattern** | ~45s | STATE-vs-CONTEXT across 4 industries. "You cannot instrument your way out of a context gap." | Panel 4 + Panel 6 |
| **2 — This Well** | ~30s | Well setup — intake-only, moderate sand, 25-min thermal window. The stakes. | Panel 1 + Panel 5 |
| **3 — The Hook** | ~30s | One signature, two causes. "On the data you have, both look the same." | Panel 2 + Panel 3 |
| **4 — H1 Discern (live)** | ~90s | Scenario replay: sensors decline → SCADA alarms → GDC already retrieved 3 docs → correct action prescribed | Live H1 demo |
| **5 — H2 Classify (live)** | ~45s | Slug flow exoneration — don't pull → $1.5k vs $150k | Live H2 demo |
| **6 — Why GDC Sovereign** | ~45s | RTOC-sovereign. IEC 62443. Outage-immune. 4-industry claim. "The answer was never in the sensors." | §9 pillars |
| **7 — Close** | ~15s | One sentence. "GDC: the AI goes to the data." | §3 spine sentence |

**Sovereign MLOps beat** (30s, can fold into Segment 6): "Train on your own fleet history in Vertex. Deploy to GDC. Run on-prem. The model lifecycle is sovereign too."

---

## Total Estimated Sessions Remaining

| Sprint | Work | Sessions |
|---|---|---|
| Sprint 1 — How It Works reconciliation | index.html (1 batched edit) | 1 |
| Sprint 2a–e — H1 Briefing | New HTML, 5 sub-sprints | 2–3 |
| Sprint 3 — H2 Briefing | New HTML, 3 panels | 1 |
| Sprint 4 — Vids script | Docs only | 1 |
| **Total** | | **5–6 sessions** |

---

## Token Budget Notes

- `index.html` is ~2,760 lines (~150K tokens per return). **Every edit to index.html = 150K tokens consumed.** Sub-sprint 2a–2e are explicitly planned as separate sessions to stay within budget.
- Each session: max 2–3 Sprint 1 changes batched into one `replace_in_file` call. Never open index.html cold — always grep for line numbers first.
- **Sprint 0 is done and committed.** Sprint 1 can start immediately in next session.
