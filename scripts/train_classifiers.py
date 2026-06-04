#!/usr/bin/env python3
"""
scripts/train_classifiers.py

Train XGBoost fault classifiers for all 4 O&G asset classes.
Outputs are saved as .ubj files suitable for LOCAL_MODELS_DIR in inference-api.

KEY DIFFERENCE FROM seed-and-train-og-models.py
------------------------------------------------
The original script had 4 ESP classes: normal, gas_lock, sand_ingress, motor_overheat.
This script adds class 4 = slug_flow to the ESP classifier.

WHY slug_flow NEEDS ITS OWN CLASS (not just "vibration_alarm")
--------------------------------------------------------------
Slug flow is surface flowline slugging — hydraulic impulse transmission from the
surface through production tubing to the downhole vibration sensor.

The DISCRIMINATING PHYSICS vs downhole mechanical faults:
  - slug_flow:     vibration RISES + temperature FLAT (no heat in motor)
  - sand_ingress:  vibration RISES + temperature RISES slowly (impeller erosion heat)
  - motor_overheat: vibration mild + temperature RISES sharply
  - gas_lock:      vibration spikes + PSI DROPS + temperature rises + amps drop

Temperature is the discriminating feature between slug_flow (surface) and downhole.
A model trained on all 5 classes can output:
  "slug_flow 89%, sand_ingress 8%" → don't pull the pump ($1,500 choke adjustment)
vs:
  "sand_ingress 91%, slug_flow 4%" → escalate ($150,000 pump replacement)

TRAINING DATA APPROACH
----------------------
Each class is represented by static-sensor snapshots with rate-of-change features.
This matches the inference-api's /predict endpoint which takes a single reading
with pre-computed slope features (dpsi_dt, dtemp_dt, dvib_dt, damps_dt).

USAGE
-----
  python scripts/train_classifiers.py
  python scripts/train_classifiers.py --output-dir gke/inference-api/models
  python scripts/train_classifiers.py --asset-class esp --n-samples 3000
"""

import argparse
import logging
from pathlib import Path

import numpy as np
import xgboost as xgb
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("train_classifiers")

# ── ESP: 5-class label map (MUST match inference-api/app.py MODEL_CONFIGS) ────
ESP_LABEL_MAP = {
    0: "normal",
    1: "gas_lock",
    2: "sand_ingress",
    3: "motor_overheat",
    4: "slug_flow",          # NEW — surface flowline slugging
}

# ── Training profiles ─────────────────────────────────────────────────────────
# Each profile defines the sensor ranges and rate-of-change features for one
# fault class. These are the STEADY-STATE ranges observed during that fault,
# NOT the nominal-to-fault transition (that's what the health regressors handle).
#
# The classifier answers: "given THIS snapshot, which fault class is this?"
# Feature vector: [psi, temp_f, vibration, motor_amps,
#                  dpsi_dt, dtemp_dt, dvib_dt, damps_dt]
#                 (8 features for ESP, 3 for others — matches inference-api)

ESP_CLASS_PROFILES = {
    # ── Class 0: Normal operation ────────────────────────────────────────────
    # Well-producing normally. All sensors nominal, near-zero rates.
    "normal": {
        "psi":      (1200, 1600),
        "temp":     (180,  220),
        "vib":      (0.8,  2.0),
        "amps":     (60,   90),
        "dpsi_dt":  (-2.0, 2.0),       # mild random variation
        "dtemp_dt": (-0.1, 0.1),       # stable temperature
        "dvib_dt":  (-0.05, 0.05),     # stable vibration
        "damps_dt": (-0.2, 0.2),       # stable current
    },
    # ── Class 1: Gas Lock ────────────────────────────────────────────────────
    # GVF >65% → impeller stages fill with gas → pump unloads
    # PSI collapses (impeller stalls), amps drop (motor unloaded),
    # vibration spikes (cavitation), temperature rises slightly initially
    # then more sharply as motor loses cooling fluid flow.
    # Reference: API RP 11S §5, Baker Hughes Centrilift Gas Handling Design Guide
    "gas_lock": {
        "psi":      (350,  800),        # PSI collapse — critical: 800 PSI SCADA alarm
        "temp":     (195,  250),        # rising — motor losing cooling
        "vib":      (5.0,  13.0),       # cavitation vibration signature
        "amps":     (20,   50),         # motor current collapses as pump unloads
        "dpsi_dt":  (-60.0, -8.0),      # rapidly declining PSI
        "dtemp_dt": (0.5,  6.0),        # rising temperature (3-8°F/min per API RP 11S)
        "dvib_dt":  (0.2,  2.5),        # increasing vibration
        "damps_dt": (-8.0, -1.0),       # declining current
    },
    # ── Class 2: Sand Ingress ────────────────────────────────────────────────
    # Formation sand erodes impeller stages over days-weeks.
    # PSI declines slowly, vib rises slowly (worn clearances),
    # temp rises (reduced hydraulic efficiency → more heat),
    # amps decline slowly as pump does less hydraulic work.
    "sand_ingress": {
        "psi":      (1050, 1500),       # slowly declining
        "temp":     (200,  255),        # slowly rising (impeller erosion heat)
        "vib":      (3.5,  10.0),       # rising (worn impeller clearances)
        "amps":     (42,   72),         # slowly declining
        "dpsi_dt":  (-5.0, -0.5),       # slow pressure decline
        "dtemp_dt": (0.3,  2.5),        # slow temperature rise — RISES (contrast with slug_flow)
        "dvib_dt":  (0.05, 0.6),        # slow vibration increase
        "damps_dt": (-1.5, -0.1),       # slow current decline
    },
    # ── Class 3: Motor Overheat ──────────────────────────────────────────────
    # Downhole cooling degradation → winding temp climbs → insulation failure.
    # Temperature is the PRIMARY signal. PSI/vib relatively stable early.
    # Critical: Class H insulation limit 356°F / 180°C (API RP 11S, IEEE 117)
    "motor_overheat": {
        "psi":      (1200, 1560),       # pressure essentially stable
        "temp":     (240,  295),        # ELEVATED — this is the primary signal
        "vib":      (2.0,  5.5),        # mild vibration (thermal expansion)
        "amps":     (82,   110),        # overcurrent as motor fights rising resistance
        "dpsi_dt":  (-2.0, 0.5),        # near-stable pressure
        "dtemp_dt": (1.5,  7.0),        # STRONG temperature rise — primary feature
        "dvib_dt":  (0.01, 0.15),       # minimal vibration change
        "damps_dt": (0.3,  3.0),        # rising current
    },
    # ── Class 4: Slug Flow ───────────────────────────────────────────────────
    # Surface flowline slug flow transmits hydraulic impulses downhole via
    # production tubing to the vibration sensor. The pump is MECHANICALLY SOUND.
    #
    # KEY DISCRIMINATING SIGNATURE vs all other classes:
    #   - Vibration: ELEVATED/RISING (hydraulic impulses from slugs)
    #   - Temperature: COMPLETELY FLAT (no heat generated in motor)
    #   - PSI: nominally stable (surface phenomenon, not pump failure)
    #   - Amps: nominally stable (pump running fine hydraulically)
    #
    # This is the H2 demo: "vibration elevated, temperature flat →
    # surface slug flow, not bearing wear → $1,500 not $150,000"
    #
    # Reference: SPE-174536-MS, ESP OEM troubleshooting guides
    "slug_flow": {
        "psi":      (1180, 1580),       # nominally stable (surface origin)
        "temp":     (182,  212),        # FLAT — stays in normal range (KEY DISCRIMINATOR)
        "vib":      (3.0,  8.0),        # ELEVATED from slug impulses
        "amps":     (60,   88),         # nominally stable (pump healthy)
        "dpsi_dt":  (-4.0, 4.0),        # minor PSI oscillation from slug periodicity
        "dtemp_dt": (-0.08, 0.08),      # ~ZERO temperature rate — THE discriminating feature
        "dvib_dt":  (0.1,  1.2),        # rising/elevated vibration rate
        "damps_dt": (-0.4, 0.4),        # stable current
    },
}

# ── Other asset class profiles (3-feature: psi, temp_f, vibration only) ───────
# These match the inference-api which uses 3 features for non-ESP assets.

GAS_LIFT_CLASS_PROFILES = {
    "normal":          {"psi": (940, 1060),  "temp": (140, 178), "vib": (1.0, 2.5)},
    "valve_failure":   {"psi": (450, 640),   "temp": (165, 200), "vib": (8.0, 14.0)},
    "thermal_runaway": {"psi": (940, 1040),  "temp": (210, 248), "vib": (3.0, 5.5)},
    "bearing_wear":    {"psi": (945, 1040),  "temp": (163, 183), "vib": (7.5, 13.5)},
}

MUD_PUMP_CLASS_PROFILES = {
    "normal":                        {"psi": (2550, 3150), "temp": (90,  120), "vib": (2.5, 4.5)},
    "pulsation_dampener_failure":    {"psi": (3800, 4600), "temp": (120, 158), "vib": (15.0, 28.0)},
    "valve_washout":                 {"psi": (1800, 2400), "temp": (115, 145), "vib": (5.0, 10.0)},
    "piston_seal_wear":              {"psi": (1900, 2450), "temp": (155, 190), "vib": (5.5, 8.5)},
}

TOP_DRIVE_CLASS_PROFILES = {
    "normal":                    {"psi": (2840, 3160), "temp": (130, 165), "vib": (1.8, 3.8)},
    "gearbox_bearing_spalling":  {"psi": (2850, 3060), "temp": (175, 222), "vib": (11.0, 20.0)},
    "hydraulic_leak":            {"psi": (1700, 2150), "temp": (158, 208), "vib": (3.5, 7.0)},
}


def gen_esp_classifier_data(n_normal: int = 4000, n_fault: int = 1500,
                             rng: np.random.Generator = None) -> tuple:
    """
    Generate ESP classifier training data (8 features, 5 classes).

    Features: [psi, temp_f, vibration, motor_amps, dpsi_dt, dtemp_dt, dvib_dt, damps_dt]
    Labels:   0=normal, 1=gas_lock, 2=sand_ingress, 3=motor_overheat, 4=slug_flow
    """
    if rng is None:
        rng = np.random.default_rng(42)

    rows, labels = [], []
    noise = 0.03   # 3% relative noise on raw sensor values

    def noisy(val, frac=noise):
        return val + rng.normal(0, abs(val * frac))

    # Class 0: normal
    p = ESP_CLASS_PROFILES["normal"]
    for _ in range(n_normal):
        psi    = noisy(rng.uniform(*p["psi"]))
        temp   = noisy(rng.uniform(*p["temp"]))
        vib    = max(0.05, noisy(rng.uniform(*p["vib"])))
        amps   = noisy(rng.uniform(*p["amps"]))
        dpsi   = rng.uniform(*p["dpsi_dt"])
        dtemp  = rng.uniform(*p["dtemp_dt"])
        dvib   = rng.uniform(*p["dvib_dt"])
        damps  = rng.uniform(*p["damps_dt"])
        rows.append([psi, temp, vib, amps, dpsi, dtemp, dvib, damps])
        labels.append(0)

    # Classes 1-4: fault classes
    fault_classes = [
        ("gas_lock",       1),
        ("sand_ingress",   2),
        ("motor_overheat", 3),
        ("slug_flow",      4),
    ]
    for fault_name, class_idx in fault_classes:
        p = ESP_CLASS_PROFILES[fault_name]
        for _ in range(n_fault):
            psi    = noisy(rng.uniform(*p["psi"]))
            temp   = noisy(rng.uniform(*p["temp"]))
            vib    = max(0.05, noisy(rng.uniform(*p["vib"])))
            amps   = noisy(rng.uniform(*p["amps"]))
            dpsi   = rng.uniform(*p["dpsi_dt"])
            dtemp  = rng.uniform(*p["dtemp_dt"])
            dvib   = rng.uniform(*p["dvib_dt"])
            damps  = rng.uniform(*p["damps_dt"])
            rows.append([psi, temp, vib, amps, dpsi, dtemp, dvib, damps])
            labels.append(class_idx)

    X = np.array(rows, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


def gen_3feature_classifier_data(profiles: dict, n_normal: int = 3000,
                                  n_fault: int = 1000,
                                  rng: np.random.Generator = None) -> tuple:
    """Generate 3-feature classifier data for gas_lift, mud_pump, top_drive."""
    if rng is None:
        rng = np.random.default_rng(42)

    rows, labels = [], []
    noise = 0.03

    def noisy(val, frac=noise):
        return val + rng.normal(0, abs(val * frac))

    class_names = list(profiles.keys())   # normal is always first
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


def train_classifier(X: np.ndarray, y: np.ndarray, n_classes: int,
                     feature_names: list, asset_class: str,
                     n_rounds: int = 250) -> xgb.Booster:
    """Train a multi-class XGBoost classifier, print classification report."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)
    dtest  = xgb.DMatrix(X_test,  label=y_test,  feature_names=feature_names)

    params = {
        "objective":        "multi:softprob",
        "num_class":        n_classes,
        "max_depth":        6,
        "learning_rate":    0.08,
        "subsample":        0.85,
        "colsample_bytree": 0.85,
        "min_child_weight": 3,
        "eval_metric":      ["mlogloss", "merror"],
        "tree_method":      "hist",
        "seed":             42,
        "verbosity":        0,
    }

    evals_result = {}
    booster = xgb.train(
        params,
        dtrain,
        num_boost_round=n_rounds,
        evals=[(dtrain, "train"), (dtest, "test")],
        evals_result=evals_result,
        early_stopping_rounds=20,
        verbose_eval=False,
    )

    # Classification report
    raw = booster.predict(dtest).reshape(-1, n_classes)
    pred_labels = raw.argmax(axis=1)

    final_mlogloss = evals_result["test"]["mlogloss"][booster.best_iteration]
    final_merror   = evals_result["test"]["merror"][booster.best_iteration]
    accuracy       = 1.0 - final_merror
    log.info(f"  Test accuracy: {accuracy:.4f}  |  mlogloss: {final_mlogloss:.4f}  "
             f"(best iteration: {booster.best_iteration})")

    # Per-class accuracy — critical for verifying slug_flow discrimination
    from sklearn.metrics import confusion_matrix
    import numpy as np
    label_names = list(ESP_LABEL_MAP.values()) if asset_class == "esp" else None
    if label_names:
        cm = confusion_matrix(y_test, pred_labels)
        log.info(f"\n  Per-class accuracy (ESP 5-class):")
        for i, name in enumerate(label_names):
            if i < len(cm):
                correct = cm[i, i]
                total   = cm[i].sum()
                log.info(f"    class {i} ({name:<20}) {correct:>4}/{total:<4} = {correct/max(total,1):.1%}")

    return booster


def main():
    parser = argparse.ArgumentParser(
        description="Train XGBoost fault classifiers for all O&G asset classes."
    )
    parser.add_argument(
        "--output-dir",
        default="gke/inference-api/models",
        help="Directory to save .ubj model files (default: gke/inference-api/models)",
    )
    parser.add_argument(
        "--asset-class", default=None,
        choices=["esp", "gas_lift", "mud_pump", "top_drive"],
        help="Train only one asset class (default: all four)",
    )
    parser.add_argument(
        "--n-samples", type=int, default=2000,
        help="Training samples per fault class for ESP normal class (default: 2000)",
    )
    parser.add_argument(
        "--n-fault", type=int, default=1000,
        help="Training samples per fault class (default: 1000)",
    )
    parser.add_argument(
        "--rounds", type=int, default=250,
        help="Max XGBoost boosting rounds (default: 250, early stopping at 20)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
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
    log.info("  GDC-PM — Fault Classifier Training")
    log.info(f"  Asset classes: {asset_classes}")
    log.info(f"  Output dir:    {output_dir.resolve()}")
    log.info("=" * 72)

    for ac in asset_classes:
        log.info(f"\n{'─'*72}")
        log.info(f"  Training: {ac.upper().replace('_', ' ')} classifier")

        if ac == "esp":
            n_classes     = 5
            label_map     = ESP_LABEL_MAP
            feature_names = ["psi", "temp_f", "vibration", "motor_amps",
                              "dpsi_dt", "dtemp_dt", "dvib_dt", "damps_dt"]
            log.info(f"  Classes:  {list(label_map.values())}")
            log.info(f"  Features: {feature_names}")
            log.info(f"  Key note: class 4 (slug_flow) has FLAT dtemp_dt — "
                     "the H2 discriminating signature")

            X, y = gen_esp_classifier_data(
                n_normal=args.n_samples,
                n_fault=args.n_fault,
                rng=rng,
            )
        else:
            profiles = {
                "gas_lift":  GAS_LIFT_CLASS_PROFILES,
                "mud_pump":  MUD_PUMP_CLASS_PROFILES,
                "top_drive": TOP_DRIVE_CLASS_PROFILES,
            }[ac]
            n_classes     = len(profiles)
            label_map     = {i: name for i, name in enumerate(profiles.keys())}
            feature_names = ["psi", "temp_f", "vibration"]
            log.info(f"  Classes:  {list(label_map.values())}")

            X, y = gen_3feature_classifier_data(
                profiles=profiles,
                n_normal=args.n_samples,
                n_fault=args.n_fault,
                rng=rng,
            )

        log.info(f"  Dataset: {len(X):,} rows × {X.shape[1]} features")
        class_counts = {label_map[i]: int((y == i).sum()) for i in range(n_classes)}
        log.info(f"  Class distribution: {class_counts}")

        booster = train_classifier(X, y, n_classes, feature_names, ac, args.rounds)

        out_path = output_dir / f"{ac}_classifier.ubj"
        booster.save_model(str(out_path))
        size_kb = out_path.stat().st_size / 1024
        log.info(f"\n  ✅ Saved: {out_path}  ({size_kb:.0f} KB)")

    log.info(f"\n{'='*72}")
    log.info("  All classifiers trained.")
    log.info(f"  Files in {output_dir}:")
    for f in sorted(output_dir.glob("*_classifier.ubj")):
        log.info(f"    {f.name}  ({f.stat().st_size // 1024} KB)")
    log.info(f"{'='*72}")
    log.info("\n  Next steps:")
    log.info("  1. Rebuild inference-api image:")
    log.info("     cd gke/inference-api && docker build -t ...")
    log.info("  2. Push and rollout:")
    log.info("     docker push ... && kubectl rollout restart deployment/inference-api -n gdc-pm")
    log.info("  3. Verify:")
    log.info("     curl -s http://gdc-pm.bdau.io/api/mlops/status | python3 -c "
             "\"import sys,json;d=json.load(sys.stdin);print(d)\"")


if __name__ == "__main__":
    main()
