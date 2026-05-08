import sys
import unittest
from datetime import timezone
from decimal import Decimal

from packages.common import MarketDataRequest, OHLCVBar, OrderBookLevel, OrderBookSnapshot, TradeTick
from packages.sdk.market_data_adapters.ccxt_readonly import (
    CcxtReadOnlyMarketDataAdapter,
    UnsafeCcxtClientError,
)


class MockedCcxtPublicClient:
    def __init__(self):
        self.calls: list[tuple[str, str, int | None]] = []

    def fetch_ohlcv(self, symbol: str, limit: int | None = None):
        self.calls.append(("fetch_ohlcv", symbol, limit))
        return [
            [1710000000000, "100.1", "110.2", "99.9", "105.5", "42.0"],
            [1710000060000, 105.5, 111.0, 104.0, 109.25, 7.75],
        ]

    def fetch_trades(self, symbol: str, limit: int | None = None):
        self.calls.append(("fetch_trades", symbol, limit))
        return [
            {"timestamp": 1710000001000, "price": "105.6", "amount": "0.25", "side": "buy"},
            {"timestamp": 1710000002000, "price": "105.7", "amount": "0.50"},
        ]

    def fetch_order_book(self, symbol: str, limit: int | None = None):
        self.calls.append(("fetch_order_book", symbol, limit))
        return {
            "timestamp": 1710000003000,
            "bids": [["105.0", "1.5"], ["104.5", "2.0"]],
            "asks": [["106.0", "2.5"], ["106.5", "3.0"]],
        }


class EmptyOrderBookClient(MockedCcxtPublicClient):
    def fetch_order_book(self, symbol: str, limit: int | None = None):
        self.calls.append(("fetch_order_book", symbol, limit))
        return {"timestamp": 1710000003000, "bids": [], "asks": []}


class LocalErrorClient(MockedCcxtPublicClient):
    def fetch_ohlcv(self, symbol: str, limit: int | None = None):
        raise RuntimeError("fake local fetch failure")


def unsafe_client_with(method_name: str):
    return type(
        f"UnsafeClientWith{method_name}",
        (MockedCcxtPublicClient,),
        {method_name: lambda self: None},
    )


class CcxtReadOnlyMockedIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.request = MarketDataRequest(
            symbol="BTC/USDT",
            venue="ccxt:fake",
            asset_class="crypto",
            instrument_type="spot",
            limit=2,
        )

    def test_tests_do_not_import_ccxt(self):
        self.assertNotIn("ccxt", sys.modules)

    def test_ohlcv_rows_convert_to_bars_and_forward_limit(self):
        client = MockedCcxtPublicClient()
        adapter = CcxtReadOnlyMarketDataAdapter(client)

        bars = adapter.fetch_ohlcv(self.request)

        self.assertEqual(client.calls, [("fetch_ohlcv", "BTC/USDT", 2)])
        self.assertEqual(len(bars), 2)
        self.assertTrue(all(isinstance(bar, OHLCVBar) for bar in bars))
        self.assertEqual(bars[0].timestamp.tzinfo, timezone.utc)
        self.assertEqual(bars[0].open, Decimal("100.1"))
        self.assertEqual(bars[0].close, Decimal("105.5"))
        self.assertEqual(bars[1].high, Decimal("111.0"))
        self.assertEqual(bars[1].volume, Decimal("7.75"))

    def test_trade_dicts_convert_to_ticks_and_missing_side_is_none(self):
        adapter = CcxtReadOnlyMarketDataAdapter(MockedCcxtPublicClient())

        trades = adapter.fetch_trades(self.request)

        self.assertEqual(len(trades), 2)
        self.assertTrue(all(isinstance(trade, TradeTick) for trade in trades))
        self.assertEqual(trades[0].timestamp.tzinfo, timezone.utc)
        self.assertEqual(trades[0].price, Decimal("105.6"))
        self.assertEqual(trades[0].quantity, Decimal("0.25"))
        self.assertEqual(trades[0].side, "buy")
        self.assertEqual(trades[1].price, Decimal("105.7"))
        self.assertIsNone(trades[1].side)

    def test_order_book_dict_converts_to_snapshot_levels(self):
        adapter = CcxtReadOnlyMarketDataAdapter(MockedCcxtPublicClient())

        snapshot = adapter.fetch_order_book(self.request)

        self.assertIsInstance(snapshot, OrderBookSnapshot)
        self.assertEqual(snapshot.timestamp.tzinfo, timezone.utc)
        self.assertTrue(all(isinstance(level, OrderBookLevel) for level in snapshot.bids))
        self.assertTrue(all(isinstance(level, OrderBookLevel) for level in snapshot.asks))
        self.assertEqual(snapshot.bids[0].price, Decimal("105.0"))
        self.assertEqual(snapshot.asks[1].quantity, Decimal("3.0"))

    def test_empty_order_book_sides_are_handled_safely(self):
        adapter = CcxtReadOnlyMarketDataAdapter(EmptyOrderBookClient())

        snapshot = adapter.fetch_order_book(self.request)

        self.assertEqual(snapshot.bids, [])
        self.assertEqual(snapshot.asks, [])

    def test_unsupported_methods_return_safe_empty_lists(self):
        adapter = CcxtReadOnlyMarketDataAdapter(MockedCcxtPublicClient())

        self.assertEqual(adapter.fetch_funding_rates(self.request), [])
        self.assertEqual(adapter.fetch_news(self.request), [])
        self.assertEqual(adapter.fetch_market_calendar(self.request), [])
        self.assertEqual(adapter.fetch_economic_calendar(self.request), [])

    def test_dangerous_client_methods_are_rejected(self):
        for method_name in (
            "create_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "set_leverage",
            "private_post_order",
            "private_delete_order",
        ):
            with self.subTest(method_name=method_name):
                with self.assertRaises(UnsafeCcxtClientError):
                    CcxtReadOnlyMarketDataAdapter(unsafe_client_with(method_name)())

    def test_local_fake_errors_propagate_deterministically_without_secrets(self):
        adapter = CcxtReadOnlyMarketDataAdapter(LocalErrorClient())

        with self.assertRaises(RuntimeError) as raised:
            adapter.fetch_ohlcv(self.request)

        message = str(raised.exception)
        self.assertEqual(message, "fake local fetch failure")
        self.assertNotIn("secret", message.lower())
        self.assertNotIn("token", message.lower())

    def test_adapter_exposes_no_prohibited_execution_methods(self):
        adapter = CcxtReadOnlyMarketDataAdapter(MockedCcxtPublicClient())
        prohibited = {
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

        self.assertTrue(prohibited.isdisjoint(set(dir(adapter))))

    def test_no_credentials_or_network_handles_are_required(self):
        adapter = CcxtReadOnlyMarketDataAdapter(MockedCcxtPublicClient())

        self.assertFalse(hasattr(adapter, "api_key"))
        self.assertFalse(hasattr(adapter, "secret"))
        self.assertFalse(hasattr(adapter, "session"))
        self.assertFalse(hasattr(adapter, "socket"))


if __name__ == "__main__":
    unittest.main()
