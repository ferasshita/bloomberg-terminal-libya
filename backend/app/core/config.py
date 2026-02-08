"""Core configuration for the application."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Libyan Financial Terminal"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/libyan_terminal"
    
    # Telegram
    TELEGRAM_API_ID: str
    TELEGRAM_API_HASH: str
    TELEGRAM_PHONE: Optional[str] = None
    TELEGRAM_SESSION_NAME: str = "libyan_terminal_session"
    TELEGRAM_CHANNELS: list[str] = ["@EwanLibya", "@AlMushir"]
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o"
    
    # Fulus.ly API
    FULUS_API_URL: str = "https://api.fulus.ly/v1"
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Rate limiting
    SCRAPER_BUFFER_SECONDS: int = 5
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
