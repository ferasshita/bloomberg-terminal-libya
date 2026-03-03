"""Unit tests for AnalysisService – signal generation."""
import pytest

from app.services.analysis import AnalysisService


@pytest.fixture
def service() -> AnalysisService:
    return AnalysisService()


# ---------------------------------------------------------------------------
# generate_signal
# ---------------------------------------------------------------------------

class TestGenerateSignal:
    def test_oversold_rsi_gives_buy(self, service):
        result = service.generate_signal(rsi=25.0, panic_index=10.0)
        assert result["signal"] == "BUY"
        assert result["confidence"] >= 70.0

    def test_overbought_rsi_gives_sell(self, service):
        result = service.generate_signal(rsi=75.0, panic_index=10.0)
        assert result["signal"] == "SELL"
        assert result["confidence"] >= 70.0

    def test_neutral_rsi_gives_hold(self, service):
        result = service.generate_signal(rsi=50.0, panic_index=10.0)
        assert result["signal"] == "HOLD"

    def test_approaching_oversold_gives_buy(self, service):
        result = service.generate_signal(rsi=35.0, panic_index=10.0)
        assert result["signal"] == "BUY"

    def test_approaching_overbought_gives_sell(self, service):
        result = service.generate_signal(rsi=65.0, panic_index=10.0)
        assert result["signal"] == "SELL"

    def test_high_panic_reduces_buy_confidence(self, service):
        low_panic = service.generate_signal(rsi=25.0, panic_index=10.0)
        high_panic = service.generate_signal(rsi=25.0, panic_index=70.0)
        assert high_panic["confidence"] < low_panic["confidence"]

    def test_high_panic_hold_becomes_sell(self, service):
        result = service.generate_signal(rsi=50.0, panic_index=70.0)
        assert result["signal"] == "SELL"

    def test_calm_market_mentioned_in_reasoning(self, service):
        result = service.generate_signal(rsi=50.0, panic_index=10.0)
        assert "calm" in result["reasoning"].lower()

    def test_panic_mentioned_in_reasoning(self, service):
        result = service.generate_signal(rsi=50.0, panic_index=80.0)
        assert "panic" in result["reasoning"].lower()

    def test_forecast_up_increases_buy_confidence(self, service):
        base = service.generate_signal(rsi=25.0, panic_index=10.0, forecast_trend="neutral")
        boosted = service.generate_signal(rsi=25.0, panic_index=10.0, forecast_trend="up")
        assert boosted["confidence"] > base["confidence"]

    def test_forecast_down_increases_sell_confidence(self, service):
        base = service.generate_signal(rsi=75.0, panic_index=10.0, forecast_trend="neutral")
        boosted = service.generate_signal(rsi=75.0, panic_index=10.0, forecast_trend="down")
        assert boosted["confidence"] > base["confidence"]

    def test_confidence_capped_at_95(self, service):
        result = service.generate_signal(rsi=25.0, panic_index=5.0, forecast_trend="up")
        assert result["confidence"] <= 95.0

    def test_rsi_reflected_in_result(self, service):
        result = service.generate_signal(rsi=42.5, panic_index=15.0)
        assert result["rsi"] == pytest.approx(42.5)

    def test_panic_index_reflected_in_result(self, service):
        result = service.generate_signal(rsi=50.0, panic_index=33.3)
        assert result["market_panic_index"] == pytest.approx(33.3)
