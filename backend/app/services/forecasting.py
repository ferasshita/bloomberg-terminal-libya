"""Forecasting service using Meta's Prophet."""
from datetime import datetime, timedelta
from typing import Optional
import logging

import pandas as pd
from prophet import Prophet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.data import DailyData, TickData

logger = logging.getLogger(__name__)


class ForecastingService:
    """
    Forecasting service using Meta's Prophet.
    
    Features:
    - Time series forecasting for currency rates
    - 24h and 48h predictions
    - Confidence intervals
    - Uses historical data from TimescaleDB
    """
    
    def __init__(self):
        """Initialize forecasting service."""
        self.db_session: Optional[AsyncSession] = None
        
    async def set_db_session(self, session: AsyncSession):
        """Set database session."""
        self.db_session = session
    
    async def get_historical_data(
        self,
        currency_pair: str,
        days: int = 30,
    ) -> pd.DataFrame:
        """
        Get historical data for forecasting.
        
        Combines daily data with aggregated tick data.
        """
        if not self.db_session:
            raise ValueError("Database session not set")
        
        # Get daily data
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = await self.db_session.execute(
            select(DailyData)
            .where(DailyData.currency_pair == currency_pair)
            .where(DailyData.date >= cutoff_date)
            .order_by(DailyData.date)
        )
        
        daily_records = result.scalars().all()
        
        if not daily_records:
            # Fallback to tick data
            logger.warning(f"No daily data found for {currency_pair}, using tick data")
            return await self._get_tick_data_aggregated(currency_pair, days)
        
        # Convert to DataFrame
        data = []
        for record in daily_records:
            data.append({
                "ds": record.date,
                "y": record.close,
            })
        
        df = pd.DataFrame(data)
        return df
    
    async def _get_tick_data_aggregated(
        self,
        currency_pair: str,
        days: int,
    ) -> pd.DataFrame:
        """Aggregate tick data into daily format."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = await self.db_session.execute(
            select(TickData)
            .where(TickData.currency_pair == currency_pair)
            .where(TickData.timestamp >= cutoff_date)
            .order_by(TickData.timestamp)
        )
        
        tick_records = result.scalars().all()
        
        if not tick_records:
            logger.warning(f"No tick data found for {currency_pair}")
            return pd.DataFrame(columns=["ds", "y"])
        
        # Convert to DataFrame and aggregate by day
        data = []
        for record in tick_records:
            data.append({
                "timestamp": record.timestamp,
                "price": record.price,
            })
        
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        
        # Aggregate by date (use mean price)
        daily_df = df.groupby("date").agg({"price": "mean"}).reset_index()
        daily_df.columns = ["ds", "y"]
        daily_df["ds"] = pd.to_datetime(daily_df["ds"])
        
        return daily_df
    
    def train_model(self, df: pd.DataFrame) -> Prophet:
        """Train Prophet model on historical data."""
        if len(df) < 2:
            raise ValueError("Not enough data for forecasting")
        
        # Configure Prophet
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=False,
            changepoint_prior_scale=0.05,
            interval_width=0.95,
        )
        
        # Fit model
        model.fit(df)
        
        return model
    
    def generate_forecast(
        self,
        model: Prophet,
        periods: int = 48,  # hours
    ) -> pd.DataFrame:
        """Generate forecast for the next N periods."""
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq="H")
        
        # Generate predictions
        forecast = model.predict(future)
        
        return forecast
    
    async def forecast_currency(
        self,
        currency_pair: str,
        hours: int = 48,
    ) -> dict:
        """
        Generate forecast for a currency pair.
        
        Returns:
            Dictionary with forecast data and confidence intervals
        """
        try:
            # Get historical data
            df = await self.get_historical_data(currency_pair)
            
            if len(df) < 2:
                logger.warning(f"Insufficient data for {currency_pair}")
                return {
                    "currency_pair": currency_pair,
                    "forecast": [],
                    "error": "Insufficient historical data"
                }
            
            # Train model
            model = self.train_model(df)
            
            # Generate forecast
            forecast = self.generate_forecast(model, periods=hours)
            
            # Get future predictions only
            future_forecast = forecast[forecast["ds"] > datetime.now()]
            
            # Format results
            results = []
            for _, row in future_forecast.iterrows():
                results.append({
                    "timestamp": row["ds"].isoformat(),
                    "predicted_price": round(row["yhat"], 4),
                    "lower_bound": round(row["yhat_lower"], 4),
                    "upper_bound": round(row["yhat_upper"], 4),
                    "confidence": 0.95,
                })
            
            return {
                "currency_pair": currency_pair,
                "forecast": results[:hours],  # Limit to requested hours
                "model_info": {
                    "training_samples": len(df),
                    "forecast_period_hours": hours,
                }
            }
            
        except Exception as e:
            logger.error(f"Error forecasting {currency_pair}: {e}", exc_info=True)
            return {
                "currency_pair": currency_pair,
                "forecast": [],
                "error": str(e)
            }
    
    async def forecast_multiple(
        self,
        currency_pairs: list[str],
        hours: int = 24,
    ) -> dict:
        """Generate forecasts for multiple currency pairs."""
        results = {}
        
        for pair in currency_pairs:
            results[pair] = await self.forecast_currency(pair, hours)
        
        return results
