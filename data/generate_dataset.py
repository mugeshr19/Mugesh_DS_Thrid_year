"""
Data Generator for Real-Time Traffic Congestion Predictive Modeling
Generates high-fidelity traffic telemetry grounded in Greenshields' Fundamental Diagram of Traffic Flow:
    q = k * v
where q is flow (volume), k is density, v is space mean speed.

Produces:
1. data/raw/traffic_sensor_dataset.csv (14 days of 5-min intervals across 10 urban sensors = ~40,320 records)
2. data/sample/traffic_sample_500.csv (compact sample for quick inspection/testing)
"""

import os
import math
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Sensor definitions with realistic urban geometry, free-flow speeds (km/h), and lane capacities (veh/hr)
SENSORS = [
    {
        "sensor_id": "SENSOR-101",
        "road_segment_id": "SEG-NORTH-EXPR-01",
        "road_name": "North Interstate Expressway",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed_limit": 100.0,
        "free_flow_speed": 105.0,
        "capacity_veh_per_hr": 2200,
        "jam_density_veh_per_km": 120.0
    },
    {
        "sensor_id": "SENSOR-102",
        "road_segment_id": "SEG-DOWNTOWN-ART-02",
        "road_name": "Central Downtown Arterial",
        "latitude": 37.7833,
        "longitude": -122.4167,
        "speed_limit": 50.0,
        "free_flow_speed": 52.0,
        "capacity_veh_per_hr": 1200,
        "jam_density_veh_per_km": 95.0
    },
    {
        "sensor_id": "SENSOR-103",
        "road_segment_id": "SEG-HARBOR-BRG-03",
        "road_name": "Harbor Bay Bridge Approach",
        "latitude": 37.7952,
        "longitude": -122.3938,
        "speed_limit": 80.0,
        "free_flow_speed": 85.0,
        "capacity_veh_per_hr": 2000,
        "jam_density_veh_per_km": 110.0
    },
    {
        "sensor_id": "SENSOR-104",
        "road_segment_id": "SEG-FINANCIAL-DIST-04",
        "road_name": "Financial District Loop",
        "latitude": 37.7915,
        "longitude": -122.4010,
        "speed_limit": 40.0,
        "free_flow_speed": 42.0,
        "capacity_veh_per_hr": 900,
        "jam_density_veh_per_km": 85.0
    },
    {
        "sensor_id": "SENSOR-105",
        "road_segment_id": "SEG-TECH-HUB-BLVD-05",
        "road_name": "Tech Hub Boulevard",
        "latitude": 37.7650,
        "longitude": -122.3990,
        "speed_limit": 60.0,
        "free_flow_speed": 62.0,
        "capacity_veh_per_hr": 1500,
        "jam_density_veh_per_km": 100.0
    },
    {
        "sensor_id": "SENSOR-106",
        "road_segment_id": "SEG-WESTSIDE-PKWY-06",
        "road_name": "Westside Parkway",
        "latitude": 37.7580,
        "longitude": -122.4450,
        "speed_limit": 70.0,
        "free_flow_speed": 74.0,
        "capacity_veh_per_hr": 1800,
        "jam_density_veh_per_km": 105.0
    },
    {
        "sensor_id": "SENSOR-107",
        "road_segment_id": "SEG-AIRPORT-FWY-07",
        "road_name": "Airport Link Freeway",
        "latitude": 37.7200,
        "longitude": -122.3900,
        "speed_limit": 110.0,
        "free_flow_speed": 115.0,
        "capacity_veh_per_hr": 2400,
        "jam_density_veh_per_km": 125.0
    },
    {
        "sensor_id": "SENSOR-108",
        "road_segment_id": "SEG-MIDTOWN-INT-08",
        "road_name": "Midtown Transit Interchange",
        "latitude": 37.7780,
        "longitude": -122.4280,
        "speed_limit": 45.0,
        "free_flow_speed": 48.0,
        "capacity_veh_per_hr": 1100,
        "jam_density_veh_per_km": 90.0
    },
    {
        "sensor_id": "SENSOR-109",
        "road_segment_id": "SEG-EAST-BYPASS-09",
        "road_name": "East Industrial Bypass",
        "latitude": 37.7500,
        "longitude": -122.3850,
        "speed_limit": 65.0,
        "free_flow_speed": 68.0,
        "capacity_veh_per_hr": 1600,
        "jam_density_veh_per_km": 100.0
    },
    {
        "sensor_id": "SENSOR-110",
        "road_segment_id": "SEG-UNIV-CAMPUS-10",
        "road_name": "University Campus Perimeter",
        "latitude": 37.7620,
        "longitude": -122.4580,
        "speed_limit": 40.0,
        "free_flow_speed": 42.0,
        "capacity_veh_per_hr": 850,
        "jam_density_veh_per_km": 80.0
    }
]

def classify_congestion(speed_ratio: float, occupancy: float) -> str:
    """
    Classify congestion according to Highway Capacity Manual (HCM) criteria:
    speed_ratio = average_speed / speed_limit
    occupancy = percentage (0 - 100%)
    """
    if speed_ratio >= 0.85 and occupancy < 18.0:
        return "Free Flow"
    elif speed_ratio >= 0.60 and occupancy < 32.0:
        return "Moderate"
    elif speed_ratio >= 0.35 and occupancy < 50.0:
        return "Heavy"
    else:
        return "Severe"

def generate_traffic_data(days=14, interval_minutes=5, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    start_date = datetime(2026, 9, 1, 0, 0, 0)
    total_intervals = (days * 24 * 60) // interval_minutes
    timestamps = [start_date + timedelta(minutes=i * interval_minutes) for i in range(total_intervals)]

    records = []

    # Pre-generate some random incidents (e.g. stalled vehicle, lane closure)
    # Incident format: (sensor_id, start_idx, duration_intervals, severity_drop)
    incidents = []
    for _ in range(12):
        s_id = random.choice(SENSORS)["sensor_id"]
        # incidents more likely between 7am and 20pm
        day = random.randint(0, days - 1)
        hour = random.choice([8, 9, 12, 17, 18, 19])
        minute = random.choice([0, 15, 30, 45])
        start_ts = start_date + timedelta(days=day, hours=hour, minutes=minute)
        start_idx = int((start_ts - start_date).total_seconds() / (interval_minutes * 60))
        duration = random.randint(4, 18)  # 20 to 90 mins
        severity = random.uniform(0.40, 0.75)  # 40% - 75% speed drop
        incidents.append((s_id, start_idx, duration, severity))

    print(f"Generating traffic stream for {len(SENSORS)} sensors over {days} days ({len(timestamps)} timestamps per sensor)...")

    for sensor in SENSORS:
        s_id = sensor["sensor_id"]
        v_f = sensor["free_flow_speed"]
        v_limit = sensor["speed_limit"]
        k_jam = sensor["jam_density_veh_per_km"]
        capacity = sensor["capacity_veh_per_hr"]
        lat = sensor["latitude"]
        lng = sensor["longitude"]
        road_seg = sensor["road_segment_id"]
        road_name = sensor["road_name"]

        # Track rolling states for temporal lag features
        sensor_speeds = []
        sensor_volumes = []
        sensor_densities = []

        for idx, ts in enumerate(timestamps):
            hour = ts.hour + ts.minute / 60.0
            weekday = ts.weekday()
            is_weekend = 1 if weekday >= 5 else 0

            # Base diurnal demand curve (fraction of capacity)
            # Morning peak: 7:30 - 9:30 (peak at 8:30)
            # Evening peak: 16:30 - 19:30 (peak at 17:45)
            # Midday plateau: 11:30 - 14:00
            # Night base: 0:00 - 5:00
            if is_weekend:
                # Weekend traffic: smoother afternoon bell curve (11:00 - 18:00)
                demand = 0.15 + 0.55 * math.exp(-((hour - 14.5) ** 2) / 18.0)
            else:
                m_peak = 0.70 * math.exp(-((hour - 8.5) ** 2) / 2.2)
                e_peak = 0.85 * math.exp(-((hour - 17.75) ** 2) / 3.0)
                midday = 0.45 * math.exp(-((hour - 13.0) ** 2) / 8.0)
                night = 0.10 + 0.05 * math.sin(hour / 4.0)
                demand = max(0.08, night + m_peak + e_peak + midday)

            # Add sensor-specific variations and random fluctuations
            fluctuation = np.random.normal(0.0, 0.06)
            demand_ratio = np.clip(demand + fluctuation, 0.05, 1.35)

            # Check for active incidents
            incident_active = False
            for inc_sensor, inc_start, inc_dur, inc_drop in incidents:
                if inc_sensor == s_id and inc_start <= idx < inc_start + inc_dur:
                    demand_ratio = min(1.4, demand_ratio * 1.3)  # bottleneck queues buildup
                    incident_active = True
                    break

            # Calculate density (k in veh/km) based on demand
            # Under free-flow k = demand * k_crit, under congested k rises towards k_jam
            k_crit = k_jam / 2.0  # Greenshields critical density
            if demand_ratio <= 0.85:
                # Uncongested regime
                density = (demand_ratio / 0.85) * (k_crit * 0.75)
                # Speed from Greenshields: v = v_f * (1 - density / k_jam)
                speed = v_f * (1.0 - (density / k_jam)) + np.random.normal(0, 1.8)
            else:
                # Congested / oversaturated regime
                excess = demand_ratio - 0.85
                density = (k_crit * 0.75) + (excess / 0.5) * (k_jam - k_crit * 0.75)
                density = min(density, k_jam * 0.95)
                # Speed drops non-linearly
                speed = v_f * (1.0 - (density / k_jam))
                speed = max(8.0, speed + np.random.normal(0, 2.5))

            if incident_active:
                speed = max(6.0, speed * 0.45 + np.random.normal(0, 1.5))
                density = min(k_jam * 0.98, density * 1.35)

            speed = float(np.clip(speed, 5.0, v_limit * 1.15))
            speed = round(speed, 2)
            density = round(float(density), 2)

            # Flow rate (veh/hr) = density (veh/km) * speed (km/h)
            flow_rate = density * speed
            volume_veh_per_hr = int(min(flow_rate, capacity * 1.25))

            # Vehicle count in this 5-min interval: volume / (60 / interval)
            vehicle_count = int(round(volume_veh_per_hr * (interval_minutes / 60.0)))
            vehicle_count = max(1, vehicle_count)

            # Road occupancy percentage: related to density and average vehicle length (~6m effective)
            # Occ % ~ (density * 6m / 1000m) * 100 * factor
            occupancy = float(np.clip((density / k_jam) * 100.0 * 0.85, 2.0, 98.0))
            occupancy = round(occupancy, 2)

            speed_ratio = speed / v_limit
            congestion_level = classify_congestion(speed_ratio, occupancy)

            sensor_speeds.append(speed)
            sensor_volumes.append(volume_veh_per_hr)
            sensor_densities.append(density)

            records.append({
                "sensor_id": s_id,
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "road_segment_id": road_seg,
                "road_name": road_name,
                "latitude": lat,
                "longitude": lng,
                "speed_limit": v_limit,
                "vehicle_count": vehicle_count,
                "average_speed": speed,
                "occupancy_rate": occupancy,
                "traffic_density": density,
                "traffic_volume": volume_veh_per_hr,
                "congestion_level": congestion_level,
                "is_simulated": False,  # Historical baseline ground-truth
                "data_quality_flag": "VALID"
            })

    df = pd.DataFrame(records)

    # Sort strictly by timestamp and sensor
    df["timestamp_dt"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by=["sensor_id", "timestamp_dt"]).reset_index(drop=True)

    # Calculate 15-minute future speed (horizon = 3 intervals of 5 min) and 30-min future speed
    # Target for forecasting without leakage: future speed within the same sensor
    df["target_speed_15m"] = df.groupby("sensor_id")["average_speed"].shift(-3)
    df["target_speed_30m"] = df.groupby("sensor_id")["average_speed"].shift(-6)
    df["target_congestion_15m"] = df.groupby("sensor_id")["congestion_level"].shift(-3)

    # Fill tail NAs with last available value within group
    df["target_speed_15m"] = df.groupby("sensor_id")["target_speed_15m"].bfill()
    df["target_speed_30m"] = df.groupby("sensor_id")["target_speed_30m"].bfill()
    df["target_congestion_15m"] = df.groupby("sensor_id")["target_congestion_15m"].bfill()

    df = df.drop(columns=["timestamp_dt"])
    return df

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/sample", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    df = generate_traffic_data(days=14, interval_minutes=5)
    raw_path = "data/raw/traffic_sensor_dataset.csv"
    df.to_csv(raw_path, index=False)
    print(f"Saved full dataset: {raw_path} with {len(df):,} records and {len(df.columns)} columns.")

    sample_path = "data/sample/traffic_sample_500.csv"
    df.head(500).to_csv(sample_path, index=False)
    print(f"Saved sample dataset: {sample_path}")

    # Summary
    print("\nDataset Class Distribution:")
    print(df["congestion_level"].value_counts(normalize=True).round(3))
    print("\nDataset Basic Statistics:")
    print(df[["vehicle_count", "average_speed", "occupancy_rate", "traffic_density", "traffic_volume"]].describe().round(2))
