from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from packages.domain.base import require_non_empty

from .evidence_summary import LoopEvidenceSummary
from .local import ObservabilityError


class EvidenceGateDecision(str, Enum):
    PASS = "pass"
    REVIEW = "review"
    BLOCK = "block"


@dataclass(frozen=True)
class EvidenceQualityGatePolicy:
    min_integrity_score: Decimal = Decimal("1.000000")
    min_coverage_score: Decimal = Decimal("1.000000")
    require_entries: bool = True
    block_on_tamper: bool = True
    block_on_missing_required_evidence: bool = True

    def __post_init__(self) -> None:
        _ratio(self.min_integrity_score, "min_integrity_score")
        _ratio(self.min_coverage_score, "min_coverage_score")


@dataclass(frozen=True)
class EvidenceQualityGateResult:
    decision: EvidenceGateDecision
    policy: EvidenceQualityGatePolicy
    integrity_score: Decimal
    coverage_score: Decimal
    tamper_detected: bool
    total_entry_count: int
    missing_record_types: tuple[str, ...]
    reasons: tuple[str, ...]
    promotion_allowed: bool = False
    remediation_allowed: bool = False
    trading_allowed: bool = False
    execution_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False

    def __post_init__(self) -> None:
        if self.total_entry_count < 0:
            raise ObservabilityError("total_entry_count must be non-negative")
        for reason in self.reasons:
            require_non_empty(reason, "reason")

    def to_dict(self) -> dict[str, object]:
        return {
            "decision": self.decision.value,
            "integrity_score": str(self.integrity_score),
            "coverage_score": str(self.coverage_score),
            "tamper_detected": self.tamper_detected,
            "total_entry_count": self.total_entry_count,
            "missing_record_types": list(self.missing_record_types),
            "reasons": list(self.reasons),
            "policy": {
                "min_integrity_score": str(self.policy.min_integrity_score),
                "min_coverage_score": str(self.policy.min_coverage_score),
                "require_entries": self.policy.require_entries,
                "block_on_tamper": self.policy.block_on_tamper,
                "block_on_missing_required_evidence": self.policy.block_on_missing_required_evidence,
            },
            "promotion_allowed": self.promotion_allowed,
            "remediation_allowed": self.remediation_allowed,
            "trading_allowed": self.trading_allowed,
            "execution_allowed": self.execution_allowed,
            "network_allowed": self.network_allowed,
            "credentials_allowed": self.credentials_allowed,
        }


def evaluate_evidence_quality_gate(
    summary: LoopEvidenceSummary,
    *,
    policy: EvidenceQualityGatePolicy | None = None,
) -> EvidenceQualityGateResult:
    gate_policy = policy or EvidenceQualityGatePolicy()
    reasons: list[str] = []
    blocking = False

    if gate_policy.require_entries and summary.total_entry_count == 0:
        reasons.append("no_evidence_entries")
        blocking = True
    if gate_policy.block_on_tamper and summary.tamper_detected:
        reasons.append("tamper_detected")
        blocking = True
    if summary.integrity_score < gate_policy.min_integrity_score:
        reasons.append("integrity_score_below_policy")
        blocking = True
    if summary.coverage_score < gate_policy.min_coverage_score:
        reasons.append("coverage_score_below_policy")
        blocking = True
    if gate_policy.block_on_missing_required_evidence and summary.missing_record_types:
        reasons.append("missing_required_evidence")
        blocking = True
    if summary.violations:
        reasons.append("summary_violations_present")
        blocking = True

    if blocking:
        decision = EvidenceGateDecision.BLOCK
        promotion_allowed = False
    elif reasons:
        decision = EvidenceGateDecision.REVIEW
        promotion_allowed = False
    else:
        decision = EvidenceGateDecision.PASS
        promotion_allowed = True
        reasons.append("evidence_quality_gate_passed")

    return EvidenceQualityGateResult(
        decision=decision,
        policy=gate_policy,
        integrity_score=summary.integrity_score,
        coverage_score=summary.coverage_score,
        tamper_detected=summary.tamper_detected,
        total_entry_count=summary.total_entry_count,
        missing_record_types=summary.missing_record_types,
        reasons=tuple(reasons),
        promotion_allowed=promotion_allowed,
        remediation_allowed=False,
        trading_allowed=False,
        execution_allowed=False,
        network_allowed=False,
        credentials_allowed=False,
    )


def _ratio(value: Decimal, field_name: str) -> None:
    if not isinstance(value, Decimal):
        raise ObservabilityError(f"{field_name} must be Decimal")
    if value < Decimal("0") or value > Decimal("1"):
        raise ObservabilityError(f"{field_name} must be between 0 and 1")
