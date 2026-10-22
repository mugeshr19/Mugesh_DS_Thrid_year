"""
Real-Time Streaming Engine for IoT Traffic Analytics
Continuously ingests simulated or live sensor telemetry, runs ML inference,
persists observations and predictions to SQLite, and broadcasts via WebSockets.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Ensure paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ml")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data")))

from database.crud import (
    get_all_sensors, insert_observation, insert_prediction,
    get_recent_sensor_history
)
from streaming.sensor_simulator import SensorSimulator
from api.websocket import ws_manager
from predict import get_predictor
from generate_dataset import SENSORS

logger = logging.getLogger("traffic.streaming")

class StreamingEngine:
    def __init__(self, interval_seconds: float = 3.0):
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.simulator = SensorSimulator(SENSORS)
        self.predictor = None
        self.sensor_buffers: Dict[str, List[Dict[str, Any]]] = {}
        self.events_processed = 0
        self.last_stream_time = None
        self.sensor_ids = [s["sensor_id"] for s in SENSORS]
        self._init_sensor_buffers()

    def _init_sensor_buffers(self):
        """Loads the last 4 observations per sensor into in-memory buffer."""
        for s_id in self.sensor_ids:
            recent = get_recent_sensor_history(s_id, limit=4)
            self.sensor_buffers[s_id] = recent if recent else []

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        if self.predictor is None:
            self.predictor = get_predictor()
        self.task = asyncio.create_task(self._run_loop())
        logger.info(f"Streaming engine started with interval {self.interval_seconds}s across {len(self.sensor_ids)} sensors.")

    async def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Streaming engine stopped.")

    def set_interval(self, seconds: float):
        self.interval_seconds = max(0.5, min(30.0, float(seconds)))
        logger.info(f"Stream interval updated to {self.interval_seconds}s")

    def inject_incident(self, sensor_id: str, severity: float = 0.65, duration_seconds: int = 60):
        self.simulator.inject_incident(sensor_id, severity, duration_seconds)
        logger.warning(f"Simulated incident injected on {sensor_id}: {severity*100}% speed drop for {duration_seconds}s")

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "interval_seconds": self.interval_seconds,
            "events_processed": self.events_processed,
            "connected_ws_clients": ws_manager.client_count,
            "last_stream_time": self.last_stream_time or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "active_incidents": {
                k: v["description"] for k, v in self.simulator.active_incidents.items()
            },
            "sensor_count": len(self.sensor_ids),
            "stream_mode": "SIMULATED_LIVE_STREAM"
        }

    async def _run_loop(self):
        sensor_index = 0
        while self.is_running:
            try:
                # Round-robin emit a sensor reading, or batch-emit 2 sensors per tick
                for _ in range(2):
                    s_id = self.sensor_ids[sensor_index]
                    sensor_index = (sensor_index + 1) % len(self.sensor_ids)
                    await self._process_sensor_tick(s_id)

                self.last_stream_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                await asyncio.sleep(self.interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in streaming loop: {e}", exc_info=True)
                await asyncio.sleep(self.interval_seconds)

    async def _process_sensor_tick(self, sensor_id: str):
        # 1. Generate observation
        obs = self.simulator.generate_observation(sensor_id)
        
        # 2. Get history buffer for feature engineering
        history = self.sensor_buffers.get(sensor_id, [])

        # 3. Run real-time ML prediction
        prediction = self.predictor.predict(obs, sensor_history=history)

        # 4. Persist to DB
        try:
            obs_id = insert_observation(obs)
            obs["id"] = obs_id
            if prediction.get("status") == "SUCCESS":
                pred_id = insert_prediction(prediction)
                prediction["id"] = pred_id
        except Exception as e:
            logger.error(f"Database write error for {sensor_id}: {e}")

        # 5. Update in-memory buffer (keep last 5)
        history.append(obs)
        if len(history) > 5:
            history.pop(0)
        self.sensor_buffers[sensor_id] = history
        self.events_processed += 1

        # 6. Broadcast over WebSocket to all connected clients
        broadcast_payload = {
            "type": "TRAFFIC_OBSERVATION_AND_PREDICTION",
            "timestamp": obs["timestamp"],
            "observation": obs,
            "prediction": prediction,
            "stream_stats": {
                "events_processed": self.events_processed,
                "interval_seconds": self.interval_seconds
            }
        }
        await ws_manager.broadcast_json(broadcast_payload)

# Singleton engine instance
streaming_engine = StreamingEngine(interval_seconds=3.0)
