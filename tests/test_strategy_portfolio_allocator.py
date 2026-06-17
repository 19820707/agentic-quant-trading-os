from __future__ import annotations

import unittest
from datetime import datetime, timezone
from decimal import Decimal

from packages.domain import Signal, SignalMetadata, SignalSide, SignalStrength, StrategyId, StrategyVersion, Symbol, Venue
from strategies import (
    StrategyError,
    StrategyPortfolioAllocationPolicy,
    StrategyPortfolioAllocator,
    StrategySignalWeight,
)


NOW = datetime(2026, 6, 17, 12, 0, tzinfo=timezone.utc)
BTC = Symbol("BTC/USDT")
PAPER = Venue("paper")


class StrategyPortfolioAllocatorTests(unittest.TestCase):
    def test_allocator_combines_weighted_signals_into_non_executable_candidate(self) -> None:
        allocator = StrategyPortfolioAllocator(
            StrategyPortfolioAllocationPolicy(allocator_id="allocator_local_001"),
            (
                StrategySignalWeight(StrategyId("trend"), Decimal("0.60")),
                StrategySignalWeight(StrategyId("mean_reversion"), Decimal("0.40")),
            ),
        )

        candidate = allocator.allocate(
            (
                self._signal("trend", SignalSide.BUY, Decimal("0.80")),
                self._signal("mean_reversion", SignalSide.BUY, Decimal("0.50")),
            ),
            evaluated_at=NOW,
            correlation_id="corr_allocator_001",
        )

        self.assertEqual(candidate.side, SignalSide.BUY)
        self.assertEqual(candidate.long_score, Decimal("0.680"))
        self.assertEqual(candidate.short_score, Decimal("0"))
        self.assertEqual(candidate.confidence, Decimal("1"))
        self.assertFalse(candidate.order_intent_allowed)
        self.assertFalse(candidate.execution_allowed)
        self.assertTrue(candidate.signal_candidate_id.startswith("sigcand_"))

    def test_allocator_detects_conflict_and_can_abstain(self) -> None:
        allocator = StrategyPortfolioAllocator(
            StrategyPortfolioAllocationPolicy(
                allocator_id="allocator_local_002",
                min_confidence=Decimal("0.05"),
                conflict_ratio_warning=Decimal("0.20"),
                abstain_on_conflict_ratio=Decimal("0.45"),
            ),
            (
                StrategySignalWeight(StrategyId("trend"), Decimal("0.50")),
                StrategySignalWeight(StrategyId("mean_reversion"), Decimal("0.50")),
            ),
        )

        candidate = allocator.allocate(
            (
                self._signal("trend", SignalSide.BUY, Decimal("0.90")),
                self._signal("mean_reversion", SignalSide.SELL, Decimal("0.90")),
            ),
            evaluated_at=NOW,
            correlation_id="corr_allocator_002",
        )

        self.assertEqual(candidate.side, SignalSide.HOLD)
        self.assertIn("strategy_conflict", candidate.risk_flags)
        self.assertIn("conflict_abstain", candidate.risk_flags)

    def test_allocator_marks_low_confidence_and_ignores_hold_or_unweighted_signals(self) -> None:
        allocator = StrategyPortfolioAllocator(
            StrategyPortfolioAllocationPolicy(allocator_id="allocator_local_003", min_confidence=Decimal("0.75")),
            (
                StrategySignalWeight(StrategyId("trend"), Decimal("1.0")),
                StrategySignalWeight(StrategyId("mean_reversion"), Decimal("1.0")),
            ),
        )

        candidate = allocator.allocate(
            (
                self._signal("trend", SignalSide.BUY, Decimal("0.51")),
                self._signal("mean_reversion", SignalSide.SELL, Decimal("0.49")),
                self._signal("observer", SignalSide.HOLD, Decimal("0.50")),
            ),
            evaluated_at=NOW,
            correlation_id="corr_allocator_003",
        )

        self.assertEqual(candidate.side, SignalSide.HOLD)
        self.assertIn("low_confidence", candidate.risk_flags)
        self.assertIn("ignored_unweighted_or_hold_signals", candidate.risk_flags)

    def test_allocator_is_deterministic(self) -> None:
        allocator = StrategyPortfolioAllocator(
            StrategyPortfolioAllocationPolicy(allocator_id="allocator_local_004"),
            (StrategySignalWeight(StrategyId("trend"), Decimal("1.0")),),
        )
        signals = (self._signal("trend", SignalSide.SELL, Decimal("0.75")),)

        first = allocator.allocate(signals, evaluated_at=NOW, correlation_id="corr_allocator_004")
        second = allocator.allocate(signals, evaluated_at=NOW, correlation_id="corr_allocator_004")

        self.assertEqual(first.signal_candidate_id, second.signal_candidate_id)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_allocator_rejects_mixed_markets_and_empty_actionable_inputs(self) -> None:
        allocator = StrategyPortfolioAllocator(
            StrategyPortfolioAllocationPolicy(allocator_id="allocator_local_005"),
            (StrategySignalWeight(StrategyId("trend"), Decimal("1.0")),),
        )

        with self.assertRaises(StrategyError):
            allocator.allocate(
                (
                    self._signal("trend", SignalSide.BUY, Decimal("0.50"), symbol=BTC),
                    self._signal("trend", SignalSide.BUY, Decimal("0.50"), symbol=Symbol("ETH/USDT")),
                ),
                evaluated_at=NOW,
                correlation_id="corr_allocator_005",
            )

        with self.assertRaises(StrategyError):
            allocator.allocate(
                (self._signal("trend", SignalSide.HOLD, Decimal("0.50")),),
                evaluated_at=NOW,
                correlation_id="corr_allocator_006",
            )

    def test_allocator_exposes_no_execution_methods(self) -> None:
        allocator = StrategyPortfolioAllocator(
            StrategyPortfolioAllocationPolicy(allocator_id="allocator_local_006"),
            (StrategySignalWeight(StrategyId("trend"), Decimal("1.0")),),
        )

        forbidden = {
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

        self.assertTrue(forbidden.isdisjoint(dir(allocator)))

    def _signal(
        self,
        strategy_id: str,
        side: SignalSide,
        strength: Decimal,
        *,
        symbol: Symbol = BTC,
        venue: Venue = PAPER,
    ) -> Signal:
        return Signal.deterministic(
            strategy_id=StrategyId(strategy_id),
            strategy_version=StrategyVersion("1.0.0"),
            symbol=symbol,
            venue=venue,
            side=side,
            strength=SignalStrength(strength),
            generated_at=NOW,
            metadata=SignalMetadata(model_version=f"{strategy_id}:1.0.0", rationale="allocator test"),
        )


if __name__ == "__main__":
    unittest.main()
