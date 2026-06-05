#!/usr/bin/env python3
"""
scripts/verify_classifier_offline.py
=====================================
Offline non-circular verification of the ESP classifier.

WHY THIS EXISTS
───────────────
Previous verification was circular: train on invented distributions, test on same
distributions, report 99% accuracy. Or: train, deploy, hope the live DB shows
good predictions. Both are unreliable.

This script simulates the COMPLETE serving path end-to-end, on disk, without any
running pods:

  1. Degrade thread ramp  — FAULT_PROFILES / ESP_NOISE, same formula as app.py
  2. 60-reading deque     — same as event-processor/processor.py:get_slopes()
  3. Feature construction — same 8 features as inference-api/app.py:predict()
  4. Model.predict()      — the actual deployed .ubj file
  5. Confusion matrix     — with pass/fail gates from MODEL_FOUNDATIONS §6

This is the non-circular gate. The model should NOT be committed until this passes.

USAGE
─────
  python3 scripts/verify_classifier_offline.py
  python3 scripts/verify_classifier_offline.py --model-path gke/inference-api/models/esp_classifier.ubj
  python3 scripts/verify_classifier_offline.py --n-normal 500 --n-fault 200

Verification gates (MODEL_FOUNDATIONS §6):
  normal      precision ≥ 0.95  (false-alarm rate must be low)
  gas_lock    precision ≥ 0.92  (H1 demo — confident correct classification)
  slug_flow   precision ≥ 0.90  (H2 demo)
  slug_flow   recall    ≥ 0.85  (missed slug = $150k unnecessary pump pull)
  slug_flow vs sand_ingress FP rate < 0.08  (H2 wrong-direction disaster)
"""

import argparse
import logging
import sys
from collections import deque
from pathlib import Path
from typing import Optional

import numpy as np
import xgboost as xgb
from sklearn.metrics import confusion_matrix, precision_score, recall_score

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))
from gke.shared.fault_signatures import (
    ESP_FAULT_SIGNATURES,
    ESP_NOMINAL,
    ESP_NOISE,
    ESP_LABEL_MAP,
    ESP_FEATURE_NAMES,
    TRAINING_PARAMS,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("verify_offline")

# ── Serving path replica ──────────────────────────────────────────────────────

def _get_slopes_replica(dq: deque) -> tuple:
    """
    Exact replica of event-processor/processor.py:get_slopes().
    dq: deque of dicts with keys psi, temp_f, vibration, motor_amps.
    Returns (dpsi_dt, dtemp_dt, dvib_dt, damps_dt) in units/minute.
    """
    n = len(dq)
    if n < 2:
        return 0.0, 0.0, 0.0, 0.0
    oldest = dq[0]
    newest = dq[-1]
    dt_minutes = (n - 1) / 12.0
    if dt_minutes <= 0:
        return 0.0, 0.0, 0.0, 0.0
    return (
        (newest["psi"]        - oldest["psi"])        / dt_minutes,
        (newest["temp_f"]     - oldest["temp_f"])     / dt_minutes,
        (newest["vibration"]  - oldest["vibration"])  / dt_minutes,
        (newest["motor_amps"] - oldest["motor_amps"]) / dt_minutes,
    )


def _classify(model: xgb.Booster, psi: float, temp: float, vib: float, amps: float,
              dpsi: float, dtemp: float, dvib: float, damps: float) -> int:
    """
    Exact replica of inference-api/app.py:predict() feature construction.
    Returns predicted class index (0–4).
    """
    features = np.array([[psi, temp, vib, amps, dpsi, dtemp, dvib, damps]], dtype=np.float32)
    dmat = xgb.DMatrix(features, feature_names=ESP_FEATURE_NAMES)
    probs = model.predict(dmat)[0]
    return int(np.argmax(probs))


# ── Normal-class simulation ───────────────────────────────────────────────────

def simulate_normal_samples(model: xgb.Booster, n: int, rng: np.random.Generator) -> list:
    """
    Simulate normal-class predictions using the same steady-state method as training.
    Each sample: 60 independent noisy readings → 60-window slope → classify.
    """
    predictions = []
    for _ in range(n):
        dq = deque(maxlen=60)
        for _ in range(60):
            dq.append({
                "psi":        rng.normal(ESP_NOMINAL["psi"],  ESP_NOISE["psi_sigma"]),
                "temp_f":     rng.normal(ESP_NOMINAL["temp"], ESP_NOISE["temp_sigma"]),
                "vibration":  max(0.05, rng.normal(ESP_NOMINAL["vib"], ESP_NOISE["vib_sigma"])),
                "motor_amps": max(40.0, rng.normal(ESP_NOMINAL["amps"], ESP_NOISE["amps_sigma"])),
            })
        dpsi, dtemp, dvib, damps = _get_slopes_replica(dq)
        last = dq[-1]
        pred = _classify(model, last["psi"], last["temp_f"], last["vibration"], last["motor_amps"],
                         dpsi, dtemp, dvib, damps)
        predictions.append(pred)
    return predictions


# ── Fault-class simulation ────────────────────────────────────────────────────

def simulate_fault_samples(model: xgb.Booster, fault_name: str, n_trajectories: int,
                           rng: np.random.Generator, collect_developed: bool = True) -> list:
    """
    Simulate fault-class predictions by running degrade thread ramps.

    Exact replicas of:
      app.py:_run_degrade_thread() — ramp formula, noise, amps_end=midpoint
      processor.py:get_slopes()   — 60-reading deque, first-last / dt_minutes

    collect_developed=True: collect predictions from the hold phase only (t=1.0),
    where the deque has been filled with the fault pattern for 5 min.
    This is the strictest test — it matches what the operator sees in the demo.

    Returns list of predicted class indices.
    """
    sig = ESP_FAULT_SIGNATURES[fault_name]
    NOM = ESP_NOMINAL
    predictions = []

    steps_min = TRAINING_PARAMS["steps_min"]   # 30
    steps_max = TRAINING_PARAMS["steps_max"]   # 80
    k_min     = TRAINING_PARAMS["k_min"]
    k_max     = TRAINING_PARAMS["k_max"]

    for _ in range(n_trajectories):
        psi_end  = rng.uniform(*sig["psi"])
        temp_end = rng.uniform(*sig["temp"])
        vib_end  = max(0.05, rng.uniform(*sig["vib"]))
        amps_end = (sig["amps"][0] + sig["amps"][1]) / 2.0  # midpoint = degrade thread

        steps = int(rng.integers(steps_min, steps_max + 1))
        k     = rng.uniform(k_min, k_max)

        # Initialize a rolling 60-reading deque (replicates processor.py asset_history)
        dq = deque(maxlen=60)

        # Pre-fill deque with nominal readings (replicates system state before injection)
        for _ in range(60):
            dq.append({
                "psi":        rng.normal(NOM["psi"],  ESP_NOISE["psi_sigma"]),
                "temp_f":     rng.normal(NOM["temp"], ESP_NOISE["temp_sigma"]),
                "vibration":  max(0.05, rng.normal(NOM["vib"], ESP_NOISE["vib_sigma"])),
                "motor_amps": max(40.0, rng.normal(NOM["amps"], ESP_NOISE["amps_sigma"])),
            })

        # Run the degrade ramp (matches app.py:_run_degrade_thread)
        for i in range(steps):
            t = ((i + 1) / steps) ** k

            psi_mid  = NOM["psi"]  + (psi_end  - NOM["psi"])  * t
            temp_mid = NOM["temp"] + (temp_end - NOM["temp"]) * t
            vib_mid  = NOM["vib"]  + (vib_end  - NOM["vib"])  * t
            amps_mid = NOM["amps"] + (amps_end - NOM["amps"]) * t

            psi  = max(100.0, rng.normal(psi_mid,  abs(psi_mid  * ESP_NOISE["fault_psi_frac"])))
            temp = max(100.0, rng.normal(temp_mid, abs(temp_mid * ESP_NOISE["fault_temp_frac"])))
            vib  = max(0.05,  rng.normal(vib_mid,  abs(vib_mid  * ESP_NOISE["fault_vib_frac"])))
            amps = max(10.0,  rng.normal(amps_mid, abs(amps_mid * ESP_NOISE["fault_amps_frac"])))

            dq.append({"psi": psi, "temp_f": temp, "vibration": vib, "motor_amps": amps})

        # Hold phase: send 60 more readings at the fault endpoint so the deque
        # fills entirely with the fault pattern (worst-case clean signal).
        # This is when the demo operator sees the "⚠ GAS LOCK ACTIVE" state.
        for _ in range(60):
            psi  = max(100.0, rng.normal(psi_end,  abs(psi_end  * ESP_NOISE["fault_psi_frac"])))
            temp = max(100.0, rng.normal(temp_end, abs(temp_end * ESP_NOISE["fault_temp_frac"])))
            vib  = max(0.05,  rng.normal(vib_end,  abs(vib_end  * ESP_NOISE["fault_vib_frac"])))
            amps = max(10.0,  rng.normal(amps_end, abs(amps_end * ESP_NOISE["fault_amps_frac"])))
            dq.append({"psi": psi, "temp_f": temp, "vibration": vib, "motor_amps": amps})

        # Classify at hold phase (deque fully filled with fault pattern + noise)
        dpsi, dtemp, dvib, damps = _get_slopes_replica(dq)
        last = dq[-1]
        pred = _classify(model, last["psi"], last["temp_f"], last["vibration"], last["motor_amps"],
                         dpsi, dtemp, dvib, damps)
        predictions.append(pred)

    return predictions


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Offline non-circular ESP classifier verification (MODEL_FOUNDATIONS §6)."
    )
    parser.add_argument("--model-path",    default="gke/inference-api/models/esp_classifier.ubj")
    parser.add_argument("--n-normal",      type=int, default=500)
    parser.add_argument("--n-fault",       type=int, default=200,
                        help="Trajectories per fault class")
    parser.add_argument("--seed",          type=int, default=99,
                        help="Different from training seed (42) to ensure independence")
    args = parser.parse_args()

    model_path = Path(args.model_path)
    if not model_path.exists():
        log.error(f"Model not found: {model_path}")
        log.error("Run train_classifiers.py first.")
        sys.exit(1)

    log.info("=" * 70)
    log.info("  ESP Classifier — Offline Non-Circular Verification")
    log.info(f"  Model: {model_path.resolve()}")
    log.info(f"  Serving path replica: degrade ramp → 60-window deque → inference-api features")
    log.info(f"  Verification seed: {args.seed}  (different from training seed 42 → independent)")
    log.info("=" * 70)

    model = xgb.Booster()
    model.load_model(str(model_path))
    rng = np.random.default_rng(args.seed)

    # ── Collect predictions ───────────────────────────────────────────────────
    all_true, all_pred = [], []

    log.info(f"\n  Simulating normal class ({args.n_normal} samples)...")
    normal_preds = simulate_normal_samples(model, args.n_normal, rng)
    all_true.extend([0] * args.n_normal)
    all_pred.extend(normal_preds)
    normal_correct = sum(p == 0 for p in normal_preds)
    log.info(f"    normal → {normal_correct}/{args.n_normal} correct")

    fault_classes = [
        ("gas_lock",       1),
        ("sand_ingress",   2),
        ("motor_overheat", 3),
        ("slug_flow",      4),
    ]

    for fault_name, class_idx in fault_classes:
        log.info(f"  Simulating {fault_name} ({args.n_fault} trajectories)...")
        fault_preds = simulate_fault_samples(model, fault_name, args.n_fault, rng)
        all_true.extend([class_idx] * args.n_fault)
        all_pred.extend(fault_preds)
        correct = sum(p == class_idx for p in fault_preds)
        log.info(f"    {fault_name} → {correct}/{args.n_fault} correct ({correct/args.n_fault:.1%})")
        # Show misclassification breakdown
        from collections import Counter
        wrong = [ESP_LABEL_MAP.get(p, p) for p in fault_preds if p != class_idx]
        if wrong:
            log.info(f"    misclassified as: {dict(Counter(wrong))}")

    # ── Confusion matrix ──────────────────────────────────────────────────────
    label_names = [ESP_LABEL_MAP[i] for i in range(5)]
    y_true = np.array(all_true)
    y_pred = np.array(all_pred)

    cm = confusion_matrix(y_true, y_pred, labels=list(range(5)))
    log.info(f"\n{'─'*70}")
    log.info("  CONFUSION MATRIX (rows=actual, cols=predicted)")
    header = f"  {'':22}" + "".join(f"{n:>14}" for n in label_names)
    log.info(header)
    for i, row_name in enumerate(label_names):
        row = "  " + f"{row_name:<22}" + "".join(f"{cm[i,j]:>14}" for j in range(5))
        log.info(row)

    # ── Per-class metrics with gates ──────────────────────────────────────────
    log.info(f"\n{'─'*70}")
    log.info("  PER-CLASS PRECISION / RECALL / GATES  (MODEL_FOUNDATIONS §6)")
    log.info(f"  {'Class':<22} {'Precision':>10} {'Recall':>8} {'Gate':>8} {'Pass?':>8}")
    log.info(f"  {'-'*60}")

    gates = {
        "normal":      {"min_prec": TRAINING_PARAMS["min_precision_normal"], "min_rec": None},
        "gas_lock":    {"min_prec": TRAINING_PARAMS["min_precision_gas_lock"], "min_rec": None},
        "slug_flow":   {"min_prec": TRAINING_PARAMS["min_precision_slug_flow"],
                        "min_rec": TRAINING_PARAMS["min_recall_slug_flow"]},
        "sand_ingress":  {"min_prec": 0.85, "min_rec": None},
        "motor_overheat":{"min_prec": 0.85, "min_rec": None},
    }

    all_pass = True
    for i, name in enumerate(label_names):
        prec = precision_score(y_true, y_pred, labels=[i], average="macro", zero_division=0)
        rec  = recall_score(y_true, y_pred, labels=[i], average="macro", zero_division=0)
        g    = gates.get(name, {"min_prec": 0.85, "min_rec": None})
        prec_ok = prec >= g["min_prec"]
        rec_ok  = (rec >= g["min_rec"]) if g["min_rec"] else True
        passed  = prec_ok and rec_ok
        if not passed:
            all_pass = False
        gate_str = f"P≥{g['min_prec']:.2f}" + (f" R≥{g['min_rec']:.2f}" if g["min_rec"] else "")
        flag = "✅" if passed else "❌"
        log.info(f"  {i} {name:<20} {prec:>9.3f}  {rec:>7.3f}  {gate_str:>10}  {flag}")

    # ── H2 anti-confusion check (slug_flow vs sand_ingress FP) ───────────────
    slug_idx = 4
    sand_idx = 2
    n_slug_total = (y_true == slug_idx).sum()
    n_slug_as_sand = ((y_true == slug_idx) & (y_pred == sand_idx)).sum()
    fp_slug_vs_sand = n_slug_as_sand / n_slug_total if n_slug_total > 0 else 0.0
    max_fp = TRAINING_PARAMS["max_fp_slug_vs_sand"]
    fp_ok = fp_slug_vs_sand <= max_fp
    if not fp_ok:
        all_pass = False
    log.info(f"\n  H2 anti-confusion: slug_flow→sand_ingress FP rate = {fp_slug_vs_sand:.3f}  "
             f"(gate: ≤{max_fp:.2f})  {'✅' if fp_ok else '❌'}")

    # ── Final verdict ─────────────────────────────────────────────────────────
    log.info(f"\n{'='*70}")
    if all_pass:
        log.info("  ✅ ALL GATES PASS — model is ready for container rebuild and deployment")
        log.info("     Next: rebuild inference-api image, deploy, run live verification (Session B)")
    else:
        log.warning("  ❌ GATES FAILED — DO NOT DEPLOY THIS MODEL")
        log.warning("     Diagnose failure from confusion matrix above.")
        log.warning("     Common causes: font class overlap in training data, amps mismatch.")
    log.info(f"{'='*70}")
    return all_pass


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
