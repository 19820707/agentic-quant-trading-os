from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath


class AgentRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentPolicyDecision(str, Enum):
    ALLOW_PR_ONLY = "allow_pr_only"
    REQUIRE_HUMAN_REVIEW = "require_human_review"
    BLOCK = "block"


class AgentPolicyError(RuntimeError):
    """Raised when an agent request violates the local governance boundary."""


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    requested_role: str
    task_type: str
    summary: str
    target_files: tuple[str, ...]


@dataclass(frozen=True)
class AgentPatchPlan:
    task_id: str
    proposed_files: tuple[str, ...]
    test_commands: tuple[str, ...]
    rollback_plan: str


@dataclass(frozen=True)
class AgentRiskAssessment:
    risk_level: AgentRiskLevel
    policy_decision: AgentPolicyDecision
    findings: tuple[str, ...]
    sandbox_required: bool = True
    test_evidence_required: bool = True
    human_review_required: bool = True
    direct_main_write_allowed: bool = False
    auto_merge_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False
    trading_changes_allowed: bool = False
    risk_approval_allowed: bool = False
    execution_allowed: bool = False

    def to_contract_payload(self) -> dict[str, object]:
        return {
            "risk_level": self.risk_level.value,
            "policy_decision": self.policy_decision.value,
            "policy_findings": list(self.findings),
            "sandbox_required": self.sandbox_required,
            "test_evidence_required": self.test_evidence_required,
            "human_review_required": self.human_review_required,
            "direct_main_write_allowed": self.direct_main_write_allowed,
            "auto_merge_allowed": self.auto_merge_allowed,
            "network_allowed": self.network_allowed,
            "credentials_allowed": self.credentials_allowed,
            "trading_changes_allowed": self.trading_changes_allowed,
            "risk_approval_allowed": self.risk_approval_allowed,
            "execution_allowed": self.execution_allowed,
        }


@dataclass(frozen=True)
class AgentPolicyEngine:
    """Deterministic local policy engine for agent-authored engineering changes.

    It classifies proposed changes only. It never edits files, runs commands,
    reads credentials, opens pull requests, calls networks, or approves execution.
    """

    critical_path_markers: tuple[str, ...] = (
        "execution",
        "broker",
        "exchange",
        "risk_gateway",
        "risk-gateway",
        "approved_order",
        "order_intent",
        "secrets",
        ".env",
    )
    critical_content_markers: tuple[str, ...] = (
        "create_order",
        "submit_order",
        "cancel_order",
        "withdraw",
        "transfer",
        "api_key",
        "private_key",
        "broker_secret",
        "exchange_secret",
        "auto_merge",
        "write_to_main",
    )
    high_path_markers: tuple[str, ...] = (
        ".github/workflows",
        "scripts/",
        "packages/contracts/schemas/trading",
        "packages/contracts/schemas/security",
    )
    medium_path_markers: tuple[str, ...] = (
        "packages/contracts/schemas",
        "packages/sdk",
        "tests/",
    )
    # Governance and build files: a change here alters who may approve what, or
    # what runs in CI, so it always needs a human.
    governance_path_markers: tuple[str, ...] = (
        "agents.md",
        "codeowners",
        "security.md",
        "security/",
        ".github/",
        "pyproject.toml",
        "package.json",
        "makefile",
        "docker_compose",
        "infra/",
        "packages/common",
    )
    # The only paths an agent may change on a pull-request-only basis. Anything
    # not listed here and not matched above falls back to human review.
    low_impact_path_prefixes: tuple[str, ...] = ("docs/",)

    def assess(self, task: AgentTask, patch_plan: AgentPatchPlan) -> AgentRiskAssessment:
        findings: list[str] = []
        normalized_paths = tuple(self._normalize_path(path) for path in patch_plan.proposed_files)
        haystack = " ".join(
            (
                task.requested_role,
                task.task_type,
                task.summary,
                " ".join(task.target_files),
                " ".join(patch_plan.proposed_files),
                " ".join(patch_plan.test_commands),
                patch_plan.rollback_plan,
            )
        ).lower()

        if task.task_id != patch_plan.task_id:
            findings.append("patch plan task_id does not match agent task")
            return self._assessment(AgentRiskLevel.CRITICAL, AgentPolicyDecision.BLOCK, findings)

        if not patch_plan.test_commands:
            findings.append("test evidence command list is required")
            return self._assessment(AgentRiskLevel.CRITICAL, AgentPolicyDecision.BLOCK, findings)

        if not patch_plan.rollback_plan.strip():
            findings.append("rollback plan is required")
            return self._assessment(AgentRiskLevel.CRITICAL, AgentPolicyDecision.BLOCK, findings)

        if not normalized_paths:
            findings.append("patch plan must list the files it proposes to change")
            return self._assessment(AgentRiskLevel.CRITICAL, AgentPolicyDecision.BLOCK, findings)

        if any(self._is_unsafe_path(path) for path in patch_plan.proposed_files):
            findings.append("proposed file paths must be relative and must not contain traversal segments")
            return self._assessment(AgentRiskLevel.CRITICAL, AgentPolicyDecision.BLOCK, findings)

        declared_targets = {self._normalize_path(path) for path in task.target_files}
        if not set(normalized_paths) <= declared_targets:
            findings.append("patch plan proposes files outside the task's declared target files")
            return self._assessment(AgentRiskLevel.CRITICAL, AgentPolicyDecision.BLOCK, findings)

        if self._contains_marker(normalized_paths, self.critical_path_markers):
            findings.append("critical path marker detected")

        if any(marker in haystack for marker in self.critical_content_markers):
            findings.append("critical capability marker detected")

        if findings:
            return self._assessment(AgentRiskLevel.CRITICAL, AgentPolicyDecision.BLOCK, findings)

        if self._contains_marker(normalized_paths, self.high_path_markers):
            findings.append("high-impact platform path requires human review")
            return self._assessment(AgentRiskLevel.HIGH, AgentPolicyDecision.REQUIRE_HUMAN_REVIEW, findings)

        if self._contains_marker(normalized_paths, self.governance_path_markers):
            findings.append("governance, security or build path requires human review")
            return self._assessment(AgentRiskLevel.HIGH, AgentPolicyDecision.REQUIRE_HUMAN_REVIEW, findings)

        if self._contains_marker(normalized_paths, self.medium_path_markers):
            findings.append("contract, SDK, or test path requires human review")
            return self._assessment(AgentRiskLevel.MEDIUM, AgentPolicyDecision.REQUIRE_HUMAN_REVIEW, findings)

        if not all(path.startswith(self.low_impact_path_prefixes) for path in normalized_paths):
            findings.append("path is not on the low-impact allowlist and requires human review")
            return self._assessment(AgentRiskLevel.MEDIUM, AgentPolicyDecision.REQUIRE_HUMAN_REVIEW, findings)

        findings.append("documentation-only or low-impact path may proceed to pull-request-only review")
        return self._assessment(AgentRiskLevel.LOW, AgentPolicyDecision.ALLOW_PR_ONLY, findings)

    def ensure_pr_only_allowed(self, assessment: AgentRiskAssessment) -> None:
        if assessment.policy_decision is not AgentPolicyDecision.ALLOW_PR_ONLY:
            raise AgentPolicyError("agent change is not allowed without human review")

    def _assessment(
        self,
        risk_level: AgentRiskLevel,
        decision: AgentPolicyDecision,
        findings: list[str],
    ) -> AgentRiskAssessment:
        return AgentRiskAssessment(
            risk_level=risk_level,
            policy_decision=decision,
            findings=tuple(findings),
        )

    def _contains_marker(self, paths: tuple[str, ...], markers: tuple[str, ...]) -> bool:
        # Hyphens and underscores are interchangeable, so the ``order_intent``
        # marker also covers ``services/order-intent-service``.
        folded_paths = tuple(path.replace("-", "_") for path in paths)
        folded_markers = tuple(marker.replace("-", "_") for marker in markers)
        return any(marker in path for path in folded_paths for marker in folded_markers)

    def _normalize_path(self, path: str) -> str:
        pure_path = PurePosixPath(path.strip().replace("\\", "/"))
        return pure_path.as_posix().lower()

    def _is_unsafe_path(self, path: str) -> bool:
        cleaned = path.strip().replace("\\", "/")
        if not cleaned or cleaned.startswith(("/", "~")):
            return True
        if len(cleaned) > 1 and cleaned[1] == ":":
            return True
        return ".." in PurePosixPath(cleaned).parts


def build_default_agent_policy_engine() -> AgentPolicyEngine:
    return AgentPolicyEngine()
