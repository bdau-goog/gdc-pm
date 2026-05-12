# GDC-PM Phase 4.2 — Deployment Status
**Status:** Deployed — 2026-05-12  
**Preceded by:** `PHASE_4_1_DEPLOYMENT_STATUS.md`  
**UI:** http://35.188.3.97  

---

## What Was Done

Phase 4.2 closed the three items of outstanding work identified in `PHASE_4_1_DEPLOYMENT_STATUS.md`:

### 1. Asset Intel Drawer — Sensor List Updated

**File:** `gke/fault-trigger-ui/index.html`  
**Change:** Added the 4th-sensor entries to the `ASSET_PHYSICS` constant in the Asset Intel drawer Physics tab.

| Asset Class | New Sensor Entry |
|---|---|
| ESP | Motor Current — 60–90 A nominal · >105 A (Motor Overheat) / <45 A (Gas Lock / Sand Erosion) |
| Mud Pump | Stroke Rate — 75–100 SPM nominal · >120 SPM or Chaotic (Dampener Rupture) / <60 SPM (Valve Washout) |

Gas Lift and Top Drive drawers remain at 3 sensors (no 4th sensor for those asset classes).

---

### 2. Grafana Dashboard Panels — motor_amps and spm

**File:** `gke/grafana/k8s/grafana-configmap.yaml`  
**Change:** Added two new timeseries panels to the GDC-PM dashboard at row y:34, shifting ML metric panels down.

| Panel ID | Title | SQL Column | Thresholds |
|---|---|---|---|
| 29 | Motor Current — ESP Assets (A) | `motor_amps` | Red:<45 · Green:45–95 · Yellow:95–105 · Red:>105 |
| 30 | Stroke Rate — Mud Pump Assets (SPM) | `spm` | Red:<60 · Green:60–110 · Yellow:110–120 · Red:>120 |

**Updated panel grid layout (no overlaps):**
- y:0 — Active Alerts table  
- y:7 — Stat row (6 KPI tiles)  
- y:11 — Fleet Health Timeline  
- y:18 — Pressure row (Compressors / Turbines / Transformers)  
- y:26 — Temperature + Vibration  
- **y:34 — Motor Current (NEW) + Stroke Rate (NEW)**  
- y:42 — ML Confidence + Anomaly Rate  
- y:50 — Recent ML Detections (full-width table)  

Grafana ConfigMap applied and pod restarted at 15:00 UTC.

---

### 3. Higher-Sample Model Retraining (300 samples / 300 rounds)

**Script:** `scripts/retrain_edge_models.py --n-samples 300 --rounds 300`  
**Run time:** 181 seconds  
**Total training rows:** 648,000 rows × 8 features (ESP, MudPump) or 6 features (GasLift, TopDrive)

| Model File | Version | RMSE (min) | Features | Notes |
|---|---|---|---|---|
| `esp_rul_v2.ubj` | V2 edge-calibrated | **0.177** | 8 | Down from 0.185 in Phase 4.1 |
| `esp_rul.ubj` | V1 cloud-drifted | 0.577 | 8 | Intentionally noisy for MLOps demo |
| `gas_lift_rul_v2.ubj` | V2 edge-calibrated | 0.227 | 6 | Unchanged feature count |
| `mud_pump_rul_v2.ubj` | V2 edge-calibrated | **0.166** | 8 | Best model — tightest RMSE |
| `mud_pump_rul.ubj` | V1 cloud-drifted | 0.541 | 8 | Intentionally noisy |
| `top_drive_rul_v2.ubj` | V2 edge-calibrated | 0.177 | 6 | Unchanged feature count |

Spot-checks at 25%/50%/75% through degradation trajectory: all within 0.4 min of actual RUL.

---

## Live Cluster State (at deployment)

```
Pod:   fault-trigger-ui-d9ff484f5-wkskj   1/1   Running   AGE: 22s
Image: us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
Digest: sha256:54dabc61ff986efae7e18e53fd8a336de80184fc74c74620586bc2fb135c6958

Startup log confirms:
  ✅ Loaded V2 model: top_drive (1426 KB)
  Model registry: V1=['esp', 'gas_lift', 'mud_pump', 'top_drive']  V2=['esp', 'gas_lift', 'mud_pump', 'top_drive']
  Active version on startup: V2
```

**DB verification (pre-deployment):**
- ESP motor_amps: 68–89 A (nominal ~75 A, spec 60–90 A) ✓
- Mud Pump spm: 83–89 SPM (nominal ~87 SPM, spec 75–100 SPM) ✓

---

## Outstanding Work (Phase 4.3 / Future)

1. **Pad Charlie assets** — ESP-CHARLIE-* have motor_amps simulated but are not in demo scenarios; only Pad Alpha ESPs are in the fault injection UI. All 12 ESPs benefit from the 8-feature model equally.
2. **Browser smoke test** — No browser available in the development environment at time of deployment. Test the following in a browser session:
   - `ESP-ALPHA-2` → 4 tabs (Intake Pres. / Winding Temp / Vibration / **Motor Current**)
   - `MUD-RIG42-1` → 4 tabs (Disch. Pres. / Fluid Temp / Vibration / **Stroke Rate**)
   - `GLIFT-BRAVO-1` → 3 tabs only (no 4th)
   - Asset Intel drawer for ESP → Physics tab shows 4 sensor cards
   - Asset Intel drawer for Mud Pump → Physics tab shows 4 sensor cards
   - Grafana Historical Telemetry tab → Motor Current and Stroke Rate panels visible

---

## Next Session Prompt Suggestion

```
Read docs/PHASE_4_2_DEPLOYMENT_STATUS.md. The three outstanding items from Phase 4.1 
have been completed: Asset Intel drawer sensor list updated, Grafana panels added for 
motor_amps and spm, and edge models retrained (300 samples/300 rounds — best RMSE 0.166). 
The live system is at http://35.188.3.97. 

The only remaining work for Phase 4.2 is a browser visual verification (see the 
Outstanding Work section). After verifying, the next feature work is Pad Charlie assets 
(Phase 4.3).
```
