from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from packages.sdk.agentic_self_programming import (
    AgentPatchPlan,
    AgentPolicyDecision,
    AgentPolicyEngine,
    AgentRiskAssessment,
    AgentRiskLevel,
    AgentTask,
    build_default_agent_policy_engine,
)


class MissionStatus(str, Enum):
    CANDIDATE = "candidate"
    SELECTED = "selected"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class MissionType(str, Enum):
    ARCHITECTURE = "architecture"
    CONTRACT = "contract"
    TESTING = "testing"
    SECURITY = "security"
    RELIABILITY = "reliability"
    RUNTIME_SCAFFOLD = "runtime_scaffold"
    DOCUMENTATION = "documentation"


class SprintManagerError(ValueError):
    """Raised when sprint planning input is unsafe or inconsistent."""


@dataclass(frozen=True)
class ProductModel:
    """Local product model used to rank engineering missions.

    This is a deterministic local planning model, not an LLM runtime. It does
    not call network, read credentials, edit files, open PRs, or approve work.
    """

    product_goal: str
    strategic_themes: tuple[str, ...]
    forbidden_capabilities: tuple[str, ...] = (
        "live trading",
        "broker credentials",
        "exchange credentials",
        "order submission",
        "withdrawals",
        "auto merge",
        "write to main",
    )

    def __post_init__(self) -> None:
        _require_non_empty(self.product_goal, "product_goal")
        if not self.strategic_themes:
            raise SprintManagerError("strategic_themes must not be empty")


@dataclass(frozen=True)
class CapabilityState:
    capability_id: str
    maturity: str
    enabled: bool = False
    blocked_reason: str = ""

    def __post_init__(self) -> None:
        _require_non_empty(self.capability_id, "capability_id")
        _require_non_empty(self.maturity, "maturity")


@dataclass(frozen=True)
class MissionCandidate:
    mission_id: str
    title: str
    mission_type: MissionType
    summary: str
    target_files: tuple[str, ...]
    expected_tests: tuple[str, ...]
    dependencies: tuple[str, ...] = ()
    value_score: int = 1
    urgency_score: int = 1
    complexity_score: int = 1
    risk_score: int = 1

    def __post_init__(self) -> None:
        _require_non_empty(self.mission_id, "mission_id")
        _require_non_empty(self.title, "title")
        _require_non_empty(self.summary, "summary")
        if not self.target_files:
            raise SprintManagerError("mission target_files must not be empty")
        if not self.expected_tests:
            raise SprintManagerError("mission expected_tests must not be empty")
        for field_name in ("value_score", "urgency_score", "complexity_score", "risk_score"):
            value = getattr(self, field_name)
            if value < 1 or value > 10:
                raise SprintManagerError(f"{field_name} must be between 1 and 10")


@dataclass(frozen=True)
class SprintItem:
    mission: MissionCandidate
    status: MissionStatus
    priority_score: int
    risk_assessment: AgentRiskAssessment
    rationale: tuple[str, ...]

    @property
    def mission_id(self) -> str:
        return self.mission.mission_id


@dataclass(frozen=True)
class SprintPlan:
    sprint_id: str
    product_goal: str
    selected: tuple[SprintItem, ...]
    blocked: tuple[SprintItem, ...]
    deferred: tuple[SprintItem, ...]
    capacity_points: int
    safety_invariants: tuple[str, ...] = (
        "no direct main writes",
        "no auto merge",
        "no credentials",
        "no network execution",
        "no live trading",
        "no risk approval",
        "no execution approval",
    )

    def to_summary(self) -> dict[str, object]:
        return {
            "sprint_id": self.sprint_id,
            "product_goal": self.product_goal,
            "selected": [item.mission_id for item in self.selected],
            "blocked": [item.mission_id for item in self.blocked],
            "deferred": [item.mission_id for item in self.deferred],
            "capacity_points": self.capacity_points,
            "safety_invariants": list(self.safety_invariants),
        }


@dataclass(frozen=True)
class AutonomousSprintManager:
    policy_engine: AgentPolicyEngine = field(default_factory=build_default_agent_policy_engine)

    def plan_sprint(
        self,
        *,
        sprint_id: str,
        product_model: ProductModel,
        capabilities: tuple[CapabilityState, ...],
        missions: tuple[MissionCandidate, ...],
        capacity_points: int,
    ) -> SprintPlan:
        _require_non_empty(sprint_id, "sprint_id")
        if capacity_points <= 0:
            raise SprintManagerError("capacity_points must be positive")
        if not missions:
            raise SprintManagerError("missions must not be empty")

        capability_index = {capability.capability_id: capability for capability in capabilities}
        selected: list[SprintItem] = []
        blocked: list[SprintItem] = []
        deferred: list[SprintItem] = []
        used_capacity = 0

        items = [self._score_mission(product_model, capability_index, mission) for mission in missions]
        items.sort(key=lambda item: (-item.priority_score, item.mission.mission_id))

        for item in items:
            if item.status is MissionStatus.BLOCKED:
                blocked.append(item)
                continue

            cost = item.mission.complexity_score
            if used_capacity + cost <= capacity_points:
                selected.append(_with_status(item, MissionStatus.SELECTED))
                used_capacity += cost
            else:
                deferred.append(_with_status(item, MissionStatus.DEFERRED))

        return SprintPlan(
            sprint_id=sprint_id,
            product_goal=product_model.product_goal,
            selected=tuple(selected),
            blocked=tuple(blocked),
            deferred=tuple(deferred),
            capacity_points=capacity_points,
        )

    def _score_mission(
        self,
        product_model: ProductModel,
        capability_index: dict[str, CapabilityState],
        mission: MissionCandidate,
    ) -> SprintItem:
        risk_assessment = self.policy_engine.assess(
            AgentTask(
                task_id=mission.mission_id,
                requested_role=self._role_for(mission.mission_type),
                task_type=self._task_type_for(mission.mission_type),
                summary=mission.summary,
                target_files=mission.target_files,
            ),
            AgentPatchPlan(
                task_id=mission.mission_id,
                proposed_files=mission.target_files,
                test_commands=mission.expected_tests,
                rollback_plan=f"Revert mission {mission.mission_id} branch or remove changed files.",
            ),
        )

        rationale: list[str] = []
        blocked_reasons = self._blocked_reasons(product_model, capability_index, mission, risk_assessment)
        if blocked_reasons:
            return SprintItem(
                mission=mission,
                status=MissionStatus.BLOCKED,
                priority_score=0,
                risk_assessment=risk_assessment,
                rationale=tuple(blocked_reasons),
            )

        theme_bonus = self._theme_bonus(product_model, mission)
        risk_penalty = self._risk_penalty(risk_assessment.risk_level)
        priority = (
            (mission.value_score * 4)
            + (mission.urgency_score * 3)
            + theme_bonus
            - (mission.complexity_score * 2)
            - risk_penalty
            - mission.risk_score
        )
        rationale.append(f"value={mission.value_score}")
        rationale.append(f"urgency={mission.urgency_score}")
        rationale.append(f"theme_bonus={theme_bonus}")
        rationale.append(f"risk_level={risk_assessment.risk_level.value}")
        rationale.append(f"policy_decision={risk_assessment.policy_decision.value}")

        return SprintItem(
            mission=mission,
            status=MissionStatus.CANDIDATE,
            priority_score=priority,
            risk_assessment=risk_assessment,
            rationale=tuple(rationale),
        )

    def _blocked_reasons(
        self,
        product_model: ProductModel,
        capability_index: dict[str, CapabilityState],
        mission: MissionCandidate,
        risk_assessment: AgentRiskAssessment,
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        haystack = " ".join((mission.title, mission.summary, " ".join(mission.target_files))).lower()
        for forbidden in product_model.forbidden_capabilities:
            if forbidden in haystack:
                reasons.append(f"forbidden capability requested: {forbidden}")

        for dependency in mission.dependencies:
            capability = capability_index.get(dependency)
            if capability is None:
                reasons.append(f"missing dependency capability: {dependency}")
            elif not capability.enabled:
                reasons.append(f"dependency not enabled: {dependency}")

        if risk_assessment.policy_decision is AgentPolicyDecision.BLOCK:
            reasons.extend(risk_assessment.findings)

        return tuple(reasons)

    def _theme_bonus(self, product_model: ProductModel, mission: MissionCandidate) -> int:
        haystack = f"{mission.title} {mission.summary}".lower()
        return sum(2 for theme in product_model.strategic_themes if theme.lower() in haystack)

    def _risk_penalty(self, risk_level: AgentRiskLevel) -> int:
        return {
            AgentRiskLevel.LOW: 0,
            AgentRiskLevel.MEDIUM: 3,
            AgentRiskLevel.HIGH: 6,
            AgentRiskLevel.CRITICAL: 100,
        }[risk_level]

    def _role_for(self, mission_type: MissionType) -> str:
        if mission_type is MissionType.SECURITY:
            return "security_reviewer"
        if mission_type is MissionType.ARCHITECTURE:
            return "architecture_reviewer"
        if mission_type is MissionType.TESTING:
            return "test_runner"
        return "code_maintainer"

    def _task_type_for(self, mission_type: MissionType) -> str:
        if mission_type is MissionType.DOCUMENTATION:
            return "documentation"
        if mission_type is MissionType.CONTRACT:
            return "contract"
        if mission_type is MissionType.TESTING:
            return "test"
        return "runtime_scaffold"


def _with_status(item: SprintItem, status: MissionStatus) -> SprintItem:
    return SprintItem(
        mission=item.mission,
        status=status,
        priority_score=item.priority_score,
        risk_assessment=item.risk_assessment,
        rationale=item.rationale,
    )


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SprintManagerError(f"{field_name} must be a non-empty string")


def build_default_sprint_manager() -> AutonomousSprintManager:
    return AutonomousSprintManager()
