# H3 Optimize — Decision Dossier (Session BS+48)
**Date:** 2026-06-25 · Session BS+48 · **Status:** Architecture locked; build scoped for next session.
**Purpose:** Zero-loss preservation of the complete H3 reasoning chain. This document records everything that was eliminated, why, every RT verdict, every citation, and the exact build plan. Before any H3 code or recording, read this entire file. Do not re-open closed debates unless you have new evidence.

---

## 1. The Question This Session Answered

> *"Does H3 have an honest, unassailable reason to exist — or is GDC just cosplaying as a control system that SCADA already is?"*

**Short answer:** Yes — H3 earns its place, but only with the exact framing below. Every prior framing failed. The one that survives is the two-timescale control hierarchy, with a 5-angle moat and one physics rule (trim-DOWN-only). Details follow.

---

## 2. Eliminated Options (Do NOT Reopen)

These were considered, tested, and eliminated. Each entry records the exact reason so a future session doesn't waste tokens rediscovering the same failure.

### ❌ ELIMINATED: "Edge does the optimization"
- **Why it fails:** The shared gas ceiling (e.g., 8 MMscfd) is a **field-wide shared constraint.** A single pad node has no visibility or authority over other pads' allocations. Only a layer seeing *all* wells can allocate a shared constraint. Optimization is categorically a global-view job.

### ❌ ELIMINATED: "Edge corrects a gas-contract overrun that the cloud plan caused"
- **Why it fails:** The gas contract is **central and known at plan time.** It belongs in the cloud's objective function from the start — not as a post-hoc edge "correction." Worse: in the actual code, `evaluate_field()` (the "edge oracle") **IS** Vizier's objective function. So "cloud proposes / edge corrects gas" would mean the same component correcting itself. Dishonest and incoherent.

### ❌ ELIMINATED: "Story 1 as the headline" (cloud=search, edge=objective-function)
- **Preserved as fallback** (it is true to code) but not strong enough as the hero story. Too abstract for CXO+engineer audience. Story 2 (below) is the honest and compelling version.

### ❌ ELIMINATED: "The optimizer searches and learns trial-by-trial" (over a batch)
- **Why it fails:** The current code calls `suggest_trials(count=15)` — a **single batch**. Vizier does NOT iterate/learn from trial 1 before proposing trial 2. Narrating it as "learns" is a silent lie. Fix: make the loop iterative before this claim appears on screen. See Build Plan section.

### ❌ ELIMINATED: "Operators won't give data to Siemens/AspenTech/SLB because they're untrusted"
- **Why it fails:** RT FAILS. Operators *do* hand significant data and control to these vendors under strict contracts every day. This is demonstrably false and will "immediately alienate any experienced operator" (RT verdict). Replace with the vendor-neutral-platform framing (see Moat section).

### ❌ ELIMINATED: "GDC invented / is a new control paradigm"
- **Why it fails:** It's applied RTO-over-MPC, the established refinery/grid pattern. Claiming novelty makes us look ignorant of control history. The honest framing is: "we're the sovereign edge substrate for the two-timescale pattern the industry already knows it needs." Concession = credibility.

### ❌ ELIMINATED: "SCADA lets the pump die" (anti-SCADA strawman)
- Permanently banned by .clinerules. SCADA trips and protects. We win on **context fusion**, not on "SCADA is dumb."

---

## 3. The Locked Thesis — Story 2: Two-Timescale Control Hierarchy

**Architectural name:** RTO-over-MPC (Real-Time Optimizer over Model Predictive Control), the standard refinery/grid pattern. Applied here to ESP fleet optimization.

### Layer 1 — Cloud / Planning (slow, global, periodic)
- **Who:** Vertex AI Vizier (Bayesian optimizer, in code: `aiplatform_v1.VizierServiceClient`, project `gdc-pm-v2`, region `us-central1`)
- **Job:** Solve the GLOBAL, COUPLED, ECONOMIC allocation — how to divide a single SHARED gas-takeaway contract across all wells to maximize total oil/revenue.
- **Why coupled:** Each well's optimal Hz depends on others because they share ONE gas budget.
- **Why periodic (not real-time):** Global allocation depends on slow variables (GOR, contract limits, prices, well ranking) that don't change minute-to-minute. Cannot continuously re-solve a fleet-wide joint optimization in real time — economically prohibitive and unnecessary.
- **What it knows:** Best recent picture of the field (last shift or daily snapshot).

### Layer 2 — Edge / Execution (fast, local, continuous)
- **Who:** Google Distributed Cloud, on-prem at pad/RTOC (GKE + AlloyDB + XGBoost models + local physics)
- **Job:** Take the cloud's allocation as a **TARGET** and reconcile it against **LIVE reality the plan could not have known** — a motor running hotter than modeled (degrading seal), a well slugging now, a well that tripped an hour ago.
- **When target is unachievable:** Edge **trims DOWN** that asset locally and holds the rest to plan. Does NOT round-trip to cloud. Does NOT reallocate UP (see Physics Hole below).
- **Data boundary:** Only setpoint vectors (Hz) + scalar scores (cash-flow) cross to the cloud. Raw high-frequency sensor data, reservoir data, contract details — **never leave the site.**
- **Offline:** If network drops, last safe plan keeps running; edge continues enforcing local safety limits.

### Why Both Layers Are Required (RT-confirmed SURVIVES)
- **Edge CANNOT do cloud's job:** No field-wide visibility or authority over a shared constraint.
- **Cloud CANNOT do edge's job:** Streaming every well's high-freq state for continuous central reconciliation = data gravity + latency problem, infeasible at fleet scale. Not physically impossible, but economically prohibitive.
- **RT verdict:** *"'You need both layers' is practically true for fleet-scale O&G."* — SURVIVES.

---

## 4. Physics Hole #3 — CLOSED

**The hole:** If the edge **reallocates UP** to recover lost production when one well is trimmed, it can **breach the shared gas contract ceiling** the cloud was protecting. The edge has no global view of what other wells are doing.

**The rule:** **The edge may ONLY trim DOWN within its slice.** Trimming DOWN (less Hz on a motor-hot well) is always gas-safe — less gas produced, ceiling not breached, no global view needed. Reallocating UP touches the shared budget and requires the cloud.

**The narrative:** Giving back a little production until the next cloud re-optimization cycle is **correct, not a bug**. It is "safe by construction — the edge never breaches your gas contract, even mid-perturbation, even offline."

**Code implication (build rule):** When implementing the plan-vs-live-state reconciliation (Build Plan step 2), `evaluate_field_live()` must only allow `hz_live[i] ≤ hz_plan[i]` per well. No up-reallocation logic.

---

## 5. The Moat — Five Independent Angles

The prior single-moat ("distrust Siemens") failed. A real moat is layered — kill one, four remain.

### Angle 1 — Greenfield Reach (cited, ~24% PdM / ~11% ML-APM)
- **Source:** Industry survey (uptimeai.com / reliamag.com, 2023): only ~24% of O&G companies run ANY predictive maintenance strategy; only ~11% reach ML-driven maturity.
- **Claim:** For the ~76–89% who have no ML APM, GDC is not "better than SmartSignal" — it's their **first and only AI layer**, on infrastructure they already govern with Google. No incumbent to defeat; pure greenfield.
- **Must-NOT-say:** "Super-majors don't run advanced APM" (they do, partially). Say: "even super-majors are mixed — not 100% coverage across all wells."

### Angle 2 — Horizontal Platform vs. Point Product
- SmartSignal/PRiSM/Mtell are **single-purpose APM products.** GDC is a **general-purpose compute+AI platform** (GKE / AlloyDB / Vertex) — the same sovereign box runs H1 diagnosis, H2 document fusion, H3 optimization, and any future app.
- **Claim:** "Buy a tool vs. own the platform your whole fleet's AI runs on."
- RT verdict: SURVIVES-IF-REWORDED (scope "vendor-neutral" to "neutral relative to equipment vendors").

### Angle 3 — Unstructured-Context Fusion (STRONGEST, CATEGORICAL)
- APM is **sensor-data-only by architecture.** It does not read vendor PM portals, PVT PDFs, workover records, flaring permits, shift notes — the off-sensor documents that H1 and H2 show are decisive.
- **This is categorical, not incremental**: it's not "GDC does it faster" — APM structurally **cannot** do it at all.
- RT verdict: SURVIVES (confirmed as core, defensible value proposition across both H2 Claim B passes).
- **This moat applies identically to H1 AND H2** — it's the GDC spine across all three horizons.

### Angle 4 — Sovereign Fleet Model-Ops
- One owned ML lifecycle across hundreds of sites: **GitOps config / Config-Sync** (declarative policy fleet-wide), **central Vertex training → edge deploy/rollback**, **governed enterprise IAM**, consistent audit.
- Control-automation vendors give you a control product per site; they are NOT a fleet-wide, self-owned, declaratively-managed, identity-integrated ML platform.
- **MUST-NOT-SAY:** "GitOps manages PLC/SCADA Level-1/2 configs" (it doesn't; it manages the GDC apps + infra layer only). RT Top Fix #1.

### Angle 5 — Sovereignty / Data-Gravity / Outage-Tolerance
- Raw high-frequency + reservoir + contract data stays on-prem. Only setpoints + scores cross. Runs through link drop.
- Already validated by .clinerules integrity note (app.py L6741–6763).

### Synthesis Line (no anti-competitor FUD)
> *"Most operators don't have advanced APM at all — and those who do bought a sensor-only point product. GDC isn't a better alarm: it fuses the documents APM can't read, runs your whole fleet's AI under one governed lifecycle you own, and keeps your data on-site. Where APM exists, GDC complements it; where it doesn't, GDC is the first AI layer you need."*

---

## 6. Must-NOT-Say (RT-Confirmed, Permanent)

| # | Must NOT say | Why |
|---|---|---|
| 1 | "Operators don't trust control vendors with their data" | FUD — demonstrably false. RT FAILS. Alienates operators. |
| 2 | "GDC invented / is a new control paradigm" | It's applied RTO/MPC. Claiming novelty invites "I've been doing this since 1995." |
| 3 | "The edge does the global optimization" | Requires field-wide view the edge doesn't have. |
| 4 | "14 of 15 proposals were rejected on-prem" as a hero stat | Reads as a broken optimizer. Fix feasible-rate first (Build Plan step 1). |
| 5 | Over-lean on "world-class Bayesian" tool name | Vizier-vs-LP is contestable (RT SURVIVES-IF-REWORDED). Lead with the *problem*. |
| 6 | "Vendor-neutral" without scoping | Scope to "neutral relative to equipment vendors." Google is a vendor too. |
| 7 | "GitOps/declarative LCM" manages PLC/SCADA/Level-1/2 | It manages GDC apps + infra only. RT Top Fix #1. |

---

## 7. Verified Facts (Live Cloud + Code)

| Fact | Source | Value |
|---|---|---|
| Real Vizier project | app.py L6504 | `gdc-pm-v2` / `us-central1` |
| Real studies confirmed | live REST API | 10 studies `gdc_pad_alpha_field_opt_*` (2026-06-23 → 06-24) |
| Latest study trial breakdown | live REST API (study 593258648990) | 15 trials: **14 INFEASIBLE, 1 feasible** |
| Root cause of 14/15 infeasible | code analysis | Shared gas ceiling + wide independent Hz bounds + batch suggest = random darts miss the thin feasible region ~93% of the time |
| Vizier call type | app.py L6734 | `suggest_trials(count=15)` — **single batch**, NOT iterative |
| Oracle runs on-prem | app.py L6621 | `evaluate_field()` — thermal polynomial + RUL + gas ceiling; returns infeasible verdict to Vizier |
| Data boundary | app.py L6707–6767 | Hz vectors + scalar cash-flow score only cross to Vizier. No reservoir/well data. |
| Vizier cost | Gemini search, finout.io | First 100 trials/month **FREE**; then $1/trial (Bayesian). 15/run → ~6 free runs/month. No GPU. |
| APM penetration | uptimeai.com / reliamag.com (2023) | ~24% any PdM strategy; ~11% ML-maturity. Super-majors mixed. |

---

## 8. RT History (Both Passes)

### RT Pass 1 (framing: "14/15 rejected + batch as search")
- **Claim A elements:** 14/15 reject rate → FAILS (reads as "broken, not 'world-class'"). "Search" over a batch → FAILS (misrepresents the process). Cloud/edge separation → SURVIVES-IF-REWORDED. Scale claim → FAILS (undermined by 14/15).
- **Claim B elements (H2):** "Be proactive / instant-triage is reactive" → FAILS (fuzzer). Document fusion + cost dichotomy → SURVIVES.
- **Adjudication (my ruling):** 14/15 and batch-as-search LAND (real; fix the feasible-rate + make iterative). H2 "proactive" attacks are NOISE (factually wrong — the off-sensor PM overdue variable *cannot* be predicted from telemetry by definition; rejected). H2 document fusion + cost SURVIVE.

### RT Pass 2 (validation: two-timescale + moat)
- **Two-timescale thesis:** cloud layer → SURVIVES; edge layer → SURVIVES; "need both layers" → SURVIVES. Direct quote: *"Is this two-timescale decomposition honest for O&G? SURVIVES. This is a standard and well-understood hierarchical control architecture (RTO over MPC)."*
- **Vendor-trust moat:** FAILS. *"Operators DO hand over data to control vendors. This is a marketing FUD tactic."*
- **"Vendor-neutral" (reworded to equipment-vendor scope):** SURVIVES-IF-REWORDED.
- **Value line summary:** SURVIVES. *"This is a concise and accurate summary of the two-timescale control paradigm."*
- **Adjudication (my ruling):** Thesis fully validated. Vendor-FUD FAILS = real; replace with 5-angle moat. The "point product vs platform" and sovereign moats survive. "Architecture alone is not a moat" — correct; the moat is the combination of (3) unstructured fusion + (4) Model-Ops + greenfield reach + sovereignty.

---

## 9. H3 Three-Act Demo Plan (Record-Ready After Build)

**Act 1 — THE CLOUD PLAN (real Vizier, hero of the show):**
Run Vizier iteratively (post-fix); show trials arriving sequentially, converging to the per-well allocation. The Pareto chart in the cloud panel (in-app, Option B — clean real-data panel, not raw GCP console).
- VO: *"The cloud's job is the global allocation — dividing a shared gas budget across wells to maximize revenue. That's Vertex AI Vizier, Google's Bayesian optimizer, running in the cloud. It doesn't see your wells; it sees a vector of setpoints and a score. It proposes; the edge answers."*
- Show trials converging (feasible vs infeasible, with fix in place so the convergence is real).

**Act 2 — EDGE RECONCILE (the new honest beat — where GDC plays):**
Inject one live perturbation: *A-5's motor is running hotter than the plan assumed* (e.g., 12°F above nominal — degrading seal). Edge detects on-prem, **trims A-5 down** (58 Hz → 53 Hz), holds the rest to plan.
- VO: *"The plan said 58 Hz for A-5. But A-5's motor is running hot today — hotter than when the plan was made. The edge detects this on-prem, trims A-5 down to protect the motor and stay under the gas ceiling, and holds the rest to plan. No cloud round-trip. Your data didn't move."*
- This is the "plan doesn't survive contact with implementation" problem, solved: the edge absorbs the fast, local, per-asset reality the cloud can't track.

**Act 3 — SOVEREIGN / SCALE:**
Pull back: one plan → many edge nodes, each trimming to live reality, all under one owned operating model. Safety enforced locally even offline.
- VO: *"The same collaboration runs across the fleet. One central plan per cycle; N sovereign edge nodes each protecting their own assets against live conditions — on your data, under your governance, even if the network drops."*
- This is where the 5-angle moat lands.

---

## 10. Build Plan (Next Session, Exact)

### Step 1 — Make Vizier Loop Iterative
- **File:** `app.py` ~L6701–6770 (function `vizier_optimize()`)
- **Change:** Replace `suggest_trials(count=15)` single-batch with iterative: suggest small batch (e.g., 5) → score on edge → `complete_trial` back → repeat 3× = 15 trials in 3 rounds.
- **Why:** (a) Raises feasible rate (Vizier learns the gas-ceiling boundary from round-1 rejections); (b) makes "it searches and learns" **literally true**; (c) kills the "93% random noise" attack.
- **Cost:** Still ~15 trials per run. Verified $0 additional (within free tier). No GPU.

### Step 2 — Plan-vs-Live-State Split (Story 2 mechanism)
- **File:** `app.py` `vizier_optimize()` return payload; `tab_h3.html` display
- **Change:** Return both `plan_hz_vec` (what Vizier computed) AND `live_hz_vec` (after edge trims one perturbed well). One well (e.g., A-5) gets a live motor temp +12°F injected — simulating a degrading seal not visible in the cloud plan.
- **New edge function:** `reconcile_live(plan_hz_vec, live_well_params)` → applies trim-DOWN rule; returns `live_hz_vec` and a `trims` list showing which wells were adjusted and why (motor temp over threshold, RUL derate).
- **MUST:** Enforce `hz_live[i] ≤ hz_plan[i]` per well (hole #3 rule).

### Step 3 — Presentation (Panel B + Feasibility Visual)
- **tab_h3.html:** Add cloud-panel (Vizier results) vs edge-panel (live reconcile + trims).
- Render infeasible trials as rejected (✗) in trial log; feasible as (✓). This is already in the data (`is_failure`).
- Add the `live_hz_vec` column to the per-well table (shows trimmed vs planned).
- Label: small "⏺ Architecture view — system-to-system flow" tag (same honesty-register discipline as H1/H2 "⏺ Scenario Replay").

### Step 4 — Verify Live (before recording)
- `curl http://gdc-pm.bdau.io/api/vizier/optimize` and confirm: iterative (3 rounds visible in trial log), feasible rate improved, `live_hz_vec` present in response, trim on A-5 visible.
- H3-S4 constraintDoc.found=True: confirm RAG query for midstream contract returns a found=True result consistently.

### Step 5 — H2 Instant-Triage (can be done same session)
- **File:** `static/app.js` `loadH2Scenario()` (around L2057–2090)
- **Change:** After `this.h2ReplayData = data`, set `this.h2CursorIdx = data.scada_alarm_idx` (load at active alarm, not idx=0).
- Optionally hide/disable the Play/Pause/FF transport controls on H2 (or just leave them — the instant-load is the fix; the controls are then available for scrubbing back, which is fine).
- **Verify:** Tab opens with the 90-day history already plotted, VIB-HI alarm active, docs ready. No more "watch 8 weeks play out."

---

## 11. Decision Record (one-line each, permanent)

| Decision | Rationale |
|---|---|
| Story 2 over Story 1 | Cloud-plans-on-nominal / edge-reconciles-live is the honest, CXO-legible version. |
| Edge trims DOWN only | Hole #3: up-reallocation breaches shared gas ceiling. Cloud re-optimizes next cycle. |
| Iterative Vizier loop | Fixes 14/15 root cause + makes "searches/learns" honest. Batch was a silent lie. |
| Plan-vs-live-state split | What makes Story 2 REAL rather than narrated. The one genuinely new mechanism. |
| "Vendor-neutral" scoped to equipment vendors | RT FAILS on broad trust claim. Vendor-neutral = no equipment-brand bias, not "neutral in general." |
| H3 is architecture story, not operator tool | No human clicks "Run Vizier" in production — it runs machine-to-machine. Showing the collaboration in slow motion is honest and correct for a mixed audience. |
| APM-penetration stat used | Cited (uptimeai.com / reliamag.com, 2023). Tagged 🟡 OUR-USE (directional, defensible). Say "most operators" not "all operators." |
