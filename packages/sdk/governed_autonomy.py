from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from packages.domain.base import deterministic_id, require_aware_datetime
from packages.sdk.agentic_self_programming import AgentPolicyDecision, AgentRiskLevel
from packages.sdk.autonomous_sprint_manager import MissionStatus, SprintItem, SprintPlan


class GovernedAutonomyError(ValueError):
    """Raised when a governed autonomy plan would exceed its authority."""


class AutonomyActionState(str, Enum):
    READY_FOR_PR_PREPARATION = "ready_for_pr_preparation"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class AutonomyPermission(str, Enum):
    PLAN = "plan"
    MODIFY_FILES_IN_BRANCH = "modify_files_in_branch"
    RUN_LOCAL_TESTS = "run_local_tests"
    PREPARE_DRAFT_PR = "prepare_draft_pr"
    REQUEST_HUMAN_REVIEW = "request_human_review"
    RECORD_EVIDENCE = "record_evidence"


@dataclass(frozen=True)
class AutonomyWorkOrder:
    mission_id: str
    title: str
    state: AutonomyActionState
    risk_level: AgentRiskLevel
    policy_decision: AgentPolicyDecision
    target_files: tuple[str, ...]
    test_commands: tuple[str, ...]
    required_evidence: tuple[str, ...]
    permitted_actions: tuple[AutonomyPermission, ...]
    rationale: tuple[str, ...]
    human_review_required: bool
    branch_only: bool = True
    direct_main_write_allowed: bool = False
    auto_merge_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False
    risk_approval_allowed: bool = False
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        _non_empty(self.mission_id, "mission_id")
        _non_empty(self.title, "title")
        if not self.target_files:
            raise GovernedAutonomyError("target_files must not be empty")
        if not self.required_evidence:
            raise GovernedAutonomyError("required_evidence must not be empty")
        if not self.rationale:
            raise GovernedAutonomyError("rationale must not be empty")
        if not self.branch_only:
            raise GovernedAutonomyError("autonomy work orders must be branch-only")
        if any(
            (
                self.direct_main_write_allowed,
                self.auto_merge_allowed,
                self.network_allowed,
                self.credentials_allowed,
                self.risk_approval_allowed,
                self.execution_allowed,
            )
        ):
            raise GovernedAutonomyError("autonomy work order cannot grant critical authority")
        if self.state is AutonomyActionState.READY_FOR_PR_PREPARATION:
            if self.policy_decision is not AgentPolicyDecision.ALLOW_PR_ONLY:
                raise GovernedAutonomyError("ready work requires allow_pr_only policy")
            if self.human_review_required:
                raise GovernedAutonomyError("ready work cannot require human review")
        if self.state is AutonomyActionState.HUMAN_REVIEW_REQUIRED and not self.human_review_required:
            raise GovernedAutonomyError("human-review state must require human review")
        if self.state is AutonomyActionState.BLOCKED and AutonomyPermission.MODIFY_FILES_IN_BRANCH in self.permitted_actions:
            raise GovernedAutonomyError("blocked work cannot modify files")

    def to_payload(self) -> dict[str, object]:
        return {
            "mission_id": self.mission_id,
            "title": self.title,
            "state": self.state.value,
            "risk_level": self.risk_level.value,
            "policy_decision": self.policy_decision.value,
            "target_files": list(self.target_files),
            "test_commands": list(self.test_commands),
            "required_evidence": list(self.required_evidence),
            "permitted_actions": [action.value for action in self.permitted_actions],
            "rationale": list(self.rationale),
            "human_review_required": self.human_review_required,
            "branch_only": True,
            "direct_main_write_allowed": False,
            "auto_merge_allowed": False,
            "network_allowed": False,
            "credentials_allowed": False,
            "risk_approval_allowed": False,
            "execution_allowed": False,
        }


@dataclass(frozen=True)
class GovernedAutonomyPlan:
    plan_id: str
    sprint_id: str
    created_at: datetime
    work_orders: tuple[AutonomyWorkOrder, ...]
    required_evidence: tuple[str, ...]
    ready_count: int
    human_review_count: int
    blocked_count: int
    deferred_count: int
    direct_main_write_allowed: bool = False
    auto_merge_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False
    risk_approval_allowed: bool = False
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        _non_empty(self.plan_id, "plan_id")
        _non_empty(self.sprint_id, "sprint_id")
        require_aware_datetime(self.created_at, "created_at")
        if not self.work_orders:
            raise GovernedAutonomyError("work_orders must not be empty")
        if not self.required_evidence:
            raise GovernedAutonomyError("required_evidence must not be empty")
        counts = {
            AutonomyActionState.READY_FOR_PR_PREPARATION: self.ready_count,
            AutonomyActionState.HUMAN_REVIEW_REQUIRED: self.human_review_count,
            AutonomyActionState.BLOCKED: self.blocked_count,
            AutonomyActionState.DEFERRED: self.deferred_count,
        }
        for state, expected in counts.items():
            actual = sum(1 for work_order in self.work_orders if work_order.state is state)
            if actual != expected:
                raise GovernedAutonomyError(f"{state.value} count mismatch")
        if any(
            (
                self.direct_main_write_allowed,
                self.auto_merge_allowed,
                self.network_allowed,
                self.credentials_allowed,
                self.risk_approval_allowed,
                self.execution_allowed,
            )
        ):
            raise GovernedAutonomyError("governed autonomy plan cannot grant critical authority")

    def to_contract_payload(self, *, trace_id: str, correlation_id: str) -> dict[str, object]:
        _non_empty(trace_id, "trace_id")
        _non_empty(correlation_id, "correlation_id")
        return {
            "schema_version": "0.1.0",
            "trace_id": trace_id,
            "correlation_id": correlation_id,
            "plan_id": self.plan_id,
            "sprint_id": self.sprint_id,
            "created_at": self.created_at.isoformat(),
            "work_orders": [work_order.to_payload() for work_order in self.work_orders],
            "required_evidence": list(self.required_evidence),
            "ready_count": self.ready_count,
            "human_review_count": self.human_review_count,
            "blocked_count": self.blocked_count,
            "deferred_count": self.deferred_count,
            "direct_main_write_allowed": False,
            "auto_merge_allowed": False,
            "network_allowed": False,
            "credentials_allowed": False,
            "risk_approval_allowed": False,
            "execution_allowed": False,
        }


@dataclass(frozen=True)
class GovernedAutonomyPlanner:
    """Turns a sprint plan into a bounded autonomy plan."""

    def build_plan(
        self,
        *,
        sprint_plan: SprintPlan,
        created_at: datetime,
        extra_required_evidence: tuple[str, ...] = (),
    ) -> GovernedAutonomyPlan:
        require_aware_datetime(created_at, "created_at")
        work_orders = tuple(
            _work_order_for_item(item)
            for item in (
                sprint_plan.selected
                + sprint_plan.blocked
                + sprint_plan.deferred
            )
        )
        if not work_orders:
            raise GovernedAutonomyError("sprint plan contains no work")
        required_evidence = tuple(
            sorted(
                {
                    "scaffold_audit",
                    "secret_artifact_audit",
                    "unit_tests",
                    "py_compile",
                    *extra_required_evidence,
                    *(
                        evidence
                        for work_order in work_orders
                        for evidence in work_order.required_evidence
                    ),
                }
            )
        )
        plan_id = deterministic_id(
            "gap",
            sprint_plan.sprint_id,
            created_at.isoformat(),
            ",".join(work_order.mission_id for work_order in work_orders),
        )
        return GovernedAutonomyPlan(
            plan_id=plan_id,
            sprint_id=sprint_plan.sprint_id,
            created_at=created_at,
            work_orders=work_orders,
            required_evidence=required_evidence,
            ready_count=sum(1 for item in work_orders if item.state is AutonomyActionState.READY_FOR_PR_PREPARATION),
            human_review_count=sum(1 for item in work_orders if item.state is AutonomyActionState.HUMAN_REVIEW_REQUIRED),
            blocked_count=sum(1 for item in work_orders if item.state is AutonomyActionState.BLOCKED),
            deferred_count=sum(1 for item in work_orders if item.state is AutonomyActionState.DEFERRED),
        )


def build_default_governed_autonomy_planner() -> GovernedAutonomyPlanner:
    return GovernedAutonomyPlanner()


def _work_order_for_item(item: SprintItem) -> AutonomyWorkOrder:
    assessment = item.risk_assessment
    if item.status is MissionStatus.BLOCKED or assessment.policy_decision is AgentPolicyDecision.BLOCK:
        state = AutonomyActionState.BLOCKED
        actions = (AutonomyPermission.REQUEST_HUMAN_REVIEW, AutonomyPermission.RECORD_EVIDENCE)
        human_review_required = True
    elif item.status is MissionStatus.DEFERRED:
        state = AutonomyActionState.DEFERRED
        actions = (AutonomyPermission.PLAN, AutonomyPermission.RECORD_EVIDENCE)
        human_review_required = True
    elif assessment.policy_decision is AgentPolicyDecision.REQUIRE_HUMAN_REVIEW:
        state = AutonomyActionState.HUMAN_REVIEW_REQUIRED
        actions = (AutonomyPermission.PLAN, AutonomyPermission.REQUEST_HUMAN_REVIEW, AutonomyPermission.RECORD_EVIDENCE)
        human_review_required = True
    else:
        state = AutonomyActionState.READY_FOR_PR_PREPARATION
        actions = (
            AutonomyPermission.PLAN,
            AutonomyPermission.MODIFY_FILES_IN_BRANCH,
            AutonomyPermission.RUN_LOCAL_TESTS,
            AutonomyPermission.PREPARE_DRAFT_PR,
            AutonomyPermission.RECORD_EVIDENCE,
        )
        human_review_required = False

    required_evidence = tuple(
        sorted(
            {
                "rollback_plan",
                "test_evidence",
                *_evidence_for_risk(assessment.risk_level),
                *_evidence_for_files(item.mission.target_files),
            }
        )
    )
    return AutonomyWorkOrder(
        mission_id=item.mission_id,
        title=item.mission.title,
        state=state,
        risk_level=assessment.risk_level,
        policy_decision=assessment.policy_decision,
        target_files=item.mission.target_files,
        test_commands=item.mission.expected_tests,
        required_evidence=required_evidence,
        permitted_actions=actions,
        rationale=item.rationale + assessment.findings,
        human_review_required=human_review_required,
    )


def _evidence_for_risk(risk_level: AgentRiskLevel) -> tuple[str, ...]:
    if risk_level is AgentRiskLevel.LOW:
        return ("local_diff_review",)
    if risk_level is AgentRiskLevel.MEDIUM:
        return ("human_code_review", "local_diff_review")
    if risk_level is AgentRiskLevel.HIGH:
        return ("human_code_review", "security_review", "local_diff_review")
    return ("human_code_review", "security_review", "blocked_scope_record")


def _evidence_for_files(target_files: tuple[str, ...]) -> tuple[str, ...]:
    normalized = " ".join(path.replace("\\", "/").lower() for path in target_files)
    evidence: set[str] = set()
    if "packages/contracts/schemas" in normalized:
        evidence.add("contract_validation")
    if "packages/sdk" in normalized:
        evidence.add("sdk_unit_tests")
    if "docs/" in normalized:
        evidence.add("documentation_review")
    if ".github/workflows" in normalized or "scripts/" in normalized:
        evidence.add("ci_safety_review")
    if "risk" in normalized or "execution" in normalized or "trading" in normalized:
        evidence.add("deterministic_risk_gateway_review")
    return tuple(sorted(evidence))


def _non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise GovernedAutonomyError(f"{field_name} must be a non-empty string")
