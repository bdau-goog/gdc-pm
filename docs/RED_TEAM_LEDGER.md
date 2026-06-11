# GDC Demo — Red Team Ledger

**Purpose:** Every hostile-engineer rebuttal against on-screen claims, ranked by risk.
Only claims with **Honest answer = YES** are pixel-eligible.
Trigger phrase **"red team"** re-runs this audit at any checkpoint.

---

## Verdict Key
| Code | Meaning |
|------|---------|
| ✅ YES | We have an honest, citable answer |
| ⚠ WEAK | Partially defensible — must soften or caveat before showing |
| ❌ NO | Cannot be honestly defended — must cut or redesign |

---

## H1 — Discern Tab (ESP Fluid Unloading)

| # | Challenge | Target | Severity | Honest answer? | Fix applied |
|---|-----------|--------|----------|----------------|-------------|
| H1-1 | "CLAIM_LEDGER says gas-lock/drawdown share psi 875–1100 / vib 2.0–3.5, but FAULT_PROFILES in app.py says psi 400–600 / vib 4.5–6.5" | CLAIM_LEDGER.md H1 rows | 🔴 CRITICAL | ❌ NO — ledger contradicts code | **Fixed Session V**: CLAIM_LEDGER.md reconciled to actual FAULT_PROFILES values |
| H1-2 | "A multivariate SCADA rule can distinguish gas lock from drawdown" | H1 ambiguity premise | 🟠 HIGH | ✅ YES — no numeric combination of PIP/Amps/Temp/Vib can discriminate; FAULT_PROFILES are identical arrays | Stated honestly in Physics panel; we concede rule-based *detection* to SCADA and win only on *classification* via unstructured context |
| H1-3 | "Your lead time (GDC vs Smart SCADA) is inflated" | `lead_time_minutes` on screen | 🟠 HIGH | ✅ YES — computed as `t_min[scada_idx] - t_min[gdc_idx]` from real model output; we do not inflate | Code comment confirms; `model_used` field shown on screen shows FALLBACK if model absent |
| H1-4 | "GVF 78% at intake is a made-up sensor reading" | H1 shift note UI text | 🟡 MEDIUM | ⚠ WEAK — GVF is not directly sensed; it's inferred from casing pressure + separator GOR | **Fix Session V**: soften to "suspected high GVF (inferred from casing pressure + separator GOR)" — not a direct measurement |
| H1-5 | "Fluid level 150 ft above intake — how do you know? ESP sensors measure pressure, not depth" | H1 Fluid Drawdown SVG + doc card | 🟠 HIGH | ✅ YES — sourced from the 06:00 Echometer acoustic survey log that is retrieved via RAG. We do not infer depth from pressure; we *read the log*. Source cited on-screen. | GDC's advantage is *reading the log*; SVG annotates "Source: 06:00 Acoustic Survey" |
| H1-6 | "The Echometer survey would be ordered, not streaming" | H1 Fluid Drawdown SVG | 🟠 HIGH | ✅ YES — narrative: survey ordered by lease operator on prior tour at 06:00, PDF uploaded to shared drive, GDC retrieves it 15 min later when the anomaly fires. This is the silo story. | On-screen metadata: "Ad-Hoc Survey · Executed 06:00 · Uploaded 15 min prior" |
| H1-7 | "4.2 ft/s critical sand-transport velocity is well-specific, not universal" | H1 VFD contraindication claim | 🟡 MEDIUM | ✅ YES — computed from this well's bore geometry; displayed with SPE-174536 citation as the physical basis; labeled "demo-specific" | Citation shown; no claim of universality |
| H1-8 | "Motor temp rises in gas lock AND drawdown — you say it's the discriminator for H2 but show it rising in H1" | H1 physics panel / H2 physics reframe | 🟠 HIGH | ✅ YES — in H1 temp DOES rise (loss of cooling fluid flow in both gas lock and drawdown is IDENTICAL, which is WHY they can't be discriminated by telemetry). In H2 slug flow, temp stays FLAT because the pump is hydraulically healthy and cooling is unaffected. These are different mechanisms. | Physics panel explicitly states: "H1 — both faults lose cooling flow, both temps rise. H2 — pump healthy, cooling unaffected, temp flat. Flat temp is the H2 discriminator." |

---

## H2 — Classify Tab (ESP Slug Flow Discrimination)

| # | Challenge | Target | Severity | Honest answer? | Fix applied |
|---|-----------|--------|----------|----------------|-------------|
| H2-1 | "Surface slugs can't mechanically shake a gauge 2 miles down a damped, clamped tubing string" | Original H2 physics narrative ("shock down the tubing") | 🔴 CRITICAL | ❌ NO — downhole transmission is negligible. **Cut the old mechanism.** | **Fixed Session V**: reframed to in-string multiphase slug loading *at the pump* (cyclic gas/liquid slugs reach the pump intake via the production tubing itself) — gauge is at the pump, transmission objection eliminated |
| H2-2 | "14-minute slug periodicity — that's a separator test cadence, not a slug cycle" | H2 "Separator Test Report" document | 🟠 HIGH | ⚠ WEAK — well-test reports show multi-hour averaged rates; they do not resolve minute-scale cycles | **Fix Session V**: re-source periodicity to wellhead/flowline pressure SCADA trend + VFD amp swing. Separator test cited only for the GOR-rising evidence. |
| H2-3 | "Vibration says 2.4 mm/s in the UI but the classifier was trained on 4.0–6.5 mm/s" | H2 banner vib number vs FAULT_PROFILES + fault_signatures | 🔴 CRITICAL — silent contradiction | ❌ NO — three files disagree | **Fix Session V**: reconcile to FAULT_PROFILES (4.0–6.5); UI shows "rising toward 4.5 mm/s peak"; simulator updated to match |
| H2-4 | "Vibration below 5.0 mm/s trip — why would anyone call a rig?" | H2 $150k pull premise | 🟠 HIGH | ⚠ WEAK without ISA-18.2 level split | **Fix Session V**: model HI alarm at 4.0 mm/s (fires; demands decision); HH trip at 5.0 mm/s (not yet crossed). Operator reacts to the rising-trend HI — realistic. $150k avoided if surface cause identified before escalation. |
| H2-5 | "If the pump health score is 0.95, why does your UI say the pump might need pulling?" | H2 SCADA "pull" action card | 🟠 HIGH | ✅ YES — health score is the downhole pump condition; SCADA operator doesn't see health score, only sees vibration alarm. The *SCADA* pull impulse comes from the vibration HI, not the health score. | GDC's health score is shown on its own panel to differentiate: "Downhole pump health: 0.95 — HEALTHY" vs "SCADA vibration HI fired." |
| H2-6 | "Your classifier was trained on flat-temp data — it will always output slug_flow if temp is flat, regardless of vibration pattern. That's circularity." | esp_classifier.ubj training design | 🟡 MEDIUM | ✅ YES — flat `dtemp_dt` is one feature; the classifier distinguishes slug_flow from normal by the *concurrent vib rise*. A flat-temp, flat-vib point scores as normal. | Physics panel explains: "Classifier inputs: vib rate + temp rate simultaneously. Normal: both flat. Slug: vib rises, temp flat. Bearing: both rise. Three distinct signatures." |
| H2-7 | "You said 'SCADA has no mechanism to read unstructured documents' — advanced SCADA like PI Vision has notes/annotations" | H2 SCADA architecture claim | 🟡 MEDIUM | ✅ YES — OSIsoft PI/Aveva supports narrative annotations in the historian, but these are manually entered, asset-specific, and not semantically searchable against a fault hypothesis in real time. GDC's pgvector RAG retrieves and synthesizes the relevant passage automatically in < 2 seconds. | Concede honestly: "Advanced SCADA historians *store* annotations; they do not *semantically retrieve* cross-document context against a live fault hypothesis. That retrieval + synthesis is GDC's architecture." |
| H2-8 | "The shift note, choke log, and separator test are all hand-authored for your demo" | H2 evidence wall documents | 🟡 MEDIUM | ✅ YES — seeded for the demo. In deployment, `_intel_generator` reads from live field data integrations. RAG pipeline and fusion mechanism are identical. | Challenge answer pre-loaded in the Physics & Logic panel |

---

## Cross-Cutting (applies to all tabs)

| # | Challenge | Target | Severity | Honest answer? | Fix applied |
|---|-----------|--------|----------|----------------|-------------|
| X-1 | "Your cloud AI (Gemma) is making clinical safety decisions" | LLM advisor language | 🟠 HIGH | ✅ YES — GDC Advisor is explicitly an *operator-assist* tool, not autonomous control. Human operator executes every action. Language audit: "Recommend" / "Advise" — never "Command" / "Decide." | All LLM output uses "Recommended action:" prefix; action cards require operator click |
| X-2 | "The cost numbers ($150k, $1.5k) are made up" | All monetary claims | 🟠 HIGH | ✅ YES — all sourced in CLAIM_LEDGER.md and app.py RESOLUTION_OPTIONS. WTX rig spot rate $14k/day × 3 days + motor + cable + deferred prod. | Inline source note shown next to every cost: `[WTX spot rig $14k/day × 3d · OEM motor]` |
| X-3 | "The demo is pre-scripted — this wouldn't work on a real well with real noise" | Whole demo | 🟡 MEDIUM | ✅ YES — scenario is pre-computed but the model is real XGBoost (`esp_health.ubj`, `esp_classifier.ubj`), RMSE and recall metrics verified, and the RAG is against real embedded OEM manuals. | `model_used` field on screen; `FALLBACK_SYNTHETIC` label appears if model absent |

---

## Pending / Needs Investigation

| # | Issue | Status |
|---|-------|--------|
| P-1 | Verify `esp_health.ubj` actual output on a slug_flow input trajectory — does it stay near 1.0 or dip? | **Must verify before H2 UI ships** |
| P-2 | Source a citeable SPE reference for in-string multiphase slug loading causing pump vibration (cyclic hydraulic imbalance at the impeller) | Candidate: SPE-174536 §3.4; Baker Hughes Centrilift Gas Handling Design Guide (need exact section) |
| P-3 | Confirm ISA-18.2 HI alarm level vs HH trip level naming convention in the UI exactly matches the standard | ISA-18.2 Table 5.2 levels: Warning / High (H) / High-High (HH) |

---

---

## Batch B Fixes — Session W (June 9, 2026)

| RT # | Challenge | Severity | Fix applied | Status |
|------|-----------|----------|-------------|--------|
| RT-1 | "92%/94% confidence literals are fabricated HTML — not from any model or computation" | 🔴 CRITICAL | Replaced with live Bayesian posterior `_bayes_discriminate()` — naive-Bayes log-odds over 4 document-derived findings (Good 1950 / Fagan 1975). `P(fluid_drawdown)` = 99.6% computed live from `_BAYES_FINDINGS`. Verified: API returns `bayes_pct: 99.6` on every run. | ✅ FIXED |
| RT-2 | "`hs = 1.0000` shows on confirmed-fault verdict when cursor goes past array bound — contradicts active fault state" | 🟠 HIGH | Fixed: Zone 1 health score now uses `Math.min(h1CursorIdx, h1ReplayData.health_score.length-1)` safe clamped index. Pre-detection fallback uses same expression. Never shows 1.0000 on degraded trajectory. | ✅ FIXED |
| RT-3 | "Sonic log at 06:00 says 'Emergency shutdown is the correct action' — a document with a shutdown order would cause operators to act before the demo window opens" | 🔴 CRITICAL (Document Realism Gate G2/G3) | De-smoking-gunned: sonic log body now shows measurements-only (240 ft submergence, within limits, flat casing pressure). All diagnosis and shutdown orders removed. Moved to GDC verdict layer only. | ✅ FIXED |
| RT-4 | "GOR provenance: acoustic sonic survey doesn't measure GOR — a separator test does" | 🟠 HIGH (Document Realism Gate G5/G6) | New `Separator Lab Report` modal added with correct GOR provenance (Permian Fluid Analytics lab). GOR row removed from sonic log table. Doc 2 in evidence stack now opens the lab report modal. | ✅ FIXED |
| RT-5 | "Sonic log modal says 'Well A-1' but the H1 scenario is anchored to Well A-3 everywhere else" | 🟡 MEDIUM | Fixed: sonic log modal, shift note modal, and all document header rows updated to A-3. Confirmed: `Well A-1` count in container = 0. | ✅ FIXED |
| RT-6 | "The Bayesian posterior is circular — documents are seeded to match the fault type" | 🟡 MEDIUM | This is an honest challenge. Addressed in Physics & Logic panel: 'This is a demonstration of what the system would do when these documents exist. XGBoost detection is genuinely live (new trajectory per run). Bayesian fusion is computed, not hardcoded.' LR values labeled as conservative transparent weights, not calibrated parameters. | ✅ ACKNOWLEDGED |
| RT-7 | "The sonic log modal has Baker Hughes SONiK™ — a real product trademarked by a real company" | 🟠 HIGH (Document Realism Gate G1) | Replaced with fictional service provider: `Permian Acoustic Services (SONiX-2)`. No real company or product trademark. | ✅ FIXED |
| RT-8 | "The shut-in option was framed as zero-cost — that's dishonest (restart costs apply)" | 🟠 HIGH | Fixed Session W Batch A. Shut-in now says 'Deferred production + restart costs apply (see ⓘ)'. | ✅ FIXED (Batch A) |
| RT-9 | "OEM Guide doc card says 'Baker Hughes ESP' — another real-company reference in a synthetic document" | 🟡 MEDIUM (Document Realism Gate G1) | Fixed: doc card now says 'Permian ESP Operational Manual'. | ✅ FIXED |
| RT-10 | "Bayesian LR values (8, 5, 3, 2) — are those calibrated from data or made up?" | 🟡 MEDIUM | LR values are conservative transparent weights grounded in API RP 11S §7.2 physics. NOT calibrated from empirical data. Stated explicitly on-screen in the evidence table: `{{ h1ReplayData.bayes_lr_note }}` renders 'Conservative transparent weights grounded in API RP 11S §7.2; not calibrated from empirical data.' Pre-empts the challenge. | ✅ ADDRESSED |

---

*Last updated: Session AR (June 11, 2026) — H2 dual-AI red-team; scenario invalidated; frac-hit reframe committed*
*Smoke test: N/A — no code written this session (correct — scenario invalid)*

## Session AR — H2 Dual-AI Red-Team Findings (June 11, 2026)

Both Gemini (web) and Claude Opus (web) ran the H2 slug-flow narrative through independent expert red-teams. Convergent verdicts:

| # | Challenge | Target | Severity | Verdict | Action |
|---|---|---|---|---|---|
| H2-9 | "Flat winding temperature is not a bearing-vs-slug discriminator — RTD is in the motor, bearings are in pump/protector (thermally separated); early mechanical wear doesn't move the winding RTD. And in a high-GOR well, gas at the intake *reduces cooling* → temp trends up, not flat — the discriminator runs backwards." | H2 briefing P2 "temp is the discriminator" claim | 🔴 CRITICAL | **FAILS** (both) | **Cut "flat temp = categorical discriminator."** Demote to one weak corroborating signal. Lead diagnosis with the telemetric signature that actually separates cases: cyclic amps-with-recovery + cyclic PIP (APM also reads this). |
| H2-10 | "$150k pull vs $1,500 truck roll is a false dichotomy — the real baseline for cyclic amps/vib is choke/VFD adjustment first. The same $1,500 action reached from the amp chart, not a reflexive workover." | H2 P3 cost comparison | 🔴 CRITICAL | **FAILS** (both) | **Kill the binary.** Reframe as "reduced diagnostic latency + avoided repeated HH trips + deferred production" OR reframe entire scenario (see H2-11). |
| H2-11 | "The deciding signal (cyclic amps-with-recovery + cyclic PIP) is in the telemetry — APM already reads it. Documents only corroborate. L3 moat is not load-bearing here." | H2 L3 value proposition | 🔴 CRITICAL | **FAILS** (both) — same failure class as H1 pre-reframe | **Scenario must be replaced.** See committed reframe in DEMO_MASTER §5: offset-well frac-hit interference (cause is categorically off-sensor, recorded only in third-party document). |
| H2-12 | "APM (SmartSignal/PRiSM/Mtell) stops at an anomaly score — over-concession." | H2 APM baseline claim | 🟠 HIGH | **FAILS** (both) — Mtell classifies trained failure modes + attaches canned SOP | Concede: Mtell can say "gas interference" *if trained*; cannot derive root cause or action by fusing this tour's choke log + separator test + shift note. Scope the moat to that narrower claim. |
| H2-C1 | "Downhole ESP gauges report vibration in g (0–5 g), not mm/s velocity (that's the surface ISO-10816 convention). 4.0/5.0 mm/s signals the scenario was written by a surface-PdM engineer." | H2 vib units across UI + H1 "0.41 in/s" | 🔴 CRITICAL — SURVIVES-IF-FIXED | **Must convert to g or justify surface-mounted sensor.** Applies to H1 vib display too. Add to Known Integrity State. |
| H2-C2 | "ISA-18.2 HI=4.0 / HH=5.0 misuses the standard — ISA-18.2 governs alarm management/rationalization, not trip levels. Numeric limits are from the OEM." | H2 alarm framing | 🟡 MEDIUM | **SURVIVES-IF-REWORDED** | Change to "OEM vibration limits, rationalized per ISA-18.2 alarm management" |
| H2-C3 | "90% classifier confidence is a single softmax number — calibration is notoriously poor on rare-event, few-shot classification. Reads as overfit theater." | H2 GDC verdict confidence display | 🟠 HIGH | **SURVIVES-IF-REPLACED** | Replace bare % with the **evidence chain + citations** that produced the verdict. Confidence % alone is the weakest possible presentation to this audience. |

**Process finding (Session AR — applies to all sessions):**
- The slug-flow scenario and the H1 scenario share the same root failure: the deciding variable was reachable from telemetry, making the L3 moat efficiency-only, not categorical. A scenario gate (4 survival tests, see DEMO_MASTER §5) has been added to `.clinerules` and must be applied to *any* new H2 candidate before code.
- Red-teaming persona and web access make a measurable difference in quality. The in-session hostile-engineer persona (same model, adversarial framing) caught both H2-10 and H2-11 without external search — which confirms the gap was primarily context/stance, not capability.

---

## Session AE — New Findings (June 10, 2026)

| RT # | Challenge | Target | Severity | Honest answer? | Fix applied |
|------|-----------|--------|----------|----------------|-------------|
| RT-NEW-2 | "Your Class H limit is listed as 270°F, 275°F, 284°F, and 300°F in four different places — and none of them is Class H (Class H = 180°C = 356°F per IEC 60085 / NEMA MG-1)" | index.html thermal copy (H3 panel, SCADA SP tile, sensor glossary) | 🔴 CRITICAL — NO-SILENT-LIE + SOURCE violation | ✅ YES — 280°F is a defensible derated operating setpoint; labeling it "Class H limit" was wrong. Class H = 356°F / 180°C (IEC 60085 — stable textbook standard). Fix: reconciled all on-screen values to 280°F; relabeled to "derated operating setpoint"; IEC 60085 / NEMA MG-1 cited for insulation rating. app.py motor_overheat methodology also updated. | **Fixed Session AE** |
| RT-NEW-3 | "Your CLAIM_LEDGER says SCADA fires a 'multivariate rate-of-change alarm, not a static threshold' — but 12/12 live runs fire the static floor" | CLAIM_LEDGER.md H1 row 2 vs. live behavior | 🟠 HIGH — internal contradiction (ledger vs system) | ✅ YES — static floor (1,020 PSI rolling avg) structurally beats the rate rule because 1,020 PSI is only ~15% below nominal. On-screen `scada_rule_fired` already shows the true rule (no UI silent lie). The CLAIM_LEDGER narrative was over-claiming. Fix: relabel to factual description of what fires. | **Ledger reworded Session AE** |
| RT-NEW-4 | "$45,000/day deferred production (H3 panel) is unsourced" | index.html H3 panel footnote | 🟡 MEDIUM | ⚠ WEAK — this is the WTX rig spread rate cited as C3 basis for the $150k gas_lock workover. Same figure; not independently unsourced. Survivable if challenged consistently. No change required — figure traces to app.py FINANCIAL_JUSTIFICATIONS gas_lock line_items. | **No change — SURVIVES with C3 citation chain** |
| RT-NEW-5 | "18-hour lead / $200k / ROI 66:1 for motor_overheat — how is that sourced?" | app.py FINANCIAL_JUSTIFICATIONS motor_overheat methodology string | 🟡 MEDIUM — 🔴 NEEDS-EXPERT | ✅ ADDRESSED — dropped "ROI: 66:1" (false precision), corrected "Class H limit 280°F" label, softened "$200,000" to "~$150k–$200k (motor + workover + deferred production)", added 🔴 NEEDS-EXPERT tag so the string cannot ship as a hard fact. Motor_overheat is not in the scripted H1/H2/H3 path but is latent in the intel feed; reachability via justify modal still needs SME confirmation before demo. | **Softened Session AE** |
| RT-L2-DRIFT | "Your 'SCADA Alarm Zone — Lead Time Consumed' banner is in red uppercase — that's a headline, not a footnote. DEMO_MASTER §3 says lead-time is demoted to supporting evidence." | index.html injectionRunning banner (legacy operations panel) + empty-state "see GDC lead time advantage" | 🟡 MEDIUM — L3-pivot fidelity | ✅ YES — DEMO_MASTER §3(6) explicitly demotes lead-time to footnote. Fix: color changed from `var(--red)` to `var(--muted)`, weight from 700 to 400, text from "SCADA Alarm Zone — Lead Time Consumed" to "SCADA alarm zone — GDC already resolved the ambiguous fault signal". Empty-state text changed from "see GDC lead time advantage" to "see GDC resolve ambiguous fault signals". Lead-time on H1/H2 Discern/Classify banners already correctly styled as `color:var(--muted)` footnotes — no change needed there. | **Fixed Session AE** |
