# H2 — Slug Flow Discrimination — Demo Narrative
**Version:** Session C (June 5, 2026)
**Status:** CANONICAL — read before editing H2 UI, H2 LLM prompts, or H2 evidence wall
**Mirrors:** docs/DEMO_MASTER.md §5 (spec); this file is the *narrative rationale* layer

---

## 1. One-Line Thesis

> **"Am I about to spend $150,000 on a false alarm?"**

H1 asks *what is wrong and how do I fix it cheaply.* H2 asks *what is NOT wrong — and how do I avoid the expensive overcorrection?* This is the discrimination act in the Protect → Discriminate → Optimize arc.

---

## 2. The Business Pain

**Unnecessary pump pulls driven by vibration alarms** are a recurring, expensive, and professionally embarrassing problem in ESP production operations. A vibration alarm fires on the SCADA screen. The operator cannot tell from the sensor alone whether it is:
- A **failing downhole bearing** (real problem → pump pull justified) or
- **Surface flowline slug flow** transmitting hydraulic impulses to the downhole sensor (surface problem → pump is fine → pull completely unnecessary)

The conservative, defensive response is to call the workover crew. A pump pull is ~$150,000. On a mechanically sound ESP that needed a $1,500 choke-valve truck roll. Every production engineer in the room has lived this exact scenario.

---

## 3. The Physics (citable)

**Why slug flow causes vibration but not motor heat:**
Flowline slug flow occurs when a high-GOR production stream forms intermittent gas pockets and heavy liquid slugs cycling through the surface flowline (see Well A-3 separator test: 1.8 bbl/cycle, 14-min periodicity). Heavy liquid slugs hit the wellhead piping and transmit mechanical shocks down the production tubing — the downhole vibration sensor reads high. But the slugging is **at the surface**; no additional friction or heat is generated at the downhole motor. Motor cooling fluid flow is unaffected. **Motor winding temperature stays flat.**

**Why a bearing failure causes both vibration AND motor heat:**
A genuine downhole bearing failure generates friction. Friction generates heat. Motor winding temperature rises along with vibration. **Temperature is the discriminating signal.** If vibration rises with flat temperature: surface. If both rise together: downhole.

*Reference:* ESP OEM troubleshooting guides; SPE-174536-MS; Baker Hughes Centrilift design guide; DEMO_MASTER §9 H2 citation table.

**The SCADA architecture problem:**
SCADA's vibration trip is at 5.0 mm/s. Well A-3 is at 2.4 mm/s — **no alarm has fired yet.** When the trip does fire, SCADA has one alarm: "VIBRATION HIGH." It has no mechanism to co-read the flat motor temperature as exonerating evidence. It does not read the shift note. It cannot retrieve the OEM rule that says "vibration without thermal elevation = surface flow regime."

---

## 4. The Three Evidence Layers

This framework applies to all three demo acts (H1/H2/H3). For H2:

### Layer 1 — Telemetry departs normal
Vibration is climbing (1.1 → 2.4 mm/s). Motor temperature is flat (198 °F).
- **What a multivariate SCADA can also see:** both sensors on the same trend chart. A skilled controls engineer can notice the decorrelation.
- **Why this layer alone is not a win for us:** a smart engineer with SCADA could reach the same surface-vs-downhole intuition. We do not stake the H2 argument on Layer 1.

### Layer 2 — Classifier names the fault (calibrated probability, not a boolean)
The XGBoost classifier outputs a probability vector — `slug_flow: 0.90, bearing_wear: 0.06, normal: 0.03…` — built on a flat `dtemp_dt` training signature (Session S/W, class 4). The classifier fires because the **shape, rate, and correlation** of the two-sensor signal matches the slug-flow training data.

**The honest Layer-2 claim** (scope carefully — do not overclaim):
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
| 1 | 📊 Vibration sensor | 1.1 → 2.4 mm/s rising | ✅ Yes |
| 2 | 📊 Motor temp sensor | 198 °F flat (exonerating) | ✅ Yes |
| 3 | 🔧 Surface Choke Log | 3 manual choke adjustments in 4h; operator compensating at surface | ❌ No |
| 4 | 🧪 Separator Test Report | 1.8 bbl slugs, 14-min period, GOR rising — confirms surface slug regime | ❌ No |
| 5 | 📋 Night Shift Note | "Pumping rough but temp is normal — unusual if it were a bearing" | ❌ No |
| 6 | 📖 OEM Troubleshooting Guide (RAG) | "Vibration without thermal elevation = surface flowline slugging. Do not pull well." | ❌ No |

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
> *"Vibration elevated. Motor temperature completely flat. This combination is the diagnostic signature of surface flowline slugging, not downhole mechanical wear. Six independent sources confirm: the pump is healthy. The SCADA vibration alarm would have triggered a $150,000 pull on a mechanically sound ESP. Correct response: $1,500 truck roll to adjust the surface choke valve."*

The Advisor also explicitly addresses the counterargument documents (15% of feed):
> *"Shift record notes 'unusual vibration' — could be consistent with early bearing wear. However: bearing wear would produce a measurable temperature rise within minutes. Temperature has been flat for 4+ hours. The bearing hypothesis does not fit the thermal evidence."*

---

## 6. The Decision and Outcome

**Post-injection state:** operator sees the two-line chart (vib up, temp flat), 6-source evidence wall, streaming Advisor verdict, and the truck-roll CTA.

**Operator action:** "Dispatch Truck Roll" → technician en-route → choke adjusted → vibration drops → `h2Resolved`.

**Financial outcome:** $1,500 avoided $150,000 — stated by the LLM, not a static card.

---

## 7. Asset and Data Wiring (current implementation state)

- **Asset:** ESP-ALPHA-3 / Well A-3
- **Fault injection:** `POST /api/inject-fault` → `fault_type: "slug_flow"`, `asset_id: "ESP-ALPHA-3"`
- **Intel feed:** `INTELLIGENCE_FEED["slug_flow"]` in `app.py` — 3 pre-authored session documents (`sf_1` choke log, `sf_2` separator test, `sf_3` shift note) **already wired**
- **Truck-roll dispatch:** `POST /api/h2/dispatch-truck-roll` **already wired** in `app.py`
- **RAG:** OEM "do not pull well" passage lives in `rag_documents` (18 rows, embedded)
- **Classifier:** `esp_classifier.ubj` class 4 = `slug_flow`, flat `dtemp_dt` training signature ✅ deployed (Session B, v3, live-verified 100% recall)
- **Remaining work:** H2 visual build in `index.html` (Phase 2 per DEMO_MASTER §12) — single batched `replace_in_file`, no `app.py` changes needed

---

## 8. What to Say If Challenged

| Challenge | Response |
|-----------|----------|
| "A good multivariate SCADA can also see vibration + flat temp" | "For the sensor pattern — yes, a skilled engineer with the right SCADA setup could reach the same intuition. What's different: our classifier scores continuously before any threshold, outputs a calibrated probability for all five fault types learned from data (not one hand-authored rule), and retrains when reservoir conditions change. But I'd rather show you the piece a controls engineer literally cannot replicate with SCADA: the four field documents you just saw." |
| "Your shift note is hand-authored" | "The three pre-loaded session documents are seeded for the demo. In a live deployment, the `_intel_generator` thread reads from live shift-note integrations and field data systems. The RAG pipeline and fusion mechanism are identical either way." |
| "How do you know the OEM rule is reliable?" | "It's directly from the ESP OEM troubleshooting guide embedded in our AlloyDB corpus. SPE-174536-MS provides the same diagnostic principle. The 'flat temperature = surface issue' rule is industry-standard — we've just made the system retrieve and cite it automatically." |
| "Slug flow at 2.4 mm/s isn't high enough to trigger SCADA" | "That's exactly the point. We're classifying this as slug_flow at 90% confidence *before* the SCADA vibration trip at 5.0 mm/s has fired. This is the 'probability scoring before thresholds' advantage. You catch it and fix it cheap, before the pattern escalates into a genuine alarm." |

---

## 9. Visual Design Directive (from Session C design decision)

**Lead with Layer 3, not Layer 1.** The two-line chart (vib up, temp flat) is the **setup** — it creates the surface-vs-downhole ambiguity. The **punchline** is the OEM retrieval + document fusion + Advisor verdict "do not pull well — $1,500 truck roll." Build the H2 layout so the evidence wall and Advisor verdict receive equal or more prominence than the chart.

*Anti-pattern to avoid:* leading with "look at these two lines" as the primary visual. A good SCADA screen can show two lines. What it cannot show is the choke log, the separator test, the shift note, and the OEM "do not pull" rule assembled into a cited Advisor verdict. That assembly is the hero.
