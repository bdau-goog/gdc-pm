# GDC Operations Intelligence — Stakeholder Brief

**Audience:** Customer executives and business stakeholders  
**Version:** Session BS+3 (June 15, 2026) — H2 Paraffin/Wax Scenario Confirmed  
**Source of truth for value proposition language:** DEMO_MASTER.md §3 (locked)  
**Claim compliance:** All hard figures are tagged OUR-CODE or TEXTBOOK (SURVIVES). Ranges marked as estimates are labeled accordingly.  
**H2 scenario status:** Paraffin/wax deposition narrative — passed hostile-engineer red-team (Session BG). Elastomer-seal scenario permanently retired.

---

## What We Built

### H1 — Discern: Reading the Situation

When an oil well's pump begins to struggle, it shows the same sensor pattern for two very different problems — one that is fixed cheaply by slowing the pump down, and one where slowing the pump down destroys it. The difference between a \$2,500 adjustment and a \$150,000 workover depends on knowing *which* situation the well is actually in. That answer is not in the sensor data. It is in field documents: the operator's shift note from that morning, a recent fluid analysis, a record of what happened the last time this well was worked on.

GDC Discern fuses those documents against the live sensor signal in seconds and hands the operator a plain-language verdict — cited, auditable, and available on every well simultaneously, regardless of the hour or how many other wells are alarming at the same time.

### H2 — Classify: Finding the Right Fix

When a pump gradually degrades over several weeks, the sensor pattern typically points to one cause: bearing wear. A standard AI monitoring platform correctly identifies the symptom — and recommends the standard response: pull the pump and rebuild it. That costs somewhere in the range of \$70,000–\$100,000.

GDC Classify goes further. It reads three documents the monitoring platform cannot see: a chemical vendor service log showing the well's 90-day paraffin treatment was 52 days overdue due to a vendor logistics delay; a fluid lab report confirming the crude's high wax content and recommended treatment interval; and the last pull record showing the pump bearings were inspected as normal 18 months ago. The actual root cause is paraffin deposition in the production tubing — the pump is working harder against a restriction, not against failing bearings. The correct response is a surface hot-oil truck job (estimated $3,000–$6,000). The $70,000–$100,000 pump pull is averted entirely. The expensive fix addresses the symptom. GDC finds the cause.

### H3 — Optimize: Running the Field, Not Just the Pump

Once the system knows which wells are healthy, the next question is: what is the most productive way to run them together? Six wells on the same pad share a gas-handling limit set by the midstream contract. Every barrel of oil produced comes with associated gas, and different wells produce very different amounts of gas per barrel. Running every well at the same speed wastes the shared gas budget on the wells that produce the most gas per barrel, leaving production capacity unused on the wells that produce the least.

GDC Optimize ranks the wells by their gas efficiency, allocates the gas budget to the most efficient wells first, and throttles only the wells that are expensive in gas terms. In the demonstration scenario, this approach recovers approximately 78 additional barrels per day — roughly \$369,000 in additional revenue over a 90-day period — while keeping the gas ceiling exactly satisfied. The safety constraint that protects each motor runs locally, inside the operator's boundary, regardless of whether the internet link is available.

---

## The Problem Each Horizon Solves

| Horizon | The Problem Without GDC | What GDC Delivers | What It Avoids |
|---|---|---|---|
| **H1 — Discern** | Ambiguous sensor signal forces a conservative shutdown on every unloading event — the safe default when cause is unknown | Cited diagnosis in seconds: correct low-cost action where safe, correct shutdown where necessary | \$150k workover from the wrong intervention; unnecessary production deferral from unnecessary shutdown |
| **H2 — Classify** | AI monitoring flags bearing wear and recommends a pump pull — correct symptom, wrong root cause, expensive fix | Reads the vendor service log + fluid lab report + pull history; identifies overdue paraffin treatment as root cause; recommends a surface hot-oil truck job | \$70k–\$100k pump pull averted; estimated surface treatment ~\$3k–\$6k *(soft estimate — verify with field service vendor)* |
| **H3 — Optimize** | Uniform throttle is the safe default when there is no cross-well optimizer — leaves production on the table | Allocates the gas budget to the most efficient wells first; recovers deferred production within the contract ceiling | Approximately 78 bbl/d of deferred production under uniform throttle *(figure from current scenario parameters — will vary by field)* |

---

## The Honest Relationship with SCADA

GDC is not a replacement for SCADA. It works alongside it. A plain-language picture of the three tiers:

**Alarms (what SCADA does):** SCADA monitors individual sensor readings against hard limits. When a reading crosses its limit, SCADA alarms and, for the most critical conditions, shuts the equipment down to protect it. This is the foundation of safe operations. GDC does not compete here, and does not claim SCADA fails to protect equipment — it does.

**Patterns (what advanced AI monitoring does):** Predictive monitoring platforms (products from GE, AVEVA, Aspen, and others) go further: they watch how multiple sensors move *together* over time and flag when the pattern looks like the early stages of a known fault, before any individual reading crosses its alarm limit. This is a real capability, and GDC does not claim these platforms are missing it.

**Context (what GDC adds):** Neither SCADA nor any current monitoring platform reads the *documents* — shift notes, workover reports, lab analyses, service records — in real time as part of a live diagnosis. Those documents contain the context that determines whether a sensor pattern means one thing or another, and what the right action is. That is the gap GDC closes. It is not a matter of speed or workload; it is an architectural difference. No current SCADA or monitoring product is designed to fuse unstructured field documents into a live fault diagnosis.

> *"GDC does not tell operators what SCADA already knows. It tells them what SCADA architecturally cannot."*

---

## The Same Capability in Other Industries

The pattern GDC exploits is not specific to oil wells. In every industrial setting, sensors and monitoring platforms reach a diagnostic boundary — a point where the answer depends on something that happened in the past and was recorded in a document, not in a data stream. GDC resolves that boundary.

| Industry | The Ambiguous Signal | The Context in Documents (not sensors) | The GDC Resolution |
|---|---|---|---|
| **Power & Energy** | Transformer gas levels rising / turbine vibration anomaly | Maintenance log, load history, prior fault record, service schedule | Distinguishes normal aging from incipient fault; recommends targeted inspection vs. full outage |
| **Manufacturing** | Motor or pump bearing temperature rising | Lubrication log, production schedule, prior rebuild record, OEM service bulletin | Identifies missed lubrication interval vs. mechanical wear — different repairs, different urgency |
| **Mining** | Haul-truck driveline signal degrading | Service history, haul-road condition report, OEM technical service bulletin, shift note | Distinguishes road-induced stress from component wear — avoids unnecessary teardown |

These are not hypothetical extensions. They are the same three-tier architecture (sensor alarm → pattern detection → document context) applied to different assets. The platform is the same; the field documents change.

---

## Why "Inside the Perimeter" Matters

The AI-powered diagnostic advisor — the capability major APM platform vendors are building for cloud deployment in 2025–2026 — GDC delivers inside the operator's sovereign boundary, on open-weight AI models, without sending operational data to a public cloud service.

For many operators, that distinction is not a preference — it is a requirement.

**Isolation and self-sufficiency.** Under standard industrial security frameworks (IEC 62443), production and operations technology data must not cross the public internet. Beyond compliance, the internet link can fail at the worst possible moment — during a price spike, a storm, a process upset. GDC's AI runs locally. When the connection drops, the system keeps working.

**Data residency.** Reservoir data, production history, and well files are commercially sensitive. National operators and operators in data-residency jurisdictions cannot send this data to a public cloud service, regardless of encryption. GDC keeps the data where it already lives.

**Governance and intellectual property.** GDC uses open-weight AI models (Gemma) running on-premises. Proprietary operational data — sensor readings, field documents, diagnostic queries — never passes through a third-party model provider's infrastructure and is never logged externally.

> *"The data cannot come to the AI, so the AI goes to the data — GDC puts Google's AI stack inside the operator's sovereign boundary."*

---

*For the full technical specification, scenario physics, and claim sourcing, see `docs/DEMO_MASTER.md`. For the verified claim register, see `docs/CLAIM_LEDGER.md`.*
