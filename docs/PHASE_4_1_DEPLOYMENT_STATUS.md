# GDC-PM Phase 4.1 — Deployment Status & Test Plan
**Status:** Deployed — commit `e7eed2c`  
**Date:** 2026-05-12  
**Preceded by:** `PHASE_4_PLAN.md` (commit `304bc60`)  
**UI:** http://35.188.3.97

---

## What Was Done

Phase 4.1 closed the gap identified in `PHASE_4_PLAN.md`: `motor_amps` (ESP) and `spm` (Mud Pump) were wired end-to-end through every layer of the pipeline.

### Files Changed (12)

| File | Change |
|---|---|
| `gke/alloydb-omni/k8s/init-schema.yaml` | ADD COLUMN motor_amps, spm (also applied live via kubectl exec) |
| `gke/telemetry-simulator/simulator.py` | motor_amps on ESP (normal + gas_lock/sand_ingress/motor_overheat), spm on Mud Pump (normal + valve_washout/piston_seal_wear/pulsation_dampener erratic) |
| `gke/event-processor/processor.py` | Extracts + INSERTs motor_amps, spm |
| `scripts/retrain_edge_models.py` | 8-feature vectors for ESP/MudPump, V1 (noise×5 cloud-drifted) + V2 (noise×1 edge-calibrated), noise_scale parameter |
| `gke/fault-trigger-ui/models/esp_rul.ubj` | V1 8-feature retrained |
| `gke/fault-trigger-ui/models/esp_rul_v2.ubj` | V2 8-feature retrained (RMSE 0.185 min) |
| `gke/fault-trigger-ui/models/mud_pump_rul.ubj` | V1 8-feature retrained |
| `gke/fault-trigger-ui/models/mud_pump_rul_v2.ubj` | V2 8-feature retrained (RMSE 0.174 min) |
| `gke/fault-trigger-ui/models/gas_lift_rul_v2.ubj` | V2 refreshed (6-feature, unchanged) |
| `gke/fault-trigger-ui/models/top_drive_rul_v2.ubj` | V2 refreshed (6-feature, unchanged) |
| `gke/fault-trigger-ui/app.py` | SQL adds motor_amps/spm; 8-feature DMatrix for ESP/MudPump; amps/spm chart metric; 4th sensor in degrade ramp + hold + inject + scenario |
| `gke/fault-trigger-ui/index.html` | SENSOR4_TAB const; conditional tab-sensor4 (Motor Current/Stroke Rate); selectAsset wires tab; selectTab handles amps/spm |

### Live Cluster State (at commit)
- AlloyDB: `motor_amps NUMERIC(7,2)` and `spm NUMERIC(7,2)` columns confirmed present
- All 3 pods Running: `event-processor`, `telemetry-simulator`, `fault-trigger-ui`
- fault-trigger-ui startup log confirms all 8 models loaded (V1+V2 × all 4 classes)
- Active model version: V2

---

## ⚠️ Known Issues / Not Yet Verified in Browser

The code is deployed but the following have NOT been visually confirmed in a browser session:

1. **4th sensor tab appears for ESP assets** — selecting any ESP-ALPHA-* should show "Motor Current" as a 4th sensor tab
2. **4th sensor tab appears for Mud Pump assets** — selecting any MUD-RIG42-* should show "Stroke Rate"  
3. **4th sensor tab is hidden for Gas Lift and Top Drive** — no tab should appear for GLIFT-BRAVO-* or TOPDRIVE-RIG42-*
4. **Motor Current chart renders** — clicking the tab should plot ~75A baseline, trending toward fault values during gradual degrade injection
5. **Stroke Rate chart renders** — SPM baseline ~87 SPM, rising during valve_washout fault injection
6. **8-feature RUL predictions work** — injecting sand_ingress on an ESP and watching the RUL counter behave stably (V2) vs erratically (V1 via retrain button)
7. **Grafana shows motor_amps and spm** — the Grafana dashboard may need a panel update to visualize the new columns (not yet done — Grafana ConfigMap not updated in this phase)

---

## Test Protocol for Next Session

### Quick Smoke Test (5 min)
1. Open http://35.188.3.97
2. Click **Pad Alpha** site card → select **ESP-ALPHA-2**
3. Verify 4 sensor tabs appear: `Intake Pres. | Winding Temp | Vibration | Motor Current`
4. Click **Motor Current** tab → chart should render at ~75A nominal
5. Click **Rig 42** site card → select **MUD-RIG42-1**
6. Verify 4 sensor tabs: `Disch. Pres. | Fluid Temp | Vibration | Stroke Rate`
7. Click **Stroke Rate** tab → chart at ~87 SPM nominal
8. Click **Pad Bravo** → select **GLIFT-BRAVO-1** → verify NO 4th tab (only 3)

### Full Demo Test (15 min)
1. Select **ESP-ALPHA-2**, choose **Sand Ingress**, **Gradual ramp**
2. Click **⚡ Inject Fault**
3. Watch the Vibration chart start degrading
4. Click **Motor Current** tab → motor_amps should visibly decline (sand erosion reduces hydraulic work → lower current)
5. Let ramp run 2–3 minutes → RUL prediction should be stable ~40-45 min (V2 model)
6. Click **☁ Retrain via Vertex AI** → wait for pipeline animation → V1 swap should show more variance in RUL
7. Acknowledge the dispatch, verify reset works

### MLOps Demo Test (3 min)
1. Inject **Motor Overheat** on **ESP-ALPHA-1** (instant burst × 3)
2. Click **Motor Current** tab → should show 88–105A (overcurrent signature)
3. Verify RUL is still computed from the 8-feature vector (check app.py logs via `kubectl logs -n gdc-pm -l app=fault-trigger-ui --tail=5` — should see `(8f)` in the debug line)

---

## Known Outstanding Work (Phase 4.2 / Future)

1. **Grafana dashboard panels** — Add `motor_amps` and `spm` panels to `gke/grafana/k8s/grafana-configmap.yaml` so the Historical Telemetry tab shows them
2. **Higher-sample model retraining** — Current models use 50 samples/200 rounds. For better demonstration quality, run `python scripts/retrain_edge_models.py --n-samples 300 --rounds 300` — takes ~4 min, produces tighter V2 RMSE and more noticeably drifted V1
3. **Asset Intel drawer sensor list** — The Physics tab in the Asset Intel drawer doesn't yet show Motor Current / Stroke Rate as a monitored sensor for ESP/MudPump (cosmetic only)
4. **Pad Charlie assets** — ESP-CHARLIE-* also have motor_amps (simulated) but only Pad Alpha is in the demo scenarios; all 12 ESPs benefit equally

---

## Next Session Prompt Suggestion

```
Read docs/PHASE_4_1_DEPLOYMENT_STATUS.md. We need to test the deployed Phase 4.1 
changes in the browser. The known outstanding work is: (1) verify the 4th sensor tab 
appears correctly for ESP and Mud Pump assets, (2) confirm motor_amps and spm charts 
render with real data during fault injection, (3) optionally add Grafana panels for 
the new columns. Start by running the Quick Smoke Test described in the doc.
```
