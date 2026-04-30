"""
gke/telemetry-simulator/simulator.py

Continuously generates realistic stator/PRD telemetry and publishes
it to a RabbitMQ exchange. Operates in two modes:

  1. Normal Operation: Streams continuous normal telemetry with Gaussian
     noise across all configured assets (one message every 5 seconds).
  2. Injected Fault: When a FAULT_TYPE env variable is set, publishes a
     single burst of fault telemetry for a specified asset, then reverts
     to normal. Used by the fault-trigger-ui.

Environment Variables:
  RABBITMQ_HOST       — RabbitMQ host (default: gdc-pm-rabbitmq.gdc-pm...)
  RABBITMQ_PORT       — AMQP port (default: 5672)
  RABBITMQ_USER       — Username (default: gdc_user)
  RABBITMQ_PASS       — Password
  RABBITMQ_VHOST      — Virtual host (default: gdc-pm)
  TELEMETRY_INTERVAL  — Seconds between normal readings (default: 5)
  INJECT_FAULT        — Fault type to inject on next cycle: prd_failure,
                        thermal_runaway, bearing_wear, or none
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
RABBITMQ_HOST    = os.environ.get("RABBITMQ_HOST", "gdc-pm-rabbitmq.gdc-pm.svc.cluster.local")
RABBITMQ_PORT    = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER    = os.environ.get("RABBITMQ_USER", "gdc_user")
RABBITMQ_PASS    = os.environ.get("RABBITMQ_PASS", "")
RABBITMQ_VHOST   = os.environ.get("RABBITMQ_VHOST", "gdc-pm")
TELEMETRY_INTERVAL = float(os.environ.get("TELEMETRY_INTERVAL", "5"))

EXCHANGE_NAME  = "telemetry"
ROUTING_KEY    = "sensor.reading"

ASSETS = [
    "COMP-TX-VALLEY-01",
    "COMP-TX-VALLEY-02",
    "COMP-TX-RIDGE-01",
    "COMP-TX-RIDGE-02",
    "COMP-TX-BASIN-01",
]


# ── Telemetry Generators ──────────────────────────────────────────────────────
def normal_reading(asset_id: str) -> dict:
    return {
        "asset_id"    : asset_id,
        "psi"         : round(random.gauss(855, 8), 2),
        "temp_f"      : round(random.gauss(112, 3), 2),
        "vibration"   : round(abs(random.gauss(0.02, 0.005)), 4),
        "failure_type": "normal",
        "source"      : "simulator",
    }


def prd_failure_reading(asset_id: str) -> dict:
    return {
        "asset_id"    : asset_id,
        "psi"         : round(random.gauss(645, 20), 2),
        "temp_f"      : round(random.gauss(162, 6), 2),
        "vibration"   : round(abs(random.gauss(0.90, 0.12)), 4),
        "failure_type": "prd_failure",
        "source"      : "simulator",
    }


def thermal_runaway_reading(asset_id: str) -> dict:
    return {
        "asset_id"    : asset_id,
        "psi"         : round(random.gauss(845, 12), 2),
        "temp_f"      : round(random.gauss(188, 10), 2),
        "vibration"   : round(abs(random.gauss(0.12, 0.04)), 4),
        "failure_type": "thermal_runaway",
        "source"      : "simulator",
    }


def bearing_wear_reading(asset_id: str) -> dict:
    return {
        "asset_id"    : asset_id,
        "psi"         : round(random.gauss(850, 10), 2),
        "temp_f"      : round(random.gauss(124, 5), 2),
        "vibration"   : round(abs(random.gauss(0.45, 0.07)), 4),
        "failure_type": "bearing_wear",
        "source"      : "simulator",
    }


FAULT_GENERATORS = {
    "prd_failure"    : prd_failure_reading,
    "thermal_runaway": thermal_runaway_reading,
    "bearing_wear"   : bearing_wear_reading,
}


# ── RabbitMQ Connection ───────────────────────────────────────────────────────
def connect_rabbitmq() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30,
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
    payload = json.dumps({
        **reading,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    })
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
        body=payload,
        properties=pika.BasicProperties(
            content_type="application/json",
            delivery_mode=2,  # persistent
        ),
    )
    log.info(f"[→ RabbitMQ] {reading['asset_id']} | {reading['failure_type']} | "
             f"psi={reading['psi']} temp={reading['temp_f']} vib={reading['vibration']}")


# ── Main Loop ─────────────────────────────────────────────────────────────────
def main():
    log.info("Starting GDC-PM Telemetry Simulator...")
    log.info(f"Assets: {ASSETS}")
    log.info(f"Interval: {TELEMETRY_INTERVAL}s | RabbitMQ: {RABBITMQ_HOST}/{RABBITMQ_VHOST}")

    conn = connect_rabbitmq()
    channel = conn.channel()

    # Declare exchange (idempotent)
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="topic",
        durable=True,
    )

    cycle = 0
    while True:
        try:
            # Check for fault injection instruction from environment
            inject_fault = os.environ.get("INJECT_FAULT", "none").lower().strip()
            inject_asset = os.environ.get("INJECT_ASSET", ASSETS[0])

            for asset_id in ASSETS:
                if inject_fault != "none" and asset_id == inject_asset:
                    generator = FAULT_GENERATORS.get(inject_fault)
                    if generator:
                        reading = generator(asset_id)
                        publish(channel, reading)
                        # Clear the injection flag after one publish
                        os.environ["INJECT_FAULT"] = "none"
                        continue

                reading = normal_reading(asset_id)
                publish(channel, reading)

            cycle += 1
            time.sleep(TELEMETRY_INTERVAL)

        except pika.exceptions.AMQPConnectionError:
            log.warning("RabbitMQ connection lost. Reconnecting...")
            try:
                conn.close()
            except Exception:
                pass
            conn = connect_rabbitmq()
            channel = conn.channel()
            channel.exchange_declare(
                exchange=EXCHANGE_NAME,
                exchange_type="topic",
                durable=True,
            )
        except KeyboardInterrupt:
            log.info("Simulator stopped.")
            break
        except Exception as e:
            log.error(f"Unexpected error: {e}")
            time.sleep(5)

    conn.close()


if __name__ == "__main__":
    main()
