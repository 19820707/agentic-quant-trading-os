from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum


class PersistenceDisciplineError(ValueError):
    """Raised when persistence discipline inputs are invalid."""


class PersistenceHealth(str, Enum):
    STABLE = "stable"
    WATCH = "watch"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class PersistenceDecision(str, Enum):
    CONTINUE = "continue"
    REDUCE_SCOPE = "reduce_scope"
    REQUIRE_HUMAN_REVIEW = "require_human_review"
    BLOCK = "block"


@dataclass(frozen=True)
class PersistenceIteration:
    iteration_id: str
    completed: bool
    validation_passed: bool
    evidence_refs: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    regression_detected: bool = False

    def __post_init__(self) -> None:
        _non_empty(self.iteration_id, "iteration_id")
        for evidence_ref in self.evidence_refs:
            _non_empty(evidence_ref, "evidence_ref")
        for blocker in self.blockers:
            _non_empty(blocker, "blocker")


@dataclass(frozen=True)
class PersistenceDisciplineReport:
    iteration_count: int
    completed_count: int
    validation_passed_count: int
    blocked_count: int
    regression_count: int
    evidence_gap_count: int
    consecutive_progress_count: int
    consecutive_blocked_count: int
    persistence_score: Decimal
    health: PersistenceHealth
    decision: PersistenceDecision
    required_evidence: tuple[str, ...]
    required_actions: tuple[str, ...]
    reasons: tuple[str, ...]
    autonomous_remediation_allowed: bool = False
    runtime_change_allowed: bool = False
    trading_allowed: bool = False
    execution_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name, value in (
            ("iteration_count", self.iteration_count),
            ("completed_count", self.completed_count),
            ("validation_passed_count", self.validation_passed_count),
            ("blocked_count", self.blocked_count),
            ("regression_count", self.regression_count),
            ("evidence_gap_count", self.evidence_gap_count),
            ("consecutive_progress_count", self.consecutive_progress_count),
            ("consecutive_blocked_count", self.consecutive_blocked_count),
        ):
            if value < 0:
                raise PersistenceDisciplineError(f"{field_name} must be non-negative")
        _ratio(self.persistence_score, "persistence_score")
        for item in self.required_evidence + self.required_actions + self.reasons:
            _non_empty(item, "report item")

    def to_dict(self) -> dict[str, object]:
        return {
            "iteration_count": self.iteration_count,
            "completed_count": self.completed_count,
            "validation_passed_count": self.validation_passed_count,
            "blocked_count": self.blocked_count,
            "regression_count": self.regression_count,
            "evidence_gap_count": self.evidence_gap_count,
            "consecutive_progress_count": self.consecutive_progress_count,
            "consecutive_blocked_count": self.consecutive_blocked_count,
            "persistence_score": str(self.persistence_score),
            "health": self.health.value,
            "decision": self.decision.value,
            "required_evidence": list(self.required_evidence),
            "required_actions": list(self.required_actions),
            "reasons": list(self.reasons),
            "autonomous_remediation_allowed": self.autonomous_remediation_allowed,
            "runtime_change_allowed": self.runtime_change_allowed,
            "trading_allowed": self.trading_allowed,
            "execution_allowed": self.execution_allowed,
            "network_allowed": self.network_allowed,
            "credentials_allowed": self.credentials_allowed,
        }


class PersistenceDisciplineEngine:
    """Turns persistence into measurable local engineering discipline.

    Persistence here means repeated small, evidenced progress. It does not mean
    bypassing safety gates, forcing scope, editing runtime state, or continuing
    through regressions without review.
    """

    def evaluate(self, iterations: tuple[PersistenceIteration, ...]) -> PersistenceDisciplineReport:
        if not iterations:
            return _report(
                iteration_count=0,
                completed_count=0,
                validation_passed_count=0,
                blocked_count=0,
                regression_count=0,
                evidence_gap_count=0,
                consecutive_progress_count=0,
                consecutive_blocked_count=0,
                persistence_score=Decimal("0.000000"),
                health=PersistenceHealth.WATCH,
                decision=PersistenceDecision.REDUCE_SCOPE,
                reasons=("no_iteration_history",),
                required_actions=("define_next_small_testable_step",),
            )

        completed_count = sum(1 for item in iterations if item.completed)
        validation_passed_count = sum(1 for item in iterations if item.validation_passed)
        blocked_count = sum(1 for item in iterations if item.blockers)
        regression_count = sum(1 for item in iterations if item.regression_detected)
        evidence_gap_count = sum(1 for item in iterations if item.completed and not item.evidence_refs)
        consecutive_progress_count = _consecutive_progress(iterations)
        consecutive_blocked_count = _consecutive_blocked(iterations)
        persistence_score = _score(iterations)

        decision, health, reasons, actions = _decision(
            persistence_score=persistence_score,
            regression_count=regression_count,
            evidence_gap_count=evidence_gap_count,
            consecutive_progress_count=consecutive_progress_count,
            consecutive_blocked_count=consecutive_blocked_count,
        )

        return _report(
            iteration_count=len(iterations),
            completed_count=completed_count,
            validation_passed_count=validation_passed_count,
            blocked_count=blocked_count,
            regression_count=regression_count,
            evidence_gap_count=evidence_gap_count,
            consecutive_progress_count=consecutive_progress_count,
            consecutive_blocked_count=consecutive_blocked_count,
            persistence_score=persistence_score,
            health=health,
            decision=decision,
            reasons=reasons,
            required_actions=actions,
        )


def build_default_persistence_discipline_engine() -> PersistenceDisciplineEngine:
    return PersistenceDisciplineEngine()


def _decision(
    *,
    persistence_score: Decimal,
    regression_count: int,
    evidence_gap_count: int,
    consecutive_progress_count: int,
    consecutive_blocked_count: int,
) -> tuple[PersistenceDecision, PersistenceHealth, tuple[str, ...], tuple[str, ...]]:
    reasons: list[str] = []
    actions: list[str] = []

    if consecutive_blocked_count >= 3:
        reasons.append("three_consecutive_blocked_iterations")
        actions.extend(("stop_expansion", "require_human_review", "produce_rollback_or_recovery_plan"))
        return PersistenceDecision.BLOCK, PersistenceHealth.BLOCKED, tuple(reasons), tuple(actions)
    if regression_count > 0:
        reasons.append("regression_detected")
        actions.extend(("freeze_scope", "add_regression_test", "require_human_review"))
        return PersistenceDecision.REQUIRE_HUMAN_REVIEW, PersistenceHealth.DEGRADED, tuple(reasons), tuple(actions)
    if consecutive_blocked_count >= 2:
        reasons.append("two_consecutive_blocked_iterations")
        actions.extend(("reduce_scope_to_smallest_reproducible_unit", "require_failure_mode_review"))
        return PersistenceDecision.REQUIRE_HUMAN_REVIEW, PersistenceHealth.DEGRADED, tuple(reasons), tuple(actions)
    if evidence_gap_count > 0:
        reasons.append("completed_work_missing_evidence")
        actions.extend(("attach_validation_evidence", "run_relevant_checks"))
        return PersistenceDecision.REDUCE_SCOPE, PersistenceHealth.WATCH, tuple(reasons), tuple(actions)
    if persistence_score < Decimal("0.50"):
        reasons.append("persistence_score_below_minimum")
        actions.extend(("reduce_scope", "increase_feedback_frequency"))
        return PersistenceDecision.REDUCE_SCOPE, PersistenceHealth.WATCH, tuple(reasons), tuple(actions)
    if consecutive_progress_count >= 2 and persistence_score >= Decimal("0.75"):
        reasons.append("evidenced_progress_streak")
        actions.extend(("continue_next_small_step", "keep_evidence_gate_required"))
        return PersistenceDecision.CONTINUE, PersistenceHealth.STABLE, tuple(reasons), tuple(actions)

    reasons.append("progress_observed_but_not_yet_stable")
    actions.extend(("continue_with_narrow_scope", "keep_validation_required"))
    return PersistenceDecision.REDUCE_SCOPE, PersistenceHealth.WATCH, tuple(reasons), tuple(actions)


def _report(
    *,
    iteration_count: int,
    completed_count: int,
    validation_passed_count: int,
    blocked_count: int,
    regression_count: int,
    evidence_gap_count: int,
    consecutive_progress_count: int,
    consecutive_blocked_count: int,
    persistence_score: Decimal,
    health: PersistenceHealth,
    decision: PersistenceDecision,
    reasons: tuple[str, ...],
    required_actions: tuple[str, ...],
) -> PersistenceDisciplineReport:
    return PersistenceDisciplineReport(
        iteration_count=iteration_count,
        completed_count=completed_count,
        validation_passed_count=validation_passed_count,
        blocked_count=blocked_count,
        regression_count=regression_count,
        evidence_gap_count=evidence_gap_count,
        consecutive_progress_count=consecutive_progress_count,
        consecutive_blocked_count=consecutive_blocked_count,
        persistence_score=persistence_score,
        health=health,
        decision=decision,
        required_evidence=("unit_tests", "py_compile", "scaffold_audit", "evidence_quality_gate"),
        required_actions=required_actions,
        reasons=reasons,
        autonomous_remediation_allowed=False,
        runtime_change_allowed=False,
        trading_allowed=False,
        execution_allowed=False,
        network_allowed=False,
        credentials_allowed=False,
    )


def _consecutive_progress(iterations: tuple[PersistenceIteration, ...]) -> int:
    count = 0
    for item in reversed(iterations):
        if item.completed and item.validation_passed and item.evidence_refs and not item.blockers and not item.regression_detected:
            count += 1
        else:
            break
    return count


def _consecutive_blocked(iterations: tuple[PersistenceIteration, ...]) -> int:
    count = 0
    for item in reversed(iterations):
        if item.blockers:
            count += 1
        else:
            break
    return count


def _score(iterations: tuple[PersistenceIteration, ...]) -> Decimal:
    total = Decimal(len(iterations))
    completed = Decimal(sum(1 for item in iterations if item.completed))
    validated = Decimal(sum(1 for item in iterations if item.validation_passed))
    evidenced = Decimal(sum(1 for item in iterations if item.evidence_refs))
    penalties = Decimal(sum(1 for item in iterations if item.blockers or item.regression_detected))
    raw_score = ((completed + validated + evidenced) - penalties) / (total * Decimal("3"))
    return max(Decimal("0"), min(Decimal("1"), raw_score)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def _ratio(value: Decimal, field_name: str) -> None:
    if not isinstance(value, Decimal):
        raise PersistenceDisciplineError(f"{field_name} must be Decimal")
    if value < Decimal("0") or value > Decimal("1"):
        raise PersistenceDisciplineError(f"{field_name} must be between 0 and 1")


def _non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise PersistenceDisciplineError(f"{field_name} must be a non-empty string")
