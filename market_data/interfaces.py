from __future__ import annotations

from collections.abc import Iterable, Iterator
from datetime import datetime
from typing import Protocol, TypeAlias, runtime_checkable

from packages.domain import (
    FundingRate,
    OHLCVCandle,
    OpenInterest,
    OrderBookDelta,
    OrderBookSnapshot,
    Symbol,
    Ticker,
    Trade,
    Venue,
)

from .resilience import AdapterHealth


MarketDataEvent: TypeAlias = Trade | Ticker | OHLCVCandle | OrderBookSnapshot | OrderBookDelta | FundingRate | OpenInterest


@runtime_checkable
class MarketDataAdapter(Protocol):
    def connect(self) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        raise NotImplementedError

    def subscribe(self, symbol: Symbol, venue: Venue) -> None:
        raise NotImplementedError

    def unsubscribe(self, symbol: Symbol, venue: Venue) -> None:
        raise NotImplementedError

    def get_historical_candles(
        self,
        symbol: Symbol,
        venue: Venue,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> tuple[OHLCVCandle, ...]:
        raise NotImplementedError

    def get_order_book_snapshot(self, symbol: Symbol, venue: Venue) -> OrderBookSnapshot:
        raise NotImplementedError

    def stream_events(self) -> Iterator[MarketDataEvent]:
        raise NotImplementedError

    def health(self) -> AdapterHealth:
        raise NotImplementedError


@runtime_checkable
class MarketDataWriter(Protocol):
    def write_event(self, event: MarketDataEvent) -> None:
        raise NotImplementedError

    def write_many(self, events: Iterable[MarketDataEvent]) -> None:
        raise NotImplementedError
