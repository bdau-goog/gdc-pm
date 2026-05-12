# GDC-PM Phase 3.1 — Chart Refactor & Terminology Update
**Status:** Complete — Deployed to `gdc-edge-simulation`
**Date:** 2026-05-12
**Preceded by:** `PHASE_3_DEPLOYMENT_STATUS.md`

---

## Executive Summary
This session addressed critical UX and physics-alignment issues in the ML Predictive Forecast chart (`app.py:plot_forecast()`). The core functionality (XGBoost models, telemetry simulation, etc.) was sound, but the visualization of the data was confusing and occasionally contradictory.

### 1. Chart Layout & Rendering Fixes
*   **The Bug:** The `fig.update_layout(shapes=[...])` call was blindly overwriting the vertical lines added previously via `fig.add_shape()`, meaning the PNR, Cloud Alert, and Failure lines were constantly disappearing.
*   **The Fix:** Moved the "NOW" vertical line creation out of the `update_layout` parameters and into a sequential `add_shape()` call so all vertical markers accumulate correctly.

### 2. Time-to-Failure vs Sensor Slope Misalignment
*   **The Bug:** The orange ML prediction line was forcing a straight line from the current sensor reading directly to the critical threshold over exactly the RUL time window. This resulted in an impossibly steep slope that visually contradicted the actual gentle slope of the telemetry data.
*   **The Fix:**
    *   The orange dotted line now projects the *actual measured sensor slope* (e.g., `dpsi_dt`) into the future, remaining perfectly collinear with the blue historical data.
    *   The ML model's prediction is now visualized exclusively via a **solid vertical red line** spanning the full height of the chart at `now + rul_minutes`.
*   **The Narrative Impact:** This creates a powerful demo moment. The operator sees a gentle, "safe-looking" sensor trend line, but the ML model places a bright red failure line just 20 minutes out. *"The naive extrapolation says we have hours. The ML model recognizes the complex multi-variate signature of gas lock and says we have 20 minutes. This is why edge AI beats threshold alarms."*

### 3. Vertical Line Clarity
*   Pre-computed all key times (`ttf_time`, `cloud_alert_t`, `pnr_t`) before defining the X-axis range.
*   The X-axis is now tightly sized to ensure all active markers are visible, but capped at a max of 60 minutes ahead of `now` for the PNR extension to prevent high-PNR faults (like Sand Ingress at 120m) from rendering the live telemetry as a tiny unreadable sliver.
*   Three distinct line colors for clarity:
    *   `⚡ Alarm in Xm` (Red `#ff1744`) — at y=0.97
    *   `☁ Cloud T+20m` (Purple `#ce93d8`) — at y=0.89
    *   `⛔ PNR T+Ym` (Orange `#ff6d00`) — at y=0.81 (skipped if PNR=0)

### 4. Always-Visible Response Windows
*   Previously, the time comparisons between Edge vs Cloud were hidden behind the "Cloud Prediction" toggle.
*   Now, an always-visible callout box sits in the bottom right corner showing the decrementing response window remaining before physical damage (PNR) occurs, contrasting the Edge detection time (T+0) with the Cloud alert time (T+20m).
*   The toggle button (renamed to `☁ Show Arrows`) now exclusively adds horizontal span arrows between the vertical lines for additional visual emphasis.

### 5. Terminology Shift: "Failure" vs "Alarm"
*   **The Confusion:** Users were conflating the ML "Predicted Failure" with the physical "Point of No Return (PNR)". Why was failure predicted in 29m if the PNR was 120m out?
*   **The Clarification:** The XGBoost model predicts when the *sensor* will cross the critical threshold — which is when the conventional SCADA system would fire an alarm. The PNR is the physical deadline for irreversible equipment damage.
*   **The Change:**
    *   Chart text changed from `⚠ PREDICTED FAILURE` to `⚡ ALARM IN Xm — sensor threshold approaching`.
    *   Chart legend changed from `Failure Threshold` to `Alarm Threshold`.
*   **The Narrative Impact:** The edge AI is now augmenting the existing system, not replacing it. *"Your SCADA system will alarm in 29 minutes. We are telling you right now, giving you nearly half an hour of advance warning to resolve the issue before the alarm even sounds, and well before the 120m physical damage deadline."*

### 6. Confidence Band Visualization
*   **The Bug:** The noise band for the projection was calculated as `0.005–0.02 × y_start`. For a vibration reading starting at 2 mm/s, this resulted in an invisibly thin 0.04 mm/s band on a 1–9 mm/s chart.
*   **The Fix:** The cone now widens as a fraction of the *projected y-range* (or 10% of `y_crit` minimum), ensuring it is clearly visible across all asset classes and sensor scales.

## Summary for the Demo Script
The core demo flow should focus on **Gas Lock** on an ESP.
Gas lock has a 25-minute PNR. When injected, the model predicts the alarm threshold will be crossed in ~20 minutes. The vertical lines for Cloud Alert (20m), Alarm (20m), and PNR (25m) are tightly grouped, making the urgency visceral and demonstrating exactly why the 20-minute cloud latency renders traditional cloud analytics useless for O&G edge use cases.