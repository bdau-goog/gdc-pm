# H2 Synthetic Documents — Approved Spec
**Version:** Session AV (June 11, 2026)
**Status:** All 5 documents approved. All G1–G6 gates pass. All Gemini red-team claims SURVIVES.
**Enforcement:** No document text may be modified without re-running G1–G6 gate check and Gemini second_opinion. No backend code or UI may display any of these documents until this file exists and is committed.

---

## Architecture — Date Templating (ALL H1/H2/H3 static seeds)

Static seed documents must NOT contain hardcoded calendar dates. All dates are computed in Python using date arithmetic anchored to `today` at backend startup:

```python
from datetime import datetime, timedelta

# H2 date anchors (compute once at startup, used for all H2 static seed docs)
SCENARIO_DATE   = datetime.now()
WORKOVER_DATE   = SCENARIO_DATE - timedelta(weeks=8)       # ~8 weeks prior
PRIOR_PULL_DATE = WORKOVER_DATE - timedelta(weeks=78)      # ~18 months prior to workover

def fmt(dt): return dt.strftime("%B %d, %Y")
```

SCADA alarm history events in Document 5 are distributed algorithmically over the
`PRIOR_PULL_DATE → SCENARIO_DATE` window (see Document 5 generation spec below).

This same pattern applies to ALL H1 and H3 static seed documents (Batch B remediation for H1
sonic log, shift note, and GOR lab report — see DEMO_MASTER §8 open items).

---

## Document 1 — Workover Completion Report
**Type:** 🔄 DYNAMIC (Gemma generates per H2 scenario run)
**G1–G6:** ALL PASS ✅ | **Red-team:** All claims SURVIVES ✅
**Session approved:** AV

### Gemma Prompt Template

The `/api/h2/scenario-replay` endpoint calls Gemma with the following template, injecting
randomized parameters. The generated text is returned in `doc_reveals[0]`.

```
Generate a realistic Permian Basin ESP workover completion report for a field technician.
Use ONLY these exact parameters and do not add diagnosis or recommendation:

Well: {WELL_ID}
Workover Date: {FILL_DATE}
WO Number: WO-{YEAR}-{SEQ}-{WELL_SEQ}
Service Company: Basin Lift Services LLC
Crew Supervisor: {TECH_INITIALS}
Motor nameplate: {MOTOR_HP} hp / {MOTOR_VOLTS} V / {MOTOR_AMPS_NP} A
Set depth: {SET_DEPTH} ft MD
Hydraulic fill product: {VENDOR} {PRODUCT_CODE}
Hydraulic fill volume: {FILL_VOLUME} gal
Startup amps: {STARTUP_AMPS} A
WHP tubing at startup: {WHP_TP} psi
WHP casing at startup: {WHP_CP} psi
Startup rate: approx. {STARTUP_RATE} BOPD / {STARTUP_WATER} BWPD

Format as a terse field report. Include: scope of work, pull conditions (motor IR,
pump wear, protector weeping — give plausible values), new assembly installation,
hydraulic fill procedure reference (SPC-ESP-003), fill completion without leakage,
startup readings. No diagnosis. No recommendation. Sign with {TECH_INITIALS}.
End with: "Company Rep sign-off: [Pending RTOC review — field copy]"
```

### Randomized Parameter Ranges

| Parameter | Range / Options |
|---|---|
| `{VENDOR}` | "TexPlex Industrial Fluids" / "Delta Basin Supply Co." / "Corsair Oilfield Products" |
| `{PRODUCT_CODE}` | "TP-450HD" / "DB-460GS" / "CP-HF460" |
| `{FILL_DATE}` | `WORKOVER_DATE` formatted (Python: `fmt(WORKOVER_DATE)`) |
| `{FILL_VOLUME}` | Uniform random: 2.9–3.3 gal |
| `{SET_DEPTH}` | Uniform random: 7750–8100 ft MD |
| `{TECH_INITIALS}` | "R.M." / "J.V." / "T.K." |
| `{STARTUP_AMPS}` | Uniform random: 82–88 A (below 100A nameplate) |
| `{STARTUP_RATE}` | Uniform random: 165–215 BOPD |
| `{STARTUP_WATER}` | Uniform random: 85–145 BWPD |
| `{WHP_TP}` | Uniform random: 290–350 psi |
| `{WHP_CP}` | Uniform random: 165–200 psi |
| `{MOTOR_HP}` | 150 (fixed) |
| `{MOTOR_VOLTS}` | 1200 (fixed) |
| `{MOTOR_AMPS_NP}` | 100 (fixed — gives headroom above startup amps) |
| `{LOT_NO}` | Random 6-digit alphanumeric |

**Note on product codes:** TP-450HD / DB-460GS / CP-HF460 — none hint at synthetic ester
chemistry by name. Incompatibility only surfaces when crossed with Document 2 OEM matrix
(which identifies the fluid CLASS from the product code via the compatibility table).

---

## Document 2 — OEM Fluid Compatibility Matrix
**Type:** 📌 STATIC SEED (no dates — truly static, no templating needed)
**G1–G6:** ALL PASS ✅ | **Red-team:** All 13 claims SURVIVES ✅ (ASTM D471 cited)
**Session approved:** AV

### Seed Text (seed once at startup — unchanged across runs)

```
PermPump Systems
ESP Series 4000 Service Manual — Rev. 3
Section 8.4: Hydraulic Fluid Compatibility — Protector/Seal Section

Table 8-2: Approved Hydraulic Fill Fluids — Protector Section
Seal material (Series 4000 standard configuration): Buna-N / NBR elastomer shaft seals

INSTRUCTIONS: Confirm hydraulic fill product fluid class against Table 8-2 BEFORE
filling. Use of an INCOMPATIBLE fluid class voids the protector warranty. All
compatibility ratings below assume operation within motor nameplate temperature range.
Higher wellbore temperatures accelerate elastomer degradation.

FLUID CLASS                                        | Buna-N/NBR  | Viton/FKM | HNBR
                                                   | [STANDARD]  | [OPTIONAL]| [OPT]
---------------------------------------------------+-------------+-----------+------
Petroleum-based mineral oil (ISO VG 100-460)       | COMPATIBLE  | COMPATIBLE| COMP
Synthetic hydrocarbon - PAO (ISO VG 100-460)       | COMPATIBLE  | COMPATIBLE| COMP
Synthetic ester-based fluid (polyol ester,         |             |           |
  diester, trimethylolpropane ester)               | INCOMPATIBLE| COMPATIBLE| COND*
Phosphate ester hydraulic fluid                    | INCOMPATIBLE| COMPATIBLE| COMP
Water-glycol hydraulic fluid (<=50% glycol)        | COND+       | COND+     | COMP

INCOMPATIBLE = Failure expected within days to weeks of continuous service.
COMPATIBLE   = Approved for use within nameplate temperature limits.
COND         = Conditionally compatible - see footnote.

*HNBR / synthetic ester: Maximum 120 deg C continuous. Consult factory if >80% ester.
+Water-glycol: Non-Arctic use only. Monitor for seal dimensional change above 60 deg C.

NOTES:
1. The Series 4000 protector ships with Buna-N (NBR) shaft seals as standard. Confirm
   seal material at order if an alternative was specified.
2. WARNING: "Synthetic" or "Synthetic Blend" on a product label does NOT distinguish
   PAO (COMPATIBLE) from ester-based (INCOMPATIBLE). Confirm base-stock fluid class
   with the supplier before use. Do not rely on label language or product name alone.
3. Initial symptoms of INCOMPATIBLE fluid exposure: seal dimensional instability,
   hardening. Observable operating symptoms (vibration anomaly, temperature rise)
   typically develop over 3-8 weeks of continuous service.

Document ID: PPS-4000-SVC-003-R3
```

### pgvector Seeding Notes
- `doc_type`: `oem_manual`
- `asset_id`: `ESP-ALPHA-3`
- `relevance_hint`: `fluid compatibility protector seal Buna-N synthetic ester hydraulic fill`
- Seed once at startup. No refresh needed (no dates).

---

## Document 3 — Prior Pull Record
**Type:** 📌 STATIC SEED (Python date-templated at startup)
**G1–G6:** ALL PASS ✅ | **Red-team (revised):** All claims SURVIVES ✅
**Session approved:** AV

### Key fixes from red-team:
- Motor IR: 0.9 MΩ (FAIL) → 8.4 MΩ (above IEEE 43-2000 minimum 2.2 MΩ for 1200V)
- Bearing condition: "NORMAL" (too vague) → quantitative (thrust washer, clearances, surface scoring)
- "Condemned" vs "no anomalous findings": reconciled — condemned = lifecycle, not failure
- Narrative role clarified: establishes healthy bearing baseline; timing argument (Week 3-4
  post-workover onset) is the decisive evidence, not just "normal 18 months ago"

### Seed Text (Python-templated)

```python
doc3_text = f"""BASIN LIFT SERVICES LLC — ESP TEARDOWN / COMPLETION REPORT
Well: ESP-ALPHA-3 | Block 7 Pad | Andrews County, WTX
Pull Date: {fmt(PRIOR_PULL_DATE)} | WO: WO-{PRIOR_PULL_DATE.strftime('%Y-%m%d')}-A3
Purpose: Scheduled replacement — production efficiency below operator target after
18-month run (moderate-sand well; operator performance-based lifecycle program).

MOTOR: Winding resistance (post-pull): 8.4 MΩ (above 2.2 MΩ minimum per IEEE 43-2000
for 1200V class). External: housing abrasion lower section — normal. Internal: windings
intact, no fluid ingress, no contamination. Disposition: returned to OEM for rewind
evaluation (standard for used motors in good condition).

PUMP: 30 stages. Stages 1-4 elevated wear consistent with intake position and sand
exposure. Remaining stages within limits. Condemned per performance-based lifecycle —
not anomalous failure. Replaced with new 7-stage AR-trim.

PROTECTOR: Shaft seal — slight weeping, lower bag (expected wear at run life).
Bearing condition: thrust washer 0.122 in (OEM tolerance 0.110-0.135 in); radial
clearances within spec; races show light polish, no scoring, no pitting, no
contamination. Internal oil: dark-brown (normal oxidation). No wellbore fluid ingress.
Condemned per performance-based lifecycle — not anomalous failure.

SUMMARY: All components within wear parameters for 18-month service interval. No
components condemned for cause (no anomalous failure). Bearings in good condition at
pull — no wear beyond light polishing. Cause of pull: scheduled replacement per
operator efficiency monitoring program.

Service Engineer: [fictional initials — randomize per demo if needed]
"""
```

### pgvector Seeding Notes
- `doc_type`: `pull_record`
- `asset_id`: `ESP-ALPHA-3`
- `relevance_hint`: `ESP teardown bearing condition prior pull protector inspection`
- Re-seed at startup (dates change). Embedding regenerated on content change.

---

## Document 4 — Lease Operator Field Tour Note
**Type:** 🔄 DYNAMIC (Gemma generates per H2 scenario run)
**G1–G6:** ALL PASS ✅ | **Red-team (revised):** All claims SURVIVES ✅
**Session approved:** AV

### Key fixes from red-team:
- Changed from "RTOC operator" to "Lease Operator" (RTOC is remote, can't do walkdown)
- Fixed amps: 87A on 100A nameplate (NOT above nameplate). SCADA setpoint 102A.
- Baseline reference: "SCADA historian ~83A" not "from memory"
- Vibration: "below SCADA vibration threshold" — not an alarm, just a walkdown observation

### Gemma Prompt Template

```
Generate a brief Permian Basin lease operator field tour note for a well stop.
Use ONLY these exact parameters. Record observations only — no diagnosis.

Well: {WELL_ID}
Tour date: {NOTE_DATE}
Tour shift: {TOUR_SHIFT}
Operator initials: {OP_INITIALS}
Tour stop time: {CHECK_TIME}
WHP tubing: {WHP_TP} psi
WHP casing: {WHP_CP} psi
Motor amps at panel display: {TOUR_AMPS} A
SCADA baseline (historian): ~{BASELINE_AMPS} A post-workover average
Motor nameplate: 100 A | SCADA overload setpoint: 102 A

Observations to include:
- Amps slightly above recent baseline — within normal operating band, no alarm
- Slight wellhead vibration above typical noted on walkdown — below SCADA threshold
- No surface anomalies, no leaks
- Action: flagged for monitoring next tour, no immediate action

Terse field note style. Sign with {OP_INITIALS}.
```

### Randomized Parameter Ranges

| Parameter | Range / Options |
|---|---|
| `{NOTE_DATE}` | `SCENARIO_DATE - timedelta(days=random(1,4))` formatted |
| `{TOUR_SHIFT}` | "Day shift (06:00-18:00)" / "Night shift (18:00-06:00)" |
| `{OP_INITIALS}` | "T.K." / "R.M." / "J.V." |
| `{CHECK_TIME}` | Random time within shift hours |
| `{TOUR_AMPS}` | Uniform random: 86–89 A |
| `{BASELINE_AMPS}` | Fixed: 83 |
| `{WHP_TP}` | Uniform random: 315–345 psi |
| `{WHP_CP}` | Uniform random: 180–200 psi |

---

## Document 5 — Well History Extract
**Type:** 📌 STATIC SEED (Python date-templated at startup)
**G1–G6:** ALL PASS ✅ | **Red-team (revised):** All claims SURVIVES ✅
**Session approved:** AV

### Key fixes from red-team:
- Added 7 minor SCADA events over 24-month window (realistic per EEMUA 191)
- Removed "efficiency decline Week 3-4" (that's GDC's retrospective analysis, not a field log)
- Fixed 36-month/18-month inconsistency: both workovers use performance-based lifecycle language
- "Production trend" notes normal performance — decline is not flagged in the static document

### Seed Text (Python-templated)

```python
# Distribute 7 minor SCADA events between PRIOR_PULL_DATE and SCENARIO_DATE
import random
window_days = (SCENARIO_DATE - PRIOR_PULL_DATE).days
event_days  = sorted(random.sample(range(30, window_days - 30), 7))
event_dates = [PRIOR_PULL_DATE + timedelta(days=d) for d in event_days]
event_types = [
    "Brief underload trip — auto-restart OK, no follow-up",
    "High-temp transient — cleared within 4 min, no intervention",
    "Underload trip — auto-restart, normal",
    "Brief overload (voltage surge) — cleared 3 min",
    "Underload trip — restart normal",
    "High-temp transient — cleared, normal",
    "Brief communication loss — restored automatically",
]

scada_events = "\n".join(
    f"  {fmt(d)}   {t}"
    for d, t in zip(event_dates, event_types)
)

doc5_text = f"""WELL HISTORY SUMMARY — ESP-ALPHA-3
Generated: {fmt(SCENARIO_DATE)} | Source: RTOC Well File / SCADA Historian
Period covered: 24 months ({fmt(PRIOR_PULL_DATE)} – {fmt(SCENARIO_DATE)})

EVENT LOG (most recent first):
  {fmt(WORKOVER_DATE)}   ESP REPLACEMENT — WO-{WORKOVER_DATE.strftime('%Y-%m%d')}-A3
                    Scope: Motor/pump/protector replacement (unscheduled —
                    vibration/amp anomaly, operator-flagged). Duration: 1 day.
                    No complications. Well returned to production 14:35 same day.

  {fmt(PRIOR_PULL_DATE)}   ESP REPLACEMENT — WO-{PRIOR_PULL_DATE.strftime('%Y-%m%d')}-A3
                    Scope: Scheduled replacement per production efficiency
                    monitoring (18-month run, efficiency below operator threshold —
                    moderate-sand lifecycle program). Duration: 1 day. No complications.

SCADA ALARM HISTORY (last 24 months — notable events):
  {fmt(SCENARIO_DATE - timedelta(days=2))}   Amp/vibration deviation — operator flagged, monitoring only
{scada_events}

PRODUCTION TREND: Post-{fmt(PRIOR_PULL_DATE)} workover through {fmt(WORKOVER_DATE)} —
normal production, consistent with expected decline curve. No anomalies flagged by
SCADA or production monitoring in this interval. Post-{fmt(WORKOVER_DATE)} workover
through {fmt(SCENARIO_DATE)}: normal initial production.

Note: Extract covers 24-month window. Full well history in RTOC well file.
"""
```

### pgvector Seeding Notes
- `doc_type`: `well_history`
- `asset_id`: `ESP-ALPHA-3`
- `relevance_hint`: `ESP well history workover event log timeline SCADA alarm history`
- Re-seed at startup (dates change). Embedding regenerated on content change.

---

## G1–G6 Summary Table — All 5 Documents

| Doc | G1 | G2 | G3 | G4 | G5 | G6 | Status |
|---|---|---|---|---|---|---|---|
| 1 Workover Completion Report | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ APPROVED |
| 2 OEM Fluid Compatibility Matrix | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ APPROVED |
| 3 Prior Pull Record | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ APPROVED |
| 4 Lease Operator Tour Note | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ APPROVED |
| 5 Well History Extract | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ APPROVED |

---

## Document-to-Claim Chain (H2 GDC Verdict Logic)

```
SENSOR PATTERN (amps elevated + vibration rising) — bearing wear signature on 4-sensor string
    ↓
GDC L2 classifier: mechanical degradation flag → routes to L3 fusion
    ↓
Doc 1 retrieved: workover 8 weeks ago, fluid {VENDOR} {PRODUCT_CODE} used
    ↓
Doc 2 cross-reference: product class = synthetic ester → Buna-N: INCOMPATIBLE
    ↓
Doc 2 Note 3: "3-8 weeks for symptoms" → timeline matches onset at Week 3-4
    ↓
Doc 3 retrieved: bearings NORMAL at last pull (18 months ago) — no pre-existing wear
    ↓
Doc 4 retrieved: operator noted amps + vibration 2 days ago — confirms progressive trend
    ↓
Doc 5 retrieved: workover 8 weeks ago confirmed, no prior anomalies in 24 months
    ↓
GDC VERDICT: "Bearing contamination from well fluid ingress through seal degraded by
incompatible workover fluid. Root cause: {VENDOR} {PRODUCT_CODE} (synthetic ester class)
incompatible with Buna-N seals per OEM matrix. Correct action: flush + reseal protector
(~$8k-$15k) — NOT pump pull. Bearing wear is real but caused by the ingress pathway,
not mechanical wear age."
```

---

## Open Items (carry forward to NEXT_SESSION_PROMPT)

1. **H2-C1 flush+reseal cost ~$8k–$15k** — still 🔴 NEEDS-EXPERT. Display as soft range.
   No hard public source found in two Gemini searches. Cannot harden without OEM field
   service quote.

2. **H1 static seed date-templating** — H1 field_intel documents (sonic log, shift note,
   GOR lab report) still have hardcoded dates. Address as part of H1 Batch B remediation
   (see DEMO_MASTER §8). Apply same Python date-templating pattern.

3. **H3 static seeds** — Check if H3 has any date-bearing static documents. Apply pattern
   if needed.
