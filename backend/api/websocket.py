"""
WebSocket Connection Manager for Real-Time Traffic Stream Broadcast
"""

import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("traffic.websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast_json(self, data: Dict[str, Any]):
        if not self.active_connections:
            return
        
        # Serialize once
        message_str = json.dumps(data)
        stale_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Error sending to WebSocket client: {e}")
                stale_connections.append(connection)

        for stale in stale_connections:
            self.disconnect(stale)

    @property
    def client_count(self) -> int:
        return len(self.active_connections)

ws_manager = ConnectionManager()
