from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from backtesting import BacktestConfig, BacktestError, run_event_driven_backtest
from packages.domain import CorrelationId, OHLCVCandle, RiskDecision, StrategyId, StrategyVersion, Symbol, Venue
from risk import RiskLimits, RiskRuntimeState
from strategies import MovingAverageCrossoverParameters, MovingAverageCrossoverStrategy, StrategyConfig


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)
BTC = Symbol("BTC/USDT")
PAPER = Venue("paper")


def candle(index: int, close: str, volume: str = "1000") -> OHLCVCandle:
    price = Decimal(close)
    return OHLCVCandle(
        symbol=BTC,
        venue=PAPER,
        timestamp=NOW + timedelta(minutes=index),
        open=price,
        high=price + Decimal("1"),
        low=price - Decimal("1"),
        close=price,
        volume=Decimal(volume),
    )


def events() -> tuple[OHLCVCandle, ...]:
    return (
        candle(0, "100"),
        candle(1, "101"),
        candle(2, "104"),
        candle(3, "105"),
    )


def strategy() -> MovingAverageCrossoverStrategy:
    return MovingAverageCrossoverStrategy(
        StrategyConfig(
            strategy_id=StrategyId("bt.ma"),
            strategy_version=StrategyVersion("1.0.0"),
            symbol=BTC,
            venue=PAPER,
        ),
        MovingAverageCrossoverParameters(short_window=2, long_window=3),
    )


def config(**overrides: object) -> BacktestConfig:
    values = {
        "backtest_id": "bt_fixture",
        "portfolio_id": "portfolio_fixture",
        "starting_cash": Decimal("10000"),
        "order_quantity": Decimal("1"),
    }
    values.update(overrides)
    return BacktestConfig(**values)


def limits(**overrides: object) -> RiskLimits:
    values = {
        "max_order_notional": Decimal("1000"),
        "max_symbol_exposure": Decimal("5000"),
        "max_venue_exposure": Decimal("5000"),
        "max_gross_exposure": Decimal("10000"),
        "max_leverage": Decimal("2"),
        "max_daily_loss": Decimal("1000"),
        "max_drawdown": Decimal("2000"),
        "max_open_orders": 100,
        "max_orders_per_minute": 20,
        "stale_price_after": timedelta(minutes=5),
        "max_price_deviation_bps": Decimal("250"),
        "min_liquidity_notional": Decimal("1000"),
    }
    values.update(overrides)
    return RiskLimits(**values)


class BacktestingEngineTests(unittest.TestCase):
    def test_config_blocks_live_network_credentials_and_unsafe_paper_fill(self) -> None:
        for flag in ("live_trading_enabled", "network_allowed", "credentials_allowed"):
            with self.subTest(flag=flag):
                with self.assertRaises(BacktestError):
                    config(**{flag: True})

        with self.assertRaises(BacktestError):
            config(allow_paper_fills=True, paper_runtime_enabled=False)

    def test_backtest_generates_signals_but_blocks_order_intents_by_default(self) -> None:
        result = run_event_driven_backtest(
            config=config(),
            strategy=strategy(),
            events=events(),
            risk_limits=limits(),
            started_at=NOW,
            correlation_id=CorrelationId("corr_backtest"),
        )

        self.assertEqual(result.runtime_mode, "local_research_only")
        self.assertEqual(result.metrics.events_seen, 4)
        self.assertEqual(result.metrics.candles_seen, 4)
        self.assertEqual(result.metrics.signals_emitted, 2)
        self.assertEqual(result.metrics.order_intents_created, 0)
        self.assertEqual(result.metrics.risk_checks, 0)
        self.assertTrue(all(warning.startswith("order_intent_creation_blocked:") for warning in result.warnings))
        self.assertFalse(result.live_trading_used)
        self.assertFalse(result.network_used)
        self.assertFalse(result.credentials_used)

    def test_order_intent_research_path_runs_risk_but_remains_fail_closed(self) -> None:
        result = run_event_driven_backtest(
            config=config(allow_order_intent_creation=True),
            strategy=strategy(),
            events=events(),
            risk_limits=limits(),
            risk_runtime=RiskRuntimeState(kill_switch_active=True, peak_equity=Decimal("10000")),
            started_at=NOW,
            correlation_id=CorrelationId("corr_backtest"),
        )

        self.assertEqual(result.metrics.order_intents_created, 2)
        self.assertEqual(result.metrics.risk_checks, 2)
        self.assertEqual(result.metrics.rejected_risk_checks, 2)
        self.assertTrue(all(risk_result.decision is RiskDecision.REJECT for risk_result in result.risk_results))
        self.assertEqual(result.metrics.paper_fills, 0)

    def test_paper_fill_attempts_are_rejected_without_explicit_risk_approval(self) -> None:
        result = run_event_driven_backtest(
            config=config(
                allow_order_intent_creation=True,
                allow_paper_fills=True,
                paper_runtime_enabled=True,
            ),
            strategy=strategy(),
            events=events(),
            risk_limits=limits(),
            risk_runtime=RiskRuntimeState(kill_switch_active=False, peak_equity=Decimal("10000")),
            started_at=NOW,
            correlation_id=CorrelationId("corr_backtest"),
        )

        self.assertEqual(result.metrics.review_risk_checks, 2)
        self.assertEqual(result.metrics.paper_fills, 0)
        self.assertTrue(any(warning.startswith("paper_fill_rejected:") for warning in result.warnings))

    def test_backtest_is_deterministic_for_same_inputs(self) -> None:
        first = run_event_driven_backtest(
            config=config(allow_order_intent_creation=True),
            strategy=strategy(),
            events=events(),
            risk_limits=limits(),
            started_at=NOW,
            correlation_id=CorrelationId("corr_backtest"),
        )
        second = run_event_driven_backtest(
            config=config(allow_order_intent_creation=True),
            strategy=strategy(),
            events=events(),
            risk_limits=limits(),
            started_at=NOW,
            correlation_id=CorrelationId("corr_backtest"),
        )

        self.assertEqual([signal.signal_id for signal in first.signals], [signal.signal_id for signal in second.signals])
        self.assertEqual(
            [intent.order_intent_id for intent in first.order_intents],
            [intent.order_intent_id for intent in second.order_intents],
        )
        self.assertEqual(first.metrics, second.metrics)


if __name__ == "__main__":
    unittest.main()
