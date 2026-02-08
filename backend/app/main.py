"""Main FastAPI application."""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import engine, Base
from app.api.v1.routes import api_router
from app.services.telegram_scraper import TelegramPriceScraper
from app.services.fulus_sync import FulusSyncService
from app.api.websocket import ws_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Global service instances
telegram_scraper: TelegramPriceScraper = None
fulus_sync: FulusSyncService = None


async def init_database():
    """Initialize database and create tables."""
    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        
        # Enable TimescaleDB extension and create hypertables
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"))
            
            # Create hypertable for tick_data
            await conn.execute(text("""
                SELECT create_hypertable('tick_data', 'timestamp', 
                    if_not_exists => TRUE,
                    chunk_time_interval => INTERVAL '1 day'
                );
            """))
            
            # Create hypertable for daily_data
            await conn.execute(text("""
                SELECT create_hypertable('daily_data', 'date',
                    if_not_exists => TRUE,
                    chunk_time_interval => INTERVAL '7 days'
                );
            """))
            
            logger.info("TimescaleDB hypertables created successfully")
        except Exception as e:
            logger.warning(f"Could not create hypertables (using standard tables): {e}")


async def start_background_services():
    """Start background services."""
    global telegram_scraper, fulus_sync
    
    # Initialize Telegram scraper
    telegram_scraper = TelegramPriceScraper(
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        phone=settings.TELEGRAM_PHONE,
        session_name=settings.TELEGRAM_SESSION_NAME,
        channels=settings.TELEGRAM_CHANNELS,
    )
    
    # Set WebSocket callback
    telegram_scraper.set_websocket_callback(ws_manager.send_price_update)
    
    # Start scraper in background
    asyncio.create_task(run_telegram_scraper())
    
    # Initialize Fulus sync service
    fulus_sync = FulusSyncService()
    
    # Run initial sync
    asyncio.create_task(run_initial_sync())
    
    logger.info("Background services started")


async def run_telegram_scraper():
    """Run Telegram scraper."""
    try:
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            await telegram_scraper.set_db_session(session)
            await telegram_scraper.start_listening()
    except Exception as e:
        logger.error(f"Error in Telegram scraper: {e}", exc_info=True)


async def run_initial_sync():
    """Run initial sync of historical data."""
    try:
        from app.core.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            await fulus_sync.set_db_session(session)
            await fulus_sync.sync_all()
            
        # Start periodic sync
        asyncio.create_task(run_periodic_sync())
    except Exception as e:
        logger.error(f"Error in initial sync: {e}", exc_info=True)


async def run_periodic_sync():
    """Run periodic sync of historical data."""
    try:
        await fulus_sync.run_periodic_sync(interval_hours=24)
    except Exception as e:
        logger.error(f"Error in periodic sync: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Libyan Financial Terminal API")
    await init_database()
    await start_background_services()
    
    yield
    
    # Shutdown
    logger.info("Shutting down API")
    if telegram_scraper:
        await telegram_scraper.stop()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time Libyan financial terminal API",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
