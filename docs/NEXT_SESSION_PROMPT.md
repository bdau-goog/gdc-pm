# GDC-PM — Session 7 Handoff

**Date:** 2026-05-19  
**Live URL:** http://35.188.3.97  
**Project:** `gdc-pm-v2` | Cluster: `gdc-edge-simulation` | Namespace: `gdc-pm`  
**Current image:** `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`  
**Git head:** `9be43bd` (master — no commits made this session, all changes are live in the running container)

---

## What Was Done in Session 6 (Phases 16 + UI Refinements)

### Phase 16 — Live Intelligence Generator (complete, deployed)

**What was built:**
- **`field_intel` AlloyDB table** — added to `init-schema.yaml` with live migration in `app.py` (`_ensure_field_intel_table()`). Schema: `id, created_at, asset_id, asset_class, fault_context, doc_type, headline, detail, ai_relevance, icon, lbl, lbl_type`
- **`_intel_generator` background thread** — runs every 2–5 min; picks an asset (80% chance of active-fault asset), assembles a prompt with live sensor context from `active_degrades[asset_id]["current_sensors"]`, calls Ollama, inserts result into `field_intel`, prunes to 100 most recent rows
- **`/api/field-intelligence` endpoint** — returns newest-first documents with human-readable timestamps, `gi_` prefixed IDs (avoid collision with hardcoded `fi1..fi10`), `is_anomaly` flag
- **`current_sensors` tracking in `_run_degrade_thread`** — ramp loop updates `active_degrades[asset_id]["current_sensors"] = {psi, temp, vib}` every 5s so intel generator has live degraded sensor values for contextual prompts
- **`OLLAMA_DISPLAY_MODEL`** — separate display label from actual model. UI shows `OLLAMA_DISPLAY_MODEL`; calls still use `OLLAMA_MODEL`. Override: `kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_DISPLAY_MODEL="gemma4:27b"`
- **`fetchFieldIntel()` polling in UI** — polls `/api/field-intelligence?limit=20` every 60s (first call at 90s after startup to let generator produce first doc). Deduplicates by `id`, prepends new items to `fieldIntelItems`, triggers `.act-new` CSS flash animation for 3.5s

### UI Redesign — Deep Dive Panel (complete, deployed)

**Changes from user feedback:**
1. **Fault injection panel removed from deep dive** — replaced with minimal status strip: `⚡ [FaultName] · 28% degraded [progress bar] ↺ Reset`. Injection still available via Fleet map context menu and ✏️ Craft Fault header button
2. **Chart physics fixed (root cause)** — replaced two-segment exponential with single continuous exponential `f(t) = y_start + (y_failure - y_start) × (exp(k × t/ttf_total_min) - 1) / (exp(k) - 1)`. The old approach forced the curve to pivot at `rul_minutes` (SCADA detection time), creating an unphysical kink. Both `_build_sensor()` (JSON endpoint) and `plot_forecast()` (Plotly iframe) updated
3. **"How to use" card removed** — the "How to use this panel" info box below the Consult button was removed for cleanliness
4. **SCADA vs AI banner enlarged** — padding increased to `14px 16px`, border `2px`, status text `1.2rem font-weight:800`. Much more prominent
5. **AI Lead Time banner added** — blue banner between SCADA/AI cards and sensor grid: `⏱  19 min — GDC AI leads SCADA by this margin · SCADA: ✓ NORMAL · AI: ⚡ Fault detected`
6. **Asset node shapes** — distinct per type: ESP = circle (50%), Gas Lift = organic oval (52% 48% 48% 52% / 60% 60% 40% 40%), Mud Pump = squircle (28%), Top Drive = four-lobe blob (50% 30% 50% 30% / 30% 50% 30% 50%). Legend updated. Rig 42 nodes split into `mud-node` / `topdrive-node` classes using `ASSET_META[assetId].aclass`
7. **Mini sensor grid in context menu** — when fault is active, shows PSI / Temp °F / Vib mm/s in orange-tinted 3-column grid sourced from `activeDegradesMap[assetId].current_sensors`
8. **Cost removed from fault-selector** — `$XXX,XXX` replacement cost badge removed from fault injection rows in context menu. Still accessible in ⓘ tooltip
9. **Copilot default height** — raised from 280px to 360px; drag handle still available

---

## Current Cluster State

```
gdc-edge-simulation / gdc-pm namespace
────────────────────────────────────────
fault-trigger-ui       1/1 Running   ← Primary demo UI + FastAPI backend
telemetry-simulator    1/1 Running   ← Generates 12 readings/min
event-processor        1/1 Running   ← RabbitMQ → inference → AlloyDB
alloydb-omni           1/1 Running   ← PostgreSQL edge DB (now has field_intel table)
gdc-pm-rabbitmq        1/1 Running   ← AMQP message broker
grafana                1/1 Running   ← SCADA dashboard (http://136.115.220.48)
ollama                 1/1 Running   ← gemma:2b local LLM (actual loaded model)
inference-api          1/1 Running   ← Legacy BQML inference (not used by current UI)
```

**IMPORTANT:** The live Ollama deployment runs `gemma:2b`. The YAML is updated for `gemma4:27b` on L4 but NOT applied (requires L4 node provisioning and project-admin IAM grant). `OLLAMA_DISPLAY_MODEL` is currently unset (defaults to same as `OLLAMA_MODEL = gemma4:27b`). To make it honest until upgrade: `kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_MODEL="gemma:2b"` — but this may break prompts optimized for gemma4 formatting.

---

## Outstanding Development Items (To-Do)

### High Priority

**5. Route generated intelligence to model** *(dependent on Phase 16, now complete)*
- The intel generator already uses Ollama + live sensor context — Phase 16 is done
- Remaining: when a fault is active, generated docs should appear in the Deep Dive **"Live Intelligence Feed"** panel as new evidence nodes (currently only pre-canned `INTELLIGENCE_FEED` docs appear there)
- Implementation: modify `get_intelligence_feed()` in `app.py` to also query `field_intel` for the current `fault_context`, merge with the pre-canned `INTELLIGENCE_FEED` items, return combined list sorted newest-first
- The UI `fetchIntelligenceFeed()` already calls `/api/intelligence-feed/{asset_id}?fault_type=X` — backend just needs to include generated docs in the response

**6. gemma:2b display string**
- `OLLAMA_DISPLAY_MODEL` env var is now supported in `app.py` and `get_mlops_status()`
- Option A: Leave as-is (displays `gemma4:27b` which is aspirational but inaccurate)
- Option B: `kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_DISPLAY_MODEL="gemma:2b"` (honest)
- Option C: Wait until L4/gemma4 upgrade is applied

**7. Gemma 4 / L4 GPU Upgrade** *(infrastructure, requires project admin)*
- YAML files are ready (`gke/ollama/k8s/ollama.yaml` updated to target L4, gemma4:27b, 50Gi)
- Pending steps:
  1. Project admin grants: `gcloud projects add-iam-policy-binding gdc-pm-v2 --member="serviceAccount:dev-workstation-sa@gdc-pm-v2.iam.gserviceaccount.com" --role="roles/container.developer"`
  2. Provision L4 GPU node pool in GKE cluster
  3. Apply RBAC: `kubectl apply -f gke/ollama/k8s/ollama-scheduler.yaml`
  4. Apply updated Ollama deployment: `kubectl apply -f gke/ollama/k8s/ollama.yaml`
  5. First startup will pull gemma4:27b (~15GB, 5-15 min)
  6. Update display: `kubectl set env deployment/fault-trigger-ui -n gdc-pm OLLAMA_MODEL=gemma4:27b`

### Medium Priority

**8. Grafana Time Range Extension**
- Current: `now-2h` default
- Goal: Extend to `now-6h` or `now-8h` to show slower fault development curves
- File: `gke/grafana/k8s/grafana-configmap.yaml` — change `"from": "now-2h"` in the `time` object
- Apply: `kubectl apply -f gdc-pm/gke/grafana/k8s/grafana-configmap.yaml && kubectl rollout restart deployment/grafana -n gdc-pm`
- Test first: all 6 timeseries panels use `date_trunc('minute', event_time)` — should stay fast

**9. Fleet Telemetry — Reduce Spaghetti Lines**
- Vibration and Temperature panels still show all 14 assets simultaneously
- Options:
  - Pre-filter to show only the 4-5 highest-activity assets by default  
  - Split into sub-panels by asset class (ESP-only, Gas Lift-only, Rig-only)
  - Since `?kiosk=tv` hides the `$asset` variable dropdown, legend-click is the only isolation mechanism

**10. Deep Dive — Field Intelligence Dynamic Integration**
- Currently when a fault is active, the Live Intelligence Feed in Deep Dive shows hardcoded `INTELLIGENCE_FEED` items for that fault type
- The `field_intel` table now exists with AI-generated documents — need to merge them into the feed
- See Item 5 above for implementation plan

### Low Priority / Future

**11. Demo Flow Polish**
- Consider whether the `⚡ GDC Edge AI Detection Timeline` in Grafana needs annotation arrows
- Suggested demo script: start on Fleet Telemetry (SCADA "all clear") → switch to Fleet Operations → click ESP-A2 → Sand Ingress → watch AI detect while SCADA stays silent → consult agent → approve remediation

**12. Chart Y-Axis Calibration Note**
- The single exponential curve now correctly shows a continuous decline from current sensor value to failure state
- The SCADA alarm vertical marker (ML-predicted time) may not align exactly with where the curve crosses `y_crit` — this is intentional: the ML model's time prediction and the physical sensor trajectory are independent estimates, both shown simultaneously
- This is actually more honest than the previous "forced alignment" approach

---

## Constraints — Do Not Violate

- **Never apply `terraform/gke.tf`** — destroys the live cluster
- **Never change iframe to `?kiosk`** — must stay `?kiosk=tv` for chart rendering stability  
- **Only edit:** `gke/fault-trigger-ui/app.py`, `gke/fault-trigger-ui/index.html`, `gke/grafana/k8s/grafana-configmap.yaml`
- Gemma keepalive thread is in `app.py` — prevents cold starts during demos
- XGBoost health models (`*.ubj`) are validated — do not retrain without specific reason
- `_ensure_field_intel_table()` creates the `field_intel` table idempotently on startup — safe to run repeatedly

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

## Key Lessons Learned (Session 6)

**Chart physics — single vs two-segment exponential:** The two-segment approach (segment 1: y_start→y_crit at rul_minutes; segment 2: y_crit→y_failure) creates an unphysical kink because the derivative is discontinuous at the SCADA detection time. A single exponential `f(t) = y_start + (y_failure - y_start) × (exp(k×t/T) - 1) / (exp(k) - 1)` is physically correct — sensor values degrade continuously regardless of when AI or SCADA detects the fault. The detection time is just a vertical marker, independent of the curve shape.

**SCADA alarm marker vs curve crossing:** With the single exponential, the SCADA alarm vertical marker (from the ML model's `rul_minutes` prediction) may not exactly align with where the curve crosses `y_crit`. This is acceptable — they are independent estimates. The curve shows the physical trajectory; the marker shows the ML model's time prediction. Both are useful, neither invalidates the other.

**Intel generator startup timing:** The `_intel_generator` thread sleeps 60s on startup before calling `_ensure_field_intel_table()`. This means the first generated document appears ~2-5 minutes after container start. The UI's `fetchFieldIntel` is delayed 90s with a `setTimeout` to accommodate this.

**`replace_in_file` partial replacement danger (reminder from Session 5):** When replacing large HTML blocks, always verify div counts before/after. Always use `grep -n` to audit structural divs. The lesson from Session 5 saved time in Session 6 — all replacements were done in small targeted blocks.
