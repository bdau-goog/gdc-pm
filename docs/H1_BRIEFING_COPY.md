# H1 Briefing Panels — Verbose Copy Archive
**Archived:** Session BS+7 (2026-06-15) — before "slide-not-document" condensation pass  
**Purpose:** Reference for restoring detailed prose if needed for documentation, investor decks, or future wordier variants.  
**Source:** `gke/fault-trigger-ui/templates/tab_h1.html` (git: 282441f)

---

## PANEL 1 — This Well

**Section tag:** THE SCENARIO

**Headline:** Same Signal. Two Causes. One Right Decision.

**Body paragraph (main):**
A Permian ESP well goes into unloading at 06:23. The RTOC operator's screen shows the same sensor decline for two root causes with opposite correct actions — one costs $2,500, the other risks $150,000.

**Context callout (blue left-border box):**
The RTOC has PIP, Amps, Winding Temp, and Vibration in real time. The full document corpus — shift notes, sonic surveys, GOR lab reports, workover records — is in AlloyDB. **GDC reads and fuses it in seconds.**

**Well metadata card (WELL ESP-ALPHA-N · PAD ALPHA · PERMIAN BASIN):**
- Formation: Mature Permian unconventional · moderate-sand
- Pump: ESP · AR-trim impellers (abrasion-resistant)
- Sensor string: Intake-only PDG — PIP, Motor Amps, Winding Temp, Vibration · *no downhole discharge gauge* (~90% of Permian ESPs)
- Operating: 52 Hz · 3,120 RPM · nominal PIP ~1,245 PSI

**Metric tiles:**
- $8–15/bbl — ESP lifting cost
- $2.5k–$150k — outcome range / event
- <2s — GDC doc fusion

**SVG labels:**
- X-MAS (wellhead)
- PDG / INTAKE (sensor callout)
- no disch. / gauge (annotation)
- PUMP ✓, MOTOR ✓ (components)
- 197°F · 52 Hz (motor state)
- PERFS, FORMATION, ~9,800 ft MD

**Sensor readout tiles (nominal):**
- PIP: 1,245 PSI ●
- AMPS: 68.2 A ●
- TEMP: 197°F ●
- VIB: 1.4 mm/s ●

---

## PANEL 2 — What is an Unload?

**Section tag:** THE EVENT

**Headline:** What is an Unloading Event?

**Body paragraph:**
The pump stops moving fluid effectively. **PIP and Motor Amps decline together** — while Winding Temp and Vibration stay flat in the early window.

**Sensor tile descriptions (scrubber-driven, FAULT state text):**

*PUMP INTAKE PRESSURE (PIP):*
- Header: "PUMP INTAKE PRESSURE ↘ / DECLINING"
- Range: ~1,245 PSI nominal → ~850 PSI fault
- Physics: Hydraulic head drops as gas enters pump stages or reservoir fluid level depletes below intake

*MOTOR AMPS:*
- Header: "MOTOR AMPS ↘ / DECLINING"
- Range: ~68 A nominal → ~28 A fault
- Physics: VFD current drops as the impeller loses hydraulic resistance — correlated with PIP decline

*WINDING TEMP:*
- Header: "WINDING TEMP → / INITIALLY FLAT"
- Range: ~197°F nominal, stays flat early
- Physics: Motor cooling still flowing — temp is the *lagging* signal. Rises only with sustained gas lock (API RP 11S §4.2)

*VIBRATION:*
- Header: "VIBRATION → / FLAT"
- Range: ~1.4 mm/s nominal, stays flat
- Physics: No bearing-contact change during hydraulic unloading — distinguishes this from bearing wear (H2 scenario)

**Key insight callout (bottom, blue box):**
Key insight: PIP and Amps decline together while Temp and Vib stay flat. The cause — gas lock or drawdown — is not in any of these numbers. It lives in the field documents. → THE HOOK: one signature · two opposite actions — THE MOAT: STATE vs CONTEXT — THE PLATFORM: universal pattern.

---

## PANEL 3 — One Signature, Two Causes

**Section tag:** THE HOOK

**Headline:** One Signature, Two Causes

**Body paragraph:**
Both failure modes produce the **identical PIP + Amps decline** on an intake-only sensor string. The cause — and the correct action — are not in these numbers.

**LEFT column — GAS LOCK:**
- Header: GAS LOCK
- Sub: Annulus HIGH · Gas pocket at pump intake
- SVG labels: HIGH / STABLE (fluid level), bubbles at intake, PUMP ⚠, MOTOR ✓, PERFS, FORMATION · HIGH GOR
- Action callout (blue box): ✔ Safe action: VFD trim 52→44 Hz — gas pocket vents up flooded annulus. ~$2,500

**RIGHT column — FLUID DRAWDOWN:**
- Header: FLUID DRAWDOWN
- Sub: Annulus DEPLETED · Dynamic fluid level falling
- SVG labels: GAS (vapor zone), LOW (fluid level), SAND (at intake), PUMP ⚠, MOTOR ✓, PERFS, FORMATION · LOW LEVEL
- Action callout (red box): ✘ VFD trim is riskier: velocity drops toward sand-transport limit at 44 Hz. Shut-in is the correct action for this well type. ~$150k risk

**Bottom callout (same sensor output banner):**
- Left label: SAME SENSOR OUTPUT ↓
- Right text: "On this well's sensor, the live decline looks the same."
- Bars: PIP (declining, blue) + AMPS (declining, green)

---

## PANEL 4 — STATE vs. CONTEXT

**Section tag:** THE MOAT

**Headline:** STATE vs. CONTEXT

**Body paragraph:**
Sensors report what the well is doing *right now*. The correct action depends on what *happened* — and that is categorically not a real-time measurement.

**LEFT column — STATE:**
- Column header: STATE
- Sub: "What the sensors report — right now"
- Tag rows (animated reveal):
  - PIP: 612 PSI ↓
  - AMPS: 34.2 A ↓
  - WINDING TEMP: 246 °F —
  - VIBRATION: 0.41 in/s —
- Closing italic: "Even a perfect gauge sharpens the STATE. It cannot report what happened last week."

**RIGHT column — CONTEXT:**
- Column header: CONTEXT
- Sub: "What no sensor can report"
- Document cards (animated reveal):
  1. WORKOVER RECORD — Last workover: 14 months ago · annulus condition unknown
  2. GOR TREND — Gas-Oil Ratio rising +18% over 60 days — reservoir depletion signal
  3. OFFSET FRAC REPORT — Adjacent frac 8 days ago · pressure transient still propagating
  4. SHIFT NOTE — "Pumping rough for 3 days — no change in surface rate" — Night crew, 06:00
- Closing italic: "The deciding context lives here. Not on any sensor."

**Full-width bottom statement:**
You cannot instrument your way out of a context gap.

---

## PANEL 5 — How Operators Decide Today (The Decision)

**Section tag:** THE DECISION

**Headline:** How Operators Decide Today

**Sub-badge:** moderate-sand well · AR-trim

**Alarm banner:**
- Label: ONE ALARM: UNDERLOAD
- Body: Cause unknown — gas lock **OR** fluid drawdown?

**LEFT card — VFD TRIM 52 → 44 Hz:**
- ✔ Right for gas lock — stays online
- ✔ Preserves production ~$2,500
- ✘ Riskier if drawdown
- Sand risk callout: Sand makes it costly — velocity drops toward transport limit

**RIGHT card — SHUT-IN:**
- ✔ Safe for **both** causes
- ✔ Pump always protected
- ✘ Defers production
- + restart cost $3–8k · every time

**Bottom closing statement:**
Safe is not free. The protective shut-in is paid on every ambiguous alarm — including the ones that were only gas lock.

**Bottom sub-line:**
GDC reads the documents. The confident call replaces the cautious default.

---

## PANEL 6 — This Pattern Is Universal

**Section tag:** THE PLATFORM

**Headline:** This Pattern Is Universal

**Body paragraph:**
STATE is what every gauge reports. CONTEXT is what decides. This gap exists in every industry that runs physical assets.

**Table rows (animated, 3 rows):**

*Row 1 — O&G / ESP Well:*
- STATE: PIP ↓ · Amps ↓ — Intake-only PDG — identical on gas lock & drawdown
- CONTEXT: Workover record · GOR trend / Shift note from tour operator

*Row 2 — P&E / Transformer:*
- STATE: Load current ↑ · winding temp ↑ — SCADA flags thermal exceedance
- CONTEXT: Loading plan · maintenance log / Seasonal demand forecast

*Row 3 — MFG / Factory motor:*
- STATE: Vibration ↑ · temperature nominal — Same signature as bearing wear
- CONTEXT: Lubrication record · OEM bulletin / Line throughput log

**Closing statement:**
This is not an oilfield trick. It is the structural gap in every industrial AI deployment.

**Closing sub-line:**
The AI goes to the data.

---

## Notes on copy decisions (Session BS+7)

- The "Key insight" box at the bottom of P2 was flagged by user as "unnecessary" — it summarises what the narration covers.
- P4's 4-row STATE tag-list was identified as "too jargon-heavy for non-engineers" — redesign as arc-gauge cluster planned.
- P5's action cards were flagged as verbose — narration carries the economics story.
- P6 was missing industry icons — to be added in Phase 2.
- All numbers in this copy are sourced from deployed code (FAULT_PROFILES, RESOLUTION_OPTIONS) and pass the Claim Ledger. They should not be changed without updating the Claim Ledger.
