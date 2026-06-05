"""
gke/shared/fault_signatures.py
===============================
CANONICAL ESP fault signature table — single source of truth.

This module is the authoritative definition of what each ESP fault class looks
like in 8-dimensional sensor space. Every training script, verification script,
and simulator profile must agree with the ranges defined here.

When a live FAULT_PROFILE is changed in app.py, update this table first;
training follows.

Sources:
  - gas_lock:       API RP 11S §5, Baker Hughes Centrilift Gas Handling Design Guide
                    71,794 live DB rows: avg PSI 971, avg vib 3.04 mm/s
  - slug_flow:      SPE-174536-MS §3.4; vib widened to 4.0–6.5 for H2 story credibility
  - motor_overheat: API RP 11S §4.2, IEEE 117 (Class H insulation 356°F / 180°C)
  - sand_ingress:   SPE-192586-MS (progressive impeller erosion)

Version: Session U (June 5, 2026) — matches FAULT_PROFILES in app.py after slug_flow fix
"""

# ── Nominal (healthy) operating point ─────────────────────────────────────────
# Ground-truthed against 931,652 live DB rows.
ESP_NOMINAL = {
    "psi":  1400.0,   # PSI (live avg 1,400)
    "temp": 198.0,    # °F  (live avg 198)
    "vib":  1.40,     # mm/s (live avg 1.40)
    "amps": 75.0,     # A   (live avg 75, simulator uses gauss(75,6))
}

# ── Normal operating ranges ────────────────────────────────────────────────────
ESP_NORMAL_RANGES = {
    "psi":      (1200, 1600),
    "temp":     (180,  220),
    "vib":      (0.8,  2.0),
    "amps":     (60,   90),
    "dpsi_dt":  (-2.0, 2.0),
    "dtemp_dt": (-0.1, 0.1),
    "dvib_dt":  (-0.05, 0.05),
    "damps_dt": (-0.2, 0.2),
}

# ── Canonical fault-signature table ───────────────────────────────────────────
# Features: [psi, temp_f, vibration, motor_amps,
#            dpsi_dt, dtemp_dt, dvib_dt, damps_dt]
#
# These are MID-RAMP signatures (what the classifier sees during an active
# fault injection), NOT end-of-failure catastrophic values.
#
# Each entry maps to a class index in the ESP classifier:
#   0 = normal        (see ESP_NORMAL_RANGES above)
#   1 = gas_lock
#   2 = sand_ingress
#   3 = motor_overheat
#   4 = slug_flow

ESP_FAULT_SIGNATURES = {
    # ── Class 1: Gas Lock ────────────────────────────────────────────────────
    # Impeller stages fill with gas (GVF > 65%) → pump unloads.
    # PSI crashes (mid-ramp: 875–1,100 from live injection data, NOT 350–800
    # catastrophic endpoint), amps drop, temp rises as motor loses cooling flow.
    # Primary discriminators: dpsi_dt strongly negative + damps_dt negative together.
    # Reference: API RP 11S §5; live DB avg 971 PSI over 71,794 gas_lock rows.
    "gas_lock": {
        "psi":      (875,  1100),   # mid-ramp: live injection range, NOT stall endpoint
        "temp":     (195,  210),    # early thermal rise as cooling flow collapses
        "vib":      (2.0,  3.5),    # cavitation onset (matches FAULT_PROFILES)
        "amps":     (20,   45),     # motor unloads as pump stops doing hydraulic work
        "dpsi_dt":  (-60.0, -8.0),  # rapidly declining PSI — the primary flag
        "dtemp_dt": (0.5,  6.0),    # rising: 3–8°F/min per API RP 11S motor thermal model
        "dvib_dt":  (0.2,  2.5),    # increasing cavitation vibration
        "damps_dt": (-8.0, -1.0),   # declining current (pump unloading)
        "class_idx": 1,
    },

    # ── Class 2: Sand Ingress ────────────────────────────────────────────────
    # Formation sand erodes impeller stages over days–weeks.
    # Gradual PSI + amps decline, slow vib + temp rise (impeller erosion heat).
    # Both vib AND temp rise distinguishes this from slug_flow (temp flat).
    # Reference: SPE-192586-MS (progressive impeller erosion signatures).
    "sand_ingress": {
        "psi":      (1050, 1500),
        "temp":     (200,  255),    # slowly rising — impeller erosion heat
        "vib":      (3.5,  10.0),   # worn clearances → rising vibration
        "amps":     (42,   72),     # declining as pump efficiency drops
        "dpsi_dt":  (-5.0, -0.5),
        "dtemp_dt": (0.3,  2.5),    # RISES (contrast with slug_flow: flat)
        "dvib_dt":  (0.05, 0.6),
        "damps_dt": (-1.5, -0.1),
        "class_idx": 2,
    },

    # ── Class 3: Motor Overheat ──────────────────────────────────────────────
    # Downhole cooling degradation → winding temp climbs toward Class H limit.
    # Temperature is the PRIMARY signal; PSI/vib relatively stable early.
    # Critical limit: 356°F / 180°C (API RP 11S, IEEE 117, NEMA MG-1 Part 3).
    "motor_overheat": {
        "psi":      (1200, 1560),
        "temp":     (240,  295),    # ELEVATED at rest — primary class signal
        "vib":      (2.0,  5.5),    # mild thermal-expansion vibration
        "amps":     (82,   110),    # overcurrent as motor fights rising winding resistance
        "dpsi_dt":  (-2.0, 0.5),
        "dtemp_dt": (1.5,  7.0),    # STRONG positive slope — primary discriminator
        "dvib_dt":  (0.01, 0.15),
        "damps_dt": (0.3,  3.0),    # rising current
        "class_idx": 3,
    },

    # ── Class 4: Slug Flow ───────────────────────────────────────────────────
    # Surface flowline slug flow transmits hydraulic impulses through production
    # tubing to the downhole vibration sensor. THE PUMP IS MECHANICALLY SOUND.
    #
    # KEY DISCRIMINATING SIGNATURE vs ALL other classes:
    #   vibration: ELEVATED (4.0–6.5 mm/s)
    #   temperature: COMPLETELY FLAT (dtemp_dt ≈ 0)
    #   PSI: nominally stable (surface phenomenon, not pump degradation)
    #   amps: nominally stable (pump running fine hydraulically)
    #
    # Vib range 4.0–6.5 rationale: SPE-174536-MS §3.4 — slug impulses in 2-3/8"
    # production tubing. Widened from live FAULT_PROFILES (2.2–3.2) because the
    # H2 demo requires a credible "vibration alarm" that clearly separates from
    # normal (0.8–2.0). Still below gas_lock cavitation (typically 5–13 mm/s).
    # Temperature-flatness (dtemp_dt ≈ 0) remains the primary discriminator
    # regardless of vibration level.
    # Reference: SPE-174536-MS §3.4, ESP OEM troubleshooting guides.
    "slug_flow": {
        "psi":      (1180, 1580),   # nominally stable (surface origin)
        "temp":     (182,  212),    # FLAT — stays in normal range (KEY DISCRIMINATOR)
        "vib":      (4.0,  6.5),    # ELEVATED from slug impulses
        "amps":     (60,   88),     # nominally stable (pump healthy)
        "dpsi_dt":  (-4.0, 4.0),    # minor oscillation from slug periodicity
        "dtemp_dt": (-0.08, 0.08),  # ≈ ZERO — THE discriminating feature vs all other faults
        "dvib_dt":  (0.15, 1.5),    # rising/elevated vibration rate
        "damps_dt": (-0.4, 0.4),    # stable current
        "class_idx": 4,
    },
}

# ── Class index map (must match inference-api MODEL_CONFIGS["esp"]["label_map"]) ──
ESP_LABEL_MAP = {
    0: "normal",
    1: "gas_lock",
    2: "sand_ingress",
    3: "motor_overheat",
    4: "slug_flow",
}

ESP_FEATURE_NAMES = [
    "psi", "temp_f", "vibration", "motor_amps",
    "dpsi_dt", "dtemp_dt", "dvib_dt", "damps_dt",
]

# ── Canonical training parameters (from MODEL_FOUNDATIONS.md §5A) ─────────────
TRAINING_PARAMS = {
    "n_normal":       6000,   # larger normal class matches live DB ratio (~93% normal)
    "n_trajectories": 600,    # per fault class; 600 × ~55 steps ≈ 33,000 rows each
    "steps_min":      30,     # min ramp steps per trajectory
    "steps_max":      80,     # max ramp steps per trajectory (30–80 matches live 150–1500s)
    "k_min":          3.0,    # exponent range for exponential ramp ((i+1)/steps)^k
    "k_max":          4.0,
    "slope_window":   12,     # readings for slope computation: 12 × 5s = 60s
    "warmup_steps":   12,     # skip first N steps until slope history is valid
    "noise_frac":     0.015,  # 1.5% relative sensor noise
    "max_rounds":     300,
    "learning_rate":  0.08,
    "max_depth":      6,
    "early_stopping": 20,
    "seed":           42,
    # Pass/fail thresholds for non-circular verification (MODEL_FOUNDATIONS §6)
    "min_precision_gas_lock":    0.92,
    "min_precision_slug_flow":   0.90,
    "min_recall_slug_flow":      0.85,
    "max_fp_slug_vs_sand":       0.08,
    "min_precision_normal":      0.95,
}
