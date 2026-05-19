# GDC-PM — Session 6 Handoff

**Date:** 2026-05-19  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2` | Cluster: `gdc-edge-simulation` | Namespace: `gdc-pm`  
**Current image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Git head:** `9be43bd` (master)

---

## What Was Done in Session 5 (Phase 15)

### Phase 15 — Dual-Reality UI Redesign (complete, deployed)

**Problem:** The old 3-column "Fleet Operations" tab was a wall of text — 10 dense O&G document cards + 6 verbose demo scenario cards overwhelmed both business and technical audiences.

**Solution:** Complete redesign of the Fleet Operations tab inspired by the `gdc-das-life` DAS demo's spatial, interactive approach.

**What's live:**
- **KPI Banner** (top): Assets Online | ⚡ AI Detections | SCADA Alarms (always 0) | Savings Protected ($)
- **2D Spatial Fleet Map** (main body, left): 3 site zones (Pad Alpha, Pad Bravo, Rig 42) with interactive circular asset nodes. Click a node → context menu with fault-specific options + ⓘ scenario/cost tooltip. Active faults pulse orange.
- **Colored Metric Grid** (per site zone): 5 metric cards each, threshold-colored green/orange/red
- **Resizable Splitter**: Drag between fleet map and intel stream to redistribute screen space
- **Terse Field Intelligence Stream** (right, resizable): 10 document rows at 34px each — icon | headline | badge | time. AI alerts float to top. Click to expand full document modal.
- **Deep Dive — SCADA vs AI Banner**: Two-panel contrast: "SCADA: ✓ NORMAL" (green) vs "GDC Edge AI: ⚡ ANOMALY DETECTED" (orange, pulsing). Makes the core narrative visually explicit.

### Phase 15 Bugfix — Vue mount failure (complete, deployed)

The initial Phase 15 deployment broke Vue entirely. Root cause: `replace_in_file` only replaced through the opening of the old `fleet-section` div, leaving the old Field Intelligence and Predictive Horizon columns + two orphaned `</div>` closing tags dangling between the new dashboard and deep dive views. Browser used orphaned divs to prematurely close `#tab-operations` and `.app-body`, pushing all modals and tabs outside `#app`. Fixed by removing 200 lines of orphaned old HTML.

---

## Current Cluster State

```
gdc-edge-simulation / gdc-pm namespace
────────────────────────────────────────
fault-trigger-ui       1/1 Running   ← Primary demo UI + FastAPI backend
telemetry-simulator    1/1 Running   ← Generates 12 readings/min
event-processor        1/1 Running   ← RabbitMQ → inference → AlloyDB
alloydb-omni           1/1 Running   ← PostgreSQL edge DB
gdc-pm-rabbitmq        1/1 Running   ← AMQP message broker
grafana                1/1 Running   ← SCADA dashboard (http://136.115.220.48)
ollama                 1/1 Running   ← gemma:2b local LLM (actual loaded model)
inference-api          1/1 Running   ← Legacy BQML inference (not used by current UI)
```

**IMPORTANT:** The live Ollama deployment runs `gemma:2b`. The YAML is updated for `gemma4:27b` on L4 but NOT applied (requires L4 node provisioning and project-admin IAM grant).

---

## Outstanding Development Items (To-Do)

### High Priority

**4. Live Intelligence Generator** *(backend + UI)*
- **What:** A FastAPI background task (APScheduler or asyncio) that runs every 2-5 min, generates realistic O&G field documents using Ollama, stores in AlloyDB, and surfaces in the intel stream
- **Why:** Currently the 10 intel stream items are hardcoded. Dynamic documents that respond to fault context would make the demo much more compelling — presenter can point out "the AI just generated a new shift note that correlates with the fault we just injected"
- **Implementation plan:**
  1. New AlloyDB table: `field_intel` (id, asset_id, fault_context, doc_type, headline, detail, ai_relevance, created_at)
  2. New `app.py` background task: calls Ollama with structured prompt, biased toward fault type when active
  3. New `/api/field-intelligence` endpoint: returns newest-first, optionally filtered by asset/fault context
  4. UI: poll `/api/field-intelligence` every 60s, prepend new rows with `.act-new` flash animation (CSS already in place)
- **Prompt template example:**
  ```
  Generate a realistic O&G {doc_type} for {asset_id} ({asset_class}).
  Context: {fault_type} fault detected. Current sensors: {sensor_summary}.
  Format: One-line headline + 150-word body in authentic field language.
  ```

**5. Route generated intelligence to model** *(dependent on #4)*
- The intelligence generator would use the existing Ollama `httpx` client in `app.py`
- When a fault is active, pass fault_type + sensor values as context to bias the generation
- Documents generated during a fault should show up in the Deep Dive "Live Intelligence Feed" as new evidence nodes, creating the "multi-modal fusion" narrative in real-time

### Medium Priority

**6. gemma:2b display string**
- Currently shows `gemma:2b` in the Edge status bar (accurate — that's what's loaded)
- **Option A:** Leave as-is (honest) until L4/gemma4 upgrade is applied
- **Option B:** Add `OLLAMA_DISPLAY_MODEL` env var in `app.py` to separate display from actual calls:
  ```python
  OLLAMA_DISPLAY_MODEL = os.getenv("OLLAMA_DISPLAY_MODEL", OLLAMA_MODEL)
  ```
  Then patch: `kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_DISPLAY_MODEL="gemma4:27b"`
- Recommend Option B once decided

**7. Gemma 4 / L4 GPU Upgrade** *(infrastructure, requires project admin)*
- YAML files are ready (`gke/ollama/k8s/ollama.yaml` updated to target L4, gemma4:27b, 50Gi)
- Pending steps:
  1. Project admin grants: `gcloud projects add-iam-policy-binding gdc-pm-v2 --member="serviceAccount:dev-workstation-sa@gdc-pm-v2.iam.gserviceaccount.com" --role="roles/container.developer"`
  2. Provision L4 GPU node pool in GKE cluster
  3. Apply RBAC: `kubectl apply -f gke/ollama/k8s/ollama-scheduler.yaml`
  4. Apply updated Ollama deployment: `kubectl apply -f gke/ollama/k8s/ollama.yaml`
  5. First startup will pull gemma4:27b (~15GB, 5-15 min)
  6. Update display: `kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_MODEL=gemma4:27b`

**8. Asset Hover Metrics** *(UI enhancement)*
- When context menu opens for an active asset, show a mini sensor reading grid
- Use `degStatus` from the active degradation map to display current PSI/Temp/Vib values
- Gives the presenter immediate context without clicking into deep dive

**9. Grafana Time Range Extension**
- Current: `now-2h` default
- Goal: Extend to `now-4h` or `now-6h` to show slower fault development curves
- All 6 timeseries panels use `date_trunc('minute', event_time)` — should stay fast
- Test before applying: inspect query times in Grafana

**10. Fleet Telemetry — Reduce Spaghetti Lines**
- Vibration and Temperature panels still show all 14 assets simultaneously
- Options:
  - Pre-filter to show only the 4-5 highest-activity assets by default
  - Split into separate sub-panels by asset class (ESP-only, Gas Lift-only, Rig-only)
  - Since `?kiosk=tv` hides the `$asset` variable dropdown, legend-click is the only isolation mechanism

### Low Priority / Future

**11. Field Intelligence Dynamic Integration from AlloyDB**
- Currently hardcoded in `FIELD_INTEL_ITEMS` in `index.html`
- Future: migrate to `/api/field-intelligence` endpoint backed by AlloyDB
- Enables fault-context-aware document filtering

**12. Demo Flow Polish**
- Consider adding a "Demo Cheat Sheet" overlay for presenters (like `gdc-das-life` had)
- Consider whether the `⚡ GDC Edge AI Detection Timeline` in Grafana needs annotation arrows
- Suggested demo script: start on Fleet Telemetry (SCADA "all clear"), switch to Fleet Operations, click ESP-A2 → Sand Ingress, watch AI detect while SCADA stays silent, consult agent, approve remediation

---

## Constraints — Do Not Violate

- **Never apply `terraform/gke.tf`** — destroys the live cluster
- **Never change iframe to `?kiosk`** — must stay `?kiosk=tv` for chart rendering stability  
- **Only edit:** `gke/fault-trigger-ui/app.py`, `gke/fault-trigger-ui/index.html`, `gke/grafana/k8s/grafana-configmap.yaml`
- Gemma keepalive thread is in `app.py` — prevents cold starts during demos
- XGBoost health models (`*.ubj`) are validated — do not retrain without specific reason

---

## Rebuild & Deploy Commands

```bash
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

---

## Key Lesson Learned (Session 5)

**`replace_in_file` partial replacement danger:** When replacing a large multi-div HTML block, the tool only replaces the exact matched string. If the SEARCH pattern ends mid-structure (e.g., at the opening tag of a div whose content spans hundreds of lines), the remaining content (closing divs, sibling divs) is left orphaned in the file. This caused the Vue mount failure. Always verify div counts before/after major HTML replacements, and use `grep -n` to audit structural divs.
