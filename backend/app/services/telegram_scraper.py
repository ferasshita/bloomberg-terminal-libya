"""Telegram price scraper using Telethon."""
import asyncio
import re
from datetime import datetime
from typing import Optional, Callable
import logging

from telethon import TelegramClient, events
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.data import TickData, TelegramMessage

logger = logging.getLogger(__name__)
settings = get_settings()


class TelegramPriceScraper:
    """
    Scraper for monitoring Libyan Telegram channels for currency prices.
    
    Features:
    - Connects to Telegram using Telethon
    - Monitors specified channels for price updates
    - Parses Arabic and English price formats
    - Handles buy/sell price distinctions
    - Rate limiting with buffer
    - Saves to TimescaleDB
    """
    
    # Regex patterns for price matching
    PRICE_PATTERNS = [
        # Arabic patterns
        r'(?:سعر|صرف)\s*(?:الدولار|اليورو|USD|EUR)\s*(?:الآن)?\s*:?\s*(\d+\.?\d*)',
        r'(USD|EUR)/LYD\s*:?\s*(\d+\.?\d*)',
        r'(?:الدولار|اليورو)\s*(?:بـ)?\s*(\d+\.?\d*)',
        # English patterns
        r'USD\s*(?:rate|price)?\s*:?\s*(\d+\.?\d*)',
        r'EUR\s*(?:rate|price)?\s*:?\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:LYD|دينار)',
    ]
    
    # Buy/Sell indicators
    BUY_KEYWORDS = ['شراء', 'buy', 'bid', 'buying']
    SELL_KEYWORDS = ['بيع', 'sell', 'ask', 'selling']
    
    # Currency pair mapping
    CURRENCY_MAP = {
        'دولار': 'USD/LYD',
        'يورو': 'EUR/LYD',
        'USD': 'USD/LYD',
        'EUR': 'EUR/LYD',
    }
    
    def __init__(
        self,
        api_id: str,
        api_hash: str,
        phone: Optional[str] = None,
        session_name: str = "scraper_session",
        channels: Optional[list[str]] = None,
    ):
        """Initialize the Telegram scraper."""
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.channels = channels or settings.TELEGRAM_CHANNELS
        
        self.client: Optional[TelegramClient] = None
        self.db_session: Optional[AsyncSession] = None
        self.ws_callback: Optional[Callable] = None
        self.last_message_time = datetime.now()
        self.buffer_seconds = settings.SCRAPER_BUFFER_SECONDS
        
    async def connect(self):
        """Connect to Telegram."""
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        await self.client.start(phone=self.phone)
        logger.info("Connected to Telegram")
        
    async def set_db_session(self, session: AsyncSession):
        """Set database session."""
        self.db_session = session
        
    def set_websocket_callback(self, callback: Callable):
        """Set callback for WebSocket emissions."""
        self.ws_callback = callback
        
    def parse_price(self, text: str) -> Optional[dict]:
        """
        Parse price information from message text.
        
        Returns dict with: currency_pair, price, price_type
        """
        text_lower = text.lower()
        
        # Determine currency pair
        currency_pair = None
        for keyword, pair in self.CURRENCY_MAP.items():
            if keyword.lower() in text_lower:
                currency_pair = pair
                break
        
        if not currency_pair:
            # Default to USD/LYD if dollar mentioned
            if 'dollar' in text_lower or 'دولار' in text:
                currency_pair = 'USD/LYD'
            else:
                return None
        
        # Extract price
        price = None
        for pattern in self.PRICE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Get the last group (the price number)
                groups = match.groups()
                price_str = groups[-1] if len(groups) > 0 else groups[0]
                try:
                    price = float(price_str)
                    break
                except (ValueError, IndexError):
                    continue
        
        if not price or price <= 0 or price > 100:  # Sanity check
            return None
        
        # Determine buy/sell
        price_type = "mid"  # Default
        for keyword in self.BUY_KEYWORDS:
            if keyword in text_lower:
                price_type = "buy"
                break
        
        for keyword in self.SELL_KEYWORDS:
            if keyword in text_lower:
                price_type = "sell"
                break
        
        return {
            "currency_pair": currency_pair,
            "price": price,
            "price_type": price_type,
        }
    
    async def save_tick_data(
        self,
        currency_pair: str,
        price: float,
        price_type: str,
        source_channel: str,
        raw_message: str,
        message_id: int,
    ):
        """Save tick data to database."""
        if not self.db_session:
            logger.warning("No database session available")
            return
        
        tick = TickData(
            timestamp=datetime.now(),
            currency_pair=currency_pair,
            price=price,
            price_type=price_type,
            source_channel=source_channel,
            raw_message=raw_message,
            message_id=message_id,
        )
        
        self.db_session.add(tick)
        await self.db_session.commit()
        logger.info(f"Saved tick: {currency_pair} @ {price}")
        
    async def save_message(
        self,
        channel: str,
        message_id: int,
        text: str,
        contains_price: bool,
    ):
        """Save Telegram message for sentiment analysis."""
        if not self.db_session:
            return
        
        message = TelegramMessage(
            timestamp=datetime.now(),
            channel=channel,
            message_id=message_id,
            text=text,
            contains_price=contains_price,
        )
        
        self.db_session.add(message)
        await self.db_session.commit()
        
    async def handle_message(self, event):
        """Handle incoming Telegram message."""
        # Rate limiting buffer
        now = datetime.now()
        time_diff = (now - self.last_message_time).total_seconds()
        if time_diff < self.buffer_seconds:
            await asyncio.sleep(self.buffer_seconds - time_diff)
        
        self.last_message_time = datetime.now()
        
        # Get message details
        message = event.message
        text = message.text or ""
        channel = event.chat.username or str(event.chat_id)
        
        logger.info(f"Message from {channel}: {text[:50]}...")
        
        # Parse price
        price_data = self.parse_price(text)
        
        # Save message for sentiment analysis
        await self.save_message(
            channel=channel,
            message_id=message.id,
            text=text,
            contains_price=price_data is not None,
        )
        
        if price_data:
            # Save tick data
            await self.save_tick_data(
                currency_pair=price_data["currency_pair"],
                price=price_data["price"],
                price_type=price_data["price_type"],
                source_channel=channel,
                raw_message=text,
                message_id=message.id,
            )
            
            # Emit via WebSocket
            if self.ws_callback:
                await self.ws_callback({
                    "type": "price_update",
                    "data": {
                        "timestamp": datetime.now().isoformat(),
                        "currency_pair": price_data["currency_pair"],
                        "price": price_data["price"],
                        "price_type": price_data["price_type"],
                        "source_channel": channel,
                    }
                })
    
    async def start_listening(self):
        """Start listening to configured channels."""
        if not self.client:
            await self.connect()
        
        # Register handler for new messages
        @self.client.on(events.NewMessage(chats=self.channels))
        async def message_handler(event):
            try:
                await self.handle_message(event)
            except Exception as e:
                logger.error(f"Error handling message: {e}", exc_info=True)
        
        logger.info(f"Listening to channels: {self.channels}")
        
        # Run until disconnected
        await self.client.run_until_disconnected()
    
    async def stop(self):
        """Stop the scraper."""
        if self.client:
            await self.client.disconnect()
            logger.info("Disconnected from Telegram")
