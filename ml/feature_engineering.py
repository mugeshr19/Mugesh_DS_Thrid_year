"""
Traffic Feature Engineering Module
Transforms raw sensor observations into predictive features without data leakage.
Supports both batch historical data processing and real-time streaming observations.
"""

import math
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional

# Standard feature columns used for ML modeling
FEATURE_COLUMNS = [
    "average_speed",
    "traffic_volume",
    "occupancy_rate",
    "traffic_density",
    "speed_ratio",
    "sin_hour",
    "cos_hour",
    "day_of_week",
    "is_weekend",
    "is_rush_hour",
    "speed_lag1",
    "speed_lag2",
    "speed_lag3",
    "volume_lag1",
    "occupancy_lag1",
    "speed_drop_rate",
    "rolling_mean_speed_15m",
    "rolling_std_speed_15m",
    "vc_ratio",
    "sensor_idx"
]

SENSOR_MAP = {
    "SENSOR-101": 0,
    "SENSOR-102": 1,
    "SENSOR-103": 2,
    "SENSOR-104": 3,
    "SENSOR-105": 4,
    "SENSOR-106": 5,
    "SENSOR-107": 6,
    "SENSOR-108": 7,
    "SENSOR-109": 8,
    "SENSOR-110": 9
}

def compute_temporal_features(ts: datetime):
    hour = ts.hour + ts.minute / 60.0
    sin_hour = math.sin(2 * math.pi * hour / 24.0)
    cos_hour = math.cos(2 * math.pi * hour / 24.0)
    dow = ts.weekday()
    is_weekend = 1 if dow >= 5 else 0
    is_rush = 1 if ((7.0 <= hour <= 9.75 or 16.5 <= hour <= 19.75) and not is_weekend) else 0
    return sin_hour, cos_hour, dow, is_weekend, is_rush

def engineer_batch_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chronologically engineers features for training from a bulk historical DataFrame.
    Strictly prevents future leakage by using backward shifts and rolling windows only.
    """
    df_feat = df.copy()
    df_feat["timestamp_dt"] = pd.to_datetime(df_feat["timestamp"])
    df_feat = df_feat.sort_values(by=["sensor_id", "timestamp_dt"]).reset_index(drop=True)

    # Temporal features
    temporal = df_feat["timestamp_dt"].apply(compute_temporal_features)
    df_feat["sin_hour"] = [t[0] for t in temporal]
    df_feat["cos_hour"] = [t[1] for t in temporal]
    df_feat["day_of_week"] = [t[2] for t in temporal]
    df_feat["is_weekend"] = [t[3] for t in temporal]
    df_feat["is_rush_hour"] = [t[4] for t in temporal]

    # Speed ratio
    df_feat["speed_limit"] = df_feat["speed_limit"].fillna(60.0)
    df_feat["speed_ratio"] = df_feat["average_speed"] / df_feat["speed_limit"]

    # Lag features per sensor (backward shifts only)
    df_feat["speed_lag1"] = df_feat.groupby("sensor_id")["average_speed"].shift(1)
    df_feat["speed_lag2"] = df_feat.groupby("sensor_id")["average_speed"].shift(2)
    df_feat["speed_lag3"] = df_feat.groupby("sensor_id")["average_speed"].shift(3)

    df_feat["volume_lag1"] = df_feat.groupby("sensor_id")["traffic_volume"].shift(1)
    df_feat["occupancy_lag1"] = df_feat.groupby("sensor_id")["occupancy_rate"].shift(1)

    # Speed drop rate
    df_feat["speed_drop_rate"] = (df_feat["speed_lag1"] - df_feat["average_speed"]) / np.maximum(df_feat["speed_lag1"], 10.0)

    # Rolling 15-minute statistics (3 observations backward including current)
    df_feat["rolling_mean_speed_15m"] = df_feat.groupby("sensor_id")["average_speed"].transform(
        lambda x: x.rolling(window=3, min_periods=1).mean()
    )
    df_feat["rolling_std_speed_15m"] = df_feat.groupby("sensor_id")["average_speed"].transform(
        lambda x: x.rolling(window=3, min_periods=1).std().fillna(0.0)
    )

    # Volume to capacity proxy
    df_feat["vc_ratio"] = df_feat["traffic_volume"] / (df_feat["speed_limit"] * 25.0)

    # Sensor encoding
    df_feat["sensor_idx"] = df_feat["sensor_id"].map(SENSOR_MAP).fillna(0).astype(int)

    # Backfill the initial 3 warmup lag rows per sensor with current observation values
    df_feat["speed_lag1"] = df_feat["speed_lag1"].fillna(df_feat["average_speed"])
    df_feat["speed_lag2"] = df_feat["speed_lag2"].fillna(df_feat["speed_lag1"])
    df_feat["speed_lag3"] = df_feat["speed_lag3"].fillna(df_feat["speed_lag2"])
    df_feat["volume_lag1"] = df_feat["volume_lag1"].fillna(df_feat["traffic_volume"])
    df_feat["occupancy_lag1"] = df_feat["occupancy_lag1"].fillna(df_feat["occupancy_rate"])
    df_feat["speed_drop_rate"] = df_feat["speed_drop_rate"].fillna(0.0)

    df_feat = df_feat.drop(columns=["timestamp_dt"])
    return df_feat

def engineer_streaming_features(
    current_obs: Dict[str, Any],
    sensor_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, float]:
    """
    Computes model features for a single real-time streaming observation using in-memory sensor buffer.
    """
    ts_str = current_obs.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    try:
        ts = pd.to_datetime(ts_str)
    except Exception:
        ts = datetime.utcnow()

    sin_hour, cos_hour, dow, is_weekend, is_rush = compute_temporal_features(ts)

    speed = float(current_obs.get("average_speed", 50.0))
    volume = float(current_obs.get("traffic_volume", 500.0))
    occ = float(current_obs.get("occupancy_rate", 15.0))
    density = float(current_obs.get("traffic_density", 12.0))
    speed_limit = float(current_obs.get("speed_limit", 60.0))
    sensor_id = str(current_obs.get("sensor_id", "SENSOR-101"))
    sensor_idx = SENSOR_MAP.get(sensor_id, 0)

    speed_ratio = speed / max(speed_limit, 20.0)
    vc_ratio = volume / max(speed_limit * 25.0, 100.0)

    # Use history buffer if available (ordered newest to oldest or oldest to newest)
    if sensor_history and len(sensor_history) > 0:
        # Assume history sorted with most recent previous at index -1
        prev1 = sensor_history[-1]
        prev2 = sensor_history[-2] if len(sensor_history) >= 2 else prev1
        prev3 = sensor_history[-3] if len(sensor_history) >= 3 else prev2

        speed_lag1 = float(prev1.get("average_speed", speed))
        speed_lag2 = float(prev2.get("average_speed", speed_lag1))
        speed_lag3 = float(prev3.get("average_speed", speed_lag2))

        volume_lag1 = float(prev1.get("traffic_volume", volume))
        occupancy_lag1 = float(prev1.get("occupancy_rate", occ))

        recent_speeds = [speed, speed_lag1, speed_lag2]
        rolling_mean_speed = float(np.mean(recent_speeds))
        rolling_std_speed = float(np.std(recent_speeds))
    else:
        # Fallback when sensor just connected
        speed_lag1 = speed
        speed_lag2 = speed
        speed_lag3 = speed
        volume_lag1 = volume
        occupancy_lag1 = occ
        rolling_mean_speed = speed
        rolling_std_speed = 0.0

    speed_drop_rate = (speed_lag1 - speed) / max(speed_lag1, 10.0)

    return {
        "average_speed": speed,
        "traffic_volume": volume,
        "occupancy_rate": occ,
        "traffic_density": density,
        "speed_ratio": round(speed_ratio, 4),
        "sin_hour": round(sin_hour, 4),
        "cos_hour": round(cos_hour, 4),
        "day_of_week": int(dow),
        "is_weekend": int(is_weekend),
        "is_rush_hour": int(is_rush),
        "speed_lag1": round(speed_lag1, 2),
        "speed_lag2": round(speed_lag2, 2),
        "speed_lag3": round(speed_lag3, 2),
        "volume_lag1": round(volume_lag1, 1),
        "occupancy_lag1": round(occupancy_lag1, 2),
        "speed_drop_rate": round(speed_drop_rate, 4),
        "rolling_mean_speed_15m": round(rolling_mean_speed, 2),
        "rolling_std_speed_15m": round(rolling_std_speed, 2),
        "vc_ratio": round(vc_ratio, 4),
        "sensor_idx": int(sensor_idx)
    }
