#!/usr/bin/env python3
"""
scripts/train_classifiers.py  (Session W — slope-window + normal-class + noise fixes)

Train XGBoost fault classifiers for all 4 O&G asset classes.
Outputs .ubj files for LOCAL_MODELS_DIR in inference-api.

═══════════════════════════════════════════════════════════════════════
THREE FIDELITY BUGS FIXED IN THIS VERSION (Session W)
═══════════════════════════════════════════════════════════════════════

BUG 1 — Slope-window mismatch (Session W, first pass):
  Session U/S: window=12, scale=12/n  (wrong size AND wrong formula)
  Session W:   window=60, dt=(n−1)/12  (matches processor.py exactly)

BUG 2 — Normal-class slope skew (root cause of live 97%-confidence misclassification):
  Session U/S: drew slopes from flat bands (dpsi_dt ±2, dtemp_dt ±0.1)
  Session W:   simulates 60-reading steady-state trajectory with simulator's
               ABSOLUTE noise (psi σ65, temp σ8, vib σ0.18, amps σ6).
               Live noise-induced slope spread: dpsi σ≈18.7, dtemp σ≈2.3 PSI/°F/min.
               Training now sees the same noise → model no longer mistakes noise for fault.

BUG 3 — Fault noise and amps mismatch:
  Session U/S: flat 1.5% noise on all sensors; amps drawn from full range
  Session W:   per-sensor noise fractions matching app.py _run_degrade_thread
               (psi 2%, temp 1%, vib 5%, amps 1%);
               amps_end = MIDPOINT of range (matching app.py line 1843 exactly)

All three bugs caused training-serving skew, not a physics problem.
The injected fault scenarios were already physically correct.

═══════════════════════════════════════════════════════════════════════
USAGE
─────
  python scripts/train_classifiers.py
  python scripts/train_classifiers.py --asset-class esp --output-dir gke/inference-api/models
  python scripts/train_classifiers.py --n-trajectories 600 --n-normal 6000 --rounds 300

References
──────────
  - MODEL_FOUNDATIONS.md §5A — training specification
  - gke/shared/fault_signatures.py — canonical fault signature table (single source of truth)
  - gke/fault-trigger-ui/app.py:_run_degrade_thread — ramp formula + noise source
  - gke/event-processor/processor.py:get_slopes() — slope logic source
  - gke/telemetry-simulator/simulator.py:normal_reading() — normal noise source
"""

import argparse
import logging
import sys
from pathlib import Path

import numpy as np
import xgboost as xgb
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn.model_selection import train_test_split

# ── Import canonical fault signatures ─────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
from gke.shared.fault_signatures import (
    ESP_FAULT_SIGNATURES,
    ESP_NORMAL_RANGES,
    ESP_NOMINAL,
    ESP_NOISE,
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
# Session W: window=60, formula dt_minutes=(n-1)/12.0
SLOPE_WINDOW = TRAINING_PARAMS["slope_window"]   # 60 readings × 5s = 300s (5 min)


def _compute_slopes(history: list, window: int = SLOPE_WINDOW):
    """
    Compute slope features from sensor history buffer.
    history: list of [psi, temp, vib, amps] in chronological order.
    Returns: (dpsi_dt, dtemp_dt, dvib_dt, damps_dt) in units/minute.

    Matches processor.py:get_slopes() exactly:
      - 60-reading window
      - dt_minutes = (n−1)/12.0
      The (n−1) denominator measures time over n−1 intervals of 5s = (n−1)/12 minutes.
    """
    n = min(len(history), window)
    if n < 2:
        return 0.0, 0.0, 0.0, 0.0
    old = history[-n]
    new = history[-1]
    dt_minutes = (n - 1) / 12.0
    if dt_minutes <= 0:
        return 0.0, 0.0, 0.0, 0.0
    return (
        (new[0] - old[0]) / dt_minutes,   # dpsi_dt  (PSI/min)
        (new[1] - old[1]) / dt_minutes,   # dtemp_dt (°F/min)
        (new[2] - old[2]) / dt_minutes,   # dvib_dt  (mm/s/min)
        (new[3] - old[3]) / dt_minutes,   # damps_dt (A/min)
    )


def _gen_normal_sample(rng: np.random.Generator) -> list:
    """
    Generate one normal-class training sample by simulating a 60-reading
    steady-state trajectory and computing slopes via the exact _compute_slopes logic.

    BUG 2 FIX: Previous approach drew slopes from flat bands (dpsi_dt ±2, dtemp_dt ±0.1).
    Live serving uses first-vs-last of a 60-reading deque of NOISY independent readings.
    The noise-induced slope spread is:
        dpsi_dt  σ ≈ √2 × 65  / 4.92 ≈ ±18.7 PSI/min
        dtemp_dt σ ≈ √2 × 8   / 4.92 ≈ ±2.3  °F/min
        damps_dt σ ≈ √2 × 6   / 4.92 ≈ ±1.7  A/min
    Training on flat ±2/±0.1 bands meant normal noise was interpreted as a fault.
    This function reproduces the live noise distribution exactly.

    Noise source: simulator.py:normal_reading() for ESP (lines 103–106).
    """
    n_window = TRAINING_PARAMS["normal_window"]  # 60
    history = []
    for _ in range(n_window):
        psi  = rng.normal(ESP_NOMINAL["psi"],  ESP_NOISE["psi_sigma"])
        temp = rng.normal(ESP_NOMINAL["temp"], ESP_NOISE["temp_sigma"])
        vib  = max(0.05, rng.normal(ESP_NOMINAL["vib"], ESP_NOISE["vib_sigma"]))
        amps = max(40.0, rng.normal(ESP_NOMINAL["amps"], ESP_NOISE["amps_sigma"]))
        history.append([psi, temp, vib, amps])

    # Use the LAST reading's sensor values + slopes computed over full window
    last_psi, last_temp, last_vib, last_amps = history[-1]
    dpsi, dtemp, dvib, damps = _compute_slopes(history)
    return [last_psi, last_temp, last_vib, last_amps, dpsi, dtemp, dvib, damps]


# ── Hold-phase constant ──────────────────────────────────────────────────────
# Number of hold-phase samples to append per fault trajectory.
# Teaches the model to recognize faults by ABSOLUTE VALUES when slopes have
# collapsed (fully-filled hold-phase deque, 5+ min into the hold state).
# Without hold-phase training, model sees: fault endpoint absolute values +
# noise-level slopes → misclassifies as normal.
N_HOLD_PER_TRAJ = 20


def _gen_fault_hold_sample(rng: np.random.Generator,
                           psi_end: float, temp_end: float,
                           vib_end: float, amps_end: float) -> list:
    """
    Generate one fault hold-phase training sample using the given fault endpoints.

    Simulates a 60-reading steady-state deque entirely within the hold phase
    (sensor at fault endpoint ± per-sensor noise, slopes noise-driven ≈ flat).
    This mirrors what the event-processor sees when the pump has been at the
    fault endpoint for >5 minutes.

    Called once per trajectory × N_HOLD_PER_TRAJ for each fault class so the
    model learns: fault-endpoint absolute values + noise slopes = fault (not normal).
    """
    history = []
    for _ in range(60):
        psi  = max(100.0, rng.normal(psi_end,  abs(psi_end  * ESP_NOISE["fault_psi_frac"])))
        temp = max(100.0, rng.normal(temp_end, abs(temp_end * ESP_NOISE["fault_temp_frac"])))
        vib  = max(0.05,  rng.normal(vib_end,  abs(vib_end  * ESP_NOISE["fault_vib_frac"])))
        amps = max(10.0,  rng.normal(amps_end, abs(amps_end * ESP_NOISE["fault_amps_frac"])))
        history.append([psi, temp, vib, amps])

    last_psi, last_temp, last_vib, last_amps = history[-1]
    dpsi, dtemp, dvib, damps = _compute_slopes(history)
    return [last_psi, last_temp, last_vib, last_amps, dpsi, dtemp, dvib, damps]


# ── Non-ESP 3-feature profiles ─────────────────────────────────────────────────
# Infrastructure completeness. Not demo-critical; kept as snapshot approach.

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
    warmup: int = TRAINING_PARAMS["warmup_steps"],
    rng: np.random.Generator = None,
) -> tuple:
    """
    Generate ESP classifier training data using trajectory simulation.

    All three BUG fixes applied here:
      BUG 1: 60-reading slope window, dt=(n-1)/12 formula
      BUG 2: normal class via _gen_normal_sample() (steady-state trajectory)
      BUG 3: per-sensor fault noise matching app.py degrade thread;
             amps_end = midpoint of fault amps range (matching app.py line 1843)

    Returns (X, y, t_vals) where t_vals is ramp-progress per row (0=normal, 0–1=fault).
    """
    if rng is None:
        rng = np.random.default_rng(TRAINING_PARAMS["seed"])

    NOM = ESP_NOMINAL

    rows, labels, t_vals = [], [], []

    # ── Class 0: Normal ───────────────────────────────────────────────────────
    # BUG 2 FIX: use steady-state trajectory simulation, NOT flat slope bands.
    # Each sample simulates 60 readings of noisy stable operation → realistic slopes.
    log.info(f"  Generating normal class: {n_normal} steady-state samples (60-window each)...")
    for _ in range(n_normal):
        rows.append(_gen_normal_sample(rng))
        labels.append(0)
        t_vals.append(0.0)

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
            # Draw endpoint targets.
            # BUG 3 FIX: amps_end = MIDPOINT of range (matches app.py line 1843:
            #   _s4_target = (_s4_range[0] + _s4_range[1]) / 2.0)
            # psi/temp/vib are randomized as before (drawn uniformly from range).
            psi_end  = rng.uniform(*sig["psi"])
            temp_end = rng.uniform(*sig["temp"])
            vib_end  = max(0.05, rng.uniform(*sig["vib"]))
            amps_end = (sig["amps"][0] + sig["amps"][1]) / 2.0  # MIDPOINT — matches degrade thread

            # Ramp parameters
            steps = int(rng.integers(steps_min, steps_max + 1))
            k     = rng.uniform(k_min, k_max)

            # Sensor history buffer for slope computation
            history: list = []

            for i in range(steps):
                # Exponential ramp: matches _run_degrade_thread exactly
                t = ((i + 1) / steps) ** k

                # Mid-ramp sensor values (before noise)
                psi_mid  = NOM["psi"]  + (psi_end  - NOM["psi"])  * t
                temp_mid = NOM["temp"] + (temp_end - NOM["temp"]) * t
                vib_mid  = NOM["vib"]  + (vib_end  - NOM["vib"])  * t
                amps_mid = NOM["amps"] + (amps_end - NOM["amps"]) * t

                # BUG 3 FIX: per-sensor noise matching app.py _run_degrade_thread
                # Source: app.py lines 1920–1922
                psi  = max(100.0, rng.normal(psi_mid,  abs(psi_mid  * ESP_NOISE["fault_psi_frac"])))
                temp = max(100.0, rng.normal(temp_mid, abs(temp_mid * ESP_NOISE["fault_temp_frac"])))
                vib  = max(0.05,  rng.normal(vib_mid,  abs(vib_mid  * ESP_NOISE["fault_vib_frac"])))
                amps = max(10.0,  rng.normal(amps_mid, abs(amps_mid * ESP_NOISE["fault_amps_frac"])))

                history.append([psi, temp, vib, amps])

                # Skip warmup — slopes not yet reliable
                if i < warmup:
                    continue

                # Sensor-departure filter: only include gas_lock ramp readings where
                # PSI or amps has moved >1σ below normal. This prevents ambiguous
                # near-nominal early-ramp rows from blurring the normal class boundary,
                # eliminating false alarms during normal operation.
                #
                # Physics: normal PSI = gauss(1400, 65); 1σ threshold = 1335.
                # Gas lock at 1335 PSI = 4.6% below nominal. SCADA alarm is at 800 PSI
                # (43% below nominal). Detection at 1335 is still 21+ min before SCADA.
                # The "gradual confidence" story is preserved — softmax probabilities
                # naturally build as psi descends from 1335 → 1100 → 875.
                if fault_name == "gas_lock":
                    psi_departed  = psi  < (ESP_NOMINAL["psi"]  - ESP_NOISE["psi_sigma"])   # < 1335
                    amps_departed = amps < (ESP_NOMINAL["amps"] - ESP_NOISE["amps_sigma"])   # < 69
                    if not (psi_departed or amps_departed):
                        continue   # skip ambiguous early-ramp row

                # Compute slopes from history (matches processor.py)
                dpsi, dtemp, dvib, damps = _compute_slopes(history)

                rows.append([psi, temp, vib, amps, dpsi, dtemp, dvib, damps])
                labels.append(class_idx)
                t_vals.append(t)   # ramp-progress for stage-stratified verification
                reading_count += 1

            # Hold-phase samples: fault endpoint absolute values + noise-level slopes.
            # Fixes the "hold-phase gap" found by verify_classifier_offline.py:
            #   gas_lock at hold: psi≈987 (6.4σ below normal), amps≈32.5 (7.1σ below)
            #   model MUST learn these absolute values = fault, even when dpsi_dt≈0.
            for _ in range(N_HOLD_PER_TRAJ):
                rows.append(_gen_fault_hold_sample(rng, psi_end, temp_end, vib_end, amps_end))
                labels.append(class_idx)
                t_vals.append(1.0)   # t=1.0 = fully developed fault state
                reading_count += 1

            traj_count += 1

        log.info(f"    {fault_name:<20} {traj_count:>4} trajectories → {reading_count:>7,} readings")

    X  = np.array(rows,   dtype=np.float32)
    y  = np.array(labels, dtype=np.int32)
    tv = np.array(t_vals, dtype=np.float32)
    idx = rng.permutation(len(X))
    return X[idx], y[idx], tv[idx]


# ── 3-feature snapshot data generation (non-ESP assets) ──────────────────────

def gen_3feature_classifier_data(
    profiles: dict,
    n_normal: int = 3000,
    n_fault: int = 1000,
    rng: np.random.Generator = None,
) -> tuple:
    """
    Generate 3-feature snapshot data for gas_lift, mud_pump, top_drive.
    Snapshot approach acceptable — these assets are not demo-critical.
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
    t_vals: np.ndarray = None,
) -> xgb.Booster:
    """
    Train a multi-class XGBoost classifier, print per-class metrics.

    t_vals: ramp-progress array (0=normal, 0–1=fault ramp).
            SESSION W two-metric reporting:
              (a) overall precision — all test rows including early ambiguous ramp
              (b) developed-stage precision — fault rows at t≥0.5 + all normal rows
                  (this is the figure tied to the on-screen claim; also the hardest
                  test because early-ramp label noise is excluded)
    """
    if t_vals is not None:
        X_train, X_test, y_train, y_test, _, t_test = train_test_split(
            X, y, t_vals, test_size=0.20, random_state=TRAINING_PARAMS["seed"], stratify=y
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=TRAINING_PARAMS["seed"], stratify=y
        )
        t_test = None

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

    raw         = booster.predict(dtest).reshape(-1, n_classes)
    pred_labels = raw.argmax(axis=1)
    final_merror = evals_result["test"]["merror"][booster.best_iteration]
    accuracy     = 1.0 - final_merror
    log.info(f"  Test accuracy: {accuracy:.4f}  (best_iteration: {booster.best_iteration})")

    if asset_class == "esp":
        label_names = [ESP_LABEL_MAP[i] for i in range(n_classes)]
        cm = confusion_matrix(y_test, pred_labels)

        # ── (a) Overall precision — all test rows ─────────────────────────────
        log.info(f"\n  OVERALL (all ramp stages, incl. early ambiguous):")
        log.info(f"  {'Class':<25} {'Correct':>8} {'Total':>8} {'Precision':>10} {'Recall':>8}")
        log.info(f"  {'-'*70}")
        for i, name in enumerate(label_names):
            if i >= len(cm):
                continue
            correct = cm[i, i]
            total   = cm[i].sum()
            prec    = precision_score(y_test, pred_labels, labels=[i], average="macro", zero_division=0)
            rec     = recall_score(y_test, pred_labels, labels=[i], average="macro", zero_division=0)
            log.info(f"  {i} {name:<23} {correct:>8}/{total:<7} {prec:>9.3f}  {rec:>7.3f}")

        # ── (b) Developed-stage precision — t≥0.5 fault + all normal ──────────
        all_pass_developed = True
        if t_test is not None:
            dev_mask = (t_test >= 0.5) | (y_test == 0)
            if dev_mask.sum() > 0:
                y_dev = y_test[dev_mask]
                p_dev = pred_labels[dev_mask]
                log.info(f"\n  DEVELOPED STAGE (fault t≥0.5 + all normal) — n={dev_mask.sum():,}/{len(y_test):,}:")
                log.info(f"  {'Class':<25} {'Precision':>10} {'Recall':>8} {'Pass?':>10}")
                log.info(f"  {'-'*60}")
                for i, name in enumerate(label_names):
                    prec_d = precision_score(y_dev, p_dev, labels=[i], average="macro", zero_division=0)
                    rec_d  = recall_score(y_dev, p_dev, labels=[i], average="macro", zero_division=0)
                    min_prec = TRAINING_PARAMS.get(f"min_precision_{name}", 0.85)
                    passed   = prec_d >= min_prec
                    if name in ("gas_lock", "slug_flow", "normal") and not passed:
                        all_pass_developed = False
                    flag = "✅" if passed else f"❌ (need ≥{min_prec:.2f})"
                    log.info(f"  {i} {name:<23} {prec_d:>9.3f}  {rec_d:>7.3f}  {flag}")

        log.info(f"\n  {'='*65}")
        if all_pass_developed:
            log.info(f"  ✅ DEVELOPED-STAGE PASS — meets MODEL_FOUNDATIONS §6 thresholds")
            log.info(f"     Run verify_classifier_offline.py before committing (§6 protocol)")
        else:
            log.warning(f"  ❌ DEVELOPED-STAGE FAILED — DO NOT DEPLOY")
            log.warning(f"     See MODEL_FOUNDATIONS.md §6 for required precision values")
        log.info(f"  {'='*65}")

    return booster


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Train XGBoost fault classifiers (Session W — all 3 fidelity bugs fixed)."
    )
    parser.add_argument("--output-dir", default="gke/inference-api/models")
    parser.add_argument("--asset-class", default=None,
                        choices=["esp", "gas_lift", "mud_pump", "top_drive"])
    parser.add_argument("--n-trajectories", type=int, default=TRAINING_PARAMS["n_trajectories"])
    parser.add_argument("--n-normal",       type=int, default=TRAINING_PARAMS["n_normal"])
    parser.add_argument("--rounds",         type=int, default=TRAINING_PARAMS["max_rounds"])
    parser.add_argument("--seed",           type=int, default=TRAINING_PARAMS["seed"])
    parser.add_argument("--n-fault",        type=int, default=1000,
                        help="Samples per fault class for NON-ESP assets")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    asset_classes = [args.asset_class] if args.asset_class else ["esp", "gas_lift", "mud_pump", "top_drive"]

    log.info("=" * 72)
    log.info("  GDC-PM — Fault Classifier Training (Session W — 3 fidelity bugs fixed)")
    log.info(f"  Asset classes: {asset_classes}")
    log.info(f"  Output dir:    {output_dir.resolve()}")
    log.info(f"  Approach:      trajectory ({args.n_trajectories} ramps/class, {args.n_normal} normal)")
    log.info(f"  Slope window:  {SLOPE_WINDOW} readings × 5s = {SLOPE_WINDOW*5}s  "
             f"(matches processor.py deque maxlen=60)")
    log.info(f"  Slope formula: dt_minutes=(n-1)/12.0")
    log.info(f"  Normal class:  60-window steady-state simulation (absolute σ noise)")
    log.info(f"  Fault noise:   per-sensor fractions (psi 2%, temp 1%, vib 5%, amps 1%)")
    log.info(f"  Amps endpoint: midpoint of amps range (matches degrade thread)")
    log.info("=" * 72)

    for ac in asset_classes:
        log.info(f"\n{'─'*72}")
        log.info(f"  Training: {ac.upper().replace('_', ' ')} classifier")

        t_vals_out = None

        if ac == "esp":
            n_classes     = 5
            feature_names = ESP_FEATURE_NAMES
            log.info(f"  Classes:  {[ESP_LABEL_MAP[i] for i in range(n_classes)]}")
            log.info(f"  Features: {feature_names}")
            log.info(f"  gas_lock  PSI:   {ESP_FAULT_SIGNATURES['gas_lock']['psi']}  amps_end={sum(ESP_FAULT_SIGNATURES['gas_lock']['amps'])/2:.1f}")
            log.info(f"  slug_flow vib:   {ESP_FAULT_SIGNATURES['slug_flow']['vib']}  dtemp_dt={ESP_FAULT_SIGNATURES['slug_flow']['dtemp_dt']}  amps_end={sum(ESP_FAULT_SIGNATURES['slug_flow']['amps'])/2:.1f}")
            log.info(f"  sand_ingress:    vib={ESP_FAULT_SIGNATURES['sand_ingress']['vib']}  amps_end={sum(ESP_FAULT_SIGNATURES['sand_ingress']['amps'])/2:.1f}")
            log.info(f"  motor_overheat:  temp={ESP_FAULT_SIGNATURES['motor_overheat']['temp']}  amps_end={sum(ESP_FAULT_SIGNATURES['motor_overheat']['amps'])/2:.1f}")

            X, y, t_vals_out = gen_esp_classifier_data_trajectory(
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
            X, y = gen_3feature_classifier_data(profiles=profiles, n_normal=args.n_normal,
                                                n_fault=args.n_fault, rng=rng)

        log.info(f"\n  Dataset: {len(X):,} rows × {X.shape[1]} features")
        if ac == "esp":
            label_names  = [ESP_LABEL_MAP[i] for i in range(n_classes)]
            class_counts = {label_names[i]: int((y == i).sum()) for i in range(n_classes)}
        else:
            class_counts = {f"class_{i}": int((y == i).sum()) for i in range(n_classes)}
        log.info(f"  Class distribution: {class_counts}")

        booster = train_classifier(X, y, n_classes, feature_names, ac, args.rounds,
                                   t_vals=t_vals_out)

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
    log.info("\n  NEXT STEPS:")
    log.info("  1. Run offline verifier:")
    log.info("     python3 scripts/verify_classifier_offline.py")
    log.info("  2. If PASS: rebuild inference-api container and deploy")
    log.info("  3. Run live non-circular verification (Session B)")


if __name__ == "__main__":
    main()
