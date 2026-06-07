# GDC Predictive Maintenance — Demo Narrative Guide

**Version:** Session 7  
**Live demo URL:** http://35.188.3.97  
**Grafana URL:** http://136.115.220.48  

---

## The One-Sentence Pitch

> "GDC Edge AI gives operators more time, more flexibility, and a higher probability of success — because it sees multi-variant failure signatures and AI-corroborated evidence that SCADA fundamentally cannot, and it delivers that intelligence at the source without depending on a network connection."

---

## The Core Narrative Structure

Every element of this demo is built to prove a single contrast:

| Traditional SCADA | GDC Edge AI |
|---|---|
| Single-sensor, threshold-based alarms | Multi-variate pattern recognition (6–8 sensors simultaneously) |
| Reactive — alarms when failure is already happening | Predictive — detects precursors days or weeks before failure |
| No knowledge of documents, logs, or schedules | Fuses sensor telemetry with shift logs, lab reports, and PM records |
| Binary state: NORMAL / ALARM | Continuous health score + specific time-to-failure projection |
| "The pump is failing" | "The pump will fail in 14 days, the part takes 12 days to arrive, order today" |

The demo walks the audience through three phases that prove this contrast with live, running code.

---

## Phase 1 — Establish the Baseline: "SCADA Sees Nothing Wrong"

**Application panel:** Grafana dashboard (Fleet Telemetry tab)  
**Purpose:** Establish what best-in-class, well-configured SCADA monitoring looks like — and demonstrate that it is blind to the early-stage fault you are about to inject.

### What to Show

Navigate to the **Fleet Telemetry** tab. The Grafana dashboard loads in `?kiosk=tv` mode with the following narrative panels:

1. **Fleet Status KPIs (top row):** "Active Assets (10m) = 14/14. SCADA Hard-Limit Alarms = 0. Time Since Last Hard Alarm = N/A." Emphasize: **all green, all normal, SCADA is happy.**

2. **ESP Intake Pressure chart:** Show that the pressure lines are stable, well within the 800–1,850 PSI green zone. Narrate: *"This is what a best-practice SCADA dashboard looks like. All 6 wells are in range. No alarms."*

3. **Vibration charts (now split by asset class):** Point to the ESP, Gas Lift, and Rig 42 sub-panels. Narrate: *"Vibration is nominal on every asset. The SCADA threshold is 10 mm/s. Nothing is close."*

4. **⚡ Edge AI Detection Timeline (bottom of Grafana):** Currently empty. Narrate: *"And the AI timeline is empty too — because we haven't injected a fault yet. Watch what happens."*

5. **🔴 SCADA Hard-Threshold Breach Log:** Empty. Emphasize: *"This table is the key. In a traditional monitoring center, if this table is empty, the operator goes home. By the time it fills up, it's too late."*

### Why This Matters

SCADA is reactive. The Grafana dashboard in this demo is not a straw man — it is a well-designed, real-time monitoring view with proper thresholds, proper KPIs, and asset-specific alarm limits. The power of the demo comes from showing that even this good SCADA system will remain silent while a multi-million dollar failure develops.

---

## Phase 2 — Inject the Fault: "GDC Sees It First"

**Application panel:** Fleet Operations tab → Fleet Map → context menu  
**Purpose:** Show GDC detecting a fault pattern in real-time while SCADA remains silent.

### What to Show

1. **Switch to the Fleet Operations tab.** The 2D spatial fleet map appears with three site zones (Pad Alpha, Pad Bravo, Rig 42) and 14 interactive asset nodes.

2. **Right-click (or click) `ESP-ALPHA-2`** — the most capable demo asset. The context menu opens with a mini sensor grid showing live PSI / Temp / Vib readings.

3. **Select "Sand Ingress"** from the context menu and choose a gradual ramp duration (e.g., 30 minutes). Click "Start Degradation."

4. **Watch the fleet map:** Within seconds, `ESP-ALPHA-2` begins pulsing orange. The KPI banner updates: "AI Detections: 1."

5. **Return to Grafana (Fleet Telemetry tab)** and show simultaneously:
   - **SCADA Breach Log:** Still empty. Intake pressure is declining slowly but hasn't crossed 800 PSI.
   - **Vibration panels:** Vibration on the ESP sub-panel is slowly rising — but it is at ~3.5 mm/s, nowhere near the SCADA HIGH at 10 mm/s.
   - **⚡ Edge AI Detection Timeline:** An orange "AI Warning" bar now appears on ESP-ALPHA-2.

**Narrate:** *"That's the contrast. SCADA has no alarms. The breach log is empty. But our Edge AI — running XGBoost models on the GDC cluster right here — has already scored this sensor combination and detected the early signature of sand impeller erosion. We have days. SCADA would have hours."*

### What the AI Is Actually Detecting

The XGBoost health model scores 6–8 features simultaneously:
- **PSI** — intake pressure (declining slowly)
- **Temp** — motor winding temperature (slightly elevated)
- **Vibration** — rising at a specific sub-harmonic rate correlated with impeller erosion
- **Motor Amps** — declining (pump doing less hydraulic work as stages erode)
- **dpsi/dt, dvib/dt, damps/dt** — rate-of-change slopes that project the trajectory

No single sensor is alarming. It is the *correlation* between sensors — declining current + rising vibration — that constitutes the diagnostic signature. SCADA cannot see multivariate correlations. GDC can.

---

## Phase 3 — Deep Dive: "What the AI Knows (and SCADA Doesn't)"

**Application panel:** Fleet Operations tab → click `ESP-ALPHA-2` → Open Deep Dive  
**Purpose:** Show the full depth of evidence and the actionable output.

### The Deep Dive Panel

Open the deep dive for `ESP-ALPHA-2`. This panel presents five interlocking elements that together prove the full value proposition:

#### 1. SCADA vs AI Contrast Banner (top of panel)
Two side-by-side status cards:
- **Left (green):** `SCADA: ✓ NORMAL` — no threshold breach, SCADA is content
- **Right (orange, pulsing):** `⚡ GDC Edge AI: Fault Detected`

Below them, a blue **AI Lead Time banner** quantifies the advantage:
> "⏱ 19 min — GDC AI leads SCADA by this margin · SCADA: ✓ NORMAL · AI: ⚡ Fault detected"

Narrate: *"This is the headline. GDC detected this fault 19 minutes — or in the sand ingress case, 14 days — before SCADA would have generated a single alarm."*

#### 2. Sensor Forecast Charts (center)
Four tabs: PSI / Temp / Vib / Motor Amps. Each shows:
- **Blue solid line:** Live historical telemetry from AlloyDB Omni (the last 10 minutes of real data)
- **Orange dotted line + confidence cone:** ML RUL projection — where the sensor is heading
- **Red dashed horizontal line:** SCADA alarm threshold (where SCADA would finally react)
- **Red vertical marker:** `⚡ SCADA Alarm in [X]m` — when the trajectory crosses the threshold
- **Orange vertical marker:** `⛔ PNR [T+Xm]` — Point of No Return, after which damage is irreversible

Narrate: *"The blue line is now. The orange projection is where physics says this asset is going. The red line is SCADA's threshold — and the vertical marker shows exactly when we'll cross it. The orange PNR marker is when it's too late to prevent damage."*

**Key teaching point:** The chart uses a single continuous exponential (k=3.5 for hours-scale faults, k=1.8 for days-scale faults). There is no artificial "kink" — the physics of degradation are continuous. The SCADA marker is an ML-predicted time, independent of the curve shape. Both are shown simultaneously; neither invalidates the other.

#### 3. Live Intelligence Feed (right column)
A scrollable list of evidence documents. After Phase 16 (the current build), this feed contains **two layers**:

**Layer 1 — Live AI-Generated Documents (orange `AI` badge, `gi_*` prefixed):**
Generated by the `_intel_generator` background thread every 2–5 minutes. Gemma (running on the GDC cluster) is prompted with live sensor context: current PSI, temperature, and vibration readings from the active fault. It generates realistic O&G field documents — shift notes, well test reports, VFD logs — that are contextually accurate for the fault type and current sensor state. These are stored in AlloyDB `field_intel` table and retrieved in real-time.

**Layer 2 — Pre-Vetted Reference Documents (domain-specific badges):**
Curated unstructured documents for each fault type:
- 🧪 Lab reports (BS&W water cut, sand concentration, oil analysis)
- 📋 Shift handover notes ("minor vibration noted on A-2 during last connection")
- 📦 ERP inventory queries (SAP MM — 12-day lead time, 0 local stock)
- 🔧 Maximo PM records (overdue by 460 ft, last inspection at 14,200 ft)

Narrate: *"This is multi-modal fusion. The AI isn't just looking at sensors — it is reading the shift notes, the lab reports, the ERP inventory query, and generating its own contextual documents. Every one of these documents corroborates the sensor signal from a different angle."*

Clicking any document opens the full text with an AI relevance annotation that explains specifically why this document matters for this fault at this moment.

#### 4. Gemma Finding (bottom of feed)
> "🤖 Gemma: Correlating 3-day BS&W trend (+0.41%), salinity increase (+17%), and shift handover note with 1.2 mm/s vibration slope — high confidence (94%) sand ingress is underway. SCADA will not alarm for ~14 days."

This is the capstone of the evidence case — the LLM synthesizing the document corpus and the sensor telemetry into a single, natural-language conclusion with a confidence percentage.

#### 5. AI Lead Time Calculation
The Deep Dive computes and displays the exact lead time advantage. For sand ingress:
- **GDC detects:** Now (with 14-day RUL projection)
- **SCADA detects:** When vibration crosses 10 mm/s, approximately 13.5 days from now
- **Lead time advantage:** ~13.5 days

---

## Phase 4 — Agentic Resolution: "The AI Knows What to Do"

**Application panel:** Deep Dive → Consult Agent button  
**Purpose:** Show that GDC doesn't just detect — it recommends a specific, enterprise-grounded response.

### The GDC Ops Agent

Click "⚡ Consult Agent." The Copilot panel opens (or expands from the bottom) with:

1. **Enterprise Context Query:** The agent immediately queries the relevant enterprise system for this fault type:
   - Sand Ingress → SAP Materials Management (part inventory, lead time)
   - Thermal Runaway → IBM Maximo (field crew schedules, work order append)
   - Valve Washout → Pason EDR (rig pump status, ECD window, next connection)

2. **Rule-Based Recommendation (instant):** Delivered in milliseconds without waiting for the LLM:
   > "📦 Order ESP Sand-Handler Assembly now — standard freight 12d arrives before failure (14d). Unit cost $145,000. Failure without order = $8,500/day deferred production."

3. **Gemma-Enhanced Narrative (streaming):** Tokens stream in from the local Gemma model, providing a conversational elaboration of the recommendation, citing specific sensor values and the enterprise context.

4. **4-Tier Remediation Panel (right side of Copilot):**
   Tiered by urgency against the PNR:
   - **Early** (≥ PNR × 1.5): Software-only, zero-cost SCADA adjustment
   - **Urgent** (between thresholds): Crew dispatch, part ordering
   - **Critical** (< PNR × 0.5): Emergency procedure
   - **Post-PNR**: Recovery/damage assessment only

   Each tier is viability-scored: `VIABLE` / `MARGINAL` / `NOT VIABLE` based on time-to-execute vs. remaining window.

Narrate: *"The AI hasn't just detected the problem — it's consulted the supply chain, found the right part, checked the lead time, and told the operator exactly what to do. At the Early tier, we still have 9 days of buffer and the recommendation is just a standard purchase order. By the time SCADA alarms, we'd be in the Critical tier — with an emergency workover already booked."*

### Multi-Turn Conversation
The agent supports follow-up questions. Ask: *"Why would the driller miss this?"* or *"What happens if we don't order the part today?"* — the agent uses the fault physics, sensor context, and enterprise data to respond in natural language.

---

## Phase 5 — The Financial Case: "GDC Pays for Itself"

**Application panel:** Fleet Financials tab / ⓘ Justify button in Copilot  
**Purpose:** Quantify the ROI for a skeptical audience.

### Intervention Cost vs. Damage Cost

The Financial Justification Modal provides OEM-sourced, itemized cost breakdowns for every fault type:

| Intervention Stage | Scenario | Cost |
|---|---|---|
| Early (GDC-detected, software-only) | Gas Lock VFD adjustment | $2,500 |
| Early (GDC-detected, scheduled part order) | Sand Ingress — pump kit on standard freight | $5,000 |
| Urgent (GDC-detected, crew dispatch) | Bearing Wear — bearing replacement during planned trip | $8,200 |
| Post-SCADA (alarm fire, emergency response) | Sand Ingress — workover required | $85,000–$120,000 |
| Post-PNR (failure materialized) | Motor Overheat — full winding replacement + workover | $200,000 |

The Fleet Financials ledger tracks every acknowledged work order: cost avoided, cost incurred, and net savings. The **Fleet Savings Ticker** in the top banner updates in real time.

Narrate: *"This isn't a conceptual ROI model. Every number has an OEM source citation. Click the Justify button and you'll see the Baker Hughes Centrilift price list, the Ariel service manual, the IADC rig rate survey — everything an operator or procurement manager would need to validate the number."*

---

## The Three-Scenario Proof (Summary)

Each of the three primary demo scenarios demonstrates a distinct dimension of the value proposition:

| Scenario | Site | Fault | Primary Value | SCADA Would Have... |
|---|---|---|---|---|
| ESP Sand Ingress | Pad Alpha | Impeller erosion | **Supply chain lead time** (14-day window vs 12-day lead time) | Alarmed 24h before catastrophic failure — too late to avoid the wait |
| Gas Lift Thermal Runaway | Pad Bravo | Fin-fan cooling degradation | **Route optimization** (crew already scheduled on-site tomorrow) | Alarmed when temp crossed 230°F — $1,800 emergency dispatch required |
| Mud Pump Valve Washout | Rig 42 | Valve seat erosion (masked by driller) | **Undetectable pattern** (driller compensation hides it from SCADA entirely) | **Never alarmed** — standpipe pressure looked normal throughout |

---

## Key Talking Points for Objections

### "Our SCADA already has rate-of-change alarms"
Rate-of-change alarms still look at single sensors. They cannot detect the *correlation* between declining motor current and rising vibration that constitutes the impeller erosion signature. A rate-of-change alarm would either fire too early (false positives every time there's normal variation) or too late (set loose enough to avoid false positives). The model was trained on the specific sensor correlation pattern — it distinguishes sand ingress from gas lock from motor overheat with 94% confidence.

### "We could do this in the cloud"
For gradual faults (majority): Cloud latency doesn't affect detection — both GDC and cloud would detect them at similar times. The real arguments for edge are: (1) security — production data never crosses the internet, (2) data gravity — streaming 200GB/day of 50Hz vibration data over VSAT is uneconomical, (3) survivability — the rig keeps detecting during outages. See `WHY_GDC.md` for the full case.

### "How accurate is the model?"
The XGBoost health models are validated on synthetic data generated by the same fault-physics parameters that govern the simulator. Fault-type discrimination accuracy in demo conditions is ~94%. In production, models would be retrained on historical failure events from the customer's own fleet — which is the MLOps pipeline also demonstrated in the app.

### "Is the LLM reliable?"
The LLM (Gemma 2B running on-prem) enhances — it doesn't replace — the rule-based system. The agent recommendation is deterministic and enterprise-grounded regardless of whether Gemma is available. Gemma adds the narrative synthesis and the multi-turn conversation. If Gemma is unavailable, the agent falls back gracefully to the rule-based recommendation with zero user-visible degradation.

---

## Demo Flow — Quick Reference

```
1. Fleet Telemetry tab → Grafana (SCADA: all green, SCADA Breach Log empty)
2. Fleet Operations tab → Fleet Map → Right-click ESP-ALPHA-2 → Sand Ingress
3. Fleet Telemetry tab → Show: Vib rising on ESP panel, AI Timeline populated, SCADA log still empty
4. Fleet Operations tab → Click ESP-ALPHA-2 → Open Deep Dive
5. Deep Dive → SCADA vs AI banner (normal vs detected)
6. Deep Dive → Sensor charts (trajectory, PNR marker, SCADA alarm marker)
7. Deep Dive → Live Intelligence Feed (AI-generated + lab report + shift note + ERP query)
8. Deep Dive → Gemma Finding (synthesis statement)
9. Copilot → Consult Agent → supply chain recommendation
10. Copilot → HITL Panel → show tiered actions, viability scores
11. Fleet Financials → show avoided-cost ledger
12. ⓘ Justify button → itemized cost breakdown with OEM citations
```

---

## Related Documentation

- `VALUE_PROPOSITION.md` — Concise statement of the four SCADA/ML gaps
- `WHY_GDC.md` — The four-pillar case for edge inference (security, data gravity, latency, survivability)
- `WHY_THESE_SCENARIOS.md` — Detailed failure physics for each scenario (the "why" behind the sensor signatures)
- `ARCHITECTURE.md` — Technical stack and component diagram
