#!/usr/bin/env python3
"""
scripts/seed-turbine-data.py

Generates training data for the Gas Turbine Generator failure classifier
and loads it directly into BigQuery.

Failure classes:
  0 — normal               (nominal: PSI ~2200, Temp ~1050°F, Vib ~0.05mm)
  1 — combustion_instability  (PSI drops to ~1800, Temp spikes, Vib elevated)
  2 — blade_fouling           (PSI mild drop, Temp climbs slowly, Vib slight rise)
  3 — rotor_imbalance         (PSI/Temp near nominal, Vib climbs progressively)

Usage:
  python3 scripts/seed-turbine-data.py --project gdc-pm
  python3 scripts/seed-turbine-data.py --project gdc-pm --rows 4000
"""

import argparse
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from google.cloud import bigquery

# ── Configuration ─────────────────────────────────────────────────────────────
DATASET_ID  = "grid_reliability_gold"
TABLE_ID    = "turbine_telemetry_raw"
LOCATION    = "us-east4"

ASSETS = [
    "GTG-VALLEY-01",
    "GTG-RIDGE-01",
]

# Failure codes (integer label for BQML)
NORMAL                  = 0
COMBUSTION_INSTABILITY  = 1
BLADE_FOULING           = 2
ROTOR_IMBALANCE         = 3

FAILURE_RATE = 0.12


def generate_normal_row(asset_id: str, ts: datetime, aging_factor: float = 0.0) -> dict:
    """
    Normal turbine operation with Gaussian noise.
    Slight blade fouling drift built in over time (aging_factor 0→1).
    """
    psi       = random.gauss(2200, 25) - aging_factor * 15
    temp_f    = random.gauss(1050, 12) + aging_factor * 8
    vibration = abs(random.gauss(0.05, 0.008)) + aging_factor * 0.005
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(psi, 2),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(vibration, 4),
        "is_failure"  : NORMAL,
        "failure_type": "normal",
    }


def generate_combustion_instability_row(asset_id: str, ts: datetime) -> dict:
    """
    Combustion instability / surge: fuel-air ratio imbalance causes rapid
    PSI swings and temperature spike. High vibration from pressure oscillations.
    """
    psi       = random.gauss(1800, 40)   # sharp PSI drop from surge
    temp_f    = random.gauss(1120, 15)   # temperature spike
    vibration = abs(random.gauss(0.18, 0.04))  # elevated from pressure oscillation
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(psi, 2),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : COMBUSTION_INSTABILITY,
        "failure_type": "combustion_instability",
    }


def generate_blade_fouling_row(asset_id: str, ts: datetime, severity: float = 0.5) -> dict:
    """
    Blade fouling: progressive deposit buildup reduces aerodynamic efficiency.
    PSI drops slightly, temperature climbs gradually, vibration increases moderately.
    """
    psi       = random.gauss(2100 - severity * 80, 20)  # efficiency loss → PSI drop
    temp_f    = random.gauss(1075 + severity * 35, 12)  # thermal inefficiency
    vibration = abs(random.gauss(0.07 + severity * 0.04, 0.01))  # slight imbalance
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(psi, 2),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : BLADE_FOULING,
        "failure_type": "blade_fouling",
    }


def generate_rotor_imbalance_row(asset_id: str, ts: datetime, severity: float = 0.5) -> dict:
    """
    Rotor imbalance: mass redistribution causes progressive vibration increase.
    PSI and temperature largely normal — distinguishable only via vibration signature.
    """
    psi       = random.gauss(2195, 18)   # near-normal
    temp_f    = random.gauss(1055, 10)   # slight rise from bearing friction
    vibration = abs(random.gauss(0.25 + severity * 0.35, 0.05))  # climbing
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(psi, 2),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : ROTOR_IMBALANCE,
        "failure_type": "rotor_imbalance",
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
                if failure_roll < 0.40:
                    rows.append(generate_combustion_instability_row(asset_id, ts))
                elif failure_roll < 0.70:
                    severity = min(1.0, aging_factor * 2.0)
                    rows.append(generate_blade_fouling_row(asset_id, ts, severity))
                else:
                    severity = min(1.0, aging_factor * 2.0)
                    rows.append(generate_rotor_imbalance_row(asset_id, ts, severity))
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
            bigquery.SchemaField("psi",          "FLOAT"),
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

    print("\n📊 Turbine Failure Class Distribution:")
    print(df["failure_type"].value_counts().to_string())
    failure_pct = (df["is_failure"] > 0).sum() / len(df) * 100
    print(f"\n   Total Failure Rate: {failure_pct:.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Seed BigQuery training data for the gas turbine failure classifier.")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--rows", type=int, default=4000,
                        help="Total rows to generate (default: 4000)")
    args = parser.parse_args()

    print(f"🔧 Generating {args.rows} rows of turbine telemetry training data...")
    df = generate_dataset(total_rows=args.rows)

    print(f"📤 Loading to BigQuery project '{args.project}'...")
    load_to_bigquery(df, args.project)

    print("\n✅ Turbine training data seeded. Run scripts/train-turbine-model.sh next.")


if __name__ == "__main__":
    main()
