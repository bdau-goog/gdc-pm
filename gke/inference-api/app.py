"""
gke/inference-api/app.py

FastAPI Inference Service for the Stator/PRD Failure Classifier.

Loads the exported XGBoost model from GCS at startup, then serves real-time
predictions over a local REST API. Designed to run on GKE or GDC edge nodes
without any dependency on BigQuery at prediction time.

Endpoints:
  POST /predict       — Predict failure class from telemetry
  GET  /health        — Liveness/readiness check
  GET  /model-info    — Model metadata
"""

import os
import logging
import tempfile
from contextlib import asynccontextmanager

import numpy as np
import xgboost as xgb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.cloud import storage

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("inference-api")

# ── Configuration ─────────────────────────────────────────────────────────────
GCS_MODEL_PATH = os.environ.get("GCS_MODEL_PATH", "")   # e.g. gs://gdc-pm-models/stator_classifier/latest/
MODEL_LOCAL_PATH = "/tmp/stator_model.bst"

# Failure class labels matching the training dataset
LABEL_MAP = {
    0: "normal",
    1: "prd_failure",
    2: "thermal_runaway",
    3: "bearing_wear",
}

# ── Global model reference ────────────────────────────────────────────────────
model: xgb.Booster | None = None
model_gcs_path: str = ""


def download_model_from_gcs(gcs_uri: str, local_path: str) -> None:
    """Download the model.bst file from a GCS URI."""
    if not gcs_uri.startswith("gs://"):
        raise ValueError(f"Invalid GCS URI: {gcs_uri}")

    path = gcs_uri[5:]
    bucket_name, *prefix_parts = path.rstrip("/").split("/")
    prefix = "/".join(prefix_parts)

    log.info(f"Downloading model from gs://{bucket_name}/{prefix}")
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Look for model.bst in the given path
    blobs = list(client.list_blobs(bucket_name, prefix=prefix))
    model_blob = next((b for b in blobs if b.name.endswith("model.bst")), None)

    if model_blob is None:
        # Try common BQML export structure names
        model_blob = next((b for b in blobs if "xgboost" in b.name.lower()), None)

    if model_blob is None:
        log.error(f"Available blobs: {[b.name for b in blobs]}")
        raise FileNotFoundError(f"No model.bst found in {gcs_uri}")

    model_blob.download_to_filename(local_path)
    log.info(f"Model downloaded to {local_path} ({model_blob.size} bytes)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model at startup."""
    global model, model_gcs_path
    model_gcs_path = GCS_MODEL_PATH.strip()

    if not model_gcs_path:
        log.warning("GCS_MODEL_PATH not set — running in demo mode with no model loaded.")
    else:
        try:
            download_model_from_gcs(model_gcs_path, MODEL_LOCAL_PATH)
            model = xgb.Booster()
            model.load_model(MODEL_LOCAL_PATH)
            log.info("✅ Model loaded successfully.")
        except Exception as e:
            log.error(f"❌ Failed to load model: {e}")
            raise RuntimeError(f"Could not load model from {model_gcs_path}: {e}")

    yield  # App runs here

    log.info("Shutting down inference API.")


app = FastAPI(
    title="GDC-PM Stator Failure Inference API",
    description="Real-time XGBoost inference for stator/PRD failure classification on GKE/GDC",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Request / Response Models ─────────────────────────────────────────────────
class TelemetryInput(BaseModel):
    psi: float = Field(..., description="Pressure in PSI", example=855.0)
    temp_f: float = Field(..., description="Temperature in Fahrenheit", example=112.0)
    vibration: float = Field(..., description="Vibration in mm", example=0.02)


class PredictionResponse(BaseModel):
    predicted_class: int
    predicted_label: str
    confidence: float
    is_failure: bool
    probabilities: dict[str, float]
    input: TelemetryInput


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_path: str


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok" if model is not None else "model_not_loaded",
        model_loaded=model is not None,
        model_path=model_gcs_path,
    )


@app.get("/model-info")
def model_info():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {
        "model_type": "BOOSTED_TREE_CLASSIFIER (XGBoost)",
        "classes": LABEL_MAP,
        "features": ["psi", "temp_f", "vibration"],
        "gcs_source": model_gcs_path,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: TelemetryInput):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded — check GCS_MODEL_PATH")

    # Build feature matrix (must match training column order: psi, temp_f, vibration)
    features = np.array([[payload.psi, payload.temp_f, payload.vibration]], dtype=np.float32)
    dmat = xgb.DMatrix(features, feature_names=["psi", "temp_f", "vibration"])

    # Predict probabilities across all classes
    raw_probs = model.predict(dmat)  # shape: (1, num_classes) or (1,) for binary

    if raw_probs.ndim == 1:
        # Binary classifier: prob of class 1
        prob_failure = float(raw_probs[0])
        probs = {LABEL_MAP[0]: 1.0 - prob_failure, LABEL_MAP[1]: prob_failure}
        predicted_class = 1 if prob_failure >= 0.5 else 0
        confidence = prob_failure if predicted_class == 1 else (1.0 - prob_failure)
    else:
        # Multi-class: raw_probs shape is (1, num_classes)
        class_probs = raw_probs[0]
        predicted_class = int(np.argmax(class_probs))
        confidence = float(class_probs[predicted_class])
        probs = {LABEL_MAP.get(i, str(i)): float(p) for i, p in enumerate(class_probs)}

    predicted_label = LABEL_MAP.get(predicted_class, "unknown")
    is_failure = predicted_class > 0

    log.info(
        f"Prediction: {predicted_label} (class={predicted_class}, "
        f"conf={confidence:.3f}) | "
        f"psi={payload.psi} temp={payload.temp_f} vib={payload.vibration}"
    )

    return PredictionResponse(
        predicted_class=predicted_class,
        predicted_label=predicted_label,
        confidence=round(confidence, 4),
        is_failure=is_failure,
        probabilities={k: round(v, 4) for k, v in probs.items()},
        input=payload,
    )
