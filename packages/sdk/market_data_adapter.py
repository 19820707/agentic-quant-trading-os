from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

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

"""Read-only market data adapter boundary.

This module defines method signatures only. It grants no execution authority,
does not access broker credentials, and does not implement network behavior.
External adapters must be implemented in future PRs behind this interface.
"""


@runtime_checkable
class ReadOnlyMarketDataAdapter(Protocol):
    def adapter_name(self) -> str:
        raise NotImplementedError

    def health(self) -> MarketDataHealth:
        raise NotImplementedError

    def fetch_ohlcv(self, request: MarketDataRequest) -> Sequence[OHLCVBar]:
        raise NotImplementedError

    def fetch_trades(self, request: MarketDataRequest) -> Sequence[TradeTick]:
        raise NotImplementedError

    def fetch_order_book(self, request: MarketDataRequest) -> OrderBookSnapshot:
        raise NotImplementedError

    def fetch_funding_rates(self, request: MarketDataRequest) -> Sequence[FundingRate]:
        raise NotImplementedError

    def fetch_market_calendar(self, request: MarketDataRequest) -> Sequence[MarketCalendarEvent]:
        raise NotImplementedError

    def fetch_economic_calendar(self, request: MarketDataRequest) -> Sequence[EconomicCalendarEvent]:
        raise NotImplementedError

    def fetch_news(self, request: MarketDataRequest) -> Sequence[NewsEvent]:
        raise NotImplementedError
