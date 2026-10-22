"""
Database Seeding Script
Populates sensors metadata and initial baseline historical telemetry from raw dataset.
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Adjust path so imports work when executed directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data")))

from database.connection import init_db
from database.crud import seed_sensors, seed_historical_observations, insert_prediction, get_recent_sensor_history
from predict import get_predictor

from generate_dataset import SENSORS

def run_seed():
    print("Initializing SQLite database tables...")
    init_db()

    print(f"Seeding {len(SENSORS)} urban traffic sensors...")
    seed_sensors(SENSORS)

    raw_path = "data/raw/traffic_sensor_dataset.csv"
    if os.path.exists(raw_path):
        print(f"Loading baseline observations from {raw_path}...")
        df = pd.read_csv(raw_path)
        # Take the most recent 2 days (576 intervals * 10 sensors = 5,760 records)
        df["timestamp_dt"] = pd.to_datetime(df["timestamp"])
        max_ts = df["timestamp_dt"].max()
        cutoff_ts = max_ts - pd.Timedelta(days=2)
        df_recent = df[df["timestamp_dt"] >= cutoff_ts].sort_values("timestamp_dt").copy()
        df_recent = df_recent.drop(columns=["timestamp_dt"])

        records = df_recent.to_dict(orient="records")
        print(f"Inserting {len(records):,} baseline historical records...")
        seed_historical_observations(records)

        # Generate initial predictions for each sensor's latest reading
        predictor = get_predictor()
        print("Generating baseline predictions for current sensor states...")
        for s in SENSORS:
            s_id = s["sensor_id"]
            history = get_recent_sensor_history(s_id, limit=4)
            if history:
                latest = history[-1]
                pred = predictor.predict(latest, sensor_history=history[:-1])
                if pred["status"] == "SUCCESS":
                    insert_prediction(pred)

        print("Database seeding completed successfully!")
    else:
        print(f"Warning: {raw_path} not found. Generated empty tables.")

if __name__ == "__main__":
    run_seed()
