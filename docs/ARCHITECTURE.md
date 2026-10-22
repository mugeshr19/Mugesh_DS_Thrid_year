# System Architecture Specification

**System Name:** UrbanFlow AI Telemetry & Traffic Congestion Prediction System  
**System Type:** Real-Time Distributed Telemetry Streaming & Machine Learning Inference Platform  

---

## 1. High-Level Architecture Overview

```
 [IoT Sensor Network / Simulation Engine]
        │ (5-min telemetry: speed, volume, occupancy, density)
        ▼
 [FastAPI Streaming Engine (asyncio background worker)]
        │
        ├─► [Data Ingestion & Validation Layer]
        │        │
        │        ▼
        ├─► [Chronological Feature Engineering Engine]
        │        │ (20 lag, rolling, cyclical, & V/C features)
        │        ▼
        ├─► [Scikit-Learn ML Inference Service]
        │        │ (HistGBM Classifier + Regressor)
        │        ▼
        ├─► [SQLite Persistence Layer (WAL Mode)]
        │        │ (Observations, Predictions, System Logs)
        │        ▼
        └─► [WebSocket Broadcast Channel (`/api/ws/traffic-stream`)]
                 │ (Low-latency JSON push)
                 ▼
 [React + Vite + TypeScript Web Analytics Dashboard]
   - Overview Dashboard
   - Live Telemetry Monitoring
   - Interactive Leaflet OpenStreetMap
   - Real-Time Prediction Center Sandbox
   - Historical Diurnal Analytics
   - Empirical Model Insights & Confusion Matrix
   - System Information & API Catalog
```

---

## 2. Component Specifications

### 2.1 Telemetry Simulation & Ingestion Engine (`backend/streaming/`)
- **`sensor_simulator.py`**: Simulates 10 multi-modal urban sensors with Greenshields physics, diurnal demand curves (AM/PM peaks), and dynamic incident injection capability.
- **`engine.py`**: Asynchronous background event loop running via FastAPI lifespan. Gathers observations, runs validation, computes streaming lag features, persists to SQLite, and broadcasts payloads over WebSockets.

### 2.2 Machine Learning Pipeline (`ml/`)
- **`preprocessing.py`**: Data quality filters, bounds checking, missing-value handling.
- **`feature_engineering.py`**: Temporal lags ($t-1, t-2, t-3$), rolling statistics ($15\text{m}$ mean/std), speed drop rates, cyclical sine/cosine hour encodings.
- **`train_model.py`**: Offline model training with chronological 80/20 train/test split.
- **`predict.py`**: Low-latency production inference engine providing 15-minute classification and multi-horizon speed forecasting.

### 2.3 Storage Layer (`backend/database/`)
- SQLite database (`traffic_analytics.db`) configured with:
  - Write-Ahead Logging (`PRAGMA journal_mode=WAL;`) for concurrent read/write throughput.
  - Foreign key integrity (`PRAGMA foreign_keys=ON;`).
  - Multi-column indexes on `(sensor_id, timestamp)`.

### 2.4 Communication Protocols
- **REST API**: Standard JSON endpoints for metadata, historical queries with pagination, and on-demand inference.
- **WebSocket (`ws://localhost:8000/api/ws/traffic-stream`)**:
  - Immediate network snapshot push upon client connection.
  - Continuous incremental broadcasts as new telemetry arrives.
  - Heartbeat ping/pong support.

### 2.5 Frontend Dashboard (`frontend/`)
- **Framework**: React 18 with TypeScript and Vite bundler.
- **Visuals**: Modern light theme design system with subtle elevation, custom SVG markers on OpenStreetMap, and responsive Recharts components.
