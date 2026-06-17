from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, getcontext
from enum import Enum


getcontext().prec = 28


class CognitiveAutonomyError(ValueError):
    """Raised when local cognitive autonomy inputs are invalid."""


class CognitiveHealth(str, Enum):
    STABLE = "stable"
    WATCH = "watch"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class HealingActionType(str, Enum):
    INCREASE_EVIDENCE = "increase_evidence"
    REDUCE_SCOPE = "reduce_scope"
    REQUIRE_HUMAN_REVIEW = "require_human_review"
    PAUSE_AUTONOMY = "pause_autonomy"
    RECALIBRATE_MODEL = "recalibrate_model"


@dataclass(frozen=True)
class AgentJudgment:
    agent_id: str
    hypothesis_id: str
    probability: Decimal
    confidence: Decimal
    evidence_weight: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        _non_empty(self.agent_id, "agent_id")
        _non_empty(self.hypothesis_id, "hypothesis_id")
        _ratio(self.probability, "probability")
        _ratio(self.confidence, "confidence")
        _positive(self.evidence_weight, "evidence_weight")


@dataclass(frozen=True)
class CollectiveConsensus:
    hypothesis_id: str
    consensus_probability: Decimal
    confidence: Decimal
    disagreement: Decimal
    participant_count: int
    health: CognitiveHealth


@dataclass(frozen=True)
class ForecastObservation:
    forecast_id: str
    probability: Decimal
    outcome: bool

    def __post_init__(self) -> None:
        _non_empty(self.forecast_id, "forecast_id")
        _ratio(self.probability, "probability")


@dataclass(frozen=True)
class CalibrationReport:
    sample_count: int
    brier_score: Decimal
    mean_probability: Decimal
    empirical_frequency: Decimal
    calibration_error: Decimal
    health: CognitiveHealth


@dataclass(frozen=True)
class FractalDiagnostics:
    sample_count: int
    directional_change_rate: Decimal
    path_efficiency: Decimal
    roughness: Decimal
    regime_label: str
    health: CognitiveHealth


@dataclass(frozen=True)
class StabilityDiagnostics:
    sample_count: int
    mean_return: Decimal
    mean_abs_return: Decimal
    stress_energy: Decimal
    shock_ratio: Decimal
    health: CognitiveHealth


@dataclass(frozen=True)
class SelfHealingAction:
    action_type: HealingActionType
    reason: str
    priority: int

    def __post_init__(self) -> None:
        _non_empty(self.reason, "reason")
        if self.priority < 1 or self.priority > 5:
            raise CognitiveAutonomyError("priority must be between 1 and 5")


@dataclass(frozen=True)
class CognitiveAutonomyReport:
    consensus: CollectiveConsensus
    calibration: CalibrationReport
    fractal: FractalDiagnostics
    stability: StabilityDiagnostics
    health: CognitiveHealth
    healing_actions: tuple[SelfHealingAction, ...]
    autonomy_allowed: bool = False
    trading_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False


class CognitiveAutonomyEngine:
    """Deterministic local cognition layer.

    The engine performs local analysis only. It does not call LLMs, train neural
    networks, call network, read credentials, edit files, approve risk, or
    approve execution.
    """

    def collective_consensus(self, judgments: tuple[AgentJudgment, ...]) -> CollectiveConsensus:
        if not judgments:
            raise CognitiveAutonomyError("judgments must not be empty")
        hypothesis_ids = {judgment.hypothesis_id for judgment in judgments}
        if len(hypothesis_ids) != 1:
            raise CognitiveAutonomyError("all judgments must refer to the same hypothesis")

        weights = tuple(judgment.confidence * judgment.evidence_weight for judgment in judgments)
        total_weight = sum(weights, Decimal("0"))
        if total_weight <= Decimal("0"):
            raise CognitiveAutonomyError("total judgment weight must be positive")

        consensus_probability = _quantize(
            sum((judgment.probability * weight for judgment, weight in zip(judgments, weights)), Decimal("0"))
            / total_weight
        )
        disagreement = _quantize(
            sum((abs(judgment.probability - consensus_probability) for judgment in judgments), Decimal("0"))
            / Decimal(len(judgments))
        )
        confidence = _quantize(
            min(Decimal("1"), (sum((judgment.confidence for judgment in judgments), Decimal("0")) / Decimal(len(judgments))) * (Decimal("1") - disagreement))
        )

        return CollectiveConsensus(
            hypothesis_id=judgments[0].hypothesis_id,
            consensus_probability=consensus_probability,
            confidence=confidence,
            disagreement=disagreement,
            participant_count=len(judgments),
            health=_consensus_health(disagreement, confidence),
        )

    def calibration_report(self, observations: tuple[ForecastObservation, ...]) -> CalibrationReport:
        if not observations:
            raise CognitiveAutonomyError("observations must not be empty")
        sample_count = len(observations)
        outcomes = tuple(Decimal("1") if item.outcome else Decimal("0") for item in observations)
        brier = _quantize(
            sum(((item.probability - outcome) ** 2 for item, outcome in zip(observations, outcomes)), Decimal("0"))
            / Decimal(sample_count)
        )
        mean_probability = _quantize(sum((item.probability for item in observations), Decimal("0")) / Decimal(sample_count))
        empirical_frequency = _quantize(sum(outcomes, Decimal("0")) / Decimal(sample_count))
        calibration_error = _quantize(abs(mean_probability - empirical_frequency))

        return CalibrationReport(
            sample_count=sample_count,
            brier_score=brier,
            mean_probability=mean_probability,
            empirical_frequency=empirical_frequency,
            calibration_error=calibration_error,
            health=_calibration_health(calibration_error, sample_count),
        )

    def fractal_diagnostics(self, prices: tuple[Decimal, ...]) -> FractalDiagnostics:
        if len(prices) < 3:
            raise CognitiveAutonomyError("at least three prices are required")
        for price in prices:
            _positive(price, "price")

        returns = _differences(prices)
        direction_changes = Decimal(
            sum(
                1
                for previous, current in zip(returns, returns[1:])
                if previous != Decimal("0") and current != Decimal("0") and (previous > 0) != (current > 0)
            )
        )
        possible_changes = Decimal(max(1, len(returns) - 1))
        directional_change_rate = _quantize(direction_changes / possible_changes)
        net_move = abs(prices[-1] - prices[0])
        path_length = sum((abs(item) for item in returns), Decimal("0"))
        path_efficiency = _quantize(Decimal("1") if path_length == 0 else net_move / path_length)
        roughness = _quantize(Decimal("1") - path_efficiency)

        return FractalDiagnostics(
            sample_count=len(prices),
            directional_change_rate=directional_change_rate,
            path_efficiency=path_efficiency,
            roughness=roughness,
            regime_label=_regime_label(roughness, directional_change_rate),
            health=_fractal_health(roughness, directional_change_rate),
        )

    def stability_diagnostics(self, prices: tuple[Decimal, ...]) -> StabilityDiagnostics:
        if len(prices) < 3:
            raise CognitiveAutonomyError("at least three prices are required")
        returns = tuple((current - previous) / previous for previous, current in zip(prices, prices[1:]))
        sample_count = len(returns)
        mean_return = _quantize(sum(returns, Decimal("0")) / Decimal(sample_count))
        abs_returns = tuple(abs(item) for item in returns)
        mean_abs_return = _quantize(sum(abs_returns, Decimal("0")) / Decimal(sample_count))
        stress_energy = _quantize(sum((item * item for item in returns), Decimal("0")) / Decimal(sample_count))
        shocks = sum(1 for item in abs_returns if item > (mean_abs_return * Decimal("2")))
        shock_ratio = _quantize(Decimal(shocks) / Decimal(sample_count))

        return StabilityDiagnostics(
            sample_count=sample_count,
            mean_return=mean_return,
            mean_abs_return=mean_abs_return,
            stress_energy=stress_energy,
            shock_ratio=shock_ratio,
            health=_stability_health(stress_energy, shock_ratio),
        )

    def analyze(
        self,
        *,
        judgments: tuple[AgentJudgment, ...],
        observations: tuple[ForecastObservation, ...],
        prices: tuple[Decimal, ...],
    ) -> CognitiveAutonomyReport:
        consensus = self.collective_consensus(judgments)
        calibration = self.calibration_report(observations)
        fractal = self.fractal_diagnostics(prices)
        stability = self.stability_diagnostics(prices)
        health = _overall_health((consensus.health, calibration.health, fractal.health, stability.health))
        healing_actions = self_healing_actions(consensus, calibration, fractal, stability, health)

        return CognitiveAutonomyReport(
            consensus=consensus,
            calibration=calibration,
            fractal=fractal,
            stability=stability,
            health=health,
            healing_actions=healing_actions,
            autonomy_allowed=False,
            trading_allowed=False,
            network_allowed=False,
            credentials_allowed=False,
        )


def self_healing_actions(
    consensus: CollectiveConsensus,
    calibration: CalibrationReport,
    fractal: FractalDiagnostics,
    stability: StabilityDiagnostics,
    health: CognitiveHealth,
) -> tuple[SelfHealingAction, ...]:
    actions: list[SelfHealingAction] = []
    if consensus.health in {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED}:
        actions.append(SelfHealingAction(HealingActionType.INCREASE_EVIDENCE, "collective disagreement is too high", 2))
    if calibration.health in {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED}:
        actions.append(SelfHealingAction(HealingActionType.RECALIBRATE_MODEL, "forecast calibration is outside tolerance", 1))
    if fractal.health is CognitiveHealth.DEGRADED:
        actions.append(SelfHealingAction(HealingActionType.REDUCE_SCOPE, "market path roughness is elevated", 3))
    if stability.health in {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED}:
        actions.append(SelfHealingAction(HealingActionType.PAUSE_AUTONOMY, "stability diagnostics indicate stress", 1))
    if health is not CognitiveHealth.STABLE:
        actions.append(SelfHealingAction(HealingActionType.REQUIRE_HUMAN_REVIEW, "cognitive health is not stable", 1))
    return tuple(sorted(actions, key=lambda item: (item.priority, item.action_type.value)))


def _differences(values: tuple[Decimal, ...]) -> tuple[Decimal, ...]:
    return tuple(current - previous for previous, current in zip(values, values[1:]))


def _consensus_health(disagreement: Decimal, confidence: Decimal) -> CognitiveHealth:
    if disagreement >= Decimal("0.35") or confidence < Decimal("0.30"):
        return CognitiveHealth.BLOCKED
    if disagreement >= Decimal("0.20") or confidence < Decimal("0.50"):
        return CognitiveHealth.DEGRADED
    if disagreement >= Decimal("0.10") or confidence < Decimal("0.70"):
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _calibration_health(calibration_error: Decimal, sample_count: int) -> CognitiveHealth:
    if sample_count < 5:
        return CognitiveHealth.WATCH
    if calibration_error >= Decimal("0.25"):
        return CognitiveHealth.BLOCKED
    if calibration_error >= Decimal("0.15"):
        return CognitiveHealth.DEGRADED
    if calibration_error >= Decimal("0.08"):
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _fractal_health(roughness: Decimal, directional_change_rate: Decimal) -> CognitiveHealth:
    if roughness >= Decimal("0.80") and directional_change_rate >= Decimal("0.70"):
        return CognitiveHealth.DEGRADED
    if roughness >= Decimal("0.65") or directional_change_rate >= Decimal("0.60"):
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _stability_health(stress_energy: Decimal, shock_ratio: Decimal) -> CognitiveHealth:
    if stress_energy >= Decimal("0.010") or shock_ratio >= Decimal("0.35"):
        return CognitiveHealth.BLOCKED
    if stress_energy >= Decimal("0.0025") or shock_ratio >= Decimal("0.20"):
        return CognitiveHealth.DEGRADED
    if stress_energy >= Decimal("0.0010") or shock_ratio >= Decimal("0.10"):
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _overall_health(states: tuple[CognitiveHealth, ...]) -> CognitiveHealth:
    if CognitiveHealth.BLOCKED in states:
        return CognitiveHealth.BLOCKED
    if CognitiveHealth.DEGRADED in states:
        return CognitiveHealth.DEGRADED
    if CognitiveHealth.WATCH in states:
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _regime_label(roughness: Decimal, directional_change_rate: Decimal) -> str:
    if roughness < Decimal("0.35") and directional_change_rate < Decimal("0.35"):
        return "persistent_trend"
    if roughness > Decimal("0.70") and directional_change_rate > Decimal("0.55"):
        return "choppy_mean_reverting"
    return "mixed_transition"


def _ratio(value: Decimal, field_name: str) -> None:
    if not isinstance(value, Decimal):
        raise CognitiveAutonomyError(f"{field_name} must be Decimal")
    if value < Decimal("0") or value > Decimal("1"):
        raise CognitiveAutonomyError(f"{field_name} must be between 0 and 1")


def _positive(value: Decimal, field_name: str) -> None:
    if not isinstance(value, Decimal):
        raise CognitiveAutonomyError(f"{field_name} must be Decimal")
    if value <= Decimal("0"):
        raise CognitiveAutonomyError(f"{field_name} must be positive")


def _non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise CognitiveAutonomyError(f"{field_name} must be a non-empty string")


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def build_default_cognitive_autonomy_engine() -> CognitiveAutonomyEngine:
    return CognitiveAutonomyEngine()
