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

# ── RUL Model Registry ─────────────────────────────────────────────────────────
# Keyed by asset_class → loaded xgb.Booster (or None)
RUL_MODELS: dict = {}

def load_rul_models() -> None:
    """Load XGBoost RUL regressors from the models directory at startup."""
    try:
        import xgboost as xgb
        for asset_class in ("esp", "gas_lift", "mud_pump", "top_drive"):
            model_path = MODELS_DIR / f"{asset_class}_rul.ubj"
            if model_path.exists():
                booster = xgb.Booster()
                booster.load_model(str(model_path))
                RUL_MODELS[asset_class] = booster
                log.info(f"✅ Loaded RUL model: {asset_class}")
            else:
                log.warning(f"⚠️  RUL model not found: {model_path}")
    except ImportError:
        log.warning("xgboost not available — RUL predictions will use fallback curve fitting")
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
        "description": "Gas entrainment rising — pump efficiency degrading as free gas overwhelms impeller stages",
        "color": "#f44336",
        "psi_range": (350, 750), "temp_range": (195, 245), "vib_range": (6.0, 12.0),
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
                       acknowledged, ack_time, ack_operator
                FROM telemetry_events
                ORDER BY event_time DESC LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        conn.close()
        return {"events": [dict(r) for r in rows]}
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

    active_degrades[asset_id] = {"running": True, "fault_type": fault_type, "step": 0, "steps": steps}
    log.info(f"▶ Gradual degrade: {fault_type} on {asset_id} ({steps} steps)")

    for i in range(steps):
        if not active_degrades.get(asset_id, {}).get("running"):
            break
        t = (i + 1) / steps
        psi  = (nr["psi"][0] + nr["psi"][1]) / 2 + t * (profile["psi_range"][0]  - (nr["psi"][0] + nr["psi"][1]) / 2)
        temp = (nr["temp"][0] + nr["temp"][1]) / 2 + t * (profile["temp_range"][0] - (nr["temp"][0] + nr["temp"][1]) / 2)
        vib  = (nr["vib"][0] + nr["vib"][1]) / 2  + t * (profile["vib_range"][0]  - (nr["vib"][0] + nr["vib"][1]) / 2)

        reading = {
            "asset_id"    : asset_id,
            "asset_type"  : asset_class,
            "psi"         : round(psi  + random.uniform(-abs(psi * 0.015),  abs(psi * 0.015)),  1),
            "temp_f"      : round(temp + random.uniform(-abs(temp * 0.008), abs(temp * 0.008)), 1),
            "vibration"   : round(max(0.05, vib + random.uniform(-abs(vib * 0.04), abs(vib * 0.04))), 3),
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

    active_degrades.pop(asset_id, None)
    log.info(f"✅ Degrade complete: {fault_type} on {asset_id}")


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
    if asset_id not in active_degrades:
        raise HTTPException(status_code=404, detail=f"No active degradation on {asset_id}")
    active_degrades[asset_id]["running"] = False
    return {"status": "cancelling", "asset": asset_id}


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
    """Acknowledge a dispatch and record the cost_avoided from REMEDIATION_COSTS."""
    try:
        conn = get_db()
        # Fetch the event's fault label to look up remediation cost
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT failure_type, predicted_label FROM telemetry_events WHERE id=%s",
                (event_id,),
            )
            ev = cur.fetchone()
        if not ev:
            conn.close()
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found.")
        # Cost lookup: prefer predicted_label, fall back to failure_type
        fault_key = (ev["predicted_label"] or ev["failure_type"] or "").lower()
        cost = REMEDIATION_COSTS.get(fault_key, 0)
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE telemetry_events "
                "SET acknowledged=TRUE, ack_time=NOW(), ack_operator=%s, cost_avoided=%s "
                "WHERE id=%s AND acknowledged=FALSE",
                (req.operator, cost, event_id),
            )
            updated = cur.rowcount
        conn.commit()
        conn.close()
        if updated == 0:
            raise HTTPException(status_code=404,
                                detail=f"Event {event_id} not found or already acknowledged.")
        log.info(f"Acknowledged event {event_id} | fault={fault_key} | cost_avoided=${cost:,}")
        return {"status": "acknowledged", "event_id": event_id,
                "operator": req.operator, "cost_avoided": cost}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Acknowledge error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/api/savings")
def get_savings():
    """Return the cumulative cost_avoided sum — powers the Fleet Savings Ticker."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(SUM(cost_avoided), 0) FROM telemetry_events")
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
            # Reset entire savings counter so the demo can start fresh
            cur.execute("UPDATE telemetry_events SET cost_avoided=0")
        conn.commit()
        conn.close()
        log.info(f"Cleared {cleared} pending work orders and reset savings ticker")
        return {"status": "cleared", "count": cleared}
    except Exception as e:
        log.error(f"clear-dispatch error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


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

    # Query last 20 minutes of telemetry
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT event_time, psi, temp_f, vibration, failure_type, predicted_label
                FROM telemetry_events
                WHERE asset_id = %s AND event_time > NOW() - INTERVAL '20 minutes'
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
    is_degrading   = active_degrades.get(asset_id, {}).get("running", False)
    forecast_color = "#00e676"  # green = stable
    status_text    = "✓ NOMINAL OPERATION"

    recent_labels = [str(r.get("predicted_label") or "normal").lower() for r in rows[-10:]]
    fault_count   = sum(1 for l in recent_labels if l not in ("normal", ""))
    fault_fraction = fault_count / max(len(recent_labels), 1)
    # A gradual injection in progress also justifies running RUL
    classifier_active = (fault_fraction > 0.20) or is_degrading

    if len(rows) >= 8 and classifier_active and asset_class in RUL_MODELS:
        try:
            import xgboost as xgb
            rul_model = RUL_MODELS[asset_class]
            last_psi, last_temp, last_vib = psi_v[-1], temp_v[-1], vib_v[-1]
            # Compute rate-of-change features (per minute) using a stable window
            window = min(8, len(rows) - 1)
            dt_min = max(0.5, (times[-1] - times[-1 - window]).total_seconds() / 60.0)
            dpsi  = (psi_v[-1]  - psi_v[-1 - window])  / dt_min
            dtemp = (temp_v[-1] - temp_v[-1 - window]) / dt_min
            dvib  = (vib_v[-1]  - vib_v[-1 - window])  / dt_min
            features = np.array([[last_psi, last_temp, last_vib, dpsi, dtemp, dvib]],
                                 dtype=np.float32)
            feature_names = ["psi", "temp_f", "vibration", "dpsi_dt", "dtemp_dt", "dvib_dt"]
            dmat = xgb.DMatrix(features, feature_names=feature_names)
            rul_minutes = float(rul_model.predict(dmat)[0])
            rul_minutes = max(0.0, min(rul_minutes, 600.0))

            # Status text color (red = urgent) — separate from the DOTTED line color
            if rul_minutes < 60:
                status_color = "#f44336"   # red text: imminent
                status_text  = f"⚠ PREDICTED FAILURE — {int(rul_minutes)}m REMAINING"
            elif rul_minutes < 180:
                status_color = "#ff6d00"   # orange text: warning
                status_text  = f"⚠ DEGRADATION DETECTED — {int(rul_minutes//60)}h {int(rul_minutes%60)}m RUL"
            else:
                status_color = "#ffb300"   # yellow text: early trend
                status_text  = f"⚡ DEGRADATION TREND — RUL {int(rul_minutes//60)}h {int(rul_minutes%60)}m"
            # The DOTTED forecast line is always orange — keeps it distinct from the
            # red dashed failure threshold line and from the blue historical trace.
            forecast_color = "#ff8c00"
        except Exception as e:
            log.warning(f"RUL prediction failed for {asset_id}: {e}")
    elif len(rows) < 8:
        status_text  = f"⏳ COLLECTING BASELINE ({len(rows)}/8 readings)"
        status_color = "#5a6a7a"

    if rul_minutes is None:
        status_color = forecast_color  # green for nominal

    # ── Forecast Projection ───────────────────────────────────────────────────
    future_times = [now + timedelta(minutes=i * 2) for i in range(1, 36)]  # next 70 min

    if rul_minutes is not None and rul_minutes < 580:
        # Project toward the critical threshold linearly based on RUL
        y_start = float(y_vals[-1])
        if crit_dir == "above":
            forecast_y = np.linspace(y_start, y_crit * 1.02, len(future_times))
        else:
            forecast_y = np.linspace(y_start, y_crit * 0.98, len(future_times))
    else:
        # Stable: flat projection with small noise
        avg_y      = float(np.mean(y_vals[-10:]))
        forecast_y = np.full(len(future_times), avg_y)

    noise   = np.linspace(0.01, 0.12, len(future_times)) * np.abs(forecast_y)
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

    # 5. Estimated failure annotation (Edge AI)
    if rul_minutes is not None and rul_minutes < 400 and rul_minutes > 5:
        ttf_time = now + timedelta(minutes=rul_minutes)
        fig.add_annotation(
            x=ttf_time, y=y_crit,
            text=f"<b>⚡ Edge AI: {int(rul_minutes//60)}h {int(rul_minutes%60)}m</b>",
            showarrow=True, arrowhead=2, arrowwidth=2, arrowcolor="#f44336",
            ax=0, ay=-40,
            font=dict(color="#fff", size=11),
            bgcolor="rgba(244,67,54,0.85)", bordercolor="#f44336", borderpad=4,
        )

    # Build title — default Edge AI title; will be replaced if cloud comparison succeeds
    _title_text = (
        f"<b>{asset_id}</b> — {y_label}<br>"
        f"<span style='font-size:12px;color:{forecast_color}'>{status_text}</span>"
    )

    # 6. Cloud vs Edge comparison overlay ─────────────────────────────────────
    # Simulates what happens when VSAT bandwidth constraints force data downsampling
    # and cloud processing latency prevents timely failure prediction.
    if compare_cloud and len(rows) >= 8 and classifier_active and asset_class in RUL_MODELS:
        try:
            import xgboost as xgb
            rul_model = RUL_MODELS[asset_class]
            cloud_latency_min = 5  # VSAT + cloud round-trip latency (minutes)

            # Simulate VSAT bandwidth constraint: apply 10-reading rolling average
            bw_window = min(10, len(y_vals))
            kernel    = np.ones(bw_window) / bw_window
            y_cloud   = np.convolve(y_vals, kernel, mode="same")
            psi_cloud = np.convolve(psi_v,  kernel, mode="same")
            temp_cloud= np.convolve(temp_v, kernel, mode="same")
            vib_cloud = np.convolve(vib_v,  kernel, mode="same")

            win = min(8, len(rows) - 1)
            dt_c = max(0.5, (times[-1] - times[-1 - win]).total_seconds() / 60.0)
            cloud_dpsi  = (psi_cloud[-1]  - psi_cloud[-1 - win])  / dt_c
            cloud_dtemp = (temp_cloud[-1] - temp_cloud[-1 - win]) / dt_c
            cloud_dvib  = (vib_cloud[-1]  - vib_cloud[-1 - win])  / dt_c

            cloud_feats = np.array([[
                float(psi_cloud[-1]), float(temp_cloud[-1]), float(vib_cloud[-1]),
                cloud_dpsi, cloud_dtemp, cloud_dvib
            ]], dtype=np.float32)
            feature_names = ["psi", "temp_f", "vibration", "dpsi_dt", "dtemp_dt", "dvib_dt"]
            cloud_dmat = xgb.DMatrix(cloud_feats, feature_names=feature_names)
            cloud_rul  = float(rul_model.predict(cloud_dmat)[0])
            cloud_rul  = max(0.0, min(cloud_rul, 600.0))

            cloud_future = [t + timedelta(minutes=cloud_latency_min) for t in future_times]
            y_cloud_start = float(y_cloud[-1])
            if cloud_rul < 580:
                if crit_dir == "above":
                    cloud_forecast = np.linspace(y_cloud_start, y_crit * 1.02, len(cloud_future))
                else:
                    cloud_forecast = np.linspace(y_cloud_start, y_crit * 0.98, len(cloud_future))
            else:
                cloud_forecast = np.full(len(cloud_future), float(np.mean(y_cloud[-10:])))

            fig.add_trace(go.Scatter(
                x=cloud_future, y=cloud_forecast, mode="lines",
                name="☁ Cloud Inference (VSAT)",
                line=dict(color="#9c27b0", width=2.5, dash="dash"),
            ))

            if cloud_rul < 400 and cloud_rul > 5:
                cloud_ttf = now + timedelta(minutes=cloud_rul + cloud_latency_min)
                fig.add_annotation(
                    x=cloud_ttf, y=y_crit,
                    text=f"<b>☁ Cloud: {int(cloud_rul//60)}h {int(cloud_rul%60)}m<br>(+{cloud_latency_min}m VSAT delay)</b>",
                    showarrow=True, arrowhead=2, arrowwidth=2, arrowcolor="#9c27b0",
                    ax=0, ay=-75,
                    font=dict(color="#fff", size=10),
                    bgcolor="rgba(156,39,176,0.85)", bordercolor="#9c27b0", borderpad=4,
                )

            # Override title with cloud comparison summary
            edge_txt = f"{int(rul_minutes)}m" if rul_minutes else "N/A"
            cloud_txt = f"{int(cloud_rul)}m (+{cloud_latency_min}m)"
            _title_text = (
                f"<b>{asset_id}</b> — {y_label} | "
                f"<span style='color:#ff8c00'>⚡ Edge AI: {edge_txt}</span>  "
                f"<span style='color:#9c27b0'>☁ Cloud: {cloud_txt}</span>"
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
                   range=[times[0], future_times[-1]]),
        yaxis=dict(title=y_label, gridcolor="#1e2a38", zeroline=False,
                   showline=True, linecolor="#2a3a50",
                   range=[min(min(y_vals), min(lower_y)) * 0.90,
                          max(max(y_vals), max(upper_y), y_crit) * 1.10]),
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


# ── Serve Frontend HTML ────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index():
    with open("/app/index.html") as f:
        return f.read()
