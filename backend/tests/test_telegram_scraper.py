"""Unit tests for TelegramPriceScraper – price parsing logic."""
import pytest

from app.services.telegram_scraper import TelegramPriceScraper


@pytest.fixture
def scraper() -> TelegramPriceScraper:
    """Create a scraper instance without connecting to Telegram."""
    return TelegramPriceScraper(api_id="0", api_hash="0")


# ---------------------------------------------------------------------------
# parse_price – Arabic messages
# ---------------------------------------------------------------------------

class TestParsePriceArabic:
    def test_arabic_dollar_rate(self, scraper):
        text = "سعر الدولار الآن: 6.85"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["currency_pair"] == "USD/LYD"
        assert result["price"] == pytest.approx(6.85)
        assert result["price_type"] == "mid"

    def test_arabic_buy_indicator(self, scraper):
        text = "سعر الدولار شراء 6.80 بيع 6.90"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["price_type"] == "buy"

    def test_arabic_sell_indicator(self, scraper):
        text = "سعر اليورو بيع 7.50"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["currency_pair"] == "EUR/LYD"
        assert result["price_type"] == "sell"

    def test_arabic_dinar_price(self, scraper):
        text = "الدولار بـ 6.75 دينار"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["currency_pair"] == "USD/LYD"
        assert result["price"] == pytest.approx(6.75)


# ---------------------------------------------------------------------------
# parse_price – English messages
# ---------------------------------------------------------------------------

class TestParsePriceEnglish:
    def test_usd_lyd_pair(self, scraper):
        text = "USD/LYD: 6.85"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["currency_pair"] == "USD/LYD"
        assert result["price"] == pytest.approx(6.85)

    def test_eur_lyd_pair(self, scraper):
        text = "EUR/LYD: 7.40"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["currency_pair"] == "EUR/LYD"
        assert result["price"] == pytest.approx(7.40)

    def test_usd_rate_label(self, scraper):
        text = "USD rate: 6.90"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["currency_pair"] == "USD/LYD"

    def test_buy_keyword(self, scraper):
        text = "USD/LYD buy 6.80"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["price_type"] == "buy"

    def test_sell_keyword(self, scraper):
        text = "USD/LYD sell 6.95"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["price_type"] == "sell"


# ---------------------------------------------------------------------------
# parse_price – edge / sanity checks
# ---------------------------------------------------------------------------

class TestParsePriceEdgeCases:
    def test_no_price_returns_none(self, scraper):
        text = "أهلاً وسهلاً بكم في قناتنا"
        result = scraper.parse_price(text)
        assert result is None

    def test_price_too_high_returns_none(self, scraper):
        """Prices above 100 should be rejected by the sanity check."""
        text = "USD/LYD: 150.00"
        result = scraper.parse_price(text)
        assert result is None

    def test_price_zero_returns_none(self, scraper):
        text = "USD/LYD: 0"
        result = scraper.parse_price(text)
        assert result is None

    def test_unrecognised_currency_returns_none(self, scraper):
        text = "GBP rate: 8.00"
        result = scraper.parse_price(text)
        assert result is None

    def test_decimal_price(self, scraper):
        text = "سعر الدولار الآن: 6.875"
        result = scraper.parse_price(text)
        assert result is not None
        assert result["price"] == pytest.approx(6.875)
