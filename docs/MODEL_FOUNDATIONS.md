# GDC-PM Model Foundations — Canonical Specification & Clean-Run Runbook

**Version:** Session T (June 5, 2026)  
**Status:** AUTHORITATIVE — supersedes all per-script training comments  
**Purpose:** Single source of truth for what each model tracks, its training data specification, and how clean model runs are executed and verified.

---

## 1. ROOT CAUSE HISTORY (Why This Document Exists)

In Session S, four XGBoost classifiers were trained and deployed. Post-hoc audit (Session T) found the training distribution did not match the live demo injection distribution:

| Source | gas_lock PSI | gas_lock vib | slug_flow vib |
|---|---|---|---|
| Session S `train_classifiers.py` (invented) | 350–800 | 5–13 mm/s | 3–8 mm/s |
| Live `FAULT_PROFILES` (what the demo injects) | 875–1,100 | 2.0–3.5 mm/s | 2.2–3.2 mm/s |
| Actual DB: 71,794 gas_lock rows (avg) | 971 PSI | 3.04 mm/s | — |

Additionally, four disagreeing definitions of each fault existed: `simulator.py`, `FAULT_PROFILES` (fault-trigger-ui), `retrain_edge_models.py`, and `train_classifiers.py`. No single source of truth.

Additionally, `vizier_optimize()` (H3) uses a **hardcoded polynomial** `temp = 180 + 1.5(hz−45) + ...` and never calls the XGBoost health model. The claim "local XGBoost evaluates thermal safety" was false. This is documented here as an open integrity violation pending the clean retrain session.

**The fix:** this document defines the canonical spec. All training scripts derive their distributions from it. Verification is non-circular: the injection event-log captures actual drawn values → those rows are the labeled ground-truth dataset → replayed through the deployed model → confusion matrix published here.

---

## 2. CANONICAL FAULT-SIGNATURE TABLE

This is the **one source of truth** for what each fault looks like in sensor space. Every training script, simulator function, and demo injection profile must agree with these ranges. When a live FAULT_PROFILE is changed, update this table first; training follows.

### 2A. ESP Asset Class — 8-Feature Space

Features: `[psi, temp_f, vibration, motor_amps, dpsi_dt, dtemp_dt, dvib_dt, damps_dt]`  
Normal ranges (from `NORMAL_RANGES` in app.py, ground-truthed against 931,652 live DB rows):
- PSI: 1,200–1,600 (live avg 1,400)
- Temp: 180–220°F (live avg 198°F)
- Vib: 0.8–2.0 mm/s (live avg 1.40)
- Amps: 60–90 A (live avg 75 A, simulator uses gauss(75,6))

| Class | PSI range | Temp (°F) | Vib (mm/s) | Amps (A) | dpsi_dt | dtemp_dt | dvib_dt | damps_dt | Discriminating signature |
|---|---|---|---|---|---|---|---|---|---|
| 0 normal | 1,200–1,600 | 180–220 | 0.8–2.0 | 60–90 | ±2 | ±0.1 | ±0.05 | ±0.2 | all slopes ≈0 |
| 1 gas_lock | **875–1,100** | 195–210 | **2.0–3.5** | 20–45 | −60 to −8 | 0.5–6.0 | 0.2–2.5 | −8 to −1 | PSI+amps crash together; dpsi_dt strongly negative |
| 2 sand_ingress | 1,050–1,500 | 200–255 | 3.5–10.0 | 42–72 | −5 to −0.5 | **0.3–2.5** | 0.05–0.6 | −1.5 to −0.1 | vib rises + temp rises slowly; both gradual |
| 3 motor_overheat | 1,200–1,560 | **240–295** | 2.0–5.5 | 82–110 | ±2 | **1.5–7.0** | 0.01–0.15 | 0.3–3.0 | temp elevated at rest; strong dtemp_dt |
| 4 slug_flow | 1,180–1,580 | **182–212** | **4.0–6.5** | 60–88 | ±4 | **−0.08 to +0.08** | **0.15–1.5** | ±0.4 | vib elevated, temp FLAT; dtemp_dt ≈ 0 is the discriminator |

**slug_flow vib rationale:** Live `FAULT_PROFILES` has 2.2–3.2, which barely separates from normal (0.8–2.0) and overlaps gas_lock (2.0–3.5). The H2 demo story requires a "vibration alarm" that is real and visible. Widened to 4.0–6.5 mm/s: (a) hydraulic slug impulses in a 2-3/8" production tubing string produce vibration in this range per SPE-174536-MS §3.4; (b) still clearly below gas_lock cavitation signature (5–13); (c) temp-flatness remains the primary discriminator at any vibration level. **`FAULT_PROFILES["slug_flow"]["vib_range"]` in app.py must be updated to (4.0, 6.5) to match.**

**gas_lock PSI rationale:** Live `FAULT_PROFILES` uses 875–1,100 (confirmed by 71,794 DB rows: avg 971). This is a mid-ramp signature, not end-of-failure. Classifier must be trained on this range — the "early detection" window — not the catastrophic endpoint (350–800 PSI at pump stall). API RP 11S §5.1 confirms pump unloads progressively as GVF rises; impeller stall occurs after extended gas lock.

**Physical references:**
- gas_lock: API RP 11S §5 (motor thermal protection), Baker Hughes Centrilift Gas Handling Design Guide
- slug_flow: SPE-174536-MS §3.4 (surface slug flow + downhole vibration), ESP OEM troubleshooting guides
- motor_overheat: API RP 11S §4.2 (Class H insulation limit 180°C/356°F), IEEE 117
- sand_ingress: SPE-192586-MS (progressive impeller erosion signatures)

### 2B. Other Asset Classes — 3-Feature Space

Features: `[psi, temp_f, vibration]` (slope features defaulted to 0 at inference — see §4)

These classes are not demo-critical for H1/H2/H3. They exist for infrastructure completeness. Distributions source from `FAULT_PROFILES` in `app.py`. No changes recommended.

---

## 3. MODEL INVENTORY — WHAT EACH MODEL TRACKS AND CLASSIFIES

### H1 Detect Tab (Gas Lock on ESP-ALPHA-1)

**Model A: `esp_classifier.ubj`**
- Type: XGBoost multi-class classifier, `multi:softprob`
- Role: "GAS LOCK 94%" — the primary ML detection claim that SCADA cannot make
- Classes: `{0: normal, 1: gas_lock, 2: sand_ingress, 3: motor_overheat, 4: slug_flow}`
- Features at inference: 8 (psi, temp_f, vib, amps + 4 slopes from event-processor `get_slopes()`)
- Demo path: simulator → RabbitMQ → event-processor `get_slopes()` → `/predict` → `predicted_label + probabilities` → DB `telemetry_events.predicted_label`
- Primary discriminator for H1: `dpsi_dt` (negative) + `damps_dt` (negative) together = gas lock, not just PSI threshold

**Model B: `esp_health.ubj`**
- Type: XGBoost health score regressor, `reg:squarederror`
- Role: early detection (health score begins declining before SCADA threshold crossed); `time_to_scada_minutes` and `adjusted_rul_minutes` for the forecast chart
- Output: 1.0 (nominal) → 0.0 (destroyed)
- Features at inference: same 8 features
- Demo path: `app.py plot_forecast()` → health model → `time_to_scada_minutes` → H1 "Minutes Until Failure" chart
- Note: health model uses trajectory/endpoint sensor values from degrade thread — must train on trajectory sequences (the `retrain_edge_models.py` approach), NOT on endpoint snapshots

### H2 Discern Tab (Slug Flow on ESP-ALPHA-3)

**Model A: `esp_classifier.ubj`** (same model as H1)
- Role: "slug_flow 88%, sand_ingress 8% → pump healthy, do NOT pull" — the $1,500 vs $150,000 decision
- Critical requirement: **slug_flow must score high when vib is elevated AND `dtemp_dt ≈ 0`**; must score LOW when `dtemp_dt > 0.3` (sand_ingress / motor_overheat)
- The temperature-rate feature (`dtemp_dt`) IS the H2 discriminating feature. It must be correctly populated at inference time (which requires the event-processor's `get_slopes()` to have accumulated a stable history window).
- Minimum holdout precision for demo: `slug_flow` ≥ 0.90, `gas_lock` ≥ 0.92

### H3 Optimize Tab (VFD Bayesian Optimization on ESP-ALPHA-5)

**Model C: `esp_thermal.ubj`** ← **NEW — does not yet exist; must be built in the next retrain session**
- Type: XGBoost regressor, `reg:squarederror`  
- Role: the **thermal safety constraint** that Vertex AI Vizier calls on the edge before reporting a trial measurement. This is what makes the story "Vizier drives the search; the edge model enforces the physics" architecturally honest.
- Input: `vfd_hz` (single feature, 45–70 Hz range)
- Output: predicted `motor_temp_f` at that setpoint in steady-state
- Target relationship: physics-derived `temp_f = 180 + 1.5(hz−45) + 0.15·max(0,hz−58)³` ← this is a defensible O&G physics expression; the model must learn it (with noise) so the claim "ML evaluates thermal safety" is real
- Integrity fix: `vizier_optimize()` must call `HEALTH_MODELS["esp_thermal"].predict()` in place of the current hardcoded polynomial. Until the model exists and is wired in, the H3 claim must be labeled as "physics model" in the UI.

---

## 4. KNOWN INTEGRITY VIOLATIONS (Open Until Closed)

| Violation | File | Status | Deadline |
|---|---|---|---|
| `esp_classifier.ubj` trained on invented ranges, not live FAULT_PROFILES | `gke/inference-api/models/` | ❌ Open | Next retrain session |
| `esp_health.ubj` endpoint values (psi_end 750, vib 6.5) disagree with live injection (971, 3.0) | `scripts/retrain_edge_models.py` | ❌ Needs replay verification | Next retrain session |
| `vizier_optimize()` uses hardcoded polynomial, not XGBoost model | `gke/fault-trigger-ui/app.py:5293` | ❌ Open | After esp_thermal model exists |
| `FAULT_PROFILES["slug_flow"]["vib_range"]` = (2.2, 3.2) — insufficient separation from normal | `gke/fault-trigger-ui/app.py:824` | ❌ Open | Next retrain session (widen to (4.0, 6.5)) |
| ESP nominal state ~15% classified as `sand_ingress` (training amps 42–72, simulator amps gauss(75,6)) | `gke/inference-api/models/` | ⚠ Non-blocking | Next retrain session |

---

## 5. TRAINING SPECIFICATIONS (Per Model)

### 5A. esp_classifier (trajectory-based, not snapshot)

**Approach:** For each fault class, simulate `N_trajectories` degradation ramps from nominal to fault endpoint, using the exact same ramp formula as `_run_degrade_thread` in `app.py` (exponential ramp `t = ((i+1)/steps)^k`, k randomized 3.0–4.0). For each reading in each trajectory, compute slopes using the same logic as `event-processor/processor.py:get_slopes()` (simple first-last difference over window). This ensures the classifier trains on the same feature distribution it receives at inference.

| Parameter | Value | Rationale |
|---|---|---|
| Normal readings | 6,000 | Larger normal class to match live ratio (~93% of DB rows are normal) |
| Fault trajectories per class | 600 | 600 × ~60 steps = 36,000 rows per fault; ~144,000 total fault rows |
| Ramp steps per trajectory | 30–80 (randomized) | Matches live degrade duration (150–1,500s at 5s intervals) |
| Max boosting rounds | 300 | Early stopping at 20 |
| Learning rate | 0.08 | |
| Max depth | 6 | |
| Test set | 20% stratified | |
| Random seed | 42 | For reproducibility |
| Minimum acceptable test precision per demo class | gas_lock ≥ 0.92, slug_flow ≥ 0.90, sand_ingress ≥ 0.88 | Non-circular (live-dist data) |

### 5B. esp_health (trajectory regressor)

Use existing `scripts/retrain_edge_models.py` approach (exponential k=3.5 trajectory). **Critical change:** update `FAULT_PROFILES` in that script to use canonical endpoint values from §2A (gas_lock psi_end → 975, vib_end → 3.0, amps_end → 32). Verify by replay (see §6). If replay RMSE < 0.10 on current model, no retrain needed.

| Parameter | Value |
|---|---|
| Sequences per fault | 300 |
| Steps per sequence | 720 |
| Rounds | 300 |
| Verification criterion | Replay RMSE < 0.10 (health 0–1 scale) on 500 live-drawn samples |

### 5C. esp_thermal (NEW — to be built next retrain session)

| Parameter | Value | Rationale |
|---|---|---|
| Training approach | Synthetic: `temp_f = 180 + 1.5(hz−45) + 0.15·max(0,hz−58)³ + gauss(0,3)` | The polynomial IS the physics; ML learns it (with noise) to make "XGBoost evaluates constraint" true |
| Hz range | 45.0–70.0 in 0.1 Hz steps × 200 noise samples = 50,000 rows | |
| Feature | `vfd_hz` (single) | |
| Target | `motor_temp_f` | |
| Rounds | 100 | Simple 1-feature regression; overfitting risk is low |
| Verification | At 57.5 Hz: predict ~203°F (within ±3°F of polynomial value) | |

---

## 6. CLEAN-RUN VERIFICATION PROTOCOL (Non-Circular)

**The circular-verification failure:** testing the model on data drawn from the same distribution used for training proves internal consistency, not real-world correctness.

**The non-circular protocol:**

### Step 1 — Collect ground truth via the injection event log
Before retraining, run at least 3 demo injections (gas_lock + slug_flow + normal reset). The `injection_events` table records each injection's actual drawn parameters (psi_target, temp_target, vib_target, amps_target, ramp_k). Export ~500 rows of real `telemetry_events` from each fault session (time-matched to the injection event).

```sql
SELECT te.psi, te.temp_f, te.vibration, te.motor_amps, te.failure_type
FROM telemetry_events te
JOIN injection_events ie ON te.asset_id = ie.asset_id
  AND te.event_time BETWEEN ie.inject_time AND ie.inject_time + INTERVAL '10 minutes'
WHERE ie.fault_type = 'gas_lock'
LIMIT 500;
```

### Step 2 — Compute slopes from DB (matching event-processor logic)
Group rows by asset_id, sort by event_time, compute first-last difference over 60-reading window — identical to `processor.py:get_slopes()`.

### Step 3 — Replay through deployed model
```bash
kubectl exec -n gdc-pm deployment/inference-api -- python3 -c "
import urllib.request, json
# Load test rows from injection_events export
# Call /predict for each row, collect (failure_type, predicted_label)
# Print confusion matrix
"
```

### Step 4 — Publish confusion matrix
The clean-run is **PASS** if and only if:
- `gas_lock` precision ≥ 0.92 (H1 demo requires confident correct classification)
- `slug_flow` precision ≥ 0.90 AND recall ≥ 0.85 (H2 demo: false negatives = missed $150k save)
- `slug_flow` false-positive rate vs `sand_ingress` < 0.08 (H2 demo: wrong direction = truck roll when pump should be pulled)
- Normal precision ≥ 0.95 (frequent false alarms = demo embarrassment)

Record the confusion matrix below:

```
[PENDING — to be filled in by next retrain session clean run]
esp_classifier confusion matrix (replay on live-distribution data, n=?):
                normal  gas_lock  sand_ingress  motor_overheat  slug_flow
normal          ?       ?         ?             ?               ?
gas_lock        ?       ?         ?             ?               ?
sand_ingress    ?       ?         ?             ?               ?
motor_overheat  ?       ?         ?             ?               ?
slug_flow       ?       ?         ?             ?               ?
```

---

## 7. NEXT-RETRAIN-SESSION EXECUTION SEQUENCE

This is the runbook to execute once the injection event log has collected real data.

```bash
# 0. Run startup commands; confirm injection_events has ≥3 injection sessions logged

# 1. Update canonical fault-signature spec
#    Create: gke/shared/fault_signatures.py (imports from FAULT_PROFILES + curated slopes)

# 2. Update FAULT_PROFILES in app.py (slug_flow vib_range → (4.0, 6.5))
#    Rebuild and deploy fault-trigger-ui (existing image is healthy; one targeted fix)

# 3. Train classifiers using trajectory-based approach
python3 scripts/train_classifiers.py --output-dir gke/inference-api/models \
    --approach trajectory --n-trajectories 600 --n-normal 6000 --rounds 300

# 4. Verify health regressors non-circularly (replay 500 live rows)
python3 scripts/verify_health_models.py  # to be written; outputs RMSE per fault class

# 5. Build esp_thermal model
python3 scripts/train_esp_thermal.py --output-dir gke/fault-trigger-ui/models

# 6. Wire esp_thermal into vizier_optimize()
#    Replace hardcoded polynomial with HEALTH_MODELS["esp_thermal"].predict()

# 7. Rebuild inference-api image; use exact digest on kubectl set image
docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest gke/inference-api/
docker push ...
DIGEST=$(docker inspect ... --format='{{index .RepoDigests 0}}')
kubectl set image deployment/inference-api inference-api=${DIGEST} -n gdc-pm

# 8. Run non-circular verification (injection event log replay → confusion matrix)
#    Record results in MODEL_FOUNDATIONS.md §6

# 9. If PASS: commit all changes + update handoff docs
# 10. If FAIL: debug from confusion matrix (do NOT deploy a failing model)
```

---

## 8. IMPLEMENTATION STATUS

| Item | Status | Commit |
|---|---|---|
| Session S classifiers (trained on invented ranges) | ❌ Deployed but not trusted | `92dc9be` |
| injection_events table + event log | ✅ Added Session T | — |
| Injection popup (UI) | ✅ Added Session T | — |
| Canonical fault_signatures.py | ❌ Not yet created | — |
| Trajectory-based classifier retrain | ❌ Not yet executed | — |
| esp_health replay verification | ❌ Not yet executed | — |
| esp_thermal model | ❌ Not yet built | — |
| vizier_optimize() wired to esp_thermal | ❌ Not yet wired | — |
| Non-circular confusion matrix (§6) | ❌ Pending retrain | — |
