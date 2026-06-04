# GDC Edge AI Demo — Situation Brief for External Review
**Date:** June 4, 2026  
**Purpose:** Comprehensive briefing document for use with external AI models to obtain a fresh perspective on visual design, demo flow, and bug remediation.  
**Audience:** AI assistant being asked to propose a better demo plan.

---

## PART 1: WHAT WE ARE BUILDING AND WHY

### The Product
GDC Edge AI is a predictive maintenance platform for upstream oil & gas operations. It runs entirely on-premises (no cloud dependency during field operations) on a Google Distributed Cloud (GDC) edge cluster. The platform demonstrates that an AI stack — XGBoost health models, a vector database (AlloyDB Omni with pgvector), a local LLM (Gemma 4 on NVIDIA L4 GPU), and a RabbitMQ message broker — can detect equipment failures earlier, more accurately, and with richer context than SCADA threshold monitoring alone.

### The Core Value Proposition
SCADA systems (the industry standard: OSIsoft PI, Ignition, Wonderware) monitor sensors against hard thresholds. They alarm when a value crosses a limit. They cannot:
- Distinguish between failure modes that produce similar sensor signatures
- Output a probability score before any threshold is crossed
- Cross-reference an unstructured shift note or lab report against sensor trends

GDC claims to do all three. The demo must prove these three claims visually and compellingly in under 5 minutes to a business audience (not engineers).

### The Three-Act Structure

| Act | Tab Name | Scenario | Asset | Core Claim |
|-----|----------|----------|-------|------------|
| H1 | Detect | Gas Lock on an ESP pump | ESP-ALPHA-1 | GDC detects 25 min before SCADA alarms → $0 fix instead of $150k pump pull |
| H2 | Discern | Slug Flow false alarm on ESP | ESP-ALPHA-3 | GDC prevents unnecessary $150k pump pull — vibration alarm is surface issue, not downhole |
| H3 | Optimize | VFD frequency optimization | ESP-ALPHA-1 | GDC doesn't just protect — it maximizes production: +$1.2M over 90 days |

### The Technology Stack (All Real, Production-Grade)
- **XGBoost health models** — trained on physics-accurate simulated sensor data, saved as `.ubj` files, loaded and serving predictions in-cluster
- **AlloyDB Omni** — PostgreSQL + pgvector, stores telemetry events, field intelligence documents, and RAG document embeddings
- **Gemma 4 (gemma4:latest)** — local LLM on NVIDIA L4 GPU, generates field intelligence documents and streams diagnostic assessments
- **RabbitMQ** — durable message broker connecting the telemetry simulator to the event processor
- **Vertex AI Vizier** — Google Cloud Bayesian optimization service used in H3 (the one cloud dependency, intentional)
- **Telemetry Simulator** — generates physics-accurate sensor data for ESP, Gas Lift, Mud Pump, and Top Drive assets
- **Event Processor** — consumes RabbitMQ messages, runs XGBoost classification on each telemetry event, writes results to AlloyDB

---

## PART 2: INTENDED DEMO FLOW (H1 IN DETAIL)

### Pre-Injection State (Nominal Monitoring)
The Detect tab opens showing a live monitoring dashboard. The system is watching ESP-ALPHA-1. All sensors are nominal:
- PIP (pump intake pressure): ~1,400 PSI
- Motor current: ~75 Amps  
- Motor winding temperature: ~198°F
- Vibration: ~0.8 mm/s

The **Dual-Reality Bar** at the top shows:
- LEFT: "SCADA · ESP-ALPHA-1: 4 signals — All Nominal · No alarm"
- RIGHT: "GDC AI · ESP-ALPHA-1: GAS LOCK — 94% confidence" (chips: Shift note, Lab GOR↑, VFD events, API RP 11S)

The **Primary Chart** ("Minutes Until Pump Failure") shows three lines all flat at 120 minutes — the system is in nominal state, no fault projected.

The **GDC Advisor** panel says: *"Monitoring ESP-ALPHA-1. All sensors nominal. Ready to analyze downhole anomalies."*

The **Intelligence Feed** shows recent field documents (shift logs, routine tests).

### Post-Injection State (Fault Active)
Operator clicks "Inject Gas Lock." The following should happen:

1. **Sensor data changes** — The telemetry simulator begins generating gas-lock fault patterns:
   - PIP declines (pump losing suction as GVF increases)
   - Motor amps decline (pump unloading on gas void)
   - Motor temperature rises (loss of cooling fluid flow through motor annulus)
   - The GDC-AI side of the dual-reality bar shows GAS LOCK 94%

2. **Primary chart** — The three lines begin diverging:
   - Gray line (SCADA threshold monitoring): **stays at 120** — honestly, SCADA hasn't alarmed
   - Orange dashed line (GDC sensor-only XGBoost): **starts declining** toward zero as the model detects the fault pattern
   - Solid orange line (GDC context-fused): **declines faster** than sensor-only after RAG documents are retrieved — the gap between lines 2 and 3 is labeled "⚡ Context Fusion: −Nm"

3. **SCADA secondary chart** — Shows the 4 raw sensors (PIP, Amps, Temp, Vib) normalized to % change from baseline. PIP and Amps should decline together (orange). Temp and Vib stay flat (blue/grey). This visually proves "SCADA can see these sensors too — but hasn't crossed a threshold."

4. **GDC Advisor** — Auto-starts streaming a diagnosis: *"Gas lock confirmed at 94% confidence. PIP declining at X PSI/min, motor amps declining at Y A/min. Five independent sources converge: [shift note, lab GOR test, VFD events, sensor telemetry, API RP 11S]. Your $0 option expires in 10 minutes."*

5. **Intelligence feed** — New AI-generated field documents appear every 15-30 seconds with a "⚡ GDC AI — just now" badge. Each new document reflects the current (evolving) fault state. The LLM updates its assessment when counterargument documents appear.

6. **Well strip (CSS instrument panel, far right)** — Shows animated fluid column turning amber/orange, pump status changing, motor temperature rising, GVF% bar increasing.

7. **Window of Options** — Three intervention cards appear:
   - $0 — VFD 52→44 Hz — VIABLE (clock counting down)
   - ~$2,000 — Emergency shutdown + restart — VIABLE
   - $150,000 — Well pull + pump replacement — POST-PNR ONLY

8. **Operator approves VFD speed-down** — Charts animate recovery: PIP climbs, amps stabilize, motor temperature drops. Advisor confirms: *"Recovery on track."*

### The Business Punchline
"25 minutes of warning. Zero dollars. Pump preserved. Without GDC: SCADA alarms when the motor is already damaged. Only option left: $150,000 pull."

---

## PART 3: CURRENT BROKEN STATE — SPECIFIC BUGS

### Bug 1: Primary Chart Shows Flat Line After Fault Injection
**What we see:** After clicking "Inject Gas Lock," the "Minutes Until Failure" chart shows a flat horizontal line at approximately 16-20 minutes. It doesn't decline over time.

**Why it's broken:** The API endpoint `/api/plot/forecast-data/ESP-ALPHA-1` is being polled by the frontend, but the returned `time_to_scada_minutes` and `adjusted_rul_minutes` values appear stable at ~16 minutes. The frontend accumulates these into a `h1RulHistory[]` array to draw a rolling time-series, but the values aren't changing between polls, so the "chart" is just a flat line at whatever the current prediction is. 

The deeper issue: the XGBoost health model is converting its output (a health score of 0.65) into a time estimate via a formula. If the health score doesn't change much between polls, the time estimate doesn't change. The chart needs to show *declining minutes* over *elapsed demo time*, not just the instantaneous model output.

**API response right now (with fault apparently still active from a prior session):**
```
time_to_scada_minutes: 16.1
adjusted_rul_minutes: 16.1  ← SAME as time_to_scada, no context fusion gap
health_score: 0.6568
fault_active: None  ← NULL even though sensors show fault patterns
slopes: dpsi_dt: 27.587, dtemp_dt: 9.007, dvib_dt: 0.262, ds4_dt: -2.855
```

**Key integrity violation:** `adjusted_rul_minutes == time_to_scada_minutes`. The context fusion multiplier (`adjust_rul_with_documents()`) is not producing any delta. Either no matching documents are being retrieved, or the function is not being reached. The entire "context fusion is better" visual argument depends on these two lines diverging.

### Bug 2: Health Score is 0.65 in "Nominal" State  
**What we see:** Even without a fault injected, the health model returns `health_score: 0.6568` — which the system interprets as "65% healthy," i.e., already degraded. A clean nominal ESP should score close to 1.0.

**Why it's broken:** The telemetry simulator may be generating sensor values that the model interprets as mildly degraded. The model was trained on physics-accurate data, but the live simulator's nominal operating point may not match the training distribution exactly. Alternatively, the `_intel_generator` background thread is writing documents that contain GVF > 70% (which the code explicitly seeds at `random.randint(71, 85)` — see line 187 of app.py), which may be triggering fault-state classification even when no fault has been injected.

### Bug 3: SCADA Chart Shows All Sensors Flat (No Divergence)
**What we see:** After injection, the 4-sensor normalized SCADA chart shows all 4 sensors (PIP, Amps, Temp, Vib) near zero percent change. They don't diverge.

**Why it's broken:** The chart normalizes sensors to "% Δ from initial baseline value." The baseline is captured when the chart first renders. If the fault injection changes the DB rows but the chart's cached baseline was set at a high-PIP moment, and the current values haven't moved much relative to that baseline, the % change will be small. The chart may also be showing correctly (sensors ARE within SCADA thresholds) but the visual effect of a flat chart directly contradicts the "PIP and Amps declining together" story we're trying to tell.

### Bug 4: Intelligence Feed Not Updating
**What we see:** The intelligence feed shows documents from "58 ago", "1d ago", "1d ago" — no new documents are appearing during the active fault.

**Why it's broken:** The `_intel_generator` background thread runs in app.py every 20-30 seconds and is supposed to generate new Gemma-authored field intel documents when a fault is active. The frontend polls for new documents every 15 seconds via `h1FeedPollInterval`. The feed items not updating suggests either: (a) the background thread stopped running, (b) the thread is running but not writing to the DB, or (c) the frontend poll is not fetching new items or not re-rendering when it does.

The fact that `field_intel` has only 86 rows (vs expected 99-110) after multiple sessions suggests the generator may have been running for a while but stopped.

### Bug 5: GDC Advisor Fires Once, Then Stops
**What we see:** The Advisor streams one response on fault injection, then goes silent. There is no "continuing assessment" as the fault evolves. No mention of which specific documents changed the RUL estimate.

**Why it's broken:** The Advisor is triggered once by `_startAdvisorStream()` on the inject button click. There is no mechanism to re-trigger the Advisor when:
- New intelligence documents arrive
- The model's RUL estimate changes significantly
- The context-fused estimate diverges from the sensor-only estimate

The intended behavior is that the Advisor should update its assessment when the context fusion produces a new delta — specifically saying something like: *"A new lab report just retrieved by RAG shows GOR at 1,310 scf/bbl — this is consistent with gas migration. My context-fused estimate is now 18 minutes, down from sensor-only estimate of 24 minutes."*

### Bug 6: No Visual Differentiation Between SCADA and GDC Assessment
**What we see:** The Dual-Reality Bar at top shows "GAS LOCK — 94% confidence" from GDC — but this is static text, not driven by the model's actual real-time output. Meanwhile the sensor chart shows nothing alarming.

**Why it's a problem:** If an audience member asks "how does the AI know it's gas lock?" the answer should be visible: the model just ran on those sensor slopes and produced 94% confidence. But visually, the chart shows sensors barely moving, the RUL line is flat, and the Advisor has gone quiet. The entire live-inference narrative has collapsed.

---

## PART 4: ROOT CAUSE ANALYSIS

### The Fundamental Architecture Problem
The demo has accumulated **two layers of complexity** that are fighting each other:

**Layer 1 — Real XGBoost model on real DB data:**  
The `esp_health.ubj` model runs against `telemetry_events` rows from AlloyDB. It produces a continuous health score. This is real. But the model was trained on specific sensor feature distributions, and if the simulator's live output doesn't match those distributions closely, the health score is noisy and doesn't correlate cleanly with "fault injected = score drops."

**Layer 2 — Scripted fault injection with physics-accurate sensor ramps:**  
The "Inject Gas Lock" button triggers `active_degrades`, which tells the telemetry simulator to ramp sensor values over 5 minutes (5x compressed from real 25 min). This is also real. But the connection between "simulator is ramping sensors" and "model is updating its prediction" is lossy — the model needs enough fault-labeled rows in the 10-minute query window before it produces a meaningful RUL estimate.

**The gap between layers:** When the fault is first injected, the 10-minute DB window contains mostly nominal rows. The model sees a mixed window and produces a noisy health score. By the time the window fills with fault rows (~5-8 min), the "demo" is essentially over.

### The Context Fusion Problem
The `adjust_rul_with_documents()` function applies multipliers to the XGBoost RUL estimate based on keywords found in retrieved RAG documents. It uses simple string matching (`if "gvf" in content.lower()`). The function is correct in design but it only fires if:
1. The RAG retrieval actually returns documents with matching keywords
2. The `_intel_generator` is actively writing new, fault-specific documents

If `field_intel` has stale documents (1-2 days old), the RAG query may be retrieving those old documents which may not match the keyword conditions. Result: multiplier = 1.0, adjusted_rul = raw_rul, no context fusion gap.

### The Visual Design Problem
The current chart design requires the audience to understand what "Minutes Until Pump Failure" means and why the SCADA line staying at 120 is a meaningful comparison. This requires narration. The visual doesn't self-explain.

Additionally, the well strip (CSS instrument panel) on the right is purely decorative — it's not connected to meaningful model output. The "motor warming" shown in the animation is driven by a CSS timer, not by actual motor temperature data from the model.

---

## PART 5: WHAT DOES WORK

To be fair to the implementation, these components ARE working correctly:

1. **XGBoost models ARE loaded and running** — The event processor classifies every telemetry event (every 5 seconds) and writes `predicted_label` to `telemetry_events`. The labels are visible in the DB.

2. **Gemma 4 / Ollama IS running** — `ollama_online: True, model: gemma4:latest`. LLM responses are real Gemma output, not hardcoded.

3. **AlloyDB RAG IS populated** — 18 RAG documents (OEM manuals, API standards) are embedded and queryable via pgvector. The `/api/agent/chat` endpoint works for follow-up questions.

4. **Vertex AI Vizier (H3) IS working** — The Bayesian optimization loop runs real trials and produces a Pareto frontier chart.

5. **Window of Options logic IS correct** — The viability tickers for the three intervention options correctly decay over time once a fault is active.

6. **The overall page structure IS good** — Three tabs (Detect/Discern/Optimize), dual-reality bar, 3-column layout, CSS instrument panel aesthetic. This is the right structure.

7. **The business narrative IS compelling** — $0 vs $150k. $1,500 vs $150,000. $1.2M additional revenue. The numbers are real and defensible. The audience cares about these.

---

## PART 6: WHAT A WORKING DEMO NEEDS

For a compelling 5-minute demo tomorrow, the minimum required behavior is:

### Must-Fix (Demo Breaks Without These)
1. **Sensor data must visibly change after fault injection.** The SCADA chart must show PIP and Amps declining. This is the foundation. If sensors don't move, nothing else matters.

2. **The "Minutes Until Failure" primary line must count down, not sit flat.** The audience needs to see urgency building. Even if the exact numbers aren't model-derived, the visual must show time running out.

3. **SCADA line must stay high, GDC line must go down.** This is the entire value proposition in one visual. If both lines move the same way or don't move, the demo fails.

4. **The Advisor must provide at least one clear, specific, contextual statement** that references a real document: *"The shift note from Tour 2 records GVF above 70%. The separator gas test shows GOR rising. Combined with the PIP decline rate of X PSI/min, this is gas lock."*

### Should-Fix (Demo is Weak Without These)
5. **Intelligence feed should show at least 2-3 fresh documents** with timestamps of "just now" or "2 min ago" during the demo.

6. **The context-fusion gap must be visible** — even if only 5-10 minutes difference. The visual bracket between sensor-only and context-fused lines is the only way to show the RAG pipeline is doing something.

7. **The Advisor should provide a second update** when new documents arrive, specifically saying what changed: *"Updated assessment: new lab report retrieved. GOR at 1,310 scf/bbl confirms gas migration. Revised estimate: 18 minutes (down from 22)."*

---

## PART 7: DESIGN CONSTRAINTS AND BOUNDARIES

### Hard Constraints (Cannot Change)
- The platform runs on a GKE cluster at `gdc-pm.bdau.io`
- No npm/webpack/React/build pipeline — vanilla HTML/JS + Vue.js via CDN only
- The `terraform/gke.tf` cannot be applied (would destroy the live cluster)
- XGBoost `.ubj` models cannot be retrained without new training data and explicit decision
- All changes go into `gke/fault-trigger-ui/index.html` and `gke/fault-trigger-ui/app.py`
- Deploy path: `docker build → docker push → kubectl rollout restart`
- No browser on the SSH remote (no Puppeteer/browser automation available for testing)
- Branch: `feature-trio-scenarios` — do not merge to main

### Soft Constraints (Breakable With Discussion)
- "No hardcoded values" is a principle, not an absolute. For demo purposes, pre-scripted sensor trajectories that look real are acceptable — the fault injection button is visible and labeled.
- The LLM streaming is real Gemma output, but the *timing* and *triggering* of when the Advisor speaks can be scripted around the demo flow.
- The context fusion delta does not need to come from the RAG pipeline in real-time — it can be computed from the fault injection state and presented honestly as "the model's estimate adjusted by retrieved documents."

### The "Honest Simulation" Principle
The demo acknowledges it uses simulated sensor data. The fault injection button is visible. This is stated upfront. What is NOT acceptable:
- Displaying a value that says "model output: X" when X is actually hardcoded
- Showing the Advisor streaming text that doesn't reflect what the model actually knows
- Showing the SCADA line at 120 when the model is also producing 120 (both flat = no story)

---

## PART 8: TECHNICAL ARCHITECTURE (FOR CONTEXT)

### Data Flow
```
Telemetry Simulator (K8s pod)
  → generates physics-accurate sensor readings every 5s
  → publishes to RabbitMQ exchange "telemetry"

Event Processor (K8s pod)  
  → consumes from RabbitMQ
  → loads esp_health.ubj / gas_lift_health.ubj / etc.
  → runs XGBoost .predict() on each event
  → writes to AlloyDB: telemetry_events (psi, temp_f, vibration, motor_amps, 
     failure_type, predicted_label, confidence)

fault-trigger-ui / app.py (K8s pod — FastAPI)
  → /api/live-telemetry/{asset_id} — last DB row, current sensor values
  → /api/plot/forecast-data/{asset_id} — 10 min history + XGBoost RUL + chart data
  → /api/agent/chat — Gemma follow-up chat
  → /api/intel/feed/{asset_id} — latest field_intel documents
  → /api/mlops/status — system health check
  → Background thread: _intel_generator (writes new Gemma docs to field_intel every 20-30s)
  → Background thread: active_degrades (tracks fault injection state per asset)

fault-trigger-ui / index.html (Vue.js SPA)
  → Polls /api/live-telemetry every 5s
  → Polls /api/plot/forecast-data every 10s (H1 chart data)
  → Polls /api/intel/feed every 15s during active fault
  → Renders Plotly charts (primary RUL chart, SCADA secondary chart)
```

### Key API Response (forecast-data) — Current State
```json
{
  "time_to_scada_minutes": 16.1,    // XGBoost sensor-only estimate
  "adjusted_rul_minutes": 16.1,     // RAG-context-adjusted estimate (SAME = no fusion delta)
  "health_score": 0.6568,           // Raw model output (0=failed, 1=healthy)
  "fault_active": null,             // Should be "gas_lock" when fault is running
  "slopes": {
    "dpsi_dt": 27.587,              // PSI rate of change (positive = rising??)
    "dtemp_dt": 9.007,              // Temp rate of change
    "dvib_dt": 0.262,               // Vibration rate of change  
    "ds4_dt": -2.855                // Motor amps rate of change (negative = declining ✓)
  }
}
```

Note: `dpsi_dt` being positive (27.587) is suspicious for a gas lock scenario where PIP should be declining. This may indicate the slope calculation is using the wrong sign convention or the fault is not currently active.

---

## PART 9: THE QUESTION FOR EXTERNAL REVIEW

Given all of the above, here is what I need help with:

**The core question:** How do we build a compelling 5-minute visual demo of this technology stack that will be convincing to a non-technical business audience tomorrow, given that:

1. The real-time model outputs are noisy and don't produce clean declining curves
2. The LLM (Gemma 4) can generate compelling text but fires only once
3. The sensor simulation IS generating the right physics — the plumbing to display it is broken
4. We cannot abandon the real technology (must use real XGBoost models, real Gemma, real AlloyDB)
5. We have 1 developer, ~6-8 hours of remaining time today

**Specific questions:**
- Should we make the primary chart demo-scripted (pre-compute the declining curves based on elapsed time since injection) while keeping the model outputs as a secondary verification display?
- Should the "Minutes Until Failure" concept be replaced with something more intuitive — like a Health Score gauge that drops from green to red, with a countdown timer?
- How should the LLM Advisor re-trigger? On a timer? On a significant model state change? On new document retrieval?
- What is the single most compelling visual for "SCADA can't see this, GDC can"?
- Is the three-line chart (SCADA/sensor-only/context-fused) the right approach, or is there a simpler visual that self-explains without narration?

---

## PART 10: CURRENT LIVE STATE

```
Cluster: GKE at gdc-pm.bdau.io
All pods: 1/1 Running
Ollama: online, gemma4:latest
AlloyDB: 86 field_intel rows, 18 rag_documents
Git: 919c7ee (feature-trio-scenarios)
Image: sha256:c335c72c (fault-trigger-ui)
```

The application is live and accessible at `http://gdc-pm.bdau.io`

**Demo credentials:** None required — open access on the cluster's public IP.

---

*End of brief. Total implementation investment: 16 sessions on June 3-4, 2026. The architecture is sound. The plumbing is built. The demo story is correct. The execution gaps are in chart rendering, polling logic, and LLM re-triggering.*
