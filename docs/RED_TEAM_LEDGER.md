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

*Last updated: Session V (June 9, 2026) — initial population*
*Next update: after H2 UI ships and smoke tests pass*
