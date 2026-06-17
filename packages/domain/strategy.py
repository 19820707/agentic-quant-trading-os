from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .base import (
    SerializableModel,
    deterministic_id,
    parse_datetime,
    parse_decimal,
    require_aware_datetime,
    require_non_empty,
    require_ratio,
)
from .market_data import Symbol, Venue


@dataclass(frozen=True)
class StrategyId(SerializableModel):
    value: str

    def __post_init__(self) -> None:
        require_non_empty(self.value, "strategy_id")


@dataclass(frozen=True)
class StrategyVersion(SerializableModel):
    value: str

    def __post_init__(self) -> None:
        require_non_empty(self.value, "strategy_version")


class SignalSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class SignalStrength(SerializableModel):
    value: Decimal

    def __post_init__(self) -> None:
        require_ratio(self.value, "signal_strength")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "SignalStrength":
        return cls(parse_decimal(data["value"], "signal_strength"))


@dataclass(frozen=True)
class SignalMetadata(SerializableModel):
    model_version: str
    rationale: str = ""
    attributes: dict[str, str | int | Decimal | bool | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.model_version, "model_version")


@dataclass(frozen=True)
class Signal(SerializableModel):
    signal_id: str
    strategy_id: StrategyId
    strategy_version: StrategyVersion
    symbol: Symbol
    venue: Venue
    side: SignalSide
    strength: SignalStrength
    generated_at: datetime
    metadata: SignalMetadata

    def __post_init__(self) -> None:
        require_non_empty(self.signal_id, "signal_id")
        require_aware_datetime(self.generated_at, "generated_at")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Signal":
        return cls(
            signal_id=str(data["signal_id"]),
            strategy_id=StrategyId(str(data["strategy_id"]["value"])),
            strategy_version=StrategyVersion(str(data["strategy_version"]["value"])),
            symbol=Symbol(str(data["symbol"]["value"])),
            venue=Venue(str(data["venue"]["value"])),
            side=SignalSide(str(data["side"])),
            strength=SignalStrength.from_dict(data["strength"]),
            generated_at=parse_datetime(data["generated_at"], "generated_at"),
            metadata=SignalMetadata(
                model_version=str(data["metadata"]["model_version"]),
                rationale=str(data["metadata"].get("rationale", "")),
                attributes=dict(data["metadata"].get("attributes", {})),
            ),
        )

    @classmethod
    def deterministic(
        cls,
        *,
        strategy_id: StrategyId,
        strategy_version: StrategyVersion,
        symbol: Symbol,
        venue: Venue,
        side: SignalSide,
        strength: SignalStrength,
        generated_at: datetime,
        metadata: SignalMetadata,
    ) -> "Signal":
        signal_id = deterministic_id(
            "sig",
            strategy_id.value,
            strategy_version.value,
            symbol.value,
            venue.value,
            side.value,
            generated_at.isoformat(),
        )
        return cls(signal_id, strategy_id, strategy_version, symbol, venue, side, strength, generated_at, metadata)
