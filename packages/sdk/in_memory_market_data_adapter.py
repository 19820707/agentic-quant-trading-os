"""Read-only in-memory market data adapter with time-range filtering."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable

from packages.common import (
    EconomicCalendarEvent,
    FundingRate,
    MarketCalendarEvent,
    MarketDataHealth,
    MarketDataRequest,
    NewsEvent,
    OHLCVBar,
    OrderBookSnapshot,
    TradeTick,
)

__all__ = [
    "InMemoryMarketDataAdapter",
    "InMemoryMarketDataSnapshot",
]


@dataclass(frozen=True)
class InMemoryMarketDataSnapshot:
    ohlcv: tuple[OHLCVBar, ...] = ()
    trades: tuple[TradeTick, ...] = ()
    order_books: tuple[OrderBookSnapshot, ...] = ()
    funding_rates: tuple[FundingRate, ...] = ()
    market_calendar: tuple[MarketCalendarEvent, ...] = ()
    economic_calendar: tuple[EconomicCalendarEvent, ...] = ()
    news: tuple[NewsEvent, ...] = ()


@dataclass
class InMemoryMarketDataAdapter:
    """Read-only adapter backed by static in-memory market data.

    Supports optional start_time / end_time filtering on all queries that carry
    a temporal field (timestamp, starts_at, scheduled_at, published_at). Filtering
    is applied before the limit so callers get a stable, time-bounded window.
    """

    name: str = "in-memory-market-data"
    snapshot: InMemoryMarketDataSnapshot = field(default_factory=InMemoryMarketDataSnapshot)

    def adapter_name(self) -> str:
        return self.name

    def health(self) -> MarketDataHealth:
        return MarketDataHealth(
            adapter_name=self.adapter_name(),
            status="OK",
            checked_at=datetime.now(timezone.utc),
            stale=False,
            message="in-memory read-only adapter",
        )

    def fetch_ohlcv(self, request: MarketDataRequest) -> tuple[OHLCVBar, ...]:
        return self._filter_symbol_venue_time(self.snapshot.ohlcv, request, "timestamp")

    def fetch_trades(self, request: MarketDataRequest) -> tuple[TradeTick, ...]:
        return self._filter_symbol_venue_time(self.snapshot.trades, request, "timestamp")

    def fetch_order_book(self, request: MarketDataRequest) -> OrderBookSnapshot:
        matches = self._filter_symbol_venue_time(self.snapshot.order_books, request, "timestamp")
        if not matches:
            return OrderBookSnapshot(
                symbol=request.symbol,
                venue=request.venue,
                timestamp=datetime.now(timezone.utc),
                bids=[],
                asks=[],
            )
        return matches[-1]

    def fetch_funding_rates(self, request: MarketDataRequest) -> tuple[FundingRate, ...]:
        return self._filter_symbol_venue_time(self.snapshot.funding_rates, request, "timestamp")

    def fetch_market_calendar(self, request: MarketDataRequest) -> tuple[MarketCalendarEvent, ...]:
        matches = tuple(
            event for event in self.snapshot.market_calendar
            if event.venue == request.venue
        )
        matches = self._filter_time_range(matches, request, "starts_at")
        return self._limit(matches, request)

    def fetch_economic_calendar(self, request: MarketDataRequest) -> tuple[EconomicCalendarEvent, ...]:
        filtered = self._filter_time_range(self.snapshot.economic_calendar, request, "scheduled_at")
        return self._limit(filtered, request)

    def fetch_news(self, request: MarketDataRequest) -> tuple[NewsEvent, ...]:
        filtered = self._filter_time_range(self.snapshot.news, request, "published_at")
        return self._limit(filtered, request)

    # ── internal helpers ──────────────────────────────────────────────────────

    def _filter_symbol_venue_time(
        self,
        items: Iterable,
        request: MarketDataRequest,
        time_attr: str,
    ) -> tuple:
        matches = tuple(
            item for item in items
            if item.symbol == request.symbol and item.venue == request.venue
        )
        matches = self._filter_time_range(matches, request, time_attr)
        return self._limit(matches, request)

    def _filter_time_range(
        self,
        items: tuple,
        request: MarketDataRequest,
        time_attr: str,
    ) -> tuple:
        """Return only items whose `time_attr` falls within [start_time, end_time]."""
        result = items
        if request.start_time is not None:
            result = tuple(
                item for item in result
                if getattr(item, time_attr) >= request.start_time
            )
        if request.end_time is not None:
            result = tuple(
                item for item in result
                if getattr(item, time_attr) <= request.end_time
            )
        return result

    def _limit(self, items: Iterable, request: MarketDataRequest) -> tuple:
        values = tuple(items)
        if request.limit is None:
            return values
        return values[: request.limit]
