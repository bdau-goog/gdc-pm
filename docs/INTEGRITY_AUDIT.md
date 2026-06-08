# GDC-PM Integrity Audit
**Session U — June 5, 2026**  
**Scope:** `gke/fault-trigger-ui/index.html`, `gke/fault-trigger-ui/static/app.js`, `gke/fault-trigger-ui/app.py`  
**Auditor:** Cline / Session U  
**Status:** ✅ ALL V-ITEMS RESOLVED — verified Session H (June 8, 2026)

---

## ✅ Session H Reconciliation (June 8, 2026) — All Display Violations Cleared

Grep-verified against live code (`git a2eee90`). Every V-item from the Session U audit has been fixed in Sessions V/E/G:

| ID | Status | Verification |
|---|---|---|
| V-01 | ✅ FIXED | `grep "94%" index.html` → empty |
| V-02 | ✅ FIXED | `h1TopClassProb` / `h1TopClass` bound from `class_probs` in app.js:1082 |
| V-03 | ✅ FIXED | Motor state from `h1SensorTemp` thresholds (Session V; audited Session G) |
| V-04 | ✅ FIXED | `h1GvfPct` bound live from `field_intel` feed in app.js:1083–1084; `grep "68%\|22%" index.html` → empty |
| V-05 | ✅ FIXED | `grep "52%" index.html` → empty |
| V-06 | ✅ FIXED | `grep "52%" index.html` → empty |
| V-07 | ✅ FIXED | `grep "94%" app.js` → empty |
| V-08 | ✅ FIXED | `OLLAMA_DISPLAY_MODEL` removed; `app.py:4876` reports `OLLAMA_MODEL` directly |
| V-09 | ✅ FIXED | Walkthrough banner at `index.html:1068`; `$1,200` value removed (`grep` → empty) |

**No open display-integrity violations remain for H1. INTEGRITY_AUDIT.md is now archived — all items closed.**

---

---

## Classification Key

| Symbol | Class | Rule |
|--------|-------|------|
| 🔴 VIOLATION | Imitates live output but is static/fabricated | Must bind to real source or be deleted |
| 🟡 ILLUSTRATIVE | Worked example; static is permitted | Must carry visible `"Example"` / `"Walkthrough"` marker on screen |
| 🟢 FACT | Cited physical/domain constant; static is permitted | Must carry citation |

All three classes derive from global `.clinerules` §6 (Integrity — End to End), added Session U.

---

## 1. Confidence / Model Output Violations

### V-01 — H1 Physics Primer: "at 94% confidence" claim
- **File:** `index.html:377`
- **Current:** `"XGBoost detects the correlated 4-sensor signature... at 94% confidence"`
- **Problem:** Claims a specific confidence percentage for a model that has not passed non-circular verification. The trained model's developed-stage precision has not yet been measured against live injection data (verification is pending, see MODEL_FOUNDATIONS §6).
- **Fix (Session V):** Replace with "≥92% once the fault pattern is confirmed (validated precision — see How It Works tab)" and add ⓘ popover citing MODEL_FOUNDATIONS §6 threshold. Update value after Session W verification.
- **Root cause:** UI built before model existed; placeholder never updated.

### V-02 — H1 Status Badge: hardcoded "GAS LOCK - 94% confidence"
- **File:** `index.html:429`
- **Current:** `h1Injected ? 'GAS LOCK - 94% confidence' : 'Monitoring'`
- **Problem:** Status badge string is a static literal. Every demo injection always shows "94% confidence" regardless of what the model actually returns.
- **Fix (Session V):** Bind to `h1TopClass` and `h1TopClassProb` Vue data properties, which `forecast-data` already populates from `class_probs`. Pattern: `` {{ h1Injected ? `${h1TopClassLabel} · ${(h1TopClassProb*100).toFixed(0)}% confidence` : 'Monitoring' }} ``
- **Backend source:** `/api/plot/forecast-data` → `class_probs` dict (already returned, not consumed).

### V-03 — H1 Motor State: `h1ElapsedMin > 15` drives CRITICAL/NOMINAL
- **File:** `index.html:440, 442, 443, 455, 456`
- **Current:** `h1ElapsedMin > 15 ? 'CRITICAL' : 'GAS LOCK'` and same for dot color, motor label color
- **Problem:** Motor health state (NOMINAL / GAS LOCK / CRITICAL / RECOVERING) is driven by a wall-clock timer (elapsed minutes since injection), not by the actual sensor temperature. At T+16m the UI screams "MOTOR CRITICAL" when `h1SensorTemp` may still read 199°F — well below the 280°F SCADA alarm. Explicitly called out in DEMO_MASTER §15, R6, and Phase 12 Known Integrity Violations.
- **Fix (Session V):** Derive from `h1SensorTemp` thresholds matching the physics: NOMINAL (<230°F), WARMING (230–260°F), CRITICAL (≥260°F). Pattern: `h1SensorTemp >= 260 ? 'CRITICAL' : h1SensorTemp >= 230 ? 'GAS LOCK' : 'NOMINAL'`. Bind `h1SensorTemp` from `/api/degrade-status/{asset_id}` → `current_sensors.temp`.
- **Physical reference:** API RP 11S §5 Class H insulation: 180°C / 356°F continuous limit; 280°F is the SCADA alarm threshold used in this demo.

### V-04 — H1 GVF Display: hardcoded `'68%' : '22%'`
- **File:** `index.html:464`
- **Current:** `h1Injected ? '68%' : '22%'`
- **Problem:** Gas Void Fraction is hardcoded to flip between two static values on inject/nominal toggle. The actual GVF drawn for each injection is logged in `injection_events` and varies per run.
- **Fix (Session V):** Add `h1GvfPct` Vue data property. Populate from `/api/degrade-status/ESP-ALPHA-1` → the current sensor context, or from the inject response's `injection_params` field. Pre-inject: show the last 7-day rolling average from `injection_events` where `fault_type='normal'`, or display "—" if unknown.
- **Backend source:** `injection_events.vib_target` and context available in `active_degrades["ESP-ALPHA-1"]["current_sensors"]`.

### V-05 — H2 Physics Text: "AI Confidence: 52%"
- **File:** `index.html:647, 681`
- **Current:** `"AI Confidence: 52%"` and `"52% confidence 'slug_flow'"` in H2 Physics Primer/Explanation text
- **Problem:** These appear in descriptive text but present a specific confidence value as if it's a fact about how the model behaves. H2 is ⏳ NOT STARTED (DEMO_MASTER §12 Phase 2). The value 52% has no backing — slug_flow developed-stage confidence is expected to be ≥90% once the model is trained.
- **Fix (Session V):** Replace "52%" in descriptive text with "initially low, building to ≥90% as the slug pattern is confirmed" — this accurately describes the gradual-confidence behavior and doesn't commit to a fake number. Add `"Walkthrough Example"` context if showing a scenario example.

### V-06 — H2 AI Confidence Card: `52% (Ambiguous)`
- **File:** `index.html:731`
- **Current:** `<span class="h3-card-val">52% (Ambiguous)</span>`
- **Problem:** A card widget styled identically to live data output, displaying a hardcoded confidence value for an unimplemented feature (H2 is not built). A viewer can't tell this is a static mockup.
- **Fix (Session V):** Add a `"PREVIEW — not yet live"` badge to the entire H2 tab until it's implemented, OR bind this card to the real Vue data property `h2TopClassProb` (even if currently null, showing `"—"`) once H2 is built in Session V+.

### V-07 — App.js Advisor Pre-load: `'Gas lock diagnosis confirmed at 94% confidence'`
- **File:** `app.js:1413`
- **Current:** Hardcoded string used as the GDC Advisor's initial assessment template after injection.
- **Problem:** The advisor's "initial assessment" uses a static 94% confidence number, not the model's actual output. This is what the audience sees first when the fault is injected — it's the most prominent claim and it's fake.
- **Fix (Session V):** Replace with a template that interpolates live values. The Advisor stream endpoint (`/api/agent/recommend-stream`) already returns `class_probs` from the forecast endpoint — pass the actual `gas_lock` probability into the initial text. Interim fallback: `"Gas lock pattern detected · confidence building"` (no fake number).

---

## 2. Health / Identity Violations

### V-08 — `OLLAMA_DISPLAY_MODEL`: Designed to Show Wrong Model Name
- **File:** `app.py:60-63`, `app.py:4870`
- **Current:** `OLLAMA_DISPLAY_MODEL = os.environ.get("OLLAMA_DISPLAY_MODEL", OLLAMA_MODEL)` and `"ollama_model": OLLAMA_DISPLAY_MODEL if ollama_online else "offline"`
- **Problem:** The variable's own comment reads: *"Allows showing 'gemma:27b' in the UI even while gemma:2b is actually loaded."* This is a Dimension 4 violation (Health/Status Integrity) by design. If anyone queries `/api/mlops/status`, the model name returned may not be the model running.
- **Fix (Session V):** Delete `OLLAMA_DISPLAY_MODEL` entirely. Line 4870 becomes `"ollama_model": OLLAMA_MODEL if ollama_online else "offline"`. The running model name is queryable from Ollama's `/api/tags` endpoint; use that directly if cross-verification is needed.
- **Note:** `OLLAMA_MODEL` is currently `"gemma4:latest"` and the cluster IS running `gemma4:latest`, so there's no current active lie — but the infrastructure for deception exists and must be removed.

---

## 3. Architecture Tab Walkthrough (Needs "Example" Marker)

### V-09 — Architecture Tab: Live-Looking Chips With No "Walkthrough" Context
- **File:** `index.html:1459, 1514-1516, 1538, 1587, 1610, 1645, 1689, 1692, 1715, 1724`
- **Current:** Chip widgets showing `Health Score: 0.34`, `Confidence: 91.4%`, `Base RUL: 22.1 min`, `8.4% free gas at intake`, `gas_lock · Health 0.34 · Base RUL 22.1 min` — with no marker indicating these are illustrative examples.
- **Problem:** These are 🟡 ILLUSTRATIVE (Architecture-tab walkthrough of the pipeline) but look identical to the live-data widgets elsewhere in the app. A code reviewer sees `91.4%` and wonders which API returns it. A viewer may mistake a walkthrough for a live value.
- **Fix (Session V):** Add a single visible `"Walkthrough Example — not live data"` banner at the top of the Architecture tab's pipeline walkthrough section. No value changes required; just the context label. This converts 🔴 risk to 🟡 compliant. (Binding to live data in the Arch tab is possible but out of scope — the Arch tab is deliberately a step-by-step explanation, not a dashboard.)
- **Financial discrepancy sub-item:** `index.html:1800` shows `$1,200` in the architecture walkthrough. The Window of Options in the live H1 demo shows `~$2,000` for emergency shutdown (line 588) and `$1,500` for slug_flow truck roll (REMEDIATION_TIERED). `$1,200` matches neither. Align to the correct value from `REMEDIATION_TIERED` or mark as approximate.

---

## 4. Confirmed Clean (No Fix Required)

### 🟢 Physical Constants (cited, static is correct)

| Location | Value | Citation |
|---|---|---|
| index.html:361 | `284°F per API RP 11S` | ✅ Cited inline |
| index.html:815,840 | `270°F` winding temp, `$150,000` burnout penalty | ✅ API RP 11S; financial sourced in FINANCIAL_JUSTIFICATIONS |
| Multiple | `Class H insulation 180°C / 356°F` | ✅ API RP 11S, IEEE 117, NEMA MG-1 |
| Multiple | `VFD 52→44 Hz = 3,120→2,640 RPM` | ✅ Physics: RPM=(Hz×120)/poles |
| index.html:1013 | `$45k/day` deferred production | ✅ `FINANCIAL_JUSTIFICATIONS["gearbox_bearing_spalling"]` |

### 🟢 Financial Values (reconciled against app.py — no drift)

| Displayed | Source in app.py | Match? |
|---|---|---|
| `$150,000` pump replacement | `REMEDIATION_COSTS["gas_lock"] = 150000` | ✅ |
| `$150,000` unnecessary well pull (H2) | `REMEDIATION_COSTS["slug_flow"] = 150000` | ✅ |
| `$1,500` truck roll (H2) | `REMEDIATION_TIERED["slug_flow"]["early"]["cost_incurred"] = 1500` | ✅ |
| `$0` VFD speed-down | `REMEDIATION_TIERED["gas_lock"]["early"]["cost_incurred"] = 2500` — but $0 refers to *capital* cost, not deferred production | ✅ Different metric, not a contradiction |
| `$148,500` H2 net avoided | `150,000 - 1,500 = 148,500` | ✅ Correct arithmetic |
| `$1,200` arch tab (line 1800) | No match in REMEDIATION_COSTS or REMEDIATION_TIERED | ❌ **Flagged as V-09 sub-item** |

---

## 5. Summary Table — Session V Fix Queue

| ID | File | Line(s) | Class | Priority | Fix Type |
|---|---|---|---|---|---|
| V-01 | index.html | 377 | 🔴 | HIGH | Replace with verified threshold once model passes |
| V-02 | index.html | 429 | 🔴 | HIGH | Bind to `h1TopClass` / `h1TopClassProb` from `class_probs` |
| V-03 | index.html | 440-456 | 🔴 | HIGH | Bind motor state to `h1SensorTemp` numeric thresholds |
| V-04 | index.html | 464 | 🔴 | MEDIUM | Bind GVF to injection params / degrade-status API |
| V-05 | index.html | 647,681 | 🔴 | MEDIUM | Replace "52%" with behavior description |
| V-06 | index.html | 731 | 🔴 | MEDIUM | Add "PREVIEW — not live" badge to H2 tab |
| V-07 | app.js | 1413 | 🔴 | HIGH | Remove hardcoded "94%" from advisor pre-load string |
| V-08 | app.py | 60-63,4870 | 🔴 | HIGH | Delete `OLLAMA_DISPLAY_MODEL`; report `OLLAMA_MODEL` |
| V-09 | index.html | 1459-1724,1800 | 🟡→🟢 | LOW | Add "Walkthrough Example" banner; fix $1,200 amount |

**Total violations: 9 items (some span multiple lines)**  
**Total 🟡 ILLUSTRATIVE requiring marker: 1 section (arch tab)**  
**Total 🟢 FACTS verified clean: all financial values except V-09 sub-item**

---

## 6. Model Integrity Violations (separate from display — per MODEL_FOUNDATIONS.md)

These are tracked in MODEL_FOUNDATIONS.md §4 but listed here for completeness:

| ID | Description | Status |
|---|---|---|
| M-01 | `esp_classifier.ubj` (v1, Session U) trained with correct distributions but fails precision thresholds (gas_lock 0.815, slug_flow 0.746) | ❌ Not committed — git checkout'd per ML Integrity rule |
| M-02 | Session S `esp_classifier.ubj` trained on invented ranges (PSI 350–800 vs live 875–1100) | ❌ Deployed in inference-api (0 replicas) — replace in Session W |
| M-03 | `vizier_optimize()` uses hardcoded polynomial, never calls XGBoost `esp_thermal` model | ❌ Open — Session W (build esp_thermal) |
| M-04 | Non-circular verification not yet run — confusion matrix in MODEL_FOUNDATIONS §6 is empty | ❌ Pending Session W |

---

*Next: populate Known Integrity State table in NEXT_SESSION_PROMPT.md → Session V fixes all 🔴 items → Session W fixes M-01/M-02/M-04.*
