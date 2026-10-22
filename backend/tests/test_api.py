"""
Unit and Integration Tests for FastAPI Endpoints and Streaming Engine
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, BACKEND_DIR)

from app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "version" in data

def test_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert "active_sensors" in data
    assert data["active_sensors"] >= 10
    assert "avg_network_speed" in data
    assert "congestion_breakdown" in data
    assert "streaming_status" in data

def test_list_sensors():
    response = client.get("/api/sensors")
    assert response.status_code == 200
    sensors = response.json()
    assert len(sensors) == 10
    sensor_101 = next((s for s in sensors if s["sensor_id"] == "SENSOR-101"), None)
    assert sensor_101 is not None
    assert sensor_101["speed_limit"] == 100.0
    assert "latitude" in sensor_101

def test_current_traffic():
    response = client.get("/api/traffic/current")
    assert response.status_code == 200
    traffic = response.json()
    assert len(traffic) >= 10
    assert "congestion_level" in traffic[0]
    assert "average_speed" in traffic[0]

def test_traffic_history():
    response = client.get("/api/traffic/history?limit=10&page=1")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["records"]) <= 10

def test_predict_endpoint_valid():
    payload = {
        "sensor_id": "SENSOR-101",
        "average_speed": 35.0,
        "vehicle_count": 140,
        "occupancy_rate": 42.0,
        "traffic_volume": 1680,
        "speed_limit": 100.0
    }
    response = client.post("/api/predictions/predict", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "SUCCESS"
    assert result["predicted_congestion_15m"] in ["Free Flow", "Moderate", "Heavy", "Severe"]
    assert result["predicted_speed_15m"] > 0
    assert "confidence" in result
    assert "class_probabilities" in result

def test_predict_endpoint_invalid_speed():
    payload = {
        "sensor_id": "SENSOR-101",
        "average_speed": 350.0,  # exceeds maximum 200
        "vehicle_count": 80,
        "occupancy_rate": 20.0
    }
    response = client.post("/api/predictions/predict", json=payload)
    assert response.status_code == 422  # Pydantic validation error

def test_model_metrics():
    response = client.get("/api/model/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert "regression" in data
    assert "confusion_matrix" in data["classification"]
    assert data["classification"]["best_metrics"]["accuracy"] > 0.80

def test_stream_status():
    response = client.get("/api/stream/status")
    assert response.status_code == 200
    data = response.json()
    assert "is_running" in data
    assert "sensor_count" in data

def test_stream_rate_adjustment():
    response = client.post("/api/stream/rate", json={"interval_seconds": 2.5})
    assert response.status_code == 200
    assert response.json()["interval_seconds"] == 2.5
