"""WebSocket manager for real-time updates."""
import json
import logging
from typing import Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manager for WebSocket connections."""
    
    def __init__(self):
        """Initialize the WebSocket manager."""
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_price_update(self, data: dict):
        """Send price update to all clients."""
        await self.broadcast({
            "type": "price_update",
            "data": data,
        })
    
    async def send_analysis_update(self, data: dict):
        """Send analysis update to all clients."""
        await self.broadcast({
            "type": "analysis_update",
            "data": data,
        })


# Global WebSocket manager instance
ws_manager = WebSocketManager()
