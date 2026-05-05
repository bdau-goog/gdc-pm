# GDC-PM Demo UI Overhaul — Action Plan
**Status:** APPROVED — Ready for Implementation  
**Baseline Commit:** `85a78ca` — "Save stable 3-column UI and timeline fixes before major visual overhaul"  
**Goal:** Transform the `fault-trigger-ui` from a functional-but-flat tabular panel into a compelling, immersive Operations Command Center that conveys both the **business value** (fast local detection, survivability during network outages, local team dispatch) and the **technical value** (edge ML on GDC, multivariate anomaly detection via 3D sensor clustering) of GDC Predictive Maintenance.

---

## What We Are Replacing & Why

**Current State:**
- A 3-column layout: Fault Injection controls (left) | Events log (center) | Asset Selector list (right)
- Grafana dashboards for historical time-series charts
- Status: Functional, but dry and tabular — hard to convey "wow" to non-technical audiences

**Reference:** `~/gdc-das-life` is the gold standard. It uses:
- `das-web-trigger`: A Leaflet.js interactive *real geo-map* of wells, clickable to inject signals
- `das-web-ui/dashboard.html`: An event log + embedded iframe from the `plotly-visualizer` microservice
- `plotly-visualizer`: A dedicated FastAPI service that renders a 3D Plotly chart of DAS fiber sensor data per event

**Our approach:** Consolidate everything into a single unified `fault-trigger-ui` frontend (no separate plotly service). Our stack: FastAPI + vanilla JS/HTML. The key insight for PdM is that *space* (which plant, which asset) and *3D sensor clustering* are the "aha" visuals.

---

## Phase 1 — Interactive Plant Map (Business Value: Situational Awareness)

### What We Are Building
Replace the right-hand "Asset Selector" list with a stylized **SVG Plant Diagram** of the three facility zones. It shows the 10 assets spatially so operators immediately see which site has a problem.

### Asset Layout (for the SVG map)
```
Valley Substation                Ridge Plant                  Basin Station
┌─────────────────────┐         ┌─────────────────────┐      ┌──────────────┐
│  ⚙ COMP-V01         │         │  ⚙ COMP-R01         │      │ ⚙ COMP-B01  │
│  ⚙ COMP-V02         │         │  ⚙ COMP-R02         │      │             │
│  🔄 TURB-V01        │         │  🔄 TURB-R01        │      │ ⚡ XFMR-B01 │
│  ⚡ XFMR-V01        │         │  ⚡ XFMR-R01        │      │             │
└─────────────────────┘         └─────────────────────┘      └──────────────┘
```

### Asset IDs (10 assets total)
| Asset ID     | Type        | Site          |
|--------------|-------------|---------------|
| COMP-V01     | Compressor  | Valley        |
| COMP-V02     | Compressor  | Valley        |
| TURB-V01     | Turbine     | Valley        |
| XFMR-V01     | Transformer | Valley        |
| COMP-R01     | Compressor  | Ridge         |
| COMP-R02     | Compressor  | Ridge         |
| TURB-R01     | Turbine     | Ridge         |
| XFMR-R01     | Transformer | Ridge         |
| COMP-B01     | Compressor  | Basin         |
| XFMR-B01     | Transformer | Basin         |

### Behavior Per Node
- **Normal:** Solid green border, no animation
- **Warning (Degrading):** Orange border, slow 2s pulse glow animation
- **Critical:** Red border, rapid 1s pulse, red "dispatch required" badge
- **Click:** Selects that asset → updates the Fault Injection controls → updates the 3D Sensor plot for that asset

### Visual Style
- Dark theme: `#0b0c10` background (same as `das-web-trigger`)
- Font: Inter + JetBrains Mono (same as `das-web-trigger`)
- SVG map floats over a subtly styled topology background (think industrial schematic lines connecting sites)
- Color palette: Green `#00e676`, Yellow `#ffb300`, Orange `#ff6d00`, Red `#f44336`

---

## Phase 2 — 3D Multivariate Sensor Visualization (Technical Value: Edge ML)

### What We Are Building
A **3D Plotly scatter plot** showing the last 100 readings for the selected asset, rendered server-side by FastAPI and returned as a full interactive HTML fragment embedded in an iframe.

### New FastAPI Endpoint
```
GET /api/plot/3d/{asset_id}
```
- Queries AlloyDB for the last 100 `telemetry_readings` rows for the given asset_id
- Generates a `plotly.graph_objects.Figure` with a 3D scatter trace:
  - X = `pressure_psi`
  - Y = `temperature_f`
  - Z = `vibration_mm`
  - Color = by `predicted_label` (green=normal, yellow=advisory, orange=warning, red=critical)
- Returns a self-contained HTML page (using `fig.write_html(...)` with `full_html=True`)
- The `index.html` will embed this via `<iframe src="/api/plot/3d/{asset_id}">` and reload it every 10 seconds

### The Visual Story Explained in the Demo
> "Normal readings form a tight green cluster in 3D space — all three metrics are correlated and stable. 
> Watch what happens when I inject 'Thermal Runaway'. Temperature rises, but pressure stays normal. 
> A classic single-metric threshold alarm on temperature alone would wait until it crossed 160°F. 
> Our XGBoost model running *right here on GDC*, sees the breakout from the normal cluster immediately 
> and fires an alert at 148°F. That's the difference between a planned coolant flush and a catastrophic failure."

### Dependencies to add to `requirements.txt`
```
plotly==5.22.0
kaleido==0.2.1   # For static image export if needed
```

---

## Phase 3 — Long-Term Gradual Degradation Injection

### The Problem with Current Fault Injection
Current faults inject a *static* changed reading once. This doesn't visually illustrate how ML catches *progressive* degradation over time.

### What We Are Building
A new "Simulate Degradation" injection mode in the backend.

**New FastAPI endpoint:**
```
POST /api/inject/degrade
Body: {"asset_id": "COMP-V01", "fault_type": "bearing_wear", "duration_seconds": 60}
```

**Backend behavior:**
- Launches a **background asyncio task**
- Over `duration_seconds` (e.g., 60), incrementally adjusts the simulator parameters for that asset:
  - Bearing Wear: `vibration_mm` ramps +0.3/step every 5s
  - Thermal Runaway: `temperature_f` ramps +2°F/step every 5s
  - Fouling: `pressure_psi` ramps -1.5 psi/step every 5s
- After the `duration_seconds`, values reset to normal baseline (auto-recovery)

**UI Behavior:**
- The 3D plot refreshes every 10 seconds and the viewer literally **watches the data points migrate** from the green normal cluster into the orange/red fault zone over time
- The Event Log captures an alert when the ML model crosses the prediction threshold (not when the injection starts)
- This shows **detection lag is minutes, not hours** — key business value for PdM

---

## Phase 4 — "Cloud Disconnect" Simulation Toggle

### Purpose
To prove GDC's survivability story: the plant keeps running and detecting faults even when the central cloud is unreachable.

### UI Component
A toggle switch in the header:
```
🌐 Cloud Connected  ⟵  [TOGGLE] ⟶  ✈ Airgap Mode
```

**When toggled to "Airgap Mode":**
- Header turns a dim red/amber color
- "Cloud Connection Lost" badge appears
- The map, telemetry, 3D plot, and event log **continue to function** (they only talk to the local GDC services, never directly to GCP)
- A floating "GDC Edge ✅ Operational" badge appears to emphasize the point

**Backend behavior:**
- The toggle call `POST /api/simulate/airgap?enabled=true` simply writes a flag to an in-memory state
- If enabled, the `/api/events` and `/api/telemetry` endpoints add a header `X-Data-Source: local-gdc-only` (the frontend reads this to show the badge)
- This is entirely simulated — the flag doesn't actually block network calls — the UX tells the story

---

## Phase 5 — Local Dispatch Ticket Flow

### Purpose
To illustrate the "actionability" value: when GDC detects a fault, it immediately creates a local remediation work order and alerts on-site teams, even without cloud connectivity.

### UI Behavior
When a Critical or Warning event is detected (appears in Event Log):
1. An animated "Local Alert" banner slides in from the top: **"⚠ DISPATCH REQUIRED: Thermal Runaway — COMP-V01 — Valley Substation"**
2. The asset node on the Plant Map gets a red pulsing circle with a white exclamation mark
3. Clicking the asset node on the map (or clicking the alert banner) opens a **Dispatch Modal**:
   ```
   ┌─ Local Work Order ─────────────────────────────────────┐
   │  Asset: COMP-V01 (Valley Substation Compressor #1)      │
   │  Alert: Thermal Runaway Detected at 14:23:07 UTC        │
   │  Risk: Potential compressor failure in ~2-4 hours       │
   │  Action Required: Coolant system inspection + flush     │
   │  Estimated Downtime Avoided: $150,000+                  │
   │  Local Contact: Valley Station Team (Extension 412)     │
   │                                                          │
   │  [Acknowledge & Dispatch]  [View Sensor Data]           │
   └─────────────────────────────────────────────────────────┘
   ```
4. Clicking **"Acknowledge & Dispatch"** clears the alert badge on the map and logs a "Acknowledged" event in the Event Log

### Backend support needed
- `POST /api/events/{event_id}/acknowledge` — marks an event as acknowledged in AlloyDB
- `GET /api/events` already returns events; add `acknowledged` boolean field to the response

---

## Full UI Layout (New Design)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚡ GDC Predictive Maintenance — Operations Command       🌐 [Cloud/Airgap] │
├──────────────────────────────┬──────────────────────────────────────────────┤
│                              │  ┌─────── Plant Asset Map ────────────────┐  │
│  LIVE EVENT LOG              │  │  [Valley]   [Ridge]   [Basin]          │  │
│  ─────────────────────────   │  │  Compressor Turbine Transformer icons  │  │
│  ⚠ 14:23 COMP-V01 CRITICAL  │  │  with live health colors per asset     │  │
│  ⚙ 14:18 XFMR-R01 ADVISORY  │  └────────────────────────────────────────┘  │
│  ✓ 14:11 COMP-B01 NORMAL    │                                               │
│  ...                         │  ┌─────── 3D Sensor Cluster ──────────────┐  │
│                              │  │  PSI × Temp × Vibration                │  │
│  FAULT INJECTION             │  │  (Plotly 3D iframe for selected asset)  │  │
│  ─────────────────────────   │  └────────────────────────────────────────┘  │
│  Selected: COMP-V01          │                                               │
│  [Bearing Wear (Gradual)]    │  ┌─────── Inject Controls ────────────────┐  │
│  [Thermal Runaway (Gradual)] │  │  ○ Bearing Wear (Gradual ~60s)         │  │
│  [PRD Failure (Instant)]     │  │  ○ Thermal Runaway (Gradual ~45s)      │  │
│  [Reset / Normal]            │  │  ● PRD Valve Failure (Instant)         │  │
│                              │  │  [Inject Fault]  [Reset to Normal]     │  │
└──────────────────────────────┴──────────────────────────────────────────────┘
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `gke/fault-trigger-ui/requirements.txt` | Add `plotly==5.22.0` |
| `gke/fault-trigger-ui/app.py` | New endpoints: `/api/plot/3d/{asset_id}`, `/api/inject/degrade`, `/api/simulate/airgap`, `/api/events/{id}/acknowledge` |
| `gke/fault-trigger-ui/index.html` | Full redesign: SVG Plant Map + 3D iframe + Dispatch Modal |
| `gke/fault-trigger-ui/Dockerfile` | Ensure plotly installed |
| `gke/fault-trigger-ui/k8s/fault-trigger-ui.yaml` | No changes expected |

---

## Implementation Order

1. **Backend first:** Add `plotly` to `requirements.txt`. Add `/api/plot/3d/{asset_id}` to `app.py`. Test locally.
2. **Frontend 3D panel:** Add the iframe panel to `index.html` and wire it to auto-reload.
3. **Plant Map SVG:** Build the SVG map layout with the 10 asset nodes and health-state wiring.
4. **Fault injection UI:** Replace the old list selector with the new injection panel that is driven by clicking map nodes.
5. **Gradual degradation:** Add the `/api/inject/degrade` background task endpoint.
6. **Airgap toggle:** Add the header toggle and UI state to show/hide cloud status.
7. **Dispatch modal:** Add the dispatch modal popup linked to critical events.
8. **Build & deploy:** `docker build`, `docker push`, `kubectl rollout restart`.

---

## Key Demo Script (30-second storyline)

> "Our plant has 10 monitored assets across three remote locations. [Point at Map] Everything is green — normal operations. 
> I'm going to simulate a real-world scenario: the bearing on Compressor V01 is starting to wear. 
> [Click Bearing Wear on COMP-V01 → Hit Inject] 
> Now watch the 3D sensor chart... over the next 60 seconds, you'll see the vibration signal migrate out of the normal cluster. 
> [Wait ~30s] The model just triggered — our local GDC edge is dispatching an alert to the Valley Station team. 
> [Flip Airgap Toggle] And notice: even though I've just taken the cloud network offline, the system is still operational. 
> Local detection, local alerting, local dispatch. That's GDC."

---

*Document created: 2026-05-05*  
*To resume from a clean context: read this file, look at baseline commit `85a78ca`, and start with Phase 2 (3D Plotly API endpoint in `app.py`).*
