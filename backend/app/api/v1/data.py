"""Data API endpoints."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.data import TickData, DailyData, TelegramMessage
from app.schemas.data import TickDataSchema, DailyDataSchema, TelegramMessageSchema

router = APIRouter()


@router.get("/tick", response_model=list[TickDataSchema])
async def get_tick_data(
    currency_pair: str = Query("USD/LYD"),
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
):
    """Get tick data for the last N hours."""
    cutoff = datetime.now() - timedelta(hours=hours)
    
    result = await db.execute(
        select(TickData)
        .where(TickData.currency_pair == currency_pair)
        .where(TickData.timestamp >= cutoff)
        .order_by(TickData.timestamp.desc())
        .limit(1000)
    )
    
    records = result.scalars().all()
    return records


@router.get("/daily", response_model=list[DailyDataSchema])
async def get_daily_data(
    currency_pair: str = Query("USD/LYD"),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get daily data for the last N days."""
    cutoff = datetime.now() - timedelta(days=days)
    
    result = await db.execute(
        select(DailyData)
        .where(DailyData.currency_pair == currency_pair)
        .where(DailyData.date >= cutoff)
        .order_by(DailyData.date)
    )
    
    records = result.scalars().all()
    return records


@router.get("/messages", response_model=list[TelegramMessageSchema])
async def get_telegram_messages(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get recent Telegram messages."""
    cutoff = datetime.now() - timedelta(hours=hours)
    
    result = await db.execute(
        select(TelegramMessage)
        .where(TelegramMessage.timestamp >= cutoff)
        .order_by(TelegramMessage.timestamp.desc())
        .limit(limit)
    )
    
    records = result.scalars().all()
    return records


@router.get("/latest-price")
async def get_latest_price(
    currency_pair: str = Query("USD/LYD"),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest price for a currency pair."""
    result = await db.execute(
        select(TickData)
        .where(TickData.currency_pair == currency_pair)
        .order_by(TickData.timestamp.desc())
        .limit(1)
    )
    
    record = result.scalar_one_or_none()
    
    if not record:
        return {"currency_pair": currency_pair, "price": None, "timestamp": None}
    
    return {
        "currency_pair": currency_pair,
        "price": record.price,
        "price_type": record.price_type,
        "timestamp": record.timestamp.isoformat(),
        "source": record.source_channel,
    }
