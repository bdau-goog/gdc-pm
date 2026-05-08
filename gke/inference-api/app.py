"""
gke/inference-api/app.py

FastAPI Inference Service — Multi-Asset-Type Failure Classifier.

Loads XGBoost models for each asset class from GCS at startup, then serves
real-time predictions over a local REST API. The correct model is selected
based on the `asset_type` field in each prediction request.

Asset type → Model mapping:
  compressor   → stator_classifier     (PSI/Temp/Vib — compressor failure modes)
  turbine      → turbine_classifier    (PSI/Temp/Vib — turbine failure modes)
  transformer  → transformer_classifier (kV/Temp/Vib stored as PSI/Temp/Vib)

Environment Variables:
  GCS_MODEL_BUCKET   — GCS bucket name (e.g. 'gdc-pm-models')
                       Models loaded from gs://{bucket}/{model_name}/latest/
  GCS_MODEL_PATH     — Legacy: path for stator_classifier only (deprecated)

Endpoints:
  POST /predict       — Predict failure class from telemetry
  GET  /health        — Liveness/readiness check
  GET  /model-info    — Loaded model registry status
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import xgboost as xgb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.cloud import storage

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("inference-api")

# ── Configuration ─────────────────────────────────────────────────────────────
# ── Mode 1: GCS (GKE / cloud simulation) ──────────────────────────────────────
GCS_MODEL_BUCKET = os.environ.get("GCS_MODEL_BUCKET", "")
# Legacy single-model support: if GCS_MODEL_PATH is set but not GCS_MODEL_BUCKET,
# use it as the stator classifier path.
GCS_MODEL_PATH   = os.environ.get("GCS_MODEL_PATH", "")

# ── Mode 2: Local filesystem (GDC Software-Only / air-gapped) ─────────────────
# Set LOCAL_MODELS_DIR to a directory containing model files named
# {model_name}.ubj, {model_name}.bst, or {model_name}.json
# e.g. LOCAL_MODELS_DIR=/app/models with files:
#   /app/models/esp_classifier.ubj
#   /app/models/gas_lift_classifier.ubj
#   /app/models/mud_pump_classifier.ubj
#   /app/models/top_drive_classifier.ubj
# When set, GCS is not contacted and no GCP credentials are needed.
LOCAL_MODELS_DIR = os.environ.get("LOCAL_MODELS_DIR", "")

# ── Model Registry ────────────────────────────────────────────────────────────
# Each asset type maps to a named model. Models are loaded at startup from GCS.
# Label maps match the integer classes used during BQML training (is_failure column).

MODEL_CONFIGS = {
    # ── Upstream O&G Asset Classes (Primary) ──────────────────────────────────
    "esp_classifier": {
        "description": "ESP (Electrical Submersible Pump) — Failure Classifier",
        "label_map": {
            0: "normal",
            1: "gas_lock",
            2: "sand_ingress",
            3: "motor_overheat",
        },
    },
    "gas_lift_classifier": {
        "description": "Gas Lift Compressor — Failure Classifier",
        "label_map": {
            0: "normal",
            1: "valve_failure",
            2: "thermal_runaway",
            3: "bearing_wear",
        },
    },
    "mud_pump_classifier": {
        "description": "Triplex Mud Pump — Failure Classifier",
        "label_map": {
            0: "normal",
            1: "pulsation_dampener_failure",
            2: "valve_washout",
            3: "piston_seal_wear",
        },
    },
    "top_drive_classifier": {
        "description": "Top Drive — Failure Classifier",
        "label_map": {
            0: "normal",
            1: "gearbox_bearing_spalling",
            2: "hydraulic_leak",
        },
    },
    # ── Legacy Power/Industrial Classes (Kept for backward compatibility) ─────
    "stator_classifier": {
        "description": "Gas Compressor — Legacy Failure Classifier",
        "label_map": {
            0: "normal",
            1: "prd_failure",
            2: "thermal_runaway",
            3: "bearing_wear",
        },
    },
    "turbine_classifier": {
        "description": "Gas Turbine Generator — Legacy Failure Classifier",
        "label_map": {
            0: "normal",
            1: "combustion_instability",
            2: "blade_fouling",
            3: "rotor_imbalance",
        },
    },
    "transformer_classifier": {
        "description": "High-Voltage Transformer — Legacy Failure Classifier",
        "label_map": {
            0: "normal",
            1: "winding_overheat",
            2: "dielectric_breakdown",
            3: "core_loosening",
        },
    },
}

# Maps asset_type field → classifier model name
ASSET_TYPE_TO_MODEL = {
    # O&G asset types (primary)
    "esp":       "esp_classifier",
    "gas_lift":  "gas_lift_classifier",
    "mud_pump":  "mud_pump_classifier",
    "top_drive": "top_drive_classifier",
    # Legacy industrial (kept for backward compat)
    "compressor":   "stator_classifier",
    "turbine":      "turbine_classifier",
    "transformer":  "transformer_classifier",
}

# Global model registry: model_name → loaded xgb.Booster (or None if unavailable)
MODEL_REGISTRY: dict[str, xgb.Booster | None] = {k: None for k in MODEL_CONFIGS}


# ── GCS Download ─────────────────────────────────────────────────────────────
def download_model_from_gcs(gcs_uri: str, local_path: str) -> None:
    """Download the model.bst file from a GCS URI."""
    if not gcs_uri.startswith("gs://"):
        raise ValueError(f"Invalid GCS URI: {gcs_uri}")

    path = gcs_uri[5:]
    bucket_name, *prefix_parts = path.rstrip("/").split("/")
    prefix = "/".join(prefix_parts)

    log.info(f"Downloading model from gs://{bucket_name}/{prefix}")
    client = storage.Client()
    blobs  = list(client.list_blobs(bucket_name, prefix=prefix))

    # Look for model.bst (BQML export name) or any xgboost artifact
    model_blob = (
        next((b for b in blobs if b.name.endswith("model.bst")), None) or
        next((b for b in blobs if "xgboost" in b.name.lower()), None)
    )

    if model_blob is None:
        available = [b.name for b in blobs]
        raise FileNotFoundError(
            f"No model.bst found in {gcs_uri}. Available: {available}"
        )

    model_blob.download_to_filename(local_path)
    log.info(f"Downloaded: {model_blob.name} ({model_blob.size} bytes) → {local_path}")


def load_model(model_name: str) -> xgb.Booster | None:
    """
    Load a model by name. Priority order:
    1. LOCAL_MODELS_DIR (GDC Software-Only / air-gapped) — no GCP required.
    2. GCS_MODEL_BUCKET (GKE / cloud) — downloaded via google-cloud-storage.
    3. Legacy GCS_MODEL_PATH (stator_classifier backward compat only).
    """
    # ── Priority 1: Local filesystem (GDC Software-Only / air-gapped) ────────
    if LOCAL_MODELS_DIR:
        for ext in (".ubj", ".bst", ".json"):
            local_path = os.path.join(LOCAL_MODELS_DIR, f"{model_name}{ext}")
            if os.path.exists(local_path):
                try:
                    booster = xgb.Booster()
                    booster.load_model(local_path)
                    log.info(f"✅ Loaded model from local path: {local_path}")
                    return booster
                except Exception as e:
                    log.warning(f"⚠️  Failed to load {local_path}: {e}")
        log.warning(f"⚠️  Model '{model_name}' not found in LOCAL_MODELS_DIR={LOCAL_MODELS_DIR}")
        return None

    # ── Priority 2/3: GCS download (GKE / cloud) ─────────────────────────────
    if GCS_MODEL_BUCKET:
        gcs_uri = f"gs://{GCS_MODEL_BUCKET}/{model_name}/latest/"
    elif model_name == "stator_classifier" and GCS_MODEL_PATH:
        gcs_uri = GCS_MODEL_PATH.strip()
    else:
        log.warning(f"No path configured for model '{model_name}' — skipping.")
        return None

    local_path = f"/tmp/{model_name}.bst"
    try:
        download_model_from_gcs(gcs_uri, local_path)
        booster = xgb.Booster()
        booster.load_model(local_path)
        log.info(f"✅ Loaded model: {model_name}")
        return booster
    except Exception as e:
        log.warning(f"⚠️  Could not load model '{model_name}': {e}")
        return None


# ── Startup / Lifespan ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all configured models at startup. Gracefully skips unavailable ones."""
    if LOCAL_MODELS_DIR:
        log.info(f"Loading models from LOCAL_MODELS_DIR={LOCAL_MODELS_DIR} (air-gapped / GDC Software-Only mode)")
        for model_name in MODEL_CONFIGS:
            MODEL_REGISTRY[model_name] = load_model(model_name)
    elif GCS_MODEL_BUCKET or GCS_MODEL_PATH:
        log.info("Loading models from GCS (cloud / GKE mode)")
        for model_name in MODEL_CONFIGS:
            MODEL_REGISTRY[model_name] = load_model(model_name)
    else:
        log.warning(
            "Neither LOCAL_MODELS_DIR nor GCS_MODEL_BUCKET is set — "
            "running in dry-run mode. All predictions will return 503."
        )

    loaded  = [k for k, v in MODEL_REGISTRY.items() if v is not None]
    missing = [k for k, v in MODEL_REGISTRY.items() if v is None]
    if loaded:
        log.info(f"Models loaded ({len(loaded)}): {loaded}")
    if missing:
        log.warning(f"Models not available: {missing}")

    yield

    log.info("Shutting down inference API.")


# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="GDC-PM Multi-Asset Failure Inference API",
    description=(
        "Real-time XGBoost inference for compressor, turbine, and transformer "
        "failure classification on GKE/GDC edge nodes."
    ),
    version="2.0.0",
    lifespan=lifespan,
)


# ── Request / Response Models ─────────────────────────────────────────────────
class TelemetryInput(BaseModel):
    # Primary sensor features (same 3 features used for all asset types)
    psi:       float = Field(..., ge=0,   le=6000,  description="Pressure (PSI) — ESP intake, compressor discharge, mud pump, etc.")
    temp_f:    float = Field(..., ge=-50, le=1500,  description="Temperature (°F) — wide range for all asset types")
    vibration: float = Field(..., ge=0,   le=50.0,  description="Vibration amplitude (mm/s) — up to 28+ for mud pump dampener failures")
    # Asset routing
    asset_type: str  = Field(default="esp",
                             description="Asset class: compressor | turbine | transformer")
    # Optional extended sensors (not yet used in scoring, stored for future models)
    kv:         Optional[float] = Field(default=None, description="Line voltage kV (transformers)")

    class Config:
        # Allow extra fields gracefully (forward-compatible)
        extra = "ignore"


class PredictionResponse(BaseModel):
    predicted_class: int
    predicted_label: str
    confidence: float
    is_failure: bool
    probabilities: dict[str, float]
    asset_type: str
    model_used: str
    input: TelemetryInput


class HealthResponse(BaseModel):
    status: str
    models_loaded: dict[str, bool]
    gcs_bucket: str


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
def health():
    models_status = {k: v is not None for k, v in MODEL_REGISTRY.items()}
    any_loaded = any(models_status.values())
    return HealthResponse(
        status="ok" if any_loaded else "no_models_loaded",
        models_loaded=models_status,
        gcs_bucket=GCS_MODEL_BUCKET or GCS_MODEL_PATH or "(not configured)",
    )


@app.get("/model-info")
def model_info():
    """Returns the loaded model registry with label maps and status."""
    info = {}
    for model_name, config in MODEL_CONFIGS.items():
        info[model_name] = {
            "loaded": MODEL_REGISTRY[model_name] is not None,
            "description": config["description"],
            "label_map": config["label_map"],
            "features": ["psi (or kV)", "temp_f", "vibration"],
        }
    return {"models": info, "asset_type_routing": ASSET_TYPE_TO_MODEL}


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: TelemetryInput):
    # Determine which model to use based on asset_type
    model_name = ASSET_TYPE_TO_MODEL.get(payload.asset_type.lower(), "stator_classifier")
    model      = MODEL_REGISTRY.get(model_name)

    if model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Model '{model_name}' is not loaded. "
                f"Ensure the model has been trained (bash scripts/train-{payload.asset_type}-model.sh) "
                f"and GCS_MODEL_BUCKET is set correctly."
            )
        )

    label_map = MODEL_CONFIGS[model_name]["label_map"]

    # Build feature matrix — always [psi, temp_f, vibration] in this order
    # For transformers, psi column contains kV (handled by training data convention)
    features = np.array([[payload.psi, payload.temp_f, payload.vibration]], dtype=np.float32)
    dmat     = xgb.DMatrix(features, feature_names=["psi", "temp_f", "vibration"])

    # Predict
    raw_probs = model.predict(dmat)

    if raw_probs.ndim == 1:
        # Binary classifier edge case
        prob_failure    = float(raw_probs[0])
        predicted_class = 1 if prob_failure >= 0.5 else 0
        confidence      = prob_failure if predicted_class == 1 else (1.0 - prob_failure)
        probs           = {label_map.get(0, "0"): 1.0 - prob_failure,
                           label_map.get(1, "1"): prob_failure}
    else:
        # Multi-class (standard BQML export)
        class_probs     = raw_probs[0]
        predicted_class = int(np.argmax(class_probs))
        confidence      = float(class_probs[predicted_class])
        probs           = {label_map.get(i, str(i)): float(p)
                           for i, p in enumerate(class_probs)}

    predicted_label = label_map.get(predicted_class, "unknown")
    is_failure      = predicted_class > 0

    log.info(
        f"[{model_name}] {payload.asset_type} | "
        f"{predicted_label} (class={predicted_class}, conf={confidence:.3f}) | "
        f"psi={payload.psi} temp={payload.temp_f} vib={payload.vibration}"
    )

    return PredictionResponse(
        predicted_class=predicted_class,
        predicted_label=predicted_label,
        confidence=round(confidence, 4),
        is_failure=is_failure,
        probabilities={k: round(v, 4) for k, v in probs.items()},
        asset_type=payload.asset_type,
        model_used=model_name,
        input=payload,
    )
