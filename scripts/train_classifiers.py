#!/usr/bin/env python3
"""
scripts/train_classifiers.py  (Session U — trajectory-based rewrite)

Train XGBoost fault classifiers for all 4 O&G asset classes.
Outputs .ubj files for LOCAL_MODELS_DIR in inference-api.

═══════════════════════════════════════════════════════════════
CRITICAL CHANGE vs Session S (snapshot approach — DO NOT REVERT)
═══════════════════════════════════════════════════════════════
Session S used static snapshot sampling:
  - Drew (psi, temp, vib, amps, dpsi_dt, ...) independently from per-class ranges
  - gas_lock trained on PSI 350–800 (invented, NOT the live injection range 875–1100)
  - slug_flow trained on vib 3–8 mm/s (wrong, barely above normal 0.8–2.0)
  - Verification was circular: accuracy measured against the same invented distribution

Session U uses trajectory-based simulation:
  - For each fault class, simulate N degradation ramps from nominal → fault endpoint
  - Each ramp uses the SAME exponential formula as _run_degrade_thread in app.py
      t = ((i+1)/steps)^k   where k ~ Uniform(3.0, 4.0)
  - Slope features computed via first-last difference over a 12-reading window,
    matching the exact logic in event-processor/processor.py:get_slopes()
  - All distributions sourced from fault_signatures.py which mirrors FAULT_PROFILES
    in app.py — NEVER invented

This ensures the training distribution matches the inference distribution exactly.

USAGE
─────
  python scripts/train_classifiers.py
  python scripts/train_classifiers.py --asset-class esp --output-dir gke/inference-api/models
  python scripts/train_classifiers.py --n-trajectories 600 --n-normal 6000 --rounds 300

References
──────────
  - MODEL_FOUNDATIONS.md §5A — training specification
  - gke/shared/fault_signatures.py — canonical fault signature table
  - gke/fault-trigger-ui/app.py:_run_degrade_thread — ramp formula source
  - gke/event-processor/processor.py:get_slopes() — slope logic source
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix, precision_score
from sklearn.model_selection import train_test_split

# ── Import canonical fault signatures ─────────────────────────────────────────
# fault_signatures.py lives in gke/shared/ — add repo root to sys.path so the
# import works regardless of where the script is invoked from.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
from gke.shared.fault_signatures import (
    ESP_FAULT_SIGNATURES,
    ESP_NORMAL_RANGES,
    ESP_NOMINAL,
    ESP_LABEL_MAP,
    ESP_FEATURE_NAMES,
    TRAINING_PARAMS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("train_classifiers")

# ── Slope computation ──────────────────────────────────────────────────────────
# MUST match event-processor/processor.py:get_slopes() exactly.
# Simple first-last difference over the last WINDOW readings.
# Returns (dpsi_dt, dtemp_dt, dvib_dt, damps_dt) per reading.
SLOPE_WINDOW = TRAINING_PARAMS["slope_window"]   # 12 readings × 5s = 60s


def _compute_slopes(history: list, window: int = SLOPE_WINDOW):
    """
    Compute slope features from sensor history buffer.
    history: list of [psi, temp, vib, amps] in chronological order.
    Returns: (dpsi_dt, dtemp_dt, dvib_dt, damps_dt) as per-reading deltas.
    Matches processor.py:get_slopes() first-last difference over window.
    """
    n = min(len(history), window)
    if n < 2:
        return 0.0, 0.0, 0.0, 0.0
    old = history[-n]
    new = history[-1]
    # Divide by n (number of steps, each ~5s) to get per-step slope.
    # Multiply by 12 (readings/min) to convert to per-minute — matches
    # the `READINGS_PER_MIN = 12.0` scaling in app.py's forecast endpoint.
    scale = 12.0 / n
    return (
        (new[0] - old[0]) * scale,   # dpsi_dt  (PSI/min)
        (new[1] - old[1]) * scale,   # dtemp_dt (°F/min)
        (new[2] - old[2]) * scale,   # dvib_dt  (mm/s/min)
        (new[3] - old[3]) * scale,   # damps_dt (A/min)
    )


# ── Non-ESP 3-feature profiles ─────────────────────────────────────────────────
# Infrastructure completeness. Not demo-critical; kept as snapshot approach
# since slope features are not computed for non-ESP assets at inference time.

GAS_LIFT_CLASS_PROFILES = {
    "normal":           {"psi": (940, 1060),  "temp": (140, 178), "vib": (1.0, 2.5)},
    "valve_failure":    {"psi": (450, 640),   "temp": (165, 200), "vib": (8.0, 14.0)},
    "thermal_runaway":  {"psi": (940, 1040),  "temp": (210, 248), "vib": (3.0, 5.5)},
    "bearing_wear":     {"psi": (945, 1040),  "temp": (163, 183), "vib": (7.5, 13.5)},
}

MUD_PUMP_CLASS_PROFILES = {
    "normal":                       {"psi": (2550, 3150), "temp": (90,  120), "vib": (2.5, 4.5)},
    "pulsation_dampener_failure":   {"psi": (3800, 4600), "temp": (120, 158), "vib": (15.0, 28.0)},
    "valve_washout":                {"psi": (1800, 2400), "temp": (115, 145), "vib": (5.0, 10.0)},
    "piston_seal_wear":             {"psi": (1900, 2450), "temp": (155, 190), "vib": (5.5, 8.5)},
}

TOP_DRIVE_CLASS_PROFILES = {
    "normal":                   {"psi": (2840, 3160), "temp": (130, 165), "vib": (1.8, 3.8)},
    "gearbox_bearing_spalling": {"psi": (2850, 3060), "temp": (175, 222), "vib": (11.0, 20.0)},
    "hydraulic_leak":           {"psi": (1700, 2150), "temp": (158, 208), "vib": (3.5, 7.0)},
}


# ── ESP trajectory-based data generation ──────────────────────────────────────

def gen_esp_classifier_data_trajectory(
    n_normal: int = TRAINING_PARAMS["n_normal"],
    n_trajectories: int = TRAINING_PARAMS["n_trajectories"],
    steps_min: int = TRAINING_PARAMS["steps_min"],
    steps_max: int = TRAINING_PARAMS["steps_max"],
    k_min: float = TRAINING_PARAMS["k_min"],
    k_max: float = TRAINING_PARAMS["k_max"],
    noise_frac: float = TRAINING_PARAMS["noise_frac"],
    warmup: int = TRAINING_PARAMS["warmup_steps"],
    rng: np.random.Generator = None,
) -> tuple:
    """
    Generate ESP classifier training data using trajectory simulation.

    For each fault class:
      1. Draw a target endpoint from fault_signatures.py canonical ranges
      2. Simulate a degradation ramp from nominal → endpoint using exponential
         ramp t = ((i+1)/steps)^k (same formula as app.py:_run_degrade_thread)
      3. At each step, compute slope features from recent history
         (same window/difference logic as processor.py:get_slopes())
      4. Include readings from step WARMUP onward (slopes are reliable by then)

    This gives ~(n_trajectories × avg_steps − warmup) rows per fault class.
    Normal class: static sampling with near-zero slopes (no trajectory needed).

    Returns (X, y) arrays with features and class labels.
    """
    if rng is None:
        rng = np.random.default_rng(TRAINING_PARAMS["seed"])

    NOM = ESP_NOMINAL

    def noisy(val: float, frac: float = noise_frac) -> float:
        return val + rng.normal(0.0, abs(val * frac))

    rows, labels = [], []

    # ── Class 0: Normal ───────────────────────────────────────────────────────
    # No trajectory — draw sensor values from normal ranges with near-zero slopes.
    nr = ESP_NORMAL_RANGES
    for _ in range(n_normal):
        psi  = noisy(rng.uniform(*nr["psi"]))
        temp = noisy(rng.uniform(*nr["temp"]))
        vib  = max(0.05, noisy(rng.uniform(*nr["vib"])))
        amps = noisy(rng.uniform(*nr["amps"]))
        # Slopes are genuinely near-zero during normal operation
        dpsi  = rng.uniform(*nr["dpsi_dt"])
        dtemp = rng.uniform(*nr["dtemp_dt"])
        dvib  = rng.uniform(*nr["dvib_dt"])
        damps = rng.uniform(*nr["damps_dt"])
        rows.append([psi, temp, vib, amps, dpsi, dtemp, dvib, damps])
        labels.append(0)

    # ── Classes 1–4: Fault trajectories ──────────────────────────────────────
    fault_classes = [
        ("gas_lock",       1),
        ("sand_ingress",   2),
        ("motor_overheat", 3),
        ("slug_flow",      4),
    ]

    for fault_name, class_idx in fault_classes:
        sig = ESP_FAULT_SIGNATURES[fault_name]
        traj_count = 0
        reading_count = 0

        for _ in range(n_trajectories):
            # Draw a target endpoint for this specific trajectory.
            # Using the fault signature's ENTIRE range so the classifier
            # sees the full distribution of fault intensities.
            psi_end  = rng.uniform(*sig["psi"])
            temp_end = rng.uniform(*sig["temp"])
            vib_end  = max(0.05, rng.uniform(*sig["vib"]))
            amps_end = rng.uniform(*sig["amps"])

            # Ramp parameters — randomized to match live degrade diversity
            steps = int(rng.integers(steps_min, steps_max + 1))
            k     = rng.uniform(k_min, k_max)

            # Sensor history buffer for slope computation
            history: list = []

            for i in range(steps):
                # Exponential ramp: matches _run_degrade_thread exactly
                t = ((i + 1) / steps) ** k

                # Ramp each sensor from nominal toward fault endpoint
                psi  = noisy(NOM["psi"]  + (psi_end  - NOM["psi"])  * t)
                temp = noisy(NOM["temp"] + (temp_end - NOM["temp"]) * t)
                vib  = max(0.05, noisy(NOM["vib"] + (vib_end - NOM["vib"]) * t))
                amps = noisy(NOM["amps"] + (amps_end - NOM["amps"]) * t)

                history.append([psi, temp, vib, amps])

                # Skip warmup steps — slopes not yet reliable
                if i < warmup:
                    continue

                # Compute slopes from history (matches processor.py)
                dpsi, dtemp, dvib, damps = _compute_slopes(history)

                rows.append([psi, temp, vib, amps, dpsi, dtemp, dvib, damps])
                labels.append(class_idx)
                reading_count += 1

            traj_count += 1

        log.info(f"    {fault_name:<20} {traj_count:>4} trajectories → {reading_count:>7,} readings")

    X = np.array(rows, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


# ── 3-feature snapshot data generation (non-ESP assets) ──────────────────────

def gen_3feature_classifier_data(
    profiles: dict,
    n_normal: int = 3000,
    n_fault: int = 1000,
    rng: np.random.Generator = None,
) -> tuple:
    """
    Generate 3-feature snapshot data for gas_lift, mud_pump, top_drive.
    Snapshot approach is acceptable here because:
    - These assets are infrastructure-completeness only (not demo-critical)
    - Inference-api uses 3 features (no slope features) for non-ESP assets
    - Trajectory approach would add complexity without improving demo quality
    """
    if rng is None:
        rng = np.random.default_rng(TRAINING_PARAMS["seed"])

    rows, labels = [], []
    noise = 0.03

    def noisy(val):
        return val + rng.normal(0, abs(val * noise))

    class_names = list(profiles.keys())
    for class_idx, class_name in enumerate(class_names):
        p = profiles[class_name]
        n = n_normal if class_idx == 0 else n_fault
        for _ in range(n):
            psi  = noisy(rng.uniform(*p["psi"]))
            temp = noisy(rng.uniform(*p["temp"]))
            vib  = max(0.05, noisy(rng.uniform(*p["vib"])))
            rows.append([psi, temp, vib])
            labels.append(class_idx)

    X = np.array(rows, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


# ── Training ──────────────────────────────────────────────────────────────────

def train_classifier(
    X: np.ndarray,
    y: np.ndarray,
    n_classes: int,
    feature_names: list,
    asset_class: str,
    n_rounds: int = TRAINING_PARAMS["max_rounds"],
) -> xgb.Booster:
    """
    Train a multi-class XGBoost classifier, print per-class metrics.
    Returns the booster at best_iteration.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=TRAINING_PARAMS["seed"], stratify=y
    )

    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)
    dtest  = xgb.DMatrix(X_test,  label=y_test,  feature_names=feature_names)

    params = {
        "objective":        "multi:softprob",
        "num_class":        n_classes,
        "max_depth":        TRAINING_PARAMS["max_depth"],
        "learning_rate":    TRAINING_PARAMS["learning_rate"],
        "subsample":        0.85,
        "colsample_bytree": 0.85,
        "min_child_weight": 3,
        "eval_metric":      ["mlogloss", "merror"],
        "tree_method":      "hist",
        "seed":             TRAINING_PARAMS["seed"],
        "verbosity":        0,
    }

    evals_result = {}
    booster = xgb.train(
        params,
        dtrain,
        num_boost_round=n_rounds,
        evals=[(dtrain, "train"), (dtest, "test")],
        evals_result=evals_result,
        early_stopping_rounds=TRAINING_PARAMS["early_stopping"],
        verbose_eval=False,
    )

    # Per-class metrics
    raw        = booster.predict(dtest).reshape(-1, n_classes)
    pred_labels = raw.argmax(axis=1)
    final_merror = evals_result["test"]["merror"][booster.best_iteration]
    accuracy     = 1.0 - final_merror
    log.info(f"  Test accuracy: {accuracy:.4f}  (best_iteration: {booster.best_iteration})")

    if asset_class == "esp":
        label_names = [ESP_LABEL_MAP[i] for i in range(n_classes)]
        cm = confusion_matrix(y_test, pred_labels)
        log.info(f"\n  Per-class metrics (ESP 5-class):")
        log.info(f"  {'Class':<25} {'Correct':>8} {'Total':>8} {'Precision':>10} {'PASS?':>8}")
        log.info(f"  {'-'*65}")

        all_pass = True
        for i, name in enumerate(label_names):
            if i >= len(cm):
                continue
            correct  = cm[i, i]
            total    = cm[i].sum()
            prec     = precision_score(y_test, pred_labels, labels=[i], average="macro",
                                       zero_division=0)
            min_prec = TRAINING_PARAMS.get(f"min_precision_{name}", 0.85)
            passed   = prec >= min_prec
            if not passed:
                all_pass = False
            flag = "✅" if passed else f"❌ (need ≥{min_prec:.2f})"
            log.info(f"  {i} {name:<23} {correct:>8}/{total:<7} {prec:>9.3f}  {flag}")

        # Pass/fail verdict
        log.info(f"\n  {'='*65}")
        if all_pass:
            log.info(f"  ✅ ALL CLASSES PASS — model meets MODEL_FOUNDATIONS §6 thresholds")
        else:
            log.warning(f"  ❌ SOME CLASSES FAILED — DO NOT DEPLOY until pass thresholds are met")
            log.warning(f"     See MODEL_FOUNDATIONS.md §6 for required precision values")
        log.info(f"  {'='*65}")

    return booster


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Train XGBoost fault classifiers — trajectory-based (Session U)."
    )
    parser.add_argument(
        "--output-dir", default="gke/inference-api/models",
        help="Directory to save .ubj model files (default: gke/inference-api/models)",
    )
    parser.add_argument(
        "--asset-class", default=None,
        choices=["esp", "gas_lift", "mud_pump", "top_drive"],
        help="Train only one asset class (default: all four)",
    )
    parser.add_argument(
        "--n-trajectories", type=int, default=TRAINING_PARAMS["n_trajectories"],
        help=f"Fault trajectories per class (default: {TRAINING_PARAMS['n_trajectories']})",
    )
    parser.add_argument(
        "--n-normal", type=int, default=TRAINING_PARAMS["n_normal"],
        help=f"Normal class samples (default: {TRAINING_PARAMS['n_normal']})",
    )
    parser.add_argument(
        "--rounds", type=int, default=TRAINING_PARAMS["max_rounds"],
        help=f"Max XGBoost boosting rounds (default: {TRAINING_PARAMS['max_rounds']})",
    )
    parser.add_argument(
        "--seed", type=int, default=TRAINING_PARAMS["seed"],
        help=f"Random seed (default: {TRAINING_PARAMS['seed']})",
    )
    parser.add_argument(
        "--n-fault", type=int, default=1000,
        help="Training samples per fault class for NON-ESP assets (default: 1000)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    asset_classes = (
        [args.asset_class] if args.asset_class
        else ["esp", "gas_lift", "mud_pump", "top_drive"]
    )

    log.info("=" * 72)
    log.info("  GDC-PM — Fault Classifier Training (Session U — Trajectory-Based)")
    log.info(f"  Asset classes: {asset_classes}")
    log.info(f"  Output dir:    {output_dir.resolve()}")
    log.info(f"  Approach:      trajectory ({args.n_trajectories} ramps/class, {args.n_normal} normal)")
    log.info(f"  Distributions: sourced from fault_signatures.py (canonical, not invented)")
    log.info("=" * 72)

    for ac in asset_classes:
        log.info(f"\n{'─'*72}")
        log.info(f"  Training: {ac.upper().replace('_', ' ')} classifier")

        if ac == "esp":
            n_classes     = 5
            feature_names = ESP_FEATURE_NAMES
            log.info(f"  Classes:  {[ESP_LABEL_MAP[i] for i in range(n_classes)]}")
            log.info(f"  Features: {feature_names}")
            log.info(f"  Approach: TRAJECTORY-BASED — {args.n_trajectories} ramps × 30-80 steps per fault")
            log.info(f"  gas_lock PSI range:   {ESP_FAULT_SIGNATURES['gas_lock']['psi']}  "
                     f"(live injection range, NOT catastrophic endpoint)")
            log.info(f"  slug_flow vib range:  {ESP_FAULT_SIGNATURES['slug_flow']['vib']}  "
                     f"(widened for H2 story credibility)")
            log.info(f"  slug_flow dtemp_dt:   {ESP_FAULT_SIGNATURES['slug_flow']['dtemp_dt']}  "
                     f"(≈0 — the H2 discriminating feature)")

            X, y = gen_esp_classifier_data_trajectory(
                n_normal=args.n_normal,
                n_trajectories=args.n_trajectories,
                rng=rng,
            )

        else:
            profiles = {
                "gas_lift":  GAS_LIFT_CLASS_PROFILES,
                "mud_pump":  MUD_PUMP_CLASS_PROFILES,
                "top_drive": TOP_DRIVE_CLASS_PROFILES,
            }[ac]
            n_classes     = len(profiles)
            feature_names = ["psi", "temp_f", "vibration"]
            label_map     = {i: name for i, name in enumerate(profiles.keys())}
            log.info(f"  Classes:  {list(label_map.values())}")
            log.info(f"  Approach: snapshot (non-ESP, infrastructure completeness only)")

            X, y = gen_3feature_classifier_data(
                profiles=profiles,
                n_normal=args.n_normal,
                n_fault=args.n_fault,
                rng=rng,
            )

        log.info(f"\n  Dataset: {len(X):,} rows × {X.shape[1]} features")
        if ac == "esp":
            label_names = [ESP_LABEL_MAP[i] for i in range(n_classes)]
            class_counts = {label_names[i]: int((y == i).sum()) for i in range(n_classes)}
        else:
            class_counts = {f"class_{i}": int((y == i).sum()) for i in range(n_classes)}
        log.info(f"  Class distribution: {class_counts}")

        booster = train_classifier(X, y, n_classes, feature_names, ac, args.rounds)

        out_path = output_dir / f"{ac}_classifier.ubj"
        booster.save_model(str(out_path))
        size_kb = out_path.stat().st_size / 1024
        log.info(f"\n  ✅ Saved: {out_path}  ({size_kb:.0f} KB)")

    log.info(f"\n{'='*72}")
    log.info("  All classifiers trained.")
    log.info(f"  Files in {output_dir.resolve()}:")
    for f in sorted(output_dir.glob("*_classifier.ubj")):
        log.info(f"    {f.name}  ({f.stat().st_size // 1024} KB)")
    log.info(f"{'='*72}")
    log.info("\n  NEXT STEPS (MODEL_FOUNDATIONS §7):")
    log.info("  1. Rebuild inference-api image:")
    log.info("     docker build -t us-central1-docker.pkg.dev/gdc-pm-v2/gdc-models/inference-api:latest gke/inference-api/")
    log.info("  2. Push and get digest:")
    log.info("     docker push ... && docker inspect --format='{{index .RepoDigests 0}}'")
    log.info("  3. Deploy with exact digest:")
    log.info("     kubectl scale deployment/inference-api --replicas=1 -n gdc-pm")
    log.info("     kubectl set image deployment/inference-api inference-api=<DIGEST> -n gdc-pm")
    log.info("  4. Scale up fault-trigger-ui and run ≥3 injections (gas_lock + slug_flow + normal)")
    log.info("  5. Non-circular verification (replay injection_events rows through /predict)")
    log.info("     Target: gas_lock ≥ 0.92 precision, slug_flow ≥ 0.90 precision / 0.85 recall")


if __name__ == "__main__":
    main()
