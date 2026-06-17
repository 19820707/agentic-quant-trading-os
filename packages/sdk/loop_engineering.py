from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path

from observability import EvidenceJournalEntry, LocalEvidenceJournal
from packages.sdk.autonomous_sprint_manager import (
    AutonomousSprintManager,
    CapabilityState,
    MissionCandidate,
    ProductModel,
    SprintPlan,
    build_default_sprint_manager,
)
from packages.sdk.cognitive_autonomy import (
    AgentJudgment,
    CognitiveAutonomyEngine,
    CognitiveAutonomyReport,
    CognitiveHealth,
    ForecastObservation,
    build_default_cognitive_autonomy_engine,
)
from packages.sdk.cognitive_autonomy_advanced import (
    AdvancedCognitiveAutonomyEngine,
    AdvancedCognitiveAutonomyReport,
    NeuralActivationSnapshot,
    build_default_advanced_cognitive_autonomy_engine,
)
from packages.sdk.persistence_discipline import (
    PersistenceDecision,
    PersistenceDisciplineEngine,
    PersistenceDisciplineReport,
    PersistenceIteration,
    build_default_persistence_discipline_engine,
)


class LoopEngineeringError(ValueError):
    """Raised when a local engineering loop input is unsafe or inconsistent."""


class LoopSignalCategory(str, Enum):
    CI = "ci"
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    RELIABILITY = "reliability"
    RESEARCH = "research"
    TRADING_BOUNDARY = "trading_boundary"


class LoopDecision(str, Enum):
    CONTINUE = "continue"
    REDUCE_SCOPE = "reduce_scope"
    REQUIRE_HUMAN_REVIEW = "require_human_review"
    BLOCK = "block"


class LoopPhase(str, Enum):
    OBSERVE = "observe"
    DIAGNOSE = "diagnose"
    PLAN = "plan"
    POLICY_VERIFY = "policy_verify"
    EVIDENCE = "evidence"
    REVIEW = "review"


@dataclass(frozen=True)
class LoopSignal:
    signal_id: str
    category: LoopSignalCategory
    severity: int
    summary: str
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _non_empty(self.signal_id, "signal_id")
        _non_empty(self.summary, "summary")
        if self.severity < 1 or self.severity > 5:
            raise LoopEngineeringError("signal severity must be between 1 and 5")


@dataclass(frozen=True)
class LoopIterationInput:
    loop_id: str
    iteration_id: str
    generated_at: datetime
    product_model: ProductModel
    capabilities: tuple[CapabilityState, ...]
    missions: tuple[MissionCandidate, ...]
    signals: tuple[LoopSignal, ...]
    judgments: tuple[AgentJudgment, ...]
    observations: tuple[ForecastObservation, ...]
    prices: tuple[Decimal, ...]
    capacity_points: int
    neural_snapshot: NeuralActivationSnapshot | None = None
    persistence_iterations: tuple[PersistenceIteration, ...] = ()
    evidence_required: bool = True

    def __post_init__(self) -> None:
        _non_empty(self.loop_id, "loop_id")
        _non_empty(self.iteration_id, "iteration_id")
        if self.generated_at.tzinfo is None:
            raise LoopEngineeringError("generated_at must be timezone-aware")
        if not self.missions:
            raise LoopEngineeringError("loop missions must not be empty")
        if not self.signals:
            raise LoopEngineeringError("loop signals must not be empty")
        if self.capacity_points <= 0:
            raise LoopEngineeringError("capacity_points must be positive")


@dataclass(frozen=True)
class LoopRunReport:
    loop_id: str
    iteration_id: str
    generated_at: datetime
    decision: LoopDecision
    phases_completed: tuple[LoopPhase, ...]
    sprint_plan: SprintPlan
    cognitive_report: CognitiveAutonomyReport
    advanced_cognitive_report: AdvancedCognitiveAutonomyReport | None
    persistence_report: PersistenceDisciplineReport | None
    signal_summary: dict[str, int]
    required_evidence: tuple[str, ...]
    rationale: tuple[str, ...]
    patch_allowed: bool = False
    direct_main_write_allowed: bool = False
    auto_merge_allowed: bool = False
    trading_allowed: bool = False
    risk_approval_allowed: bool = False
    execution_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False

    def to_evidence_payload(self) -> dict[str, object]:
        return {
            "loop_id": self.loop_id,
            "iteration_id": self.iteration_id,
            "generated_at": self.generated_at.isoformat(),
            "decision": self.decision.value,
            "phases_completed": [phase.value for phase in self.phases_completed],
            "selected_missions": [item.mission_id for item in self.sprint_plan.selected],
            "blocked_missions": [item.mission_id for item in self.sprint_plan.blocked],
            "deferred_missions": [item.mission_id for item in self.sprint_plan.deferred],
            "cognitive_health": self.cognitive_report.health.value,
            "advanced_cognitive_health": self.advanced_cognitive_report.health.value
            if self.advanced_cognitive_report is not None
            else None,
            "advanced_self_healing_evidence_required": list(
                self.advanced_cognitive_report.self_healing_plan.evidence_required
            )
            if self.advanced_cognitive_report is not None
            else [],
            "persistence_decision": self.persistence_report.decision.value
            if self.persistence_report is not None
            else None,
            "persistence_score": str(self.persistence_report.persistence_score)
            if self.persistence_report is not None
            else None,
            "persistence_required_actions": list(self.persistence_report.required_actions)
            if self.persistence_report is not None
            else [],
            "signal_summary": dict(self.signal_summary),
            "required_evidence": list(self.required_evidence),
            "rationale": list(self.rationale),
            "patch_allowed": self.patch_allowed,
            "direct_main_write_allowed": self.direct_main_write_allowed,
            "auto_merge_allowed": self.auto_merge_allowed,
            "trading_allowed": self.trading_allowed,
            "risk_approval_allowed": self.risk_approval_allowed,
            "execution_allowed": self.execution_allowed,
            "network_allowed": self.network_allowed,
            "credentials_allowed": self.credentials_allowed,
        }

    def append_to_evidence_journal(self, journal: LocalEvidenceJournal) -> EvidenceJournalEntry:
        return journal.append_loop_run_report(self)


@dataclass(frozen=True)
class LoopEngineeringEngine:
    sprint_manager: AutonomousSprintManager
    cognitive_engine: CognitiveAutonomyEngine
    advanced_cognitive_engine: AdvancedCognitiveAutonomyEngine | None = None
    persistence_engine: PersistenceDisciplineEngine | None = None

    def run_iteration(self, input_data: LoopIterationInput) -> LoopRunReport:
        sprint_plan = self.sprint_manager.plan_sprint(
            sprint_id=f"{input_data.loop_id}:{input_data.iteration_id}",
            product_model=input_data.product_model,
            capabilities=input_data.capabilities,
            missions=input_data.missions,
            capacity_points=input_data.capacity_points,
        )
        cognitive_report = self.cognitive_engine.analyze(
            judgments=input_data.judgments,
            observations=input_data.observations,
            prices=input_data.prices,
        )
        advanced_cognitive_report = None
        if self.advanced_cognitive_engine is not None and input_data.neural_snapshot is not None:
            advanced_cognitive_report = self.advanced_cognitive_engine.analyze(
                judgments=input_data.judgments,
                observations=input_data.observations,
                prices=input_data.prices,
                neural_snapshot=input_data.neural_snapshot,
            )
        persistence_report = None
        if self.persistence_engine is not None and input_data.persistence_iterations:
            persistence_report = self.persistence_engine.evaluate(input_data.persistence_iterations)
        signal_summary = _signal_summary(input_data.signals)
        decision, rationale = _decide(
            sprint_plan=sprint_plan,
            cognitive_report=cognitive_report,
            advanced_cognitive_report=advanced_cognitive_report,
            persistence_report=persistence_report,
            signals=input_data.signals,
            evidence_required=input_data.evidence_required,
        )

        return LoopRunReport(
            loop_id=input_data.loop_id,
            iteration_id=input_data.iteration_id,
            generated_at=input_data.generated_at,
            decision=decision,
            phases_completed=(
                LoopPhase.OBSERVE,
                LoopPhase.DIAGNOSE,
                LoopPhase.PLAN,
                LoopPhase.POLICY_VERIFY,
                LoopPhase.EVIDENCE,
                LoopPhase.REVIEW,
            ),
            sprint_plan=sprint_plan,
            cognitive_report=cognitive_report,
            advanced_cognitive_report=advanced_cognitive_report,
            persistence_report=persistence_report,
            signal_summary=signal_summary,
            required_evidence=_required_evidence(input_data.signals, advanced_cognitive_report, persistence_report),
            rationale=rationale,
        )


def _decide(
    *,
    sprint_plan: SprintPlan,
    cognitive_report: CognitiveAutonomyReport,
    advanced_cognitive_report: AdvancedCognitiveAutonomyReport | None,
    persistence_report: PersistenceDisciplineReport | None,
    signals: tuple[LoopSignal, ...],
    evidence_required: bool,
) -> tuple[LoopDecision, tuple[str, ...]]:
    rationale: list[str] = []
    max_severity = max(signal.severity for signal in signals)
    trading_boundary_signal = any(signal.category is LoopSignalCategory.TRADING_BOUNDARY for signal in signals)

    if max_severity >= 5:
        rationale.append("severity_5_signal_blocks_loop")
        return LoopDecision.BLOCK, tuple(rationale)
    if cognitive_report.health is CognitiveHealth.BLOCKED:
        rationale.append("cognitive_health_blocked")
        return LoopDecision.BLOCK, tuple(rationale)
    if advanced_cognitive_report is not None and advanced_cognitive_report.health is CognitiveHealth.BLOCKED:
        rationale.append("advanced_cognitive_health_blocked")
        return LoopDecision.BLOCK, tuple(rationale)
    if persistence_report is not None and persistence_report.decision is PersistenceDecision.BLOCK:
        rationale.append("persistence_discipline_blocked")
        return LoopDecision.BLOCK, tuple(rationale)
    if trading_boundary_signal:
        rationale.append("trading_boundary_signal_requires_human_review")
        return LoopDecision.REQUIRE_HUMAN_REVIEW, tuple(rationale)
    if sprint_plan.blocked:
        rationale.append("sprint_plan_has_blocked_missions")
        return LoopDecision.REQUIRE_HUMAN_REVIEW, tuple(rationale)
    if cognitive_report.health is CognitiveHealth.DEGRADED:
        rationale.append("cognitive_health_degraded")
        return LoopDecision.REQUIRE_HUMAN_REVIEW, tuple(rationale)
    if advanced_cognitive_report is not None and advanced_cognitive_report.health is CognitiveHealth.DEGRADED:
        rationale.append("advanced_cognitive_health_degraded")
        return LoopDecision.REQUIRE_HUMAN_REVIEW, tuple(rationale)
    if persistence_report is not None and persistence_report.decision is PersistenceDecision.REQUIRE_HUMAN_REVIEW:
        rationale.append("persistence_discipline_requires_human_review")
        return LoopDecision.REQUIRE_HUMAN_REVIEW, tuple(rationale)
    if max_severity >= 4:
        rationale.append("severity_4_signal_requires_human_review")
        return LoopDecision.REQUIRE_HUMAN_REVIEW, tuple(rationale)
    if sprint_plan.deferred:
        rationale.append("capacity_deferred_missions_reduce_scope")
        return LoopDecision.REDUCE_SCOPE, tuple(rationale)
    if cognitive_report.health is CognitiveHealth.WATCH:
        rationale.append("cognitive_health_watch_reduce_scope")
        return LoopDecision.REDUCE_SCOPE, tuple(rationale)
    if advanced_cognitive_report is not None and advanced_cognitive_report.health is CognitiveHealth.WATCH:
        rationale.append("advanced_cognitive_health_watch_reduce_scope")
        return LoopDecision.REDUCE_SCOPE, tuple(rationale)
    if persistence_report is not None and persistence_report.decision is PersistenceDecision.REDUCE_SCOPE:
        rationale.append("persistence_discipline_reduce_scope")
        return LoopDecision.REDUCE_SCOPE, tuple(rationale)
    if evidence_required and any(not signal.evidence_refs for signal in signals):
        rationale.append("missing_signal_evidence_reduce_scope")
        return LoopDecision.REDUCE_SCOPE, tuple(rationale)
    if max_severity >= 3:
        rationale.append("moderate_signal_reduce_scope")
        return LoopDecision.REDUCE_SCOPE, tuple(rationale)

    rationale.append("safe_local_loop_can_continue_to_pr_only_planning")
    return LoopDecision.CONTINUE, tuple(rationale)


def _signal_summary(signals: tuple[LoopSignal, ...]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for signal in signals:
        summary[signal.category.value] = summary.get(signal.category.value, 0) + 1
    return dict(sorted(summary.items()))


def _required_evidence(
    signals: tuple[LoopSignal, ...],
    advanced_cognitive_report: AdvancedCognitiveAutonomyReport | None = None,
    persistence_report: PersistenceDisciplineReport | None = None,
) -> tuple[str, ...]:
    evidence = {
        "unit_tests",
        "scaffold_audit",
        "secret_artifact_audit",
        "py_compile",
    }
    for signal in signals:
        if signal.category is LoopSignalCategory.SECURITY:
            evidence.add("security_policy_review")
        if signal.category is LoopSignalCategory.RELIABILITY:
            evidence.add("failure_mode_review")
        if signal.category is LoopSignalCategory.TRADING_BOUNDARY:
            evidence.add("deterministic_risk_gateway_review")
            evidence.add("human_approval_record")
    if advanced_cognitive_report is not None:
        evidence.update(advanced_cognitive_report.self_healing_plan.evidence_required)
    if persistence_report is not None:
        evidence.update(persistence_report.required_evidence)
    return tuple(sorted(evidence))


def _non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise LoopEngineeringError(f"{field_name} must be a non-empty string")


def build_default_loop_engineering_engine() -> LoopEngineeringEngine:
    return LoopEngineeringEngine(
        sprint_manager=build_default_sprint_manager(),
        cognitive_engine=build_default_cognitive_autonomy_engine(),
        advanced_cognitive_engine=build_default_advanced_cognitive_autonomy_engine(),
        persistence_engine=build_default_persistence_discipline_engine(),
    )


def run_loop_iteration_with_evidence(
    *,
    engine: LoopEngineeringEngine,
    input_data: LoopIterationInput,
    journal_path: Path,
    journal_id: str = "local-loop-engineering-journal",
) -> tuple[LoopRunReport, EvidenceJournalEntry]:
    journal = LocalEvidenceJournal(journal_path, journal_id=journal_id)
    report = engine.run_iteration(input_data)
    entry = report.append_to_evidence_journal(journal)
    return report, entry
