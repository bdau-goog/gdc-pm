# GDC-PM — Change Log

## Phase 14 (2026-05-15 — Session 4, Part 3)

### LLM Upgrade, Tab Reorder, Field Intelligence Enhancement, Cost Optimization

**gke/fault-trigger-ui/index.html**
- **Tab reorder:** Fleet Telemetry → Fleet Operations → Fleet Financials (Telemetry is now first and the default view on load)
- **Fleet Telemetry loads on mount:** `this.loadGrafana()` called in `mounted()` — Grafana iframe begins loading immediately when app opens
- **LLM display string:** `'gemma:2b'` fallback → `'gemma4:27b'` in both the Edge/Cloud status bar and Copilot panel header
- **Field Intelligence click-through:** All 10 routine report cards are now clickable — `@click="openFeedModal(item)"` opens the existing feed-detail modal with full document text
- **FIELD_INTEL_ITEMS enriched:** Each item now has `detail` (full verbatim report text), `ts_label` (for modal header), and `ai_relevance` (explains how GDC AI uses this document). Content is authentic: Maximo WOs, spectroscopic oil analysis with metals/viscosity/cleanliness codes, API BS&W analysis, EDR driller's notes, Pason mud reports, VFD calibration logs, directional surveys
- **Tab labels renamed:** "Operations" → "Fleet Operations"; "Historical Telemetry" → "Fleet Telemetry"

**gke/fault-trigger-ui/app.py**
- `OLLAMA_MODEL` default: `"gemma3:12b"` → `"gemma4:27b"`

**gke/fault-trigger-ui/k8s/fault-trigger-ui.yaml**
- `OLLAMA_MODEL` env var added explicitly to deployment spec: `"gemma4:27b"` — overrides code default, persists across container image updates
- `GRAFANA_URL` env var added (was previously only injected by app.py logic)
- Resource limits increased: CPU `100m/500m` → `250m/1000m`, Memory `128Mi/256Mi` → `512Mi/1Gi`

**gke/ollama/k8s/ollama.yaml** (YAML updated — not applied to live cluster; requires L4 node pool provisioning)
- GPU node target: `nvidia-a2` → `nvidia-l4` (24GB VRAM, Ada Lovelace architecture)
- Model: `gemma:2b` → `gemma4:27b` (Q4_K_M, ~15GB VRAM, fits on L4 with 7GB headroom)
- PVC storage: `10Gi` → `50Gi` (gemma4:27b model is ~15GB)
- Container resources: `4Gi/8Gi` memory → `12Gi/26Gi`; CPU `1000m` → `4000m/8000m`
- Flash attention enabled: `OLLAMA_FLASH_ATTENTION=1`; context window: `OLLAMA_NUM_CTX=8192`
- Ollama image: `0.3.12` → `latest` (required for Gemma 4 support)
- Init container: updated to pull `gemma4:27b`; improved health-check loop before pull

**gke/ollama/k8s/ollama-scheduler.yaml** (NEW — partially applied)
- Kubernetes CronJobs for automated L4 cost management
- `ollama-stand-up`: 6:00 AM UTC Mon–Fri → `kubectl scale ollama --replicas=1`
- `ollama-stand-down`: 6:00 PM UTC daily → `kubectl scale ollama --replicas=0`
- ServiceAccount + Role + RoleBinding for scoped RBAC
- **Applied:** ServiceAccount + CronJobs created ✅
- **Pending (requires project admin):** Role + RoleBinding need `container.roles.create` IAM permission. To enable:
  ```bash
  gcloud projects add-iam-policy-binding gdc-pm-v2 \
    --member="serviceAccount:dev-workstation-sa@gdc-pm-v2.iam.gserviceaccount.com" \
    --role="roles/container.developer"
  kubectl apply -f gke/ollama/k8s/ollama-scheduler.yaml
  ```
- **Cost impact:** L4 GPU ~$0.65/hr. Working hours only (45h/week) vs 24/7 = ~78% cost reduction (~$500/mo → ~$110/mo)

**scripts/ollama-stand-up.sh** (NEW)
**scripts/ollama-stand-down.sh** (NEW)
- Manual shell script equivalents of the CronJobs
- Work immediately with current IAM permissions (no RBAC required)
- Usage: `./scripts/ollama-stand-up.sh` / `./scripts/ollama-stand-down.sh`

---

## Phase 13.4 (2026-05-15 — Session 4, Part 6)

### Edge AI Detection Timeline — Tooltip Fix + Height Increase

**gke/grafana/k8s/grafana-configmap.yaml** (Panel 9 — state-timeline)
- **Tooltip mode:** `"multi"` (not set) → `"single"` — prevents the state-timeline from inheriting the shared crosshair tooltip from adjacent pressure/vibration panels. Now hovering over an asset row shows only that asset's AI state label ("AI Warning" / "AI Critical"), not a list of PSI values from other panels.
- **showValue:** `"never"` → `"auto"` — when the orange block is wide enough, Grafana renders the state label ("AI Warning") inside the block itself so the meaning is immediately obvious without needing to hover.
- **Height:** `h: 7` → `h: 10` — more vertical space for the y-axis asset labels, preventing truncation when multiple assets are simultaneously flagged.
- **rowHeight:** `0.85` → `0.9` — slightly thicker state blocks for better visual weight.

---

## Phase 13.3 (2026-05-15 — Session 4, Part 5)

### Grafana Blank Chart Fix — kiosk=tv + Legend Restore

**Root cause identified:** Changing the Grafana iframe URL from `?kiosk=tv` to `?kiosk` (to expose the Asset variable dropdown) broke Grafana's embedded timeseries chart rendering. In `kiosk=tv` mode Grafana operates in pure display mode and the React chart renderer initializes correctly. In `kiosk` mode (partial kiosk) the Grafana frontend attempts to maintain interactive state with the parent window, which conflicts with the Vue iframe integration and prevents chart rendering.

**gke/fault-trigger-ui/index.html**
- `loadGrafana()`: reverted `?kiosk` → `?kiosk=tv` — restores stable chart rendering
- Note: without the top-bar visible, the `$asset` variable dropdown is not accessible to users in the embedded view. Asset isolation is provided instead by clicking legend items (clicking a series name in the chart legend isolates that line, clicking again restores all).

**gke/grafana/k8s/grafana-configmap.yaml**
- All 6 timeseries panels: `"displayMode": "hidden"` → `"displayMode": "list"` (legends visible again)
- Legends were hidden to save space when we thought the variable dropdown provided isolation; with the dropdown gone, legends are the only selection mechanism and must be visible.

---

## Phase 13.2 (2026-05-15 — Session 4, Part 4)

### Grafana Timeseries Performance Fix — Time Bucketing

**gke/grafana/k8s/grafana-configmap.yaml**
- **Root cause:** All 6 timeseries panels used `GROUP BY event_time, asset_id` — since each telemetry reading has a unique timestamp, this returned every individual raw row. At 12 readings/min × 12h × 14 assets = **120,960 raw rows** per full-fleet query, causing Grafana to time out before rendering.
- **Fix (attempt 1 — partial):** Replaced with `$__timeGroupAlias(event_time,'5m')`. Queries became fast (1.06s) and returned correct data (confirmed in Grafana Inspect tool), but timeseries charts still rendered blank. Root cause: `$__timeGroupAlias` in Grafana 10.4.2 returns a float Unix epoch, which the timeseries panel renderer cannot graph.
- **Fix (attempt 2 — final):** Replaced with `to_timestamp(floor(extract(epoch from event_time)/300)*300) AS time`. This explicitly converts the 5-minute epoch bucket back to a proper `TIMESTAMPTZ` column named "time", which the Grafana timeseries panel can render correctly. **60× data reduction maintained.**
- **State Timeline** uses 1-minute buckets: `to_timestamp(floor(extract(epoch from event_time)/60)*60)` with `MAX()` to preserve discrete fault detection events.
- **Result:** All 6 timeseries panels render correctly and fast. Data quality unchanged: `AVG()` over 5-minute buckets is equivalent to raw values for trend visualization.

---

## Phase 13.1 (2026-05-15 — Session 4, Part 2)

### Grafana Dashboard Fix-Pass + UI Kiosk Mode Fix

**gke/grafana/k8s/grafana-configmap.yaml**
- **Template variable fixed:** Added `definition`, `sort`, `regex`, `options` fields; `allValue` changed from `".*"` regex to `"All"` literal. All panel SQL updated to `('All' = '$asset' OR asset_id = '$asset')` — reliable string comparison, no regex
- **Asset dropdown now visible:** Changed iframe URL in `index.html` from `?kiosk=tv` (hides all controls) to `?kiosk` (hides nav bar only, exposes variable dropdowns and time picker)
- **Legends removed from all timeseries panels:** Changed `displayMode` from `"list"` to `"hidden"` on all 6 timeseries panels. Tooltips set to `"multi"` — hover shows all series values. No vertical space consumed by legend boxes
- **SCADA Hard-Threshold Breach Log:** Alarm log SQL completely rewritten to filter on actual sensor physics (psi < 800, motor_amps < 45, temp_f > 230, vibration > 10, etc.) rather than ML `predicted_label`. This log is empty in normal/early-degradation state, which is the core demo narrative
- **Table title:** Renamed to `"🔴 SCADA Hard-Threshold Breach Log"` with `alarm_type` column showing exactly which SCADA limit was crossed
- **Fleet Status KPIs:** `SCADA Hard-Limit Alarms (1h)` and `Time Since Last Hard Alarm` stats now also use hard-threshold SQL (was `predicted_label IN (...)`)
- **Edge AI Detection Timeline:** Renamed from "Fleet Health State Timeline" to `"⚡ GDC Edge AI Detection Timeline"`. Description explains this is the AI layer that detects precursors that don't appear in the SCADA breach log
- **Row section labels:** Added `"⚡ Edge AI vs SCADA"` row separator before the AI timeline + breach log, making the contrast section explicit
- **maxDataPoints: 200** added to all 8 data panels — limits query result size and reduces Grafana rendering load
- **Gas Lift stat:** Swapped `Avg Mud Pump` stat for `Avg Gas Lift Discharge P` in the fleet status row for better coverage

**gke/fault-trigger-ui/index.html**
- `?kiosk=tv` → `?kiosk` in `loadGrafana()` function — exposes the Asset variable dropdown when viewing the Historical Telemetry tab

---

## Phase 13 (2026-05-15 — Session 4)

### Grafana SCADA Dashboard Redesign — Realistic Monitoring View

**gke/grafana/k8s/grafana-configmap.yaml**
- Complete dashboard redesign to reflect how a real O&G operator would actually use a SCADA monitoring tool
- **Narrative purpose:** A well-designed, readable, functional monitoring dashboard is still fundamentally reactive — it cannot detect multi-variable fault precursors before SCADA alarm thresholds are breached
- **Template variable** (`$asset` dropdown) added — operator can select any individual asset or "All". Eliminates spaghetti charts; each timeseries shows clean per-asset lines
- **Time range extended** from `now-30m` → `now-12h` (one operator shift), making slow-moving degradation trends (e.g., −2 PSI/hr valve washout slope) actually visible on the chart — yet still not enough for a human to act on without AI assistance
- **Physics-first layout** — removed ML confidence / anomaly rate from top of page; replaced with operational sections: Fleet Status → Pressure → Vibration & Temperature → Electrical & Mechanical → Alarm Log
- **Row separators** (`Fleet Status`, `Pressure`, `Vibration & Temperature`, `Electrical & Mechanical`, `Alarm Log`) for clean navigation
- **SCADA annotation overlay** added — red vertical markers appear on all charts when critical alarms (gas_lock, valve_failure, dampener) fire, showing exactly when the reactive system "woke up"
- **Panel descriptions** rewritten to narrate the gap: each chart description explains what a SCADA alarm threshold is, why the early precursor falls below it, and why multi-variable correlation is needed
- **Stat row** (6 KPIs): Active Assets, SCADA Alarms (1h), Unacknowledged Alarms, Time Since Last Alarm, Avg ESP Pressure, Avg Mud Pump Pressure
- **Timeseries panels**: ESP Intake Pressure, Gas Lift Discharge Pressure, Vibration (all assets, filtered), Temperature (all assets, filtered), Motor Current (ESP), Stroke Rate (Mud Pump)
- **Bottom section**: Fleet Health State Timeline + Alarm Log table (shift-scoped, 60 events)
- Refresh cadence changed from `5s` → `10s` (less flicker, more realistic for an operator display)

---

## Phase 12 (2026-05-13 — Session 3)

### Self-Justifying Demo + UI Refinement

**app.py**
- Added `FINANCIAL_JUSTIFICATIONS` dict: itemized cost breakdowns for all 11 fault types with OEM pricing, labor rates, API references
- Added `/api/financial-justification/{fault_type}` endpoint (placed after `hitl-approve`, before `index`)
- Bug fixed: endpoint was initially placed before `app = FastAPI(...)` causing `NameError` on startup; corrected to after `app` definition

**index.html**
- Added `--g-blue`, `--g-green`, `--g-yellow`, `--g-red` CSS vars (muted Google Material dark-mode palette)
- Outcome card border/title/savings: neon green → muted `--g-green` (#81c995)
- `ⓘ Cost Basis` button added to HITL remediation panel header (fires `fetchJustification()`)
- Financial Justification Modal: 3-col summary + itemized unmitigated/intervention breakdowns + methodology + references
- Vue data: added `justifyModalOpen`, `justifyData`; method `fetchJustification()`

---

## Phase 11.2 (2026-05-13 — Session 2)

### Dashboard 3-Column Layout + Field Intelligence Panel

**index.html**
- Dashboard layout: 2-col → 3-col (`fleet 360px` | `field-intel 310px` | `horizon flex:1`)
- Fleet cards: larger fonts (0.9rem site name, 0.68rem asset chips), 2×2 KPI mini-grid (Production, Uptime, GOR/Lift Eff/ROP, Wellhead P/WOB)
- Field Intelligence Panel: 10 pre-seeded routine O&G reports (Well Tests, Maximo PM, Oil Analysis, Shift Handovers, Directional Surveys) with Report/Routine/Lab/Survey badges
- "Open Asset Dashboard (no fault)" button added to asset quick-select
- Copilot panel: chat log narrowed to 250px; HITL expanded to flex:1 with 4-tier remediation grid (Early/Urgent/Critical/Post-PNR from `/api/resolution-actions`)
- Tier selection: click to select, green highlight; "ACTIVE" badge on current tier
- ✏️ Craft Fault button in Deep Dive header → modal with fault type picker + duration input
- Grafana iframe: added `&refresh=5s` parameter
- Vue data: `remediationTiers`, `selectedTierKey`, `craftModalOpen`, `craftFaultType`, `craftDuration`, `fieldIntelItems`

---

## Phase 11.1 (prior session)

### Bug Fixes
- `requests` library added to requirements.txt (SSE stream was silently failing)
- Ollama model: `OLLAMA_MODEL=gemma:2b` env var patched (only gemma:2b is loaded)
- Grafana URL fixed: `/d/telemetry` → `/d/gdc-pm-main`
- Gemma prompt: `SENSOR INTELLIGENCE` from `GEMMA_FINDINGS` injected into both initial and follow-up prompts
- ML projection: removed 3-day display cap; now ≤500-point downsampling

### New Scenarios
- Motor Over-Temp — ESP Emergency (ESP-ALPHA-4, motor_overheat, Hours, $200k)
- Gas Lock — SCADA Autonomous Control (ESP-ALPHA-1, gas_lock, Minutes, $150k)
- Journal Bearing Wear — Predictive Scheduling (GLIFT-BRAVO-3, bearing_wear, Hours, $85k)

### Dashboard Redesign
- KPI Strip removed (was duplicating fleet card data)
- Fleet cards on LEFT (300px), Predictive Horizon flex:1 RIGHT
- Deep Dive: Intelligence Feed takes primary vertical space; HITL card 420px; Copilot header shows actual LLM model name
