"""
Main Application Entry Point for Real-Time Traffic Congestion Prediction
FastAPI application with Lifespan management, REST endpoints, and WebSocket streaming.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "ml"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "data"))

from database.connection import init_db
from database.crud import get_current_traffic_state
from api.routes import router as api_router
from api.websocket import ws_manager
from streaming.engine import streaming_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("traffic.app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()

    logger.info("Starting background real-time streaming engine...")
    await streaming_engine.start()
    
    yield

    logger.info("Shutting down real-time streaming engine...")
    await streaming_engine.stop()

app = FastAPI(
    title="Real-Time Traffic Congestion Predictive Modeling API",
    description="Live IoT Sensor Stream Analytics & Predictive Modeling API grounded in Greenshields Traffic Physics and Machine Learning",
    version="1.2.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST routes
app.include_router(api_router)

# Mount outputs/figures directory so the frontend can display the analytical charts directly
figures_dir = os.path.join(PROJECT_ROOT, "outputs", "figures")
if os.path.exists(figures_dir):
    app.mount("/outputs/figures", StaticFiles(directory=figures_dir), name="figures")

@app.websocket("/api/ws/traffic-stream")
async def websocket_traffic_stream(websocket: WebSocket):
    """
    Real-time streaming endpoint for live IoT traffic observations and ML predictions.
    Pushes live events every N seconds as new telemetry arrives.
    """
    await ws_manager.connect(websocket)
    try:
        # Send initial network snapshot immediately upon connection
        current_state = get_current_traffic_state()
        await websocket.send_json({
            "type": "INITIAL_NETWORK_SNAPSHOT",
            "sensors": current_state,
            "stream_status": streaming_engine.get_status()
        })

        # Keep connection open and listen for client messages / pings
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket client error: {e}")
        ws_manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
