# GDC-PM Phase 4.1 — Full Sensor Extension & Model Retrain
**Status:** Not Started  
**Date Created:** 2026-05-12  
**Preceded by:** `PHASE_4_PLAN.md` (deployed)  
**Issue:** Phase 4 added `motor_amps` (ESP) and `spm` (Mud Pump) to the UI data model and demo narrative, but did not update the telemetry simulator, event processor, AlloyDB schema, or XGBoost models to generate and use these sensors. This omission must be corrected before the scenarios are presented as technically authentic.

---

## The Gap

Phase 4 defines `SENSOR4_CONFIG` in `app.py` and added `amps_range`/`spm_range` to `FAULT_PROFILES`, but the pipeline below that level remains unchanged:

| Layer | Current State | Required State |
|---|---|---|
| `telemetry-simulator` | Generates only `psi, temp_f, vibration` | Must generate `motor_amps` (ESP) and `spm` (Mud Pump) |
| `event-processor` | Inserts only `psi, temp_f, vibration` | Must read and INSERT `motor_amps`, `spm` |
| AlloyDB `telemetry_events` | No `motor_amps` or `spm` columns | Needs `ADD COLUMN IF NOT EXISTS` migration |
| XGBoost models (ESP) | 6 features: `[psi, temp, vib, dpsi, dtemp, dvib]` | 8 features: `[psi, temp, vib, motor_amps, dpsi, dtemp, dvib, damps_dt]` |
| XGBoost models (Mud Pump) | 6 features: `[psi, temp, vib, dpsi, dtemp, dvib]` | 8 features: `[psi, temp, vib, spm, dpsi, dtemp, dvib, dspm_dt]` |
| `app.py` chart metrics | `psi`, `temp`, `vib` only | Add `amps` (ESP) and `spm` (Mud Pump) as 4th plotable metric |
| `index.html` sensor tabs | 3 tabs for all asset classes | Add 4th tab conditionally (ESP→"Current", Mud Pump→"Strokes") |

Gas Lift and Top Drive assets have no 4th sensor and require no model changes.

---

## Implementation Plan — Option A (Full Retrain)

### Step 1: AlloyDB Schema Migration
Update `gke/alloydb-omni/k8s/init-schema.yaml` to add:
```sql
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS motor_amps NUMERIC(7,2);
ALTER TABLE telemetry_events ADD COLUMN IF NOT EXISTS spm NUMERIC(7,2);
```
Run the migration against the live cluster via `kubectl exec`.

---

### Step 2: Telemetry Simulator Update (`simulator.py`)
In the reading generation loop, add the 4th sensor for appropriate asset classes.

**ESP normal operation:**
```python
if asset_class == "esp":
    reading["motor_amps"] = round(random.uniform(60, 90), 1)  # nominal range
```

**ESP fault injection (ramp toward fault values):**
- `gas_lock`: motor_amps ramps toward (20, 45) — pump unloads as GVF rises
- `sand_ingress`: motor_amps ramps toward (45, 65) — efficiency loss
- `motor_overheat`: motor_amps ramps toward (88, 105) — overcurrent

**Mud Pump normal operation:**
```python
if asset_class == "mud_pump":
    reading["spm"] = round(random.uniform(75, 100), 1)  # nominal range
```

**Mud Pump fault injection:**
- `valve_washout`: spm ramps toward (95, 120) — driller compensates
- `piston_seal_wear`: spm ramps toward (90, 110)
- `pulsation_dampener_failure`: spm erratic (55, 135)

---

### Step 3: Event Processor Update (`processor.py`)
In the `process_message()` function where the AlloyDB INSERT is built, add:
```python
motor_amps = data.get("motor_amps")   # None for non-ESP assets
spm        = data.get("spm")          # None for non-MudPump assets
```
And extend the `INSERT INTO telemetry_events` SQL to include these two columns.

---

### Step 4: XGBoost Model Retraining (`scripts/retrain_edge_models.py`)
This is the core of Phase 4.1. The training script must be extended to:

**For ESP (V1 and V2):**
- Generate `motor_amps` values correlated with fault state:
  - Normal: 60–90 A (nominal)
  - sand_ingress: declining from nominal → 45–65 A over fault duration
  - gas_lock: dropping sharply → 20–45 A
  - motor_overheat: rising → 88–105 A
- Compute `damps_dt` (amps rate of change per minute, same slope calculation as other channels)
- Feature vector: `[psi, temp_f, vibration, motor_amps, dpsi_dt, dtemp_dt, dvib_dt, damps_dt]`

**For Mud Pump (V1 and V2):**
- Generate `spm` values correlated with fault state:
  - Normal: 75–100 SPM (nominal)
  - valve_washout: rising from nominal → 95–120 SPM over fault duration
  - piston_seal_wear: rising → 90–110 SPM
  - pulsation_dampener_failure: erratic (55–135 SPM)
- Compute `dspm_dt` (SPM rate of change per minute)
- Feature vector: `[psi, temp_f, vibration, spm, dpsi_dt, dtemp_dt, dvib_dt, dspm_dt]`

**Gas Lift (unchanged):** `[psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]`
**Top Drive (unchanged):** `[psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]`

**V1 vs V2 profiles remain the same logic:**
- V1: trained on 5-min interval data with cloud-noise profile (`noise × 0.01`) — intentionally drifted
- V2: trained on 5-sec interval data with edge-noise profile (`noise × 0.002`) — stable

**Output model files (new):**
- `esp_classifier_v2.bst` — updated with motor_amps feature
- `esp_rul_v2.ubj` — updated with motor_amps feature
- `mud_pump_classifier_v2.bst` — updated with spm feature
- `mud_pump_rul_v2.ubj` — updated with spm feature
- (V1 drifted variants of the above)

**Important:** Gas Lift and Top Drive model files remain unchanged.

---

### Step 5: app.py — Feature Vector and Chart Updates

**Feature vector update in `plot_forecast()`:**
For ESP and Mud Pump assets, extend the XGBoost `dmat` feature vector from 6 to 8 features:
```python
# ESP
feature_row = np.array([[last_psi, last_temp, last_vib, last_amps,
                          dpsi_dt, dtemp_dt, dvib_dt, damps_dt]])
feature_names = ["psi", "temp_f", "vibration", "motor_amps",
                  "dpsi_dt", "dtemp_dt", "dvib_dt", "damps_dt"]
```

**Chart metric extension:**
Add `amps` and `spm` as plottable metrics in `plot_forecast()`. When `metric == "amps"` (ESP) or `metric == "spm"` (Mud Pump), query the new columns from AlloyDB and plot them with appropriate alarm threshold lines.

---

### Step 6: index.html — 4th Sensor Tab

Add a 4th sensor tab that appears conditionally based on asset class:
```javascript
const SENSOR4_TAB = {
  esp:      {metric: 'amps', label: 'Motor Current'},
  mud_pump: {metric: 'spm',  label: 'Stroke Rate'},
}
```
When `selectAsset()` is called, show/hide the 4th tab based on whether `SENSOR4_TAB[aclass]` exists.

---

### Step 7: Build and Deploy (3 containers)
```bash
# 1. Event Processor
docker build -t "${REG}/event-processor:latest" gke/event-processor/
docker push "${REG}/event-processor:latest"
kubectl rollout restart deployment/event-processor -n gdc-pm

# 2. Telemetry Simulator
docker build -t "${REG}/telemetry-simulator:latest" gke/telemetry-simulator/
docker push "${REG}/telemetry-simulator:latest"
kubectl rollout restart deployment/telemetry-simulator -n gdc-pm

# 3. Fault Trigger UI (app.py + new model files)
docker build -t "${REG}/fault-trigger-ui:latest" gke/fault-trigger-ui/
docker push "${REG}/fault-trigger-ui:latest"
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```

---

## Files to Modify

| File | Change Type |
|---|---|
| `gke/alloydb-omni/k8s/init-schema.yaml` | Add 2 ALTER TABLE statements |
| `gke/telemetry-simulator/simulator.py` | Add motor_amps/spm generation per asset_class and fault_type |
| `gke/event-processor/processor.py` | Add motor_amps/spm to INSERT statement |
| `scripts/retrain_edge_models.py` | Extend feature vectors, add 4th sensor to training data generation |
| `gke/fault-trigger-ui/models/*.bst/*.ubj` | Replace with retrained 8-feature models (ESP + Mud Pump only) |
| `gke/fault-trigger-ui/app.py` | Extend XGBoost dmat, add amps/spm chart metric support |
| `gke/fault-trigger-ui/index.html` | Add 4th sensor tab (conditional) |

---

## Verification Checklist

After deployment, verify:
- [ ] Grafana: ESP assets show `motor_amps` trending on fault injection (declining on sand_ingress, dropping fast on gas_lock)
- [ ] Grafana: Mud Pump assets show `spm` rising on valve_washout (compensation signature)
- [ ] Plotly chart: 4th sensor tab visible and plotting for ESP and Mud Pump assets
- [ ] XGBoost RUL prediction: stable and reasonable for all 4 asset classes with extended feature vector
- [ ] MLOps demo: V1 model shows higher variance (still trained on 5-min cloud noise profile)

---

## Context for Retraining Script

The existing retraining script is at `scripts/retrain_edge_models.py`. It currently:
- Generates synthetic training sequences for all 4 asset classes
- Uses `[psi, temp, vib]` as sensor channels
- Trains separate classifier (`.bst`) and RUL regressor (`.ubj`) for V1 and V2

The extension adds a 4th sensor channel for ESP and Mud Pump only. Gas Lift and Top Drive training code is unchanged. Output model files for those two asset classes are dropped into `gke/fault-trigger-ui/models/` with the same naming convention.
