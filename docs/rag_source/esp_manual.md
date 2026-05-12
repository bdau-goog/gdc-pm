# Electrical Submersible Pump (ESP) — Predictive Maintenance Manual

## System Overview

An Electrical Submersible Pump (ESP) is a downhole centrifugal pump deployed on a tubing string inside the wellbore. The motor and pump assembly is permanently submerged in produced fluid, which provides cooling. The surface Variable Frequency Drive (VFD) controls motor speed and continuously monitors motor current (amps), voltage, and winding temperature via a surface-mounted motor controller.

**Primary monitored channels:**
- **Intake Pressure (PSI):** Measured by a downhole pressure/temperature gauge (PDG). Nominal range: 1,200–1,600 PSI. Decline indicates reduced reservoir inflow or gas entrainment.
- **Motor Winding Temperature (°F):** Measured by the PDG or motor sensor. Nominal range: 180–220°F. Rise indicates inadequate cooling or electrical overload.
- **Motor Vibration (mm/s):** Measured by the PDG accelerometer. Nominal range: 0.8–2.0 mm/s. Rise indicates mechanical imbalance, bearing wear, or fluid-end damage.
- **Motor Current (A):** Measured at the VFD surface panel. Nominal range: 60–90 A. The most sensitive early indicator of pump hydraulic condition and motor health.

## Why Motor Current Is the Critical Early Indicator

Motor current is directly proportional to the hydraulic work the pump performs. As impeller stages erode from sand ingress, or as gas entrains and reduces fluid density, the pump performs less work — current declines. This relationship means current deviation from baseline is detectable *before* any other sensor crosses an alarm threshold.

A SCADA system alarming on absolute current (e.g., "< 40 A underload" or "> 100 A overcurrent") will only trigger when the failure has already progressed significantly. The predictive signal is in the *trend rate* of current relative to operating speed — not the absolute value.

---

## Sand Ingress

### Failure Mechanism
Formation sand erodes impeller stage vanes, bowls, and radial bearings over time. Erosion is progressive: early-stage erosion is microscopic and measurable only through pump efficiency monitoring. Late-stage erosion causes gross mechanical imbalance, impeller fragmentation, and motor seizure.

Sand-handler ESP configurations (tungsten carbide radial bearings, hardened impeller and diffuser materials) slow erosion but do not prevent it. In high-sand formations, even sand-handler pumps require periodic replacement.

### What GDC Detects (That SCADA Misses)
The combined multivariate signature of sand ingress emerges **days to weeks before any SCADA threshold is crossed:**
- **Motor current declining** relative to operating speed — pump hydraulic efficiency dropping as stages erode (current may decline from 80 A toward 65–70 A while pump is still circulating)
- **Vibration rising slowly** from sub-harmonic impeller imbalance — often starting in the 0.38–0.47× running frequency range, manifesting as overall amplitude creep from 1.2 to 2.5–3.0 mm/s
- **Intake pressure holding normal** — masking the failure from pressure-only SCADA monitoring
- **Motor temperature slightly elevated** — additional friction from eroded stages

SCADA's vibration High-High (HH) alarm (e.g., > 8 mm/s) fires when impeller damage is severe. By that point, stage replacement is mandatory.

### Resolution Options
1. **Reduce Pump Rate 20% via VFD:** Lowers sand influx velocity through the pump. Slows erosion progression. Allows time to plan workover. (Cost: $0, Time: Instant)
2. **Inject Chemical Sand Consolidator:** Downhole chemical treatment to consolidate loose sand in the near-wellbore region. Effectiveness varies by formation. (Cost: $5,000, Time: 4 hours)
3. **Schedule ESP Workover — Pull and Replace Assembly:** Pull ESP string, replace worn stages or full assembly with sand-handler configuration. Requires workover rig. (Cost: $85,000–$145,000, Time: 3–5 days)

### Procurement Lead Times (Sand-Handler Configuration)
Standard ESP replacement pumps (400-series, clean service) are often available from regional distribution hubs. Sand-handler configurations with tungsten carbide radial bearings and hardened stages are custom-assembled and typically require:
- **Local field warehouse:** 0–3 days (if matching standard unit available)
- **Regional hub (e.g., Midland, TX):** 3–7 days
- **Manufacturer facility (Baker Hughes Centrilift — Claremore OK; Schlumberger — Rosharon TX):** 10–21 days
- **Air freight premium** for expedited delivery: $6,000–$10,000 above standard cost

**Key recommendation principle:** If GDC predicts failure in 14 days and manufacturer lead time is 12 days, order immediately. Waiting for the SCADA alarm (which fires 24–48 hours before failure) guarantees 10+ days of deferred production.

---

## Gas Lock

### Failure Mechanism
Gas entrainment in the fluid stream causes the ESP impeller to encounter a compressible gas void instead of liquid. Above a critical Gas Void Fraction (GVF), typically 50–70%, centrifugal pump efficiency collapses. The pump "locks up" — spinning but no longer moving fluid. Without fluid cooling, the motor overheats rapidly.

Gas lock is an acute event that progresses within 15–30 minutes from onset of elevated GVF to full pump lock-up.

### What GDC Detects (That SCADA Misses)
- **Intake pressure declining** as gas void fraction rises in the pump intake (from 1,400 PSI toward 875–1,000 PSI) — a trend the XGBoost model recognizes as the gas lock trajectory even before the threshold is crossed
- **Motor current declining sharply** — as fluid density drops with gas entrainment, the pump does less hydraulic work (current may drop from 80 A to 30–45 A as the void fraction rises)
- **Vibration increasing** — unstable flow through the impeller stages as gas and liquid alternate

SCADA alarms when intake pressure crosses 800 PSI — by which point the pump is already struggling or locked. GDC recognizes the combined current-pressure-vibration signature earlier.

### Resolution Options
1. **Reduce VFD Frequency 10–15%:** Lowers pump intake pressure requirements, allowing gas to migrate up the annulus rather than entering the pump intake. Most effective for mild to moderate GVF. (Cost: $0, Time: Instant — SCADA command)
2. **Open Casing Annulus Valve:** Bleeds gas from the casing annulus, reducing annulus pressure and gas migration into the pump intake. (Cost: $500, Time: 2 hours — requires field visit)
3. **Shut Down and Allow Gas Migration:** If GVF is severe, shut pump down, allow gas to migrate up the annulus (typically 2–4 hours), then restart. (Cost: Production deferral, Time: 2–4 hours)

---

## Motor Over-Temperature

### Failure Mechanism
ESP motor windings require produced fluid flow past the motor for cooling. If flow rate drops (e.g., due to gas lock, declining reservoir PI, or pump wear), motor temperature rises. Above 280°F, winding insulation (typically Class H for ESP motors) begins to degrade. Insulation failure causes motor winding short-circuit and motor burnout, requiring a full ESP pull.

### What GDC Detects (That SCADA Misses)
- **Motor temperature trending upward** while intake pressure and motor current remain in normal ranges — indicates reduced cooling flow without full gas lock
- **Motor current slightly elevated** — motor working harder against reduced fluid cooling (increased resistance at higher temperature)
- **Rate of temperature rise** — GDC detects a temperature trend rate that predicts when 280°F will be reached, even when current absolute temperature (e.g., 240°F) has not yet triggered the SCADA HH alarm

### Resolution Options
1. **Reduce Pump Frequency 15% via VFD:** Reduces motor current draw and heat generation. Lower motor loading = lower temperature. (Cost: $0, Time: Instant)
2. **Increase Choke Opening (if surface flow controlled):** Increases produced flow rate through the motor cooling jacket. (Cost: $0, Time: Instant)
3. **Emergency Shutdown:** If temperature exceeds 270°F and is still rising, shut pump down immediately to prevent winding burnout. (Cost: Production deferral, Time: Until root cause resolved)
4. **Pull and Replace Motor:** If winding insulation has degraded (confirmed by insulation resistance test), replace motor on next workover. (Cost: $85,000–$200,000, Time: 3–6 days)
