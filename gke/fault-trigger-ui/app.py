"""
gke/fault-trigger-ui/app.py

Fault Trigger UI — FastAPI backend for the GDC-PM Predictive Maintenance Demo.
Upstream O&G Edition: 20 assets across 4 sites (Pad Alpha, Pad Bravo, Pad Charlie, Rig 42).

Provides:
  1. Live asset status from AlloyDB Omni
  2. Fault injection via RabbitMQ (instant + gradual ramp)
  3. XGBoost RUL Regressor-powered Predictive Forecast charts
  4. Airgap simulation toggle
  5. Dispatch acknowledgement workflow
"""

import json
import logging
import os
import random
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import pika
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("fault-trigger-ui")

# ── Configuration ─────────────────────────────────────────────────────────────
RABBITMQ_HOST  = os.environ.get("RABBITMQ_HOST", "gdc-pm-rabbitmq.gdc-pm.svc.cluster.local")
RABBITMQ_PORT  = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER  = os.environ.get("RABBITMQ_USER", "gdc_user")
RABBITMQ_PASS  = os.environ.get("RABBITMQ_PASS", "")
RABBITMQ_VHOST = os.environ.get("RABBITMQ_VHOST", "gdc-pm")

ALLOYDB_HOST = os.environ.get("ALLOYDB_HOST", "alloydb-omni.gdc-pm.svc.cluster.local")
ALLOYDB_PORT = int(os.environ.get("ALLOYDB_PORT", "5432"))
ALLOYDB_DB   = os.environ.get("ALLOYDB_DB", "grid_reliability")
ALLOYDB_USER = os.environ.get("ALLOYDB_USER", "postgres")
ALLOYDB_PASS = os.environ.get("ALLOYDB_PASS", "")

EXCHANGE_NAME = "telemetry"
ROUTING_KEY   = "sensor.reading"
MODELS_DIR    = Path("/app/models")

# ── RUL Model Registries (Task 3 — dual-version for MLOps demo) ───────────────
# V1: original models trained on clean 5-minute interval data (intentionally drifted)
# V2: retrained models matched to 5-second edge noise profile (stable, calibrated)
# The active version is controlled at runtime via /api/model/version endpoints.
RUL_MODELS_V1: dict = {}   # {asset_class: xgb.Booster} — loaded from *_rul.ubj
RUL_MODELS_V2: dict = {}   # {asset_class: xgb.Booster} — loaded from *_rul_v2.ubj
_active_model_version: str = "v2"   # default: V2 edge-calibrated (stable, correct scale)
                                     # V1 available via /api/model/version for MLOps drift demo

# ── RUL Smoothing Buffer ──────────────────────────────────────────────────────
# Exponential-weighted rolling average of recent predictions per asset —
# smooths out individual noisy XGBoost predictions without masking real trends.
from collections import deque
import statistics as _stats
RUL_HISTORY: dict = {}   # {asset_id: deque(maxlen=10)}


def load_rul_models() -> None:
    """
    Load both V1 and V2 XGBoost RUL regressors from the models directory at startup.

    V1 (*_rul.ubj):    original cloud-trained models — deliberately drifted for demo
    V2 (*_rul_v2.ubj): edge-calibrated retrained models — should be stable at inference
    """
    try:
        import xgboost as xgb
        for asset_class in ("esp", "gas_lift", "mud_pump", "top_drive"):
            # ── V1 — original (drifted) ────────────────────────────────────────
            v1_path = MODELS_DIR / f"{asset_class}_rul.ubj"
            if v1_path.exists():
                b = xgb.Booster()
                b.load_model(str(v1_path))
                RUL_MODELS_V1[asset_class] = b
                log.info(f"✅ Loaded V1 model: {asset_class}  ({v1_path.stat().st_size//1024} KB)")
            else:
                log.warning(f"⚠️  V1 model not found: {v1_path}")

            # ── V2 — edge-calibrated (stable) ─────────────────────────────────
            v2_path = MODELS_DIR / f"{asset_class}_rul_v2.ubj"
            if v2_path.exists():
                b = xgb.Booster()
                b.load_model(str(v2_path))
                RUL_MODELS_V2[asset_class] = b
                log.info(f"✅ Loaded V2 model: {asset_class}  ({v2_path.stat().st_size//1024} KB)")
            else:
                log.info(f"ℹ️  V2 model not yet available: {v2_path} (run scripts/retrain_edge_models.py)")

        log.info(f"Model registry: V1={list(RUL_MODELS_V1.keys())}  V2={list(RUL_MODELS_V2.keys())}")
        log.info(f"Active version on startup: {_active_model_version.upper()}")
    except ImportError:
        log.warning("xgboost not available — RUL predictions will use geometric fallback")
    except Exception as e:
        log.error(f"Error loading RUL models: {e}")


load_rul_models()

# ── Asset Fleet ────────────────────────────────────────────────────────────────
# Pure-pad architecture: each pad uses a single artificial lift method.
#   Pad Alpha   — 6 ESPs (ESP production pad)
#   Pad Bravo   — 4 Gas Lift Compressors (gas lift production pad)
#   Pad Charlie — 6 ESPs (ESP production pad)
#   Rig 42      — 3 Mud Pumps + 1 Top Drive (drilling rig)
ASSETS = [
    # Pad Alpha (ESP Production — Pure ESP Pad)
    "ESP-ALPHA-1", "ESP-ALPHA-2", "ESP-ALPHA-3",
    "ESP-ALPHA-4", "ESP-ALPHA-5", "ESP-ALPHA-6",
    # Pad Bravo (Gas Lift Production — Pure Gas Lift Pad)
    "GLIFT-BRAVO-1", "GLIFT-BRAVO-2", "GLIFT-BRAVO-3", "GLIFT-BRAVO-4",
    # Pad Charlie (ESP Production — Pure ESP Pad)
    "ESP-CHARLIE-1", "ESP-CHARLIE-2", "ESP-CHARLIE-3",
    "ESP-CHARLIE-4", "ESP-CHARLIE-5", "ESP-CHARLIE-6",
    # Rig 42 (Drilling)
    "MUD-RIG42-1", "MUD-RIG42-2", "MUD-RIG42-3",
    "TOPDRIVE-RIG42-1",
]

ASSET_REGISTRY = {
    # ── Pad Alpha ESPs ────────────────────────────────────────────────────────
    "ESP-ALPHA-1": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Alpha — Well A-1", "site": "pad_alpha", "criticality": "CRITICAL",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-ALPHA-2": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Alpha — Well A-2", "site": "pad_alpha", "criticality": "CRITICAL",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-ALPHA-3": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Alpha — Well A-3", "site": "pad_alpha", "criticality": "HIGH",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-ALPHA-4": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Alpha — Well A-4", "site": "pad_alpha", "criticality": "HIGH",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-ALPHA-5": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Alpha — Well A-5", "site": "pad_alpha", "criticality": "HIGH",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-ALPHA-6": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Alpha — Well A-6", "site": "pad_alpha", "criticality": "MEDIUM",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    # ── Pad Bravo Gas Lift Compressors ────────────────────────────────────────
    "GLIFT-BRAVO-1": {
        "asset_type": "Gas Lift Compressor", "asset_class": "gas_lift",
        "location": "Pad Bravo — Injection Station", "site": "pad_bravo", "criticality": "HIGH",
        "psi_label": "Discharge Pressure (PSI)", "temp_label": "Discharge Temp (°F)",
        "vib_label": "Frame Vibration (mm/s)",
        "nominal_psi": 1000.0, "nominal_temp_f": 158.0, "nominal_vib": 1.7,
        "crit_psi": 600.0, "crit_temp": 230.0, "crit_vib": 12.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "GLIFT-BRAVO-2": {
        "asset_type": "Gas Lift Compressor", "asset_class": "gas_lift",
        "location": "Pad Bravo — Injection Station", "site": "pad_bravo", "criticality": "MEDIUM",
        "psi_label": "Discharge Pressure (PSI)", "temp_label": "Discharge Temp (°F)",
        "vib_label": "Frame Vibration (mm/s)",
        "nominal_psi": 1000.0, "nominal_temp_f": 158.0, "nominal_vib": 1.7,
        "crit_psi": 600.0, "crit_temp": 230.0, "crit_vib": 12.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "GLIFT-BRAVO-3": {
        "asset_type": "Gas Lift Compressor", "asset_class": "gas_lift",
        "location": "Pad Bravo — Injection Station", "site": "pad_bravo", "criticality": "HIGH",
        "psi_label": "Discharge Pressure (PSI)", "temp_label": "Discharge Temp (°F)",
        "vib_label": "Frame Vibration (mm/s)",
        "nominal_psi": 1000.0, "nominal_temp_f": 158.0, "nominal_vib": 1.7,
        "crit_psi": 600.0, "crit_temp": 230.0, "crit_vib": 12.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "GLIFT-BRAVO-4": {
        "asset_type": "Gas Lift Compressor", "asset_class": "gas_lift",
        "location": "Pad Bravo — Injection Station", "site": "pad_bravo", "criticality": "MEDIUM",
        "psi_label": "Discharge Pressure (PSI)", "temp_label": "Discharge Temp (°F)",
        "vib_label": "Frame Vibration (mm/s)",
        "nominal_psi": 1000.0, "nominal_temp_f": 158.0, "nominal_vib": 1.7,
        "crit_psi": 600.0, "crit_temp": 230.0, "crit_vib": 12.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    # ── Pad Charlie ESPs ──────────────────────────────────────────────────────
    "ESP-CHARLIE-1": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Charlie — Well C-1", "site": "pad_charlie", "criticality": "CRITICAL",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-CHARLIE-2": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Charlie — Well C-2", "site": "pad_charlie", "criticality": "HIGH",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-CHARLIE-3": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Charlie — Well C-3", "site": "pad_charlie", "criticality": "HIGH",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-CHARLIE-4": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Charlie — Well C-4", "site": "pad_charlie", "criticality": "HIGH",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-CHARLIE-5": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Charlie — Well C-5", "site": "pad_charlie", "criticality": "MEDIUM",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "ESP-CHARLIE-6": {
        "asset_type": "Electrical Submersible Pump", "asset_class": "esp",
        "location": "Pad Charlie — Well C-6", "site": "pad_charlie", "criticality": "MEDIUM",
        "psi_label": "Intake Pressure (PSI)", "temp_label": "Motor Winding Temp (°F)",
        "vib_label": "Motor Vibration (mm/s)",
        "nominal_psi": 1400.0, "nominal_temp_f": 198.0, "nominal_vib": 1.4,
        "crit_psi": 800.0, "crit_temp": 280.0, "crit_vib": 8.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    # ── Rig 42 ────────────────────────────────────────────────────────────────
    "MUD-RIG42-1": {
        "asset_type": "Triplex Mud Pump", "asset_class": "mud_pump",
        "location": "Rig 42 — Pump Room", "site": "rig_42", "criticality": "CRITICAL",
        "psi_label": "Discharge Pressure (PSI)", "temp_label": "Fluid End Temp (°F)",
        "vib_label": "Module Vibration (mm/s)",
        "nominal_psi": 2850.0, "nominal_temp_f": 105.0, "nominal_vib": 3.5,
        "crit_psi": 1800.0, "crit_temp": 180.0, "crit_vib": 20.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "MUD-RIG42-2": {
        "asset_type": "Triplex Mud Pump", "asset_class": "mud_pump",
        "location": "Rig 42 — Pump Room", "site": "rig_42", "criticality": "CRITICAL",
        "psi_label": "Discharge Pressure (PSI)", "temp_label": "Fluid End Temp (°F)",
        "vib_label": "Module Vibration (mm/s)",
        "nominal_psi": 2850.0, "nominal_temp_f": 105.0, "nominal_vib": 3.5,
        "crit_psi": 1800.0, "crit_temp": 180.0, "crit_vib": 20.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "MUD-RIG42-3": {
        "asset_type": "Triplex Mud Pump", "asset_class": "mud_pump",
        "location": "Rig 42 — Pump Room", "site": "rig_42", "criticality": "HIGH",
        "psi_label": "Discharge Pressure (PSI)", "temp_label": "Fluid End Temp (°F)",
        "vib_label": "Module Vibration (mm/s)",
        "nominal_psi": 2850.0, "nominal_temp_f": 105.0, "nominal_vib": 3.5,
        "crit_psi": 1800.0, "crit_temp": 180.0, "crit_vib": 20.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
    "TOPDRIVE-RIG42-1": {
        "asset_type": "Top Drive", "asset_class": "top_drive",
        "location": "Rig 42 — Derrick Floor", "site": "rig_42", "criticality": "CRITICAL",
        "psi_label": "Hydraulic Pressure (PSI)", "temp_label": "Gearbox Oil Temp (°F)",
        "vib_label": "Gearbox Vibration (mm/s)",
        "nominal_psi": 3000.0, "nominal_temp_f": 148.0, "nominal_vib": 2.8,
        "crit_psi": 2000.0, "crit_temp": 220.0, "crit_vib": 15.0,
        "psi_crit_dir": "below", "temp_crit_dir": "above", "vib_crit_dir": "above",
    },
}

# Normal sensor ranges per asset class (for "reset to normal" injection)
NORMAL_RANGES = {
    "esp":       {"psi": (1200, 1600), "temp": (180, 220), "vib": (0.8, 2.0)},
    "gas_lift":  {"psi": (940, 1060),  "temp": (140, 178), "vib": (1.0, 2.5)},
    "mud_pump":  {"psi": (2550, 3150), "temp": (90, 120),  "vib": (2.5, 4.5)},
    "top_drive": {"psi": (2840, 3160), "temp": (130, 165), "vib": (1.8, 3.8)},
}

# ── Fault Profiles ─────────────────────────────────────────────────────────────
FAULT_PROFILES = {
    # ── ESP Faults ────────────────────────────────────────────────────────────
    "gas_lock": {
        "label": "Gas Lock", "asset_class": "esp",
        "description": "Gas entrainment rising — pump efficiency degrading, intake pressure declining toward lock-up",
        "color": "#f44336",
        # PSI range represents the APPROACH to gas lock (900–1100, near the 800 PSI critical threshold)
        # NOT the post-lock state. This lets the RUL model predict when PSI will cross 800 PSI.
        "psi_range": (875, 1100), "temp_range": (195, 225), "vib_range": (3.5, 6.5),
    },
    "sand_ingress": {
        "label": "Sand Ingress", "asset_class": "esp",
        "description": "Formation sand erodes impeller stages — vibration rises over hours while pressure holds",
        "color": "#f9a825",
        "psi_range": (1280, 1580), "temp_range": (200, 240), "vib_range": (4.5, 9.5),
    },
    "motor_overheat": {
        "label": "Motor Over-Temp", "asset_class": "esp",
        "description": "Downhole cooling degrades — winding temp climbs toward insulation failure (>280°F)",
        "color": "#ff6d00",
        "psi_range": (1300, 1560), "temp_range": (265, 295), "vib_range": (2.5, 4.5),
    },
    # ── Gas Lift Compressor Faults ────────────────────────────────────────────
    "valve_failure": {
        "label": "Check Valve Failure", "asset_class": "gas_lift",
        "description": "Check valve breaks open — discharge pressure crashes as gas reverses through compressor",
        "color": "#e53935",
        "psi_range": (450, 640), "temp_range": (165, 200), "vib_range": (8.0, 14.0),
    },
    "thermal_runaway": {
        "label": "Thermal Runaway", "asset_class": "gas_lift",
        "description": "Cylinder jacket cooling fails — discharge temp climbs while pressure stays normal",
        "color": "#ff6f00",
        "psi_range": (940, 1040), "temp_range": (210, 248), "vib_range": (3.0, 5.5),
    },
    "bearing_wear": {
        "label": "Journal Bearing Wear", "asset_class": "gas_lift",
        "description": "Crankshaft bearing wear — frame vibration rises slowly over hours, pressure/temp stable",
        "color": "#f9a825",
        "psi_range": (945, 1040), "temp_range": (163, 183), "vib_range": (7.5, 13.5),
    },
    # ── Mud Pump Faults ───────────────────────────────────────────────────────
    "pulsation_dampener_failure": {
        "label": "Dampener Rupture", "asset_class": "mud_pump",
        "description": "Bladder ruptures — extreme pressure hammer and vibration spike, immediate pipe-rupture risk",
        "color": "#b71c1c",
        "psi_range": (3800, 4600), "temp_range": (120, 158), "vib_range": (15.0, 28.0),
    },
    "valve_washout": {
        "label": "Valve Seat Washout", "asset_class": "mud_pump",
        "description": "Fluid erodes valve seat over time — discharge pressure slowly declines as valve leaks",
        "color": "#e65100",
        "psi_range": (1800, 2400), "temp_range": (115, 145), "vib_range": (5.0, 10.0),
    },
    "piston_seal_wear": {
        "label": "Liner Seal Wear", "asset_class": "mud_pump",
        "description": "Piston-liner seals degrade — fluid end temp rises, discharge pressure slowly drops",
        "color": "#f57f17",
        "psi_range": (1900, 2450), "temp_range": (155, 190), "vib_range": (5.5, 8.5),
    },
    # ── Top Drive Faults ──────────────────────────────────────────────────────
    "gearbox_bearing_spalling": {
        "label": "Gearbox Bearing Spalling", "asset_class": "top_drive",
        "description": "Bearing race fatigue — distinctive vibration signature rises over 4–12h, seizure risk",
        "color": "#880e4f",
        "psi_range": (2850, 3060), "temp_range": (175, 222), "vib_range": (11.0, 20.0),
    },
    "hydraulic_leak": {
        "label": "Hydraulic System Leak", "asset_class": "top_drive",
        "description": "Hydraulic fluid loss — system pressure drops until top drive loses torque capacity",
        "color": "#4a148c",
        "psi_range": (1700, 2150), "temp_range": (158, 208), "vib_range": (3.5, 7.0),
    },
}

# Faults valid per asset class
FAULTS_BY_CLASS = {
    "esp":       ["gas_lock", "sand_ingress", "motor_overheat"],
    "gas_lift":  ["valve_failure", "thermal_runaway", "bearing_wear"],
    "mud_pump":  ["pulsation_dampener_failure", "valve_washout", "piston_seal_wear"],
    "top_drive": ["gearbox_bearing_spalling", "hydraulic_leak"],
}

# ── Point-of-No-Return (PNR) per fault type ────────────────────────────────────
# Minutes from fault onset after which operator intervention cannot prevent
# equipment damage or production loss. Based on real O&G failure physics.
# Used in the Edge vs Cloud comparison chart to quantify the response window.
PNR_MINUTES = {
    "gas_lock":                   25,   # Gas fraction >70% — pump impeller stalls
    "sand_ingress":               120,  # Impeller erosion accumulates over hours
    "motor_overheat":             30,   # Winding insulation fails above 280°F
    "valve_failure":               5,   # Instantaneous pressure crash
    "thermal_runaway":            40,   # Thermal mass buys ~40min before seizure
    "bearing_wear":               240,  # Gradual spalling — longest window
    "pulsation_dampener_failure":  0,   # Instantaneous — pipe-rupture risk
    "valve_washout":               60,  # Mud circulation loss develops over ~1h
    "piston_seal_wear":           180,  # Slow seal degradation
    "gearbox_bearing_spalling":    90,  # Vibration signature builds over hours
    "hydraulic_leak":              45,  # Pressure decay allows ~45min window
}

# ── RUL-Tiered Resolution Actions (Task 6) ─────────────────────────────────────
# Physics-grounded interventions per fault type, tiered by remaining time window.
# Tier logic (computed vs PNR for that fault):
#   early:    RUL ≥ PNR × 1.5  → low urgency, software/SCADA preferred
#   urgent:   PNR × 0.5 ≤ RUL < PNR × 1.5 → must act now
#   critical: RUL < PNR × 0.5  → emergency only
#   post_pnr: PNR exceeded      → recovery/damage assessment
REMEDIATION_TIERED = {
    "gas_lock": {   # PNR=25m
        "early":    {"action": "Reduce VFD frequency 10–15% via SCADA to raise intake pressure and clear gas void", "type": "software_command", "time_to_execute": "<5 min", "cost_incurred": 2500},
        "urgent":   {"action": "Immediate VFD cutback to 60% + page on-call field engineer for pump inspection",   "type": "field_notification", "time_to_execute": "15–20 min", "cost_incurred": 8000},
        "critical": {"action": "Emergency VFD shutdown + initiate staged pump restart protocol via SCADA",         "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 15000},
        "post_pnr": {"action": "Pull and replace ESP string — impeller stalled, order workover rig",               "type": "workover", "time_to_execute": "3–5 days", "cost_incurred": 150000},
    },
    "sand_ingress": {   # PNR=120m
        "early":    {"action": "Reduce pump rate 20% to lower sand influx; sample fluid for sand concentration",   "type": "software_command", "time_to_execute": "<10 min", "cost_incurred": 5000},
        "urgent":   {"action": "Shut in well for fluid sampling; mobilise workover crew for scheduled ESP pull",   "type": "field_notification", "time_to_execute": "30–60 min", "cost_incurred": 25000},
        "critical": {"action": "Immediate ESP shutdown to prevent full impeller destruction; plan emergency workover", "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 35000},
        "post_pnr": {"action": "Full workover — pull ESP string and replace impeller stages; run sand control study", "type": "workover", "time_to_execute": "5–7 days", "cost_incurred": 85000},
    },
    "motor_overheat": {   # PNR=30m
        "early":    {"action": "Reduce motor load 15% via VFD — lower current draw reduces winding temperature",   "type": "software_command", "time_to_execute": "<5 min", "cost_incurred": 3000},
        "urgent":   {"action": "Reduce frequency to 40 Hz + notify field engineer; inspect surface cable for hotspots", "type": "field_notification", "time_to_execute": "10–15 min", "cost_incurred": 12000},
        "critical": {"action": "Emergency ESP shutdown — winding insulation failure imminent; prepare pull rig",   "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 20000},
        "post_pnr": {"action": "Pull and replace motor + cable — winding burned out; full re-installation required", "type": "workover", "time_to_execute": "4–6 days", "cost_incurred": 200000},
    },
    "valve_failure": {   # PNR=5m
        "early":    {"action": "Reduce compressor speed 20% to limit discharge pressure swing; inspect check valve", "type": "software_command", "time_to_execute": "<5 min", "cost_incurred": 3000},
        "urgent":   {"action": "Controlled compressor shutdown + dispatch field crew for emergency valve inspection", "type": "field_notification", "time_to_execute": "10–15 min", "cost_incurred": 10000},
        "critical": {"action": "Emergency compressor shutdown — reverse gas flow damaging compressor internals",    "type": "emergency_procedure", "time_to_execute": "<2 min", "cost_incurred": 18000},
        "post_pnr": {"action": "Pull valve mandrel and replace check valve disk; inspect compressor for backflow damage", "type": "workover", "time_to_execute": "1–3 days", "cost_incurred": 42500},
    },
    "thermal_runaway": {   # PNR=40m
        "early":    {"action": "Reduce compressor speed 20%; verify cooling water flow rate and temperature delta",  "type": "software_command", "time_to_execute": "<5 min", "cost_incurred": 4000},
        "urgent":   {"action": "Cut to 50% speed + dispatch mechanic to inspect jacket cooling circuit for blockage", "type": "field_notification", "time_to_execute": "15–20 min", "cost_incurred": 15000},
        "critical": {"action": "Emergency compressor shutdown — thermal seizure imminent; flush cooling system",     "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 25000},
        "post_pnr": {"action": "Replace cylinder head and cooling jacket; full compressor rebuild required",         "type": "workover", "time_to_execute": "5–8 days", "cost_incurred": 150000},
    },
    "bearing_wear": {   # PNR=240m
        "early":    {"action": "Reduce RPM 10% to lower bearing load; schedule planned bearing swap within 48h",   "type": "software_command", "time_to_execute": "<10 min", "cost_incurred": 5000},
        "urgent":   {"action": "Reduce to 70% rated speed + mobilise bearing replacement crew for next slot",       "type": "field_notification", "time_to_execute": "30–60 min", "cost_incurred": 20000},
        "critical": {"action": "Compressor to minimum-load idle; bearing replacement within 4 hours required",     "type": "emergency_procedure", "time_to_execute": "30 min", "cost_incurred": 40000},
        "post_pnr": {"action": "Emergency bearing and shaft replacement; inspect crankshaft for scoring damage",    "type": "workover", "time_to_execute": "3–5 days", "cost_incurred": 85000},
    },
    "pulsation_dampener_failure": {   # PNR=0 — always emergency
        "early":    {"action": "IMMEDIATE: Reduce pump stroke 30% + isolate dampener; inspect bladder integrity",  "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 15000},
        "urgent":   {"action": "EMERGENCY: Pipe-rupture risk — stop pump, evacuate area, call well control",       "type": "emergency_procedure", "time_to_execute": "<2 min", "cost_incurred": 50000},
        "critical": {"action": "EMERGENCY STOP: Stand clear — bladder failure causes pressure hammer; shut in immediately", "type": "emergency_procedure", "time_to_execute": "<1 min", "cost_incurred": 75000},
        "post_pnr": {"action": "Replace dampener bladder; inspect standpipe for rupture damage; resume drilling",  "type": "workover", "time_to_execute": "1–2 days", "cost_incurred": 500000},
    },
    "valve_washout": {   # PNR=60m
        "early":    {"action": "Reduce pump rate 25% to slow erosion; monitor differential pressure; sample return flow", "type": "software_command", "time_to_execute": "<5 min", "cost_incurred": 5000},
        "urgent":   {"action": "Reduce to minimum circulation + schedule fluid end inspection during next connection", "type": "field_notification", "time_to_execute": "20–30 min", "cost_incurred": 18000},
        "critical": {"action": "Stop circulation, switch to backup pump; prepare valve seat rebuild kit",           "type": "emergency_procedure", "time_to_execute": "<15 min", "cost_incurred": 30000},
        "post_pnr": {"action": "Fluid end rebuild — replace valve seats, valve inserts, and piston liners",        "type": "workover", "time_to_execute": "4–8 hours", "cost_incurred": 52500},
    },
    "piston_seal_wear": {   # PNR=180m
        "early":    {"action": "Continue operation — schedule liner seal replacement during next planned connection stop", "type": "software_command", "time_to_execute": "<5 min", "cost_incurred": 2500},
        "urgent":   {"action": "Reduce pump rate 20% + order seal kit; plan replacement within 2 hours",           "type": "field_notification", "time_to_execute": "30–60 min", "cost_incurred": 8000},
        "critical": {"action": "Slow to minimum rate + begin immediate liner and piston seal replacement",         "type": "emergency_procedure", "time_to_execute": "30 min", "cost_incurred": 15000},
        "post_pnr": {"action": "Complete fluid end overhaul — replace liner, piston assembly, and seal; check bore", "type": "workover", "time_to_execute": "8–12 hours", "cost_incurred": 15000},
    },
    "gearbox_bearing_spalling": {   # PNR=90m
        "early":    {"action": "Reduce top drive RPM 10%; add vibration monitoring; schedule bearing inspection at next trip", "type": "software_command", "time_to_execute": "<5 min", "cost_incurred": 8000},
        "urgent":   {"action": "Slow to back-reaming speeds only + mobilise specialist crew for gearbox inspection", "type": "field_notification", "time_to_execute": "30–45 min", "cost_incurred": 30000},
        "critical": {"action": "Stop rotation — use rotary table backup + order gearbox bearing replacement immediately", "type": "emergency_procedure", "time_to_execute": "<10 min", "cost_incurred": 55000},
        "post_pnr": {"action": "Crane-lift top drive for gearbox replacement; drilling halted until repair complete", "type": "workover", "time_to_execute": "2–4 days", "cost_incurred": 120000},
    },
    "hydraulic_leak": {   # PNR=45m
        "early":    {"action": "Reduce hydraulic pressure 10%; monitor fluid level; locate leak during next stand", "type": "software_command", "time_to_execute": "<5 min", "cost_incurred": 1500},
        "urgent":   {"action": "Reduce to minimum torque + dispatch rigger to locate and patch hydraulic line",     "type": "field_notification", "time_to_execute": "15–20 min", "cost_incurred": 5000},
        "critical": {"action": "Stop top drive rotation — hydraulic loss removes torque capacity for directional work", "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 8000},
        "post_pnr": {"action": "Replace failed hydraulic line/fitting; top off reservoir; pressure-test before resuming", "type": "workover", "time_to_execute": "2–4 hours", "cost_incurred": 8000},
    },
}

# ── Remediation Cost Registry ──────────────────────────────────────────────────
# Cost avoided (USD) when an operator acknowledges a Critical/Warning dispatch.
# Represents the financial risk prevented by early Edge AI detection.
REMEDIATION_COSTS = {
    "gas_lock":                   150000,  # Production stopped + workover
    "sand_ingress":                85000,  # Workover + impeller replacement
    "motor_overheat":             200000,  # Motor burnout + replacement
    "valve_failure":               42500,  # Valve replacement + downtime
    "thermal_runaway":            150000,  # Compressor rebuild
    "bearing_wear":                85000,  # Bearing replacement + rig-down
    "pulsation_dampener_failure": 500000,  # Pipeline damage + emergency response
    "valve_washout":               52500,  # Fluid end rebuild
    "piston_seal_wear":            15000,  # Seal kit + 8h maintenance
    "gearbox_bearing_spalling":   120000,  # Gearbox repair + drilling halt
    "hydraulic_leak":               8000,  # Hydraulic repair + drilling delay
}

# ── Demo Scenarios ─────────────────────────────────────────────────────────────
SCENARIOS = {
    "esp_gas_lock_cascade": {
        "name": "ESP Gas Lock — Cascade Failure",
        "description": (
            "Sand ingress in ESP-ALPHA-2 progresses to gas lock. "
            "Demonstrates how the ML model catches sand erosion early before catastrophic failure."
        ),
        "asset": "ESP-ALPHA-2",
        "steps": [
            {"fault": "sand_ingress",  "delay_s": 0,  "burst": 3,
             "note": "Sand erosion detected — vibration rising"},
            {"fault": "sand_ingress",  "delay_s": 15, "burst": 5,
             "note": "Sand ingress accelerating — impeller wear visible"},
            {"fault": "gas_lock",      "delay_s": 30, "burst": 5,
             "note": "Gas lock triggered — production loss imminent"},
        ],
    },
    "rig_drilling_emergency": {
        "name": "Rig 42 — Drilling Emergency",
        "description": (
            "Mud pump valve washout simultaneously with top drive vibration. "
            "Demonstrates fleet-wide multi-asset monitoring during a drilling crisis."
        ),
        "asset": "MUD-RIG42-1",
        "steps": [
            {"fault": "valve_washout",              "asset_override": "MUD-RIG42-1",       "delay_s": 0,  "burst": 3,
             "note": "Mud pump #1: valve washout beginning"},
            {"fault": "gearbox_bearing_spalling",   "asset_override": "TOPDRIVE-RIG42-1",  "delay_s": 5,  "burst": 3,
             "note": "Top drive: bearing spalling detected"},
            {"fault": "valve_washout",              "asset_override": "MUD-RIG42-2",       "delay_s": 10, "burst": 3,
             "note": "Mud pump #2: valve washout spreading — drilling at risk"},
        ],
    },
    "pad_alpha_production_loss": {
        "name": "Pad Alpha — Multi-Well Production Loss",
        "description": (
            "Motor overheat cascade across three ESPs on Pad Alpha. "
            "Shows GDC monitoring a pure-ESP production pad under simultaneous thermal stress."
        ),
        "asset": "ESP-ALPHA-1",
        "steps": [
            {"fault": "motor_overheat", "asset_override": "ESP-ALPHA-1",    "delay_s": 0,  "burst": 3,
             "note": "ESP-ALPHA-1: motor winding temperature rising"},
            {"fault": "motor_overheat", "asset_override": "ESP-ALPHA-3",    "delay_s": 5,  "burst": 3,
             "note": "ESP-ALPHA-3: motor overheat spreading — shared cooling loop"},
            {"fault": "motor_overheat", "asset_override": "ESP-ALPHA-2",    "delay_s": 10, "burst": 3,
             "note": "ESP-ALPHA-2: motor overheat — Pad Alpha production critical"},
        ],
    },
}

# ── In-Memory State ────────────────────────────────────────────────────────────
scenario_status: dict = {"running": False, "name": None, "step": 0, "total": 0, "note": ""}
airgap_mode: bool = False
active_degrades: dict = {}  # {asset_id: {"running": bool, "fault_type": str, "step": int, "steps": int}}


# ── DB Helper ─────────────────────────────────────────────────────────────────
def get_db():
    return psycopg2.connect(
        host=ALLOYDB_HOST, port=ALLOYDB_PORT,
        dbname=ALLOYDB_DB, user=ALLOYDB_USER, password=ALLOYDB_PASS,
        connect_timeout=5,
    )


def publish_to_rabbitmq(reading: dict) -> None:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST, credentials=credentials, socket_timeout=5,
    )
    conn = pika.BlockingConnection(params)
    channel = conn.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.basic_publish(
        exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY,
        body=json.dumps(reading),
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )
    conn.close()


# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(title="GDC-PM Fault Trigger UI", version="3.0.0")


# ── Pydantic Models ────────────────────────────────────────────────────────────
class InjectRequest(BaseModel):
    fault_type: str
    asset_id: str
    count: Optional[int] = 1


class DegradeRequest(BaseModel):
    asset_id: str
    fault_type: str
    duration_seconds: int = 60


class ScenarioRequest(BaseModel):
    scenario_id: str


class AcknowledgeRequest(BaseModel):
    operator: Optional[str] = "ops"
    resolution_action: Optional[str] = None
    cost_incurred: Optional[float] = 0


# ── Core API Endpoints ─────────────────────────────────────────────────────────
@app.get("/api/assets")
def get_assets():
    return {"assets": ASSETS}


@app.get("/api/asset-metadata")
def get_asset_metadata():
    return {"assets": ASSET_REGISTRY}


@app.get("/api/fault-types")
def get_fault_types():
    return {"fault_types": {k: {"label": v["label"], "description": v["description"],
                                "color": v["color"], "asset_class": v["asset_class"]}
                            for k, v in FAULT_PROFILES.items()}}


@app.get("/api/faults-by-class")
def get_faults_by_class():
    return {"faults_by_class": FAULTS_BY_CLASS}


@app.get("/api/asset-status")
def get_asset_status():
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (asset_id)
                       asset_id, predicted_label AS last_prediction, event_time AS last_seen
                FROM telemetry_events
                ORDER BY asset_id, event_time DESC
                """
            )
            rows = cur.fetchall()
        conn.close()
        now = datetime.utcnow()
        statuses = []
        for r in rows:
            row = dict(r)
            age = (now - r["last_seen"].replace(tzinfo=None)).total_seconds()
            if age > 30:
                row["last_prediction"] = "stale"
            statuses.append(row)
        return {"statuses": statuses}
    except Exception as e:
        log.error(f"asset-status DB error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/api/recent-events")
def get_recent_events(limit: int = 50):
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, event_time, asset_id, asset_type, psi, temp_f, vibration,
                       failure_type, predicted_label, confidence, source,
                       ai_narrative, recommended_action, similar_events_count,
                       acknowledged, ack_time, ack_operator, cost_avoided, cost_incurred
                FROM telemetry_events
                ORDER BY event_time DESC LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        conn.close()
        result = []
        for r in rows:
            row = dict(r)
            # ── is_failed: sensor-threshold detection ─────────────────────────
            # True when the current reading's sensors have crossed the asset's
            # critical thresholds — indicates the PNR has already been passed
            # and the failure mode has physically manifested.
            is_failed = False
            asset_id = row.get("asset_id", "")
            ft = (row.get("failure_type") or "").lower()
            if ft and ft != "normal" and asset_id in ASSET_REGISTRY:
                meta = ASSET_REGISTRY[asset_id]
                try:
                    psi = float(row.get("psi") or 0)
                    temp = float(row.get("temp_f") or 0)
                    vib = float(row.get("vibration") or 0)
                    if meta["psi_crit_dir"] == "below" and psi > 0 and psi < meta["crit_psi"]:
                        is_failed = True
                    if meta["psi_crit_dir"] == "above" and psi > meta["crit_psi"]:
                        is_failed = True
                    if meta["temp_crit_dir"] == "above" and temp > meta["crit_temp"]:
                        is_failed = True
                    if meta["vib_crit_dir"] == "above" and vib > meta["crit_vib"]:
                        is_failed = True
                except (TypeError, ValueError):
                    pass
            row["is_failed"] = is_failed
            result.append(row)
        return {"events": result}
    except Exception as e:
        log.error(f"recent-events DB error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/api/alert-summary")
def get_alert_summary():
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT predicted_label, COUNT(*) AS count
                FROM telemetry_events
                WHERE event_time > NOW() - INTERVAL '30 minutes'
                GROUP BY predicted_label
                ORDER BY count DESC
                """
            )
            rows = cur.fetchall()
        conn.close()
        return {"summary": [dict(r) for r in rows]}
    except Exception as e:
        log.error(f"alert-summary DB error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.post("/api/inject-fault")
def inject_fault(req: InjectRequest):
    if req.asset_id not in ASSETS:
        raise HTTPException(status_code=400, detail=f"Unknown asset: {req.asset_id}")

    asset_class = ASSET_REGISTRY[req.asset_id]["asset_class"]
    count = max(1, min(req.count or 1, 10))
    injected = []

    if req.fault_type == "normal":
        # Use per-asset-class normal ranges
        nr = NORMAL_RANGES.get(asset_class, NORMAL_RANGES["esp"])
        for _ in range(count):
            reading = {
                "asset_id"    : req.asset_id,
                "asset_type"  : asset_class,
                "psi"         : round(random.uniform(*nr["psi"]), 1),
                "temp_f"      : round(random.uniform(*nr["temp"]), 1),
                "vibration"   : round(random.uniform(*nr["vib"]), 3),
                "failure_type": "normal",
                "source"      : "manual_injection",
                "timestamp"   : datetime.utcnow().isoformat() + "Z",
            }
            publish_to_rabbitmq(reading)
            injected.append(reading)
    else:
        if req.fault_type not in FAULT_PROFILES:
            raise HTTPException(status_code=400, detail=f"Unknown fault type: {req.fault_type}")
        profile = FAULT_PROFILES[req.fault_type]
        for _ in range(count):
            reading = {
                "asset_id"    : req.asset_id,
                "asset_type"  : asset_class,
                "psi"         : round(random.uniform(*profile["psi_range"]), 1),
                "temp_f"      : round(random.uniform(*profile["temp_range"]), 1),
                "vibration"   : round(random.uniform(*profile["vib_range"]), 3),
                "failure_type": req.fault_type,
                "source"      : "manual_injection",
                "timestamp"   : datetime.utcnow().isoformat() + "Z",
            }
            publish_to_rabbitmq(reading)
            injected.append(reading)

    log.info(f"Injected {count}× {req.fault_type} on {req.asset_id}")
    return {"status": "injected", "fault": req.fault_type, "asset": req.asset_id,
            "count": count, "readings": injected}


# ── Gradual Degradation ────────────────────────────────────────────────────────
def _run_degrade_thread(asset_id: str, fault_type: str, duration_seconds: int) -> None:
    global active_degrades
    asset_class = ASSET_REGISTRY[asset_id]["asset_class"]
    profile = FAULT_PROFILES[fault_type]
    nr = NORMAL_RANGES.get(asset_class, NORMAL_RANGES["esp"])
    steps = max(1, duration_seconds // 5)

    active_degrades[asset_id] = {
        "running": True, "fault_type": fault_type, "step": 0, "steps": steps,
        "fault_onset_utc": datetime.utcnow().isoformat() + "Z",  # Task 7: authoritative onset for PNR/Cloud calc
    }
    log.info(f"▶ Gradual degrade: {fault_type} on {asset_id} ({steps} steps)")

    for i in range(steps):
        if not active_degrades.get(asset_id, {}).get("running"):
            break
        t = (i + 1) / steps
        psi  = (nr["psi"][0] + nr["psi"][1]) / 2 + t * (profile["psi_range"][0]  - (nr["psi"][0] + nr["psi"][1]) / 2)
        temp = (nr["temp"][0] + nr["temp"][1]) / 2 + t * (profile["temp_range"][0] - (nr["temp"][0] + nr["temp"][1]) / 2)
        vib  = (nr["vib"][0] + nr["vib"][1]) / 2  + t * (profile["vib_range"][0]  - (nr["vib"][0] + nr["vib"][1]) / 2)

        # Dramatically lower noise for gradual degradation so the XGBoost model can
        # accurately calculate the slope over long (1hr+) durations without noise
        # causing the rate-of-change to flip positive/negative on every refresh.
        reading = {
            "asset_id"    : asset_id,
            "asset_type"  : asset_class,
            "psi"         : round(psi  + random.uniform(-abs(psi * 0.002),  abs(psi * 0.002)),  1),
            "temp_f"      : round(temp + random.uniform(-abs(temp * 0.001), abs(temp * 0.001)), 1),
            "vibration"   : round(max(0.05, vib + random.uniform(-abs(vib * 0.005), abs(vib * 0.005))), 3),
            "failure_type": fault_type,
            "source"      : "gradual_degrade",
            "timestamp"   : datetime.utcnow().isoformat() + "Z",
        }
        try:
            publish_to_rabbitmq(reading)
        except Exception as e:
            log.error(f"Degrade publish error: {e}")

        active_degrades[asset_id]["step"] = i + 1
        time.sleep(5)

    # ── Hold phase ────────────────────────────────────────────────────────────
    # Ramp is complete. Keep sending the final fault-level readings every 5s
    # so the 10-minute query window stays populated and the RUL/incidents
    # remain active until the operator explicitly clicks ↺ Reset.
    # The simulator is still skipping this asset because it's still in
    # active_degrades — only cancel_degrade / resetNormal removes it.
    if asset_id in active_degrades:
        active_degrades[asset_id].update({"running": False, "held": True, "step": steps})

    # Final fault-level values (end of ramp = 100% of the way to fault range)
    final_psi  = (nr["psi"][0]  + nr["psi"][1])  / 2 + (profile["psi_range"][0]  - (nr["psi"][0]  + nr["psi"][1])  / 2)
    final_temp = (nr["temp"][0] + nr["temp"][1]) / 2 + (profile["temp_range"][0] - (nr["temp"][0] + nr["temp"][1]) / 2)
    final_vib  = (nr["vib"][0]  + nr["vib"][1])  / 2 + (profile["vib_range"][0]  - (nr["vib"][0]  + nr["vib"][1])  / 2)

    log.info(f"⏸ Holding fault state: {fault_type} on {asset_id} — awaiting operator reset")
    while asset_id in active_degrades:
        time.sleep(5)
        if asset_id not in active_degrades:
            break  # Operator clicked Reset — exit immediately
        hold_reading = {
            "asset_id"    : asset_id,
            "asset_type"  : asset_class,
            "psi"         : round(final_psi  + random.uniform(-abs(final_psi  * 0.002), abs(final_psi  * 0.002)), 1),
            "temp_f"      : round(final_temp + random.uniform(-abs(final_temp * 0.001), abs(final_temp * 0.001)), 1),
            "vibration"   : round(max(0.05, final_vib + random.uniform(-abs(final_vib * 0.005), abs(final_vib * 0.005))), 3),
            "failure_type": fault_type,
            "source"      : "gradual_degrade",
            "timestamp"   : datetime.utcnow().isoformat() + "Z",
        }
        try:
            publish_to_rabbitmq(hold_reading)
        except Exception as e:
            log.error(f"Hold-phase publish error: {e}")

    log.info(f"✅ Fault released: {fault_type} on {asset_id} — operator reset")


@app.post("/api/inject/degrade")
def inject_degrade(req: DegradeRequest):
    if req.asset_id in active_degrades:
        raise HTTPException(status_code=409, detail=f"Degradation already running on {req.asset_id}")
    if req.fault_type not in FAULT_PROFILES:
        raise HTTPException(status_code=400, detail=f"Unknown fault type: {req.fault_type}")
    if req.asset_id not in ASSETS:
        raise HTTPException(status_code=400, detail=f"Unknown asset: {req.asset_id}")
    t = threading.Thread(target=_run_degrade_thread,
                         args=(req.asset_id, req.fault_type, req.duration_seconds), daemon=True)
    t.start()
    return {"status": "started", "asset": req.asset_id, "fault_type": req.fault_type,
            "duration_seconds": req.duration_seconds}


@app.get("/api/degrade-status")
def get_degrade_status():
    return {"active": active_degrades}


@app.post("/api/cancel-degrade/{asset_id}")
def cancel_degrade(asset_id: str):
    """Stop the degrade/hold thread and remove the asset so the simulator resumes."""
    if asset_id not in active_degrades:
        raise HTTPException(status_code=404, detail=f"No active degradation on {asset_id}")
    # Signal any running loop to exit, then remove the entry.
    # Both the ramp loop and the hold loop check `asset_id in active_degrades`
    # or `active_degrades[asset_id]["running"]` — removing the entry cleanly
    # terminates both and lets the simulator resume normal readings.
    active_degrades[asset_id]["running"] = False
    active_degrades.pop(asset_id, None)
    # Clear the RUL smoothing buffer so stale predictions don't bleed into
    # the next injection cycle on the same asset.
    RUL_HISTORY.pop(asset_id, None)
    log.info(f"Cancelled / reset fault injection for {asset_id}")
    return {"status": "cancelled", "asset": asset_id}


# ── Scenarios ──────────────────────────────────────────────────────────────────
@app.get("/api/scenarios")
def get_scenarios():
    return {"scenarios": {k: {"name": v["name"], "description": v["description"],
                              "step_count": len(v["steps"]), "asset": v["asset"]}
                          for k, v in SCENARIOS.items()}}


@app.get("/api/scenario-status")
def get_scenario_status():
    return scenario_status


def _run_scenario_thread(scenario_id: str, scenario: dict) -> None:
    global scenario_status
    steps = scenario["steps"]
    scenario_status.update({"running": True, "name": scenario["name"],
                             "step": 0, "total": len(steps), "note": "Starting..."})
    log.info(f"▶ Scenario: {scenario['name']}")
    for i, step in enumerate(steps):
        asset_id   = step.get("asset_override", scenario["asset"])
        fault_type = step["fault"]
        burst      = step.get("burst", 3)
        note       = step.get("note", f"Step {i+1}")
        scenario_status.update({"step": i + 1, "note": note})
        asset_class = ASSET_REGISTRY.get(asset_id, {}).get("asset_class", "esp")
        profile = FAULT_PROFILES.get(fault_type, {})
        if not profile:
            log.error(f"Unknown fault type in scenario: {fault_type}")
            continue
        for _ in range(burst):
            reading = {
                "asset_id"    : asset_id,
                "asset_type"  : asset_class,
                "psi"         : round(random.uniform(*profile["psi_range"]), 1),
                "temp_f"      : round(random.uniform(*profile["temp_range"]), 1),
                "vibration"   : round(random.uniform(*profile["vib_range"]), 3),
                "failure_type": fault_type,
                "source"      : "scenario",
                "timestamp"   : datetime.utcnow().isoformat() + "Z",
            }
            try:
                publish_to_rabbitmq(reading)
            except Exception as e:
                log.error(f"Scenario step error: {e}")
        if i < len(steps) - 1:
            time.sleep(step.get("delay_s", 0))
    scenario_status.update({"running": False, "step": len(steps), "note": "Scenario complete."})
    log.info(f"✅ Scenario '{scenario['name']}' complete.")


@app.post("/api/run-scenario")
def run_scenario(req: ScenarioRequest, background_tasks: BackgroundTasks):
    if scenario_status.get("running"):
        raise HTTPException(status_code=409, detail="A scenario is already running.")
    scenario = SCENARIOS.get(req.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404,
                            detail=f"Unknown scenario: {req.scenario_id}. Available: {list(SCENARIOS.keys())}")
    t = threading.Thread(target=_run_scenario_thread, args=(req.scenario_id, scenario), daemon=True)
    t.start()
    return {"status": "started", "scenario": scenario["name"], "steps": len(scenario["steps"])}


# ── Acknowledgement ────────────────────────────────────────────────────────────
@app.post("/api/acknowledge/{event_id}")
def acknowledge_event(event_id: int, req: AcknowledgeRequest):
    """Acknowledge a dispatch and record the cost_avoided from REMEDIATION_COSTS.
    Also auto-cancels any active fault injection for the asset so simulation stops cleanly."""
    try:
        conn = get_db()
        # Fetch the event's fault label AND asset_id to cancel any active degrade
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT asset_id, failure_type, predicted_label FROM telemetry_events WHERE id=%s",
                (event_id,),
            )
            ev = cur.fetchone()
        if not ev:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found.")
        # Cost lookup: prefer predicted_label, fall back to failure_type
        fault_key = (ev["predicted_label"] or ev["failure_type"] or "").lower()
        asset_id  = ev["asset_id"]
        cost = REMEDIATION_COSTS.get(fault_key, 0)
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE telemetry_events "
                "SET acknowledged=TRUE, ack_time=NOW(), ack_operator=%s, cost_avoided=%s, "
                "recommended_action=COALESCE(%s, recommended_action), cost_incurred=%s "
                "WHERE id=%s AND acknowledged=FALSE",
                (req.operator, cost, req.resolution_action, req.cost_incurred, event_id),
            )
            updated = cur.rowcount
        conn.commit()
        conn.close()
        if updated == 0:
            raise HTTPException(status_code=404,
                                detail=f"Event {event_id} not found or already acknowledged.")
        # ── Auto-cancel the fault injection thread for this asset ─────────────
        # Resolving the event should stop the simulation cleanly so the next
        # operator action starts from a clean state without a lingering hold phase.
        if asset_id and asset_id in active_degrades:
            active_degrades[asset_id]["running"] = False
            active_degrades.pop(asset_id, None)
            RUL_HISTORY.pop(asset_id, None)
            log.info(f"Auto-cancelled fault injection for {asset_id} on acknowledgement")
        log.info(f"Acknowledged event {event_id} | asset={asset_id} | fault={fault_key} | cost_avoided=${cost:,}")
        return {"status": "acknowledged", "event_id": event_id,
                "operator": req.operator, "cost_avoided": cost, "asset_id": asset_id}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Acknowledge error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/api/savings")
def get_savings():
    """Return the cumulative cost_avoided sum minus cost_incurred — powers the Fleet Savings Ticker."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(cost_avoided - cost_incurred), 0) FROM telemetry_events")
            total = float(cur.fetchone()[0])
        conn.close()
        return {"total_savings": total}
    except Exception as e:
        log.error(f"savings error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.post("/api/clear-dispatch")
def clear_dispatch():
    """Mark ALL unacknowledged events as acknowledged and reset cost_avoided for a clean demo restart."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE telemetry_events SET acknowledged=TRUE, ack_time=NOW(), ack_operator='demo_reset' "
                "WHERE acknowledged=FALSE"
            )
            cleared = cur.rowcount
            # Reset entire savings counters so the demo can start fresh
            cur.execute("UPDATE telemetry_events SET cost_avoided=0, cost_incurred=0")
        conn.commit()
        conn.close()
        log.info(f"Cleared {cleared} pending work orders and reset savings ticker")
        return {"status": "cleared", "count": cleared}
    except Exception as e:
        log.error(f"clear-dispatch error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# ── Model Version Swap (Task 3 — MLOps demo) ──────────────────────────────────
class ModelVersionRequest(BaseModel):
    version: str   # "v1" or "v2"


@app.get("/api/model/version")
def get_model_version():
    """Return the currently active RUL model version and registry sizes."""
    return {
        "active_version": _active_model_version,
        "v1_loaded": list(RUL_MODELS_V1.keys()),
        "v2_loaded": list(RUL_MODELS_V2.keys()),
    }


@app.post("/api/model/version")
def set_model_version(req: ModelVersionRequest):
    """
    Switch the active RUL model version between V1 (drifted) and V2 (calibrated).
    Called by the frontend after the simulated Vertex AI retraining pipeline completes.
    """
    global _active_model_version
    if req.version not in ("v1", "v2"):
        raise HTTPException(status_code=400, detail="version must be 'v1' or 'v2'")
    if req.version == "v2" and not RUL_MODELS_V2:
        raise HTTPException(
            status_code=503,
            detail="V2 models not yet loaded — run scripts/retrain_edge_models.py and rebuild container",
        )
    prev = _active_model_version
    _active_model_version = req.version
    # Clear smoothing buffers so the new model's predictions start fresh
    RUL_HISTORY.clear()
    log.info(f"🔄 Model swapped: {prev.upper()} → {req.version.upper()} | "
             f"V1 assets={list(RUL_MODELS_V1.keys())} | V2 assets={list(RUL_MODELS_V2.keys())}")
    return {
        "status": "swapped",
        "previous_version": prev,
        "active_version": _active_model_version,
        "message": (
            f"Now using V2 edge-calibrated models — RUL predictions will stabilise"
            if req.version == "v2" else
            f"Reverted to V1 cloud-trained models (training-serving skew demo mode)"
        ),
    }


# ── RUL-Tiered Resolution Actions Endpoint (Task 6) ──────────────────────────
@app.get("/api/resolution-actions/{fault_type}")
def get_resolution_actions(
    fault_type: str,
    rul_minutes: float = 60.0,
    is_pnr_exceeded: bool = False,
):
    """
    Return the RUL-tiered resolution actions for a fault type with viability scoring.

    Tier selection logic:
      post_pnr: is_pnr_exceeded=True OR PNR=0 (instantaneous)
      critical: RUL < PNR × 0.5
      urgent:   PNR × 0.5 ≤ RUL < PNR × 1.5
      early:    RUL ≥ PNR × 1.5

    Viability:
      VIABLE:    time_to_execute ≤ rul_minutes
      MARGINAL:  rul_minutes < time_to_execute ≤ rul_minutes × 1.5
      NOT VIABLE: time_to_execute > rul_minutes × 1.5
    """
    tiers = REMEDIATION_TIERED.get(fault_type)
    if not tiers:
        raise HTTPException(status_code=404, detail=f"No tiered actions for: {fault_type}")

    pnr_min = PNR_MINUTES.get(fault_type, 30)

    # Determine active tier
    if is_pnr_exceeded or pnr_min == 0:
        active_tier = "post_pnr"
    elif rul_minutes < pnr_min * 0.5:
        active_tier = "critical"
    elif rul_minutes < pnr_min * 1.5:
        active_tier = "urgent"
    else:
        active_tier = "early"

    # Parse "time_to_execute" string → minutes for viability calculation
    def _tte_to_min(tte: str) -> float:
        s = tte.lower()
        if "<1 " in s:  return 1.0
        if "<2 " in s:  return 2.0
        if "<5 " in s:  return 5.0
        if "<10 " in s: return 10.0
        if "<15 " in s: return 15.0
        if "<20 " in s: return 20.0
        if "15–20" in s or "15-20" in s: return 20.0
        if "10–15" in s or "10-15" in s: return 15.0
        if "20–30" in s or "20-30" in s: return 30.0
        if "30–45" in s or "30-45" in s: return 45.0
        if "30–60" in s or "30-60" in s: return 45.0
        if "30 min" in s: return 30.0
        if "4–8 h" in s or "4-8 h" in s: return 360.0
        if "8–12 h" in s or "8-12 h" in s: return 480.0
        return 999.0  # multi-day workover

    def _viability(tier_name: str, tier_data: dict) -> dict:
        tte_min = _tte_to_min(tier_data.get("time_to_execute", "999"))
        if is_pnr_exceeded or active_tier == "post_pnr":
            v_text, v_color, v_dim = "RECOVERY", "#ce93d8", False
        elif tte_min <= rul_minutes:
            v_text, v_color, v_dim = "VIABLE", "#00e676", False
        elif tte_min <= rul_minutes * 1.5:
            v_text, v_color, v_dim = "MARGINAL", "#ffb300", False
        else:
            v_text, v_color, v_dim = "NOT VIABLE", "#f44336", True
        return {
            **tier_data,
            "tier":           tier_name,
            "is_active":      tier_name == active_tier,
            "viability":      v_text,
            "viability_color": v_color,
            "dim":            v_dim,
        }

    return {
        "fault_type":       fault_type,
        "pnr_minutes":      pnr_min,
        "active_tier":      active_tier,
        "rul_minutes":      rul_minutes,
        "is_pnr_exceeded":  is_pnr_exceeded,
        "actions":          {k: _viability(k, v) for k, v in tiers.items()},
    }


# ── Airgap Simulation ─────────────────────────────────────────────────────────
@app.get("/api/simulate/airgap")
def get_airgap():
    return {"airgap": airgap_mode}


@app.post("/api/simulate/airgap")
def set_airgap(enabled: bool = True):
    global airgap_mode
    airgap_mode = enabled
    log.info(f"Airgap mode: {airgap_mode}")
    return {"airgap": airgap_mode}


# ── ML Predictive Forecast Visualization ─────────────────────────────────────
@app.get("/api/plot/forecast/{asset_id}", response_class=HTMLResponse)
def plot_forecast(asset_id: str, metric: str = "auto", compare_cloud: bool = False):
    """
    Returns a Plotly time-series chart with:
      - Historical telemetry for the selected sensor
      - XGBoost RUL Regressor prediction → dotted line + Cone of Uncertainty
      - Failure threshold line
      - Estimated failure time annotation
      - Optional purple dashed Cloud Inference line (compare_cloud=true)

    metric: psi | temp | vib | auto (auto selects the primary degrading sensor)
    compare_cloud: when true, adds a second VSAT-constrained+delayed cloud prediction line
    """
    import plotly.graph_objects as go
    from datetime import timedelta
    import numpy as np

    if asset_id not in ASSET_REGISTRY:
        return HTMLResponse(
            f'<body style="background:#0b0c10;color:#f44336;font-family:Inter,sans-serif;padding:30px">'
            f'<p>Unknown asset: {asset_id}</p></body>', status_code=404
        )

    asset_meta  = ASSET_REGISTRY[asset_id]
    asset_class = asset_meta["asset_class"]

    # Query last 10 minutes of telemetry (shorter window avoids stale spike outliers
    # from prior burst injections distorting the y-axis and feature computation)
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT event_time, psi, temp_f, vibration, failure_type, predicted_label
                FROM telemetry_events
                WHERE asset_id = %s AND event_time > NOW() - INTERVAL '10 minutes'
                ORDER BY event_time ASC
                """,
                (asset_id,),
            )
            rows = cur.fetchall()
        conn.close()
    except Exception as e:
        return HTMLResponse(
            f'<body style="background:#0b0c10;color:#f44336;font-family:Inter,sans-serif;padding:30px">'
            f'<p>DB Error: {e}</p></body>', status_code=500
        )

    if not rows:
        return HTMLResponse(
            f'<body style="background:#0b0c10;color:#5a6a7a;font-family:Inter,sans-serif;'
            f'display:flex;align-items:center;justify-content:center;height:100vh;margin:0">'
            f'<p>No data yet for {asset_id}.<br>Waiting for telemetry...</p></body>'
        )

    times  = [r["event_time"] for r in rows]
    psi_v  = np.array([float(r["psi"])       for r in rows])
    temp_v = np.array([float(r["temp_f"])    for r in rows])
    vib_v  = np.array([float(r["vibration"]) for r in rows])
    now    = times[-1]

    # Select metric to plot
    if metric == "auto" or metric not in ("psi", "temp", "vib"):
        # Pick the sensor with the highest relative deviation from its nominal
        nom_psi  = asset_meta["nominal_psi"]
        nom_temp = asset_meta["nominal_temp_f"]
        nom_vib  = asset_meta["nominal_vib"]
        dev_psi  = abs(psi_v[-1]  - nom_psi)  / max(nom_psi,  1)
        dev_temp = abs(temp_v[-1] - nom_temp) / max(nom_temp, 1)
        dev_vib  = abs(vib_v[-1]  - nom_vib)  / max(nom_vib,  1)
        metric = "psi" if dev_psi >= dev_temp and dev_psi >= dev_vib else \
                 "temp" if dev_temp >= dev_vib else "vib"

    if metric == "psi":
        y_vals    = psi_v
        y_label   = asset_meta.get("psi_label", "Pressure (PSI)")
        y_crit    = asset_meta["crit_psi"]
        crit_dir  = asset_meta["psi_crit_dir"]
    elif metric == "temp":
        y_vals    = temp_v
        y_label   = asset_meta.get("temp_label", "Temperature (°F)")
        y_crit    = asset_meta["crit_temp"]
        crit_dir  = asset_meta["temp_crit_dir"]
    else:
        y_vals    = vib_v
        y_label   = asset_meta.get("vib_label", "Vibration (mm/s)")
        y_crit    = asset_meta["crit_vib"]
        crit_dir  = asset_meta["vib_crit_dir"]

    # ── RUL Prediction ────────────────────────────────────────────────────────
    # GATE: Only run the RUL Regressor when:
    #   1. We have enough data (min 8 readings = ~40s of simulator data)
    #   2. The XGBoost Classifier has detected a fault in recent readings
    #      (>20% of last 10 readings are non-normal)
    # If the classifier says "normal", there is no time-to-failure to project.
    # The classifier detects anomalies; the RUL regressor only quantifies them.
    rul_minutes    = None
    # is_degrading: True during the active ramp OR during the hold phase
    _deg_state     = active_degrades.get(asset_id, {})
    is_degrading   = _deg_state.get("running", False) or _deg_state.get("held", False)
    forecast_color = "#00e676"  # green = stable
    status_text    = "✓ NOMINAL OPERATION"

    recent_labels = [str(r.get("predicted_label") or "normal").lower() for r in rows[-10:]]
    fault_count   = sum(1 for l in recent_labels if l not in ("normal", ""))
    fault_fraction = fault_count / max(len(recent_labels), 1)
    # A gradual injection in progress (or held at fault) also justifies running RUL
    classifier_active = (fault_fraction > 0.20) or is_degrading

    if len(rows) >= 8 and classifier_active:
        try:
            # ── Task 1: XGBoost RUL with fault-only clean feature extraction ──────
            #
            # ROOT CAUSE of V1 instability (training-serving skew):
            #   The 10-min query window mixes pre-fault normal readings + fault readings.
            #   The slope over this mixed window starts near-zero (inflated RUL ~3.5h)
            #   then steepens as the window fills with fault readings (RUL crashes to ~41m).
            #
            # FIX: Filter to fault-labeled readings ONLY before computing features.
            #   By feeding only fault-phase data into the slope calculation, the model
            #   sees a clean, consistent degradation signal from the first fault reading.
            #   The V1 model will still show variance (it was trained on clean 5-min data)
            #   but will no longer exhibit the "arc" artifact caused by window mixing.
            #   This instability is intentional for the MLOps demo (Task 3 retrains it).
            # ─────────────────────────────────────────────────────────────────────

            # Filter to fault-labeled readings only (removes pre-fault baseline pollution)
            fault_mask = np.array([
                (r.get("failure_type") or "").lower() not in ("normal", "")
                for r in rows
            ])
            fault_idx = np.where(fault_mask)[0]

            if len(fault_idx) >= 6:
                # Clean window: only fault-phase readings
                psi_w  = psi_v[fault_idx]
                temp_w = temp_v[fault_idx]
                vib_w  = vib_v[fault_idx]
            else:
                # Early in injection (<6 fault readings): fall back to full window
                win   = min(60, len(psi_v))
                psi_w  = psi_v[-win:]
                temp_w = temp_v[-win:]
                vib_w  = vib_v[-win:]

            t_w = np.arange(len(psi_w), dtype=np.float64)
            n_w = len(t_w)

            # Current sensor values: median of last 8 fault readings (noise-resistant)
            curr_n    = min(8, n_w)
            last_psi  = float(np.median(psi_w[-curr_n:]))
            last_temp = float(np.median(temp_w[-curr_n:]))
            last_vib  = float(np.median(vib_w[-curr_n:]))

            # Regression slopes — converted from (sensor-unit / 5-sec reading) → per minute
            # 12 readings/min at 5-second intervals.  V1 training used PSI/min features.
            READINGS_PER_MIN = 12.0
            if n_w >= 6:
                dpsi_dt  = float(np.polyfit(t_w, psi_w,  1)[0]) * READINGS_PER_MIN
                dtemp_dt = float(np.polyfit(t_w, temp_w, 1)[0]) * READINGS_PER_MIN
                dvib_dt  = float(np.polyfit(t_w, vib_w,  1)[0]) * READINGS_PER_MIN
            else:
                dpsi_dt = dtemp_dt = dvib_dt = 0.0

            # ── XGBoost Regressor predict — version-aware ─────────────────────
            rul_raw    = None
            _registry  = RUL_MODELS_V2 if _active_model_version == "v2" else RUL_MODELS_V1
            rul_model  = _registry.get(asset_class)
            if rul_model is not None:
                import xgboost as xgb
                feature_row = np.array([[last_psi, last_temp, last_vib,
                                         dpsi_dt, dtemp_dt, dvib_dt]])
                dmat    = xgb.DMatrix(
                    feature_row,
                    feature_names=["psi", "temp_f", "vibration",
                                   "dpsi_dt", "dtemp_dt", "dvib_dt"],
                )
                rul_raw = float(rul_model.predict(dmat)[0])
                rul_raw = max(0.0, min(rul_raw, 600.0))
                log.debug(f"XGBoost RUL raw={rul_raw:.1f}m  asset={asset_id}  "
                          f"psi={last_psi:.0f}  dpsi={dpsi_dt:.3f}/min  "
                          f"temp={last_temp:.1f}  vib={last_vib:.3f}")
            else:
                # ── Geometric fallback when model file not present ─────────────
                log.warning(f"No RUL model for {asset_class} — using geometric fallback")
                if n_w >= 6:
                    slope_psi  = float(np.polyfit(t_w, psi_w,  1)[0])
                    slope_temp = float(np.polyfit(t_w, temp_w, 1)[0])
                    slope_vib  = float(np.polyfit(t_w, vib_w,  1)[0])
                else:
                    slope_psi = slope_temp = slope_vib = 0.0
                sensor_now   = last_psi  if metric == "psi"  else last_temp if metric == "temp" else last_vib
                sensor_slope = slope_psi if metric == "psi"  else slope_temp if metric == "temp" else slope_vib
                if crit_dir == "below" and sensor_slope < -0.001:
                    gap = sensor_now - y_crit
                    if gap > 0:
                        rul_raw = (gap / abs(sensor_slope)) * 5.0 / 60.0
                elif crit_dir == "above" and sensor_slope > 0.001:
                    gap = y_crit - sensor_now
                    if gap > 0:
                        rul_raw = (gap / abs(sensor_slope)) * 5.0 / 60.0
                if rul_raw is None:
                    total_range = abs(asset_meta.get(
                        "nominal_psi" if metric == "psi" else
                        "nominal_temp_f" if metric == "temp" else "nominal_vib",
                        y_crit * 0.8) - y_crit)
                    gap = abs(sensor_now - y_crit)
                    if (crit_dir == "below" and sensor_now <= y_crit) or \
                       (crit_dir == "above" and sensor_now >= y_crit):
                        rul_raw = 0.0
                    elif total_range > 0:
                        rul_raw = min(30.0, gap / total_range * 60.0)
                    else:
                        rul_raw = 30.0
                rul_raw = max(0.0, min(rul_raw, 600.0))

            # ── Exponential-weighted smoothing buffer (10 readings, ~100s) ───────
            # Prevents a single noisy XGBoost prediction from flipping the display.
            if rul_raw is not None:
                if asset_id not in RUL_HISTORY:
                    RUL_HISTORY[asset_id] = deque(maxlen=10)
                RUL_HISTORY[asset_id].append(rul_raw)
                hist    = list(RUL_HISTORY[asset_id])
                n_hist  = len(hist)
                weights = np.array([0.75 ** (n_hist - 1 - i) for i in range(n_hist)])
                rul_minutes = float(np.average(hist, weights=weights))

                if rul_minutes < 60:
                    status_color = "#f44336"
                    status_text  = f"⚠ PREDICTED FAILURE — {int(rul_minutes)}m REMAINING"
                elif rul_minutes < 180:
                    status_color = "#ff6d00"
                    status_text  = f"⚠ DEGRADATION DETECTED — {int(rul_minutes//60)}h {int(rul_minutes%60)}m RUL"
                else:
                    status_color = "#ffb300"
                    status_text  = f"⚡ DEGRADATION TREND — RUL {int(rul_minutes//60)}h {int(rul_minutes%60)}m"
                forecast_color = "#ff8c00"

        except Exception as e:
            log.warning(f"RUL prediction failed for {asset_id}: {e}")
    elif len(rows) < 8:
        status_text  = f"⏳ COLLECTING BASELINE ({len(rows)}/8 readings)"
        status_color = "#5a6a7a"

    if rul_minutes is None:
        status_color = forecast_color  # green for nominal

    # ── Task 5: PNR & Asset Failure State Detection ───────────────────────────
    # Compute ONCE here — shared by chart overlays and compare_cloud section.
    fault_onset          = None
    detected_fault_type  = None
    is_pnr_exceeded      = False
    is_asset_failed_plot = False

    _dgi = active_degrades.get(asset_id, {})
    if _dgi.get("fault_onset_utc"):
        try:
            fault_onset         = datetime.fromisoformat(_dgi["fault_onset_utc"].replace("Z", ""))
            detected_fault_type = _dgi.get("fault_type")
        except Exception:
            pass
    if fault_onset is None and classifier_active:
        for r in rows:
            ft = (r.get("failure_type") or "").lower()
            if ft and ft != "normal":
                _et = r["event_time"]
                # Strip tz-info to match naive UTC from active_degrades["fault_onset_utc"]
                fault_onset = _et.replace(tzinfo=None) if getattr(_et, "tzinfo", None) else _et
                detected_fault_type = ft; break
    if fault_onset and detected_fault_type:
        _pnr_m = PNR_MINUTES.get(detected_fault_type, 9999)
        if _pnr_m < 9999:
            is_pnr_exceeded = ((datetime.utcnow() - fault_onset).total_seconds() / 60) > _pnr_m
    if classifier_active:
        for _r in rows[-5:]:
            _ft = (_r.get("failure_type") or "").lower()
            if not _ft or _ft == "normal":
                continue
            try:
                _p = float(_r.get("psi") or 0); _t = float(_r.get("temp_f") or 0); _v = float(_r.get("vibration") or 0)
                if asset_meta["psi_crit_dir"] == "below" and _p > 0 and _p < asset_meta["crit_psi"]: is_asset_failed_plot = True
                if asset_meta["temp_crit_dir"] == "above" and _t > asset_meta["crit_temp"]:           is_asset_failed_plot = True
                if asset_meta["vib_crit_dir"]  == "above" and _v > asset_meta["crit_vib"]:            is_asset_failed_plot = True
            except Exception: pass
            if is_asset_failed_plot: break

    # ── Forecast Projection ───────────────────────────────────────────────────
    # Shared starting point: median of last 5 readings (stable, no noise spike)
    y_start = float(np.median(y_vals[-5:]))
    # The target end-value is just past the critical threshold
    y_end   = y_crit * 0.98 if crit_dir == "below" else y_crit * 1.02

    if rul_minutes is not None and rul_minutes < 580:
        # Scale the future time window so the line crosses y_crit at EXACTLY
        # rul_minutes from NOW — the visual crossover always matches the text label.
        horizon_min = max(70, int(rul_minutes * 1.12) + 5)
        future_times = [now + timedelta(minutes=i) for i in range(1, horizon_min + 1)]
        # Linear ramp: y_start at t=0, y_end at t=rul_minutes, flat after that
        t_arr   = np.array(range(1, len(future_times) + 1), dtype=float)
        frac    = np.clip(t_arr / max(rul_minutes, 0.5), 0.0, 1.0)
        forecast_y = y_start + (y_end - y_start) * frac
    else:
        # Nominal / stable: flat projection
        future_times = [now + timedelta(minutes=i * 2) for i in range(1, 36)]
        forecast_y   = np.full(len(future_times), y_start)

    noise   = np.linspace(0.01, 0.10, len(future_times)) * np.abs(forecast_y)
    upper_y = forecast_y + noise
    lower_y = forecast_y - noise

    # Cone fill color: orange when degrading, green when stable
    cone_rgba = "255,140,0" if rul_minutes is not None else "0,230,118"

    # ── Build Plotly Figure ───────────────────────────────────────────────────
    fig = go.Figure()

    # 1. Historical line — blue
    fig.add_trace(go.Scatter(
        x=times, y=y_vals, mode="lines", name="Live Telemetry",
        line=dict(color="#1e90ff", width=2.5),
    ))

    # 2. ML RUL Projection — orange dotted (always distinct from red threshold)
    fig.add_trace(go.Scatter(
        x=future_times, y=forecast_y, mode="lines", name="ML RUL Projection",
        line=dict(color=forecast_color, width=2.5, dash="dot"),
    ))

    # 3. Cone of uncertainty — semi-transparent orange or green
    fig.add_trace(go.Scatter(
        x=future_times + future_times[::-1],
        y=list(upper_y) + list(lower_y)[::-1],
        fill="toself",
        fillcolor=f"rgba({cone_rgba}, 0.10)",
        line=dict(color="rgba(255,255,255,0)"),
        name="95% Confidence",
        hoverinfo="skip",
    ))

    # 4. Failure threshold line
    fig.add_trace(go.Scatter(
        x=[times[0], future_times[-1]], y=[y_crit, y_crit],
        mode="lines", name="Failure Threshold",
        line=dict(color="#f44336", width=1.5, dash="dash"),
        hoverinfo="skip",
    ))

    # 5. Predicted failure time flag — always shown when fault is active
    # Points to where the orange line visually crosses the failure threshold
    if rul_minutes is not None and rul_minutes > 0:
        ttf_time = now + timedelta(minutes=rul_minutes)
        lbl = f"{int(rul_minutes)}m" if rul_minutes < 60 else f"{int(rul_minutes//60)}h {int(rul_minutes%60)}m"
        fig.add_annotation(
            x=ttf_time, y=y_crit,
            text=f"<b>⚡ Failure in {lbl}</b>",
            showarrow=True, arrowhead=2, arrowwidth=2, arrowcolor="#f44336",
            ax=0, ay=-44,
            font=dict(color="#fff", size=11),
            bgcolor="rgba(244,67,54,0.88)", bordercolor="#f44336", borderpad=4,
        )

    # x-axis upper bound — extended to show cloud comparison line if it runs further
    _x_end = future_times[-1]

    # Build title — default; overridden by State B/C and compare_cloud below
    _title_text = (
        f"<b>{asset_id}</b> — {y_label}<br>"
        f"<span style='font-size:12px;color:{forecast_color}'>{status_text}</span>"
    )

    # ── Task 5 State B: PNR Exceeded ─────────────────────────────────────────
    if is_pnr_exceeded and not is_asset_failed_plot and fault_onset and detected_fault_type:
        _fl  = detected_fault_type.replace("_", " ").upper()
        _pm  = PNR_MINUTES.get(detected_fault_type, 30)
        _pt  = fault_onset + timedelta(minutes=_pm)
        _title_text = (
            f"<b>⚠ INTERVENTION WINDOW CLOSED — {_fl}</b><br>"
            f"<span style='color:#f44336;font-size:11px'>⛔ PNR exceeded — damage window has passed</span>"
        )
        if _pt >= times[0]:
            fig.add_annotation(
                x=_pt, y=0.5, xref="x", yref="paper",
                text="<b>⛔ PNR PASSED<br>Damage Irreversible</b>",
                showarrow=False, xanchor="center",
                font=dict(color="#f44336", size=13, family="JetBrains Mono"),
                bgcolor="rgba(244,67,54,0.18)", bordercolor="rgba(244,67,54,0.7)",
                borderpad=8, borderwidth=1,
            )

    # ── Task 5 State C: Asset Failed — Sensors Past Critical Threshold ────────
    if is_asset_failed_plot:
        fig.update_layout(plot_bgcolor="rgba(50,10,10,0.8)")
        _title_text = (
            f"<b>🔴 ASSET FAILURE — {asset_id} Offline</b><br>"
            f"<span style='color:#f44336;font-size:11px'>Critical thresholds crossed — failure manifested</span>"
        )
        fig.add_trace(go.Scatter(
            x=[now, future_times[-1]], y=[y_crit, y_crit], mode="lines", name="Failure Level",
            line=dict(color="rgba(244,67,54,0.8)", width=3), hoverinfo="skip",
        ))
        fig.add_annotation(
            x=0.5, y=0.48, xref="paper", yref="paper",
            text="<b>🔴 ASSET OFFLINE</b>",
            showarrow=False, xanchor="center",
            font=dict(color="#f44336", size=16, family="JetBrains Mono"),
            bgcolor="rgba(244,67,54,0.15)", bordercolor="rgba(244,67,54,0.6)",
            borderpad=10, borderwidth=1,
        )

    # ── PNR Vertical Line — always visible when fault is active ───────────────
    # Drawn unconditionally so operators always know the intervention deadline
    # without needing to toggle the Cloud Comparison overlay.
    _pnr_line_drawn  = False
    _pnr_time_always = None
    if classifier_active and fault_onset and detected_fault_type:
        _pnr_m_always = PNR_MINUTES.get(detected_fault_type, 0)
        if _pnr_m_always > 0:  # Skip instantaneous faults (PNR=0, e.g. dampener rupture)
            _pnr_time_always = fault_onset + timedelta(minutes=_pnr_m_always)
            # Extend x-axis to include PNR time (past or future)
            _x_end = max(_x_end, _pnr_time_always + timedelta(minutes=3))
            fig.add_shape(
                type="line",
                x0=_pnr_time_always, x1=_pnr_time_always, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="rgba(244,67,54,0.95)", width=3, dash="solid"),
            )
            fig.add_annotation(
                x=_pnr_time_always, y=0.97, xref="x", yref="paper",
                text=f"<b>⛔ PNR T+{_pnr_m_always}m</b>",
                showarrow=False, xanchor="left", xshift=6,
                font=dict(color="#f44336", size=11, family="JetBrains Mono"),
                bgcolor="rgba(244,67,54,0.15)", bordercolor="rgba(244,67,54,0.5)", borderpad=4,
            )
            _pnr_line_drawn = True

    # 6. Edge vs Cloud Resiliency Overlay ─────────────────────────────────────
    # When compare_cloud=True, adds authentic latency-based comparison overlays:
    #   - Point-of-No-Return (PNR) vertical line — physics-based, per fault type
    #   - Cloud Detection Zone — shaded band at T+15 to T+25 from fault onset
    #     (realistic VSAT uplink + batch processing + queue + notification latency)
    #   - Summary callout showing edge vs cloud response windows in minutes
    # This is NOT a model handicap — it reflects real-world VSAT infrastructure
    # constraints that make cloud-only approaches unsuitable for edge O&G.
    if compare_cloud and classifier_active:
        try:
            # ── Fault onset — reuse values computed by Task 5 block ───────────
            # fault_onset + detected_fault_type already resolved; provide fallback
            # for compare_cloud timing only if neither were set above.
            if fault_onset is None:
                _t0 = times[0]
                fault_onset = _t0.replace(tzinfo=None) if getattr(_t0, "tzinfo", None) else _t0
                detected_fault_type = next(
                    (str(r.get("predicted_label") or "").lower()
                     for r in rows if (r.get("predicted_label") or "normal") not in ("normal", "")),
                    None
                )

            pnr_min = PNR_MINUTES.get(detected_fault_type or "", 30)
            pnr_time = fault_onset + timedelta(minutes=pnr_min)

            # ── Cloud Detection Window ────────────────────────────────────────
            # Realistic VSAT O&G latency model:
            #   • Batch uplink interval:   5–10 min (VSAT bandwidth limited)
            #   • Cloud inference + queue: 3–7 min (multi-tenant processing)
            #   • Alert round-trip (VSAT): 2–5 min (back to edge device)
            #   • Midpoint estimate used for the vertical line: T+20
            cloud_detect_mid_min = 20
            cloud_detect_time = fault_onset + timedelta(minutes=cloud_detect_mid_min)

            # Extend x-axis far enough to show both vertical lines + arrow spans
            x_end_candidates = [_x_end, pnr_time, cloud_detect_time + timedelta(minutes=5)]
            if rul_minutes:
                x_end_candidates.append(now + timedelta(minutes=max(60, rul_minutes * 1.2)))
            _x_end = max(x_end_candidates)

            # ── PNR line already drawn above — skip to avoid duplicate ────────
            # (_pnr_line_drawn = True means it's already on the chart)
            # Recompute pnr_time for use by the arrows below.

            # ── Cloud Alert vertical line — solid purple ───────────────────────
            fig.add_shape(
                type="line",
                x0=cloud_detect_time, x1=cloud_detect_time, y0=0, y1=1,
                xref="x", yref="paper",
                line=dict(color="rgba(156,39,176,0.9)", width=2.5, dash="solid"),
            )
            fig.add_annotation(
                x=cloud_detect_time, y=0.97, xref="x", yref="paper",
                text=f"<b>☁ Cloud Alert T+{cloud_detect_mid_min}m</b>",
                showarrow=False, xanchor="left", xshift=6,
                font=dict(color="#ce93d8", size=11, family="JetBrains Mono"),
                bgcolor="rgba(156,39,176,0.15)", bordercolor="rgba(156,39,176,0.5)", borderpad=4,
            )

            # ── Response window calculations ──────────────────────────────────
            edge_window_min  = pnr_min          # Edge detects at T+0, full PNR window available
            cloud_window_min = max(0, pnr_min - cloud_detect_mid_min)

            # Edge result
            if edge_window_min > 0:
                edge_verdict = f"✅ SAVED — {edge_window_min}m response window"
                edge_color   = "#00e676"
            else:
                edge_verdict = "⚠ MARGINAL — instant fault"
                edge_color   = "#ffb300"

            # Cloud result
            if cloud_window_min <= 0:
                cloud_verdict = f"❌ LOST — alert arrives after PNR ({cloud_detect_mid_min}m > {pnr_min}m)"
                cloud_color   = "#f44336"
            else:
                cloud_verdict = f"⚠ PARTIAL — only {cloud_window_min}m window"
                cloud_color   = "#ffb300"

            # ── Time-to-React arrows (Task 4) ─────────────────────────────────
            # Horizontal span arrows at fixed paper-y heights so they never
            # overlap the telemetry traces.  axref/ayref="x"/"paper" lets Plotly
            # draw the arrow tail in data coordinates and the head in data coords.

            # Edge arrow: fault_onset → PNR  (green, y=0.88 paper)
            if edge_window_min > 0:
                fig.add_annotation(
                    x=pnr_time, y=0.88,
                    xref="x", yref="paper",
                    ax=fault_onset, ay=0.88,
                    axref="x", ayref="paper",
                    arrowhead=2, arrowsize=1.2, arrowwidth=2.5,
                    arrowcolor="#00e676",
                    text=f"  ⚡ Edge: {edge_window_min}m to act",
                    showarrow=True, xanchor="left",
                    font=dict(color="#00e676", size=10),
                    bgcolor="rgba(0,230,118,0.08)", borderpad=3,
                )

            # Cloud arrow: cloud_detect_time → PNR  (purple, y=0.80 paper)
            # If cloud_window_min == 0, show a "NO WINDOW" label at the PNR line instead
            if cloud_window_min > 0:
                fig.add_annotation(
                    x=pnr_time, y=0.80,
                    xref="x", yref="paper",
                    ax=cloud_detect_time, ay=0.80,
                    axref="x", ayref="paper",
                    arrowhead=2, arrowsize=1.2, arrowwidth=2.5,
                    arrowcolor="#ce93d8",
                    text=f"  ☁ Cloud: {cloud_window_min}m to act",
                    showarrow=True, xanchor="left",
                    font=dict(color="#ce93d8", size=10),
                    bgcolor="rgba(156,39,176,0.08)", borderpad=3,
                )
            else:
                fig.add_annotation(
                    x=cloud_detect_time, y=0.80,
                    xref="x", yref="paper",
                    text="  ☁ NO WINDOW — Alert after PNR",
                    showarrow=False, xanchor="left", xshift=6,
                    font=dict(color="#f44336", size=10),
                    bgcolor="rgba(244,67,54,0.08)", borderpad=3,
                )

            # Asset financial risk
            asset_risk = REMEDIATION_COSTS.get(detected_fault_type or "", 0)
            risk_str   = f"${asset_risk:,}" if asset_risk else "N/A"

            # ── Summary callout box (top-right corner) ────────────────────────
            callout_text = (
                f"<b>GDC Edge vs Cloud Analysis</b><br>"
                f"<span style='color:#00e676'>⚡ Edge AI: Detected at T+0 (<1s)</span><br>"
                f"<span style='color:{edge_color}'>{edge_verdict}</span><br>"
                f"<span style='color:#ce93d8'>☁ Cloud AI: Alert at T+{cloud_detect_mid_min}m (VSAT)</span><br>"
                f"<span style='color:{cloud_color}'>{cloud_verdict}</span><br>"
                f"<span style='color:#f44336'>⛔ Point of No Return: T+{pnr_min}m</span><br>"
                f"<span style='color:#a0b0c0'>💰 Asset at risk: {risk_str}</span>"
            )
            fig.add_annotation(
                x=0.99, y=0.72, xref="paper", yref="paper",
                text=callout_text,
                showarrow=False, xanchor="right", yanchor="top", align="left",
                font=dict(color="#e0e0e0", size=10.5),
                bgcolor="rgba(15,19,24,0.92)", bordercolor="#2a3a50", borderpad=10,
                borderwidth=1,
            )

            # ── Override chart title ──────────────────────────────────────────
            _title_text = (
                f"<b>{asset_id}</b> — {y_label} · Edge vs Cloud Resiliency<br>"
                f"<span style='color:{edge_color}; font-size:11px'>"
                f"⚡ Edge: {edge_verdict}  "
                f"<span style='color:{cloud_color}'>☁ Cloud: {cloud_verdict}</span>"
                f"</span>"
            )
        except Exception as e:
            log.warning(f"Cloud comparison failed for {asset_id}: {e}")

    # Styling ─────────────────────────────────────────────────────────────────
    fig.update_layout(
        paper_bgcolor="#0b0c10", plot_bgcolor="#0f1318",
        font=dict(color="#e0e0e0", family="Inter, sans-serif", size=11),
        margin=dict(l=55, r=20, t=50, b=40),
        title=dict(
            text=_title_text,
            font=dict(size=14, color="#e0e0e0"), x=0.02, y=0.95
        ),
        xaxis=dict(title="Time (UTC)", gridcolor="#1e2a38", zeroline=False,
                   showline=True, linecolor="#2a3a50",
                   range=[times[0], _x_end]),
        yaxis=dict(title=y_label, gridcolor="#1e2a38", zeroline=False,
                   showline=True, linecolor="#2a3a50",
                   range=[
                       # Use 5th-percentile of recent data (clips extreme outlier spikes
                       # from prior burst injections that create the wedge appearance)
                       min(float(np.percentile(y_vals, 5)), y_crit) * 0.85,
                       max(float(np.percentile(y_vals, 95)), float(np.max(upper_y)), y_crit) * 1.10,
                   ]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(11,12,16,0.7)", bordercolor="#1e2a38", borderwidth=1),
        shapes=[dict(type="line", x0=now, x1=now, y0=0, y1=1, xref="x", yref="paper",
                     line=dict(color="#5a6a7a", width=1.5, dash="dot"))],
    )
    fig.add_annotation(
        x=now, y=1.0, xref="x", yref="paper",
        text="NOW", showarrow=False, xanchor="right", xshift=-5, yanchor="bottom",
        font=dict(color="#5a6a7a", size=10, family="JetBrains Mono"),
    )

    html = fig.to_html(full_html=True, include_plotlyjs="cdn",
                       config={"displayModeBar": False, "responsive": True})
    html = html.replace("<body>", '<body style="background:#0b0c10;margin:0;padding:0;overflow:hidden;">')
    return HTMLResponse(html)


# ── Fleet Financials Ledger ───────────────────────────────────────────────────
@app.get("/api/ledger")
def get_ledger(limit: int = 200):
    """
    Return acknowledged events for the Fleet Financials ledger.
    Uses its own query (not subject to the recent-events limit=40) so old
    acknowledged records are always visible regardless of telemetry volume.
    """
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, ack_time, event_time, asset_id, failure_type,
                       predicted_label, recommended_action, cost_avoided, cost_incurred
                FROM telemetry_events
                WHERE acknowledged = TRUE
                ORDER BY COALESCE(ack_time, event_time) DESC LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        conn.close()
        return {"events": [dict(r) for r in rows]}
    except Exception as e:
        log.error(f"ledger error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# ── Serve Frontend HTML ────────────────────────────────────────────────────────
GRAFANA_EXTERNAL_IP = os.environ.get("GRAFANA_URL", "http://136.115.220.48")


@app.get("/", response_class=HTMLResponse)
def index():
    with open("/app/index.html") as f:
        html = f.read()
    # Inject Grafana URL as a meta tag so the frontend doesn't have to guess
    html = html.replace(
        '<meta charset="UTF-8" />',
        f'<meta charset="UTF-8" />\n  <meta name="grafana-url" content="{GRAFANA_EXTERNAL_IP}">',
    )
    return html
