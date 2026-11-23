"""Self-consistency tests for market data records.

A record that contradicts itself (a bar whose high is below its low, a crossed
order book, a timestamp without a time zone) is rejected when it is built, so
it cannot reach features, models or risk checks.
"""

import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from packages.common import (
    FundingRate,
    MarketCalendarEvent,
    MarketDataRequest,
    MarketDataValidationError,
    OHLCVBar,
    OrderBookLevel,
    OrderBookSnapshot,
    TradeTick,
)


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
NAIVE = datetime(2026, 1, 1)


def _decimals(*values: str) -> tuple[Decimal, ...]:
    return tuple(Decimal(value) for value in values)


def _bar(open_="100", high="110", low="90", close="105", volume="1", timestamp=NOW) -> OHLCVBar:
    return OHLCVBar("BTC/USDT", "paper", timestamp, *_decimals(open_, high, low, close, volume))


def _level(price: str, quantity: str = "1") -> OrderBookLevel:
    return OrderBookLevel(Decimal(price), Decimal(quantity))


class MarketDataValidationTests(unittest.TestCase):
    def test_consistent_records_are_accepted(self):
        _bar()
        _bar(open_="100", high="100", low="100", close="100", volume="0")
        TradeTick("BTC/USDT", "paper", NOW, Decimal("100"), Decimal("0.5"))
        OrderBookSnapshot("BTC/USDT", "paper", NOW, bids=[_level("99")], asks=[_level("101")])
        OrderBookSnapshot("BTC/USDT", "paper", NOW, bids=[], asks=[])
        FundingRate("BTC/USDT", "paper", NOW, Decimal("-0.0001"))
        MarketDataRequest("BTC/USDT", "paper", "crypto", "spot", start_time=NOW, end_time=NOW, limit=1)

    def test_inconsistent_bars_are_rejected(self):
        cases = {
            "high below low": {"high": "80"},
            "high below close": {"close": "120"},
            "low above open": {"low": "101"},
            "negative volume": {"volume": "-1"},
            "zero price": {"low": "0"},
            "naive timestamp": {"timestamp": NAIVE},
        }
        for label, overrides in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(MarketDataValidationError):
                    _bar(**overrides)

    def test_invalid_trades_are_rejected(self):
        for price, quantity, timestamp in (("0", "1", NOW), ("100", "0", NOW), ("100", "-1", NOW), ("100", "1", NAIVE)):
            with self.subTest(price=price, quantity=quantity, aware=timestamp.tzinfo is not None):
                with self.assertRaises(MarketDataValidationError):
                    TradeTick("BTC/USDT", "paper", timestamp, Decimal(price), Decimal(quantity))

    def test_invalid_order_book_levels_are_rejected(self):
        for price, quantity in (("0", "1"), ("-1", "1"), ("100", "-1")):
            with self.subTest(price=price, quantity=quantity):
                with self.assertRaises(MarketDataValidationError):
                    _level(price, quantity)

    def test_crossed_or_locked_order_book_is_rejected(self):
        for bid, ask in (("101", "100"), ("100", "100")):
            with self.subTest(bid=bid, ask=ask):
                with self.assertRaises(MarketDataValidationError):
                    OrderBookSnapshot("BTC/USDT", "paper", NOW, bids=[_level(bid)], asks=[_level(ask)])

    def test_order_book_and_funding_rate_require_aware_timestamps(self):
        with self.assertRaises(MarketDataValidationError):
            OrderBookSnapshot("BTC/USDT", "paper", NAIVE, bids=[], asks=[])
        with self.assertRaises(MarketDataValidationError):
            FundingRate("BTC/USDT", "paper", NAIVE, Decimal("0"))

    def test_calendar_event_cannot_end_before_it_starts(self):
        with self.assertRaises(MarketDataValidationError):
            MarketCalendarEvent("cal", "paper", "SESSION", NOW, NOW - timedelta(hours=1))

    def test_invalid_requests_are_rejected(self):
        base = {"symbol": "BTC/USDT", "venue": "paper", "asset_class": "crypto", "instrument_type": "spot"}
        cases = {
            "empty symbol": {"symbol": " "},
            "empty venue": {"venue": ""},
            "zero limit": {"limit": 0},
            "negative limit": {"limit": -5},
            "inverted window": {"start_time": NOW, "end_time": NOW - timedelta(seconds=1)},
        }
        for label, overrides in cases.items():
            with self.subTest(case=label):
                with self.assertRaises(MarketDataValidationError):
                    MarketDataRequest(**{**base, **overrides})

    def test_validation_error_is_a_value_error(self):
        self.assertTrue(issubclass(MarketDataValidationError, ValueError))


if __name__ == "__main__":
    unittest.main()
