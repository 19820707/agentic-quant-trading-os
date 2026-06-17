from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Protocol

from packages.domain import (
    OHLCVCandle,
    Signal,
    SignalMetadata,
    SignalSide,
    SignalStrength,
    StrategyId,
    StrategyVersion,
    Symbol,
    Venue,
)
from packages.domain.base import DomainModelError, require_aware_datetime, require_non_empty, require_ratio


class StrategyError(ValueError):
    """Raised when a strategy violates local scaffold safety constraints."""


class StrategyMode(str, Enum):
    RESEARCH = "RESEARCH"
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    PAPER_ONLY = "PAPER_ONLY"


PROHIBITED_STRATEGY_METHOD_NAMES = {
    "buy",
    "sell",
    "order",
    "submit_order",
    "cancel_order",
    "edit_order",
    "withdraw",
    "transfer",
    "execute",
    "place_order",
    "create_order",
}


@dataclass(frozen=True)
class StrategyCapabilityProfile:
    strategy_family: str
    supported_modes: frozenset[StrategyMode]
    emits_signals: bool = True
    creates_order_intents: bool = False
    uses_network: bool = False
    uses_credentials: bool = False
    supports_long: bool = True
    supports_short: bool = True

    def __post_init__(self) -> None:
        require_non_empty(self.strategy_family, "strategy_family")
        if not self.supported_modes:
            raise StrategyError("strategy capability profile must declare at least one supported mode")
        if not self.emits_signals:
            raise StrategyError("strategy capability profile must emit signals in this scaffold")
        if self.creates_order_intents:
            raise StrategyError("strategies must not create OrderIntent objects")
        if self.uses_network:
            raise StrategyError("strategies must not use network access")
        if self.uses_credentials:
            raise StrategyError("strategies must not use credentials")

    def allows_mode(self, mode: StrategyMode) -> bool:
        return mode in self.supported_modes


@dataclass(frozen=True)
class StrategyConfig:
    strategy_id: StrategyId
    strategy_version: StrategyVersion
    symbol: Symbol
    venue: Venue
    mode: StrategyMode = StrategyMode.RESEARCH
    parameters: dict[str, str | int | Decimal | bool] = field(default_factory=dict)
    live_trading_enabled: bool = False
    order_intent_creation_enabled: bool = False
    max_signals_per_event: int = 1

    def __post_init__(self) -> None:
        if self.live_trading_enabled:
            raise StrategyError("strategy live trading must be disabled in scaffold mode")
        if self.order_intent_creation_enabled:
            raise StrategyError("strategies must not create OrderIntent objects")
        require_positive_int(self.max_signals_per_event, "max_signals_per_event")


@dataclass(frozen=True)
class StrategyRuntimeContext:
    correlation_id: str
    generated_at: datetime
    runtime_mode: str = "local_only"
    network_allowed: bool = False
    credentials_allowed: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.correlation_id, "correlation_id")
        require_aware_datetime(self.generated_at, "generated_at")
        if self.runtime_mode != "local_only":
            raise StrategyError("strategy runtime must remain local_only")
        if self.network_allowed:
            raise StrategyError("strategy runtime must not allow network access")
        if self.credentials_allowed:
            raise StrategyError("strategy runtime must not allow credentials")


@dataclass(frozen=True)
class StrategyOutput:
    signals: tuple[Signal, ...] = ()
    diagnostics: dict[str, str | int | Decimal | bool | None] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    order_intents_created: bool = False

    def __post_init__(self) -> None:
        if self.order_intents_created:
            raise StrategyError("strategy output must not contain OrderIntent creation")


class Strategy(Protocol):
    @property
    def config(self) -> StrategyConfig:
        ...

    def on_start(self, context: StrategyRuntimeContext) -> StrategyOutput:
        ...

    def on_market_data(self, event: OHLCVCandle, context: StrategyRuntimeContext) -> StrategyOutput:
        ...

    def on_timer(self, context: StrategyRuntimeContext) -> StrategyOutput:
        ...

    def on_stop(self, context: StrategyRuntimeContext) -> StrategyOutput:
        ...


class BaseResearchStrategy:
    """Base class for local-only strategies that emit signals, never orders."""

    def __init__(self, config: StrategyConfig, capabilities: StrategyCapabilityProfile | None = None) -> None:
        self._config = config
        self._capabilities = capabilities or StrategyCapabilityProfile(
            strategy_family=self.__class__.__name__,
            supported_modes=frozenset({StrategyMode.RESEARCH, StrategyMode.BACKTEST, StrategyMode.PAPER, StrategyMode.PAPER_ONLY}),
        )
        if not self._capabilities.allows_mode(config.mode):
            raise StrategyError(f"strategy mode {config.mode.value} is not supported by {self._capabilities.strategy_family}")
        validate_strategy_surface(self)

    @property
    def config(self) -> StrategyConfig:
        return self._config

    @property
    def capabilities(self) -> StrategyCapabilityProfile:
        return self._capabilities

    def on_start(self, context: StrategyRuntimeContext) -> StrategyOutput:
        return StrategyOutput(diagnostics={"status": "started", "runtime_mode": context.runtime_mode})

    def on_timer(self, context: StrategyRuntimeContext) -> StrategyOutput:
        return StrategyOutput(diagnostics={"status": "timer_ignored", "runtime_mode": context.runtime_mode})

    def on_stop(self, context: StrategyRuntimeContext) -> StrategyOutput:
        return StrategyOutput(diagnostics={"status": "stopped", "runtime_mode": context.runtime_mode})

    def _signal(
        self,
        *,
        side: SignalSide,
        strength: Decimal,
        generated_at: datetime,
        rationale: str,
        attributes: dict[str, Any] | None = None,
    ) -> Signal:
        require_ratio(strength, "signal_strength")
        return Signal.deterministic(
            strategy_id=self.config.strategy_id,
            strategy_version=self.config.strategy_version,
            symbol=self.config.symbol,
            venue=self.config.venue,
            side=side,
            strength=SignalStrength(strength),
            generated_at=generated_at,
            metadata=SignalMetadata(
                model_version=f"{self.config.strategy_id.value}:{self.config.strategy_version.value}",
                rationale=rationale,
                attributes=dict(attributes or {}),
            ),
        )


def validate_strategy_surface(strategy: object) -> None:
    exposed = set(dir(strategy))
    prohibited = sorted(exposed.intersection(PROHIBITED_STRATEGY_METHOD_NAMES))
    if prohibited:
        raise StrategyError(f"strategy exposes prohibited execution-like methods: {', '.join(prohibited)}")


def require_positive_int(value: int, field_name: str) -> int:
    if not isinstance(value, int) or value <= 0:
        raise DomainModelError(f"{field_name} must be a positive integer")
    return value


def decimal_average(values: tuple[Decimal, ...]) -> Decimal:
    if not values:
        raise StrategyError("cannot average empty value set")
    return sum(values, Decimal("0")) / Decimal(len(values))
