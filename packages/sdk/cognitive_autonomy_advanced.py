from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP, getcontext

from .cognitive_autonomy import (
    AgentJudgment,
    CognitiveAutonomyEngine,
    CognitiveAutonomyError,
    CognitiveAutonomyReport,
    CognitiveHealth,
    ForecastObservation,
    HealingActionType,
    SelfHealingAction,
)


getcontext().prec = 28


@dataclass(frozen=True)
class NeuralActivationSnapshot:
    """Local-only neural state summary.

    This is not a neural-network runtime. It is a deterministic diagnostic
    envelope for model or agent activation-like values produced elsewhere.
    """

    snapshot_id: str
    activations: tuple[Decimal, ...]
    baseline: tuple[Decimal, ...] = ()
    uncertainty: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        _non_empty(self.snapshot_id, "snapshot_id")
        if not self.activations:
            raise CognitiveAutonomyError("activations must not be empty")
        for activation in self.activations:
            _ratio(activation, "activation")
        if self.baseline and len(self.baseline) != len(self.activations):
            raise CognitiveAutonomyError("baseline must match activation length")
        for baseline_value in self.baseline:
            _ratio(baseline_value, "baseline")
        _ratio(self.uncertainty, "uncertainty")


@dataclass(frozen=True)
class NeuralStabilityDiagnostics:
    sample_count: int
    activation_mean: Decimal
    activation_concentration: Decimal
    entropy_proxy: Decimal
    saturation_ratio: Decimal
    drift: Decimal
    uncertainty: Decimal
    health: CognitiveHealth


@dataclass(frozen=True)
class CollectiveIntelligenceDiagnostics:
    participant_count: int
    evidence_concentration: Decimal
    dissent_ratio: Decimal
    consensus_confidence: Decimal
    collective_resilience: Decimal
    health: CognitiveHealth


@dataclass(frozen=True)
class ReliabilityBucket:
    lower_bound: Decimal
    upper_bound: Decimal
    forecast_count: int
    mean_probability: Decimal
    empirical_frequency: Decimal
    calibration_error: Decimal


@dataclass(frozen=True)
class ReliabilityDiagram:
    bucket_count: int
    sample_count: int
    buckets: tuple[ReliabilityBucket, ...]
    expected_calibration_error: Decimal
    max_calibration_error: Decimal
    health: CognitiveHealth


@dataclass(frozen=True)
class PhysicsDiagnostics:
    sample_count: int
    mean_velocity: Decimal
    mean_abs_velocity: Decimal
    volatility_proxy: Decimal
    kinetic_energy: Decimal
    stress_potential: Decimal
    directional_entropy_proxy: Decimal
    health: CognitiveHealth


@dataclass(frozen=True)
class ScientificValidityReport:
    judgment_count: int
    forecast_observation_count: int
    price_sample_count: int
    evidence_floor_met: bool
    falsifiable: bool
    overfit_warning: bool
    health: CognitiveHealth


@dataclass(frozen=True)
class AdvancedSelfHealingPlan:
    health: CognitiveHealth
    actions: tuple[SelfHealingAction, ...]
    evidence_required: tuple[str, ...]
    remediation_allowed: bool = False
    runtime_change_allowed: bool = False
    trading_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False


@dataclass(frozen=True)
class AdvancedCognitiveAutonomyReport:
    base_report: CognitiveAutonomyReport
    collective_intelligence: CollectiveIntelligenceDiagnostics
    neural_stability: NeuralStabilityDiagnostics
    reliability: ReliabilityDiagram
    physics: PhysicsDiagnostics
    scientific_validity: ScientificValidityReport
    self_healing_plan: AdvancedSelfHealingPlan
    health: CognitiveHealth
    autonomy_allowed: bool = False
    runtime_change_allowed: bool = False
    trading_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False


class AdvancedCognitiveAutonomyEngine:
    """Deterministic advanced cognition layer.

    The engine is local diagnostics only. It does not train models, call LLMs,
    call network, read credentials, edit files, approve risk, approve execution,
    create orders, or enable runtime changes.
    """

    def __init__(self, base_engine: CognitiveAutonomyEngine | None = None) -> None:
        self._base = base_engine or CognitiveAutonomyEngine()

    def collective_intelligence_diagnostics(
        self,
        judgments: tuple[AgentJudgment, ...],
    ) -> CollectiveIntelligenceDiagnostics:
        consensus = self._base.collective_consensus(judgments)
        weights = tuple(judgment.confidence * judgment.evidence_weight for judgment in judgments)
        total_weight = sum(weights, Decimal("0"))
        if total_weight <= Decimal("0"):
            raise CognitiveAutonomyError("total judgment weight must be positive")
        normalized_weights = tuple(weight / total_weight for weight in weights)
        evidence_concentration = _quantize(sum((weight * weight for weight in normalized_weights), Decimal("0")))
        dissent_count = sum(
            1
            for judgment in judgments
            if abs(judgment.probability - consensus.consensus_probability) >= Decimal("0.20")
        )
        dissent_ratio = _quantize(Decimal(dissent_count) / Decimal(len(judgments)))
        collective_resilience = _quantize(
            max(Decimal("0"), Decimal("1") - evidence_concentration - dissent_ratio + consensus.confidence)
            / Decimal("2")
        )

        return CollectiveIntelligenceDiagnostics(
            participant_count=len(judgments),
            evidence_concentration=evidence_concentration,
            dissent_ratio=dissent_ratio,
            consensus_confidence=consensus.confidence,
            collective_resilience=collective_resilience,
            health=_collective_health(evidence_concentration, dissent_ratio, consensus.confidence),
        )

    def neural_stability_diagnostics(self, snapshot: NeuralActivationSnapshot) -> NeuralStabilityDiagnostics:
        sample_count = len(snapshot.activations)
        activation_mean = _quantize(sum(snapshot.activations, Decimal("0")) / Decimal(sample_count))
        normalized_total = sum(snapshot.activations, Decimal("0"))
        if normalized_total == Decimal("0"):
            activation_concentration = Decimal("1.000000")
        else:
            normalized = tuple(value / normalized_total for value in snapshot.activations)
            activation_concentration = _quantize(sum((value * value for value in normalized), Decimal("0")))
        entropy_proxy = _quantize(max(Decimal("0"), Decimal("1") - activation_concentration))
        saturation_count = sum(
            1 for value in snapshot.activations if value <= Decimal("0.05") or value >= Decimal("0.95")
        )
        saturation_ratio = _quantize(Decimal(saturation_count) / Decimal(sample_count))
        if snapshot.baseline:
            drift = _quantize(
                sum(
                    (abs(current - baseline) for current, baseline in zip(snapshot.activations, snapshot.baseline)),
                    Decimal("0"),
                )
                / Decimal(sample_count)
            )
        else:
            drift = Decimal("0.000000")

        return NeuralStabilityDiagnostics(
            sample_count=sample_count,
            activation_mean=activation_mean,
            activation_concentration=activation_concentration,
            entropy_proxy=entropy_proxy,
            saturation_ratio=saturation_ratio,
            drift=drift,
            uncertainty=_quantize(snapshot.uncertainty),
            health=_neural_health(drift, saturation_ratio, snapshot.uncertainty, activation_concentration),
        )

    def reliability_diagram(
        self,
        observations: tuple[ForecastObservation, ...],
        *,
        bucket_count: int = 5,
    ) -> ReliabilityDiagram:
        if not observations:
            raise CognitiveAutonomyError("observations must not be empty")
        if bucket_count < 2 or bucket_count > 20:
            raise CognitiveAutonomyError("bucket_count must be between 2 and 20")

        grouped: list[list[ForecastObservation]] = [[] for _ in range(bucket_count)]
        for observation in observations:
            raw_index = int((observation.probability * Decimal(bucket_count)).to_integral_value(rounding=ROUND_FLOOR))
            index = min(bucket_count - 1, max(0, raw_index))
            grouped[index].append(observation)

        buckets: list[ReliabilityBucket] = []
        weighted_error = Decimal("0")
        max_error = Decimal("0")
        total = Decimal(len(observations))
        for index, bucket_items in enumerate(grouped):
            lower_bound = _quantize(Decimal(index) / Decimal(bucket_count))
            upper_bound = _quantize(Decimal(index + 1) / Decimal(bucket_count))
            if not bucket_items:
                bucket = ReliabilityBucket(
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    forecast_count=0,
                    mean_probability=Decimal("0.000000"),
                    empirical_frequency=Decimal("0.000000"),
                    calibration_error=Decimal("0.000000"),
                )
            else:
                count = Decimal(len(bucket_items))
                mean_probability = _quantize(
                    sum((item.probability for item in bucket_items), Decimal("0")) / count
                )
                empirical_frequency = _quantize(
                    sum((Decimal("1") if item.outcome else Decimal("0") for item in bucket_items), Decimal("0"))
                    / count
                )
                calibration_error = _quantize(abs(mean_probability - empirical_frequency))
                weighted_error += calibration_error * count
                max_error = max(max_error, calibration_error)
                bucket = ReliabilityBucket(
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    forecast_count=len(bucket_items),
                    mean_probability=mean_probability,
                    empirical_frequency=empirical_frequency,
                    calibration_error=calibration_error,
                )
            buckets.append(bucket)

        expected_calibration_error = _quantize(weighted_error / total)
        max_calibration_error = _quantize(max_error)

        return ReliabilityDiagram(
            bucket_count=bucket_count,
            sample_count=len(observations),
            buckets=tuple(buckets),
            expected_calibration_error=expected_calibration_error,
            max_calibration_error=max_calibration_error,
            health=_reliability_health(expected_calibration_error, max_calibration_error, len(observations)),
        )

    def physics_diagnostics(self, prices: tuple[Decimal, ...]) -> PhysicsDiagnostics:
        if len(prices) < 3:
            raise CognitiveAutonomyError("at least three prices are required")
        for price in prices:
            _positive(price, "price")
        velocities = tuple((current - previous) / previous for previous, current in zip(prices, prices[1:]))
        sample_count = len(velocities)
        mean_velocity = _quantize(sum(velocities, Decimal("0")) / Decimal(sample_count))
        abs_velocities = tuple(abs(item) for item in velocities)
        mean_abs_velocity = _quantize(sum(abs_velocities, Decimal("0")) / Decimal(sample_count))
        variance = (
            sum(((item - mean_velocity) * (item - mean_velocity) for item in velocities), Decimal("0"))
            / Decimal(sample_count)
        )
        volatility_proxy = _quantize(variance)
        kinetic_energy = _quantize(sum((item * item for item in velocities), Decimal("0")) / Decimal(sample_count))
        max_abs_velocity = max(abs_velocities)
        stress_potential = _quantize(
            Decimal("0") if mean_abs_velocity == Decimal("0") else max_abs_velocity / mean_abs_velocity
        )
        sign_changes = Decimal(
            sum(
                1
                for previous, current in zip(velocities, velocities[1:])
                if previous != Decimal("0") and current != Decimal("0") and (previous > 0) != (current > 0)
            )
        )
        directional_entropy_proxy = _quantize(sign_changes / Decimal(max(1, sample_count - 1)))

        return PhysicsDiagnostics(
            sample_count=sample_count,
            mean_velocity=mean_velocity,
            mean_abs_velocity=mean_abs_velocity,
            volatility_proxy=volatility_proxy,
            kinetic_energy=kinetic_energy,
            stress_potential=stress_potential,
            directional_entropy_proxy=directional_entropy_proxy,
            health=_physics_health(kinetic_energy, stress_potential, directional_entropy_proxy),
        )

    def scientific_validity_report(
        self,
        *,
        judgments: tuple[AgentJudgment, ...],
        observations: tuple[ForecastObservation, ...],
        prices: tuple[Decimal, ...],
    ) -> ScientificValidityReport:
        if not judgments:
            raise CognitiveAutonomyError("judgments must not be empty")
        if not observations:
            raise CognitiveAutonomyError("observations must not be empty")
        if len(prices) < 3:
            raise CognitiveAutonomyError("at least three prices are required")

        evidence_floor_met = len(judgments) >= 3 and len(observations) >= 10 and len(prices) >= 10
        falsifiable = all(item.probability > Decimal("0") and item.probability < Decimal("1") for item in observations)
        overfit_warning = len(observations) < 30 or len(prices) < 30

        return ScientificValidityReport(
            judgment_count=len(judgments),
            forecast_observation_count=len(observations),
            price_sample_count=len(prices),
            evidence_floor_met=evidence_floor_met,
            falsifiable=falsifiable,
            overfit_warning=overfit_warning,
            health=_scientific_health(evidence_floor_met, falsifiable, overfit_warning),
        )

    def advanced_self_healing_plan(
        self,
        *,
        base_report: CognitiveAutonomyReport,
        collective: CollectiveIntelligenceDiagnostics,
        neural: NeuralStabilityDiagnostics,
        reliability: ReliabilityDiagram,
        physics: PhysicsDiagnostics,
        science: ScientificValidityReport,
    ) -> AdvancedSelfHealingPlan:
        health = _overall_health(
            (
                base_report.health,
                collective.health,
                neural.health,
                reliability.health,
                physics.health,
                science.health,
            )
        )
        actions = list(base_report.healing_actions)
        if collective.health in {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED}:
            actions.append(SelfHealingAction(HealingActionType.INCREASE_EVIDENCE, "collective resilience is weak", 2))
        if neural.health in {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED}:
            actions.append(SelfHealingAction(HealingActionType.PAUSE_AUTONOMY, "neural diagnostics are unstable", 1))
        if reliability.health in {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED}:
            actions.append(SelfHealingAction(HealingActionType.RECALIBRATE_MODEL, "reliability buckets show drift", 1))
        if physics.health in {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED}:
            actions.append(SelfHealingAction(HealingActionType.REDUCE_SCOPE, "physics stress diagnostics are elevated", 2))
        if science.health is not CognitiveHealth.STABLE:
            actions.append(SelfHealingAction(HealingActionType.REQUIRE_HUMAN_REVIEW, "scientific validity gate is not stable", 1))

        unique_actions = tuple(sorted({(item.action_type, item.reason): item for item in actions}.values(), key=lambda item: (item.priority, item.action_type.value, item.reason)))
        evidence_required = _evidence_requirements(health)

        return AdvancedSelfHealingPlan(
            health=health,
            actions=unique_actions,
            evidence_required=evidence_required,
            remediation_allowed=False,
            runtime_change_allowed=False,
            trading_allowed=False,
            network_allowed=False,
            credentials_allowed=False,
        )

    def analyze(
        self,
        *,
        judgments: tuple[AgentJudgment, ...],
        observations: tuple[ForecastObservation, ...],
        prices: tuple[Decimal, ...],
        neural_snapshot: NeuralActivationSnapshot,
    ) -> AdvancedCognitiveAutonomyReport:
        base_report = self._base.analyze(judgments=judgments, observations=observations, prices=prices)
        collective = self.collective_intelligence_diagnostics(judgments)
        neural = self.neural_stability_diagnostics(neural_snapshot)
        reliability = self.reliability_diagram(observations)
        physics = self.physics_diagnostics(prices)
        science = self.scientific_validity_report(judgments=judgments, observations=observations, prices=prices)
        plan = self.advanced_self_healing_plan(
            base_report=base_report,
            collective=collective,
            neural=neural,
            reliability=reliability,
            physics=physics,
            science=science,
        )

        return AdvancedCognitiveAutonomyReport(
            base_report=base_report,
            collective_intelligence=collective,
            neural_stability=neural,
            reliability=reliability,
            physics=physics,
            scientific_validity=science,
            self_healing_plan=plan,
            health=plan.health,
            autonomy_allowed=False,
            runtime_change_allowed=False,
            trading_allowed=False,
            network_allowed=False,
            credentials_allowed=False,
        )


def build_default_advanced_cognitive_autonomy_engine() -> AdvancedCognitiveAutonomyEngine:
    return AdvancedCognitiveAutonomyEngine()


def _collective_health(
    evidence_concentration: Decimal,
    dissent_ratio: Decimal,
    confidence: Decimal,
) -> CognitiveHealth:
    if evidence_concentration >= Decimal("0.70") or dissent_ratio >= Decimal("0.50") or confidence < Decimal("0.30"):
        return CognitiveHealth.BLOCKED
    if evidence_concentration >= Decimal("0.55") or dissent_ratio >= Decimal("0.35") or confidence < Decimal("0.50"):
        return CognitiveHealth.DEGRADED
    if evidence_concentration >= Decimal("0.45") or dissent_ratio >= Decimal("0.20") or confidence < Decimal("0.70"):
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _neural_health(
    drift: Decimal,
    saturation_ratio: Decimal,
    uncertainty: Decimal,
    activation_concentration: Decimal,
) -> CognitiveHealth:
    if (
        drift >= Decimal("0.35")
        or saturation_ratio >= Decimal("0.60")
        or uncertainty >= Decimal("0.70")
        or activation_concentration >= Decimal("0.85")
    ):
        return CognitiveHealth.BLOCKED
    if (
        drift >= Decimal("0.25")
        or saturation_ratio >= Decimal("0.40")
        or uncertainty >= Decimal("0.50")
        or activation_concentration >= Decimal("0.70")
    ):
        return CognitiveHealth.DEGRADED
    if (
        drift >= Decimal("0.15")
        or saturation_ratio >= Decimal("0.20")
        or uncertainty >= Decimal("0.30")
        or activation_concentration >= Decimal("0.55")
    ):
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _reliability_health(
    expected_calibration_error: Decimal,
    max_calibration_error: Decimal,
    sample_count: int,
) -> CognitiveHealth:
    if sample_count < 5:
        return CognitiveHealth.WATCH
    if expected_calibration_error >= Decimal("0.25") or max_calibration_error >= Decimal("0.50"):
        return CognitiveHealth.BLOCKED
    if expected_calibration_error >= Decimal("0.15") or max_calibration_error >= Decimal("0.35"):
        return CognitiveHealth.DEGRADED
    if expected_calibration_error >= Decimal("0.08") or max_calibration_error >= Decimal("0.20"):
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _physics_health(
    kinetic_energy: Decimal,
    stress_potential: Decimal,
    directional_entropy_proxy: Decimal,
) -> CognitiveHealth:
    if kinetic_energy >= Decimal("0.010") or stress_potential >= Decimal("3.0"):
        return CognitiveHealth.BLOCKED
    if kinetic_energy >= Decimal("0.0025") or stress_potential >= Decimal("2.2"):
        return CognitiveHealth.DEGRADED
    if kinetic_energy >= Decimal("0.0010") or directional_entropy_proxy >= Decimal("0.70"):
        return CognitiveHealth.WATCH
    return CognitiveHealth.STABLE


def _scientific_health(
    evidence_floor_met: bool,
    falsifiable: bool,
    overfit_warning: bool,
) -> CognitiveHealth:
    if not falsifiable:
        return CognitiveHealth.BLOCKED
    if not evidence_floor_met:
        return CognitiveHealth.DEGRADED
    if overfit_warning:
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


def _evidence_requirements(health: CognitiveHealth) -> tuple[str, ...]:
    base = (
        "calibration_window",
        "collective_dissent_review",
        "lineage_reference",
        "loop_engineering_evidence_record",
    )
    if health is CognitiveHealth.STABLE:
        return ("routine_audit_sample",)
    if health is CognitiveHealth.WATCH:
        return base[:2]
    if health is CognitiveHealth.DEGRADED:
        return base
    return base + ("human_approval_record", "rollback_plan")


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
