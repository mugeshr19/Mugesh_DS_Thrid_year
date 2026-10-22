"""
Unit Tests for Data Preprocessing and Feature Engineering
"""

import sys
import os
import pytest
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "ml"))

from preprocessing import validate_observation
from feature_engineering import compute_temporal_features, engineer_streaming_features, FEATURE_COLUMNS

def test_validate_observation_valid():
    raw = {
        "sensor_id": "SENSOR-101",
        "timestamp": "2026-09-01 08:30:00",
        "average_speed": 55.4,
        "vehicle_count": 65,
        "occupancy_rate": 18.2,
        "traffic_volume": 780,
        "traffic_density": 14.1
    }
    is_valid, flag, clean = validate_observation(raw)
    assert is_valid is True
    assert flag == "VALID"
    assert clean["average_speed"] == 55.4

def test_validate_observation_out_of_bounds():
    raw = {
        "sensor_id": "SENSOR-101",
        "timestamp": "2026-09-01 08:30:00",
        "average_speed": -15.0,  # invalid negative speed
        "vehicle_count": 50,
        "occupancy_rate": 20.0
    }
    is_valid, flag, clean = validate_observation(raw)
    assert is_valid is False
    assert flag == "OUT_OF_BOUNDS"

def test_temporal_features_rush_hour():
    # 8:30 AM on Tuesday (weekday = 1) -> rush hour
    dt_morning_rush = datetime(2026, 9, 1, 8, 30, 0)
    sin_h, cos_h, dow, is_weekend, is_rush = compute_temporal_features(dt_morning_rush)
    assert dow == 1
    assert is_weekend == 0
    assert is_rush == 1

    # 2:00 AM on Sunday -> no rush
    dt_night = datetime(2026, 9, 6, 2, 0, 0)
    _, _, dow_sun, is_weekend_sun, is_rush_sun = compute_temporal_features(dt_night)
    assert dow_sun == 6
    assert is_weekend_sun == 1
    assert is_rush_sun == 0

def test_engineer_streaming_features():
    obs = {
        "sensor_id": "SENSOR-101",
        "timestamp": "2026-09-01 08:30:00",
        "average_speed": 40.0,
        "vehicle_count": 100,
        "occupancy_rate": 30.0,
        "traffic_volume": 1200,
        "speed_limit": 100.0
    }
    history = [
        {"average_speed": 50.0, "traffic_volume": 1100, "occupancy_rate": 25.0},
        {"average_speed": 45.0, "traffic_volume": 1150, "occupancy_rate": 28.0}
    ]
    feats = engineer_streaming_features(obs, history)
    for col in FEATURE_COLUMNS:
        assert col in feats, f"Missing feature {col}"
    assert feats["speed_lag1"] == 45.0
    assert feats["speed_drop_rate"] > 0  # Speed dropped from 45 to 40
