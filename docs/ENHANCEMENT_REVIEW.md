# GDC-PM — Code Review & Enhancement Roadmap
**Prepared:** 2026-04-30  
**Audience:** Engineering & Demo Team  
**Scope:** Full code review of all services + strategic enhancement recommendations for the power/energy operations audience

---

## Part 1 — Code Review: Bugs, Risks & Quick Fixes

### 1.1 `app.py` (fault-trigger-ui) — SQL Injection via `ORDER BY` in subquery
**File:** `gke/fault-trigger-ui/app.py`, lines 196–208  
**Issue:** The `get_alert_summary()` endpoint has a malformed SQL query — `ORDER BY event_time DESC` appears *before* `GROUP BY predicted_label`, which will cause a PostgreSQL error at runtime. `LIMIT 200` is applied before the `GROUP BY`, which means the counts are computed on the last 200 raw rows, not over a time window. This will produce misleading numbers as the table grows.

```python
# CURRENT (broken):
SELECT predicted_label, COUNT(*) AS count
FROM telemetry_events
ORDER BY event_time DESC     ← ORDER before GROUP BY = syntax error in Postgres
LIMIT 200
GROUP BY predicted_label

# FIX:
SELECT predicted_label, COUNT(*) AS count
FROM telemetry_events
WHERE event_time > NOW() - INTERVAL '30 minutes'
GROUP BY predicted_label
ORDER BY count DESC
```

### 1.2 `app.py` (fault-trigger-ui) — Dead Code in `injectFault()`
**File:** `gke/fault-trigger-ui/index.html`, lines 203–211  
**Issue:** The `injectFault('normal')` branch constructs a `payload` and `url` variable that are immediately overridden by `actualUrl` and `actualPayload`. The `FAULT_PROFILES` validation in `inject_fault()` will reject `'normal'` since it's not in `FAULT_PROFILES`, but the backend `inject-normal` endpoint is never actually called. The flow works only because `inject_fault` also accepts `normal` implicitly via the fallback.

**Fix:** Either add `"normal"` to `FAULT_PROFILES` (simplest) or clean up the dead variable assignments in the frontend and route `normal` explicitly to `/api/inject-normal`.

### 1.3 `processor.py` — DB Connection Not Health-Checked
**File:** `gke/event-processor/processor.py`, line 179–180  
**Issue:** The DB connection is established once at startup. If AlloyDB Omni restarts or times out after hours of operation, the `db_conn` handle becomes stale. `psycopg2` will raise an `InterfaceError` on the next `INSERT`, the `rollback()` will also fail, and the message will be acked — **silently dropped**.

**Fix:** Add a connection health check / reconnect wrapper around the `INSERT` block:

```python
def ensure_db_connected(conn):
    try:
        conn.cursor().execute("SELECT 1")
        return conn
    except Exception:
        log.warning("DB connection lost — reconnecting...")
        return connect_db()
```

### 1.4 `simulator.py` — Fault Injection Clears After One Asset, Not One Cycle
**File:** `gke/telemetry-simulator/simulator.py`, line 180  
**Issue:** `os.environ["INJECT_FAULT"] = "none"` is set the moment the first matching asset publishes. If `INJECT_ASSET` is set to a specific asset, this is correct. But because the environment variable is cleared inside the per-asset loop, if `INJECT_ASSET` does not match any asset exactly, the env var is *never* cleared, causing the fault to fire on every cycle indefinitely.

**Fix:** Move the clear operation *outside* the per-asset loop, after all assets have been iterated:

```python
# After the for loop:
if inject_fault != "none":
    os.environ["INJECT_FAULT"] = "none"
```

### 1.5 `app.py` (inference-api) — No Input Range Validation
**File:** `gke/inference-api/app.py`, lines 109–112  
**Issue:** The `TelemetryInput` model accepts any float. A malformed upstream message (e.g., `psi: -9999` from a sensor glitch) will produce a confident but wrong prediction. XGBoost will happily score it.

**Fix:** Add Pydantic validators with domain-appropriate bounds:

```python
class TelemetryInput(BaseModel):
    psi:       float = Field(..., ge=0,    le=2000,  description="Pressure in PSI")
    temp_f:    float = Field(..., ge=-50,  le=500,   description="Temperature in Fahrenheit")
    vibration: float = Field(..., ge=0,   le=10.0,  description="Vibration in mm")
```

### 1.6 `init-schema.yaml` — No Partition / Time-Based Pruning
**Issue:** `telemetry_events` is an unbounded, unpartitioned table. At 5-second intervals across 5 assets, it accumulates ~86,400 rows/day. After a week of demo use it will degrade Grafana query performance.

**Fix:** Add a partition by `event_time` and a background pruning job, or at minimum an auto-vacuum-friendly row TTL:

```sql
-- Add to schema init
CREATE INDEX IF NOT EXISTS idx_events_time_asset ON telemetry_events(event_time DESC, asset_id);

-- Pruning job (add as a Kubernetes CronJob)
DELETE FROM telemetry_events WHERE event_time < NOW() - INTERVAL '7 days';
```

### 1.7 `grafana-configmap.yaml` — PSI Unit Is Wrong
**File:** `gke/grafana/k8s/grafana-configmap.yaml`, line 188  
**Issue:** The PSI chart uses `"unit": "pressurebar"` — this displays values in bar notation with a "bar" suffix. The data is in PSI (1 bar ≈ 14.5 PSI). Grafana has `"unit": "pressurepsi"` for this.

**Fix:** Change to `"unit": "pressurepsi"` on panel id 5.

---

## Part 2 — Fault Trigger UI: Enhancement Recommendations

### 2.1 Per-Asset Live Status Badges
**Current:** The asset list is static buttons with no real-time state.  
**Enhancement:** Augment `/api/assets` (or add `/api/asset-status`) to return the *most recent prediction* per asset. Display a colored status badge next to each asset name:

| Status | Color | Meaning |
|---|---|---|
| `NORMAL` | Green dot | Last prediction: normal |
| `DEGRADING` | Yellow dot | bearing_wear detected in last 5 min |
| `CRITICAL` | Pulsing red | prd_failure or thermal_runaway in last 5 min |
| `STALE` | Gray dot | No data received in >30s |

This turns the asset selector from a control into a **live situational awareness panel**.

### 2.2 Alert Severity Row with Real-Time Counts
**Current:** The summary chips just show raw counts with no differentiation by severity or recency.  
**Enhancement:** Replace the chip row with a fixed 3-panel severity bar at the top of the events panel:

```
┌─────────────────────────────────────────────────────────┐
│  🔴 CRITICAL   3  │  🟠 WARNING   7  │  🟡 ADVISORY  12  │
│  PRD Failures     │  Thermal Events  │  Bearing Alerts   │
│  [last 30 min]    │  [last 30 min]   │  [last 30 min]    │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Alert Acknowledgement Workflow
**Current:** No way to mark alerts as seen/handled.  
**Enhancement:** Add an `acknowledged` boolean column to `telemetry_events`. Unacknowledged failures should be visually distinct (full-opacity red/orange rows). An operator can click a row to acknowledge it, which fades it to muted styling and records `ack_time` and `ack_user`. This is a foundational operations workflow pattern.

### 2.4 Trend Sparklines in the Event Table
**Current:** Raw numeric readings in the table are hard to contextualize without knowing the history.  
**Enhancement:** For each asset in the events table, add an inline mini sparkline (SVG, can be generated with a small JS library like uPlot or even plain SVG paths from the last 20 readings cached client-side). Operators can instantly see *direction of change*, not just current value.

### 2.5 Inject Scenario Chaining
**Current:** Each injection is a single fault type, fixed burst count.  
**Enhancement:** For demo purposes, add a "Scenario Playlist" feature: a named sequence of fault injections with delays that tells a story:

```json
{
  "name": "Compressor Cascade Failure",
  "steps": [
    { "fault": "bearing_wear",    "asset": "COMP-TX-VALLEY-01", "delay_s": 0,  "burst": 3 },
    { "fault": "bearing_wear",    "asset": "COMP-TX-VALLEY-01", "delay_s": 15, "burst": 5 },
    { "fault": "thermal_runaway", "asset": "COMP-TX-VALLEY-01", "delay_s": 30, "burst": 5 },
    { "fault": "prd_failure",     "asset": "COMP-TX-VALLEY-01", "delay_s": 60, "burst": 5 }
  ]
}
```

This makes demos far more compelling: the audience watches a bearing issue escalate to a catastrophic PRD failure — the exact scenario the system is designed to prevent.

---

## Part 3 — Grafana Dashboard: Enhancement Recommendations

### 3.1 Add a Fleet Heat Map Panel (The "At-a-Glance" Panel)
**Current:** Five time-series charts present too much information simultaneously.  
**Enhancement:** Add a **state timeline / heat map panel** at the very top showing the predicted state of each asset over time as colored bands:

```
Asset               [10m ago ────────────────── Now]
COMP-TX-VALLEY-01  ██████████████████░░░░░░░░░░████
COMP-TX-VALLEY-02  ████████████████████████████████
COMP-TX-RIDGE-01   ████████████████████████████████
COMP-TX-RIDGE-02   ████████████████████████████████
COMP-TX-BASIN-01   ████████████████████████░░░░░░░░

[Legend: ████ Normal  ░░░░ Bearing Wear  ████ Thermal  ████ PRD]
```

This is the most operationally valuable panel — an operator can see the health history of every asset in a 3-second glance.

**Query:**
```sql
SELECT event_time AS time, asset_id AS metric,
       CASE predicted_class
         WHEN 0 THEN 0 WHEN 1 THEN 3 WHEN 2 THEN 2 WHEN 3 THEN 1
       END AS value
FROM telemetry_events
WHERE $__timeFilter(event_time)
ORDER BY event_time
```
(Use Grafana's "State Timeline" panel type with value-to-color mapping.)

### 3.2 Add Confidence Score Trend Chart
**Current:** Confidence is only shown in the raw table.  
**Enhancement:** A time-series chart of *ML confidence* for the detected failure class per asset. When the model sees a bearing wear event with 52% confidence, it's a marginal call. When it hits 99.9%, action is imminent. Showing the confidence trend is a powerful differentiator: **the ML model is expressing uncertainty**, which no threshold alarm can do.

```sql
SELECT event_time AS time, asset_id AS metric, confidence AS value
FROM telemetry_events
WHERE predicted_class > 0 AND $__timeFilter(event_time)
ORDER BY event_time
```

### 3.3 Add Anomaly Rate Panel (KPI Trend)
**Enhancement:** A 24-hour anomaly rate trend — hourly percentage of readings that were predicted as failures. This gives operations leadership a high-level KPI that's meaningful for reporting:

```sql
SELECT date_trunc('hour', event_time) AS time,
       ROUND(100.0 * SUM(CASE WHEN predicted_class > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS value
FROM telemetry_events
WHERE event_time > NOW() - INTERVAL '24 hours'
GROUP BY 1 ORDER BY 1
```

### 3.4 Add a "First Occurrence" Alert Table
**Enhancement:** A dedicated panel showing *the first time each current active fault was detected* on each asset, how long it has been active, and how many times it has been re-detected. This models a real operations ticket — you need to know when the problem started, not just that it exists now.

### 3.5 Threshold Band Annotations
**Enhancement:** Add Grafana annotations to the time-series charts marking the exact timestamps when `predicted_class` transitions from `0 → non-zero`. These render as vertical lines on the chart with a tooltip. This makes the before/after contrast of a fault injection immediately visible in a demo.

---

## Part 4 — Expanding the Asset Model Beyond Compressors

### 4.1 Power/Energy Facility Asset Taxonomy

A realistic power generation or refinery facility has several distinct asset classes, each with its own telemetry signature and failure modes. Expanding the model to cover these transforms this from a "compressor demo" into a **facility-wide operations intelligence platform**.

#### Tier 1: Add Now (New Asset Types with Existing 3-Feature Model)

These assets can be modeled with the same 3-feature (PSI/Temp/Vibration) schema with different nominal ranges:

| Asset Class | ID Prefix | PSI Nominal | Temp °F Nominal | Vibration Nominal | New Failure Modes |
|---|---|---|---|---|---|
| Gas Turbine Generator | `GTG-` | 2200 PSI | 1050°F | 0.05mm | `combustion_instability`, `blade_fouling` |
| High-Voltage Transformer | `XFR-` | N/A → use `kV` | 185°F (oil) | 0.01mm | `dielectric_breakdown`, `winding_overheat` |
| Boiler Feedwater Pump | `BFP-` | 4500 PSI | 250°F | 0.08mm | `cavitation`, `seal_failure` |
| Cooling Tower Fan | `CTF-` | 50 PSI | 95°F | 0.15mm | `blade_imbalance`, `gearbox_wear` |
| Pipeline Segment | `PL-` | 1200 PSI | 60°F | 0.005mm | `stress_corrosion_crack`, `external_corrosion` |

**Key Insight:** The model architecture doesn't change — only the training data distribution and failure class names change per asset type. The `asset_type` field is the router.

#### Tier 2: Extended Sensor Inputs (Phase 2 Model)

Real operations teams instrument assets with more than 3 sensors. The most impactful additions are:

| Feature | Engineering Unit | New Failure Modes Enabled |
|---|---|---|
| `flow_rate` | GPM or SCFM | Blockage, bypass valve failure, flow reversal |
| `current_draw` | Amps | Motor overload, phase imbalance, stator fault |
| `voltage` | VAC/VDC | Under/over voltage, power quality events |
| `rpm` | Revolutions/min | Overspeeed, underspeed, rotor imbalance |
| `acoustic_emission` | dB | Early bearing fault (detects 3–6 weeks before vibration changes) |
| `oil_particle_count` | Particles/mL | Lubrication degradation (predicts bearing failure before vibration spikes) |

### 4.2 Asset Registry Pattern

Add a lightweight `asset_registry` table to AlloyDB Omni and a matching ConfigMap that drives the simulator:

```sql
CREATE TABLE asset_registry (
    asset_id       TEXT PRIMARY KEY,
    asset_type     TEXT NOT NULL,         -- 'compressor', 'turbine', 'transformer', etc.
    location       TEXT NOT NULL,         -- 'Valley Substation', 'Ridge Plant', etc.
    criticality    INTEGER NOT NULL,      -- 1 (critical) – 5 (low)
    nominal_psi    NUMERIC(8,2),
    nominal_temp_f NUMERIC(8,2),
    nominal_vib    NUMERIC(8,4),
    online_since   TIMESTAMPTZ,
    notes          TEXT
);
```

The fault-trigger-ui's `/api/assets` endpoint can then return rich asset metadata instead of just a list of strings, enabling the UI to show asset type, location, and criticality.

### 4.3 Implications for the ML Model

#### Training Data Changes

| Concern | Current State | With Multi-Asset Expansion |
|---|---|---|
| Training rows | 3,000 rows, 5 assets, 1 type | Need 3,000+ rows *per asset type* for reliable generalization |
| Feature count | 3 features | 5–10 features depending on asset class |
| Class count | 4 classes | 4–8 classes per asset type |
| Model count | 1 global model | Either: (a) 1 model per asset type, or (b) 1 model with `asset_type` as a categorical feature |

#### Recommended Model Architecture: Multi-Model per Asset Class

Train one BQML `BOOSTED_TREE_CLASSIFIER` per asset type. This is simpler, more interpretable, and avoids the model needing to learn cross-asset transfer:

```sql
-- For compressors (existing):
CREATE OR REPLACE MODEL `gdc_pm.stator_classifier` ...

-- For turbines (new):
CREATE OR REPLACE MODEL `gdc_pm.turbine_classifier`
OPTIONS(model_type='BOOSTED_TREE_CLASSIFIER', input_label_cols=['failure_type'])
AS SELECT psi, temp_f, vibration, current_draw, rpm, failure_type
   FROM `grid_reliability_gold.turbine_telemetry_raw`;
```

The Inference API can be extended to route predictions to the appropriate model:

```python
MODEL_REGISTRY = {
    "compressor":   xgb.Booster(),  # loads stator_classifier/model.bst
    "turbine":      xgb.Booster(),  # loads turbine_classifier/model.bst
    "transformer":  xgb.Booster(),  # loads transformer_classifier/model.bst
}
```

#### Feature Engineering Opportunities (for Higher Accuracy)

The current model trains on instantaneous raw readings. Operations teams benefit from *derived features* that expose time-domain patterns the raw values miss:

| Derived Feature | Formula | What It Captures |
|---|---|---|
| `psi_delta_5m` | `psi(t) - psi(t-5min)` | Rate of pressure change (PRD precursor) |
| `temp_rate_of_rise` | `(temp(t) - temp(t-10min)) / 10` | Thermal runaway early warning |
| `vibration_rms_60s` | Rolling RMS over 60s window | Smoother bearing wear signal |
| `vibration_peak_ratio` | `peak / rms` | Distinguishes bearing defect from imbalance |
| `asset_age_hours` | `NOW() - online_since` | Aging factor improves bearing wear prediction |

These require the event processor to maintain a short rolling buffer per asset (in-memory dict or Redis), compute the features, and pass them to the inference API.

---

## Part 5 — Making Alerts Stand Out: Visual Hierarchy for Operators

### 5.1 The Core Problem: Alert Fatigue

Operations teams monitoring high-data-rate streams develop "alert blindness" — when everything is color-coded, nothing stands out. The current design uses red/orange/yellow consistently, which is correct, but misses several key UX patterns from industrial HMI (Human-Machine Interface) design:

### 5.2 Principles for Industrial Alert UX

**1. Motion only for urgency**  
Only actively worsening events should animate. Stable faults are static. Use CSS `@keyframes` pulsing glow *only* on alerts with `confidence > 0.85 AND event_time > NOW() - 30s`. This means a new PRD failure literally flashes on screen; a 10-minute-old bearing wear alert is a static badge.

**2. Severity color must be absolute, not relative**  
Map severity to a consistent 4-tier system across every UI surface:

| Tier | Color | Hex | Meaning |
|---|---|---|---|
| CRITICAL | Red + pulse | `#FF1744` | Immediate safety or equipment risk (PRD failure) |
| WARNING  | Amber | `#FF9100` | Approaching unsafe threshold (thermal runaway) |
| ADVISORY | Yellow | `#FFD600` | Degradation trend, not yet urgent (bearing wear) |
| NORMAL   | Teal | `#00BFA5` | Confirmed good health |

**3. Sound cue for CRITICAL (opt-in)**  
A single short alert tone (Web Audio API, never autoplay on load) for `prd_failure` detections. Industrial control rooms use sound deliberately.

**4. "Eyes on" indicator**  
When a CRITICAL fault is detected, the tab title should change to `🔴 [3 CRITICAL] GDC-PM` via `document.title`. Operators with many browser tabs will see this immediately.

### 5.3 Fault Trigger UI — Targeted CSS/UX Changes

```css
/* Pulsing alert for fresh critical events in the table */
@keyframes critical-pulse {
  0%   { background: rgba(255,23,68,0.08); }
  50%  { background: rgba(255,23,68,0.22); }
  100% { background: rgba(255,23,68,0.08); }
}
.row-critical-fresh { animation: critical-pulse 1.5s ease-in-out infinite; }

/* Severity-tiered row backgrounds */
.row-critical  { border-left: 3px solid #FF1744; }
.row-warning   { border-left: 3px solid #FF9100; }
.row-advisory  { border-left: 3px solid #FFD600; }
```

Apply `.row-critical-fresh` only when `event_time` is within the last 60 seconds — after that, downgrade to `.row-critical`. This prevents entire tables from being animated.

### 5.4 Grafana — Alert Manager Integration

Currently, Grafana dashboards are view-only. Add Grafana Alert Rules that fire to a webhook when thresholds are crossed:

```yaml
# Alert rule: PRD Failure in last 5 minutes
condition: COUNT(*) > 0
WHERE predicted_label = 'prd_failure' 
  AND event_time > NOW() - INTERVAL '5 minutes'

# Notification: POST to fault-trigger-ui /api/webhook-alert
# (enables the UI to show a banner when Grafana independently detects a fault)
```

This creates a closed-loop alerting system where Grafana and the UI both surface the same events.

---

## Part 6 — Planning for LLM Integration (No GPU Required Now)

### 6.1 Design for LLM from Day 1, Deploy When Ready

The right pattern is to **instrument the data layer now** so that when a Vertex AI or local LLM is available, no re-architecting is needed. The LLM becomes a consumer of structured data that already exists.

### 6.2 What Data the LLM Will Need

Add the following to the `telemetry_events` table schema today:

```sql
-- Add to init-schema.yaml
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS
  ai_narrative TEXT;           -- LLM-generated plain-English explanation (populated later)

ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS
  recommended_action TEXT;     -- LLM-generated action recommendation

ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS
  similar_events_count INTEGER; -- Pre-computed: how many similar events in last 7 days
```

### 6.3 The LLM Integration Architecture (Vertex AI Gemini)

```
telemetry_events (AlloyDB)
         │
         ▼  (on predicted_class > 0)
Event Processor ──→ Vertex AI Gemini Flash API ──→ ai_narrative column
   (structured JSON context)                         (stored back in DB)
         │
         ▼
Fault Trigger UI  ──→ Renders narrative in event row tooltip
Grafana           ──→ Shows narrative in table panel
```

**Prompt Template (ready to use when Gemini is available):**

```python
NARRATIVE_PROMPT = """
You are an expert operations engineer at a power generation facility.
An ML model has detected the following condition:

Asset: {asset_id} (Type: {asset_type}, Location: {location})
Sensor Reading: PSI={psi}, Temp={temp_f}°F, Vibration={vibration}mm
ML Prediction: {predicted_label} (confidence: {confidence:.1%})
Time of Detection: {event_time}
Similar events in last 7 days: {similar_events_count}

In 2 sentences, explain what this condition means to an operations technician
and recommend the single most important immediate action.
Be specific. Do not use jargon. Do not repeat the sensor values.
"""
```

### 6.4 Near-Term LLM-Free Alternatives (Implement Now)

Until Gemini is available, deliver the same UX promise using **rule-based narrative generation**:

```python
NARRATIVES = {
    "prd_failure": (
        "The pressure relief device on {asset_id} has activated — "
        "pressure has dropped to {psi:.0f} PSI (nominal 855). "
        "Recommend immediate isolation and physical inspection of the PRD."
    ),
    "thermal_runaway": (
        "{asset_id} is operating at {temp_f:.0f}°F — {delta:.0f}°F above the "
        "safe operating limit of 150°F. Recommend checking cooling water flow "
        "and reducing load immediately."
    ),
    "bearing_wear": (
        "Elevated vibration ({vibration:.3f}mm vs nominal 0.02mm) indicates "
        "progressive bearing degradation on {asset_id}. "
        "Schedule lubrication inspection within 48 hours to prevent escalation."
    ),
}
```

These are stored in the same `ai_narrative` column — when the real LLM is activated, it simply overwrites these rule-based strings with richer language, and no UI changes are needed.

### 6.5 Vertex AI Pipeline (Cloud-Side Training Enhancement)

Once Vertex AI is in scope, add:
1. **Vertex AI Experiments** — log each BQML training run as an experiment with metrics
2. **Vertex AI Model Registry** — promote the `model.bst` through `staging → production` gates before it reaches the edge
3. **Vertex AI Feature Store** — if derived features (rolling RMS, delta values) are added, Feature Store provides the same feature values at training and serving time, preventing training/serving skew

---

## Part 7 — Implementation Priority Matrix

| Enhancement | Effort | Impact | Recommended Phase |
|---|---|---|---|
| Fix SQL bug in `get_alert_summary()` | Low | High (data quality) | **Immediate** |
| Fix simulator fault-clear race condition | Low | High (correctness) | **Immediate** |
| Add input range validation to inference-api | Low | Medium | **Immediate** |
| DB reconnect logic in event-processor | Low | High (reliability) | **Immediate** |
| Asset status badges on fault-trigger-ui | Medium | High (demo impact) | Phase 1 |
| Severity alert row with pulsing CSS | Low | High (demo impact) | Phase 1 |
| Tab title alert counter | Low | Medium | Phase 1 |
| Fleet heat map panel in Grafana | Medium | Very High (ops value) | Phase 1 |
| Confidence trend chart in Grafana | Low | High (differentiator) | Phase 1 |
| Rule-based narrative in `ai_narrative` column | Medium | High (LLM readiness) | Phase 1 |
| Multi-asset type registry & schema | Medium | High (scope expansion) | Phase 2 |
| Gas Turbine Generator asset class | Medium | High (energy story) | Phase 2 |
| Transformer asset class | Medium | High (power grid story) | Phase 2 |
| Add flow_rate + current_draw features | Medium | High (model accuracy) | Phase 2 |
| Scenario Playlist for demos | Medium | High (demo quality) | Phase 2 |
| Alert acknowledgement workflow | High | High (enterprise UX) | Phase 2 |
| Vertex AI Model Registry integration | Medium | Medium | Phase 3 |
| Vertex AI Gemini narrative generation | Medium | Very High | Phase 3 (with GPU/API access) |
| Derived feature computation (rolling RMS, deltas) | High | Very High (model accuracy) | Phase 3 |
