from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class MarketDataRequest:
    symbol: str
    venue: str
    asset_class: str
    instrument_type: str
    start_time: datetime | None = None
    end_time: datetime | None = None
    limit: int | None = None


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


@dataclass(frozen=True)
class TradeTick:
    symbol: str
    venue: str
    timestamp: datetime
    price: Decimal
    quantity: Decimal
    side: str | None = None


@dataclass(frozen=True)
class OrderBookLevel:
    price: Decimal
    quantity: Decimal


@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: str
    venue: str
    timestamp: datetime
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]


@dataclass(frozen=True)
class FundingRate:
    symbol: str
    venue: str
    timestamp: datetime
    funding_rate: Decimal


@dataclass(frozen=True)
class MarketCalendarEvent:
    calendar_id: str
    venue: str
    event_type: str
    starts_at: datetime
    ends_at: datetime


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
