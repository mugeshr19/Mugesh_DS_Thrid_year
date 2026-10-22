# Database Schema Specification

**Database Engine:** SQLite 3  
**Journaling Mode:** Write-Ahead Logging (WAL)  
**File Path:** `backend/traffic_analytics.db`  

---

## 1. Entity Relationship Overview

```
 ┌──────────────────────┐          ┌───────────────────────────────┐
 │       sensors        │ 1      * │      traffic_observations     │
 ├──────────────────────┼──────────┼───────────────────────────────┤
 │ sensor_id (PK)       │          │ id (PK AUTOINCREMENT)         │
 │ road_segment_id      │          │ sensor_id (FK)                │
 │ road_name            │          │ timestamp                     │
 │ latitude             │          │ vehicle_count                 │
 │ longitude            │          │ average_speed                 │
 │ speed_limit          │          │ occupancy_rate                │
 │ capacity_veh_per_hr  │          │ traffic_density               │
 │ status               │          │ traffic_volume                │
 │ created_at           │          │ congestion_level              │
 └──────────────────────┘          │ is_simulated                  │
            │ 1                    │ data_quality_flag             │
            │                      │ created_at                    │
            │ *                    └───────────────────────────────┘
 ┌──────────┴─────────────────────────┐
 │            predictions             │
 ├────────────────────────────────────┤
 │ id (PK AUTOINCREMENT)              │
 │ sensor_id (FK)                     │
 │ observation_timestamp              │
 │ prediction_timestamp               │
 │ forecast_horizon_minutes           │
 │ predicted_congestion               │
 │ predicted_speed                    │
 │ confidence                         │
 │ class_probabilities_json           │
 │ explanations_json                  │
 │ model_version                      │
 │ created_at                         │
 └────────────────────────────────────┘
```

---

## 2. Table Specifications

### 2.1 Table: `sensors`
Stores metadata and spatial attributes of physical or simulated IoT telemetry nodes.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `sensor_id` | TEXT | PRIMARY KEY | Unique sensor identifier (e.g. `SENSOR-101`) |
| `road_segment_id` | TEXT | NOT NULL | Corridor segment tag (e.g. `SEG-NORTH-EXPR-01`) |
| `road_name` | TEXT | NOT NULL | Human-readable corridor name |
| `latitude` | REAL | NOT NULL | WGS84 latitude coordinate |
| `longitude` | REAL | NOT NULL | WGS84 longitude coordinate |
| `speed_limit` | REAL | NOT NULL | Statutory speed limit in km/h |
| `capacity_veh_per_hr`| INTEGER | NOT NULL | Theoretical roadway throughput capacity |
| `status` | TEXT | DEFAULT 'ACTIVE' | Operational status (`ACTIVE`, `MAINTENANCE`) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record insertion timestamp |

### 2.2 Table: `traffic_observations`
Stores 5-minute historical and streaming IoT sensor telemetry records.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique sequence identifier |
| `sensor_id` | TEXT | FOREIGN KEY REFERENCES sensors | Originating sensor node |
| `timestamp` | TEXT | NOT NULL | Observation timestamp (UTC format) |
| `vehicle_count` | INTEGER | NOT NULL | Count of vehicles within 5-min interval |
| `average_speed` | REAL | NOT NULL | Space mean speed in km/h |
| `occupancy_rate`| REAL | NOT NULL | Percentage of loop detector time occupied (0-100%) |
| `traffic_density`| REAL | NOT NULL | Traffic density in veh/km ($k$) |
| `traffic_volume`| INTEGER | NOT NULL | Flow volume in veh/h ($q$) |
| `congestion_level`| TEXT | NOT NULL | Free Flow, Moderate, Heavy, Severe |
| `is_simulated` | BOOLEAN | DEFAULT 0 | 0 = Real/Historical, 1 = Live Simulated Stream |
| `data_quality_flag`| TEXT | DEFAULT 'VALID' | Data quality validation flag |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record insertion timestamp |

### 2.3 Table: `predictions`
Persists machine learning inference outputs, multi-horizon forecasts, and explainability factors.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique prediction identifier |
| `sensor_id` | TEXT | FOREIGN KEY REFERENCES sensors | Monitored road segment |
| `observation_timestamp` | TEXT | NOT NULL | Telemetry observation timestamp |
| `prediction_timestamp` | TEXT | NOT NULL | Model inference execution timestamp |
| `forecast_horizon_minutes`| INTEGER | DEFAULT 15 | Horizon in minutes (15, 30) |
| `predicted_congestion` | TEXT | NOT NULL | Free Flow, Moderate, Heavy, Severe |
| `predicted_speed` | REAL | NOT NULL | Forecasted continuous speed in km/h |
| `confidence` | REAL | NOT NULL | Classification probability confidence (0.0 - 1.0) |
| `class_probabilities_json`| TEXT | NULL | JSON string of class posterior probabilities |
| `explanations_json` | TEXT | NULL | JSON array of human-readable explanation factors |
| `model_version` | TEXT | NOT NULL | Model identifier (e.g. `v1.2.0-HistGBM`) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Ingestion timestamp |

---

## 3. Database Indexes

To maintain sub-millisecond query performance during high-frequency telemetry ingestion:
- `idx_obs_sensor_time`: `CREATE INDEX idx_obs_sensor_time ON traffic_observations(sensor_id, timestamp);`
- `idx_obs_time`: `CREATE INDEX idx_obs_time ON traffic_observations(timestamp);`
- `idx_pred_sensor_time`: `CREATE INDEX idx_pred_sensor_time ON predictions(sensor_id, prediction_timestamp);`
- `idx_pred_time`: `CREATE INDEX idx_pred_time ON predictions(prediction_timestamp);`
