"""
gke/telemetry-simulator/simulator.py

Continuously generates realistic telemetry for all 20 Upstream O&G assets
across 4 sites and publishes readings to RabbitMQ.

Asset classes and their sensor meanings:
  esp        — Electrical Submersible Pump (Downhole)
               psi = Intake Pressure (1200–1600 PSI)
               temp_f = Motor Winding Temp (180–220°F)
               vibration = Motor Vibration (0.8–2.0 mm/s)
  gas_lift   — Gas Lift Compressor (Surface)
               psi = Discharge Pressure (940–1060 PSI)
               temp_f = Discharge Temp (140–178°F)
               vibration = Frame Vibration (1.0–2.5 mm/s)
  mud_pump   — Triplex Mud Pump (Drilling Rig)
               psi = Discharge Pressure (2550–3150 PSI)
               temp_f = Fluid End Temp (90–120°F)
               vibration = Module Vibration (2.5–4.5 mm/s)
  top_drive  — Top Drive (Drilling Rig Rotary System)
               psi = Hydraulic System Pressure (2840–3160 PSI)
               temp_f = Gearbox Oil Temp (130–165°F)
               vibration = Gearbox Vibration (1.8–3.8 mm/s)

Fleet: 4 sites × 4–6 assets each = 20 monitored assets (pure-pad architecture)
  Pad Alpha   — 6 ESPs (pure ESP production pad)
  Pad Bravo   — 4 Gas Lift Compressors (pure gas lift production pad)
  Pad Charlie — 6 ESPs (pure ESP production pad)
  Rig 42      — 3 Mud Pumps + 1 Top Drive (drilling rig)

Environment Variables:
  RABBITMQ_HOST       — RabbitMQ host
  RABBITMQ_PORT       — AMQP port (default: 5672)
  RABBITMQ_USER       — Username
  RABBITMQ_PASS       — Password
  RABBITMQ_VHOST      — Virtual host (default: gdc-pm)
  TELEMETRY_INTERVAL  — Seconds between normal readings (default: 5)
"""

import os
import json
import logging
import random
import time
from datetime import datetime

import pika

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("telemetry-simulator")

# ── Configuration ─────────────────────────────────────────────────────────────
RABBITMQ_HOST      = os.environ.get("RABBITMQ_HOST", "gdc-pm-rabbitmq.gdc-pm.svc.cluster.local")
RABBITMQ_PORT      = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER      = os.environ.get("RABBITMQ_USER", "gdc_user")
RABBITMQ_PASS      = os.environ.get("RABBITMQ_PASS", "")
RABBITMQ_VHOST     = os.environ.get("RABBITMQ_VHOST", "gdc-pm")
TELEMETRY_INTERVAL = float(os.environ.get("TELEMETRY_INTERVAL", "5"))

EXCHANGE_NAME = "telemetry"
ROUTING_KEY   = "sensor.reading"

# ── Asset Fleet (4 sites, 20 assets) ─────────────────────────────────────────
# Pure-pad architecture: each pad uses a single artificial lift method.
# Each entry: (asset_id, asset_class, site)
ASSET_REGISTRY = [
    # ── Pad Alpha — Pure ESP Production Pad (6 ESPs) ──────────────────────────
    ("ESP-ALPHA-1",    "esp",      "pad_alpha"),
    ("ESP-ALPHA-2",    "esp",      "pad_alpha"),
    ("ESP-ALPHA-3",    "esp",      "pad_alpha"),
    ("ESP-ALPHA-4",    "esp",      "pad_alpha"),
    ("ESP-ALPHA-5",    "esp",      "pad_alpha"),
    ("ESP-ALPHA-6",    "esp",      "pad_alpha"),
    # ── Pad Bravo — Pure Gas Lift Production Pad (4 Gas Lifts) ────────────────
    ("GLIFT-BRAVO-1",  "gas_lift", "pad_bravo"),
    ("GLIFT-BRAVO-2",  "gas_lift", "pad_bravo"),
    ("GLIFT-BRAVO-3",  "gas_lift", "pad_bravo"),
    ("GLIFT-BRAVO-4",  "gas_lift", "pad_bravo"),
    # ── Pad Charlie — Pure ESP Production Pad (6 ESPs) ────────────────────────
    ("ESP-CHARLIE-1",  "esp",      "pad_charlie"),
    ("ESP-CHARLIE-2",  "esp",      "pad_charlie"),
    ("ESP-CHARLIE-3",  "esp",      "pad_charlie"),
    ("ESP-CHARLIE-4",  "esp",      "pad_charlie"),
    ("ESP-CHARLIE-5",  "esp",      "pad_charlie"),
    ("ESP-CHARLIE-6",  "esp",      "pad_charlie"),
    # ── Rig 42 — Drilling Rig ─────────────────────────────────────────────────
    ("MUD-RIG42-1",    "mud_pump", "rig_42"),
    ("MUD-RIG42-2",    "mud_pump", "rig_42"),
    ("MUD-RIG42-3",    "mud_pump", "rig_42"),
    ("TOPDRIVE-RIG42-1","top_drive","rig_42"),
]

ASSETS        = [a[0] for a in ASSET_REGISTRY]
ASSET_CLASSES = {a[0]: a[1] for a in ASSET_REGISTRY}
ASSET_SITES   = {a[0]: a[2] for a in ASSET_REGISTRY}


# ── Normal Telemetry Generators ───────────────────────────────────────────────
def normal_reading(asset_id: str, asset_class: str) -> dict:
    """Generate a physically realistic nominal reading for the given asset class."""
    if asset_class == "esp":
        # Electrical Submersible Pump — downhole
        psi       = round(random.gauss(1400, 65), 1)
        temp_f    = round(random.gauss(198, 8), 1)
        vibration = round(max(0.1, random.gauss(1.4, 0.18)), 3)

    elif asset_class == "gas_lift":
        # Gas Lift Compressor — surface injection
        psi       = round(random.gauss(1000, 22), 1)
        temp_f    = round(random.gauss(158, 6), 1)
        vibration = round(max(0.1, random.gauss(1.7, 0.18)), 3)

    elif asset_class == "mud_pump":
        # Triplex Mud Pump — drilling rig
        psi       = round(random.gauss(2850, 85), 1)
        temp_f    = round(random.gauss(105, 5), 1)
        vibration = round(max(0.2, random.gauss(3.5, 0.35)), 3)

    elif asset_class == "top_drive":
        # Top Drive — drilling rig rotary system
        psi       = round(random.gauss(3000, 55), 1)
        temp_f    = round(random.gauss(148, 5), 1)
        vibration = round(max(0.1, random.gauss(2.8, 0.28)), 3)

    else:
        # Fallback
        psi       = round(random.gauss(1000, 50), 1)
        temp_f    = round(random.gauss(150, 10), 1)
        vibration = round(abs(random.gauss(2.0, 0.3)), 3)

    return {
        "asset_id"    : asset_id,
        "asset_type"  : asset_class,
        "psi"         : psi,
        "temp_f"      : temp_f,
        "vibration"   : vibration,
        "failure_type": "normal",
        "source"      : "simulator",
        "timestamp"   : datetime.utcnow().isoformat() + "Z",
    }


# ── ESP Fault Generators ──────────────────────────────────────────────────────
def gas_lock_reading(asset_id: str) -> dict:
    """Gas Lock: gas pockets overwhelm pump stages. PSI crashes, vibration spikes."""
    return {
        "asset_id": asset_id, "asset_type": "esp",
        "psi":       round(random.gauss(550, 75), 1),
        "temp_f":    round(random.gauss(222, 12), 1),
        "vibration": round(max(0.5, random.gauss(9.0, 1.4)), 3),
        "failure_type": "gas_lock", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def sand_ingress_reading(asset_id: str) -> dict:
    """Sand Ingress: formation sand erodes impeller. Vibration climbs steadily."""
    return {
        "asset_id": asset_id, "asset_type": "esp",
        "psi":       round(random.gauss(1360, 60), 1),
        "temp_f":    round(random.gauss(210, 10), 1),
        "vibration": round(max(0.5, random.gauss(6.5, 1.0)), 3),
        "failure_type": "sand_ingress", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def motor_overheat_reading(asset_id: str) -> dict:
    """Motor Overheat: downhole cooling degraded. Temperature climbs."""
    return {
        "asset_id": asset_id, "asset_type": "esp",
        "psi":       round(random.gauss(1380, 60), 1),
        "temp_f":    round(random.gauss(278, 8), 1),
        "vibration": round(max(0.5, random.gauss(3.0, 0.4)), 3),
        "failure_type": "motor_overheat", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ── Gas Lift Fault Generators ─────────────────────────────────────────────────
def valve_failure_reading(asset_id: str) -> dict:
    """Valve Failure: check valve breaks. Discharge pressure crashes, vibration spikes."""
    return {
        "asset_id": asset_id, "asset_type": "gas_lift",
        "psi":       round(random.gauss(530, 55), 1),
        "temp_f":    round(random.gauss(178, 10), 1),
        "vibration": round(max(0.5, random.gauss(11.0, 1.5)), 3),
        "failure_type": "valve_failure", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def thermal_runaway_reading(asset_id: str) -> dict:
    """Thermal Runaway: cooling degradation. Temperature climbs, pressure normal."""
    return {
        "asset_id": asset_id, "asset_type": "gas_lift",
        "psi":       round(random.gauss(990, 22), 1),
        "temp_f":    round(random.gauss(228, 8), 1),
        "vibration": round(max(0.5, random.gauss(3.5, 0.5)), 3),
        "failure_type": "thermal_runaway", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def bearing_wear_reading(asset_id: str) -> dict:
    """Bearing Wear: progressive bearing degradation. Frame vibration climbs."""
    return {
        "asset_id": asset_id, "asset_type": "gas_lift",
        "psi":       round(random.gauss(985, 22), 1),
        "temp_f":    round(random.gauss(172, 6), 1),
        "vibration": round(max(0.5, random.gauss(10.0, 1.5)), 3),
        "failure_type": "bearing_wear", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ── Mud Pump Fault Generators ─────────────────────────────────────────────────
def pulsation_dampener_failure_reading(asset_id: str) -> dict:
    """Pulsation Dampener Failure: bladder rupture. Sudden extreme pressure spike + vibration."""
    return {
        "asset_id": asset_id, "asset_type": "mud_pump",
        "psi":       round(random.gauss(4200, 190), 1),
        "temp_f":    round(random.gauss(138, 12), 1),
        "vibration": round(max(1.0, random.gauss(22.0, 3.0)), 3),
        "failure_type": "pulsation_dampener_failure", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def valve_washout_reading(asset_id: str) -> dict:
    """Valve Seat Washout: fluid erodes valve seat. Discharge pressure slowly declines."""
    return {
        "asset_id": asset_id, "asset_type": "mud_pump",
        "psi":       round(random.gauss(2050, 85), 1),
        "temp_f":    round(random.gauss(128, 10), 1),
        "vibration": round(max(0.5, random.gauss(7.5, 1.0)), 3),
        "failure_type": "valve_washout", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def piston_seal_wear_reading(asset_id: str) -> dict:
    """Piston Seal Wear: seals degrade. Fluid temp rises, pressure slowly drops."""
    return {
        "asset_id": asset_id, "asset_type": "mud_pump",
        "psi":       round(random.gauss(2150, 85), 1),
        "temp_f":    round(random.gauss(168, 12), 1),
        "vibration": round(max(0.5, random.gauss(6.5, 0.9)), 3),
        "failure_type": "piston_seal_wear", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ── Top Drive Fault Generators ────────────────────────────────────────────────
def gearbox_bearing_spalling_reading(asset_id: str) -> dict:
    """Gearbox Bearing Spalling: metal fatigue in gearbox. Vibration signature climbs."""
    return {
        "asset_id": asset_id, "asset_type": "top_drive",
        "psi":       round(random.gauss(2950, 55), 1),
        "temp_f":    round(random.gauss(198, 12), 1),
        "vibration": round(max(0.5, random.gauss(15.5, 2.0)), 3),
        "failure_type": "gearbox_bearing_spalling", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def hydraulic_leak_reading(asset_id: str) -> dict:
    """Hydraulic Leak: fluid loss reduces system pressure over time."""
    return {
        "asset_id": asset_id, "asset_type": "top_drive",
        "psi":       round(random.gauss(1900, 85), 1),
        "temp_f":    round(random.gauss(182, 12), 1),
        "vibration": round(max(0.5, random.gauss(5.0, 0.7)), 3),
        "failure_type": "hydraulic_leak", "source": "simulator",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ── Fault Dispatch Table ──────────────────────────────────────────────────────
FAULT_GENERATORS = {
    # ESP
    "gas_lock":                       gas_lock_reading,
    "sand_ingress":                   sand_ingress_reading,
    "motor_overheat":                 motor_overheat_reading,
    # Gas Lift
    "valve_failure":                  valve_failure_reading,
    "thermal_runaway":                thermal_runaway_reading,
    "bearing_wear":                   bearing_wear_reading,
    # Mud Pump
    "pulsation_dampener_failure":     pulsation_dampener_failure_reading,
    "valve_washout":                  valve_washout_reading,
    "piston_seal_wear":               piston_seal_wear_reading,
    # Top Drive
    "gearbox_bearing_spalling":       gearbox_bearing_spalling_reading,
    "hydraulic_leak":                 hydraulic_leak_reading,
}


# ── RabbitMQ Publishing ───────────────────────────────────────────────────────
def get_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=60,
        socket_timeout=10,
    )
    return pika.BlockingConnection(params)


def publish(channel, reading: dict) -> None:
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
        body=json.dumps(reading),
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,
        ),
    )


# ── Main Loop ─────────────────────────────────────────────────────────────────
def run() -> None:
    log.info(f"Telemetry Simulator starting. Fleet: {len(ASSET_REGISTRY)} assets (pure-pad)")
    log.info(f"  Sites: Pad Alpha (6 ESPs), Pad Bravo (4 Gas Lifts), Pad Charlie (6 ESPs), Rig 42 (4)")
    log.info(f"  Publishing to {RABBITMQ_HOST} every {TELEMETRY_INTERVAL}s per asset")

    conn    = None
    channel = None

    while True:
        try:
            if conn is None or conn.is_closed:
                log.info("Connecting to RabbitMQ...")
                conn    = get_connection()
                channel = conn.channel()
                channel.exchange_declare(
                    exchange=EXCHANGE_NAME,
                    exchange_type="topic",
                    durable=True,
                )
                log.info("RabbitMQ connected ✅")

            for asset_id, asset_class, site in ASSET_REGISTRY:
                reading = normal_reading(asset_id, asset_class)
                publish(channel, reading)
                log.debug(f"  {asset_id} ({asset_class}) | "
                          f"psi={reading['psi']} temp={reading['temp_f']} vib={reading['vibration']}")

            time.sleep(TELEMETRY_INTERVAL)

        except pika.exceptions.AMQPConnectionError as e:
            log.warning(f"RabbitMQ connection error: {e}. Reconnecting in 10s...")
            conn = None
            time.sleep(10)
        except Exception as e:
            log.error(f"Unexpected error: {e}", exc_info=True)
            time.sleep(5)


if __name__ == "__main__":
    run()
