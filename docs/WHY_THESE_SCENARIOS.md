# Why These Scenarios — The Demo Narrative

## The Core Differentiator

Traditional SCADA and sensor-based monitoring systems are fundamentally **reactive**. They alarm when a sensor crosses a pre-programmed threshold — by which point, the failure is already in progress. GDC's predictive approach does something categorically different: it recognizes the **multivariate pattern** that precedes a failure, days or weeks before any individual sensor would trigger an alarm.

The three demo scenarios were specifically chosen to represent the three distinct types of value GDC delivers. Each scenario answers the question: *"Why couldn't you just configure a better SCADA setpoint?"*

---

## Why SCADA Can't See These (The Honest Answer)

Before explaining each scenario, it's worth being precise about what SCADA *can* and *cannot* do:

**What SCADA does well:**
- Single-sensor threshold alarms (PSI < 800, Temp > 280°F)
- Rate-of-change alarms (PSI dropping faster than X PSI/min)
- Simple calculated values (differential pressure, pump efficiency at a single point in time)

**What SCADA cannot do:**
- Recognize **multivariate signatures** — e.g., "current is declining slowly AND vibration is rising at a specific sub-harmonic frequency AND intake pressure is holding stable" = early-stage impeller erosion
- **Trend a sensor relative to its own baseline** under constant load conditions (distinguishing ambient temperature rise from equipment fouling)
- Detect **compensation behavior** — a driller manually increasing SPM to maintain pressure, which makes the pump look healthy when it's actually losing efficiency
- **Project a trajectory** to predict when a threshold will be crossed, accounting for the specific failure physics of each fault type

The three scenarios exploit exactly these gaps.

---

## Scenario 1: Pad Alpha — ESP Sand Ingress
### "14 days of advance warning on a $145,000 pump that takes 12 days to order"

**The failure physics:**
Formation sand erodes the tungsten carbide impeller stages inside the ESP. It's progressive: the first grains of sand that enter the pump begin wearing micro-channels into the vane faces. Over days to weeks, these channels grow until the impeller stages are too damaged to maintain flow.

**What SCADA sees:**
- Intake pressure: NORMAL (1,400 PSI — sand isn't blocking flow yet)
- Motor temperature: Slightly elevated (friction, but below High alarm)
- Vibration: Creeping upward but below the 8 mm/s High-High alarm
- **SCADA conclusion: All sensors in normal range. No action required.**

**What GDC sees (that SCADA misses):**
- Motor current is declining relative to operating speed — the pump is doing less hydraulic work as stages lose efficiency (this is the earliest indicator, appearing before vibration amplitude changes significantly)
- Vibration is rising, and the *pattern* of that rise (gradual, correlated with declining current) matches the specific signature of impeller vane erosion — not cavitation, not bearing wear, not electrical issues
- The *rate* at which both sensors are trending gives the model a projected time-to-threshold of approximately 14 days

**The agentic value:**
GDC queries the ERP (SAP MM) and finds: no sand-handler ESP in local inventory, 12-day standard lead time from Baker Hughes Centrilift in Claremore, OK. With a 14-day failure window and a 12-day lead time, the operator has a 2-day buffer to order and still receive parts before failure.

**Why this is compelling:**
If the operator waits for the SCADA vibration alarm (which fires 24–48 hours before catastrophic failure), they will be ordering a pump with a 12-day lead time and facing 10+ days of shut-in deferred production. At $8,500/day production value, that's **$85,000–$120,000 in avoided losses** from a timely order.

*"GDC predicted this 14 days out. SCADA would have told you 24 hours out — too late to avoid the wait."*

---

## Scenario 2: Pad Bravo — Gas Lift Thermal Runaway
### "A 45-minute cooler flush that saves a $150,000 compressor rebuild and 4 wells offline"

**The failure physics:**
The gas lift compressor (Ariel reciprocating package) compresses lift gas at 1,000 PSI. Compression generates significant heat. Cooling is provided by an aerial fin-fan cooler — a large finned radiator with an electric fan. In Permian Basin operations, the fins accumulate cottonwood seeds, dust, and insect debris. Fouling reduces cooling efficiency by 15–40%, and discharge temperature rises progressively until the cylinder head seals and valve materials (PEEK polymer) begin to degrade. Above 245°F, thermal seizure becomes a risk.

**What SCADA sees:**
- Discharge pressure: NORMAL (1,000 PSI)
- Discharge temperature: 205°F — elevated but below the 215°F High alarm
- Frame vibration: NORMAL
- **SCADA conclusion: Temperature is a bit high but it's a hot day. No action required.**

**What GDC sees (that SCADA misses):**
- Ambient temperature on this particular day is 82°F — same as the last two weeks.
- Over the last 8 days, discharge temperature has risen from 185°F to 205°F under *constant load* (same suction and discharge pressures, same speed).
- A 20°F rise under constant load means the cooling system's heat rejection capacity has degraded by approximately 25%.
- GDC's delta-T analysis (temperature gain per unit of compression work) is trending toward the 215°F High alarm in approximately 72 hours at the current rate.

**The agentic value:**
GDC queries the FSM (IBM Maximo) and finds: Crew B (2 mechanics, certified for compressor operations) is scheduled at Pad Bravo *tomorrow at 14:00* for transmitter calibration on Well B-3. Aerial cooler flush requires 45 minutes and no parts. Appending the task to their existing work order costs zero additional travel.

**Why this is compelling:**
An emergency dispatch to flush the cooler next week (after the alarm fires) costs $1,800 in truck roll, plus a 4-hour compressor outage affecting all wells on the injection system. Appending the task to tomorrow's route costs $0. 

*"GDC spotted a cooling problem developing over 8 days that looked like normal temperature variation to SCADA. By checking the maintenance schedule, the agent found a crew already heading to the site tomorrow — the fix costs nothing."*

---

## Scenario 3: Rig 42 — Mud Pump Valve Washout
### "A controlled pump swap that prevents a stuck-pipe incident worth $500,000+"

**The failure physics:**
The triplex mud pump's valve assembly consists of a polyurethane valve insert seated on a hardened steel seat. High-pressure drilling fluid containing barite, sand, and drill solids flows through this valve at 3,000 PSI on every stroke. Over 100–300 pump hours, the abrasive fluid erodes a small channel around the valve seat — a "washout." As the channel grows, each stroke leaks more fluid backward, reducing volumetric efficiency.

**What SCADA sees (and why it's masked):**
This is the most subtle scenario, because *the driller actively hides the problem from SCADA without knowing it.*

When a valve starts washing out, standpipe pressure begins to drift slightly lower. The driller's automatic response is to increase stroke rate (SPM) to maintain the required flow rate for hole cleaning. From SCADA's perspective:
- Standpipe pressure: NORMAL (driller compensated)
- Total flow rate: NORMAL (driller compensated)
- **SCADA conclusion: Normal drilling operations. No action required.**

The driller has inadvertently masked the efficiency loss. SCADA can only see that the pump is delivering the required flow — it cannot see that the pump is working harder than it should to deliver that flow.

**What GDC sees (that SCADA misses):**
- SPM has been slowly increasing over the last 3 hours (from 89 to 96 SPM) while standpipe pressure has remained constant.
- Volumetric efficiency — calculated as actual output per stroke vs theoretical — has declined from 95% to 81%.
- Fluid end temperature is rising slightly (fluid leaking backward generates heat in the liner).
- This is the exact multivariate signature of valve seat washout. Not piston seal wear (which shows a different temperature pattern), not liner wear (which progresses more slowly).

**The agentic value (and the safety dimension):**
GDC queries the Rig Control System (Pason EDR) and finds: MUD-RIG42-2 and MUD-RIG42-3 are available. Current total flow requirement is 700 GPM. ECD window allows the transition. Next pipe connection is in 22 minutes.

The critical point: **you cannot stop mud circulation while actively drilling.** Stopping the pump while in a reactive shale formation would allow cuttings to fall back, the wellbore walls to swell, and the drill string to become mechanically stuck. Stuck pipe typically costs $1–5M to resolve. The agent's recommendation is not "stop the pump" — it's "perform a controlled transition, bringing the standby pump online first to maintain total flow, then reducing the failing pump."

*"SCADA says the pump is working fine because the driller is compensating. GDC sees the compensation itself — rising SPM against constant pressure — as the diagnostic signal. And it knows the correct response isn't to stop: it's a controlled pump swap that keeps ECD stable."*

---

## Why Three Different Scenarios?

Each scenario demonstrates a different dimension of GDC's value:

| Scenario | Primary Value | Time Horizon | Enterprise System | "SCADA Would Have..." |
|---|---|---|---|---|
| ESP Sand Ingress | **Supply chain lead time** | Days to weeks | ERP (SAP MM) | Alarmed 24h before catastrophic failure — too late to avoid the wait |
| Gas Lift Thermal Runaway | **Workforce route optimization** | Days | FSM (Maximo) | Alarmed when temp crossed the absolute limit — emergency callout required |
| Mud Pump Valve Washout | **Active operational control** | Hours | Rig Control (Pason) | Never alarmed at all — standpipe pressure looked normal |

Together, they make the argument that predictive maintenance on GDC is not just about "detecting things faster." It's about:
1. Having enough lead time to procure parts before failure (not after)
2. Integrating with the operational schedule to eliminate unnecessary cost
3. Detecting failure modes that conventional monitoring physically cannot see

---

## The Presenter's Closing Statement

> "What you've seen is three different assets, three different failure modes, and three different ways GDC gets ahead of the problem — weeks before SCADA would alarm, days before a part needs to be on site, or detecting patterns that a threshold alarm would never catch at all. The AI didn't replace the operator. It gave them the right information at the right time, checked what they needed to fix it, and told them exactly what to do. That's predictive maintenance at the edge."
