# UrbanFlow AI — Real-Time Traffic Congestion Predictive Modeling Using Live IoT Sensor Stream Analytics

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178C6.svg)](https://www.typescriptlang.org/)
[![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-1.7+-F7931E.svg)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL--Mode-003B57.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An academic and production-ready Intelligent Transportation System (ITS) platform that ingests streaming traffic sensor telemetry, evaluates Greenshields traffic physics, extracts temporal lag/rolling features, executes machine learning inference for multi-horizon congestion prediction, and broadcasts live results over WebSockets to an interactive monitoring dashboard.

---

## 1. Problem Statement

Urban vehicular congestion leads to severe economic losses, fuel waste, elevated carbon emissions, and unpredictable travel delays. Conventional traffic management relies either on static signal timings or post-incident reporting. Anticipatory traffic control requires real-time predictive models capable of ingesting high-frequency IoT sensor telemetry and forecasting congestion transitions (free-flow $\to$ moderate $\to$ heavy $\to$ severe gridlock) 15 to 30 minutes before physical bottleneck queues materialize.

---

## 2. Project Objectives

1. **IoT Stream Analytics Engine**: Ingest 5-minute interval sensor telemetry (speed, volume, occupancy, density) with strict bounds checking, out-of-bounds validation, and data quality tagging.
2. **Physics-Grounded Feature Engineering**: Extract 20 non-leaking features including temporal lags ($t-1, t-2, t-3$), 15-minute rolling statistics, speed drop rates ($\Delta v / \Delta t$), and cyclical diurnal encodings.
3. **Multi-Horizon ML Prediction**: Deploy both multi-class congestion classification (Level of Service A through F) and continuous speed forecasting (15-min and 30-min horizons).
4. **Interactive GIS Dashboard**: Provide an OpenStreetMap Leaflet interface with real-time color-coded sensor pins, telemetry monitoring, on-demand prediction sandbox, and empirical confusion matrix visualization.
5. **Real-Time WebSocket Protocol**: Deliver sub-second telemetry and AI inference updates to connected clients with stream rate controls and manual incident injection.

---

## 3. Key Features

- **Real-Time WebSocket Broadcasting**: Incremental sensor telemetry and prediction pushes over ASGI WebSockets (`/api/ws/traffic-stream`).
- **Interactive Leaflet GIS Map**: OpenStreetMap integration centered on 10 metropolitan sensor corridors with clickable telemetry popups.
- **Incident & Bottleneck Simulation**: Trigger synthetic accidents or lane closures to test predictive congestion alerts in real time.
- **Dual Machine Learning Models**:
  - *Classifier*: Histogram-based Gradient Boosting (HistGBM) achieving **90.2% Accuracy** and **0.7729 Macro F1** (+302% over baseline).
  - *Regressor*: Continuous speed forecaster achieving **2.382 km/h MAE** (23.5% error reduction relative to persistence baseline).
- **Strict Leakage Prevention**: Chronological 80/20 train/test split without future data contamination.
- **Explainability Engine**: Natural language factor extraction (e.g. rush hour peak, rapid deceleration, high V/C ratio).
- **Automated Verification Suite**: Full test coverage of REST endpoints, schema validation, feature engineering, and ML inference.

---

## 4. System Architecture

```
 [IoT Sensor Stream / Simulator]
        │ (5-min telemetry: speed, volume, occupancy, density)
        ▼
 [FastAPI Streaming Engine (asyncio loop)]
        │
        ├─► [Validation Layer] ──► Quality Flagging (VALID / OUT_OF_BOUNDS)
        │
        ├─► [Feature Engine]  ──► 20 Chronological Lag & Rolling Features
        │
        ├─► [ML Predictor]    ──► 15m & 30m Dual-Horizon Forecasts
        │
        ├─► [SQLite Database] ──► WAL Mode Persistence & Indexed Queries
        │
        └─► [WebSocket Bus]   ──► Real-Time Broadcast to Connected Dashboards
                 │
                 ▼
 [React + Vite + TypeScript Frontend]
   ├─ Overview Dashboard
   ├─ Live Telemetry Monitoring & Controls
   ├─ Interactive Leaflet GIS Traffic Map
   ├─ Prediction Center Sandbox
   ├─ Diurnal Historical Analytics & Figures
   ├─ Model Insights & Confusion Matrix
   └─ System Information & API Catalog
```

---

## 5. Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.11) | High-performance asynchronous REST API & native WebSocket support |
| **Streaming Server** | Uvicorn (ASGI) | Asynchronous event loop for concurrent streaming and client broadcasting |
| **Machine Learning** | Scikit-Learn 1.7.2, Joblib | Fast, serialized Histogram Gradient Boosting (HistGBM) ensembles |
| **Data Processing** | Pandas, NumPy | Vectorized time-series manipulation and feature engineering |
| **Database** | SQLite 3 (WAL Mode) | Zero-configuration local database with WAL concurrency and indices |
| **Scientific Visuals**| Matplotlib, Seaborn | Publication-quality analytical figures (`outputs/figures/`) |
| **Frontend Framework**| React 18, Vite, TypeScript | Modern, strongly-typed component architecture with sub-second HMR |
| **Mapping** | Leaflet with OpenStreetMap | Lightweight interactive GIS map with custom SVG telemetry markers |
| **Data Visualization**| Recharts | Composable responsive SVG charts for speeds, volumes, and trends |
| **Icons & Design** | Lucide React, Custom CSS | Clean slate modern light theme following ITS dashboard best practices |

---

## 6. Monitored Sensor Network

The system monitors 10 strategic multi-modal urban corridors:

| Sensor ID | Road Name | Segment ID | Lat / Lng | Speed Limit | Capacity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SENSOR-101` | North Interstate Expressway | `SEG-NORTH-EXPR-01` | 37.7749, -122.4194 | 100 km/h | 2,200 veh/h |
| `SENSOR-102` | Central Downtown Arterial | `SEG-DOWNTOWN-ART-02`| 37.7833, -122.4167 | 50 km/h | 1,200 veh/h |
| `SENSOR-103` | Harbor Bay Bridge Approach | `SEG-HARBOR-BRG-03` | 37.7952, -122.3938 | 80 km/h | 2,000 veh/h |
| `SENSOR-104` | Financial District Loop | `SEG-FINANCIAL-DIST-04`| 37.7915, -122.4010 | 40 km/h | 900 veh/h |
| `SENSOR-105` | Tech Hub Boulevard | `SEG-TECH-HUB-BLVD-05`| 37.7650, -122.3990 | 60 km/h | 1,500 veh/h |
| `SENSOR-106` | Westside Parkway | `SEG-WESTSIDE-PKWY-06`| 37.7580, -122.4450 | 70 km/h | 1,800 veh/h |
| `SENSOR-107` | Airport Link Freeway | `SEG-AIRPORT-FWY-07` | 37.7200, -122.3900 | 110 km/h | 2,400 veh/h |
| `SENSOR-108` | Midtown Transit Interchange | `SEG-MIDTOWN-INT-08` | 37.7780, -122.4280 | 45 km/h | 1,100 veh/h |
| `SENSOR-109` | East Industrial Bypass | `SEG-EAST-BYPASS-09` | 37.7500, -122.3850 | 65 km/h | 1,600 veh/h |
| `SENSOR-110` | University Campus Perimeter | `SEG-UNIV-CAMPUS-10` | 37.7620, -122.4580 | 40 km/h | 850 veh/h |

---

## 7. Project Directory Structure

```
Real-Time Traffic Congestion Predictive/
├── backend/
│   ├── api/
│   │   ├── routes.py                 # REST endpoints
│   │   └── websocket.py              # WebSocket connection manager
│   ├── database/
│   │   ├── connection.py             # SQLite WAL connection
│   │   ├── crud.py                   # Parameterized database queries
│   │   └── seed.py                   # Initial database seeder
│   ├── schemas/
│   │   └── traffic.py                # Pydantic validation schemas
│   ├── streaming/
│   │   ├── engine.py                 # Streaming worker & broadcast loop
│   │   └── sensor_simulator.py       # Greenshields IoT telemetry simulator
│   ├── tests/
│   │   ├── run_tests.py              # Async integration test suite
│   │   ├── test_api.py               # REST API tests
│   │   └── test_feature_engineering.py # Unit feature tests
│   ├── app.py                        # FastAPI entry point
│   └── traffic_analytics.db          # SQLite database file
├── data/
│   ├── generate_dataset.py           # 14-day 40,320 record data generator
│   ├── raw/
│   │   └── traffic_sensor_dataset.csv
│   └── sample/
│       └── traffic_sample_500.csv
├── docs/
│   ├── ARCHITECTURE.md               # Detailed system design
│   ├── DATABASE_SCHEMA.md            # Schema definitions & indices
│   └── METHODOLOGY.md                # Research methodology & formulas
├── frontend/
│   ├── src/
│   │   ├── components/Navbar.tsx     # Navigation & stream controls
│   │   ├── hooks/useTrafficStream.ts # WebSocket streaming hook
│   │   ├── pages/
│   │   │   ├── OverviewDashboard.tsx # Real-time KPIs & trends
│   │   │   ├── LiveMonitoring.tsx    # Live telemetry table & incident injection
│   │   │   ├── TrafficMap.tsx        # Leaflet OpenStreetMap GIS
│   │   │   ├── PredictionCenter.tsx  # Interactive ML prediction sandbox
│   │   │   ├── HistoricalAnalytics.tsx # Empirical charts & figures
│   │   │   ├── ModelInsights.tsx     # Confusion matrix & feature importances
│   │   │   └── SystemInformation.tsx # Architecture diagram & API catalog
│   │   ├── services/api.ts           # Typed API communication
│   │   ├── types/traffic.ts          # TypeScript interfaces
│   │   ├── App.tsx                   # Main layout container
│   │   ├── index.css                 # CSS Design System
│   │   └── main.tsx                  # React entry point
│   ├── index.html                    # SEO-optimized HTML entry
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── ml/
│   ├── models/
│   │   ├── congestion_classifier.joblib # Trained HistGBM Classifier
│   │   ├── speed_forecaster.joblib      # Trained HistGBM Regressor
│   │   └── scaler.joblib
│   ├── evaluate_model.py             # Generates publication figures
│   ├── feature_engineering.py        # Streaming & batch feature logic
│   ├── predict.py                    # Inference service with explainability
│   ├── preprocessing.py              # Data cleaning and bounds validation
│   └── train_model.py                # Chronological training pipeline
├── outputs/
│   ├── figures/                      # Publication-grade PNG charts
│   └── metrics/                      # JSON evaluation scorecards
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 8. Prerequisites

- **Python**: 3.10 or 3.11+
- **Node.js**: v18+ or v20+ (v22 verified)
- **NPM**: v9+ or v10+

---

## 9. Installation & Setup Instructions

### Step 1: Clone or Navigate to Directory
```bash
cd "d:/projects/Real-Time Traffic Congestion Predictive"
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 10. Reproduce Dataset, Train Models & Seed Database

All scripts are reproducible and deterministic:

### Step 1: Generate Ground-Truth Benchmark Dataset (14 Days, 40,320 Records)
```bash
python data/generate_dataset.py
```

### Step 2: Run Machine Learning Training Pipeline
```bash
python ml/train_model.py
```
*Trains HistGBM Classifier and Regressor using chronological split, evaluates against baselines, and persists models to `ml/models/` and metrics to `outputs/metrics/`.*

### Step 3: Generate Publication-Grade Analytical Figures
```bash
python ml/evaluate_model.py
```
*Generates 7 analytical figures in `outputs/figures/`.*

### Step 4: Seed Database with Initial Baseline Telemetry
```bash
python backend/database/seed.py
```

---

## 11. Running Automated Verification Tests

Run the full async test suite (10 test suites covering all endpoints, prediction validation, and feature calculations):

```bash
python backend/tests/run_tests.py
```

Expected output:
```text
=================================================================
ALL 10 TEST SUITES PASSED FLAWLESSLY (100% SUCCESS)!
=================================================================
```

---

## 12. Launching the Application

### Launch Backend Server (Port 8000)
From the project root:
```bash
python backend/app.py
```
*Or using Uvicorn directly:*
```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`
- WebSocket Endpoint: `ws://localhost:8000/api/ws/traffic-stream`

### Launch Frontend Dashboard (Port 5173)
In a separate terminal:
```bash
cd frontend
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 13. REST API Endpoint Reference

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service operational health check |
| `GET` | `/api/dashboard/summary` | Aggregated network KPIs, LOS breakdown, 24-hr trend |
| `GET` | `/api/sensors` | Monitored sensor nodes with coordinates and limits |
| `GET` | `/api/traffic/current` | Latest observed telemetry and predictions |
| `GET` | `/api/traffic/history` | Paginated historical observations with filters |
| `POST`| `/api/predictions/predict` | On-demand ML inference for custom parameters |
| `GET` | `/api/model/metrics` | Classification & regression evaluation scorecards |
| `GET` | `/api/stream/status` | Streaming engine status and connected clients count |
| `POST`| `/api/stream/toggle` | Start, pause, or resume the live telemetry stream |
| `POST`| `/api/stream/rate` | Configure streaming interval (seconds between events) |
| `POST`| `/api/stream/inject-incident`| Inject simulated road collision or bottleneck queue |
| `WS`  | `/api/ws/traffic-stream` | WebSocket channel broadcasting real-time observations |

---

## 14. Academic Evidence & Report Artifacts

The system provides persistent empirical evidence for academic publications in `outputs/`:
- `outputs/figures/traffic_speed_distribution.png`: Empirical speed distribution fit.
- `outputs/figures/hourly_traffic_patterns.png`: Diurnal inverse volume/speed curve.
- `outputs/figures/speed_vs_volume_fundamental_diagram.png`: Greenshields fundamental diagram.
- `outputs/figures/congestion_level_distribution.png`: HCM Level of Service distribution.
- `outputs/figures/model_confusion_matrix.png`: Multiclass confusion matrix.
- `outputs/figures/model_comparison_metrics.png`: Baseline comparison bar charts.
- `outputs/figures/feature_importance.png`: Top permutation feature importances.
- `outputs/metrics/classification_metrics.json`: Complete classification report and confusion counts.
- `outputs/metrics/regression_metrics.json`: MAE, RMSE, and $R^2$ scores.

---

## 15. Known Limitations & Future Enhancements

- **Physical IoT Hardware**: In the current deployment, live observations are generated via a high-fidelity simulator grounded in Greenshields physics. Real SCATS or PeMS roadside loop hardware can be interfaced by pointing `StreamingEngine` to external MQTT/Kafka broker topics.
- **Spatial Graph Neural Networks**: While HistGBM effectively captures temporal lags and corridor IDs, future iterations could integrate Spatio-Temporal Graph Convolutional Networks (ST-GCN) to model multi-hop congestion spillover across complex road networks.
