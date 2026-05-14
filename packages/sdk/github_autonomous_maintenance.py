from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable


class AutonomousMaintenanceError(Exception):
    """Base error for local autonomous maintenance dry-run components."""


class AutonomousWriteBlocked(AutonomousMaintenanceError):
    """Raised when a component is asked to mutate GitHub or local repositories."""


class AutonomousCredentialBlocked(AutonomousMaintenanceError):
    """Raised when a component is asked to use credentials or token-bearing inputs."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _reject_credential_like_values(values: Iterable[str]) -> None:
    credential_markers = ("token", "secret", "password", "api_key", "private_key", "ghp_", "github_pat_")
    for value in values:
        lowered = value.lower()
        if any(marker in lowered for marker in credential_markers):
            raise AutonomousCredentialBlocked("credential-like value is not allowed in dry-run maintenance")


@dataclass(frozen=True)
class RepositoryRef:
    full_name: str
    default_branch: str = "main"
    monitored: bool = True


@dataclass(frozen=True)
class WebhookEvent:
    event_type: str
    repository: str
    delivery_id: str
    received_at: datetime


@dataclass(frozen=True)
class ScanRequest:
    repository: RepositoryRef
    trigger: str
    scanners: tuple[str, ...]
    dry_run: bool = True


@dataclass(frozen=True)
class Finding:
    finding_id: str
    repository: str
    finding_type: str
    severity: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class PatchPlan:
    patch_plan_id: str
    finding_id: str
    risk_class: str
    planned_files: tuple[str, ...]
    planned_tests: tuple[str, ...]
    rollback_plan: str
    sandbox_required: bool = True
    branch_creation_allowed: bool = False
    commit_allowed: bool = False
    pull_request_allowed: bool = False
    auto_merge_allowed: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    decision_id: str
    finding_id: str
    patch_plan_id: str
    risk_class: str
    decision: str
    allowed_next_action: str
    human_review_required: bool = True
    repository_write_allowed: bool = False
    branch_creation_allowed: bool = False
    pull_request_allowed: bool = False
    auto_merge_allowed: bool = False


@dataclass(frozen=True)
class TestRunResult:
    command: str
    passed: bool
    evidence: str


@dataclass(frozen=True)
class ReviewResult:
    finding_id: str
    risk_class: str
    summary: str
    human_review_required: bool = True


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    repository: str
    finding_id: str
    patch_plan_id: str
    policy_decision_id: str
    evidence_items: tuple[str, ...]
    tests_executed: tuple[str, ...]
    repository_write_performed: bool = False
    auto_merge_performed: bool = False


@dataclass
class AuditLog:
    events: list[str] = field(default_factory=list)

    def record(self, event: str) -> None:
        _reject_credential_like_values((event,))
        self.events.append(event)


class GitHubRepositoryDiscovery:
    def discover(self, repositories: Iterable[str]) -> list[RepositoryRef]:
        refs = []
        for repository in repositories:
            _reject_credential_like_values((repository,))
            if "/" not in repository:
                raise ValueError("repository must use owner/name format")
            refs.append(RepositoryRef(full_name=repository))
        return refs


class MultiRepoMonitor:
    def build_scan_requests(self, repositories: Iterable[RepositoryRef], trigger: str = "manual") -> list[ScanRequest]:
        return [
            ScanRequest(repository=repository, trigger=trigger, scanners=("scaffold_audit", "contract_tests"))
            for repository in repositories
            if repository.monitored
        ]


class WebhookReceiver:
    def receive_dry_run(self, event_type: str, repository: str, delivery_id: str) -> WebhookEvent:
        _reject_credential_like_values((event_type, repository, delivery_id))
        return WebhookEvent(event_type=event_type, repository=repository, delivery_id=delivery_id, received_at=_utc_now())


class ScheduledScanner:
    def schedule_dry_run(self, repository: RepositoryRef) -> ScanRequest:
        return ScanRequest(repository=repository, trigger="scheduled_dry_run", scanners=("scaffold_audit", "secret_artifact_audit"))


class FindingEngine:
    def derive_findings(self, scan_request: ScanRequest, failed_checks: Iterable[str]) -> list[Finding]:
        findings = []
        for index, failed_check in enumerate(failed_checks, start=1):
            _reject_credential_like_values((failed_check,))
            findings.append(
                Finding(
                    finding_id=f"mfr_dry_run_{index}",
                    repository=scan_request.repository.full_name,
                    finding_type="ci_failure",
                    severity="medium",
                    evidence=(failed_check, "dry-run finding only"),
                )
            )
        return findings


class RiskClassifier:
    def classify(self, finding: Finding) -> str:
        if finding.severity in {"critical", "high"}:
            return finding.severity
        if any("execution" in item.lower() or "credential" in item.lower() for item in finding.evidence):
            return "high"
        return finding.severity


class PatchPlanner:
    def plan(self, finding: Finding, risk_class: str) -> PatchPlan:
        return PatchPlan(
            patch_plan_id=f"ppr_{finding.finding_id.removeprefix('mfr_')}",
            finding_id=finding.finding_id,
            risk_class=risk_class,
            planned_files=("docs/architecture/github_autonomous_maintenance_governance.md",),
            planned_tests=("python -m unittest discover -s tests", "python scripts/scaffold_audit.py"),
            rollback_plan="discard dry-run patch plan; no repository write performed",
        )


class PolicyEngine:
    def decide(self, finding: Finding, patch_plan: PatchPlan) -> PolicyDecision:
        if patch_plan.risk_class in {"high", "critical"}:
            decision = "BLOCK"
            next_action = "none"
        else:
            decision = "REQUIRE_HUMAN_REVIEW"
            next_action = "manual_review"
        return PolicyDecision(
            decision_id=f"acpd_{finding.finding_id.removeprefix('mfr_')}",
            finding_id=finding.finding_id,
            patch_plan_id=patch_plan.patch_plan_id,
            risk_class=patch_plan.risk_class,
            decision=decision,
            allowed_next_action=next_action,
        )


class SandboxPatchRunner:
    def run(self, patch_plan: PatchPlan) -> PatchPlan:
        if patch_plan.branch_creation_allowed or patch_plan.commit_allowed or patch_plan.pull_request_allowed:
            raise AutonomousWriteBlocked("dry-run sandbox must not allow repository writes")
        return patch_plan


class TestRunner:
    def plan_only(self, commands: Iterable[str]) -> list[TestRunResult]:
        results = []
        for command in commands:
            _reject_credential_like_values((command,))
            results.append(TestRunResult(command=command, passed=True, evidence="planned-only; command not executed"))
        return results


class BranchCommitPRBot:
    def create_branch_commit_or_pr(self) -> None:
        raise AutonomousWriteBlocked("branch, commit and pull request creation are disabled in dry-run mode")


class PRReviewerAgent:
    def review(self, finding: Finding, risk_class: str) -> ReviewResult:
        return ReviewResult(
            finding_id=finding.finding_id,
            risk_class=risk_class,
            summary="dry-run review requires human approval before any repository write",
        )


class EvidenceIndex:
    def build(
        self,
        repository: RepositoryRef,
        finding: Finding,
        patch_plan: PatchPlan,
        decision: PolicyDecision,
        test_results: Iterable[TestRunResult],
    ) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=f"mer_{finding.finding_id.removeprefix('mfr_')}",
            repository=repository.full_name,
            finding_id=finding.finding_id,
            patch_plan_id=patch_plan.patch_plan_id,
            policy_decision_id=decision.decision_id,
            evidence_items=finding.evidence + ("dry-run evidence index",),
            tests_executed=tuple(result.command for result in test_results),
        )


class RollbackEngine:
    def plan(self, patch_plan: PatchPlan) -> str:
        return patch_plan.rollback_plan


@dataclass
class AutonomousMaintenanceDryRunPipeline:
    discovery: GitHubRepositoryDiscovery = field(default_factory=GitHubRepositoryDiscovery)
    monitor: MultiRepoMonitor = field(default_factory=MultiRepoMonitor)
    webhook_receiver: WebhookReceiver = field(default_factory=WebhookReceiver)
    scheduled_scanner: ScheduledScanner = field(default_factory=ScheduledScanner)
    finding_engine: FindingEngine = field(default_factory=FindingEngine)
    patch_planner: PatchPlanner = field(default_factory=PatchPlanner)
    risk_classifier: RiskClassifier = field(default_factory=RiskClassifier)
    policy_engine: PolicyEngine = field(default_factory=PolicyEngine)
    sandbox_patch_runner: SandboxPatchRunner = field(default_factory=SandboxPatchRunner)
    test_runner: TestRunner = field(default_factory=TestRunner)
    branch_commit_pr_bot: BranchCommitPRBot = field(default_factory=BranchCommitPRBot)
    pr_reviewer_agent: PRReviewerAgent = field(default_factory=PRReviewerAgent)
    evidence_index: EvidenceIndex = field(default_factory=EvidenceIndex)
    rollback_engine: RollbackEngine = field(default_factory=RollbackEngine)
    audit_log: AuditLog = field(default_factory=AuditLog)

    def run(self, repositories: Iterable[str], failed_checks: Iterable[str]) -> list[EvidenceRecord]:
        repo_refs = self.discovery.discover(repositories)
        scan_requests = self.monitor.build_scan_requests(repo_refs)
        evidence_records = []

        for scan_request in scan_requests:
            self.audit_log.record(f"scan_request:{scan_request.repository.full_name}:{scan_request.trigger}")
            findings = self.finding_engine.derive_findings(scan_request, failed_checks)
            for finding in findings:
                risk_class = self.risk_classifier.classify(finding)
                patch_plan = self.patch_planner.plan(finding, risk_class)
                self.sandbox_patch_runner.run(patch_plan)
                decision = self.policy_engine.decide(finding, patch_plan)
                test_results = self.test_runner.plan_only(patch_plan.planned_tests)
                self.pr_reviewer_agent.review(finding, risk_class)
                self.rollback_engine.plan(patch_plan)
                evidence_records.append(
                    self.evidence_index.build(scan_request.repository, finding, patch_plan, decision, test_results)
                )

        return evidence_records
