#!/usr/bin/env python3
"""
Sprint L1 patch — weight metadata migration.

Changes to app.py:
  1. _ensure_field_intel_table(): add ALTER TABLE IF NOT EXISTS for 6 new columns
  2. New _seed_h1_bayes_findings_bg() + thread launch (after H2 seed thread)
  3. _bayes_discriminate(): refactor to read from field_intel DB, fallback to _BAYES_FINDINGS

Run from project root:
  python3 scripts/sprint_l1_patch.py [--dry-run]
"""
import re, sys, pathlib

APP = pathlib.Path("gke/fault-trigger-ui/app.py")
dry_run = "--dry-run" in sys.argv

src = APP.read_text()

# ── helpers ──────────────────────────────────────────────────────────────────

def replace_once(text, search, replacement, label):
    if search not in text:
        print(f"  ❌  BLOCK '{label}' — SEARCH not found. Aborting.")
        sys.exit(1)
    count = text.count(search)
    if count > 1:
        print(f"  ⚠️  BLOCK '{label}' — search matched {count} times, using first.")
    result = text.replace(search, replacement, 1)
    print(f"  ✅  BLOCK '{label}' applied.")
    return result


# ── BLOCK 1: ADD ALTER TABLE columns in _ensure_field_intel_table() ──────────

B1_SEARCH = """\
                CREATE INDEX IF NOT EXISTS idx_field_intel_fault
                  ON field_intel(fault_context, created_at DESC);

                -- Fix 11b: fault_sessions audit log"""

B1_REPLACE = """\
                CREATE INDEX IF NOT EXISTS idx_field_intel_fault
                  ON field_intel(fault_context, created_at DESC);

                -- Sprint L1: Bayesian weight metadata columns (additive, backward-compatible)
                ALTER TABLE field_intel ADD COLUMN IF NOT EXISTS finding_code TEXT;
                ALTER TABLE field_intel ADD COLUMN IF NOT EXISTS lr_base      REAL;
                ALTER TABLE field_intel ADD COLUMN IF NOT EXISTS lr_min       REAL;
                ALTER TABLE field_intel ADD COLUMN IF NOT EXISTS lr_max       REAL;
                ALTER TABLE field_intel ADD COLUMN IF NOT EXISTS lr_source    TEXT;
                ALTER TABLE field_intel ADD COLUMN IF NOT EXISTS finding_dir  TEXT;

                -- Fix 11b: fault_sessions audit log"""

src = replace_once(src, B1_SEARCH, B1_REPLACE, "ALTER TABLE columns")


# ── BLOCK 2: New _seed_h1_bayes_findings_bg() after H2 seed thread ───────────

B2_SEARCH = 'threading.Thread(target=_seed_h2_static_docs_bg, daemon=True, name="h2-seed").start()'

B2_REPLACE = '''threading.Thread(target=_seed_h2_static_docs_bg, daemon=True, name="h2-seed").start()

# ── Sprint L1: H1 Bayesian evidence docs — seed into field_intel with LR metadata ─
# These rows supply _bayes_discriminate() when it queries the DB.
# Seeding is idempotent (checks existence first). Runs 40s after startup so that
# _ensure_field_intel_table() (triggered at ~10s by the intel-feed thread) has
# already created the new columns.
#
# Physics citations per row:
#   F1  API RP 11S §4.2  (gas lock requires free gas at impeller)
#   F2  API RP 11S §7.2  (gas accumulation builds casing back-pressure)
#   F3  API RP 11S §7.2  (gas-lock annulus stays flooded; drawdown depletes)
#   F4  production engineering standard (rising GOR = gas-lock precursor)
#
# LR bands are conservative ranges:
#   F1  [2.0, 4.5]  anchor 3.0
#   F2  [1.5, 3.0]  anchor 2.0
#   F3  [1.2, 2.5]  anchor 1.6
#   F4  [1.1, 2.0]  anchor 1.4
#
_H1_BAYES_SEED_DOCS = [
    # ── fluid_drawdown evidence ──────────────────────────────────────────────
    dict(
        asset_id="__h1_bayes_corpus__", asset_class="esp",
        fault_context="fluid_drawdown", doc_type="acoustic_survey",
        headline="Acoustic Survey — Free Gas at Intake: NONE DETECTED",
        detail=(
            "Permian Basin Acoustic Services — Well Survey Report\\n"
            "Survey Date: [dynamic] | Technician: field crew\\n\\n"
            "Free Gas at Pump Intake: NONE DETECTED\\n"
            "Fluid Level Above Pump: declining vs 72-hr baseline\\n"
            "Casing Pressure: flat or declining\\n"
            "Notes: No acoustic gas signature at intake depth. "
            "Fluid column declining consistent with reservoir depletion."
        ),
        ai_relevance="Absence of free gas at intake rules out gas lock as primary mechanism (API RP 11S §4.2).",
        icon="📋", lbl="FIELD DOC", lbl_type="static_seed",
        finding_code="F1", lr_base=3.0, lr_min=2.0, lr_max=4.5,
        lr_source="API RP 11S §4.2", finding_dir="drawdown",
    ),
    dict(
        asset_id="__h1_bayes_corpus__", asset_class="esp",
        fault_context="fluid_drawdown", doc_type="shift_note",
        headline="Shift Note — Casing Pressure: Flat / Declining",
        detail=(
            "RTOC Operator Shift Note — Tour 2\\n"
            "Casing pressure on Well A-3: flat to slightly declining over past 4 hours.\\n"
            "No casing pressure build observed. GVF not elevated.\\n"
            "Fluid level survey requested."
        ),
        ai_relevance="Flat casing pressure = no gas accumulation in annulus. Confirms reservoir drawdown, not gas lock (API RP 11S §7.2).",
        icon="📋", lbl="SHIFT NOTE", lbl_type="static_seed",
        finding_code="F2", lr_base=2.0, lr_min=1.5, lr_max=3.0,
        lr_source="API RP 11S §7.2", finding_dir="drawdown",
    ),
    dict(
        asset_id="__h1_bayes_corpus__", asset_class="esp",
        fault_context="fluid_drawdown", doc_type="acoustic_survey",
        headline="Acoustic Survey — Dynamic Fluid Level Declining",
        detail=(
            "Permian Basin Acoustic Services — Well Survey Report\\n"
            "Dynamic Fluid Level: declining vs 72-hr baseline (-42 ft trend).\\n"
            "Casing annulus: partially depleted above pump.\\n"
            "Notes: Fluid column reduction consistent with reservoir drawdown. "
            "Gas lock annulus would remain fully flooded."
        ),
        ai_relevance="Declining fluid column confirms casing depletion — gas lock annulus stays flooded (API RP 11S §7.2).",
        icon="📋", lbl="FIELD DOC", lbl_type="static_seed",
        finding_code="F3", lr_base=1.6, lr_min=1.2, lr_max=2.5,
        lr_source="API RP 11S §7.2", finding_dir="drawdown",
    ),
    dict(
        asset_id="__h1_bayes_corpus__", asset_class="esp",
        fault_context="fluid_drawdown", doc_type="separator_test",
        headline="Separator Test — GOR Nominal / Not Rising",
        detail=(
            "Permian Basin Field Operations — Separator Test Report\\n"
            "Test Date: [dynamic] | Duration: 2 hours\\n\\n"
            "Gas-Oil Ratio (GOR): nominal — no trend increase vs 30-day baseline.\\n"
            "Water Cut: stable.\\n"
            "Notes: Stable GOR with declining fluid level indicates reservoir depletion "
            "without active gas migration. Rising GOR would suggest gas-lock precursor."
        ),
        ai_relevance="Stable GOR rules out free-gas migration into pump stream — consistent with drawdown, not gas lock.",
        icon="📋", lbl="SEPARATOR TEST", lbl_type="static_seed",
        finding_code="F4", lr_base=1.4, lr_min=1.1, lr_max=2.0,
        lr_source="Production engineering standard", finding_dir="drawdown",
    ),
    # ── gas_lock evidence ────────────────────────────────────────────────────
    dict(
        asset_id="__h1_bayes_corpus__", asset_class="esp",
        fault_context="gas_lock", doc_type="shift_note",
        headline="Shift Note — GVF Elevated / Free Gas Observed at Intake",
        detail=(
            "RTOC Operator Shift Note — Tour 2\\n"
            "Well A-3: GVF estimated elevated based on casing pressure behaviour. "
            "Free gas at intake depth suspected (casing pressure building). "
            "VFD frequency trim being considered."
        ),
        ai_relevance="Free gas at intake directly confirms gas lock mechanism (API RP 11S §4.2). Casing annulus flooded.",
        icon="📋", lbl="SHIFT NOTE", lbl_type="static_seed",
        finding_code="F1", lr_base=3.0, lr_min=2.0, lr_max=4.5,
        lr_source="API RP 11S §4.2", finding_dir="gas_lock",
    ),
    dict(
        asset_id="__h1_bayes_corpus__", asset_class="esp",
        fault_context="gas_lock", doc_type="shift_note",
        headline="Shift Note — Casing Pressure Elevated and Rising",
        detail=(
            "RTOC Operator Shift Note — Tour 2\\n"
            "Casing pressure Well A-3: elevated +18 PSI above 72-hr baseline and trending upward. "
            "Consistent with gas accumulation in annulus above pump."
        ),
        ai_relevance="Rising casing pressure = gas accumulating in annulus — confirms gas lock mechanism (API RP 11S §7.2).",
        icon="📋", lbl="SHIFT NOTE", lbl_type="static_seed",
        finding_code="F2", lr_base=2.0, lr_min=1.5, lr_max=3.0,
        lr_source="API RP 11S §7.2", finding_dir="gas_lock",
    ),
    dict(
        asset_id="__h1_bayes_corpus__", asset_class="esp",
        fault_context="gas_lock", doc_type="shift_note",
        headline="Shift Note — Dynamic Fluid Level Stable (Annulus Flooded)",
        detail=(
            "RTOC Operator Shift Note — Tour 2\\n"
            "Fluid level estimate: stable vs 72-hr baseline. "
            "Casing annulus appears fully submerged. "
            "Pump intake below fluid contact."
        ),
        ai_relevance="Stable fluid level with annulus flooded confirms gas lock — drawdown would deplete the column (API RP 11S §7.2).",
        icon="📋", lbl="SHIFT NOTE", lbl_type="static_seed",
        finding_code="F3", lr_base=1.6, lr_min=1.2, lr_max=2.5,
        lr_source="API RP 11S §7.2", finding_dir="gas_lock",
    ),
    dict(
        asset_id="__h1_bayes_corpus__", asset_class="esp",
        fault_context="gas_lock", doc_type="separator_test",
        headline="Separator Test — GOR Elevated / Rising",
        detail=(
            "Permian Basin Field Operations — Separator Test Report\\n"
            "Gas-Oil Ratio (GOR): elevated +22% above 30-day baseline and trending upward. "
            "Separator gas rate increasing. "
            "Notes: Rising GOR consistent with free gas migration into pump intake stream — "
            "gas-lock precursor signature."
        ),
        ai_relevance="Rising GOR confirms free-gas migration into pump stream — gas lock precursor (production engineering standard).",
        icon="📋", lbl="SEPARATOR TEST", lbl_type="static_seed",
        finding_code="F4", lr_base=1.4, lr_min=1.1, lr_max=2.0,
        lr_source="Production engineering standard", finding_dir="gas_lock",
    ),
]


def _seed_h1_bayes_findings_bg() -> None:
    """
    Sprint L1: Seed H1 Bayesian evidence docs into field_intel with LR metadata.
    Idempotent — checks for existing rows before inserting.
    Runs 40s after startup to allow _ensure_field_intel_table() to create columns first.
    """
    import time as _time_mod
    _time_mod.sleep(40)
    try:
        conn = _get_db_conn()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM field_intel WHERE asset_id = '__h1_bayes_corpus__'"
            )
            existing = cur.fetchone()[0]
            if existing >= len(_H1_BAYES_SEED_DOCS):
                log.info(f"✅ H1 Bayesian evidence docs already seeded ({existing} rows).")
                conn.close()
                return
            # Clear any partial seed and re-insert cleanly
            cur.execute("DELETE FROM field_intel WHERE asset_id = '__h1_bayes_corpus__'")
            for doc in _H1_BAYES_SEED_DOCS:
                cur.execute(
                    """
                    INSERT INTO field_intel
                      (asset_id, asset_class, fault_context, doc_type,
                       headline, detail, ai_relevance, icon, lbl, lbl_type,
                       finding_code, lr_base, lr_min, lr_max, lr_source, finding_dir)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        doc["asset_id"], doc["asset_class"], doc["fault_context"],
                        doc["doc_type"], doc["headline"], doc["detail"],
                        doc["ai_relevance"], doc["icon"], doc["lbl"], doc["lbl_type"],
                        doc["finding_code"], doc["lr_base"], doc["lr_min"],
                        doc["lr_max"], doc["lr_source"], doc["finding_dir"],
                    )
                )
        conn.commit()
        conn.close()
        log.info(f"✅ H1 Bayesian evidence docs seeded ({len(_H1_BAYES_SEED_DOCS)} rows) into field_intel.")
    except Exception as _se:
        log.warning(f"H1 Bayesian evidence seeding failed (non-fatal): {_se}")


threading.Thread(target=_seed_h1_bayes_findings_bg, daemon=True, name="h1-bayes-seed").start()'''

src = replace_once(src, B2_SEARCH, B2_REPLACE, "H1 bayes seed function + thread")


# ── BLOCK 3: Refactor _bayes_discriminate() to read from DB ──────────────────

B3_SEARCH = '''\
def _bayes_discriminate(fault_type: str) -> dict:
    """
    Compute naive-Bayes posterior P(fault_type) via log-odds fusion.
    Prior = 50/50 (encodes telemetry ambiguity honestly).
    Returns posterior probability and structured findings for UI evidence table.
    """
    ft = fault_type if fault_type in _BAYES_FINDINGS else "gas_lock"
    findings = _BAYES_FINDINGS[ft]
    prior_odds = 1.0   # 50/50
    odds = prior_odds
    steps = []
    for f in findings:
        prev_odds = odds
        odds *= f["lr"]
        prev_p = round(prev_odds / (1.0 + prev_odds) * 100, 1)
        new_p  = round(odds       / (1.0 + odds)       * 100, 1)
        steps.append({
            "id":      f["id"],
            "label":   f["label"],
            "source":  f["source"],
            "lr":      f["lr"],
            "prior_p": prev_p,
            "post_p":  new_p,
            "physics": f["physics"],
        })
    posterior_prob = round(odds / (1.0 + odds), 4)
    return {
        "fault_type":    ft,
        "prior_odds":    prior_odds,
        "final_odds":    round(odds, 2),
        "posterior_pct": round(posterior_prob * 100, 1),
        "posterior":     posterior_prob,
        "steps":         steps,
        "method":        "naive-Bayes log-odds (Good 1950 / Fagan 1975)",
        "lr_note":       "Conservative transparent weights grounded in API RP 11S §7.2; not calibrated from empirical data.",
    }'''

B3_REPLACE = '''\
def _bayes_discriminate(fault_type: str) -> dict:
    """
    Sprint L1: Compute naive-Bayes posterior P(fault_type) via log-odds fusion.
    Prior = 50/50 (encodes telemetry ambiguity honestly).

    Reads findings + LR weights from field_intel DB (Sprint L1 — weights as metadata,
    not code constants). Falls back to _BAYES_FINDINGS dict if DB is unavailable or
    corpus not yet seeded.

    Returns posterior probability and structured findings for UI evidence table.
    """
    ft = fault_type if fault_type in _BAYES_FINDINGS else "gas_lock"

    # ── Try DB-backed findings first ─────────────────────────────────────────
    findings = None
    db_source = "fallback"
    try:
        conn = _get_db_conn()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT finding_code, headline, detail, lr_base, lr_min, lr_max,
                       lr_source, finding_dir, ai_relevance
                FROM field_intel
                WHERE asset_id = '__h1_bayes_corpus__'
                  AND fault_context = %s
                  AND finding_code IS NOT NULL
                ORDER BY finding_code
                """,
                (ft,)
            )
            rows = cur.fetchall()
        conn.close()
        if rows:
            findings = []
            for row in rows:
                fc, headline, detail, lr_base, lr_min, lr_max, lr_src, fdir, physics = row
                findings.append({
                    "id":       fc,
                    "label":    headline,
                    "source":   detail[:120] + "…" if len(detail) > 120 else detail,
                    "lr":       float(lr_base),
                    "lr_base":  float(lr_base),
                    "lr_min":   float(lr_min) if lr_min is not None else None,
                    "lr_max":   float(lr_max) if lr_max is not None else None,
                    "lr_source": lr_src or "",
                    "physics":  physics or "",
                })
            db_source = "field_intel"
    except Exception as _dbe:
        log.debug(f"_bayes_discriminate: DB read failed, using fallback: {_dbe}")

    # ── Fallback to hardcoded dict ────────────────────────────────────────────
    if not findings:
        raw = _BAYES_FINDINGS.get(ft, _BAYES_FINDINGS["gas_lock"])
        findings = [
            {
                "id":        f["id"],
                "label":     f["label"],
                "source":    f["source"],
                "lr":        f["lr"],
                "lr_base":   f["lr"],
                "lr_min":    None,
                "lr_max":    None,
                "lr_source": f["physics"][:60],
                "physics":   f["physics"],
            }
            for f in raw
        ]
        db_source = "code_fallback"

    # ── Bayesian fusion (identical arithmetic regardless of source) ───────────
    prior_odds = 1.0   # 50/50
    odds = prior_odds
    steps = []
    for f in findings:
        prev_odds = odds
        odds *= f["lr"]
        prev_p = round(prev_odds / (1.0 + prev_odds) * 100, 1)
        new_p  = round(odds       / (1.0 + odds)       * 100, 1)
        steps.append({
            "id":        f["id"],
            "label":     f["label"],
            "source":    f["source"],
            "lr":        f["lr"],
            "lr_base":   f.get("lr_base"),
            "lr_min":    f.get("lr_min"),
            "lr_max":    f.get("lr_max"),
            "lr_source": f.get("lr_source", ""),
            "prior_p":   prev_p,
            "post_p":    new_p,
            "physics":   f.get("physics", ""),
        })
    posterior_prob = round(odds / (1.0 + odds), 4)
    return {
        "fault_type":    ft,
        "prior_odds":    prior_odds,
        "final_odds":    round(odds, 2),
        "posterior_pct": round(posterior_prob * 100, 1),
        "posterior":     posterior_prob,
        "steps":         steps,
        "method":        "naive-Bayes log-odds (Good 1950 / Fagan 1975)",
        "lr_note":       "Conservative transparent weights grounded in API RP 11S §7.2; not calibrated from empirical data.",
        "weight_source": db_source,
    }'''

src = replace_once(src, B3_SEARCH, B3_REPLACE, "_bayes_discriminate DB refactor")


# ── Write output ──────────────────────────────────────────────────────────────

if dry_run:
    print("\nDry-run: no file written.")
else:
    APP.write_text(src)
    print(f"\n✅  All 3 blocks applied. {APP} written ({len(src.splitlines())} lines).")
