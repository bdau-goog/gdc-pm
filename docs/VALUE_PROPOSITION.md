# GDC Predictive Maintenance — Value Proposition
### AI/ML on GDC vs. Traditional SCADA Monitoring

---

## The Core Statement

Traditional SCADA systems are excellent at simple operational boundaries — they ring a loud bell when a single sensor crosses a hard threshold (like Intake Pressure dropping below 800 PSI). However, by the time that threshold is crossed, the failure is already happening.

The AI/ML models deployed on GDC provide value where SCADA fundamentally cannot: **they recognize the multivariate pattern that precedes a failure, days or weeks before any individual sensor would trigger a conventional alarm.**

---

## Four Specific Gaps Where ML Beats SCADA

### 1. Recognizing Multivariate Signatures

SCADA looks at sensors in isolation. An ML model looks at the *relationship between* sensors simultaneously.

**Example — ESP Sand Ingress:** SCADA sees intake pressure, motor temperature, and vibration all sitting below their individual alarm limits, so it reports "Normal." The ML model detects that motor current is declining *while* vibration is rising at a specific sub-harmonic frequency. That specific combination of correlated variance is the signature of early-stage impeller erosion — visible to the model days or weeks before vibration hits the critical SCADA threshold.

### 2. Detecting Human Compensation (Masking)

Drillers and operators routinely compensate for equipment degradation through manual adjustments. This inadvertently masks the failure from SCADA.

**Example — Mud Pump Valve Washout:** As a valve begins to fail and discharge pressure drifts lower, the driller increases stroke rate (SPM) to maintain required drilling pressure. SCADA sees correct pressure and correct flow — it concludes operations are normal. The ML model tracks the ratio of SPM to discharge pressure (volumetric efficiency) and detects that the pump is working progressively harder to deliver the same output. It surfaces the degradation that the operator has hidden from SCADA without realizing it.

### 3. Projecting Trajectories — Time-to-Failure, Not Time-of-Failure

SCADA provides a snapshot of the present. ML models use causal rolling-window slope features to project a trajectory forward in time.

Instead of merely knowing that vibration is "high," the model understands the *rate of acceleration* of that vibration and can predict that the critical 8 mm/s threshold will be breached in approximately 14 days. This is the difference between "we have a problem" and "we have a problem and we have exactly 14 days to solve it before the pump is destroyed."

### 4. Enabling Agentic Resolution

Because the ML model buys the operator time, the GDC Agent has a window to act that did not previously exist. It can cross-reference ERP systems (SAP MM) to check parts inventory, or Field Service Management systems (IBM Maximo) to check crew schedules — and resolve the impending fault before it becomes a failure event.

- **SCADA world:** Alarm fires when pump is failing. Operator orders part. 12-day lead time. 10 days of shut-in deferred production. $85,000–$120,000 in lost production value.
- **GDC ML world:** Model predicts failure 14 days out. Agent sees 12-day lead time in SAP. Operator orders part the same day. Part arrives before failure. $0 deferred production.

---

## The One-Line Summary

> **SCADA tells you when equipment is breaking. GDC ML tells you when it *will* break, what the exact failure mode is, and precisely how to intervene before the damage is done.**

---

## Related Documents

- `WHY_THESE_SCENARIOS.md` — Detailed failure physics for each demo scenario
- `WHY_GDC.md` — Why this demo runs on GDC (Google Distributed Cloud) specifically
