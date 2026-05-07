import unittest
from datetime import datetime, timezone
from decimal import Decimal

from packages.common import MarketDataRequest, OHLCVBar, OrderBookLevel, OrderBookSnapshot, TradeTick
from packages.sdk import InMemoryMarketDataAdapter, InMemoryMarketDataSnapshot, ReadOnlyMarketDataAdapter


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class InMemoryMarketDataAdapterTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = InMemoryMarketDataSnapshot(
            ohlcv=(
                OHLCVBar(
                    symbol="BTC/USDT",
                    venue="paper",
                    timestamp=NOW,
                    open=Decimal("30000"),
                    high=Decimal("30010"),
                    low=Decimal("29990"),
                    close=Decimal("30005"),
                    volume=Decimal("1"),
                ),
            ),
            trades=(
                TradeTick(
                    symbol="BTC/USDT",
                    venue="paper",
                    timestamp=NOW,
                    price=Decimal("30005"),
                    quantity=Decimal("0.1"),
                    side=None,
                ),
            ),
            order_books=(
                OrderBookSnapshot(
                    symbol="BTC/USDT",
                    venue="paper",
                    timestamp=NOW,
                    bids=(OrderBookLevel(price=Decimal("30000"), quantity=Decimal("1")),),
                    asks=(OrderBookLevel(price=Decimal("30010"), quantity=Decimal("1")),),
                ),
            ),
        )
        self.adapter = InMemoryMarketDataAdapter(snapshot=self.snapshot)
        self.request = MarketDataRequest(
            symbol="BTC/USDT",
            venue="paper",
            asset_class="crypto",
            instrument_type="spot",
            limit=1,
        )

    def test_adapter_satisfies_read_only_protocol(self):
        self.assertIsInstance(self.adapter, ReadOnlyMarketDataAdapter)

    def test_fetches_static_in_memory_market_data(self):
        self.assertEqual(len(self.adapter.fetch_ohlcv(self.request)), 1)
        self.assertEqual(len(self.adapter.fetch_trades(self.request)), 1)
        self.assertEqual(self.adapter.fetch_order_book(self.request).venue, "paper")

    def test_returns_empty_order_book_when_missing(self):
        request = MarketDataRequest(
            symbol="ETH/USDT",
            venue="paper",
            asset_class="crypto",
            instrument_type="spot",
        )

        order_book = self.adapter.fetch_order_book(request)

        self.assertEqual(order_book.bids, [])
        self.assertEqual(order_book.asks, [])

    def test_adapter_requires_no_credentials_or_network_client(self):
        self.assertFalse(hasattr(self.adapter, "api_key"))
        self.assertFalse(hasattr(self.adapter, "secret"))
        self.assertFalse(hasattr(self.adapter, "session"))
        self.assertFalse(hasattr(self.adapter, "client"))

    def test_adapter_exposes_no_order_or_execution_methods(self):
        forbidden = {
            "buy",
            "sell",
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "execute",
        }

        self.assertTrue(forbidden.isdisjoint(dir(self.adapter)))


if __name__ == "__main__":
    unittest.main()
