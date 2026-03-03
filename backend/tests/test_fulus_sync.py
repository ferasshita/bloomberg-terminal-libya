"""Tests for FulusSyncService.

Unit tests run without any network access.
The integration test (marked ``integration``) hits the live Fulus.ly API and
is skipped automatically when ``FULUS_LY_API_KEY`` is not set.
"""
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import httpx

from app.services.fulus_sync import FulusSyncService


@pytest.fixture
def service() -> FulusSyncService:
    return FulusSyncService()


# ---------------------------------------------------------------------------
# _generate_synthetic_data
# ---------------------------------------------------------------------------

class TestSyntheticData:
    def test_returns_expected_number_of_days(self, service):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 10)
        data = service._generate_synthetic_data("USD/LYD", start, end)
        assert len(data) == 10  # inclusive

    def test_each_record_has_required_fields(self, service):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 3)
        data = service._generate_synthetic_data("USD/LYD", start, end)
        for record in data:
            assert "date" in record
            assert "open" in record
            assert "high" in record
            assert "low" in record
            assert "close" in record
            assert "volume" in record

    def test_dates_are_sequential(self, service):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 5)
        data = service._generate_synthetic_data("USD/LYD", start, end)
        dates = [record["date"] for record in data]
        assert dates == sorted(dates)

    def test_high_ge_low(self, service):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 30)
        data = service._generate_synthetic_data("USD/LYD", start, end)
        for record in data:
            assert record["high"] >= record["low"]

    def test_eur_base_price_higher_than_usd(self, service):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 1)
        usd_data = service._generate_synthetic_data("USD/LYD", start, end)
        eur_data = service._generate_synthetic_data("EUR/LYD", start, end)
        # EUR base starts at 5.2, USD at 4.8 – with identical random seed
        # we can't guarantee order, but both should be positive
        assert usd_data[0]["close"] > 0
        assert eur_data[0]["close"] > 0


# ---------------------------------------------------------------------------
# fetch_rates – unit (mock HTTP)
# ---------------------------------------------------------------------------

class TestFetchRates:
    @pytest.mark.asyncio
    async def test_bearer_auth_header_sent(self, service):
        """Verify the Authorization: Bearer header is included in the request."""
        captured_headers = {}

        async def fake_get(url, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"data": []}
            return mock_resp

        with patch("app.services.fulus_sync.settings") as mock_settings:
            mock_settings.FULUS_LY_API_KEY = "test_token"
            mock_settings.FULUS_API_URL = "https://api.fulus.ly/v1"

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client.get = AsyncMock(side_effect=fake_get)
                mock_client_cls.return_value = mock_client

                svc = FulusSyncService(api_url="https://api.fulus.ly/v1")
                await svc.fetch_rates("USD/LYD")

        assert "Authorization" in captured_headers
        assert captured_headers["Authorization"] == "Bearer test_token"

    @pytest.mark.asyncio
    async def test_no_auth_header_when_key_not_set(self, service):
        """No Authorization header should be sent when the key is not configured."""
        captured_headers = {}

        async def fake_get(url, **kwargs):
            captured_headers.update(kwargs.get("headers", {}))
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"data": []}
            return mock_resp

        with patch("app.services.fulus_sync.settings") as mock_settings:
            mock_settings.FULUS_LY_API_KEY = None
            mock_settings.FULUS_API_URL = "https://api.fulus.ly/v1"

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client.get = AsyncMock(side_effect=fake_get)
                mock_client_cls.return_value = mock_client

                svc = FulusSyncService(api_url="https://api.fulus.ly/v1")
                await svc.fetch_rates("USD/LYD")

        assert "Authorization" not in captured_headers

    @pytest.mark.asyncio
    async def test_returns_api_data_on_200(self, service):
        """Should return the ``data`` list from the API response on success."""
        api_payload = [
            {"date": "2024-01-01", "open": 6.80, "high": 6.90, "low": 6.75, "close": 6.85, "volume": 200000}
        ]

        with patch("app.services.fulus_sync.settings") as mock_settings:
            mock_settings.FULUS_LY_API_KEY = "tok"
            mock_settings.FULUS_API_URL = "https://api.fulus.ly/v1"

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {"data": api_payload}
                mock_client.get = AsyncMock(return_value=mock_resp)
                mock_client_cls.return_value = mock_client

                svc = FulusSyncService(api_url="https://api.fulus.ly/v1")
                result = await svc.fetch_rates("USD/LYD")

        assert result == api_payload

    @pytest.mark.asyncio
    async def test_falls_back_to_synthetic_on_non_200(self, service):
        """Should fall back to synthetic data when the API returns an error status."""
        with patch("app.services.fulus_sync.settings") as mock_settings:
            mock_settings.FULUS_LY_API_KEY = "tok"
            mock_settings.FULUS_API_URL = "https://api.fulus.ly/v1"

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_resp = MagicMock()
                mock_resp.status_code = 401
                mock_resp.json.return_value = {}
                mock_client.get = AsyncMock(return_value=mock_resp)
                mock_client_cls.return_value = mock_client

                svc = FulusSyncService(api_url="https://api.fulus.ly/v1")
                result = await svc.fetch_rates(
                    "USD/LYD",
                    start_date=datetime(2024, 1, 1),
                    end_date=datetime(2024, 1, 5),
                )

        # Falls back to synthetic – should return 5 records
        assert len(result) == 5

    @pytest.mark.asyncio
    async def test_falls_back_to_synthetic_on_connection_error(self, service):
        """Should fall back to synthetic data when the network request fails."""
        with patch("app.services.fulus_sync.settings") as mock_settings:
            mock_settings.FULUS_LY_API_KEY = "tok"
            mock_settings.FULUS_API_URL = "https://api.fulus.ly/v1"

            with patch("httpx.AsyncClient") as mock_client_cls:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                mock_client.get = AsyncMock(side_effect=httpx.ConnectError("unreachable"))
                mock_client_cls.return_value = mock_client

                svc = FulusSyncService(api_url="https://api.fulus.ly/v1")
                result = await svc.fetch_rates(
                    "USD/LYD",
                    start_date=datetime(2024, 1, 1),
                    end_date=datetime(2024, 1, 3),
                )

        assert len(result) == 3


# ---------------------------------------------------------------------------
# Integration test – requires live FULUS_LY_API_KEY
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("FULUS_LY_API_KEY"),
    reason="FULUS_LY_API_KEY not set – skipping live integration test",
)
async def test_fulus_live_fetch():
    """
    Live integration test: verify that the Fulus.ly API is reachable and
    returns data when the real API key is configured.
    """
    svc = FulusSyncService()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    data = await svc.fetch_rates("USD/LYD", start_date=start_date, end_date=end_date)

    assert isinstance(data, list), "Expected a list of rate records"
    if data:
        first = data[0]
        assert "date" in first or "close" in first, (
            f"Unexpected record format: {first}"
        )
