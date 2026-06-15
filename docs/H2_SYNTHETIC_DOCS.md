# H2 Synthetic Documents — Approved Spec (Paraffin/Wax Scenario)
**Version:** Session BS (June 15, 2026)
**Status:** All 3 documents in the H2 doc-stack approved. All G1–G6 gates pass. All Gemini red-team claims SURVIVES.
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

---

## Document 1 — Chemical Service Log (Hot-Oil / Paraffin Inhibitor Treatment)
**Type:** 🔄 DYNAMIC (Gemma/Backend generates per H2 scenario run)
**G1–G6:** ALL PASS ✅ | **Red-team:** All claims SURVIVES ✅
**Session approved:** BS

### Text Template
```
CHEMICAL SERVICE LOG — HOT-OIL / PARAFFIN INHIBITOR TREATMENT
Well: ESP-ALPHA-3 | Andrews County, WTX
Service Company: {PM_VENDOR}
Operator PM Instruction: {PM_INTERVAL_DAYS}-day hot-oil treatment cycle

TREATMENT HISTORY:
  Last completed treatment: {LAST_HOIL_DATE}
  Next treatment due:       {PM_DUE_DATE}
  Current date:             {SCENARIO_DATE}
  Status:                   {PM_OVERDUE_DAYS} DAYS PAST DUE

DELAY NOTE ({PM_DUE_DATE}):
  Scheduled hot-oil unit not available. Unit committed to Midland Basin
  pad operations through end of month. Treatment rescheduled.
  As of {SCENARIO_DATE}: no confirmed reschedule date on file.

WELL NOTES: High-wax crude confirmed. WAT ~{WAT_F}°F per PVT report.
  Operator standing instruction: treat every {PM_INTERVAL_DAYS} days maximum;
  treat sooner if vibration or amp anomaly observed.

IMMEDIATE ACTION: Dispatch hot-oil unit. Well shows vib/amp deviation
  consistent with tubing restriction. Do NOT delay further.
```

---

## Document 2 — Fluid PVT Report
**Type:** 📌 STATIC SEED (Python date-templated at startup)
**G1–G6:** ALL PASS ✅ | **Red-team:** All claims SURVIVES ✅
**Session approved:** BS

### Text Template
```
FLUID PVT REPORT — ESP-ALPHA-3
Andrews County, WTX | Analyzed: {WORKOVER_DATE}
Laboratory: PBFA-{WORKOVER_YEAR}-A3

CRUDE OIL CHARACTERIZATION:
  API Gravity:              28.4° API
  Gas-Oil Ratio:            820 scf/bbl
  Water Cut:                22%
  Wax Content (by weight):  8.3% — HIGH
  Pour Point:               38°F
  Wax Appearance Temp (WAT): {WAT_F}°F (ASTM D5985 cross-polarization)

PARAFFIN DEPOSITION RISK: HIGH
  Tubing wall temperature drops below WAT in upper 1,500–2,000 ft of
  production string. Estimated radial deposition rate: 0.5–1.2 mm/month.
  At {TOTAL_DAYS_SINCE_TREATMENT} days since last treatment,
  restriction may significantly reduce tubing flow area.

SYSTEM CURVE NOTE (API RP 11S):
  Tubing restriction → lower producing rate → reduced drawdown → PIP elevation.
  Pump intake operates above WAT at depth — pump itself is not the deposition zone.

RECOMMENDED TREATMENT INTERVAL: {PM_INTERVAL_DAYS} days maximum.
```

---

## Document 3 — Prior Pull Record (ESP Teardown/Completion Report)
**Type:** 📌 STATIC SEED (Python date-templated at startup)
**G1–G6:** ALL PASS ✅ | **Red-team:** All claims SURVIVES ✅
**Session approved:** BS

### Text Template
```
BASIN LIFT SERVICES LLC — ESP TEARDOWN / COMPLETION REPORT
Well: ESP-ALPHA-3 | Block 7 Pad | Andrews County, WTX
Pull Date: {PRIOR_PULL_DATE} | WO: WO-{PRIOR_PULL_YEAR_MONTH_DAY}-A3
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

Service Engineer: [Basin Lift Services LLC field record]
```

---

## G1–G6 Summary Table — All 3 Documents

| Doc | G1 | G2 | G3 | G4 | G5 | G6 | Status |
|---|---|---|---|---|---|---|---|
| 1 Chemical Service Log | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ APPROVED |
| 2 Fluid PVT Report | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ APPROVED |
| 3 Prior Pull Record | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ APPROVED |

---

## Document-to-Claim Chain (H2 GDC Verdict Logic)

```
SENSOR PATTERN (amps elevated + vibration rising) — bearing wear signature on 4-sensor string
    ↓
GDC L2 classifier: mechanical degradation flag → routes to L3 fusion
    ↓
Doc 1 retrieved: last hot-oil treatment was Day 0, overdue by 52 days (vendor truck delay)
    ↓
Doc 2 cross-reference: crude has WAT of 118°F and high wax content (8.3%) → high paraffin risk
    ↓
Doc 3 retrieved: prior pull record 18 months ago shows bearings were normal with light polish (rules out bearing age)
    ↓
GDC VERDICT: "Paraffin/wax deposition in production tubing — NOT bearing wear. Hot-oil PM treatment
52 days overdue (last: Day 0, due: Day 90). Vendor delay logged. PVT confirms WAT 118°F, 8.3% wax content.
PIP rising is the hydraulic signature of tubing restriction (restriction → lower flow → less drawdown → PIP ↑).
Temperature flat confirms hydraulic restriction, not mechanical bearing wear (which would generate friction/heat).
Prior pull record confirms bearings were normal — age hypothesis eliminated. Correct action: hot-oil truck
(~$3k–$6k, surface-only, no pull). Pump pull (~$70k–$100k) addresses bearing symptom only; wax remains."
```
