from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from packages.domain import Signal, SignalSide, StrategyId, Symbol, Venue
from packages.domain.base import (
    SerializableModel,
    deterministic_id,
    require_aware_datetime,
    require_non_empty,
    require_positive,
    require_ratio,
)

from .base import PROHIBITED_STRATEGY_METHOD_NAMES, StrategyError


@dataclass(frozen=True)
class StrategySignalWeight:
    strategy_id: StrategyId
    weight: Decimal
    enabled: bool = True

    def __post_init__(self) -> None:
        require_positive(self.weight, "weight")


@dataclass(frozen=True)
class StrategyPortfolioAllocationPolicy:
    allocator_id: str
    min_confidence: Decimal = Decimal("0.05")
    conflict_ratio_warning: Decimal = Decimal("0.25")
    abstain_on_conflict_ratio: Decimal = Decimal("0.50")

    def __post_init__(self) -> None:
        require_non_empty(self.allocator_id, "allocator_id")
        require_ratio(self.min_confidence, "min_confidence")
        require_ratio(self.conflict_ratio_warning, "conflict_ratio_warning")
        require_ratio(self.abstain_on_conflict_ratio, "abstain_on_conflict_ratio")
        if self.conflict_ratio_warning > self.abstain_on_conflict_ratio:
            raise StrategyError("conflict_ratio_warning must be <= abstain_on_conflict_ratio")


@dataclass(frozen=True)
class AllocatedSignalCandidate(SerializableModel):
    signal_candidate_id: str
    allocator_id: str
    symbol: Symbol
    venue: Venue
    side: SignalSide
    confidence: Decimal
    net_score: Decimal
    long_score: Decimal
    short_score: Decimal
    conflict_ratio: Decimal
    contributing_signal_ids: tuple[str, ...]
    risk_flags: tuple[str, ...]
    generated_at: datetime
    correlation_id: str
    rationale: str
    order_intent_allowed: bool = False
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.signal_candidate_id, "signal_candidate_id")
        require_non_empty(self.allocator_id, "allocator_id")
        require_ratio(self.confidence, "confidence")
        require_positive(self.long_score + self.short_score, "gross_signal_score")
        require_ratio(self.conflict_ratio, "conflict_ratio")
        require_aware_datetime(self.generated_at, "generated_at")
        require_non_empty(self.correlation_id, "correlation_id")
        require_non_empty(self.rationale, "rationale")
        if not self.contributing_signal_ids:
            raise StrategyError("allocated signal candidate requires contributing signals")
        if self.order_intent_allowed:
            raise StrategyError("allocated signal candidate must not allow OrderIntent creation")
        if self.execution_allowed:
            raise StrategyError("allocated signal candidate must not allow execution")


class StrategyPortfolioAllocator:
    """Aggregates local strategy signals into one non-executable candidate."""

    def __init__(self, policy: StrategyPortfolioAllocationPolicy, weights: tuple[StrategySignalWeight, ...]) -> None:
        self.policy = policy
        self._weights = {weight.strategy_id.value: weight for weight in weights if weight.enabled}
        if not self._weights:
            raise StrategyError("strategy portfolio allocator requires at least one enabled strategy weight")
        validate_allocator_surface(self)

    def allocate(
        self,
        signals: tuple[Signal, ...],
        *,
        evaluated_at: datetime,
        correlation_id: str,
    ) -> AllocatedSignalCandidate:
        require_aware_datetime(evaluated_at, "evaluated_at")
        require_non_empty(correlation_id, "correlation_id")
        if not signals:
            raise StrategyError("allocator requires at least one signal")

        symbol, venue = _require_single_market(signals)
        long_score = Decimal("0")
        short_score = Decimal("0")
        ignored = 0
        contributing: list[str] = []

        for signal in signals:
            weight = self._weights.get(signal.strategy_id.value)
            if weight is None:
                ignored += 1
                continue
            strength = signal.strength.value
            contribution = weight.weight * strength
            if signal.side is SignalSide.BUY:
                long_score += contribution
                contributing.append(signal.signal_id)
            elif signal.side is SignalSide.SELL:
                short_score += contribution
                contributing.append(signal.signal_id)
            else:
                ignored += 1

        gross = long_score + short_score
        if gross <= Decimal("0"):
            raise StrategyError("allocator received no actionable weighted BUY/SELL signals")

        net_score = long_score - short_score
        confidence = min(abs(net_score) / gross, Decimal("1"))
        conflict_ratio = min(long_score, short_score) / gross
        risk_flags = _risk_flags(
            ignored=ignored,
            conflict_ratio=conflict_ratio,
            confidence=confidence,
            policy=self.policy,
        )
        side = _allocated_side(
            net_score=net_score,
            confidence=confidence,
            conflict_ratio=conflict_ratio,
            policy=self.policy,
        )
        rationale = (
            f"local_strategy_portfolio_allocation side={side.value} "
            f"confidence={confidence} conflict_ratio={conflict_ratio}"
        )
        signal_candidate_id = deterministic_id(
            "sigcand",
            self.policy.allocator_id,
            symbol.value,
            venue.value,
            side.value,
            str(net_score),
            evaluated_at.isoformat(),
            correlation_id,
        )
        return AllocatedSignalCandidate(
            signal_candidate_id=signal_candidate_id,
            allocator_id=self.policy.allocator_id,
            symbol=symbol,
            venue=venue,
            side=side,
            confidence=confidence,
            net_score=net_score,
            long_score=long_score,
            short_score=short_score,
            conflict_ratio=conflict_ratio,
            contributing_signal_ids=tuple(contributing),
            risk_flags=tuple(risk_flags),
            generated_at=evaluated_at,
            correlation_id=correlation_id,
            rationale=rationale,
            order_intent_allowed=False,
            execution_allowed=False,
        )


def _require_single_market(signals: tuple[Signal, ...]) -> tuple[Symbol, Venue]:
    symbol = signals[0].symbol
    venue = signals[0].venue
    for signal in signals:
        if signal.symbol != symbol or signal.venue != venue:
            raise StrategyError("allocator requires all signals to target one symbol and venue")
    return symbol, venue


def _risk_flags(
    *,
    ignored: int,
    conflict_ratio: Decimal,
    confidence: Decimal,
    policy: StrategyPortfolioAllocationPolicy,
) -> list[str]:
    flags: list[str] = []
    if ignored:
        flags.append("ignored_unweighted_or_hold_signals")
    if conflict_ratio >= policy.conflict_ratio_warning:
        flags.append("strategy_conflict")
    if confidence < policy.min_confidence:
        flags.append("low_confidence")
    if conflict_ratio >= policy.abstain_on_conflict_ratio:
        flags.append("conflict_abstain")
    return flags


def _allocated_side(
    *,
    net_score: Decimal,
    confidence: Decimal,
    conflict_ratio: Decimal,
    policy: StrategyPortfolioAllocationPolicy,
) -> SignalSide:
    if confidence < policy.min_confidence or conflict_ratio >= policy.abstain_on_conflict_ratio:
        return SignalSide.HOLD
    if net_score > Decimal("0"):
        return SignalSide.BUY
    if net_score < Decimal("0"):
        return SignalSide.SELL
    return SignalSide.HOLD


def validate_allocator_surface(allocator: object) -> None:
    exposed = set(dir(allocator))
    prohibited = sorted(exposed.intersection(PROHIBITED_STRATEGY_METHOD_NAMES))
    if prohibited:
        raise StrategyError(f"allocator exposes prohibited execution-like methods: {', '.join(prohibited)}")
