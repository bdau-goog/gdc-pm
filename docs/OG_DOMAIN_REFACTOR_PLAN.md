# GDC-PM: Upstream O&G Domain Refactor — Complete Architecture Plan
**Status:** APPROVED — Ready for Implementation  
**Context Baseline:** Commit `e124af7` ("Predictive Forecast chart + color mapping fix")  
**Goal:** Transform the demo from a generic Power/Industrial scenario into a credible, technically accurate **Upstream Oil & Gas Fleet Predictive Maintenance** platform, suitable for presentation to drilling and production operations managers.

---

## Part 1: Why This Refactor Is Required

The current demo uses "Gas Compressors," "Gas Turbine Generators," and "115kV Transformers" with fault types like "Core Loosening" and "Dielectric Breakdown." These are valid industrial assets, but they do not resonate with an Upstream O&G audience (drilling engineers, production engineers, HSE managers). The O&G audience will immediately recognize that:
1. The assets are from the power utilities sector, not oil and gas.
2. The fault types are not things their maintenance teams think about.
3. The sensor ranges (850 PSI discharge pressure, 112°F temperature) match gas transmission compressors, not downhole equipment.

This refactor replaces every asset and fault type with ones that directly map to the O&G audience's day-to-day concerns while maintaining the same demo architecture (RabbitMQ → Inference → AlloyDB → UI).

---

## Part 2: The New Asset Fleet (4 Sites, 20 Assets)

### Site Architecture

| Site ID | Site Name | Type | Asset Count |
|---------|-----------|------|-------------|
| PAD-ALPHA | Pad Alpha | Production | 6 assets |
| PAD-BRAVO | Pad Bravo | Production | 6 assets |
| PAD-CHARLIE | Pad Charlie | Production | 4 assets |
| RIG-42 | Rig 42 | Drilling | 4 assets |

**Total: 20 monitored assets**

### Asset Definitions Per Site

#### Pad Alpha (Production Pad)
| Asset ID | Asset Type | Asset Class | Criticality |
|----------|-----------|-------------|-------------|
| ESP-ALPHA-1 | Electrical Submersible Pump | `esp` | CRITICAL |
| ESP-ALPHA-2 | Electrical Submersible Pump | `esp` | CRITICAL |
| ESP-ALPHA-3 | Electrical Submersible Pump | `esp` | HIGH |
| ESP-ALPHA-4 | Electrical Submersible Pump | `esp` | HIGH |
| GLIFT-ALPHA-1 | Gas Lift Compressor | `gas_lift` | HIGH |
| GLIFT-ALPHA-2 | Gas Lift Compressor | `gas_lift` | MEDIUM |

#### Pad Bravo (Production Pad)
| Asset ID | Asset Type | Asset Class | Criticality |
|----------|-----------|-------------|-------------|
| ESP-BRAVO-1 | Electrical Submersible Pump | `esp` | CRITICAL |
| ESP-BRAVO-2 | Electrical Submersible Pump | `esp` | HIGH |
| ESP-BRAVO-3 | Electrical Submersible Pump | `esp` | HIGH |
| ESP-BRAVO-4 | Electrical Submersible Pump | `esp` | MEDIUM |
| GLIFT-BRAVO-1 | Gas Lift Compressor | `gas_lift` | HIGH |
| GLIFT-BRAVO-2 | Gas Lift Compressor | `gas_lift` | MEDIUM |

#### Pad Charlie (Production Pad)
| Asset ID | Asset Type | Asset Class | Criticality |
|----------|-----------|-------------|-------------|
| ESP-CHARLIE-1 | Electrical Submersible Pump | `esp` | CRITICAL |
| ESP-CHARLIE-2 | Electrical Submersible Pump | `esp` | HIGH |
| ESP-CHARLIE-3 | Electrical Submersible Pump | `esp` | HIGH |
| GLIFT-CHARLIE-1 | Gas Lift Compressor | `gas_lift` | HIGH |

#### Rig 42 (Drilling Rig)
| Asset ID | Asset Type | Asset Class | Criticality |
|----------|-----------|-------------|-------------|
| MUD-RIG42-1 | Triplex Mud Pump | `mud_pump` | CRITICAL |
| MUD-RIG42-2 | Triplex Mud Pump | `mud_pump` | CRITICAL |
| MUD-RIG42-3 | Triplex Mud Pump | `mud_pump` | HIGH |
| TOPDRIVE-RIG42-1 | Top Drive | `top_drive` | CRITICAL |

---

## Part 3: Sensor Definitions Per Asset Class

All assets use the same three sensor fields in the database (`psi`, `temp_f`, `vibration`) but the physical meaning varies by asset class. This allows us to use the same schema and models with appropriate re-labeling.

### ESP (Electrical Submersible Pump)
*Scenario:* Pump is installed 5,000ft downhole, lifting oil to surface.

| Field | Physical Meaning | Unit | Normal Range | Critical Threshold |
|-------|-----------------|------|-------------|-------------------|
| `psi` | Motor Intake Pressure | PSI | 1,200 – 1,600 | < 800 (gas ingestion) |
| `temp_f` | Motor Winding Temperature | °F | 180 – 220 | > 280 (overheat) |
| `vibration` | Motor Vibration | mm/s | 0.8 – 2.0 | > 8.0 (mechanical) |

### Gas Lift Compressor
*Scenario:* Surface compressor injecting lift gas into production tubing.

| Field | Physical Meaning | Unit | Normal Range | Critical Threshold |
|-------|-----------------|------|-------------|-------------------|
| `psi` | Discharge Pressure | PSI | 900 – 1,100 | < 600 (valve failure) |
| `temp_f` | Discharge Temperature | °F | 140 – 175 | > 230 (thermal event) |
| `vibration` | Frame Vibration | mm/s | 1.0 – 2.5 | > 12.0 (bearing failure) |

### Mud Pump (Triplex)
*Scenario:* Drilling rig pump circulating drilling fluid.

| Field | Physical Meaning | Unit | Normal Range | Critical Threshold |
|-------|-----------------|------|-------------|-------------------|
| `psi` | Discharge Pressure | PSI | 2,500 – 3,200 | spike > 4,500 or drop < 1,800 |
| `temp_f` | Fluid End Temperature | °F | 90 – 120 | > 180 (seal degradation) |
| `vibration` | Module Vibration | mm/s | 2.0 – 5.0 | > 20.0 (pulsation dampener failure) |

### Top Drive
*Scenario:* Drilling rig rotary drive system.

| Field | Physical Meaning | Unit | Normal Range | Critical Threshold |
|-------|-----------------|------|-------------|-------------------|
| `psi` | Hydraulic System Pressure | PSI | 2,800 – 3,200 | < 2,000 (hydraulic loss) |
| `temp_f` | Gearbox Oil Temperature | °F | 130 – 165 | > 220 (gearbox failure) |
| `vibration` | Gearbox Vibration | mm/s | 1.5 – 4.0 | > 15.0 (bearing spalling) |

---

## Part 4: Fault Profiles Per Asset Class

### ESP Faults

| Fault ID | Fault Name | Physical Story | Affected Sensors | Type |
|----------|-----------|----------------|-----------------|------|
| `gas_lock` | Gas Lock | Gas pockets overwhelm pump stages — intake PSI drops dramatically, vibration becomes erratic | PSI ↓↓, Vib ↑↑ | **Instant** |
| `sand_ingress` | Sand Ingress | Fine formation sand erodes impeller — vibration climbs steadily over hours | Vib ↑ gradual | **Gradual** |
| `motor_overheat` | Motor Overheat | Downhole cooling circulation reduced — motor temperature climbs | Temp ↑ gradual | **Gradual** |

### Gas Lift Compressor Faults

| Fault ID | Fault Name | Physical Story | Affected Sensors | Type |
|----------|-----------|----------------|-----------------|------|
| `valve_failure` | Valve Failure | Check valve breaks — discharge pressure drops and vibration spikes | PSI ↓↓, Vib ↑↑ | **Instant** |
| `thermal_runaway` | Thermal Runaway | Cooling degradation — discharge temperature climbs while pressure stays normal | Temp ↑ gradual | **Gradual** |
| `bearing_wear` | Bearing Wear | Progressive bearing degradation — frame vibration climbs over hours | Vib ↑ gradual | **Gradual** |

### Mud Pump Faults

| Fault ID | Fault Name | Physical Story | Affected Sensors | Type |
|----------|-----------|----------------|-----------------|------|
| `pulsation_dampener_failure` | Pulsation Dampener Failure | Dampener bladder ruptures — sudden extreme vibration and pressure spikes | PSI spike, Vib ↑↑↑ | **Instant** |
| `valve_washout` | Valve Seat Washout | High-velocity fluid erodes valve seat — discharge pressure slowly declines | PSI ↓ gradual | **Gradual** |
| `piston_seal_wear` | Piston Seal Wear | Piston seals degrade — fluid temp rises, pressure slowly drops | PSI ↓ gradual, Temp ↑ | **Gradual** |

### Top Drive Faults

| Fault ID | Fault Name | Physical Story | Affected Sensors | Type |
|----------|-----------|----------------|-----------------|------|
| `gearbox_bearing_spalling` | Gearbox Bearing Spalling | Metal-to-metal fatigue in gearbox — vibration climbs distinctively | Vib ↑ gradual | **Gradual** |
| `hydraulic_leak` | Hydraulic Leak | Hydraulic fluid loss — system pressure drops over time | PSI ↓ gradual | **Gradual** |

---

## Part 5: ML Model Architecture

### Two Models Per Asset Class (8 total)

We train **two XGBoost models** for each of the 4 asset classes:

1. **Fault Classifier:** Predicts which fault is occurring (multi-class classification).
   - Input: PSI, Temp, Vibration (current values)
   - Output: Class label (`normal`, `gas_lock`, `sand_ingress`, etc.)
   - Used by: `inference-api` for real-time detection

2. **RUL Regressor:** Predicts Remaining Useful Life in minutes (regression).
   - Input: PSI, Temp, Vibration + delta-PSI/min, delta-Temp/min, delta-Vib/min (rate of change features)
   - Output: Float (minutes until predicted failure)
   - Used by: `/api/plot/forecast` endpoint to plot the genuine ML prediction curve

### RUL Training Data Format
```csv
psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt, rul_minutes
1420.3, 195.2, 1.2, -2.1, 0.5, 0.08, 240.0
1385.1, 198.7, 1.4, -4.5, 0.9, 0.15, 210.0
...
840.2, 228.3, 6.8, -18.2, 5.1, 0.85, 12.0
```

### Training Data Volume Per Asset Class
- 5,000 normal readings (various conditions)
- 1,000 readings per fault type × fault count = 3,000–3,500 fault readings
- 2,000 gradual degradation trajectories with RUL labels
- **Total per asset class: ~10,000 rows**

### Model Files
```
gke/inference-api/models/
  esp-classifier.json
  esp-regressor.json
  gas_lift-classifier.json
  gas_lift-regressor.json
  mud_pump-classifier.json
  mud_pump-regressor.json
  top_drive-classifier.json
  top_drive-regressor.json
```

---

## Part 6: Backend API Changes

### New Asset Registry (20 Assets)
`app.py` in `fault-trigger-ui` will contain the full 20-asset `ASSET_REGISTRY` dictionary with all metadata, sensor labels, and fault type assignments.

### New Endpoints

```
GET /api/plot/forecast/{asset_id}?metric=pressure|temp|vibration
```
- `metric` selects which sensor to plot on the Y-axis (default: the primary degrading sensor for the active fault)
- RUL forecast line is drawn from the XGBoost Regressor output, NOT from curve-fitting
- Returns fully self-contained Plotly HTML iframe

```
POST /api/clear-dispatch
```
- Marks ALL unacknowledged events as acknowledged in AlloyDB
- Enables the presenter to instantly reset the board between demo runs

### Updated Inference API
The `inference-api` will load 8 model files (4 classifiers + 4 regressors). For each incoming reading:
1. Select the correct classifier and regressor based on the asset class.
2. Classifier output → `predicted_label` (fault type name)
3. Regressor output → `rul_minutes` (new column in `telemetry_events`)
4. Both stored to AlloyDB.

### Database Schema Change
Add `rul_minutes FLOAT` column to `telemetry_events` table.

---

## Part 7: Frontend UI Layout (New Design)

### Layout Overview
```
┌─── HEADER ───────────────────────────────────────────────────────────────────┐
│  ⚡ GDC Predictive Maintenance — O&G Fleet      🌐 [Airgap Toggle]  HH:MM:SS │
├───────────────────────────────────────────────────────────────────────────────┤
│  ┌── FLEET HEALTH BAR (always visible) ──────────────────────────────────┐   │
│  │  🔴 Pad Alpha [4 ESP, 2 GL] — 2 Critical   ⚠ Pad Bravo — 1 Warning  │   │
│  │  ✓  Pad Charlie — Nominal                  ✓ Rig 42 — Nominal        │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌── ACTIVE INCIDENTS PANEL (only when faults exist) ────────────────────┐  │
│  │  🔴 ESP-ALPHA-2  Gas Lock       RUL: 43m ████░░░░░░  [Diagnose ▶]   │  │
│  │  🔴 MUD-RIG42-1  Valve Washout  RUL: 1h 20m ███░░░░░  [Diagnose ▶] │  │
│  │  ⚠  ESP-ALPHA-4  Motor Overheat RUL: 3h 10m ██░░░░░░  [Diagnose ▶] │  │
│  │                          [ Clear All Work Orders ]                    │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
├──────────────────┬──────────────────────────────────────────────────────────┤
│  LIVE EVENT FEED │  ┌── FAULT INJECTION ────────────────────────────────┐  │
│                  │  │  Selected: ESP-ALPHA-2                             │  │
│  HH:MM:SS        │  │  [ Gas Lock (Instant) ] [ Sand Ingress (Gradual)] │  │
│  ESP-ALPHA-2     │  │  [ Motor Overheat (Gradual) ] [Reset to Normal]   │  │
│  gas_lock ⚠     │  └───────────────────────────────────────────────────┘  │
│  RUL: 43m        │  ┌── ML PREDICTIVE FORECAST: ESP-ALPHA-2 ─────────── ┐ │
│  ...             │  │  [ Intake Pressure ] | [ Motor Temp ] | [ Vibration│ │
│                  │  │                                                     │ │
│                  │  │  [Plotly chart: historical + RUL ML projection     │ │
│                  │  │  + cone of uncertainty + failure threshold line]   │ │
│                  │  └───────────────────────────────────────────────────┘ │
└──────────────────┴──────────────────────────────────────────────────────────┘
```

### Key UI Components

1. **Fleet Health Bar:** Always-visible compact row of 4 site cards. Each shows the site name, asset type summary, and worst current severity. Clicking a site shows its asset list inline (below the bar) while keeping all other sites visible.

2. **Active Incidents Panel:** Auto-appears when any fault is detected. Shows all faulting assets sorted by shortest RUL first. Each row includes:
   - Asset ID + Site
   - Fault type (from ML classifier output)
   - RUL bar (visual urgency meter: full=long time, empty=imminent)
   - `[Diagnose ▶]` button to load that asset's chart + pre-fill the dispatch modal
   - `Clear All Work Orders` clears the board instantly

3. **Sensor Tabs:** Three tabs above the Plotly forecast chart for the selected asset. Each tab shows its sensor label (e.g., "Intake Pressure (PSI)", "Motor Temp (°F)", "Vibration (mm/s)"). Clicking a tab reloads the chart with that metric on the Y-axis. The ML RUL projection adapts to the selected metric automatically.

4. **Fault Injection Panel:** Shows only the fault types relevant to the selected asset class. Clearly labels each as `(Instant)` or `(Gradual)`. Duration slider for gradual faults.

---

## Part 8: Implementation Order

### Step 1: Data Generation (Scripts)
Update/create:
- `scripts/seed-esp-data.py`
- `scripts/seed-gas-lift-data.py`
- `scripts/seed-mud-pump-data.py`
- `scripts/seed-top-drive-data.py`

Each generates both classifier training data and RUL regressor training data as separate CSV files.

### Step 2: Model Training
Update:
- `scripts/train-esp-model.sh` (trains 2 models)
- `scripts/train-gas-lift-model.sh`
- `scripts/train-mud-pump-model.sh`
- `scripts/train-top-drive-model.sh`

### Step 3: Inference API Update
Update:
- `gke/inference-api/app.py` — load 8 models, asset class routing, write `rul_minutes` to AlloyDB
- `gke/alloydb-omni/k8s/init-schema.yaml` — add `rul_minutes FLOAT` column migration

### Step 4: Telemetry Simulator Update
Update:
- `gke/telemetry-simulator/simulator.py` — 20 assets, new sensor ranges per asset class

### Step 5: Fault Trigger UI — Backend
Update:
- `gke/fault-trigger-ui/app.py` — 20 assets, new fault profiles, new endpoints
  - `/api/plot/forecast/{asset_id}?metric=pressure|temp|vibration` using RUL regressor output
  - `POST /api/clear-dispatch`

### Step 6: Fault Trigger UI — Frontend
Rewrite:
- `gke/fault-trigger-ui/index.html` — Fleet Health Bar, Active Incidents Panel, sensor tabs

### Step 7: Build, Push, Deploy
```bash
docker build && docker push  # inference-api
docker build && docker push  # fault-trigger-ui
kubectl rollout restart deployment/inference-api -n gdc-pm
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
```

---

## Part 9: Phase 4 — Agentic RAG Architecture (Design Only — Not Implemented Yet)

### Local Gemma Inference Server
- **Model:** Gemma 2 2B Instruct (quantized Q4, runs on CPU) via Ollama
- **Deployment:** New Kubernetes Deployment `gemma-inference` in `gdc-pm` namespace
- **API:** Ollama OpenAI-compatible API at `http://gemma-inference:11434/v1/chat/completions`
- **GPU Option:** Optional NVIDIA T4 node pool on GKE for Gemma 9B; CPU-only 2B is sufficient for demo

### RAG Knowledge Base (pgvector in AlloyDB Omni)
Enable `pgvector` extension in AlloyDB Omni.
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE maintenance_docs (
    id SERIAL PRIMARY KEY,
    asset_class TEXT,
    fault_type TEXT,
    doc_section TEXT,
    content TEXT,
    embedding VECTOR(768)
);
```
Load synthetic "OEM Maintenance Manuals" (JSON files) with content like:
- ESP Gas Lock: troubleshooting steps, required tools, downtime history
- Mud Pump Valve Washout: inspection procedure, replacement parts, HPT intervals

### gemma-assessor Service
A new Python microservice that:
1. Polls AlloyDB for new unacknowledged events with `ai_narrative IS NULL`
2. For each event, queries pgvector for the 3 most relevant maintenance manual sections
3. Constructs a prompt: `"Asset: ESP-ALPHA-2. Fault: gas_lock. RUL: 43 minutes. Sensor data: ... [RAG context]. Generate an assessment and recommended actions."`
4. POSTs to local Gemma API
5. Writes the response to `telemetry_events.ai_narrative`

### Agentic Tools
The `gemma-assessor` can optionally be extended to an **Agent** with tools:
- `get_asset_telemetry(asset_id)` → Live sensor reading
- `query_oem_manual(asset_class, fault_type)` → RAG document retrieval
- `check_parts_inventory(part_number)` → Returns stock (simulated)
- `adjust_setpoint(asset_id, parameter, delta)` → Simulated remediation action

The agent loop demonstrates: *"GDC Edge AI not only detected the fault, it read the manual, checked parts availability, and reduced motor frequency by 15% to prevent gas lock — all locally, with the cloud disconnected."*

---

*Document created: 2026-05-05*  
*Resume from here with a clean context: read this file, check baseline commit `e124af7`, and start with Step 1 (seed data generation scripts).*
