"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class TickDataSchema(BaseModel):
    """Schema for tick data."""
    
    id: int
    timestamp: datetime
    currency_pair: str
    price: float
    price_type: str
    source_channel: str
    raw_message: str
    message_id: Optional[int] = None
    
    model_config = {"from_attributes": True}


class DailyDataSchema(BaseModel):
    """Schema for daily data."""
    
    id: int
    date: datetime
    currency_pair: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
    source: str
    
    model_config = {"from_attributes": True}


class PriceUpdateSchema(BaseModel):
    """Schema for real-time price updates via WebSocket."""
    
    timestamp: datetime
    currency_pair: str
    price: float
    price_type: str
    change_percent: Optional[float] = None
    source_channel: str


class ForecastSchema(BaseModel):
    """Schema for forecast data."""
    
    timestamp: datetime
    currency_pair: str
    predicted_price: float
    lower_bound: float
    upper_bound: float
    confidence: float


class SignalSchema(BaseModel):
    """Schema for buy/sell signals."""
    
    signal: Literal["BUY", "SELL", "HOLD"]
    confidence: float = Field(ge=0, le=100)
    rsi: float
    market_panic_index: float
    reasoning: str


class AnalysisResponseSchema(BaseModel):
    """Schema for complete analysis response."""
    
    current_price: float
    currency_pair: str
    forecast_24h: list[ForecastSchema]
    forecast_48h: list[ForecastSchema]
    signal: SignalSchema
    recent_messages: list[dict]
    ai_reasoning: str


class TelegramMessageSchema(BaseModel):
    """Schema for Telegram messages."""
    
    timestamp: datetime
    channel: str
    text: str
    sentiment_score: Optional[float] = None
    contains_price: bool
    
    model_config = {"from_attributes": True}
