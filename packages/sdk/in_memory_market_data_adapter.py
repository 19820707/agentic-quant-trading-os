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
from packages.common.market_data import is_within_request_window


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

    Every fetch honours the request time window, so a point-in-time request
    (``end_time`` set) never returns records dated after it.
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
        return self._filter_symbol_venue(self.snapshot.ohlcv, request)

    def fetch_trades(self, request: MarketDataRequest) -> tuple[TradeTick, ...]:
        return self._filter_symbol_venue(self.snapshot.trades, request)

    def fetch_order_book(self, request: MarketDataRequest) -> OrderBookSnapshot:
        matches = tuple(
            book
            for book in self.snapshot.order_books
            if book.symbol == request.symbol
            and book.venue == request.venue
            and is_within_request_window(book.timestamp, request)
        )
        if not matches:
            return OrderBookSnapshot(
                symbol=request.symbol,
                venue=request.venue,
                timestamp=request.end_time or datetime.now(timezone.utc),
                bids=[],
                asks=[],
            )
        # Latest book as of the request window, regardless of snapshot order.
        return max(matches, key=lambda book: book.timestamp)

    def fetch_funding_rates(self, request: MarketDataRequest) -> tuple[FundingRate, ...]:
        return self._filter_symbol_venue(self.snapshot.funding_rates, request)

    def fetch_market_calendar(self, request: MarketDataRequest) -> tuple[MarketCalendarEvent, ...]:
        return tuple(
            event
            for event in self.snapshot.market_calendar
            if event.venue == request.venue and is_within_request_window(event.starts_at, request)
        )

    def fetch_economic_calendar(self, request: MarketDataRequest) -> tuple[EconomicCalendarEvent, ...]:
        return self._limit(
            (
                event
                for event in self.snapshot.economic_calendar
                if is_within_request_window(event.scheduled_at, request)
            ),
            request,
        )

    def fetch_news(self, request: MarketDataRequest) -> tuple[NewsEvent, ...]:
        return self._limit(
            (item for item in self.snapshot.news if is_within_request_window(item.published_at, request)),
            request,
        )

    def _filter_symbol_venue(self, items: Iterable, request: MarketDataRequest) -> tuple:
        matches = tuple(
            item for item in items
            if item.symbol == request.symbol
            and item.venue == request.venue
            and is_within_request_window(item.timestamp, request)
        )
        return self._limit(matches, request)

    def _limit(self, items: Iterable, request: MarketDataRequest) -> tuple:
        values = tuple(items)
        if request.limit is None:
            return values
        return values[:request.limit]
