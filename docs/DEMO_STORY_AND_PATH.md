# GDC Edge AI Demo — Story and Path to Recording
**Created:** Session AU (June 11, 2026)  
**Purpose:** Stakeholder-ready narrative of how we got here, the locked value proposition, full horizon stories, and the morning checklist to reach recorded narrations.  
**Audience:** Internal stakeholders, GDC sales, technical reviewers.

---

## Section A — The Journey: How We Got Here

### Why This Story Matters

This document records the intellectual path that produced the demo. We show it to stakeholders not as an apology, but as evidence: we stress-tested every claim with a hostile-engineering persona before shipping a single pixel. What survived is real. What was cut was cut because it would not have survived a five-minute challenge from an O&G engineer in the room.

### Beat 1 — We Started by Overclaiming Against SCADA

Early versions of the demo framed GDC as a detection-race winner: "GDC sees the fault 8 minutes before SCADA alarms." The story was visually dramatic and easy to understand. It was also wrong in the wrong ways.

A hostile red-team identified the structural problem: advanced APM platforms (GE SmartSignal, AVEVA PRiSM, Aspen Mtell) do adaptive multivariate ML. Against best-of-breed APM, our lead-time converges to near-zero. We were implying "SCADA lets the pump die" — a straw man. SCADA trips and shuts the well in to protect the pump. It does not let the pump die.

**What we cut:** detection-race framing, lead-time banners, "Smart SCADA" label, "PUMP SEIZED" outcome card.  
**What we kept:** the honest architecture story. SCADA trips on tags. APM scores tag-patterns. GDC reads the documents.

### Beat 2 — We Over-Corrected and Conceded Too Much

After retiring the detection race, we tried to make L3 document-fusion alone carry the moat. This produced scenarios where a skilled engineer with the same documents, given time, could reach the same conclusion. Every demo ended with an implicit "but a human could figure this out" exposure.

The honest answer — which we articulate now — is not that GDC sees what humans cannot. It is that GDC makes an expert-level diagnosis *automatic, fleet-scale, instant, cited, and inside your perimeter* — turning a conclusion that is possible in principle into one that happens every time in practice, at 2am, across 200 wells, without dispatching anyone.

### Beat 3 — H2 Slug Flow: Dual-AI Red-Team Found Four Fails

The H2 scenario was designed around slug-flow discrimination (intermittent gas/liquid slugs causing cyclic vibration that looks like bearing wear). We ran a dual-AI red-team (Gemini + Claude Opus, independently, with hostile-engineer personas and web access). Both passes converged on four FAIL verdicts:

1. **Flat-temperature discriminator runs backwards:** The winding RTD is in the motor, not the pump/protector bearings. In high-GOR wells, gas at intake reduces cooling — temperature trends *up*, not flat. The discriminator we claimed was the deciding signal ran in the wrong direction.
2. **False dichotomy on costs:** The real baseline is a choke/VFD adjustment first — the same cheap surface action from the amp chart. We framed $150k pull vs. $1,500 truck roll as the only two options. Wrong.
3. **Deciding signal is telemetric:** Cyclic amps-with-recovery + cyclic PIP *is* the deciding signal. APM reads it. Documents only corroborate. L3 moat was efficiency-only, not categorical.
4. **APM stopped at anomaly score — overclaims:** Mtell classifies trained failure modes and attaches canned SOPs. We understated what APM does.

H2 slug-flow was retired. Correctly.

### Beat 4 — H2 Frac-Hit: Failed Test 1

The replacement candidate — offset-well frac-hit interference — was appealing: the neighbor's frac schedule is categorically off-sensor (third-party regulatory filing). But in-session red-team and Gemini validation found it fails **Test 1 (discrete past event)**: experienced Permian operators recognise frac-hit signatures. The ambiguity claim was the same failure class as slug-flow. A "pre-alert" reframe (proactive RRC filing monitoring) was proposed and correctly rejected by the user as too O&G-specific for a broad value story.

### Beat 5 — The L2 Over-Concession: Root Cause Identified

After two H2 failures, the root problem crystallised: by over-conceding L2 (trying to prove only L3 carries the moat), we were generating scenarios that a skilled engineer could resolve on one well, given time. That produced weak stories because the honest answer to "but a human could figure this out" is yes — *on one well, with time*.

GDC's value is not exclusive capability. It is **automatic + fleet-scale + instant + cited + sovereign**. We needed to claim that honestly, not try to win on sensor-vs-document impossibility alone.

### Beat 6 — The Resolution: Where, Not What

A neutral Gemini market-check (no hostile priming — "what are major APM vendors building for 2025–2026?") returned: C3.ai, GE Vernova, AVEVA, Aspen Mtell, and Cognite all have roadmap items for LLM-based, document-aware, real-time diagnosis. The entire APM industry is building this capability — for cloud deployment.

GDC's differentiator is **WHERE** it runs, not **WHAT** it does. The capability class is industry-validated. GDC delivers it inside the operator's sovereign perimeter, on open weights, where the data already lives. That claim is true, cannot be attacked, and is aligned with where the market is going.

### Beat 7 — What Survived Is Real

We refused to ship a claim we couldn't defend. Three sessions of red-teaming — hostile-engineer personas, dual-AI validation with web access, in-persona challenge-before-defense discipline — produced a value proposition that passes every gate. The scenarios that survived are physically correct, provenance-traceable, categorically off-sensor at the decisive variable, and common enough that fleet-scale automation has defensible ROI.

**The demo that exists is the demo we can stand behind.**

---

## Section B — Locked Value Proposition

> **The strategy is decided. Do not re-litigate. The following is the authoritative framing for all demo copy, narration, and stakeholder communication.**

### The Thesis

The AI-powered diagnostic advisor — the capability the entire APM industry (GE Vernova, AVEVA, Aspen Mtell, Cognite, C3.ai) is building for cloud deployment in 2025–2026 — GDC delivers inside the operator's sovereign boundary, on open-weight Gemma, at the edge, where the data already lives.

### Three Gaps

**1. The Diagnostic Gap**  
SCADA says *that* something is wrong. APM says the *pattern* is anomalous. Neither says *why*, because "why" lives in unstructured documents — shift notes, workover reports, OEM manuals, lab results, completion records. No sensor-based system can read them in real time. GDC reads the documents.

**2. The Scale Gap**  
A senior engineer can diagnose one well. They cannot diagnose 200 wells at 2am. GDC gives every operator senior-level differential diagnosis on every asset at once — automatic, cited, with an audit trail.

**3. The Sovereignty Gap**  
Cloud APM requires data egress — precluded for NOCs, IEC 62443 OT-compliance operators, and jurisdictions with data-residency law. GDC is the only complete path for those operators. The decision and the safety constraint both remain on-premise.

### The Honest-Footing Rule

When challenged with "but a human could figure this out":

> *"Yes — a skilled engineer could reach this conclusion with the right documents and time, on a single well. What GDC does is make it automatic, fleet-scale, instant, cited, and inside your perimeter — turning a diagnosis that's possible in principle into one that happens every time in practice."*

### The Competitive Claim (Gemini neutral-search confirmed — use this exact wording)

> *"No native, production-ready commercial product combines real-time ML anomaly detection with LLM-based differential diagnosis over unstructured maintenance documents — as of 2025–2026, this is where all major APM platforms are heading. GDC delivers it now, inside the sovereign perimeter, on open weights."*

### Market Validation

- C3.ai 2026 roadmap: "virtual subject matter expert… full context — all sensor data, structured, unstructured, past work performed on the machine"
- GE Vernova, AVEVA, Aspen Mtell, Cognite: all have GenAI roadmap items for document-aware diagnosis
- The direction is industry-validated. GDC's differentiator is WHERE it runs (sovereign edge), not WHAT (the AI capability class).

---

## Section C — Full H1 Story: DISCERN

**Tab:** Discern | **Arc beat:** The Diagnostic Gap | **Vid spine:** "One signature. Two causes. Opposite actions. The answer was never in the sensors."

### The Asset

Mature Permian Basin ESP well. Moderate-sand formation. AR-trim (abrasion-resistant) pump. Standard **intake-only** PDG sensor string — no downhole discharge-pressure gauge. This is the configuration of approximately 90% of Permian ESPs. The RTOC has PIP, Motor Amps, Winding Temp, and Vibration from this well.

### The Event

Pump Intake Pressure (PIP) and Motor Current (Amps) decline together. On an intake-only sensor string, this signature is genuinely ambiguous between two root causes with *opposite* correct actions:

| Cause | Mechanism | Correct Action |
|---|---|---|
| **Gas Lock** | Casing annulus fully submerged. Gas pocket in pump stages. Pump unloads hydraulically. | **VFD trim 52 → 44 Hz.** Slows impeller; gas pocket vents up the submerged annulus. Well stays online. ~$2,500. |
| **Fluid Drawdown** | Dynamic fluid level critically depleted. Pump runs dry. | **Emergency shut-in.** In a moderate-sand well, VFD trim drops velocity below critical sand-transport threshold → solids compact around rotating impeller → pump seizure → ~$150k workover. |

*Source: API RP 11S §7.2. Ambiguity on intake-only string: Gemini + Claude Opus independent expert reviews, June 10, 2026.*

### Why the Sensor Cannot Resolve It

The clean discriminators are absent or slow:
- A **discharge-pressure gauge** would resolve state (head collapses in gas lock, holds in drawdown) — this well doesn't have one.
- An **acoustic fluid-level shot (Echometer)** is the independent ground truth — but requires dispatching a crew (hours; far exceeds the ~25-min thermal window).
- **PIP itself is a submergence proxy** — with gas breaking out, the annulus gradient is uncertain, degrading the inference.

In the early decision window, on the data the RTOC has, the signal is genuinely ambiguous.

### Why Sand Makes the Stakes Asymmetric

In a moderate-sand well, VFD trim during drawdown is not merely suboptimal — it is catastrophically destructive. A clean well can be stabilised with a trim-down. This well cannot. Sand is the stakes-setter. The Briefing establishes the well's character before the live scenario plays.

### The Deciding Context (Not in Any Sensor)

Whether trim is safe depends on the well's **sand/completion history**, the **GOR trend**, any **offset-well frac activity**, and the most recent **shift note**. None of these are sensor signals. They are field events recorded only in unstructured documents.

### GDC's Resolution

GDC's pgvector RAG pipeline retrieves:
- The **06:15 Operator Shift Note** (elevated GVF, rising GOR, casing pressure building → Gas Lock indicators, stable sand history → VFD trim safe)
- The **06:00 Sonic-Survey Summary** (fluid level near intake, flat casing pressure, no free-gas indicators → Drawdown → trim contraindicated, shut-in)

The context the documents supply — in seconds — is what the RTOC operator cannot assemble in time from the sensor screen alone.

### The Win

Without GDC: standard policy on ambiguous underload alarm = production-deferring shut-in (safe for both causes, but costs ~$3k–$8k in deferred production + restart). *Correct decision, expensive by default.*

With GDC: cited differential diagnosis in seconds, operator reviews and approves (HITL), confident production-preserving action every time. At 2am across 200 wells, operators default to reflexive shut-in. GDC enables the better call.

### Cross-Industry Universality

| Vertical | Ambiguous Signal | Deciding Context (in documents) |
|---|---|---|
| **O&G upstream** | ESP PIP + amps decline | Sand history · GOR lab report · sonic survey · shift note |
| **Power & Energy** | Transformer DGA gas rise | LTC maintenance log · loading plan · prior fault record |
| **Manufacturing** | Motor vibration rise | Maintenance log · tooling-change record · production schedule |

---

## Section D — Full H2 Story: CLASSIFY

**Tab:** Classify | **Arc beat:** The Provenance Gap | **Vid spine:** "The pump isn't failing. The last workover is. And it's written down in a report no sensor can read."

### The Asset

Permian ESP producer, 8 weeks post-workover. Standard 4-sensor string: PIP, motor amps, winding temp, single-axis vibration accelerometer.

### The Event

Motor efficiency declining + vibration rising slowly over 3–4 weeks. On the standard 4-sensor string, this pattern matches early **bearing wear** — the most common cause of this signature, and the cause any APM platform would route to.

### The Hidden Cause

During the workover 8 weeks ago, the crew used a **non-OEM-spec hydraulic fluid incompatible with the Buna-N elastomer shaft seals**. This is documented only in the workover completion report (fluid type, vendor, date). No online sensor on the running ESP carries this information — it is physically impossible for one to do so.

### Why APM Gets It Wrong

Elastomer seal degradation and bearing wear produce genuinely ambiguous signatures on a standard 4-sensor ESP string without vibration spectral analysis or dedicated bearing temperature sensors. *(Source: API RP 11S3, 11S5; Gemini search confirmed.)* APM routes to the *statistically common* hypothesis — bearing wear — and recommends pump-pull investigation. APM cannot access the workover completion report.

### GDC's Resolution

L2 classifier (XGBoost, `esp_health.ubj`) flags mechanical degradation → routes to L3 fusion.

Gemma reads:
1. **Workover completion report** — fluid type and vendor recorded (measurements/observations only; no diagnosis)
2. **OEM fluid compatibility matrix** — the recorded fluid class is INCOMPATIBLE with Buna-N elastomers
3. **Timing correlation** — 3-week symptom onset matches expected elastomer swell timeline for that fluid class
4. **Last pull record** — bearing condition: normal. Eliminates bearing-wear hypothesis.

**GDC verdict:** "Elastomer seal degradation from workover fluid incompatibility — NOT bearing wear. Correct action: controlled flush + reseal (~$8k–$15k)."

### The Win

| Path | Action | Cost |
|---|---|---|
| APM diagnosis | Bearing wear → pump-pull investigation | ~$70k–$100k (WTX spot rig ~$14k/day × 3 days + motor inspection + deferred production) |
| GDC diagnosis | Elastomer degradation → flush + reseal | ~$8k–$15k |

**The fluid-seal relationship is purely documentary. No sensor or APM platform can infer it. The cause was never in any telemetry — it was in a document from 8 weeks ago.**

At fleet scale (200 wells, 2am), no operator will think to check the 8-week-old workover completion report when a vibration alarm fires. GDC generates the non-obvious provenance hypothesis automatically.

### Why This Class Is Common and Material

51% of ESP failures are attributed to human factors / operational problems. *(2014 SPE AI Conference survey; SPE 185275-MS, 194398-MS, 144562-MS.)* The maintenance-provenance class — wrong fluid, non-spec parts, improper procedures — is the common case, not an edge case.

### Cross-Industry Universality

| Vertical | Ambiguous Signal | Hidden Provenance Cause |
|---|---|---|
| **O&G upstream** | ESP efficiency decline + vibration rise | Wrong hydraulic fluid in workover completion report |
| **Power & Energy** | Transformer overheating | Non-spec cooling fluid in last service record |
| **Manufacturing/MRO** | Pump cavitation or actuator degradation | Fluid/feedstock change in batch/service record |
| **Mining** | Gearbox signature anomaly | Wrong lubricant grade in maintenance log |

### Survival Test Confirmation (All 4 Pass)

| Test | Result | Evidence |
|---|---|---|
| **1. Discrete past event** | ✅ PASS | Wrong-fluid fill is a specific event at a specific time (workover date), not a slow drift |
| **2. Categorically off-sensor** | ✅ PASS | No online sensor on the running ESP can measure historical fluid-fill provenance. Physically impossible. |
| **3. APM mis-routes** | ✅ PASS | Standard 4-sensor string: bearing wear and seal degradation genuinely ambiguous (API RP 11S3/S5). APM routes to bearing wear → $70k–$100k pull. |
| **4. Common and material** | ✅ PASS | 51% of ESP failures = human factors/operational problems. Fleet-scale automation has defensible ROI. |

---

## Section E — Full H3 Story: OPTIMIZE

**Tab:** Optimize | **Arc beat:** The Sovereignty Gap | **Vid spine:** "Push for the price window. The edge holds the safety line — even if the cloud goes dark."

### The Setup

Oil price spikes. The operator wants to run the ESP faster — 50 Hz → 58 Hz — to capture the production upside. This is a standard O&G economics decision.

### The Risk

Faster means hotter. Motor winding temperature exceeds the field derated operating setpoint of **280°F** → motor burnout → ~$150k failure. *(IEC 60085 Class H insulation limit = 356°F / 180°C; field operating setpoint derated to 280°F — the limit enforced in the demo.)*

### The Collaboration (Honest Hybrid — Not Air-Gap)

This is NOT an air-gap claim. The framing is precise:

> "Vertex AI Vizier searches the optimization space using Gaussian process math — only parameter-level data goes to cloud, never raw operational telemetry. The local XGBoost thermal model (`esp_thermal.ubj`) evaluates every candidate setpoint against the 280°F constraint and holds it — even if the WAN link drops mid-search. The decision and the safety constraint both remain on-premise."

| Component | Where | What it does |
|---|---|---|
| Vertex AI Vizier | Cloud | GP-based Bayesian search over Hz + well parameters — generates candidate setpoints |
| `esp_thermal.ubj` (XGBoost) | Edge (RTOC) | Evaluates each candidate against 280°F thermal constraint |
| Human operator (HITL) | RTOC | Reviews and approves the final setpoint |

### The Novel Piece

It is not the cloud optimization (Bayesian search is common). It is the **edge safety constraint that holds when the link dies** — at precisely the wrong moment (process upset, storm, satellite outage during a price spike). The edge is the safety system.

### The Win

The operator runs at the optimized setpoint — within thermal limits, capturing the production upside. If the satellite link drops mid-search, the edge model holds the constraint. The AI goes as far as it safely can. No further.

### Cross-Industry Universality

| Vertical | Optimization goal | Edge-held safety constraint |
|---|---|---|
| **O&G upstream** | Max Hz for production upside | Motor winding temp limit (280°F) |
| **Power & Energy** | Push transformer loading at peak demand | Hot-spot temperature limit (IEC 60076) |
| **Manufacturing** | Line-speed throughput | Quality/thermal process constraint |

---

## Section F — Path to Recordings: The Morning Checklist

The following is the ordered checklist to reach recorded narrations. Execute top to bottom.

```
MORNING SESSION — ordered checklist to reach recorded narrations

BUILD (do first):
1. [ ] Read this document (confirm framing matches what's in the UI)
2. [ ] Walk H1 all 6 briefing panels — note any copy changes against locked framing
3. [ ] Walk H1 scenario replay — confirm cited verdict, document reveals, HITL
4. [ ] Build H2 3-panel briefing (per Priority 6 spec in NEXT_SESSION_PROMPT)
5. [ ] Sign off H2 synthetic documents (workover report, OEM matrix, shift note) against G1–G6 gate
6. [ ] Walk H2 scenario replay (needs backend endpoint + replay UI)
7. [ ] Walk H3 Optimize tab — confirm honest Vizier hybrid framing in copy
8. [ ] Fix H3 tab copy ("no cloud dependency" → honest hybrid framing per P4)

RECORD:
9. [ ] Record H1 narration (~90–120s) — script in docs/VIDEO_SCRIPT.md
10. [ ] Record H2 narration (~90–120s) — script in docs/VIDEO_SCRIPT.md
11. [ ] Record H3 narration (~90–120s) — script in docs/VIDEO_SCRIPT.md
12. [ ] Record overview / value-prop narration (~60s) — script in docs/VIDEO_SCRIPT.md
```

---

## Appendix — Key Decisions and Why

| Decision | Reasoning |
|---|---|
| Cut detection-race framing | Against best-of-breed APM, lead-time converges to near-zero. Straw man against SCADA. |
| Cut slug-flow H2 | 4 FAILs in dual-AI red-team. Deciding signal is telemetric. |
| Cut frac-hit H2 | Fails Test 1 — experienced Permian operators recognise signatures. |
| Chose maintenance-provenance H2 | Passes all 4 survival tests. Purely documentary cause. Common class. |
| Honest hybrid H3 (not air-gap) | "No cloud dependency" is too absolute. Honest: decision and safety constraint on-premise; Vizier does cloud GP math only. |
| Sovereignty as differentiator | Industry is building the capability for cloud. GDC's WHERE is the moat, not WHAT. |
| Concede L2 honestly | Makes the L3 moat more credible. Never claim "SCADA can't do multivariate detection." |
