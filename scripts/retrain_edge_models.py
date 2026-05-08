#!/usr/bin/env python3
"""
scripts/retrain_edge_models.py

Phase 3 Task 2 — Generate V2 XGBoost RUL training data that accurately
reproduces the 5-second noise profile of the edge simulator and retrain
the RUL regressors for all four asset classes.

WHY V2 IS NEEDED (Training-Serving Skew):
  V1 models were trained on perfectly clean 5-minute interval synthetic data.
  The edge simulator publishes at 5-second intervals with Gaussian noise matching:
      psi  ± psi * 0.002   (~±0.2%)
      temp ± temp * 0.001  (~±0.1%)
      vib  ± vib * 0.005   (~±0.5%)
  When V1 features (slope over a mixed/noisy window) are fed to a V1 model that
  expected clean 5-minute differences, the predictions are high-variance and
  uncalibrated. V2 closes this gap by training on the exact same noise profile.

OUTPUT:
  gke/fault-trigger-ui/models/{asset_class}_rul_v2.ubj   (embedded in container)
  gs://gdc-pm-v2-models/rul_models_v2/{asset_class}_rul_v2.ubj  (with --upload-gcs)

USAGE:
  python scripts/retrain_edge_models.py
  python scripts/retrain_edge_models.py --upload-gcs
  python scripts/retrain_edge_models.py --n-samples 500 --rounds 400
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

# Fault endpoint values — use the LOW end of psi/temp/vib_range as the degraded
# target (the ramp heads toward the onset of failure, not full critical threshold).
# This exactly matches _run_degrade_thread()'s target: profile["psi_range"][0]
FAULT_PROFILES = {
    "esp": {
        "gas_lock":       {"psi_end": 875,  "temp_end": 195, "vib_end": 3.5},
        "sand_ingress":   {"psi_end": 1280, "temp_end": 200, "vib_end": 4.5},
        "motor_overheat": {"psi_end": 1300, "temp_end": 265, "vib_end": 2.5},
    },
    "gas_lift": {
        "valve_failure":   {"psi_end": 450, "temp_end": 165, "vib_end": 8.0},
        "thermal_runaway": {"psi_end": 940, "temp_end": 210, "vib_end": 3.0},
        "bearing_wear":    {"psi_end": 945, "temp_end": 163, "vib_end": 7.5},
    },
    "mud_pump": {
        "pulsation_dampener_failure": {"psi_end": 3800, "temp_end": 120, "vib_end": 15.0},
        "valve_washout":              {"psi_end": 1800, "temp_end": 115, "vib_end": 5.0},
        "piston_seal_wear":           {"psi_end": 1900, "temp_end": 155, "vib_end": 5.5},
    },
    "top_drive": {
        "gearbox_bearing_spalling": {"psi_end": 2850, "temp_end": 175, "vib_end": 11.0},
        "hydraulic_leak":           {"psi_end": 1700, "temp_end": 158, "vib_end": 3.5},
    },
}

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
    nr: dict, fp: dict, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate one 720-step degradation sequence with 5-second noise matching
    the gradual-degrade thread in app.py:
        psi  ± psi  × 0.002
        temp ± temp × 0.001
        vib  ± vib  × 0.005

    Returns
    -------
    X : (720, 6) float32 — [psi, temp_f, vibration, dpsi_dt, dtemp_dt, dvib_dt]
    y : (720,)  float32 — RUL in minutes, from ~60.0 down to 0.0
    """
    psi_start  = (nr["psi"][0]  + nr["psi"][1])  / 2.0
    temp_start = (nr["temp"][0] + nr["temp"][1]) / 2.0
    vib_start  = (nr["vib"][0]  + nr["vib"][1])  / 2.0

    psi_end  = fp["psi_end"]
    temp_end = fp["temp_end"]
    vib_end  = fp["vib_end"]

    t_frac = np.linspace(1 / STEPS, 1.0, STEPS)   # avoids exactly 0

    psi_clean  = psi_start  + t_frac * (psi_end  - psi_start)
    temp_clean = temp_start + t_frac * (temp_end - temp_start)
    vib_clean  = vib_start  + t_frac * (vib_end  - vib_start)

    # Clamp to physical minimums
    psi_clean  = np.maximum(psi_clean,  1.0)
    temp_clean = np.maximum(temp_clean, 1.0)
    vib_clean  = np.maximum(vib_clean,  0.01)

    # Noise profile — identical to _run_degrade_thread()
    psi_seq  = psi_clean  + rng.uniform(-psi_clean  * 0.002, psi_clean  * 0.002)
    temp_seq = temp_clean + rng.uniform(-temp_clean * 0.001, temp_clean * 0.001)
    vib_seq  = np.maximum(
        0.05,
        vib_clean + rng.uniform(-vib_clean * 0.005, vib_clean * 0.005),
    )

    # Slope features — per-minute (multiply by READINGS_PER_MIN)
    dpsi_dt  = _rolling_slopes(psi_seq,  SLOPE_WINDOW) * READINGS_PER_MIN
    dtemp_dt = _rolling_slopes(temp_seq, SLOPE_WINDOW) * READINGS_PER_MIN
    dvib_dt  = _rolling_slopes(vib_seq,  SLOPE_WINDOW) * READINGS_PER_MIN

    # RUL labels: step i has (STEPS - 1 - i) steps remaining × 5s ÷ 60 = minutes
    rul_min = np.arange(STEPS - 1, -1, -1, dtype=np.float32) * 5.0 / 60.0

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
) -> Path:
    import xgboost as xgb  # local import so the argparse help works without xgb

    log.info("=" * 62)
    log.info(f"  Training V2 RUL model — {asset_class.upper()}")
    log.info("=" * 62)

    nr     = NORMAL_RANGES[asset_class]
    faults = FAULT_PROFILES[asset_class]

    all_X, all_y = [], []
    for fault_name, fp in faults.items():
        log.info(f"  ↳ Generating {n_samples:,} × {STEPS}-step sequences: {fault_name}")
        t0 = time.time()
        for _ in range(n_samples):
            X_seq, y_seq = generate_sequence(nr, fp, rng)
            all_X.append(X_seq)
            all_y.append(y_seq)
        log.info(f"      done in {time.time()-t0:.1f}s")

    X_train = np.vstack(all_X)
    y_train = np.concatenate(all_y)

    total_rows = X_train.shape[0]
    log.info(f"\n  Dataset: {total_rows:,} rows × {X_train.shape[1]} features")
    log.info(f"  RUL range: {y_train.min():.2f} – {y_train.max():.2f} minutes")

    dtrain = xgb.DMatrix(
        X_train,
        label=y_train,
        feature_names=["psi", "temp_f", "vibration", "dpsi_dt", "dtemp_dt", "dvib_dt"],
    )

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

    # Spot-check: prediction at 25%, 50%, 75% through a fresh test sequence
    fp_ref = list(faults.values())[0]
    X_test, y_test = generate_sequence(nr, fp_ref, rng)
    preds = model.predict(xgb.DMatrix(X_test, feature_names=["psi", "temp_f", "vibration", "dpsi_dt", "dtemp_dt", "dvib_dt"]))
    for q in (0.25, 0.50, 0.75):
        idx = int(q * STEPS)
        log.info(f"  Spot-check at t={q:.0%}: pred={preds[idx]:.1f}m  actual={y_test[idx]:.1f}m")

    # Save — suffix _v2 to avoid overwriting V1 models
    out_path = output_dir / f"{asset_class}_rul_v2.ubj"
    model.save_model(str(out_path))
    size_kb = out_path.stat().st_size / 1024
    log.info(f"\n  ✅ Saved: {out_path}  ({size_kb:.0f} KB)")
    return out_path


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retrain V2 XGBoost RUL models on 5-second edge noise profile data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--output-dir",
        default="gke/fault-trigger-ui/models",
        help="Directory to save .ubj model files (also embedded into container at build time)",
    )
    parser.add_argument(
        "--n-samples", type=int, default=300,
        help="Training sequences per fault type per asset class (300×720 rows each)",
    )
    parser.add_argument(
        "--rounds", type=int, default=300,
        help="XGBoost boosting rounds",
    )
    parser.add_argument(
        "--upload-gcs", action="store_true",
        help="Upload V2 models to gs://gdc-pm-v2-models/rul_models_v2/ after training",
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

    log.info(f"\n{'='*62}")
    log.info(f" GDC-PM Phase 3 — V2 RUL Model Retraining")
    log.info(f"{'='*62}")
    log.info(f" Asset classes : {asset_classes}")
    log.info(f" Samples/fault : {args.n_samples:,} × {STEPS} steps = {args.n_samples*STEPS:,} rows/fault")
    log.info(f" Noise profile : psi±0.2%  temp±0.1%  vib±0.5%  (matches edge simulator)")
    log.info(f" RUL label     : minutes (0 – 60 min)")
    log.info(f" Output dir    : {output_dir.resolve()}")
    log.info(f"{'='*62}\n")

    t_total = time.time()
    trained = []
    for ac in asset_classes:
        p = train_asset_class(ac, output_dir, rng, args.n_samples, args.rounds)
        trained.append(p)

    log.info(f"\n{'='*62}")
    log.info(f" All V2 models trained in {time.time()-t_total:.0f}s")
    log.info(f"{'='*62}")
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

    log.info("\n─── Next steps ─────────────────────────────────────────────")
    log.info("  1. V2 models saved to gke/fault-trigger-ui/models/ (staged for container)")
    log.info("  2. app.py Task 3 will load both V1 (*_rul.ubj) and V2 (*_rul_v2.ubj)")
    log.info("  3. Rebuild fault-trigger-ui image after Task 3 to embed V2 models")
    log.info("  4. Demo flow: inject fault → show V1 variance → retrain → V2 stabilises")
    log.info("─────────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
