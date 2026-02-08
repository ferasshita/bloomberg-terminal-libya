"""Analysis service with signal generation and AI reasoning."""
from datetime import datetime, timedelta
from typing import Optional
import logging

import pandas as pd
from ta.momentum import RSIIndicator
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.models.data import TickData, TelegramMessage
from app.services.forecasting import ForecastingService

logger = logging.getLogger(__name__)
settings = get_settings()


class AnalysisService:
    """
    Complete analysis service combining forecasting, signals, and AI reasoning.
    
    Features:
    - RSI-based buy/sell signals
    - Market panic index from sentiment
    - AI reasoning using LLM
    - Complete market analysis
    """
    
    # Volatility keywords for panic index
    PANIC_KEYWORDS = [
        'أزمة', 'انهيار', 'crisis', 'collapse', 'panic',
        'shortage', 'نقص', 'liquidity', 'سيولة',
        'black market', 'السوق السوداء', 'inflation', 'تضخم',
    ]
    
    def __init__(self):
        """Initialize analysis service."""
        self.db_session: Optional[AsyncSession] = None
        self.forecasting = ForecastingService()
        self.openai_client: Optional[AsyncOpenAI] = None
        
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def set_db_session(self, session: AsyncSession):
        """Set database session."""
        self.db_session = session
        await self.forecasting.set_db_session(session)
    
    async def get_current_price(self, currency_pair: str) -> Optional[float]:
        """Get the most recent price for a currency pair."""
        if not self.db_session:
            return None
        
        result = await self.db_session.execute(
            select(TickData.price)
            .where(TickData.currency_pair == currency_pair)
            .order_by(TickData.timestamp.desc())
            .limit(1)
        )
        
        return result.scalar_one_or_none()
    
    async def calculate_rsi(
        self,
        currency_pair: str,
        period: int = 14,
    ) -> Optional[float]:
        """Calculate RSI indicator."""
        if not self.db_session:
            return None
        
        # Get recent tick data
        cutoff = datetime.now() - timedelta(days=30)
        
        result = await self.db_session.execute(
            select(TickData)
            .where(TickData.currency_pair == currency_pair)
            .where(TickData.timestamp >= cutoff)
            .order_by(TickData.timestamp)
        )
        
        records = result.scalars().all()
        
        if len(records) < period + 1:
            logger.warning(f"Insufficient data for RSI calculation: {len(records)}")
            return 50.0  # Neutral RSI
        
        # Convert to DataFrame
        data = pd.DataFrame([
            {"timestamp": r.timestamp, "price": r.price}
            for r in records
        ])
        
        # Calculate RSI
        rsi_indicator = RSIIndicator(close=data["price"], window=period)
        rsi = rsi_indicator.rsi()
        
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    
    async def calculate_market_panic_index(self) -> float:
        """
        Calculate market panic index based on Telegram message sentiment.
        
        Returns a value between 0 (calm) and 100 (panic).
        """
        if not self.db_session:
            return 0.0
        
        # Get last 100 messages
        cutoff = datetime.now() - timedelta(hours=24)
        
        result = await self.db_session.execute(
            select(TelegramMessage)
            .where(TelegramMessage.timestamp >= cutoff)
            .order_by(TelegramMessage.timestamp.desc())
            .limit(100)
        )
        
        messages = result.scalars().all()
        
        if not messages:
            return 0.0
        
        # Count panic keywords
        panic_count = 0
        for message in messages:
            text_lower = message.text.lower()
            for keyword in self.PANIC_KEYWORDS:
                if keyword.lower() in text_lower:
                    panic_count += 1
                    break
        
        # Calculate index (0-100)
        panic_index = min((panic_count / len(messages)) * 100, 100)
        
        return round(panic_index, 2)
    
    def generate_signal(
        self,
        rsi: float,
        panic_index: float,
        forecast_trend: str = "neutral",
    ) -> dict:
        """
        Generate buy/sell signal based on RSI and panic index.
        
        Logic:
        - RSI < 30: Oversold -> BUY
        - RSI > 70: Overbought -> SELL
        - High panic (>60): Caution -> HOLD/SELL
        - Forecast uptrend + low RSI: Strong BUY
        """
        signal = "HOLD"
        confidence = 50.0
        reasoning = ""
        
        # RSI-based signal
        if rsi < 30:
            signal = "BUY"
            confidence = 70.0
            reasoning = "RSI indicates oversold conditions. "
        elif rsi > 70:
            signal = "SELL"
            confidence = 70.0
            reasoning = "RSI indicates overbought conditions. "
        elif rsi < 40:
            signal = "BUY"
            confidence = 60.0
            reasoning = "RSI approaching oversold territory. "
        elif rsi > 60:
            signal = "SELL"
            confidence = 60.0
            reasoning = "RSI approaching overbought territory. "
        
        # Adjust for panic index
        if panic_index > 60:
            if signal == "BUY":
                confidence *= 0.7  # Reduce confidence
            elif signal == "HOLD":
                signal = "SELL"
                confidence = 55.0
            reasoning += f"High market panic detected ({panic_index:.0f}/100). "
        elif panic_index < 20:
            reasoning += "Market sentiment is calm. "
        
        # Adjust for forecast (if provided)
        if forecast_trend == "up" and signal == "BUY":
            confidence = min(confidence * 1.2, 95.0)
            reasoning += "Forecast confirms upward trend. "
        elif forecast_trend == "down" and signal == "SELL":
            confidence = min(confidence * 1.2, 95.0)
            reasoning += "Forecast confirms downward trend. "
        
        return {
            "signal": signal,
            "confidence": round(confidence, 2),
            "rsi": round(rsi, 2),
            "market_panic_index": panic_index,
            "reasoning": reasoning.strip(),
        }
    
    async def get_recent_messages(self, limit: int = 10) -> list[dict]:
        """Get recent Telegram messages for context."""
        if not self.db_session:
            return []
        
        result = await self.db_session.execute(
            select(TelegramMessage)
            .order_by(TelegramMessage.timestamp.desc())
            .limit(limit)
        )
        
        messages = result.scalars().all()
        
        return [
            {
                "timestamp": msg.timestamp.isoformat(),
                "channel": msg.channel,
                "text": msg.text[:200],  # Truncate
                "contains_price": msg.contains_price,
            }
            for msg in messages
        ]
    
    async def generate_ai_reasoning(
        self,
        currency_pair: str,
        current_price: float,
        forecast_data: dict,
        signal_data: dict,
        recent_messages: list[dict],
    ) -> str:
        """
        Generate AI reasoning using LLM.
        
        Provides human-readable explanation of market conditions.
        """
        if not self.openai_client:
            return "AI reasoning unavailable (no API key configured)."
        
        # Prepare context
        message_summaries = "\n".join([
            f"- {msg['channel']}: {msg['text'][:100]}"
            for msg in recent_messages[:5]
        ])
        
        prompt = f"""You are a financial analyst for Libyan currency markets. Analyze the following data and provide a concise explanation (2-3 sentences) of why the {currency_pair} rate is moving.

Current Price: {current_price}
RSI: {signal_data['rsi']}
Market Panic Index: {signal_data['market_panic_index']}/100
Signal: {signal_data['signal']} (Confidence: {signal_data['confidence']}%)

Recent Telegram Messages:
{message_summaries}

Provide a clear, actionable summary of market conditions and the reasoning behind the current {signal_data['signal']} signal."""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in Libyan currency markets."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI reasoning: {e}")
            return f"Market shows {signal_data['signal']} signal with {signal_data['confidence']:.0f}% confidence based on technical indicators."
    
    async def analyze(
        self,
        currency_pair: str = "USD/LYD",
    ) -> dict:
        """
        Perform complete analysis for a currency pair.
        
        Returns comprehensive analysis with forecast, signals, and AI reasoning.
        """
        # Get current price
        current_price = await self.get_current_price(currency_pair)
        
        if not current_price:
            logger.warning(f"No current price data for {currency_pair}")
            current_price = 0.0
        
        # Get forecast
        forecast_24h = await self.forecasting.forecast_currency(currency_pair, hours=24)
        forecast_48h = await self.forecasting.forecast_currency(currency_pair, hours=48)
        
        # Calculate RSI
        rsi = await self.calculate_rsi(currency_pair)
        
        # Calculate panic index
        panic_index = await self.calculate_market_panic_index()
        
        # Determine forecast trend
        forecast_trend = "neutral"
        if forecast_24h.get("forecast"):
            first_price = forecast_24h["forecast"][0]["predicted_price"]
            last_price = forecast_24h["forecast"][-1]["predicted_price"]
            if last_price > first_price * 1.01:
                forecast_trend = "up"
            elif last_price < first_price * 0.99:
                forecast_trend = "down"
        
        # Generate signal
        signal = self.generate_signal(rsi or 50.0, panic_index, forecast_trend)
        
        # Get recent messages
        recent_messages = await self.get_recent_messages()
        
        # Generate AI reasoning
        ai_reasoning = await self.generate_ai_reasoning(
            currency_pair,
            current_price,
            forecast_24h,
            signal,
            recent_messages,
        )
        
        return {
            "current_price": current_price,
            "currency_pair": currency_pair,
            "forecast_24h": forecast_24h.get("forecast", []),
            "forecast_48h": forecast_48h.get("forecast", []),
            "signal": signal,
            "recent_messages": recent_messages,
            "ai_reasoning": ai_reasoning,
        }
