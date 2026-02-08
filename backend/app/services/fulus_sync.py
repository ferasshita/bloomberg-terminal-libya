"""Fulus.ly API sync service for historical data."""
import asyncio
from datetime import datetime, timedelta
from typing import Optional
import logging

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.data import DailyData

logger = logging.getLogger(__name__)
settings = get_settings()


class FulusSyncService:
    """
    Service for syncing historical daily EOD rates from fulus.ly API.
    
    Features:
    - Fetches daily exchange rates
    - Handles multiple currency pairs
    - Incremental sync (only new data)
    - Saves to TimescaleDB
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """Initialize the sync service."""
        self.api_url = api_url or settings.FULUS_API_URL
        self.db_session: Optional[AsyncSession] = None
        
    async def set_db_session(self, session: AsyncSession):
        """Set database session."""
        self.db_session = session
        
    async def get_last_sync_date(self, currency_pair: str) -> Optional[datetime]:
        """Get the last synced date for a currency pair."""
        if not self.db_session:
            return None
        
        result = await self.db_session.execute(
            select(DailyData.date)
            .where(DailyData.currency_pair == currency_pair)
            .order_by(DailyData.date.desc())
            .limit(1)
        )
        
        last_date = result.scalar_one_or_none()
        return last_date
    
    async def fetch_rates(
        self,
        currency_pair: str = "USD/LYD",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> list[dict]:
        """
        Fetch historical rates from fulus.ly API.
        
        Note: This is a mock implementation. Adjust based on actual API.
        """
        if not end_date:
            end_date = datetime.now()
        
        if not start_date:
            # Default to 30 days ago
            start_date = end_date - timedelta(days=30)
        
        # Mock API call - replace with actual fulus.ly API
        # For now, generate synthetic data
        logger.info(f"Fetching rates for {currency_pair} from {start_date} to {end_date}")
        
        try:
            async with httpx.AsyncClient() as client:
                # Example API endpoint (adjust based on actual API)
                response = await client.get(
                    f"{self.api_url}/rates",
                    params={
                        "pair": currency_pair,
                        "start": start_date.strftime("%Y-%m-%d"),
                        "end": end_date.strftime("%Y-%m-%d"),
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json().get("data", [])
                else:
                    logger.warning(f"API returned status {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error fetching rates: {e}")
            # Return synthetic data for development
            return self._generate_synthetic_data(currency_pair, start_date, end_date)
    
    def _generate_synthetic_data(
        self,
        currency_pair: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict]:
        """Generate synthetic historical data for development."""
        data = []
        current_date = start_date
        base_price = 4.8 if "USD" in currency_pair else 5.2
        
        while current_date <= end_date:
            # Simple random walk
            import random
            price_change = random.uniform(-0.1, 0.1)
            base_price += price_change
            
            data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "open": round(base_price + random.uniform(-0.05, 0.05), 4),
                "high": round(base_price + random.uniform(0, 0.1), 4),
                "low": round(base_price - random.uniform(0, 0.1), 4),
                "close": round(base_price, 4),
                "volume": random.randint(100000, 500000),
            })
            
            current_date += timedelta(days=1)
        
        return data
    
    async def save_daily_data(self, currency_pair: str, data: list[dict]):
        """Save daily data to database."""
        if not self.db_session:
            logger.warning("No database session available")
            return
        
        for item in data:
            daily = DailyData(
                date=datetime.strptime(item["date"], "%Y-%m-%d"),
                currency_pair=currency_pair,
                open=item["open"],
                high=item["high"],
                low=item["low"],
                close=item["close"],
                volume=item.get("volume"),
                source="fulus.ly",
            )
            
            self.db_session.add(daily)
        
        await self.db_session.commit()
        logger.info(f"Saved {len(data)} daily records for {currency_pair}")
    
    async def sync_currency_pair(
        self,
        currency_pair: str = "USD/LYD",
        days_back: int = 30,
    ):
        """Sync a specific currency pair."""
        # Get last sync date
        last_sync = await self.get_last_sync_date(currency_pair)
        
        if last_sync:
            start_date = last_sync + timedelta(days=1)
        else:
            start_date = datetime.now() - timedelta(days=days_back)
        
        end_date = datetime.now()
        
        if start_date > end_date:
            logger.info(f"{currency_pair} is up to date")
            return
        
        # Fetch and save data
        data = await self.fetch_rates(currency_pair, start_date, end_date)
        
        if data:
            await self.save_daily_data(currency_pair, data)
        else:
            logger.warning(f"No data fetched for {currency_pair}")
    
    async def sync_all(self, currency_pairs: Optional[list[str]] = None):
        """Sync all configured currency pairs."""
        if not currency_pairs:
            currency_pairs = ["USD/LYD", "EUR/LYD"]
        
        for pair in currency_pairs:
            try:
                await self.sync_currency_pair(pair)
            except Exception as e:
                logger.error(f"Error syncing {pair}: {e}", exc_info=True)
    
    async def run_periodic_sync(self, interval_hours: int = 24):
        """Run periodic sync task."""
        while True:
            try:
                logger.info("Starting periodic sync")
                await self.sync_all()
                logger.info("Periodic sync completed")
            except Exception as e:
                logger.error(f"Error in periodic sync: {e}", exc_info=True)
            
            # Wait for next sync
            await asyncio.sleep(interval_hours * 3600)
