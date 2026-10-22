"""
Database Connection and Initialization for Traffic Analytics
Using SQLite for lightweight, reproducible, and zero-configuration local deployment.
"""

import os
import sqlite3
from typing import Generator
from contextlib import contextmanager

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "traffic_analytics.db"))

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high concurrency between streaming worker and read APIs
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

@contextmanager
def db_session() -> Generator[sqlite3.Connection, None, None]:
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes tables and indexes if they do not exist."""
    with db_session() as conn:
        cursor = conn.cursor()

        # 1. Sensors metadata table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            sensor_id TEXT PRIMARY KEY,
            road_segment_id TEXT NOT NULL,
            road_name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            speed_limit REAL NOT NULL,
            capacity_veh_per_hr INTEGER NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Traffic observations table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            vehicle_count INTEGER NOT NULL,
            average_speed REAL NOT NULL,
            occupancy_rate REAL NOT NULL,
            traffic_density REAL NOT NULL,
            traffic_volume INTEGER NOT NULL,
            congestion_level TEXT NOT NULL,
            is_simulated BOOLEAN DEFAULT 0,
            data_quality_flag TEXT DEFAULT 'VALID',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
        );
        """)

        # 3. Predictions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT NOT NULL,
            observation_timestamp TEXT NOT NULL,
            prediction_timestamp TEXT NOT NULL,
            forecast_horizon_minutes INTEGER DEFAULT 15,
            predicted_congestion TEXT NOT NULL,
            predicted_speed REAL NOT NULL,
            confidence REAL NOT NULL,
            class_probabilities_json TEXT,
            explanations_json TEXT,
            model_version TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
        );
        """)

        # 4. Data quality logs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_quality_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sensor_id TEXT,
            flag TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Indexes for fast historical analytics and real-time dashboard queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_sensor_time ON traffic_observations(sensor_id, timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_time ON traffic_observations(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_sensor_time ON predictions(sensor_id, prediction_timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_time ON predictions(prediction_timestamp);")

    print(f"Database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    init_db()
