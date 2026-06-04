# GDC Predictive Maintenance — Master Demo Specification

**Version:** Session J (June 4, 2026)  
**Status:** AUTHORITATIVE — supersedes DEMO_NARRATIVE.md and DEMO_NARRATIVE_UPDATE.md  
**Usage:** Every new session reads this document before writing any code. Every design decision is captured here. Disagree with something? Update this file first, then update the code.

---

## 1. THE PRODUCT STATEMENT

GDC Edge AI gives production operators more time before a failure becomes irreversible. More time creates more options. More options allow cheaper, lower-risk solutions. This translates directly to capital preserved and production protected.

The demo proves this across three distinct dimensions — protection, discrimination, and optimization — using a single continuous technology stack running entirely on-premises without cloud dependency.

### The Simulation Framing (Acknowledge, Don't Hide)

The demo uses physics-accurate simulated sensor data and hand-crafted operational documents. This is appropriate for a demonstration environment and is never hidden. The fault injection button is visible and labeled.

**One sentence for the audience:** *"In a customer deployment, the fault injection button is replaced by a live data connection to the customer's existing sensors. The architecture, AI models, RAG pipeline, and decision workflows are identical."*

The technology stack is 100% real and production-grade:
- XGBoost health models: trained, validated, running on-cluster
- RabbitMQ message broker: production durable message queue
- AlloyDB Omni: PostgreSQL + pgvector, real persistent storage
- Gemma 4 (gemma4:latest): running on NVIDIA L4 GPU, no cloud required
- Vertex AI Vizier: real Google Cloud optimization service (H3)
- The failure physics: accurate per API RP 11S, OEM manuals, and published SPE papers

---

## 2. CORE VALUE PROPOSITION — THE DEFENSIBLE SCADA vs ML ARGUMENT

### What Advanced SCADA CAN Do (acknowledge honestly)
Modern SCADA platforms (OSIsoft PI, Ignition, Wonderware) can:
- Rate-of-change alarms on individual sensors
- Simple two-sensor correlation rules
- Calculated efficiency metrics (e.g., volumetric efficiency)
- Trend deviation alarms

### Where ML Genuinely Wins (three specific, defensible claims)

**Claim 1 — Fault Discrimination:**
SCADA can detect that two sensors are declining together. It cannot tell you *which* failure mode it is. Declining PIP + declining amps could be gas lock, well depletion, downhole restriction, surface backpressure issue, or sand ingress. Each requires a different response. Acting on the wrong diagnosis costs money. The XGBoost model discriminates between these specific fault signatures at ~94% confidence because the *shape*, *rate*, and *sensor correlation pattern* differ for each.

**Claim 2 — Probability Scoring Before Thresholds (SCADA's Architecture Cannot Do This):**
SCADA alarms are deterministic: threshold crossed = alarm. ML outputs a continuous probability score at every 5-second reading, even when all sensors are within nominal ranges. When the health score reaches 0.82, the model is already at 67% gas lock confidence — no SCADA rule has fired. This is genuinely earlier detection: not by configuring tighter thresholds, but by recognizing probabilistic precursor patterns that precede any threshold crossing.

**Claim 3 — Context Fusion (The Unique Differentiator):**
No SCADA system reads the shift note. No SCADA system queries the separator gas test. No SCADA system cross-references the overnight GOR trend from the production lab report. The RAG pipeline fuses sensor telemetry with operational documents (shift notes, lab reports, PM records, OEM manuals, field intelligence) to reach a more comprehensive and earlier assessment. SCADA sees a declining pressure line. GDC sees a diagnosis with a documented evidence chain.

---

## 3. THE THREE-ACT NARRATIVE STRUCTURE

| Act | Scenario | Asset | Core Claim | GDC Advantage |
|-----|----------|-------|------------|---------------|
| H1 | Gas Lock | ESP-ALPHA-1 | *More time = more options* | 25 min before SCADA alarms |
| H2 | Slug Flow | ESP-ALPHA-3 | *Right diagnosis = right action* | Prevents $150k unnecessary pump pull |
| H3 | VFD Optimization | ESP-ALPHA-1 | *Don't just protect — maximize* | $1.2M additional revenue over 90 days |

**Narrative arc:** Protect → Discriminate → Optimize

H1 proves: GDC prevents catastrophic failure by detecting the precursor pattern with enough lead time to act cheaply.  
H2 proves: GDC prevents expensive over-reaction by distinguishing surface problems from downhole problems.  
H3 proves: GDC doesn't just keep you from losing — it actively maximizes what you can gain.

---

## 4. H1 SPECIFICATION — GAS LOCK EMERGENCY

### The Physics (defensible per API RP 11S)

**What is gas lock:**
An ESP is a multi-stage centrifugal pump submerged in production wellbore fluid (oil + water + gas mixture). When Gas Void Fraction (GVF) at pump intake exceeds the pump's handling threshold (~60–65% for standard designs, per Baker Hughes Centrilift design guides), the impeller stages fill primarily with gas. A centrifugal pump cannot efficiently pressurize compressible gas. Pump throughput drops dramatically.

**The actual failure mechanism — NOT "running dry":**
The ESP is still submerged in fluid. The failure is thermal, not mechanical dryout. When gas lock occurs, fluid flow through the motor annulus collapses — the motor loses its cooling medium. The motor continues generating heat (electrical input - hydraulic output ≈ 0) but the flow that removes that heat is gone. Motor winding temperature rises at 3–8°F per minute until Class H insulation (180°C continuous rating per API RP 11S and IEEE 117) is exceeded. Winding insulation failure is irreversible.

**The 25-minute PNR:**
25 minutes is a defensible conservative estimate based on:
- Motor thermal physics: 3–8°F/min rise from operating temperature (~175–200°F) to insulation damage threshold (~250–280°F)
- API RP 11S and ESP manufacturer guidelines (Baker Hughes, Schlumberger) recommend maximum 15–30 minutes gas-locked running
- The demo uses 25 minutes as the mid-range conservative value

**What to say if challenged on timing precision:** *"25 minutes is a conservative estimate based on ESP motor thermal physics and manufacturer guidelines consistent with API RP 11S. The actual value varies by motor size, wellbore temperature, and pump configuration. The point is: the window is measured in minutes, not hours — which makes edge detection, not cloud analytics, the only viable approach."*

### H1 Demo Flow (5x compressed time — real 25 min in ~5 demo min)

1. **Tab opens → nominal state.** Charts are LIVE and ticking from real `telemetry_events` DB rows. SCADA card shows real sensor values (~1,400 PSI, ~198°F, ~75A). Well schematic shows mostly liquid with minor gas bubbles. GDC Copilot says: *"Monitoring ESP-ALPHA-1. All sensors nominal. Ready to analyze downhole anomalies."*

2. **Click "Inject Gas Lock."** Evidence wall activates in sequence. LLM Copilot auto-starts streaming assessment. Well animation shifts: gas bubbles increase, motor temperature color shifts amber. Charts show the live decline.

3. **Window of Options timeline** shows three options available now; the $0 option's viability clock runs down in real-time.

4. **Operator clicks "Approve VFD Speed-Down."** Charts animate recovery: PIP climbs, amps stabilize, motor temperature cools. LLM Copilot confirms: *"Recovery on track. PIP rising at expected rate."*

5. **Capital preserved: $150,000. Direct cost: $0.**

### H1 UI Layout

```
╔══════════════════════════════════════════════════════════════════════════╗
║ STATUS BAR: [SCADA: ✓ All Nominal · No alarms] | [GDC: 94% gas_lock ⚠] ║
╠═══════════════════════════════════╦════════════════════════════════════╣
║ LEFT (55%) — THE WELL             ║ RIGHT (45%) — THE EVIDENCE & MIND  ║
║                                   ║                                     ║
║ [2D SVG Well Schematic]           ║ [EVIDENCE CONVERGENCE WALL]         ║
║ Wellbore cross-section            ║ 5 source categories, activating     ║
║ Animated gas/liquid particles     ║ in sequence on injection            ║
║ Motor temp color gradient         ║                                     ║
║                                   ║ [CITED LLM COPILOT — streaming]     ║
║ [Primary Plotly Chart]            ║ Auto-triggers on inject             ║
║ Blue: live telemetry              ║ Superscript citations [¹][²][³]     ║
║ Orange dashed: ML projection      ║ Clickable to source document        ║
║ Red dashed: SCADA threshold       ║ Multi-turn follow-up chat           ║
║ Orange bar: PNR marker            ║                                     ║
║                                   ║                                     ║
║ [WINDOW OF OPTIONS TIMELINE]      ║ [LIVE DOCUMENT FEED]                ║
║ ●────────●─────────────●────●     ║ New AI docs every 20-30s            ║
║ NOW    T+10m          T+25m FAIL  ║ ⚡ GDC AI — just now (badge)        ║
║ [$0 ✓][+$8k✓][$150k—]            ║ Includes neutral + counterarg docs  ║
║                                   ║                                     ║
║ [APPROVE BUTTON — active option]  ║                                     ║
╚══════════════════════════════════╩════════════════════════════════════╝
```

### H1 Evidence Wall — 5 Source Categories

Each category is a visual row. Dim/inactive before injection. Activates with a pulse glow in sequence as the RAG pipeline retrieves each type.

| Category | Icon | Example Content | Activation Order |
|----------|------|-----------------|-----------------|
| Sensor Telemetry | 📊 | PIP -14 PSI/min ↓, Amps -2.3A/min ↓ | 1st (immediate) |
| Operator Shift Notes | 📋 | "Higher than usual GVF this morning — possibly gas migration" | 2nd |
| Lab / Field Tests | 🧪 | Separator gas rate 142 Mscf/d ↑, GOR 1,310 scf/bbl ↑ | 3rd |
| VFD / Process Logs | ⚡ | Soft unload events × 3, Power factor 0.71 ↓ | 4th |
| Technical Standards | 📖 | API RP 11S §5.3: VFD speed-down as primary intervention | 5th |

Final line: **"🤖 GDC AI: 94% confidence — gas_lock · 5 independent sources — all convergent"**

SCADA access comparison (always visible, not animated):
- LEFT box: 4 sensors + hard thresholds → "✓ NORMAL, No alarm"
- RIGHT box: same 4 sensors + 4 document sources + AI synthesis → "⚠ GAS LOCK 94%"

### H1 Window of Options

Replace "RUL" entirely. Show three option cards with viability that changes in real-time:

| Option | Action | Cost | Viability State |
|--------|--------|------|-----------------|
| A | VFD 52→44 Hz via SCADA | $0 | VIABLE (T+0 to T+18m), then MARGINAL, then EXPIRED |
| B | Emergency shutdown + restart | ~$2,000 | VIABLE (T+0 to T+23m), then EXPIRED |
| C | Well pull + pump replacement | $150,000 | POST-PNR only |

**Financial case is stated by the LLM only, not a separate card.** The copilot says: *"Your $0 option is viable now. Waiting 10 minutes moves you to the $2,000 tier. Waiting 25 minutes leaves only $150,000."*

---

## 5. H2 SPECIFICATION — SLUG FLOW DISCRIMINATION

### The Core Story (Reframe from current implementation)

H1 asks: "What IS wrong and how do I fix it cheaply?"  
H2 asks: "What is NOT wrong — am I about to spend $150,000 on a false alarm?"

**The false positive problem:** Unnecessary pump pulls driven by SCADA vibration alarms (that cannot distinguish surface flowline slugging from downhole mechanical wear) are a known, expensive, and frustrating problem in production operations. Every production engineer has experienced it.

### The Physics

Flowline slug flow causes hydraulic impulses that transmit through the production tubing to the downhole vibration sensor. Vibration rises (alarming). BUT: surface slugging does NOT generate heat in the downhole motor. A genuine downhole bearing failure DOES generate heat (friction). Temperature is the discriminating signal.

**The diagnostic key:** SCADA sees vibration high (alarming) and temperature within normal range. SCADA cannot connect these two facts. An ML model trained on both signals simultaneously immediately classifies: "vibration without thermal elevation = surface flow regime, not mechanical wear."

### H2 Evidence Wall (different from H1)

| Category | Icon | Content | Story |
|----------|------|---------|-------|
| Sensor: Vibration | 📊 | 1.1 → 2.4 mm/s ↑ | Alarming |
| Sensor: Motor Temp | 📊 | 198°F → flat | EXONERATING |
| Operator Shift Note | 📋 | "Pumping rough but temp is normal" | Operator saw it, didn't know what it meant |
| Separator Test | 🧪 | 1.8 bbl slug volumes, 14-min periodicity | Confirms surface slug flow |
| Surface Choke Log | 📋 | 3 manual choke adjustments this tour | Operator was compensating |
| OEM Troubleshooting | 📖 | "Vibration without thermal elevation = surface flow regime" | The diagnostic rule |

**LLM says:** *"Vibration elevated. Motor temperature completely flat. This combination is the diagnostic signature of surface flowline slugging, not downhole mechanical wear. Six independent sources confirm: the pump is healthy. The SCADA vibration alarm would have triggered a $150,000 pull on a mechanically sound ESP. Correct response: $1,500 truck roll to adjust the surface choke valve."*

### H2 Key Visual

The primary visual is a two-line chart superimposed: Vibration (rising, orange) and Motor Temperature (flat, blue). One chart. Two lines. One line moves, one doesn't. The entire diagnostic insight is visible in 3 seconds.

Well schematic: the pump glows GREEN (healthy) while the surface flowline shows slug animation (orange slugs). The visual contrast — alarm at surface, healthy pump downhole — is immediately intuitive.

**$1,500 vs $150,000 decision outcome is stated by the LLM.** No separate financial card.

---

## 6. H3 SPECIFICATION — VFD BAYESIAN OPTIMIZATION

### The Core Story

H1 and H2 prove GDC protects your assets. H3 proves GDC doesn't just prevent loss — it actively creates value.

**The setup:** Oil price jumped 40%. ESPs are running at conservative 50 Hz setpoints. The question is not "is the pump OK?" — the pump is fine. The question is: "What is the maximum production rate that doesn't risk the pump?"

### Why This Requires Both Edge and Cloud

- **What Vertex AI Vizier does:** Gaussian Process Bandit optimization running in Google Cloud. Suggests the next frequency to test, updates its model based on results.
- **What GDC provides:** The local XGBoost RUL model evaluates whether a suggested frequency is thermally safe. Vizier can't make this evaluation — the physics model lives on the edge cluster.
- **The architectural story:** *"GDC doesn't replace cloud AI — it extends cloud intelligence to places where the relevant physics and data live. Vizier does the search; GDC enforces the constraints."*

### H3 Evidence Wall (Strategic character, different from H1/H2)

| Category | Icon | Content |
|----------|------|---------|
| Edge Model | 📊 | XGBoost RUL projections at 15 test frequencies (local, millisecond latency) |
| Technical Standard | 📖 | API RP 11S Class H limit = hard constraint (retrieved from AlloyDB RAG) |
| Motor Thermal State | 🌡 | Current operating temperature at 50 Hz (baseline) |
| Cloud Optimization | 🌐 | Vertex AI Vizier Gaussian Process posterior (cloud, queried by edge) |
| Market Context | 💰 | $112/bbl current oil price (optimization parameter) |

### H3 Financial Delta

At 50 Hz (conservative): baseline production rate  
At 57.5 Hz (Vizier optimal): +143 BBL/day × $112/bbl × 90 days = **$1.2M additional revenue**

The Pareto frontier chart shows: all 15 trial points, the thermal safety boundary (from local RUL model), the current conservative setpoint, and the optimal point. The financial delta bar is immediately visible.

**LLM says:** *"Bayesian optimization complete. Vertex AI Vizier evaluated 15 configurations. Optimal: 57.5 Hz. Projected additional revenue over 90 days: $1.2M. Motor thermal model confirms this remains within Class H insulation limits. Recommend deployment."*

---

## 7. SHARED UI DESIGN PATTERNS

These patterns are used identically across H1, H2, and H3. Build them once for H1, configure for H2 and H3.

### The Evidence Convergence Wall
- 5 category rows, each with icon, label, brief content summary, timestamp
- Inactive/dimmed before fault injection
- Activates in sequence with a glow animation as RAG pipeline retrieves each type
- Final synthesis line showing total sources and confidence
- SCADA access comparison (static — always visible)

### The Cited LLM Copilot
- Auto-starts streaming on fault injection (no "Consult Agent" button required)
- Narrative includes superscript citations: [¹] [²] [³] linking to specific source documents
- Clicking a citation opens the source document text in a modal
- Chat input accepts follow-up questions → streaming response from Gemma
- Financial case is stated here only — not in separate static cards

### The Animated Well Schematic (SVG, 2D)
- Pure SVG, dark-mode, 2D cross-section
- Animated particles: blue circles (liquid), yellow circles (gas)
- Motor housing with temperature color gradient: green (cool) → amber (warm) → red (critical)
- Pre-injection: mostly blue particles, green motor
- Post-injection (H1): increasing yellow particles, warming motor color
- H2: pump body glows green (healthy), surface flowline shows slug animation
- H3: pump body at optimal state with VFD frequency badge

### The Window of Options Timeline (H1 and H2 only, not H3)
- Horizontal timeline: NOW → options expiring → PNR → FAILURE
- Option cards with live viability badges: VIABLE (green) / MARGINAL (amber) / NOT VIABLE (gray)
- Viability updates every 5 seconds based on remaining window
- Financial cost shown on each card — the window-closing effect makes costs rise over time
- No separate "RUL" metric anywhere in the UI

### Live Document Generation (The Agentic Evidence Feed)
- Background thread (`_intel_generator`) runs every 20–30 seconds
- Generates AI documents using Gemma with live sensor context
- New documents appear in the feed with "⚡ GDC AI — just now" badge and glow animation
- Document type mix: ~55% supporting, ~30% neutral/routine, ~15% with competing hypothesis
- The 15% counterargument documents are explicitly addressed by the LLM copilot ("Alternative interpretation noted: [X]. However: [evidence refuting X]")
- This visible, continuous document generation is the most concrete demonstration of autonomous intelligence

---

## 8. AGENTIC ELEMENTS — WHAT QUALIFIES

### Genuine Agentic Components (feature these prominently)

**A. The `_intel_generator` Thread (Primary Agentic Component)**
- Runs continuously every 20–30 seconds without being triggered
- Goal: maintain a contextually accurate intelligence corpus for active faults
- Perceives: active fault state, current sensor readings, fault type
- Acts: prompts Gemma with live context, writes AI documents to AlloyDB
- Adapts: document content reflects current (not initial) sensor state
- **Make this visible:** Every new document with "⚡ GDC AI — just now" is this agent working

**B. Enterprise Context Queries (Tool Use)**
- When diagnosing a fault, the agent queries external systems (simulated SAP MM, Maximo, Pason EDR)
- Show this as a visible API call with response: "Querying SAP MM... Part MAT-4002-TC-100... 0 local stock, 12-day lead time"
- This is the "tool use" pattern that defines modern AI agents

**C. Vertex AI Vizier Optimization Loop (H3)**
- Vizier suggests frequency → local XGBoost evaluates → result returned to Vizier → Vizier updates posterior → next suggestion
- Autonomous multi-step optimization with tool use (local model as constraint evaluator)
- Label this explicitly as "agentic optimization" in the H3 UI

**D. Post-Approval Recovery Monitoring (To Implement)**
- After HITL approval in H1, agent continues monitoring recovery
- At T+2 min after VFD speed-down: "Recovery on track. PIP rising at expected rate."
- If recovery is slower than expected: "Recovery slower than projected. Consider step-down to 40 Hz."
- This "continuous assessment after action" loop is the defining agentic behavior

### The Honest Agentic Framing (for audiences who push back)

> *"We deliberately chose not to give the AI direct control of production equipment. In oil and gas, autonomous actuation of field equipment requires regulatory approval and carries significant liability. What we built is an autonomous intelligence layer — always running, always synthesizing, always building the evidence case and querying the relevant systems. The operator retains control of the physical world. The AI autonomously manages the information world. That architecture — autonomous intelligence, human control — is exactly right for safety-critical operations."*

---

## 9. CORPUS DEFENSIBILITY — CITATION REQUIREMENTS

Every factual claim in H1, H2, and H3 must trace to a real source. If it cannot be cited, reword or remove it.

### H1 Citations Required

| Claim | Required Source |
|-------|----------------|
| Gas lock PNR ~15–30 min | API RP 11S §5 (motor thermal protection), ESP manufacturer thermal bulletins |
| VFD speed-down = primary intervention | API RP 11S §5.3 |
| Class H insulation = 180°C continuous | API RP 11S, IEEE 117, NEMA MG-1 Part 3 |
| GVF handling threshold ~60–65% | API RP 11S, Baker Hughes Centrilift Gas Handling Design Guide |
| Motor cooled by fluid flow | API RP 11S §4.2 |
| VFD 52 Hz = 3,120 RPM / 44 Hz = 2,640 RPM | Physics: RPM = (Hz × 120) / poles (2-pole motor standard) |

### H2 Citations Required

| Claim | Required Source |
|-------|----------------|
| Vibration WITHOUT temperature rise = surface issue | ESP OEM troubleshooting guides, SPE-174536-MS |
| Temperature WITH vibration rise = downhole mechanical | ESP thermal model documentation |

### H3 Citations Required

| Claim | Required Source |
|-------|----------------|
| Class H limit = hard constraint | API RP 11S, same as H1 |
| Optimal Hz derivation | Computed from local XGBoost model (defensible as ML output) |

### The `ⓘ` Decoration Pattern

Every specific technical claim in the LLM output and in the UI is decorated with a small `ⓘ` icon that opens a concise panel showing:
- The source document name and section
- The exact text that supports the claim
- Why this source is authoritative

This is the "info decoration" layer — unobtrusive in the flow, available for deep dives.

---

## 10. DYNAMIC DOCUMENT REALISM REQUIREMENTS

The `_intel_generator` background thread must produce documents that pass an "operator authenticity test" — an experienced production engineer should read them and find them plausible.

### Document Type Weights

| Category | Target % | Purpose |
|----------|----------|---------|
| Supporting documents | ~55% | Corroborate the developing fault |
| Neutral / routine documents | ~30% | Normal operational records that precede the fault (shift logs that found nothing wrong, routine inspections) |
| Counterargument documents | ~15% | Competing hypotheses or observations that could argue against the GDC assessment |

### Counterargument Document Templates (H1 examples)

- *"PIP has been running 50–80 PSI below nominal for 3 weeks — suspected gradual reservoir drawdown. No corrective action recommended at this time."* (Alternative explanation for declining PIP)
- *"Motor current decline noted during afternoon tour. Attributed to VFD calibration drift — scheduled for verification next maintenance cycle."* (Alternative explanation for declining amps)
- *"Vibration reading at well A-1 within normal limits per last quarterly inspection (3 months ago)."* (Technically accurate but stale)

The LLM copilot must explicitly address counterargument documents when they appear in the retrieved corpus. This demonstrates genuine reasoning, not cherry-picking. Example:
> *"Shift record attributes declining PIP to reservoir drawdown [³]. However: reservoir drawdown produces proportional decline in motor amps correlated with production rate. The amps here are declining faster than production rate — inconsistent with drawdown. Pattern is consistent with pump unloading on gas void."*

---

## 11. WHAT HAS BEEN REMOVED AND WHY

| Removed | Why | Where the function moved |
|---------|-----|--------------------------|
| Fleet Operations tab | User explicitly requested removal. Navigation friction before the demo story. | Removed entirely. H1/H2/H3 are the primary experience. |
| Static financial cards (3-column grid) | Financial figures without context are just numbers. Financial case belongs in the LLM narrative. | LLM copilot states financial implications in context |
| Standalone "Financial Impact" card | Same as above | LLM states it |
| RUL (Remaining Useful Life) label | Engineering metric, not intuitively compelling to business audience | Replaced by Window of Options (showing which actions are still viable) |
| "Consult Agent" button requirement | Demo narrative is disrupted by requiring a button click to see the intelligence | LLM auto-starts streaming on fault injection |
| Fleet Financials tab | Financial outcomes recorded but the demo story doesn't require a ledger tab | Can remain as a secondary reference tab but not in the primary demo flow |

---

## 12. IMPLEMENTATION ORDER

### Phase 1: H1 (Complete Before Starting H2)

1. **Write updated RAG corpus** (citations added to existing manuals, counterargument seeds added to `INTELLIGENCE_FEED`)
2. **app.py changes (single `replace_in_file` call):**
   - Add `slopes` dict to `/api/plot/forecast-data/{asset_id}` response
   - Update `_intel_generator` for 55/30/15 document mix with counterargument templates
   - Add `post_approval_monitor()` function for recovery monitoring after HITL
   - Wire `hitl_approve()` to launch recovery monitor for gas_lock
3. **index.html changes (single `replace_in_file` call):**
   - Build H1 layout (2D well SVG, evidence wall, cited LLM copilot, window-of-options, live document feed)
   - Wire `setMainTab('horizon1')` to start live telemetry poll and load baseline intel
   - LLM copilot auto-starts on injection (no button needed)
   - Window of Options with live viability tickers
   - Remove static financial cards; remove Fleet Operations tab link

### Phase 2: H2 (After H1 is verified)

- Reuse evidence wall pattern with H2 evidence configuration
- Reuse cited LLM copilot with H2 prompting
- Add two-line Vibration+Temperature chart as primary visual
- Update well SVG for surface vs downhole contrast
- Configure window-of-options for slug flow time horizon

### Phase 3: H3 (After H2 is verified)

- Reuse evidence wall with H3 strategic evidence configuration  
- Add financial delta bar to existing Pareto frontier chart
- Add "Edge + Cloud" architecture badge on Vertex AI Vizier element
- Update LLM prompt for optimization context

---

## 13. FIVE-MINUTE DEMO SCRIPT

```
:00  Tab opens. Charts are live and ticking.
     "This is a real monitoring system watching a Pad Alpha ESP.
      All sensors nominal. SCADA: all green. No alarms."

:30  Inject gas lock fault.
     "Watch what GDC sees — that SCADA cannot."
     [Evidence wall activates in sequence. LLM begins streaming.
      Well animation: gas bubbles increase, motor warms amber]

:60  LLM copilot streaming:
     "Gas lock confirmed at 94% confidence. PIP declining.
      Five independent sources — sensors, shift note, separator test,
      VFD log, API RP 11S — all pointing the same direction.
      Your $0 option expires in about 10 minutes."

:90  Click "Approve VFD Speed-Down"
     [Charts animate recovery. LLM: "Recovery on track."]
     "Twenty-five minutes of warning. Zero dollars. Pump preserved."

:2:00 Switch to H2.
     "Same platform. Vibration alarm just fired on A-3."
     [Show two-line chart: vibration up, temperature flat]
     "Temperature didn't move. GDC: this is surface slugging.
      Pump is healthy. $1,500 truck roll, not $150,000 pump pull."

:3:00 Switch to H3.
     "Oil price up 40%. These pumps are running conservative setpoints."
     [Run Vizier — 15 trials plot in real-time on Pareto frontier]
     "Bayesian optimization: 57.5 Hz is optimal. Thermal limit held."
     [Click Deploy]
     "$1.2 million of additional production over 90 days.
      That's the proactive case."

:5:00 "Three scenarios. Three different ways the same platform
       pays for itself before lunch."
```

---

## 14. SESSION HANDOFF RULES (Meta)

**`docs/DEMO_MASTER.md` (this file):** The permanent spec. Updated only when design decisions change. Every session reads this first. Takes precedence over all other documentation.

**`docs/NEXT_SESSION_PROMPT.md`:** Operational state only (~40 lines max). Contains: cluster pod status, mandatory startup commands, current git head and image digest, next 2–3 specific implementation tasks with verification steps. Changes every session.

**`docs/SESSION_LOG.md`:** Append-only history. One paragraph per session. Never overwritten. New sessions read only the last 3–5 entries for context on what was tried and rejected.

**The `.clinerules` startup rule:** Every session runs the 4 mandatory commands AND reads `DEMO_MASTER.md` before writing any code. The NEXT_SESSION_PROMPT.md describes WHERE WE ARE. DEMO_MASTER.md describes WHAT WE'RE BUILDING.
