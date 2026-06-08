# GDC-PM Backend Architecture Conformance Report
**Date:** June 7, 2026 — Session D audit  
**Purpose:** Map every backend component against the DEMO_MASTER.md target architecture. Three buckets: ✅ Correct / ❌ Integrity violation / 🗑 Legacy/dead (safe to kill).  
**Authority:** DEMO_MASTER.md (spec) + MODEL_FOUNDATIONS.md (model spec). This report supersedes all prior architecture docs.

---

## Target Architecture (from DEMO_MASTER §1–4)

The H1/H2/H3 demo requires exactly this pipeline, and nothing else:

```
Simulator → RabbitMQ → Event Processor → [classifier only] → DB (telemetry_events)
                                  ↓
                    app.py degrade thread → RabbitMQ → (same path above)
                                  ↓
                    app.py _intel_generator → Gemma (periodic, fault-active only) → DB (field_intel)
                                  ↓
                    app.py /api/plot/forecast-data → health model → RUL / health score
                    app.py /api/intelligence-feed → field_intel + baseline docs
                    app.py /api/agent/chat → Gemma streaming → H1/H2/H3 Advisor
                    app.py /api/degrade-status → live sensor state
                    app.py /api/vizier/optimize → Vertex AI Vizier (H3)
```

---

## Component Audit

### ✅ CORRECT — Keep As-Is

| Component | File | Status |
|---|---|---|
| Telemetry simulator (14 assets, 5s intervals) | `gke/telemetry-simulator/simulator.py` | ✅ Working |
| RabbitMQ → event-processor message pipeline | `gke/event-processor/processor.py` | ✅ Working |
| XGBoost classifier inference (inference-api) | `gke/inference-api/app.py` | ✅ Working — returns predicted_label + confidence |
| `get_slopes()` 60-reading window in event-processor | `processor.py:435` | ✅ Correct architecture (feeds 8-feature ESP classifier) |
| Degrade thread `_run_degrade_thread()` | `app.py:1824` | ✅ Correct — randomized ramp, 5s steps, publishes to RabbitMQ |
| `active_degrades` in-memory state | `app.py:1541` | ✅ Correct — authoritative live sensor source |
| `_intel_generator` background thread | `app.py:498` | ✅ Correct — only runs during active fault, 20-30s intervals, Gemma + RAG |
| `/api/intelligence-feed/{asset_id}` | `app.py:4644` | ✅ Working |
| `/api/agent/chat` + fallback template | `app.py:5111` | ✅ Working (returns fallback when Gemma busy — acceptable) |
| `/api/degrade-status/{asset_id}` | `app.py:3602` | ✅ Working — returns health_score, is_active, current_sensors |
| `/api/plot/forecast-data/{asset_id}` | `app.py:3685` | ✅ Working — health model, RUL, sensor traces |
| `/api/live-telemetry/{asset_id}` | `app.py:5148` | ✅ Working |
| `/api/agent/hitl-approve` | `app.py:5036` | ✅ Working |
| `/api/recovery-status/{asset_id}` | `app.py:5098` | ✅ Working |
| `/api/vizier/optimize` (H3) | `app.py:5416` | ✅ Runs real Vertex AI Vizier GP Bandit |
| AlloyDB pgvector RAG (18 manual sections) | rag_documents table | ✅ Working |
| FAULT_PROFILES for H1/H2/H3 ESP faults | `app.py:816` | ✅ Correct gas_lock, slug_flow, sand_ingress, motor_overheat |
| `gke/shared/fault_signatures.py` | Single source of truth for fault features | ✅ Created Session U |

---

### ❌ INTEGRITY VIOLATIONS — Must Fix Before Demo

**I1 — H1 SCADA alarm fires on stale DB data (the thesis-killer)**  
- **File:** `gke/fault-trigger-ui/static/app.js:1237` + `index.html:490-492`  
- **What's wrong:** `h1RawAmps` is read from the last point of the `/api/plot/forecast-data` sensor trace (a DB query). With the 32k RabbitMQ backlog, that DB row may be hours old — showing low amps from a prior gas-lock session. The alarm condition `h1RawAmps < 50` fires against stale fault data while displaying current live amps. SCADA fires "within seconds" of inject because the DB still holds old fault readings.  
- **Fix:** Read sensor bar values exclusively from `/api/degrade-status/{asset_id}.current_sensors` (in-memory, immediate) NOT from the forecast DB trace.  
- **Integrity class:** Display-vs-reality mismatch. DEMO_MASTER §15 R6: "If the real data cannot be obtained, show '—', not a fake value."

**I2 — Missing 4th sensor bar (Vibration)**  
- **File:** `index.html:454-516`  
- **What's wrong:** H1 shows PIP / AMPS / TEMP bars. Vibration (4th gas-lock signal: cavitation onset 1.4→3.0 mm/s) is absent. Status banner says "4 sensors" — that's a lie.  
- **Fix:** Add VIB sensor bar with `↑ Higher = worse · Alarm: > 4.0 mm/s` directional context. Read from same `current_sensors` source fix as I1.

**I3 — Thermal countdown shows absurd values early**  
- **File:** `index.html:410` + `app.py:3956`  
- **What's wrong:** Banner shows "993 min to 280°F limit" at T+00:10. Root cause: `_thermal_lead = (280 − temp) / dtemp_dt`. At injection onset, `dtemp_dt ≈ 0` (temperature hasn't moved yet). Division by near-zero = absurd large number.  
- **Fix:** Gate the display: only show thermal countdown once `dtemp_dt > 0.2°F/min` (meaningful rise detected). Before that: show `"— (monitoring temp)"`. The GDC story is "classifier fires first, temp moves later" — a blank temp countdown at T+00:10 is MORE honest and more on-message than 993.

**I4 — H3 Vizier hardcoded polynomial (not XGBoost)**  
- **File:** `app.py:5293` (approx — `vizier_optimize()`)  
- **What's wrong:** `temp = 180 + 1.5(hz−45) + ...` is hardcoded. DEMO_MASTER §6 and MODEL_FOUNDATIONS §3 both require `esp_thermal.ubj` XGBoost model.  
- **Fix:** Build `esp_thermal` model (MODEL_FOUNDATIONS §5C runbook) and wire in. Until model exists: label it "physics model" in the H3 UI — not "XGBoost model." (MODEL_FOUNDATIONS §3 explicitly says to do this.)  
- **Integrity class:** Claim-vs-implementation mismatch. Not blocking H1/H2 demo.

**I5 — `esp_classifier.ubj` trained on invented ranges (Session S)**  
- **File:** `gke/inference-api/models/esp_classifier.ubj`  
- **What's wrong:** Trained on PSI 350–800 for gas_lock (actual live injection: 875–1,100). Precision 0.81 overall. HOWEVER: in practice the confidence ramp works (event-processor logs show 87-100% gas_lock confidence at developed stage), which suggests the *relative* pattern (PSI+amps declining together, slopes negative) is learned even if the absolute range is off.  
- **Fix:** Retrain per MODEL_FOUNDATIONS §7 Session W runbook. Not blocking current H1 demo — it's working in practice — but the confidence figure in the UI must acknowledge overall vs developed-stage (MODEL_FOUNDATIONS §9 decision).  
- **Priority:** Medium. Execute after H1/H2 UI is stable.

---

### 🗑 LEGACY / VESTIGIAL — Safe to Kill

**L1 — System 2: synchronous per-message Gemma call in event-processor**  
- **File:** `gke/event-processor/processor.py:186-325`, `k8s/event-processor.yaml` (`AI_NARRATIVE_ENABLED=rag`)  
- **What it is:** Legacy from the old power-generation demo. Calls Ollama/Gemma on every single RabbitMQ message (all 14 assets, 24/7) to generate `ai_narrative` + `recommended_action` columns.  
- **Why it's vestigial:** These columns are only consumed by one cell (`recommended_action`) in a secondary "recent events" table (index.html:1035). NOT used by H1/H2/H3 Advisor at all. The real GDC Advisor (System 1 = `_intel_generator` + `/api/agent/chat`) is a completely separate path.  
- **Why it's harmful:** With `prefetch_count=1` and 30s Gemma timeout, this is the sole cause of the 32k RabbitMQ backlog. 32k backlog → stale DB rows → SCADA fires in seconds (Integrity bug I1).  
- **Kill method:** `AI_NARRATIVE_ENABLED=false` in `event-processor.yaml` + `kubectl rollout restart`. One-line change. No image rebuild. Takes effect in ~30s.  
- **Impact of kill:** `ai_narrative` + `recommended_action` columns go NULL for new rows. The "recent events" table cell shows "—". Zero demo impact.

**L2 — Power-gen narrative templates in event-processor (wrong asset type)**  
- **File:** `processor.py:87-134`  
- **What it is:** `NARRATIVE_TEMPLATES` for `prd_failure`, `thermal_runaway`, `bearing_wear` — compressor/turbine fault templates. `NOMINALS` dict for `compressor`, `turbine`, `transformer`. `infer_asset_type()` maps COMP/GTG/XFR prefixes.  
- **Why vestigial:** These asset types don't exist in this demo. For `ESP-ALPHA-1`, `infer_asset_type` returns `"compressor"` (default fallback), then `generate_rag_narrative` is called with `asset_type="compressor"`, finds no matching docs, returns `(None, None)`. Zero output for every ESP event.  
- **Kill method:** Delete these functions after L1 is applied (they become dead code the moment `AI_NARRATIVE_ENABLED=false`). Can be done as part of a subsequent cleanup commit.

**L3 — `FAULT_PROFILES` non-demo entries in app.py**  
- **File:** `app.py:843-905` (after slug_flow entry)  
- **What it is:** `pulsation_dampener_failure`, `valve_failure`, `valve_washout`, `piston_seal_wear` (mud pump), `gearbox_bearing_spalling` (top_drive), `hydraulic_leak`, and others.  
- **Why not a problem:** These don't interfere with H1/H2/H3 paths and allow the demo to run other asset-class scenarios (mud pump, gas lift) if needed. Do NOT delete these. They're harmless background completeness.  
- **Verdict:** Leave in place.

**L4 — Old `/api/plot/forecast/{asset_id}` iframe endpoint**  
- **File:** `app.py:2431` — full HTML page render for chart embedding  
- **What it is:** Returns a full Plotly HTML page. No current UI uses it — H1/H2/H3 all use `/api/plot/forecast-data/{asset_id}` JSON.  
- **Kill method:** Comment out or delete. Non-critical; can defer.

**L5 — `/api/scenarios`, `/api/run-scenario` endpoints**  
- **File:** `app.py:2110-2177`  
- **What it is:** A batch scenario-runner. Not used in H1/H2/H3 UI flow.  
- **Verdict:** Defer deletion (no queue/integrity impact). Low priority.

---

## Approved Kill-List (Recommended Execution Order)

| Priority | Item | File/Action | Verification |
|---|---|---|---|
| **P0 — NOW** | Kill System 2 Gemma (L1) | `AI_NARRATIVE_ENABLED=false` in event-processor.yaml | Queue drains to <100 within 5 min; depth holds near 0 |
| **P0 — NOW** | One-time backlog purge | `rabbitmqctl purge_queue` | Queue = 0 |
| **P1 — H1 integrity** | Fix alarm source desync (I1) | `app.js` + `index.html`: read sensors from `degrade-status.current_sensors` | SCADA bars show live values, alarm never fires at inject |
| **P1 — H1 integrity** | Add Vibration bar (I2) | `index.html`: add 4th sensor bar | 4 bars visible, banner truthful |
| **P1 — H1 integrity** | Clamp thermal countdown (I3) | `index.html:410`: gate on `dtemp_dt > 0.2` | Banner shows "—" at T+00:10, real countdown starts ~T+02 |
| **P2 — H3 integrity** | Label H3 correctly (I4) | `index.html` H3 tab: "physics model" label until esp_thermal built | No false claim |
| **P3 — model retrain** | Retrain esp_classifier (I5) | MODEL_FOUNDATIONS §7 runbook | Precision ≥ 0.92 gas_lock, ≥ 0.90 slug_flow |
| **P3 — model retrain** | Build esp_thermal (I4) | MODEL_FOUNDATIONS §5C | H3 claim becomes true |
| **P4 — cleanup** | Delete L2 power-gen code | `processor.py` dead-code removal | After L1 deployed |

---

## What This Report Does NOT Address (UI Layer — Separate Track)

The H1 UI redesign (DEMO_MASTER §15 "race" framing, well schematic, 4-sensor bars, advisor layout) is a pure front-end concern and is **not part of this backend conformance audit**. The UI redesign should not begin until P0 and P1 above are verified working — otherwise we're designing on top of a broken data layer.

---

*Last updated: Session D (June 7, 2026). Update this document after each fix is verified deployed.*
