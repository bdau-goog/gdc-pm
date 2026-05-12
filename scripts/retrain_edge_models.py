#!/usr/bin/env python3
"""
scripts/retrain_edge_models.py

Phase 4.1 — Extend V1 and V2 XGBoost RUL models for ESP and Mud Pump to use
an 8-feature vector that includes the 4th sensor channel:
  ESP:      [psi, temp_f, vibration, motor_amps, dpsi_dt, dtemp_dt, dvib_dt, damps_dt]
  Mud Pump: [psi, temp_f, vibration, spm,        dpsi_dt, dtemp_dt, dvib_dt, dspm_dt ]

Gas Lift and Top Drive remain at 6 features (unchanged):
  Gas Lift / Top Drive: [psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]

WHY TWO MODEL VERSIONS (V1 and V2):

  V1 (*_rul.ubj):  Trained with CLOUD noise profile (noise_scale=5× edge).
                   Simulates a model trained on 5-minute SCADA interval data that is
                   then served against 5-second edge telemetry — training-serving skew.
                   Produces intentionally high variance for the MLOps drift demo.
                   Noise profile: psi×0.01, temp×0.005, vib×0.025, sensor4×0.015

  V2 (*_rul_v2.ubj): Trained with EDGE noise profile (noise_scale=1×).
                   Matches the exact noise characteristics of the edge simulator.
                   Produces stable, calibrated predictions.
                   Noise profile: psi×0.002, temp×0.001, vib×0.005, sensor4×0.003

V1 for Gas Lift and Top Drive are NOT updated (they remain 6-feature; app.py
handles them with the 6-feature code path regardless of model version).

OUTPUT:
  gke/fault-trigger-ui/models/esp_rul.ubj          — V1 drifted,   8-feature
  gke/fault-trigger-ui/models/esp_rul_v2.ubj       — V2 calibrated, 8-feature
  gke/fault-trigger-ui/models/mud_pump_rul.ubj     — V1 drifted,   8-feature
  gke/fault-trigger-ui/models/mud_pump_rul_v2.ubj  — V2 calibrated, 8-feature
  gke/fault-trigger-ui/models/gas_lift_rul_v2.ubj  — V2 calibrated, 6-feature
  gke/fault-trigger-ui/models/top_drive_rul_v2.ubj — V2 calibrated, 6-feature

USAGE:
  python scripts/retrain_edge_models.py
  python scripts/retrain_edge_models.py --asset-class esp --version v2
  python scripts/retrain_edge_models.py --n-samples 500 --rounds 400
  python scripts/retrain_edge_models.py --upload-gcs
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
log = logging.getLogger("retrain_v2")

# ── Asset definitions — must match app.py exactly ─────────────────────────────
NORMAL_RANGES = {
    "esp":       {"psi": (1200, 1600), "temp": (180, 220), "vib": (0.8, 2.0)},
    "gas_lift":  {"psi": (940, 1060),  "temp": (140, 178), "vib": (1.0, 2.5)},
    "mud_pump":  {"psi": (2550, 3150), "temp": (90, 120),  "vib": (2.5, 4.5)},
    "top_drive": {"psi": (2840, 3160), "temp": (130, 165), "vib": (1.8, 3.8)},
}

# ── 4th-sensor normal ranges — must match SENSOR4_CONFIG in app.py ────────────
SENSOR4_NORMAL = {
    "esp":      (60.0, 90.0),    # motor_amps nominal range (A)
    "mud_pump": (75.0, 100.0),   # spm nominal range (SPM)
}

# ── Fault endpoint values ─────────────────────────────────────────────────────
# psi/temp/vib_end: low end of fault range (approach to failure, not full critical).
# amps_end / spm_end: midpoint of the fault-level range for that sensor.
# spm_erratic: True for pulsation_dampener_failure (random walk, not linear ramp).
FAULT_PROFILES = {
    "esp": {
        "gas_lock": {
            "psi_end": 875,  "temp_end": 195, "vib_end": 3.5,
            "amps_end": 32.5,   # pump unloads sharply as GVF rises (range 20–45 A)
        },
        "sand_ingress": {
            "psi_end": 1280, "temp_end": 200, "vib_end": 4.5,
            "amps_end": 55.0,   # declining as impeller stages erode (range 45–65 A)
        },
        "motor_overheat": {
            "psi_end": 1300, "temp_end": 265, "vib_end": 2.5,
            "amps_end": 96.5,   # overcurrent driving heat buildup (range 88–105 A)
        },
    },
    "gas_lift": {
        "valve_failure":   {"psi_end": 450, "temp_end": 165, "vib_end": 8.0},
        "thermal_runaway": {"psi_end": 940, "temp_end": 210, "vib_end": 3.0},
        "bearing_wear":    {"psi_end": 945, "temp_end": 163, "vib_end": 7.5},
    },
    "mud_pump": {
        "pulsation_dampener_failure": {
            "psi_end": 3800, "temp_end": 120, "vib_end": 15.0,
            "spm_end": 95.0, "spm_erratic": True,  # chaotic (range 55–135 SPM)
        },
        "valve_washout": {
            "psi_end": 1800, "temp_end": 115, "vib_end": 5.0,
            "spm_end": 107.5,   # driller compensates for efficiency loss (range 95–120 SPM)
        },
        "piston_seal_wear": {
            "psi_end": 1900, "temp_end": 155, "vib_end": 5.5,
            "spm_end": 100.0,   # moderate compensation over days (range 90–110 SPM)
        },
    },
    "top_drive": {
        "gearbox_bearing_spalling": {"psi_end": 2850, "temp_end": 175, "vib_end": 11.0},
        "hydraulic_leak":           {"psi_end": 1700, "temp_end": 158, "vib_end": 3.5},
    },
}

# ── Noise profiles ─────────────────────────────────────────────────────────────
# noise_scale=1.0 → V2 edge-calibrated profile (matches 5-second edge simulator)
# noise_scale=5.0 → V1 cloud-drifted profile  (simulates 5-minute SCADA data)
#
# Base multipliers (V2, scale=1.0):
#   psi:     ± psi × 0.002
#   temp:    ± temp × 0.001
#   vib:     ± vib × 0.005
#   sensor4: ± s4  × 0.003
#
# V1 multiplier: base × 5.0 = psi×0.01, temp×0.005, vib×0.025, sensor4×0.015
PSI_NOISE_BASE    = 0.002
TEMP_NOISE_BASE   = 0.001
VIB_NOISE_BASE    = 0.005
SENSOR4_NOISE_BASE = 0.003

# ── Hyper-parameters ──────────────────────────────────────────────────────────
STEPS            = 720      # 720 steps × 5s = 60 minutes of degradation
SLOPE_WINDOW     = 60       # 60-reading (5-minute) window for slope features
READINGS_PER_MIN = 12.0     # 60s ÷ 5s = 12 readings per minute


# ── Vectorised rolling slope ──────────────────────────────────────────────────
def _rolling_slopes(arr: np.ndarray, window: int) -> np.ndarray:
    """
    Compute the linear regression slope over a causal rolling window.

    Returns slopes in (arr-units / reading).  Caller converts to per-minute
    by multiplying by READINGS_PER_MIN.

    Uses the closed-form OLS slope:
        β = cov(t, y) / var(t)
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


# ── Sequence generator ────────────────────────────────────────────────────────
def generate_sequence(
    nr: dict,
    fp: dict,
    rng: np.random.Generator,
    noise_scale: float = 1.0,
    sensor4_nr: tuple | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate one 720-step degradation sequence.

    Parameters
    ----------
    nr          : normal ranges dict {"psi": (lo,hi), "temp": (lo,hi), "vib": (lo,hi)}
    fp          : fault profile dict with *_end values and optional sensor4 keys
    rng         : numpy Generator (seeded)
    noise_scale : 1.0 for V2 edge-calibrated, 5.0 for V1 cloud-drifted
    sensor4_nr  : normal range tuple (lo, hi) for the 4th sensor, or None

    Returns
    -------
    X : (720, 6) or (720, 8) float32 — feature matrix
        6-feature: [psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]
        8-feature: [psi, temp_f, vibration, sensor4, dpsi_dt, dtemp_dt, dvib_dt, ds4_dt]
    y : (720,) float32 — RUL in minutes (60.0 → 0.0)
    """
    psi_start  = (nr["psi"][0]  + nr["psi"][1])  / 2.0
    temp_start = (nr["temp"][0] + nr["temp"][1]) / 2.0
    vib_start  = (nr["vib"][0]  + nr["vib"][1])  / 2.0

    t_frac = np.linspace(1 / STEPS, 1.0, STEPS)   # avoids exactly 0

    psi_clean  = psi_start  + t_frac * (fp["psi_end"]  - psi_start)
    temp_clean = temp_start + t_frac * (fp["temp_end"] - temp_start)
    vib_clean  = vib_start  + t_frac * (fp["vib_end"]  - vib_start)

    # Clamp to physical minimums
    psi_clean  = np.maximum(psi_clean,  1.0)
    temp_clean = np.maximum(temp_clean, 1.0)
    vib_clean  = np.maximum(vib_clean,  0.01)

    ns = noise_scale
    psi_seq  = psi_clean  + rng.uniform(-psi_clean  * PSI_NOISE_BASE  * ns,
                                          psi_clean  * PSI_NOISE_BASE  * ns)
    temp_seq = temp_clean + rng.uniform(-temp_clean * TEMP_NOISE_BASE * ns,
                                          temp_clean * TEMP_NOISE_BASE * ns)
    vib_seq  = np.maximum(
        0.05,
        vib_clean + rng.uniform(-vib_clean * VIB_NOISE_BASE * ns,
                                  vib_clean * VIB_NOISE_BASE * ns),
    )

    # Slope features — per-minute
    dpsi_dt  = _rolling_slopes(psi_seq,  SLOPE_WINDOW) * READINGS_PER_MIN
    dtemp_dt = _rolling_slopes(temp_seq, SLOPE_WINDOW) * READINGS_PER_MIN
    dvib_dt  = _rolling_slopes(vib_seq,  SLOPE_WINDOW) * READINGS_PER_MIN

    # RUL label: step i → (STEPS-1-i) × 5s ÷ 60 = minutes
    rul_min = np.arange(STEPS - 1, -1, -1, dtype=np.float32) * 5.0 / 60.0

    # ── 4th sensor (ESP: motor_amps; Mud Pump: spm) ───────────────────────────
    s4_key    = "amps_end" if "amps_end" in fp else ("spm_end" if "spm_end" in fp else None)
    has_s4    = s4_key is not None and sensor4_nr is not None

    if has_s4:
        s4_start = (sensor4_nr[0] + sensor4_nr[1]) / 2.0
        s4_end   = fp[s4_key]

        if fp.get("spm_erratic"):
            # Pulsation dampener failure: chaotic stroke rate — random walk around midpoint
            s4_mid   = (sensor4_nr[0] + sensor4_nr[1]) / 2.0
            s4_range = (sensor4_nr[1] - sensor4_nr[0])
            # Progressive widening of the random walk as fault develops
            s4_clean = s4_mid + (t_frac - 0.5) * s4_range * 0.4
            s4_seq   = np.maximum(
                20.0,
                s4_clean + rng.uniform(-s4_clean * SENSOR4_NOISE_BASE * ns * 5,
                                         s4_clean * SENSOR4_NOISE_BASE * ns * 5),
            )
        else:
            s4_clean = s4_start + t_frac * (s4_end - s4_start)
            s4_clean = np.maximum(s4_clean, 1.0)
            s4_seq   = np.maximum(
                1.0,
                s4_clean + rng.uniform(-s4_clean * SENSOR4_NOISE_BASE * ns,
                                         s4_clean * SENSOR4_NOISE_BASE * ns),
            )

        ds4_dt = _rolling_slopes(s4_seq, SLOPE_WINDOW) * READINGS_PER_MIN

        X = np.column_stack(
            [psi_seq, temp_seq, vib_seq, s4_seq, dpsi_dt, dtemp_dt, dvib_dt, ds4_dt]
        ).astype(np.float32)
    else:
        X = np.column_stack(
            [psi_seq, temp_seq, vib_seq, dpsi_dt, dtemp_dt, dvib_dt]
        ).astype(np.float32)

    return X, rul_min


# ── Per-class training ────────────────────────────────────────────────────────
def train_asset_class(
    asset_class: str,
    output_dir: Path,
    rng: np.random.Generator,
    n_samples: int,
    n_rounds: int,
    noise_scale: float = 1.0,
    suffix: str = "v2",
) -> Path:
    """
    Train one XGBoost RUL regressor.

    Parameters
    ----------
    asset_class : "esp" | "gas_lift" | "mud_pump" | "top_drive"
    noise_scale : 1.0 = V2 edge-calibrated, 5.0 = V1 cloud-drifted
    suffix      : "v2"  → saves as {asset_class}_rul_v2.ubj
                  "v1"  → saves as {asset_class}_rul.ubj
    """
    import xgboost as xgb  # local import so the argparse help works without xgb

    version_tag = "V2 (edge-calibrated)" if suffix == "v2" else "V1 (cloud-drifted)"
    log.info("=" * 68)
    log.info(f"  Training {version_tag} RUL model — {asset_class.upper()}")
    log.info(f"  noise_scale={noise_scale:.1f}  output={suffix}")
    log.info("=" * 68)

    nr     = NORMAL_RANGES[asset_class]
    faults = FAULT_PROFILES[asset_class]

    # Determine 4th sensor config
    sensor4_nr = SENSOR4_NORMAL.get(asset_class)   # None for gas_lift, top_drive

    if asset_class == "esp":
        feature_names = ["psi", "temp_f", "vibration", "motor_amps",
                         "dpsi_dt", "dtemp_dt", "dvib_dt", "damps_dt"]
    elif asset_class == "mud_pump":
        feature_names = ["psi", "temp_f", "vibration", "spm",
                         "dpsi_dt", "dtemp_dt", "dvib_dt", "dspm_dt"]
    else:
        feature_names = ["psi", "temp_f", "vibration", "dpsi_dt", "dtemp_dt", "dvib_dt"]

    all_X, all_y = [], []
    for fault_name, fp in faults.items():
        log.info(f"  ↳ Generating {n_samples:,} × {STEPS}-step sequences: {fault_name}")
        t0 = time.time()
        for _ in range(n_samples):
            X_seq, y_seq = generate_sequence(nr, fp, rng, noise_scale, sensor4_nr)
            all_X.append(X_seq)
            all_y.append(y_seq)
        log.info(f"      done in {time.time()-t0:.1f}s  ({X_seq.shape[1]} features)")

    X_train = np.vstack(all_X)
    y_train = np.concatenate(all_y)

    total_rows = X_train.shape[0]
    log.info(f"\n  Dataset: {total_rows:,} rows × {X_train.shape[1]} features")
    log.info(f"  RUL range: {y_train.min():.2f} – {y_train.max():.2f} minutes")
    log.info(f"  Feature names: {feature_names}")

    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)

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

    log.info(f"\n  Training XGBoost ({n_rounds} rounds, hist method)…")
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

    train_time = time.time() - t_train
    final_rmse = evals_result["train"]["rmse"][-1]
    log.info(f"  Training complete in {train_time:.1f}s  |  Final RMSE: {final_rmse:.3f} min")

    # Spot-check predictions at 25%, 50%, 75% through a fresh test sequence
    fp_ref = list(faults.values())[0]
    X_test, y_test = generate_sequence(nr, fp_ref, rng, noise_scale, sensor4_nr)
    preds = model.predict(xgb.DMatrix(X_test, feature_names=feature_names))
    for q in (0.25, 0.50, 0.75):
        idx = int(q * STEPS)
        log.info(f"  Spot-check at t={q:.0%}: pred={preds[idx]:.1f}m  actual={y_test[idx]:.1f}m")

    # Save model — suffix determines V1 vs V2 filename
    if suffix == "v2":
        out_path = output_dir / f"{asset_class}_rul_v2.ubj"
    else:
        out_path = output_dir / f"{asset_class}_rul.ubj"

    model.save_model(str(out_path))
    size_kb = out_path.stat().st_size / 1024
    log.info(f"\n  ✅ Saved: {out_path}  ({size_kb:.0f} KB)")
    return out_path


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retrain XGBoost RUL models (Phase 4.1 — 8-feature ESP and Mud Pump)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output-dir",
        default="gke/fault-trigger-ui/models",
        help="Directory to save .ubj model files",
    )
    parser.add_argument(
        "--n-samples", type=int, default=300,
        help="Training sequences per fault type per asset class",
    )
    parser.add_argument(
        "--rounds", type=int, default=300,
        help="XGBoost boosting rounds",
    )
    parser.add_argument(
        "--upload-gcs", action="store_true",
        help="Upload models to gs://gdc-pm-v2-models/rul_models_v2/ after training",
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
    parser.add_argument(
        "--version", default=None,
        choices=["v1", "v2"],
        help="Train only V1 or only V2 (default: both V1 and V2 for ESP/MudPump, V2-only for others)",
    )
    args = parser.parse_args()

    # Check xgboost is available
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

    log.info(f"\n{'='*68}")
    log.info(f" GDC-PM Phase 4.1 — RUL Model Retraining")
    log.info(f"{'='*68}")
    log.info(f" Asset classes : {asset_classes}")
    log.info(f" Samples/fault : {args.n_samples:,} × {STEPS} steps = {args.n_samples*STEPS:,} rows/fault")
    log.info(f" 4th sensor    : ESP → motor_amps (8 features), Mud Pump → spm (8 features)")
    log.info(f"                 Gas Lift, Top Drive unchanged (6 features)")
    log.info(f" V2 noise      : psi±0.2%  temp±0.1%  vib±0.5%  s4±0.3%  (edge-calibrated)")
    log.info(f" V1 noise      : psi±1.0%  temp±0.5%  vib±2.5%  s4±1.5%  (cloud-drifted, MLOps demo)")
    log.info(f" RUL label     : minutes (0 – 60 min)")
    log.info(f" Output dir    : {output_dir.resolve()}")
    log.info(f"{'='*68}\n")

    t_total = time.time()
    trained = []

    for ac in asset_classes:
        # ESP and Mud Pump: train V1 and V2 (unless --version restricts it)
        # Gas Lift and Top Drive: train V2 only (V1 files remain 6-feature, unchanged)
        needs_v1 = ac in ("esp", "mud_pump")

        train_v2 = args.version in (None, "v2")
        train_v1 = needs_v1 and args.version in (None, "v1")

        if train_v2:
            p = train_asset_class(ac, output_dir, rng, args.n_samples, args.rounds,
                                  noise_scale=1.0, suffix="v2")
            trained.append(p)

        if train_v1:
            # Use a fresh RNG with an offset seed for V1 so training data differs
            rng_v1 = np.random.default_rng(args.seed + 1000)
            p = train_asset_class(ac, output_dir, rng_v1, args.n_samples, args.rounds,
                                  noise_scale=5.0, suffix="v1")
            trained.append(p)

    log.info(f"\n{'='*68}")
    log.info(f" All models trained in {time.time()-t_total:.0f}s")
    log.info(f"{'='*68}")
    for p in trained:
        log.info(f"  {p}")

    if args.upload_gcs:
        gcs_prefix = "gs://gdc-pm-v2-models/rul_models_v2"
        log.info(f"\nUploading to {gcs_prefix}/…")
        for p in trained:
            dest = f"{gcs_prefix}/{p.name}"
            r = subprocess.run(["gsutil", "cp", str(p), dest],
                               capture_output=True, text=True)
            if r.returncode == 0:
                log.info(f"  ✅ {dest}")
            else:
                log.error(f"  ❌ Upload failed: {r.stderr.strip()}")

    log.info("\n─── Next steps ─────────────────────────────────────────────────────")
    log.info("  1. Models saved to gke/fault-trigger-ui/models/ (staged for container rebuild)")
    log.info("  2. Rebuild fault-trigger-ui Docker image to embed updated model files")
    log.info("  3. kubectl rollout restart deployment/fault-trigger-ui -n gdc-pm")
    log.info("  4. MLOps demo: V1 shows higher RUL variance (cloud-noise drift)")
    log.info("                 V2 stabilises after ☁ Retrain via Vertex AI button")
    log.info("────────────────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
