from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from packages.domain import OHLCVCandle, SignalSide, StrategyId, StrategyVersion, Symbol, Venue
from strategies import (
    GridResearchParameters,
    GridResearchStrategy,
    InventoryAwareMarketMakingStrategy,
    InventoryMarketMakingParameters,
    MeanReversionParameters,
    MeanReversionStrategy,
    MovingAverageCrossoverParameters,
    MovingAverageCrossoverStrategy,
    StrategyConfig,
    StrategyError,
    StrategyMode,
    StrategyOutput,
    StrategyRuntimeContext,
    VolatilityBreakoutParameters,
    VolatilityBreakoutStrategy,
    validate_strategy_surface,
)


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)


def candle(index: int, close: str) -> OHLCVCandle:
    close_value = Decimal(close)
    return OHLCVCandle(
        symbol=Symbol("BTC/USDT"),
        venue=Venue("paper"),
        timestamp=NOW + timedelta(minutes=index),
        open=close_value,
        high=close_value + Decimal("1"),
        low=close_value - Decimal("1"),
        close=close_value,
        volume=Decimal("10"),
    )


def config(*, mode: StrategyMode = StrategyMode.RESEARCH) -> StrategyConfig:
    return StrategyConfig(
        strategy_id=StrategyId("research.strategy"),
        strategy_version=StrategyVersion("1.0.0"),
        symbol=Symbol("BTC/USDT"),
        venue=Venue("paper"),
        mode=mode,
    )


def context() -> StrategyRuntimeContext:
    return StrategyRuntimeContext(correlation_id="corr_strategy_test", generated_at=NOW)


class StrategyEngineTests(unittest.TestCase):
    def test_strategy_config_blocks_live_trading_and_order_intents(self) -> None:
        with self.assertRaises(StrategyError):
            StrategyConfig(
                strategy_id=StrategyId("unsafe"),
                strategy_version=StrategyVersion("1.0.0"),
                symbol=Symbol("BTC/USDT"),
                venue=Venue("paper"),
                live_trading_enabled=True,
            )

    def test_strategy_modes_support_local_research_backtest_and_paper(self) -> None:
        for mode in (StrategyMode.RESEARCH, StrategyMode.BACKTEST, StrategyMode.PAPER, StrategyMode.PAPER_ONLY):
            with self.subTest(mode=mode):
                strategy = MovingAverageCrossoverStrategy(
                    config(mode=mode),
                    MovingAverageCrossoverParameters(short_window=2, long_window=3),
                )

                self.assertTrue(strategy.capabilities.allows_mode(mode))
                self.assertTrue(strategy.capabilities.emits_signals)
                self.assertFalse(strategy.capabilities.creates_order_intents)
                self.assertFalse(strategy.capabilities.uses_network)
                self.assertFalse(strategy.capabilities.uses_credentials)

        with self.assertRaises(StrategyError):
            StrategyConfig(
                strategy_id=StrategyId("unsafe"),
                strategy_version=StrategyVersion("1.0.0"),
                symbol=Symbol("BTC/USDT"),
                venue=Venue("paper"),
                order_intent_creation_enabled=True,
            )

    def test_runtime_context_is_local_only_and_without_credentials(self) -> None:
        with self.assertRaises(StrategyError):
            StrategyRuntimeContext(correlation_id="corr", generated_at=NOW, network_allowed=True)

        with self.assertRaises(StrategyError):
            StrategyRuntimeContext(correlation_id="corr", generated_at=NOW, credentials_allowed=True)

    def test_output_rejects_order_intent_creation_marker(self) -> None:
        with self.assertRaises(StrategyError):
            StrategyOutput(order_intents_created=True)

    def test_strategy_surface_rejects_execution_like_methods(self) -> None:
        UnsafeStrategy = type(
            "UnsafeStrategy",
            (),
            {"submit_" + "order": lambda self: None},
        )

        with self.assertRaises(StrategyError):
            validate_strategy_surface(UnsafeStrategy())

    def test_moving_average_crossover_emits_deterministic_signal_only(self) -> None:
        strategy = MovingAverageCrossoverStrategy(
            config(),
            MovingAverageCrossoverParameters(short_window=2, long_window=3),
        )

        warmup = strategy.on_market_data(candle(0, "100"), context())
        self.assertEqual(warmup.signals, ())

        strategy.on_market_data(candle(1, "101"), context())
        output = strategy.on_market_data(candle(2, "104"), context())

        self.assertEqual(len(output.signals), 1)
        signal = output.signals[0]
        self.assertEqual(signal.side, SignalSide.BUY)
        self.assertFalse(output.order_intents_created)
        self.assertIn("short_ma", signal.metadata.attributes)

        repeated = MovingAverageCrossoverStrategy(
            config(),
            MovingAverageCrossoverParameters(short_window=2, long_window=3),
        )
        repeated.on_market_data(candle(0, "100"), context())
        repeated.on_market_data(candle(1, "101"), context())
        repeated_output = repeated.on_market_data(candle(2, "104"), context())

        self.assertEqual(repeated_output.signals[0].signal_id, signal.signal_id)

    def test_mean_reversion_emits_sell_when_price_is_above_threshold(self) -> None:
        strategy = MeanReversionStrategy(
            config(),
            MeanReversionParameters(lookback_window=3, threshold_bps=Decimal("50")),
        )

        strategy.on_market_data(candle(0, "100"), context())
        strategy.on_market_data(candle(1, "100"), context())
        output = strategy.on_market_data(candle(2, "110"), context())

        self.assertEqual(output.signals[0].side, SignalSide.SELL)
        self.assertIn("deviation", output.signals[0].metadata.attributes)

    def test_volatility_breakout_uses_prior_window_without_lookahead(self) -> None:
        strategy = VolatilityBreakoutStrategy(
            config(),
            VolatilityBreakoutParameters(lookback_window=2),
        )

        strategy.on_market_data(candle(0, "100"), context())
        strategy.on_market_data(candle(1, "101"), context())
        output = strategy.on_market_data(candle(2, "105"), context())

        self.assertEqual(output.signals[0].side, SignalSide.BUY)
        self.assertEqual(output.signals[0].metadata.attributes["prior_high"], Decimal("102"))

    def test_grid_research_runs_in_local_modes_and_remains_signal_only(self) -> None:
        strategy = GridResearchStrategy(
            config(mode=StrategyMode.BACKTEST),
            GridResearchParameters(lower_bound=Decimal("95"), upper_bound=Decimal("105"), levels=5),
        )
        output = strategy.on_market_data(candle(0, "94"), context())

        self.assertEqual(output.signals[0].side, SignalSide.BUY)
        self.assertEqual(output.signals[0].metadata.attributes["local_only"], True)
        self.assertEqual(output.signals[0].metadata.attributes["mode"], StrategyMode.BACKTEST.value)
        self.assertFalse(output.order_intents_created)

    def test_inventory_market_making_emits_inventory_pressure_signal_only(self) -> None:
        strategy = InventoryAwareMarketMakingStrategy(
            config(mode=StrategyMode.PAPER),
            InventoryMarketMakingParameters(
                target_inventory=Decimal("1.0"),
                current_inventory=Decimal("0.25"),
                max_inventory_abs=Decimal("2.0"),
                quote_spread_bps=Decimal("20"),
                inventory_skew_bps=Decimal("5"),
            ),
        )

        output = strategy.on_market_data(candle(0, "100"), context())
        signal = output.signals[0]

        self.assertEqual(signal.side, SignalSide.BUY)
        self.assertEqual(signal.metadata.attributes["inventory_gap"], Decimal("0.75"))
        self.assertEqual(signal.metadata.attributes["inventory_pressure"], Decimal("0.375"))
        self.assertEqual(signal.metadata.attributes["bid_reference"], Decimal("99.900"))
        self.assertEqual(signal.metadata.attributes["ask_reference"], Decimal("100.100"))
        self.assertEqual(signal.metadata.attributes["order_creation_allowed"], False)
        self.assertFalse(output.order_intents_created)

    def test_strategy_rejects_wrong_market_event(self) -> None:
        strategy = MovingAverageCrossoverStrategy(
            config(),
            MovingAverageCrossoverParameters(short_window=2, long_window=3),
        )
        wrong_event = OHLCVCandle(
            symbol=Symbol("ETH/USDT"),
            venue=Venue("paper"),
            timestamp=NOW,
            open=Decimal("100"),
            high=Decimal("101"),
            low=Decimal("99"),
            close=Decimal("100"),
            volume=Decimal("1"),
        )

        with self.assertRaises(StrategyError):
            strategy.on_market_data(wrong_event, context())


if __name__ == "__main__":
    unittest.main()
