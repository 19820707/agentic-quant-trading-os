from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from packages.domain import OHLCVCandle, SignalSide
from packages.domain.base import DomainModelError, require_positive, require_ratio

from .base import (
    BaseResearchStrategy,
    StrategyCapabilityProfile,
    StrategyConfig,
    StrategyError,
    StrategyMode,
    StrategyOutput,
    StrategyRuntimeContext,
    decimal_average,
    require_positive_int,
)


@dataclass(frozen=True)
class MovingAverageCrossoverParameters:
    short_window: int
    long_window: int
    min_strength: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        require_positive_int(self.short_window, "short_window")
        require_positive_int(self.long_window, "long_window")
        if self.short_window >= self.long_window:
            raise DomainModelError("short_window must be lower than long_window")
        require_ratio(self.min_strength, "min_strength")


class MovingAverageCrossoverStrategy(BaseResearchStrategy):
    def __init__(self, config: StrategyConfig, parameters: MovingAverageCrossoverParameters) -> None:
        super().__init__(
            config,
            StrategyCapabilityProfile(
                strategy_family="moving_average_crossover",
                supported_modes=frozenset({StrategyMode.RESEARCH, StrategyMode.BACKTEST, StrategyMode.PAPER, StrategyMode.PAPER_ONLY}),
            ),
        )
        self.parameters = parameters
        self._closes: list[Decimal] = []

    def on_market_data(self, event: OHLCVCandle, context: StrategyRuntimeContext) -> StrategyOutput:
        self._require_expected_market(event)
        self._closes.append(event.close)

        if len(self._closes) < self.parameters.long_window:
            return StrategyOutput(diagnostics={"status": "warming_up", "observations": len(self._closes)})

        short_values = tuple(self._closes[-self.parameters.short_window :])
        long_values = tuple(self._closes[-self.parameters.long_window :])
        short_ma = decimal_average(short_values)
        long_ma = decimal_average(long_values)
        edge = (short_ma - long_ma) / long_ma
        strength = min(abs(edge), Decimal("1"))

        if strength < self.parameters.min_strength:
            side = SignalSide.HOLD
        elif short_ma > long_ma:
            side = SignalSide.BUY
        elif short_ma < long_ma:
            side = SignalSide.SELL
        else:
            side = SignalSide.HOLD

        signal = self._signal(
            side=side,
            strength=strength,
            generated_at=event.timestamp,
            rationale="moving_average_crossover_research_signal",
            attributes={
                "short_window": self.parameters.short_window,
                "long_window": self.parameters.long_window,
                "short_ma": short_ma,
                "long_ma": long_ma,
                "order_creation_allowed": False,
            },
        )
        return StrategyOutput(signals=(signal,), diagnostics={"status": "signal_emitted"})

    def _require_expected_market(self, event: OHLCVCandle) -> None:
        if event.symbol != self.config.symbol or event.venue != self.config.venue:
            raise StrategyError("market data event does not match strategy symbol/venue")


@dataclass(frozen=True)
class MeanReversionParameters:
    lookback_window: int
    threshold_bps: Decimal

    def __post_init__(self) -> None:
        require_positive_int(self.lookback_window, "lookback_window")
        require_positive(self.threshold_bps, "threshold_bps")


class MeanReversionStrategy(BaseResearchStrategy):
    def __init__(self, config: StrategyConfig, parameters: MeanReversionParameters) -> None:
        super().__init__(
            config,
            StrategyCapabilityProfile(
                strategy_family="mean_reversion",
                supported_modes=frozenset({StrategyMode.RESEARCH, StrategyMode.BACKTEST, StrategyMode.PAPER, StrategyMode.PAPER_ONLY}),
            ),
        )
        self.parameters = parameters
        self._closes: list[Decimal] = []

    def on_market_data(self, event: OHLCVCandle, context: StrategyRuntimeContext) -> StrategyOutput:
        self._closes.append(event.close)
        if len(self._closes) < self.parameters.lookback_window:
            return StrategyOutput(diagnostics={"status": "warming_up", "observations": len(self._closes)})

        window = tuple(self._closes[-self.parameters.lookback_window :])
        mean = decimal_average(window)
        threshold = self.parameters.threshold_bps / Decimal("10000")
        deviation = (event.close - mean) / mean
        strength = min(abs(deviation), Decimal("1"))

        if deviation <= -threshold:
            side = SignalSide.BUY
        elif deviation >= threshold:
            side = SignalSide.SELL
        else:
            side = SignalSide.HOLD

        return StrategyOutput(
            signals=(
                self._signal(
                    side=side,
                    strength=strength,
                    generated_at=event.timestamp,
                    rationale="mean_reversion_research_signal",
                    attributes={
                        "lookback_window": self.parameters.lookback_window,
                        "mean": mean,
                        "deviation": deviation,
                        "threshold_bps": self.parameters.threshold_bps,
                    },
                ),
            ),
            diagnostics={"status": "signal_emitted"},
        )


@dataclass(frozen=True)
class VolatilityBreakoutParameters:
    lookback_window: int

    def __post_init__(self) -> None:
        require_positive_int(self.lookback_window, "lookback_window")


class VolatilityBreakoutStrategy(BaseResearchStrategy):
    def __init__(self, config: StrategyConfig, parameters: VolatilityBreakoutParameters) -> None:
        super().__init__(
            config,
            StrategyCapabilityProfile(
                strategy_family="volatility_breakout",
                supported_modes=frozenset({StrategyMode.RESEARCH, StrategyMode.BACKTEST, StrategyMode.PAPER, StrategyMode.PAPER_ONLY}),
            ),
        )
        self.parameters = parameters
        self._candles: list[OHLCVCandle] = []

    def on_market_data(self, event: OHLCVCandle, context: StrategyRuntimeContext) -> StrategyOutput:
        if len(self._candles) < self.parameters.lookback_window:
            self._candles.append(event)
            return StrategyOutput(diagnostics={"status": "warming_up", "observations": len(self._candles)})

        prior_window = tuple(self._candles[-self.parameters.lookback_window :])
        prior_high = max(candle.high for candle in prior_window)
        prior_low = min(candle.low for candle in prior_window)
        self._candles.append(event)

        if event.close > prior_high:
            side = SignalSide.BUY
            distance = (event.close - prior_high) / prior_high
        elif event.close < prior_low:
            side = SignalSide.SELL
            distance = (prior_low - event.close) / prior_low
        else:
            side = SignalSide.HOLD
            distance = Decimal("0")

        return StrategyOutput(
            signals=(
                self._signal(
                    side=side,
                    strength=min(distance, Decimal("1")),
                    generated_at=event.timestamp,
                    rationale="volatility_breakout_research_signal",
                    attributes={
                        "lookback_window": self.parameters.lookback_window,
                        "prior_high": prior_high,
                        "prior_low": prior_low,
                    },
                ),
            ),
            diagnostics={"status": "signal_emitted"},
        )


@dataclass(frozen=True)
class GridResearchParameters:
    lower_bound: Decimal
    upper_bound: Decimal
    levels: int

    def __post_init__(self) -> None:
        require_positive(self.lower_bound, "lower_bound")
        require_positive(self.upper_bound, "upper_bound")
        if self.lower_bound >= self.upper_bound:
            raise DomainModelError("lower_bound must be below upper_bound")
        require_positive_int(self.levels, "levels")
        if self.levels < 2:
            raise DomainModelError("levels must be at least 2")


class GridResearchStrategy(BaseResearchStrategy):
    """Paper-only research scaffold that emits observation signals, never orders."""

    def __init__(self, config: StrategyConfig, parameters: GridResearchParameters) -> None:
        super().__init__(
            config,
            StrategyCapabilityProfile(
                strategy_family="grid_research",
                supported_modes=frozenset({StrategyMode.RESEARCH, StrategyMode.BACKTEST, StrategyMode.PAPER, StrategyMode.PAPER_ONLY}),
            ),
        )
        self.parameters = parameters

    def on_market_data(self, event: OHLCVCandle, context: StrategyRuntimeContext) -> StrategyOutput:
        if event.close <= self.parameters.lower_bound:
            side = SignalSide.BUY
            strength = min((self.parameters.lower_bound - event.close) / self.parameters.lower_bound, Decimal("1"))
        elif event.close >= self.parameters.upper_bound:
            side = SignalSide.SELL
            strength = min((event.close - self.parameters.upper_bound) / self.parameters.upper_bound, Decimal("1"))
        else:
            side = SignalSide.HOLD
            strength = Decimal("0")

        return StrategyOutput(
            signals=(
                self._signal(
                    side=side,
                    strength=strength,
                    generated_at=event.timestamp,
                    rationale="grid_research_paper_only_observation",
                    attributes={
                        "lower_bound": self.parameters.lower_bound,
                        "upper_bound": self.parameters.upper_bound,
                        "levels": self.parameters.levels,
                        "local_only": True,
                        "mode": self.config.mode.value,
                    },
                ),
            ),
            diagnostics={"status": "local_grid_signal_emitted", "mode": self.config.mode.value},
        )


@dataclass(frozen=True)
class InventoryMarketMakingParameters:
    target_inventory: Decimal
    current_inventory: Decimal
    max_inventory_abs: Decimal
    quote_spread_bps: Decimal
    inventory_skew_bps: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        require_positive(self.max_inventory_abs, "max_inventory_abs")
        require_positive(self.quote_spread_bps, "quote_spread_bps")
        if self.inventory_skew_bps < Decimal("0"):
            raise DomainModelError("inventory_skew_bps must be non-negative")
        if abs(self.target_inventory) > self.max_inventory_abs:
            raise DomainModelError("target_inventory must be within max_inventory_abs")
        if abs(self.current_inventory) > self.max_inventory_abs:
            raise DomainModelError("current_inventory must be within max_inventory_abs")


class InventoryAwareMarketMakingStrategy(BaseResearchStrategy):
    """Local signal-only market-making scaffold with inventory pressure controls."""

    def __init__(self, config: StrategyConfig, parameters: InventoryMarketMakingParameters) -> None:
        super().__init__(
            config,
            StrategyCapabilityProfile(
                strategy_family="inventory_aware_market_making",
                supported_modes=frozenset({StrategyMode.RESEARCH, StrategyMode.BACKTEST, StrategyMode.PAPER, StrategyMode.PAPER_ONLY}),
            ),
        )
        self.parameters = parameters

    def on_market_data(self, event: OHLCVCandle, context: StrategyRuntimeContext) -> StrategyOutput:
        self._require_expected_market(event)
        inventory_gap = self.parameters.target_inventory - self.parameters.current_inventory
        inventory_pressure = abs(inventory_gap) / self.parameters.max_inventory_abs
        strength = min(inventory_pressure, Decimal("1"))

        if inventory_gap > Decimal("0"):
            side = SignalSide.BUY
        elif inventory_gap < Decimal("0"):
            side = SignalSide.SELL
        else:
            side = SignalSide.HOLD

        half_spread = self.parameters.quote_spread_bps / Decimal("20000")
        bid_reference = event.close * (Decimal("1") - half_spread)
        ask_reference = event.close * (Decimal("1") + half_spread)

        return StrategyOutput(
            signals=(
                self._signal(
                    side=side,
                    strength=strength,
                    generated_at=event.timestamp,
                    rationale="inventory_aware_market_making_local_signal",
                    attributes={
                        "target_inventory": self.parameters.target_inventory,
                        "current_inventory": self.parameters.current_inventory,
                        "max_inventory_abs": self.parameters.max_inventory_abs,
                        "inventory_gap": inventory_gap,
                        "inventory_pressure": inventory_pressure,
                        "quote_spread_bps": self.parameters.quote_spread_bps,
                        "inventory_skew_bps": self.parameters.inventory_skew_bps,
                        "bid_reference": bid_reference,
                        "ask_reference": ask_reference,
                        "local_only": True,
                        "order_creation_allowed": False,
                    },
                ),
            ),
            diagnostics={
                "status": "inventory_market_making_signal_emitted",
                "mode": self.config.mode.value,
                "quotes_are_references_only": True,
            },
        )

    def _require_expected_market(self, event: OHLCVCandle) -> None:
        if event.symbol != self.config.symbol or event.venue != self.config.venue:
            raise StrategyError("market data event does not match strategy symbol/venue")
