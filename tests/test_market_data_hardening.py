"""Tests for market data type input validation (MarketDataValidationError boundary)."""

import unittest
from datetime import datetime, timezone
from decimal import Decimal

from packages.common.market_data import (
    ALLOWED_HEALTH_STATUSES,
    ALLOWED_TRADE_SIDES,
    EconomicCalendarEvent,
    FundingRate,
    MarketCalendarEvent,
    MarketDataHealth,
    MarketDataRequest,
    MarketDataValidationError,
    NewsEvent,
    OHLCVBar,
    OrderBookLevel,
    OrderBookSnapshot,
    TradeTick,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
LATER = datetime(2026, 1, 2, tzinfo=timezone.utc)


class MarketDataRequestValidationTests(unittest.TestCase):
    def _req(self, **kw) -> MarketDataRequest:
        defaults = dict(symbol="BTC/USDT", venue="paper", asset_class="crypto", instrument_type="spot")
        defaults.update(kw)
        return MarketDataRequest(**defaults)

    def test_valid_request_accepted(self):
        req = self._req()
        self.assertEqual(req.symbol, "BTC/USDT")

    def test_empty_symbol_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._req(symbol="")

    def test_blank_symbol_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._req(symbol="   ")

    def test_empty_venue_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._req(venue="")

    def test_empty_asset_class_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._req(asset_class="")

    def test_empty_instrument_type_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._req(instrument_type="")

    def test_zero_limit_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._req(limit=0)

    def test_negative_limit_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._req(limit=-5)

    def test_positive_limit_accepted(self):
        self.assertEqual(self._req(limit=100).limit, 100)

    def test_none_limit_accepted(self):
        self.assertIsNone(self._req(limit=None).limit)

    def test_start_before_end_accepted(self):
        req = self._req(start_time=NOW, end_time=LATER)
        self.assertEqual(req.start_time, NOW)

    def test_inverted_time_range_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._req(start_time=LATER, end_time=NOW)

    def test_only_start_time_accepted(self):
        self.assertEqual(self._req(start_time=NOW).start_time, NOW)

    def test_only_end_time_accepted(self):
        self.assertEqual(self._req(end_time=NOW).end_time, NOW)


class OHLCVBarValidationTests(unittest.TestCase):
    def _bar(self, **kw) -> OHLCVBar:
        defaults = dict(
            symbol="BTC/USDT", venue="paper", timestamp=NOW,
            open=Decimal("100"), high=Decimal("110"), low=Decimal("90"),
            close=Decimal("105"), volume=Decimal("10"),
        )
        defaults.update(kw)
        return OHLCVBar(**defaults)

    def test_valid_bar_accepted(self):
        self.assertEqual(self._bar().symbol, "BTC/USDT")

    def test_empty_symbol_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._bar(symbol="")

    def test_high_below_low_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._bar(high=Decimal("80"), low=Decimal("90"))

    def test_high_equals_low_accepted(self):
        bar = self._bar(high=Decimal("100"), low=Decimal("100"), open=Decimal("100"), close=Decimal("100"))
        self.assertEqual(bar.high, bar.low)

    def test_negative_volume_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._bar(volume=Decimal("-1"))

    def test_zero_volume_accepted(self):
        self.assertEqual(self._bar(volume=Decimal("0")).volume, Decimal("0"))

    def test_negative_open_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._bar(open=Decimal("-1"))

    def test_zero_close_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._bar(close=Decimal("0"))

    def test_validation_error_is_value_error(self):
        self.assertTrue(issubclass(MarketDataValidationError, ValueError))


class TradeTickValidationTests(unittest.TestCase):
    def _tick(self, **kw) -> TradeTick:
        defaults = dict(symbol="BTC/USDT", venue="paper", timestamp=NOW,
                        price=Decimal("100"), quantity=Decimal("1"))
        defaults.update(kw)
        return TradeTick(**defaults)

    def test_valid_tick_accepted(self):
        self.assertEqual(self._tick().price, Decimal("100"))

    def test_zero_price_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._tick(price=Decimal("0"))

    def test_negative_price_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._tick(price=Decimal("-1"))

    def test_zero_quantity_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._tick(quantity=Decimal("0"))

    def test_invalid_side_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._tick(side="long")

    def test_all_valid_sides_accepted(self):
        for side in (None, "buy", "sell"):
            with self.subTest(side=side):
                self.assertEqual(self._tick(side=side).side, side)

    def test_allowed_trade_sides_constant(self):
        self.assertIn(None, ALLOWED_TRADE_SIDES)
        self.assertIn("buy", ALLOWED_TRADE_SIDES)
        self.assertIn("sell", ALLOWED_TRADE_SIDES)


class OrderBookLevelValidationTests(unittest.TestCase):
    def test_positive_values_accepted(self):
        level = OrderBookLevel(price=Decimal("100"), quantity=Decimal("1"))
        self.assertEqual(level.price, Decimal("100"))

    def test_zero_price_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            OrderBookLevel(price=Decimal("0"), quantity=Decimal("1"))

    def test_negative_price_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            OrderBookLevel(price=Decimal("-5"), quantity=Decimal("1"))

    def test_zero_quantity_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            OrderBookLevel(price=Decimal("100"), quantity=Decimal("0"))

    def test_negative_quantity_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            OrderBookLevel(price=Decimal("100"), quantity=Decimal("-1"))


class OrderBookSnapshotValidationTests(unittest.TestCase):
    def test_empty_book_accepted(self):
        ob = OrderBookSnapshot(symbol="BTC/USDT", venue="paper", timestamp=NOW, bids=[], asks=[])
        self.assertEqual(ob.symbol, "BTC/USDT")

    def test_empty_symbol_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            OrderBookSnapshot(symbol="", venue="paper", timestamp=NOW, bids=[], asks=[])

    def test_empty_venue_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            OrderBookSnapshot(symbol="BTC/USDT", venue="", timestamp=NOW, bids=[], asks=[])


class MarketDataHealthValidationTests(unittest.TestCase):
    def _health(self, **kw) -> MarketDataHealth:
        defaults = dict(adapter_name="test-adapter", status="OK", checked_at=NOW, stale=False)
        defaults.update(kw)
        return MarketDataHealth(**defaults)

    def test_all_allowed_statuses_accepted(self):
        for status in ALLOWED_HEALTH_STATUSES:
            with self.subTest(status=status):
                self.assertEqual(self._health(status=status).status, status)

    def test_unknown_status_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._health(status="UNKNOWN")

    def test_empty_status_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._health(status="")

    def test_empty_adapter_name_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            self._health(adapter_name="")

    def test_allowed_health_statuses_is_frozenset(self):
        self.assertIsInstance(ALLOWED_HEALTH_STATUSES, frozenset)
        self.assertGreater(len(ALLOWED_HEALTH_STATUSES), 0)


class MarketCalendarEventValidationTests(unittest.TestCase):
    def test_valid_event_accepted(self):
        event = MarketCalendarEvent(
            calendar_id="cal-001", venue="NYSE", event_type="HOLIDAY",
            starts_at=NOW, ends_at=LATER,
        )
        self.assertEqual(event.calendar_id, "cal-001")

    def test_empty_calendar_id_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            MarketCalendarEvent(calendar_id="", venue="NYSE", event_type="HOLIDAY",
                                starts_at=NOW, ends_at=LATER)

    def test_inverted_time_range_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            MarketCalendarEvent(calendar_id="cal-001", venue="NYSE", event_type="HOLIDAY",
                                starts_at=LATER, ends_at=NOW)

    def test_equal_times_accepted(self):
        event = MarketCalendarEvent(calendar_id="cal-001", venue="NYSE", event_type="HOLIDAY",
                                    starts_at=NOW, ends_at=NOW)
        self.assertEqual(event.starts_at, event.ends_at)


class EconomicCalendarEventValidationTests(unittest.TestCase):
    def test_valid_event_accepted(self):
        event = EconomicCalendarEvent(event_id="eco-001", country="US",
                                      indicator="CPI", scheduled_at=NOW)
        self.assertEqual(event.event_id, "eco-001")

    def test_empty_country_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            EconomicCalendarEvent(event_id="eco-001", country="", indicator="CPI", scheduled_at=NOW)

    def test_empty_indicator_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            EconomicCalendarEvent(event_id="eco-001", country="US", indicator="", scheduled_at=NOW)


class NewsEventValidationTests(unittest.TestCase):
    def test_valid_event_accepted(self):
        event = NewsEvent(news_id="n-001", source="Reuters",
                          headline="Market Update", published_at=NOW)
        self.assertEqual(event.news_id, "n-001")

    def test_empty_headline_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            NewsEvent(news_id="n-001", source="Reuters", headline="", published_at=NOW)

    def test_empty_source_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            NewsEvent(news_id="n-001", source="", headline="Market Update", published_at=NOW)


class FundingRateValidationTests(unittest.TestCase):
    def test_positive_funding_rate_accepted(self):
        fr = FundingRate(symbol="BTC/USDT", venue="paper", timestamp=NOW, funding_rate=Decimal("0.0001"))
        self.assertEqual(fr.funding_rate, Decimal("0.0001"))

    def test_negative_funding_rate_accepted(self):
        fr = FundingRate(symbol="BTC/USDT", venue="paper", timestamp=NOW, funding_rate=Decimal("-0.0001"))
        self.assertEqual(fr.funding_rate, Decimal("-0.0001"))

    def test_empty_symbol_rejected(self):
        with self.assertRaises(MarketDataValidationError):
            FundingRate(symbol="", venue="paper", timestamp=NOW, funding_rate=Decimal("0.0001"))


if __name__ == "__main__":
    unittest.main()
