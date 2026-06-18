# GDC Edge AI Demo — Challenged & Refined Narrative Guidance (Gemini Perspective)
**Created:** Session BS+28 (June 18, 2026)  
**File Path:** `/home/brian/gdc-pm/docs/NARRATIVE_GUIDANCE_GEMINI.md`  
**Purpose:** A deeply challenged, red-teamed, and intellectually hardened iteration of the narrative guidance. This document adopts an adversarial "hostile-engineer" persona to expose vulnerabilities in the standard marketing story, refine our claims to be unassailable, and provide updated, bulletproof guidance for the three video personas.  
**Primary Persona Focus:** Persona 2 (Product / Operations Context) & Persona 3 (Deep Technical Context).

---

## Section 1 — The Hostile Red-Team Audit (Challenge Phase)

Before drawing a single pixel or recording a single line of narration for our videos, every core scenario claim must survive the scrutiny of a skeptical, 20-year O&G production and ESP reliability engineer. Below is the adversarial red-team audit of the standard demo narrative.

### H1 (Discern) Red-Team Challenge

> **Hostile Attack:** *"You claim SCADA is blind to unloading events and GDC is the savior. That's a classic straw man. Every modern VFD/SCADA system has underload torque and current limits that trip the pump offline in seconds to protect it. You're not saving a pump from dying; SCADA already does that by shutting it down. Furthermore, you claim a morning shift note has high-fidelity 'casing gas' or 'sand history' data. In reality, GOR is measured at the test separator once a month, and shift notes are notoriously low-fidelity. How does an operator trust a local LLM reading sloppy text to make a safety-critical speed-down decision?"*

#### The "Survives-If-Reworded" Refinement
1. **SCADA Concession:** We must explicitly concede that SCADA protects the pump. SCADA does *not* let the pump burn out; it trips on underload to protect it. GDC's value is **production continuity vs. reactive shut-in**.
2. **The Ambiguity Moat:** After SCADA trips (or when the telemetry begins to slide toward the trip limit), the operator has an ambiguous situation: Is this a transient gas pocket (which can be cleared by slowing the pump down, keeping the well online and saving ~$3k–$8k in restart/deferred costs) or is it a depleted reservoir with sand bridging risk (where running the pump slower is catastrophic, and a shut-in is mandatory)?
3. **The Document Integrity:** The GDC pgvector RAG does not treat the shift note as an absolute arbiter of reservoir physics. Instead, it treats the shift note and sonic survey as **contextual corroboration**. The Bayesian math combines these unstructured clues with live telemetry to generate a *probabilistic score*, not a deterministic directive.
4. **The Video Guidance:** Narrations must never say *"SCADA fails to protect the asset."* They must say: *"SCADA trips to protect the pump, leaving the operator with a blind choice between an unnecessary shut-in and a catastrophic sand seizure. GDC resolves the blind choice before the well is shut in."*

---

### H2 (Classify) Red-Team Challenge

> **Hostile Attack:** *"You claim an overdue paraffin PM log proves the pump's vibration is just wax, not bearing wear. That's a dangerous double-fault risk. What if the pump has genuine mechanical bearing wear AND the hot-oil job is overdue? If your 'GDC Advisor' tells an operator 'Do not pull' because of a service log, and the shaft snaps because the bearings were actually shot, you've just caused a catastrophic downhole failure. No sane operator is going to risk a $100k completion because an LLM read an overdue maintenance date."*

#### The "Survives-If-Reworded" Refinement
1. **The Double-Fault Mitigation:** GDC does not rely on a single document. It conducts a **differential diagnosis** by cross-referencing *multiple* siloed data sources.
2. **The Causal Chain:**
   - Document A (Chemical Service Log) proves the treatment is **52 days overdue** on a formation known for high wax (WAT 118°F). This establishes a high *prior probability* for paraffin restriction.
   - Document B (Prior Pull Record) shows the pump bearings were inspected and found **normal only 18 months ago** (on an ESP lifecycle of 2–3 years). This lowers the prior probability of premature bearing wear.
   - Live Telemetry (PIP stable/rising while amps rise and efficiency falls) is **physically consistent with hydraulic restriction** (tubing backpressure), whereas bearing wear typically exhibits stable system curves with fluctuating, spikey PIP and rapid temperature spikes.
3. **The Operator Role:** GDC is an *Advisor*, not an autonomous actor. It presents the *cited evidence* to the human operator (Human-in-the-Loop gate) who makes the final call based on the combined physical and documentary evidence.
4. **The Video Guidance:** Emphasize that GDC *combines* physics and history: *"GDC doesn't just look at the schedule delay. It cross-references the 18-month bearing inspection record, matches the telemetry against restriction hydraulics, and presents an auditable, cited differential case to the engineer."*

---

### H3 (Optimize) Red-Team Challenge

> **Hostile Attack:** *"You call this 'edge-cloud collaboration' where Vizier optimizes and the edge enforces. But if the satellite link drops, your GP Bandit is dead. If you fall back to a local linear LP (gas-only), you've lost the non-linear thermal and RUL optimization. You're just running a basic fallback recipe. You can't claim continuous optimization when your primary optimizer is offline."*

#### The "Survives-If-Reworded" Refinement
1. **The Edge Autonomy:** Concede that the GP Bandit search requires the WAN link. If the satellite link drops, *active exploration* halts.
2. **The Edge Safety Shield:** The core claim is that **the safety constraint remains local**. In traditional cloud-only systems, if the WAN drops, the control setpoint could drift, or the safety loop must drop to a highly conservative baseline. With GDC, the local XGBoost thermal model (`esp_thermal.ubj`) continues to run on-premise at 100% availability. It acts as an autonomous guardrail that continues to enforce the derated 280°F limit even if the cloud goes dark.
3. **The Video Guidance:** Frame the H3 value around **sovereign safety enforcement** rather than "uninterrupted cloud optimization." Use the phrasing: *"The cloud searches for the next dollar of margin; the edge holds the safety line. If the link goes dark, the edge maintains the current optimal setpoint and continues local safety enforcement, offline and uninterrupted."*

---

## Section 2 — Refined Narrative Guidance for the Three Personas

Adopting our challenged and hardened perspective, we now refine the core focus and messaging hierarchy for each video walkthrough.

```
                  THE CORE NARRATIVE SPECTRUM
                  
   PERSONA 1: BUSINESS                PERSONA 2: PRODUCT             PERSONA 3: DEEP TECH
┌─────────────────────────┐        ┌────────────────────────┐     ┌────────────────────────┐
│ Focus: ROI, OPEX,       │        │ Focus: Capabilities,   │     │ Focus: Architecture,   │
│ Production Continuity,  │        │ Productization, Moat,  │     │ GKE, pgvector, local   │
│ Capital Preservation.   │        │ Deployment, packaging. │     │ inference, MLOps, RAG. │
│ "Continuous runtime    │        │ "How Halliburton sells │     │ "Built better, easier, │
│ at fleet scale."        │        │ unassailable edge-AI." │     │ faster, and cheaper."  │
└─────────────────────────┘        └────────────────────────┘     └────────────────────────┘
```

---

### Persona 1: Business Context (Operator & Halliburton Business)

This video must establish GDC as an OPEX-shrinking, revenue-protecting asset. It is a conversation about **risk management and margin preservation**.

#### The Refining Principles (Operator View)
- **Ditch the Binary $150k/$3k Hype:** Skeptical CFOs know that not every bad trim results in a seized pump, and hot-oil flushes aren't always $3k. Instead, frame the argument around **fleet-scale probability and capital protection**.
- **Focus on Operational Leverage:** Emphasize that GDC does not require hiring more engineers. It takes the rare, expensive diagnostic expertise of a senior production engineer and automates it across hundreds of wells, 24/7.
- **The Continuity Theme:** SCADA protects the pump by shutting it in. GDC protects the P&L by keeping it running safely.

#### The Refining Principles (Halliburton Business View)
- **Contract Defense:** Service companies survive on long-term artificial lift contracts. A provider that can guarantee lower customer lifting costs and zero unnecessary pump pulls owns the market.
- **Differentiated Software Margin:** Standard hardware services are heavily commoditized. Delivering a high-margin, sovereign edge-AI software platform on top of existing ESP contracts is Halliburton's highest leverage path to capturing market share from SLB (Lift IQ) and Baker Hughes.

---

### Persona 2: Product Context (Operations & Product Managers)
*Note: This is the first narrative slated for production. The following guidance must be followed verbatim.*

This video must explain **the productization of the GDC Edge AI platform**. It must show how Halliburton packages, deploys, and monetizes these advanced capabilities.

#### The Strategic Spine
Product Managers do not sell raw tech; they sell **packaged business outcomes**. The narrative must show how the underlying architecture is translated into an unassailable product offering:

```
        ┌────────────────────────────────────────────────────────┐
        │                 THE PACKAGED PRODUCT                   │
        ├────────────────────────────────────────────────────────┤
        │ 1. Continuous Telemetry Monitoring (Local XGBoost)     │
        │ 2. Automated Event-Driven Semantic RAG (AlloyDB Omni)  │
        │ 3. Sovereign Differential Diagnosis (Gemma 4 Edge LLM)  │
        │ 4. Human-In-The-Loop Approval Interface (FastAPI UI)   │
        └────────────────────────────────────────────────────────┘
```

#### Key Capability Packaging Guidance for the Video

1. **Capability 1: Local Pre-Threshold Anomaly Detection (System A)**
   - *Video Focus:* Show the XGBoost model running locally on GDC GKE. It monitors joint multivariate drift (correlated PIP/Amps decline) and crosses a 0.87 probability threshold before SCADA hard limits are reached.
   - *Product Value:* This is packaged as a "non-intrusive overlay." It installs alongside the customer's existing SCADA network without requiring telemetry migration.

2. **Capability 2: Automated On-Premise Document Fusion (System A)**
   - *Video Focus:* The moment the pre-threshold alarm fires, GDC automatically triggers local semantic retrieval (AlloyDB Omni + pgvector). It searches the private, on-prem well dossier (shift notes, labs, pull reports).
   - *Product Value:* This is "Zero Data Egress RAG." It operates locally on standard CPU hardware. It does not require a cloud connection or expensive GPU nodes to retrieve the critical context.

3. **Capability 3: Sovereign Generative Advisories (System B)**
   - *Video Focus:* Gemma 4 (local GPU) reads the retrieved documents and extracts structured findings, modulates confidence, and generates the cited operator-language advisory.
   - *Product Value:* "Auditable AI." Every recommendation has a clickable source citation linking to the specific lines of the retrieved shift note, lab analysis, or workover report. The AI is accountable and challengeable.

4. **Capability 4: The Edge Safety optimization (H3)**
   - *Video Focus:* Show the division of labor between cloud search (Vizier) and edge enforcement (XGBoost safety polynomial).
   - *Product Value:* "Autonomous Local Safety." The product guarantees that even if Starlink drops, the motor winding temperature safety limits (280°F) are enforced locally on GDC, without delay or cloud dependency.

---

### Persona 3: Deep Technical Context (Architects & Engineers)

This video is purely a technical discussion. It must prove that GDC + Google Cloud + Gemini make building and running sovereign edge-AI **better, easier, faster, and cheaper** than custom-built legacy alternatives.

#### The "Better, Easier, Faster, Cheaper" Technical Proof Points

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           THE TECHNICAL PROOF                            │
├──────────────────┬──────────────────┬──────────────────┬─────────────────┤
│      BETTER      │      EASIER      │      FASTER      │     CHEAPER     │
├──────────────────┼──────────────────┼──────────────────┼─────────────────┤
│ AlloyDB Omni with│ Standard GKE     │ Ingest & Seed    │ Separation of   │
│ pgvector RAG.    │ Control Plane.   │ Python pipeline. │ System A (CPU)  │
│ Runs on-premise  │ Familiar tooling │ Local UBJ models │ and System B    │
│ standard Postgres│ (kubectl) and    │ baked in image.  │ (GPU). GPU off  │
│ semantics.       │ container APIs.  │ 10-sec deployment│ by default.     │
└──────────────────┴──────────────────┴──────────────────┴─────────────────┘
```

1. **Better (PostgreSQL + pgvector on AlloyDB Omni):**
   - *The Claim:* Traditional edge RAG requires bespoke, specialized vector databases that are difficult to manage and scale on-premises.
   - *The GDC Advantage:* GDC runs AlloyDB Omni with pgvector. The entire RAG pipeline is managed using standard, production-hardened PostgreSQL semantics. Engineers write standard SQL queries with vector operators.
   - *Offline Survival:* Because the database and pgvector search run locally inside GKE, the retrieval loop is fully functional when disconnected from the WAN.

2. **Easier (Unified GKE Control Plane):**
   - *The Claim:* Building and deploying edge applications typically means managing complex, custom Linux edge agents or specialized IoT runtimes.
   - *The GDC Advantage:* GDC exposes a native GKE interface. Deploying the telemetry simulator, event processor, database, and inference API is as simple as managing standard Kubernetes manifests. Tooling is unified: `kubectl rollout restart` is our deployment pipeline.

3. **Faster (Local Model Ingestion and Zero-Build UI):**
   - *The Claim:* UI deployment and model serving in enterprise OT environments usually require complex build servers, webpack pipelines, and MLflow serving layers.
   - *The GDC Advantage:* The XGBoost models (`.ubj`) are baked directly into the FastAPI Docker image. The frontend uses a vanilla HTML/JS stack served by FastAPI (Vue via CDN, zero build steps). A UI change is a 10-second Docker build and a GKE rollout.

4. **Cheaper (GPU Discipline and System Isolation):**
   - *The Claim:* Running continuous LLM inference at the edge is prohibitively expensive because it requires dedicated, high-performance GPU nodes running 24/7.
   - *The GDC Advantage:* We isolate the architecture into two tiers:
     - **System A (Continuous, CPU-Only):** Telemetry ingestion, health scoring, AlloyDB RAG, and SentenceTransformer embedding run continuously on standard, low-cost CPU nodes.
     - **System B (On-Demand, GPU-Only):** The Gemma LLM (Ollama) is scaled to zero and brought up only when a differential advisory is requested or a recording session is active (`./scripts/gpu-start.sh`). This dramatically reduces the edge hardware cost profile.

---

## Section 3 — Refined Video Script Corrections & Sourcing

To ensure our video production script (`docs/VIDEO_SCRIPT.md`) is completely aligned with these red-teamed and refined perspectives, we must apply the following specific corrections to the script file.

### Required Script Updates (Minimal Diff & Sourced to Code)

1. **H1 Panel Count & Names:**
   - Ensure the script reflects 5 slides (not 6) in the H1 deck, matching `h1.html` verbatim.
   - Panel names in script must be updated:
     - Slide 1: THE SCENARIO — *"Same Signal. Two Causes. One Right Decision."*
     - Slide 2: AMBIGUOUS TELEMETRY — *"One Signature, Two Physical Realities"*
     - Slide 3: DECISION SUPPORT — *"Motor Burnout vs. Sand Bridging"*
     - Slide 4: ADDING CONTEXT — *"Fusing Telemetry and Unstructured Well History"*
     - Slide 5: INDUSTRIAL APPLICATION — *"Solving the Edge Context Gap — At Scale"*

2. **H1 Empirical Detection Indices:**
   - Correct the stale hardcoded index references in the script to reflect the dynamic, run-dependent reality established by `HEALTH_THRESHOLD=0.87` (BS+26).
   - `gdc_detect_idx` stale `33` $\rightarrow$ `35–46 (run-dependent)`
   - `alarm_idx` stale `60` $\rightarrow$ `55–73 (run-dependent)`
   - Change narration language: *"twenty-seven data points after GDC"* $\rightarrow$ *"4–9 minutes before the SCADA alarm fires"*.

3. **H1 Walkthrough Scrubber Phrasing:**
   - Replace *"Advance scrubber to t=30 (pre-detection zone)"* $\rightarrow$ *"Advance scrubber slowly into the pre-detection zone"*.
   - Replace *"GDC detects the anomaly here — at index thirty-three"* $\rightarrow$ *"GDC detects the anomaly here — the amber GDC detect marker fires"*.
   - Replace *"SCADA fires its alarm here — at index sixty"* $\rightarrow$ *"SCADA fires its alarm here — the red SCADA alarm marker fires, 4–9 minutes after GDC already had context"*.

4. **H1 Physics — Lagging Temp/Vib:**
   - Add this note to Slide 2/3 panel narration: *"Notice: winding temperature and vibration stay near-nominal through this entire detection window — they are lagging indicators. Only pump intake pressure and motor amps decline. SCADA's thermal and vibration trip thresholds never cross in the decision window. The ambiguity is precisely why the early window matters."*

5. **H2 Vibration Units Correction:**
   - **Critical Physics Fix:** The script currently says *"Vibration rising — from 0.15 to 0.38 inches per second RMS"*. This uses incorrect units (in/s). The active code in `app.py` uses metric millimeters per second (`mm/s`) with `vib_nom=0.9–1.2 mm/s`, `vib_end=4.2–4.9 mm/s`, and ISA-18.2 High alarm at 4.0 mm/s.
   - Update script narration to: *"Vibration rising — from nominally 1.0 to 4.5 millimeters per second RMS, crossing the ISA-18.2 High alarm threshold at 4.0 mm/s"*.

6. **Integrity Tables at Bottom of Script:**
   - Update the `Integrity Gate Table` and `Screen Flow Summary` rows for Horizon 1 to reflect 5 slides (not 6) and the dynamic run-dependent indices.

---

*For full implementation steps to apply these script corrections directly to `docs/VIDEO_SCRIPT.md`, see the NEXT_SESSION_PROMPT.md Priority 1 checklist.*
