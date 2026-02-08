"""API v1 routes."""
from fastapi import APIRouter

from app.api.v1 import data, analysis, websocket

api_router = APIRouter()

api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
