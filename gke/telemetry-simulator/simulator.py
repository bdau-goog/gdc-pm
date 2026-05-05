"""
gke/telemetry-simulator/simulator.py

Continuously generates realistic telemetry for all registered asset types and
publishes it to a RabbitMQ exchange. Supports three asset classes:

  compressor  — Gas compressors (PSI/Temp/Vib)
                Failure modes: prd_failure, thermal_runaway, bearing_wear
  turbine     — Gas turbine generators (PSI/Temp/Vib — high range)
                Failure modes: combustion_instability, blade_fouling, rotor_imbalance
  transformer — HV transformers (kV stored as PSI/Temp/Vib)
                Failure modes: winding_overheat, dielectric_breakdown, core_loosening

Environment Variables:
  RABBITMQ_HOST       — RabbitMQ host
  RABBITMQ_PORT       — AMQP port (default: 5672)
  RABBITMQ_USER       — Username
  RABBITMQ_PASS       — Password
  RABBITMQ_VHOST      — Virtual host (default: gdc-pm)
  TELEMETRY_INTERVAL  — Seconds between normal readings (default: 5)
  INJECT_FAULT        — Fault type to inject: prd_failure, combustion_instability,
                        winding_overheat, etc. or 'none'
  INJECT_ASSET        — Asset ID to target for fault injection
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

# ── Asset Registry ────────────────────────────────────────────────────────────
# Each entry: (asset_id, asset_type)
# asset_type drives both the telemetry generator and the inference API model routing.
ASSET_REGISTRY = [
    # Compressors (stator_classifier)
    ("COMP-TX-VALLEY-01", "compressor"),
    ("COMP-TX-VALLEY-02", "compressor"),
    ("COMP-TX-RIDGE-01",  "compressor"),
    ("COMP-TX-RIDGE-02",  "compressor"),
    ("COMP-TX-BASIN-01",  "compressor"),
    # Gas Turbine Generators (turbine_classifier)
    ("GTG-VALLEY-01",     "turbine"),
    ("GTG-RIDGE-01",      "turbine"),
    # HV Transformers (transformer_classifier) — psi column stores kV
    ("XFR-VALLEY-01",     "transformer"),
    ("XFR-RIDGE-01",      "transformer"),
    ("XFR-BASIN-01",      "transformer"),
]

# Flat list of asset IDs (for env var matching)
ASSETS = [a[0] for a in ASSET_REGISTRY]
# Dict: asset_id → asset_type
ASSET_TYPES = {a[0]: a[1] for a in ASSET_REGISTRY}


# ── Normal Telemetry Generators ───────────────────────────────────────────────
def normal_reading(asset_id: str, asset_type: str) -> dict:
    """Generate a nominal reading for the given asset type."""
    if asset_type == "turbine":
        psi       = round(random.gauss(2200, 25), 2)
        temp_f    = round(random.gauss(1050, 12), 2)
        vibration = round(abs(random.gauss(0.05, 0.008)), 4)
    elif asset_type == "transformer":
        psi       = round(random.gauss(115, 1.2), 3)   # kV stored in psi column
        temp_f    = round(random.gauss(185, 4), 2)
        vibration = round(abs(random.gauss(0.010, 0.002)), 4)
    else:  # compressor (default)
        psi       = round(random.gauss(855, 8), 2)
        temp_f    = round(random.gauss(112, 3), 2)
        vibration = round(abs(random.gauss(0.02, 0.005)), 4)

    return {
        "asset_id"    : asset_id,
        "asset_type"  : asset_type,
        "psi"         : psi,
        "temp_f"      : temp_f,
        "vibration"   : vibration,
        "failure_type": "normal",
        "source"      : "simulator",
    }


# ── Compressor Failure Generators ─────────────────────────────────────────────
def prd_failure_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "compressor",
        "psi":       round(random.gauss(645, 20), 2),
        "temp_f":    round(random.gauss(162, 6), 2),
        "vibration": round(abs(random.gauss(0.90, 0.12)), 4),
        "failure_type": "prd_failure", "source": "simulator",
    }


def thermal_runaway_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "compressor",
        "psi":       round(random.gauss(845, 12), 2),
        "temp_f":    round(random.gauss(188, 10), 2),
        "vibration": round(abs(random.gauss(0.12, 0.04)), 4),
        "failure_type": "thermal_runaway", "source": "simulator",
    }


def bearing_wear_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "compressor",
        "psi":       round(random.gauss(850, 10), 2),
        "temp_f":    round(random.gauss(124, 5), 2),
        "vibration": round(abs(random.gauss(0.45, 0.07)), 4),
        "failure_type": "bearing_wear", "source": "simulator",
    }


# ── Turbine Failure Generators ────────────────────────────────────────────────
def combustion_instability_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "turbine",
        "psi":       round(random.gauss(1800, 40), 2),   # pressure surge drop
        "temp_f":    round(random.gauss(1120, 15), 2),   # temperature spike
        "vibration": round(abs(random.gauss(0.18, 0.04)), 4),
        "failure_type": "combustion_instability", "source": "simulator",
    }


def blade_fouling_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "turbine",
        "psi":       round(random.gauss(2060, 25), 2),   # efficiency loss
        "temp_f":    round(random.gauss(1093, 12), 2),   # thermal inefficiency
        "vibration": round(abs(random.gauss(0.09, 0.015)), 4),
        "failure_type": "blade_fouling", "source": "simulator",
    }


def rotor_imbalance_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "turbine",
        "psi":       round(random.gauss(2195, 18), 2),   # near-normal
        "temp_f":    round(random.gauss(1055, 10), 2),   # slight friction rise
        "vibration": round(abs(random.gauss(0.42, 0.07)), 4),   # progressive climb
        "failure_type": "rotor_imbalance", "source": "simulator",
    }


# ── Transformer Failure Generators ────────────────────────────────────────────
def winding_overheat_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "transformer",
        "psi":       round(random.gauss(110, 2), 3),     # kV — slight voltage sag
        "temp_f":    round(random.gauss(212, 6), 2),     # dangerous oil temperature
        "vibration": round(abs(random.gauss(0.015, 0.003)), 4),
        "failure_type": "winding_overheat", "source": "simulator",
    }


def dielectric_breakdown_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "transformer",
        "psi":       round(random.gauss(90, 5), 3),      # kV — severe voltage collapse
        "temp_f":    round(random.gauss(210, 8), 2),     # arc fault heating
        "vibration": round(abs(random.gauss(0.022, 0.005)), 4),
        "failure_type": "dielectric_breakdown", "source": "simulator",
    }


def core_loosening_reading(asset_id: str) -> dict:
    return {
        "asset_id": asset_id, "asset_type": "transformer",
        "psi":       round(random.gauss(114.5, 1.2), 3),  # kV — near-normal
        "temp_f":    round(random.gauss(189, 4), 2),
        "vibration": round(abs(random.gauss(0.09, 0.015)), 4),  # distinctive rise
        "failure_type": "core_loosening", "source": "simulator",
    }


# ── Fault Generator Dispatch ─────────────────────────────────────────────────
FAULT_GENERATORS = {
    # Compressor
    "prd_failure"            : prd_failure_reading,
    "thermal_runaway"        : thermal_runaway_reading,
    "bearing_wear"           : bearing_wear_reading,
    # Turbine
    "combustion_instability" : combustion_instability_reading,
    "blade_fouling"          : blade_fouling_reading,
    "rotor_imbalance"        : rotor_imbalance_reading,
    # Transformer
    "winding_overheat"       : winding_overheat_reading,
    "dielectric_breakdown"   : dielectric_breakdown_reading,
    "core_loosening"         : core_loosening_reading,
}


# ── RabbitMQ ─────────────────────────────────────────────────────────────────
def connect_rabbitmq() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST, credentials=credentials,
        heartbeat=60, blocked_connection_timeout=30,
    )
    for attempt in range(1, 11):
        try:
            conn = pika.BlockingConnection(params)
            log.info(f"✅ Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
            return conn
        except Exception as e:
            log.warning(f"RabbitMQ connection attempt {attempt}/10 failed: {e}")
            time.sleep(6)
    raise RuntimeError("Could not connect to RabbitMQ after 10 attempts.")


def publish(channel, reading: dict) -> None:
    payload = json.dumps({**reading, "timestamp": datetime.utcnow().isoformat() + "Z"})
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
        body=payload,
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )
    log.info(f"[→ RabbitMQ] {reading['asset_id']} ({reading['asset_type']}) | "
             f"{reading['failure_type']} | psi={reading['psi']} "
             f"temp={reading['temp_f']} vib={reading['vibration']}")


# ── Main Loop ─────────────────────────────────────────────────────────────────
def main():
    log.info("Starting GDC-PM Telemetry Simulator — Multi-Asset-Type Mode")
    log.info(f"Assets: {ASSETS}")
    log.info(f"Interval: {TELEMETRY_INTERVAL}s | RabbitMQ: {RABBITMQ_HOST}/{RABBITMQ_VHOST}")

    conn    = connect_rabbitmq()
    channel = conn.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)

    cycle = 0
    while True:
        try:
            inject_fault = os.environ.get("INJECT_FAULT", "none").lower().strip()
            inject_asset = os.environ.get("INJECT_ASSET", ASSETS[0])
            fault_fired  = False

            for asset_id in ASSETS:
                asset_type = ASSET_TYPES[asset_id]

                if inject_fault != "none" and asset_id == inject_asset:
                    generator = FAULT_GENERATORS.get(inject_fault)
                    if generator:
                        reading     = generator(asset_id)
                        fault_fired = True
                        publish(channel, reading)
                        continue
                    else:
                        log.warning(
                            f"Unknown fault type '{inject_fault}'. "
                            f"Known types: {list(FAULT_GENERATORS.keys())}"
                        )

                reading = normal_reading(asset_id, asset_type)
                publish(channel, reading)

            # Clear injection flag AFTER the full asset loop — never inside it.
            # This prevents the flag being lost if INJECT_ASSET doesn't match.
            if inject_fault != "none":
                os.environ["INJECT_FAULT"] = "none"
                if not fault_fired:
                    log.warning(
                        f"INJECT_FAULT='{inject_fault}' was set but "
                        f"INJECT_ASSET='{inject_asset}' did not match any known asset. "
                        f"Known assets: {ASSETS}"
                    )

            cycle += 1
            time.sleep(TELEMETRY_INTERVAL)

        except pika.exceptions.AMQPConnectionError:
            log.warning("RabbitMQ connection lost. Reconnecting...")
            try:
                conn.close()
            except Exception:
                pass
            conn    = connect_rabbitmq()
            channel = conn.channel()
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
        except KeyboardInterrupt:
            log.info("Simulator stopped.")
            break
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            time.sleep(5)

    conn.close()


if __name__ == "__main__":
    main()
