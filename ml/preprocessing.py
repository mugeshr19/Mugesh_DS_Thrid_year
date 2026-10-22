"""
Data Preprocessing and Validation Module
Ensures high data quality for both offline historical training and real-time streaming inference.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple, List

# Validation bounds
MIN_SPEED_KMH = 0.0
MAX_SPEED_KMH = 200.0
MIN_OCCUPANCY = 0.0
MAX_OCCUPANCY = 100.0
MIN_VEHICLE_COUNT = 0
MAX_VEHICLE_COUNT = 1000

VALID_CONGESTION_LEVELS = ["Free Flow", "Moderate", "Heavy", "Severe"]

def validate_observation(record: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates a single IoT traffic sensor telemetry observation.
    Returns: (is_valid, quality_flag, cleaned_record)
    """
    cleaned = dict(record)
    errors = []

    # 1. Sensor ID check
    sensor_id = str(cleaned.get("sensor_id", "")).strip()
    if not sensor_id:
        return False, "INVALID_SENSOR_ID", cleaned
    cleaned["sensor_id"] = sensor_id

    # 2. Timestamp validation
    ts_raw = cleaned.get("timestamp")
    if isinstance(ts_raw, str):
        try:
            # Handle ISO or standard formats
            dt = pd.to_datetime(ts_raw)
            cleaned["timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return False, "INVALID_TIMESTAMP", cleaned
    elif isinstance(ts_raw, (datetime, pd.Timestamp)):
        cleaned["timestamp"] = ts_raw.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return False, "MISSING_TIMESTAMP", cleaned

    # 3. Numeric conversions & bounds
    try:
        speed = float(cleaned.get("average_speed", -1))
        if not (MIN_SPEED_KMH <= speed <= MAX_SPEED_KMH):
            errors.append(f"speed {speed} out of bounds")
        cleaned["average_speed"] = round(speed, 2)
    except (TypeError, ValueError):
        errors.append("average_speed not numeric")

    try:
        occ = float(cleaned.get("occupancy_rate", -1))
        if not (MIN_OCCUPANCY <= occ <= MAX_OCCUPANCY):
            errors.append(f"occupancy {occ} out of bounds")
        cleaned["occupancy_rate"] = round(occ, 2)
    except (TypeError, ValueError):
        errors.append("occupancy_rate not numeric")

    try:
        vc = int(cleaned.get("vehicle_count", -1))
        if not (MIN_VEHICLE_COUNT <= vc <= MAX_VEHICLE_COUNT):
            errors.append(f"vehicle_count {vc} out of bounds")
        cleaned["vehicle_count"] = vc
    except (TypeError, ValueError):
        errors.append("vehicle_count not numeric")

    try:
        vol = int(cleaned.get("traffic_volume", -1))
        cleaned["traffic_volume"] = max(0, vol)
    except (TypeError, ValueError):
        cleaned["traffic_volume"] = int(cleaned.get("vehicle_count", 0)) * 12

    try:
        density = float(cleaned.get("traffic_density", 0.0))
        cleaned["traffic_density"] = round(max(0.0, density), 2)
    except (TypeError, ValueError):
        cleaned["traffic_density"] = 0.0

    if errors:
        cleaned["data_quality_flag"] = "OUT_OF_BOUNDS"
        return False, "OUT_OF_BOUNDS", cleaned

    cleaned["data_quality_flag"] = "VALID"
    return True, "VALID", cleaned

def clean_historical_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw dataframe, drops nulls, filters out corrupted rows,
    and sorts strictly chronologically.
    """
    df_clean = df.copy()

    # Drop true duplicates
    df_clean = df_clean.drop_duplicates(subset=["sensor_id", "timestamp"]).reset_index(drop=True)

    # Convert timestamps
    df_clean["timestamp_dt"] = pd.to_datetime(df_clean["timestamp"])

    # Filter bounds
    mask = (
        (df_clean["average_speed"] >= MIN_SPEED_KMH) &
        (df_clean["average_speed"] <= MAX_SPEED_KMH) &
        (df_clean["occupancy_rate"] >= MIN_OCCUPANCY) &
        (df_clean["occupancy_rate"] <= MAX_OCCUPANCY) &
        (df_clean["vehicle_count"] >= MIN_VEHICLE_COUNT)
    )
    df_clean = df_clean[mask].copy()

    # Sort chronologically by sensor and time
    df_clean = df_clean.sort_values(by=["sensor_id", "timestamp_dt"]).reset_index(drop=True)
    df_clean = df_clean.drop(columns=["timestamp_dt"])
    return df_clean
