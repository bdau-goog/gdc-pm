#!/usr/bin/env python3
"""
scripts/seed-and-train-og-models.py

Generates training data and trains XGBoost models for all 4 O&G asset classes:
  ESP (Electrical Submersible Pump)
  Gas Lift Compressor
  Mud Pump (Triplex)
  Top Drive

For each asset class, trains TWO models:
  1. Fault Classifier  — predicts fault type (normal/gas_lock/etc.)
     Uploaded to GCS at gs://{bucket}/{class}_classifier/latest/
  2. RUL Regressor     — predicts Remaining Useful Life in minutes
     Saved locally to gke/fault-trigger-ui/models/{class}_rul.ubj

Usage:
  python3 scripts/seed-and-train-og-models.py
  python3 scripts/seed-and-train-og-models.py --bucket gdc-pm-v2-models
"""

import argparse
import os
import random
import tempfile
from pathlib import Path

import numpy as np
import xgboost as xgb
from sklearn.metrics import classification_report, mean_absolute_error
from sklearn.model_selection import train_test_split

# ── Configuration ─────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT  = SCRIPT_DIR.parent
MODELS_DIR = REPO_ROOT / "gke" / "fault-trigger-ui" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_BUCKET = "gdc-pm-v2-models"

# Random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ── Asset Class Profiles ───────────────────────────────────────────────────────
# Each asset class defines:
#   classes: ordered list of fault class names (class 0 = normal)
#   normal: (psi_mean, psi_std, temp_mean, temp_std, vib_mean, vib_std)
#   faults: {class_name: (psi_mean, psi_std, temp_mean, temp_std, vib_mean, vib_std)}
#   gradual_faults: list of class names that are gradual (ramp) vs instant (burst)
#   rul_thresholds: {sensor: (threshold, direction)} — "above" or "below"

ASSET_PROFILES = {
    "esp": {
        "description": "Electrical Submersible Pump — Downhole production",
        "classes": ["normal", "gas_lock", "sand_ingress", "motor_overheat"],
        "normal":  (1400, 70,   198, 8,   1.4, 0.2),
        "faults": {
            "gas_lock":      (550, 80,  222, 12,  9.0, 1.5),   # PSI crash, Vib spike
            "sand_ingress":  (1360, 65, 210, 10,  6.5, 1.0),   # Vib rises
            "motor_overheat":(1380, 65, 278, 8,   3.0, 0.4),   # Temp rises
        },
        "gradual_faults": ["sand_ingress", "motor_overheat"],
        "instant_faults":  ["gas_lock"],
        "rul_primary": {
            "sand_ingress":   ("vib",  "above", 8.0),
            "motor_overheat": ("temp", "above", 280.0),
            "gas_lock":       ("psi",  "below", 800.0),
        },
        "normal_ranges": {"psi": (1200, 1600), "temp": (180, 220), "vib": (0.8, 2.0)},
        "fault_ranges": {
            "gas_lock":       {"psi": (350, 750), "temp": (195, 245), "vib": (6.0, 12.0)},
            "sand_ingress":   {"psi": (1280, 1580), "temp": (200, 240), "vib": (4.5, 9.5)},
            "motor_overheat": {"psi": (1300, 1560), "temp": (265, 295), "vib": (2.5, 4.5)},
        },
        "sensor_labels": {
            "psi": ("Intake Pressure", "PSI"),
            "temp": ("Motor Winding Temp", "°F"),
            "vib": ("Motor Vibration", "mm/s"),
        },
    },

    "gas_lift": {
        "description": "Gas Lift Compressor — Surface injection",
        "classes": ["normal", "valve_failure", "thermal_runaway", "bearing_wear"],
        "normal":  (1000, 25,  158, 6,   1.7, 0.2),
        "faults": {
            "valve_failure":   (530, 55,  178, 10,  11.0, 1.5),
            "thermal_runaway": (990, 25,  228, 8,   3.5, 0.5),
            "bearing_wear":    (985, 25,  172, 6,   10.0, 1.5),
        },
        "gradual_faults": ["thermal_runaway", "bearing_wear"],
        "instant_faults":  ["valve_failure"],
        "rul_primary": {
            "valve_failure":   ("psi",  "below", 600.0),
            "thermal_runaway": ("temp", "above", 230.0),
            "bearing_wear":    ("vib",  "above", 12.0),
        },
        "normal_ranges": {"psi": (940, 1060), "temp": (140, 178), "vib": (1.0, 2.5)},
        "fault_ranges": {
            "valve_failure":   {"psi": (450, 640), "temp": (165, 200), "vib": (8.0, 14.0)},
            "thermal_runaway": {"psi": (940, 1040), "temp": (210, 248), "vib": (3.0, 5.5)},
            "bearing_wear":    {"psi": (945, 1040), "temp": (163, 183), "vib": (7.5, 13.5)},
        },
        "sensor_labels": {
            "psi": ("Discharge Pressure", "PSI"),
            "temp": ("Discharge Temp", "°F"),
            "vib": ("Frame Vibration", "mm/s"),
        },
    },

    "mud_pump": {
        "description": "Triplex Mud Pump — Drilling rig",
        "classes": ["normal", "pulsation_dampener_failure", "valve_washout", "piston_seal_wear"],
        "normal":  (2850, 90,  105, 5,   3.5, 0.4),
        "faults": {
            "pulsation_dampener_failure": (4200, 200, 138, 12, 22.0, 3.0),
            "valve_washout":              (2050, 90,  128, 10, 7.5, 1.0),
            "piston_seal_wear":           (2150, 90,  168, 12, 6.5, 0.9),
        },
        "gradual_faults": ["valve_washout", "piston_seal_wear"],
        "instant_faults":  ["pulsation_dampener_failure"],
        "rul_primary": {
            "pulsation_dampener_failure": ("vib",  "above", 20.0),
            "valve_washout":              ("psi",  "below", 1800.0),
            "piston_seal_wear":           ("temp", "above", 180.0),
        },
        "normal_ranges": {"psi": (2550, 3150), "temp": (90, 120), "vib": (2.5, 4.5)},
        "fault_ranges": {
            "pulsation_dampener_failure": {"psi": (3800, 4600), "temp": (120, 158), "vib": (15.0, 28.0)},
            "valve_washout":              {"psi": (1800, 2400), "temp": (115, 145), "vib": (5.0, 10.0)},
            "piston_seal_wear":           {"psi": (1900, 2450), "temp": (155, 190), "vib": (5.5, 8.5)},
        },
        "sensor_labels": {
            "psi": ("Discharge Pressure", "PSI"),
            "temp": ("Fluid End Temp", "°F"),
            "vib": ("Module Vibration", "mm/s"),
        },
    },

    "top_drive": {
        "description": "Top Drive — Drilling rig rotary system",
        "classes": ["normal", "gearbox_bearing_spalling", "hydraulic_leak"],
        "normal":  (3000, 55,  148, 5,   2.8, 0.3),
        "faults": {
            "gearbox_bearing_spalling": (2950, 55,  198, 12, 15.5, 2.0),
            "hydraulic_leak":           (1900, 90,  182, 12, 5.0, 0.7),
        },
        "gradual_faults": ["gearbox_bearing_spalling", "hydraulic_leak"],
        "instant_faults":  [],
        "rul_primary": {
            "gearbox_bearing_spalling": ("vib",  "above", 15.0),
            "hydraulic_leak":           ("psi",  "below", 2000.0),
        },
        "normal_ranges": {"psi": (2840, 3160), "temp": (130, 165), "vib": (1.8, 3.8)},
        "fault_ranges": {
            "gearbox_bearing_spalling": {"psi": (2850, 3060), "temp": (175, 222), "vib": (11.0, 20.0)},
            "hydraulic_leak":           {"psi": (1700, 2150), "temp": (158, 208), "vib": (3.5, 7.0)},
        },
        "sensor_labels": {
            "psi": ("Hydraulic Pressure", "PSI"),
            "temp": ("Gearbox Oil Temp", "°F"),
            "vib": ("Gearbox Vibration", "mm/s"),
        },
    },
}


# ── Data Generation ────────────────────────────────────────────────────────────
def gen_classifier_data(profile: dict, n_normal: int = 5000, n_fault: int = 1500) -> tuple:
    """Generate classifier training data (PSI, Temp, Vib → fault label)."""
    rows, labels = [], []
    nr = profile["normal_ranges"]

    # Normal readings
    for _ in range(n_normal):
        psi = np.random.uniform(*nr["psi"])
        temp = np.random.uniform(*nr["temp"])
        vib = np.random.uniform(*nr["vib"])
        rows.append([psi, temp, vib])
        labels.append(0)

    # Fault readings
    classes = profile["classes"][1:]  # skip normal
    for i, fault_name in enumerate(classes):
        fr = profile["fault_ranges"][fault_name]
        for _ in range(n_fault):
            psi  = np.random.uniform(*fr["psi"])
            temp = np.random.uniform(*fr["temp"])
            vib  = np.random.uniform(*fr["vib"])
            # Add noise
            psi  += np.random.normal(0, abs(psi * 0.02))
            temp += np.random.normal(0, abs(temp * 0.01))
            vib  += np.random.normal(0, abs(vib * 0.05))
            rows.append([psi, temp, vib])
            labels.append(i + 1)

    X = np.array(rows, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)
    idx = np.random.permutation(len(X))
    return X[idx], y[idx]


def gen_rul_data(profile: dict, n_trajectories: int = 400) -> tuple:
    """
    Generate RUL regressor training data.
    Each trajectory is a gradual degradation from normal to fault.
    Features: [psi, temp, vib, dpsi, dtemp, dvib]
    Label: RUL in minutes
    """
    rows, rul_vals = [], []
    nr = profile["normal_ranges"]

    # Add stable normal trajectories (RUL = very large → capped at 600min)
    for _ in range(n_trajectories // 3):
        steps = 40
        psi_prev = np.random.uniform(*nr["psi"])
        temp_prev = np.random.uniform(*nr["temp"])
        vib_prev  = np.random.uniform(*nr["vib"])
        for step in range(steps):
            psi  = psi_prev  + np.random.normal(0, nr["psi"][1] * 0.01)
            temp = temp_prev + np.random.normal(0, nr["temp"][1] * 0.01)
            vib  = max(0.05, vib_prev + np.random.normal(0, nr["vib"][1] * 0.01))
            dpsi  = (psi - psi_prev) / 5.0   # per minute
            dtemp = (temp - temp_prev) / 5.0
            dvib  = (vib - vib_prev) / 5.0
            rows.append([psi, temp, vib, dpsi, dtemp, dvib])
            rul_vals.append(600.0)  # nominal: not heading to failure
            psi_prev, temp_prev, vib_prev = psi, temp, vib

    # Gradual fault trajectories
    for fault_name in profile["gradual_faults"]:
        fr = profile["fault_ranges"][fault_name]
        for _ in range(n_trajectories):
            # Total steps to failure: 30-80 (each step = 5 minutes → 150–400 minutes TTF)
            total_steps = np.random.randint(30, 80)
            # Starting point: normal operating conditions
            psi_start  = np.random.uniform(*nr["psi"])
            temp_start = np.random.uniform(*nr["temp"])
            vib_start  = np.random.uniform(*nr["vib"])
            # Ending point: fault conditions
            psi_end  = np.random.uniform(*fr["psi"])
            temp_end = np.random.uniform(*fr["temp"])
            vib_end  = np.random.uniform(*fr["vib"])

            psi_prev  = psi_start
            temp_prev = temp_start
            vib_prev  = vib_start

            for step in range(total_steps):
                t = (step + 1) / total_steps   # 0→1 degradation fraction
                psi  = psi_start  + t * (psi_end  - psi_start)  + np.random.normal(0, abs(psi_start * 0.015))
                temp = temp_start + t * (temp_end - temp_start) + np.random.normal(0, abs(temp_start * 0.008))
                vib  = max(0.05, vib_start + t * (vib_end - vib_start) + np.random.normal(0, abs(vib_start * 0.04)))
                dpsi  = (psi - psi_prev) / 5.0
                dtemp = (temp - temp_prev) / 5.0
                dvib  = (vib - vib_prev) / 5.0
                rul = max(0.0, (total_steps - step - 1) * 5.0)
                rows.append([psi, temp, vib, dpsi, dtemp, dvib])
                rul_vals.append(rul)
                psi_prev, temp_prev, vib_prev = psi, temp, vib

    # Instant fault readings with very low RUL (0-5 min)
    for fault_name in profile["instant_faults"]:
        fr = profile["fault_ranges"][fault_name]
        for _ in range(n_trajectories // 2):
            psi  = np.random.uniform(*fr["psi"])
            temp = np.random.uniform(*fr["temp"])
            vib  = np.random.uniform(*fr["vib"])
            rows.append([psi, temp, vib, 0.0, 0.0, 0.0])
            rul_vals.append(np.random.uniform(0.0, 5.0))

    X = np.array(rows, dtype=np.float32)
    y = np.array(rul_vals, dtype=np.float32)
    idx = np.random.permutation(len(X))
    return X[idx], y[idx]


# ── Model Training ─────────────────────────────────────────────────────────────
def train_classifier(X: np.ndarray, y: np.ndarray, n_classes: int, asset_class: str) -> xgb.Booster:
    """Train a multi-class XGBoost classifier."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=["psi", "temp_f", "vibration"])
    dtest  = xgb.DMatrix(X_test,  label=y_test,  feature_names=["psi", "temp_f", "vibration"])

    params = {
        "objective":        "multi:softprob",
        "num_class":        n_classes,
        "max_depth":        6,
        "learning_rate":    0.1,
        "n_estimators":     200,
        "subsample":        0.85,
        "colsample_bytree": 0.85,
        "eval_metric":      ["mlogloss", "merror"],
        "seed":             42,
        "verbosity":        0,
    }
    evals_result = {}
    booster = xgb.train(
        params, dtrain, num_boost_round=200,
        evals=[(dtrain, "train"), (dtest, "test")],
        evals_result=evals_result,
        early_stopping_rounds=15,
        verbose_eval=False,
    )

    # Evaluate
    preds = booster.predict(dtest)
    pred_labels = preds.reshape(-1, n_classes).argmax(axis=1)
    from sklearn.metrics import accuracy_score
    acc = accuracy_score(y_test, pred_labels)
    print(f"    Accuracy: {acc:.4f}")
    return booster


def train_rul_regressor(X: np.ndarray, y: np.ndarray, asset_class: str) -> xgb.Booster:
    """Train an XGBoost RUL regressor."""
    feature_names = ["psi", "temp_f", "vibration", "dpsi_dt", "dtemp_dt", "dvib_dt"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_names)
    dtest  = xgb.DMatrix(X_test,  label=y_test,  feature_names=feature_names)

    params = {
        "objective":        "reg:squarederror",
        "max_depth":        6,
        "learning_rate":    0.08,
        "subsample":        0.85,
        "colsample_bytree": 0.85,
        "eval_metric":      "rmse",
        "seed":             42,
        "verbosity":        0,
    }
    booster = xgb.train(
        params, dtrain, num_boost_round=300,
        evals=[(dtrain, "train"), (dtest, "test")],
        early_stopping_rounds=20,
        verbose_eval=False,
    )

    # Evaluate
    preds = booster.predict(dtest)
    mae = mean_absolute_error(y_test, preds)
    print(f"    MAE: {mae:.1f} min")
    return booster


# ── GCS Upload ─────────────────────────────────────────────────────────────────
def upload_model_to_gcs(booster: xgb.Booster, model_name: str, bucket_name: str) -> None:
    """Save model to a temp file and upload to GCS at the standard inference-api path."""
    try:
        from google.cloud import storage as gcs
        client = gcs.Client()
        bucket = client.bucket(bucket_name)
        gcs_path = f"{model_name}/latest/model.bst"

        with tempfile.NamedTemporaryFile(suffix=".bst", delete=False) as tmp:
            tmp_path = tmp.name

        booster.save_model(tmp_path)
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(tmp_path)
        os.unlink(tmp_path)
        print(f"    ✅ Uploaded to gs://{bucket_name}/{gcs_path}")
    except Exception as e:
        print(f"    ⚠️  GCS upload failed: {e}")
        print(f"       (Model saved locally only)")


def save_model_locally(booster: xgb.Booster, filename: str) -> None:
    """Save model as UBJ file to fault-trigger-ui/models/ directory."""
    path = MODELS_DIR / filename
    booster.save_model(str(path))
    print(f"    ✅ Saved locally to {path}")


# ── Metadata File ──────────────────────────────────────────────────────────────
def save_metadata() -> None:
    """Save asset class sensor label metadata for the fault-trigger-ui to use."""
    import json
    metadata = {}
    for ac, prof in ASSET_PROFILES.items():
        metadata[ac] = {
            "sensor_labels": prof["sensor_labels"],
            "gradual_faults": prof["gradual_faults"],
            "instant_faults": prof["instant_faults"],
            "rul_primary": prof["rul_primary"],
            "normal_ranges": prof["normal_ranges"],
            "fault_ranges": prof["fault_ranges"],
        }
    meta_path = MODELS_DIR / "asset_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✅ Saved asset metadata to {meta_path}")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Seed O&G training data and train XGBoost models for all 4 asset classes.")
    parser.add_argument("--bucket", default=DEFAULT_BUCKET,
                        help=f"GCS bucket for classifier models (default: {DEFAULT_BUCKET})")
    parser.add_argument("--no-gcs", action="store_true",
                        help="Skip GCS upload (local files only)")
    parser.add_argument("--rows", type=int, default=5000,
                        help="Normal rows per classifier (default: 5000)")
    args = parser.parse_args()

    print("\n" + "="*70)
    print("  GDC-PM — O&G Domain Model Training")
    print("  Training XGBoost Classifier + RUL Regressor per asset class")
    print("="*70)

    for asset_class, profile in ASSET_PROFILES.items():
        print(f"\n{'─'*70}")
        print(f"  Asset Class: {asset_class.upper().replace('_', ' ')}")
        print(f"  {profile['description']}")
        print(f"  Fault Classes: {', '.join(profile['classes'])}")
        print()

        # ── Classifier ───────────────────────────────────────────────────────
        print(f"  [1/2] Training Fault Classifier ({len(profile['classes'])} classes)...")
        X_clf, y_clf = gen_classifier_data(profile, n_normal=args.rows, n_fault=1500)
        print(f"        Dataset: {len(X_clf)} rows")
        clf = train_classifier(X_clf, y_clf, len(profile["classes"]), asset_class)

        clf_name = f"{asset_class}_classifier"
        if not args.no_gcs:
            upload_model_to_gcs(clf, clf_name, args.bucket)
        save_model_locally(clf, f"{clf_name}.bst")

        # ── RUL Regressor ─────────────────────────────────────────────────────
        print(f"\n  [2/2] Training RUL Regressor...")
        X_rul, y_rul = gen_rul_data(profile, n_trajectories=400)
        print(f"        Dataset: {len(X_rul)} rows | RUL range: {y_rul.min():.0f}–{y_rul.max():.0f} min")
        rul = train_rul_regressor(X_rul, y_rul, asset_class)

        rul_name = f"{asset_class}_rul"
        if not args.no_gcs:
            upload_model_to_gcs(rul, rul_name, args.bucket)
        save_model_locally(rul, f"{rul_name}.ubj")

    # ── Metadata ──────────────────────────────────────────────────────────────
    print(f"\n  Saving asset metadata...")
    save_metadata()

    print("\n" + "="*70)
    print("  ✅ All 8 models trained and saved.")
    print(f"  RUL models in: {MODELS_DIR}")
    print(f"  Classifier models in GCS: gs://{args.bucket}/")
    print()
    print("  Next steps:")
    print("   1. Rebuild and redeploy the inference-api:")
    print("      (update app.py to route esp/gas_lift/mud_pump/top_drive)")
    print("   2. Rebuild and redeploy the fault-trigger-ui:")
    print("      (Dockerfile now copies gke/fault-trigger-ui/models/)")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
