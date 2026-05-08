import unittest
from datetime import datetime, timezone
from decimal import Decimal

from packages.common import MarketDataHealth, MarketDataRequest, OHLCVBar, OrderBookSnapshot, TradeTick
from packages.sdk import (
    DuplicateMarketDataAdapterError,
    MarketDataAdapterRegistry,
    MarketDataAdapterRegistryError,
    ReadOnlyMarketDataAdapter,
    UnknownMarketDataAdapterError,
)
from packages.sdk.market_data_adapter_registry import register_ccxt_readonly_adapter


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class RegistryFixtureAdapter:
    def adapter_name(self) -> str:
        return "registry-fixture"

    def health(self) -> MarketDataHealth:
        return MarketDataHealth(
            adapter_name=self.adapter_name(),
            status="OK",
            checked_at=NOW,
            stale=False,
            message=None,
        )

    def fetch_ohlcv(self, request: MarketDataRequest) -> tuple:
        return ()

    def fetch_trades(self, request: MarketDataRequest) -> tuple:
        return ()

    def fetch_order_book(self, request: MarketDataRequest) -> OrderBookSnapshot:
        return OrderBookSnapshot(symbol=request.symbol, venue=request.venue, timestamp=NOW, bids=[], asks=[])

    def fetch_funding_rates(self, request: MarketDataRequest) -> tuple:
        return ()

    def fetch_market_calendar(self, request: MarketDataRequest) -> tuple:
        return ()

    def fetch_economic_calendar(self, request: MarketDataRequest) -> tuple:
        return ()

    def fetch_news(self, request: MarketDataRequest) -> tuple:
        return ()


class FakeCcxtRegistryClient:
    def fetch_ohlcv(self, symbol: str, limit: int | None = None):
        return [[1710000000000, "100", "110", "90", "105", "12.5"]]

    def fetch_trades(self, symbol: str, limit: int | None = None):
        return [{"timestamp": 1710000001000, "price": "105.25", "amount": "0.5", "side": "buy"}]

    def fetch_order_book(self, symbol: str, limit: int | None = None):
        return {
            "timestamp": 1710000002000,
            "bids": [["105.0", "1.0"]],
            "asks": [["106.0", "2.0"]],
        }


class MarketDataAdapterRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = MarketDataAdapterRegistry()

    def test_registers_and_lists_read_only_adapter_factory(self):
        self.registry.register("fixture", RegistryFixtureAdapter, "Fixture adapter")

        adapters = self.registry.list_adapters()

        self.assertEqual(len(adapters), 1)
        self.assertEqual(adapters[0].name, "fixture")
        self.assertTrue(adapters[0].read_only)

    def test_create_returns_read_only_adapter_instance(self):
        self.registry.register("fixture", RegistryFixtureAdapter)

        adapter = self.registry.create("fixture")

        self.assertIsInstance(adapter, ReadOnlyMarketDataAdapter)
        self.assertEqual(adapter.adapter_name(), "registry-fixture")

    def test_exists_returns_expected_values(self):
        self.registry.register("fixture", RegistryFixtureAdapter)

        self.assertTrue(self.registry.exists("fixture"))
        self.assertFalse(self.registry.exists("missing"))

    def test_unknown_adapter_raises_clear_error(self):
        with self.assertRaises(UnknownMarketDataAdapterError):
            self.registry.create("missing")

        with self.assertRaises(UnknownMarketDataAdapterError):
            self.registry.get_info("missing")

    def test_duplicate_adapter_registration_is_rejected(self):
        self.registry.register("fixture", RegistryFixtureAdapter)

        with self.assertRaises(DuplicateMarketDataAdapterError):
            self.registry.register("fixture", RegistryFixtureAdapter)

    def test_unsafe_adapter_names_are_rejected(self):
        for name in ("", "../fixture", "fixture/name", "fixture\\name"):
            with self.subTest(name=name):
                with self.assertRaises(MarketDataAdapterRegistryError):
                    self.registry.register(name, RegistryFixtureAdapter)

    def test_registry_does_not_require_network_or_credentials(self):
        self.registry.register("fixture", RegistryFixtureAdapter)
        adapter = self.registry.create("fixture")

        self.assertFalse(hasattr(adapter, "api_key"))
        self.assertFalse(hasattr(adapter, "secret"))
        self.assertFalse(hasattr(adapter, "session"))
        self.assertFalse(hasattr(adapter, "client"))

    def test_registry_does_not_expose_order_or_execution_methods(self):
        forbidden = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "execute",
        }

        self.assertTrue(forbidden.isdisjoint(dir(self.registry)))

    def test_registers_ccxt_readonly_adapter_with_fake_client_only(self):
        register_ccxt_readonly_adapter(self.registry, FakeCcxtRegistryClient())

        self.assertTrue(self.registry.exists("ccxt-readonly"))
        info = self.registry.get_info("ccxt-readonly")
        self.assertTrue(info.read_only)

        adapter = self.registry.create("ccxt-readonly")

        self.assertIsInstance(adapter, ReadOnlyMarketDataAdapter)
        self.assertEqual(adapter.adapter_name(), "ccxt-readonly")

    def test_registered_ccxt_readonly_adapter_fetches_fake_market_data(self):
        register_ccxt_readonly_adapter(self.registry, FakeCcxtRegistryClient())
        adapter = self.registry.create("ccxt-readonly")
        request = MarketDataRequest(
            symbol="BTC/USDT",
            venue="ccxt:fake",
            asset_class="crypto",
            instrument_type="spot",
            limit=1,
        )

        bars = adapter.fetch_ohlcv(request)
        trades = adapter.fetch_trades(request)
        order_book = adapter.fetch_order_book(request)

        self.assertIsInstance(bars[0], OHLCVBar)
        self.assertEqual(bars[0].close, Decimal("105"))
        self.assertIsInstance(trades[0], TradeTick)
        self.assertEqual(trades[0].price, Decimal("105.25"))
        self.assertIsInstance(order_book, OrderBookSnapshot)
        self.assertEqual(order_book.bids[0].quantity, Decimal("1.0"))

    def test_registered_ccxt_readonly_adapter_exposes_no_execution_methods(self):
        register_ccxt_readonly_adapter(self.registry, FakeCcxtRegistryClient())
        adapter = self.registry.create("ccxt-readonly")
        forbidden = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "execute",
        }

        self.assertTrue(forbidden.isdisjoint(dir(adapter)))

    def test_ccxt_readonly_registration_still_rejects_duplicates(self):
        register_ccxt_readonly_adapter(self.registry, FakeCcxtRegistryClient())

        with self.assertRaises(DuplicateMarketDataAdapterError):
            register_ccxt_readonly_adapter(self.registry, FakeCcxtRegistryClient())


if __name__ == "__main__":
    unittest.main()
