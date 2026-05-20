# Next Session Prompt — GDC UI Fixes (Continued)

## What Was Fixed This Sprint

- **Sensor tabs**: Now a standalone row in the GDC AI panel (between GDC header and GDC chart) — correctly separated from the SCADA header
- **SCADA chart**: Now renders (Plotly.purge + newPlot + resize)
- **Bridge bar**: Larger (62px), glowing gradient fill, brighter text
- **Column resize handles**: Visible (8px wide, ⋮ icon, border highlights)
- **compareRowHeight**: Default bumped to 520px
- **_initColResizer**: Dataset guard prevents listener leak on navigation
- **Deployment note**: Use `kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm` after pushing :latest images — Kubernetes won't restart pods on tag-only pushes

---

## CRITICAL BUG: SCADA X-Axis Not Synced to GDC Chart

The SCADA chart renders but its **X axis shows a different time window** than the GDC chart:
- **GDC chart**: shows ~16:38 → NOW (~16:50) → 18:00 projection
- **SCADA chart**: shows ~16:31 → 16:40 (raw data extent, not GDC display window)

### Root Cause
In `renderChart()`, the SCADA x range is set as:
```javascript
range: [(gdcLayout.xaxis?.range?.[0] || histX[0]), histX[nowIdx]]
```
`gdcLayout.xaxis?.range?.[0]` is **null/undefined** (backend doesn't set it), so the fallback `histX[0]` is used. This is the raw start of the telemetry trace data, which is earlier than what the GDC chart displays.

### Fix
Replace the SCADA xaxis range with the **GDC chart's actual rendered x range**. After the GDC chart is drawn, read its layout:

```javascript
// After Plotly.react(elGdc, ...), get the actual displayed x range:
const gdcActualRange = elGdc.layout?.xaxis?.range;
// Use that range for SCADA left edge:
const xLeft = gdcActualRange?.[0] ?? gdcLayout.xaxis?.range?.[0] ?? histX[0];
const xRight = histX[nowIdx]; // SCADA stops at NOW, no projection
scadaLayout.xaxis.range = [xLeft, xRight];
```

Or alternatively: make the GDC chart `Plotly.react` first (it's synchronous enough), then read `elGdc.layout.xaxis.range` for the SCADA.

---

# Previous Sprint Notes Below
# Next Session Prompt — GDC UI Testing & Refinement

## Context

We are working in the `gdc-pm` repo. Primary files:
- `gdc-pm/gke/fault-trigger-ui/index.html` — Vue.js + Plotly single-page UI
- `gdc-pm/gke/grafana/k8s/grafana-configmap.yaml` — Grafana dashboard ConfigMap

Live at: **http://35.188.3.97**

Latest image digest: `sha256:c5a057ee09d9a150ce0f083668096454c692b3a481190a9ddc6adebb173d47c2`

---

## Completed This Sprint (for context)

- **SCADA chart fixed:** `gdcLayout` hoisted to outer scope of `renderChart()` — chart now renders correctly with shared X/Y axes
- **Sensor tabs:** Moved to GDC AI chart header using flex spacer; both charts switch on tab click
- **initialRulMap:** Per-asset map — navigating fleet → deepdive no longer resets advance notice
- **Column resizers:** Drag handles between Evidence/Agent/Resolution bottom panels; persisted in sessionStorage
- **Grafana:** `now-2h` default, all pressure panels use `"psi"` unit (no ksi auto-scale), ESP stat panels show descriptive display names
- **Ollama gemma4:27b:** Zone-f PVC lock broken — new PVC provisioned, NAP targeting `us-central1-c` for L4 GPU

---

## Session Goals — End-to-End UI Testing

Run through the complete demo narrative and document/fix any remaining issues. Priority order:

### 1. Verify SCADA Chart Renders (first priority check)
- Open deep dive on any asset, inject a fault, confirm the Traditional SCADA chart shows:
  - The Live Telemetry line (blue, historical only, no future projection)
  - The SCADA Alarm Threshold horizontal dashed line
  - Y-axis aligned to the same scale as the GDC AI chart
  - X-axis showing the same start time as GDC chart, capped at NOW
- If still empty: add `console.log('scadaTraces:', scadaTraces.length)` in `renderChart()` to diagnose

### 2. Verify Sensor Tabs Visible on AI Chart Header
- In deep dive, confirm Pressure / Temperature / Vibration / Motor Current tabs appear in the GDC AI Forecast header (not on the SCADA header)
- Confirm clicking tabs switches both charts simultaneously

### 3. Full Demo Run-Through — All 6 Scenarios
Run each scenario end-to-end and note any visual/UX issues:

| Scenario | Asset | Fault | Expected horizon |
|----------|-------|-------|-----------------|
| Sand Ingress | ESP-ALPHA-2 | sand_ingress | Days |
| Thermal Runaway | GLIFT-BRAVO-1 | thermal_runaway | Hours |
| Valve Seat Washout | MUD-RIG42-1 | valve_washout | Hours |
| Motor Over-Temp | ESP-ALPHA-4 | motor_overheat | Hours |
| Gas Lock | ESP-ALPHA-1 | gas_lock | Minutes |
| Bearing Wear | GLIFT-BRAVO-3 | bearing_wear | Hours |

For each check:
- [ ] AI chart renders with correct traces (live telemetry + ML projection + SCADA threshold)
- [ ] SCADA chart renders with correct traces (historical only)
- [ ] Bridge bar shows correct advance notice values
- [ ] Intelligence Feed populates with relevant documents
- [ ] Agent consultation works and generates relevant response
- [ ] Remediation tiers show (4 options with viability badge)
- [ ] Approve & Execute → savings appear in Fleet Financials

### 4. gemma4:27b Verification
Check if the L4 node has provisioned and gemma4:27b has been pulled:
```bash
kubectl get pods -n gdc-pm -l app=ollama -o wide
kubectl exec -n gdc-pm deployment/ollama -- ollama list
```
If model is live, test via a deep dive agent consultation. Verify the response quality is noticeably better than gemma:2b (longer, more contextual, references specific field documents).

### 5. Known UX Issues to Address (if found during testing)
- **Resize handle height:** The `compareRowHeight` is persisted from sessionStorage — if a previous session left it at 88% full-screen, chart panels will be too tall. May want to cap the sessionStorage default more conservatively or add a "reset layout" button.
- **Chart area height distribution:** With 430px compare-row, the GDC chart and SCADA chart each get roughly `(430 - 46 - 36 - 36) / 2 ≈ 156px`. This may be too short. Consider making the default higher (e.g. 520px) or making the GDC chart taller than SCADA.
- **Mobile/narrow viewport:** The GDC header now has title + status + spacer + tabs + assetId + ⓘ button. On narrow screens this could overflow. Test at 1280px width.
- **Column resizer event listener leak:** `_initColResizer` adds new event listeners every time `openDeepDive` is called without removing old ones. Add a guard to check if the handle already has a listener, or use a flag.

### 6. Grafana Telemetry Tab — Final PSI Check
- Open Fleet Telemetry tab
- Confirm ESP Intake Pressure timeseries shows `psi` units (e.g. 1,400 psi, not 1.4 ksi)
- Confirm stat panels show "ESP Intake Pressure (PSI)" as the sub-label
- Confirm default time range is 2 hours

### 7. Nice-to-Have Enhancements (if time permits)
- **SCADA chart title:** Currently shows `"SCADA Monitor — No Alarms Active"` as a Plotly title inside the chart. Could remove this since the header bar already shows that status.
- **Bridge bar at 0 remaining:** When `time_to_scada_minutes = 0`, show a red "⚠ SCADA ALARM ZONE" banner instead of a zero-width bar.
- **Tooltip on sensor tabs:** Add `title="Switch both charts to [Pressure/Temperature/Vibration] view"` for UX clarity.

---

## Infrastructure Notes

**Ollama L4 provisioning:** If still pending after > 1 hour, check:
```bash
# See why autoscaler isn't provisioning
kubectl get events -n gdc-pm --sort-by='.lastTimestamp' | grep -E "FailedScaleUp|TriggeredScale" | tail -10
# If stockout is persisting in all us-central1 zones, check availability
gcloud compute accelerator-types list --filter="name=nvidia-l4" --format="table(zone)" | grep "us-"
```
If us-central1 is fully exhausted, consider temporarily switching the Ollama deployment's `nodeSelector` to use `us-east4` zones (where L4 is also available) — but this requires a new cluster or separate node pool.

---

## Files to Edit

- `gdc-pm/gke/fault-trigger-ui/index.html` — all UI changes
- `gdc-pm/gke/grafana/k8s/grafana-configmap.yaml` — Grafana-only changes (no Docker rebuild)

## Deploy Commands

```bash
# UI changes:
cd /home/brian/gdc-pm && bash gke/fault-trigger-ui/start-fault-trigger-ui.sh

# Grafana-only changes:
kubectl apply -f gdc-pm/gke/grafana/k8s/grafana-configmap.yaml
kubectl rollout restart deployment/grafana -n gdc-pm
```
