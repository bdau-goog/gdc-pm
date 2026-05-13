#!/usr/bin/env python3
"""
scripts/retrain_edge_models.py

Phase 5.1 — Core Physics Engine Rebuild
========================================
Trains a single XGBoost Health Score regressor per asset class.

WHAT CHANGED FROM PHASE 4.1
-----------------------------
  Phase 4.1: Predicted RUL_Minutes (60 → 0) using a LINEAR degradation curve.
             Had V1 (cloud-drifted) and V2 (edge-calibrated) model variants.

  Phase 5.1: Predicts Health_Score (1.0 → 0.0) using an EXPONENTIAL degradation
             curve.  Single high-quality model per asset class.  No V1/V2 split.

WHY HEALTH SCORE INSTEAD OF RUL_MINUTES
-----------------------------------------
  The old RUL approach locked every fault into a 60-minute clock.
  Sand Ingress on an ESP takes 14 days — a 60-minute countdown is physically
  wrong and makes the agentic value proposition narratively absurd.

  Health Score is agnostic to physical time.  The model learns to score the
  STATE of equipment health from the multivariate sensor signature.  The UI
  layer (app.py FAULT_PHYSICS config) then maps Health Score → physical time
  for each fault mode:
    - gas_lock:     0.75 h total   (45 minutes)
    - sand_ingress: 336 h total    (14 days)
    - gearbox_bearing_spalling: 10 h, etc.

  This lets one model architecture correctly serve both a 45-minute Gas Lock
  and a 14-day Sand Ingress scenario without retraining.

WHY EXPONENTIAL DEGRADATION
-----------------------------
  Real equipment failure is NOT linear.  It follows Bath-Tub physics:
    - Long incipient period: sensors barely move (SCADA is silent)
    - Accelerating degradation: the ML model catches the slope early
    - Rapid final phase: SCADA alarm fires → PNR → Failure in quick succession

  Formula: t_frac = (exp(k * t) - 1) / (exp(k) - 1)   where k = 3.5
    - At t = 0.0: t_frac ≈ 0   → sensors at nominal, health = 1.0
    - At t = 0.5: t_frac ≈ 0.11 → sensors only 11% toward fault endpoint
    - At t = 0.75: t_frac ≈ 0.32 → still subtle — ML detects, SCADA does not
    - At t = 0.90: t_frac ≈ 0.65 → SCADA alarm fires
    - At t = 1.0: t_frac = 1.0  → sensors at fault endpoint, health = 0.0

  This produces the correct physical timeline on the chart:
    ML Detection → SCADA Alarm → PNR → Failure

FEATURE VECTORS (unchanged from Phase 4.1)
--------------------------------------------
  ESP (8 features):
    [psi, temp_f, vibration, motor_amps, dpsi_dt, dtemp_dt, dvib_dt, damps_dt]
  Mud Pump (8 features):
    [psi, temp_f, vibration, spm, dpsi_dt, dtemp_dt, dvib_dt, dspm_dt]
  Gas Lift / Top Drive (6 features):
    [psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]

NOISE PROFILE
--------------
  Single edge-calibrated profile (V2 equivalent from Phase 4.1):
    psi:     ± psi  × 0.002
    temp:    ± temp × 0.001
    vib:     ± vib  × 0.005
    sensor4: ± s4   × 0.003

OUTPUT FILES
-------------
  gke/fault-trigger-ui/models/esp_health.ubj
  gke/fault-trigger-ui/models/gas_lift_health.ubj
  gke/fault-trigger-ui/models/mud_pump_health.ubj
  gke/fault-trigger-ui/models/top_drive_health.ubj

  Old *_rul.ubj and *_rul_v2.ubj files are NOT deleted by this script.
  Phase 5.2 will update app.py to load *_health.ubj instead.

USAGE
------
  python scripts/retrain_edge_models.py
  python scripts/retrain_edge_models.py --asset-class esp
  python scripts/retrain_edge_models.py --n-samples 300 --rounds 300
  python scripts/retrain_edge_models.py --n-samples 500 --rounds 400 --upload-gcs
"""

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("retrain_health")

# ── Asset normal operating ranges — must match NORMAL_RANGES in app.py ─────────
NORMAL_RANGES = {
    "esp":       {"psi": (1200, 1600), "temp": (180, 220), "vib": (0.8, 2.0)},
    "gas_lift":  {"psi": (940, 1060),  "temp": (140, 178), "vib": (1.0, 2.5)},
    "mud_pump":  {"psi": (2550, 3150), "temp": (90, 120),  "vib": (2.5, 4.5)},
    "top_drive": {"psi": (2840, 3160), "temp": (130, 165), "vib": (1.8, 3.8)},
}

# ── 4th-sensor normal ranges — must match SENSOR4_CONFIG in app.py ─────────────
SENSOR4_NORMAL = {
    "esp":      (60.0, 90.0),    # motor_amps nominal range (A)
    "mud_pump": (75.0, 100.0),   # spm nominal range (strokes/min)
}

# ── Fault endpoint values ───────────────────────────────────────────────────────
# *_end values represent the sensor state AT health_score = 0.0 (destroyed).
# These are the physical failure values, NOT the SCADA alarm thresholds.
# The SCADA alarm threshold is defined in FAULT_PHYSICS in app.py and will be
# reached at ~health_score 0.15–0.30 depending on the fault mode.
FAULT_PROFILES = {
    "esp": {
        # ── Gas Lock ──────────────────────────────────────────────────────────
        # Gas void fraction >80% → pump cavitates → intake pressure collapses
        # Timeline: 45 minutes total  (FAULT_PHYSICS total_hours = 0.75)
        "gas_lock": {
            "psi_end":  750,   # PSI at impeller stall (critical: 800 PSI)
            "temp_end": 200,   # Motor winding temp rises slightly as pump unloads
            "vib_end":  6.5,   # Cavitation vibration signature
            "amps_end": 28.0,  # Motor current collapses as pump unloads (crit: 40 A)
        },
        # ── Sand Ingress ──────────────────────────────────────────────────────
        # Formation sand slowly erodes impeller stages over 14 days
        # Timeline: 336 hours total  (FAULT_PHYSICS total_hours = 336)
        "sand_ingress": {
            "psi_end":  1100, # Intake pressure drops as impeller stages erode
            "temp_end": 245,  # Motor runs hotter as efficiency degrades
            "vib_end":  9.5,  # Increasing vibration from worn impeller clearances
            "amps_end": 42.0, # Current declines as pump does less hydraulic work
        },
        # ── Motor Overheat ────────────────────────────────────────────────────
        # Downhole cooling degradation → winding temp climbs → insulation failure
        # Timeline: 4 hours total  (FAULT_PHYSICS total_hours = 4)
        "motor_overheat": {
            "psi_end":  1280, # Pressure stable early; drops slightly at end
            "temp_end": 295,  # Winding temperature at thermal failure (crit: 280°F)
            "vib_end":  4.5,  # Minor vibration increase from thermal expansion
            "amps_end": 105.0, # Overcurrent as motor fights rising resistance
        },
    },
    "gas_lift": {
        # ── Check Valve Failure ───────────────────────────────────────────────
        # Valve breaks open → discharge pressure crashes as gas reverses
        # Timeline: 15 minutes total  (FAULT_PHYSICS total_hours = 0.25)
        "valve_failure": {
            "psi_end":  380,  # Discharge pressure at full reversal (crit: 600 PSI)
            "temp_end": 200,  # Temp rises from gas backflow heating
            "vib_end":  14.0, # Severe vibration from reverse gas flow
        },
        # ── Thermal Runaway ───────────────────────────────────────────────────
        # Cylinder jacket cooling fails → temp climbs toward seizure
        # Timeline: 72 hours total  (FAULT_PHYSICS total_hours = 72)
        "thermal_runaway": {
            "psi_end":  920,  # Pressure drops slightly as efficiency degrades at high temp
            "temp_end": 248,  # Cylinder discharge temp at seizure (crit: 230°F)
            "vib_end":  5.5,  # Minor vibration from thermal distortion
        },
        # ── Journal Bearing Wear ──────────────────────────────────────────────
        # Crankshaft bearing race fatigues → vibration signature rises over hours
        # Timeline: 16 hours total  (FAULT_PHYSICS total_hours = 16)
        "bearing_wear": {
            "psi_end":  945,  # Pressure essentially stable until late-stage
            "temp_end": 183,  # Temp rises slightly from bearing friction
            "vib_end":  13.5, # Frame vibration at bearing destruction (crit: 12 mm/s)
        },
    },
    "mud_pump": {
        # ── Pulsation Dampener Failure ────────────────────────────────────────
        # Bladder ruptures → extreme pressure hammer → immediate pipe-rupture risk
        # Timeline: 5 minutes total  (FAULT_PHYSICS total_hours = 0.083)
        "pulsation_dampener_failure": {
            "psi_end":  4600,  # Pressure spike at bladder failure (crit: standpipe limit)
            "temp_end": 158,   # Heat from pressure energy dissipation
            "vib_end":  28.0,  # Catastrophic vibration from pressure hammer (crit: 20 mm/s)
            "spm_end":  95.0,  # Chaotic erratic stroke rate
            "spm_erratic": True,
        },
        # ── Valve Seat Washout ────────────────────────────────────────────────
        # Fluid erosion of valve seat → discharge pressure slowly declines
        # Timeline: 10 hours total  (FAULT_PHYSICS total_hours = 10)
        "valve_washout": {
            "psi_end":  1600,  # Pressure at full valve failure (crit: 1800 PSI)
            "temp_end": 145,   # Modest heating from fluid turbulence at eroded seat
            "vib_end":  10.0,  # Vibration from valve flutter/chatter
            "spm_end":  120.0, # Driller compensates for efficiency loss
        },
        # ── Liner Seal Wear ───────────────────────────────────────────────────
        # Piston-liner seals degrade → fluid end temp rises, pressure drops slowly
        # Timeline: 4 days total  (FAULT_PHYSICS total_hours = 96)
        "piston_seal_wear": {
            "psi_end":  1750,  # Discharge pressure at seal failure
            "temp_end": 190,   # Fluid end temperature at liner overheating (crit: 180°F)
            "vib_end":  8.5,   # Vibration from liner slap as clearance increases
            "spm_end":  108.0, # Moderate driller compensation over days
        },
    },
    "top_drive": {
        # ── Gearbox Bearing Spalling ──────────────────────────────────────────
        # Bearing race fatigue → distinctive vibration signature → seizure risk
        # Timeline: 10 hours total  (FAULT_PHYSICS total_hours = 10)
        "gearbox_bearing_spalling": {
            "psi_end":  2840,  # Hydraulic pressure stable until late-stage
            "temp_end": 222,   # Gearbox oil temp rises from bearing friction heat
            "vib_end":  20.0,  # Vibration at full bearing destruction (crit: 15 mm/s)
        },
        # ── Hydraulic System Leak ─────────────────────────────────────────────
        # Hydraulic fluid loss → system pressure decay → torque capacity lost
        # Timeline: 6 hours total  (FAULT_PHYSICS total_hours = 6)
        "hydraulic_leak": {
            "psi_end":  1500,  # Hydraulic pressure at loss of torque (crit: 2000 PSI)
            "temp_end": 208,   # Temp rises as pump works harder to maintain failing pressure
            "vib_end":  7.0,   # Vibration from air intrusion in hydraulic circuit
        },
    },
}

# ── Edge-calibrated noise profile (V2 equivalent from Phase 4.1) ───────────────
# Matches the 5-second edge simulator telemetry noise characteristics.
# Single profile — no more V1 (cloud-drifted) noise for the MLOps drift demo.
PSI_NOISE_BASE     = 0.002   # ± 0.2% of reading
TEMP_NOISE_BASE    = 0.001   # ± 0.1% of reading
VIB_NOISE_BASE     = 0.005   # ± 0.5% of reading
SENSOR4_NOISE_BASE = 0.003   # ± 0.3% of reading

# ── Training hyper-parameters ──────────────────────────────────────────────────
STEPS            = 720      # 720 steps per sequence (arbitrary — health score is dimensionless)
SLOPE_WINDOW     = 60       # 60-reading causal window for slope features
READINGS_PER_MIN = 12.0     # Normalisation factor for slope units (60s ÷ 5s = 12)

# ── Exponential degradation curve ─────────────────────────────────────────────
# k controls the convexity of the failure curve:
#   k = 0 → linear (same as Phase 4.1)
#   k = 3.5 → realistic: slow incipient phase, rapid final failure
# At k=3.5 with t in [0,1]:
#   t=0.50 → t_frac ≈ 0.11  (sensors barely moved — ML detects, SCADA silent)
#   t=0.75 → t_frac ≈ 0.32  (slope features strengthening — ML alarm)
#   t=0.87 → t_frac ≈ 0.60  (SCADA threshold crossed)
#   t=0.94 → t_frac ≈ 0.80  (PNR passed — irreversible damage)
#   t=1.00 → t_frac = 1.00  (health_score = 0.0, destruction)
EXP_K = 3.5


# ── Vectorised rolling slope ───────────────────────────────────────────────────
def _rolling_slopes(arr: np.ndarray, window: int) -> np.ndarray:
    """
    Compute the OLS linear regression slope over a causal rolling window.

    Returns slopes in (arr-units / reading).  Caller multiplies by
    READINGS_PER_MIN to convert to per-minute rate of change.

    Closed-form OLS slope:   β = cov(t, y) / var(t)
    where t = [0, 1, …, w-1] for a window of length w.
    """
    n = len(arr)
    slopes = np.zeros(n, dtype=np.float64)
    for i in range(n):
        start = max(0, i - window + 1)
        y = arr[start : i + 1]
        w = len(y)
        if w < 3:
            continue
        t = np.arange(w, dtype=np.float64)
        t_c = t - t.mean()
        denom = float(t_c @ t_c)
        if denom == 0.0:
            continue
        slopes[i] = float(t_c @ (y - y.mean())) / denom
    return slopes


# ── Sequence generator ─────────────────────────────────────────────────────────
def generate_sequence(
    nr: dict,
    fp: dict,
    rng: np.random.Generator,
    sensor4_nr: tuple | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate one STEPS-step degradation sequence for a single fault mode.

    Parameters
    ----------
    nr          : normal ranges dict {"psi": (lo,hi), "temp": (lo,hi), "vib": (lo,hi)}
    fp          : fault profile dict with *_end values and optional sensor4 keys
    rng         : numpy Generator (seeded externally for reproducibility)
    sensor4_nr  : normal range (lo, hi) for the 4th sensor, or None

    Returns
    -------
    X : (STEPS, 6) or (STEPS, 8) float32 — feature matrix
        6-feature: [psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]
        8-feature: [psi, temp_f, vibration, sensor4, dpsi_dt, dtemp_dt, dvib_dt, ds4_dt]

    y : (STEPS,) float32 — Health Score:  1.0 (nominal) → 0.0 (destroyed)
        The health score is the INVERSE of the degradation fraction:
            health_score[i] = 1.0 - t_frac[i]
        so the model sees health = 1.0 when sensors are nominal and
        health = 0.0 when sensors are at the failure endpoint.
    """
    # ── Starting point: midpoint of nominal range ─────────────────────────────
    psi_start  = (nr["psi"][0]  + nr["psi"][1])  / 2.0
    temp_start = (nr["temp"][0] + nr["temp"][1]) / 2.0
    vib_start  = (nr["vib"][0]  + nr["vib"][1])  / 2.0

    # ── Exponential degradation curve ─────────────────────────────────────────
    # t_lin: uniform [0, 1] representing fractional position along the sequence.
    # t_frac: exponentially warped position — slow start, rapid finish.
    # At step 0: t_frac ≈ 0  → sensors nominal, health = 1.0
    # At step -1: t_frac = 1 → sensors at fault endpoint, health = 0.0
    t_lin  = np.linspace(0.0, 1.0, STEPS)
    t_frac = (np.exp(EXP_K * t_lin) - 1.0) / (np.exp(EXP_K) - 1.0)

    # ── Sensor signal: nominal → fault endpoint via exponential ramp ──────────
    psi_clean  = psi_start  + t_frac * (fp["psi_end"]  - psi_start)
    temp_clean = temp_start + t_frac * (fp["temp_end"] - temp_start)
    vib_clean  = vib_start  + t_frac * (fp["vib_end"]  - vib_start)

    # Physical minimums
    psi_clean  = np.maximum(psi_clean,  1.0)
    temp_clean = np.maximum(temp_clean, 1.0)
    vib_clean  = np.maximum(vib_clean,  0.01)

    # ── Add edge-calibrated noise ──────────────────────────────────────────────
    psi_seq  = psi_clean  + rng.uniform(
        -psi_clean  * PSI_NOISE_BASE,
         psi_clean  * PSI_NOISE_BASE)
    temp_seq = temp_clean + rng.uniform(
        -temp_clean * TEMP_NOISE_BASE,
         temp_clean * TEMP_NOISE_BASE)
    vib_seq  = np.maximum(
        0.05,
        vib_clean + rng.uniform(
            -vib_clean * VIB_NOISE_BASE,
             vib_clean * VIB_NOISE_BASE),
    )

    # ── Slope features: rate of change per minute ─────────────────────────────
    dpsi_dt  = _rolling_slopes(psi_seq,  SLOPE_WINDOW) * READINGS_PER_MIN
    dtemp_dt = _rolling_slopes(temp_seq, SLOPE_WINDOW) * READINGS_PER_MIN
    dvib_dt  = _rolling_slopes(vib_seq,  SLOPE_WINDOW) * READINGS_PER_MIN

    # ── Health Score label ─────────────────────────────────────────────────────
    # Directly derived from the degradation fraction so the model learns to map
    # sensor state → health score.  This is deliberately deterministic (no noise
    # on the label) — the sensor noise is the training challenge.
    health_score = (1.0 - t_frac).astype(np.float32)

    # ── 4th sensor (ESP: motor_amps, Mud Pump: spm) ───────────────────────────
    s4_key = ("amps_end" if "amps_end" in fp
               else ("spm_end" if "spm_end" in fp
               else None))
    has_s4 = s4_key is not None and sensor4_nr is not None

    if has_s4:
        s4_start = (sensor4_nr[0] + sensor4_nr[1]) / 2.0
        s4_end   = fp[s4_key]

        if fp.get("spm_erratic"):
            # Pulsation dampener failure: chaotic / erratic stroke rate.
            # Model the erratic behaviour as a widening random walk driven by
            # the exponential degradation fraction.
            s4_mid   = (sensor4_nr[0] + sensor4_nr[1]) / 2.0
            s4_range = sensor4_nr[1] - sensor4_nr[0]
            # Spread widens exponentially — nearly normal early, chaotic at end
            s4_clean = s4_mid + (t_frac - 0.5) * s4_range * 0.4
            s4_seq   = np.maximum(
                20.0,
                s4_clean + rng.uniform(
                    -s4_clean * SENSOR4_NOISE_BASE * 5 * (1.0 + t_frac * 4),
                     s4_clean * SENSOR4_NOISE_BASE * 5 * (1.0 + t_frac * 4)),
            )
        else:
            # Standard monotonic ramp along the exponential curve
            s4_clean = s4_start + t_frac * (s4_end - s4_start)
            s4_clean = np.maximum(s4_clean, 1.0)
            s4_seq   = np.maximum(
                1.0,
                s4_clean + rng.uniform(
                    -s4_clean * SENSOR4_NOISE_BASE,
                     s4_clean * SENSOR4_NOISE_BASE),
            )

        ds4_dt = _rolling_slopes(s4_seq, SLOPE_WINDOW) * READINGS_PER_MIN

        X = np.column_stack(
            [psi_seq, temp_seq, vib_seq, s4_seq,
             dpsi_dt, dtemp_dt, dvib_dt, ds4_dt]
        ).astype(np.float32)
    else:
        X = np.column_stack(
            [psi_seq, temp_seq, vib_seq, dpsi_dt, dtemp_dt, dvib_dt]
        ).astype(np.float32)

    return X, health_score


# ── Per-class training ─────────────────────────────────────────────────────────
def train_asset_class(
    asset_class: str,
    output_dir: Path,
    rng: np.random.Generator,
    n_samples: int,
    n_rounds: int,
) -> Path:
    """
    Train one XGBoost Health Score regressor for an asset class.

    Trains on all fault types for that class combined, with n_samples sequences
    per fault type.  The model learns the multivariate sensor → health_score
    mapping across all fault modes simultaneously.

    Parameters
    ----------
    asset_class : "esp" | "gas_lift" | "mud_pump" | "top_drive"
    output_dir  : directory to write {asset_class}_health.ubj
    rng         : numpy Generator (seeded)
    n_samples   : training sequences per fault type
    n_rounds    : XGBoost boosting rounds

    Returns
    -------
    Path to saved model file.
    """
    import xgboost as xgb  # local import so --help works without xgboost

    log.info("=" * 72)
    log.info(f"  Training Health Score model — {asset_class.upper()}")
    log.info(f"  Fault modes: {list(FAULT_PROFILES[asset_class].keys())}")
    log.info(f"  Samples per fault: {n_samples:,} × {STEPS} steps = "
             f"{n_samples * STEPS:,} rows/fault")
    log.info("=" * 72)

    nr        = NORMAL_RANGES[asset_class]
    faults    = FAULT_PROFILES[asset_class]
    sensor4_nr = SENSOR4_NORMAL.get(asset_class)  # None for gas_lift, top_drive

    # ── Feature names ─────────────────────────────────────────────────────────
    if asset_class == "esp":
        feature_names = ["psi", "temp_f", "vibration", "motor_amps",
                         "dpsi_dt", "dtemp_dt", "dvib_dt", "damps_dt"]
    elif asset_class == "mud_pump":
        feature_names = ["psi", "temp_f", "vibration", "spm",
                         "dpsi_dt", "dtemp_dt", "dvib_dt", "dspm_dt"]
    else:
        feature_names = ["psi", "temp_f", "vibration",
                         "dpsi_dt", "dtemp_dt", "dvib_dt"]

    # ── Generate training data ─────────────────────────────────────────────────
    all_X, all_y = [], []
    for fault_name, fp in faults.items():
        log.info(f"  ↳ {fault_name} — generating {n_samples:,} sequences …")
        t0 = time.time()
        for _ in range(n_samples):
            X_seq, y_seq = generate_sequence(nr, fp, rng, sensor4_nr)
            all_X.append(X_seq)
            all_y.append(y_seq)
        log.info(f"      done in {time.time()-t0:.1f}s  "
                 f"({X_seq.shape[1]} features, "
                 f"health range: {y_seq.min():.3f}–{y_seq.max():.3f})")

    X_train = np.vstack(all_X)
    y_train = np.concatenate(all_y)

    total_rows = X_train.shape[0]
    log.info(f"\n  Dataset: {total_rows:,} rows × {X_train.shape[1]} features")
    log.info(f"  Health Score range: {y_train.min():.4f} – {y_train.max():.4f}")
    log.info(f"  Features: {feature_names}")

    # ── Sanity check: health score must span 0.0 → 1.0 ───────────────────────
    if y_train.min() > 0.01:
        log.warning(f"  ⚠️  Minimum health score is {y_train.min():.4f} — "
                    "expected near 0.0.  Check t_frac endpoint.")
    if y_train.max() < 0.99:
        log.warning(f"  ⚠️  Maximum health score is {y_train.max():.4f} — "
                    "expected near 1.0.  Check t_frac start.")

    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)

    # ── XGBoost parameters ────────────────────────────────────────────────────
    # Learning rate 0.05 with 300 rounds gives a well-regularised health score
    # model without over-fitting to the exact exponential curve shape.
    # min_child_weight=5 prevents the tree from fitting noise near health=0 or 1.
    params = {
        "objective":        "reg:squarederror",
        "max_depth":        6,
        "learning_rate":    0.05,
        "subsample":        0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 5,
        "tree_method":      "hist",
        "eval_metric":      "rmse",
        "seed":             42,
        "verbosity":        0,
    }

    log.info(f"\n  Training XGBoost ({n_rounds} rounds, hist method) …")
    t_train = time.time()

    evals_result = {}
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=n_rounds,
        evals=[(dtrain, "train")],
        evals_result=evals_result,
        verbose_eval=max(1, n_rounds // 5),
    )

    train_time   = time.time() - t_train
    final_rmse   = evals_result["train"]["rmse"][-1]
    log.info(f"  Training complete in {train_time:.1f}s  |  "
             f"Final RMSE: {final_rmse:.5f}  (health score, 0.0–1.0 scale)")

    # ── Spot-check predictions ────────────────────────────────────────────────
    # Use the FIRST fault mode as the reference test sequence.
    # Check at 25%, 50%, 75% and 90% through the degradation timeline.
    # Expected results (exponential k=3.5):
    #   t=25%: health ≈ 0.97  (sensors barely moved)
    #   t=50%: health ≈ 0.89  (subtle degradation — ML starts detecting)
    #   t=75%: health ≈ 0.68  (slope features strengthening)
    #   t=90%: health ≈ 0.35  (SCADA threshold zone — most faults alarm ~0.15-0.30)
    fp_ref = list(faults.values())[0]
    X_test, y_test = generate_sequence(nr, fp_ref, rng, sensor4_nr)
    dtest  = xgb.DMatrix(X_test, feature_names=feature_names)
    preds  = model.predict(dtest)

    log.info(f"\n  Spot-check predictions (first fault mode: {list(faults.keys())[0]}):")
    log.info(f"  {'Position':<12} {'Pred Health':>12} {'True Health':>12} {'Error':>10}")
    log.info(f"  {'-'*50}")
    for q, label in ((0.25, "t=25%"), (0.50, "t=50%"),
                     (0.75, "t=75%"), (0.90, "t=90%"), (1.00, "t=100%")):
        idx = min(int(q * STEPS) - 1, STEPS - 1)
        err = abs(preds[idx] - y_test[idx])
        log.info(f"  {label:<12} {preds[idx]:>12.4f} {y_test[idx]:>12.4f} {err:>10.4f}")

    # Verify the critical thresholds are well-placed:
    # SCADA alarm zone (health ≈ 0.15–0.30): find where predicted health crosses 0.25
    for threshold in (0.30, 0.15, 0.05):
        crossings = np.where(preds < threshold)[0]
        if len(crossings):
            cross_pct = (crossings[0] / STEPS) * 100
            log.info(f"  Health < {threshold:.2f} first at step "
                     f"{crossings[0]}/{STEPS} ({cross_pct:.1f}% into sequence)")
        else:
            log.info(f"  Health never drops below {threshold:.2f} in test sequence ⚠️")

    # ── Save model ────────────────────────────────────────────────────────────
    out_path = output_dir / f"{asset_class}_health.ubj"
    model.save_model(str(out_path))
    size_kb = out_path.stat().st_size / 1024
    log.info(f"\n  ✅ Saved: {out_path}  ({size_kb:.0f} KB)")
    return out_path


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Phase 5.1 — Retrain XGBoost Health Score models for all asset classes.\n"
            "Produces health_score (1.0 → 0.0) with exponential degradation curve.\n"
            "Replaces Phase 4.1 RUL models (60min → 0min, linear)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--output-dir",
        default="gke/fault-trigger-ui/models",
        help="Directory to save .ubj model files",
    )
    parser.add_argument(
        "--n-samples", type=int, default=300,
        help="Training sequences per fault type per asset class (default: 300)",
    )
    parser.add_argument(
        "--rounds", type=int, default=300,
        help="XGBoost boosting rounds (default: 300)",
    )
    parser.add_argument(
        "--upload-gcs", action="store_true",
        help="Upload models to gs://gdc-pm-v2-models/health_models/ after training",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for reproducible training data",
    )
    parser.add_argument(
        "--asset-class", default=None,
        choices=["esp", "gas_lift", "mud_pump", "top_drive"],
        help="Train only one asset class (default: all four)",
    )
    args = parser.parse_args()

    # ── Dependency check ──────────────────────────────────────────────────────
    try:
        import xgboost as xgb
        log.info(f"XGBoost version: {xgb.__version__}")
    except ImportError:
        log.error("xgboost not installed — run: pip install xgboost")
        sys.exit(1)

    rng = np.random.default_rng(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    asset_classes = (
        [args.asset_class] if args.asset_class
        else ["esp", "gas_lift", "mud_pump", "top_drive"]
    )

    # ── Print degradation curve reference values ──────────────────────────────
    t_refs  = np.array([0.0, 0.25, 0.50, 0.75, 0.87, 0.94, 1.0])
    tf_refs = (np.exp(EXP_K * t_refs) - 1.0) / (np.exp(EXP_K) - 1.0)

    log.info(f"\n{'='*72}")
    log.info(f" GDC-PM Phase 5.1 — Health Score Model Retraining")
    log.info(f"{'='*72}")
    log.info(f" Asset classes  : {asset_classes}")
    log.info(f" Samples/fault  : {args.n_samples:,} × {STEPS} steps = "
             f"{args.n_samples * STEPS:,} rows/fault")
    log.info(f" Target         : health_score  1.0 (nominal) → 0.0 (destroyed)")
    log.info(f" Degradation    : exponential curve  k={EXP_K}")
    log.info(f" Noise          : edge-calibrated  psi±0.2%  temp±0.1%  vib±0.5%  s4±0.3%")
    log.info(f" Models         : single *_health.ubj per asset class (no V1/V2 split)")
    log.info(f" Output dir     : {output_dir.resolve()}")
    log.info(f"\n Exponential curve reference:")
    log.info(f"   {'Timeline':>10}  {'t_frac':>8}  {'health':>8}  Notes")
    log.info(f"   {'-'*55}")
    notes = ["start",
             "t=25%: subtle — ML alert zone starts",
             "t=50%: slope features strengthening",
             "t=75%: late incipient",
             "t=87%: SCADA alarm fires (~health 0.30)",
             "t=94%: PNR — irreversible damage (~health 0.10)",
             "t=100%: destruction — health = 0.0"]
    for t, tf, note in zip(t_refs, tf_refs, notes):
        log.info(f"   {t*100:>9.0f}%  {tf:>8.4f}  {1-tf:>8.4f}  {note}")
    log.info(f"{'='*72}\n")

    t_total = time.time()
    trained = []

    for ac in asset_classes:
        p = train_asset_class(ac, output_dir, rng, args.n_samples, args.rounds)
        trained.append(p)

    log.info(f"\n{'='*72}")
    log.info(f" All models trained in {time.time()-t_total:.0f}s")
    log.info(f"{'='*72}")
    for p in trained:
        size_kb = p.stat().st_size / 1024
        log.info(f"  {p}  ({size_kb:.0f} KB)")

    # ── Optional GCS upload ───────────────────────────────────────────────────
    if args.upload_gcs:
        gcs_prefix = "gs://gdc-pm-v2-models/health_models"
        log.info(f"\nUploading to {gcs_prefix}/…")
        for p in trained:
            dest = f"{gcs_prefix}/{p.name}"
            r = subprocess.run(
                ["gsutil", "cp", str(p), dest],
                capture_output=True, text=True,
            )
            if r.returncode == 0:
                log.info(f"  ✅ {dest}")
            else:
                log.error(f"  ❌ Upload failed: {r.stderr.strip()}")

    log.info("\n─── Phase 5.1 complete — next steps ────────────────────────────────")
    log.info("  1. Verify model outputs (health scores must span 0.0–1.0 cleanly)")
    log.info("  2. Phase 5.2: Update app.py to load *_health.ubj + add FAULT_PHYSICS")
    log.info("  3. Phase 5.3: Rebuild index.html (Copilot Workspace + Intervention Slider)")
    log.info("  4. Phase 5.4: Docker rebuild + kubectl rollout restart")
    log.info("─────────────────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
