# GDC Edge AI Demo — Narrative Guidance for Video Production
**Created:** Session BS+28 (June 18, 2026)  
**Purpose:** Strategic narrative framework for three Veo-based video walkthroughs. Defines the primary communication focus, key messages, and claim boundaries for each of the three audience personas.  
**Source of truth:** `docs/DEMO_MASTER.md` (specs, physics), `docs/STAKEHOLDER_BRIEF.md` (business framing), `docs/DEMO_STORY_AND_PATH.md` (red-team history)  
**First narrative to produce:** Persona 2 (Product / Operations Context) — see §3.  
**Claim compliance:** All hard figures in this document have SURVIVES status in `docs/CLAIM_LEDGER.md`. Ranges marked 🔴 are soft estimates confirmed directionally by SME; do not present as hard numbers.

---

## Section 1 — The Architecture of the Story

### Why the Three Personas Are Different Conversations

GDC Edge AI solves the same technical problem — automatically closing the document-context gap in real-time operational diagnosis — but the commercial significance of that solution reads differently depending on who is asking.

- **Persona 1** asks: *"Does this improve my business economics?"* They want to know what gets protected, what gets avoided, and whether the ROI case is credible. They will tolerate one or two technical sentences. They will not tolerate jargon.
- **Persona 2** asks: *"What capabilities does this require, what is the product architecture, and how do we package it?"* They are the operators and product managers who translate business requirements into systems that field engineers and digital teams must deliver. They want to understand what Halliburton (or any OFS firm) would need to build, deploy, and support.
- **Persona 3** asks: *"How does the technology actually work, and is it the right architecture?"* They are the engineers and cloud architects who will evaluate Google Cloud, GDC, Kubernetes, local inference, and the RAG pipeline. They will look for claims that cannot survive first-principles scrutiny.

**These are not the same conversation delivered at different levels of abstraction.** Each narrative needs a distinct spine, distinct value hierarchy, and distinct claim vocabulary. The scenarios (H1, H2, H3) appear in all three, but the emphasis, entry point, and exit point differ for each persona.

---

### The Three-Act Scenario Structure — Summary for Video Purposes

Before defining the per-persona focus, here is the authoritative summary of the three demo horizons. All video narratives must use these descriptions verbatim.

#### H1 — DISCERN: One Signal. Two Causes. Opposite Actions.

**Asset:** Permian Basin ESP well. Intake-only sensor string: Pump Inlet Pressure (PIP), Motor Amps, Winding Temperature, Vibration. No downhole discharge gauge (~90% of Permian ESPs).

**The Event:** PIP and Motor Amps decline together. On an intake-only string, this signature is physically ambiguous between:

| Cause | Mechanism | Correct Action | Cost if Wrong |
|---|---|---|---|
| **Gas Lock** | Annulus submerged; gas pocket in pump stages | VFD trim: 52 → 44 Hz. Well stays online. | If patient misidentified as drawdown and shut in: ~$3k–$8k deferred production + restart costs |
| **Fluid Drawdown** | Dynamic fluid level critically depleted | Emergency shut-in. Do NOT trim. | If misidentified as gas lock and VFD trimmed: sand velocity drops → solids compact around rotating impeller → pump seizure → **~$150k workover** |

**Why sensors cannot resolve it:** The decisive discriminators (discharge pressure gauge, acoustic fluid-level shot) are either absent or require dispatching a crew (hours). PIP alone cannot distinguish gas breakthrough from fluid depletion on this string configuration.

**What GDC does:** pgvector RAG retrieves the operator shift note and the sonic survey summary — documents that establish whether the well is submerged-with-gas (trim is safe) or drawn-down-critically (trim is catastrophic). In seconds, with citations, before the SCADA alarm completes.

**Lead time (BS+26, HEALTH_THRESHOLD=0.87):** GDC's XGBoost health score crosses its detection threshold **4–9 minutes before the SCADA hard-limit alarm fires**. Winding Temperature and Vibration remain near-nominal throughout the entire detection window (they are lagging indicators; only PIP and Amps are leading). The temporal advantage is material but secondary — the categorical moat is document-context fusion, which no sensor-based system can architecturally replicate.

**The Win:** Without GDC, standard policy on ambiguous underload = conservative shut-in (safe for both causes; ~$3k–$8k deferred production cost). With GDC, cited differential diagnosis drives the correct and cheaper action, every time, at fleet scale, at 2am.

---

#### H2 — CLASSIFY: The Right Symptom. The Wrong Cause. An Expensive Fix.

**Asset:** Permian ESP producer on a waxy carbonate formation. Standard 4-sensor string (PIP, Motor Amps, Winding Temp, Vibration). No discharge gauge.

**The Event — 3–4 week trajectory:**
- Motor amps rising (+12–18% above nominal)
- Vibration rising (nominally ~1.0 mm/s → ~4.5 mm/s RMS; crosses ISA-18.2 High alarm at 4.0 mm/s)
- Motor efficiency declining (~8–12% below nominal)
- PIP stable or slightly rising (restriction above pump steepens system curve → pump operating point shifts to lower flow → less drawdown → PIP builds; per API RP 11S)

**What APM does:** Rising amps + rising vibration + declining efficiency on a 4-sensor string **is the pattern-signature of early bearing wear** — the most common ESP failure class in APM training data. Best-of-breed APM (SmartSignal, AVEVA PRiSM, Aspen Mtell) correctly identifies the symptom; it routes to the most-probable failure hypothesis and recommends pump-pull investigation. **Correct symptom. Wrong root cause. Wrong fix. Cost: ~$70k–$100k.**

**The Hidden Cause:** Well A-3's 90-day paraffin hot-oil treatment is **52 days overdue** (Day 142). The well produces from a waxy carbonate formation (Wax Appearance Temperature ~118°F per PVT analysis). As produced fluids cool below WAT rising up the tubing, paraffin deposits on the tubing walls. The growing restriction forces the pump to work harder — driving the signature APM reads as bearing wear. The delay is documented in the **chemical vendor service log** — not in SCADA, not in any sensor, not visible to any APM.

**Why the gap is structural, not behavioral:** A third-party vendor logistics dispute caused the delay. The operator is not negligent. The vendor portal is simply not integrated with the SCADA/APM data stack. GDC closes the silo; it does not expose operator failure. *(SME-confirmed: Bill Barna, Permian production engineer: "Many operators have poor programs. Often, there are so many false positives, nobody believes the system. All of the problems you listed happen.")*

**What GDC does:** Semantic RAG retrieves three siloed documents APM cannot access:
1. **Chemical vendor service log** — 90-day hot-oil interval; last treatment Day 0; Day 142 = 52 days overdue. Delay reason: vendor truck availability logistics dispute. *(Gemma-generated per run — dynamic document)*
2. **Fluid PVT lab report** — crude WAT = 118°F; high wax content; 90-day treatment interval confirmed per production engineering recommendation. *(Static seed)*
3. **Prior pull record** — last workover 18 months ago; bearings: NORMAL; no unusual wear. *(Static seed — eliminates bearing-wear hypothesis)*

**GDC Verdict:** *"Paraffin wax deposition — NOT bearing wear. Hot-oil treatment overdue by 52 days — consistent with restriction onset at Day ~106. Bearings normal at last inspection 18 months ago — bearing-wear hypothesis eliminated. Dispatch hot-oil truck. Do NOT pull."*

**The Win:**

| Path | Action | Cost |
|---|---|---|
| APM-recommended | Pump-pull investigation (bearing wear hypothesis) | ~$70k–$100k |
| GDC-recommended | Hot-oil truck roll + annulus flush | ~$3k–$6k *(🔴 soft estimate; SME-confirmed directionally)* |

**Pump pull completely averted.** The well resumes nominal production within hours of the hot-oil treatment.

---

#### H3 — OPTIMIZE: Maximum Production. No Pump Destroyed.

**Asset:** Pad Alpha — 6 active ESP producers (A-1 through A-6) operating under a single midstream gas-compression takeaway contract.

**The Binding Constraint:** Gas ceiling **8.0 MMscfd** (🟡 OUR-CODE — representative of real Permian midstream contract structure; scenario parameter). Every barrel of oil produced carries associated gas. Wells differ dramatically in Gas-Oil Ratio (GOR):

| Well | GOR (scf/bbl) | Character |
|---|---|---|
| A-3, A-6 | 450 | Lowest GOR — most gas-efficient |
| A-1, A-2 | 520–680 | Low GOR |
| A-4 | 890 | Mid-GOR |
| A-5 | 1,350 | Highest GOR — throttle first |

**Without GDC (SCADA Uniform Throttle):** Scale every well back equally to stay below the ceiling. Safe, conservative, and suboptimal — it wastes the gas budget on high-GOR wells that could give more gas-efficient wells room to run faster. Cost: ~**78 bbl/d of deferred production**.

**With GDC (Joint Optimal Setpoint Allocation — Pad Alpha):**
- Vertex AI Vizier (cloud Gaussian Process Bandit) searches the 6-dimensional Hz optimization space. Only parameter-level data (Hz vectors and objective scores) goes to cloud. **Raw operational telemetry and well identities never leave the sovereign boundary.**
- The local physics polynomial `T = f(vfd_hz, motor_amps, intake_fluid_temp, water_cut_pct)` evaluates every Vizier candidate against the 280°F winding-temperature operating limit *on-premise*.
- LP-optimal analytical solution (closed form, gas-only) is computed locally as both the initialization baseline and the WAN-down fallback.
- Human operator reviews and approves the final setpoint package (HITL gate).

**Result (live Vizier API, 2026-06-11):**

| Well | SCADA Uniform | GDC Optimal | Role |
|---|---|---|---|
| A-3 | ~63.0 Hz | **66.0 Hz** | Lowest GOR — full speed |
| A-6 | ~63.0 Hz | **66.0 Hz** | Lowest GOR — full speed |
| A-1, A-2 | ~63.0 Hz | 65.5 Hz | Low GOR — near max |
| A-4 | ~63.0 Hz | 64.2 Hz | Mid-GOR — modest trim |
| A-5 | ~63.0 Hz | **59.7 Hz** | Highest GOR — throttled |

**Uplift: +77.9 bbl/d · +$369,225 over 90 days · Gas: 7.9999/8.0 MMscfd ✓** *(🟡 OUR-CODE — live Vizier API result; grep-verifiable in app.py)*

**The Edge-Safety Novel Piece:** If the WAN link drops mid-search (price spike, storm, satellite outage during a process upset), the LP-optimal local result is the approved output. The safety constraint holds. The optimization does not require a cloud round-trip to enforce the motor temperature limit. The **edge is the safety system.**

---

## Section 2 — The Value Architecture: Three Tiers, One Platform

This framework applies in all three persona narratives. The tier structure is the honest competitive framing (DEMO_MASTER §3 — LOCKED).

```
TIER 1 — SCADA (threshold alarms)
SCADA fires when an individual tag crosses a hard limit. It trips and shuts the well
in to protect the pump. It does not diagnose root cause. It does not say why.
GDC concedes this completely: SCADA protection is the foundation. GDC does not
compete at Tier 1 and does not claim "SCADA lets the pump die." It does not.

TIER 2 — ADVANCED APM (pattern detection)
Products: GE SmartSignal, AVEVA PRiSM, Aspen Mtell, SLB Lift IQ Edge (~5–15% of
Permian independents). These score the joint multivariate pattern drift across multiple
sensors and flag anomalies before individual thresholds are crossed.
GDC concedes L2 detection quality honestly: against threshold-only SCADA, XGBoost
provides a genuine pre-threshold edge. Against best-of-breed APM, detection quality
converges. The L2 moat is deployment simplicity (no legacy APM footprint required),
not detection quality superiority over elite APM.

TIER 3 — DOCUMENT CONTEXT FUSION (GDC's categorical moat)
No SCADA product and no current APM product reads unstructured field documents —
shift notes, workover reports, OEM manuals, lab results, vendor service logs,
completion records — in real time, as part of a live fault diagnosis.
That is the architectural gap. That is what H1, H2, and H3 all demonstrate closing.
```

> **The Honest-Footing Rule** (use when challenged with "but a human could figure this out"):
> *"Yes — a skilled engineer could reach this conclusion with the right documents and time, on a single well. What GDC does is make it automatic, fleet-scale, instant, cited, and inside your perimeter — turning a diagnosis that's possible in principle into one that happens every time in practice."*

---

## Section 3 — Persona 2: Product Context (FIRST NARRATIVE TO PRODUCE)

**Audience:** Halliburton operations managers, digital product managers, and solutions architects. The people who decide what capabilities to build, what to price, and how to position a digital services offering.

**The Core Question This Persona Is Answering:** *If Halliburton offers these capabilities and competitors do not, will it take market share? What are the capabilities, specifically?*

### The Narrative Spine

**Entry point:** The engineering problem is not new. Operators have always needed to know why a pump is struggling — not just that it is struggling. The constraint has always been the same: the answer lives in documents, not data streams.

**Tension:** Every major APM vendor (GE Vernova, AVEVA, Aspen Mtell, C3.ai, Cognite) is building the document-aware diagnostic layer. They are building it for cloud deployment. Their answer is to send the operational data to a cloud service.

**Resolution:** GDC delivers that same capability class — now, in production — inside the operator's sovereign perimeter. For the operators who cannot send their data to a public cloud (NOC-jurisdiction operators, IEC 62443 OT-compliance environments, data-residency law), this is not a preference. It is the only path that exists.

> *"The entire APM industry is building this. GDC delivers it now, inside the sovereign perimeter, on open weights."*
> *(Gemini neutral-search confirmed, Session AT — use this exact wording)*

### Capability Modules — What Halliburton Delivers

Frame each of these as a discrete, packageable capability:

**Capability 1: Pre-Threshold Anomaly Scoring (System A — CPU)**
- XGBoost health scoring (6 models per asset class), trained on real-or-representative operational trajectories
- Scores run locally, continuously, without cloud round-trip
- Detection fires before individual SCADA tags cross hard limits
- **Packaging angle:** Drop-in alongside existing SCADA, zero migration of existing alarm infrastructure

**Capability 2: Semantic Document Retrieval (System A — CPU)**
- SentenceTransformer `all-MiniLM-L6-v2` embeddings + AlloyDB pgvector (local)
- Retrieves operationally-relevant unstructured documents (shift notes, workover reports, lab results, vendor logs) in response to a live fault signal
- Runs entirely on CPU. No GPU required for document retrieval.
- **Packaging angle:** This is the categorical architectural differentiator — no current SCADA or APM product has this. It is CPU-resident, survivable, and does not require a network link.

**Capability 3: Differential Diagnosis Generation (System B — GPU/Gemma)**
- Gemma 4 via Ollama, on-premises GPU (NVIDIA L4)
- Reads retrieved documents → extracts structured findings → generates operator-language advisory with cited evidence
- Modulates confidence based on document specificity (emphatic/qualified/absent)
- **Packaging angle:** The advisory text cites its evidence sources. Auditable. Challengeable. Not a black box. *(Position against cloud LLM services where the "why" is opaque)*

**Capability 4: Human-in-the-Loop Approval Gate (HITL)**
- Every GDC-recommended action requires explicit RTOC operator approval before execution
- Action packages include cited evidence, alternative options, and risk language
- **Packaging angle:** This is the regulatory and risk management story. No autonomous actuation on safety-critical equipment. The operator remains accountable. GDC is a decision-support tool, not an autonomous agent.

**Capability 5: Pad-Level Field Optimization with Edge-Enforced Safety Constraints (H3)**
- Vertex AI Vizier GP Bandit (cloud) drives the multi-constraint optimization search
- Local XGBoost thermal model evaluates every candidate against the 280°F winding-temperature limit on-premise
- LP-optimal analytical baseline computed locally as both the transparent audit trail and the WAN-down fallback
- **Packaging angle:** Cloud handles the search. Edge holds the safety line. Even if the satellite link drops during a price spike, the motor protection constraint does not drop with it.

### Competitive Framing for Persona 2

| Competitor | What They Have Today | Where GDC Wins |
|---|---|---|
| SLB Lift IQ Edge | On-prem ESP monitoring, multivariate anomaly detection | No document-context RAG layer. Detection-only, no differential diagnosis. |
| GE SmartSignal / AVEVA PRiSM | Cloud APM, advanced multivariate ML, some GenAI roadmap items | Cloud-only egress. No sovereign on-prem RAG+LLM. Customer data leaves the perimeter. |
| Aspen Mtell | Trained failure-mode classification + recommended SOPs | Sensor-trained only. Cannot access unstructured field documents. SOPs are canned, not context-driven. |
| C3.ai (2026 roadmap) | "Virtual SME — full context, structured + unstructured" | Roadmap, not production. Cloud deployment. Data egress required. |

> **Competitive claim (Gemini neutral-search confirmed — use verbatim):**
> *"No native, production-ready commercial product combines real-time ML anomaly detection with LLM-based differential diagnosis over unstructured maintenance documents — as of 2025–2026, this is where all major APM platforms are heading. GDC delivers it now, inside the sovereign perimeter, on open weights."*

### Claim Guardrails for Persona 2

- **Do not claim Halliburton is the only path for sovereign on-prem.** SLB Lift IQ has on-prem components. Win on architectural design (RAG + LLM + edge safety constraint as an integrated stack), not exclusivity.
- **Do not claim APM misses all faults.** APM catches many faults correctly. Win on the specific class APM cannot reach: root-cause disambiguation that requires document context.
- **Do not claim GDC replaces SCADA.** GDC adds a diagnostic layer above it. Frame explicitly as complementary.
- **Cost figures (🔴 soft estimates):** Hot-oil truck roll ~$3k–$6k and pump-pull ~$70k–$100k are SME-confirmed directionally. Do not present them as hard contract prices. Add "verified with your field service vendor" qualifier.

---

## Section 4 — Persona 1A: Business Context (Operator)

**Audience:** E&P operator executives, production superintendents, VP Production, Chief Operating Officer. The people who own lifting costs as a P&L line item and who make capital allocation decisions on workovers.

**The Core Question This Persona Is Answering:** *Does this reduce my lifting costs, protect my production uptime, and reduce my workover spend? Is the ROI story real and defensible?*

### The Narrative Spine

**Entry point:** Lifting cost is one of the most controllable variables in oilfield economics — and also one of the least optimized. The workover schedule, the PM program, the operator response to a 2am alarm — these are all lifting-cost events. GDC automates the most expensive diagnostic step: determining the correct action in a time-constrained decision window, across every well simultaneously.

**Tension:** The people making these decisions are already overloaded. An RTOC at 2am manages 200+ alarms across a field. The information that would change the decision (the recent lab report, the overdue vendor PM, the shift note from three hours ago) is in a folder or a portal that no operator can consult in the 25-minute window before the decision becomes irreversible.

**Resolution:** GDC retrieves it automatically and surfaces it where the operator already lives — the SCADA terminal — in seconds, cited, ready for approval. The operator makes the better call. The $150k workover becomes a $3k hot-oil truck. The unnecessary shut-in becomes a production-preserving VFD trim.

### Operator-Specific Message Hierarchy

1. **Workover avoidance (H2):** The single highest-ROI message for operators. A single averted unnecessary pump pull more than justifies annual platform cost. The comparison: ~$70k–$100k pump-pull investigation avoided vs. ~$3k–$6k hot-oil truck roll. This is not a detection story — it is a root-cause disambiguation story.

2. **Production protection (H1):** Incorrect response to an ambiguous unloading event. VFD trim on a sand well causes pump seizure (~$150k workover). Conservative shut-in loses production (~$3k–$8k per event). GDC enables the correct, cheaper action by knowing the well's document history.

3. **Production uplift (H3):** Joint optimization across a pad under a gas ceiling constraint. +77.9 bbl/d of production currently deferred by uniform throttling. At current Permian crude prices, this represents ~$369,225 in additional revenue over 90 days — from production the pad is already physically capable of delivering.

4. **Scale without staffing:** The core economic argument. A senior production engineer can manually review one well with all documents in ~20 minutes. GDC does it in seconds, across the entire fleet, simultaneously, every alarm cycle. The staffing constraint that drives conservative default actions (shut-in everything uncertain) is removed.

### Key Claim Boundaries for Persona 1A

- **Do NOT cite the $150k / $3k cost pair as hard numbers without qualification.** These are OUR-CODE / NEEDS-EXPERT figures. Use: *"the difference between a $3,000 truck job and a six-figure workover."*
- **Lead time (H1) is 4–9 minutes, run-dependent.** Do not say "8 minutes" or "always before SCADA." Say: *"minutes before the SCADA alarm fires."*
- **Uplift figure (+77.9 bbl/d) is from this scenario's parameters.** Qualify it: *"In this scenario — parameters will vary by field."*
- **Do NOT say "GDC prevents every bad outcome."** GDC improves the probability of the correct diagnosis. The operator retains approval authority. HITL gate is always present.

---

## Section 5 — Persona 1B: Business Context (Halliburton)

**Audience:** Halliburton business development executives, service company GMs, digital services leadership. The people asking whether this creates a differentiated, defensible market position.

**The Core Question This Persona Is Answering:** *Does this platform allow Halliburton to take market share from competitors by giving E&P customers measurably lower operating costs — specifically lifting costs — in a way that competitors cannot match in the near term?*

### The Narrative Spine

**Entry point:** The APM market is consolidating around LLM-based, document-aware diagnosis. GE Vernova, AVEVA, Aspen Mtell, and C3.ai all have it on their 2025–2026 roadmap. They are building it for cloud deployment. The capability class is being validated by the entire industry. The question for Halliburton is not whether operators will want it. They will. The question is: who delivers it inside the sovereign perimeter, and who owns that relationship?

**Tension:** For the subset of operators who can use cloud APM services (public data egress allowed, stable connectivity), existing vendors have a multi-year head start. Halliburton's differentiated path is the operators who **cannot** use cloud services — national oil companies, IEC 62443-constrained production OT environments, operators in data-residency jurisdictions. This is not a niche. It is a strategically important and growing segment that current cloud APM vendors are architecturally excluded from serving.

**Resolution:** GDC delivers the same L3 document-aware diagnostic capability — now, in production, validated on Permian ESP scenarios — inside the sovereign boundary, on open-weight models, without requiring data egress. Halliburton wraps this in a field-services delivery model (well document ingestion, model fine-tuning, RTOC integration) that a cloud software vendor cannot replicate.

### Halliburton-Specific Message Hierarchy

1. **The beachhead market:** Sovereign operators (NOC jurisdiction, IEC 62443 OT, data-residency law) cannot send their operational data to a public cloud under any commercially available APM contract. GDC is architecturally designed for this market from the ground up. Competitors are not.

2. **The moat is architectural, not just contractual:** GDC uses open-weight Gemma on-premise hardware. Customer operational data — sensor readings, field documents, diagnostic queries — never passes through a third-party model provider's infrastructure and is never logged externally. This survives even the aggressive IP/data-governance challenge.

3. **Existing Halliburton relationships are the distribution channel:** Document ingestion (ESP pull records, completion reports, PVT analyses, vendor service logs) maps directly to data Halliburton already generates and holds on behalf of its customers. The RAG corpus is the field-service archive that Halliburton owns the relationship for.

4. **The competitive displacement story (ESP market):** SLB Lift IQ is the most direct competitor in the ESP digital services space. Lift IQ has on-prem components and strong ESP-specific data. The GDC differentiator is not detection quality — it is document-context RAG + LLM-based differential diagnosis, a layer that Lift IQ does not have in production today.

### Key Claim Boundaries for Persona 1B

- **Do NOT claim Halliburton is the only possible sovereign path.** Legacy on-prem APM deployments (SmartSignal/PRiSM on-prem) exist, though they lack the LLM/RAG layer. Win on the integrated stack, not on "only option."
- **Do NOT claim 5–15% APM penetration means the other 85% is uncontested.** Threshold-only SCADA operators are valid GDC customers, but they present a different sales motion (introduce APM + LLM together vs. displace existing APM). Distinguish the two segments.
- **The "capture market share" story is strongest at the sovereign segment, not the total addressable market.** Be specific about which segment you are displacing into.

---

## Section 6 — Persona 3: Deep Technical Context

**Audience:** Google Cloud / GDC solutions architects, Halliburton IT and OT engineers, field IT infrastructure leads. The people who will evaluate whether the architecture is sound, deployable, and maintainable.

**The Core Question This Persona Is Answering:** *With Google Cloud, GDC, and Gemini — can we build this better, easier, faster, and cheaper than any alternative?*

### The Narrative Spine

**Entry point:** The hard part of industrial edge AI is not the algorithm. It is the operational context: the system needs to know which documents are relevant to this asset at this moment, retrieve them instantly, and evaluate them against a live sensor signal — without any dependency on a network connection for the safety-critical path.

**Tension:** Traditional on-prem deployments of enterprise AI require complex build pipelines, bespoke model serving infrastructure, and fragile integrations between the unstructured data store and the real-time sensor layer. The result is usually a system that works in the lab and drifts in the field.

**Resolution:** Google Distributed Cloud provides the foundation that makes this buildable without reinventing the infrastructure. GKE on-prem means the same API surface engineers already know. AlloyDB Omni with pgvector means the RAG pipeline uses standard PostgreSQL semantics, no vector-database vendor lock-in, and survives on-premise without cloud connectivity. Gemma on Ollama means the LLM runs locally on commodity GPU with open weights, zero external API dependency, and no data egress.

### Technical Architecture — Honest Summary

| Layer | Technology | Where it runs | Key property |
|---|---|---|---|
| Telemetry ingest | RabbitMQ → event-processor | Edge (GKE) | Sub-second sensor ingestion; decoupled from ML inference |
| Health scoring (System A) | XGBoost `esp_health.ubj` (6 models) | Edge (GKE, CPU) | Pre-threshold anomaly detection; survives GPU-off |
| Document store (System A) | AlloyDB Omni + pgvector | Edge (GKE, CPU) | Local semantic search; no cloud round-trip; standard PostgreSQL API |
| Embeddings (System A) | `all-MiniLM-L6-v2` SentenceTransformer | Edge (GKE, CPU) | CPU-resident; document retrieval does not require GPU |
| LLM generation (System B) | Gemma 4 via Ollama | Edge (GKE, GPU — NVIDIA L4) | Open weights; zero API egress; GPU off by default in dev |
| Field optimization | Vertex AI Vizier (GP Bandit) | Cloud (parameter-only data) | Only Hz vectors and scores go to cloud; no telemetry egress |
| Safety constraint evaluation | `esp_thermal.ubj` XGBoost polynomial | Edge (GKE, CPU) | Evaluates motor thermal limit; does not require cloud round-trip |
| Human-in-the-Loop gate | Vue SPA HITL approval card | RTOC operator terminal | No autonomous actuation on safety-critical equipment |

### Why GDC Specifically (the "better/easier/faster/cheaper" proof points)

**Better:**
- AlloyDB Omni's pgvector implementation is Spanner-lineage code with production-hardened indexing, not a research vector DB. For a system that will hold thousands of ESP field documents and must serve semantic queries under operational latency constraints, this matters.
- Gemma open weights: the customer retains model sovereignty. If Google discontinues a model version, the customer's inference is not bricked. No API key. No external dependency chain.

**Easier:**
- GKE on GDC exposes the same Kubernetes control plane the team already knows. No new orchestration paradigm. `kubectl get pods -n gdc-pm` works exactly as it does in standard GKE.
- No build pipeline required in the UI layer. Vanilla HTML + JavaScript served by FastAPI. Vue via CDN. No webpack. No npm build step. The UI can be updated and redeployed in a single docker build.

**Faster:**
- AlloyDB Omni initializes schema from a ConfigMap-based init job. The entire field-document corpus can be re-seeded from Python with `ingest_manuals.py`. Disaster recovery is a re-pull and a re-seed, not a complex snapshot/restore cycle.
- The XGBoost models (`*.ubj`) are trained locally, versioned in the repo, and baked into the Docker image. Model updates are a `docker build` + `kubectl rollout restart`. No MLflow pipeline required.

**Cheaper:**
- GPU is scaled to zero by default. The Gemma LLM (System B) is brought up only when needed with `./scripts/gpu-start.sh`. System A (CPU) — health scoring, document retrieval, semantic embedding — runs continuously at no GPU cost. The separation of System A and System B is a deliberate cost-architecture decision, not a limitation.
- AlloyDB Omni runs as a standard Kubernetes pod. No AlloyDB Cloud instance billing. The pgvector search runs inside the cluster.

### Technical Claim Guardrails for Persona 3

- **Do NOT claim Gemma outperforms GPT-4 / Gemini Pro for this task.** Gemma's role is extraction and summarization from retrieved documents. It is not evaluated against proprietary models. The value is deployment flexibility and data sovereignty, not raw capability.
- **Do NOT claim RMSE=0.00185 proves production-grade accuracy.** It is the retrain RMSE on our synthetic training set. It demonstrates that the model correctly learns the intended trajectory, not that it generalizes to all Permian ESP wells. Be precise.
- **Do NOT claim "no cloud dependency."** Vertex AI Vizier (H3) makes cloud API calls. The honest claim: *"No public-cloud dependency for the safety decision — the thermal constraint and the approved setpoint both run on-premise."*
- **GPU cost billing starts at `gpu-start.sh`.** Always pair with `gpu-stop.sh`. Approximately $0.65/hr at NVIDIA L4 pricing. Never leave GPU scaled up between sessions.

---

## Section 7 — Veo Intro Segments — Guidance Per Persona

Each video begins with a Veo-generated visual intro that establishes context before the demo walkthrough begins. These are NOT documentary footage — they are stylized, impressionistic visualizations. The physical scenarios are accurate; the presentation is cinematic.

### Persona 1 Intro (Business Context — Operator + Halliburton)

**Visual theme:** Nighttime Permian field. RTOC operator at a terminal. Pump alarms firing. The human scale of the problem — one person, two hundred wells, one critical window.

**Core Veo prompt guidance:**
- Dark, high-contrast industrial aesthetic. Blue/amber ISA-101-style HMI light on operator's face.
- Close-up: pump intake sensor readings declining on screen. Medium shot: operator scanning multiple windows simultaneously.
- No cartoon failure. No explosion. The drama is the decision under time pressure, not the failure itself.
- **Voice hook:** *"When an alarm fires at 2am, the difference between a $3,000 truck job and a six-figure workover is in a document no one has time to read."*

### Persona 2 Intro (Product / Operations Manager Context)

**Visual theme:** The product architecture in motion. Data flows from wellhead to RTOC terminal. Documents emerging from folders, being read and synthesized. The product view — layers, interfaces, outputs.

**Core Veo prompt guidance:**
- Technical but accessible. Show data flow, not code.
- Wellhead → sensor signal → RTOC screen. Separately: document folder → RAG retrieval → structured advisory.
- The convergence: sensor signal + document context = one cited verdict on an operator's screen.
- **Voice hook:** *"Halliburton's customers need three capabilities the competition doesn't offer yet. Here is what they look like in production."*

### Persona 3 Intro (Deep Technical Context)

**Visual theme:** The stack in motion. GKE pods, Kubernetes architecture, local inference. The Google Cloud / GDC infrastructure layer beneath the application.

**Core Veo prompt guidance:**
- Stylized infrastructure visualization. Not a slide screenshot — an architectural animation.
- Emphasize the edge/cloud split: local inference node (warmer, copper tones) + cloud optimizer call (cooler, blue tones) with a deliberate WAN link that can be shown breaking and recovering.
- **Voice hook:** *"With GDC, Gemma, and AlloyDB Omni — the same AI capability class the cloud vendors are building for 2026 runs on-premise today, on open weights, without sending a byte of operational data to a public cloud service."*

---

## Section 8 — Red-Team Boundaries (Mandatory for All Personas)

Every claim in every video must pass the following gates before appearing on screen. These are not guidelines; they are blocking conditions.

### Claims That Are Permanently Blocked (Do Not Use)

| ❌ Blocked Claim | Why Blocked |
|---|---|
| "GDC detects faults before SCADA" (unqualified) | Against best-of-breed APM, detection converges. Against advanced SCADA with rate-of-change rules, may be marginal. Qualified claim: "before the SCADA hard-limit alarm fires, by 4–9 minutes on this scenario." |
| "SCADA lets the pump die" | SCADA trips and shuts the well in to protect the pump. This statement is a straw man. |
| "Flush and reseal in place" for downhole ESP protector | Physically impossible. Correcting a downhole ESP protector requires pulling the completion. Always. (Gate 5 failure — Session BE) |
| "Halliburton is the only sovereign path" | SLB Lift IQ has on-prem components. Legacy APM vendors have on-prem options. Win on integrated stack, not exclusivity. |
| "No cloud dependency" (unqualified) | Vertex AI Vizier (H3) uses cloud for GP Bandit search. Qualified: "No public-cloud dependency for the safety decision." |
| "GDC autonomously controls the equipment" | HITL gate is always present. Operator approves every action. GDC is decision-support, not autonomous control. |
| VFD trim as "always safe" (without qualifying sand status) | VFD trim during fluid drawdown in a sand well causes pump seizure. Context-dependent. |

### The Physics Constraints That Must Hold in All H1 References

- **PIP and Motor Amps are LEADING indicators** — they decline from the onset of the unloading event.
- **Winding Temperature and Vibration are LAGGING indicators** — they remain near-nominal through the entire GDC detection window (first ~55% of the replay sequence), then rise gradually but stay below SCADA trip thresholds throughout. Both remain GREEN throughout the decision window.
- API RP 11S §4.2: thermal mass delays winding-temperature rise; cavitation onset is mild until high Gas Volume Fraction.
- The model (`esp_health.ubj`, retrained BS+25) scores on PIP/Amps leading decline. Temp/Vib lagging behavior is correct physics and confirmed by retrain verification.

---

*For full specification of each scenario: `docs/DEMO_MASTER.md`. For verified claim register: `docs/CLAIM_LEDGER.md`. For hostile-engineer red-team history: `docs/RED_TEAM_LEDGER.md`. For operational state and deployment commands: `docs/NEXT_SESSION_PROMPT.md`.*
