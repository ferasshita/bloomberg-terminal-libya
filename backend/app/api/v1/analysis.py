"""Analysis API endpoints."""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analysis import AnalysisService
from app.schemas.data import AnalysisResponseSchema

router = APIRouter()


@router.get("/complete", response_model=AnalysisResponseSchema)
async def get_complete_analysis(
    currency_pair: str = Query("USD/LYD"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get complete analysis including:
    - Current price
    - 24h and 48h forecast
    - Buy/Sell signal
    - Market panic index
    - AI reasoning
    """
    analysis_service = AnalysisService()
    await analysis_service.set_db_session(db)
    
    result = await analysis_service.analyze(currency_pair)
    
    return result


@router.get("/signal")
async def get_signal(
    currency_pair: str = Query("USD/LYD"),
    db: AsyncSession = Depends(get_db),
):
    """Get buy/sell signal for a currency pair."""
    analysis_service = AnalysisService()
    await analysis_service.set_db_session(db)
    
    # Calculate RSI and panic index
    rsi = await analysis_service.calculate_rsi(currency_pair)
    panic_index = await analysis_service.calculate_market_panic_index()
    
    # Generate signal
    signal = analysis_service.generate_signal(rsi or 50.0, panic_index)
    
    return signal


@router.get("/panic-index")
async def get_panic_index(
    db: AsyncSession = Depends(get_db),
):
    """Get current market panic index."""
    analysis_service = AnalysisService()
    await analysis_service.set_db_session(db)
    
    panic_index = await analysis_service.calculate_market_panic_index()
    
    return {
        "market_panic_index": panic_index,
        "timestamp": datetime.now().isoformat(),
    }
