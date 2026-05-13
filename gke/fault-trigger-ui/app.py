"""
gke/fault-trigger-ui/app.py

Fault Trigger UI — FastAPI backend for the GDC-PM Predictive Maintenance Demo.
Upstream O&G Edition: 14 assets across 3 sites (Pad Alpha, Pad Bravo, Rig 42).

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
from fastapi.responses import HTMLResponse, StreamingResponse
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

OLLAMA_URL   = os.environ.get("OLLAMA_URL",   "http://ollama.gdc-pm.svc.cluster.local:11434")
# Phase 6.2: Reduced to gemma3:12b for faster demo response time.
# gemma:2b was too small; gemma3:27b is too slow. 12b hits the sweet spot.
# Override via OLLAMA_MODEL env var if a different model is pulled.
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:12b")

# ── Health Score Model Registry (Phase 5.1) ───────────────────────────────────
# Single edge-calibrated XGBoost Health Score model per asset class.
# Predicts health_score (1.0 = perfect, 0.0 = destroyed) from 6- or 8-feature
# sensor + slope vectors.  Replaces the V1/V2 RUL dual-model MLOps demo.
# Models trained by scripts/retrain_edge_models.py with exponential k=3.5 curve.
HEALTH_MODELS: dict = {}   # {asset_class: xgb.Booster} — loaded from *_health.ubj

# ── Health Score Smoothing Buffer ─────────────────────────────────────────────
# Exponential-weighted rolling average of recent predictions per asset —
# smooths out individual noisy XGBoost predictions without masking real trends.
from collections import deque
HEALTH_HISTORY: dict = {}  # {asset_id: deque(maxlen=10)}


def load_health_models() -> None:
    """
    Load Phase 5.1 XGBoost Health Score models from the models directory at startup.
    Each asset class has one model: {asset_class}_health.ubj
    Predicts health_score 1.0 (nominal) → 0.0 (destroyed).
    """
    try:
        import xgboost as xgb
        for asset_class in ("esp", "gas_lift", "mud_pump", "top_drive"):
            path = MODELS_DIR / f"{asset_class}_health.ubj"
            if path.exists():
                b = xgb.Booster()
                b.load_model(str(path))
                HEALTH_MODELS[asset_class] = b
                log.info(f"✅ Loaded health model: {asset_class}  ({path.stat().st_size//1024} KB)")
            else:
                # Fall back to legacy V2 RUL model if health model not yet built
                legacy = MODELS_DIR / f"{asset_class}_rul_v2.ubj"
                if legacy.exists():
                    log.warning(f"⚠️  {path.name} not found — legacy {legacy.name} present but "
                                f"not loaded (run scripts/retrain_edge_models.py for Phase 5.1 models)")
                else:
                    log.warning(f"⚠️  No model found for {asset_class} — predictions will use fallback")
        log.info(f"Health model registry: {list(HEALTH_MODELS.keys())}")
    except ImportError:
        log.warning("xgboost not available — health predictions will use geometric fallback")
    except Exception as e:
        log.error(f"Error loading health models: {e}")


load_health_models()


# ── Phase 7.4: Ollama Model Warm-Up ───────────────────────────────────────────
# Prevents gemma3:12b from cold-starting after >10 minutes of inactivity on GKE.
# Sends a minimal dummy completion request at startup then every 5 minutes.
# Runs in a daemon thread so it does not block the FastAPI startup sequence.
def _ollama_keepalive() -> None:
    """Background ping to prevent Ollama model cold-start during demos."""
    import requests as _req
    time.sleep(15)  # Wait 15s for the container to fully initialize before first ping
    while True:
        try:
            resp = _req.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": "ping", "stream": False,
                      "options": {"num_predict": 1, "temperature": 0.0}},
                timeout=30,
            )
            if resp.status_code == 200:
                log.debug(f"🔥 Ollama keepalive OK — model {OLLAMA_MODEL} is warm")
            else:
                log.debug(f"Ollama keepalive: HTTP {resp.status_code}")
        except Exception as e:
            log.debug(f"Ollama keepalive ping failed (non-fatal): {e}")
        time.sleep(300)  # Ping every 5 minutes


threading.Thread(target=_ollama_keepalive, daemon=True, name="ollama-keepalive").start()
log.info(f"🔥 Ollama keepalive thread started — model: {OLLAMA_MODEL}, interval: 5min")


# ── Asset Fleet ────────────────────────────────────────────────────────────────
# Pure-pad architecture: each pad uses a single artificial lift method.
#   Pad Alpha   — 6 ESPs (ESP production pad)
#   Pad Bravo   — 4 Gas Lift Compressors (gas lift production pad)
#   Rig 42      — 3 Mud Pumps + 1 Top Drive (drilling rig)
ASSETS = [
    # Pad Alpha (ESP Production — Pure ESP Pad)
    "ESP-ALPHA-1", "ESP-ALPHA-2", "ESP-ALPHA-3",
    "ESP-ALPHA-4", "ESP-ALPHA-5", "ESP-ALPHA-6",
    # Pad Bravo (Gas Lift Production — Pure Gas Lift Pad)
    "GLIFT-BRAVO-1", "GLIFT-BRAVO-2", "GLIFT-BRAVO-3", "GLIFT-BRAVO-4",
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

# ── Fourth Sensor Config (Phase 4) ────────────────────────────────────────────
# motor_amps for ESP: measured at VFD surface panel — standard on every ESP installation.
#   Current is proportional to pump hydraulic work. As stages erode or gas locks the pump,
#   current falls — the earliest and most sensitive indicator of pump health degradation.
# spm for Mud Pump: stroke counter is the most basic drilling measurement (Pason/NOV EDR).
#   SPM × liner_vol = theoretical flow. When SPM trends up while PSI holds, the driller
#   is compensating for valve leakage — the volumetric efficiency signature SCADA misses.
SENSOR4_CONFIG = {
    "esp": {
        "key": "motor_amps", "range_key": "amps_range",
        "label": "Motor Current (A)",
        "nominal": 75.0, "normal_range": (60, 90),
        "crit": 40.0, "crit_dir": "below",
    },
    "mud_pump": {
        "key": "spm", "range_key": "spm_range",
        "label": "Stroke Rate (SPM)",
        "nominal": 87.0, "normal_range": (75, 100),
        "crit": 115.0, "crit_dir": "above",
    },
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
        "amps_range": (20, 45),   # Pump unloads as gas void fraction rises — current drops sharply
    },
    "sand_ingress": {
        "label": "Sand Ingress", "asset_class": "esp",
        "description": "Formation sand erodes impeller stages — vibration rises over hours while pressure holds",
        "color": "#f9a825",
        "psi_range": (1280, 1580), "temp_range": (200, 240), "vib_range": (4.5, 9.5),
        "amps_range": (45, 65),   # Declining as impeller stages erode — pump does less hydraulic work
    },
    "motor_overheat": {
        "label": "Motor Over-Temp", "asset_class": "esp",
        "description": "Downhole cooling degrades — winding temp climbs toward insulation failure (>280°F)",
        "color": "#ff6d00",
        "psi_range": (1300, 1560), "temp_range": (265, 295), "vib_range": (2.5, 4.5),
        "amps_range": (88, 105),  # Overcurrent — motor drawing more power fighting increased resistance
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
        "spm_range": (55, 135),   # Erratic — bladder failure causes chaotic pressure pulsation
    },
    "valve_washout": {
        "label": "Valve Seat Washout", "asset_class": "mud_pump",
        "description": "Fluid erodes valve seat over time — discharge pressure slowly declines as valve leaks",
        "color": "#e65100",
        "psi_range": (1800, 2400), "temp_range": (115, 145), "vib_range": (5.0, 10.0),
        "spm_range": (95, 120),   # Rising — driller compensates for efficiency loss by increasing stroke rate
    },
    "piston_seal_wear": {
        "label": "Liner Seal Wear", "asset_class": "mud_pump",
        "description": "Piston-liner seals degrade — fluid end temp rises, discharge pressure slowly drops",
        "color": "#f57f17",
        "psi_range": (1900, 2450), "temp_range": (155, 190), "vib_range": (5.5, 8.5),
        "spm_range": (90, 110),   # Moderate rise — slower compensation over days of seal degradation
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

# ── Fault Physics Configuration (Phase 5.2 / Phase 6.1) ──────────────────────
# Maps each fault type to its physical time horizon and SCADA/PNR health thresholds.
# The health score model is time-agnostic — FAULT_PHYSICS is the UI layer that
# converts health_score (0.0–1.0) → physical time remaining for each fault.
#
# INVARIANT:  scada_alarm_health > pnr_health > 0.0   (always)
# This guarantees: time_to_scada < time_to_pnr < time_to_failure (always correct)
# So the chart sequence ML Detection → SCADA Alarm → PNR → Failure is ALWAYS right.
#
# Phase 6.1 additions:
#   scada_sensor  — the sensor tab that shows the SCADA alarm threshold line
#   pnr_sensor    — the sensor tab that shows the PNR vertical marker
#   primary_sensor — the most important tab to inspect first (highlighted in UI)
# Sensor key → metric name mapping used by /api/plot/forecast/:
#   "amps"     → Motor Current (ESP only)
#   "temp"     → Winding / Fluid / Gearbox Temperature
#   "vib"      → Vibration
#   "psi"      → Intake / Discharge / Hydraulic Pressure
# Only the matching tab receives threshold annotations — showing a SCADA or PNR
# marker on a non-causal sensor is physically wrong and confuses operators.
FAULT_PHYSICS = {
    # ── Long Horizon (Days) — Supply Chain / Workover ─────────────────────────
    "sand_ingress": {
        "horizon_label": "Days",
        "total_hours": 336,           # 14 days
        "scada_alarm_health": 0.15,   # Fires at 85% degraded (Day 11.9)
        "pnr_health": 0.05,           # Irreversible at 95% degraded (Day 13.3)
        "scada_sensor": "vib",        # Vibration high alarm from impeller erosion
        "pnr_sensor": "vib",          # Vibration also drives PNR (impellers destroyed)
        "primary_sensor": "vib",
        "intervention_type": "supply_chain",
    },
    "piston_seal_wear": {
        "horizon_label": "Days",
        "total_hours": 96,            # 4 days
        "scada_alarm_health": 0.20,
        "pnr_health": 0.08,
        "scada_sensor": "psi",        # Pressure drop (leaking past seal)
        "pnr_sensor": "vib",          # Vibration as piston wipes
        "primary_sensor": "psi",
        "intervention_type": "maintenance_scheduling",
    },
    "gearbox_bearing_spalling": {
        "horizon_label": "Hours",
        "total_hours": 10,
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "scada_sensor": "vib",        # Vibration high alarm (bearing roughness)
        "pnr_sensor": "temp",         # Thermal runaway as bearing seizes
        "primary_sensor": "vib",
        "intervention_type": "maintenance_scheduling",
    },
    # ── Medium Horizon (Hours) — Crew Dispatch ────────────────────────────────
    "motor_overheat": {
        "horizon_label": "Hours",
        "total_hours": 4,
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "scada_sensor": "temp",       # Temperature high alarm
        "pnr_sensor": "temp",         # Temperature drives insulation failure
        "primary_sensor": "temp",
        "intervention_type": "operational_control",
    },
    "thermal_runaway": {
        "horizon_label": "Hours",
        "total_hours": 72,
        "scada_alarm_health": 0.20,
        "pnr_health": 0.07,
        "scada_sensor": "temp",       # Temp high alarm (cylinder overheating)
        "pnr_sensor": "temp",         # Winding temp burnout / seizure
        "primary_sensor": "temp",
        "intervention_type": "maintenance_scheduling",
    },
    "valve_washout": {
        "horizon_label": "Hours",
        "total_hours": 10,
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "scada_sensor": "psi",        # Pressure drop (valve leaking)
        "pnr_sensor": "psi",          # Pressure / valve seat destroyed
        "primary_sensor": "psi",
        "intervention_type": "maintenance_scheduling",
    },
    "hydraulic_leak": {
        "horizon_label": "Hours",
        "total_hours": 6,
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "scada_sensor": "psi",        # Pressure drop (fluid loss)
        "pnr_sensor": "psi",          # Pressure / loss of prime
        "primary_sensor": "psi",
        "intervention_type": "operational_control",
    },
    "bearing_wear": {
        "horizon_label": "Hours",
        "total_hours": 16,
        "scada_alarm_health": 0.20,
        "pnr_health": 0.08,
        "scada_sensor": "vib",        # Vibration high alarm (bearing roughness)
        "pnr_sensor": "temp",         # Thermal runaway as bearing seizes
        "primary_sensor": "vib",
        "intervention_type": "maintenance_scheduling",
    },
    # ── Short Horizon (Minutes) — Automated/SCADA Control ────────────────────
    "gas_lock": {
        "horizon_label": "Minutes",
        "total_hours": 0.75,          # 45 min
        "scada_alarm_health": 0.30,
        "pnr_health": 0.12,
        "scada_sensor": "psi",        # PSI drops below 800 psi critical threshold
        "pnr_sensor": "temp",         # Winding temperature burnout at PNR
        "primary_sensor": "psi",      # Intake Pressure is the causal leading sensor
        "intervention_type": "operational_control",
    },
    "pulsation_dampener_failure": {
        "horizon_label": "Minutes",
        "total_hours": 0.083,         # 5 min — catastrophic / emergency
        "scada_alarm_health": 0.50,
        "pnr_health": 0.25,
        "scada_sensor": "psi",        # Pressure spike (bladder rupture)
        "pnr_sensor": "psi",          # Pressure / pipe rupture risk
        "primary_sensor": "psi",
        "intervention_type": "emergency_shutdown",
    },
    "valve_failure": {
        "horizon_label": "Minutes",
        "total_hours": 0.25,          # 15 min
        "scada_alarm_health": 0.40,
        "pnr_health": 0.15,
        "scada_sensor": "psi",        # Pressure drop (check valve failed open)
        "pnr_sensor": "psi",          # Pressure / valve destroyed
        "primary_sensor": "psi",
        "intervention_type": "operational_control",
    },
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
            # 4th sensor normal values
            _s4c = SENSOR4_CONFIG.get(asset_class)
            if _s4c:
                reading[_s4c["key"]] = round(random.uniform(*_s4c["normal_range"]), 1)
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
            # 4th sensor fault values
            _s4c = SENSOR4_CONFIG.get(asset_class)
            if _s4c and _s4c["range_key"] in profile:
                reading[_s4c["key"]] = round(random.uniform(*profile[_s4c["range_key"]]), 1)
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

        # ── 4th-sensor ramp (ESP: motor_amps, Mud Pump: spm) ──────────────────
        _s4c = SENSOR4_CONFIG.get(asset_class)
        _s4_val = None
        if _s4c and _s4c["range_key"] in profile:
            _s4_nom = _s4c["nominal"]
            _s4_rng = profile[_s4c["range_key"]]
            _s4_end = (_s4_rng[0] + _s4_rng[1]) / 2.0
            if asset_class == "mud_pump" and fault_type == "pulsation_dampener_failure":
                _s4_val = round(random.uniform(_s4_rng[0], _s4_rng[1]), 1)
            else:
                _s4_mid = _s4_nom + t * (_s4_end - _s4_nom)
                _s4_val = round(max(10.0, _s4_mid + random.uniform(-abs(_s4_mid * 0.003), abs(_s4_mid * 0.003))), 1)

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
        if _s4_val is not None:
            reading[_s4c["key"]] = _s4_val
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

    # Final 4th-sensor value (hold at fault midpoint for hold phase)
    _s4c_hold = SENSOR4_CONFIG.get(asset_class)
    _final_s4 = None
    _final_s4_rng = None
    if _s4c_hold and _s4c_hold["range_key"] in profile:
        _final_s4_rng = profile[_s4c_hold["range_key"]]
        _final_s4 = (_final_s4_rng[0] + _final_s4_rng[1]) / 2.0

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
        # 4th sensor hold-phase value
        if _final_s4 is not None and _s4c_hold is not None:
            if asset_class == "mud_pump" and fault_type == "pulsation_dampener_failure":
                hold_reading[_s4c_hold["key"]] = round(random.uniform(_final_s4_rng[0], _final_s4_rng[1]), 1)
            else:
                hold_reading[_s4c_hold["key"]] = round(max(10.0, _final_s4 + random.uniform(-abs(_final_s4 * 0.003), abs(_final_s4 * 0.003))), 1)
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
    # Clear the health score smoothing buffer so stale predictions don't bleed into
    # the next injection cycle on the same asset.
    HEALTH_HISTORY.pop(asset_id, None)
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
            # 4th sensor fault values for scenario injections
            _s4c = SENSOR4_CONFIG.get(asset_class)
            if _s4c and _s4c["range_key"] in profile:
                reading[_s4c["key"]] = round(random.uniform(*profile[_s4c["range_key"]]), 1)
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
            HEALTH_HISTORY.pop(asset_id, None)
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


# ── Health Models Status (Phase 5.2) ──────────────────────────────────────────
@app.get("/api/model/status")
def get_model_status():
    """Return Phase 5.1 health model registry status."""
    return {
        "phase": "5.1",
        "model_type": "health_score",
        "models_loaded": list(HEALTH_MODELS.keys()),
        "models_dir": str(MODELS_DIR),
        "fault_physics": {k: {"total_hours": v["total_hours"],
                              "horizon_label": v["horizon_label"],
                              "intervention_type": v["intervention_type"]}
                          for k, v in FAULT_PHYSICS.items()},
    }


class ModelVersionRequest(BaseModel):
    version: str   # "v1" or "v2"


@app.post("/api/model/version")
def set_model_version(req: ModelVersionRequest):
    """
    MLOps demo endpoint — simulates switching between model versions.
    Clears the EWA health-score smoothing buffers so the next inference
    cycle starts fresh (no stale predictions bleeding through).

    In the real GDC pipeline this would trigger an edge model swap via
    the GDC Edge Registry; here it resets the in-memory HEALTH_HISTORY
    to produce an immediate observable change in the UI.

    version: "v1" (legacy, noisier) | "v2" (retrained, stable)
    """
    if req.version not in ("v1", "v2"):
        raise HTTPException(status_code=400, detail=f"Unknown model version: {req.version}. Use 'v1' or 'v2'.")
    # Clear EWA smoothing buffers — forces fresh prediction on next poll cycle
    HEALTH_HISTORY.clear()
    log.info(f"🔄 Model version switched to {req.version} — HEALTH_HISTORY cleared")
    return {
        "status": "switched",
        "version": req.version,
        "message": (
            f"Edge model set to {req.version}. "
            f"EWA health-score buffers cleared — next inference cycle uses clean baseline."
        ),
    }


# ── Fault-Physics API (Phase 5.2) ──────────────────────────────────────────────
@app.get("/api/fault-physics")
def get_fault_physics():
    """Return FAULT_PHYSICS config for all fault modes — used by the Copilot Workspace."""
    return {"fault_physics": FAULT_PHYSICS}


@app.get("/api/fault-physics/{fault_type}")
def get_fault_physics_for(fault_type: str):
    """Return FAULT_PHYSICS config for a single fault type."""
    fp = FAULT_PHYSICS.get(fault_type)
    if not fp:
        raise HTTPException(status_code=404, detail=f"No FAULT_PHYSICS entry for: {fault_type}")
    return {"fault_type": fault_type, "physics": fp}


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
def plot_forecast(asset_id: str, metric: str = "auto"):
    """
    Returns a Plotly time-series chart with:
      - Historical telemetry for the selected sensor (psi | temp | vib)
      - XGBoost RUL Regressor prediction → dotted line + Cone of Uncertainty
      - Alarm threshold line (when crossed, SCADA would fire — GDC predicts when)
      - Estimated alarm time vertical marker (red)
      - Point of No Return vertical marker (orange)

    metric: psi | temp | vib | auto (auto selects the primary degrading sensor)
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
                SELECT event_time, psi, temp_f, vibration, motor_amps, spm,
                       failure_type, predicted_label
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

    # Strip tzinfo from DB timestamps so everything matches active_degrades naive UTC
    times  = [r["event_time"].replace(tzinfo=None) if getattr(r["event_time"], "tzinfo", None) else r["event_time"] for r in rows]
    psi_v  = np.array([float(r["psi"])       for r in rows])
    temp_v = np.array([float(r["temp_f"])    for r in rows])
    vib_v  = np.array([float(r["vibration"]) for r in rows])
    now    = times[-1]

    # Select metric to plot
    # "amps" and "spm" are explicitly user-selected (4th sensor tab) — never auto-chosen
    if metric == "auto" or metric not in ("psi", "temp", "vib", "amps", "spm"):
        # Pick the sensor with the highest relative deviation from its nominal
        nom_psi  = asset_meta["nominal_psi"]
        nom_temp = asset_meta["nominal_temp_f"]
        nom_vib  = asset_meta["nominal_vib"]
        dev_psi  = abs(psi_v[-1]  - nom_psi)  / max(nom_psi,  1)
        dev_temp = abs(temp_v[-1] - nom_temp) / max(nom_temp, 1)
        dev_vib  = abs(vib_v[-1]  - nom_vib)  / max(nom_vib,  1)
        metric = "psi" if dev_psi >= dev_temp and dev_psi >= dev_vib else \
                 "temp" if dev_temp >= dev_vib else "vib"

    _s4c = SENSOR4_CONFIG.get(asset_class)   # None for gas_lift / top_drive

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
    elif metric in ("amps", "spm") and _s4c is not None:
        # 4th sensor chart: motor_amps (ESP) or spm (Mud Pump)
        _s4_key = _s4c["key"]
        y_vals   = np.array([float(r.get(_s4_key) or _s4c["nominal"]) for r in rows])
        y_label  = _s4c["label"]
        y_crit   = _s4c["crit"]
        crit_dir = _s4c["crit_dir"]
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
    dpsi_dt = dtemp_dt = dvib_dt = 0.0   # init slopes — overridden below when classifier is active
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
    # Phase 5.2: pre-initialize health score + FAULT_PHYSICS vars at function scope
    # so they're accessible in the timeline section below even if try block raises.
    _health_score = None   # health_score from HEALTH_MODELS predict (1.0 → 0.0)
    _fp           = {}     # FAULT_PHYSICS entry for current fault type
    _fp_pnr_hs    = 0.05   # pnr_health threshold (default)
    _fp_total_h   = 1.0    # total_hours (default)
    _fp_hlabel    = "Hours"  # horizon_label (default)

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

            # ── 4th-sensor window and slope (ESP: motor_amps, Mud Pump: spm) ──
            # Uses the same fault-window filter as the 3 primary sensors.
            last_s4 = ds4_dt = 0.0
            if _s4c is not None and asset_class in ("esp", "mud_pump"):
                _s4_key = _s4c["key"]
                s4_v_all = np.array([
                    float(r.get(_s4_key) or _s4c["nominal"]) for r in rows
                ])
                if len(fault_idx) >= 6:
                    s4_w = s4_v_all[fault_idx]
                else:
                    win  = min(60, len(s4_v_all))
                    s4_w = s4_v_all[-win:]
                last_s4 = float(np.median(s4_w[-curr_n:]))
                t_s4    = np.arange(len(s4_w), dtype=np.float64)
                ds4_dt  = (float(np.polyfit(t_s4, s4_w, 1)[0]) * READINGS_PER_MIN
                           if len(s4_w) >= 6 else 0.0)

            # ── Phase 5.2: Health Score predict via HEALTH_MODELS ─────────────
            # Detects fault type early here so FAULT_PHYSICS can scale the
            # health_score prediction to physical time (Days / Hours / Minutes).
            _fp_fault_type = (
                active_degrades.get(asset_id, {}).get("fault_type")
                or next(
                    ((r.get("failure_type") or "").lower()
                     for r in rows
                     if (r.get("failure_type") or "").lower() not in ("normal", "")),
                    None,
                )
            )
            _fp = FAULT_PHYSICS.get(_fp_fault_type, {}) if _fp_fault_type else {}
            _fp_total_h  = _fp.get("total_hours",        1.0)
            _fp_scada_hs = _fp.get("scada_alarm_health", 0.15)
            _fp_pnr_hs   = _fp.get("pnr_health",         0.05)
            _fp_hlabel   = _fp.get("horizon_label",      "Hours")

            health_model = HEALTH_MODELS.get(asset_class)
            _hs_raw = None
            if health_model is not None:
                import xgboost as xgb
                if asset_class == "esp":
                    feature_row = np.array([[last_psi, last_temp, last_vib, last_s4,
                                             dpsi_dt, dtemp_dt, dvib_dt, ds4_dt]])
                    fn = ["psi","temp_f","vibration","motor_amps",
                          "dpsi_dt","dtemp_dt","dvib_dt","damps_dt"]
                elif asset_class == "mud_pump":
                    feature_row = np.array([[last_psi, last_temp, last_vib, last_s4,
                                             dpsi_dt, dtemp_dt, dvib_dt, ds4_dt]])
                    fn = ["psi","temp_f","vibration","spm",
                          "dpsi_dt","dtemp_dt","dvib_dt","dspm_dt"]
                else:
                    feature_row = np.array([[last_psi, last_temp, last_vib,
                                             dpsi_dt, dtemp_dt, dvib_dt]])
                    fn = ["psi","temp_f","vibration","dpsi_dt","dtemp_dt","dvib_dt"]
                _hs_raw = max(0.0, min(1.0,
                    float(health_model.predict(xgb.DMatrix(feature_row, feature_names=fn))[0])
                ))
                log.debug(f"Health raw={_hs_raw:.4f} asset={asset_id} "
                          f"fault={_fp_fault_type} psi={last_psi:.0f} vib={last_vib:.3f}")
            else:
                # Geometric fallback: normalize sensor deviation to pseudo-health
                log.warning(f"No health model for {asset_class} — using sensor fallback")
                if n_w >= 2:
                    _dev = abs(float(y_vals[-1]) - y_crit) / max(abs(
                        asset_meta.get("nominal_psi" if metric == "psi" else
                                       "nominal_temp_f" if metric == "temp" else "nominal_vib",
                                       y_crit) - y_crit), 1.0)
                    _hs_raw = max(0.0, min(1.0, _dev))
                else:
                    _hs_raw = 0.5

            # ── EWA smoothing (10 readings, ~100s window) ─────────────────────
            if _hs_raw is not None:
                if asset_id not in HEALTH_HISTORY:
                    HEALTH_HISTORY[asset_id] = deque(maxlen=10)
                HEALTH_HISTORY[asset_id].append(_hs_raw)
                hist    = list(HEALTH_HISTORY[asset_id])
                n_hist  = len(hist)
                weights = np.array([0.75 ** (n_hist - 1 - i) for i in range(n_hist)])
                _health_score = float(np.average(hist, weights=weights))

                # Convert health_score → rul_minutes for chart marker backward compat
                # rul_minutes = time until SCADA alarm threshold is crossed
                _ttscada_h = max(0.0, (_health_score - _fp_scada_hs) * _fp_total_h)
                rul_minutes = _ttscada_h * 60.0  # minutes until SCADA alarm

                # Status text reflects health score + FAULT_PHYSICS tier
                if _health_score <= _fp_pnr_hs:
                    status_color = "#f44336"
                    status_text  = f"🔴 PAST PNR — Health {_health_score:.0%}"
                elif _health_score <= _fp_scada_hs:
                    status_color = "#ff6d00"
                    status_text  = f"⚠ SCADA ALARM ZONE — Health {_health_score:.0%}"
                elif _health_score < 0.70:
                    status_color = "#ffb300"
                    status_text  = f"⚡ DEGRADATION — Health {_health_score:.0%}"
                else:
                    status_color = "#ffb300"
                    status_text  = f"⚡ EARLY FAULT DETECTED — Health {_health_score:.0%}"
                forecast_color = "#ff8c00"

        except Exception as e:
            log.warning(f"RUL prediction failed for {asset_id}: {e}")
    elif len(rows) < 8:
        status_text  = f"⏳ COLLECTING BASELINE ({len(rows)}/8 readings)"
        status_color = "#5a6a7a"

    if rul_minutes is None:
        status_color = forecast_color  # green for nominal

    # ── Phase 6.1: Sensor Routing — only annotate causal sensor tabs ──────────
    # _fp already has scada_sensor / pnr_sensor / primary_sensor added in Phase 6.1.
    # Show SCADA alarm threshold + "Alarm in Xm" marker ONLY on the tab that drives
    # the SCADA alarm for this fault. Show PNR marker ONLY on the PNR-causal tab.
    # If no FAULT_PHYSICS entry (nominal / unknown fault), show annotations on all
    # tabs for backward compatibility.
    _fp_scada_sensor = _fp.get("scada_sensor") if _fp else None
    _fp_pnr_sensor   = _fp.get("pnr_sensor")   if _fp else None
    _fp_primary      = _fp.get("primary_sensor") if _fp else None
    _show_scada_annotations = (not _fp_scada_sensor) or (metric == _fp_scada_sensor)
    _show_pnr_annotation    = (not _fp_pnr_sensor)   or (metric == _fp_pnr_sensor)

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
        for i, r in enumerate(rows):
            ft = (r.get("failure_type") or "").lower()
            if ft and ft != "normal":
                fault_onset = times[i]; detected_fault_type = ft; break
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
    y_start = float(np.median(y_vals[-5:]))
    y_end   = y_crit * 0.98 if crit_dir == "below" else y_crit * 1.02

    # ── Phase 5.2: Physical timeline from health score via FAULT_PHYSICS ──────
    # ttf_time = SCADA alarm time  (now + time_to_scada  from health score)
    # pnr_t    = PNR time          (now + time_to_pnr    from health score)
    # INVARIANT: ttf_time < pnr_t because scada_alarm_health > pnr_health (always)
    # This guarantees: ML Detection → SCADA Alarm → PNR → Failure SEQUENCE IS CORRECT
    ttf_time      = (now + timedelta(minutes=rul_minutes)) if (rul_minutes is not None and rul_minutes > 0) else None
    pnr_t         = None
    _pnr_m_final  = 0
    _pnr_label    = ""
    if _health_score is not None and _fp:
        # Phase 5.2: PNR from FAULT_PHYSICS pnr_health threshold
        # ALWAYS after ttf_time (SCADA alarm) because pnr_health < scada_alarm_health
        _ttpnr_h = max(0.0, (_health_score - _fp_pnr_hs) * _fp_total_h)
        if _ttpnr_h > 0:
            pnr_t = now + timedelta(hours=_ttpnr_h)
            _pnr_m_final = int(_ttpnr_h * 60)
            if _fp_hlabel == "Days":
                _pnr_label = f"T+{_ttpnr_h/24:.1f}d"
            elif _fp_hlabel == "Minutes":
                _pnr_label = f"T+{_ttpnr_h*60:.0f}m"
            else:
                _pnr_label = f"T+{_ttpnr_h:.1f}h"
    elif classifier_active and fault_onset and detected_fault_type:
        # Fallback: legacy clock-based PNR if no FAULT_PHYSICS entry
        _pnr_m_final = PNR_MINUTES.get(detected_fault_type, 0)
        if _pnr_m_final > 0:
            pnr_t = fault_onset + timedelta(minutes=_pnr_m_final)
        _pnr_label = f"T+{_pnr_m_final}m"

    # X-axis end: sized to show alarm and PNR times clearly.
    # PNR only extends the axis if it's within 60 minutes — avoids 2-hour wide charts
    # for high-PNR faults like sand_ingress (120m) and bearing_wear (240m).
    _x_cands = [now + timedelta(minutes=40)]
    if ttf_time is not None:
        _x_cands.append(ttf_time + timedelta(minutes=8))
    if pnr_t is not None:
        _mins_to_pnr = (pnr_t - now).total_seconds() / 60
        if _mins_to_pnr <= 60:
            _x_cands.append(pnr_t + timedelta(minutes=5))
    _x_end = min(max(_x_cands), now + timedelta(minutes=60))

    # Projection spans from now to x-axis end
    horizon_min  = max(int((_x_end - now).total_seconds() / 60) + 1, 40)
    future_times = [now + timedelta(minutes=i) for i in range(1, horizon_min + 1)]
    t_arr        = np.array(range(1, len(future_times) + 1), dtype=float)

    # ── Bug 1 Fix (Phase 6.1): Exponential decay — NO CLAMPING AT SCADA THRESHOLD ──
    # Previously used np.clip(t/rul_minutes, 0, 1) which caused the dotted line to go
    # FLAT at y_end (the SCADA threshold level) for the remainder of the x-axis.
    # Physically wrong: the asset does not stabilise when a SCADA alarm fires — it
    # continues degrading through the PNR and on to full failure.
    #
    # Fix: use a smooth exponential curve (k=3.5, matching the Phase 5 training curve)
    # over the FULL failure horizon (total_hours from FAULT_PHYSICS), not just rul_minutes.
    # The line crosses y_crit (SCADA threshold) en-route to y_failure (asset destroyed).
    # No np.clip — the curve never plateaus.
    if rul_minutes is not None and rul_minutes < 580:
        # Total time-to-failure from FAULT_PHYSICS (always longer than rul_minutes)
        ttf_total_min = (_fp_total_h * 60.0) if _fp else max(rul_minutes * 3.0, 60.0)
        # y_failure: where the sensor ends up at health=0 (well past the SCADA threshold)
        if crit_dir == "below":
            y_failure = max(y_crit * 0.45, 1.0)  # 55% below alarm threshold at full failure
        else:
            y_failure = y_crit * 1.80              # 80% above alarm threshold at full failure
        # Phase 10 Bug 4 fix: Two-segment exponential so the SCADA alarm vertical marker
        # aligns exactly where the dotted curve crosses y_crit.
        # Segment 1 [0 → rul_minutes]: y_start → y_crit using (exp(k*t/T1)-1)/(exp(k)-1)
        # Segment 2 [rul_minutes → ttf_total_min]: y_crit → y_failure
        # At t=rul_minutes the curve equals y_crit exactly (denominator normalises to 1).
        _k    = 3.5
        _expk = np.exp(_k) - 1.0
        _rm   = max(float(rul_minutes), 0.01)
        _seg1 = t_arr <= _rm
        _seg2 = ~_seg1
        forecast_y          = np.empty(len(t_arr))
        forecast_y[_seg1]   = y_start + (y_crit - y_start) * (np.exp(_k * t_arr[_seg1] / _rm) - 1.0) / _expk
        _remain             = max(ttf_total_min - _rm, 1.0)
        forecast_y[_seg2]   = y_crit + (y_failure - y_crit) * (np.exp(_k * (t_arr[_seg2] - _rm) / _remain) - 1.0) / _expk
    else:
        forecast_y = np.full(len(future_times), y_start)

    # Uncertainty cone: widens as a fraction of the projected y-range.
    # Using a fraction of y_start made the cone invisibly thin (0.04 mm/s on a
    # 1–9 mm/s vibration chart). Using the traversed range makes it proportional.
    _proj_range = abs(y_end - y_start) if rul_minutes is not None else abs(y_crit - y_start) * 0.1
    _cone_frac  = np.linspace(0.04, 0.18, len(future_times))  # 4% → 18% of range
    noise       = _cone_frac * max(_proj_range, abs(y_start) * 0.05)
    upper_y     = forecast_y + noise
    lower_y     = forecast_y - noise
    cone_rgba   = "255,140,0" if rul_minutes is not None else "0,230,118"

    # ── Build Plotly Figure ───────────────────────────────────────────────────
    fig = go.Figure()

    # 1. Historical telemetry — blue solid
    fig.add_trace(go.Scatter(
        x=times, y=y_vals, mode="lines", name="Live Telemetry",
        line=dict(color="#1e90ff", width=2.5),
    ))

    # 2. ML RUL projection — orange dotted
    fig.add_trace(go.Scatter(
        x=future_times, y=forecast_y, mode="lines", name="ML RUL Projection",
        line=dict(color=forecast_color, width=2.5, dash="dot"),
    ))

    # 3. Uncertainty cone
    fig.add_trace(go.Scatter(
        x=future_times + future_times[::-1],
        y=list(upper_y) + list(lower_y)[::-1],
        fill="toself", fillcolor=f"rgba({cone_rgba}, 0.08)",
        line=dict(color="rgba(255,255,255,0)"),
        name="Confidence Band", hoverinfo="skip",
    ))

    # 4. Alarm threshold — dashed red horizontal
    # Phase 6.1 fix: only draw on the SCADA-causal sensor tab.
    # e.g. for gas_lock: SCADA fires on Motor Current underload → only on "amps" tab.
    # Showing this line on the PSI or Vibration tab is physically misleading.
    if _show_scada_annotations:
        fig.add_trace(go.Scatter(
            x=[times[0], future_times[-1]], y=[y_crit, y_crit],
            mode="lines", name="SCADA Alarm Threshold",
            line=dict(color="#f44336", width=1.5, dash="dash"),
            hoverinfo="skip",
        ))

    # ── Chart title ───────────────────────────────────────────────────────────
    _title_text = (
        f"<b>{asset_id}</b> — {y_label}<br>"
        f"<span style='font-size:12px;color:{forecast_color}'>{status_text}</span>"
    )

    # ── State B: PNR Exceeded ─────────────────────────────────────────────────
    if is_pnr_exceeded and not is_asset_failed_plot and fault_onset and detected_fault_type:
        _fl = detected_fault_type.replace("_", " ").upper()
        _title_text = (
            f"<b>⚠ INTERVENTION WINDOW CLOSED — {_fl}</b><br>"
            f"<span style='color:#f44336;font-size:11px'>⛔ PNR exceeded — damage window has passed</span>"
        )
        if pnr_t and pnr_t >= times[0]:
            fig.add_annotation(
                x=pnr_t, y=0.5, xref="x", yref="paper",
                text="<b>⛔ PNR PASSED<br>Damage Irreversible</b>",
                showarrow=False, xanchor="center",
                font=dict(color="#f44336", size=13, family="JetBrains Mono"),
                bgcolor="rgba(244,67,54,0.18)", bordercolor="rgba(244,67,54,0.7)",
                borderpad=8, borderwidth=1,
            )

    # ── State C: Asset Failed ─────────────────────────────────────────────────
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

    # ── Vertical Marker 1: ML Predicted SCADA Alarm Time ── BRIGHT RED ────────
    # Phase 6.1 fix: only shown on the scada_sensor tab.
    # The alarm fires when the SPECIFIC causal sensor crosses its threshold.
    # Showing "Alarm in Xm" on a non-SCADA tab (e.g., vib tab for gas_lock
    # where SCADA fires on amps) would imply the alarm fires based on vibration,
    # which is wrong. Only the amps tab shows this marker for gas_lock.
    if ttf_time is not None and _show_scada_annotations:
        _lbl = f"{int(rul_minutes)}m" if rul_minutes < 60 else f"{int(rul_minutes//60)}h {int(rul_minutes%60)}m"
        fig.add_shape(
            type="line", x0=ttf_time, x1=ttf_time, y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(color="rgba(255,23,68,0.95)", width=3, dash="solid"),
        )
        fig.add_annotation(
            x=ttf_time, y=0.97, xref="x", yref="paper",
            text=f"<b>⚡ SCADA Alarm in {_lbl}</b>",
            showarrow=False, xanchor="center",
            font=dict(color="#ff1744", size=11, family="JetBrains Mono"),
            bgcolor="rgba(255,23,68,0.15)", bordercolor="rgba(255,23,68,0.5)", borderpad=4,
        )

    # ── Vertical Marker 2: Point of No Return ── ORANGE ───────────────────────
    # Phase 6.1 fix: only shown on the pnr_sensor tab.
    # For gearbox_bearing_spalling: PNR fires on temperature (seize) → only shown
    # on the Temp tab. Showing it on the Vibration tab would imply PNR is
    # vibration-based, which is physically wrong.
    if pnr_t is not None and classifier_active and _show_pnr_annotation:
        fig.add_shape(
            type="line", x0=pnr_t, x1=pnr_t, y0=0, y1=1,
            xref="x", yref="paper",
            line=dict(color="rgba(255,109,0,0.95)", width=3, dash="solid"),
        )
        fig.add_annotation(
            x=pnr_t, y=0.81, xref="x", yref="paper",
            text=f"<b>⛔ PNR {_pnr_label}</b>",
            showarrow=False, xanchor="center",
            font=dict(color="#ff6d00", size=11, family="JetBrains Mono"),
            bgcolor="rgba(255,109,0,0.15)", bordercolor="rgba(255,109,0,0.5)", borderpad=4,
        )

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
    )
    # ── NOW line added AFTER update_layout so it doesn't get overwritten ──────
    # CRITICAL: update_layout(shapes=[...]) REPLACES the shapes list.
    # All vertical markers above use fig.add_shape() which appends.
    # Adding the NOW line here (also via add_shape) preserves everything.
    fig.add_shape(
        type="line", x0=now, x1=now, y0=0, y1=1, xref="x", yref="paper",
        line=dict(color="#5a6a7a", width=1.5, dash="dot"),
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


# ── Agent Context API (Phase 4 — Agentic Predictive Maintenance) ──────────────
# Returns scenario-specific enterprise context data for the given fault type.
# Each fault maps to a different enterprise system and agentic scenario:
#   supply_chain         → ERP (SAP MM) — procurement, lead times, inventory
#   workforce_scheduling → FSM (Maximo) — crew schedules, work order append
#   operational_control  → Rig Control (Pason EDR) — rig state, pump status
AGENT_CONTEXTS = {
    "sand_ingress": {
        "enterprise_source": "ERP_SAP_MM", "source_label": "SAP Materials Management",
        "scenario": "supply_chain",
        "well_bom": {
            "part_description": "ESP Sand-Handler Assembly",
            "series": "400", "stages": 100, "design_rate_bpd": 2000,
            "material_spec": "Tungsten Carbide Radial Bearings",
            "manufacturer": "Baker Hughes Centrilift",
            "mat_doc_number": "MAT-4002-TC-100", "unit_cost_usd": 145000,
        },
        "inventory": {"storage_location_local": 0, "storage_location_midland_hub": 0,
                      "manufacturer_available_stock": 1, "manufacturer_location": "Claremore, OK"},
        "lead_times": {"standard_freight_days": 12, "air_freight_days": 7, "air_freight_premium_usd": 8500},
        "daily_production_value_usd": 8500,
    },
    "motor_overheat": {
        "enterprise_source": "ERP_SAP_MM", "source_label": "SAP Materials Management",
        "scenario": "supply_chain",
        "well_bom": {
            "part_description": "ESP Motor Assembly — Class H Winding",
            "series": "456", "hp": 200,
            "material_spec": "Class H High-Temperature Insulation",
            "manufacturer": "Baker Hughes Centrilift",
            "mat_doc_number": "MTR-456-200HP-H", "unit_cost_usd": 62000,
        },
        "inventory": {"storage_location_local": 0, "storage_location_midland_hub": 1,
                      "manufacturer_available_stock": 3, "manufacturer_location": "Houston, TX"},
        "lead_times": {"standard_freight_days": 5, "air_freight_days": 2, "air_freight_premium_usd": 3200},
        "daily_production_value_usd": 8500,
    },
    "gas_lock": {
        "enterprise_source": "SCADA_LOCAL", "source_label": "Local SCADA/VFD Control",
        "scenario": "software_command",
        "available_commands": [
            {"cmd": "vfd_freq_reduce_15pct", "label": "Reduce VFD Frequency 15%",
             "effect": "Lowers intake pressure requirements — allows gas void to migrate up annulus",
             "cost_usd": 0, "time_min": 1},
            {"cmd": "annulus_valve_open", "label": "Open Casing Annulus Valve",
             "effect": "Bleeds casing annulus gas, reducing GVF at pump intake",
             "cost_usd": 0, "time_min": 2},
        ],
        "current_vfd_freq_hz": 52.0, "recommended_freq_hz": 44.2,
    },
    "thermal_runaway": {
        "enterprise_source": "FSM_MAXIMO", "source_label": "IBM Maximo Field Service",
        "scenario": "workforce_scheduling",
        "site": "pad_bravo",
        "upcoming_dispatches": [
            {
                "work_order_id": "WO-2026-0847", "crew_id": "CREW-BRAVO-B", "headcount": 2,
                "scheduled_date": "Tomorrow", "scheduled_time_local": "14:00",
                "primary_task": "Transmitter calibration — Well B-3",
                "estimated_duration_hours": 2.0,
                "certifications": ["compressor_operator", "h2s_safety"],
                "available_capacity_hours": 2.5,
            }
        ],
        "appended_task": {
            "description": "Aerial fin-fan cooler flush — GLIFT-BRAVO-1",
            "estimated_duration_hours": 0.75,
            "required_certifications": ["compressor_operator"],
            "parts_required": False, "parts_cost_usd": 0, "labor_cost_usd": 0,
            "emergency_dispatch_cost_usd": 1800,
        },
    },
    "bearing_wear": {
        "enterprise_source": "FSM_MAXIMO", "source_label": "IBM Maximo Field Service",
        "scenario": "workforce_scheduling",
        "site": "pad_bravo",
        "upcoming_dispatches": [
            {
                "work_order_id": "WO-2026-0851", "crew_id": "CREW-BRAVO-A", "headcount": 3,
                "scheduled_date": "Day After Tomorrow", "scheduled_time_local": "09:00",
                "primary_task": "Quarterly compressor inspection — All Units",
                "estimated_duration_hours": 4.0,
                "certifications": ["compressor_operator", "millwright", "h2s_safety"],
                "available_capacity_hours": 3.0,
            }
        ],
        "appended_task": {
            "description": "Journal bearing replacement — GLIFT-BRAVO crankshaft",
            "estimated_duration_hours": 3.0,
            "required_certifications": ["millwright", "compressor_operator"],
            "parts_required": True, "part_number": "ARJ-42-BEARING-KIT",
            "parts_cost_usd": 8200, "parts_in_stock": True,
            "emergency_dispatch_cost_usd": 22000,
        },
    },
    "valve_failure": {
        "enterprise_source": "FSM_MAXIMO", "source_label": "IBM Maximo Field Service",
        "scenario": "emergency_dispatch",
        "site": "pad_bravo", "upcoming_dispatches": [],
        "emergency_crew": {
            "crew_id": "CREW-EMERGENCY-A", "headcount": 2,
            "est_arrival_hours": 1.5,
            "certifications": ["compressor_operator", "h2s_safety"],
            "callout_cost_usd": 3200,
        },
        "required_parts": {
            "part_description": "Check Valve Disk Assembly",
            "part_number": "CVD-1200-PSI-4IN",
            "in_stock_local": True, "unit_cost_usd": 1800,
        },
    },
    "valve_washout": {
        "enterprise_source": "DRILLSYS_PASON_EDR", "source_label": "Pason Electronic Drilling Recorder",
        "scenario": "operational_control", "local_query": True,
        "rig_id": "RIG-42", "hole_depth_ft": 12450, "inclination_deg": 38.5,
        "next_connection_min": 22,
        "ecd_constraints": {"min_flow_gpm_hole_cleaning": 650, "current_total_flow_gpm": 700},
        "pump_status": {
            "MUD-RIG42-1": {"status": "active", "current_spm": 89, "output_gpm": 350,
                            "volumetric_efficiency_pct": 81, "ve_trend": "declining"},
            "MUD-RIG42-2": {"status": "active", "current_spm": 89, "output_gpm": 350,
                            "volumetric_efficiency_pct": 95, "ve_trend": "stable"},
            "MUD-RIG42-3": {"status": "standby", "ready": True, "output_gpm": 0},
        },
        "recommended_transition": {
            "step_1": "Bring MUD-RIG42-3 online to 300 GPM",
            "step_2": "Verify stable standpipe pressure (allow 60s)",
            "step_3": "Reduce MUD-RIG42-1 to 50 GPM — maintenance mode",
            "result": "Total flow maintained at 700 GPM. ECD stable.",
        },
    },
    "pulsation_dampener_failure": {
        "enterprise_source": "DRILLSYS_PASON_EDR", "source_label": "Pason Electronic Drilling Recorder",
        "scenario": "emergency_stop", "local_query": True,
        "rig_id": "RIG-42",
        "immediate_action": "EMERGENCY STOP — Pump room personnel must evacuate immediately",
        "pump_status": {
            "MUD-RIG42-1": {"status": "active", "current_spm": 89, "output_gpm": 350},
            "MUD-RIG42-2": {"status": "active", "current_spm": 89, "output_gpm": 350},
            "MUD-RIG42-3": {"status": "standby", "ready": True, "output_gpm": 0},
        },
    },
    "piston_seal_wear": {
        "enterprise_source": "ERP_SAP_MM", "source_label": "SAP Materials Management",
        "scenario": "supply_chain",
        "well_bom": {
            "part_description": "Triplex Pump Liner Seal Kit",
            "material_spec": "Polyurethane Piston Cups + Liner O-Rings",
            "manufacturer": "National Oilwell Varco",
            "mat_doc_number": "NOV-SEAL-TK-7500", "unit_cost_usd": 3800,
        },
        "inventory": {"storage_location_local": 2, "storage_location_midland_hub": 8,
                      "manufacturer_available_stock": 100},
        "lead_times": {"standard_freight_days": 1, "air_freight_days": 0, "air_freight_premium_usd": 0},
    },
    "gearbox_bearing_spalling": {
        "enterprise_source": "ERP_SAP_MM", "source_label": "SAP Materials Management",
        "scenario": "supply_chain",
        "well_bom": {
            "part_description": "Top Drive Gearbox Bearing Kit",
            "material_spec": "Tapered Roller Bearing Set — NOV 250T Top Drive",
            "manufacturer": "National Oilwell Varco",
            "mat_doc_number": "NOV-250T-BEAR-KIT", "unit_cost_usd": 28500,
        },
        "inventory": {"storage_location_local": 0, "storage_location_midland_hub": 0,
                      "manufacturer_available_stock": 2, "manufacturer_location": "Houston, TX"},
        "lead_times": {"standard_freight_days": 4, "air_freight_days": 1, "air_freight_premium_usd": 6000},
        "next_planned_trip_hours": 18, "daily_rig_rate_usd": 45000,
    },
    "hydraulic_leak": {
        "enterprise_source": "DRILLSYS_PASON_EDR", "source_label": "Pason Electronic Drilling Recorder",
        "scenario": "operational_monitor", "local_query": True,
        "rig_id": "RIG-42",
        "hydraulic_system": {
            "current_pressure_psi": 2940, "reservoir_level_pct": 78,
            "leak_rate_psi_per_hr": 12, "estimated_hours_to_low_alarm": 3.6,
        },
        "spare_parts_on_rig": {
            "hydraulic_hose_3000psi": 2, "jic_fittings_3000psi": 6, "hydraulic_fluid_gal": 15,
        },
    },
}


@app.get("/api/agent/context/{fault_type}")
def get_agent_context(fault_type: str, asset_id: str = None):
    """Return enterprise context data for the given fault type (Phase 4 Agent API)."""
    context = AGENT_CONTEXTS.get(fault_type, {
        "enterprise_source": "ERP_SAP_MM", "source_label": "SAP Materials Management",
        "scenario": "general",
        "message": f"No specific enterprise context configured for: {fault_type}",
    })
    return {"fault_type": fault_type, "asset_id": asset_id, "context": context}


@app.post("/api/agent/recommend")
def get_agent_recommend(
    fault_type: str,
    asset_id: str,
    slider_health_score: float = None,  # Phase 5.2: Intervention Slider position (0.0–1.0)
    rul_minutes: float = None,           # Backward compat — derived from slider if absent
    is_pnr_exceeded: bool = False,
    chat_history: list = None,           # Phase 5.2: multi-turn [{role, content}]
):
    """
    Phase 5.2 — Health-score-aware agentic recommendation.

    Accepts `slider_health_score` (0.0–1.0) from the Intervention Slider to provide
    context-aware recommendations based on WHERE the operator places the slider.
    Intervention tier (EARLY/URGENT/CRITICAL/RECOVERY) is computed from health score
    vs FAULT_PHYSICS thresholds.  Multi-turn conversation supported via chat_history.

    Falls back to rule-based templates if Gemma is unavailable.
    """
    # ── Resolve health score and rul_minutes ──────────────────────────────────
    fp        = FAULT_PHYSICS.get(fault_type, {})
    fp_total  = fp.get("total_hours",        1.0)
    fp_scada  = fp.get("scada_alarm_health", 0.15)
    fp_pnr    = fp.get("pnr_health",         0.05)
    fp_itype  = fp.get("intervention_type",  "maintenance_scheduling")
    fp_hlabel = fp.get("horizon_label",      "Hours")

    # Derive rul_minutes from slider_health_score if provided
    if slider_health_score is not None:
        _hs = max(0.0, min(1.0, slider_health_score))
        _ttscada_h = max(0.0, (_hs - fp_scada) * fp_total)
        rul_minutes = _ttscada_h * 60.0
        is_pnr_exceeded = is_pnr_exceeded or (_hs <= fp_pnr)
    elif rul_minutes is None:
        rul_minutes = 60.0  # default
    else:
        _hs = None

    ctx = AGENT_CONTEXTS.get(fault_type, {})
    scenario         = ctx.get("scenario", "general")
    enterprise_source = ctx.get("enterprise_source", "ERP_SAP_MM")
    source_label     = ctx.get("source_label", enterprise_source)

    # ── Rule-based recommendation (always available, no GPU required) ─────────
    if scenario == "supply_chain":
        lead_std   = ctx.get("lead_times", {}).get("standard_freight_days", "unknown")
        lead_air   = ctx.get("lead_times", {}).get("air_freight_days", "unknown")
        air_prem   = ctx.get("lead_times", {}).get("air_freight_premium_usd", 0)
        local_stk  = ctx.get("inventory", {}).get("storage_location_local", 0)
        part_desc  = ctx.get("well_bom", {}).get("part_description", "Required Part")
        unit_cost  = ctx.get("well_bom", {}).get("unit_cost_usd", 0)
        daily_val  = ctx.get("daily_production_value_usd", 0)
        rul_days   = round(rul_minutes / 60 / 24, 1)
        if local_stk > 0:
            recommendation = (f"✅ {part_desc} is in local inventory ({local_stk} unit). "
                              f"Schedule replacement before predicted failure in {rul_days} days.")
        elif isinstance(lead_std, (int, float)) and lead_std <= rul_days:
            recommendation = (f"📦 {part_desc} requires ordering. Standard freight ({lead_std} days) "
                              f"arrives before predicted failure ({rul_days} days). "
                              f"Order now — unit cost ${unit_cost:,}. "
                              f"Failure without order = {round(rul_days * daily_val):,}/day deferred production.")
        else:
            recommendation = (f"🚨 {part_desc} standard lead time ({lead_std}d) exceeds predicted failure "
                              f"window ({rul_days}d). Air freight ({lead_air}d, +${air_prem:,}) required. "
                              f"Order immediately — daily production at risk: ${daily_val:,}/day.")
    elif scenario == "workforce_scheduling":
        dispatches = ctx.get("upcoming_dispatches", [])
        task       = ctx.get("appended_task", {})
        task_desc  = task.get("description", "Maintenance task")
        task_hrs   = task.get("estimated_duration_hours", 1)
        emg_cost   = task.get("emergency_dispatch_cost_usd", 2000)
        if dispatches:
            d        = dispatches[0]
            avail    = d.get("available_capacity_hours", 0)
            rec_str  = "✅" if avail >= task_hrs else "⚠️"
            recommendation = (f"{rec_str} Crew {d['crew_id']} ({d['headcount']} mechanics) is scheduled "
                              f"at this site {d['scheduled_date']} at {d['scheduled_time_local']} for "
                              f"'{d['primary_task']}' ({d['estimated_duration_hours']}h). "
                              f"Available capacity: {avail}h. "
                              f"Append '{task_desc}' ({task_hrs}h) to WO {d['work_order_id']} — "
                              f"zero additional travel cost vs ${emg_cost:,} emergency dispatch.")
        else:
            recommendation = (f"📞 No crew scheduled at this site. Initiate emergency dispatch for "
                              f"'{task_desc}'. Estimated cost: ${emg_cost:,}.")
    elif scenario == "operational_control":
        tr   = ctx.get("recommended_transition", {})
        conn = ctx.get("next_connection_min", "unknown")
        recommendation = (f"🔧 Controlled pump transition recommended. "
                          f"{tr.get('step_1', 'Bring standby pump online')}. "
                          f"{tr.get('result', 'Maintain ECD.')} "
                          f"Rebuild failing pump fluid end at next connection stop (~{conn} min).")
    elif scenario == "software_command":
        cmds = ctx.get("available_commands", [])
        if cmds:
            c = cmds[0]
            recommendation = (f"💻 SCADA command available: '{c['label']}'. "
                              f"Effect: {c.get('effect', 'Stabilize fault condition.')} "
                              f"Execution time: {c.get('time_min', 1)} minute(s). Cost: $0.")
        else:
            recommendation = "💻 SCADA control commands available. Execute VFD adjustment immediately."
    elif scenario == "emergency_stop":
        recommendation = ("🚨 EMERGENCY: Immediate pump shutdown required. "
                          "Evacuate pump room personnel before any inspection. "
                          "Inspect standpipe, manifold, and Kelly hose for pressure hammer damage.")
    elif scenario == "operational_monitor":
        hs  = ctx.get("hydraulic_system", {})
        hrs = hs.get("estimated_hours_to_low_alarm", "N/A")
        spares = ctx.get("spare_parts_on_rig", {})
        recommendation = (f"🔍 Hydraulic leak detected. Estimated {hrs}h until Low alarm at current rate. "
                          f"Spare hoses on rig: {spares.get('hydraulic_hose_3000psi', 0)}. "
                          f"Locate and repair during next stand break to prevent quill lock loss.")
    elif scenario == "emergency_dispatch":
        crew = ctx.get("emergency_crew", {})
        part = ctx.get("required_parts", {})
        recommendation = (f"📞 Emergency dispatch required. Crew ETA: {crew.get('est_arrival_hours', '?')}h. "
                          f"Part '{part.get('part_description', 'valve')}' — "
                          f"{'in local stock' if part.get('in_stock_local') else 'NOT in stock'}.")
    else:
        recommendation = (f"ℹ️ Context queried from {source_label}. "
                          f"Review enterprise data and select the appropriate resolution action below.")

    # ── Optional Gemma LLM enhancement ───────────────────────────────────────
    enhanced = False
    try:
        import requests as _req
        prompt = (
            f"You are an oil and gas operations AI assistant. "
            f"GDC edge AI detected '{fault_type.replace('_', ' ')}' on asset {asset_id}. "
            f"Predicted time to alarm: {rul_minutes:.0f} minutes. "
            f"Enterprise system ({source_label}) query result: "
            f"{json.dumps({k: v for k, v in ctx.items() if k not in ('pump_status',)}, default=str)[:600]}. "
            f"In 2-3 concise sentences, confirm: {recommendation}"
        )
        resp = _req.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                  "options": {"num_predict": 120, "temperature": 0.3}},
            timeout=8,
        )
        if resp.status_code == 200:
            gemma_text = resp.json().get("response", "").strip()
            if len(gemma_text) > 40:
                recommendation = gemma_text
                enhanced = True
    except Exception as e:
        log.debug(f"Gemma agent enhancement unavailable: {e}")

    return {
        "fault_type":         fault_type,
        "asset_id":           asset_id,
        "rul_minutes":        rul_minutes,
        "enterprise_source":  enterprise_source,
        "source_label":       source_label,
        "scenario":           scenario,
        "recommendation":     recommendation,
        "enhanced_by_llm":    enhanced,
        "context_summary":    {
            k: v for k, v in ctx.items()
            if k in ("inventory", "lead_times", "upcoming_dispatches",
                     "recommended_transition", "hydraulic_system", "available_commands",
                     "required_parts", "emergency_crew", "next_planned_trip_hours")
        },
    }


# ── Phase 6.2: SSE Streaming Agent Endpoint ───────────────────────────────────
@app.post("/api/agent/recommend-stream")
def get_agent_recommend_stream(
    fault_type: str,
    asset_id: str,
    slider_health_score: float = None,
    rul_minutes: float = None,
    is_pnr_exceeded: bool = False,
    chat_history: str = None,   # Phase 10: JSON string [{role, content}] for multi-turn chat
):
    """
    Phase 6.2 — SSE streaming version of /api/agent/recommend.

    SSE event format:
      data: {"type":"recommendation","text":"...","scenario":"...","source":"..."}  — immediate rule-based
      data: {"type":"token","text":"..."}   — streaming LLM tokens (if Ollama available)
      data: {"type":"done"}                 — stream complete

    The frontend (Phase 6.5) connects with EventSource, shows the rule-based
    recommendation immediately, then appends LLM tokens as they stream in.
    No full-response wait — first token appears within ~500ms.

    Prompt is tightened to <150 words to maximise speed on gemma3:12b.
    """
    # ── Compute rule-based recommendation synchronously (same logic as /api/agent/recommend)
    fp        = FAULT_PHYSICS.get(fault_type, {})
    fp_total  = fp.get("total_hours",        1.0)
    fp_scada  = fp.get("scada_alarm_health", 0.15)
    fp_pnr    = fp.get("pnr_health",         0.05)

    if slider_health_score is not None:
        _hs = max(0.0, min(1.0, slider_health_score))
        _ttscada_h = max(0.0, (_hs - fp_scada) * fp_total)
        rul_minutes = _ttscada_h * 60.0
        is_pnr_exceeded = is_pnr_exceeded or (_hs <= fp_pnr)
    elif rul_minutes is None:
        rul_minutes = 60.0

    ctx              = AGENT_CONTEXTS.get(fault_type, {})
    scenario         = ctx.get("scenario", "general")
    source_label     = ctx.get("source_label", ctx.get("enterprise_source", "ERP_SAP_MM"))

    # Rule-based recommendation (same logic as blocking endpoint, abbreviated)
    if scenario == "supply_chain":
        lead_std  = ctx.get("lead_times", {}).get("standard_freight_days", "?")
        local_stk = ctx.get("inventory", {}).get("storage_location_local", 0)
        part_desc = ctx.get("well_bom", {}).get("part_description", "Part")
        rul_days  = round(rul_minutes / 60 / 24, 1)
        if local_stk > 0:
            rule_rec = f"✅ {part_desc} in local stock. Schedule replacement before failure in {rul_days}d."
        elif isinstance(lead_std, (int, float)) and lead_std <= rul_days:
            rule_rec = f"📦 Order {part_desc} now — standard freight {lead_std}d arrives before failure ({rul_days}d)."
        else:
            air_d   = ctx.get("lead_times", {}).get("air_freight_days", "?")
            air_usd = ctx.get("lead_times", {}).get("air_freight_premium_usd", 0)
            rule_rec = f"🚨 Air freight required. Standard lead {lead_std}d > failure window {rul_days}d. Air: {air_d}d, +${air_usd:,}."
    elif scenario == "workforce_scheduling":
        dispatches = ctx.get("upcoming_dispatches", [])
        task       = ctx.get("appended_task", {})
        if dispatches:
            d = dispatches[0]
            rule_rec = f"✅ Append '{task.get('description','task')}' ({task.get('estimated_duration_hours',1)}h) to WO {d['work_order_id']} — zero travel vs ${task.get('emergency_dispatch_cost_usd',0):,} callout."
        else:
            rule_rec = f"📞 No crew on site. Emergency dispatch required. Cost: ${task.get('emergency_dispatch_cost_usd',0):,}."
    elif scenario in ("operational_control",):
        tr  = ctx.get("recommended_transition", {})
        rule_rec = f"🔧 {tr.get('step_1','Bring backup pump online')}. {tr.get('result','ECD maintained.')} Fix pump at next connection stop (~{ctx.get('next_connection_min','?')}min)."
    elif scenario == "software_command":
        cmds = ctx.get("available_commands", [])
        c    = cmds[0] if cmds else {}
        rule_rec = f"💻 Execute SCADA: '{c.get('label','VFD adjust')}'. Effect: {c.get('effect','Stabilise fault.')} Time: {c.get('time_min',1)}min. Cost: $0."
    elif scenario in ("emergency_stop", "emergency_dispatch"):
        rule_rec = "🚨 EMERGENCY: Immediate shutdown. Evacuate area. Assess for pipe damage."
    else:
        rule_rec = f"ℹ️ Context from {source_label}. Review enterprise data and select action."

    # ── Parse chat history for multi-turn context (Phase 10) ──────────────────
    _history = []
    if chat_history:
        try:
            _parsed = json.loads(chat_history)
            if isinstance(_parsed, list):
                _history = _parsed
        except Exception:
            pass

    # ── Tight LLM system prompt (<150 words) ──────────────────────────────────
    fault_label = fault_type.replace("_", " ")
    tier = "PAST PNR" if is_pnr_exceeded else ("CRITICAL" if rul_minutes < 15 else ("URGENT" if rul_minutes < 60 else "EARLY"))
    _history_txt = ""
    if _history:
        _hist_lines = "\n".join(f"{h['role'].upper()}: {h.get('content','')[:200]}" for h in _history[-4:])
        _history_txt = f"\nCONVERSATION:\n{_hist_lines}\n"
    llm_prompt = (
        f"You are GDC Ops Agent, an oil and gas predictive maintenance assistant. "
        f"Be concise — respond in exactly 2 sentences.\n\n"
        f"FAULT: {fault_label} on {asset_id}. Tier: {tier}. Time to SCADA alarm: {rul_minutes:.0f} minutes.\n"
        f"ENTERPRISE DATA ({source_label}): {rule_rec}"
        f"{_history_txt}\n"
        f"In 2 sentences: (1) confirm the immediate action, (2) state the specific next step. "
        f"No preamble. No repetition."
    )

    def _sse_generator():
        # Event 1: Rule-based recommendation (immediate, no LLM latency)
        yield f"data: {json.dumps({'type': 'recommendation', 'text': rule_rec, 'scenario': scenario, 'source': source_label, 'tier': tier, 'rul_minutes': round(rul_minutes, 1)})}\n\n"

        # Event 2+: Stream LLM tokens if Ollama available
        try:
            import requests as _req
            resp = _req.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": llm_prompt, "stream": True,
                      "options": {"num_predict": 100, "temperature": 0.2, "top_p": 0.9}},
                stream=True,
                timeout=25,
            )
            if resp.status_code == 200:
                for line in resp.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            log.debug(f"SSE agent stream error (non-fatal): {e}")

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        _sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":   "no-cache",
            "X-Accel-Buffering": "no",    # Disable nginx proxy buffering
            "Connection":      "keep-alive",
        },
    )


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


# ── Phase 6.4: Per-Asset Live Degrade Status ──────────────────────────────────
@app.get("/api/degrade-status/{asset_id}")
def get_degrade_status_for_asset(asset_id: str):
    """
    Phase 6.4: Per-asset live health status for the Intervention Slider polling loop.
    Returns current health_score converted to physical time units via FAULT_PHYSICS.
    The frontend polls this every 5s to animate the slider leftward as time ticks down.

    Returns:
        is_active        — whether a fault is currently being simulated
        health_score     — current smoothed EWA health (1.0=perfect → 0.0=destroyed)
        time_to_scada_minutes  — minutes until SCADA alarm threshold crossed
        time_to_pnr_minutes    — minutes until Point of No Return
        time_to_failure_minutes — total remaining minutes to health=0
        horizon_label    — "Minutes" | "Hours" | "Days" (physical unit label)
        scada_sensor / pnr_sensor / primary_sensor — for tab routing
    """
    import numpy as np
    dg         = active_degrades.get(asset_id, {})
    fault_type = dg.get("fault_type")
    is_active  = bool(dg)

    if not is_active or not fault_type:
        return {
            "asset_id": asset_id, "is_active": False,
            "fault_type": None, "health_score": 1.0,
            "time_to_scada_minutes": None, "time_to_pnr_minutes": None,
            "time_to_failure_minutes": None, "horizon_label": None,
            "scada_sensor": None, "pnr_sensor": None, "primary_sensor": None,
        }

    # Smoothed health score from EWA buffer (same formula as forecast endpoint)
    hist = list(HEALTH_HISTORY.get(asset_id, []))
    if hist:
        n       = len(hist)
        weights = np.array([0.75 ** (n - 1 - i) for i in range(n)])
        health_score = float(np.average(hist, weights=weights))
    else:
        health_score = 1.0  # no readings yet — assume nominal

    fp          = FAULT_PHYSICS.get(fault_type, {})
    fp_total_h  = fp.get("total_hours",        1.0)
    fp_scada_hs = fp.get("scada_alarm_health", 0.15)
    fp_pnr_hs   = fp.get("pnr_health",         0.05)
    fp_hlabel   = fp.get("horizon_label",       "Hours")

    # Time to SCADA alarm = (health − scada_threshold) × total_hours × 60
    ttscada_min = round(max(0.0, (health_score - fp_scada_hs) * fp_total_h) * 60.0, 1)
    # Time to PNR = (health − pnr_threshold) × total_hours × 60
    ttpnr_min   = round(max(0.0, (health_score - fp_pnr_hs)   * fp_total_h) * 60.0, 1)
    # Total time to failure = health × total_hours × 60 (health → 0 at full failure)
    ttf_min     = round(health_score * fp_total_h * 60.0, 1)

    return {
        "asset_id": asset_id, "is_active": True,
        "fault_type": fault_type,
        "health_score": round(health_score, 4),
        "time_to_scada_minutes": ttscada_min,
        "time_to_pnr_minutes":   ttpnr_min,
        "time_to_failure_minutes": ttf_min,
        "horizon_label": fp_hlabel,
        "scada_sensor":   fp.get("scada_sensor"),
        "pnr_sensor":     fp.get("pnr_sensor"),
        "primary_sensor": fp.get("primary_sensor"),
    }


# ── Phase 6.3: JSON Forecast Data Endpoint ────────────────────────────────────
@app.get("/api/plot/forecast-data/{asset_id}")
def get_forecast_data(asset_id: str):
    """
    Phase 6.3: Returns JSON Plotly traces for ALL sensor tabs in a single call.
    Runs ML inference once, computes per-sensor projections, and returns structured
    Plotly data that the frontend consumes via Plotly.react() for instant tab switching.

    Response shape:
      {
        "asset_id": ..., "fault_type": ..., "health_score": ...,
        "time_to_scada_minutes": ..., "time_to_pnr_minutes": ...,
        "scada_sensor": ..., "pnr_sensor": ..., "primary_sensor": ...,
        "sensors": {
          "psi":  { "traces": [...], "layout": {...}, "is_scada": bool, "is_pnr": bool },
          "temp": { ... }, "vib": { ... }, "amps": { ... }   # amps/spm for ESP/mud_pump only
        }
      }
    """
    from datetime import timedelta
    import numpy as np

    if asset_id not in ASSET_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Unknown asset: {asset_id}")

    asset_meta  = ASSET_REGISTRY[asset_id]
    asset_class = asset_meta["asset_class"]
    _s4c        = SENSOR4_CONFIG.get(asset_class)

    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT event_time, psi, temp_f, vibration, motor_amps, spm,
                       failure_type, predicted_label
                FROM telemetry_events
                WHERE asset_id = %s AND event_time > NOW() - INTERVAL '10 minutes'
                ORDER BY event_time ASC
                """,
                (asset_id,),
            )
            rows = cur.fetchall()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    if not rows:
        return {"asset_id": asset_id, "is_active": False, "sensors": {}, "no_data": True}

    times  = [r["event_time"].replace(tzinfo=None) if getattr(r["event_time"], "tzinfo", None)
              else r["event_time"] for r in rows]
    psi_v  = np.array([float(r["psi"])       for r in rows])
    temp_v = np.array([float(r["temp_f"])    for r in rows])
    vib_v  = np.array([float(r["vibration"]) for r in rows])
    now    = times[-1]

    # Detect active fault / FAULT_PHYSICS
    _deg_state    = active_degrades.get(asset_id, {})
    is_degrading  = _deg_state.get("running", False) or _deg_state.get("held", False)
    recent_labels = [str(r.get("predicted_label") or "normal").lower() for r in rows[-10:]]
    fault_fraction = sum(1 for l in recent_labels if l not in ("normal", "")) / max(len(recent_labels), 1)
    classifier_active = (fault_fraction > 0.20) or is_degrading

    _fp_fault_type = (
        _deg_state.get("fault_type") or
        next(((r.get("failure_type") or "").lower() for r in rows
              if (r.get("failure_type") or "").lower() not in ("normal", "")), None)
    )
    _fp = FAULT_PHYSICS.get(_fp_fault_type, {}) if _fp_fault_type else {}

    # Run ML inference once to get health score
    health_score    = None
    rul_minutes     = None
    pnr_minutes_rem = None
    ttf_minutes     = None

    if len(rows) >= 8 and classifier_active:
        try:
            fault_mask = np.array([(r.get("failure_type") or "").lower() not in ("normal", "") for r in rows])
            fault_idx  = np.where(fault_mask)[0]
            psi_w  = psi_v[fault_idx] if len(fault_idx) >= 6 else psi_v[-min(60,len(psi_v)):]
            temp_w = temp_v[fault_idx] if len(fault_idx) >= 6 else temp_v[-min(60,len(temp_v)):]
            vib_w  = vib_v[fault_idx] if len(fault_idx) >= 6 else vib_v[-min(60,len(vib_v)):]
            t_w = np.arange(len(psi_w), dtype=np.float64)
            n_w = len(t_w)
            RPM = 12.0
            last_psi  = float(np.median(psi_w[-min(8,n_w):]))
            last_temp = float(np.median(temp_w[-min(8,n_w):]))
            last_vib  = float(np.median(vib_w[-min(8,n_w):]))
            dpsi_dt   = float(np.polyfit(t_w, psi_w,  1)[0]) * RPM if n_w >= 6 else 0.0
            dtemp_dt  = float(np.polyfit(t_w, temp_w, 1)[0]) * RPM if n_w >= 6 else 0.0
            dvib_dt   = float(np.polyfit(t_w, vib_w,  1)[0]) * RPM if n_w >= 6 else 0.0
            last_s4 = ds4_dt = 0.0
            if _s4c and asset_class in ("esp", "mud_pump"):
                s4_all = np.array([float(r.get(_s4c["key"]) or _s4c["nominal"]) for r in rows])
                s4_w   = s4_all[fault_idx] if len(fault_idx) >= 6 else s4_all[-min(60,len(s4_all)):]
                last_s4 = float(np.median(s4_w[-min(8,len(s4_w)):]))
                ds4_dt  = float(np.polyfit(np.arange(len(s4_w),dtype=float),s4_w,1)[0])*RPM if len(s4_w)>=6 else 0.0
            health_model = HEALTH_MODELS.get(asset_class)
            if health_model:
                import xgboost as xgb
                if asset_class == "esp":
                    frow = np.array([[last_psi,last_temp,last_vib,last_s4,dpsi_dt,dtemp_dt,dvib_dt,ds4_dt]])
                    fn   = ["psi","temp_f","vibration","motor_amps","dpsi_dt","dtemp_dt","dvib_dt","damps_dt"]
                elif asset_class == "mud_pump":
                    frow = np.array([[last_psi,last_temp,last_vib,last_s4,dpsi_dt,dtemp_dt,dvib_dt,ds4_dt]])
                    fn   = ["psi","temp_f","vibration","spm","dpsi_dt","dtemp_dt","dvib_dt","dspm_dt"]
                else:
                    frow = np.array([[last_psi,last_temp,last_vib,dpsi_dt,dtemp_dt,dvib_dt]])
                    fn   = ["psi","temp_f","vibration","dpsi_dt","dtemp_dt","dvib_dt"]
                _hs_raw = max(0.0,min(1.0,float(health_model.predict(xgb.DMatrix(frow,feature_names=fn))[0])))
                if asset_id not in HEALTH_HISTORY:
                    HEALTH_HISTORY[asset_id] = deque(maxlen=10)
                HEALTH_HISTORY[asset_id].append(_hs_raw)
                hist    = list(HEALTH_HISTORY[asset_id])
                n_hist  = len(hist)
                weights = np.array([0.75 ** (n_hist-1-i) for i in range(n_hist)])
                health_score = float(np.average(hist, weights=weights))
                fp_total_h   = _fp.get("total_hours", 1.0)
                fp_scada_hs  = _fp.get("scada_alarm_health", 0.15)
                fp_pnr_hs    = _fp.get("pnr_health", 0.05)
                rul_minutes     = round(max(0.0,(health_score-fp_scada_hs)*fp_total_h)*60.0, 1)
                pnr_minutes_rem = round(max(0.0,(health_score-fp_pnr_hs)*fp_total_h)*60.0, 1)
                ttf_minutes     = round(health_score*fp_total_h*60.0, 1)
        except Exception as e:
            log.warning(f"forecast-data ML inference error for {asset_id}: {e}")

    # Build per-sensor trace data
    fp_scada_sensor = _fp.get("scada_sensor")
    fp_pnr_sensor   = _fp.get("pnr_sensor")
    fp_primary      = _fp.get("primary_sensor")
    fp_total_h      = _fp.get("total_hours", 1.0)
    fp_hlabel       = _fp.get("horizon_label", "Hours")

    ttf_time  = (now + timedelta(minutes=rul_minutes)) if rul_minutes is not None else None
    pnr_t     = (now + timedelta(minutes=pnr_minutes_rem)) if pnr_minutes_rem is not None else None

    horizon_min  = max(42, int((rul_minutes or 0) + 10)) if rul_minutes else 42
    future_times = [now + timedelta(minutes=i) for i in range(1, horizon_min + 1)]
    t_arr        = np.array(range(1, len(future_times) + 1), dtype=float)

    def _build_sensor(metric, y_vals, y_crit, crit_dir, y_label):
        """Build Plotly trace list and layout dict for one sensor tab."""
        y_start  = float(np.median(y_vals[-5:])) if len(y_vals) >= 5 else float(y_vals[-1])
        show_scada = (not fp_scada_sensor) or (metric == fp_scada_sensor)
        show_pnr   = (not fp_pnr_sensor)   or (metric == fp_pnr_sensor)

        traces = [
            {"type": "scatter", "x": [t.isoformat() for t in times], "y": y_vals.tolist(),
             "mode": "lines", "name": "Live Telemetry",
             "line": {"color": "#1e90ff", "width": 2.5}},
        ]
        if rul_minutes is not None and rul_minutes < 580:
            ttf_total_min = fp_total_h * 60.0 if _fp else max(rul_minutes*3.0, 60.0)
            y_failure = max(y_crit*0.45, 1.0) if crit_dir == "below" else y_crit*1.80
            # Phase 10 Bug 4 fix: two-segment exponential — SCADA marker aligns exactly
            _k2 = 3.5; _expk2 = np.exp(_k2) - 1.0; _rm2 = max(float(rul_minutes), 0.01)
            _s1 = t_arr <= _rm2; _s2 = ~_s1
            _py = np.empty(len(t_arr))
            _py[_s1] = y_start + (y_crit - y_start) * (np.exp(_k2 * t_arr[_s1] / _rm2) - 1.0) / _expk2
            _py[_s2] = y_crit  + (y_failure - y_crit) * (np.exp(_k2 * (t_arr[_s2] - _rm2) / max(ttf_total_min - _rm2, 1.0)) - 1.0) / _expk2
            proj_y  = _py.tolist()
        else:
            proj_y = [y_start] * len(future_times)

        traces.append({"type": "scatter", "x": [t.isoformat() for t in future_times],
                       "y": proj_y, "mode": "lines", "name": "ML RUL Projection",
                       "line": {"color": "#ff8c00" if rul_minutes else "#00e676", "width": 2.5, "dash": "dot"}})

        # Confidence cone: widens 4% → 18% of projected range (matches Phase 5 Plotly iframe cone)
        _proj_arr   = np.array(proj_y)
        _proj_range = abs(_proj_arr[-1] - y_start) if rul_minutes is not None else abs(y_crit - y_start) * 0.1
        _cone_frac  = np.linspace(0.04, 0.18, len(future_times))
        noise       = _cone_frac * max(_proj_range, abs(y_start) * 0.05)
        upper_y     = (_proj_arr + noise).tolist()
        lower_y     = (_proj_arr - noise).tolist()
        cone_rgba   = "255,140,0" if rul_minutes else "0,230,118"
        x_fwd       = [t.isoformat() for t in future_times]
        traces.append({"type": "scatter",
                       "x": x_fwd + x_fwd[::-1],
                       "y": upper_y + lower_y[::-1],
                       "fill": "toself",
                       "fillcolor": f"rgba({cone_rgba}, 0.08)",
                       "line": {"color": "rgba(255,255,255,0)"},
                       "name": "Confidence Band",
                       "hoverinfo": "skip"})

        if show_scada:
            traces.append({"type": "scatter",
                           "x": [times[0].isoformat(), future_times[-1].isoformat()],
                           "y": [y_crit, y_crit], "mode": "lines",
                           "name": "SCADA Alarm Threshold",
                           "line": {"color": "#f44336", "width": 1.5, "dash": "dash"},
                           "hoverinfo": "skip"})

        shapes = [{"type":"line","x0":now.isoformat(),"x1":now.isoformat(),"y0":0,"y1":1,
                   "xref":"x","yref":"paper","line":{"color":"#5a6a7a","width":1.5,"dash":"dot"}}]
        annotations = [{"x":now.isoformat(),"y":1.0,"xref":"x","yref":"paper","text":"NOW",
                        "showarrow":False,"xanchor":"right","xshift":-5,"yanchor":"bottom",
                        "font":{"color":"#5a6a7a","size":10,"family":"JetBrains Mono"}}]

        if ttf_time and show_scada and rul_minutes:
            lbl = f"{int(rul_minutes)}m" if rul_minutes<60 else f"{int(rul_minutes//60)}h {int(rul_minutes%60)}m"
            shapes.append({"type":"line","x0":ttf_time.isoformat(),"x1":ttf_time.isoformat(),
                           "y0":0,"y1":1,"xref":"x","yref":"paper",
                           "line":{"color":"rgba(255,23,68,0.95)","width":3,"dash":"solid"}})
            annotations.append({"x":ttf_time.isoformat(),"y":0.97,"xref":"x","yref":"paper",
                                 "text":f"<b>⚡ SCADA Alarm in {lbl}</b>","showarrow":False,
                                 "xanchor":"center","font":{"color":"#ff1744","size":11,"family":"JetBrains Mono"},
                                 "bgcolor":"rgba(255,23,68,0.15)","bordercolor":"rgba(255,23,68,0.5)","borderpad":4})
        if pnr_t and show_pnr and classifier_active:
            shapes.append({"type":"line","x0":pnr_t.isoformat(),"x1":pnr_t.isoformat(),
                           "y0":0,"y1":1,"xref":"x","yref":"paper",
                           "line":{"color":"rgba(255,109,0,0.95)","width":3,"dash":"solid"}})
            annotations.append({"x":pnr_t.isoformat(),"y":0.81,"xref":"x","yref":"paper",
                                 "text":f"<b>⛔ PNR</b>","showarrow":False,"xanchor":"center",
                                 "font":{"color":"#ff6d00","size":11,"family":"JetBrains Mono"},
                                 "bgcolor":"rgba(255,109,0,0.15)","bordercolor":"rgba(255,109,0,0.5)","borderpad":4})

        layout = {"paper_bgcolor":"#0b0c10","plot_bgcolor":"#0f1318",
                  "font":{"color":"#e0e0e0","family":"Inter, sans-serif","size":11},
                  "margin":{"l":55,"r":20,"t":50,"b":40},
                  "xaxis":{"title":"Time (UTC)","gridcolor":"#1e2a38","zeroline":False},
                  "yaxis":{"title":y_label,"gridcolor":"#1e2a38","zeroline":False},
                  "shapes": shapes, "annotations": annotations,
                  "showlegend": True,
                  "legend":{"orientation":"h","yanchor":"bottom","y":1.02,"xanchor":"right","x":1}}
        return {"traces": traces, "layout": layout,
                "is_scada": show_scada, "is_pnr": show_pnr,
                "is_primary": metric == fp_primary}

    sensors = {
        "psi":  _build_sensor("psi",  psi_v,  asset_meta["crit_psi"],  asset_meta["psi_crit_dir"],
                               asset_meta.get("psi_label",  "Pressure (PSI)")),
        "temp": _build_sensor("temp", temp_v, asset_meta["crit_temp"], asset_meta["temp_crit_dir"],
                               asset_meta.get("temp_label", "Temperature (°F)")),
        "vib":  _build_sensor("vib",  vib_v,  asset_meta["crit_vib"],  asset_meta["vib_crit_dir"],
                               asset_meta.get("vib_label",  "Vibration (mm/s)")),
    }
    if _s4c:
        s4_v = np.array([float(r.get(_s4c["key"]) or _s4c["nominal"]) for r in rows])
        s4_metric = "amps" if asset_class == "esp" else "spm"
        sensors[s4_metric] = _build_sensor(s4_metric, s4_v, _s4c["crit"], _s4c["crit_dir"], _s4c["label"])

    return {
        "asset_id": asset_id, "is_active": classifier_active,
        "fault_type": _fp_fault_type, "health_score": round(health_score, 4) if health_score else None,
        "time_to_scada_minutes": rul_minutes, "time_to_pnr_minutes": pnr_minutes_rem,
        "time_to_failure_minutes": ttf_minutes, "horizon_label": fp_hlabel,
        "scada_sensor": fp_scada_sensor, "pnr_sensor": fp_pnr_sensor, "primary_sensor": fp_primary,
        "sensors": sensors,
    }


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
