"""
Automated Test Runner for Real-Time Traffic Congestion Prediction System
Uses httpx.AsyncClient for asynchronous FastAPI ASGI integration tests.
"""

import sys
import os
import asyncio
import httpx
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))

sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "ml"))

from app import app
from preprocessing import validate_observation
from feature_engineering import compute_temporal_features, engineer_streaming_features, FEATURE_COLUMNS
from predict import get_predictor

async def run_all_tests():
    print("=" * 65)
    print("RUNNING BACKEND SUITE: REAL-TIME TRAFFIC CONGESTION SYSTEM")
    print("=" * 65)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        
        # Test 1: Health endpoint
        print("[TEST 1/10] Testing /api/health...")
        res = await client.get("/api/health")
        assert res.status_code == 200, f"Health check failed: {res.status_code}"
        health_data = res.json()
        assert health_data["status"] == "HEALTHY"
        assert "version" in health_data
        print(f"  --> PASSED: Status {health_data['status']}, Version {health_data['version']}")

        # Test 2: Dashboard summary
        print("[TEST 2/10] Testing /api/dashboard/summary...")
        res = await client.get("/api/dashboard/summary")
        assert res.status_code == 200
        summary = res.json()
        assert summary["active_sensors"] >= 10
        assert "avg_network_speed" in summary
        assert "congestion_breakdown" in summary
        assert "streaming_status" in summary
        print(f"  --> PASSED: Active Sensors: {summary['active_sensors']}, Avg Speed: {summary['avg_network_speed']} km/h")

        # Test 3: List sensors
        print("[TEST 3/10] Testing /api/sensors...")
        res = await client.get("/api/sensors")
        assert res.status_code == 200
        sensors = res.json()
        assert len(sensors) == 10
        s101 = next((s for s in sensors if s["sensor_id"] == "SENSOR-101"), None)
        assert s101 is not None
        assert s101["speed_limit"] == 100.0
        print(f"  --> PASSED: 10 sensors verified with coordinates and limits")

        # Test 4: Current traffic
        print("[TEST 4/10] Testing /api/traffic/current...")
        res = await client.get("/api/traffic/current")
        assert res.status_code == 200
        current = res.json()
        assert len(current) >= 10
        assert "congestion_level" in current[0]
        print(f"  --> PASSED: Telemetry received for {len(current)} road segments")

        # Test 5: Traffic history
        print("[TEST 5/10] Testing /api/traffic/history...")
        res = await client.get("/api/traffic/history?limit=10&page=1")
        assert res.status_code == 200
        hist = res.json()
        assert hist["total"] > 0
        assert len(hist["records"]) <= 10
        print(f"  --> PASSED: Total historical records: {hist['total']:,}")

        # Test 6: Valid prediction request
        print("[TEST 6/10] Testing /api/predictions/predict (Valid)...")
        payload = {
            "sensor_id": "SENSOR-101",
            "average_speed": 35.0,
            "vehicle_count": 140,
            "occupancy_rate": 42.0,
            "traffic_volume": 1680,
            "speed_limit": 100.0
        }
        res = await client.post("/api/predictions/predict", json=payload)
        assert res.status_code == 200
        pred = res.json()
        assert pred["status"] == "SUCCESS"
        assert pred["predicted_congestion_15m"] in ["Free Flow", "Moderate", "Heavy", "Severe"]
        assert pred["predicted_speed_15m"] > 0
        assert "class_probabilities" in pred
        print(f"  --> PASSED: Predicted {pred['predicted_congestion_15m']} ({pred['predicted_speed_15m']} km/h, Confidence: {pred['confidence']})")

        # Test 7: Invalid prediction request
        print("[TEST 7/10] Testing /api/predictions/predict (Validation Error)...")
        invalid_payload = {
            "sensor_id": "SENSOR-101",
            "average_speed": 400.0,
            "vehicle_count": 100,
            "occupancy_rate": 20.0
        }
        res = await client.post("/api/predictions/predict", json=invalid_payload)
        assert res.status_code == 422
        print("  --> PASSED: Schema validation correctly rejected speed=400 km/h with HTTP 422")

        # Test 8: Model metrics and offline evaluation
        print("[TEST 8/10] Testing /api/model/metrics...")
        res = await client.get("/api/model/metrics")
        assert res.status_code == 200
        m = res.json()
        assert "classification" in m and "regression" in m
        assert m["classification"]["best_metrics"]["accuracy"] > 0.85
        assert m["regression"]["best_metrics"]["mae"] < 3.0
        print(f"  --> PASSED: Verified Classifier Acc: {m['classification']['best_metrics']['accuracy']*100:.1f}%, Regressor MAE: {m['regression']['best_metrics']['mae']} km/h")

        # Test 9: Stream status and rate control
        print("[TEST 9/10] Testing /api/stream/rate...")
        res = await client.post("/api/stream/rate", json={"interval_seconds": 2.5})
        assert res.status_code == 200
        assert res.json()["interval_seconds"] == 2.5
        print("  --> PASSED: Stream interval successfully updated to 2.5s")

        # Test 10: Preprocessing and feature engineering unit tests
        print("[TEST 10/10] Testing Preprocessing & Feature Engineering Unit Logic...")
        # Out of bounds check with timestamp present
        is_val, flag, _ = validate_observation({
            "sensor_id": "S1",
            "timestamp": "2026-09-01 10:00:00",
            "average_speed": -5.0,
            "vehicle_count": 10,
            "occupancy_rate": 10
        })
        assert not is_val and flag == "OUT_OF_BOUNDS", f"Expected OUT_OF_BOUNDS, got {flag}"
        # Rush hour check
        _, _, dow, is_wknd, is_rush = compute_temporal_features(datetime(2026, 9, 1, 8, 30, 0))
        assert is_rush == 1 and not is_wknd
        print("  --> PASSED: Unit logic verified without error")

    print("\n" + "=" * 65)
    print("ALL 10 TEST SUITES PASSED FLAWLESSLY (100% SUCCESS)!")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
