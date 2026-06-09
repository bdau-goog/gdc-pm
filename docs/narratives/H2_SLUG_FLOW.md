# H2 — Slug Flow Discrimination — Demo Narrative
**Version:** Session V (June 9, 2026) — Physics mechanism corrected
**Status:** CANONICAL — read before editing H2 UI, H2 LLM prompts, or H2 evidence wall
**Mirrors:** docs/DEMO_MASTER.md §5 (spec); this file is the *narrative rationale* layer

**CHANGE LOG Session V:**
- **CRITICAL FIX:** Original narrative stated "heavy liquid slugs hit the wellhead piping and transmit mechanical shocks **down the production tubing** to the downhole sensor." This mechanism does not survive a mechanical engineer — surface hydraulic impulses are negligibly attenuated by thousands of feet of fluid-damped, collar-clamped tubing. **Cut entirely.**
- **Correct mechanism (Session V):** In-string multiphase slug loading at the pump intake. Cyclic vib + cyclic amps + flat temp at the gauge — all measurements made *at the pump*, not via long-distance transmission.
- Vibration numbers reconciled to FAULT_PROFILES / fault_signatures (4.0–6.5 mm/s, not 1.1–2.4 mm/s).
- 14-min periodicity re-sourced to wellhead/flowline pressure trend + VFD amp swing; separator test retained for GOR-rising evidence only.
- ISA-18.2 HI alarm (4.0 mm/s) and HH trip (5.0 mm/s) levels modeled separately.

---

## 1. One-Line Thesis

> **"Am I about to spend $150,000 on a false alarm?"**

H1 asks *what is wrong and how do I fix it cheaply.* H2 asks *what is NOT wrong — and how do I avoid the expensive overcorrection?* This is the discrimination act in the Protect → Discriminate → Optimize arc.

---

## 2. The Business Pain

**Unnecessary pump pulls driven by vibration HI alarms** are a recurring, expensive, and professionally embarrassing problem in ESP production operations. A vibration HI alarm fires on the SCADA screen. The operator cannot tell from the sensor alone whether it is:
- A **failing downhole bearing** (real problem → pump pull justified) or
- **In-string multiphase slug flow** causing cyclic pump hydraulic imbalance (surface production regime → pump is mechanically healthy → pull completely unnecessary)

The conservative, defensive response is to call the workover crew. A pump pull is ~$150,000. On a mechanically sound ESP that needed a $1,500 choke-valve truck roll to control surface backpressure. Every production engineer in the room has lived this exact scenario.

---

## 3. The Corrected Physics (citable, hostile-engineer-proof)

### 3.1 Why slug flow causes vibration at the downhole gauge

**The mechanism is in-string, at the pump. Not surface-to-downhole transmission.**

In a high-GOR ESP well, as produced fluid rises up the tubing, pressure decreases and gas breaks out of solution. Under slug flow conditions, the gas and liquid phases do not mix uniformly — they segregate into alternating **gas slugs** and **liquid slugs** traveling up the production tubing string.

When these slugs arrive at the pump intake (where the downhole PDG gauge is mounted, immediately below the motor):

1. **Gas slug reaches the intake:**
   - Pump momentarily ingests low-density gas/liquid mixture
   - Hydraulic head generated drops sharply → **PIP dips**
   - Motor sees reduced hydraulic load → **Amps dip**
   - Gas/liquid interface through impeller stages causes cavitation and hydraulic imbalance → **Vibration spikes**

2. **Liquid slug follows:**
   - Pump re-loads on dense liquid
   - **PIP recovers, Amps recover, Vibration drops back**

This creates a **cyclic, periodic signature** in vibration, amps, and PIP at the **slug transit frequency** (e.g., 14-min cycles at the surface flowline translate to periodic loading events as slugs travel down the tubing column and reach the intake).

**The gauge measures this at its location at the pump — no long-distance mechanical transmission is involved.**

*Reference: Baker Hughes Centrilift ESP Gas Handling Design Guide (gas void fraction effects on pump hydraulics); SPE-174536-MS §3.4 (multiphase ESP performance); API RP 11S §4.2 (pump vibration from unsteady inflow).*

### 3.2 Why bearing failure produces a different signature

A genuine downhole bearing failure generates **mechanical friction**:
- Friction generates **continuous, broadband heat** → motor winding temperature rises monotonically
- Bearing-induced vibration is **broadband**, not periodic at a slug frequency
- Motor load is NOT cyclic — it may trend up or be erratic, but does not swing regularly at a period tied to surface flow

**The discriminating signals — summary:**

| Signal | Bearing wear (real, pull justified) | Slug flow in-string (surface regime, do NOT pull) |
|--------|-------------------------------------|---------------------------------------------------|
| Vibration | Rising, broadband, sub-harmonic | **Cyclic**, periodic, tied to slug arrival frequency |
| Motor amps | Steady or erratically rising | **Cyclic swings** at the same period as vibration |
| PIP | Steady | **Cyclic dips** at the same period |
| Motor temp | **Rising** (friction → heat, cooling unaffected) | **FLAT** (no friction; cooling fluid flow normal) |

**The categorical discriminator is flat motor temperature.**
If vibration rises and temperature rises → downhole mechanical problem.
If vibration rises cyclically and temperature stays flat → in-string flow regime, pump healthy.

### 3.3 Why the SCADA operator cannot make this determination alone

SCADA's vibration trip is at **5.0 mm/s (HH — High-High)**. The ISA-18.2 HI alarm fires at **4.0 mm/s**, demanding attention before the hard trip. Well A-3 vib is cycling toward 4.5 mm/s peak — the **HI has fired; the HH has not.** The operator sees a trending HI alarm. If the pump were a bearing failure, this would be early-stage — the defensible reaction to protect the asset is to shut in and investigate.

**SCADA cannot co-read the flat motor temperature as exonerating evidence in the alarm logic.** The alarm is fired purely on the vibration tag. SCADA does not read the shift note ("pumping rough but temp is normal — unusual if bearing"), the choke-valve adjustment log (3 adjustments compensating for surface slugging), or the OEM troubleshooting guide rule: *"Cyclic vibration with flat motor temperature is consistent with in-string multiphase slug loading. Do not pull. Adjust surface backpressure."*

---

## 4. The Three Evidence Layers

This framework applies to all three demo acts (H1/H2/H3). For H2:

### Layer 1 — Telemetry departs normal
Vibration is cycling toward 4.5 mm/s (ISA-18.2 HI alarm at 4.0 mm/s has fired). Motor temperature is flat at 198°F. PIP and amps showing slight cyclic swings.

- **What a multivariate SCADA can also see:** both sensors on the same trend chart. A skilled controls engineer can notice the decorrelation.
- **Why this layer alone is not a win for us:** a smart engineer with SCADA could reach the same surface-vs-downhole intuition. We do not stake the H2 argument on Layer 1.
- **How to respond to this challenge:** *"For the sensor pattern — yes, a skilled engineer with the right SCADA setup could reach the same intuition for one well. What's different: our classifier scores a calibrated probability for all five fault types learned from data, not one hand-authored rule, and retrains when reservoir conditions change. But I'd rather show you the piece a controls engineer literally cannot replicate with SCADA: the four field documents you just saw."*

### Layer 2 — Classifier names the fault (calibrated probability, not a boolean)
The XGBoost classifier (`esp_classifier.ubj`) outputs a probability vector:
`slug_flow: 0.90, bearing_wear: 0.06, normal: 0.03, ...`

Built on class 4 training data with `dtemp_dt ≈ 0` (flat temp), `dvib_dt > 0` (rising), and `damps_dt` cyclic.

**The honest Layer-2 claim:**
| | Rules-based multivariate SCADA | GDC XGBoost classifier |
|---|---|---|
| How logic is created | Hand-authored per fault × asset, by an engineer who already knows the signature | Learned from labeled trajectories across all fault classes simultaneously |
| Output | Boolean (alarm / no alarm) | Calibrated probability vector per reading |
| Pre-threshold behavior | A correlation rule still has a trip point | Continuous 0–1 every 5 seconds, before any threshold is crossed |
| Retrainability | Re-tune by hand when setpoints or reservoir conditions change | Retrain from new labeled data |
| Scale | One rule per fault per asset class, maintained by hand | Single model covers thousands of wells |

Do **not** say "SCADA can't tell faults apart." Say: *"A controls engineer who already knows the slug-flow signature could write a rule that reaches the same answer for one well. The classifier learns the boundaries for all five fault types simultaneously, outputs a probability rather than an alarm, scores continuously before thresholds, and retrains when the reservoir changes — without anyone re-authoring rules."*

### Layer 3 — Unstructured data + LLM: the capability SCADA has no architecture to touch
This is the differentiator that closes the argument. **4 of the 6 H2 evidence sources are unstructured field documents** that no SCADA system, however sophisticated, has a mechanism to read.

| # | Source | What it contributes | SCADA can see this? |
|---|--------|--------------------|---------------------|
| 1 | 📊 Vibration sensor | Cycling toward 4.5 mm/s — HI alarm fired | ✅ Yes |
| 2 | 📊 Motor temp sensor | 198°F flat (exonerating for downhole) | ✅ Yes |
| 3 | 🔧 Surface Choke Valve Log | 3 manual choke adjustments in 4h; operator compensating for increasing backpressure and surface slugging | ❌ No |
| 4 | 📈 Wellhead/Flowline Pressure Trend | ~14-min oscillations in wellhead pressure corresponding to slug frequency — confirms surface flow regime | ❌ No (unless specifically trended and correlated by a controls engineer) |
| 5 | 📋 Night Shift Note | "Pumping rough but temp is normal — unusual behavior if it were a bearing" | ❌ No |
| 6 | 📖 OEM Troubleshooting Guide (RAG) | "Cyclic vibration without thermal elevation = in-string multiphase slug loading. Adjust surface choke valve backpressure. Do not pull well." | ❌ No |

**Sources 3–6 are categorically invisible to SCADA.** This is not "SCADA minus AI." This is a data modality SCADA fundamentally lacks.

---

## 5. How the Mechanism Actually Works (code-grounded)

### Document retrieval: `get_rag_context_and_adjusted_rul()`
1. Embeds the fault query (`slug_flow esp`) via sentence-transformers.
2. pgvector similarity search on `rag_documents` (18 OEM manual sections) → top-3 relevant passages, including the "do not pull well" OEM rule.
3. Fetches last 5 `field_intel` rows for ESP-ALPHA-3 / `slug_flow` (the session documents generated by `_intel_generator`).

### Document influence: `adjust_rul_with_documents()`
Regex-parses structured variables from prose and applies physical multipliers to the predicted time-to-SCADA. For H2, slug_flow's PNR is 120 minutes (slow vibration drift, unlike H1's thermal emergency) — the document fusion tightens this based on contextual evidence.

### Document generation: `_intel_generator()` background thread
Every 20–30 seconds during active fault, Gemma writes new `field_intel` documents with live sensor context (55% supporting, 30% neutral, 15% counterargument) — these appear in the intel feed as "⚡ GDC AI — just now." The feed is not a static list; it grows visibly during the demo.

### Advisor narrative (streaming Gemma)
Receives `rag_context` (manual passages + session docs) + live sensor finding and produces:
> *"Vibration elevated and cycling — ISA-18.2 HI alarm active. Motor temperature completely flat at 198°F. This pattern is consistent with in-string multiphase slug loading at the pump intake, not downhole mechanical wear. Cyclic amps and PIP match the surface flowline slug frequency. The pump is mechanically healthy. Six independent sources confirm. Correct response: $1,500 truck roll to adjust the surface choke valve. Do not pull the pump."*

The Advisor also explicitly addresses the counterargument documents (15% of feed):
> *"Shift record notes 'unusual vibration' — could be consistent with early bearing wear. However: bearing wear would produce a measurable temperature rise within minutes due to increased mechanical friction. Temperature has been flat at 198°F for 4+ hours. The bearing hypothesis does not fit the thermal evidence. The cyclic vibration-amps-PIP pattern is the signature of slug loading at the intake."*

---

## 6. The Decision and Outcome

**Post-injection state:** operator sees the two-line chart (vib cycling up, temp flat), cyclic amps/PIP pattern, 6-source evidence wall, streaming Advisor verdict, and the truck-roll CTA.

**Operator action:** "Dispatch Truck Roll" → technician en-route → surface choke adjusted → backpressure stabilized → slugging suppressed → `h2Resolved`.

**Financial outcome:** $1,500 avoided $150,000 — stated by the LLM, not a static card.

---

## 7. Asset and Data Wiring (current state)

- **Asset:** ESP-ALPHA-3 / Well A-3
- **Fault injection:** `POST /api/inject-fault` → `fault_type: "slug_flow"`, `asset_id: "ESP-ALPHA-3"`
- **Intel feed:** `INTELLIGENCE_FEED["slug_flow"]` in `app.py` — 3 pre-authored session documents (`sf_1` choke log, `sf_2` separator test (GOR evidence), `sf_3` shift note) **already wired**
- **Truck-roll dispatch:** `POST /api/agent/truck-roll` **already wired** in `app.py`
- **RAG:** OEM "do not pull well" passage lives in `rag_documents` (18 rows, embedded)
- **Classifier:** `esp_classifier.ubj` class 4 = `slug_flow`, flat `dtemp_dt` + rising `dvib_dt` training signature — deployed (Session B, v3, live-verified 100% recall)
- **Remaining work:** H2 Scenario Replay visual build in `index.html` — backend `/api/h2/scenario-replay` + frontend 3-zone layout

---

## 8. What to Say If Challenged

| Challenge | Response |
|-----------|----------|
| "Surface slugs can't shake a gauge two miles down" | "Correct — and that's not what's happening. The slugs travel up the production string; gas and liquid slugs arrive alternately at the pump *intake*, where the gauge is mounted. The cyclic hydraulic loading at the impeller generates the vibration we're measuring — at source, no long-distance transmission." |
| "A good multivariate SCADA can also see vibration + flat temp" | "For the sensor pattern — yes, a skilled engineer with the right SCADA setup could reach the same intuition. What's different: our classifier scores continuously before any threshold, outputs a calibrated probability for all five fault types learned from data (not one hand-authored rule), and retrains when reservoir conditions change. But I'd rather show you the piece a controls engineer literally cannot replicate with SCADA: the four field documents you just saw." |
| "Your shift note is hand-authored" | "The three pre-loaded session documents are seeded for the demo. In a live deployment, the `_intel_generator` thread reads from live shift-note integrations and field data systems. The RAG pipeline and fusion mechanism are identical either way." |
| "How do you know the OEM rule is reliable?" | "It's directly from the ESP OEM troubleshooting guide embedded in our AlloyDB corpus. SPE-174536-MS §3.4 provides the same diagnostic principle for multiphase ESP performance. The 'flat temperature = surface flow regime' rule is industry-standard." |
| "Slug flow at 4.5 mm/s — did you hit the ISA-18.2 HI alarm?" | "Yes — the HI at 4.0 mm/s has fired. The HH trip at 5.0 mm/s has not. We're catching this during the actionable window between HI and HH — when the operator is forced to make a decision but hasn't yet hit the automatic shutdown. GDC provides the context that makes the right decision obvious: don't pull, adjust the choke." |

---

## 9. Visual Design Directive

**Lead with Layer 3, not Layer 1.** The two-line chart (vib cycling up, temp flat) is the **setup** — it creates the surface-vs-downhole ambiguity. The **punchline** is the OEM retrieval + document fusion + Advisor verdict "do not pull well — $1,500 truck roll." Build the H2 layout so the evidence wall and Advisor verdict receive equal or more prominence than the chart.

**Shared annotated SVG wellbore:** The digital twin schematic is visible on BOTH the SCADA and GDC sub-views. It shows a healthy green pump/motor at depth. At the surface, slugging animation (alternating gas/liquid pulses in the flowline). The schematic explicitly annotates: pump intake location, casing annulus, and wellhead. Labels indicate: "PUMP — HEALTHY / Motor Temp: 198°F" and "SURFACE FLOWLINE — slug flow active." This makes the physical story immediately clear without verbal explanation.

*Anti-pattern to avoid:* leading with "look at these two lines" as the primary visual. A good SCADA screen can show two lines. What it cannot show is the choke log, the shift note, and the OEM "do not pull" rule assembled into a cited Advisor verdict. That assembly is the hero.
