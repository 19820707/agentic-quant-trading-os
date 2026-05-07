import sys
import unittest
from decimal import Decimal

from packages.common import MarketDataRequest, OHLCVBar, OrderBookSnapshot, TradeTick
from packages.sdk.market_data_adapters.ccxt_readonly import (
    CcxtReadOnlyMarketDataAdapter,
    UnsafeCcxtClientError,
)


class FakeCcxtPublicClient:
    def __init__(self):
        self.calls: list[tuple[str, str, int | None]] = []

    def fetch_ohlcv(self, symbol: str, limit: int | None = None):
        self.calls.append(("fetch_ohlcv", symbol, limit))
        return [
            [1710000000000, "100.1", "110.2", "99.9", "105.5", "42.0"],
        ]

    def fetch_trades(self, symbol: str, limit: int | None = None):
        self.calls.append(("fetch_trades", symbol, limit))
        return [
            {
                "timestamp": 1710000001000,
                "price": "105.6",
                "amount": "0.25",
                "side": "buy",
            }
        ]

    def fetch_order_book(self, symbol: str, limit: int | None = None):
        self.calls.append(("fetch_order_book", symbol, limit))
        return {
            "timestamp": 1710000002000,
            "bids": [["105.0", "1.5"]],
            "asks": [["106.0", "2.5"]],
        }


UnsafeFakeClient = type(
    "UnsafeFakeClient",
    (FakeCcxtPublicClient,),
    {"create_order": lambda self: (_ for _ in ()).throw(AssertionError("must never be called"))},
)


class CcxtReadOnlyAdapterTests(unittest.TestCase):
    def setUp(self):
        self.request = MarketDataRequest(
            symbol="BTC/USDT",
            venue="ccxt:fake",
            asset_class="crypto",
            instrument_type="spot",
            limit=1,
        )

    def test_no_ccxt_import_is_required(self):
        self.assertNotIn("ccxt", sys.modules)

    def test_no_credentials_are_required(self):
        adapter = CcxtReadOnlyMarketDataAdapter(FakeCcxtPublicClient())

        self.assertEqual(adapter.adapter_name(), "ccxt-readonly")

    def test_fetch_ohlcv_converts_fake_rows_to_bars(self):
        adapter = CcxtReadOnlyMarketDataAdapter(FakeCcxtPublicClient())

        bars = adapter.fetch_ohlcv(self.request)

        self.assertEqual(len(bars), 1)
        self.assertIsInstance(bars[0], OHLCVBar)
        self.assertEqual(bars[0].symbol, "BTC/USDT")
        self.assertEqual(bars[0].venue, "ccxt:fake")
        self.assertEqual(bars[0].open, Decimal("100.1"))
        self.assertEqual(bars[0].high, Decimal("110.2"))
        self.assertEqual(bars[0].low, Decimal("99.9"))
        self.assertEqual(bars[0].close, Decimal("105.5"))
        self.assertEqual(bars[0].volume, Decimal("42.0"))

    def test_fetch_trades_converts_fake_dicts_to_ticks(self):
        adapter = CcxtReadOnlyMarketDataAdapter(FakeCcxtPublicClient())

        trades = adapter.fetch_trades(self.request)

        self.assertEqual(len(trades), 1)
        self.assertIsInstance(trades[0], TradeTick)
        self.assertEqual(trades[0].price, Decimal("105.6"))
        self.assertEqual(trades[0].quantity, Decimal("0.25"))
        self.assertEqual(trades[0].side, "buy")

    def test_fetch_order_book_converts_fake_dict_to_snapshot(self):
        adapter = CcxtReadOnlyMarketDataAdapter(FakeCcxtPublicClient())

        snapshot = adapter.fetch_order_book(self.request)

        self.assertIsInstance(snapshot, OrderBookSnapshot)
        self.assertEqual(snapshot.bids[0].price, Decimal("105.0"))
        self.assertEqual(snapshot.bids[0].quantity, Decimal("1.5"))
        self.assertEqual(snapshot.asks[0].price, Decimal("106.0"))
        self.assertEqual(snapshot.asks[0].quantity, Decimal("2.5"))

    def test_unsupported_methods_return_empty_lists(self):
        adapter = CcxtReadOnlyMarketDataAdapter(FakeCcxtPublicClient())

        self.assertEqual(adapter.fetch_funding_rates(self.request), [])
        self.assertEqual(adapter.fetch_market_calendar(self.request), [])
        self.assertEqual(adapter.fetch_economic_calendar(self.request), [])
        self.assertEqual(adapter.fetch_news(self.request), [])

    def test_rejects_clients_with_prohibited_execution_like_methods(self):
        with self.assertRaises(UnsafeCcxtClientError):
            CcxtReadOnlyMarketDataAdapter(UnsafeFakeClient())

    def test_adapter_exposes_no_dangerous_execution_methods(self):
        adapter = CcxtReadOnlyMarketDataAdapter(FakeCcxtPublicClient())
        prohibited = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "execute",
        }

        self.assertTrue(prohibited.isdisjoint(set(dir(adapter))))

    def test_fake_client_methods_are_local_in_memory_calls(self):
        client = FakeCcxtPublicClient()
        adapter = CcxtReadOnlyMarketDataAdapter(client)

        adapter.fetch_ohlcv(self.request)
        adapter.fetch_trades(self.request)
        adapter.fetch_order_book(self.request)

        self.assertEqual(
            client.calls,
            [
                ("fetch_ohlcv", "BTC/USDT", 1),
                ("fetch_trades", "BTC/USDT", 1),
                ("fetch_order_book", "BTC/USDT", 1),
            ],
        )


if __name__ == "__main__":
    unittest.main()
