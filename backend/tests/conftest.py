"""Shared pytest fixtures for the test suite."""
import os
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def fulus_api_key() -> str | None:
    """Return the Fulus API key from the environment (for integration tests)."""
    return os.environ.get("FULUS_LY_API_KEY")


@pytest.fixture
def fulus_api_url() -> str:
    """Return the Fulus API base URL."""
    return os.environ.get("FULUS_API_URL", "https://api.fulus.ly/v1")


@pytest.fixture
def mock_db_session():
    """Return a mock async database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session
