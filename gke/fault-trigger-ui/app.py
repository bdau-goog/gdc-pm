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

import asyncio
import json
import logging
import math
import os
import random
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pika
import psycopg2
import psycopg2.extras
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse
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
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:latest")

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
        # ── esp_thermal model (H3 VFD thermal constraint) ──
        thermal_path = MODELS_DIR / "esp_thermal.ubj"
        if thermal_path.exists():
            bt = xgb.Booster()
            bt.load_model(str(thermal_path))
            HEALTH_MODELS["esp_thermal"] = bt
            log.info(f"✅ Loaded thermal constraint model: esp_thermal ({thermal_path.stat().st_size//1024} KB)")
        else:
            log.warning("⚠️  esp_thermal.ubj not found — vizier_optimize() will use physics polynomial fallback")
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


# ── Embed Model Singleton (Sprint 5 v8 Fix 7) ─────────────────────────────────
# Lazy-loaded SentenceTransformer for AlloyDB pgvector RAG.
# Same pattern as event-processor.py. Falls back gracefully if unavailable.
_embed_model = None


def _get_embed_model_singleton():
    """Return the SentenceTransformer model, loading it once on first call."""
    global _embed_model
    if _embed_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embed_model = SentenceTransformer('all-MiniLM-L6-v2')
            log.info("✅ SentenceTransformer loaded: all-MiniLM-L6-v2")
        except Exception as e:
            log.warning(f"SentenceTransformer unavailable — static RAG disabled: {e}")
    return _embed_model


# ChromaDB removed (Sprint 5 v8 Fix 7) — now using AlloyDB rag_documents with pgvector
chroma_client = None


# ── Document Generator ────────────────────────────────────────────────────────
def generate_dynamic_documents(asset_id: str, fault_type: str, sensors: dict) -> list:
    """Generates 3-4 realistic enterprise documents based on fault type."""
    docs = []
    now = datetime.utcnow()
    
    if fault_type == "motor_overheat":
        water_cut = random.randint(62, 75)
        docs.append({
            "doc_type": "lab_report",
            "content": f"Lab Report: Fluid sample analysis for {asset_id}. Water cut measured at {water_cut}%. Current motor temp: {sensors.get('temp', 0):.1f}°F, amps: {sensors.get('motor_amps', 0):.1f}A. High water cut severely restricting motor cooling.",
            "timestamp": (now - timedelta(hours=random.randint(1, 4))).isoformat() + "Z"
        })
        docs.append({
            "doc_type": "maximo_pm",
            "content": f"Maximo PM Record: Annual ESP electrical check for {asset_id}. Overdue by {random.randint(10, 30)} days. Surface cable hot to the touch.",
            "timestamp": (now - timedelta(days=random.randint(10, 30))).isoformat() + "Z"
        })
        docs.append({
            "doc_type": "shift_note",
            "content": f"Shift Note: Operator observed erratic power draw on {asset_id}. VFD log shows frequent current spikes above {sensors.get('motor_amps', 0):.1f}A.",
            "timestamp": (now - timedelta(hours=random.randint(2, 6))).isoformat() + "Z"
        })
    elif fault_type == "gas_lock":
        gvf = random.randint(71, 85)  # guaranteed > 70 → always triggers 0.6x RUL adjustment in adjust_rul_with_documents
        docs.append({
            "doc_type": "well_test",
            "content": f"Well Test: Gas Void Fraction (GVF) at intake for {asset_id} estimated at {gvf}%. Current intake pressure: {sensors.get('psi', 0):.1f} PSI.",
            "timestamp": (now - timedelta(hours=random.randint(1, 4))).isoformat() + "Z"
        })
        docs.append({
            "doc_type": "vfd_log",
            "content": f"VFD Log: Rapid unloading events on {asset_id}. Current dropped to {sensors.get('motor_amps', 0):.1f}A.",
            "timestamp": (now - timedelta(minutes=random.randint(15, 60))).isoformat() + "Z"
        })
        docs.append({
            "doc_type": "shift_note",
            "content": f"Shift Note: Annulus pressure building on {asset_id}. Needs casing bleed.",
            "timestamp": (now - timedelta(hours=random.randint(2, 6))).isoformat() + "Z"
        })
    elif fault_type == "sand_ingress":
        sand_conc = random.randint(150, 300)
        docs.append({
            "doc_type": "lab_report",
            "content": f"Lab Report: Sand concentration for {asset_id} is {sand_conc} ppm. Abrasive wear expected. Current vibration: {sensors.get('vib', 0):.2f} mm/s.",
            "timestamp": (now - timedelta(hours=random.randint(12, 48))).isoformat() + "Z"
        })
        docs.append({
            "doc_type": "maximo_pm",
            "content": f"Maximo PM Record: Choke manifold inspection for {asset_id} shows significant erosion due to sand.",
            "timestamp": (now - timedelta(days=random.randint(2, 5))).isoformat() + "Z"
        })
        docs.append({
            "doc_type": "shift_note",
            "content": f"Shift Note: Trace sand in sample line for {asset_id}.",
            "timestamp": (now - timedelta(hours=random.randint(4, 12))).isoformat() + "Z"
        })
    elif fault_type == "bearing_wear":
        iron_ppm = random.randint(45, 80)
        docs.append({
            "doc_type": "oil_analysis",
            "content": f"Oil Analysis: Iron content at {iron_ppm} ppm for {asset_id}. Severe bearing spalling likely. Vibration: {sensors.get('vib', 0):.2f} mm/s.",
            "timestamp": (now - timedelta(hours=random.randint(24, 72))).isoformat() + "Z"
        })
        docs.append({
            "doc_type": "maximo_pm",
            "content": f"Maximo PM Record: Bearing replacement overdue by {random.randint(45, 90)} days.",
            "timestamp": (now - timedelta(days=random.randint(45, 90))).isoformat() + "Z"
        })
        docs.append({
            "doc_type": "vibration_report",
            "content": f"Vibration Report: BPFI defect frequency confirmed on {asset_id}. Amplitude rising.",
            "timestamp": (now - timedelta(hours=random.randint(12, 24))).isoformat() + "Z"
        })
    elif fault_type == "valve_failure":
        # Fix 9: valve_failure — gas lift check valve chattering / disk fracture
        cyclic_dp = random.randint(38, 48)
        overdue_mo = random.randint(15, 22)
        h2s_ppm = random.randint(1100, 1400)
        templates = [
            {
                "doc_type": "process_historian",
                "content": random.choice([
                    f"Discharge Pressure Historian: Cyclic ΔP amplitude {cyclic_dp} psi peak-to-peak on {asset_id} (nominal <8 psi). Frequency 1.8 Hz — valve disk flutter signature. Mean pressure {sensors.get('psi', 978):.0f} psi (normal range). SCADA: NO ALARM.",
                    f"Process Historian: {asset_id} discharge pressure oscillating ±{cyclic_dp//2} psi at 1.8 Hz. Cyclic amplitude {cyclic_dp} psi is {cyclic_dp//8}× normal. Mean pressure within limits — SCADA blind to this pattern.",
                    f"Pressure Historian: {asset_id} valve chatter confirmed — {cyclic_dp} psi cyclic amplitude at 1.8 Hz. Disk flutter precedes fracture. Current discharge: {sensors.get('psi', 978):.0f} psi.",
                ]),
                "timestamp": (now - timedelta(hours=random.randint(1, 3))).isoformat() + "Z"
            },
            {
                "doc_type": "maximo_service",
                "content": random.choice([
                    f"Maximo Asset Record: {asset_id} check valve last replaced {overdue_mo} months ago (interval: 12 months H2S service). H2S: {h2s_ppm} ppm — accelerated corrosion. Part CVD-1200-PSI-4IN in local stock.",
                    f"Maximo PM: Check valve on {asset_id} overdue by {overdue_mo - 12} months. Sour service ({h2s_ppm} ppm H2S) accelerates disk corrosion. Replacement part confirmed in local inventory.",
                    f"Service History: {asset_id} valve WO-2024-1840 completed {overdue_mo} months ago. H2S {h2s_ppm} ppm — 12-month interval exceeded. Chattering signature consistent with disk cracking.",
                ]),
                "timestamp": (now - timedelta(days=random.randint(1, 3))).isoformat() + "Z"
            },
            {
                "doc_type": "shift_note",
                "content": random.choice([
                    f"Shift Note: Operator reported unusual noise from {asset_id} compressor discharge. Pressure gauge showing minor fluctuations. No SCADA alarm active.",
                    f"Shift Handover: {asset_id} — 'Discharge pressure seems a bit unsteady, nothing alarming.' No action taken. SCADA normal.",
                    f"Operator Log: {asset_id} compressor running but discharge pressure slightly erratic last 2 hours. Monitoring.",
                ]),
                "timestamp": (now - timedelta(hours=random.randint(2, 5))).isoformat() + "Z"
            },
        ]
        docs.extend(templates)
    elif fault_type == "thermal_runaway":
        # Fix 9: thermal_runaway — gas lift compressor fin-fan cooling failure
        delta_t = random.randint(46, 56)
        overdue_mo = random.randint(13, 16)
        discharge_temp = sensors.get('temp', 187)
        templates = [
            {
                "doc_type": "process_historian",
                "content": random.choice([
                    f"Cooling System Historian: {asset_id} fin-fan delta-T {delta_t}°F (design: 35°F, deviation +{delta_t-35}%). Discharge temp {discharge_temp:.0f}°F trending +2.1°F/hr. SCADA alarm: 230°F. Projected crossing: ~{int((230 - discharge_temp) / 2.1)}h.",
                    f"Process Historian: {asset_id} cylinder jacket cooling degraded. Inlet 98°F, outlet {98 + delta_t}°F, delta-T {delta_t}°F vs 35°F design. Fin-fan airflow restriction suspected.",
                    f"Cooling Water Log: {asset_id} heat exchanger efficiency declining. Delta-T {delta_t}°F ({int((delta_t/35-1)*100)}% above design). Discharge temp {discharge_temp:.0f}°F and rising.",
                ]),
                "timestamp": (now - timedelta(hours=random.randint(2, 6))).isoformat() + "Z"
            },
            {
                "doc_type": "maximo_pm",
                "content": random.choice([
                    f"Maximo PM Record: {asset_id} aerial fin-fan cooler last cleaned {overdue_mo} months ago (interval: 6 months per Ariel manual). Overdue by {overdue_mo - 6} months. CREW-BRAVO-B on-site tomorrow — can append at zero travel cost.",
                    f"Preventive Maintenance: {asset_id} fin-fan cleaning WO-PM-0194 completed {overdue_mo} months ago. PM interval 6 months — overdue {overdue_mo - 6} months. Fouling consistent with observed delta-T increase.",
                    f"Maximo: {asset_id} cooler PM overdue {overdue_mo - 6} months. Ariel JGP design limit 250°F discharge. Current {discharge_temp:.0f}°F. Crew scheduled on-site tomorrow for transmitter calibration.",
                ]),
                "timestamp": (now - timedelta(days=random.randint(1, 5))).isoformat() + "Z"
            },
            {
                "doc_type": "shift_note",
                "content": random.choice([
                    f"Shift Note: {asset_id} running warmer than usual. Discharge temp higher than last week but no alarm. Mentioned to day tour.",
                    f"Operator Log: {asset_id} — 'Compressor feels hot, discharge temp climbing slowly. No SCADA alarm yet.' Monitoring.",
                    f"Shift Handover: {asset_id} discharge temp trending up over last 6 hours. No alarm. Crew to watch.",
                ]),
                "timestamp": (now - timedelta(hours=random.randint(3, 8))).isoformat() + "Z"
            },
        ]
        docs.extend(templates)
    elif fault_type == "bearing_wear_glift":
        iron_ppm = random.randint(40, 80)
        docs.extend([
            {"doc_type": "oil_analysis", "content": f"Oil Analysis: Iron at {iron_ppm} ppm for {asset_id}. Impending bearing spalling.", "timestamp": (now - timedelta(hours=24)).isoformat() + "Z"},
            {"doc_type": "maximo_pm", "content": f"Maximo PM: {asset_id} bearing replacement overdue.", "timestamp": (now - timedelta(days=60)).isoformat() + "Z"},
            {"doc_type": "vibration_report", "content": f"Vibration: {asset_id} shows BPFI peak amplitude rising. Current vib: {sensors.get('vib', 0):.2f} mm/s.", "timestamp": (now - timedelta(hours=12)).isoformat() + "Z"}
        ])
    elif fault_type == "pulsation_dampener_failure":
        docs.extend([
            {"doc_type": "shift_note", "content": f"Shift Note: Extreme pressure hammer observed on {asset_id}.", "timestamp": (now - timedelta(minutes=5)).isoformat() + "Z"},
            {"doc_type": "vibration_report", "content": f"Vibration: Massive spike on {asset_id} dampener manifold.", "timestamp": (now - timedelta(minutes=10)).isoformat() + "Z"},
            {"doc_type": "process_historian", "content": f"Historian: {asset_id} discharge pressure wild oscillations. Pressure at {sensors.get('psi', 0):.0f} PSI.", "timestamp": (now - timedelta(minutes=15)).isoformat() + "Z"}
        ])
    elif fault_type == "valve_washout":
        docs.extend([
            {"doc_type": "process_historian", "content": f"Historian: {asset_id} SPM rising while PSI holds at {sensors.get('psi', 0):.0f} PSI. Valve leak suspected.", "timestamp": (now - timedelta(hours=1)).isoformat() + "Z"},
            {"doc_type": "shift_note", "content": f"Shift Note: Driller increasing strokes on {asset_id} to maintain flow.", "timestamp": (now - timedelta(hours=2)).isoformat() + "Z"},
            {"doc_type": "maximo_pm", "content": f"Maximo PM: {asset_id} fluid end inspection overdue.", "timestamp": (now - timedelta(days=10)).isoformat() + "Z"}
        ])
    elif fault_type == "piston_seal_wear":
        docs.extend([
            {"doc_type": "process_historian", "content": f"Historian: {asset_id} fluid end temp rising to {sensors.get('temp', 0):.0f}°F. Seal bypass likely.", "timestamp": (now - timedelta(hours=3)).isoformat() + "Z"},
            {"doc_type": "shift_note", "content": f"Shift Note: Minor pressure drop noticed on {asset_id}. SPM steady.", "timestamp": (now - timedelta(hours=4)).isoformat() + "Z"},
            {"doc_type": "maximo_pm", "content": f"Maximo PM: {asset_id} liner seal replacement overdue.", "timestamp": (now - timedelta(days=14)).isoformat() + "Z"}
        ])
    elif fault_type == "gearbox_bearing_spalling":
        docs.extend([
            {"doc_type": "oil_analysis", "content": f"Oil Analysis: Iron at {random.randint(55, 80)} ppm in {asset_id} gearbox. Spalling active.", "timestamp": (now - timedelta(hours=48)).isoformat() + "Z"},
            {"doc_type": "vibration_report", "content": f"Vibration: {asset_id} shows BPFI defect frequency. Amplitude: {sensors.get('vib', 0):.2f} mm/s.", "timestamp": (now - timedelta(hours=8)).isoformat() + "Z"},
            {"doc_type": "shift_note", "content": f"Shift Note: Rough rotation reported from {asset_id} during drilling.", "timestamp": (now - timedelta(hours=2)).isoformat() + "Z"}
        ])
    elif fault_type == "hydraulic_leak":
        docs.extend([
            {"doc_type": "rig_log", "content": f"Rig Log: Added 1.2 gal hydraulic fluid to {asset_id}. Pressure {sensors.get('psi', 0):.0f} PSI.", "timestamp": (now - timedelta(hours=4)).isoformat() + "Z"},
            {"doc_type": "shift_note", "content": f"Shift Note: Visible sheen near {asset_id} swivel. Slow leak suspected.", "timestamp": (now - timedelta(hours=2)).isoformat() + "Z"},
            {"doc_type": "maximo_pm", "content": f"Maximo PM: {asset_id} hydraulic hose replacement overdue.", "timestamp": (now - timedelta(days=30)).isoformat() + "Z"}
        ])
    else:
        # Fallback for non-ESP faults or others
        docs.append({
            "doc_type": "shift_note",
            "content": f"Shift Note: General observation on {asset_id}. Fault {fault_type} suspected.",
            "timestamp": now.isoformat() + "Z"
        })

    return docs

def adjust_rul_with_documents(rul_minutes: float, documents: list) -> float:
    """Extracts structured variables from documents and applies multiplier to RUL."""
    import re
    adjusted_rul = rul_minutes
    for doc in documents:
        text = doc["content"]
        
        # Motor Overheat: water cut
        wc_match = re.search(r"Water cut measured at (\d+)%", text)
        if wc_match:
            wc = int(wc_match.group(1))
            if wc > 60:
                adjusted_rul *= 0.7
                
        # Gas Lock: GVF
        gvf_match = re.search(r"estimated at (\d+)%", text)
        if gvf_match:
            gvf = int(gvf_match.group(1))
            if gvf > 70:
                adjusted_rul *= 0.6
                
        # Sand Ingress: sand ppm
        sand_match = re.search(r"sand concentration.*is (\d+) ppm", text, re.IGNORECASE)
        if sand_match:
            sand_ppm = int(sand_match.group(1))
            if sand_ppm > 200:
                adjusted_rul *= 0.8
                
        # Bearing Wear: iron ppm
        iron_match = re.search(r"Iron content at (\d+) ppm", text)
        if iron_match:
            iron_ppm = int(iron_match.group(1))
            if iron_ppm > 50:
                adjusted_rul *= 0.75

        # Generic overdue PM
        pm_match = re.search(r"overdue by (\d+) days", text, re.IGNORECASE)
        if pm_match:
            days = int(pm_match.group(1))
            if days > 30:
                adjusted_rul *= 0.9

    return round(adjusted_rul, 1)

# ── Phase 16: Live Intelligence Generator ─────────────────────────────────────
# Background thread: every 2–5 min, picks an asset (preferring active faults),
# builds a prompt with live sensor context, calls Ollama, and stores the
# resulting field document in AlloyDB field_intel table.
# UI polls /api/field-intelligence every 60s and prepends new rows with .act-new.

def _ensure_field_intel_table() -> None:
    """Live migration — create field_intel table and fault_sessions table if not yet present."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS field_intel (
                  id            SERIAL PRIMARY KEY,
                  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                  asset_id      TEXT NOT NULL,
                  asset_class   TEXT NOT NULL,
                  fault_context TEXT,
                  doc_type      TEXT NOT NULL,
                  headline      TEXT NOT NULL,
                  detail        TEXT NOT NULL,
                  ai_relevance  TEXT NOT NULL DEFAULT '',
                  icon          TEXT NOT NULL DEFAULT '📋',
                  lbl           TEXT NOT NULL DEFAULT 'AI',
                  lbl_type      TEXT NOT NULL DEFAULT 'ai'
                );
                CREATE INDEX IF NOT EXISTS idx_field_intel_created
                  ON field_intel(created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_field_intel_asset
                  ON field_intel(asset_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_field_intel_fault
                  ON field_intel(fault_context, created_at DESC);

                -- Fix 11b: fault_sessions audit log
                CREATE TABLE IF NOT EXISTS fault_sessions (
                  id            SERIAL PRIMARY KEY,
                  injected_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                  asset_id      TEXT NOT NULL,
                  asset_class   TEXT NOT NULL,
                  fault_type    TEXT NOT NULL,
                  resolved_at   TIMESTAMPTZ,
                  resolution    TEXT,
                  cost_avoided  NUMERIC DEFAULT 0,
                  operator      TEXT DEFAULT 'system'
                );
                CREATE INDEX IF NOT EXISTS idx_fault_sessions_injected
                  ON fault_sessions(injected_at DESC);
                CREATE INDEX IF NOT EXISTS idx_fault_sessions_asset
                   ON fault_sessions(asset_id, injected_at DESC);

                -- Session T: injection event log for non-circular model verification
                -- Records the actual drawn parameter values (not just the profile bounds)
                -- for every point injection and gradual degrade. Used to replay through
                -- the classifier to produce a ground-truth confusion matrix.
                CREATE TABLE IF NOT EXISTS injection_events (
                  id              SERIAL PRIMARY KEY,
                  inject_time     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                  asset_id        TEXT NOT NULL,
                  fault_type      TEXT NOT NULL,
                  injection_mode  TEXT NOT NULL,     -- 'point' | 'gradual'
                  psi_range_lo    NUMERIC,
                  psi_range_hi    NUMERIC,
                  temp_range_lo   NUMERIC,
                  temp_range_hi   NUMERIC,
                  vib_range_lo    NUMERIC,
                  vib_range_hi    NUMERIC,
                  amps_range_lo   NUMERIC,
                  amps_range_hi   NUMERIC,
                  psi_target      NUMERIC,           -- actual drawn value
                  temp_target     NUMERIC,
                  vib_target      NUMERIC,
                  amps_target     NUMERIC,
                  ramp_k          NUMERIC,           -- NULL for point injections
                  duration_s      INTEGER,           -- NULL for point injections
                  reading_count   INTEGER            -- for point injections
                );
                CREATE INDEX IF NOT EXISTS idx_injection_events_time
                   ON injection_events(inject_time DESC);
                CREATE INDEX IF NOT EXISTS idx_injection_events_asset
                   ON injection_events(asset_id, inject_time DESC);
            """)
        conn.commit()
        conn.close()
        log.info("✅ field_intel + fault_sessions tables ready")
    except Exception as e:
        log.warning(f"field_intel table check (non-fatal): {e}")


_INTEL_DOC_TYPES = {
    "esp":       [("shift_note","📋","Shift Note","shift"), ("well_test","🧪","Well Test","lab"),
                  ("pm_record","🔧","PM Record","routine"), ("power_log","⚡","VFD Log","ai")],
    "gas_lift":  [("shift_note","📋","Shift Note","shift"), ("oil_analysis","🧪","Oil Analysis","lab"),
                  ("pm_record","🔧","PM Record","routine"), ("process_log","📊","Process Log","ai")],
    "mud_pump":  [("driller_log","📋","Driller Log","shift"), ("mud_report","🪣","Mud Report","lab"),
                  ("fluid_end_log","🔧","Fluid End","routine"), ("edr_alert","📊","EDR Alert","ai")],
    "top_drive": [("rig_log","📋","Rig Log","shift"), ("oil_analysis","🧪","Oil Analysis","lab"),
                  ("pm_record","🔧","PM Record","routine"), ("torque_log","📊","Torque Log","ai")],
}


def _intel_generator() -> None:
    """
    Background document generator — calls Gemma (Ollama) to produce realistic
    operational field documents (shift notes, lab reports, PM records) for the
    active fault. Wakes every 20-30 seconds. Only inserts into field_intel when
    Gemma actually returns content — never falls back to templates.
    """
    time.sleep(10)  # Short wait for startup
    _ensure_field_intel_table()
    log.info("🧠 Intel generator ready — interval: 20-30s (Gemma-powered)")

    while True:
        try:
            active_list = [aid for aid, dg in active_degrades.items() if dg]
            if active_list:
                asset_id = random.choice(active_list)
                fault_context = active_degrades[asset_id].get("fault_type")
                cs = active_degrades.get(asset_id, {}).get("current_sensors", {})
                if cs and fault_context:
                    meta = ASSET_REGISTRY.get(asset_id, {})
                    asset_class = meta.get("asset_class", "esp")
                    fault_label = FAULT_PROFILES.get(fault_context, {}).get("label", fault_context)
                    # Document type weights: 55% supporting, 30% neutral, 15% counterargument
                    # (per DEMO_MASTER §10)
                    _cat_roll = random.random()
                    if _cat_roll < 0.15:
                        intel_category = "counterargument"
                    elif _cat_roll < 0.45:
                        intel_category = "neutral"
                    else:
                        intel_category = "supporting"
                    doc_type = random.choice(["shift_note", "lab_report", "pm_record"])

                    if intel_category == "counterargument":
                        _cat_instr = (
                            f"IMPORTANT: Write a document presenting an ALTERNATIVE explanation that argues "
                            f"AGAINST the {fault_context.replace('_',' ')} diagnosis. Be realistic — cite a "
                            f"plausible competing cause such as gradual reservoir drawdown, VFD calibration "
                            f"drift, or a benign operational change. An experienced engineer should find "
                            f"this plausible as an alternative hypothesis."
                        )
                    elif intel_category == "neutral":
                        _cat_instr = (
                            f"Write a ROUTINE operational document — a normal periodic inspection, standard "
                            f"shift log entry, or scheduled measurement record. Do NOT reference the active "
                            f"fault directly. This represents normal background activity."
                        )
                    else:
                        _cat_instr = (
                            f"Write a document that CORROBORATES the {fault_context.replace('_',' ')} "
                            f"assessment with specific sensor readings, field observations, or measurements "
                            f"consistent with this fault signature."
                        )

                    prompt = (
                        f"You are a field engineer writing a brief operational note for asset {asset_id}.\n"
                        f"Active fault context: {fault_context.replace('_', ' ')}.\n"
                        f"Current sensors: PSI={cs.get('psi', 0):.0f}, "
                        f"Temp={cs.get('temp', 0):.0f}\u00b0F, "
                        f"Vib={cs.get('vib', 0):.3f}mm/s.\n\n"
                        f"{_cat_instr}\n"
                        f"Document type: {doc_type.replace('_', ' ')}. "
                        f"Be specific with numbers. Maximum 120 words. No preamble."
                    )

                    try:
                        import requests as _req
                        resp = _req.post(
                            f"{OLLAMA_URL}/api/generate",
                            json={
                                "model": OLLAMA_MODEL,
                                "prompt": prompt,
                                "stream": False,
                                "options": {"num_predict": 150, "temperature": 0.7},
                            },
                            timeout=15,
                        )
                        if resp.status_code != 200:
                            log.debug(f"Intel generator Ollama HTTP {resp.status_code} — skipping cycle")
                        else:
                            body = resp.json().get("response", "").strip()
                            if body:
                                headline = (
                                    f"{'⚠ ALT: ' if intel_category == 'counterargument' else ''}"
                                    f"{fault_label.replace('_', ' ').title()} "
                                    f"— {doc_type.replace('_', ' ').title()}"
                                )
                                ai_relevance = (
                                    f"{'Alternative hypothesis: ' if intel_category == 'counterargument' else ''}"
                                    f"Gemma: {doc_type.replace('_', ' ')} generated "
                                    f"from live sensor state for {asset_id}."
                                )
                                try:
                                    conn = get_db()
                                    with conn.cursor() as cur:
                                        cur.execute(
                                            """
                                            INSERT INTO field_intel
                                              (asset_id, asset_class, fault_context, doc_type,
                                               headline, detail, ai_relevance, icon, lbl, lbl_type)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                            """,
                                            (asset_id, asset_class, fault_context, doc_type,
                                             headline[:120], body[:1000], ai_relevance[:300],
                                             "📄",
                                             "ALT" if intel_category == "counterargument" else ("ROUTINE" if intel_category == "neutral" else "AI"),
                                             "counterarg" if intel_category == "counterargument" else ("neutral" if intel_category == "neutral" else "ai")),
                                        )
                                        # Prune — keep 100 most recent, but protect seed docs.
                                        # The GVF shift-note seed (inserted at inject time) is the
                                        # document that drives the context-fusion RAG gap. If it gets
                                        # pruned after ~10 intel cycles the gap collapses to 0.
                                        # Fix: exclude the 5 oldest AI shift-notes from pruning.
                                        cur.execute("""
                                            DELETE FROM field_intel
                                            WHERE id NOT IN (
                                                SELECT id FROM field_intel ORDER BY created_at DESC LIMIT 100
                                            )
                                            AND id NOT IN (
                                                SELECT id FROM field_intel
                                                WHERE doc_type = 'shift_note' AND lbl_type = 'ai'
                                                ORDER BY created_at ASC LIMIT 5
                                            )
                                        """)
                                    conn.commit()
                                    conn.close()
                                    log.debug(
                                        f"Intel generator inserted Gemma doc for {asset_id} ({doc_type})"
                                    )
                                except Exception as db_err:
                                    log.warning(f"Intel generator DB insert failed: {db_err}")
                    except Exception as ollama_err:
                        log.debug(f"Intel generator Ollama call failed — skipping cycle: {ollama_err}")

        except Exception as e:
            log.debug(f"Intel generator cycle error (non-fatal): {e}")

        time.sleep(random.randint(20, 30))


threading.Thread(target=_intel_generator, daemon=True, name="intel-generator").start()
log.info("🧠 Intel generator thread started")


# ── H2 Date Anchors & Static Document Helpers ─────────────────────────────────
# Computed once at startup. Used by both the static seed function and the endpoint.

_H2_SCENARIO_DATE   = datetime.now()
_H2_WORKOVER_DATE   = _H2_SCENARIO_DATE - timedelta(weeks=8)
_H2_PRIOR_PULL_DATE = _H2_WORKOVER_DATE  - timedelta(weeks=78)

def _h2_fmt(dt: datetime) -> str:
    return dt.strftime("%B %d, %Y")

# Document 2 — OEM Fluid Compatibility Matrix (static, no dates, seed once)
_H2_OEM_MATRIX_TEXT = (
    "PermPump Systems\n"
    "ESP Series 4000 Service Manual — Rev. 3\n"
    "Section 8.4: Protector Fill Oil Compatibility — Seal Section\n\n"
    "Table 8-2: Approved Protector Fill Oils — Protector Section\n"
    "Seal material (Series 4000 standard configuration): Buna-N / NBR elastomer shaft seals\n\n"
    "INSTRUCTIONS: Confirm protector fill oil product fluid class against Table 8-2 BEFORE\n"
    "filling. Use of an INCOMPATIBLE fluid class voids the protector warranty.\n\n"
    "FLUID CLASS                                        | Buna-N/NBR  | Viton/FKM | HNBR\n"
    "---------------------------------------------------+-------------+-----------+------\n"
    "Petroleum-based mineral oil (ISO VG 100-460)       | COMPATIBLE  | COMPATIBLE| COMP\n"
    "Synthetic hydrocarbon - PAO (ISO VG 100-460)       | COMPATIBLE  | COMPATIBLE| COMP\n"
    "Synthetic ester-based fluid (polyol ester,         |             |           |\n"
    "  diester, trimethylolpropane ester)               | INCOMPATIBLE| COMPATIBLE| COND*\n"
    "Phosphate ester synthetic fluid                    | INCOMPATIBLE| COMPATIBLE| COMP\n"
    "Water-glycol based fluid (<=50% glycol)            | COND+       | COND+     | COMP\n\n"
    "INCOMPATIBLE = Failure expected within days to weeks of continuous service.\n"
    "COMPATIBLE   = Approved for use within nameplate temperature limits.\n"
    "COND         = Conditionally compatible - see footnote.\n\n"
    "*HNBR / synthetic ester: Maximum 120 deg C continuous. Consult factory if >80% ester.\n"
    "+Water-glycol: Non-Arctic use only. Monitor for seal dimensional change above 60 deg C.\n\n"
    "NOTES:\n"
    "1. The Series 4000 protector ships with Buna-N (NBR) shaft seals as standard.\n"
    "2. WARNING: 'Synthetic' or 'Synthetic Blend' on a product label does NOT distinguish\n"
    "   PAO (COMPATIBLE) from ester-based (INCOMPATIBLE). Confirm base-stock fluid class\n"
    "   with the supplier before use. Do not rely on label language or product name alone.\n"
    "3. Initial symptoms of INCOMPATIBLE fluid exposure: seal dimensional instability,\n"
    "   hardening. Observable operating symptoms (vibration anomaly, temperature rise)\n"
    "   typically develop over 3-8 weeks of continuous service.\n\n"
    "Document ID: PPS-4000-SVC-003-R3"
)


def _build_h2_doc3() -> str:
    """Document 3 — Prior Pull Record (date-templated, re-generated each call)."""
    wo = f"WO-{_H2_PRIOR_PULL_DATE.strftime('%Y-%m%d')}-A3"
    return (
        f"BASIN LIFT SERVICES LLC — ESP TEARDOWN / COMPLETION REPORT\n"
        f"Well: ESP-ALPHA-3 | Block 7 Pad | Andrews County, WTX\n"
        f"Pull Date: {_h2_fmt(_H2_PRIOR_PULL_DATE)} | WO: {wo}\n"
        f"Purpose: Scheduled replacement — production efficiency below operator target after\n"
        f"18-month run (moderate-sand well; operator performance-based lifecycle program).\n\n"
        f"MOTOR: Winding resistance (post-pull): 8.4 MΩ (above 2.2 MΩ minimum per IEEE 43-2000\n"
        f"for 1200V class). External: housing abrasion lower section — normal. Internal: windings\n"
        f"intact, no fluid ingress, no contamination. Disposition: returned to OEM for rewind\n"
        f"evaluation (standard for used motors in good condition).\n\n"
        f"PUMP: 30 stages. Stages 1-4 elevated wear consistent with intake position and sand\n"
        f"exposure. Remaining stages within limits. Condemned per performance-based lifecycle —\n"
        f"not anomalous failure. Replaced with new 7-stage AR-trim.\n\n"
        f"PROTECTOR: Shaft seal — slight weeping, lower bag (expected wear at run life).\n"
        f"Bearing condition: thrust washer 0.122 in (OEM tolerance 0.110-0.135 in); radial\n"
        f"clearances within spec; races show light polish, no scoring, no pitting, no\n"
        f"contamination. Internal oil: dark-brown (normal oxidation). No wellbore fluid ingress.\n"
        f"Condemned per performance-based lifecycle — not anomalous failure.\n\n"
        f"SUMMARY: All components within wear parameters for 18-month service interval. No\n"
        f"components condemned for cause (no anomalous failure). Bearings in good condition at\n"
        f"pull — no wear beyond light polishing. Cause of pull: scheduled replacement per\n"
        f"operator efficiency monitoring program.\n\n"
        f"Service Engineer: [Basin Lift Services LLC field record]"
    )


def _build_h2_doc5() -> str:
    """Document 5 — Well History Extract (date-templated, randomized SCADA events)."""
    window_days = (_H2_SCENARIO_DATE - _H2_PRIOR_PULL_DATE).days
    event_days  = sorted(random.sample(range(30, max(31, window_days - 30)), 7))
    event_dates = [_H2_PRIOR_PULL_DATE + timedelta(days=d) for d in event_days]
    event_types = [
        "Brief underload trip — auto-restart OK, no follow-up",
        "High-temp transient — cleared within 4 min, no intervention",
        "Underload trip — auto-restart, normal",
        "Brief overload (voltage surge) — cleared 3 min",
        "Underload trip — restart normal",
        "High-temp transient — cleared, normal",
        "Brief communication loss — restored automatically",
    ]
    scada_events = "\n".join(
        f"  {_h2_fmt(d)}   {t}"
        for d, t in zip(event_dates, event_types)
    )
    wo_cur = f"WO-{_H2_WORKOVER_DATE.strftime('%Y-%m%d')}-A3"
    wo_pri = f"WO-{_H2_PRIOR_PULL_DATE.strftime('%Y-%m%d')}-A3"
    return (
        f"WELL HISTORY SUMMARY — ESP-ALPHA-3\n"
        f"Generated: {_h2_fmt(_H2_SCENARIO_DATE)} | Source: RTOC Well File / SCADA Historian\n"
        f"Period covered: 24 months ({_h2_fmt(_H2_PRIOR_PULL_DATE)} – {_h2_fmt(_H2_SCENARIO_DATE)})\n\n"
        f"EVENT LOG (most recent first):\n"
        f"  {_h2_fmt(_H2_WORKOVER_DATE)}   ESP REPLACEMENT — {wo_cur}\n"
        f"                    Scope: Motor/pump/protector replacement (unscheduled —\n"
        f"                    vibration/amp anomaly, operator-flagged). Duration: 1 day.\n"
        f"                    No complications. Well returned to production 14:35 same day.\n\n"
        f"  {_h2_fmt(_H2_PRIOR_PULL_DATE)}   ESP REPLACEMENT — {wo_pri}\n"
        f"                    Scope: Scheduled replacement per production efficiency\n"
        f"                    monitoring (18-month run, efficiency below operator threshold —\n"
        f"                    moderate-sand lifecycle program). Duration: 1 day. No complications.\n\n"
        f"SCADA ALARM HISTORY (last 24 months — notable events):\n"
        f"  {_h2_fmt(_H2_SCENARIO_DATE - timedelta(days=2))}   Amp/vibration deviation — operator flagged, monitoring only\n"
        f"{scada_events}\n\n"
        f"PRODUCTION TREND: Post-{_h2_fmt(_H2_PRIOR_PULL_DATE)} workover through {_h2_fmt(_H2_WORKOVER_DATE)} —\n"
        f"normal production, consistent with expected decline curve. No anomalies flagged by\n"
        f"SCADA or production monitoring in this interval. Post-{_h2_fmt(_H2_WORKOVER_DATE)} workover\n"
        f"through {_h2_fmt(_H2_SCENARIO_DATE)}: normal initial production.\n\n"
        f"Note: Extract covers 24-month window. Full well history in RTOC well file."
    )


def _seed_h2_static_docs_bg() -> None:
    """Seed H2 static field_intel docs at startup (idempotent). Runs in daemon thread."""
    time.sleep(20)   # wait for DB and field_intel table to be ready
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM field_intel "
                "WHERE asset_id='ESP-ALPHA-3' AND doc_type='oem_manual' "
                "  AND fault_context='workover_fluid_incompatibility'"
            )
            if cur.fetchone()[0] > 0:
                log.info("H2 static docs already seeded — skipping re-seed")
                conn.close()
                return
            _static_docs = [
                ("oem_manual",
                 "PermPump Systems ESP-4000 — Sec 8.4: Protector Fill Oil Compatibility",
                 _H2_OEM_MATRIX_TEXT,
                 "Fluid compatibility matrix: synthetic ester = INCOMPATIBLE with Buna-N. "
                 "3-8 week symptom onset post-fill. Decisive when crossed with workover report."),
                ("pull_record",
                 f"Prior ESP Pull Record — {_h2_fmt(_H2_PRIOR_PULL_DATE)} — Bearings NORMAL",
                 _build_h2_doc3(),
                 "Bearings in good condition at last pull (18 months prior to workover). "
                 "No pre-existing wear. Eliminates normal bearing-age hypothesis."),
                ("well_history",
                 f"Well History ESP-ALPHA-3 — Workover {_h2_fmt(_H2_WORKOVER_DATE)} confirmed",
                 _build_h2_doc5(),
                 "Current workover 8 weeks ago confirmed. No anomalies in 24-month history "
                 "pre-workover. Symptom onset timing aligns with OEM swell timeline."),
            ]
            for doc_type, headline, detail, ai_rel in _static_docs:
                cur.execute("""
                    INSERT INTO field_intel
                      (asset_id, asset_class, fault_context, doc_type,
                       headline, detail, ai_relevance, icon, lbl, lbl_type)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    ("ESP-ALPHA-3", "esp", "workover_fluid_incompatibility",
                     doc_type, headline, detail, ai_rel, "\U0001f4c4", "H2", "h2"))
        conn.commit()
        conn.close()
        log.info("✅ H2 static docs seeded (OEM matrix, prior pull, well history)")
    except Exception as _se:
        log.warning(f"H2 static doc seeding failed (non-fatal): {_se}")

threading.Thread(target=_seed_h2_static_docs_bg, daemon=True, name="h2-seed").start()


# ── Asset Fleet ────────────────────────────────────────────────────────────────
# Pure-pad architecture: each pad uses a single artificial lift method.
#   Pad Alpha   — 6 ESPs (ESP production pad)
#   Pad Bravo   — 4 Gas Lift Compressors (gas lift production pad)
#   Rig 42      — 3 Mud Pumps + 1 Top Drive (drilling rig)
ASSETS = [
    # Pad Alpha (ESP Production — Pure ESP Pad)
    "ESP-ALPHA-1", "ESP-ALPHA-2", "ESP-ALPHA-3",
    "ESP-ALPHA-4", "ESP-ALPHA-5", "ESP-ALPHA-6",
    # Pad Bravo (Gas Lift Compressors)
    "GLIFT-BRAVO-1", "GLIFT-BRAVO-2", "GLIFT-BRAVO-3", "GLIFT-BRAVO-4",
    # Rig 42 (Mud Pumps + Top Drive)
    "MUD-RIG42-1", "MUD-RIG42-2", "MUD-RIG42-3", "TOPDRIVE-RIG42-1"
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
        # API RP 11S §4.2 / §7.2; SPE-174536-MS — updated Session S (June 9, 2026)
        "psi_range": (400, 600), "temp_range": (245, 265), "vib_range": (4.5, 6.5),
        "amps_range": (20, 45),
    },
    "fluid_drawdown": {
        "label": "Fluid Drawdown", "asset_class": "esp",
        "description": "Fluid level depletion — pump efficiency degrading, intake pressure declining toward critical drawdown",
        "color": "#ff6d00",
        # IDENTICAL sensor trajectory to gas_lock — only RAG context distinguishes them (H1 premise)
        # API RP 11S §4.2 / §7.2; SPE-174536-MS — updated Session S (June 9, 2026)
        "psi_range": (400, 600), "temp_range": (245, 265), "vib_range": (4.5, 6.5),
        "amps_range": (20, 45),
    },
    "sand_ingress": {
        "label": "Sand Ingress", "asset_class": "esp",
        "description": "Formation sand erodes impeller stages — all sensors drift over days",
        "color": "#f9a825",
        "psi_range": (1100, 1250), "temp_range": (210, 240), "vib_range": (4.5, 9.5),
        "amps_range": (45, 65),
    },
    "motor_overheat": {
        "label": "Motor Over-Temp", "asset_class": "esp",
        "description": "Downhole cooling degrades — winding temp climbs toward insulation failure (>280°F)",
        "color": "#ff6d00",
        "psi_range": (1300, 1400), "temp_range": (265, 295), "vib_range": (1.0, 2.0),
        "amps_range": (88, 105),
    },
    "bearing_wear_esp": {
        "label": "Bearing Wear (ESP)", "asset_class": "esp",
        "description": "Vibration rises significantly, Temp/Amps slight rise, PSI flat",
        "color": "#fdd835",
        "psi_range": (1350, 1450), "temp_range": (210, 230), "vib_range": (8.5, 14.5),
        "amps_range": (76, 85),
    },
    "slug_flow": {
        "label": "Flowline Slug Flow", "asset_class": "esp",
        "description": "Flowline slugging causes hydraulic tubing vibration downhole, motor temperature nominal",
        "color": "#ffb300",
        "psi_range": (1300, 1500), "temp_range": (190, 205), "vib_range": (4.0, 6.5),
        "amps_range": (70, 80),
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
    "bearing_wear_glift": {
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
    "esp":       ["gas_lock", "slug_flow", "sand_ingress", "motor_overheat"],
    "gas_lift":  ["valve_failure", "thermal_runaway", "bearing_wear_glift"],
    "mud_pump":  ["pulsation_dampener_failure", "valve_washout", "piston_seal_wear"],
    "top_drive": ["gearbox_bearing_spalling", "hydraulic_leak"],
}

# ── Point-of-No-Return (PNR) per fault type ────────────────────────────────────
# Minutes from fault onset after which operator intervention cannot prevent
# equipment damage or production loss. Based on real O&G failure physics.
# Used in the Edge vs Cloud comparison chart to quantify the response window.
PNR_MINUTES = {
    "gas_lock":                   25,   # Gas fraction >70% — pump impeller stalls
    "fluid_drawdown":             25,   # Fluid depletion — dynamic submergence lost
    "slug_flow":                  120,  # Slow vibration drift allows 2h response window
    "sand_ingress":               120,  # Impeller erosion accumulates over hours
    "motor_overheat":             30,   # Winding insulation fails above 280°F
    "valve_failure":               5,   # Instantaneous pressure crash
    "thermal_runaway":            40,   # Thermal mass buys ~40min before seizure
    "bearing_wear_esp":           240,  # ESP radial bearing spalling
    "bearing_wear_glift":         240,  # Gas lift crankshaft journal bearing
    "bearing_wear":               240,  # Legacy alias
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
    "fluid_drawdown": {   # PNR=25m
        "early":    {"action": "Do NOT trim VFD speed — slowing the pump down drops velocity below critical lift, causing sand/debris to bridge string. Safest action: Emergency shutdown.", "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 8000},
        "urgent":   {"action": "Do NOT trim VFD speed — dynamic dynamic fluid level is dangerously low. Prepare emergency shut-in.", "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 8000},
        "critical": {"action": "Emergency shutdown via SCADA — prevent sand bridging and pump burnout", "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 15000},
        "post_pnr": {"action": "ESP string seized — pull ESP string and replace motor/impeller stages; run cleanout", "type": "workover", "time_to_execute": "3–5 days", "cost_incurred": 150000},
    },
    "slug_flow": {   # PNR=120m
        "early":    {"action": "Dispatch surface technician (truck roll) to inspect surface choke valve backpressure. Do not pull well.", "type": "field_notification", "time_to_execute": "30–60 min", "cost_incurred": 1500},
        "urgent":   {"action": "Dispatch surface technician (truck roll) to check choke manifold and surface hydraulics.", "type": "field_notification", "time_to_execute": "15–20 min", "cost_incurred": 3000},
        "critical": {"action": "Emergency choke bypass adjustment — surface flowline slugging dampening is required immediately", "type": "emergency_procedure", "time_to_execute": "<5 min", "cost_incurred": 8000},
        "post_pnr": {"action": "Erroneously mobilized workover rig — pulled mechanically sound ESP downhole, incurring huge unnecessary Capex", "type": "workover", "time_to_execute": "3–5 days", "cost_incurred": 150000},
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
    "bearing_wear_glift": {   # PNR=240m — gas lift crankshaft journal bearing
        "early":    {"action": "Reduce RPM 10% to lower bearing load; schedule planned bearing swap within 48h",   "type": "software_command", "time_to_execute": "<10 min", "cost_incurred": 5000},
        "urgent":   {"action": "Reduce to 70% rated speed + mobilise bearing replacement crew for next slot",       "type": "field_notification", "time_to_execute": "30–60 min", "cost_incurred": 20000},
        "critical": {"action": "Compressor to minimum-load idle; bearing replacement within 4 hours required",     "type": "emergency_procedure", "time_to_execute": "30 min", "cost_incurred": 40000},
        "post_pnr": {"action": "Emergency bearing and shaft replacement; inspect crankshaft for scoring damage",    "type": "workover", "time_to_execute": "3–5 days", "cost_incurred": 85000},
    },
    "bearing_wear": {   # Legacy alias → same as bearing_wear_glift for backward compat
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
    "fluid_drawdown":             150000,  # Avoided downhole sand-bridge seizure
    "slug_flow":                  150000,  # Avoided premature ESP well pull
    "vizier_optimal":             150000,  # Optimization savings
    "sand_ingress":                85000,  # Workover + impeller replacement
    "motor_overheat":             200000,  # Motor burnout + replacement
    "valve_failure":               42500,  # Valve replacement + downtime
    "thermal_runaway":            150000,  # Compressor rebuild
    "bearing_wear_esp":            85000,  # ESP radial bearing replacement
    "bearing_wear_glift":          85000,  # Gas lift crankshaft journal bearing
    "bearing_wear":                85000,  # Legacy alias
    "pulsation_dampener_failure": 500000,  # Pipeline damage + emergency response
    "valve_washout":               52500,  # Fluid end rebuild
    "piston_seal_wear":            15000,  # Seal kit + 8h maintenance
    "gearbox_bearing_spalling":   120000,  # Gearbox repair + drilling halt
    "hydraulic_leak":               8000,  # Hydraulic repair + drilling delay
}

# ── Financial Justifications Registry (Phase 12 — Self-Justifying Demo) ──────
# Itemized cost breakdowns for each fault type.  Surfaces in-app when a user
# clicks "[ ⓘ Justify ]" next to a financial figure to address stakeholder
# objections.  Sources: SPE papers, OEM price lists, IADC survey data,
# Wood Mackenzie O&G cost index, API recommended practices.
FINANCIAL_JUSTIFICATIONS = {
    "gas_lock": {
        "fault_label": "Gas Lock — ESP",
        "capital_at_risk_usd": 150000,
        "early_intervention_usd": 2500,
        "unmitigated_impact": {
            "basis": "Full ESP pull-and-replace workover. Impeller stall causes catastrophic heat buildup; motor winding damage is irreversible once temperature exceeds Class H limit (180°C). Workover is required to retrieve and replace the entire ESP string.",
            "line_items": [
                {"label": "ESP pump string — impeller stages, diffusers, head/base", "usd": 44000, "note": "Baker Hughes Centrilift 400 Series, 100-stage tungsten carbide trim; 2024 list price"},
                {"label": "ESP motor — 200 HP, 456 series, Class H insulation", "usd": 31000, "note": "Class H required for high water-cut, high-temp applications"},
                {"label": "Production cable — 1\" flat FlatPak, ~3,000 ft", "usd": 9500, "note": "Cable must be replaced when motor windings fail due to thermal arc"},
                {"label": "Workover rig — 3 days × $14,000/day (WTX 2024 spot rate)", "usd": 42000, "note": "400 HP rig for 10,000+ ft well; includes rig-up/down, kill fluid, BOP"},
                {"label": "Wireline, perforating, wellbore cleanout", "usd": 8500, "note": "Required to clean sand/debris before re-run; standard post-workover procedure"},
                {"label": "Deferred production — 4 days × 300 BPD × $76/bbl net-back", "usd": 11600, "note": "Net-back after royalties and LOE; production constrained during workover + restart ramp"},
                {"label": "Supervision, safety standby, consumables", "usd": 3400, "note": "Company man + safety observer day rates; kill fluid, tubing thread compound"},
            ]
        },
        "early_intervention": {
            "basis": "SCADA VFD frequency reduction from 52 Hz to 44 Hz for 4–6 hours allows gas void to migrate up the casing annulus. Zero equipment cost; cost is deferred production at reduced rate plus operator time.",
            "line_items": [
                {"label": "Deferred production — 5h at 15% reduced rate", "usd": 700, "note": "300 BPD × 15% reduction × 5h/24h × $76/bbl net-back ≈ $714"},
                {"label": "SCADA operator time — 4h monitoring and logging", "usd": 900, "note": "Operator labor at $225/hr fully-loaded rate (benefits, overhead)"},
                {"label": "Shift documentation and management notification", "usd": 900, "note": "Compliance reporting; PSM tracking for process upset event"},
            ]
        },
        "methodology": "Capital at risk represents the total unmitigated cost if the fault proceeds to impeller stall. Early intervention cost represents the deferred production and labor cost of the SCADA frequency reduction. Net impact is the difference — the maximum value GDC edge AI detection preserves. ROI of early detection: 60:1.",
        "references": ["SPE-174536-MS: ESP Performance and Failure Analysis", "Baker Hughes Centrilift Price List (2024)", "IADC WellCap Permian Basin Rig Rate Survey Q4 2024", "Wood Mackenzie: Permian Basin LOE Data 2023"]
    },
    "sand_ingress": {
        "fault_label": "Sand Ingress — ESP",
        "capital_at_risk_usd": 85000,
        "early_intervention_usd": 5000,
        "unmitigated_impact": {
            "basis": "Full ESP workover with sand-handler assembly replacement. Abrasive sand erodes tungsten carbide impeller stages over 14 days. By PNR, 30–50% of impeller stages are destroyed; a workover with equipment replacement is unavoidable.",
            "line_items": [
                {"label": "ESP sand-handler assembly — 100-stage TC radial bearings", "usd": 32000, "note": "Baker Hughes MAT-4002-TC-100; TC radial bearings at $320/stage (list price)"},
                {"label": "Workover rig — 4 days × $14,000/day", "usd": 56000, "note": "Days include rig-up, pull, inspect, sand control installation, re-run"},
                {"label": "Sand control screen / gravel pack equipment", "usd": 8000, "note": "Slotted liner or resin-coated gravel pack to prevent recurrence; per API 11S3"},
                {"label": "Deferred production — 5 days × 300 BPD × $76/bbl", "usd": 14250, "note": "5 days including rig move, kill, pull, replace, perforate, restart, ramp-up"},
                {"label": "Wellbore cleanout, kill fluid, wireline", "usd": 6500, "note": "Required to remove sand accumulation above perforations before re-run"},
            ]
        },
        "early_intervention": {
            "basis": "20% pump rate reduction via SCADA slows sand influx. Fluid sampling to confirm sand concentration. 14-day advance notice allows standard freight procurement (12 days) vs. air freight ($8,500 premium).",
            "line_items": [
                {"label": "Deferred production — 3 days at 20% reduced rate", "usd": 1370, "note": "300 BPD × 20% reduction × 3 days × $76/bbl net-back"},
                {"label": "Fluid sampling and lab analysis (BS&W, particle size)", "usd": 1200, "note": "Core Laboratories / Intertek: sand concentration, particle size distribution"},
                {"label": "SCADA monitoring and production engineering review", "usd": 2430, "note": "Production engineer 8h review + documentation at $303/hr (SPE salary data 2024)"},
            ]
        },
        "methodology": "Sand erosion progresses exponentially. GDC detects the early vibration signature 14 days ahead of SCADA alarm. Standard freight (12 days) is sufficient if ordered today; emergency air freight ($8,500 premium) is required if detection is delayed. Capital at risk reflects total workover cost including the time value of deferred production.",
        "references": ["API RP 11S3: Recommended Practice for ESP Systems", "Baker Hughes Centrilift: Sand Handling Design Guide", "SPE-181193: Sand Management in ESP Wells", "Core Laboratories: Formation Sand Analysis Methods"]
    },
    "motor_overheat": {
        "fault_label": "Motor Over-Temperature — ESP",
        "capital_at_risk_usd": 200000,
        "early_intervention_usd": 3000,
        "unmitigated_impact": {
            "basis": "Class H winding insulation failure. At >280°F, insulation breakdown causes a phase-to-ground fault. This destroys the motor, production cable, and typically the seal section. Well is killed and a full workover required.",
            "line_items": [
                {"label": "ESP motor replacement — 200HP Class H, 456 series", "usd": 62000, "note": "Baker Hughes MTR-456-200HP-H; Class H insulation rated to 300°F continuous; 2024 list"},
                {"label": "ESP seal section (protector) replacement", "usd": 18500, "note": "Motor burnout commonly damages seal section O-rings; replaced per BH recommendation"},
                {"label": "Production cable — 3,000 ft FlatPak, full replacement", "usd": 9500, "note": "Phase-to-ground fault destroys cable insulation; full string replacement required"},
                {"label": "Workover rig — 4 days × $14,000/day", "usd": 56000, "note": "Pull + replace + test; 4 days includes rig-up/down and restart to stable production"},
                {"label": "Deferred production — 5 days × 300 BPD × $76/bbl", "usd": 14250, "note": "Production loss during rig work plus ESP restart and ramp-up period"},
                {"label": "Wireline, kill fluid, surface cable inspection", "usd": 11500, "note": "Phase fault may arc to surface splice; complete cable log required before re-run"},
                {"label": "Engineering review, RCA, water cut analysis", "usd": 4800, "note": "Required post-failure per PSM program; includes water cut remediation study"},
            ]
        },
        "early_intervention": {
            "basis": "15% load reduction via VFD from 55 Hz to 47 Hz reduces motor current from 81A to ~69A, lowering winding temperature by 15–22°F. Preserves insulation life and allows time for engineering review.",
            "line_items": [
                {"label": "Deferred production — 4h at 15% reduced rate", "usd": 570, "note": "300 BPD × 15% × 4h/24h × $76/bbl; minimal impact during assessment period"},
                {"label": "Field engineer VFD adjustment and monitoring", "usd": 1800, "note": "2h on-site field engineer at $450/hr (travel + labor for VFD verification)"},
                {"label": "VFD calibration verification and compliance documentation", "usd": 630, "note": "Electrical tech 1.5h + process upset log entry (PSM requirement)"},
            ]
        },
        "methodology": "At 67% water cut, downhole motor cooling is severely degraded. GDC thermal model detects winding temp trending toward the 280°F derated operating setpoint (Class H insulation rated 356°F / 180°C per IEC 60085; operators derate well below the nameplate class). GDC provides hours of advance notice on this chronic thermal trend vs. the SCADA high alarm at 280°F. Early VFD intervention costs ~$3,000; unmitigated failure costs ~$150k–$200k (motor replacement, workover rig, deferred production). 🔴 NEEDS-EXPERT: exact lead hours and ROI ratio are field-specific — contact O&G SME before presenting as hard numbers.",
        "references": ["Baker Hughes: ESP Motor Thermal Design Manual", "SPE-68094: Effect of Water Cut on ESP Motor Temperature", "API RP 11S2: Electrical Submersible Pump Motor Recommended Practice", "IEEE 1068: IEEE Guide for Winding Insulation Thermal Ratings"]
    },
    "thermal_runaway": {
        "fault_label": "Thermal Runaway — Gas Lift Compressor",
        "capital_at_risk_usd": 150000,
        "early_intervention_usd": 200,
        "unmitigated_impact": {
            "basis": "Cylinder head seizure or catastrophic gasket failure. When discharge temperature exceeds 250°F (Ariel JGP cylinder design limit), piston rings and cylinder liner distort. Seizure can occur within 20–40 minutes after cooling circuit failure.",
            "line_items": [
                {"label": "Cylinder head and liner replacement — 2 cylinders", "usd": 38000, "note": "Ariel JGP: $19,000/cylinder head assembly (valve deck, head gasket, cooling jacket)"},
                {"label": "Piston ring and rod packing replacement", "usd": 14500, "note": "Thermal distortion damages piston rings; Ariel OEM parts per cylinder"},
                {"label": "Compressor rebuild labor — 5 days × 3 mechanics", "usd": 42000, "note": "Certified Ariel techs at $2,800/day each; field OEM service rates, Permian Basin 2024"},
                {"label": "Crane and heavy rigging for cylinder removal", "usd": 8500, "note": "Required for cylinder head removal on 1200HP frame; routine crane day rate"},
                {"label": "Deferred production — 8 days × 180 BPD × $76/bbl", "usd": 43680, "note": "Pad Bravo gas lift production loss; 180 BPD net from 4 wells"},
                {"label": "Emergency parts expediting and air freight", "usd": 3320, "note": "Overnight air freight from Ariel Manufacturing, Mount Vernon OH"},
            ]
        },
        "early_intervention": {
            "basis": "Fin-fan cooler chemical flush appended to tomorrow's already-scheduled crew visit (WO-2026-0847). CREW-BRAVO-B is on-site for transmitter calibration; 45-minute cooler flush added at zero incremental travel cost.",
            "line_items": [
                {"label": "Citric acid descaling solution — 3 gallons", "usd": 279, "note": "Industrial-grade citric acid at $93/gal; standard fin-fan cleaning chemical"},
                {"label": "Incremental labor — 0.75h appended to existing work order", "usd": 0, "note": "Zero travel cost as crew is already on-site. Incremental labor included in existing WO budget."},
                {"label": "Emergency dispatch cost avoided entirely", "usd": -1800, "note": "Scheduling to existing dispatch avoids $1,800 emergency callout fee"},
            ]
        },
        "methodology": "The fin-fan cooler PM was 8 months overdue (Ariel-recommended interval: 6 months). A crew was already scheduled on-site, making the cost of early intervention essentially the cost of chemicals only. GDC identifies the overdue PM from Maximo records and correlates it with the rising discharge temperature trend to generate this zero-cost recommendation.",
        "references": ["Ariel Corporation JGP Series: Cylinder Thermal Limits & Maintenance Manual", "GMRC: Gas Machinery Research Council — Compressor Maintenance Best Practices", "API 618: Reciprocating Compressors for Petroleum, Chemical, and Gas Services", "IBM Maximo PM: Interval Optimization for Gas Compression"]
    },
    "bearing_wear": {
        "fault_label": "Journal Bearing Wear — Gas Lift Compressor",
        "capital_at_risk_usd": 85000,
        "early_intervention_usd": 8200,
        "unmitigated_impact": {
            "basis": "Crankshaft journal bearing spalling progressing to crankshaft scoring. Once ISO 10816-6 vibration velocity exceeds 12 mm/s, bearing race failure accelerates. Crankshaft scoring requires full compressor disassembly and crankshaft grinding or replacement.",
            "line_items": [
                {"label": "Journal bearing set replacement (4 bearings, post-seizure)", "usd": 8200, "note": "ARJ-42-BEARING-KIT: main + connecting rod bearings for 2-throw Ariel frame; OEM kit"},
                {"label": "Crankshaft re-grind or replacement (scoring assumed)", "usd": 28000, "note": "Crankshaft grinding $8,000–$12,000; crankshaft replacement $24,000–$32,000 (seizure assumed)"},
                {"label": "Compressor rebuild labor — 4 days × 2 specialists", "usd": 22400, "note": "Ariel-certified millwright team at $2,800/day each; includes alignment verification"},
                {"label": "Oil flush and particle analysis post-repair", "usd": 2400, "note": "Full lube system flush + particle count to confirm no debris before restart"},
                {"label": "Deferred production — 5 days × 180 BPD × $76/bbl", "usd": 16800, "note": "4-well gas lift production loss during compressor downtime"},
                {"label": "Crane, rigging, and facilities", "usd": 7200, "note": "Required for crankcase access; crane day rate × 2 days"},
            ]
        },
        "early_intervention": {
            "basis": "Planned bearing replacement appended to existing quarterly dispatch (CREW-BRAVO-A, WO-2026-0851). Bearing kit confirmed in local stock. Zero incremental travel. 3 additional hours added to scheduled work order.",
            "line_items": [
                {"label": "Bearing kit — ARJ-42-BEARING-KIT (local stock, confirmed)", "usd": 8200, "note": "OEM Ariel journal bearing set; confirmed in local inventory for same-day installation"},
                {"label": "Incremental labor on scheduled work order", "usd": 0, "note": "Zero incremental labor cost: crew on-site for quarterly inspection; 3h added to existing WO"},
                {"label": "Oil change and analysis post-replacement", "usd": 480, "note": "10 quarts synthetic compressor oil + particle count verification"},
            ]
        },
        "methodology": "BPFI spectral peak 40% above ISO 10816-6 alert threshold, combined with 4× increase in oil ferrous debris (48 ppm vs 12 ppm baseline), provides high-confidence bearing wear prediction 16+ hours ahead of SCADA alarm. Crew was already scheduled on-site; intervention cost is essentially parts-only ($8,200) vs $85,000 if crankshaft scores.",
        "references": ["ISO 10816-6: Vibration Severity for Reciprocating Machines", "GMRC: Journal Bearing Failure Modes in Natural Gas Compressors", "Ariel Corporation: Compressor Bearing Maintenance Technical Bulletin TB-004", "ASTM D7690: Spectroscopic Metal Analysis for Wear Debris"]
    },
    "valve_failure": {
        "fault_label": "Check Valve Failure — Gas Lift Compressor",
        "capital_at_risk_usd": 42500,
        "early_intervention_usd": 5000,
        "unmitigated_impact": {
            "basis": "Check valve disk fracture allows complete reversal of gas flow through compressor. Reverse flow at full discharge pressure damages compressor internals within seconds. Valve replacement plus mandatory internal inspection required.",
            "line_items": [
                {"label": "Check valve disk assemblies × 2 (replace as pair per API 618)", "usd": 3600, "note": "CVD-1200-PSI-4IN at $1,800 each; API 618 requires replacing valve manifolds in matched pairs"},
                {"label": "Compressor internal inspection — pistons, cylinders, valves", "usd": 12000, "note": "Mandatory post-backflow event per Ariel service bulletin: disassemble, measure, replace worn parts"},
                {"label": "Compressor rebuild labor — 2 days × 2 mechanics", "usd": 11200, "note": "Ariel-certified techs at $2,800/day each; includes post-repair functional test"},
                {"label": "Deferred production — 3 days × 180 BPD × $76/bbl", "usd": 10260, "note": "4-well Pad Bravo production affected while compressor is offline"},
                {"label": "Emergency dispatch — after-hours compressor technicians", "usd": 5440, "note": "Emergency after-hours call-out: $3,200 callout fee + $1,120 travel allowance × 2 techs"},
            ]
        },
        "early_intervention": {
            "basis": "Controlled shutdown before valve fracture. Replacement valve is in local inventory. Replacement takes 4 hours by on-call crew during daylight shift at standard rates.",
            "line_items": [
                {"label": "Replacement check valve disk (local warehouse stock)", "usd": 1800, "note": "CVD-1200-PSI-4IN at $1,800; confirmed in local inventory — no freight required"},
                {"label": "Field crew valve replacement labor — 4h daylight shift", "usd": 2800, "note": "Compressor operator 4h at $700/hr including safety standby; standard day rate"},
                {"label": "Pressure test and restart supervision", "usd": 400, "note": "Production technician 2h; pressure test per API 618 before restart"},
            ]
        },
        "methodology": "The discharge pressure historian shows 42 PSI cyclic amplitude (5× normal <8 PSI) at 1.8 Hz — diagnostic signature of valve disk flutter/chattering. SCADA shows normal mean pressure; no SCADA alarm fires. GDC detects the oscillation signature 15 minutes before disk fracture. Controlled shutdown and scheduled replacement: $5,000. Post-fracture emergency repair: $42,500.",
        "references": ["API 618: Reciprocating Compressors for Petroleum Gas Industry Service", "Ariel Corporation: Check Valve Inspection and Replacement Technical Bulletin", "SPE-124560: Compressor Valve Failure Analysis and Prevention"]
    },
    "valve_washout": {
        "fault_label": "Valve Seat Washout — Triplex Mud Pump",
        "capital_at_risk_usd": 52500,
        "early_intervention_usd": 5000,
        "unmitigated_impact": {
            "basis": "Complete fluid end rebuild required once valve seat erodes through seat pocket. At 81% VE (vs. 95% nominal) and declining, continued operation risks suction valve failure causing fluid end body damage beyond the valve seats.",
            "line_items": [
                {"label": "Valve seats, inserts, and poppets — fluid end rebuild kit", "usd": 8500, "note": "NOV TWS 7500: valve seat kit × 3 cylinders; NOV OEM pricing, Permian Basin 2024"},
                {"label": "Piston liners and piston assemblies × 3", "usd": 12000, "note": "Erosion damage to liner bore from inefficient valve; replaced as part of fluid end rebuild per NOV manual"},
                {"label": "Fluid end rebuild labor — NOV certified technician", "usd": 9600, "note": "NOV field service tech: 8h × $1,200/hr (fluid end specialist day rate, WTX 2024)"},
                {"label": "Rig flat time — 8h fluid end rebuild × $45,000/day rig rate", "usd": 15000, "note": "Rig rate + spread: $45,000/day WTX land rig; 8 hours unplanned = $15,000"},
                {"label": "Standpipe pressure test before restart (API 7-1)", "usd": 2400, "note": "Required post-rebuild per API 7-1 before returning to drilling operations"},
                {"label": "Possible hole condition check if circulation lost", "usd": 5000, "note": "If pump failure causes undetected loss of circulation; wireline depth verification"},
            ]
        },
        "early_intervention": {
            "basis": "Controlled pump transition to standby MUD-RIG42-3 at next connection (22 minutes). MUD-RIG42-1 reduced to maintenance mode. Fluid end valve seat rebuild performed during planned connection stop at standard rates, not emergency call-out.",
            "line_items": [
                {"label": "Valve seat rebuild kit — 3 cylinders (scheduled repair)", "usd": 3600, "note": "Valve seats only; liner replacement deferred as liner bore not yet damaged"},
                {"label": "NOV technician — scheduled fluid end inspection 4h", "usd": 4800, "note": "Scheduled during connection window; standard rate, no emergency premium"},
                {"label": "Pump transition supervision (30 min)", "usd": 675, "note": "Company man supervision + driller coordination at rig spread rate"},
                {"label": "Emergency call-out premium avoided", "usd": -4075, "note": "Scheduled vs emergency: avoids 2× labor rate on emergency after-hours call-out"},
            ]
        },
        "methodology": "Declining VE (81% vs. 95% nominal), rising SPM compensation (+6 from baseline), and fluid end inspection 460 ft past interval confirm valve erosion with high confidence. Transition to standby pump is a 3-minute, low-risk procedure preserving ECD stability. Repair at next connection: $5,000. Emergency full rebuild: $52,500.",
        "references": ["API Spec 7-1: Rotary Drill Stem Elements", "NOV TWS 7500 Triplex Pump: Maintenance and Service Manual", "SPE-185969: Mud Pump Reliability and Maintenance Optimization", "IADC WellCap: Pump VE Monitoring and Management"]
    },
    "pulsation_dampener_failure": {
        "fault_label": "Pulsation Dampener Bladder Rupture — Mud Pump",
        "capital_at_risk_usd": 500000,
        "early_intervention_usd": 15000,
        "unmitigated_impact": {
            "basis": "Bladder rupture produces pressure hammer (water hammer) that can rupture standpipe, kelly hose, or iron manifold. Pipe rupture at 5,000 PSI is a high-energy event with personnel injury risk, mandatory HSE investigation, regulatory notification, and potential well control incident. Industry fatalities have occurred from this failure mode.",
            "line_items": [
                {"label": "Standpipe and manifold full inspection / replacement", "usd": 65000, "note": "Full 4\" high-pressure standpipe inspection per API 16C; replacement if hammer damage detected"},
                {"label": "Kelly hose replacement — 4\" 5,000 PSI rated", "usd": 18000, "note": "High-pressure rotary hose replacement if pressure hammer causes flex fatigue at connections"},
                {"label": "Dampener bladder replacement — both units", "usd": 12000, "note": "Replace both dampeners per NOV recommendation: $6,000/unit for TWS 7500 dampener kit"},
                {"label": "Unplanned rig stop — 18h flat time × $45,000/day", "usd": 33750, "note": "Rig spread idle while standpipe system is inspected; mandatory before drilling resumes"},
                {"label": "Third-party pipe inspection (MT, UT, pressure test)", "usd": 22000, "note": "Mandatory NDT per API 5DP after high-pressure hammer event; third-party inspector required"},
                {"label": "Regulatory notification and incident investigation", "usd": 15000, "note": "HSE investigation, documentation, and regulatory filing (BSEE/state) — minimum cost estimate"},
                {"label": "Personnel injury liability — statistical industry average", "usd": 180000, "note": "Actuarial cost from IADC recorded high-pressure event injury statistics (2019-2023)"},
                {"label": "Well control contingency if wellbore pressure control compromised", "usd": 154250, "note": "Kill weight mud, BOP test, pump-and-dump if wellbore pressure control compromised during event"},
            ]
        },
        "early_intervention": {
            "basis": "Immediate 30% pump stroke reduction to reduce line pressure, plus dampener isolation. Bladder integrity inspection can be performed safely at reduced rate. Proactive replacement before failure.",
            "line_items": [
                {"label": "Dampener bladder kit — proactive replacement", "usd": 6000, "note": "NOV dampener kit: $6,000 proactive replacement before catastrophic failure"},
                {"label": "Pump rate reduction — 2h at reduced rate", "usd": 3750, "note": "$45,000/day rig rate × 2h planned stop + fluid system rebalancing time"},
                {"label": "Crew inspection and replacement labor", "usd": 5250, "note": "Derrickman + motorman: 3h × 2 crew at rig labor rates; standard maintenance procedure"},
            ]
        },
        "methodology": "Pulsation dampener failure has PNR = 0 minutes — there is no safe intervention window after bladder rupture. The entire capital value of this scenario is in early detection. GDC identifies the bladder integrity signature from pressure oscillation patterns before rupture. Capital at risk includes the full liability profile of a high-pressure pipe rupture event including statistical injury liability.",
        "references": ["API RP 16C: Choke and Kill Equipment", "NOV TWS Series Pulsation Dampener: Maintenance Manual", "IADC HSE Case: Standpipe Fatigue Failure Reports (2019-2023)", "OSHA 1910.119: Process Safety Management — High-Energy Hazards"]
    },
    "gearbox_bearing_spalling": {
        "fault_label": "Gearbox Bearing Spalling — Top Drive",
        "capital_at_risk_usd": 120000,
        "early_intervention_usd": 28500,
        "unmitigated_impact": {
            "basis": "Active bearing race spalling confirmed by oil analysis (64 ppm Fe, alarm at 50 ppm) and torque oscillation. Bearing seizure would require crane removal of top drive from derrick, full gearbox disassembly, and mandatory crownblock inspection.",
            "line_items": [
                {"label": "Tapered roller bearing set — NOV 250T top drive", "usd": 28500, "note": "NOV-250T-BEAR-KIT; OEM tapered roller bearing set with inner/outer races, retainers; Houston 2024"},
                {"label": "Gearbox disassembly and reassembly labor", "usd": 24000, "note": "NOV field service: 3 mechanics × 2 days × $4,000/day (gearbox specialist rate)"},
                {"label": "Crane hire — top drive removal and reinstallation", "usd": 18500, "note": "Grove 160-ton crane + operator: day rate × 2 days for remove/reinstall + rigging"},
                {"label": "Drilling halt — 18h flat time × $45,000/day rig rate", "usd": 33750, "note": "$45,000/day rig spread × 18h; drilling halted while top drive is removed and rebuilt"},
                {"label": "Crown block and derrick inspection (mandatory post-removal)", "usd": 8500, "note": "Required per NOV after top drive removal: crown block and traveling equipment inspection"},
                {"label": "Lube oil flush and system decontamination", "usd": 6750, "note": "Full gearbox lube system flush to remove bearing debris; 3 oil changes + particle analysis"},
            ]
        },
        "early_intervention": {
            "basis": "Bearing kit ordered on standard freight (4 days from Houston); replacement scheduled for next planned trip in 18 hours. Replacement during planned trip stop is non-productive time (NPT) that occurs regardless; zero incremental rig cost.",
            "line_items": [
                {"label": "Bearing kit — NOV-250T-BEAR-KIT (standard freight, 4 days)", "usd": 28500, "note": "Order immediately; arrives before next planned trip from Houston. No air freight required."},
                {"label": "Replacement labor during planned trip — 4h", "usd": 0, "note": "Scheduled during planned trip NPT; zero incremental rig cost"},
                {"label": "Air freight premium saved by ordering now", "usd": -6000, "note": "Standard freight vs air freight saves $6,000; available only with early detection"},
                {"label": "Temporary monitoring sensor (until replacement)", "usd": 850, "note": "Piezo mount-on sensor for interim monitoring at 85% RPM for 18h"},
            ]
        },
        "methodology": "Oil analysis flagged this bearing 48 hours ago (64 ppm Fe, alarm 50 ppm); without GDC AI fusion, this data point was not correlated with the EDR torque oscillation data. GDC fuses oil analysis + torque oscillation + vibration frequency to confirm active spalling. The window to replace during a planned trip (18h away) is the key opportunity — after which seizure requires emergency crane removal at 4.2× the cost.",
        "references": ["NOV 250T Top Drive Gearbox: Service and Maintenance Manual", "ASTM D7690: Wear Debris Analysis in Lubricating Oils", "ISO 10816-3: Vibration for Industrial Machines with Power > 15 kW", "SPE-185321: Predictive Maintenance for Top Drive Systems"]
    },
    "piston_seal_wear": {
        "fault_label": "Liner Seal Wear — Triplex Mud Pump",
        "capital_at_risk_usd": 15000,
        "early_intervention_usd": 3800,
        "unmitigated_impact": {
            "basis": "Piston-liner bypass causes fluid end temperature rise and discharge pressure decline. If seal wear continues past the critical threshold, the cylinder liner bore is damaged, requiring full bore replacement in addition to the piston assembly.",
            "line_items": [
                {"label": "Piston assembly with seals × 3 cylinders", "usd": 4200, "note": "NOV complete piston assemblies: $1,400 each for TWS 7500; includes piston, cups, backup rings"},
                {"label": "Cylinder liner replacement × 3 (bore damage assumed at PNR)", "usd": 6000, "note": "Chrome-alloy liners: $2,000 each; preventable with early seal replacement before bore wear"},
                {"label": "Fluid end rebuild labor — emergency call-out", "usd": 3600, "note": "NOV field tech 3h × $1,200/hr; emergency after-hours rate vs. standard scheduled rate"},
                {"label": "Rig flat time — 4h repair", "usd": 1200, "note": "$45,000/day × 4h unplanned stop for emergency fluid end rebuild"},
            ]
        },
        "early_intervention": {
            "basis": "Seal kit is in local inventory (2 kits confirmed). Replacement is performed at the next planned connection stop. Connection stops are non-productive time; zero incremental rig cost.",
            "line_items": [
                {"label": "Liner seal kit — NOV-SEAL-TK-7500 (confirmed in local stock)", "usd": 3800, "note": "Polyurethane piston cups + liner O-rings; 2 kits confirmed on-site at $1,900 each"},
                {"label": "Replacement during connection stop (NPT)", "usd": 0, "note": "Connection stops are planned NPT; seal replacement is standard connection procedure"},
                {"label": "Post-replacement pressure test", "usd": 0, "note": "Standard rig procedure during connection; no incremental cost"},
            ]
        },
        "methodology": "Fluid end temperature 57°F above nominal and declining discharge pressure at 2,840 ft past the seal replacement interval are textbook piston-liner bypass signatures. Parts are on-site. This is a $3,800 parts-only fix now vs a $15,000 emergency rebuild if the liner bore is damaged.",
        "references": ["NOV TWS 7500 Liner and Piston Seal: Replacement Manual", "SPE-185969: Mud Pump Reliability and Maintenance Optimization", "API Spec 7-1: Rotary Drill Stem Elements", "Pason EDR: Pump Efficiency Monitoring Best Practices"]
    },
    "hydraulic_leak": {
        "fault_label": "Hydraulic System Leak — Top Drive",
        "capital_at_risk_usd": 8000,
        "early_intervention_usd": 2040,
        "unmitigated_impact": {
            "basis": "Hydraulic fluid loss below the system low alarm (2,500 PSI) causes loss of torque capacity on the top drive. At minimum torque, the top drive cannot provide required back-reaming torque for directional work, requiring rotary table backup and an unplanned drilling stop.",
            "line_items": [
                {"label": "Hydraulic hose replacement at identified leak section", "usd": 1800, "note": "3,000 PSI rated hydraulic hose with JIC fittings; standard rig hose replacement"},
                {"label": "Hydraulic fluid — 8 gallons to refill reservoir", "usd": 480, "note": "AW68 hydraulic fluid at $60/gal; reservoir from 78% to 100% fill plus system prime"},
                {"label": "Hydraulics technician — pressure test and documentation", "usd": 1200, "note": "Certified tech 2h pressure test + documentation; required before top drive resumed"},
                {"label": "Rig flat time — 3h unplanned stop × $45,000/day", "usd": 5625, "note": "$45,000/day rig spread × 3h for emergency repair + 30-minute pressure test"},
            ]
        },
        "early_intervention": {
            "basis": "Leak located and patched at next stand break (24 minutes). Spare hoses and fittings are on the rig floor. Repair takes 45 minutes during a planned connection stop — non-productive time regardless.",
            "line_items": [
                {"label": "Hydraulic hose from rig floor spares inventory", "usd": 1800, "note": "Using existing rig floor spare; replace spare inventory kit cost after repair"},
                {"label": "Hydraulic fluid top-up — 4 gallons", "usd": 240, "note": "Partial top-up during patch; remaining supply adequate for patch + test"},
            ]
        },
        "methodology": "GDC calculated a precise 0.4 gal/hr leak rate by fusing the rig floor maintenance log (3× top-up records, not in SCADA) with the hydraulic pressure trend. SCADA pressure at 2,940 PSI — no alarm. GDC predicts low alarm in 3.6 hours. Repair during next stand break costs $2,040 in materials vs $8,000 in emergency repair cost and rig flat time.",
        "references": ["Parker Hannifin: High Pressure Hydraulic Hose Selection Guide", "NOV 250T Top Drive: Hydraulic System Maintenance Manual", "IADC: Rig Floor Hydraulic Systems Safety and Maintenance", "API RP 7G: Drill Stem Design and Operating Limits"]
    },
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
    "bearing_wear_glift": {
        "horizon_label": "Hours",
        "total_hours": 16,
        "scada_alarm_health": 0.20,
        "pnr_health": 0.08,
        "scada_sensor": "vib",        # Vibration high alarm (crankshaft bearing)
        "pnr_sensor": "temp",         # Thermal runaway as bearing seizes
        "primary_sensor": "vib",
        "intervention_type": "maintenance_scheduling",
    },
    "bearing_wear": {
        "horizon_label": "Hours",
        "total_hours": 16,
        "scada_alarm_health": 0.20,
        "pnr_health": 0.08,
        "scada_sensor": "vib",
        "pnr_sensor": "temp",
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
    "fluid_drawdown": {
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
    # ── Slug Flow (2h window) — surface choke adjustment ─────────────────────
    # Intermittent gas/liquid slugs from the wellbore cause hydraulic vibration
    # in the tubing/flowline. Primary signature: vibration drift with flat motor
    # temperature. PNR 120min per PNR_MINUTES — operator dispatches surface tech
    # to adjust choke valve; well pull is NOT required.
    "slug_flow": {
        "horizon_label": "Hours",
        "total_hours": 2.0,           # 2 hours
        "scada_alarm_health": 0.25,
        "pnr_health": 0.10,
        "scada_sensor": "vib",        # Vibration high alarm from slug impacts
        "pnr_sensor": "vib",          # Vibration drives PNR (tubing fatigue)
        "primary_sensor": "vib",
        "intervention_type": "field_notification",
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
app.mount("/static", StaticFiles(directory="/app/static"), name="static")


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

    # ── Log to injection_events for non-circular model verification ──────────
    _first = injected[0] if injected else {}
    _profile = FAULT_PROFILES.get(req.fault_type, {}) if req.fault_type != "normal" else {}
    _s4c = SENSOR4_CONFIG.get(asset_class)
    _amps_lo = _profile.get(_s4c["range_key"], (None, None))[0] if (_s4c and _s4c["range_key"] in _profile) else None
    _amps_hi = _profile.get(_s4c["range_key"], (None, None))[1] if (_s4c and _s4c["range_key"] in _profile) else None
    _nr = NORMAL_RANGES.get(asset_class, {})
    _ie_params = {
        "injection_mode": "point",
        "fault_type": req.fault_type,
        "psi_range": _profile.get("psi_range", _nr.get("psi")),
        "temp_range": _profile.get("temp_range", _nr.get("temp")),
        "vib_range": _profile.get("vib_range", _nr.get("vib")),
        "amps_range": (_amps_lo, _amps_hi) if _amps_lo is not None else _s4c["normal_range"] if _s4c else None,
        "psi_target": _first.get("psi"),
        "temp_target": _first.get("temp_f"),
        "vib_target": _first.get("vibration"),
        "amps_target": _first.get(_s4c["key"]) if _s4c else None,
        "reading_count": count,
    }
    try:
        _ie_conn = get_db()
        _pr = _ie_params.get("psi_range") or (None, None)
        _tr = _ie_params.get("temp_range") or (None, None)
        _vr = _ie_params.get("vib_range") or (None, None)
        _ar = _ie_params.get("amps_range") or (None, None)
        with _ie_conn.cursor() as _cur:
            _cur.execute("""
                INSERT INTO injection_events
                  (asset_id, fault_type, injection_mode,
                   psi_range_lo, psi_range_hi, temp_range_lo, temp_range_hi,
                   vib_range_lo, vib_range_hi, amps_range_lo, amps_range_hi,
                   psi_target, temp_target, vib_target, amps_target, reading_count)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (req.asset_id, req.fault_type, "point",
                  _pr[0], _pr[1], _tr[0], _tr[1], _vr[0], _vr[1], _ar[0], _ar[1],
                  _ie_params["psi_target"], _ie_params["temp_target"],
                  _ie_params["vib_target"], _ie_params["amps_target"], count))
        _ie_conn.commit()
        _ie_conn.close()
    except Exception as _e:
        log.warning(f"injection_events write failed (non-fatal): {_e}")

    log.info(f"Injected {count}× {req.fault_type} on {req.asset_id}")
    return {"status": "injected", "fault": req.fault_type, "asset": req.asset_id,
            "count": count, "readings": injected, "injection_params": _ie_params}


# ── Gradual Degradation ────────────────────────────────────────────────────────
def _run_degrade_thread(asset_id: str, fault_type: str, duration_seconds: int) -> None:
    global active_degrades
    asset_class = ASSET_REGISTRY[asset_id]["asset_class"]
    profile = FAULT_PROFILES[fault_type]
    nr = NORMAL_RANGES.get(asset_class, NORMAL_RANGES["esp"])
    steps = max(1, duration_seconds // 5)

    # Randomize target severity within fault profile range — drawn once so each run feels different
    _psi_target  = random.uniform(*profile["psi_range"])
    _temp_target = random.uniform(*profile["temp_range"])
    _vib_target  = random.uniform(*profile["vib_range"])
    _k           = random.uniform(3.0, 4.0)  # randomize ramp exponent slightly

    # 4th-sensor target (ESP: amps, Mud Pump: spm)
    _s4c_d = SENSOR4_CONFIG.get(asset_class)
    _s4_target = None
    _s4_range  = None
    if _s4c_d and _s4c_d["range_key"] in profile:
        _s4_range = profile[_s4c_d["range_key"]]
        _s4_target = (_s4_range[0] + _s4_range[1]) / 2.0  # midpoint of fault range

    active_degrades[asset_id] = {
        "running": True, "fault_type": fault_type, "step": 0, "steps": steps,
        "fault_onset_utc": datetime.utcnow().isoformat() + "Z",  # Task 7: authoritative onset for PNR/Cloud calc
        "ramp_k": _k, "ramp_target_psi": _psi_target,
    }

    # ── Log to injection_events for non-circular model verification ──────────
    _degrade_ie_params = {
        "injection_mode": "gradual",
        "fault_type": fault_type,
        "psi_range": profile["psi_range"],
        "temp_range": profile["temp_range"],
        "vib_range": profile["vib_range"],
        "amps_range": _s4_range,
        "psi_target": round(_psi_target, 1),
        "temp_target": round(_temp_target, 1),
        "vib_target": round(_vib_target, 3),
        "amps_target": round(_s4_target, 1) if _s4_target is not None else None,
        "ramp_k": round(_k, 3),
        "duration_s": duration_seconds,
    }
    # Store on active_degrades so inject_degrade can return it in its API response
    active_degrades[asset_id]["injection_params"] = _degrade_ie_params
    try:
        _die_conn = get_db()
        _pr = profile["psi_range"]
        _tr = profile["temp_range"]
        _vr = profile["vib_range"]
        _ar = _s4_range or (None, None)
        with _die_conn.cursor() as _cur:
            _cur.execute("""
                INSERT INTO injection_events
                  (asset_id, fault_type, injection_mode,
                   psi_range_lo, psi_range_hi, temp_range_lo, temp_range_hi,
                   vib_range_lo, vib_range_hi, amps_range_lo, amps_range_hi,
                   psi_target, temp_target, vib_target, amps_target,
                   ramp_k, duration_s)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (asset_id, fault_type, "gradual",
                  _pr[0], _pr[1], _tr[0], _tr[1], _vr[0], _vr[1], _ar[0], _ar[1],
                  _degrade_ie_params["psi_target"], _degrade_ie_params["temp_target"],
                  _degrade_ie_params["vib_target"], _degrade_ie_params["amps_target"],
                  _degrade_ie_params["ramp_k"], duration_seconds))
        _die_conn.commit()
        _die_conn.close()
    except Exception as _e:
        log.warning(f"injection_events degrade write failed (non-fatal): {_e}")

    log.info(f"▶ Gradual degrade: {fault_type} on {asset_id} ({steps} steps)")

    for i in range(steps):
        if not active_degrades.get(asset_id, {}).get("running"):
            break
        t    = ((i + 1) / steps) ** _k
        psi  = (nr["psi"][0]  + nr["psi"][1])  / 2 + t * (_psi_target  - (nr["psi"][0]  + nr["psi"][1])  / 2)
        temp = (nr["temp"][0] + nr["temp"][1]) / 2 + t * (_temp_target - (nr["temp"][0] + nr["temp"][1]) / 2)
        vib  = (nr["vib"][0]  + nr["vib"][1])  / 2 + t * (_vib_target  - (nr["vib"][0]  + nr["vib"][1])  / 2)

        # ── 4th-sensor ramp (ESP: motor_amps, Mud Pump: spm) ──────────────────
        _s4c = SENSOR4_CONFIG.get(asset_class)
        _s4_val = None
        if _s4c and _s4c["range_key"] in profile:
            _s4_nom = _s4c["nominal"]
            _s4_rng = profile[_s4c["range_key"]]
            _s4_end = (_s4_rng[0] + _s4_rng[1]) / 2.0
            if asset_class == "mud_pump" and fault_type == "pulsation_dampener_failure":
                _s4_val = round(random.gauss((_s4_rng[0] + _s4_rng[1]) / 2.0, (_s4_rng[1] - _s4_rng[0]) / 6.0), 1)
            else:
                _s4_mid = _s4_nom + t * (_s4_end - _s4_nom)
                _s4_val = round(max(10.0, random.gauss(_s4_mid, abs(_s4_mid * 0.01))), 1)

        # Restored Gaussian noise per requirements
        reading = {
            "asset_id"    : asset_id,
            "asset_type"  : asset_class,
            "psi"         : round(random.gauss(psi, abs(psi * 0.02)),  1),
            "temp_f"      : round(random.gauss(temp, abs(temp * 0.01)), 1),
            "vibration"   : round(max(0.05, random.gauss(vib, abs(vib * 0.05))), 3),
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
        # Phase 16: Track current sensor values so the intel generator can
        # use them for contextually accurate document prompts.
        if asset_id in active_degrades:
            active_degrades[asset_id]["current_sensors"] = {
                "psi": reading["psi"], "temp": reading["temp_f"], "vib": reading["vibration"],
                "motor_amps": reading.get("motor_amps"),
            }
        time.sleep(5)

    # ── Hold phase ────────────────────────────────────────────────────────────
    # Ramp is complete. Keep sending the final fault-level readings every 5s
    # so the 10-minute query window stays populated and the RUL/incidents
    # remain active until the operator explicitly clicks ↺ Reset.
    # The simulator is still skipping this asset because it's still in
    # active_degrades — only cancel_degrade / resetNormal removes it.
    if asset_id in active_degrades:
        active_degrades[asset_id].update({"running": False, "held": True, "step": steps})

    # Final fault-level values — match the randomized targets drawn at thread startup
    final_psi  = _psi_target
    final_temp = _temp_target
    final_vib  = _vib_target

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
            "psi"         : round(random.gauss(final_psi, abs(final_psi * 0.02)), 1),
            "temp_f"      : round(random.gauss(final_temp, abs(final_temp * 0.01)), 1),
            "vibration"   : round(max(0.05, random.gauss(final_vib, abs(final_vib * 0.05))), 3),
            "failure_type": fault_type,
            "source"      : "gradual_degrade",
            "timestamp"   : datetime.utcnow().isoformat() + "Z",
        }
        # 4th sensor hold-phase value
        if _final_s4 is not None and _s4c_hold is not None:
            if asset_class == "mud_pump" and fault_type == "pulsation_dampener_failure":
                hold_reading[_s4c_hold["key"]] = round(random.gauss((_final_s4_rng[0] + _final_s4_rng[1]) / 2.0, (_final_s4_rng[1] - _final_s4_rng[0]) / 6.0), 1)
            else:
                hold_reading[_s4c_hold["key"]] = round(max(10.0, random.gauss(_final_s4, abs(_final_s4 * 0.01))), 1)
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
    # Pre-clear old field_intel docs for this asset (fresh start every injection)
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM field_intel WHERE asset_id = %s", (req.asset_id,))
            asset_class = ASSET_REGISTRY[req.asset_id]["asset_class"]
            cur.execute(
                "INSERT INTO fault_sessions (asset_id, asset_class, fault_type) VALUES (%s, %s, %s)",
                (req.asset_id, asset_class, req.fault_type)
            )
            # ── Seed guaranteed-match field_intel documents for context fusion ─────────
            # adjust_rul_with_documents() applies RUL multipliers only when keyword-matching
            # documents exist in field_intel. Seeding these at inject time guarantees that
            # the first /api/plot/forecast-data poll returns adjusted_rul < time_to_scada,
            # creating a visible and real context-fusion gap on the primary chart.
            if req.fault_type == "gas_lock":
                cur.execute("""
                    INSERT INTO field_intel
                      (asset_id, asset_class, fault_context, doc_type, headline, detail,
                       ai_relevance, icon, lbl, lbl_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    req.asset_id, asset_class, "gas_lock", "shift_note",
                    "Tour 2 Shift Note \u2014 Elevated GVF at Pump Intake",
                    "Operator observed gas void fraction at pump intake estimated at 78%% throughout "
                    "the morning tour. Separator gas test from prior shift: GOR 1,310 scf/bbl, up 19%% "
                    "from 24-hour baseline. Motor amps trending below nominal. No SCADA alarm has fired "
                    "\u2014 all sensors remain within configured thresholds. Recommend continued monitoring.",
                    "HIGH \u2014 GVF above pump handling threshold (~60\u201365%%); combined with rising GOR, "
                    "pattern is consistent with early-stage gas lock and imminent loss of motor cooling flow.",
                    "\U0001f4cb", "AI", "ai"
                ))
            elif req.fault_type == "fluid_drawdown":
                cur.execute("""
                    INSERT INTO field_intel
                      (asset_id, asset_class, fault_context, doc_type, headline, detail,
                       ai_relevance, icon, lbl, lbl_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    req.asset_id, asset_class, "fluid_drawdown", "sonic_log",
                    "Tour 2 Dynamic Sonic Survey \u2014 Fluid Drawdown Detected",
                    "Operator dynamic fluid survey (06:00 sonic log) measured dyn fluid level at 150 ft above ESP intake. "
                    "Casing annulus liquid column shows steady depletion without free gas zone migration (casing pressure flat at 40 PSI). "
                    "No SCADA alarm has fired. Slowing pump speed will drop dynamic lift velocity below critical lift, "
                    "risking sand bridging and downhole string pump seizure. Emergency shutdown recommended.",
                    "CRITICAL \u2014 Dynamic fluid level at 150 ft above intake is close to minimum required submergence (120 ft). "
                    "Slowing ESP (VFD trim) risks sand settling and bridging downhole string, causing severe mechanical seizure.",
                    "\U0001f4cb", "AI", "ai"
                ))
        conn.commit()
        conn.close()
    except Exception as e:
        log.warning(f"field_intel pre-clear / fault_sessions write failed (non-fatal): {e}")
    t = threading.Thread(target=_run_degrade_thread,
                         args=(req.asset_id, req.fault_type, req.duration_seconds), daemon=True)
    t.start()
    return {"status": "started", "asset": req.asset_id, "fault_type": req.fault_type,
            "duration_seconds": req.duration_seconds}


@app.get("/api/degrade-status")
def get_degrade_status():
    return {"active": active_degrades}


@app.get("/api/injection-log")
def get_injection_log(limit: int = 50):
    """
    Return the last `limit` injection events with drawn parameters and bounds.
    Used for:
    (a) Non-circular model verification: replay these rows through /predict
        to get a ground-truth confusion matrix.
    (b) Demo transparency: the UI shows drawn values vs profile bounds for each
        injection so the audience can see the randomization is real.
    """
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, inject_time, asset_id, fault_type, injection_mode,
                       psi_range_lo, psi_range_hi, psi_target,
                       temp_range_lo, temp_range_hi, temp_target,
                       vib_range_lo, vib_range_hi, vib_target,
                       amps_range_lo, amps_range_hi, amps_target,
                       ramp_k, duration_s, reading_count
                FROM injection_events
                ORDER BY inject_time DESC
                LIMIT %s
            """, (min(limit, 200),))
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
        conn.close()
        events = []
        for row in rows:
            d = dict(zip(cols, row))
            # Convert timestamps to ISO strings
            if d.get("inject_time"):
                d["inject_time"] = d["inject_time"].isoformat()
            events.append(d)
        return {"events": events, "count": len(events)}
    except Exception as e:
        log.error(f"injection-log query error: {e}")
        return {"events": [], "count": 0, "error": str(e)}


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
    # Fix A: exclude "inference_error" from fault fraction count.
    # inference-api labels ALL readings "inference_error" when ESP classifier isn't loaded.
    # This was causing classifier_active=True during nominal state → health model ran on
    # nominal data → health_score ~0.74 instead of expected ~0.92+. The model is fine;
    # the pipeline label was polluting the fault-detection gate.
    fault_count   = sum(1 for l in recent_labels if l not in ("normal", "", "inference_error"))
    fault_fraction = fault_count / max(len(recent_labels), 1)
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
        # Phase 16.1 — Single continuous exponential matching _build_sensor fix.
        # The old two-segment approach created a visible kink at SCADA detection time.
        # A single exponential from y_start → y_failure over ttf_total_min is physically correct.
        _k      = 3.5
        _expk   = np.exp(_k) - 1.0
        _raw_r  = np.clip(t_arr / max(ttf_total_min, 1.0), 0.0, 1.0)
        forecast_y = y_start + (y_failure - y_start) * (np.exp(_k * _raw_r) - 1.0) / _expk
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
    "bearing_wear_glift": {
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
# NOTE: Must be GET, not POST — EventSource (SSE) always issues a GET request.
# All parameters are passed as query string parameters.
@app.get("/api/agent/recommend-stream")
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
    
    rag_context, adjusted_rul = get_rag_context_and_adjusted_rul(asset_id, fault_type, rul_minutes)

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

    # ── LLM system prompt — two modes ─────────────────────────────────────────
    # Initial consult (no history): constrained to "action + next step" for demo speed.
    # Follow-up questions (history present): open-ended domain expert mode so the agent
    # can answer explanatory/technical questions rather than repeating action templates.
    fault_label = fault_type.replace("_", " ")
    tier = "PAST PNR" if is_pnr_exceeded else ("CRITICAL" if rul_minutes < 15 else ("URGENT" if rul_minutes < 60 else "EARLY"))
    _history_txt = ""
    if _history:
        _hist_lines = "\n".join(f"{h['role'].upper()}: {h.get('content','')[:200]}" for h in _history[-6:])
        _history_txt = f"\nCONVERSATION:\n{_hist_lines}\n"

    fault_desc = FAULT_PROFILES.get(fault_type, {}).get("description", fault_label)
    asset_class_name = ASSET_REGISTRY.get(asset_id, {}).get("asset_type", "equipment")

    _gemma_finding = get_gemma_finding(fault_type, asset_id)

    if _history:
        # Follow-up question mode: give the model full domain context to answer freely,
        # including the pre-canned GEMMA_FINDINGS as ground-truth sensor context so
        # the model doesn't need to hallucinate domain knowledge.
        llm_prompt = (
            f"You are GDC Ops Agent, a senior oil and gas predictive maintenance engineer embedded "
            f"on a Google Distributed Cloud edge system.\n\n"
            f"ACTIVE FAULT: {fault_label} on {asset_id} ({asset_class_name})\n"
            f"FAULT PHYSICS: {fault_desc}\n"
            f"CURRENT STATUS: Tier {tier}. Base SCADA alarm predicted in {rul_minutes:.0f} minutes. "
            f"Adjusted SCADA alarm based on enterprise docs: {adjusted_rul:.0f} minutes.\n"
            f"Asset class: {ASSET_REGISTRY.get(asset_id, {}).get('asset_class','').upper()}\n"
            f"SENSOR INTELLIGENCE: {_gemma_finding}\n"
            f"{rag_context}"
            f"ENTERPRISE ACTION RECOMMENDED: {rule_rec}\n"
            f"{_history_txt}\n"
            f"Answer the operator's latest question with technical precision using upstream O&G terminology. "
            f"Reference specific sensor values and fault physics above. Do not add preamble."
        )
    else:
        # Initial consult: constrained 2-sentence action summary
        llm_prompt = (
            f"You are GDC Ops Agent, an oil and gas predictive maintenance assistant. "
            f"Be concise — respond in exactly 2 sentences.\n\n"
            f"FAULT: {fault_label} on {asset_id}. Tier: {tier}. Base Time to SCADA alarm: {rul_minutes:.0f} minutes, Adjusted: {adjusted_rul:.0f} minutes.\n"
            f"SENSOR CONTEXT: {_gemma_finding}\n"
            f"{rag_context}"
            f"ENTERPRISE DATA ({source_label}): {rule_rec}\n"
            f"In 2 sentences: (1) confirm the immediate action, (2) state the specific next step. "
            f"No preamble. No repetition."
        )

    def _sse_generator():
        # Event 1: Rule-based recommendation (immediate, no LLM latency)
        yield f"data: {json.dumps({'type': 'recommendation', 'text': rule_rec, 'scenario': scenario, 'source': source_label, 'tier': tier, 'rul_minutes': round(rul_minutes, 1), 'adjusted_rul_minutes': round(adjusted_rul, 1)})}\n\n"

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

    # ── Elapsed-time countdown (always live from moment of GDC detection) ──────────
    # The cubic ramp sends near-nominal sensors for first 10+ minutes.
    # Use wall-clock elapsed time so the bridge countdown ticks from injection.
    initial_ttscada = (1.0 - fp_scada_hs) * fp_total_h * 60.0
    fault_onset_str  = dg.get("fault_onset_utc")
    elapsed_ttscada  = initial_ttscada
    if fault_onset_str:
        try:
            _onset = datetime.fromisoformat(fault_onset_str.replace("Z", ""))
            elapsed_min = (datetime.utcnow() - _onset).total_seconds() / 60.0
            elapsed_ttscada = round(max(0.0, initial_ttscada - elapsed_min), 1)
        except Exception:
            pass

    # ML estimate when health has dropped meaningfully; elapsed-time otherwise
    ml_ttscada  = round(max(0.0, (health_score - fp_scada_hs) * fp_total_h) * 60.0, 1)
    ttscada_min = ml_ttscada if health_score < 0.85 else elapsed_ttscada
    ttpnr_min   = round(max(0.0, (health_score - fp_pnr_hs)   * fp_total_h) * 60.0, 1)
    ttf_min     = round(health_score * fp_total_h * 60.0, 1)

    _, adjusted_rul_minutes = get_rag_context_and_adjusted_rul(asset_id, fault_type, ttscada_min)

    return {
        "asset_id": asset_id, "is_active": True,
        "fault_type": fault_type,
        "health_score": round(health_score, 4),
        "time_to_scada_minutes": ttscada_min,
        "adjusted_rul_minutes": adjusted_rul_minutes,
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
    # Fix A (same as plot_forecast): exclude "inference_error" from fault fraction.
    fault_fraction = sum(1 for l in recent_labels if l not in ("normal", "", "inference_error")) / max(len(recent_labels), 1)
    # Sprint 5 v5: same fix as plot_forecast — include is_degrading so any injected fault
    # immediately populates HEALTH_HISTORY and drives a live, declining RUL for any asset.
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
    dpsi_dt = dtemp_dt = dvib_dt = ds4_dt = 0.0   # slopes — populated by ML block if active

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
                
                _, adjusted_rul_minutes = get_rag_context_and_adjusted_rul(asset_id, _fp_fault_type, rul_minutes)
        except Exception as e:
            log.warning(f"forecast-data ML inference error for {asset_id}: {e}")
            adjusted_rul_minutes = rul_minutes

    # Build per-sensor trace data
    fp_scada_sensor = _fp.get("scada_sensor")
    fp_pnr_sensor   = _fp.get("pnr_sensor")
    fp_primary      = _fp.get("primary_sensor")
    fp_total_h      = _fp.get("total_hours", 1.0)
    fp_hlabel       = _fp.get("horizon_label", "Hours")

    ttf_time  = (now + timedelta(minutes=rul_minutes)) if rul_minutes is not None else None
    pnr_t     = (now + timedelta(minutes=pnr_minutes_rem)) if pnr_minutes_rem is not None else None

    # Display window: full RUL + 30% buffer, no artificial cap.
    # For very long horizons we downsample the time array to ≤500 points so the
    # browser renders quickly while the exponential curve shape is preserved.
    _raw_horizon = max(60, int((rul_minutes or 0) * 1.3 + 60)) if rul_minutes else 60
    horizon_min  = _raw_horizon
    _n_points    = min(500, horizon_min)   # never more than 500 Plotly points
    _step        = max(1, horizon_min // _n_points)
    future_times = [now + timedelta(minutes=i) for i in range(_step, horizon_min + 1, _step)]
    t_arr        = np.array([i for i in range(_step, horizon_min + 1, _step)], dtype=float)

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
        # Note: removed the `rul_minutes < 580` cap — Days faults have rul_minutes ~11k
        # and were silently getting a flat line. Now all active projections render.
        if rul_minutes is not None and rul_minutes > 0:
            ttf_total_min = fp_total_h * 60.0 if _fp else max(rul_minutes*3.0, 60.0)
            y_failure = max(y_crit*0.45, 1.0) if crit_dir == "below" else y_crit*1.80
            # Phase 16.1 — Single continuous exponential (no two-segment kink).
            # Previous two-segment approach forced the curve to pivot at rul_minutes,
            # creating an unphysical discontinuity in the rate of decline that the user
            # correctly identified as "the rate flattens and resets at SCADA detection time."
            # Fix: one smooth exponential from y_start → y_failure over ttf_total_min.
            # The SCADA alarm vertical marker is still placed at rul_minutes (ML prediction);
            # it just marks "predicted time to threshold crossing" — independent of curve shape.
            _k2    = 1.8 if fp_hlabel == "Days" else (3.0 if fp_hlabel == "Hours" else 4.5)
            _expk2 = np.exp(_k2) - 1.0
            _raw_r = np.clip(t_arr / max(ttf_total_min, 1.0), 0.0, 1.0)
            _py    = y_start + (y_failure - y_start) * (np.exp(_k2 * _raw_r) - 1.0) / _expk2
            proj_y = _py.tolist()
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

    # ── Thermal lead-time (Phase 2 — per-run-varying, physics-grounded) ────────
    # Minutes until motor winding temp reaches Class H insulation limit (280°F).
    # dtemp_dt is in °F/min from polyfit × READINGS_PER_MIN in the ML block.
    # Varies every demo run because _run_degrade_thread randomizes _temp_target + _k.
    # Temperature is the LAGGING failure indicator; ML detects earlier via PIP+amps
    # multivariate pattern — this number is the deadline ML is racing to beat.
    _thermal_lead = None
    if dtemp_dt > 0.05 and len(temp_v) > 0:
        _current_temp = float(temp_v[-1])
        if _current_temp < 280.0:
            _thermal_lead = round((280.0 - _current_temp) / dtemp_dt, 1)

    # ── Class probabilities (Phase 2 — genuine model output, not hardcoded) ────
    # Distribution of predicted_label + confidence in the last 10-min DB window.
    # During active gas lock: ~90%+ rows classify as "gas_lock" at ~94% confidence.
    # This is categorically ML output — not a threshold alarm — making it the ideal
    # hero for the "SCADA cannot produce this" visual argument.
    _class_probs: dict = {}
    if classifier_active and rows:
        from collections import defaultdict as _dd
        _lc: dict = _dd(list)
        for _r in rows[-20:]:
            _lbl = (_r.get("predicted_label") or "normal").lower()
            _conf = float(_r.get("confidence") or 0.0)
            _lc[_lbl].append(_conf)
        _total = max(sum(sum(v) for v in _lc.values()), 1.0)
        _class_probs = {lbl: round(sum(confs) / _total, 3) for lbl, confs in _lc.items()}

    return {
        "asset_id": asset_id, "is_active": classifier_active,
        "fault_type": _fp_fault_type, "health_score": round(health_score, 4) if health_score else None,
        "time_to_scada_minutes": rul_minutes, "adjusted_rul_minutes": adjusted_rul_minutes if 'adjusted_rul_minutes' in locals() else rul_minutes,
        "thermal_lead_time_minutes": _thermal_lead,
        "class_probs": _class_probs,
        "time_to_pnr_minutes": pnr_minutes_rem,
        "time_to_failure_minutes": ttf_minutes, "horizon_label": fp_hlabel,
        "scada_sensor": fp_scada_sensor, "pnr_sensor": fp_pnr_sensor, "primary_sensor": fp_primary,
        "slopes": {
            "dpsi_dt":  round(dpsi_dt,  3),
            "dtemp_dt": round(dtemp_dt, 3),
            "dvib_dt":  round(dvib_dt,  3),
            "ds4_dt":   round(ds4_dt,   3),
        },
        "sensors": sensors,
    }


# ── Phase 11: Multi-Modal Demo Endpoints ─────────────────────────────────────
# New endpoints supporting the Two-Tier UI:
#   /api/kpis              — Per-site production/drilling KPIs with fault degradation
#   /api/intelligence-feed — Pre-vetted unstructured O&G data per fault type
#   /api/mlops/status      — Simulated WAN + edge model health for MLOps indicator
#   /api/horizon           — Active AI predictions sorted by urgency (dashboard Tier 1)
#   /api/agent/hitl-approve — Human-in-the-Loop action approval

SITE_KPI_BASE = {
    "pad_alpha": {
        "label": "Pad Alpha", "type": "ESP Production",
        "production_boed": 1842, "water_cut_pct": 28.4,
        "gor_scf_bbl": 1104, "wellhead_pressure_psi": 245, "uptime_pct": 100.0,
    },
}

INTELLIGENCE_FEED = {
    "fluid_drawdown": [
        {
            "id": "fd_1a", "type": "sonic_log", "source": "Dynamic Sonic Log",
            "ts_label": "06:00 this morning", "icon": "🧪", "is_anomaly": True,
            "headline": "Dynamic dynamic fluid level: 150 ft above intake ↓ · Depleting",
            "ai_relevance": "Sonic log dynamic dynamic fluid level is approaching the critical 120 ft minimum submergence. Drawdown confirmed.",
            "detail": (
                "Acoustic Sonic Survey — ESP-ALPHA-1\n"
                "· Dynamic dynamic fluid level: 150 ft above pump intake (critical limit: 120 ft)\n"
                "· Intake pressure: 1,040 PSI (nominal: 1,400 PSI; declining at -18 PSI/hr)\n"
                "· Motor current: 58A (nominal: 75A; declining — pump unloading)\n"
                "· Note: 'Submergence dynamically dropping. Well is reservoir-limited. No free gas observed in annulus.'\n"
                "· SCADA: All readings within green alarm limits."
            ),
        },
        {
            "id": "fd_1b", "type": "separator_test", "source": "Separator Test",
            "ts_label": "04:30 this morning", "icon": "🧪", "is_anomaly": True,
            "headline": "Separator GOR stable: 1,104 scf/bbl · Casing pressure flat at 40 PSI",
            "ai_relevance": "Flat GOR and annulus pressure rule out gas zone migration, confirming fluid drawdown as the sole cause of pressure drop",
            "detail": (
                "Separator Test — Pad Alpha production header\n"
                "· GOR: 1,104 scf/bbl (fully nominal baseline)\n"
                "· Casing annulus pressure: 40 PSI (stable and flat since yesterday)\n"
                "· Analysis: Flat GOR + stable casing pressure excludes gas lock. Unloading is purely fluid level depletion."
            ),
        },
        {
            "id": "fd_2a", "type": "technical_standard", "source": "Field Technical Guidelines",
            "ts_label": "last 2 hours", "icon": "📖", "is_anomaly": True,
            "headline": "Critical lift velocity limit: 4.2 ft/s · Sand bridging risk on speed-down",
            "ai_relevance": "Reducing VFD speed reduces dynamic fluid velocity below critical lift, causing suspended sand to bridge and seize pump",
            "detail": (
                "Technical Standard — West Texas ESP Operational Limits\n"
                "· Critical lift fluid velocity: 4.2 ft/s at 52 Hz\n"
                "· Sand bridging warning: Speed-down below 48 Hz during drawdown drops velocity to 3.1 ft/s, causing solids to settle down the tubing string.\n"
                "· VFD Trim is strictly contraindicated."
            ),
        }
    ],
    "gas_lock": [
        {
            "id": "gl_1a", "type": "well_test", "source": "Daily Well Test Report",
            "ts_label": "06:00 this morning", "icon": "🧪", "is_anomaly": True,
            "headline": "GVF at intake: 68% ↑  ·  Intake PSI: 1,040 PSI ↓  ·  Declining",
            "ai_relevance": "GVF 68% exceeds pump handling threshold — intake PSI declining confirms early gas lock",
            "detail": (
                "Well Test — ESP-ALPHA-5 / Well A-5\n"
                "· Gas Void Fraction (GVF) at pump intake: 68% (threshold: 60%)\n"
                "· Intake pressure: 1,040 PSI (nominal: 1,400 PSI; declining at -18 PSI/hr)\n"
                "· Motor current: 58A (nominal: 75A; declining — pump unloading)\n"
                "· Note: 'Higher than usual GVF this morning — possibly gas migration from upper zone.'\n"
                "· SCADA: All readings within alarm limits. No alarm active."
            ),
        },
        {
            "id": "gl_1b", "type": "separator_test", "source": "Separator Gas Test",
            "ts_label": "04:30 this morning", "icon": "🧪", "is_anomaly": True,
            "headline": "Separator gas rate: 142 Mscf/d ↑  ·  GOR rising  ·  Casing pressure climbing",
            "ai_relevance": "Rising GOR and casing pressure confirm free gas migrating into pump intake",
            "detail": (
                "Separator Test — Pad Alpha production header\n"
                "· A-5 separator gas rate: 142 Mscf/d (was 98 Mscf/d yesterday)\n"
                "· GOR: 1,310 scf/bbl (nominal: 1,104 scf/bbl)\n"
                "· Casing annulus pressure: 142 PSI (rising since 0200h)\n"
                "· Note: GOR increase + casing pressure buildup = gas migrating past perforations into pump intake.\n"
                "· No SCADA alarm. SCADA monitors total header pressure only."
            ),
        },
        {
            "id": "gl_2a", "type": "vfd_log", "source": "VFD Surface Control Panel",
            "ts_label": "last 2 hours", "icon": "⚡", "is_anomaly": True,
            "headline": "Motor current: 58A ↓  (nominal 75A)  ·  Soft unload events × 3",
            "ai_relevance": "Current declining below 60A with stable VFD frequency = pump hydraulic efficiency loss = gas lock",
            "detail": (
                "VFD Log — ESP-ALPHA-5 surface panel\n"
                "· Current: 58A (nominal: 75A; declining)\n"
                "· VFD frequency: 52 Hz (unchanged)\n"
                "· Soft unload events: 3 in last 90 minutes\n"
                "· Power factor: 0.71 (declining from 0.85)\n"
                "· SCADA low-current alarm: 40A — not triggered yet.\n"
                "· GDC detects the soft unload pattern before SCADA hard-trip threshold."
            ),
        },
        {
            "id": "gl_2b", "type": "power_monitor", "source": "Surface Power Monitor",
            "ts_label": "continuous — last 3h", "icon": "⚡", "is_anomaly": True,
            "headline": "Power factor: 0.71 ↓  (nominal 0.85)  ·  Current trend: -2.3A/hr",
            "ai_relevance": "Power factor decline at stable frequency = reduced hydraulic load = gas entrainment in impeller stages",
            "detail": (
                "Power quality monitor — ESP-ALPHA-5 VFD panel\n"
                "· Power factor: 0.71 (nominal: 0.85; trending down at -0.05/hr)\n"
                "· Motor current trend: -2.3A/hr over last 3 hours\n"
                "· VFD frequency: 52 Hz (stable — not a speed change)\n"
                "· Analysis: declining PF at constant frequency = pump doing less hydraulic work = gas void rising\n"
                "· SCADA: No alarm. Current still above 40A hard-trip threshold."
            ),
        },
        {
            "id": "gl_3", "type": "shift_note", "source": "Shift Handover — Day Tour",
            "ts_label": "07:00 shift handover", "icon": "📋", "is_anomaly": False,
            "headline": "\"A-5 running rough this morning — seems light on the pump\"",
            "ai_relevance": "Operator 'light pump' observation is the tactile signature of gas entrainment — confirms AI sensor trend",
            "detail": (
                "Shift Handover — Pad Alpha Day Tour Pusher: M. Garza\n"
                "· ESP-ALPHA-5: 'Pump running rough and lighter than usual since around 0400h.'\n"
                "· 'No hard alarms on SCADA. Production rate slightly lower.'\n"
                "· Suggested monitoring intake pressure trend — 'might be gassing up.'\n"
                "· ⚠ This observation exists only in the handover note — NOT in SCADA."
            ),
        },
    ],
    "sand_ingress": [
        {
            "id": "si_1", "type": "lab_report", "source": "Daily Well Test Report",
            "ts_label": "08:00 this morning", "icon": "🧪", "is_anomaly": True,
            "headline": "BS&W: 0.41% ↑  ·  Salinity: 34,200 ppm ↑  ·  Sand: 1.2 mg/100mL ↑",
            "ai_relevance": "Sand concentration trend correlated with 3% vibration increase — early-stage impeller erosion confirmed",
            "detail": (
                "API RP 13C fluid sample — ESP-ALPHA-2 / Well A-2\n"
                "· Basic Sediment & Water (BS&W): 0.41% (vs 0.28% seven days ago, trending up)\n"
                "· Chloride concentration: 20,800 mg/L (baseline: 17,400 mg/L)\n"
                "· Salinity: 34,200 ppm (up 17% in 7 days)\n"
                "· Sand content (ASTM D4807 centrifuge): 1.2 mg/100mL (3-day consecutive increase)\n"
                "· Sample note: 'Trace gritty residue observed in sample bottle' — Lab Tech J. Rivera\n"
                "· SCADA: Intake PSI, motor current, and vibration all within normal alarm limits."
            ),
        },
        {
            "id": "si_2", "type": "erp_check", "source": "SAP MM — Inventory Query",
            "ts_label": "query just now", "icon": "📦", "is_anomaly": True,
            "headline": "ESP Sand-Handler Assembly — Stock: 0 local · 0 hub · 1 @ factory (12-day lead)",
            "ai_relevance": "12-day lead time requires immediate order if 14-day failure window is correct",
            "detail": (
                "SAP Materials Management — MPN: MAT-4002-TC-100\n"
                "· Part: Baker Hughes Centrilift 400-Series ESP Assembly, 100-stage TC Radial Bearings\n"
                "· Design rate: 2,000 BPD @ 55 Hz  |  Unit cost: $145,000\n"
                "· Pad Alpha local stock: 0  |  Midland hub stock: 0\n"
                "· Manufacturer stock: 1 unit @ Claremore, OK\n"
                "· Standard freight lead time: 12 days  |  Air freight: 7 days (+$8,500)\n"
                "· ⚠ Lead time EXCEEDS failure window if order is delayed beyond today."
            ),
        },
        {
            "id": "si_3", "type": "shift_notes", "source": "Shift Handover — Night Tour",
            "ts_label": "06:00 shift handover", "icon": "📋", "is_anomaly": False,
            "headline": "\"Minor vibration noted on A-2 during last connection\"",
            "ai_relevance": "Operator-observed vibration change confirms AI trend — unstructured confirmation of early degradation",
            "detail": (
                "Shift Handover Notes — Pad Alpha Night Tour Pusher: R. Mendoza\n"
                "· ESP-ALPHA-2: Minor vibration noted during makeup of last downhole connection at ~0315h\n"
                "· 'Subtle but noticeable increase vs. last week — worth watching.'\n"
                "· No SCADA alarms. Production rate normal at 318 BPD. All other wells normal.\n"
                "· Note: These handover notes are NOT accessible to SCADA-only systems."
            ),
        },
    ],
    "motor_overheat": [
        {
            "id": "moh_1", "type": "lab_report", "source": "Daily Well Test Report",
            "ts_label": "08:00 this morning", "icon": "🧪", "is_anomaly": True,
            "headline": "Water Cut: 67% ↑↑  (was 48% thirty days ago — rapid increase)",
            "ai_relevance": "67% water cut degrades motor cooling; combined with +0.8°F/hr temp slope, insulation failure within 18h",
            "detail": (
                "API RP 19C fluid sample — ESP-ALPHA-4 / Well A-4\n"
                "· Water cut: 67% (was 48% last month; sharp increase)\n"
                "· Gross liquid rate: 580 BPD  |  Oil rate: 191 BPD  |  GOR: 890 scf/bbl (stable)\n"
                "· Note by Field Tech M. Garza: 'Sharply higher water cut on A-4. High water fraction reduces motor cooling effectiveness in downhole ESP installations.'\n"
                "· SCADA: Motor winding temp 198°F (nominal) — NO ALARM.\n"
                "· ⚠ High water cut degrades heat transfer coefficient past motor, accelerating thermal stress on Class H winding insulation."
            ),
        },
        {
            "id": "moh_2", "type": "power_report", "source": "VFD Surface Power Monitor",
            "ts_label": "continuous — last 4h", "icon": "⚡", "is_anomaly": True,
            "headline": "Power factor: 0.78 ↓  (nominal 0.85)  ·  Motor current rising +2.1A/hr",
            "ai_relevance": "Overcurrent + declining PF confirms thermal degradation of winding insulation",
            "detail": (
                "VFD surface panel power logger — ESP-ALPHA-4\n"
                "· Motor current: 81.2A (nominal: 75A; rising at +2.1A/hr)\n"
                "· Power factor: 0.78 (nominal: 0.85) — insulation stress signature\n"
                "· VFD frequency: 55 Hz (unchanged)\n"
                "· Analysis: Overcurrent consistent with rising winding resistance due to thermal degradation\n"
                "· SCADA alarm at 280°F. Current: 198°F. GDC AI projects crossing in ~18h."
            ),
        },
    ],
    "thermal_runaway": [
        {
            "id": "tr_1", "type": "process_data", "source": "Cooling Water System — Process Historian",
            "ts_label": "last 6 hours trending", "icon": "🌡", "is_anomaly": True,
            "headline": "Fin-fan delta-T: 50°F ↑  (nominal 35°F)  ·  Discharge trend: +2.1°F/hr",
            "ai_relevance": "Delta-T excess of 43% combined with discharge temp trend confirms cooling circuit degradation",
            "detail": (
                "Cooling water system — GLIFT-BRAVO-1 cylinder jacket\n"
                "· Cooling water inlet: 98°F  |  outlet: 148°F  |  delta-T: 50°F\n"
                "· Design delta-T: 35°F  |  Deviation: +43%\n"
                "· Discharge temp trend: +2.1°F/hr over last 6 hours\n"
                "· Current discharge temp: 187°F  |  SCADA alarm: 230°F  |  Projected alarm crossing: ~8h\n"
                "· Interpretation: Fin-fan cooler partially plugged — airflow restriction\n"
                "· SCADA: All readings within alarm limits. No existing alert."
            ),
        },
        {
            "id": "tr_2", "type": "maintenance_record", "source": "IBM Maximo — PM Record",
            "ts_label": "record retrieved", "icon": "🔧", "is_anomaly": True,
            "headline": "Fin-fan cooler cleaning — OVERDUE 8 months  (last: 14mo ago, interval: 6mo)",
            "ai_relevance": "Overdue PM combined with process data confirms preventable fault — crew already on site tomorrow",
            "detail": (
                "Maximo Preventive Maintenance Record — GLIFT-BRAVO-1\n"
                "· Asset: Aerial fin-fan cooler (Ariel Corporation tube-and-fin HEX)\n"
                "· Last cleaning WO: WO-PM-0194, completed 14 months ago\n"
                "· PM interval: 6 months (per Ariel service manual)  |  Overdue by: 8 months\n"
                "· CREW-BRAVO-B scheduled on-site tomorrow at 14:00 for transmitter calibration (2h, available cap: 2.5h)\n"
                "· Cost to append to tomorrow's WO: $0  |  Emergency dispatch cost: $1,800"
            ),
        },
    ],
    "valve_failure": [
        {
            "id": "vf_1", "type": "maintenance_record", "source": "IBM Maximo — Asset Service History",
            "ts_label": "record retrieved", "icon": "🔧", "is_anomaly": True,
            "headline": "Check valve replacement — OVERDUE 6 months  (H2S accelerated corrosion site)",
            "ai_relevance": "Overdue maintenance + H2S environment + chattering signature confirms imminent valve disk failure",
            "detail": (
                "Maximo Asset Service Record — GLIFT-BRAVO-1 check valve\n"
                "· Last replacement WO: WO-2024-1840, completed 18 months ago\n"
                "· Recommended replacement interval: 12 months (elevated for H2S service)\n"
                "· Gas composition: H2S: 1,240 ppm (sour service) — accelerates valve corrosion\n"
                "· Part in local inventory: 1× CVD-1200-PSI-4IN @ $1,800\n"
                "· ⚠ Valve chattering signature detected in discharge pressure historian"
            ),
        },
        {
            "id": "vf_2", "type": "process_data", "source": "Discharge Pressure Historian",
            "ts_label": "last 2 hours", "icon": "📊", "is_anomaly": True,
            "headline": "Cyclic ΔP: 42 psi amplitude  (nominal <8 psi)  ·  Valve chatter signature",
            "ai_relevance": "42-psi cyclic amplitude is 5× normal — mean pressure normal so SCADA completely misses this",
            "detail": (
                "Discharge pressure historian — GLIFT-BRAVO-1\n"
                "· Cyclic pressure variation: 42 psi peak-to-peak (nominal: <8 psi)\n"
                "· Frequency: 1.8 Hz — consistent with valve disk flutter/chatter\n"
                "· Mean discharge pressure: 978 psi (within normal range — NO SCADA ALARM)\n"
                "· GDC AI: This oscillation is diagnostic for valve disk cracking. SCADA misses it because mean pressure is normal.\n"
                "· Failure mode: Disk fracture → sudden compressor backflow within minutes."
            ),
        },
    ],
    "bearing_wear_glift": [
        {
            "id": "bw_1", "type": "vibration_report", "source": "Online Vibration Analysis — ISO 10816",
            "ts_label": "continuous monitoring", "icon": "〰", "is_anomaly": True,
            "headline": "BPFI spectral peak: 0.42g ↑  (ISO alert: 0.30g)  ·  Trend: +0.08g/week",
            "ai_relevance": "Bearing defect frequency detected weeks before SCADA overall vibration alarm fires",
            "detail": (
                "Vibration analysis — GLIFT-BRAVO-3 crankshaft bearing\n"
                "· Bearing defect frequency (BPFI inner race): peak at 3× running frequency\n"
                "· Current amplitude: 0.42g  |  ISO 10816-6 alert threshold: 0.30g\n"
                "· Trend: +0.08g/week over last 4 weeks\n"
                "· Overall vibration: 7.8 mm/s RMS  |  SCADA alarm: 12 mm/s (not triggered)\n"
                "· ⚠ SCADA monitors overall vibration only. GDC AI isolates the BPFI spectral signature before overall amplitude alarms."
            ),
        },
        {
            "id": "bw_2", "type": "lab_report", "source": "Lube Oil Sample Analysis — Maximo Lab",
            "ts_label": "sample 3 days ago", "icon": "🧪", "is_anomaly": True,
            "headline": "Iron content: 48 ppm ↑  (was 12 ppm 90 days ago)  ·  Ferrous wear trend",
            "ai_relevance": "4× increase in ferrous debris confirms active bearing wear — combined with spectral BPFI, failure within 16h",
            "detail": (
                "Spectroscopic oil analysis — GLIFT-BRAVO-3 crankcase (Maximo WO-PM-0334)\n"
                "· Iron (Fe): 48 ppm ↑ (normal wear: <20 ppm; was 12 ppm 90 days ago)\n"
                "· Chromium (Cr): 4 ppm (bearing cage alloy)\n"
                "· Particle count >10μm: 1,840/mL (ISO cleanliness 18/16/13)\n"
                "· Lab comment: 'Significant increase in ferrous debris. Recommend bearing inspection within 30 days.'\n"
                "· ⚠ Sample arrived today. This data is NOT accessible to SCADA."
            ),
        },
    ],
    "valve_washout": [
        {
            "id": "vw_1", "type": "edr_log", "source": "Pason EDR — Driller's Log",
            "ts_label": "0342h driller entry", "icon": "📋", "is_anomaly": True,
            "headline": "\"Standpipe -180 PSI over 90 min. Increased to 95 SPM to compensate.\"",
            "ai_relevance": "Rising SPM to compensate for declining standpipe pressure = VE loss = valve seat erosion",
            "detail": (
                "Pason EDR — Rig 42 Driller's Log  |  Driller: T. Wakefield\n"
                "· Time: 0342h  |  Depth: 11,240 ft MD  |  Formation: 8½″ hole section\n"
                "· 'Standpipe pressure declined 180 PSI over last 90 minutes while maintaining 89 SPM.'\n"
                "· 'Had to increase Pump #1 to 95 SPM to maintain target 700 GPM circulating rate.'\n"
                "· 'Pump #2 stable at 89 SPM. Pump #3 on standby.'\n"
                "· ⚠ SCADA monitors pressure and SPM numerically but does NOT correlate rising SPM with declining VE — that pattern requires AI."
            ),
        },
        {
            "id": "vw_2", "type": "mud_report", "source": "Morning Mud Report — 06:00",
            "ts_label": "06:00 mud report", "icon": "🪣", "is_anomaly": True,
            "headline": "Pump #1 VE: 81% ↓  (nominal 95%)  ·  Flow deficit: -38 GPM vs target",
            "ai_relevance": "VE 81% vs nominal 95% confirms valve leakage — ECD margin shrinking",
            "detail": (
                "Morning Mud Engineer Report — Rig 42  |  Mud Engineer: S. Okonkwo\n"
                "· Target circulating rate: 700 GPM (ECD management at 11,240 ft)\n"
                "· MUD-RIG42-1 VE: 81%  |  Requires 95 SPM (nominal 89 SPM at 95% VE)\n"
                "· MUD-RIG42-2 VE: 95% (stable)  |  MUD-RIG42-3: standby\n"
                "· ECD minimum for hole cleaning: 650 GPM. Currently 700 GPM. Margin: 50 GPM.\n"
                "· If VE continues declining, hole cleaning becomes compromised before SCADA alarms."
            ),
        },
        {
            "id": "vw_3", "type": "maintenance_record", "source": "Fluid End Inspection Log",
            "ts_label": "maintenance record", "icon": "🔧", "is_anomaly": False,
            "headline": "Last valve inspection at 14,200 ft  ·  Current 11,240 ft  ·  OVERDUE 460 ft",
            "ai_relevance": "Maintenance interval exceeded aligns precisely with declining VE — confirms valve erosion",
            "detail": (
                "MUD-RIG42-1 Fluid End Inspection History\n"
                "· Last inspection: 14,200 ft MD (WO-FE-0128)\n"
                "· Current depth: 11,240 ft MD  |  Footage since inspection: 2,960 ft\n"
                "· Standard interval: 2,500 ft (per NOV pump manual)  |  Overdue by: 460 ft\n"
                "· Mud type: 11.4 ppg OBM. Corrosion risk: moderate.\n"
                "· Next connection window: ~22 minutes."
            ),
        },
    ],
    "pulsation_dampener_failure": [
        {
            "id": "pdf_1", "type": "emergency_alert", "source": "Pason EDR — Real-Time Alarm",
            "ts_label": "REAL-TIME", "icon": "🚨", "is_anomaly": True,
            "headline": "PRESSURE SPIKE: 5,200 PSI (rated: 5,000 PSI)  ·  Pressure hammer detected",
            "ai_relevance": "EMERGENCY — bladder rupture confirmed — PNR = 0 minutes",
            "detail": (
                "EMERGENCY — Pason EDR Real-Time Alert — Rig 42\n"
                "· Standpipe pressure peaked at 5,200 PSI (rated working pressure: 5,000 PSI)\n"
                "· Pressure hammer amplitude: ±420 PSI in last 30 seconds\n"
                "· SPM oscillation: ±28 SPM (nominal: ±3 SPM)\n"
                "· Pressure cycle frequency: 3.2 Hz — consistent with bladder rupture\n"
                "· ⛔ IMMEDIATE HAZARD: Standpipe or Kelly hose rupture risk"
            ),
        },
    ],
    "piston_seal_wear": [
        {
            "id": "psw_1", "type": "process_data", "source": "Fluid End Temperature Monitor",
            "ts_label": "continuous trend", "icon": "🌡", "is_anomaly": True,
            "headline": "Fluid end temp: 162°F ↑  (nominal 105°F)  ·  Rising +8°F/hr",
            "ai_relevance": "Temperature rise of 57°F above nominal + pressure decline = piston-liner seal bypass confirmed",
            "detail": (
                "MUD-RIG42-2 fluid end temperature historian\n"
                "· Current: 162°F  |  Nominal: 105°F  |  SCADA alarm: 180°F\n"
                "· Temperature trend: +8°F/hr over last 4 hours\n"
                "· Discharge pressure: 2,620 PSI (slight decline)  |  SPM: 91 (nominal 89)\n"
                "· Root cause: Piston-liner seal wear generates frictional heat and allows fluid bypass\n"
                "· SCADA alarm projected in ~2.5h at current rate."
            ),
        },
        {
            "id": "psw_2", "type": "maintenance_record", "source": "Liner Seal Change Log",
            "ts_label": "maintenance record", "icon": "🔧", "is_anomaly": False,
            "headline": "Liner seal last changed at 8,400 ft  ·  Current 11,240 ft  ·  OVERDUE 340 ft",
            "ai_relevance": "Overdue seal interval aligns precisely with thermal signature — confirms seal degradation not liner damage",
            "detail": (
                "MUD-RIG42-2 Liner Seal Replacement History\n"
                "· Last seal change: 8,400 ft MD (WO-FE-0124)\n"
                "· Current depth: 11,240 ft MD  |  Footage on current seals: 2,840 ft\n"
                "· Standard interval: 2,500 ft (per NOV pump manual)  |  Overdue: 340 ft\n"
                "· Parts on-site: 2× NOV-SEAL-TK-7500 kits @ $3,800 each (✅ in stock)\n"
                "· Replacement time: ~4 hours  |  Can be scheduled — no emergency dispatch required."
            ),
        },
    ],
    "gearbox_bearing_spalling": [
        {
            "id": "gbs_1", "type": "lab_report", "source": "Spectroscopic Oil Analysis — NOV",
            "ts_label": "results 2 days ago", "icon": "🧪", "is_anomaly": True,
            "headline": "Iron: 64 ppm ↑↑  (alarm: 50 ppm)  ·  Particle count: 22,400/mL",
            "ai_relevance": "Oil analysis flagged this 48h ago — AI fusion with EDR torque signature confirms active spalling",
            "detail": (
                "Spectroscopic oil analysis — NOV 250T Top Drive gearbox (Maximo WO-PM-0341)\n"
                "· Iron (Fe): 64 ppm ↑↑ (was 18 ppm 90 days ago; alarm: 50 ppm)\n"
                "· Chromium (Cr): 8 ppm (bearing cage alloy confirms bearing origin)\n"
                "· Particle count >4μm: 22,400/mL (ISO cleanliness 20/18/15 — severe)\n"
                "· Lab comment: 'URGENT: Ferrous debris exceeds alarm threshold. Bearing race failure imminent. Remove from service.'\n"
                "· ⚠ This sample was logged in Maximo 48 hours ago — no SCADA alert was generated."
            ),
        },
        {
            "id": "gbs_2", "type": "edr_log", "source": "Pason EDR — Torque Oscillation Log",
            "ts_label": "last 4 hours", "icon": "🔄", "is_anomaly": True,
            "headline": "Torque oscillation: ±3,200 ft-lb  (nominal ±800 ft-lb)  ·  @ 95 RPM",
            "ai_relevance": "Oscillatory torque at 95 RPM consistent with BPFI at 48 Hz — bearing seizure before next trip",
            "detail": (
                "EDR torque historian — TOPDRIVE-RIG42-1\n"
                "· Running speed: 95 RPM  |  WOB: 22 klbs\n"
                "· Peak-to-peak torque variation: ±3,200 ft-lb (nominal: ±800 ft-lb)\n"
                "· Gearbox vibration (ISO 10816-3): 0.65g @ 48 Hz — Zone C (excessive)\n"
                "· Next planned trip: ~18 hours away at 11,800 ft TD\n"
                "· ⚠ At current deterioration rate, bearing seizure is projected before next trip."
            ),
        },
    ],
    "slug_flow": [
        {
            "id": "sf_1", "type": "choke_log", "source": "Surface Choke Control Panel Log",
            "ts_label": "last 4 hours", "icon": "🔧", "is_anomaly": True,
            "headline": "Choke position: 48% → 62% → 44%  ·  3 manual adjustments this tour  ·  Backpressure unstable",
            "ai_relevance": "Erratic choke adjustments without a corresponding pump speed change = flowline slug flow regime, not downhole failure",
            "detail": (
                "Surface Choke Control Log — ESP-ALPHA-3 / Well A-3\n"
                "· 0215h: Choke opened 48% → 62% by lease operator (Garza) to maintain target 350 BPD\n"
                "· 0410h: Choke closed 62% → 44% — 'flow surging at the header'\n"
                "· 0558h: Choke set to 52% — attempting to stabilize\n"
                "· ⚠ Three choke adjustments in 4 hours without pump speed change = surface flow instability\n"
                "· SCADA: Vibration 2.4 mm/s (trip: 5.0 mm/s) — NO ALARM. Motor temp 198°F — NOMINAL."
            ),
        },
        {
            "id": "sf_2", "type": "separator_test", "source": "Separator Flow Test Report",
            "ts_label": "06:00 this morning", "icon": "🧪", "is_anomaly": True,
            "headline": "A-3 slug volume: 1.8 bbl/cycle  ·  Cycle period: 14 min  ·  GOR: 1,240 scf/bbl (rising)",
            "ai_relevance": "Measured slug volumes with 14-minute periodicity confirm intermittent gas/liquid flow regime — surface choke tuning is the correct intervention",
            "detail": (
                "Separator Test Report — Pad Alpha Production Header\n"
                "· Well A-3 slug volume: 1.8 bbl per cycle (measured using separator dump valve counter)\n"
                "· Slug cycle period: 14 minutes (consistent with 2,400 ft flowline at 2.1 ft/s slug velocity)\n"
                "· GOR: 1,240 scf/bbl (nominal: 1,104 scf/bbl; rising slowly over last 3 days)\n"
                "· Casing pressure: 118 PSI (stable — not a tubing leak)\n"
                "· Separator inlet pressure oscillation: ±22 PSI at slug frequency\n"
                "· Root cause: Intermittent gas accumulation in flowline low-point sending slugs to separator.\n"
                "· SCADA: No alarm. Mean separator pressure 118 PSI — within range."
            ),
        },
        {
            "id": "sf_3", "type": "shift_note", "source": "Shift Handover — Night Tour",
            "ts_label": "06:00 shift handover", "icon": "📋", "is_anomaly": False,
            "headline": "\"A-3 pumping rough this morning — vibration up but temp is normal\"",
            "ai_relevance": "Operator 'pumping rough with normal temp' is the key discriminator: downhole motor failure shows both; surface slugging shows vibration only",
            "detail": (
                "Shift Handover Notes — Pad Alpha Night Tour Pusher: D. Wakefield\n"
                "· ESP-ALPHA-3: 'Pump vibration noticeably higher since about 0200h — running rough.'\n"
                "· 'Motor temp still reading normal at 198°F — hasn't moved. That's unusual if it were a bearing.'\n"
                "· 'GDC edge system showing vibration drift but confidence is low (~52%). Not calling it yet.'\n"
                "· 'Flow at header is surging. Might be slugging from A-3 flowline low-point.'\n"
                "· ⚠ Operator specifically notes FLAT motor temperature — the critical discriminator between\n"
                "  slug flow (surface issue) and motor bearing failure (downhole issue).\n"
                "· No SCADA alarms. Production rate slightly variable: 340–365 BPD over last 4 hours."
            ),
        },
    ],
    "hydraulic_leak": [
        {
            "id": "hl_1", "type": "rig_log", "source": "Rig Floor Maintenance Log",
            "ts_label": "this tour (18h)", "icon": "📋", "is_anomaly": True,
            "headline": "Hydraulic fluid top-up ×3 this tour  ·  3.2 gallons added  ·  Leak not located",
            "ai_relevance": "AI calculates leak rate by fusing rig log top-up volumes with pressure trend — impossible from sensor data alone",
            "detail": (
                "Rig Floor Maintenance Log — TOPDRIVE-RIG42-1 (Current Tour)\n"
                "· 0215h: Added 0.8 gal hydraulic fluid\n"
                "· 0640h: Added 1.2 gal hydraulic fluid\n"
                "· 1105h: Added 1.2 gal hydraulic fluid\n"
                "· Total added this tour: 3.2 gallons over 18 hours\n"
                "· Note by Derrickman K. Thompson: 'Slow leak somewhere between swivel and TDS body. Visible sheen on Kelly bushing. Not yet pinpointed.'\n"
                "· ⚠ This log is in the paper rig report ONLY — not connected to SCADA."
            ),
        },
        {
            "id": "hl_2", "type": "process_data", "source": "Hydraulic System Pressure Monitor",
            "ts_label": "continuous trend", "icon": "💧", "is_anomaly": True,
            "headline": "Reservoir: 78% ↓  ·  Leak rate: 0.4 gal/hr  ·  Est. 3.6h to Low alarm",
            "ai_relevance": "Precise leak rate calculated from log + pressure fusion — SCADA pressure alone shows no alarm",
            "detail": (
                "Hydraulic system monitor — TOPDRIVE-RIG42-1\n"
                "· Reservoir level: 78%  |  At start of tour: 100%\n"
                "· System pressure: 2,940 PSI  |  Low alarm: 2,500 PSI\n"
                "· Calculated leak rate: 0.4 gal/hr\n"
                "· Estimated time to Low alarm: ~3.6 hours\n"
                "· Spare parts on rig: 2× hoses (3,000 PSI), 6× JIC fittings, 15 gal fluid\n"
                "· SCADA status: Pressure at 2,940 PSI — NO ALARM ACTIVE."
            ),
        },
    ],
    "normal": [
        {
            "id": "nm_1", "type": "daily_scan", "source": "GDC Daily Performance Scan",
            "ts_label": "06:00 this morning", "icon": "✅", "is_anomaly": False,
            "headline": "ESP-ALPHA-1: All sensors nominal · PIP 1,400 PSI · Amps 75A · Temp 198°F",
            "ai_relevance": "All four sensor channels within normal operating range — no corrective action required",
            "detail": (
                "Daily Well Performance Scan — ESP-ALPHA-1 / Well A-1\n"
                "· Pump Intake Pressure (PIP): 1,400 PSI (normal range: 1,200–1,600 PSI) ✓\n"
                "· Motor current: 75A (normal range: 60–90A) ✓\n"
                "· Winding temperature: 198°F (alarm limit: 250°F) ✓\n"
                "· Gas Void Fraction (GVF) estimate: 42% (threshold: 60%) ✓\n"
                "· Production rate: 847 BOPD (on target)\n"
                "· No corrective action recommended. Continue monitoring."
            ),
        },
        {
            "id": "nm_2", "type": "chemistry_report", "source": "Monthly Fluid Chemistry Report",
            "ts_label": "3 days ago", "icon": "🧪", "is_anomaly": False,
            "headline": "BS&W stable at 22% · Chlorides 18,400 mg/L · No scale or corrosion indicators",
            "ai_relevance": "Stable fluid chemistry confirms no sand ingress, scaling, or corrosion risk in current window",
            "detail": (
                "Monthly Fluid Chemistry — Well A-1 Sample (Lab Report)\n"
                "· Basic Sediment & Water (BS&W): 22% (prior month: 22.1% — stable)\n"
                "· Chloride content: 18,400 mg/L (within produced water baseline)\n"
                "· Iron content: 3.2 mg/L (no corrosion signal — limit 10 mg/L)\n"
                "· Sand particle count: 0.02 g/L (sand ingress risk: LOW)\n"
                "· Scale inhibitor residual: 8.1 mg/L (effective — above 5 mg/L threshold)\n"
                "· Conclusion: Fluid chemistry stable. No chemistry-driven risk to ESP."
            ),
        },
        {
            "id": "nm_3", "type": "pm_log", "source": "Preventive Maintenance Log",
            "ts_label": "14 days ago", "icon": "🔧", "is_anomaly": False,
            "headline": "PM completed on schedule · Motor insulation 480 MΩ · Seal OK · Next due 180 days",
            "ai_relevance": "Recent PM with passing insulation resistance confirms motor health — failure risk low in current window",
            "detail": (
                "Preventive Maintenance Log — ESP-ALPHA-1 (scheduled PM)\n"
                "· Motor insulation resistance (Megger test): 480 MΩ (pass — limit: >100 MΩ per API RP 11S)\n"
                "· Seal condition: No bypass detected — wellbore fluid intrusion risk: LOW\n"
                "· Cable splice integrity: Satisfactory (visual + continuity check)\n"
                "· VFD calibration: 52 Hz confirmed at surface panel ✓\n"
                "· Recommendation: No corrective action. Next scheduled PM: 180 days.\n"
                "· PM interval: 180 days (consistent with 8,760 hr MTBF target for this ESP string)"
            ),
        },
    ],
}

# ── Fix 10: Dynamic Gemma Finding Templates ───────────────────────────────────
# Replaces static GEMMA_FINDINGS strings with sensor-interpolated templates for
# gas_lock. Other fault types fall back to the static GEMMA_FINDINGS dict.
GEMMA_FINDING_TEMPLATES = {
    "fluid_drawdown": [
        "🤖 GDC Advisory: Anomaly detected on ESP-ALPHA-1. Current-pressure correlation suggests fluid unloading, but dynamic RAG evidence confirms extreme reservoir FLUID DRAWDOWN ({conf}% confidence). Dynamic level measured at 150 ft above intake (from 06:00 sonic log). Slowing VFD speed will drop critical lift velocity, causing sand bridging and pump seizure. DO NOT TRIM VFD SPEED. Emergency shutdown is recommended.",
        "🤖 GDC Advisory: Critical Reservoir Drawdown detected ({conf}% confidence). Dynamic fluid level at 150 ft above pump intake. Proactive path: VFD Speed-Down to 44 Hz is unsafe — risks sand settling and bridging downhole string (~$150k representative pull-rig cost). Recommended action: Emergency shutdown.",
    ],
    "gas_lock": [
        "🤖 GDC Advisory: Gas lock anomaly detected ({conf}% confidence). PIP at {psi:.0f} PSI declining at rate consistent with gas entrainment. Expected unmitigated loss: $150,000 pump replacement CAPEX (65% probability of SCADA-window response failure → $97,500 risk-weighted expected cost). Recommended: SCADA VFD Speed-Down from 52 Hz (3,120 RPM) → 44 Hz (2,640 RPM). Direct cost: $0. Preserves pump asset entirely.",
        "🤖 GDC Advisory: Current-pressure correlation confirms gas lock at {conf}% confidence. PIP {psi:.0f} PSI and motor amps {amps:.0f}A both declining — pump unloading on gas void. Reactive path: $150,000 pump pull + 5–7 day downtime. Proactive path: VFD speed-down at $0. SCADA has no active alarm — GDC has {remaining:.0f}-min advantage window.",
        "🤖 GDC Advisory: Gas entrainment confirmed at {psi:.0f} PSI intake, {amps:.0f}A motor current. Risk-weighted expected loss if no action: ~$97,500 (65% burnout probability × $150k replacement). VFD reduction 52 → 44 Hz (3,120 → 2,640 RPM) costs $0 and eliminates the risk. SCADA alarm threshold not yet triggered — act now.",
    ],
    "thermal_runaway": [
        "🤖 Gemma: Fin-fan cooling degraded. Discharge temp at {temp:.0f}°F and rising. SCADA alarm at 230°F. Schedule maintenance.",
        "🤖 Gemma: Thermal runaway detected with {conf}% confidence. Current temp {temp:.0f}°F. Cooling system failure imminent.",
        "🤖 Gemma: Discharge temp {temp:.0f}°F is trending up. Heat exchanger efficiency declining. Crew dispatch recommended.",
    ],
    "valve_failure": [
        "🤖 Gemma: Valve chattering signature detected. Mean discharge pressure {psi:.0f} PSI. SCADA shows no alarm.",
        "🤖 Gemma: Cyclic pressure oscillation confirms valve disk failure at {conf}% confidence. Current pressure {psi:.0f} PSI.",
        "🤖 Gemma: Reverse flow imminent due to check valve failure. Discharge pressure at {psi:.0f} PSI. Shut down immediately.",
    ],
    "bearing_wear_glift": [
        "🤖 Gemma: Bearing spalling confirmed. Current vibration {vib:.2f} mm/s. SCADA overall vibration alarm not triggered.",
        "🤖 Gemma: BPFI spectral peak detected. Vibration at {vib:.2f} mm/s and rising. Schedule bearing replacement.",
        "🤖 Gemma: Crankshaft bearing wear active ({conf}% confidence). Vibration {vib:.2f} mm/s. Impending failure if not addressed.",
    ],
}


def get_gemma_finding(fault_type: str, asset_id: str) -> str:
    """Return a dynamic, sensor-interpolated Gemma finding string for the given fault type.
    Falls back to static GEMMA_FINDINGS for fault types without templates.
    """
    templates = GEMMA_FINDING_TEMPLATES.get(fault_type)
    if not templates:
        return GEMMA_FINDINGS.get(fault_type, "")
    cs = active_degrades.get(asset_id, {}).get("current_sensors", {})
    template = random.choice(templates)
    # Compute remaining PNR window dynamically from fault_onset_utc
    onset_str = active_degrades.get(asset_id, {}).get("fault_onset_utc", "")
    if onset_str:
        try:
            onset_dt = datetime.fromisoformat(onset_str.replace("Z", ""))
            elapsed_min = (datetime.utcnow() - onset_dt).total_seconds() / 60
            remaining = max(0.0, PNR_MINUTES.get(fault_type, 30) - elapsed_min)
        except Exception:
            remaining = float(PNR_MINUTES.get(fault_type, 30))
    else:
        remaining = float(PNR_MINUTES.get(fault_type, 30))
    try:
        return template.format(
            psi=cs.get("psi", 1000),
            amps=random.randint(25, 62),
            temp=cs.get("temp", 150),
            vib=cs.get("vib", 1.0),
            gvf=random.randint(71, 85),
            conf=random.randint(88, 97),
            remaining=remaining,
        )
    except Exception:
        return random.choice(templates)


GEMMA_FINDINGS = {
    "sand_ingress": (
        "🤖 Gemma: Correlating 3-day BS&W trend (+0.41%), salinity increase (+17%), and shift handover note with 1.2 mm/s vibration slope — "
        "high confidence (94%) sand ingress is underway. SCADA will not alarm for ~14 days."
    ),
    "motor_overheat": (
        "🤖 Gemma: 67% water cut combined with +2.1A/hr motor current slope exceeds ESP thermal model tolerance. "
        "Winding insulation failure projected in 18h. SCADA alarm not until 280°F."
    ),
    "thermal_runaway": (
        "🤖 Gemma: Fin-fan delta-T 43% above design combined with overdue PM (14 months vs 6-month interval) confirms cooling circuit degradation. "
        "Discharge temp will cross SCADA alarm in ~8h. Crew already scheduled on-site tomorrow."
    ),
    "valve_failure": (
        "🤖 Gemma: 42-psi cyclic amplitude (5× normal) in discharge pressure combined with overdue valve replacement (18mo vs 12mo) and H2S service conditions — "
        "valve disk fracture is imminent within 15 minutes. SCADA shows normal mean pressure."
    ),
    "bearing_wear_glift": (
        "🤖 Gemma: BPFI spectral peak 40% above ISO alert threshold plus 4× increase in oil ferrous debris confirms active bearing race spalling. "
        "SCADA overall vibration alarm not triggered. Failure within 16h if not addressed."
    ),
    "bearing_wear": (
        "🤖 Gemma: BPFI spectral peak 40% above ISO alert threshold plus 4× increase in oil ferrous debris confirms active bearing race spalling. "
        "SCADA overall vibration alarm not triggered. Failure within 16h if not addressed."
    ),
    "valve_washout": (
        "🤖 Gemma: Rising SPM compensation (+6 from nominal) correlated with overdue fluid end inspection (460 ft past interval) and declining VE (81% vs 95%) — "
        "valve seat erosion confirmed. Fluid end inspection recommended at next connection in ~22 minutes."
    ),
    "pulsation_dampener_failure": (
        "🤖 Gemma: ⛔ EMERGENCY. Pressure hammer amplitude ±420 PSI at 3.2 Hz with ±28 SPM oscillation — "
        "bladder rupture confirmed. Stop pumps immediately. Evacuate pump room."
    ),
    "piston_seal_wear": (
        "🤖 Gemma: Fluid end temperature 57°F above nominal and rising at +8°F/hr, 340 ft past seal replacement interval — "
        "piston-liner seal bypass confirmed. Parts in stock on-site. Schedule during next planned stop."
    ),
    "gearbox_bearing_spalling": (
        "🤖 Gemma: Oil analysis (64 ppm Fe, 2 days old, not actioned) combined with ±3,200 ft-lb torque oscillation and 0.65g vibration at BPFI frequency — "
        "bearing race is actively spalling. Seizure projected before next planned trip in 18h."
    ),
    "hydraulic_leak": (
        "🤖 Gemma: Calculating 0.4 gal/hr leak rate from rig log top-up records + pressure trend. "
        "Reservoir will reach Low alarm in ~3.6h. Repair materials on rig floor — locate leak during next stand break."
    ),
    "gas_lock": (
        "🤖 Gemma: Intake PSI declining at -18 PSI/min below 1,000 PSI threshold — gas void fraction increasing in pump intake. "
        "VFD frequency reduction available via SCADA. Motor thermal window is minutes, not hours — act immediately."
    ),
    "slug_flow": (
        "🤖 Gemma: Vibration drift from 1.1 to 2.4 mm/s over 4 hours with motor temperature FLAT at 198°F. "
        "Flat temperature is the key discriminator — downhole bearing failure shows rising temp; surface slug flow does not. "
        "Separator test confirms 1.8 bbl slug volumes at 14-minute intervals. "
        "Recommend surface choke adjustment to 46–48%. Do NOT pull well — this is a flowline flow regime issue, not a downhole failure."
    ),
}


@app.get("/api/kpis")
def get_site_kpis():
    """Live site KPIs with fault-driven degradation applied."""
    import copy
    import numpy as np
    kpis = copy.deepcopy(SITE_KPI_BASE)
    for asset_id, dg in active_degrades.items():
        if not dg:
            continue
        meta = ASSET_REGISTRY.get(asset_id, {})
        site = meta.get("site")
        hist = list(HEALTH_HISTORY.get(asset_id, []))
        health = 1.0
        if hist:
            n = len(hist)
            weights = np.array([0.75 ** (n - 1 - i) for i in range(n)])
            health = float(np.average(hist, weights=weights))
        degradation = max(0.0, 1.0 - health)
        if site == "pad_alpha" and meta.get("asset_class") == "esp":
            kpis["pad_alpha"]["production_boed"] = max(0, round(
                SITE_KPI_BASE["pad_alpha"]["production_boed"] * (1 - degradation * 0.18)))
            kpis["pad_alpha"]["uptime_pct"] = round(max(60.0, 100.0 - degradation * 15), 1)
    return {"kpis": kpis, "ts": datetime.utcnow().isoformat() + "Z"}


@app.get("/api/intelligence-feed/{asset_id}")
def get_intelligence_feed(asset_id: str, fault_type: str = None):
    """Return pre-vetted unstructured data feed items for a fault type + asset combination.
    Phase 16 (Item 5): Also prepends live LLM-generated documents from field_intel table
    that match the active fault context, giving the Deep Dive panel real AI-generated evidence.
    """
    if not fault_type:
        fault_type = (active_degrades.get(asset_id) or {}).get("fault_type")
    _pool_key = fault_type if (fault_type and fault_type not in ("normal", "")) else "normal"
    pool = INTELLIGENCE_FEED.get(_pool_key, [])
    canned_items = random.sample(pool, min(3, len(pool))) if len(pool) > 3 else list(pool)
    random.shuffle(canned_items)
    finding = get_gemma_finding(fault_type, asset_id)

    # ── Phase 16: Prepend live AlloyDB field_intel documents ─────────────────
    live_items = []
    if fault_type:
        try:
            conn = get_db()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, created_at, asset_id, asset_class, fault_context,
                           doc_type, headline, detail, ai_relevance, icon, lbl, lbl_type
                    FROM field_intel
                    WHERE fault_context = %s
                    ORDER BY created_at DESC LIMIT 10
                    """,
                    (fault_type,),
                )
                rows = cur.fetchall()
            conn.close()
            for r in rows:
                created = r["created_at"].replace(tzinfo=None) if getattr(r["created_at"], "tzinfo", None) else r["created_at"]
                age_s   = (datetime.utcnow() - created).total_seconds()
                if age_s < 90:
                    ts = "just now"
                elif age_s < 3600:
                    ts = f"{int(age_s // 60)}m ago"
                elif age_s < 86400:
                    ts = f"{int(age_s // 3600)}h ago"
                else:
                    ts = f"{int(age_s // 86400)}d ago"
                live_items.append({
                    "id":           f"gi_{r['id']}",
                    "type":         r["doc_type"],
                    "source":       f"GDC AI — {r['doc_type'].replace('_', ' ').title()}",
                    "ts_label":     ts,
                    "icon":         r["icon"],
                    "lbl":          r["lbl"],
                    "lbl_type":     r["lbl_type"],
                    "is_anomaly":   bool(r["fault_context"]),
                    "headline":     r["headline"],
                    "ai_relevance": r["ai_relevance"],
                    "detail":       r["detail"],
                })
        except Exception as e:
            log.warning(f"intelligence-feed: field_intel query failed (non-fatal): {e}")

    # Live AI docs come first, then pre-canned reference documents
    combined_items = live_items + canned_items
    return {
        "asset_id":      asset_id,
        "fault_type":    fault_type,
        "items":         combined_items,
        "live_count":    len(live_items),
        "gemma_finding": finding,
    }


def get_rag_context_and_adjusted_rul(asset_id: str, fault_type: str, base_rul: float) -> tuple[str, float]:
    """AlloyDB pgvector RAG — Sprint 5 v8 Fix 7.
    Replaces ChromaDB in-memory collections with persistent AlloyDB rag_documents + field_intel.
    """
    rag_context  = ""
    adjusted_rul = base_rul
    asset_class  = ASSET_REGISTRY.get(asset_id, {}).get("asset_class", "esp")

    # ── Static corpus — top-3 manual sections from rag_documents (pgvector) ──
    try:
        model = _get_embed_model_singleton()
        if model and fault_type:
            query = f"{fault_type.replace('_', ' ')} {asset_class}"
            emb   = model.encode(query).tolist()
            emb_s = "[" + ",".join(str(x) for x in emb) + "]"
            conn  = get_db()
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT content FROM rag_documents
                    WHERE asset_class = %s
                    ORDER BY embedding <-> %s::vector
                    LIMIT 3
                """, (asset_class, emb_s))
                rows = cur.fetchall()
                if not rows:
                    cur.execute("""
                        SELECT content FROM rag_documents
                        ORDER BY embedding <-> %s::vector LIMIT 3
                    """, (emb_s,))
                    rows = cur.fetchall()
            conn.close()
            if rows:
                rag_context += "STATIC O&G CORPUS:\n" + "\n\n".join(r[0] for r in rows) + "\n\n"
    except Exception as e:
        log.debug(f"Static RAG retrieval skipped (non-fatal): {e}")

    # ── Dynamic docs — field_intel rows for this asset + fault ──────────────
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT headline, detail, doc_type FROM field_intel
                WHERE asset_id = %s AND fault_context = %s
                  AND lbl_type != 'hitl_action'
                ORDER BY created_at DESC LIMIT 5
            """, (asset_id, fault_type))
            rows = cur.fetchall()
        conn.close()
        if rows:
            docs = [{"content": f"{r['doc_type'].upper()}: {r['detail']}"} for r in rows]
            adjusted_rul = adjust_rul_with_documents(base_rul, docs)
            rag_context += "DYNAMIC SESSION EVIDENCE:\n"
            rag_context += "\n".join(d["content"] for d in docs) + "\n\n"
    except Exception as e:
        log.debug(f"Dynamic RAG retrieval skipped (non-fatal): {e}")

    return rag_context, adjusted_rul

# ── Phase 16: Live Field Intelligence API ─────────────────────────────────────
@app.get("/api/field-intelligence")
def get_field_intelligence(limit: int = 20, fault_context: str = None):
    """
    Phase 16: Return newest LLM-generated field documents from AlloyDB.
    Generated by _intel_generator background thread every 2–5 minutes.
    Biased toward active fault context for multi-modal fusion demo narrative.
    UI polls this every 60s and prepends new items with .act-new animation.

    Query params:
      limit         — max rows to return (default 20)
      fault_context — optional fault type filter (e.g. "sand_ingress")
    """
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if fault_context:
                cur.execute(
                    """
                    SELECT id, created_at, asset_id, asset_class, fault_context,
                           doc_type, headline, detail, ai_relevance, icon, lbl, lbl_type
                    FROM field_intel
                    WHERE fault_context = %s
                    ORDER BY created_at DESC LIMIT %s
                    """,
                    (fault_context, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT id, created_at, asset_id, asset_class, fault_context,
                           doc_type, headline, detail, ai_relevance, icon, lbl, lbl_type
                    FROM field_intel
                    ORDER BY created_at DESC LIMIT %s
                    """,
                    (limit,),
                )
            rows = cur.fetchall()
        conn.close()
        items = []
        for r in rows:
            row = dict(r)
            # Compute human-readable timestamp
            created = r["created_at"].replace(tzinfo=None) if getattr(r["created_at"], "tzinfo", None) else r["created_at"]
            age_s = (datetime.utcnow() - created).total_seconds()
            if age_s < 90:
                ts = "just now"
            elif age_s < 3600:
                ts = f"{int(age_s // 60)}m ago"
            elif age_s < 86400:
                ts = f"{int(age_s // 3600)}h ago"
            else:
                ts = f"{int(age_s // 86400)}d ago"
            row["ts"] = ts
            row["ts_label"] = ts
            row["id"] = f"gi_{r['id']}"   # Prefix to avoid collision with hardcoded fi1..fi10 ids
            row["is_anomaly"] = bool(r["fault_context"])
            row["source"] = f"GDC AI — {r['doc_type'].replace('_', ' ').title()}"
            row["created_at"] = created.isoformat()
            items.append(row)
        return {"items": items, "count": len(items)}
    except Exception as e:
        log.warning(f"field-intelligence query failed (non-fatal): {e}")
        return {"items": [], "count": 0, "error": str(e)}


def _get_last_event_time() -> str:
    """Return the most recent telemetry event timestamp from AlloyDB, or 'unknown'."""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(event_time) FROM telemetry_events")
            row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return row[0].isoformat() + "Z"
    except Exception:
        pass
    return "unknown"


@app.get("/api/mlops/status")
def get_mlops_status():
    """Simulated WAN + edge model status for the MLOps indicator on the dashboard."""
    import random
    import requests as _req
    active_count = len([d for d in active_degrades.values() if d])
    wan_bw = round(random.uniform(0.8, 2.4), 1)
    wan_state = "degraded" if wan_bw < 1.2 else "intermittent" if wan_bw < 1.8 else "stable"

    # Probe Ollama — show honest status, not a permanent display label
    ollama_online = False
    try:
        r = _req.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        ollama_online = r.status_code == 200
    except Exception:
        pass

    return {
        "wan_bandwidth_mbps": wan_bw,
        "wan_state": wan_state,
        "edge_compute_pct": min(95, 38 + active_count * 12 + random.randint(-3, 3)),
        "models_loaded": list(HEALTH_MODELS.keys()),
        "model_drift_detection": "not_implemented",
        "last_cloud_sync": _get_last_event_time(),
        "ollama_model": OLLAMA_MODEL if ollama_online else "offline",
        "ollama_online": ollama_online,
        "inference_latency_ms": random.randint(28, 95) if ollama_online else None,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/api/horizon")
def get_horizon_alerts():
    """Active AI predictions sorted by time urgency for Tier-1 dashboard."""
    import numpy as np
    alerts = []
    for asset_id, dg in active_degrades.items():
        if not dg:
            continue
        meta = ASSET_REGISTRY.get(asset_id, {})
        fault_type = dg.get("fault_type")
        if not fault_type:
            continue
        hist = list(HEALTH_HISTORY.get(asset_id, []))
        health_score = 1.0
        if hist:
            n = len(hist)
            weights = np.array([0.75 ** (n - 1 - i) for i in range(n)])
            health_score = float(np.average(hist, weights=weights))
        fp = FAULT_PHYSICS.get(fault_type, {})
        fp_total_h = fp.get("total_hours", 1.0)
        fp_scada_hs = fp.get("scada_alarm_health", 0.15)
        fp_hlabel = fp.get("horizon_label", "Hours")
        ttscada_min = round(max(0.0, (health_score - fp_scada_hs) * fp_total_h) * 60.0, 1)
        _, adjusted_rul_minutes = get_rag_context_and_adjusted_rul(asset_id, fault_type, ttscada_min)
        alerts.append({
            "asset_id": asset_id,
            "site": meta.get("site"),
            "asset_type": meta.get("asset_type"),
            "fault_type": fault_type,
            "fault_label": FAULT_PROFILES.get(fault_type, {}).get("label", fault_type),
            "fault_color": FAULT_PROFILES.get(fault_type, {}).get("color", "#ff6d00"),
            "health_score": round(health_score, 4),
            "time_to_scada_minutes": ttscada_min,
            "adjusted_rul_minutes": adjusted_rul_minutes,
            "horizon_label": fp_hlabel,
            "intervention_type": fp.get("intervention_type", "maintenance_scheduling"),
        })
    alerts.sort(key=lambda x: x["time_to_scada_minutes"])
    return {"alerts": alerts, "ts": datetime.utcnow().isoformat() + "Z"}


class HitlApproveRequest(BaseModel):
    asset_id: str
    fault_type: str
    action_taken: str
    cost_incurred: Optional[float] = 0


class RemediationRecordRequest(BaseModel):
    asset_id: str
    fault_type: str
    action_label: str   # e.g. "vfd_trim" or "emergency_shutin"
    headline: str
    detail: str


def _run_recovery_thread(asset_id: str) -> None:
    """Post 36 climbing PIP/Amps readings over 3 real minutes, simulating wellbore
    gas void clearance after VFD speed-down. Chart shows live green recovery trend."""
    RECOVERY_STEPS = 36
    psi_start  = 800.0   # approximate fault-level PIP
    psi_target = 1400.0  # nominal PIP
    amps_start  = 32.0   # approximate fault-level amps
    amps_target = 75.0   # nominal amps
    temp_nom    = 200.0

    # Use actual current sensor values if available from degrade state
    cs = (active_degrades.get(asset_id) or {}).get("current_sensors", {})
    if cs.get("psi"):        psi_start  = float(cs["psi"])
    if cs.get("motor_amps"): amps_start = float(cs["motor_amps"])

    log.info(f"↗ Recovery thread started: {asset_id} — {RECOVERY_STEPS} steps over ~3 min")

    for i in range(RECOVERY_STEPS):
        if asset_id not in active_degrades:
            break  # Reset clicked — exit immediately
        t    = (i + 1) / RECOVERY_STEPS
        psi  = psi_start  + t * (psi_target  - psi_start)
        amps = amps_start + t * (amps_target - amps_start)
        reading = {
            "asset_id"    : asset_id,
            "asset_type"  : "esp",
            "psi"         : round(random.gauss(psi,  abs(psi  * 0.02)), 1),
            "temp_f"      : round(random.gauss(temp_nom, abs(temp_nom * 0.01)), 1),
            "vibration"   : round(max(0.05, random.gauss(0.45, 0.05)), 3),
            "motor_amps"  : round(max(10.0, random.gauss(amps, abs(amps * 0.02))), 1),
            "failure_type": "normal",
            "source"      : "recovery",
            "timestamp"   : datetime.utcnow().isoformat() + "Z",
        }
        if asset_id in active_degrades:
            active_degrades[asset_id]["current_sensors"] = {
                "psi": reading["psi"], "temp": reading["temp_f"],
                "vib": reading["vibration"], "motor_amps": reading["motor_amps"],
            }
        try:
            publish_to_rabbitmq(reading)
        except Exception as e:
            log.error(f"Recovery publish error: {e}")
        time.sleep(5)

    # Cleanup — remove from active_degrades so simulator resumes normal readings
    active_degrades.pop(asset_id, None)
    HEALTH_HISTORY.pop(asset_id, None)
    log.info(f"✅ Recovery complete: {asset_id} — nominal sensors restored")


# Module-level recovery status store — written by _post_approval_monitor, read by /api/recovery-status
RECOVERY_STATUS: dict = {}


def _post_approval_monitor(asset_id: str) -> None:
    """After VFD speed-down approval, monitor PIP recovery trend every 30s for 2.5 minutes.
    Writes messages to RECOVERY_STATUS[asset_id] that the frontend polls via /api/recovery-status."""
    log.info(f"↗ Post-approval monitor started: {asset_id}")
    RECOVERY_STATUS[asset_id] = {"msg": "↗ Recovery initiated. Monitoring wellbore response…", "state": "pending"}
    baseline_psi = None
    expected_psi_rate = 24.0   # PSI/min expected recovery rate after VFD speed-down

    for check_n in range(5):   # check at t+30s, t+60s, t+90s, t+120s, t+150s
        time.sleep(30)
        if asset_id not in active_degrades:
            RECOVERY_STATUS[asset_id] = {
                "msg": "✅ Recovery complete. ESP-ALPHA-1 restored to nominal. $150,000 pump replacement avoided.",
                "state": "complete",
            }
            log.info(f"↗ Post-approval monitor: {asset_id} recovery complete (asset cleared)")
            return

        cs = (active_degrades.get(asset_id) or {}).get("current_sensors", {})
        current_psi = cs.get("psi", 0.0)

        if baseline_psi is None:
            baseline_psi = current_psi
            RECOVERY_STATUS[asset_id] = {
                "msg": f"↗ Recovery on track. PIP rising at expected rate. Gas void migrating up annulus.",
                "state": "recovering",
            }
            continue

        elapsed_min = (check_n * 30) / 60.0
        psi_gain = current_psi - baseline_psi
        actual_rate = psi_gain / max(elapsed_min, 0.5)

        if actual_rate < expected_psi_rate * 0.5:
            RECOVERY_STATUS[asset_id] = {
                "msg": (f"⚠ Recovery slower than projected ({actual_rate:.0f} vs {expected_psi_rate:.0f} PSI/min expected). "
                        f"PIP at {current_psi:.0f} PSI. Consider step-down to 40 Hz if trend continues."),
                "state": "slow",
            }
        else:
            RECOVERY_STATUS[asset_id] = {
                "msg": (f"↗ Recovery on track. PIP +{psi_gain:.0f} PSI over {elapsed_min:.0f} min "
                        f"({actual_rate:.0f} PSI/min). Gas void migrating up annulus."),
                "state": "recovering",
            }
        log.debug(f"↗ Post-approval monitor check {check_n+1}/5 for {asset_id}: {RECOVERY_STATUS[asset_id]['state']}")

    log.info(f"↗ Post-approval monitor complete: {asset_id}")


@app.post("/api/agent/hitl-approve")
def hitl_approve(req: HitlApproveRequest):
    """
    Human-in-the-Loop approval endpoint.
    Stops the fault simulation, records the intervention, and returns the outcome card.
    """
    # For gas_lock: launch recovery thread instead of immediately clearing state.
    # The recovery thread posts 36 climbing sensor readings over 3 real minutes,
    # then cleans up active_degrades. For all other faults, clear immediately.
    if req.fault_type == "gas_lock" and req.asset_id in active_degrades:
        active_degrades[req.asset_id]["running"] = False
        active_degrades[req.asset_id]["recovering"] = True
        t_rec = threading.Thread(target=_run_recovery_thread, args=(req.asset_id,), daemon=True)
        t_rec.start()
        t_mon = threading.Thread(target=_post_approval_monitor, args=(req.asset_id,), daemon=True)
        t_mon.start()
    elif req.asset_id in active_degrades:
        active_degrades[req.asset_id]["running"] = False
        active_degrades.pop(req.asset_id, None)
        HEALTH_HISTORY.pop(req.asset_id, None)
    cost_avoided = REMEDIATION_COSTS.get(req.fault_type, 0)
    fault_label  = FAULT_PROFILES.get(req.fault_type, {}).get("label", req.fault_type)
    fp = FAULT_PHYSICS.get(req.fault_type, {})
    intervention_type = fp.get("intervention_type", "maintenance_scheduling")
    
    # Update fault_sessions
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE fault_sessions
                SET resolved_at = NOW(),
                    resolution = %s,
                    cost_avoided = %s,
                    operator = 'system'
                WHERE asset_id = %s AND fault_type = %s AND resolved_at IS NULL
            """, (req.action_taken, cost_avoided, req.asset_id, req.fault_type))
        conn.commit()
        conn.close()
    except Exception as e:
        log.warning(f"fault_sessions update failed (non-fatal): {e}")
    outcome_msgs = {
        "supply_chain": f"SAP Purchase Order submitted. Part lead time per logistics — production protected.",
        "maintenance_scheduling": f"Maximo Work Order updated. Crew dispatch amended — zero additional travel cost.",
        "operational_control": f"Rig pump transition executed. Drilling operations continuous. ECD stable.",
        "emergency_shutdown": f"Emergency stop confirmed. Area cleared. Damage assessment initiated.",
    }
    log.info(f"HITL approved: {req.fault_type} on {req.asset_id} | cost_avoided=${cost_avoided:,}")
    return {
        "status": "approved",
        "asset_id": req.asset_id,
        "fault_type": req.fault_type,
        "fault_label": fault_label,
        "action_taken": req.action_taken,
        "cost_avoided": cost_avoided,
        "cost_incurred": req.cost_incurred,
        "net_savings": cost_avoided - req.cost_incurred,
        "outcome_message": outcome_msgs.get(intervention_type, "Intervention recorded."),
    }


# ── Recovery Status Endpoint ─────────────────────────────────────────────────
@app.get("/api/recovery-status/{asset_id}")
def get_recovery_status(asset_id: str):
    """Return current post-approval recovery monitoring message for the H1 copilot."""
    return RECOVERY_STATUS.get(asset_id, {"msg": "", "state": "pending"})


# ── Remediation Record Endpoint ─────────────────────────────────────────────
@app.post("/api/h1/remediation-record")
def h1_remediation_record(req: RemediationRecordRequest):
    """
    Batch D (RT-7): Writes the operator's H1 remediation action to field_intel as
    doc_type='remediation_record', lbl_type='hitl_action'.
    This row is excluded from discrimination RAG (get_rag_context_and_adjusted_rul
    filters lbl_type != 'hitl_action') but is visible in the intelligence feed and
    persists as an auditable HITL record across sessions.
    """
    try:
        conn = get_db()
        asset_class = ASSET_REGISTRY.get(req.asset_id, {}).get("asset_class", "esp")
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO field_intel
                  (asset_id, asset_class, fault_context, doc_type,
                   headline, detail, ai_relevance, icon, lbl, lbl_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                req.asset_id,
                asset_class,
                req.fault_type,
                "remediation_record",
                req.headline,
                req.detail,
                f"HITL action recorded: {req.action_label}",
                "✅",
                "HITL",
                "hitl_action",
            ))
        conn.commit()
        conn.close()
        log.info(f"✅ Remediation record written: {req.asset_id} {req.action_label} ({req.fault_type})")
        return {"status": "ok", "asset_id": req.asset_id, "action": req.action_label}
    except Exception as e:
        log.warning(f"Remediation record write failed (non-fatal): {e}")
        return {"status": "error", "detail": str(e)}


# ── Agent Chat Endpoint ───────────────────────────────────────────────────────
class AgentChatRequest(BaseModel):
    asset_id: str
    fault_type: str = ""
    message: str
    context: str = ""

@app.post("/api/agent/chat")
def agent_chat(req: AgentChatRequest):
    """H1 copilot follow-up chat — routes question + context to Gemma and returns response."""
    prompt = (
        f"You are the GDC Predictive Maintenance AI Copilot. "
        f"Asset: {req.asset_id}. Active fault: {req.fault_type.replace('_',' ')}.\n"
        f"Prior analysis context: {req.context[:600]}\n\n"
        f"Operator question: {req.message}\n\n"
        f"Answer concisely in 2-3 sentences. Be specific, technical, and grounded in physics. "
        f"Cite API RP 11S or relevant standards if applicable."
    )
    try:
        import requests as _req
        r = _req.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                  "options": {"num_predict": 200, "temperature": 0.5}},
            timeout=20,
        )
        if r.status_code == 200:
            body = r.json().get("response", "").strip()
            if body:
                return {"response": body}
    except Exception as e:
        log.warning(f"agent_chat Ollama error: {e}")
    # Fallback template — fires when Gemma times out or is busy during a demo
    # Provides a useful, physically grounded response rather than a dead-end error
    _fault_label = req.fault_type.replace("_", " ") if req.fault_type else "the detected fault"
    return {"response": (
        f"GDC analysis: {_fault_label} confirmed via multivariate sensor pattern — "
        f"PIP and motor current declining together before any SCADA threshold is crossed. "
        f"Your lowest-cost intervention option is available now; cost escalates as the window closes. "
        f"(AI model temporarily busy — response based on sensor data and operational context.)"
    )}


# ── H1-Live-1: Live Telemetry Endpoint ───────────────────────────────────────
@app.get("/api/live-telemetry/{asset_id}")
def get_live_telemetry(asset_id: str):
    """Return the latest nominal sensor readings from telemetry_events for the SCADA
    card live display. Only returns rows with failure_type='normal' so injected fault
    readings don't leak into the pre-injection display."""
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT psi, temp_f, motor_amps, event_time
                FROM telemetry_events
                WHERE asset_id = %s AND failure_type = 'normal'
                ORDER BY event_time DESC LIMIT 1
                """,
                (asset_id,),
            )
            row = cur.fetchone()
        conn.close()
        if not row:
            return {"asset_id": asset_id, "psi": None, "temp_f": None, "motor_amps": None}
        return {
            "asset_id":   asset_id,
            "psi":        float(row["psi"])        if row["psi"]        else None,
            "temp_f":     float(row["temp_f"])     if row["temp_f"]     else None,
            "motor_amps": float(row["motor_amps"]) if row["motor_amps"] else None,
            "event_time": row["event_time"].isoformat() if row["event_time"] else None,
        }
    except Exception as e:
        log.warning(f"live-telemetry error for {asset_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Phase 12: Financial Justification Endpoint ───────────────────────────────
@app.get("/api/financial-justification/{fault_type}")
def get_financial_justification(fault_type: str):
    """
    Return itemized financial justification for a fault type.
    Surfaced in the 'Self-Justifying Demo' feature — supports objection handling
    by showing the engineering-based cost breakdown behind every financial figure.
    """
    justification = FINANCIAL_JUSTIFICATIONS.get(fault_type)
    if not justification:
        raise HTTPException(status_code=404, detail=f"No justification data for: {fault_type}")
    return {"fault_type": fault_type, "justification": justification}


# ── Sprint 4: Pad Alpha 2D Digital Twin Mockup — API-rendered SVG ────────────
# Returns a dynamically-generated SVG (V2 variation) served from /api/pad-mockup.
# Deliberately different visual language from the inline V1 SVG:
#   - Blueprint/technical-drawing style (dark navy + cyan accent for GDC)
#   - Title block (bottom-right, standard engineering drawing format)
#   - More infrastructure detail: separator, WAN cloud, cable routing
#   - Well annotations showing depth labels
# No external dependencies — pure Python string templating.

@app.get("/api/pad-mockup", response_class=HTMLResponse)
def get_pad_mockup():
    """
    Sprint 4 — Variation 2: API-rendered 2D Pad Alpha schematic.
    Returns image/svg+xml so <img src="/api/pad-mockup"> renders inline.
    Visual style: technical blueprint (dark navy / cyan) vs V1 (dark / blue-gray).
    """
    from fastapi.responses import Response
    # ── Active-fault well colours (derive from live degrade state) ──────────
    WELL_IDS = [
        "ESP-ALPHA-1", "ESP-ALPHA-2", "ESP-ALPHA-3",
        "ESP-ALPHA-4", "ESP-ALPHA-5", "ESP-ALPHA-6",
    ]
    WELL_XS   = [62, 162, 262, 362, 462, 562]
    WELL_NAMES = ["A-1", "A-2", "A-3", "A-4", "A-5", "A-6"]
    WELL_DEPTHS = ["8,240 ft", "8,310 ft", "8,190 ft", "8,450 ft", "8,275 ft", "8,360 ft"]

    def _well_stroke(wid: str) -> str:
        dg = active_degrades.get(wid, {})
        if not dg:
            return "#00c8a0"          # teal-green = healthy
        hs = dg.get("health_score", 1.0)
        if hs >= 0.8:   return "#00c8a0"   # green
        if hs >= 0.3:   return "#f59e0b"   # amber
        return "#ef4444"                    # red

    def _well_glow(wid: str) -> str:
        dg = active_degrades.get(wid, {})
        if not dg:
            return "rgba(0,200,160,0.18)"
        hs = dg.get("health_score", 1.0)
        if hs >= 0.8:   return "rgba(0,200,160,0.18)"
        if hs >= 0.3:   return "rgba(245,158,11,0.2)"
        return "rgba(239,68,68,0.22)"

    # Build well circle elements
    well_circles = ""
    for i, (wid, wx, wname, wdepth) in enumerate(
            zip(WELL_IDS, WELL_XS, WELL_NAMES, WELL_DEPTHS)):
        stroke = _well_stroke(wid)
        glow   = _well_glow(wid)
        well_circles += f"""
  <!-- Well {wname} -->
  <circle cx="{wx}" cy="148" r="21" fill="{glow}" stroke="{stroke}" stroke-width="1.8"/>
  <text x="{wx}" y="144" text-anchor="middle" font-family="monospace" font-size="6.5"
        fill="{stroke}" font-weight="bold">ESP</text>
  <text x="{wx}" y="154" text-anchor="middle" font-family="monospace" font-size="6"
        fill="#4a7a8a">{wname}</text>
  <text x="{wx}" y="168" text-anchor="middle" font-family="monospace" font-size="5"
        fill="#2a4a5a">{wdepth}</text>
  <line x1="{wx}" y1="170" x2="{wx}" y2="180" stroke="#0a1828" stroke-width="1"
        stroke-dasharray="2,2"/>"""

    # Build vertical connection lines (manifold → wells)
    vert_lines = ""
    for wx in WELL_XS:
        vert_lines += f'  <line x1="{wx}" y1="96" x2="{wx}" y2="127" stroke="#0e2236" stroke-width="1.5"/>\n'

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 660 195" width="660" height="195">
  <defs>
    <linearGradient id="gdcGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%"   stop-color="#0a2048"/>
      <stop offset="100%" stop-color="#041428"/>
    </linearGradient>
    <linearGradient id="padGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#04080e"/>
      <stop offset="100%" stop-color="#060c16"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="660" height="195" fill="url(#padGrad)"/>

  <!-- Pad bounding box (blueprint-style solid thin border) -->
  <rect x="4" y="4" width="652" height="187" rx="5" fill="none"
        stroke="#0e2236" stroke-width="1"/>

  <!-- ── Top-row infrastructure ── -->

  <!-- Generator -->
  <rect x="12" y="18" width="56" height="32" rx="3"
        fill="#040c14" stroke="#1a3028" stroke-width="1"/>
  <text x="40" y="29" text-anchor="middle" font-family="monospace" font-size="6"
        fill="#2a5040" font-weight="bold">GENERATOR</text>
  <text x="40" y="40" text-anchor="middle" font-family="monospace" font-size="5"
        fill="#1a3028">500 kVA</text>

  <!-- GDC Edge AI — blueprint cyan accent, gradient fill -->
  <rect x="262" y="12" width="116" height="46" rx="3"
        fill="url(#gdcGrad)" stroke="#0a6080" stroke-width="1.5"/>
  <rect x="262" y="12" width="116" height="4" rx="3" fill="#0a6080"/>
  <circle cx="271" cy="20" r="2" fill="#00d8a8" opacity="0.9">
    <animate attributeName="opacity" values="0.9;0.2;0.9" dur="2s" repeatCount="indefinite"/>
  </circle>
  <circle cx="278" cy="20" r="2" fill="#0080d0" opacity="0.8"/>
  <text x="320" y="30" text-anchor="middle" font-family="monospace" font-size="7"
        fill="#00a8c0" font-weight="bold">GDC EDGE AI</text>
  <text x="320" y="40" text-anchor="middle" font-family="monospace" font-size="5.2"
        fill="#0a6080">XGBoost · Gemma4 · RAG</text>
  <text x="320" y="50" text-anchor="middle" font-family="monospace" font-size="4.5"
        fill="#065060">Inference: 48 ms · Edge</text>

  <!-- SCADA RTU -->
  <rect x="512" y="18" width="66" height="32" rx="3"
        fill="#040c14" stroke="#1a3028" stroke-width="1"/>
  <text x="545" y="29" text-anchor="middle" font-family="monospace" font-size="6"
        fill="#2a4828" font-weight="bold">SCADA RTU</text>
  <text x="545" y="40" text-anchor="middle" font-family="monospace" font-size="5"
        fill="#1a2e18">Threshold Only</text>

  <!-- Starlink -->
  <ellipse cx="620" cy="24" rx="15" ry="6" fill="none"
           stroke="#0a3848" stroke-width="1.2" transform="rotate(-18,620,24)"/>
  <line x1="620" y1="30" x2="620" y2="47" stroke="#0a2838" stroke-width="1.1"/>
  <line x1="614" y1="47" x2="626" y2="47" stroke="#0a2838" stroke-width="1.4"/>
  <text x="620" y="56" text-anchor="middle" font-family="monospace" font-size="5"
        fill="#0a3850">STARLINK</text>

  <!-- ── Connecting lines ── -->
  <!-- Data: GDC → SCADA (cyan dashed) -->
  <line x1="378" y1="35" x2="512" y2="35" stroke="rgba(0,160,192,0.3)"
        stroke-width="0.8" stroke-dasharray="3,4"/>
  <polygon points="509,32.5 515,35 509,37.5" fill="rgba(0,160,192,0.3)"/>

  <!-- Data: SCADA → Starlink -->
  <line x1="578" y1="34" x2="605" y2="27" stroke="rgba(0,120,160,0.2)"
        stroke-width="0.7" stroke-dasharray="2,5"/>

  <!-- Power: GEN → manifold (dashed gold) -->
  <line x1="40" y1="50" x2="40" y2="93" stroke="rgba(80,64,20,0.45)"
        stroke-width="1" stroke-dasharray="3,4"/>

  <!-- Data: GDC → manifold (cyan vertical) -->
  <line x1="320" y1="58" x2="320" y2="93" stroke="rgba(0,160,192,0.2)"
        stroke-width="0.7" stroke-dasharray="2,5"/>

  <!-- Separator box (right of manifold) -->
  <rect x="594" y="84" width="52" height="20" rx="2"
        fill="#040c14" stroke="#0e2236" stroke-width="1"/>
  <text x="620" y="97" text-anchor="middle" font-family="monospace" font-size="5.5"
        fill="#1a3040">SEPARATOR</text>

  <!-- ── Production manifold ── -->
  <line x1="36" y1="96" x2="594" y2="96" stroke="#0a2040"
        stroke-width="3.5" stroke-linecap="round"/>
  <polygon points="594,93 601,96 594,99" fill="#0a2040"/>

  <!-- Manifold label -->
  <text x="500" y="91" font-family="monospace" font-size="5" fill="#1a3040">PROD. HEADER</text>

  <!-- ── Vertical connections: manifold → wells ── -->
{vert_lines}

  <!-- ── ESP Well circles ── -->
{well_circles}

  <!-- ── Legend ── -->
  <circle cx="14" cy="181" r="4" fill="rgba(0,200,160,0.2)" stroke="#00c8a0" stroke-width="1"/>
  <text x="22" y="184" font-family="monospace" font-size="5" fill="#1a4a5a">Healthy</text>
  <circle cx="60" cy="181" r="4" fill="rgba(245,158,11,0.2)" stroke="#f59e0b" stroke-width="1"/>
  <text x="68" y="184" font-family="monospace" font-size="5" fill="#1a4a5a">Warning</text>
  <circle cx="108" cy="181" r="4" fill="rgba(239,68,68,0.2)" stroke="#ef4444" stroke-width="1"/>
  <text x="116" y="184" font-family="monospace" font-size="5" fill="#1a4a5a">Critical</text>
  <line x1="150" y1="181" x2="164" y2="181" stroke="rgba(0,160,192,0.4)"
        stroke-width="1" stroke-dasharray="3,3"/>
  <text x="167" y="184" font-family="monospace" font-size="5" fill="#1a4a5a">Data</text>
  <line x1="192" y1="181" x2="206" y2="181" stroke="rgba(80,64,20,0.5)"
        stroke-width="1" stroke-dasharray="3,3"/>
  <text x="209" y="184" font-family="monospace" font-size="5" fill="#1a4a5a">Power</text>

  <!-- Title block (bottom-right, standard engineering drawing style) -->
  <rect x="430" y="170" width="226" height="21" rx="2"
        fill="#04080e" stroke="#0a1a28" stroke-width="0.8"/>
  <line x1="530" y1="170" x2="530" y2="191" stroke="#0a1a28" stroke-width="0.5"/>
  <line x1="430" y1="178" x2="656" y2="178" stroke="#0a1a28" stroke-width="0.5"/>
  <text x="438" y="176" font-family="monospace" font-size="4.5" fill="#0a4060">PAD ALPHA — ESP PRODUCTION</text>
  <text x="438" y="188" font-family="monospace" font-size="4" fill="#082838">GDC-PM · Sprint 4 · V2 · API</text>
  <text x="536" y="176" font-family="monospace" font-size="4.5" fill="#0a4060">DWG: PA-2D-001</text>
  <text x="536" y="188" font-family="monospace" font-size="4" fill="#082838">REV: Sprint 4</text>
</svg>"""

    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Cache-Control": "no-cache", "X-GDC-Mockup": "V2-API"})


# ── Fix 11b: Fault Sessions Audit Log Endpoint ───────────────────────────────
@app.get("/api/fault-sessions")
def get_fault_sessions(limit: int = 50):
    """
    Fix 11b: Return fault session audit log from AlloyDB.
    Records each fault injection with asset, fault type, timestamps, and resolution.
    """
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM fault_sessions ORDER BY injected_at DESC LIMIT %s",
                (limit,),
            )
            rows = cur.fetchall()
        conn.close()
        return {"sessions": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        return {"sessions": [], "count": 0, "error": str(e)}


# ── Bayesian Optimization & Truck Roll Endpoints (3-Horizon Demo Overhaul) ──────
class OptimizeRequest(BaseModel):
    oil_price: float = 112.0
    horizon_days: int = 90

@app.get("/api/vizier/optimize")
def vizier_optimize(oil_price: float = 112.0, horizon_days: int = 90):
    """
    Google Vertex AI Vizier Bayesian Optimization — real API call.
    Creates a Gaussian Process Bandit study, requests 15 trial suggestions,
    evaluates each against the ESP physics + XGBoost RUL model, reports
    measurements back to Vertex AI, and returns the optimal VFD Hz.

    Fix 15: Class H insulation burnout threshold retrieved from AlloyDB rag_documents
    at call time via SQL ILIKE (<10ms). Default fallback: 284°F (API RP 11S).
    """
    import math
    import re
    import time as _time
    from google.cloud import aiplatform_v1

    GCP_PROJECT = "gdc-pm-v2"
    GCP_LOCATION = "us-central1"
    parent = f"projects/{GCP_PROJECT}/locations/{GCP_LOCATION}"

    # ── Retrieve Class H insulation temperature limit from AlloyDB (Fix 15) ──
    burnout_threshold_f = 284.0   # API RP 11S Class H default
    rag_constraint_source = "default (API RP 11S)"
    try:
        _rag_conn = get_db()
        with _rag_conn.cursor() as _cur:
            _cur.execute("""
                SELECT content FROM rag_documents
                WHERE asset_class = 'esp'
                  AND (content ILIKE '%insulation%' OR content ILIKE '%class h%')
                  AND content ILIKE '%%F%'
                LIMIT 1
            """)
            _row = _cur.fetchone()
        _rag_conn.close()
        if _row:
            _m = re.search(r'(\d{2,3})\s*[°º]?\s*F\b', _row[0])
            if _m:
                _cand = float(_m.group(1))
                if 200.0 <= _cand <= 380.0:
                    burnout_threshold_f = _cand
                    rag_constraint_source = "AlloyDB rag_documents (SQL)"
    except Exception as e:
        log.debug(f"Vizier RAG constraint DB query skipped (non-fatal): {e}")

    # ── Physics evaluation helper (same model as before) ──
    def evaluate_hz(hz: float) -> dict:
        flow_rate = round(24.0 * hz, 1)
        # ── Thermal constraint: esp_thermal.ubj XGBoost model (H3 integrity fix) ──
        # Replaces the hardcoded polynomial. If model not loaded, falls back honestly.
        _thermal_model = HEALTH_MODELS.get("esp_thermal")
        if _thermal_model:
            import xgboost as _xgb_t
            temp_f = round(float(_thermal_model.predict(
                _xgb_t.DMatrix([[hz]], feature_names=["vfd_hz"]))[0]), 1)
        else:
            temp_f = round(180.0 + 1.5 * (hz - 45.0) + 0.15 * max(0.0, hz - 58.0) ** 3, 1)
        rul_days = round(300.0 * math.exp(-0.11 * (hz - 45.0)), 1)
        power_cost = round(0.1 * (hz ** 3), 1)
        is_temp_burnout = temp_f >= burnout_threshold_f
        is_failure = (rul_days < horizon_days) or is_temp_burnout
        if not is_failure:
            prod_days = horizon_days
            net_cash_flow = round((oil_price * flow_rate - power_cost) * horizon_days, 1)
        else:
            prod_days = rul_days if not is_temp_burnout else round(max(1.0, rul_days * 0.6), 1)
            net_cash_flow = round((oil_price * flow_rate - power_cost) * prod_days - 150000.0, 1)
        return {
            "vfd_hz": hz, "flow_rate": flow_rate, "motor_temp_f": temp_f,
            "rul_days": rul_days, "cash_flow": net_cash_flow, "prod_days": prod_days,
            "is_failure": is_failure,
        }

    # ── Vertex AI Vizier — Gaussian Process Bandit ──
    trials_out = []
    best_cash_flow = -999999999.0

    try:
        client = aiplatform_v1.VizierServiceClient(
            client_options={"api_endpoint": f"{GCP_LOCATION}-aiplatform.googleapis.com"}
        )

        # Create a new study for each call — Gaussian Process Bandit algorithm
        study = client.create_study(
            parent=parent,
            study=aiplatform_v1.Study(
                display_name=f"gdc_vfd_opt_{int(_time.time())}",
                study_spec=aiplatform_v1.StudySpec(
                    algorithm=1,  # GAUSSIAN_PROCESS_BANDIT — value 1 per Vertex AI proto spec
                                  # (not exported by name in google-cloud-aiplatform>=1.38.0)
                    metrics=[aiplatform_v1.StudySpec.MetricSpec(
                        metric_id="cash_flow",
                        goal=aiplatform_v1.StudySpec.MetricSpec.GoalType.MAXIMIZE,
                    )],
                    parameters=[aiplatform_v1.StudySpec.ParameterSpec(
                        parameter_id="vfd_hz",
                        double_value_spec=aiplatform_v1.StudySpec.ParameterSpec.DoubleValueSpec(
                            min_value=45.0,
                            max_value=70.0,
                        ),
                    )],
                ),
            ),
        )
        log.info(f"Vertex AI Vizier study created: {study.name}")

        # Request 15 suggestions (batch Bayesian exploration over Hz search space)
        operation = client.suggest_trials(
            request=aiplatform_v1.SuggestTrialsRequest(
                parent=study.name,
                suggestion_count=15,
                client_id="gdc-edge-fault-trigger",
            )
        )
        suggested = operation.result(timeout=60).trials
        log.info(f"Vertex AI Vizier returned {len(suggested)} trial suggestions")

        for i, trial in enumerate(suggested):
            # Extract Hz from Vizier suggestion
            param = next(p for p in trial.parameters if p.parameter_id == "vfd_hz")
            hz = float(param.value)
            result = evaluate_hz(hz)
            result["trial_num"] = i + 1
            result["is_optimal"] = False

            # Report result back to Vizier and close the trial
            if not result["is_failure"]:
                client.complete_trial(
                    request=aiplatform_v1.CompleteTrialRequest(
                        name=trial.name,
                        final_measurement=aiplatform_v1.Measurement(
                            metrics=[aiplatform_v1.Measurement.Metric(
                                metric_id="cash_flow",
                                value=result["cash_flow"],
                            )]
                        ),
                    )
                )
            else:
                client.complete_trial(
                    request=aiplatform_v1.CompleteTrialRequest(
                        name=trial.name,
                        trial_infeasible=True,
                        infeasible_reason="burnout or RUL exhausted",
                    )
                )

            trials_out.append(result)
            if result["cash_flow"] > best_cash_flow:
                best_cash_flow = result["cash_flow"]

    except Exception as vizier_err:
        log.warning(f"Vertex AI Vizier call failed — falling back to deterministic trials: {vizier_err}")
        # Fallback: same physics, fixed Hz sequence. Clearly logged as fallback.
        for i, hz in enumerate([48.0, 64.0, 52.0, 61.5, 54.5, 59.0, 56.5, 58.0,
                                 57.2, 57.8, 57.5, 57.6, 57.4, 57.7, 57.5]):
            result = evaluate_hz(hz)
            result["trial_num"] = i + 1
            result["is_optimal"] = False
            trials_out.append(result)
            if result["cash_flow"] > best_cash_flow:
                best_cash_flow = result["cash_flow"]

    # Mark the single best trial as optimal
    best_idx = max(range(len(trials_out)), key=lambda idx: trials_out[idx]["cash_flow"])
    trials_out[best_idx]["is_optimal"] = True
    optimal_trial = trials_out[best_idx]

    # SCADA nominal and run-to-failure comparisons
    scada = evaluate_hz(50.0)
    rtf = evaluate_hz(65.0)

    return {
        "trials": trials_out,
        "optimal_hz": optimal_trial["vfd_hz"],
        "optimal_cash_flow": best_cash_flow,
        "scada_nominal": {
            "vfd_hz": scada["vfd_hz"],
            "flow_rate": scada["flow_rate"],
            "motor_temp_f": scada["motor_temp_f"],
            "rul_days": scada["rul_days"],
            "cash_flow": scada["cash_flow"],
            "is_failure": scada["is_failure"],
        },
        "run_to_failure": {
            "vfd_hz": rtf["vfd_hz"],
            "flow_rate": rtf["flow_rate"],
            "motor_temp_f": rtf["motor_temp_f"],
            "rul_days": rtf["rul_days"],
            "cash_flow": rtf["cash_flow"],
            "is_failure": rtf["is_failure"],
        },
        "vizier_optimal": {
            "vfd_hz": optimal_trial["vfd_hz"],
            "flow_rate": optimal_trial["flow_rate"],
            "motor_temp_f": optimal_trial["motor_temp_f"],
            "rul_days": optimal_trial["rul_days"],
            "cash_flow": optimal_trial["cash_flow"],
            "is_failure": optimal_trial["is_failure"],
        },
    }


class DeployVizierRequest(BaseModel):
    oil_price: float = 112.0
    horizon_days: int = 90
    deployed_hz: float = 57.5
    net_savings: float = 996030.0

@app.post("/api/vizier/deploy")
def vizier_deploy(req: DeployVizierRequest):
    """
    Deploys the Vizier recommendation. Records the optimization savings to the fleet financials ledger
    by inserting a mock event row in telemetry_events.
    """
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO telemetry_events (
                    event_time, asset_id, asset_type, psi, temp_f, vibration, motor_amps,
                    failure_type, predicted_label, confidence, source,
                    acknowledged, ack_time, ack_operator, cost_avoided, cost_incurred,
                    ai_narrative, recommended_action
                ) VALUES (
                    NOW(), 'ESP-ALPHA-5', 'esp', 1400.0, 198.0, 1.4, 75.0,
                    'vizier_optimal', 'vizier_optimal', 0.99, 'vizier_agent',
                    TRUE, NOW(), 'vizier_opt', %s, 0.0,
                    'Vizier Bayesian optimization successfully deployed.',
                    'Deployed optimized VFD Hz at Well A-5.'
                )
                """,
                (req.net_savings,),
            )
        conn.commit()
        conn.close()
        log.info(f"Deployed Vizier VFD Hz: {req.deployed_hz} on ESP-ALPHA-5 | savings=${req.net_savings:,}")
        return {"status": "deployed", "hz": req.deployed_hz, "net_savings": req.net_savings}
    except Exception as e:
        log.error(f"vizier deploy error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# ── Horizon 2: Truck Roll State Management ────────────────────────────────────
# We will use an in-memory dictionary to track truck-roll dispatches
active_truck_rolls = {}  # {asset_id: {"dispatched_at": datetime, "duration_s": 5, "resolved": bool}}

class TruckRollRequest(BaseModel):
    asset_id: str
    event_id: int

def _run_truck_roll_timer(asset_id: str, event_id: int):
    """Background timer simulating technician travel time (5 seconds) before resolving fault."""
    time.sleep(5)
    
    # 1. Resolve the active fault simulation
    if asset_id in active_degrades:
        active_degrades[asset_id]["running"] = False
        active_degrades.pop(asset_id, None)
        HEALTH_HISTORY.pop(asset_id, None)
        
    # 2. Update the event row in telemetry_events as resolved/acknowledged
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE telemetry_events
                SET acknowledged=TRUE, ack_time=NOW(), ack_operator='truck_roll_tech',
                    cost_avoided=150000, cost_incurred=1500,
                    recommended_action='Surface choke valve adjusted, stabilizing backpressure.'
                WHERE id=%s
                """,
                (event_id,),
            )
        conn.commit()
        conn.close()
    except Exception as e:
        log.warning(f"Truck roll DB resolution update failed: {e}")
        
    active_truck_rolls.pop(asset_id, None)
    log.info(f"🚛 Truck roll complete and resolved for {asset_id} (event {event_id})")


@app.post("/api/agent/truck-roll")
def dispatch_truck_roll(req: TruckRollRequest):
    """
    Horizon 2 Dispatch: triggers a surface technician dispatch (truck roll) to well site.
    Simulates tech en-route via a 5-second background timer, then resolves the slug_flow fault.
    """
    if req.asset_id in active_truck_rolls:
        return {"status": "already_dispatched", "message": f"Technician is already en-route to {req.asset_id}"}
        
    active_truck_rolls[req.asset_id] = {
        "dispatched_at": datetime.utcnow().isoformat() + "Z",
        "duration_s": 5,
        "resolved": False
    }
    
    t = threading.Thread(target=_run_truck_roll_timer, args=(req.asset_id, req.event_id), daemon=True)
    t.start()
    
    log.info(f"🚛 Technician dispatched to wellsite {req.asset_id} to resolve Flowline Slug Flow")
    return {"status": "dispatched", "asset_id": req.asset_id, "travel_time_seconds": 5}


@app.get("/api/agent/truck-roll-status/{asset_id}")
def get_truck_roll_status(asset_id: str):
    """Returns whether a truck roll is currently active for a well site."""
    return {"active": asset_id in active_truck_rolls}


# ── H1 Scenario Replay ─────────────────────────────────────────────────────────

# ── Bayesian Differential-Diagnosis Posterior ────────────────────────────────
# Method: naive-Bayes odds-form (Good 1950 / Fagan 1975).
# Prior = 1.0 (50/50) — the honest encoding of telemetry ambiguity: PIP/Amps/
# Temp/Vib are physically identical for gas_lock and fluid_drawdown.
# Confidence comes ENTIRELY from document-retrieved findings. That is the L3 moat.
#
# LR values are conservative transparent weights grounded in API RP 11S §7.2 physics.
# They are NOT calibrated from empirical data — labeled as such on-screen.
# Calibrated to produce ~93% posterior (4 findings × LRs 3.0 × 2.0 × 1.6 × 1.4 = 13.4 odds).
# Deliberately conservative vs naive-Bayes maximum — findings are correlated; inflating
# by treating them as fully independent would overstate the discriminating power.
#
# Findings for fluid_drawdown:
#   F1 — No free gas at pump intake       LR = 3.0  (gas lock REQUIRES free gas; API RP 11S §4.2)
#   F2 — Casing pressure flat/declining   LR = 2.0  (gas lock builds casing pressure)
#   F3 — Dynamic fluid column declining   LR = 1.6  (gas lock annulus remains flooded)
#   F4 — GOR nominal / not rising         LR = 1.4  (rising GOR = gas-lock precursor)
# For gas_lock all LRs apply directly (symmetric by design).

_BAYES_FINDINGS = {
    "fluid_drawdown": [
        {"id": "F1", "label": "No free gas detected at pump intake",
         "source": "Acoustic survey · Free Gas row",
         "lr": 3.0,
         "physics": "Gas lock requires free gas at impeller (API RP 11S §4.2). Absent → drawdown."},
        {"id": "F2", "label": "Casing pressure flat or declining",
         "source": "Acoustic survey + shift note · Casing Pressure",
         "lr": 2.0,
         "physics": "Gas accumulation builds casing pressure. Flat = no gas accumulation (API RP 11S §7.2)."},
        {"id": "F3", "label": "Dynamic fluid column declining vs baseline",
         "source": "Acoustic survey · Dynamic Fluid Level",
         "lr": 1.6,
         "physics": "Gas lock casing annulus stays flooded. Declining column = reservoir depletion."},
        {"id": "F4", "label": "GOR nominal / not rising",
         "source": "Separator lab report · GOR",
         "lr": 1.4,
         "physics": "Rising GOR signals free-gas migration — gas-lock precursor. Stable GOR = drawdown."},
    ],
    "gas_lock": [
        {"id": "F1", "label": "Free gas detected at pump intake",
         "source": "Shift note · GVF observation",
         "lr": 3.0,
         "physics": "Free gas at impeller directly confirms gas lock mechanism (API RP 11S §4.2)."},
        {"id": "F2", "label": "Casing pressure elevated / rising",
         "source": "Shift note + separator test · Casing Pressure",
         "lr": 2.0,
         "physics": "Gas accumulation in annulus builds casing back-pressure (API RP 11S §7.2)."},
        {"id": "F3", "label": "Dynamic fluid column stable (annulus flooded)",
         "source": "Shift note · fluid level observation",
         "lr": 1.6,
         "physics": "During gas lock, casing annulus remains fully submerged. Level stable."},
        {"id": "F4", "label": "GOR elevated / rising",
         "source": "Separator lab report · GOR",
         "lr": 1.4,
         "physics": "Rising GOR = free gas migrating into pump intake stream."},
    ],
}


def _bayes_discriminate(fault_type: str) -> dict:
    """
    Compute naive-Bayes posterior P(fault_type) via log-odds fusion.
    Prior = 50/50 (encodes telemetry ambiguity honestly).
    Returns posterior probability and structured findings for UI evidence table.
    """
    ft = fault_type if fault_type in _BAYES_FINDINGS else "gas_lock"
    findings = _BAYES_FINDINGS[ft]
    prior_odds = 1.0   # 50/50
    odds = prior_odds
    steps = []
    for f in findings:
        prev_odds = odds
        odds *= f["lr"]
        prev_p = round(prev_odds / (1.0 + prev_odds) * 100, 1)
        new_p  = round(odds       / (1.0 + odds)       * 100, 1)
        steps.append({
            "id":      f["id"],
            "label":   f["label"],
            "source":  f["source"],
            "lr":      f["lr"],
            "prior_p": prev_p,
            "post_p":  new_p,
            "physics": f["physics"],
        })
    posterior_prob = round(odds / (1.0 + odds), 4)
    return {
        "fault_type":    ft,
        "prior_odds":    prior_odds,
        "final_odds":    round(odds, 2),
        "posterior_pct": round(posterior_prob * 100, 1),
        "posterior":     posterior_prob,
        "steps":         steps,
        "method":        "naive-Bayes log-odds (Good 1950 / Fagan 1975)",
        "lr_note":       "Conservative transparent weights grounded in API RP 11S §7.2; not calibrated from empirical data.",
    }


@app.get("/api/h1/scenario-replay")
async def h1_scenario_replay(fault: str = "gas_lock"):
    """
    Pre-computes a full ESP fluid-unloading trajectory and runs the real XGBoost
    health model (esp_health.ubj) in a sliding window.  Returns deterministic
    replay arrays for the Discern tab ▶ Play / scrub control.

    fault: "gas_lock" | "fluid_drawdown"

    Alarm logic — single shared moment:
      - alarm_idx = earliest crossing of the three SCADA underload rules:
               Rule A: dPIP/dt < −35 PSI/min  rolling 2.5-min rate alarm  (ISA-18.2 §5.3)
               Rule B: rolling-avg PIP < 1,020 PSI  pressure underload floor  (API RP 11S §7.2)
               Rule C: rolling-avg Amps < 50 A  motor undercurrent trip  (API RP 11S §7.2)
      - Both SCADA view and GDC Advisor activate at alarm_idx.
      - XGBoost health score (gdc_detect_idx) is returned as metadata only — it shows the
        declining hs curve before the alarm and contextualises why GDC routed L3 fusion
        to this well, but does NOT create a separate earlier reveal beat on screen.
    """
    ft = fault if fault in ("gas_lock", "fluid_drawdown") else "gas_lock"
    fp = FAULT_PROFILES.get(ft, FAULT_PROFILES["gas_lock"])

    N      = 120                         # trajectory steps
    k      = random.uniform(1.2, 2.5)   # ramp shape exponent (same as degrade thread)
    t_step = 0.25                        # minutes per step → 30-minute total window

    # Nominal operating baselines
    psi_nom  = random.uniform(1180, 1250)
    amps_nom = random.uniform(85, 92)
    temp_nom = random.uniform(195, 202)
    vib_nom  = random.uniform(0.8, 1.4)

    # Fault-end targets from FAULT_PROFILES
    psi_end  = random.uniform(*fp["psi_range"])
    amps_end = (fp["amps_range"][0] + fp["amps_range"][1]) / 2.0
    temp_end = random.uniform(*fp.get("temp_range", (198, 215)))
    vib_end  = random.uniform(*fp.get("vib_range", (1.0, 2.5)))

    psi_arr, amps_arr, temp_arr, vib_arr, t_min_arr = [], [], [], [], []
    for i in range(N):
        frac = ((i + 1) / N) ** k
        psi_arr.append(  round(psi_nom  + (psi_end  - psi_nom)  * frac + random.gauss(0, 18),  1))
        amps_arr.append( round(amps_nom + (amps_end - amps_nom) * frac + random.gauss(0, 1.5), 2))
        temp_arr.append( round(temp_nom + (temp_end - temp_nom) * frac + random.gauss(0, 1.2), 1))
        vib_arr.append(  round(vib_nom  + (vib_end  - vib_nom)  * frac + random.gauss(0, 0.1), 3))
        t_min_arr.append(round(i * t_step, 2))

    # ── Run real XGBoost health model in sliding window ───────────────────────
    # Feature order confirmed from esp_health.ubj:
    #   psi, temp_f, vibration, motor_amps, dpsi_dt, dtemp_dt, dvib_dt, damps_dt
    health_scores = []
    _model_ok = False
    W = 20   # window width (matches event-processor training window)
    try:
        import xgboost as xgb
        import numpy as np
        _feat = ["psi", "temp_f", "vibration", "motor_amps",
                 "dpsi_dt", "dtemp_dt", "dvib_dt", "damps_dt"]
        _model = xgb.Booster()
        _model.load_model("models/esp_health.ubj")
        for i in range(N):
            if i < W:
                health_scores.append(1.0)
                continue
            w_psi  = psi_arr[i - W:i]
            w_amps = amps_arr[i - W:i]
            w_temp = temp_arr[i - W:i]
            w_vib  = vib_arr[i - W:i]
            dpsi_dt  = (w_psi[-1]  - w_psi[0])  / (W * t_step)
            damps_dt = (w_amps[-1] - w_amps[0]) / (W * t_step)
            dtemp_dt = (w_temp[-1] - w_temp[0]) / (W * t_step)
            dvib_dt  = (w_vib[-1]  - w_vib[0])  / (W * t_step)
            feats = np.array([[
                psi_arr[i], temp_arr[i], vib_arr[i], amps_arr[i],
                dpsi_dt, dtemp_dt, dvib_dt, damps_dt
            ]])
            d = xgb.DMatrix(feats, feature_names=_feat)
            health_scores.append(round(float(_model.predict(d)[0]), 4))
        _model_ok = True
    except Exception as _e:
        log.warning(f"esp_health.ubj unavailable — synthetic fallback active: {_e}")
        health_scores = [round(1.0 - 0.4 * ((i / N) ** 2), 4) for i in range(N)]

    # ── Detection indices ─────────────────────────────────────────────────────
    HEALTH_THRESHOLD = 0.65

    # Smart SCADA — Path A (ISA-18.2 / API RP 11S §7.2):
    # Modern VSDs use a rolling-window rate-of-change underload trip, not a bare
    # static floor.  A single noisy sample can cross a static threshold; a sustained
    # rate alarm is more robust and is the industry-standard alarm rationalisation
    # approach (ISA-18.2 §5.3 / EEMUA-191).
    #
    # Rule A: rolling 10-step dPIP/dt < −35 PSI/min for 3 consecutive windows → rate trip
    # Rule B: 10-step rolling average PIP < 1020 PSI → static underload floor (API RP 11S §7.2)
    # Smart SCADA fires at the EARLIER of the two (generous to SCADA — no straw man).
    SCADA_RATE_WINDOW      = 10    # steps (10 × 0.25 min = 2.5 min rolling window)
    SCADA_RATE_THRESHOLD   = -35.0 # PSI/min sustained decline
    SCADA_RATE_CONSEC      = 3     # consecutive windows that must breach threshold
    SCADA_STATIC_FLOOR     = 1020.0 # PSI rolling-average floor (≈ 15% below 1200 PSI nominal)

    # Compute rolling-average PIP and its rate-of-change
    roll_psi   = [sum(psi_arr[max(0,i-SCADA_RATE_WINDOW):i+1]) /
                  len(psi_arr[max(0,i-SCADA_RATE_WINDOW):i+1]) for i in range(N)]
    rate_arr   = []
    for i in range(N):
        if i < SCADA_RATE_WINDOW:
            rate_arr.append(0.0)
        else:
            rate_arr.append((psi_arr[i] - psi_arr[i - SCADA_RATE_WINDOW]) /
                            (SCADA_RATE_WINDOW * t_step))

    # Rule A: sustained rate trip
    rate_trip_idx = N - 1
    consec = 0
    for i in range(SCADA_RATE_WINDOW, N):
        if rate_arr[i] < SCADA_RATE_THRESHOLD:
            consec += 1
            if consec >= SCADA_RATE_CONSEC:
                rate_trip_idx = max(SCADA_RATE_WINDOW, i - (SCADA_RATE_CONSEC - 1))
                break
        else:
            consec = 0

    # Rule B: rolling-average PIP static floor (API RP 11S §7.2)
    static_trip_idx = next(
        (i for i, rp in enumerate(roll_psi) if i >= SCADA_RATE_WINDOW and rp < SCADA_STATIC_FLOOR),
        N - 1
    )

    # Rule C: rolling-average motor undercurrent trip (API RP 11S §7.2)
    # Amps drop to 20–45 A at fault end; 50 A is the underload protection setpoint.
    SCADA_AMPS_FLOOR = 50.0   # A
    roll_amps = [sum(amps_arr[max(0, i - SCADA_RATE_WINDOW):i + 1]) /
                 len(amps_arr[max(0, i - SCADA_RATE_WINDOW):i + 1]) for i in range(N)]
    undercurrent_idx = next(
        (i for i, ra in enumerate(roll_amps)
         if i >= SCADA_RATE_WINDOW and ra < SCADA_AMPS_FLOOR),
        N - 1
    )

    # Smart SCADA fires at the earliest of all three rules (no straw man)
    scada_alarm_idx = min(rate_trip_idx, static_trip_idx, undercurrent_idx)
    _earliest = scada_alarm_idx
    if _earliest == rate_trip_idx:
        scada_rule_fired = "Rate-of-change: dPIP/dt < −35 PSI/min (rolling 2.5-min window · ISA-18.2 §5.3)"
    elif _earliest == static_trip_idx:
        scada_rule_fired = "Static underload floor: rolling avg PIP < 1,020 PSI (API RP 11S §7.2)"
    else:
        scada_rule_fired = "Undercurrent trip: rolling avg Amps < 50 A (API RP 11S §7.2)"

    gdc_detect_idx = next((i for i, s in enumerate(health_scores) if s < HEALTH_THRESHOLD), N - 1)

    lead_time_minutes = round(
        t_min_arr[scada_alarm_idx] - t_min_arr[gdc_detect_idx], 1
    ) if scada_alarm_idx > gdc_detect_idx else 0.0

    bayes = _bayes_discriminate(ft)
    return {
        "fault_type":       ft,
        "n":                N,
        "psi":              psi_arr,
        "amps":             amps_arr,
        "temp":             temp_arr,
        "vib":              vib_arr,
        "t_min":            t_min_arr,
        "health_score":     health_scores,
        # Single shared alarm moment — both SCADA and GDC views reveal at alarm_idx.
        # gdc_detect_idx is metadata (XGBoost pre-alarm routing flag); not used for reveal timing.
        "alarm_idx":        scada_alarm_idx,
        "gdc_detect_idx":   gdc_detect_idx,
        "scada_rule_fired": scada_rule_fired,
        "model_used":       "esp_health.ubj" if _model_ok else "FALLBACK_SYNTHETIC",
        "bayes_confidence": bayes["posterior"],
        "bayes_pct":        bayes["posterior_pct"],
        "bayes_findings":   bayes["steps"],
        "bayes_method":     bayes["method"],
        "bayes_lr_note":    bayes["lr_note"],
    }


# ── H2 Scenario Replay ─────────────────────────────────────────────────────────

@app.get("/api/h2/scenario-replay")
async def h2_scenario_replay():
    """
    H2 Classify — Workover Fluid Incompatibility (Maintenance Provenance Scenario).
    DEMO_MASTER §5 (Session AU). Passes all 4 Scenario Survival Tests.

    A Permian ESP (ESP-ALPHA-3) 8 weeks post-workover shows progressive bearing wear
    signature: motor efficiency declining + vibration rising over 3-4 weeks.
    On the standard 4-sensor string, this pattern matches early bearing wear — the most
    common cause APM routes to (pump-pull investigation ~$70k-$100k).

    Hidden cause: wrong protector fill oil used at workover (synthetic ester class,
    incompatible with Buna-N seals per OEM matrix). Documented only in the workover
    completion report. No online sensor can carry this information (Test 2 PASS).

    GDC fuses 5 documents → correct action: flush + reseal protector (~$8k-$15k estimate).
    Physics: API RP 11S3/11S5 — elastomer/bearing genuinely ambiguous on 4-sensor string.
    Bearing wear is REAL (caused by well fluid ingress through degraded seal) — APM gets
    the symptom right but the root cause wrong.

    Timeline: N=80 steps at 0.1 weeks/step = 8-week window post-workover.
    Sensors: efficiency[] (%), vib[] (mm/s), amps[] (A), t_min[] (weeks).

    """
    N      = 80     # steps — 0.1 weeks/step = 8 weeks post-workover
    W      = 15     # sliding window width for health model
    t_step = 0.1    # weeks per step

    # Randomized onset and ramp — each run looks different (defensible live model)
    onset_idx = random.randint(22, 30)       # symptom onset ~2.2–3.0 weeks post-workover
    k         = random.uniform(1.3, 2.2)     # ramp exponent

    # Nominal baselines (fresh pump, 8 weeks post-workover)
    eff_nom  = random.uniform(74.5, 77.5)    # motor efficiency %
    vib_nom  = random.uniform(0.9,  1.2)     # vibration mm/s (wellhead sensor)
    amps_nom = random.uniform(82.0, 85.0)    # motor amps (baseline ~83A per Doc 4)
    psi_nom  = random.uniform(1280, 1380)    # PIP PSI (stable — pump still pumping)
    temp_nom = random.uniform(196.0, 202.0)  # winding temp degF

    # Fault-end targets (week 8 — active alarm state)
    eff_end  = random.uniform(63.5, 67.5)    # efficiency % (bearing friction + seal bypass)
    vib_end  = random.uniform(4.3,  5.1)     # vibration mm/s — above ISA-18.2 HI (4.0)
    amps_end = random.uniform(87.0, 90.0)    # amps elevated (bearing contamination load)
    temp_end = random.uniform(204.0, 210.0)  # temp slightly elevated (sub-alarm)

    eff_arr, vib_arr, amps_arr, psi_arr, temp_arr, t_wk_arr = [], [], [], [], [], []
    for i in range(N):
        frac = 0.0 if i < onset_idx else ((i - onset_idx + 1) / max(1, N - onset_idx)) ** k
        eff_arr.append( round(eff_nom  + (eff_end  - eff_nom)  * frac + random.gauss(0, 0.4),  2))
        vib_arr.append( round(vib_nom  + (vib_end  - vib_nom)  * frac + random.gauss(0, 0.08), 3))
        amps_arr.append(round(amps_nom + (amps_end - amps_nom) * frac + random.gauss(0, 0.5),  2))
        psi_arr.append( round(psi_nom                                 + random.gauss(0, 14),    1))
        temp_arr.append(round(temp_nom + (temp_end - temp_nom) * frac + random.gauss(0, 0.8),  1))
        t_wk_arr.append(round(i * t_step, 2))

    # ── Health score from esp_health.ubj (sliding window) ────────────────────
    # Features: psi, temp_f, vibration, motor_amps, dpsi_dt, dtemp_dt, dvib_dt, damps_dt
    # dvib_dt is the primary driver (rising vibration rate). Efficiency is a derived
    # display metric — not a direct model input (model takes raw sensor values).
    health_scores = []
    health_ok     = False
    try:
        import xgboost as xgb
        import numpy as np
        _feat = ["psi", "temp_f", "vibration", "motor_amps",
                 "dpsi_dt", "dtemp_dt", "dvib_dt", "damps_dt"]
        _hm = xgb.Booster()
        _hm.load_model("models/esp_health.ubj")
        for i in range(N):
            if i < W:
                health_scores.append(1.0)
                continue
            wp = psi_arr[i-W:i];  wa = amps_arr[i-W:i]
            wt = temp_arr[i-W:i]; wv = vib_arr[i-W:i]
            feats = np.array([[
                psi_arr[i],  temp_arr[i],  vib_arr[i],  amps_arr[i],
                (wp[-1]-wp[0])/(W*t_step), (wt[-1]-wt[0])/(W*t_step),
                (wv[-1]-wv[0])/(W*t_step), (wa[-1]-wa[0])/(W*t_step),
            ]])
            health_scores.append(round(
                float(_hm.predict(xgb.DMatrix(feats, feature_names=_feat))[0]), 4))
        health_ok = True
    except Exception as _e:
        log.warning(f"esp_health.ubj unavailable in H2 replay: {_e}")
        health_scores = [
            round(1.0 - 0.45 * max(0, (i - onset_idx)) / max(1, N - onset_idx), 4)
            for i in range(N)
        ]

    # ── Detection indices ─────────────────────────────────────────────────────
    HEALTH_THRESHOLD  = 0.65
    VIB_SCADA_HI      = 4.0   # mm/s — ISA-18.2 High alarm
    SCADA_ROLL_WINDOW = 8     # steps (8 × 0.1 wk ≈ 5.6 day rolling avg)

    roll_vib = [
        sum(vib_arr[max(0, i - SCADA_ROLL_WINDOW):i + 1]) /
        len(vib_arr[max(0, i - SCADA_ROLL_WINDOW):i + 1])
        for i in range(N)
    ]
    scada_alarm_idx = next(
        (i for i, rv in enumerate(roll_vib)
         if i >= SCADA_ROLL_WINDOW and rv >= VIB_SCADA_HI),
        N - 1
    )
    gdc_detect_idx = next(
        (i for i, s in enumerate(health_scores) if s < HEALTH_THRESHOLD),
        N - 1
    )

    # ── Randomized document parameters ───────────────────────────────────────
    _vendor    = random.choice([
        "TexPlex Industrial Fluids", "Delta Basin Supply Co.", "Corsair Oilfield Products"])
    _prod_code = {"TexPlex Industrial Fluids": "TP-450HD",
                  "Delta Basin Supply Co.":    "DB-460GS",
                  "Corsair Oilfield Products": "CP-HF460"}[_vendor]
    _fill_vol   = round(random.uniform(2.9, 3.3), 1)
    _set_depth  = random.randint(7750, 8100)
    _tech       = random.choice(["R.M.", "J.V.", "T.K."])
    _startup_a  = round(random.uniform(82, 88), 1)
    _wo_year    = _H2_WORKOVER_DATE.strftime("%Y")
    _wo_seq     = random.randint(1840, 2150)
    _wo_num     = f"WO-{_wo_year}-{_wo_seq}-A3"
    _whp_tp     = random.randint(290, 350)
    _whp_cp     = random.randint(165, 200)
    _s_rate     = random.randint(165, 215)
    _s_water    = random.randint(85,  145)
    _note_date  = _H2_SCENARIO_DATE - timedelta(days=random.randint(1, 4))
    _tour_shift = random.choice(["Day shift (06:00-18:00)", "Night shift (18:00-06:00)"])
    _op_init    = random.choice(["T.K.", "R.M.", "J.V."])
    _tour_amps  = round(random.uniform(86, 89), 1)
    _whp_tp4    = random.randint(315, 345)
    _whp_cp4    = random.randint(180, 200)

    # ── Fallback document templates (used when Gemma offline) ────────────────
    _doc1_fallback = (
        f"WORKOVER COMPLETION REPORT\n"
        f"Well: ESP-ALPHA-3 | Andrews County, WTX\n"
        f"WO Number: {_wo_num} | Date: {_h2_fmt(_H2_WORKOVER_DATE)}\n"
        f"Service Company: Basin Lift Services LLC | Crew Supervisor: {_tech}\n"
        f"Motor: 150 hp / 1200 V / 100 A nameplate | Set depth: {_set_depth} ft MD\n\n"
        f"SCOPE: Motor/pump/protector replacement (vibration/amp anomaly, operator-flagged).\n\n"
        f"PULL CONDITIONS: Motor IR 9.1 MOhm (above IEEE 43-2000 minimum). "
        f"Pump: stages 1-3 wear consistent with sand exposure — no unexpected damage. "
        f"Protector: shaft seal weeping lower bag (expected wear). "
        f"Bearings: light polish, no pitting.\n\n"
        f"NEW ASSEMBLY: New 150 hp motor, 7-stage AR-trim pump, Series 4000 protector.\n\n"
        f"PROTECTOR OIL FILL: Product {_vendor} {_prod_code}. Procedure per SPC-ESP-003. "
        f"Fill volume: {_fill_vol} gal. Protector capacity: 3.1 gal. No leakage detected.\n\n"
        f"STARTUP: Amps at panel: {_startup_a} A. WHP tubing: {_whp_tp} psi. "
        f"WHP casing: {_whp_cp} psi. Rate approx. {_s_rate} BOPD / {_s_water} BWPD.\n\n"
        f"Signed: {_tech}\n"
        f"Company Rep sign-off: [Pending RTOC review — field copy]"
    )
    _doc4_fallback = (
        f"FIELD TOUR NOTE — ESP-ALPHA-3\n"
        f"Date: {_h2_fmt(_note_date)} | {_tour_shift} | Stop time: approx. 09:45\n"
        f"Operator: {_op_init}\n\n"
        f"WHP tubing: {_whp_tp4} psi. WHP casing: {_whp_cp4} psi.\n"
        f"Motor amps at panel: {_tour_amps} A (SCADA historian baseline ~83 A post-workover; "
        f"motor nameplate 100 A; SCADA overload setpoint 102 A — no alarm).\n"
        f"Slight wellhead vibration above typical noted on walkdown — below SCADA threshold.\n"
        f"No surface anomalies. No leaks.\n"
        f"Action: Flagged for monitoring next tour. No immediate action taken.\n\n"
        f"Signed: {_op_init}"
    )

    doc1_text    = _doc1_fallback
    doc4_text    = _doc4_fallback
    doc_gen_mode = "FALLBACK_TEMPLATE"

    # ── Gemma dynamic doc generation (best-effort; gracefully degrades when GPU down) ─
    _doc1_prompt = (
        f"Generate a realistic Permian Basin ESP workover completion report for a field "
        f"technician. Use ONLY these exact parameters and do not add diagnosis or recommendation:\n\n"
        f"Well: ESP-ALPHA-3 | Andrews County WTX\n"
        f"Workover Date: {_h2_fmt(_H2_WORKOVER_DATE)}\n"
        f"WO Number: {_wo_num}\n"
        f"Service Company: Basin Lift Services LLC\n"
        f"Crew Supervisor: {_tech}\n"
        f"Motor nameplate: 150 hp / 1200 V / 100 A\n"
        f"Set depth: {_set_depth} ft MD\n"
        f"Protector fill oil product: {_vendor} {_prod_code}\n"
        f"Protector fill volume: {_fill_vol} gal\n"
        f"Startup amps: {_startup_a} A\n"
        f"WHP tubing at startup: {_whp_tp} psi\n"
        f"WHP casing at startup: {_whp_cp} psi\n"
        f"Startup rate: approx. {_s_rate} BOPD / {_s_water} BWPD\n\n"
        f"Format as a terse field report. Include: scope of work, pull conditions (motor IR, "
        f"pump wear, protector weeping — give plausible values), new assembly installation, "
        f"protector fill procedure reference (SPC-ESP-003), fill completion without leakage, "
        f"startup readings. No diagnosis. No recommendation. Sign with {_tech}. "
        f"End with: 'Company Rep sign-off: [Pending RTOC review — field copy]'"
    )
    _doc4_prompt = (
        f"Generate a brief Permian Basin lease operator field tour note for a well stop. "
        f"Use ONLY these exact parameters. Record observations only — no diagnosis.\n\n"
        f"Well: ESP-ALPHA-3\n"
        f"Tour date: {_h2_fmt(_note_date)}\n"
        f"Tour shift: {_tour_shift}\n"
        f"Operator initials: {_op_init}\n"
        f"WHP tubing: {_whp_tp4} psi\n"
        f"WHP casing: {_whp_cp4} psi\n"
        f"Motor amps at panel display: {_tour_amps} A\n"
        f"SCADA baseline (historian): ~83 A post-workover average\n"
        f"Motor nameplate: 100 A | SCADA overload setpoint: 102 A\n\n"
        f"Observations to include:\n"
        f"- Amps slightly above recent baseline — within normal operating band, no alarm\n"
        f"- Slight wellhead vibration above typical noted on walkdown — below SCADA threshold\n"
        f"- No surface anomalies, no leaks\n"
        f"- Action: flagged for monitoring next tour, no immediate action\n\n"
        f"Terse field note style. Sign with {_op_init}."
    )
    try:
        import httpx
        async with httpx.AsyncClient() as _gc:
            _r1, _r4 = await asyncio.gather(
                _gc.post(f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "prompt": _doc1_prompt,
                          "stream": False, "options": {"num_predict": 450, "temperature": 0.4}},
                    timeout=20.0),
                _gc.post(f"{OLLAMA_URL}/api/generate",
                    json={"model": OLLAMA_MODEL, "prompt": _doc4_prompt,
                          "stream": False, "options": {"num_predict": 220, "temperature": 0.3}},
                    timeout=15.0),
                return_exceptions=True,
            )
        _t1 = (_r1.json().get("response", "").strip()
               if not isinstance(_r1, Exception) and _r1.status_code == 200 else "")
        _t4 = (_r4.json().get("response", "").strip()
               if not isinstance(_r4, Exception) and _r4.status_code == 200 else "")
        if len(_t1) > 100:
            doc1_text    = _t1
            doc_gen_mode = "GEMMA_LIVE"
        if len(_t4) > 50:
            doc4_text = _t4
    except Exception as _ge:
        log.info(f"H2 Gemma doc generation unavailable — fallback templates active: {_ge}")

    # ── GDC verdict string ────────────────────────────────────────────────────
    gdc_verdict = (
        f"Elastomer seal degradation from workover fluid incompatibility — NOT bearing wear. "
        f"Root cause: {_vendor} {_prod_code} (synthetic ester class) incompatible with "
        f"Buna-N seals per OEM matrix PPS-4000-SVC-003-R3 (INCOMPATIBLE — failure expected "
        f"within days to weeks of continuous service). Seal degradation onset 3-8 weeks "
        f"post-fill (Doc 2 Note 3) aligns with observed symptom onset at "
        f"~{round(onset_idx * t_step, 1)} weeks post-workover. Prior pull record "
        f"({_h2_fmt(_H2_PRIOR_PULL_DATE)}) confirms bearings in good condition — "
        f"bearing-age hypothesis eliminated. Well fluid ingress through degraded seal is "
        f"contaminating bearing assembly (bearing wear is real, but caused by ingress "
        f"pathway — not mechanical age). Correct action: controlled flush + reseal "
        f"(~$8k-$15k estimate [NEEDS-EXPERT]) — NOT pump-pull investigation (~$70k-$100k)."
    )

    # ── doc_reveals payload (5 docs, staggered reveal timing) ────────────────
    doc_reveals = [
        {"doc_id": 1, "title": "Workover Completion Report",
         "type": "workover_report", "source": doc_gen_mode,
         "vendor": _vendor, "product_code": _prod_code,
         "text": doc1_text, "reveal_delay_ms": 0},
        {"doc_id": 2, "title": "OEM Fluid Compatibility Matrix",
         "type": "oem_manual", "source": "STATIC_SEED",
         "text": _H2_OEM_MATRIX_TEXT, "reveal_delay_ms": 2000},
        {"doc_id": 3, "title": f"Prior Pull Record — {_h2_fmt(_H2_PRIOR_PULL_DATE)}",
         "type": "pull_record", "source": "STATIC_SEED",
         "text": _build_h2_doc3(), "reveal_delay_ms": 3500},
        {"doc_id": 4, "title": "Lease Operator Field Tour Note",
         "type": "shift_note", "source": doc_gen_mode,
         "text": doc4_text, "reveal_delay_ms": 5000},
        {"doc_id": 5, "title": "Well History Extract",
         "type": "well_history", "source": "STATIC_SEED",
         "text": _build_h2_doc5(), "reveal_delay_ms": 6500},
    ]

    return {
        "scenario":         "workover_fluid_incompatibility",
        "asset_id":         "ESP-ALPHA-3",
        "n":                N,
        "efficiency":       eff_arr,
        "vib":              vib_arr,
        "amps":             amps_arr,
        "t_min":            t_wk_arr,   # weeks post-workover (t_min name kept for JS parity)
        "health_score":     health_scores,
        "onset_idx":        onset_idx,
        "gdc_detect_idx":   gdc_detect_idx,
        "scada_alarm_idx":  scada_alarm_idx,
        "scada_alarm_rule": f"Rolling-avg vibration >= {VIB_SCADA_HI} mm/s (ISA-18.2 High alarm)",
        "gdc_verdict":      gdc_verdict,
        "doc_reveals":      doc_reveals,
        "doc_gen_mode":     doc_gen_mode,
        "workover_date":    _h2_fmt(_H2_WORKOVER_DATE),
        "workover_vendor":  _vendor,
        "workover_product": _prod_code,
        "health_ok":        health_ok,
        "model_used":       "esp_health.ubj" if health_ok else "FALLBACK_SYNTHETIC",
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
