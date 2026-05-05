# GDC-PM: Upstream O&G Business Value Overhaul
**Status:** APPROVED — Ready for Implementation  
**Context Baseline:** Commit `696b80e` ("Gate RUL forecast on classifier output") and `8bd0045` ("Unambiguous sensor tab labels")  
**Goal:** Elevate the O&G demo from "technical charts" to a compelling executive-level **Business Value** story. We will replace the generic "Airgap" toggle with three high-impact features that prove the financial and operational necessity of Edge AI, while tightening the physical credibility of the simulated asset fleet.

---

## Feature 1: Pure Pad Architecture (Credibility)
**The Problem:** Currently, production pads mix Electrical Submersible Pumps (ESPs) and Gas Lift Compressors on the exact same pad. In reality, a pad uses a single artificial lift method.
**The Fix:** Restructure the 20 assets so pads are pure.

### New Fleet Layout (20 Assets Total)
*   **Pad Alpha (ESP Production):** 6 ESPs (`ESP-ALPHA-1` through `-6`)
*   **Pad Bravo (Gas Lift Production):** 4 Gas Lift Compressors (`GLIFT-BRAVO-1` through `-4`)
*   **Pad Charlie (ESP Production):** 6 ESPs (`ESP-CHARLIE-1` through `-6`)
*   **Rig 42 (Drilling):** 3 Mud Pumps (`MUD-RIG42-1` to `-3`), 1 Top Drive (`TOPDRIVE-RIG42-1`)

*Note: Sensor physics (nominal/critical ranges) and XGBoost models are already perfectly tuned for these 4 asset classes and do not require retraining. Only the registry routing in `app.py`, `simulator.py`, and `index.html` needs updating.*

---

## Feature 2: Cumulative Savings Ticker (Financial Value)
**The Problem:** We claim GDC saves money by preventing failure, but we never show the receipts.
**The Fix:** A persistent, fleet-wide savings counter in the header.

### Backend Implementation
1.  **Database:** `telemetry_events` needs a new column: `ALTER TABLE telemetry_events ADD COLUMN cost_avoided NUMERIC DEFAULT 0;`
2.  **API Endpoint (`POST /api/acknowledge/{event_id}`):** When an operator acknowledges a Critical/Warning dispatch, the backend looks up the `cost` from the `REMEDIATION` dictionary (e.g., "$150,000") and writes `150000` to the `cost_avoided` column.
3.  **API Endpoint (`GET /api/savings`):** `SELECT SUM(cost_avoided) FROM telemetry_events;`
4.  **API Endpoint (`POST /api/clear-dispatch`):** Also resets the `cost_avoided` to 0 so the demo can be restarted cleanly.

### Frontend Implementation
-   Top right header: **`💰 Fleet Savings Avoided: $2,450,000`** (glows green when updating).

---

## Feature 3: Asset Intelligence Drawer (Educational Value)
**The Problem:** Presenters need a cheat sheet to explain *why* these specific sensors matter, and executives need to see that the physics and economics are grounded in reality.
**The Fix:** A slide-out information panel.

### Frontend Implementation
-   Next to the "📈 ML Forecast" title, add an `[ ℹ Asset Intel ]` button.
-   Clicking opens a right-side drawer or centered modal with two tabs:
    *   **[ Physics ]**: Explains the asset's function and the 3 monitored sensors, explicitly listing the Normal vs Critical Thresholds (e.g., "Intake Pressure: Nominal 1400 PSI / Critical <800 PSI (Gas Lock)").
    *   **[ Economics ]**: Explains the cost of failure. (e.g., "ESP Replacement: $150,000. Deferred Production: $45,000/day. Total Risk: ~$300k per event").
-   *Data Source:* All this information already exists in the `ASSET_REGISTRY` and `REMEDIATION` dictionaries.

---

## Feature 4: Cloud vs. Edge Latency Overlay (Technical Value)
**The Problem:** Why can't we just send this data to Google Cloud Vertex AI? Why do we need a GDC edge node on the rig?
**The Fix:** Visually prove that bandwidth constraints and cloud latency cause you to miss the failure window.

### Backend Implementation (`/api/plot/forecast/{asset_id}`)
Add a `?compare_cloud=true` query parameter to the Plotly endpoint.
When active, generate a **second prediction line (Purple Dashed)**:
1.  **Simulate VSAT Bandwidth Constraints:** Take the raw historical data (`y_vals`) and apply a rolling average (e.g., a 10-reading / 50-second moving average). This simulates downsampling data to save satellite bandwidth.
2.  **Simulate Processing Latency:** Shift the entire purple line 5 minutes (or whatever makes the visual impact clear) into the future.
3.  **Run the RUL Model:** Pass this smoothed, delayed data through the XGBoost RUL Regressor.
4.  **The Result:** The purple line will be flatter (it missed the high-frequency transient spike) and shifted right.

### Frontend Implementation
-   Add a toggle button above the chart: `[ ☁ Compare Cloud vs Edge Inference ]`
-   **The Demo Narrative:** "The orange line is GDC Edge AI — it sees the raw 100Hz vibration data instantly and predicts failure at 10:00 AM. The purple line is what happens if you average the data to save VSAT bandwidth and send it to the cloud. The cloud prediction arrives at 10:08 AM. But the pump exploded at 10:00 AM. Edge AI is mandatory here."

---

## Execution Order
1.  **DB Migration:** Add `cost_avoided` to AlloyDB.
2.  **Pure Pad Restructure:** Update `app.py` and `simulator.py` registries.
3.  **Savings Ticker & Asset Intel:** Update `app.py` API and `index.html` UI.
4.  **Cloud vs Edge Overlay:** Update the Plotly generation logic in `app.py`.
5.  **Build & Deploy:** Rollout the new containers.

*Document created: 2026-05-05*
*Resume from here with a clean context.*