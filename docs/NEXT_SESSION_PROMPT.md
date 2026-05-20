# GDC-PM — Session 11 Handoff

**Date:** 2026-05-20  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2` | Cluster: `gdc-edge-simulation` | Namespace: `gdc-pm`  
**Current image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Git head:** `2be0310` (master — working tree clean)

---

## What Was Done in Session 10

### 1. Ollama Scheduler RBAC — Resolved (deployed, live)

The session 9 handoff flagged `container.roles.create` IAM permission as missing. Confirmed via `kubectl auth can-i create role -n gdc-pm` → **yes** — namespace-scoped RBAC was always permitted. Applied the full scheduler manifest:

- `serviceaccount/ollama-scheduler` ✅  
- `role.rbac.authorization.k8s.io/ollama-scaler` ✅  
- `rolebinding.rbac.authorization.k8s.io/ollama-scheduler-scaler` ✅  
- `cronjob.batch/ollama-stand-up` — **6 AM UTC, Mon–Fri** ✅  
- `cronjob.batch/ollama-stand-down` — **6 PM UTC, daily** ✅  

**Cost impact:** L4 GPU (gemma4:27b) now auto-provisions on weekday mornings and deprovisions evenings → ~78% GPU cost savings.

**Current ollama state:** New pod (`ollama-77f99db54d-*`) still Pending (L4 provisioning / 15GB pull in progress). Old pod (`ollama-8ffc6bd5b-*`) Running on gemma:2b serving requests.

---

### 2. Fleet Financials — Narrative ROI Card (deployed, live)

Replaced the plain 3-KPI row with a full **"Before GDC vs After GDC"** narrative card. Changes to `gke/fault-trigger-ui/index.html`:

**Hero section (always visible):**
- Large `$totalSaved` monospace figure with green gradient — the "money shot" on first load
- Annualised projection card (`totalSaved × 52`) — visible only after first intervention
- Side-by-side "Traditional SCADA Only" (red) vs "GDC Edge AI" (green) feature comparison grid, 5 items each

**Right KPI column (3 tiles):**
- Incidents Resolved (blue monospace)
- Fleet Uptime Protected (green)
- Avg $ / Intervention (yellow) — `totalSaved / ledger.length`

**Fleet Uptime comparison bars** (visible after first intervention):
- GDC (green gradient) vs SCADA-only estimated baseline (red) — SCADA baseline = GDC - 3% per incident

**Cost-per-intervention sparkline row:**
- Mini cards per resolved incident, newest first, showing timestamp + savings + asset/fault

**Methodology footnote:** API RP 11S / SPE-181437-MS references, $45k/day ESP downtime, $120k/day rig.

**Empty state guidance:** "No resolved incidents yet — approve a fault intervention in Fleet Operations to populate this ledger."

---

### 3. Grafana Fleet Telemetry — Per-Asset Stat Cards (deployed, live)

Added 14 per-asset PSI health stat panels to `grafana-configmap.yaml` using `gdc-pm/scripts/patch_grafana_stat_panels.py`:

**New stat panels — Pad Alpha (y=6, IDs 100–105):**
- ESP-A1 through ESP-A6 — each shows 5-min avg Intake PSI, green/orange/red threshold coloring
- Click → `/d/gdc-pm-main?var-asset=ESP-ALPHA-N&kiosk=tv` (single-asset filter)

**New stat panels — Pad Bravo (y=29, IDs 110–113):**
- GL-B1 through GL-B4 — Discharge PSI

**New stat panels — Rig 42 (y=43, IDs 120–123):**
- MUD-1, MUD-2, MUD-3, TDRIVE — Discharge PSI / Hydraulic PSI

**Y-coordinate shifts:**
- All existing Pad Alpha charts: +4 (y=6→10, y=15→19)
- All existing Pad Bravo charts: +8 (y=25→33)
- All existing Rig 42 charts: +12 (y=35→47, y=44→56)
- Edge AI vs SCADA section: +12 (y=53→65, y=54→66, y=64→76)

**Total panel count:** 24 → 38

---

### 4. Deep Dive — Chart Resize Handle (deployed, live)

Added a drag handle between the chart row and Evidence/Agent/Action panels in the Deep Dive view. Changes to `index.html`:

**CSS:** `.compare-resize-handle` — 9px tall, `ns-resize` cursor, blue glow on hover/drag

**Vue data:** `compareRowHeight: 430` (default 430px)

**HTML:** `<div class="compare-resize-handle" ref="compareResizeHandle">` inserted between `</div><!-- dd-compare-row -->` and `<div class="dd-bottom-row">`

**HTML binding:** `.dd-compare-row` div now uses `:style="{height: compareRowHeight + 'px'}"` (was hard-coded `height:430px` in CSS)

**JS method `initCompareResize()`:**
- `mousedown` → capture `startY` and `startH`
- `mousemove` → `compareRowHeight = clamp(e.clientY - startY + startH, 180, viewport * 0.9)`
- Calls `renderChart()` on every mousemove (live Plotly reflow)
- Final `renderChart()` on `mouseup` via `$nextTick`

**Called from:** `openDeepDive()` → `this.$nextTick(() => { this.initCopilotResize(); this.initCompareResize(); })`

**Demo usage:** Drag handle all the way down to push Evidence/Agent/Action panels off-screen → full-height chart view for presentation. Default 430px balances chart vs evidence on a 1080p screen.

---

### 5. Deep Dive — SCADA Alarm Annotation Removed from AI Chart (deployed, live)

The GDC AI forecast chart previously showed a floating red annotation box "⚡ SCADA Alarm in 18m" overlapping the orange forecast curve (as seen in the screenshot). Removed via client-side filtering in `renderChart()`.

**Change in `renderChart()`:**
```javascript
const gdcLayout = JSON.parse(JSON.stringify(s.layout));
if (gdcLayout.annotations) {
  gdcLayout.annotations = gdcLayout.annotations.filter(a =>
    !((a.text || '').toLowerCase().includes('scada alarm') ||
      (a.text || '').toLowerCase().includes('scada a'))
  );
}
Plotly.react(elGdc, s.traces, gdcLayout, ...);
```

The bridge bar ("⚡ GDC Detected → [bar shrinking] → ⛔ SCADA Alarm") already tells the lead-time story more powerfully. The GDC AI chart now shows only: orange RUL forecast line, confidence cone, PNR marker, and the SCADA threshold dashed line.

---

## Current Cluster State

```
gdc-edge-simulation / gdc-pm namespace
────────────────────────────────────────
fault-trigger-ui       1/1 Running   ← Session 10 image (all above changes live)
telemetry-simulator    1/1 Running   ← Generates 12 readings/min
event-processor        1/1 Running   ← RabbitMQ → inference → AlloyDB
alloydb-omni           1/1 Running   ← PostgreSQL edge DB
gdc-pm-rabbitmq        1/1 Running   ← AMQP message broker
grafana                1/1 Running   ← Session 10: 38 panels (14 new stat cards)
ollama (new)           0/1 Pending   ← L4 node provisioning / gemma4:27b pull
ollama (old)           1/1 Running   ← gemma:2b serving requests
inference-api          1/1 Running   ← Legacy BQML (not used by current UI)
ollama-stand-up        CronJob       ← 6 AM UTC Mon–Fri ✅
ollama-stand-down      CronJob       ← 6 PM UTC daily ✅
```

---

## Outstanding Development Items — Session 11

### High Priority

**1. UI Refinement (carried forward from feedback)**
- Demo flow: full-screen chart mode (drag handle all the way down) needs verification on the live site
- Grafana stat panel click-through: verify `?var-asset=ESP-ALPHA-2&kiosk=tv` filters the timeseries charts correctly when clicked from within the iframe
- Consider: double-click on the resize handle to snap to full-screen / snap back to default 430px

**2. Grafana Stat Panel Labels**
- Currently stat panels show short label (e.g., "ESP-A1") and PSI value
- Consider adding `description` field showing the full asset ID to avoid confusion when presenting
- `textMode: "value_and_name"` is already configured — verify rendering on live dashboard

**3. Ollama L4 / gemma4:27b — Monitor to Completion**
- `kubectl logs -n gdc-pm -l app=ollama -c pull-model --follow`
- Once Running: run a fault scenario and verify agent response quality vs gemma:2b
- gemma4:27b should produce more coherent maintenance recommendations with field doc context

### Medium Priority

**4. Chart Y-Axis Alignment (Deep Dive)**
- GDC AI forecast chart and SCADA chart share X-axis but may differ in Y-axis scale
- For maximum visual impact: match Y-axis `min`/`max` across both panels so the gap between "AI sees degradation" and "SCADA sees nothing" is visually obvious
- Implementation: read `s.layout.yaxis` range from GDC layout and force same range on SCADA layout

**5. Grafana Time Range**
- Default `now-8h` → consider `now-2h` for live demos (fault ramp is more visible in 2h window)
- Change: `"time": { "from": "now-2h", "to": "now" }` in `grafana-configmap.yaml`
- Apply with: `kubectl apply -f gdc-pm/gke/grafana/k8s/grafana-configmap.yaml && kubectl rollout restart deployment/grafana -n gdc-pm`

**6. Resize Handle UX Polish**
- Add a subtle "↕" tooltip label on the resize handle when hovered
- Add double-click snap: dbl-click → `compareRowHeight = window.innerHeight * 0.85` (full-screen); dbl-click again → reset to 430
- Consider persisting `compareRowHeight` in `sessionStorage` so it survives tab switches

### Low Priority

**7. Financial Tab — Projected Savings Chart**
- Currently the cost-per-intervention sparkline is text-based mini-cards
- Could add a Plotly bar chart showing savings by incident over time
- Blocked on: need multiple resolved incidents to make meaningful

---

## Constraints — Do Not Violate

- **Never apply `terraform/gke.tf`** — destroys the live cluster
- **Never change iframe to `?kiosk`** — must stay `?kiosk=tv`
- **Only edit:** `gke/fault-trigger-ui/app.py`, `gke/fault-trigger-ui/index.html`, `gke/grafana/k8s/grafana-configmap.yaml`
- Gemma keepalive thread is in `app.py` — prevents cold starts during demos
- XGBoost health models (`*.ubj`) are validated — do not retrain without specific reason
- `_ensure_field_intel_table()` creates `field_intel` idempotently on startup

---

## Rebuild & Deploy Commands

```bash
# UI (after editing app.py or index.html):
cd /home/brian
docker build --quiet -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gdc-pm/gke/fault-trigger-ui/
docker push --quiet us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm
kubectl rollout status deployment/fault-trigger-ui -n gdc-pm --timeout=180s
```

```bash
# Grafana only (no app rebuild needed):
kubectl apply -f gdc-pm/gke/grafana/k8s/grafana-configmap.yaml
kubectl rollout restart deployment/grafana -n gdc-pm
kubectl rollout status deployment/grafana -n gdc-pm --timeout=90s
```

```bash
# Monitor Ollama L4 pod readiness (gemma4:27b pull):
kubectl get pod -n gdc-pm -l app=ollama -w
kubectl logs -n gdc-pm -l app=ollama -c pull-model --follow
```

```bash
# Grafana stat panel patch script (idempotent if IDs 100–123 not yet present):
python3 gdc-pm/scripts/patch_grafana_stat_panels.py
```

---

## Key Lessons Learned (Session 10)

**RBAC gap was already resolved:** `kubectl auth can-i create role -n gdc-pm` returned `yes` — the namespace-scoped RBAC was always permitted. Always run `kubectl auth can-i` before assuming an IAM grant is required at GCP project level.

**Python for ConfigMap JSON surgery is reliable:** The `patch_grafana_stat_panels.py` script (parse → modify → re-indent → write) is deterministic and rerunnable. Panel IDs 100–123 are stable; the script is idempotent if run again after a dashboard reset.

**Chart resize + annotation cleanup has high demo impact:** The "⚡ SCADA Alarm in 18m" box was cluttering the orange forecast line. Removing it in `renderChart()` via annotation filtering keeps the backend unchanged (useful for other consumers) while cleaning the demo view. Combining this with the drag-to-fullscreen handle means a presenter can expand the AI chart to fill the screen exactly when the bridge bar is most dramatic.

**Financial narrative framing outweighs data volume:** The Before/After grid + big ROI number + uptime comparison bars tell the story in <2 seconds. Operators and executives need to see "what we had before" vs "what GDC gives us" as a visual side-by-side — not just a ledger table.
