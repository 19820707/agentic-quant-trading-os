from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from .base import (
    SerializableModel,
    parse_datetime,
    parse_decimal,
    require_aware_datetime,
    require_non_empty,
    require_non_negative,
    require_positive,
)


@dataclass(frozen=True)
class Symbol(SerializableModel):
    value: str

    def __post_init__(self) -> None:
        require_non_empty(self.value, "symbol")


@dataclass(frozen=True)
class Venue(SerializableModel):
    value: str

    def __post_init__(self) -> None:
        require_non_empty(self.value, "venue")


@dataclass(frozen=True)
class Trade(SerializableModel):
    trade_id: str
    symbol: Symbol
    venue: Venue
    timestamp: datetime
    price: Decimal
    quantity: Decimal
    side: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.trade_id, "trade_id")
        require_aware_datetime(self.timestamp, "timestamp")
        require_positive(self.price, "price")
        require_positive(self.quantity, "quantity")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Trade":
        return cls(
            trade_id=str(data["trade_id"]),
            symbol=Symbol(str(data["symbol"]["value"])),
            venue=Venue(str(data["venue"]["value"])),
            timestamp=parse_datetime(data["timestamp"], "timestamp"),
            price=parse_decimal(data["price"], "price"),
            quantity=parse_decimal(data["quantity"], "quantity"),
            side=data.get("side") if data.get("side") is None else str(data["side"]),
        )


@dataclass(frozen=True)
class Ticker(SerializableModel):
    symbol: Symbol
    venue: Venue
    timestamp: datetime
    bid: Decimal
    ask: Decimal
    last: Decimal

    def __post_init__(self) -> None:
        require_aware_datetime(self.timestamp, "timestamp")
        require_positive(self.bid, "bid")
        require_positive(self.ask, "ask")
        require_positive(self.last, "last")
        if self.bid > self.ask:
            raise ValueError("bid must be less than or equal to ask")


@dataclass(frozen=True)
class OHLCVCandle(SerializableModel):
    symbol: Symbol
    venue: Venue
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        require_aware_datetime(self.timestamp, "timestamp")
        for field_name in ("open", "high", "low", "close"):
            require_positive(getattr(self, field_name), field_name)
        require_non_negative(self.volume, "volume")
        if self.low > self.high:
            raise ValueError("low must be less than or equal to high")
        if self.open > self.high or self.close > self.high or self.open < self.low or self.close < self.low:
            raise ValueError("open and close must stay inside high/low range")


@dataclass(frozen=True)
class OrderBookLevel(SerializableModel):
    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        require_positive(self.price, "price")
        require_positive(self.quantity, "quantity")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "OrderBookLevel":
        return cls(
            price=parse_decimal(data["price"], "price"),
            quantity=parse_decimal(data["quantity"], "quantity"),
        )


@dataclass(frozen=True)
class OrderBookSnapshot(SerializableModel):
    symbol: Symbol
    venue: Venue
    timestamp: datetime
    bids: tuple[OrderBookLevel, ...]
    asks: tuple[OrderBookLevel, ...]

    def __post_init__(self) -> None:
        require_aware_datetime(self.timestamp, "timestamp")
        if any(level.quantity <= Decimal("0") for level in self.bids + self.asks):
            raise ValueError("order book quantities must be positive")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "OrderBookSnapshot":
        return cls(
            symbol=Symbol(str(data["symbol"]["value"])),
            venue=Venue(str(data["venue"]["value"])),
            timestamp=parse_datetime(data["timestamp"], "timestamp"),
            bids=tuple(OrderBookLevel.from_dict(item) for item in data["bids"]),
            asks=tuple(OrderBookLevel.from_dict(item) for item in data["asks"]),
        )


@dataclass(frozen=True)
class OrderBookDelta(SerializableModel):
    symbol: Symbol
    venue: Venue
    timestamp: datetime
    sequence: int
    bid_updates: tuple[OrderBookLevel, ...]
    ask_updates: tuple[OrderBookLevel, ...]

    def __post_init__(self) -> None:
        require_aware_datetime(self.timestamp, "timestamp")
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")


@dataclass(frozen=True)
class FundingRate(SerializableModel):
    symbol: Symbol
    venue: Venue
    timestamp: datetime
    funding_rate: Decimal

    def __post_init__(self) -> None:
        require_aware_datetime(self.timestamp, "timestamp")
        require_non_negative(abs(self.funding_rate), "funding_rate")


@dataclass(frozen=True)
class OpenInterest(SerializableModel):
    symbol: Symbol
    venue: Venue
    timestamp: datetime
    quantity: Decimal
    notional: Decimal | None = None

    def __post_init__(self) -> None:
        require_aware_datetime(self.timestamp, "timestamp")
        require_non_negative(self.quantity, "quantity")
        if self.notional is not None:
            require_non_negative(self.notional, "notional")
