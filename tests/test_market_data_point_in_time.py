"""Point-in-time and leakage tests for read-only market data adapters.

A request with ``end_time`` set must never return a record dated after it, and
adapters must not invent timestamps for records that have none.
"""

import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from packages.common import (
    EconomicCalendarEvent,
    FundingRate,
    MarketCalendarEvent,
    MarketDataRequest,
    NewsEvent,
    OHLCVBar,
    OrderBookLevel,
    OrderBookSnapshot,
    TradeTick,
)
from packages.common.market_data import is_within_request_window
from packages.sdk import InMemoryMarketDataAdapter, InMemoryMarketDataSnapshot
from packages.sdk.market_data_adapters.ccxt_readonly import (
    CcxtReadOnlyMarketDataAdapter,
    MissingMarketDataTimestampError,
)


T0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
HOUR = timedelta(hours=1)
SYMBOL = "BTC/USDT"
VENUE = "paper"


def _request(**overrides) -> MarketDataRequest:
    values = {"symbol": SYMBOL, "venue": VENUE, "asset_class": "crypto", "instrument_type": "spot"}
    values.update(overrides)
    return MarketDataRequest(**values)


def _bar(timestamp: datetime) -> OHLCVBar:
    one = Decimal("1")
    return OHLCVBar(SYMBOL, VENUE, timestamp, one, one, one, one, one)


def _book(timestamp: datetime, price: str) -> OrderBookSnapshot:
    level = OrderBookLevel(price=Decimal(price), quantity=Decimal("1"))
    return OrderBookSnapshot(SYMBOL, VENUE, timestamp, bids=[level], asks=[])


class RequestWindowTests(unittest.TestCase):
    def test_bounds_are_inclusive_and_optional(self):
        self.assertTrue(is_within_request_window(T0, _request()))
        self.assertTrue(is_within_request_window(T0, _request(start_time=T0, end_time=T0)))
        self.assertFalse(is_within_request_window(T0 + HOUR, _request(end_time=T0)))
        self.assertFalse(is_within_request_window(T0 - HOUR, _request(start_time=T0)))

    def test_naive_datetimes_are_read_as_utc(self):
        naive = datetime(2026, 1, 1, 1)

        self.assertFalse(is_within_request_window(naive, _request(end_time=T0)))
        self.assertTrue(is_within_request_window(naive, _request(end_time=T0 + HOUR)))


class InMemoryPointInTimeTests(unittest.TestCase):
    def setUp(self):
        times = (T0, T0 + HOUR, T0 + 2 * HOUR)
        self.adapter = InMemoryMarketDataAdapter(
            snapshot=InMemoryMarketDataSnapshot(
                ohlcv=tuple(_bar(moment) for moment in times),
                trades=tuple(TradeTick(SYMBOL, VENUE, moment, Decimal("1"), Decimal("1")) for moment in times),
                # Deliberately out of chronological order.
                order_books=(_book(T0 + 2 * HOUR, "102"), _book(T0, "100"), _book(T0 + HOUR, "101")),
                funding_rates=tuple(FundingRate(SYMBOL, VENUE, moment, Decimal("0.01")) for moment in times),
                market_calendar=tuple(
                    MarketCalendarEvent(f"cal_{index}", VENUE, "SESSION", moment, moment + HOUR)
                    for index, moment in enumerate(times)
                ),
                economic_calendar=tuple(
                    EconomicCalendarEvent(f"eco_{index}", "US", "CPI", moment) for index, moment in enumerate(times)
                ),
                news=tuple(NewsEvent(f"news_{index}", "wire", "headline", moment) for index, moment in enumerate(times)),
            )
        )
        self.as_of = _request(end_time=T0 + HOUR)

    def test_no_series_returns_records_after_end_time(self):
        cutoff = self.as_of.end_time

        self.assertTrue(all(bar.timestamp <= cutoff for bar in self.adapter.fetch_ohlcv(self.as_of)))
        self.assertTrue(all(tick.timestamp <= cutoff for tick in self.adapter.fetch_trades(self.as_of)))
        self.assertTrue(all(rate.timestamp <= cutoff for rate in self.adapter.fetch_funding_rates(self.as_of)))
        self.assertTrue(all(event.starts_at <= cutoff for event in self.adapter.fetch_market_calendar(self.as_of)))
        self.assertTrue(
            all(event.scheduled_at <= cutoff for event in self.adapter.fetch_economic_calendar(self.as_of))
        )
        self.assertTrue(all(item.published_at <= cutoff for item in self.adapter.fetch_news(self.as_of)))

    def test_as_of_request_returns_exactly_the_known_records(self):
        self.assertEqual(len(self.adapter.fetch_ohlcv(self.as_of)), 2)
        self.assertEqual(len(self.adapter.fetch_trades(self.as_of)), 2)
        self.assertEqual(len(self.adapter.fetch_news(self.as_of)), 2)

    def test_start_time_excludes_older_records(self):
        bars = self.adapter.fetch_ohlcv(_request(start_time=T0 + HOUR))

        self.assertEqual([bar.timestamp for bar in bars], [T0 + HOUR, T0 + 2 * HOUR])

    def test_unbounded_request_returns_everything(self):
        self.assertEqual(len(self.adapter.fetch_ohlcv(_request())), 3)

    def test_order_book_is_latest_as_of_end_time_not_last_in_storage(self):
        self.assertEqual(self.adapter.fetch_order_book(self.as_of).timestamp, T0 + HOUR)
        self.assertEqual(self.adapter.fetch_order_book(_request()).timestamp, T0 + 2 * HOUR)

    def test_empty_order_book_before_any_data_is_stamped_with_the_request_time(self):
        before_data = _request(end_time=T0 - HOUR)

        book = self.adapter.fetch_order_book(before_data)

        self.assertEqual((book.bids, book.asks), ([], []))
        self.assertEqual(book.timestamp, T0 - HOUR)

    def test_limit_applies_after_the_time_window(self):
        bars = self.adapter.fetch_ohlcv(_request(start_time=T0 + HOUR, limit=1))

        self.assertEqual([bar.timestamp for bar in bars], [T0 + HOUR])


class _FakePublicClient:
    def __init__(self, order_book_timestamp=1767225600000):
        self._order_book_timestamp = order_book_timestamp

    def fetch_ohlcv(self, symbol, limit=None):
        base = 1767225600000  # 2026-01-01T00:00:00Z in milliseconds
        return [[base + index * 3_600_000, "1", "1", "1", "1", "1"] for index in range(3)]

    def fetch_trades(self, symbol, limit=None):
        return [{"timestamp": None, "price": "1", "amount": "1"}]

    def fetch_order_book(self, symbol, limit=None):
        return {"timestamp": self._order_book_timestamp, "bids": [], "asks": []}


class CcxtReadOnlyPointInTimeTests(unittest.TestCase):
    def test_bars_after_end_time_are_dropped(self):
        adapter = CcxtReadOnlyMarketDataAdapter(_FakePublicClient())

        bars = adapter.fetch_ohlcv(_request(end_time=T0 + HOUR))

        self.assertEqual([bar.timestamp for bar in bars], [T0, T0 + HOUR])

    def test_record_without_timestamp_is_rejected_instead_of_using_the_clock(self):
        adapter = CcxtReadOnlyMarketDataAdapter(_FakePublicClient())

        with self.assertRaises(MissingMarketDataTimestampError):
            adapter.fetch_trades(_request())

    def test_order_book_without_timestamp_is_rejected(self):
        adapter = CcxtReadOnlyMarketDataAdapter(_FakePublicClient(order_book_timestamp=None))

        with self.assertRaises(MissingMarketDataTimestampError):
            adapter.fetch_order_book(_request())


if __name__ == "__main__":
    unittest.main()
