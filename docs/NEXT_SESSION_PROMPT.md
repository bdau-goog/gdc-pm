# Next Session Prompt — GDC Edge AI Demo (Operational State)
**Date:** June 9, 2026 (Session R — Physics Audit & Design Overhaul, doc-only)
**git head:** `f27f6c6` (pre-session — no code changed this session, design only)
**fault-trigger-ui image:** `sha256:a751a83e` (1/1 Running — Session Q, still current)
**inference-api image:** `sha256:d1194989` (1/1 Running — unchanged)
**Branch:** `feature-trio-clean` — do NOT merge to main

---

## STEP 1: Run These Four Commands First

```bash
kubectl get pods -n gdc-pm --no-headers
kubectl get deployment ollama -n gdc-pm -o jsonpath='{.spec.replicas}'; echo ""
curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "import sys,json;d=json.load(sys.stdin);print('ollama_online:',d.get('ollama_online'),'model:',d.get('ollama_model'))"
kubectl exec -n gdc-pm deployment/alloydb-omni -- psql -U postgres -d grid_reliability -c "SELECT COUNT(*) FROM field_intel; SELECT COUNT(*) FROM rag_documents;"
```

**Expected when healthy:**
- All 8 pods 1/1 Running · ollama replicas: 1
- ollama_online: True · model: gemma4:latest
- field_intel: ~2–3 · rag_documents: 18

---

## STEP 2: Read DEMO_MASTER.md (MANDATORY)

```bash
cat ~/gdc-pm/docs/DEMO_MASTER.md
```

---

## STEP 3: Session S — Next Implementation Tasks

### ⚠ PRIORITY 1: Model Retraining (ML Integrity — MUST DO FIRST)

Our XGBoost models (`esp_health.ubj`, `esp_classifier.ubj`) were trained on **physically inaccurate** fault endpoint ranges. The H1 demo chart currently shows flat ~199°F temperature and modest PIP decline — which is physically wrong for an ESP unloading event (motor cooling collapses, winding temp must rise). We CANNOT show these charts to O&G engineers until this is fixed.

**The Ground-Truth Physics Ranges (sourced: API RP 11S §4.2 / §7.2, SPE-174536-MS):**

| Metric | Nominal | Fault End-State (Gas Lock & Drawdown) | Physical Reason |
|--------|---------|----------------------------------------|-----------------|
| PIP (`psi`) | 1200–1250 PSI | **400–600 PSI** | Casing annulus hydrostatic column depleted / gas unloads stages |
| Amps (`amps`) | 85–92 A | **20–45 A** (midpoint 32.5A) | Motor underload as impeller stages fill with gas/vapor |
| Winding Temp (`temp_f`) | 195–202°F | **245–265°F** | Thermal runaway — motor cooling fluid flow collapses |
| Vibration (`vib`) | 0.8–1.4 mm/s | **4.5–6.5 mm/s** | Intense downhole cavitation during stage unloading |

**CRITICAL:** Gas Lock and Fluid Drawdown have **IDENTICAL raw sensor trajectories** (this is the H1 premise). Only unstructured context (RAG) distinguishes them.

**Retraining Steps:**
```bash
# 1. Update canonical physics ranges
#    Edit gke/shared/fault_signatures.py:
#    gas_lock:      psi(400,600), temp(245,265), vib(4.5,6.5), amps(20,45)
#    fluid_drawdown: same as gas_lock (they are identical on raw sensors)

# 2. Run ESP classifier retraining (~10 seconds)
cd ~/gdc-pm
python scripts/train_classifiers.py --asset-class esp \
    --output-dir gke/inference-api/models \
    --n-trajectories 600 --n-normal 24000 --rounds 300

# 3. Run health model retraining (~10 seconds)
python scripts/seed-and-train-og-models.py

# 4. Rebuild and deploy inference-api
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest gke/inference-api/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest
kubectl rollout restart deployment/inference-api -n gdc-pm

# 5. Run the offline verification check
python scripts/verify_classifier_offline.py
# Expected: gas_lock >= 0.92 precision, slug_flow >= 0.90 precision, normal >= 0.95
```

---

### PRIORITY 2: Build Surveillance Tab (New Opening Hook)

Add a new `Surveillance` tab as the **first tab** in the header nav (before "Discern"). This is a static, no-polling tab — all values are defensible fleet-representative numbers requiring zero backend changes.

**Tab label in HTML:** `Surveillance` (add before the existing "Discern" tab `hdr-tab` div)

**Content (all static — no API calls):**
1. **Hero Scope Panel** — dark banner with 4 stat metrics:
   - `Monitored Production Pads: 6`
   - `Active ESPs: 156`
   - `Active SCADA Alarms: 14`
   - `Unstructured Document Corpus: 8,412 documents (AlloyDB pgvector)`
2. **Pad/Field Triage Grid** — 6 compact field cards (Pad Alpha → Foxtrot):
   - Each shows: pad name, ESP count, current status dot (green = Nominal, amber = Alert)
   - Pad Alpha card: amber dot, `⚠ Well A-3 — Unloading Anomaly Active`
3. **Active Alarm Noise Panel** (right 30%) — static alarm list replicating a real DCS feed:
   ```
   ⚠ GLIFT-BRAVO-1   High Vibration (6.2 mm/s)    03:14 ago
   ⚠ MUD-RIG42-2     Fluid End Temp High (138°F)   07:22 ago
   ⚠ ESP-ALPHA-3     PIP Declining                  00:45 ago ← THIS ONE
   ⚠ TOPDRIVE-RIG42  Gearbox Temp Elevated          11:07 ago
   ⚠ GLIFT-BRAVO-3   Discharge Pressure Low         19:44 ago
   ... 9 more alarms active
   ```
   Caption: `"14 alarms active — GDC scanning 8,412 documents on all 156 ESPs simultaneously"`
4. **Deep-Dive CTA Button** — `[ 🔍 Deep-Dive — Well A-3 Unloading Anomaly ]` that calls `setMainTab('horizon1')` and triggers `loadH1Scenario()` when clicked.

**Vue state needed:** `mainTab` already exists. The CTA button just calls the existing H1 tab navigation methods. No new backend endpoints required.

---

### PRIORITY 3: Backend Scenario Replay Physics Update (`app.py`)

Update `/api/h1/scenario-replay` (lines 5827–5965):
1. **`psi_nom`** ramp: start `random.uniform(1180, 1250)`, end `random.uniform(400, 600)` (not 875–1100)
2. **`temp_nom`** ramp: start `random.uniform(195, 202)`, end `random.uniform(245, 265)` (not 195–210)
3. **`vib_nom`** ramp: start `random.uniform(0.8, 1.4)`, end `random.uniform(4.5, 6.5)` (not 2.0–3.5)
4. **`amps_nom`** ramp: start `random.uniform(85, 92)`, end midpoint of `(20, 45)` = 32.5A
5. **SCADA alarm rules**: Update from the single `psi < 1020` floor to the 3-rule set:
   - Rule A: dPIP/dt < -35 PSI/min (rolling 2.5-min rate alarm, ISA-18.2 §5.3)
   - Rule B: rolling-avg PIP < 1020 PSI (pressure underload floor, API RP 11S §7.2) ← fires ~T=10 min
   - Rule C: Amps < 50 A (motor undercurrent trip, API RP 11S §7.2) ← fires ~T=18 min
   - Fire at earliest of all three. Also update `FAULT_PROFILES["gas_lock"]` and `["fluid_drawdown"]` in `app.py` to match these ranges so the degrade thread is also corrected.
6. **Update SCADA alarm banner text** to say `"PIP < 1020 PSI"` (not 800).

**Expected result after fix:** GDC detects at ~T=6 min, Smart-SCADA alarms at ~T=10 min, lead-time = ~4 minutes.

---

### PRIORITY 4: H1 Frontend Layout Redesign (`index.html` + `app.js`)

**3a. Move timeline scrubber directly above the 4-stack charts (Left Column only):**
- Remove the scrubber from its current position (below the banner, spanning full width).
- Place it inside the Left Column `div`, immediately above `#h1-replay-chart`.
- Set `padding-left: 48px; padding-right: 12px` (matches Plotly's `margin: {l:48, r:12}`).
- Because the scrubber now lives inside the resizable left column, it will resize with the Plotly area automatically. The grey cursor line and slider knob will stay **perfectly vertically aligned** at any column width.

**3b. Add "ⓘ Physics & Logic" info drawer button:**
- Place it in the header bar next to `↺ New Scenario`.
- Toggles a collapsable info panel above the charts explaining: ESP Unloading Physics, SCADA 4-rule trip logic, XGBoost pre-threshold multivariate detection, L3 RAG context fusion.

**3c. Strict SCADA/GDC visual partition in Decision Console:**
- **SCADA View active:** Hide the SVG downhole wellbore panel entirely. Hide GDC-only elements (`hs = X.XXXX`, health threshold labels, fault type reveal). Show a bare-metal 2×2 sensor grid (PIP / Amps / Temp / Vib) with live cursor values and SCADA threshold annotations. No downhole visualization (SCADA does not have a downhole digital twin).
- **GDC Advisor active:** Reveal the SVG wellbore digital twin. Show GDC health score, pgvector RAG document cards, fault type, and informed intervention cards.

**3d. Scrubber-reactive SVG wellbore digital twin:**
- **Fluid column** (already bound to PIP) — with the PIP now crashing to 400–600 PSI, the visible drain will be dramatic.
- **Gas bubbles** (Gas Lock): opacity and count bound to `Math.max(0, h1CursorIdx - h1ReplayData.gdc_detect_idx) / (h1ReplayData.n - h1ReplayData.gdc_detect_idx)`. Pre-detection: 0 bubbles. Post-detection: bubbles intensify as you scrub.
- **Sand settling** (Drawdown): same binding — sand particles become visible and sink as scrubber passes detection.
- **No flashing/gamified effects** — clean, static-positioned SVG elements with opacity transitions only.

**3e. Eliminate chart x-axis truncation:**
- The current code shows the full 30-minute pre-computed array. After the 120-step array is played, the chart should transition to continuous live telemetry scrolling, showing the last 30 minutes as a rolling window.

---

### PRIORITY 5: Deploy and Verify

```bash
# Rebuild fault-trigger-ui
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest gke/fault-trigger-ui/
docker push us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest
kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm

# Verify smoke test passes
cd ~/gdc-pm && node scripts/ui_smoke.mjs
# Expected: ✅ SMOKE TEST PASSED (12/12 assertions, 0 console errors)

# Verify scenario replay with updated physics
curl -s "http://gdc-pm.bdau.io/api/h1/scenario-replay?fault=gas_lock" | python3 -c \
  "import sys,json;d=json.load(sys.stdin);
   print('n:',d['n'],'gdc:',d['gdc_detect_idx'],'scada:',d['scada_alarm_idx'],
         'lead:',d['lead_time_minutes'],'psi_final:',round(d['psi'][-1],0),
         'temp_final:',round(d['temp'][-1],0),'amps_final:',round(d['amps'][-1],1),
         'vib_final:',round(d['vib'][-1],2),'model:',d['model_used'])"
# Expected: gdc ~ 24, scada ~ 40, lead ~ 4 min, psi_final ~ 450–550, temp_final ~ 255–265, amps_final ~ 30–35, vib_final ~ 5.0–6.0
```

---

## Known Integrity State

| Item | Status | Note |
|------|--------|------|
| H1 Scenario Replay (Session Q) | ⚠ PHYSICS INACCURATE | PIP too high (875–1100 → correct: 400–600), Temp flat (needs to rise to 245–265°F), Vib too low |
| Smart SCADA alarm logic | ⚠ FIRES TOO LATE | scada_alarm_idx=119/120 in Session Q. Needs multi-rule update (PIP floor, Amps trip). |
| `esp_health.ubj` / `esp_classifier.ubj` | ⚠ RETRAIN REQUIRED | Trained on old (875–1100 PSI, 195–210°F) ranges. Will mis-score corrected physics trajectory. |
| SCADA tab shows GDC health header | ⚠ INTEGRITY VIOLATION | GDC-only elements (hs=0.6953, XGBoost threshold) visible on SCADA view. Must be hidden. |
| SVG wellbore animations | ⚠ FIRE ONCE, STAY | Currently fire on `h1RagRevealed = true` and stay indefinitely. Need scrubber-position binding. |
| Scrubber vs chart misalignment | ⚠ NOT IN LEFT COLUMN | Scrubber is outside the resizable left column. GDC▲/SCADA▲ tick marks may drift. |

---

## Constraints (Permanent)
- `terraform/gke.tf` must NOT be applied
- No browser on SSH remote — use `node scripts/ui_smoke.mjs` instead
- Batch all edits to same file in ONE `replace_in_file` call
- Registry: `us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/fault-trigger-ui:latest`
- Do NOT use "Copilot" anywhere in the UI
- `feature-trio-clean` branch — do NOT merge to main
- Gas Lock and Fluid Drawdown have IDENTICAL sensor trajectories — this is the H1 premise
