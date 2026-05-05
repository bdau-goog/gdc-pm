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
import threading
import time
from datetime import datetime
from typing import Optional

import pika
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, BackgroundTasks
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
    # Gas Compressors
    "COMP-TX-VALLEY-01",
    "COMP-TX-VALLEY-02",
    "COMP-TX-RIDGE-01",
    "COMP-TX-RIDGE-02",
    "COMP-TX-BASIN-01",
    # Gas Turbine Generators
    "GTG-VALLEY-01",
    "GTG-RIDGE-01",
    # High-Voltage Transformers
    "XFR-VALLEY-01",
    "XFR-RIDGE-01",
    "XFR-BASIN-01",
]

# Asset metadata registry (authoritative for the API; mirrors index.html ASSET_META)
ASSET_REGISTRY = {
    "COMP-TX-VALLEY-01": {
        "asset_type": "Gas Compressor — Reciprocating", "asset_class": "compressor",
        "location": "Valley Transmission Substation", "criticality": "HIGH",
        "nominal_psi": 855.0, "nominal_temp_f": 112.0, "nominal_vib": 0.02,
        "online_since": "2023-06-15",
    },
    "COMP-TX-VALLEY-02": {
        "asset_type": "Gas Compressor — Reciprocating", "asset_class": "compressor",
        "location": "Valley Transmission Substation", "criticality": "MEDIUM",
        "nominal_psi": 855.0, "nominal_temp_f": 112.0, "nominal_vib": 0.02,
        "online_since": "2023-06-15",
    },
    "COMP-TX-RIDGE-01": {
        "asset_type": "Gas Compressor — Centrifugal", "asset_class": "compressor",
        "location": "Ridge Transmission Plant", "criticality": "CRITICAL",
        "nominal_psi": 855.0, "nominal_temp_f": 112.0, "nominal_vib": 0.02,
        "online_since": "2022-11-01",
    },
    "COMP-TX-RIDGE-02": {
        "asset_type": "Gas Compressor — Centrifugal", "asset_class": "compressor",
        "location": "Ridge Transmission Plant", "criticality": "HIGH",
        "nominal_psi": 855.0, "nominal_temp_f": 112.0, "nominal_vib": 0.02,
        "online_since": "2022-11-01",
    },
    "COMP-TX-BASIN-01": {
        "asset_type": "Gas Compressor — Screw", "asset_class": "compressor",
        "location": "Basin Distribution Station", "criticality": "HIGH",
        "nominal_psi": 855.0, "nominal_temp_f": 112.0, "nominal_vib": 0.02,
        "online_since": "2024-01-10",
    },
    "GTG-VALLEY-01": {
        "asset_type": "Gas Turbine Generator", "asset_class": "turbine",
        "location": "Valley Transmission Substation", "criticality": "CRITICAL",
        "nominal_psi": 2200.0, "nominal_temp_f": 1050.0, "nominal_vib": 0.05,
        "online_since": "2024-03-01",
    },
    "GTG-RIDGE-01": {
        "asset_type": "Gas Turbine Generator", "asset_class": "turbine",
        "location": "Ridge Transmission Plant", "criticality": "CRITICAL",
        "nominal_psi": 2200.0, "nominal_temp_f": 1050.0, "nominal_vib": 0.05,
        "online_since": "2024-03-01",
    },
    "XFR-VALLEY-01": {
        "asset_type": "HV Transformer (115kV)", "asset_class": "transformer",
        "location": "Valley Transmission Substation", "criticality": "CRITICAL",
        "nominal_psi": 115.0, "nominal_temp_f": 185.0, "nominal_vib": 0.01,
        "online_since": "2021-05-10",
    },
    "XFR-RIDGE-01": {
        "asset_type": "HV Transformer (115kV)", "asset_class": "transformer",
        "location": "Ridge Transmission Plant", "criticality": "CRITICAL",
        "nominal_psi": 115.0, "nominal_temp_f": 185.0, "nominal_vib": 0.01,
        "online_since": "2021-05-10",
    },
    "XFR-BASIN-01": {
        "asset_type": "HV Transformer (115kV)", "asset_class": "transformer",
        "location": "Basin Distribution Station", "criticality": "HIGH",
        "nominal_psi": 115.0, "nominal_temp_f": 185.0, "nominal_vib": 0.01,
        "online_since": "2023-08-20",
    },
}

# Fault telemetry profiles — covers all three asset classes.
# The 'normal' profile uses compressor ranges; normal readings for turbines/transformers
# are generated by the telemetry-simulator (which knows each asset's type).
# Manual injections via the UI always target a specific asset; the asset_class
# in ASSET_REGISTRY determines whether the profile values are physically plausible.
FAULT_PROFILES = {
    # ── Universal ──────────────────────────────────────────────────────────────
    "normal": {
        "label": "Normal",
        "description": "Nominal operating conditions — all sensors within expected ranges",
        "color": "#00BFA5",
        "psi_range": (847, 863), "temp_range": (109, 115), "vib_range": (0.015, 0.025),
    },
    # ── Compressor Faults ──────────────────────────────────────────────────────
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
        "psi_range": (845, 860), "temp_range": (120, 132), "vib_range": (0.35, 0.60),
    },
    # ── Turbine Faults ─────────────────────────────────────────────────────────
    "combustion_instability": {
        "label": "Combustion Instability",
        "description": "Fuel-air ratio imbalance causes surge — PSI drops to ~1800, Temp spikes",
        "color": "#b71c1c",
        "psi_range": (1760, 1840), "temp_range": (1105, 1135), "vib_range": (0.14, 0.22),
    },
    "blade_fouling": {
        "label": "Blade Fouling",
        "description": "Deposit buildup reduces aerodynamic efficiency — PSI drops, Temp climbs",
        "color": "#e65100",
        "psi_range": (2020, 2100), "temp_range": (1081, 1105), "vib_range": (0.07, 0.11),
    },
    "rotor_imbalance": {
        "label": "Rotor Imbalance",
        "description": "Mass redistribution causes progressive vibration — PSI/Temp near nominal",
        "color": "#f57f17",
        "psi_range": (2177, 2213), "temp_range": (1045, 1065), "vib_range": (0.37, 0.47),
    },
    # ── Transformer Faults ─────────────────────────────────────────────────────
    "winding_overheat": {
        "label": "Winding Overheat",
        "description": "Overload or cooling failure — kV sags, oil temp climbs above 200°F",
        "color": "#880e4f",
        "psi_range": (108, 113), "temp_range": (205, 220), "vib_range": (0.012, 0.018),
    },
    "dielectric_breakdown": {
        "label": "Dielectric Breakdown",
        "description": "Insulation failure — kV collapses to 85–95, arc fault heating",
        "color": "#4a148c",
        "psi_range": (85, 95), "temp_range": (202, 218), "vib_range": (0.017, 0.027),
    },
    "core_loosening": {
        "label": "Core Loosening",
        "description": "Lamination bolt fatigue — kV near-normal, distinctive vibration rise",
        "color": "#1a237e",
        "psi_range": (113, 116), "temp_range": (185, 193), "vib_range": (0.075, 0.105),
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


# ── Demo Scenario Playlists ───────────────────────────────────────────────────
# Named sequences of fault injections with delays that tell an operational story.
# Run via /api/run-scenario for live demonstrations.

SCENARIOS = {
    "cascade_failure": {
        "name": "Compressor Cascade Failure",
        "description": (
            "A bearing degradation event escalates over time to thermal runaway, "
            "then catastrophic PRD pop — the exact scenario predictive maintenance is designed to prevent."
        ),
        "asset": "COMP-TX-VALLEY-01",
        "steps": [
            {"fault": "bearing_wear",    "delay_s": 0,  "burst": 3,
             "note": "Early bearing vibration detected"},
            {"fault": "bearing_wear",    "delay_s": 20, "burst": 5,
             "note": "Bearing wear intensifying"},
            {"fault": "thermal_runaway", "delay_s": 40, "burst": 5,
             "note": "Heat building from bearing friction — thermal runaway begins"},
            {"fault": "prd_failure",     "delay_s": 70, "burst": 5,
             "note": "Catastrophic PRD pop — uncontrolled pressure release"},
        ],
    },
    "thermal_event": {
        "name": "Cooling System Failure",
        "description": (
            "Demonstrates how a cooling system degradation event is invisible to pressure "
            "threshold alarms but clearly visible to the ML model."
        ),
        "asset": "COMP-TX-RIDGE-01",
        "steps": [
            {"fault": "thermal_runaway", "delay_s": 0,  "burst": 3,
             "note": "Temperature rising — cooling degradation begins"},
            {"fault": "thermal_runaway", "delay_s": 15, "burst": 5,
             "note": "Temperature climbing rapidly"},
            {"fault": "thermal_runaway", "delay_s": 30, "burst": 5,
             "note": "Critical threshold exceeded — operator action required"},
        ],
    },
    "fleet_stress": {
        "name": "Multi-Asset Stress Test",
        "description": (
            "Simultaneous faults across multiple assets — demonstrates fleet-wide "
            "monitoring capacity and the Grafana fleet health timeline."
        ),
        "asset": "COMP-TX-VALLEY-01",  # first asset; steps target different assets
        "steps": [
            {"fault": "bearing_wear",    "asset_override": "COMP-TX-VALLEY-01", "delay_s": 0,  "burst": 3,
             "note": "VALLEY-01: bearing degradation"},
            {"fault": "thermal_runaway", "asset_override": "COMP-TX-RIDGE-01",  "delay_s": 5,  "burst": 3,
             "note": "RIDGE-01: thermal event"},
            {"fault": "prd_failure",     "asset_override": "COMP-TX-BASIN-01",  "delay_s": 10, "burst": 3,
             "note": "BASIN-01: PRD failure"},
        ],
    },
}

# Track running scenario state for UI polling
scenario_status: dict = {"running": False, "name": None, "step": 0, "total": 0, "note": ""}

# ── Airgap state (in-memory) ──────────────────────────────────────────────────
airgap_mode: bool = False

# Track active gradual-degradation threads per asset_id
active_degrades: dict = {}  # {asset_id: {"running": bool, "fault_type": str}}

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(title="GDC-PM Fault Trigger UI", version="2.0.0")


# ── Models ────────────────────────────────────────────────────────────────────
class InjectRequest(BaseModel):
    fault_type: str
    asset_id: str
    count: Optional[int] = 1  # Number of fault readings to inject (burst)


# ── API Endpoints ─────────────────────────────────────────────────────────────
@app.get("/api/assets")
def get_assets():
    return {"assets": ASSETS}


@app.get("/api/fault-types")
def get_fault_types():
    return {"fault_types": {k: {"label": v["label"], "description": v["description"],
                                "color": v["color"]} for k, v in FAULT_PROFILES.items()}}


@app.get("/api/asset-metadata")
def get_asset_metadata():
    """Returns full metadata for all registered assets."""
    return {"assets": ASSET_REGISTRY}


@app.get("/api/asset-status")
def get_asset_status():
    """Returns the most recent ML prediction per asset for live status dots in the UI."""
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (asset_id)
                       asset_id,
                       predicted_label AS last_prediction,
                       event_time      AS last_seen
                FROM telemetry_events
                ORDER BY asset_id, event_time DESC
                """
            )
            rows = cur.fetchall()
        conn.close()
        # Mark assets with no recent data (>30s) as stale
        now = datetime.utcnow()
        statuses = []
        for r in rows:
            row = dict(r)
            age_sec = (now - r["last_seen"].replace(tzinfo=None)).total_seconds()
            if age_sec > 30:
                row["last_prediction"] = "stale"
            statuses.append(row)
        return {"statuses": statuses}
    except Exception as e:
        log.error(f"DB query error in asset-status: {e}")
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
    """Returns counts of each failure type in the last 30 minutes."""
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
        log.error(f"DB query error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.post("/api/inject-fault")
def inject_fault(req: InjectRequest):
    """
    Unified fault injection endpoint — handles all fault types including 'normal'.
    The UI always calls this endpoint; no separate inject-normal route needed.
    """
    if req.fault_type not in FAULT_PROFILES:
        raise HTTPException(status_code=400, detail=f"Unknown fault type: {req.fault_type}. "
                            f"Valid types: {list(FAULT_PROFILES.keys())}")
    if req.asset_id not in ASSETS:
        raise HTTPException(status_code=400, detail=f"Unknown asset: {req.asset_id}")

    profile = FAULT_PROFILES[req.fault_type]
    count   = max(1, min(req.count or 1, 10))
    injected = []

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

    log.info(f"Injected {count}× {req.fault_type} on {req.asset_id}")
    return {
        "status"  : "injected",
        "fault"   : req.fault_type,
        "asset"   : req.asset_id,
        "count"   : count,
        "readings": injected,
    }


@app.get("/api/scenarios")
def get_scenarios():
    """Returns available demo scenario playlists."""
    return {
        "scenarios": {
            k: {"name": v["name"], "description": v["description"],
                "step_count": len(v["steps"]), "asset": v["asset"]}
            for k, v in SCENARIOS.items()
        }
    }


@app.get("/api/scenario-status")
def get_scenario_status():
    """Returns the current scenario execution state for UI polling."""
    return scenario_status


class ScenarioRequest(BaseModel):
    scenario_id: str


def _run_scenario_thread(scenario_id: str, scenario: dict) -> None:
    """
    Executes scenario steps in a background thread.
    Each step injects a fault then waits delay_s before the next step.
    """
    global scenario_status
    steps = scenario["steps"]
    scenario_status.update({"running": True, "name": scenario["name"],
                             "step": 0, "total": len(steps), "note": "Starting..."})
    log.info(f"▶ Running scenario: {scenario['name']} ({len(steps)} steps)")

    for i, step in enumerate(steps):
        asset_id   = step.get("asset_override", scenario["asset"])
        fault_type = step["fault"]
        burst      = step.get("burst", 3)
        note       = step.get("note", f"Step {i+1}")

        scenario_status.update({"step": i + 1, "note": note})
        log.info(f"  Step {i+1}/{len(steps)}: {fault_type} on {asset_id} — {note}")

        profile = FAULT_PROFILES.get(fault_type, FAULT_PROFILES["normal"])
        for _ in range(burst):
            reading = {
                "asset_id"    : asset_id,
                "psi"         : round(random.uniform(*profile["psi_range"]), 2),
                "temp_f"      : round(random.uniform(*profile["temp_range"]), 2),
                "vibration"   : round(random.uniform(*profile["vib_range"]), 4),
                "failure_type": fault_type,
                "source"      : "scenario",
                "timestamp"   : datetime.utcnow().isoformat() + "Z",
            }
            try:
                publish_to_rabbitmq(reading)
            except Exception as e:
                log.error(f"Scenario step {i+1} publish error: {e}")

        # Wait before next step (don't sleep on the last step)
        if i < len(steps) - 1:
            time.sleep(step.get("delay_s", 0))

    scenario_status.update({"running": False, "step": len(steps),
                             "note": "Scenario complete."})
    log.info(f"✅ Scenario '{scenario['name']}' complete.")


@app.post("/api/run-scenario")
def run_scenario(req: ScenarioRequest, background_tasks: BackgroundTasks):
    """
    Starts a named demo scenario playlist in a background thread.
    Returns immediately; poll /api/scenario-status for progress.
    """
    if scenario_status.get("running"):
        raise HTTPException(status_code=409, detail="A scenario is already running.")
    scenario = SCENARIOS.get(req.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404,
                            detail=f"Unknown scenario: {req.scenario_id}. "
                                   f"Available: {list(SCENARIOS.keys())}")

    thread = threading.Thread(
        target=_run_scenario_thread,
        args=(req.scenario_id, scenario),
        daemon=True,
    )
    thread.start()
    log.info(f"Scenario thread started: {scenario['name']}")
    return {"status": "started", "scenario": scenario["name"],
            "steps": len(scenario["steps"])}


class AcknowledgeRequest(BaseModel):
    operator: Optional[str] = "ops"


@app.post("/api/acknowledge/{event_id}")
def acknowledge_event(event_id: int, req: AcknowledgeRequest):
    """Marks a telemetry event as acknowledged by an operator."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE telemetry_events
                SET acknowledged = TRUE,
                    ack_time     = NOW(),
                    ack_operator = %s
                WHERE id = %s
                  AND acknowledged = FALSE
                """,
                (req.operator, event_id),
            )
            updated = cur.rowcount
        conn.commit()
        conn.close()
        if updated == 0:
            raise HTTPException(status_code=404,
                                detail=f"Event {event_id} not found or already acknowledged.")
        return {"status": "acknowledged", "event_id": event_id, "operator": req.operator}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Acknowledge error: {e}")
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


# ── Gradual Degradation Injection ─────────────────────────────────────────────
class DegradeRequest(BaseModel):
    asset_id: str
    fault_type: str
    duration_seconds: int = 60


def _run_degrade_thread(asset_id: str, fault_type: str, duration_seconds: int) -> None:
    """
    Incrementally ramps sensor values from normal toward the fault profile
    over `duration_seconds`. Each step publishes one reading every 5s.
    This simulates progressive degradation that the ML model detects mid-ramp.
    """
    global active_degrades
    profile = FAULT_PROFILES.get(fault_type, FAULT_PROFILES["normal"])
    normal  = FAULT_PROFILES["normal"]
    steps   = max(1, duration_seconds // 5)

    active_degrades[asset_id] = {"running": True, "fault_type": fault_type, "step": 0, "steps": steps}
    log.info(f"▶ Gradual degrade: {fault_type} on {asset_id} over {duration_seconds}s ({steps} steps)")

    for i in range(steps):
        if not active_degrades.get(asset_id, {}).get("running"):
            log.info(f"Degrade cancelled: {asset_id}")
            break
        t = (i + 1) / steps  # 0→1 interpolation factor
        psi  = normal["psi_range"][0]  + t * (profile["psi_range"][0]  - normal["psi_range"][0])
        temp = normal["temp_range"][0] + t * (profile["temp_range"][0] - normal["temp_range"][0])
        vib  = normal["vib_range"][0]  + t * (profile["vib_range"][0]  - normal["vib_range"][0])

        reading = {
            "asset_id"    : asset_id,
            "psi"         : round(psi  + random.uniform(-3, 3),    2),
            "temp_f"      : round(temp + random.uniform(-1, 1),    2),
            "vibration"   : round(vib  + random.uniform(-0.003, 0.003), 4),
            "failure_type": fault_type,
            "source"      : "gradual_degrade",
            "timestamp"   : datetime.utcnow().isoformat() + "Z",
        }
        try:
            publish_to_rabbitmq(reading)
        except Exception as e:
            log.error(f"Degrade publish error (step {i+1}): {e}")

        active_degrades[asset_id]["step"] = i + 1
        time.sleep(5)

    active_degrades.pop(asset_id, None)
    log.info(f"✅ Gradual degrade complete: {fault_type} on {asset_id}")


@app.post("/api/inject/degrade")
def inject_degrade(req: DegradeRequest):
    """
    Starts a gradual degradation background thread for an asset.
    Sensor values ramp linearly from normal toward the fault profile over duration_seconds.
    Poll /api/degrade-status for progress.
    """
    if req.asset_id in active_degrades:
        raise HTTPException(status_code=409,
                            detail=f"Degradation already running on {req.asset_id}. "
                                   f"POST /api/cancel-degrade/{req.asset_id} to stop it.")
    if req.fault_type not in FAULT_PROFILES:
        raise HTTPException(status_code=400, detail=f"Unknown fault type: {req.fault_type}")
    if req.asset_id not in ASSETS:
        raise HTTPException(status_code=400, detail=f"Unknown asset: {req.asset_id}")

    thread = threading.Thread(
        target=_run_degrade_thread,
        args=(req.asset_id, req.fault_type, req.duration_seconds),
        daemon=True,
    )
    thread.start()
    log.info(f"Degrade thread started: {req.fault_type} on {req.asset_id}")
    return {"status": "started", "asset": req.asset_id,
            "fault_type": req.fault_type, "duration_seconds": req.duration_seconds}


@app.get("/api/degrade-status")
def get_degrade_status():
    """Returns all currently running gradual degradation tasks."""
    return {"active": active_degrades}


@app.post("/api/cancel-degrade/{asset_id}")
def cancel_degrade(asset_id: str):
    """Signals the running degradation thread for an asset to stop."""
    if asset_id not in active_degrades:
        raise HTTPException(status_code=404, detail=f"No active degradation on {asset_id}")
    active_degrades[asset_id]["running"] = False
    return {"status": "cancelling", "asset": asset_id}


# ── 3D Plotly Sensor Cluster Visualization ────────────────────────────────────
@app.get("/api/plot/3d/{asset_id}", response_class=HTMLResponse)
def plot_3d(asset_id: str):
    """
    Returns a self-contained Plotly 3D scatter HTML page for the given asset.
    Plots the last 150 readings as PSI × Temperature × Vibration, color-coded
    by the ML predicted_label. Designed to be embedded in an iframe.
    """
    import plotly.graph_objects as go

    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT psi, temp_f, vibration, predicted_label, event_time
                FROM telemetry_events
                WHERE asset_id = %s
                ORDER BY event_time DESC
                LIMIT 150
                """,
                (asset_id,),
            )
            rows = cur.fetchall()
        conn.close()
    except Exception as e:
        log.error(f"3D plot DB error: {e}")
        return HTMLResponse(
            f'<body style="background:#0b0c10;color:#e0e0e0;font-family:Inter,sans-serif;padding:30px">'
            f'<p style="color:#f44336">⚠ Database error: {e}</p></body>',
            status_code=500,
        )

    if not rows:
        return HTMLResponse(
            f'<body style="background:#0b0c10;color:#5a6a7a;font-family:Inter,sans-serif;'
            f'display:flex;align-items:center;justify-content:center;height:100vh;margin:0">'
            f'<p>No data yet for {asset_id}.<br>Waiting for telemetry...</p></body>'
        )

    label_colors = {
        "normal"  : "#00e676",
        "advisory": "#ffb300",
        "warning" : "#ff6d00",
        "critical": "#f44336",
    }
    label_sizes = {"normal": 3, "advisory": 5, "warning": 6, "critical": 7}

    # Group by predicted_label
    groups: dict = {}
    for r in rows:
        lbl = (r["predicted_label"] or "normal").lower()
        if lbl not in groups:
            groups[lbl] = {"psi": [], "temp": [], "vib": [], "ts": []}
        groups[lbl]["psi"].append(float(r["psi"]))
        groups[lbl]["temp"].append(float(r["temp_f"]))
        groups[lbl]["vib"].append(float(r["vibration"]))
        groups[lbl]["ts"].append(str(r["event_time"])[:19])

    # Build ordered traces: normal first (background), then faults on top
    order = ["normal", "advisory", "warning", "critical"]
    traces = []
    for lbl in order:
        if lbl not in groups:
            continue
        d = groups[lbl]
        traces.append(go.Scatter3d(
            x=d["psi"], y=d["temp"], z=d["vib"],
            mode="markers",
            name=lbl.title(),
            marker=dict(
                size=label_sizes.get(lbl, 5),
                color=label_colors.get(lbl, "#888"),
                opacity=0.80 if lbl == "normal" else 0.95,
                line=dict(width=0),
            ),
            text=[
                f"<b>{lbl.upper()}</b><br>PSI: {p:.1f}<br>Temp: {t:.1f}°F<br>Vib: {v:.4f} mm<br>{ts}"
                for p, t, v, ts in zip(d["psi"], d["temp"], d["vib"], d["ts"])
            ],
            hovertemplate="%{text}<extra></extra>",
        ))

    # Add any unlabeled groups
    for lbl, d in groups.items():
        if lbl in order:
            continue
        traces.append(go.Scatter3d(
            x=d["psi"], y=d["temp"], z=d["vib"],
            mode="markers", name=lbl.title(),
            marker=dict(size=4, color="#888", opacity=0.7),
        ))

    fig = go.Figure(data=traces)
    axis_style = dict(
        backgroundcolor="#0d1420",
        gridcolor="#1e2a38",
        zerolinecolor="#1e2a38",
        tickfont=dict(color="#5a6a7a", size=9),
        titlefont=dict(color="#7d8590", size=10),
    )
    fig.update_layout(
        paper_bgcolor="#0b0c10",
        plot_bgcolor="#0b0c10",
        font=dict(color="#e0e0e0", family="Inter, sans-serif", size=10),
        scene=dict(
            xaxis=dict(title="Pressure (PSI)", **axis_style),
            yaxis=dict(title="Temperature (°F)", **axis_style),
            zaxis=dict(title="Vibration (mm)", **axis_style),
            bgcolor="#0b0c10",
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(
            text=f"{asset_id} — Sensor Cluster (last {len(rows)} readings)",
            font=dict(size=11, color="#7d8590"),
            x=0.5,
        ),
        legend=dict(
            x=0.01, y=0.99, bgcolor="rgba(11,12,16,0.7)",
            bordercolor="#1e2a38", borderwidth=1,
            font=dict(size=10),
        ),
        showlegend=True,
    )

    html = fig.to_html(
        full_html=True,
        include_plotlyjs="cdn",
        config={"displayModeBar": True, "displaylogo": False,
                "modeBarButtonsToRemove": ["sendDataToCloud"]},
    )
    # Inject dark body style
    html = html.replace(
        "<body>",
        '<body style="background:#0b0c10;margin:0;padding:0;overflow:hidden;">'
    )
    return HTMLResponse(html)


# ── Serve Frontend HTML ───────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index():
    with open("/app/index.html") as f:
        return f.read()
