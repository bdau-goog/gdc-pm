"""
gke/fault-trigger-ui/app.py

Fault Trigger UI — FastAPI backend for the GDC-PM Predictive Maintenance Demo.

Provides an operator control panel to:
  1. View current asset status from AlloyDB Omni
  2. Inject specific fault scenarios by publishing directly to RabbitMQ
  3. Monitor recent detections and prediction history

This is the "demo control surface" — allowing the presenter to trigger
specific failure types on specific assets in real time during a live demo.
"""

import os
import json
import logging
import random
from datetime import datetime
from typing import Optional

import pika
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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

ALLOYDB_HOST   = os.environ.get("ALLOYDB_HOST", "alloydb-omni.gdc-pm.svc.cluster.local")
ALLOYDB_PORT   = int(os.environ.get("ALLOYDB_PORT", "5432"))
ALLOYDB_DB     = os.environ.get("ALLOYDB_DB", "grid_reliability")
ALLOYDB_USER   = os.environ.get("ALLOYDB_USER", "postgres")
ALLOYDB_PASS   = os.environ.get("ALLOYDB_PASS", "")

EXCHANGE_NAME = "telemetry"
ROUTING_KEY   = "sensor.reading"

ASSETS = [
    "COMP-TX-VALLEY-01",
    "COMP-TX-VALLEY-02",
    "COMP-TX-RIDGE-01",
    "COMP-TX-RIDGE-02",
    "COMP-TX-BASIN-01",
]

# Fault telemetry profiles
FAULT_PROFILES = {
    "prd_failure": {
        "label": "PRD Failure",
        "description": "Pressure Relief Device pop — pressure drop, temp spike, high vibration",
        "color": "#e53935",
        "psi_range":   (620, 670),
        "temp_range":  (155, 170),
        "vib_range":   (0.78, 1.05),
    },
    "thermal_runaway": {
        "label": "Thermal Runaway",
        "description": "Temperature exceeds safe operating range — pressure normal, vibration elevated",
        "color": "#ff6f00",
        "psi_range":   (840, 860),
        "temp_range":  (178, 200),
        "vib_range":   (0.08, 0.18),
    },
    "bearing_wear": {
        "label": "Bearing Wear",
        "description": "Progressive bearing degradation — vibration climbing, slight temp rise",
        "color": "#f9a825",
        "psi_range":   (845, 860),
        "temp_range":  (120, 132),
        "vib_range":   (0.35, 0.60),
    },
}


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
        virtual_host=RABBITMQ_VHOST, credentials=credentials,
        socket_timeout=5,
    )
    conn = pika.BlockingConnection(params)
    channel = conn.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.basic_publish(
        exchange=EXCHANGE_NAME,
        routing_key=ROUTING_KEY,
        body=json.dumps(reading),
        properties=pika.BasicProperties(content_type="application/json", delivery_mode=2),
    )
    conn.close()


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(title="GDC-PM Fault Trigger UI", version="1.0.0")


# ── Models ────────────────────────────────────────────────────────────────────
class InjectRequest(BaseModel):
    fault_type: str
    asset_id: str
    count: Optional[int] = 1  # Number of fault readings to inject (burst)


# ── API Endpoints ─────────────────────────────────────────────────────────────
@app.post("/api/inject-normal")
def inject_normal(req: InjectRequest):
    if req.asset_id not in ASSETS:
        raise HTTPException(status_code=400, detail=f"Unknown asset: {req.asset_id}")

    count = max(1, min(req.count or 1, 10))
    injected = []

    for _ in range(count):
        reading = {
            "asset_id"    : req.asset_id,
            "psi"         : round(random.gauss(855, 8), 2),
            "temp_f"      : round(random.gauss(112, 3), 2),
            "vibration"   : round(abs(random.gauss(0.02, 0.005)), 4),
            "failure_type": "normal",
            "source"      : "manual_injection",
            "timestamp"   : datetime.utcnow().isoformat() + "Z",
        }
        publish_to_rabbitmq(reading)
        injected.append(reading)

    log.info(f"Injected {count}x normal readings on {req.asset_id}")
    return {
        "status"  : "injected",
        "fault"   : "normal",
        "asset"   : req.asset_id,
        "count"   : count,
        "readings": injected,
    }

@app.get("/api/assets")
def get_assets():
    return {"assets": ASSETS}


@app.get("/api/fault-types")
def get_fault_types():
    return {"fault_types": {k: {"label": v["label"], "description": v["description"],
                                "color": v["color"]} for k, v in FAULT_PROFILES.items()}}


@app.get("/api/recent-events")
def get_recent_events(limit: int = 50):
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT event_time, asset_id, psi, temp_f, vibration,
                       failure_type, predicted_label, confidence, source
                FROM telemetry_events
                ORDER BY event_time DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
        conn.close()
        return {"events": [dict(r) for r in rows]}
    except Exception as e:
        log.error(f"DB query error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/api/alert-summary")
def get_alert_summary():
    """Returns counts of each failure type in the last 100 records."""
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT predicted_label, COUNT(*) AS count
                FROM telemetry_events
                ORDER BY event_time DESC
                LIMIT 200
                GROUP BY predicted_label
                """
            )
            rows = cur.fetchall()
        conn.close()
        return {"summary": [dict(r) for r in rows]}
    except Exception as e:
        log.error(f"DB query error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.post("/api/inject-fault")
def inject_fault(req: InjectRequest):
    if req.fault_type not in FAULT_PROFILES:
        raise HTTPException(status_code=400, detail=f"Unknown fault type: {req.fault_type}")
    if req.asset_id not in ASSETS:
        raise HTTPException(status_code=400, detail=f"Unknown asset: {req.asset_id}")

    profile = FAULT_PROFILES[req.fault_type]
    injected = []

    count = max(1, min(req.count or 1, 10))  # Cap at 10 injections

    for _ in range(count):
        reading = {
            "asset_id"    : req.asset_id,
            "psi"         : round(random.uniform(*profile["psi_range"]), 2),
            "temp_f"      : round(random.uniform(*profile["temp_range"]), 2),
            "vibration"   : round(random.uniform(*profile["vib_range"]), 4),
            "failure_type": req.fault_type,
            "source"      : "manual_injection",
            "timestamp"   : datetime.utcnow().isoformat() + "Z",
        }
        publish_to_rabbitmq(reading)
        injected.append(reading)

    log.info(f"Injected {count}x {req.fault_type} on {req.asset_id}")
    return {
        "status"  : "injected",
        "fault"   : req.fault_type,
        "asset"   : req.asset_id,
        "count"   : count,
        "readings": injected,
    }


# ── Serve Frontend HTML ───────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index():
    with open("/app/index.html") as f:
        return f.read()
