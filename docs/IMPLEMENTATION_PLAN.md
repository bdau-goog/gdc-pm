# GDC-PM — Phased Implementation Plan
**Prepared:** 2026-04-30  
**Based on:** ENHANCEMENT_REVIEW.md code review and stakeholder requirements  
**Audience:** Engineering Team

---

## Summary of Completed Work (This Session)

The following bugs were fixed and UI enhancements were implemented. All changes
are committed to the working tree and ready for a container rebuild.

| File | Change |
|---|---|
| `gke/fault-trigger-ui/app.py` | Fixed broken SQL in `get_alert_summary()` (ORDER before GROUP BY); removed dead `inject_normal` endpoint; added `"normal"` to `FAULT_PROFILES`; added `/api/asset-status` and `/api/asset-metadata` endpoints; added `ASSET_REGISTRY` with type/location/criticality data |
| `gke/fault-trigger-ui/index.html` | Full UX rebuild: severity bar (Critical/Warning/Advisory), per-asset live status dots, ⓘ info buttons with rich pop-up tooltips for all assets and all fault types, confidence mini-bar in events table, pulsing row animation for fresh CRITICAL events, color-coded row severity left-borders, browser tab title alert counter |
| `gke/telemetry-simulator/simulator.py` | Fixed fault-clear race condition — `INJECT_FAULT` env var now cleared after the full asset loop, not inside it; added warning log when asset name doesn't match |
| `gke/inference-api/app.py` | Added Pydantic `Field` bounds validation (PSI: 0–2000, Temp: -50–600°F, Vibration: 0–20mm) to reject sensor glitch values before they score |
| `gke/event-processor/processor.py` | Added `ensure_db_connected()` with reconnect logic; bound via `nonlocal` in the message handler closure so the processor survives AlloyDB restarts without pod restart |

**Rebuild required:** `fault-trigger-ui`, `event-processor`, `inference-api`, `telemetry-simulator`

```bash
# Rebuild and push all modified services
bash ~/bdau-basic-vpc/scripts/push-image.sh fault-trigger-ui
bash ~/bdau-basic-vpc/scripts/push-image.sh event-processor
bash ~/bdau-basic-vpc/scripts/push-image.sh inference-api
bash ~/bdau-basic-vpc/scripts/push-image.sh telemetry-simulator

# Restart deployments to pull new images
kubectl rollout restart deployment/fault-trigger-ui    -n gdc-pm
kubectl rollout restart deployment/event-processor     -n gdc-pm
kubectl rollout restart deployment/inference-api       -n gdc-pm
kubectl rollout restart deployment/telemetry-simulator -n gdc-pm
```

---

## Phase 0 — Hardening (1–2 days)

These are small, isolated changes to address the remaining items from the
code review that were not yet implemented.

### 0.1 Fix Grafana PSI Unit
**File:** `gke/grafana/k8s/grafana-configmap.yaml`, panel id 5  
**Change:** `"unit": "pressurebar"` → `"unit": "pressurepsi"`  
**Effort:** 5 minutes  

### 0.2 Add Table Pruning CronJob
**File:** New `gke/alloydb-omni/k8s/prune-events.yaml`  
At 5s interval × 5 assets = 86,400 rows/day. After 7 days, queries slow.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: prune-telemetry-events
  namespace: gdc-pm
spec:
  schedule: "0 3 * * *"          # 03:00 UTC daily
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: prune
              image: postgres:15-alpine
              env:
                - name: PGHOST
                  value: "alloydb-omni"
                - name: PGPASSWORD
                  valueFrom:
                    secretKeyRef: { name: alloydb-secret, key: password }
              command:
                - psql
                - -U
                - postgres
                - -d
                - grid_reliability
                - -c
                - "DELETE FROM telemetry_events WHERE event_time < NOW() - INTERVAL '7 days';"
```

### 0.3 Add Composite Index for Grafana Queries
**File:** `gke/alloydb-omni/k8s/init-schema.yaml`  
Add to the schema init SQL:
```sql
CREATE INDEX IF NOT EXISTS idx_events_time_asset
  ON telemetry_events(event_time DESC, asset_id);
```
This index directly serves the time-series queries Grafana runs most frequently.

### 0.4 Add Schema Columns for Future LLM Narrative
**File:** `gke/alloydb-omni/k8s/init-schema.yaml`  
Add columns now so no migration is needed later:
```sql
ALTER TABLE telemetry_events
  ADD COLUMN IF NOT EXISTS ai_narrative        TEXT,
  ADD COLUMN IF NOT EXISTS recommended_action  TEXT,
  ADD COLUMN IF NOT EXISTS similar_events_count INTEGER;
```

---

## Phase 1 — Operational UX Uplift (1 week)

Goal: Make the solution feel like a real operations platform to a power/energy audience.
These changes require code but no infrastructure changes.

### 1.1 Grafana: Fleet State Timeline Panel
**Priority:** Very High — single highest-impact Grafana addition  
**File:** `gke/grafana/k8s/grafana-configmap.yaml`

Add a new panel at the top of the dashboard using Grafana's **State Timeline**
panel type. Each row is one asset; each column is a time bucket; color = ML
predicted state. An operator reads the entire fleet health in 3 seconds.

```json
{
  "type": "state-timeline",
  "title": "Fleet Health Timeline — All Assets",
  "gridPos": { "x": 0, "y": 0, "w": 24, "h": 6 },
  "options": { "mergeValues": true, "showValue": "never" },
  "fieldConfig": {
    "defaults": {
      "mappings": [
        { "type": "value", "options": { "0": { "text": "Normal",        "color": "#00BFA5" } } },
        { "type": "value", "options": { "1": { "text": "Bearing Wear",  "color": "#FFD600" } } },
        { "type": "value", "options": { "2": { "text": "Thermal",       "color": "#FF9100" } } },
        { "type": "value", "options": { "3": { "text": "PRD Failure",   "color": "#FF1744" } } }
      ]
    }
  },
  "targets": [{
    "rawSql": "SELECT event_time AS time, asset_id AS metric, CASE predicted_class WHEN 0 THEN 0 WHEN 3 THEN 1 WHEN 2 THEN 2 WHEN 1 THEN 3 END AS value FROM telemetry_events WHERE $__timeFilter(event_time) ORDER BY event_time",
    "format": "time_series"
  }]
}
```

### 1.2 Grafana: ML Confidence Trend Chart
**Priority:** High — differentiates ML from threshold alarms in every demo  
**File:** `gke/grafana/k8s/grafana-configmap.yaml`

Add a time-series panel showing confidence score only for predicted failures.
The talking point: "A threshold alarm fires a binary yes/no. The ML model
tells you how certain it is — and that certainty trend is itself a leading
indicator."

```sql
SELECT event_time AS time, asset_id AS metric, confidence AS value
FROM telemetry_events
WHERE predicted_class > 0 AND $__timeFilter(event_time)
ORDER BY event_time
```

### 1.3 Grafana: Anomaly Rate KPI (24h Trend)
**Priority:** High — meaningful for leadership dashboards  
```sql
SELECT date_trunc('hour', event_time) AS time,
       ROUND(100.0 * SUM(CASE WHEN predicted_class > 0 THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0), 2) AS value
FROM telemetry_events
WHERE event_time > NOW() - INTERVAL '24 hours'
GROUP BY 1 ORDER BY 1
```

### 1.4 Fault Trigger UI: Rule-Based Narrative (LLM Placeholder)
**Priority:** High — delivers AI narrative experience without GPU  
**File:** `gke/fault-trigger-ui/app.py` (extend `get_recent_events`)  
**File:** `gke/event-processor/processor.py` (generate narrative on INSERT)

Add `generate_narrative()` to the event processor. When `predicted_class > 0`,
compute a rich plain-English description and store it in `ai_narrative`:

```python
NARRATIVES = {
    "prd_failure": (
        "The pressure relief device on {asset_id} has activated. Pressure has "
        "dropped to {psi:.0f} PSI against a nominal of 855 PSI. "
        "Recommend immediate isolation and physical inspection of the PRD. "
        "Estimated downtime: 4–8 hours."
    ),
    "thermal_runaway": (
        "{asset_id} is operating at {temp_f:.0f}°F — {delta:.0f}°F above "
        "the 150°F safety limit. Pressure is within normal range, which means "
        "a standard pressure alarm would not have fired. "
        "Reduce load immediately and check cooling water flow."
    ),
    "bearing_wear": (
        "Vibration on {asset_id} has reached {vibration:.3f}mm — "
        "{ratio:.0f}× the nominal 0.02mm. This indicates progressive bearing "
        "surface fatigue. Schedule lubrication inspection within 48 hours "
        "to prevent escalation to shaft seizure."
    ),
}
```

When the LLM is activated (Phase 3), this function is replaced with a
Vertex AI Gemini API call. The column and all UI display code remain unchanged.

### 1.5 Fault Trigger UI: Display Narrative in Event Table
**Priority:** Medium — completes the LLM readiness story  
**File:** `gke/fault-trigger-ui/index.html`

Add a collapsible "detail row" below each non-normal event row that shows
the `ai_narrative` text. Collapsed by default; expands on click.
This requires no backend change — just reading the `ai_narrative` field
that `get_recent_events` already returns once the column is populated.

---

## Phase 2 — Asset Expansion (2–3 weeks)

Goal: Expand from 5 compressors to a realistic multi-asset power/energy facility.
This requires new training data, new model training, and simulator expansion.

### 2.1 Add `asset_registry` Table to AlloyDB Schema
**File:** `gke/alloydb-omni/k8s/init-schema.yaml`

```sql
CREATE TABLE IF NOT EXISTS asset_registry (
    asset_id       TEXT PRIMARY KEY,
    asset_type     TEXT NOT NULL,
    asset_subtype  TEXT,
    location       TEXT NOT NULL,
    criticality    INTEGER NOT NULL DEFAULT 3,  -- 1=critical, 5=low
    nominal_psi    NUMERIC(10,2),
    nominal_temp_f NUMERIC(8,2),
    nominal_vib    NUMERIC(8,4),
    online_since   TIMESTAMPTZ,
    notes          TEXT,
    model_name     TEXT NOT NULL DEFAULT 'stator_classifier'
);

-- Seed with current assets
INSERT INTO asset_registry VALUES
  ('COMP-TX-VALLEY-01', 'compressor', 'reciprocating', 'Valley Substation', 2, 855, 112, 0.02, '2023-06-15', NULL, 'stator_classifier'),
  ('COMP-TX-VALLEY-02', 'compressor', 'reciprocating', 'Valley Substation', 3, 855, 112, 0.02, '2023-06-15', NULL, 'stator_classifier'),
  ('COMP-TX-RIDGE-01',  'compressor', 'centrifugal',   'Ridge Plant',       1, 855, 112, 0.02, '2022-11-01', NULL, 'stator_classifier'),
  ('COMP-TX-RIDGE-02',  'compressor', 'centrifugal',   'Ridge Plant',       2, 855, 112, 0.02, '2022-11-01', NULL, 'stator_classifier'),
  ('COMP-TX-BASIN-01',  'compressor', 'screw',         'Basin Station',     2, 855, 112, 0.02, '2024-01-10', NULL, 'stator_classifier')
ON CONFLICT DO NOTHING;
```

The `model_name` field is the routing key that tells the Inference API which
XGBoost model to use for this asset type.

### 2.2 New Asset Class: Gas Turbine Generator
**New assets:** `GTG-VALLEY-01`, `GTG-RIDGE-01`

| Sensor | Nominal | Failure Modes |
|---|---|---|
| PSI | 2,200 PSI | Combustion instability (drops to ~1,800) |
| Temp °F | 1,050°F | Blade fouling (climbs to ~1,150°F) |
| Vibration | 0.05mm | Rotor imbalance (climbs to >0.35mm) |

**Training data:** New `seed-turbine-data.py` generating 3,000+ rows with
4 classes: `normal`, `combustion_instability`, `blade_fouling`, `rotor_imbalance`

**BQML model:**
```sql
CREATE OR REPLACE MODEL `grid_reliability_gold.turbine_classifier`
OPTIONS(
  model_type='BOOSTED_TREE_CLASSIFIER',
  input_label_cols=['failure_type'],
  num_parallel_tree=6
)
AS SELECT psi, temp_f, vibration, failure_type
   FROM `grid_reliability_gold.turbine_telemetry_raw`;
```

### 2.3 New Asset Class: High-Voltage Transformer
**New assets:** `XFR-VALLEY-01`, `XFR-RIDGE-01`, `XFR-BASIN-01`

Transformers use `kV` (not PSI) for primary sensor, oil temperature, and
acoustic emission. This requires extending `telemetry_events` with:
```sql
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS kv NUMERIC(8,2);
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS acoustic_db NUMERIC(8,2);
```

| Sensor | Nominal | Failure Modes |
|---|---|---|
| kV | 115 kV | Dielectric breakdown (<95 kV), overvoltage (>125 kV) |
| Temp °F (oil) | 185°F | Winding overheat (>210°F) |
| Vibration | 0.01mm | Core loosening (>0.08mm) |

### 2.4 Inference API: Model Registry Router
**File:** `gke/inference-api/app.py`

Extend `TelemetryInput` to accept an optional `asset_type` field.
Load all models at startup into a registry dict. Route predictions by type:

```python
MODEL_REGISTRY: dict[str, xgb.Booster] = {}

# Load all available models at startup
for model_name in ["stator_classifier", "turbine_classifier", "transformer_classifier"]:
    path = f"{GCS_MODEL_BUCKET}/{model_name}/model.bst"
    try:
        b = xgb.Booster()
        b.load_model(download_from_gcs(path))
        MODEL_REGISTRY[model_name] = b
        log.info(f"Loaded model: {model_name}")
    except Exception as e:
        log.warning(f"Model {model_name} not found, skipping: {e}")
```

### 2.5 Telemetry Simulator: Multi-Asset-Type Support
**File:** `gke/telemetry-simulator/simulator.py`

Refactor `ASSETS` list into an `ASSET_CONFIG` dict loaded from the
`asset_registry` table at startup (via AlloyDB). Each asset type maps to
its own `normal_reading()` generator function.

### 2.6 Demo Scenario Playlist
**Files:** `gke/fault-trigger-ui/app.py`, `index.html`

Add `/api/run-scenario` endpoint accepting a named scenario. Implement
`"Cascade Failure"` as the default:

```python
SCENARIOS = {
    "cascade_failure": {
        "name": "Compressor Cascade Failure",
        "description": "Bearing wear escalates to thermal runaway, then catastrophic PRD pop.",
        "steps": [
            {"fault": "bearing_wear",    "asset": "COMP-TX-VALLEY-01", "delay_s": 0,  "burst": 3},
            {"fault": "bearing_wear",    "asset": "COMP-TX-VALLEY-01", "delay_s": 20, "burst": 5},
            {"fault": "thermal_runaway", "asset": "COMP-TX-VALLEY-01", "delay_s": 40, "burst": 5},
            {"fault": "prd_failure",     "asset": "COMP-TX-VALLEY-01", "delay_s": 70, "burst": 5},
        ]
    }
}
```

In the UI, add a "▶ Run Demo Scenario" button above the fault grid.

---

## Phase 3 — AI Narrative & Vertex AI Integration (4–6 weeks)

Prerequisite: Either Vertex AI API access (cloud-side LLM) **or** a GPU node
added to the GKE cluster for local inference.

### 3.1 Vertex AI Gemini Flash Integration
**Target:** Replace `generate_narrative()` rule-based templates with live
Vertex AI Gemini Flash API calls in the event processor.

**Cost note:** Gemini Flash is $0.075 per 1M input tokens. At 5s telemetry
intervals × 5 assets × 12% failure rate, this system generates ~1,440
failure events/day at a cost of approximately **$0.004/day** — negligible.

```python
import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project=GCP_PROJECT, location="us-central1")
gemini = GenerativeModel("gemini-1.5-flash")

def generate_ai_narrative(event: dict) -> str:
    prompt = NARRATIVE_PROMPT.format(**event)
    response = gemini.generate_content(prompt)
    return response.text
```

**Activation switch** (environment variable):
```yaml
# In event-processor.yaml
- name: AI_NARRATIVE_ENABLED
  value: "true"          # false = use rule-based templates
- name: GCP_PROJECT
  value: "gdc-pm"
```

### 3.2 Vertex AI Model Registry
**Goal:** Govern the BQML → GCS → GDC model promotion lifecycle.

```
BigQuery ML Training
       ↓
   model.bst
       ↓
Vertex AI Model Registry (staging)
       ↓  [manual approval gate]
Vertex AI Model Registry (production)
       ↓
GCS model bucket (production path)
       ↓
Inference API (downloads on startup)
```

This ensures that no untested model reaches the edge. The `train-model.sh`
script is extended to register the exported model in Vertex AI automatically.

### 3.3 Derived Feature Computation (High-Accuracy Model)
**Goal:** Add time-domain features to improve model accuracy, especially for
early bearing wear and thermal runaway precursor detection.

**Architecture:** The event processor maintains a per-asset rolling buffer
(in-memory `collections.deque`, size=12 = 60 seconds at 5s intervals):

```python
from collections import deque
ASSET_BUFFERS: dict[str, deque] = {a: deque(maxlen=12) for a in ASSETS}

def compute_derived_features(asset_id: str, psi: float, temp_f: float, vib: float) -> dict:
    buf = ASSET_BUFFERS[asset_id]
    buf.append({"psi": psi, "temp_f": temp_f, "vib": vib})
    if len(buf) < 3:
        return {}
    psi_vals  = [r["psi"]   for r in buf]
    temp_vals = [r["temp_f"] for r in buf]
    vib_vals  = [r["vib"]   for r in buf]
    return {
        "psi_delta_5m":       psi_vals[-1]  - psi_vals[0],
        "temp_rate_of_rise":  (temp_vals[-1] - temp_vals[-3]) / 15,  # °F per minute
        "vibration_rms_60s":  float(np.sqrt(np.mean(np.square(vib_vals)))),
    }
```

These derived features require retraining the BQML model with the new feature
set. The BigQuery training table needs corresponding derived columns.

### 3.4 Alert Acknowledgement Workflow
**Schema change:**
```sql
ALTER TABLE telemetry_events
  ADD COLUMN IF NOT EXISTS acknowledged   BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS ack_time       TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS ack_operator   TEXT;
```

**New API endpoint:**
```python
@app.post("/api/acknowledge/{event_id}")
def acknowledge_event(event_id: int, operator: str = "ops"):
    # UPDATE telemetry_events SET acknowledged=TRUE, ack_time=NOW(), ack_operator=...
```

**UI change:** Unacknowledged failures render full-opacity with left border.
Acknowledged events fade to 40% opacity. Click any fault row to acknowledge.

---

## Phase 4 — GDC Edge Migration (ongoing)

This phase is already designed into the architecture. When a physical GDC
appliance is available:

1. **No code changes required.** All Kubernetes manifests are already
   GDC-compatible (GKE on Bare Metal).

2. **Model pre-loading** for fully air-gapped operation:
   ```dockerfile
   # In inference-api Dockerfile, add:
   COPY model.bst /app/model.bst
   ENV GCS_MODEL_PATH=""
   ENV MODEL_LOCAL_PATH="/app/model.bst"
   ```

3. **Setup:**
   ```bash
   # On the GDC appliance
   bash ~/bdau-basic-vpc/scripts/setup-edge-auth.sh
   kubectl apply -f gke/alloydb-omni/k8s/
   kubectl apply -f gke/rabbitmq/k8s/
   kubectl apply -f gke/inference-api/k8s/
   kubectl apply -f gke/event-processor/k8s/
   kubectl apply -f gke/telemetry-simulator/k8s/
   kubectl apply -f gke/fault-trigger-ui/k8s/
   kubectl apply -f gke/grafana/k8s/
   ```

4. **Training stays in the cloud.** Only the `model.bst` artifact crosses to
   the edge. This is the core GDC value proposition.

---

## Appendix: Rebuild Checklist

After any code change, rebuild only the affected service(s):

```bash
# Single service rebuild
cd ~/gdc-pm/gke/<service-name>
docker build -t <artifact-registry-url>/gdc-pm/<service-name>:latest .
docker push <artifact-registry-url>/gdc-pm/<service-name>:latest
kubectl rollout restart deployment/<service-name> -n gdc-pm
kubectl rollout status deployment/<service-name> -n gdc-pm

# Verify
kubectl logs -l app=<service-name> -n gdc-pm --tail=50
```

Or use the shared infrastructure script:
```bash
bash ~/bdau-basic-vpc/scripts/push-image.sh <service-name>
```
