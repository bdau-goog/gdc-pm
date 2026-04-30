#!/usr/bin/env python3
"""
scripts/seed-training-data.py

Generates a rich, statistically sound training dataset for the stator/PRD
failure classifier and loads it directly into BigQuery.

Features:
  - 3,000 rows across 5 assets
  - Normal operating conditions with realistic Gaussian noise
  - 3 distinct failure classes (PRD Failure, Thermal Runaway, Bearing Wear)
  - ~12% overall failure rate distributed across assets and time

Usage:
  python3 scripts/seed-training-data.py --project gdc-pm
  python3 scripts/seed-training-data.py --project gdc-pm --rows 5000
"""

import argparse
import random
import math
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from google.cloud import bigquery

# ── Configuration ─────────────────────────────────────────────────────────────
DATASET_ID  = "grid_reliability_gold"
TABLE_ID    = "telemetry_raw"
LOCATION    = "us-east4"

ASSETS = [
    "COMP-TX-VALLEY-01",
    "COMP-TX-VALLEY-02",
    "COMP-TX-RIDGE-01",
    "COMP-TX-RIDGE-02",
    "COMP-TX-BASIN-01",
]

# Failure type labels (stored in is_failure as integer code)
NORMAL           = 0
PRD_FAILURE      = 1
THERMAL_RUNAWAY  = 2
BEARING_WEAR     = 3

FAILURE_RATE = 0.12   # ~12% failure events overall


def generate_normal_row(asset_id: str, ts: datetime, aging_factor: float = 0.0) -> dict:
    """
    Normal operating telemetry with realistic Gaussian noise.
    aging_factor (0.0–1.0) simulates gradual sensor drift over time.
    """
    psi       = random.gauss(855, 8) - aging_factor * 10     # slight pressure loss with age
    temp_f    = random.gauss(112, 3) + aging_factor * 4      # slight temp rise with age
    vibration = abs(random.gauss(0.02, 0.005)) + aging_factor * 0.005  # bearings wear over time
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(psi, 2),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(vibration, 4),
        "is_failure"  : NORMAL,
        "failure_type": "normal",
    }


def generate_prd_failure_row(asset_id: str, ts: datetime) -> dict:
    """
    PRD (Pressure Relief Device) failure: dramatic pressure drop,
    temperature spike, and high vibration from sudden release.
    """
    psi       = random.gauss(645, 20)   # sharp pressure drop
    temp_f    = random.gauss(162, 6)    # thermal spike
    vibration = random.gauss(0.90, 0.12)  # high vibration from pop
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(psi, 2),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : PRD_FAILURE,
        "failure_type": "prd_failure",
    }


def generate_thermal_runaway_row(asset_id: str, ts: datetime) -> dict:
    """
    Thermal runaway: pressure holds near normal, but temperature
    climbs well above safe operating range. Vibration is moderately elevated.
    """
    psi       = random.gauss(845, 12)   # near-normal pressure
    temp_f    = random.gauss(188, 10)   # dangerously high temp
    vibration = random.gauss(0.12, 0.04)  # moderately elevated
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(psi, 2),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : THERMAL_RUNAWAY,
        "failure_type": "thermal_runaway",
    }


def generate_bearing_wear_row(asset_id: str, ts: datetime, severity: float = 0.5) -> dict:
    """
    Bearing wear: gradual degradation with slowly climbing vibration.
    Pressure and temperature are largely normal. severity (0.0–1.0) allows
    us to model early vs. late-stage bearing wear.
    """
    psi       = random.gauss(850, 10)
    temp_f    = random.gauss(116, 5) + severity * 8  # mild thermal rise
    vibration = random.gauss(0.35 + severity * 0.25, 0.07)  # climbing vib
    return {
        "timestamp"   : ts.strftime("%I:%M:%S %p"),
        "asset_id"    : asset_id,
        "psi"         : round(psi, 2),
        "temp_f"      : round(temp_f, 2),
        "vibration"   : round(abs(vibration), 4),
        "is_failure"  : BEARING_WEAR,
        "failure_type": "bearing_wear",
    }


def generate_dataset(total_rows: int = 3000) -> pd.DataFrame:
    rows = []
    start_time = datetime(2025, 1, 1, 6, 0, 0)
    rows_per_asset = total_rows // len(ASSETS)

    for asset_id in ASSETS:
        # Compute an aging factor that increases over the asset's readings
        for i in range(rows_per_asset):
            ts           = start_time + timedelta(minutes=i * 5)
            aging_factor = i / rows_per_asset  # 0.0 at start, 1.0 at end

            roll = random.random()
            if roll < FAILURE_RATE:
                # Distribute failure types proportionally:
                #  55% PRD, 25% Thermal, 20% Bearing
                failure_roll = random.random()
                if failure_roll < 0.55:
                    rows.append(generate_prd_failure_row(asset_id, ts))
                elif failure_roll < 0.80:
                    rows.append(generate_thermal_runaway_row(asset_id, ts))
                else:
                    severity = min(1.0, aging_factor * 2.0)  # wear severity increases with age
                    rows.append(generate_bearing_wear_row(asset_id, ts, severity=severity))
            else:
                rows.append(generate_normal_row(asset_id, ts, aging_factor=aging_factor))

    df = pd.DataFrame(rows)
    # Shuffle so BQML doesn't see all normals followed by all failures
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df


def load_to_bigquery(df: pd.DataFrame, project_id: str) -> None:
    client      = bigquery.Client(project=project_id)
    dataset_ref = f"{project_id}.{DATASET_ID}"
    table_ref   = f"{dataset_ref}.{TABLE_ID}"

    # Ensure dataset exists
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = LOCATION
    client.create_dataset(dataset, exists_ok=True)
    print(f"✅ Dataset {dataset_ref} ready.")

    # Load — WRITE_TRUNCATE to reset any prior seed data cleanly
    job_config = bigquery.LoadJobConfig(
        write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE,
        schema = [
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
    load_job.result()  # Wait for completion

    table = client.get_table(table_ref)
    print(f"✅ Loaded {table.num_rows} rows into {table_ref}")

    # Print distribution summary
    print("\n📊 Class Distribution:")
    print(df["failure_type"].value_counts().to_string())
    failure_pct = (df["is_failure"] > 0).sum() / len(df) * 100
    print(f"\n   Total Failure Rate: {failure_pct:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Seed BigQuery training data for the stator failure classifier.")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--rows",    type=int, default=3000, help="Total rows to generate (default: 3000)")
    args = parser.parse_args()

    print(f"🔧 Generating {args.rows} rows of telemetry training data...")
    df = generate_dataset(total_rows=args.rows)

    print(f"📤 Loading to BigQuery project '{args.project}'...")
    load_to_bigquery(df, args.project)

    print("\n✅ Training data seeded successfully. Run scripts/train-model.sh next.")


if __name__ == "__main__":
    main()
