"""
FastAPI REST API Routes for Traffic Congestion Analytics and ML Inference
"""

import os
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from schemas.traffic import (
    PredictionRequest, StreamToggleRequest, StreamRateRequest, IncidentInjectionRequest
)
from database.crud import (
    get_all_sensors, get_current_traffic_state, get_dashboard_summary,
    get_traffic_history, get_latest_predictions, get_recent_sensor_history,
    seed_sensors
)
from streaming.engine import streaming_engine
from predict import get_predictor

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    """System health check and operational status."""
    return {
        "status": "HEALTHY",
        "timestamp": datetime.utcnow().isoformat(),
        "application": "Real-Time Traffic Congestion Predictive Modeling API",
        "version": "1.2.0",
        "streaming_active": streaming_engine.is_running
    }

@router.get("/dashboard/summary")
def get_dashboard_kpis():
    """Aggregated KPIs for Overview Dashboard."""
    summary = get_dashboard_summary()
    summary["streaming_status"] = streaming_engine.get_status()
    return summary

@router.get("/sensors")
def list_sensors():
    """Returns all 10 monitored sensors with current telemetry and coordinates."""
    return get_all_sensors()

@router.get("/traffic/current")
def get_current_traffic():
    """Returns latest observed telemetry and predictions for each road segment."""
    return get_current_traffic_state()

@router.get("/traffic/history")
def get_historical_records(
    sensor_id: Optional[str] = Query(None, description="Filter by sensor_id or 'ALL'"),
    congestion_level: Optional[str] = Query(None, description="Filter by category or 'ALL'"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500)
):
    """Paginated historical traffic telemetry records."""
    offset = (page - 1) * limit
    result = get_traffic_history(sensor_id=sensor_id, congestion_level=congestion_level, limit=limit, offset=offset)
    result["page"] = page
    result["total_pages"] = (result["total"] + limit - 1) // limit
    return result

@router.get("/traffic/congestion-summary")
def get_congestion_summary():
    """Breakdown of congestion patterns across the road network."""
    summary = get_dashboard_summary()
    return {
        "network_average_speed": summary["avg_network_speed"],
        "total_volume_flow": summary["total_volume"],
        "congested_segments_count": summary["congested_count"],
        "breakdown": summary["congestion_breakdown"],
        "hourly_dynamics": summary["hourly_trend"]
    }

@router.get("/predictions/latest")
def get_predictions(limit: int = Query(20, ge=1, le=100)):
    """Recent model predictions and explanations."""
    return get_latest_predictions(limit=limit)

@router.post("/predictions/predict")
def predict_on_demand(payload: PredictionRequest):
    """
    On-demand real-time prediction using the trained ML model.
    Accepts current traffic attributes and outputs 15-min and 30-min predictions.
    """
    predictor = get_predictor()
    
    # Retrieve recent history for this sensor if available
    history = get_recent_sensor_history(payload.sensor_id, limit=3)
    
    obs = payload.model_dump()
    if not obs.get("timestamp"):
        obs["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    result = predictor.predict(obs, sensor_history=history)
    if result.get("status") == "ERROR":
        raise HTTPException(status_code=400, detail=result.get("error"))
    return result

@router.get("/model/metrics")
def get_model_metrics():
    """Returns verified offline evaluation metrics, confusion matrix, and feature importance."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    metrics_path = os.path.join(project_root, "outputs", "metrics", "classification_metrics.json")
    reg_path = os.path.join(project_root, "outputs", "metrics", "regression_metrics.json")

    if not os.path.exists(metrics_path) or not os.path.exists(reg_path):
        raise HTTPException(status_code=404, detail="Model metrics not found. Train model first.")

    with open(metrics_path, "r") as f:
        clf_metrics = json.load(f)
    with open(reg_path, "r") as f:
        reg_metrics = json.load(f)

    return {
        "classification": clf_metrics,
        "regression": reg_metrics
    }

@router.get("/model/info")
def get_model_info():
    """Information regarding model architectures, feature definitions, and training safeguards."""
    return {
        "classifier": {
            "name": "Histogram-based Gradient Boosting Classifier (HistGBM)",
            "task": "Multi-class Congestion Level Prediction (15-min horizon)",
            "classes": ["Free Flow", "Moderate", "Heavy", "Severe"],
            "features_count": 20,
            "leakage_safeguard": "Strict chronological train/test split (80/20) with backward lags only"
        },
        "regressor": {
            "name": "Histogram-based Gradient Boosting Regressor (HistGBM)",
            "task": "Continuous Speed Forecasting (15-min ahead in km/h)",
            "target": "target_speed_15m"
        },
        "baseline_comparison": {
            "classifier_baseline": "Dummy Most Frequent (Macro F1 = 0.1921 vs HistGBM = 0.7729)",
            "regressor_baseline": "Persistence Speed (MAE = 3.112 km/h vs HistGBM = 2.382 km/h, 23.5% error reduction)"
        }
    }

@router.get("/stream/status")
def get_stream_status():
    """Current streaming engine status."""
    return streaming_engine.get_status()

@router.post("/stream/toggle")
async def toggle_stream(payload: StreamToggleRequest):
    """Start, stop, or toggle the real-time IoT sensor telemetry stream."""
    action = payload.action.lower()
    if action == "start":
        await streaming_engine.start()
    elif action == "stop":
        await streaming_engine.stop()
    else:  # toggle
        if streaming_engine.is_running:
            await streaming_engine.stop()
        else:
            await streaming_engine.start()
    return streaming_engine.get_status()

@router.post("/stream/rate")
def set_stream_rate(payload: StreamRateRequest):
    """Adjust stream frequency (seconds between sensor observations)."""
    streaming_engine.set_interval(payload.interval_seconds)
    return streaming_engine.get_status()

@router.post("/stream/inject-incident")
def inject_incident(payload: IncidentInjectionRequest):
    """Simulate a traffic collision / incident on a specific sensor."""
    try:
        streaming_engine.inject_incident(
            sensor_id=payload.sensor_id,
            severity=payload.severity,
            duration_seconds=payload.duration_seconds
        )
        return {
            "status": "INCIDENT_INJECTED",
            "sensor_id": payload.sensor_id,
            "severity_pct": int(payload.severity * 100),
            "duration_seconds": payload.duration_seconds
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
