"""Database models for tick data and daily data."""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, Integer, DateTime, Text, Index, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TickData(Base):
    """Model for real-time tick data from Telegram."""
    
    __tablename__ = "tick_data"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    currency_pair: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    price_type: Mapped[str] = mapped_column(String(10), nullable=False)  # 'buy' or 'sell'
    source_channel: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_message: Mapped[str] = mapped_column(Text, nullable=False)
    message_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    __table_args__ = (
        Index('ix_tick_data_timestamp_pair', 'timestamp', 'currency_pair'),
    )
    
    def __repr__(self) -> str:
        return f"<TickData(id={self.id}, pair={self.currency_pair}, price={self.price})>"


class DailyData(Base):
    """Model for daily EOD data from fulus.ly."""
    
    __tablename__ = "daily_data"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    currency_pair: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="fulus.ly")
    
    __table_args__ = (
        Index('ix_daily_data_date_pair', 'date', 'currency_pair'),
    )
    
    def __repr__(self) -> str:
        return f"<DailyData(date={self.date}, pair={self.currency_pair}, close={self.close})>"


class TelegramMessage(Base):
    """Model for storing all Telegram messages for sentiment analysis."""
    
    __tablename__ = "telegram_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(100), nullable=False)
    message_id: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    contains_price: Mapped[bool] = mapped_column(Integer, default=0)  # SQLite compatible
    
    __table_args__ = (
        Index('ix_telegram_messages_timestamp', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<TelegramMessage(id={self.id}, channel={self.channel})>"
