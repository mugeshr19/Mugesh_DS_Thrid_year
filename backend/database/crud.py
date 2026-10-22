"""
Database CRUD Operations for Traffic Analytics
Provides safe parameterized queries, pagination, and analytics aggregation.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .connection import db_session

def seed_sensors(sensors_list: List[Dict[str, Any]]):
    with db_session() as conn:
        cursor = conn.cursor()
        for s in sensors_list:
            cursor.execute("""
            INSERT INTO sensors (
                sensor_id, road_segment_id, road_name, latitude, longitude,
                speed_limit, capacity_veh_per_hr, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sensor_id) DO UPDATE SET
                road_segment_id=excluded.road_segment_id,
                road_name=excluded.road_name,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                speed_limit=excluded.speed_limit,
                capacity_veh_per_hr=excluded.capacity_veh_per_hr,
                status=excluded.status;
            """, (
                s["sensor_id"], s["road_segment_id"], s["road_name"],
                s["latitude"], s["longitude"], s["speed_limit"],
                s["capacity_veh_per_hr"], s.get("status", "ACTIVE")
            ))

def seed_historical_observations(records: List[Dict[str, Any]]):
    """Bulk inserts historical observations."""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
        INSERT OR IGNORE INTO traffic_observations (
            sensor_id, timestamp, vehicle_count, average_speed,
            occupancy_rate, traffic_density, traffic_volume,
            congestion_level, is_simulated, data_quality_flag
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            (
                r["sensor_id"], r["timestamp"], r["vehicle_count"],
                r["average_speed"], r["occupancy_rate"], r["traffic_density"],
                r["traffic_volume"], r["congestion_level"],
                1 if r.get("is_simulated") else 0,
                r.get("data_quality_flag", "VALID")
            ) for r in records
        ])

def insert_observation(record: Dict[str, Any]) -> int:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO traffic_observations (
            sensor_id, timestamp, vehicle_count, average_speed,
            occupancy_rate, traffic_density, traffic_volume,
            congestion_level, is_simulated, data_quality_flag
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            record["sensor_id"], record["timestamp"], record["vehicle_count"],
            record["average_speed"], record["occupancy_rate"], record["traffic_density"],
            record["traffic_volume"], record["congestion_level"],
            1 if record.get("is_simulated", False) else 0,
            record.get("data_quality_flag", "VALID")
        ))
        return cursor.lastrowid

def insert_prediction(pred: Dict[str, Any]) -> int:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO predictions (
            sensor_id, observation_timestamp, prediction_timestamp,
            forecast_horizon_minutes, predicted_congestion, predicted_speed,
            confidence, class_probabilities_json, explanations_json, model_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            pred["sensor_id"], pred["observation_timestamp"], pred["prediction_timestamp"],
            pred.get("forecast_horizon_minutes", 15),
            pred["predicted_congestion_15m"], pred["predicted_speed_15m"],
            pred.get("confidence", 0.85),
            json.dumps(pred.get("class_probabilities", {})),
            json.dumps(pred.get("explanations", [])),
            pred.get("model_version", "v1.2.0")
        ))
        return cursor.lastrowid

def get_all_sensors() -> List[Dict[str, Any]]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT s.*, 
               o.average_speed as latest_speed,
               o.congestion_level as latest_congestion,
               o.occupancy_rate as latest_occupancy,
               o.traffic_volume as latest_volume,
               o.timestamp as latest_timestamp,
               o.is_simulated as latest_is_simulated,
               p.predicted_congestion as latest_predicted_congestion,
               p.predicted_speed as latest_predicted_speed
        FROM sensors s
        LEFT JOIN (
            SELECT sensor_id, average_speed, congestion_level, occupancy_rate, traffic_volume, timestamp, is_simulated,
                   ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY timestamp DESC) as rn
            FROM traffic_observations
        ) o ON s.sensor_id = o.sensor_id AND o.rn = 1
        LEFT JOIN (
            SELECT sensor_id, predicted_congestion, predicted_speed,
                   ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY prediction_timestamp DESC) as rn
            FROM predictions
        ) p ON s.sensor_id = p.sensor_id AND p.rn = 1
        ORDER BY s.sensor_id;
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_current_traffic_state() -> List[Dict[str, Any]]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT o.*, s.road_name, s.road_segment_id, s.speed_limit, s.latitude, s.longitude,
               p.predicted_congestion as predicted_congestion_15m,
               p.predicted_speed as predicted_speed_15m,
               p.confidence as prediction_confidence
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY timestamp DESC) as rn
            FROM traffic_observations
        ) o
        JOIN sensors s ON o.sensor_id = s.sensor_id
        LEFT JOIN (
            SELECT sensor_id, predicted_congestion, predicted_speed, confidence,
                   ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY prediction_timestamp DESC) as rn
            FROM predictions
        ) p ON o.sensor_id = p.sensor_id AND p.rn = 1
        WHERE o.rn = 1
        ORDER BY o.sensor_id;
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_recent_sensor_history(sensor_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Returns the most recent observations for a sensor ordered oldest to newest."""
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM (
            SELECT * FROM traffic_observations
            WHERE sensor_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ) ORDER BY timestamp ASC;
        """, (sensor_id, limit))
        return [dict(row) for row in cursor.fetchall()]

def get_dashboard_summary() -> Dict[str, Any]:
    with db_session() as conn:
        cursor = conn.cursor()

        # Active sensors
        cursor.execute("SELECT COUNT(*) as count FROM sensors WHERE status = 'ACTIVE';")
        active_sensors = cursor.fetchone()["count"]

        # Latest readings aggregated
        cursor.execute("""
        WITH latest_obs AS (
            SELECT sensor_id, average_speed, traffic_volume, congestion_level, timestamp, is_simulated,
                   ROW_NUMBER() OVER (PARTITION BY sensor_id ORDER BY timestamp DESC) as rn
            FROM traffic_observations
        )
        SELECT 
            AVG(average_speed) as avg_network_speed,
            SUM(traffic_volume) as total_volume,
            MAX(timestamp) as last_update,
            MAX(is_simulated) as is_simulated,
            SUM(CASE WHEN congestion_level IN ('Heavy', 'Severe') THEN 1 ELSE 0 END) as congested_count,
            SUM(CASE WHEN congestion_level = 'Free Flow' THEN 1 ELSE 0 END) as count_free_flow,
            SUM(CASE WHEN congestion_level = 'Moderate' THEN 1 ELSE 0 END) as count_moderate,
            SUM(CASE WHEN congestion_level = 'Heavy' THEN 1 ELSE 0 END) as count_heavy,
            SUM(CASE WHEN congestion_level = 'Severe' THEN 1 ELSE 0 END) as count_severe
        FROM latest_obs
        WHERE rn = 1;
        """)
        summary_row = dict(cursor.fetchone() or {})

        # Hourly speed trend (last 24 hours of observations)
        cursor.execute("""
        SELECT 
            strftime('%H:00', timestamp) as hour_label,
            ROUND(AVG(average_speed), 1) as avg_speed,
            ROUND(AVG(traffic_volume), 0) as avg_volume,
            ROUND(AVG(occupancy_rate), 1) as avg_occupancy
        FROM traffic_observations
        GROUP BY hour_label
        ORDER BY hour_label ASC
        LIMIT 24;
        """)
        hourly_trend = [dict(row) for row in cursor.fetchall()]

        # Latest predictions list
        cursor.execute("""
        SELECT p.*, s.road_name 
        FROM predictions p
        JOIN sensors s ON p.sensor_id = s.sensor_id
        ORDER BY p.prediction_timestamp DESC
        LIMIT 6;
        """)
        recent_predictions = [dict(row) for row in cursor.fetchall()]

        return {
            "active_sensors": active_sensors,
            "avg_network_speed": round(summary_row.get("avg_network_speed") or 0.0, 1),
            "total_volume": int(summary_row.get("total_volume") or 0),
            "congested_count": int(summary_row.get("congested_count") or 0),
            "congestion_breakdown": {
                "free_flow": int(summary_row.get("count_free_flow") or 0),
                "moderate": int(summary_row.get("count_moderate") or 0),
                "heavy": int(summary_row.get("count_heavy") or 0),
                "severe": int(summary_row.get("count_severe") or 0)
            },
            "last_update": summary_row.get("last_update") or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "data_source_mode": "SIMULATED_LIVE" if summary_row.get("is_simulated") else "HISTORICAL_BASELINE",
            "hourly_trend": hourly_trend,
            "recent_predictions": recent_predictions
        }

def get_traffic_history(
    sensor_id: Optional[str] = None,
    congestion_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    with db_session() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM traffic_observations WHERE 1=1"
        params = []

        if sensor_id and sensor_id != "ALL":
            query += " AND sensor_id = ?"
            params.append(sensor_id)
        if congestion_level and congestion_level != "ALL":
            query += " AND congestion_level = ?"
            params.append(congestion_level)

        # Count total
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?;"
        params.extend([limit, offset])

        cursor.execute(query, params)
        records = [dict(row) for row in cursor.fetchall()]

        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "records": records
        }

def get_latest_predictions(limit: int = 20) -> List[Dict[str, Any]]:
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.*, s.road_name, s.speed_limit
        FROM predictions p
        JOIN sensors s ON p.sensor_id = s.sensor_id
        ORDER BY p.prediction_timestamp DESC
        LIMIT ?;
        """, (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            if r.get("class_probabilities_json"):
                try:
                    r["class_probabilities"] = json.loads(r["class_probabilities_json"])
                except Exception:
                    r["class_probabilities"] = {}
            if r.get("explanations_json"):
                try:
                    r["explanations"] = json.loads(r["explanations_json"])
                except Exception:
                    r["explanations"] = []
        return rows
