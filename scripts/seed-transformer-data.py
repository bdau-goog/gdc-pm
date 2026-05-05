#!/usr/bin/env python3
"""
scripts/seed-transformer-data.py

Generates training data for the High-Voltage Transformer failure classifier
and loads it directly into BigQuery.

Feature mapping for transformers (reuses 3-feature model architecture):
  psi       → kV (line voltage; nominal 115 kV)
  temp_f    → oil temperature (°F; nominal 185°F)
  vibration → vibration amplitude (mm; nominal 0.01mm)

Failure classes:
  0 — normal              (kV ~115, Temp ~185°F, Vib ~0.01mm)
  1 — winding_overheat    (kV slight drop, Temp 200–220°F, Vib mild rise)
  2 — dielectric_breakdown (kV collapses to 85–95, Temp 205–218°F, Vib moderate)
  3 — core_loosening      (kV near-nominal, Temp ~188°F, Vib climbs to 0.06–0.15mm)

NOTE: The 'psi' column stores kV for transformer assets.
      The Inference API interprets features by position, not by name.

Usage:
  python3 scripts/seed-transformer-data.py --project gdc-pm
  python3 scripts/seed-transformer-data.py --project gdc-pm --rows 4000
"""

import argparse
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from google.cloud import bigquery

# ── Configuration ─────────────────────────────────────────────────────────────
DATASET_ID  = "grid_reliability_gold"
TABLE_ID    = "transformer_telemetry_raw"
LOCATION    = "us-east4"

ASSETS = [
    "XFR-VALLEY-01",
    "XFR-RIDGE-01",
    "XFR-BASIN-01",
]

# Failure codes (integer label for BQML)
NORMAL               = 0
WINDING_OVERHEAT     = 1
DIELECTRIC_BREAKDOWN = 2
CORE_LOOSENING       = 3

FAILURE_RATE = 0.10   # Transformers have lower failure rates than compressors


def generate_normal_row(asset_id: str, ts: datetime, aging_factor: float = 0.0) -> dict:
    """
    Normal transformer operation. psi column stores kV.
    Slight insulation aging drift over time.
    """
    kv        = random.gauss(115, 1.2) - aging_factor * 0.8   # slight voltage sag with age
    temp_f    = random.gauss(185, 4) + aging_factor * 3        # slow thermal rise
    vibration = abs(random.gauss(0.010, 0.002)) + aging_factor * 0.001
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(kv, 3),        # psi column = kV for transformers
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(vibration, 4),
        "is_failure"  : NORMAL,
        "failure_type": "normal",
    }


def generate_winding_overheat_row(asset_id: str, ts: datetime, severity: float = 0.5) -> dict:
    """
    Winding overheat: sustained overload or cooling system degradation.
    Voltage drops slightly as insulation resistance decreases.
    Temperature rises significantly. Classic progressive failure.
    """
    kv        = random.gauss(112 - severity * 4, 1.5)    # voltage sag under thermal stress
    temp_f    = random.gauss(205 + severity * 15, 5)     # dangerous temperature rise
    vibration = abs(random.gauss(0.013 + severity * 0.004, 0.002))
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(kv, 3),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : WINDING_OVERHEAT,
        "failure_type": "winding_overheat",
    }


def generate_dielectric_breakdown_row(asset_id: str, ts: datetime) -> dict:
    """
    Dielectric breakdown: insulation failure causes partial discharge or flashover.
    Voltage collapses suddenly. Temperature spikes. Moderate vibration increase.
    This is a catastrophic, often irreversible event.
    """
    kv        = random.gauss(90, 5)          # severe voltage collapse
    temp_f    = random.gauss(210, 8)         # thermal event from arc fault
    vibration = abs(random.gauss(0.022, 0.005))  # moderate from electrical force
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(kv, 3),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : DIELECTRIC_BREAKDOWN,
        "failure_type": "dielectric_breakdown",
    }


def generate_core_loosening_row(asset_id: str, ts: datetime, severity: float = 0.5) -> dict:
    """
    Core loosening: lamination clamping bolt fatigue allows core movement.
    Voltage and temperature remain deceptively normal.
    Distinctive progressive vibration increase (60Hz hum amplification).
    """
    kv        = random.gauss(114.5, 1.2)     # near-normal voltage
    temp_f    = random.gauss(187 + severity * 3, 4)  # mild thermal effect
    vibration = abs(random.gauss(0.06 + severity * 0.09, 0.012))  # distinctive vib rise
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(kv, 3),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : CORE_LOOSENING,
        "failure_type": "core_loosening",
    }


def generate_dataset(total_rows: int = 4000) -> pd.DataFrame:
    rows = []
    start_time = datetime(2025, 1, 1, 6, 0, 0)
    rows_per_asset = total_rows // len(ASSETS)

    for asset_id in ASSETS:
        for i in range(rows_per_asset):
            ts           = start_time + timedelta(minutes=i * 5)
            aging_factor = i / rows_per_asset

            roll = random.random()
            if roll < FAILURE_RATE:
                failure_roll = random.random()
                if failure_roll < 0.45:
                    severity = min(1.0, aging_factor * 2.0)
                    rows.append(generate_winding_overheat_row(asset_id, ts, severity))
                elif failure_roll < 0.65:
                    rows.append(generate_dielectric_breakdown_row(asset_id, ts))
                else:
                    severity = min(1.0, aging_factor * 2.0)
                    rows.append(generate_core_loosening_row(asset_id, ts, severity))
            else:
                rows.append(generate_normal_row(asset_id, ts, aging_factor))

    df = pd.DataFrame(rows)
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df


def load_to_bigquery(df: pd.DataFrame, project_id: str) -> None:
    client      = bigquery.Client(project=project_id)
    dataset_ref = f"{project_id}.{DATASET_ID}"
    table_ref   = f"{dataset_ref}.{TABLE_ID}"

    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = LOCATION
    client.create_dataset(dataset, exists_ok=True)
    print(f"✅ Dataset {dataset_ref} ready.")

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema=[
            bigquery.SchemaField("timestamp",    "STRING"),
            bigquery.SchemaField("asset_id",     "STRING"),
            bigquery.SchemaField("psi",          "FLOAT",   # stores kV for transformers
                                 description="Stores line voltage (kV) for transformer assets"),
            bigquery.SchemaField("temp_f",       "FLOAT"),
            bigquery.SchemaField("vibration",    "FLOAT"),
            bigquery.SchemaField("is_failure",   "INTEGER"),
            bigquery.SchemaField("failure_type", "STRING"),
        ],
    )

    load_job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    load_job.result()

    table = client.get_table(table_ref)
    print(f"✅ Loaded {table.num_rows} rows into {table_ref}")

    print("\n📊 Transformer Failure Class Distribution:")
    print(df["failure_type"].value_counts().to_string())
    failure_pct = (df["is_failure"] > 0).sum() / len(df) * 100
    print(f"\n   Total Failure Rate: {failure_pct:.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Seed BigQuery training data for the HV transformer failure classifier.")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--rows", type=int, default=4000,
                        help="Total rows to generate (default: 4000)")
    args = parser.parse_args()

    print(f"🔧 Generating {args.rows} rows of transformer telemetry training data...")
    df = generate_dataset(total_rows=args.rows)

    print(f"📤 Loading to BigQuery project '{args.project}'...")
    load_to_bigquery(df, args.project)

    print("\n✅ Transformer training data seeded. Run scripts/train-transformer-model.sh next.")


if __name__ == "__main__":
    main()
