"""Local-only market data domain types with construction-time invariant validation.

All dataclasses are frozen and immutable. __post_init__ guards enforce invariants
at the boundary so downstream code can trust the types without defensive re-checking.
No network access, no credentials, no trading execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Final

__all__ = [
    "ALLOWED_HEALTH_STATUSES",
    "ALLOWED_TRADE_SIDES",
    "MarketDataValidationError",
    "MarketDataRequest",
    "OHLCVBar",
    "TradeTick",
    "OrderBookLevel",
    "OrderBookSnapshot",
    "FundingRate",
    "MarketCalendarEvent",
    "EconomicCalendarEvent",
    "NewsEvent",
    "MarketDataHealth",
]

ALLOWED_HEALTH_STATUSES: Final[frozenset[str]] = frozenset({"OK", "DEGRADED", "UNAVAILABLE"})
ALLOWED_TRADE_SIDES: Final[frozenset[str | None]] = frozenset({None, "buy", "sell"})

_ZERO: Final[Decimal] = Decimal("0")


class MarketDataValidationError(ValueError):
    """Raised when a market data object fails invariant validation at construction."""


def _require_str(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise MarketDataValidationError(f"{name} must be a non-empty string")


def _require_positive(name: str, value: Decimal) -> None:
    if value <= _ZERO:
        raise MarketDataValidationError(f"{name} must be positive; got {value}")


def _require_non_negative(name: str, value: Decimal) -> None:
    if value < _ZERO:
        raise MarketDataValidationError(f"{name} must be non-negative; got {value}")


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
        _require_str("symbol", self.symbol)
        _require_str("venue", self.venue)
        _require_str("asset_class", self.asset_class)
        _require_str("instrument_type", self.instrument_type)
        if self.limit is not None and self.limit <= 0:
            raise MarketDataValidationError(
                f"limit must be a positive integer; got {self.limit}"
            )
        if self.start_time is not None and self.end_time is not None:
            if self.start_time > self.end_time:
                raise MarketDataValidationError("start_time must not be after end_time")


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
        _require_str("symbol", self.symbol)
        _require_str("venue", self.venue)
        _require_positive("open", self.open)
        _require_positive("high", self.high)
        _require_positive("low", self.low)
        _require_positive("close", self.close)
        _require_non_negative("volume", self.volume)
        if self.high < self.low:
            raise MarketDataValidationError(
                f"high ({self.high}) must be >= low ({self.low})"
            )


@dataclass(frozen=True)
class TradeTick:
    symbol: str
    venue: str
    timestamp: datetime
    price: Decimal
    quantity: Decimal
    side: str | None = None

    def __post_init__(self) -> None:
        _require_str("symbol", self.symbol)
        _require_str("venue", self.venue)
        _require_positive("price", self.price)
        _require_positive("quantity", self.quantity)
        if self.side not in ALLOWED_TRADE_SIDES:
            raise MarketDataValidationError(
                f"side must be one of {sorted(s for s in ALLOWED_TRADE_SIDES if s is not None) + [None]!r};"
                f" got {self.side!r}"
            )


@dataclass(frozen=True)
class OrderBookLevel:
    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        _require_positive("price", self.price)
        _require_positive("quantity", self.quantity)


@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: str
    venue: str
    timestamp: datetime
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]

    def __post_init__(self) -> None:
        _require_str("symbol", self.symbol)
        _require_str("venue", self.venue)


@dataclass(frozen=True)
class FundingRate:
    symbol: str
    venue: str
    timestamp: datetime
    funding_rate: Decimal

    def __post_init__(self) -> None:
        _require_str("symbol", self.symbol)
        _require_str("venue", self.venue)


@dataclass(frozen=True)
class MarketCalendarEvent:
    calendar_id: str
    venue: str
    event_type: str
    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        _require_str("calendar_id", self.calendar_id)
        _require_str("venue", self.venue)
        _require_str("event_type", self.event_type)
        if self.starts_at > self.ends_at:
            raise MarketDataValidationError("starts_at must not be after ends_at")


@dataclass(frozen=True)
class EconomicCalendarEvent:
    event_id: str
    country: str
    indicator: str
    scheduled_at: datetime
    importance: str | None = None

    def __post_init__(self) -> None:
        _require_str("event_id", self.event_id)
        _require_str("country", self.country)
        _require_str("indicator", self.indicator)


@dataclass(frozen=True)
class NewsEvent:
    news_id: str
    source: str
    headline: str
    published_at: datetime
    url: str | None = None

    def __post_init__(self) -> None:
        _require_str("news_id", self.news_id)
        _require_str("source", self.source)
        _require_str("headline", self.headline)


@dataclass(frozen=True)
class MarketDataHealth:
    adapter_name: str
    status: str
    checked_at: datetime
    stale: bool
    message: str | None = None

    def __post_init__(self) -> None:
        _require_str("adapter_name", self.adapter_name)
        if self.status not in ALLOWED_HEALTH_STATUSES:
            raise MarketDataValidationError(
                f"status must be one of {sorted(ALLOWED_HEALTH_STATUSES)!r}; got {self.status!r}"
            )
