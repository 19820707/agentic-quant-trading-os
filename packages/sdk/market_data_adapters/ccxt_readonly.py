"""Read-only CCXT-shaped market data adapter skeleton.

This adapter does not import ccxt, install dependencies, call network, or access
credentials. Tests must use injected fake/in-memory clients only. Conversion from
raw CCXT-format data to internal domain types is guarded at the field level.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Final

from packages.common import (
    MarketDataHealth,
    MarketDataRequest,
    OHLCVBar,
    OrderBookLevel,
    OrderBookSnapshot,
    TradeTick,
)

__all__ = [
    "CcxtConversionError",
    "CcxtReadOnlyMarketDataAdapter",
    "PROHIBITED_CLIENT_METHODS",
    "UnsafeCcxtClientError",
]

PROHIBITED_CLIENT_METHODS: Final[frozenset[str]] = frozenset(
    {
        "create_order",
        "cancel_order",
        "edit_order",
        "withdraw",
        "transfer",
        "borrow",
        "repay",
        "set_leverage",
        "private_post_order",
        "private_delete_order",
    }
)


class UnsafeCcxtClientError(ValueError):
    """Raised when an injected client exposes execution-like methods."""


class CcxtConversionError(ValueError):
    """Raised when a CCXT raw data field cannot be converted to a domain type."""


class CcxtReadOnlyMarketDataAdapter:
    """Read-only CCXT-shaped market data adapter skeleton.

    This adapter does not import ccxt, install dependencies, call network, or
    access credentials. Tests must use injected fake/in-memory clients only.
    """

    def __init__(self, client: object, name: str = "ccxt-readonly") -> None:
        exposed = set(dir(client))
        prohibited = sorted(exposed & PROHIBITED_CLIENT_METHODS)
        if prohibited:
            raise UnsafeCcxtClientError(
                "injected client exposes prohibited execution-like methods: "
                + ", ".join(prohibited)
            )
        self._client = client
        self._name = name

    def adapter_name(self) -> str:
        return self._name

    def health(self) -> MarketDataHealth:
        return MarketDataHealth(
            adapter_name=self.adapter_name(),
            status="OK",
            checked_at=datetime.now(timezone.utc),
            stale=False,
            message="ccxt read-only skeleton with injected client",
        )

    def fetch_ohlcv(self, request: MarketDataRequest) -> tuple[OHLCVBar, ...]:
        rows = self._client.fetch_ohlcv(request.symbol, limit=request.limit)
        return tuple(self._ohlcv_row_to_bar(request, row) for row in rows)

    def fetch_trades(self, request: MarketDataRequest) -> tuple[TradeTick, ...]:
        rows = self._client.fetch_trades(request.symbol, limit=request.limit)
        return tuple(self._trade_to_tick(request, row) for row in rows)

    def fetch_order_book(self, request: MarketDataRequest) -> OrderBookSnapshot:
        data = self._client.fetch_order_book(request.symbol, limit=request.limit)
        timestamp = self._timestamp(data.get("timestamp"))
        return OrderBookSnapshot(
            symbol=request.symbol,
            venue=request.venue,
            timestamp=timestamp,
            bids=[self._level(level) for level in data.get("bids", [])],
            asks=[self._level(level) for level in data.get("asks", [])],
        )

    def fetch_funding_rates(self, request: MarketDataRequest) -> list:
        return []

    def fetch_market_calendar(self, request: MarketDataRequest) -> list:
        return []

    def fetch_economic_calendar(self, request: MarketDataRequest) -> list:
        return []

    def fetch_news(self, request: MarketDataRequest) -> list:
        return []

    # ── conversion helpers ────────────────────────────────────────────────────

    def _ohlcv_row_to_bar(
        self, request: MarketDataRequest, row: list[Any] | tuple[Any, ...]
    ) -> OHLCVBar:
        timestamp, open_, high, low, close, volume = row
        return OHLCVBar(
            symbol=request.symbol,
            venue=request.venue,
            timestamp=self._timestamp(timestamp),
            open=self._decimal("open", open_),
            high=self._decimal("high", high),
            low=self._decimal("low", low),
            close=self._decimal("close", close),
            volume=self._decimal("volume", volume),
        )

    def _trade_to_tick(self, request: MarketDataRequest, trade: dict[str, Any]) -> TradeTick:
        side = self._normalize_side(trade.get("side"))
        return TradeTick(
            symbol=request.symbol,
            venue=request.venue,
            timestamp=self._timestamp(trade.get("timestamp")),
            price=self._decimal("price", trade["price"]),
            quantity=self._decimal("amount", trade["amount"]),
            side=side,
        )

    def _level(self, row: list[Any] | tuple[Any, ...]) -> OrderBookLevel:
        price, quantity = row[:2]
        return OrderBookLevel(
            price=self._decimal("price", price),
            quantity=self._decimal("quantity", quantity),
        )

    def _timestamp(self, value: Any) -> datetime:
        if value is None:
            return datetime.now(timezone.utc)
        if isinstance(value, datetime):
            return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
        seconds = float(Decimal(str(value)) / Decimal("1000"))
        return datetime.fromtimestamp(seconds, tz=timezone.utc)

    def _decimal(self, field_name: str, value: Any) -> Decimal:
        if value is None:
            raise CcxtConversionError(
                f"cannot convert None to Decimal: field {field_name!r} is missing from raw data"
            )
        try:
            return Decimal(str(value))
        except InvalidOperation as exc:
            raise CcxtConversionError(
                f"cannot convert {value!r} to Decimal for field {field_name!r}"
            ) from exc

    @staticmethod
    def _normalize_side(raw: Any) -> str | None:
        """Normalize CCXT trade side to canonical lowercase 'buy'/'sell' or None."""
        if raw is None:
            return None
        if isinstance(raw, str):
            normalized = raw.strip().lower()
            if normalized in ("buy", "sell"):
                return normalized
        return None
