"""
gke/event-processor/processor.py

Consumes telemetry messages from RabbitMQ, calls the local Inference API
for a failure prediction, and writes the full event record (sensor data +
ML prediction) to AlloyDB Omni.

This is the central data pipeline for the GDC-PM edge architecture:
  RabbitMQ → Event Processor → Inference API → AlloyDB Omni → Grafana
"""

import os
import json
import logging
import time

import pika
import psycopg2
import psycopg2.extras
import requests

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("event-processor")

# ── Configuration ─────────────────────────────────────────────────────────────
RABBITMQ_HOST  = os.environ.get("RABBITMQ_HOST", "gdc-pm-rabbitmq.gdc-pm.svc.cluster.local")
RABBITMQ_PORT  = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER  = os.environ.get("RABBITMQ_USER", "gdc_user")
RABBITMQ_PASS  = os.environ.get("RABBITMQ_PASS", "")
RABBITMQ_VHOST = os.environ.get("RABBITMQ_VHOST", "gdc-pm")

ALLOYDB_HOST   = os.environ.get("ALLOYDB_HOST", "alloydb-omni.gdc-pm.svc.cluster.local")
ALLOYDB_PORT   = int(os.environ.get("ALLOYDB_PORT", "5432"))
ALLOYDB_DB     = os.environ.get("ALLOYDB_DB", "grid_reliability")
ALLOYDB_USER   = os.environ.get("ALLOYDB_USER", "postgres")
ALLOYDB_PASS   = os.environ.get("ALLOYDB_PASS", "")

INFERENCE_API_URL = os.environ.get(
    "INFERENCE_API_URL",
    "http://inference-api.gdc-pm.svc.cluster.local:8080/predict"
)

EXCHANGE_NAME = "telemetry"
QUEUE_NAME    = "telemetry.events"
ROUTING_KEY   = "sensor.#"


# ── Database Connection ───────────────────────────────────────────────────────
def connect_db() -> psycopg2.extensions.connection:
    for attempt in range(1, 11):
        try:
            conn = psycopg2.connect(
                host=ALLOYDB_HOST,
                port=ALLOYDB_PORT,
                dbname=ALLOYDB_DB,
                user=ALLOYDB_USER,
                password=ALLOYDB_PASS,
                connect_timeout=10,
            )
            log.info(f"✅ Connected to AlloyDB Omni at {ALLOYDB_HOST}:{ALLOYDB_PORT}")
            return conn
        except psycopg2.OperationalError as e:
            log.warning(f"DB connection attempt {attempt}/10 failed: {e}")
            time.sleep(6)
    raise RuntimeError("Could not connect to AlloyDB Omni after 10 attempts.")


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


# ── Inference ─────────────────────────────────────────────────────────────────
def call_inference_api(psi: float, temp_f: float, vibration: float) -> dict:
    """Call the local Inference API and return the prediction result."""
    try:
        resp = requests.post(
            INFERENCE_API_URL,
            json={"psi": psi, "temp_f": temp_f, "vibration": vibration},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        log.error(f"Inference API call failed: {e}")
        # Return a safe fallback to avoid blocking the pipeline
        return {
            "predicted_class": -1,
            "predicted_label": "inference_error",
            "confidence": 0.0,
            "is_failure": False,
        }


# ── Message Handler ───────────────────────────────────────────────────────────
def make_handler(db_conn):
    def handle_message(ch, method, properties, body):
        try:
            msg = json.loads(body)
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON message: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        asset_id  = msg.get("asset_id", "unknown")
        psi       = float(msg.get("psi", 0))
        temp_f    = float(msg.get("temp_f", 0))
        vibration = float(msg.get("vibration", 0))
        failure_type = msg.get("failure_type", "normal")
        source    = msg.get("source", "simulator")

        # Call ML model
        prediction = call_inference_api(psi, temp_f, vibration)

        predicted_class = prediction.get("predicted_class", -1)
        predicted_label = prediction.get("predicted_label", "unknown")
        confidence      = prediction.get("confidence", 0.0)
        is_failure      = prediction.get("is_failure", False)

        log.info(
            f"[✓] {asset_id} | sent={failure_type} | "
            f"predicted={predicted_label} (conf={confidence:.3f}) | "
            f"psi={psi} temp={temp_f} vib={vibration}"
        )

        # Write to AlloyDB Omni
        try:
            with db_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO telemetry_events
                      (asset_id, psi, temp_f, vibration, is_failure, failure_type,
                       predicted_class, predicted_label, confidence, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        asset_id, psi, temp_f, vibration,
                        1 if is_failure else 0,
                        failure_type,
                        predicted_class,
                        predicted_label,
                        confidence,
                        source,
                    ),
                )
            db_conn.commit()
        except Exception as e:
            log.error(f"DB write error: {e}")
            db_conn.rollback()

        ch.basic_ack(delivery_tag=method.delivery_tag)

    return handle_message


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    log.info("Starting GDC-PM Event Processor...")
    log.info(f"Inference API: {INFERENCE_API_URL}")
    log.info(f"AlloyDB: {ALLOYDB_HOST}:{ALLOYDB_PORT}/{ALLOYDB_DB}")

    db_conn  = connect_db()
    rmq_conn = connect_rabbitmq()
    channel  = rmq_conn.channel()

    # Ensure exchange and queue exist
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=ROUTING_KEY)

    # Process one message at a time (fair dispatch)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=QUEUE_NAME,
        on_message_callback=make_handler(db_conn),
    )

    log.info(f"✅ Consuming from queue '{QUEUE_NAME}'. Waiting for messages...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        log.info("Event processor stopped.")
    finally:
        try:
            rmq_conn.close()
        except Exception:
            pass
        try:
            db_conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
