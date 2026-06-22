#!/usr/bin/env python3
"""
BS+37: Apply trajectory realism improvements to H1 and H2 replay generators in app.py.

Changes per sensor-realism audit:
  H1:
    1. Independent k exponents: k_amps = k * U(0.70, 0.90)  — Amps softer than PIP
    2. AR(1) autocorrelated noise: rho=0.65, preserves marginal sigma
    3. Sigmoid lag onset: smooth S-curve replaces hard corner at _LAG_ONSET=0.55

  H2:
    1. Independent k exponents: k_vib, k_amps, k_psi — per-channel physics rates
    2. AR(1) autocorrelated noise: same rho=0.65

No model retrain needed: AR(1) noise preserves marginal sigma; slope features
over 20-step windows are minimally affected. Independent k only modestly changes
damps_dt; health model still detects the decline. Verify gdc_detect_idx < alarm_idx
after deploy.
"""

import re
import sys

APP_PY = "gke/fault-trigger-ui/app.py"

with open(APP_PY, "r", encoding="utf-8") as f:
    src = f.read()

original = src  # keep for diff check

# ──────────────────────────────────────────────────────────────────────────────
# H1 CHANGE 1: Add k_amps after the k = random.uniform(1.2, 2.5) line
# The target line is unique — only one occurrence of random.uniform(1.2, 2.5) in
# the h1_scenario_replay function context.
# ──────────────────────────────────────────────────────────────────────────────
OLD_K_LINE = '    k      = random.uniform(1.2, 2.5)   # ramp shape exponent (same as degrade thread)'
NEW_K_LINE = (
    '    k      = random.uniform(1.2, 2.5)   # PIP ramp shape exponent\n'
    '    k_amps = k * random.uniform(0.70, 0.90)   # Amps: softer ramp (hydraulic head leads, current follows)'
)

if OLD_K_LINE in src:
    src = src.replace(OLD_K_LINE, NEW_K_LINE, 1)
    print("H1 change 1 (k_amps): APPLIED")
else:
    print("H1 change 1 (k_amps): NOT FOUND — skipping")

# ──────────────────────────────────────────────────────────────────────────────
# H1 CHANGE 2: Replace the loop body (from list initialization through t_min_arr.append)
# Use the unique psi_arr initializer as the anchor.
# ──────────────────────────────────────────────────────────────────────────────
OLD_LOOP_H1 = (
    '    psi_arr, amps_arr, temp_arr, vib_arr, t_min_arr = [], [], [], [], []\n'
    '    for i in range(N):\n'
    '        frac = ((i + 1) / N) ** k                  # leading fraction \u2014 PIP, Amps\n'
    '        u    = (i + 1) / N                          # normalised position 0\u21921\n'
    '        lag_u    = 0.0 if u < _LAG_ONSET else (u - _LAG_ONSET) / (1.0 - _LAG_ONSET)\n'
    '        lag_frac = lag_u ** k                       # lagging fraction \u2014 Temp, Vib\n'
    '        psi_arr.append(  round(psi_nom  + (psi_end  - psi_nom)  * frac     + random.gauss(0, 18),  1))\n'
    '        amps_arr.append( round(amps_nom + (amps_end - amps_nom) * frac     + random.gauss(0, 1.5), 2))\n'
    '        temp_arr.append( round(temp_nom + (temp_end - temp_nom) * lag_frac + random.gauss(0, 1.2), 1))\n'
    '        vib_arr.append(  round(vib_nom  + (vib_end  - vib_nom)  * lag_frac + random.gauss(0, 0.1), 3))\n'
    '        t_min_arr.append(round(i * t_step, 2))'
)

NEW_LOOP_H1 = (
    '    # AR(1) autocorrelated noise: n_t = rho*n_{t-1} + sqrt(1-rho^2)*eps_t\n'
    '    # Marginal sigma unchanged; adjacent steps correlated (realistic historian appearance).\n'
    '    # rho=0.65 -> correlation < 0.1 beyond ~5 steps; 20-step slope features minimally affected.\n'
    '    _rho = 0.65\n'
    '    _ar  = math.sqrt(1.0 - _rho ** 2)\n'
    '    _psi_n = _amps_n = _temp_n = _vib_n = 0.0\n'
    '    psi_arr, amps_arr, temp_arr, vib_arr, t_min_arr = [], [], [], [], []\n'
    '    for i in range(N):\n'
    '        u         = (i + 1) / N\n'
    '        frac_psi  = u ** k           # PIP: base exponent (leading indicator)\n'
    '        frac_amps = u ** k_amps      # Amps: softer ramp (hydraulic lag before current responds)\n'
    '        # Sigmoid lag onset replaces hard corner at _LAG_ONSET:\n'
    '        #   ~0 for u << 0.55, smooth S-curve through 0.55, ~1 for u >> 0.55\n'
    '        lag_u    = 1.0 / (1.0 + math.exp(-14.0 * (u - _LAG_ONSET)))\n'
    '        lag_frac = lag_u ** k\n'
    '        _psi_n  = _rho * _psi_n  + _ar * random.gauss(0, 18)\n'
    '        _amps_n = _rho * _amps_n + _ar * random.gauss(0, 1.5)\n'
    '        _temp_n = _rho * _temp_n + _ar * random.gauss(0, 1.2)\n'
    '        _vib_n  = _rho * _vib_n  + _ar * random.gauss(0, 0.1)\n'
    '        psi_arr.append(  round(psi_nom  + (psi_end  - psi_nom)  * frac_psi  + _psi_n,  1))\n'
    '        amps_arr.append( round(amps_nom + (amps_end - amps_nom) * frac_amps + _amps_n, 2))\n'
    '        temp_arr.append( round(temp_nom + (temp_end - temp_nom) * lag_frac  + _temp_n, 1))\n'
    '        vib_arr.append(  round(vib_nom  + (vib_end  - vib_nom)  * lag_frac  + _vib_n,  3))\n'
    '        t_min_arr.append(round(i * t_step, 2))'
)

if OLD_LOOP_H1 in src:
    src = src.replace(OLD_LOOP_H1, NEW_LOOP_H1, 1)
    print("H1 change 2 (AR(1) + sigmoid loop): APPLIED")
else:
    print("H1 change 2 (AR(1) + sigmoid loop): NOT FOUND — checking for em-dash variant")
    # Try with plain dash (—) instead of unicode em-dash (\u2014)
    OLD_LOOP_H1_ALT = OLD_LOOP_H1.replace('\u2014', '--').replace('\u2192', '->')
    if OLD_LOOP_H1_ALT in src:
        src = src.replace(OLD_LOOP_H1_ALT, NEW_LOOP_H1, 1)
        print("H1 change 2 (AR(1) + sigmoid loop) [alt]: APPLIED")
    else:
        # Search for just the psi_arr initializer line which is pure ASCII
        marker = '    psi_arr, amps_arr, temp_arr, vib_arr, t_min_arr = [], [], [], [], []'
        idx = src.find(marker)
        if idx >= 0:
            # Find the end of the for loop (the t_min_arr.append line)
            end_marker = '        t_min_arr.append(round(i * t_step, 2))'
            end_idx = src.find(end_marker, idx)
            if end_idx >= 0:
                old_block = src[idx:end_idx + len(end_marker)]
                src = src.replace(old_block, NEW_LOOP_H1, 1)
                print("H1 change 2 (AR(1) + sigmoid loop) [substring]: APPLIED")
            else:
                print("H1 change 2: END MARKER not found — SKIPPED")
        else:
            print("H1 change 2: psi_arr marker not found — SKIPPED")

# ──────────────────────────────────────────────────────────────────────────────
# H2 CHANGE 1: Add per-sensor k values after k = random.uniform(1.2, 2.0)
# The H2 function has `k = random.uniform(1.2, 2.0)` — unique to h2_scenario_replay
# (H1 uses 1.2, 2.5)
# ──────────────────────────────────────────────────────────────────────────────
OLD_K2_LINE = '    k         = random.uniform(1.2, 2.0)\n\n    # Nominal baselines'
NEW_K2_LINE = (
    '    k         = random.uniform(1.2, 2.0)   # base ramp exponent\n'
    '    k_vib     = k * random.uniform(1.00, 1.20)   # Vib leads (mechanical friction at restriction builds first)\n'
    '    k_amps    = k * random.uniform(0.80, 0.95)   # Amps softer (electrical response to hydraulic change)\n'
    '    k_psi     = k * random.uniform(0.85, 1.00)   # PIP rises with amps (backpressure balance)\n\n'
    '    # Nominal baselines'
)

if OLD_K2_LINE in src:
    src = src.replace(OLD_K2_LINE, NEW_K2_LINE, 1)
    print("H2 change 1 (per-sensor k): APPLIED")
else:
    print("H2 change 1 (per-sensor k): NOT FOUND — skipping")

# ──────────────────────────────────────────────────────────────────────────────
# H2 CHANGE 2: Replace H2 loop body with AR(1) + per-sensor fracs
# ──────────────────────────────────────────────────────────────────────────────
OLD_LOOP_H2 = (
    '    eff_arr, vib_arr, amps_arr, psi_arr, temp_arr, t_wk_arr = [], [], [], [], [], []\n'
    '    for i in range(N):\n'
    '        frac = 0.0 if i < onset_idx else ((i - onset_idx + 1) / max(1, N - onset_idx)) ** k\n'
    '        eff_arr.append( round(eff_nom  + (eff_end  - eff_nom)  * frac + random.gauss(0, 0.4),  2))\n'
    '        vib_arr.append( round(vib_nom  + (vib_end  - vib_nom)  * frac + random.gauss(0, 0.08), 3))\n'
    '        amps_arr.append(round(amps_nom + (amps_end - amps_nom) * frac + random.gauss(0, 0.5),  2))\n'
    '        psi_arr.append( round(psi_nom  + (psi_end  - psi_nom)  * frac + random.gauss(0, 18),   1))\n'
    '        temp_arr.append(round(temp_nom + (temp_end - temp_nom) * frac + random.gauss(0, 0.8),  1))\n'
    '        t_wk_arr.append(round(i * t_step, 2))'
)

NEW_LOOP_H2 = (
    '    # AR(1) autocorrelated noise (same sigma, locally correlated steps)\n'
    '    _rho = 0.65\n'
    '    _ar  = math.sqrt(1.0 - _rho ** 2)\n'
    '    _eff_n = _vib_n = _amps_n = _psi_n = _temp_n = 0.0\n'
    '    eff_arr, vib_arr, amps_arr, psi_arr, temp_arr, t_wk_arr = [], [], [], [], [], []\n'
    '    for i in range(N):\n'
    '        u_raw     = 0.0 if i < onset_idx else (i - onset_idx + 1) / max(1, N - onset_idx)\n'
    '        u_base    = min(1.0, u_raw)\n'
    '        frac_base = u_base ** k        # efficiency + temp: base exponent\n'
    '        frac_vib  = u_base ** k_vib    # vib leads slightly (mechanical restriction precedes electrical)\n'
    '        frac_amps = u_base ** k_amps   # amps softer (current responds to hydraulic change)\n'
    '        frac_psi  = u_base ** k_psi    # pip rises with amps (backpressure balance)\n'
    '        _eff_n  = _rho * _eff_n  + _ar * random.gauss(0, 0.4)\n'
    '        _vib_n  = _rho * _vib_n  + _ar * random.gauss(0, 0.08)\n'
    '        _amps_n = _rho * _amps_n + _ar * random.gauss(0, 0.5)\n'
    '        _psi_n  = _rho * _psi_n  + _ar * random.gauss(0, 18)\n'
    '        _temp_n = _rho * _temp_n + _ar * random.gauss(0, 0.8)\n'
    '        eff_arr.append( round(eff_nom  + (eff_end  - eff_nom)  * frac_base + _eff_n,  2))\n'
    '        vib_arr.append( round(vib_nom  + (vib_end  - vib_nom)  * frac_vib  + _vib_n,  3))\n'
    '        amps_arr.append(round(amps_nom + (amps_end - amps_nom) * frac_amps + _amps_n, 2))\n'
    '        psi_arr.append( round(psi_nom  + (psi_end  - psi_nom)  * frac_psi  + _psi_n,  1))\n'
    '        temp_arr.append(round(temp_nom + (temp_end - temp_nom) * frac_base + _temp_n, 1))\n'
    '        t_wk_arr.append(round(i * t_step, 2))'
)

if OLD_LOOP_H2 in src:
    src = src.replace(OLD_LOOP_H2, NEW_LOOP_H2, 1)
    print("H2 change 2 (AR(1) + per-sensor fracs loop): APPLIED")
else:
    print("H2 change 2 (AR(1) + per-sensor fracs loop): NOT FOUND — skipping")

# ──────────────────────────────────────────────────────────────────────────────
# Write back if changes were made
# ──────────────────────────────────────────────────────────────────────────────
if src != original:
    with open(APP_PY, "w", encoding="utf-8") as f:
        f.write(src)
    print(f"\nWrote {APP_PY} ({len(src) - len(original):+d} chars)")
else:
    print("\nNo changes were made — file unchanged.")
    sys.exit(1)
