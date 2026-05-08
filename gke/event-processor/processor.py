"""
gke/event-processor/processor.py

Consumes telemetry messages from RabbitMQ, calls the local Inference API
for a failure prediction, and writes the full event record (sensor data +
ML prediction + AI narrative) to AlloyDB Omni.

Pipeline:
  RabbitMQ → Event Processor → Inference API → AlloyDB Omni → Grafana + UI

Narrative generation (AI_NARRATIVE_ENABLED env var):
  "false"      — No narrative generated (column stays NULL)
  "rule_based" — Rule-based template strings (default, no GPU/API needed)
  "gemini"     — Vertex AI Gemini Flash API (requires GCP_PROJECT + API access)
"""

import os
import json
import logging
import time
from datetime import datetime

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

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama.gdc-pm.svc.cluster.local:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma:2b")

# Narrative mode: "false" | "rule_based" | "gemini" | "rag"
AI_NARRATIVE_ENABLED = os.environ.get("AI_NARRATIVE_ENABLED", "rag").lower().strip()

# ── Embedding model singleton ─────────────────────────────────────────────────
# Loaded once at startup (not on every call) to avoid reloading 90MB of weights
# per fault event, which caused multi-second latency spikes on every message.
_EMBED_MODEL = None

def _get_embed_model():
    """Lazy singleton for the sentence embedding model."""
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            log.info("Loading embedding model all-MiniLM-L6-v2...")
            _EMBED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
            log.info("✅ Embedding model loaded")
        except Exception as e:
            log.error(f"Failed to load embedding model: {e}")
            return None
    return _EMBED_MODEL

GCP_PROJECT = os.environ.get("GCP_PROJECT", "gdc-pm")

EXCHANGE_NAME = "telemetry"
QUEUE_NAME    = "telemetry.events"
ROUTING_KEY   = "sensor.#"

# ── Rule-based Narrative Templates ────────────────────────────────────────────
# These populate the ai_narrative and recommended_action columns without a GPU.
# When AI_NARRATIVE_ENABLED="gemini", these are replaced by Vertex AI Gemini.
# The column schema and all UI display code remain unchanged.

NARRATIVE_TEMPLATES = {
    "prd_failure": {
        "narrative": (
            "The Pressure Relief Device on {asset_id} has activated and failed to reseat. "
            "Pressure has collapsed to {psi:.0f} PSI against a nominal of 855 PSI — "
            "a {psi_delta:.0f} PSI drop in a single reading cycle. "
            "Temperature spike of {temp_f:.0f}°F and vibration of {vibration:.3f}mm confirm "
            "this is a mechanical release event, not a sensor fault. "
            "This is a CRITICAL safety event: uncontrolled gas venting creates fire and explosion risk."
        ),
        "action": (
            "IMMEDIATE: Isolate {asset_id} from the pipeline. "
            "Dispatch field technician for PRD physical inspection and replacement. "
            "Notify safety officer and control room. Estimated downtime: 4–8 hours."
        ),
    },
    "thermal_runaway": {
        "narrative": (
            "{asset_id} is operating at {temp_f:.0f}°F — {temp_delta:.0f}°F above the 150°F "
            "safety threshold. Pressure is holding at {psi:.0f} PSI (within normal range), "
            "which means a standard pressure alarm would NOT have triggered this alert. "
            "This multivariate signature is characteristic of cooling system degradation. "
            "Left unaddressed for 15–45 minutes, seals will degrade and internal components will warp."
        ),
        "action": (
            "Reduce {asset_id} load to 50% immediately. "
            "Check cooling water flow rate and heat exchanger fouling. "
            "Schedule on-site inspection within 2 hours. "
            "If temperature exceeds 195°F before inspection, escalate to immediate shutdown."
        ),
    },
    "bearing_wear": {
        "narrative": (
            "Vibration on {asset_id} has reached {vibration:.3f}mm — "
            "{vib_ratio:.0f}× the nominal operating level of 0.02mm. "
            "Pressure ({psi:.0f} PSI) and temperature ({temp_f:.0f}°F) remain within normal range, "
            "indicating early-stage bearing surface fatigue rather than an acute event. "
            "This is a progressive failure mode: without intervention, vibration will continue "
            "to climb and ultimately cause shaft seizure."
        ),
        "action": (
            "Schedule lubrication inspection for {asset_id} within 48 hours. "
            "If vibration exceeds 0.55mm before inspection, advance to 4-hour response. "
            "Cost of lubrication service: ~$500. "
            "Cost of bearing replacement after seizure: $45K–$180K."
        ),
    },
}

# Nominal values for delta calculations (per asset type; matches training data)
NOMINALS = {
    "compressor":  {"psi": 855.0, "temp_f": 112.0, "vibration": 0.02},
    "turbine":     {"psi": 2200.0, "temp_f": 1050.0, "vibration": 0.05},
    "transformer": {"psi": None,   "temp_f": 185.0,  "vibration": 0.01},
}

# ── Asset type inference from asset_id prefix ─────────────────────────────────
def infer_asset_type(asset_id: str) -> str:
    prefix = asset_id.split("-")[0].upper()
    return {"COMP": "compressor", "GTG": "turbine", "XFR": "transformer"}.get(prefix, "compressor")


# ── Narrative Generation ──────────────────────────────────────────────────────
def generate_rule_based_narrative(
    asset_id: str, asset_type: str, predicted_label: str,
    psi: float, temp_f: float, vibration: float
) -> tuple[str | None, str | None]:
    """
    Returns (ai_narrative, recommended_action) using rule-based templates.
    Returns (None, None) for normal predictions.
    """
    template = NARRATIVE_TEMPLATES.get(predicted_label)
    if not template:
        return None, None

    nominals = NOMINALS.get(asset_type, NOMINALS["compressor"])
    nominal_psi   = nominals["psi"] or 0
    nominal_temp  = nominals["temp_f"]
    nominal_vib   = nominals["vibration"]

    context = {
        "asset_id":   asset_id,
        "psi":        psi,
        "temp_f":     temp_f,
        "vibration":  vibration,
        "psi_delta":  abs(nominal_psi - psi),
        "temp_delta": abs(temp_f - nominal_temp),
        "vib_ratio":  (vibration / nominal_vib) if nominal_vib > 0 else 0,
    }

    try:
        narrative = template["narrative"].format(**context)
        action    = template["action"].format(**context)
        return narrative, action
    except KeyError as e:
        log.warning(f"Narrative template key error for {predicted_label}: {e}")
        return None, None


def generate_rag_narrative(
    db_conn, asset_id: str, asset_type: str, predicted_label: str
) -> tuple[str | None, str | None]:
    """
    RAG Pipeline:
    1. Query pgvector filtered by asset_class for the fault type.
    2. Prompt local Ollama model to generate narrative and resolution options.
    """
    try:
        model = _get_embed_model()
        if model is None:
            return None, None

        query = f"{asset_type} {predicted_label}"
        query_embedding = model.encode(query).tolist()
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        # Retrieve top 3 context excerpts filtered by asset_class to avoid
        # returning ESP content for mud pump faults etc.
        context_excerpts = []
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT content FROM rag_documents
                WHERE asset_class = %s
                ORDER BY embedding <-> %s::vector
                LIMIT 3
            """, (asset_type, embedding_str))
            rows = cur.fetchall()
            if not rows:
                # Fallback: search all classes if no asset-specific docs exist
                log.warning(f"No RAG docs for asset_class '{asset_type}', searching all classes")
                cur.execute("""
                    SELECT content FROM rag_documents
                    ORDER BY embedding <-> %s::vector
                    LIMIT 3
                """, (embedding_str,))
                rows = cur.fetchall()
            for r in rows:
                context_excerpts.append(r[0])
                
        context_text = "\n\n".join(context_excerpts)
        
        prompt = f"""You are an O&G maintenance AI. The XGBoost model detected {predicted_label} on {asset_id}. Using this manual: {context_text}
        
Write a 2-sentence assessment and list 2 specific resolution options.
Output EXACTLY in this JSON format, no markdown formatting:
{{
  "assessment": "Two sentence assessment...",
  "options": [
    {{"action": "Option A action", "cost": 0, "time": "Instant"}},
    {{"action": "Option B action", "cost": 5000, "time": "4 hours"}}
  ]
}}
"""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=30)
        resp.raise_for_status()
        result_text = resp.json().get("response", "").strip()
        
        return result_text, "Awaiting operator selection"
        
    except Exception as e:
        log.error(f"RAG narrative generation failed: {e}. Falling back to rule-based.")
        return None, None

def generate_gemini_narrative(
    asset_id: str, asset_type: str, predicted_label: str, confidence: float,
    psi: float, temp_f: float, vibration: float, similar_count: int
) -> tuple[str | None, str | None]:
    """
    Calls Vertex AI Gemini Flash to generate narrative + recommended action.
    Activated when AI_NARRATIVE_ENABLED="gemini".

    Requires: pip install google-cloud-aiplatform
    """
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel

        vertexai.init(project=GCP_PROJECT, location="us-central1")
        gemini = GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are an expert operations engineer at a power generation facility.
An ML model has detected the following condition:

Asset: {asset_id} (Type: {asset_type})
Sensor Reading: PSI={psi:.1f}, Temp={temp_f:.1f}°F, Vibration={vibration:.4f}mm
ML Prediction: {predicted_label} (confidence: {confidence:.1%})
Similar events detected in last 7 days: {similar_count}

Write exactly two paragraphs:
1. In plain English, explain what this sensor pattern means physically — what is happening inside the equipment.
2. Recommend the single most important immediate action the operator should take, with a specific time window.

Be direct and specific. Do not repeat the raw sensor numbers. Do not use jargon.
Maximum 80 words total."""

        response = gemini.generate_content(prompt)
        text = response.text.strip()
        # Split narrative from action at the paragraph break
        parts = [p.strip() for p in text.split("\n\n") if p.strip()]
        narrative = parts[0] if len(parts) > 0 else text
        action    = parts[1] if len(parts) > 1 else None
        return narrative, action

    except Exception as e:
        log.error(f"Gemini narrative generation failed: {e}. Falling back to rule-based.")
        return generate_rule_based_narrative(
            asset_id, asset_type, predicted_label, psi, temp_f, vibration
        )


def generate_narrative(
    db_conn, asset_id: str, asset_type: str, predicted_label: str, predicted_class: int,
    confidence: float, psi: float, temp_f: float, vibration: float,
    similar_count: int
) -> tuple[str | None, str | None]:
    """Dispatch to the correct narrative generator based on AI_NARRATIVE_ENABLED."""
    if AI_NARRATIVE_ENABLED == "false" or predicted_class == 0:
        return None, None
    elif AI_NARRATIVE_ENABLED == "rag":
        narr, action = generate_rag_narrative(db_conn, asset_id, asset_type, predicted_label)
        if narr: return narr, action
        return generate_rule_based_narrative(asset_id, asset_type, predicted_label, psi, temp_f, vibration)
    elif AI_NARRATIVE_ENABLED == "gemini":
        return generate_gemini_narrative(
            asset_id, asset_type, predicted_label, confidence,
            psi, temp_f, vibration, similar_count
        )
    else:  # "rule_based"
        return generate_rule_based_narrative(
            asset_id, asset_type, predicted_label, psi, temp_f, vibration
        )


# ── Database Connection ───────────────────────────────────────────────────────
def connect_db() -> psycopg2.extensions.connection:
    for attempt in range(1, 11):
        try:
            conn = psycopg2.connect(
                host=ALLOYDB_HOST, port=ALLOYDB_PORT,
                dbname=ALLOYDB_DB, user=ALLOYDB_USER, password=ALLOYDB_PASS,
                connect_timeout=10,
            )
            log.info(f"✅ Connected to AlloyDB Omni at {ALLOYDB_HOST}:{ALLOYDB_PORT}")
            return conn
        except psycopg2.OperationalError as e:
            log.warning(f"DB connection attempt {attempt}/10 failed: {e}")
            time.sleep(6)
    raise RuntimeError("Could not connect to AlloyDB Omni after 10 attempts.")


def ensure_db_connected(conn: psycopg2.extensions.connection) -> psycopg2.extensions.connection:
    """
    Validate the DB connection is alive and reconnect if not.
    Called before every INSERT to guard against stale connections
    after AlloyDB Omni restarts or TCP idle timeouts.
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return conn
    except Exception:
        log.warning("AlloyDB connection stale — reconnecting...")
        try:
            conn.close()
        except Exception:
            pass
        return connect_db()


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


# ── Inference ─────────────────────────────────────────────────────────────────
def call_inference_api(asset_type: str, psi: float, temp_f: float, vibration: float,
                       kv: float | None = None) -> dict:
    """Call the local Inference API and return the prediction result."""
    try:
        payload = {"psi": psi, "temp_f": temp_f, "vibration": vibration,
                   "asset_type": asset_type}
        if kv is not None:
            payload["kv"] = kv
        resp = requests.post(INFERENCE_API_URL, json=payload, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        log.error(f"Inference API call failed: {e}")
        return {"predicted_class": -1, "predicted_label": "inference_error",
                "confidence": 0.0, "is_failure": False}


# ── Similar Event Count ───────────────────────────────────────────────────────
def count_similar_events(conn, asset_id: str, predicted_label: str) -> int:
    """Count events with the same label on the same asset in the last 7 days."""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM telemetry_events
                WHERE asset_id = %s
                  AND predicted_label = %s
                  AND event_time > NOW() - INTERVAL '7 days'
                """,
                (asset_id, predicted_label),
            )
            return cur.fetchone()[0]
    except Exception:
        return 0


# ── Message Handler ───────────────────────────────────────────────────────────
def make_handler(db_conn: psycopg2.extensions.connection):
    """
    Returns a RabbitMQ message callback. db_conn is captured in the closure
    and can be rebound via `nonlocal` when ensure_db_connected() reconnects.
    This lets the processor survive AlloyDB restarts without restarting the pod.
    """
    def handle_message(ch, method, properties, body):
        nonlocal db_conn
        try:
            msg = json.loads(body)
        except json.JSONDecodeError as e:
            log.error(f"Invalid JSON message: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        asset_id     = msg.get("asset_id", "unknown")
        asset_type   = msg.get("asset_type") or infer_asset_type(asset_id)
        psi          = float(msg.get("psi", 0))
        temp_f       = float(msg.get("temp_f", 0))
        vibration    = float(msg.get("vibration", 0))
        kv           = float(msg["kv"]) if "kv" in msg else None
        acoustic_db  = float(msg["acoustic_db"]) if "acoustic_db" in msg else None
        failure_type = msg.get("failure_type", "normal")
        source       = msg.get("source", "simulator")

        # Call ML model
        prediction      = call_inference_api(asset_type, psi, temp_f, vibration, kv)
        predicted_class = prediction.get("predicted_class", -1)
        predicted_label = prediction.get("predicted_label", "unknown")
        confidence      = prediction.get("confidence", 0.0)
        is_failure      = prediction.get("is_failure", False)

        log.info(
            f"[✓] {asset_id} ({asset_type}) | sent={failure_type} | "
            f"predicted={predicted_label} (conf={confidence:.3f}) | "
            f"psi={psi} temp={temp_f} vib={vibration}"
        )

        # Ensure DB connection is alive before writing
        db_conn = ensure_db_connected(db_conn)

        # Count similar recent events (used in narrative + stored for UI)
        similar_count = 0
        if predicted_class > 0:
            similar_count = count_similar_events(db_conn, asset_id, predicted_label)

        # Generate AI narrative
        ai_narrative, recommended_action = generate_narrative(
            db_conn=db_conn, asset_id=asset_id, asset_type=asset_type,
            predicted_label=predicted_label, predicted_class=predicted_class,
            confidence=confidence, psi=psi, temp_f=temp_f, vibration=vibration,
            similar_count=similar_count,
        )

        # Write to AlloyDB Omni
        try:
            with db_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO telemetry_events
                      (asset_id, asset_type, psi, temp_f, vibration, kv, acoustic_db,
                       is_failure, failure_type, predicted_class, predicted_label,
                       confidence, source, ai_narrative, recommended_action,
                       similar_events_count)
                    VALUES (%s,%s,%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        asset_id, asset_type, psi, temp_f, vibration, kv, acoustic_db,
                        1 if is_failure else 0, failure_type,
                        predicted_class, predicted_label, confidence, source,
                        ai_narrative, recommended_action, similar_count,
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
    log.info(f"Inference API:       {INFERENCE_API_URL}")
    log.info(f"AlloyDB:             {ALLOYDB_HOST}:{ALLOYDB_PORT}/{ALLOYDB_DB}")
    log.info(f"AI Narrative mode:   {AI_NARRATIVE_ENABLED}")

    db_conn  = connect_db()
    rmq_conn = connect_rabbitmq()
    channel  = rmq_conn.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=ROUTING_KEY)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=make_handler(db_conn))

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
