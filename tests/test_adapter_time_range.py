"""Tests for time-range filtering in InMemoryMarketDataAdapter."""

import unittest
from datetime import datetime, timezone
from decimal import Decimal

from packages.common import MarketDataRequest, OHLCVBar, TradeTick
from packages.sdk import InMemoryMarketDataAdapter, InMemoryMarketDataSnapshot

T0 = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
T1 = datetime(2026, 1, 1, 1, 0, 0, tzinfo=timezone.utc)
T2 = datetime(2026, 1, 1, 2, 0, 0, tzinfo=timezone.utc)
T3 = datetime(2026, 1, 1, 3, 0, 0, tzinfo=timezone.utc)
FUTURE = datetime(2030, 1, 1, tzinfo=timezone.utc)


def _bar(ts: datetime) -> OHLCVBar:
    return OHLCVBar(
        symbol="BTC/USDT", venue="paper", timestamp=ts,
        open=Decimal("100"), high=Decimal("110"), low=Decimal("90"),
        close=Decimal("105"), volume=Decimal("1"),
    )


def _tick(ts: datetime) -> TradeTick:
    return TradeTick(
        symbol="BTC/USDT", venue="paper", timestamp=ts,
        price=Decimal("100"), quantity=Decimal("1"),
    )


def _req(**kw) -> MarketDataRequest:
    defaults = dict(symbol="BTC/USDT", venue="paper", asset_class="crypto", instrument_type="spot")
    defaults.update(kw)
    return MarketDataRequest(**defaults)


class OHLCVTimeRangeTests(unittest.TestCase):
    def setUp(self):
        self.adapter = InMemoryMarketDataAdapter(
            snapshot=InMemoryMarketDataSnapshot(ohlcv=(_bar(T0), _bar(T1), _bar(T2), _bar(T3)))
        )

    def test_no_constraint_returns_all(self):
        self.assertEqual(len(self.adapter.fetch_ohlcv(_req())), 4)

    def test_start_time_inclusive_boundary(self):
        result = self.adapter.fetch_ohlcv(_req(start_time=T1))
        self.assertEqual(len(result), 3)
        self.assertTrue(all(b.timestamp >= T1 for b in result))

    def test_end_time_inclusive_boundary(self):
        result = self.adapter.fetch_ohlcv(_req(end_time=T2))
        self.assertEqual(len(result), 3)
        self.assertTrue(all(b.timestamp <= T2 for b in result))

    def test_closed_window_returns_interior_only(self):
        result = self.adapter.fetch_ohlcv(_req(start_time=T1, end_time=T2))
        self.assertEqual(len(result), 2)
        self.assertTrue(all(T1 <= b.timestamp <= T2 for b in result))

    def test_future_start_returns_empty(self):
        self.assertEqual(len(self.adapter.fetch_ohlcv(_req(start_time=FUTURE))), 0)

    def test_limit_applied_after_time_filter(self):
        result = self.adapter.fetch_ohlcv(_req(start_time=T2, limit=1))
        self.assertEqual(len(result), 1)
        self.assertGreaterEqual(result[0].timestamp, T2)

    def test_point_in_time_at_boundary(self):
        result = self.adapter.fetch_ohlcv(_req(start_time=T1, end_time=T1))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].timestamp, T1)


class TradeTickTimeRangeTests(unittest.TestCase):
    def setUp(self):
        self.adapter = InMemoryMarketDataAdapter(
            snapshot=InMemoryMarketDataSnapshot(
                trades=(_tick(T0), _tick(T1), _tick(T2), _tick(T3))
            )
        )

    def test_time_range_filters_trades(self):
        result = self.adapter.fetch_trades(_req(start_time=T1, end_time=T2))
        self.assertEqual(len(result), 2)

    def test_no_matching_trades_returns_empty(self):
        self.assertEqual(len(self.adapter.fetch_trades(_req(start_time=FUTURE))), 0)


class MultiSymbolTimeRangeTests(unittest.TestCase):
    """Verify that symbol/venue filter and time filter compose correctly."""

    def setUp(self):
        self.adapter = InMemoryMarketDataAdapter(
            snapshot=InMemoryMarketDataSnapshot(
                ohlcv=(
                    _bar(T0),
                    _bar(T1),
                    OHLCVBar(
                        symbol="ETH/USDT", venue="paper", timestamp=T1,
                        open=Decimal("200"), high=Decimal("210"),
                        low=Decimal("190"), close=Decimal("205"),
                        volume=Decimal("2"),
                    ),
                    _bar(T2),
                ),
            )
        )

    def test_symbol_and_time_filter_compose(self):
        result = self.adapter.fetch_ohlcv(_req(symbol="BTC/USDT", start_time=T1))
        self.assertEqual(len(result), 2)
        self.assertTrue(all(b.symbol == "BTC/USDT" for b in result))
        self.assertTrue(all(b.timestamp >= T1 for b in result))

    def test_different_symbol_unaffected(self):
        result = self.adapter.fetch_ohlcv(_req(symbol="ETH/USDT"))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].symbol, "ETH/USDT")


if __name__ == "__main__":
    unittest.main()
