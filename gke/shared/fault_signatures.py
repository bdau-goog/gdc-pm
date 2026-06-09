"""
gke/shared/fault_signatures.py
===============================
CANONICAL ESP fault signature table — single source of truth.

This module is the authoritative definition of what each ESP fault class looks
like in 8-dimensional sensor space. Every training script, verification script,
and simulator profile must agree with the ranges defined here.

**Source of truth hierarchy (Session W):**
  app.py FAULT_PROFILES  ←  this file  ←  train_classifiers.py
  (injected reality)         (canon)       (model training)

When FAULT_PROFILES in app.py changes, update this file first; training follows.
When this file changes, run train_classifiers.py to regenerate the model.

Sources:
  - gas_lock:       API RP 11S §5, Baker Hughes Centrilift Gas Handling Design Guide
                    71,794 live DB rows: avg PSI 971, avg vib 3.04 mm/s
  - slug_flow:      SPE-174536-MS §3.4; vib 4.0–6.5 for H2 story credibility
  - motor_overheat: API RP 11S §4.2, IEEE 117 (Class H insulation 356°F / 180°C)
  - sand_ingress:   SPE-192586-MS (progressive impeller erosion)

Version: Session W (June 5, 2026)
  - Endpoint ranges reconciled to app.py FAULT_PROFILES (single source of truth)
  - ESP_NOISE dict added (per-sensor σ from simulator.py + degrade thread)
  - Normal-class training now uses steady-state 60-window trajectories (not flat bands)
  - Changes: sand_ingress psi/temp/vib/amps; motor_overheat psi/temp/vib/amps; slug_flow psi/temp/amps
"""

# ── Nominal (healthy) operating point ─────────────────────────────────────────
# Ground-truthed against 931,652 live DB rows.
ESP_NOMINAL = {
    "psi":  1400.0,   # PSI (live avg 1,400)
    "temp": 198.0,    # °F  (live avg 198)
    "vib":  1.40,     # mm/s (live avg 1.40)
    "amps": 75.0,     # A   (live avg 75, simulator uses gauss(75,6))
}

# ── Per-sensor noise specification ────────────────────────────────────────────
# Normal-class noise: ABSOLUTE σ from simulator.py:normal_reading()
# Fault-ramp noise:   FRACTIONAL σ from app.py:_run_degrade_thread()
# These are imported by train_classifiers.py so training exactly reproduces
# what the live system emits. Do NOT change without updating both sources.
ESP_NOISE = {
    # Normal steady-state absolute σ — from simulator.py lines 103–106
    "psi_sigma":    65.0,    # random.gauss(1400, 65)
    "temp_sigma":   8.0,     # random.gauss(198, 8)
    "vib_sigma":    0.18,    # random.gauss(1.4, 0.18)  [absolute, NOT fractional]
    "amps_sigma":   6.0,     # random.gauss(75.0, 6.0)
    # Fault ramp fractional σ — from app.py _run_degrade_thread lines 1920–1922
    "fault_psi_frac":   0.02,   # round(random.gauss(psi, abs(psi * 0.02)), 1)
    "fault_temp_frac":  0.01,   # round(random.gauss(temp, abs(temp * 0.01)), 1)
    "fault_vib_frac":   0.05,   # round(max(0.05, random.gauss(vib, abs(vib * 0.05))), 3)
    "fault_amps_frac":  0.01,   # round(max(10.0, random.gauss(amps, abs(amps * 0.01))), 1)
}

# ── Normal operating ranges ────────────────────────────────────────────────────
# Used for documentation and the process alarm boundary check; NOT used for
# normal-class slope generation (see TRAINING_PARAMS["normal_gen"] below).
ESP_NORMAL_RANGES = {
    "psi":      (1200, 1600),
    "temp":     (180,  220),
    "vib":      (0.8,  2.0),
    "amps":     (60,   90),
    # Slope ranges represent noise-induced spread at the 60-reading (5-min) window.
    # Computed as: σ(delta_sensor) / dt_minutes where σ(delta) = √2 × sensor_sigma
    # and dt_minutes = (60−1)/12 ≈ 4.92 min.
    # dpsi_dt:  √2 × 65 / 4.92 ≈ ±18.7 PSI/min (3σ band: ±56)
    # dtemp_dt: √2 × 8  / 4.92 ≈ ±2.3  °F/min  (3σ band: ±6.9)
    # dvib_dt:  √2 × 0.18 / 4.92 ≈ ±0.052 mm/s/min
    # damps_dt: √2 × 6  / 4.92 ≈ ±1.7  A/min   (3σ band: ±5.2)
    "dpsi_dt":  (-56.0, 56.0),   # 3σ noise band at full 60-window — NOT flat ±2 !
    "dtemp_dt": (-6.9,  6.9),
    "dvib_dt":  (-0.16, 0.16),
    "damps_dt": (-5.2,  5.2),
}

# ── Canonical fault-signature table ───────────────────────────────────────────
# Features: [psi, temp_f, vibration, motor_amps,
#            dpsi_dt, dtemp_dt, dvib_dt, damps_dt]
#
# ENDPOINT ranges: what the live degrade thread ramps to (from app.py FAULT_PROFILES).
# These are MID-RAMP to HOLD-PHASE values, NOT instantaneous-failure catastrophic values.
# amps_end: MIDPOINT of amps range (matching app.py line 1843: midpoint of fault range).
#
# SLOPE ranges: representative values at the HOLD PHASE (sensors at fault endpoint,
# only noise-driven slopes remaining). These are documentation references;
# training slopes are computed live from the trajectory via _compute_slopes().
#
# Class index map:
#   0 = normal        (see ESP_NORMAL_RANGES above)
#   1 = gas_lock
#   2 = sand_ingress
#   3 = motor_overheat
#   4 = slug_flow

ESP_FAULT_SIGNATURES = {
    # ── Class 1: Gas Lock ────────────────────────────────────────────────────
    # Impeller stages fill with gas (GVF > 65%) → pump unloads.
    # PIP crashes to 400–600 PSI (casing annulus depleted / gas voids in stages).
    # Amps drop to 20–45 A (motor underload as impellers fill with gas/vapor).
    # Winding temp rises to 245–265°F (thermal runaway — cooling fluid flow collapses).
    # Vibration rises to 4.5–6.5 mm/s (intense downhole cavitation during stage unloading).
    # PRIMARY DISCRIMINATORS: dpsi_dt strongly negative + damps_dt negative TOGETHER.
    # amps_end = midpoint(20,45) = 32.5 A (matches app.py degrade thread).
    # Sources: API RP 11S §4.2 / §7.2; SPE-174536-MS. Updated Session S (June 9, 2026).
    # NOTE: fluid_drawdown has IDENTICAL sensor trajectory — only RAG context distinguishes them.
    "gas_lock": {
        "psi":      (400,  600),    # API RP 11S §7.2: casing annulus depleted, gas voids in stages
        "temp":     (245,  265),    # API RP 11S §4.2: thermal runaway, motor cooling flow collapses
        "vib":      (4.5,  6.5),    # SPE-174536-MS: intense downhole cavitation during stage unloading
        "amps":     (20,   45),     # API RP 11S §7.2: motor underload; amps_end_for_training = 32.5 (midpoint)
        "dpsi_dt":  (-60.0, -8.0),  # rapidly declining PSI — the primary flag
        "dtemp_dt": (0.5,  6.0),    # rising: 3–8°F/min per API RP 11S motor thermal model
        "dvib_dt":  (0.2,  2.5),    # increasing cavitation vibration
        "damps_dt": (-8.0, -1.0),   # declining current (pump unloading)
        "class_idx": 1,
    },

    # ── Class 2: Sand Ingress ────────────────────────────────────────────────
    # Formation sand erodes impeller stages over days–weeks.
    # BOTH vib AND temp rise → distinguishes from slug_flow (temp flat).
    # H2 "confuser": vibration rises but so does temperature — not a surface issue.
    # Reference: SPE-192586-MS (progressive impeller erosion signatures).
    # RECONCILED to app.py FAULT_PROFILES (Session W): psi (1100,1250) temp (210,240)
    # vib (4.5,9.5) amps (45,65). Previous fault_signatures had (1050,1500)/(3.5,10.0).
    "sand_ingress": {
        "psi":      (1100, 1250),   # FAULT_PROFILES: psi_range (1100,1250)
        "temp":     (210,  240),    # FAULT_PROFILES: temp_range (210,240); slowly rising
        "vib":      (4.5,  9.5),    # FAULT_PROFILES: vib_range (4.5,9.5); worn clearances
        "amps":     (45,   65),     # FAULT_PROFILES: amps_range (45,65); amps_end = 55.0
        "dpsi_dt":  (-5.0, -0.5),   # gradual decline (slow erosion)
        "dtemp_dt": (0.3,  2.5),    # RISES — contrast with slug_flow (FLAT); H2 discriminator
        "dvib_dt":  (0.05, 0.6),
        "damps_dt": (-1.5, -0.1),
        "class_idx": 2,
    },

    # ── Class 3: Motor Overheat ──────────────────────────────────────────────
    # Downhole cooling degradation → winding temp climbs toward Class H limit.
    # Temperature is the PRIMARY signal; PSI/vib relatively stable early.
    # Critical limit: 356°F / 180°C (API RP 11S, IEEE 117, NEMA MG-1 Part 3).
    # RECONCILED to app.py FAULT_PROFILES (Session W): psi (1300,1400) temp (265,295)
    # vib (1.0,2.0) amps (88,105). Previous fault_signatures had (1200,1560)/(2.0,5.5).
    "motor_overheat": {
        "psi":      (1300, 1400),   # FAULT_PROFILES: psi_range (1300,1400); nominally stable
        "temp":     (265,  295),    # FAULT_PROFILES: temp_range (265,295); ELEVATED primary
        "vib":      (1.0,  2.0),    # FAULT_PROFILES: vib_range (1.0,2.0); low (no mechanical)
        "amps":     (88,   105),    # FAULT_PROFILES: amps_range (88,105); amps_end = 96.5
        "dpsi_dt":  (-2.0, 0.5),
        "dtemp_dt": (1.5,  7.0),    # STRONG positive — primary discriminator
        "dvib_dt":  (0.01, 0.15),
        "damps_dt": (0.3,  3.0),    # rising current (motor overcurrent)
        "class_idx": 3,
    },

    # ── Class 4: Slug Flow ───────────────────────────────────────────────────
    # Surface flowline slug flow → hydraulic impulses through production tubing.
    # THE PUMP IS MECHANICALLY SOUND. H2 discrimination story.
    #
    # KEY DISCRIMINATING SIGNATURE vs ALL other classes:
    #   vibration: ELEVATED (4.0–6.5 mm/s) — slug impulses
    #   temperature: COMPLETELY FLAT (dtemp_dt ≈ 0) — pump not thermally stressed
    #   PSI: nominally stable (surface phenomenon, not pump degradation)
    #   amps: nominally stable (pump running fine hydraulically)
    #
    # RECONCILED to app.py FAULT_PROFILES (Session W): psi (1300,1500) temp (190,205)
    # amps (70,80). vib already matched (4.0,6.5). Previous: psi (1180,1580) amps (60,88).
    # Reference: SPE-174536-MS §3.4, ESP OEM troubleshooting guides.
    "slug_flow": {
        "psi":      (1300, 1500),   # FAULT_PROFILES: psi_range (1300,1500); nominally stable
        "temp":     (190,  205),    # FAULT_PROFILES: temp_range (190,205); FLAT (key signal)
        "vib":      (4.0,  6.5),    # FAULT_PROFILES: vib_range (4.0,6.5); ELEVATED slugs
        "amps":     (70,   80),     # FAULT_PROFILES: amps_range (70,80); amps_end = 75.0
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
    "n_normal":       24000,  # 24k normal vs ~38k fault/class; tuned so gas_lock precision ≥0.92
    "n_trajectories": 600,    # per fault class; 600 × ~43 steps ≈ 26,000 rows each
    "steps_min":      30,     # min ramp steps per trajectory
    "steps_max":      80,     # max ramp steps per trajectory (30–80 matches live 150–1500s)
    "k_min":          3.0,    # exponent range for exponential ramp ((i+1)/steps)^k
    "k_max":          4.0,
    "slope_window":   60,     # 60-reading deque × 5s = 300s (5 min) — matches processor.py
    "warmup_steps":   12,     # skip first N fault-ramp steps until slope history valid
    # Normal class: generated via 60-reading steady-state trajectory (NOT flat bands).
    # See gen_esp_classifier_data_trajectory() — uses ESP_NOISE absolute σ to reproduce
    # the live noise-induced slope spread (dpsi_dt σ≈18.7 PSI/min at full 60-window).
    "normal_window":  60,     # readings per normal sample (steady-state simulation)
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
