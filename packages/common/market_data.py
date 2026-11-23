from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal


class MarketDataValidationError(ValueError):
    """Raised when a market data record contradicts itself or is unusable."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise MarketDataValidationError(message)


def _require_aware(value: datetime, field: str) -> None:
    # A naive timestamp has no defined instant, which makes point-in-time
    # comparisons ambiguous. Records must say which instant they mean.
    _require(isinstance(value, datetime) and value.tzinfo is not None, f"{field} must be timezone-aware")


@dataclass(frozen=True)
class MarketDataRequest:
    symbol: str
    venue: str
    asset_class: str
    instrument_type: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    limit: int | None = None

    def __post_init__(self) -> None:
        _require(bool(self.symbol and self.symbol.strip()), "symbol is required")
        _require(bool(self.venue and self.venue.strip()), "venue is required")
        if self.limit is not None:
            _require(not isinstance(self.limit, bool) and self.limit > 0, "limit must be a positive integer")
        if self.start_time is not None and self.end_time is not None:
            _require(_as_utc(self.start_time) <= _as_utc(self.end_time), "start_time must not be after end_time")


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def is_within_request_window(timestamp: datetime, request: MarketDataRequest) -> bool:
    """Return true when a record timestamp is inside the request time window.

    Both bounds are inclusive and optional. Honouring ``end_time`` is what keeps
    a point-in-time request from seeing records published after it (lookahead).
    Naive datetimes are read as UTC.
    """

    moment = _as_utc(timestamp)
    if request.start_time is not None and moment < _as_utc(request.start_time):
        return False
    if request.end_time is not None and moment > _as_utc(request.end_time):
        return False
    return True


@dataclass(frozen=True)
class OHLCVBar:
    symbol: str
    venue: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        _require_aware(self.timestamp, "timestamp")
        _require(min(self.open, self.high, self.low, self.close) > 0, "prices must be positive")
        _require(self.high >= max(self.open, self.close, self.low), "high must be the highest price of the bar")
        _require(self.low <= min(self.open, self.close), "low must be the lowest price of the bar")
        _require(self.volume >= 0, "volume must not be negative")


@dataclass(frozen=True)
class TradeTick:
    symbol: str
    venue: str
    timestamp: datetime
    price: Decimal
    quantity: Decimal
    side: str | None = None

    def __post_init__(self) -> None:
        _require_aware(self.timestamp, "timestamp")
        _require(self.price > 0, "price must be positive")
        _require(self.quantity > 0, "quantity must be positive")


@dataclass(frozen=True)
class OrderBookLevel:
    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        _require(self.price > 0, "price must be positive")
        _require(self.quantity >= 0, "quantity must not be negative")


@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: str
    venue: str
    timestamp: datetime
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]

    def __post_init__(self) -> None:
        _require_aware(self.timestamp, "timestamp")
        if self.bids and self.asks:
            best_bid = max(level.price for level in self.bids)
            best_ask = min(level.price for level in self.asks)
            _require(best_bid < best_ask, "order book is crossed: best bid is not below best ask")


@dataclass(frozen=True)
class FundingRate:
    symbol: str
    venue: str
    timestamp: datetime
    funding_rate: Decimal

    def __post_init__(self) -> None:
        _require_aware(self.timestamp, "timestamp")


@dataclass(frozen=True)
class MarketCalendarEvent:
    calendar_id: str
    venue: str
    event_type: str
    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        _require_aware(self.starts_at, "starts_at")
        _require_aware(self.ends_at, "ends_at")
        _require(self.starts_at <= self.ends_at, "starts_at must not be after ends_at")


@dataclass(frozen=True)
class EconomicCalendarEvent:
    event_id: str
    country: str
    indicator: str
    scheduled_at: datetime
    importance: str | None = None


@dataclass(frozen=True)
class NewsEvent:
    news_id: str
    source: str
    headline: str
    published_at: datetime
    url: str | None = None


@dataclass(frozen=True)
class MarketDataHealth:
    adapter_name: str
    status: str
    checked_at: datetime
    stale: bool
    message: str | None = None
