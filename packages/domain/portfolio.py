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
from .market_data import Symbol, Venue


@dataclass(frozen=True)
class Balance(SerializableModel):
    asset: str
    total: Decimal
    available: Decimal
    locked: Decimal

    def __post_init__(self) -> None:
        require_non_empty(self.asset, "asset")
        require_non_negative(self.total, "total")
        require_non_negative(self.available, "available")
        require_non_negative(self.locked, "locked")
        if self.available + self.locked > self.total:
            raise ValueError("available plus locked cannot exceed total")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Balance":
        return cls(
            asset=str(data["asset"]),
            total=parse_decimal(data["total"], "total"),
            available=parse_decimal(data["available"], "available"),
            locked=parse_decimal(data["locked"], "locked"),
        )


@dataclass(frozen=True)
class Position(SerializableModel):
    symbol: Symbol
    venue: Venue
    quantity: Decimal
    average_entry_price: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal

    def __post_init__(self) -> None:
        if self.quantity == Decimal("0"):
            require_non_negative(self.average_entry_price, "average_entry_price")
        else:
            require_positive(abs(self.quantity), "quantity")
            require_positive(self.average_entry_price, "average_entry_price")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Position":
        return cls(
            symbol=Symbol(str(data["symbol"]["value"])),
            venue=Venue(str(data["venue"]["value"])),
            quantity=parse_decimal(data["quantity"], "quantity"),
            average_entry_price=parse_decimal(data["average_entry_price"], "average_entry_price"),
            unrealized_pnl=parse_decimal(data["unrealized_pnl"], "unrealized_pnl"),
            realized_pnl=parse_decimal(data["realized_pnl"], "realized_pnl"),
        )


@dataclass(frozen=True)
class PnL(SerializableModel):
    realized: Decimal
    unrealized: Decimal
    fees: Decimal
    funding: Decimal = Decimal("0")

    @property
    def total(self) -> Decimal:
        return self.realized + self.unrealized + self.funding - self.fees


@dataclass(frozen=True)
class ExposureSnapshot(SerializableModel):
    gross_exposure: Decimal
    net_exposure: Decimal
    by_symbol: dict[str, Decimal]
    by_venue: dict[str, Decimal]

    def __post_init__(self) -> None:
        require_non_negative(self.gross_exposure, "gross_exposure")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ExposureSnapshot":
        return cls(
            gross_exposure=parse_decimal(data["gross_exposure"], "gross_exposure"),
            net_exposure=parse_decimal(data["net_exposure"], "net_exposure"),
            by_symbol={key: parse_decimal(value, key) for key, value in data["by_symbol"].items()},
            by_venue={key: parse_decimal(value, key) for key, value in data["by_venue"].items()},
        )


@dataclass(frozen=True)
class PortfolioSnapshot(SerializableModel):
    portfolio_id: str
    timestamp: datetime
    balances: tuple[Balance, ...]
    positions: tuple[Position, ...]
    exposure: ExposureSnapshot
    pnl: PnL

    def __post_init__(self) -> None:
        require_non_empty(self.portfolio_id, "portfolio_id")
        require_aware_datetime(self.timestamp, "timestamp")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "PortfolioSnapshot":
        return cls(
            portfolio_id=str(data["portfolio_id"]),
            timestamp=parse_datetime(data["timestamp"], "timestamp"),
            balances=tuple(Balance.from_dict(item) for item in data["balances"]),
            positions=tuple(Position.from_dict(item) for item in data["positions"]),
            exposure=ExposureSnapshot.from_dict(data["exposure"]),
            pnl=PnL(
                realized=parse_decimal(data["pnl"]["realized"], "realized"),
                unrealized=parse_decimal(data["pnl"]["unrealized"], "unrealized"),
                fees=parse_decimal(data["pnl"]["fees"], "fees"),
                funding=parse_decimal(data["pnl"]["funding"], "funding"),
            ),
        )
