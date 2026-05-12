# Gas Lift Compressor — Predictive Maintenance Manual

## System Overview

Gas lift is an artificial lift method that injects high-pressure gas into the wellbore annulus. The injected gas reduces the hydrostatic pressure of the fluid column, enabling reservoir pressure to drive production to surface. A surface reciprocating gas compressor (typically Ariel, Gemini, or Exterran packaged unit) supplies the injection gas at pressures of 800–1,200 PSI.

**Primary monitored channels:**
- **Discharge Pressure (PSI):** Measured at compressor outlet. Nominal range: 940–1,060 PSI. Drop indicates valve failure or compressor unloading.
- **Discharge Temperature (°F):** Measured at compressor outlet. Nominal range: 140–178°F. Rise indicates cooling system degradation or inter-stage compression inefficiency.
- **Frame Vibration (mm/s):** Measured on compressor frame. Nominal range: 1.0–2.5 mm/s. Rise indicates crankshaft bearing wear, unbalanced piston loads, or valve knocking.

## The Delta-T Diagnostic Principle

SCADA alarms on absolute discharge temperature (e.g., High alarm at 215°F, High-High at 230°F). Operators typically accept elevated readings during hot summer days, assuming ambient temperature is the cause. This masks progressive cooling system fouling.

GDC monitors the *rate of change* of discharge temperature relative to a baseline, independent of ambient conditions. If discharge pressure and suction pressure remain constant (same compression ratio, same inter-stage heat generation) but discharge temperature trends upward at 1–2°F per day over multiple days, this identifies the cause as a cooling system issue — not ambient temperature variation.

This delta-T trend analysis is the foundation of GDC's thermal runaway detection and is genuinely invisible to absolute-threshold SCADA monitoring.

---

## Thermal Runaway (Cooling System Fouling)

### Failure Mechanism
Reciprocating gas lift compressors generate substantial heat during compression. Cooling is provided by one or both of:
- **Aerial fin-fan coolers (air-cooled):** Finned heat exchanger with an electric motor-driven fan. Fouling sources include cottonwood seeds (common in spring in many US basins), insect debris, dust (Permian Basin, Bakken), and oil mist coating. Fouling reduces convective heat transfer by 15–40%.
- **Water jacket / inter-stage coolers (water-cooled):** Produced water scaling (calcium carbonate, barium sulfate) or glycol fouling reduces coolant-side heat transfer. Common in offshore or high-water-cut production.

As cooling efficiency degrades, discharge temperature rises progressively. Above 230°F, cylinder head seals and valve materials (typically Nylon or PEEK polymer) begin to degrade. Above 250°F, risk of detonation-related damage increases.

### What GDC Detects (That SCADA Misses)
- **Discharge temperature trending upward** over 24–72 hours while suction and discharge pressures remain constant — the signature of fouling, not ambient variation
- **Rate of temperature increase** — GDC calculates the temperature trend rate under constant-load conditions, predicting when the SCADA High alarm (215°F) and High-High alarm (230°F) will be triggered
- **Temperature deviation from seasonal baseline** — GDC compares current temperature against historical same-season operating data, isolating fouling from weather effects

SCADA operators routinely accept readings of 195–210°F as "normal summer operation." GDC detects when the *upward rate* of temperature change under constant operating conditions indicates progressive cooling capacity loss.

### Resolution Options
1. **Reduce Compressor Speed 20%:** Reduces thermal load immediately. Lowers discharge temperature by 8–15°F typically. Buys time for maintenance dispatch. (Cost: Partial production deferral, Time: Instant — control system command)
2. **Aerial Fin-Fan Cooler Flush:** Blow out fin-fan cooler with compressed air or pressure washer. Removes cottonwood, dust, and debris. Restores cooling capacity typically 80–100%. (Cost: $0 parts, ~0.75 hours labor per unit, Time: 45–60 minutes)
3. **Water Jacket / Inter-Stage Cooler Descale:** Chemical descaling flush of water-side heat exchanger. Requires coolant loop isolation. (Cost: $800 chemical, 3–4 hours labor, Time: 4 hours)
4. **Emergency Compressor Shutdown:** If discharge temperature exceeds 245°F, shut down immediately to prevent valve failure or head damage. (Cost: All wells on injection system offline until resolved, Time: Until repaired)

### Workforce Scheduling Optimization
Aerial cooler cleaning requires one mechanic with compressor operator certification and approximately 45 minutes per unit. No parts or specialized tools are required beyond a compressed air wand or pressure washer.

**Key recommendation principle:** If a scheduled crew visit to the pad is within 24 hours, appending a cooler flush to the existing work order costs zero additional travel expense. The scheduled crew absorbs the task with spare capacity. An emergency dispatch at a later date costs $800–$2,500 in truck roll costs plus a 4-hour compressor outage (all injection wells offline during compressor downtime).

---

## Check Valve Failure

### Failure Mechanism
The check valve (non-return valve) in the compressor discharge prevents reverse gas flow during shutdown or pressure excursions. Valve disk failure causes immediate reverse flow — discharge pressure collapses as high-pressure gas from the injection pipeline flows back through the compressor. This is an acute, rapid failure.

### What GDC Detects
- **Discharge pressure declining rapidly** — pressure loss of 50–200 PSI within seconds to minutes of valve failure onset
- **Vibration spike** — reverse flow creates significant acoustic and mechanical excitation of the compressor frame

### Resolution Options
1. **Reduce Compressor Speed and Isolate:** Lower speed immediately, close discharge isolation valve to prevent further reverse flow. (Cost: $0, Time: Instant)
2. **Emergency Shutdown and Valve Replacement:** Pull compressor offline, replace check valve disk or full valve cartridge. (Cost: $3,200–$8,500 parts + labor, Time: 4–8 hours)
3. **Full Compressor Overhaul:** If reverse flow caused internal damage, full overhaul may be required. (Cost: $25,000–$85,000, Time: 2–5 days)

---

## Journal Bearing Wear

### Failure Mechanism
Crankshaft journal bearings in reciprocating compressors are subject to gradual wear due to lubrication breakdown, oil contamination, or overloading. As bearing clearance increases, crankshaft imbalance grows and frame vibration rises progressively. Without intervention, bearing seizure destroys the crankshaft and connecting rods.

### What GDC Detects (That SCADA Misses)
- **Frame vibration rising progressively** over days to weeks — from 1.5 mm/s toward 5–8 mm/s, well below the SCADA HH alarm (typically 12 mm/s)
- **Vibration increasing under constant load** — distinguishes mechanical wear from process-induced vibration
- **Rate of vibration increase** — GDC predicts when the HH alarm will be reached, giving the maintenance team days to plan a scheduled bearing swap

### Resolution Options
1. **Reduce RPM 10% and Schedule Planned Replacement:** Buy 24–48 hours for parts ordering and crew scheduling. Monitor vibration closely. (Cost: $0 immediate, Time: Instant)
2. **Planned Bearing Replacement During Scheduled Downtime:** Order bearing set, schedule mechanic crew, replace during next planned maintenance window. (Cost: $8,000–$15,000 parts + labor, Time: 8 hours planned downtime)
3. **Emergency Bearing Replacement:** Stop unit now, replace bearings on an emergency basis to prevent seizure. (Cost: $15,000–$25,000 emergency labor premium, Time: 12–24 hours)
4. **Emergency Compressor Rebuild:** If seizure has occurred, crankshaft and connecting rods may require replacement or overhaul. (Cost: $85,000+, Time: 2–5 days)
