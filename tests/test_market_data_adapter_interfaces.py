import inspect
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from typing import get_type_hints

from packages.common import (
    EconomicCalendarEvent,
    FundingRate,
    MarketCalendarEvent,
    MarketDataHealth,
    MarketDataRequest,
    NewsEvent,
    OHLCVBar,
    OrderBookLevel,
    OrderBookSnapshot,
    TradeTick,
)
from packages.sdk import ReadOnlyMarketDataAdapter


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class FakeReadOnlyMarketDataAdapter:
    def adapter_name(self) -> str:
        return "fake-read-only-market-data"

    def health(self) -> MarketDataHealth:
        return MarketDataHealth(
            adapter_name=self.adapter_name(),
            status="OK",
            checked_at=NOW,
            stale=False,
            message=None,
        )

    def fetch_ohlcv(self, request: MarketDataRequest) -> tuple[OHLCVBar, ...]:
        return (
            OHLCVBar(
                symbol=request.symbol,
                venue=request.venue,
                timestamp=NOW,
                open=Decimal("30000"),
                high=Decimal("30010"),
                low=Decimal("29990"),
                close=Decimal("30005"),
                volume=Decimal("1.5"),
            ),
        )

    def fetch_trades(self, request: MarketDataRequest) -> tuple[TradeTick, ...]:
        return (
            TradeTick(
                symbol=request.symbol,
                venue=request.venue,
                timestamp=NOW,
                price=Decimal("30005"),
                quantity=Decimal("0.1"),
                side=None,
            ),
        )

    def fetch_order_book(self, request: MarketDataRequest) -> OrderBookSnapshot:
        return OrderBookSnapshot(
            symbol=request.symbol,
            venue=request.venue,
            timestamp=NOW,
            bids=[OrderBookLevel(price=Decimal("30000"), quantity=Decimal("1"))],
            asks=[OrderBookLevel(price=Decimal("30010"), quantity=Decimal("1"))],
        )

    def fetch_funding_rates(self, request: MarketDataRequest) -> tuple[FundingRate, ...]:
        return (
            FundingRate(
                symbol=request.symbol,
                venue=request.venue,
                timestamp=NOW,
                funding_rate=Decimal("0.0001"),
            ),
        )

    def fetch_market_calendar(self, request: MarketDataRequest) -> tuple[MarketCalendarEvent, ...]:
        return (
            MarketCalendarEvent(
                calendar_id="calendar_fixture_001",
                venue=request.venue,
                event_type="SESSION",
                starts_at=NOW,
                ends_at=NOW,
            ),
        )

    def fetch_economic_calendar(self, request: MarketDataRequest) -> tuple[EconomicCalendarEvent, ...]:
        return (
            EconomicCalendarEvent(
                event_id="economic_fixture_001",
                country="US",
                indicator="fixture_indicator",
                scheduled_at=NOW,
                importance="LOW",
            ),
        )

    def fetch_news(self, request: MarketDataRequest) -> tuple[NewsEvent, ...]:
        return (
            NewsEvent(
                news_id="news_fixture_001",
                source="fixture",
                headline="Fixture market data news item",
                published_at=NOW,
                url=None,
            ),
        )


class MarketDataAdapterInterfaceTests(unittest.TestCase):
    def setUp(self):
        self.request = MarketDataRequest(
            symbol="BTC/USDT",
            venue="paper",
            asset_class="crypto",
            instrument_type="perpetual",
            limit=10,
        )
        self.adapter = FakeReadOnlyMarketDataAdapter()

    def test_value_objects_expose_basic_fields(self):
        self.assertEqual(self.request.symbol, "BTC/USDT")
        self.assertEqual(self.request.venue, "paper")
        self.assertEqual(self.request.asset_class, "crypto")
        self.assertEqual(self.request.instrument_type, "perpetual")

    def test_fake_adapter_returns_expected_market_data_types(self):
        self.assertIsInstance(self.adapter.health(), MarketDataHealth)
        self.assertIsInstance(self.adapter.fetch_ohlcv(self.request)[0], OHLCVBar)
        self.assertIsInstance(self.adapter.fetch_trades(self.request)[0], TradeTick)
        self.assertIsInstance(self.adapter.fetch_order_book(self.request), OrderBookSnapshot)
        self.assertIsInstance(self.adapter.fetch_funding_rates(self.request)[0], FundingRate)
        self.assertIsInstance(self.adapter.fetch_market_calendar(self.request)[0], MarketCalendarEvent)
        self.assertIsInstance(self.adapter.fetch_economic_calendar(self.request)[0], EconomicCalendarEvent)
        self.assertIsInstance(self.adapter.fetch_news(self.request)[0], NewsEvent)

    def test_protocol_defines_read_only_market_data_methods(self):
        method_names = {
            name
            for name, member in inspect.getmembers(ReadOnlyMarketDataAdapter)
            if callable(member) and not name.startswith("_")
        }

        self.assertEqual(
            method_names,
            {
                "adapter_name",
                "health",
                "fetch_ohlcv",
                "fetch_trades",
                "fetch_order_book",
                "fetch_funding_rates",
                "fetch_market_calendar",
                "fetch_economic_calendar",
                "fetch_news",
            },
        )

    def test_protocol_methods_have_explicit_return_annotations(self):
        for method_name in (
            "adapter_name",
            "health",
            "fetch_ohlcv",
            "fetch_trades",
            "fetch_order_book",
            "fetch_funding_rates",
            "fetch_market_calendar",
            "fetch_economic_calendar",
            "fetch_news",
        ):
            hints = get_type_hints(getattr(ReadOnlyMarketDataAdapter, method_name))
            self.assertIn("return", hints)

    def test_adapter_exposes_no_order_or_execution_methods(self):
        forbidden_names = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "execute",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(ReadOnlyMarketDataAdapter)))
        self.assertTrue(forbidden_names.isdisjoint(dir(self.adapter)))

    def test_fake_adapter_requires_no_network_or_credentials(self):
        self.assertFalse(hasattr(self.adapter, "api_key"))
        self.assertFalse(hasattr(self.adapter, "secret"))
        self.assertFalse(hasattr(self.adapter, "session"))
        self.assertFalse(hasattr(self.adapter, "client"))


if __name__ == "__main__":
    unittest.main()
