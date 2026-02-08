"""WebSocket endpoint."""
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from app.api.websocket import ws_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    
    Clients connect to receive:
    - Price updates
    - Analysis updates
    - Market alerts
    """
    await ws_manager.connect(websocket)
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to Libyan Financial Terminal"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            
            # Handle ping/pong for keepalive
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
