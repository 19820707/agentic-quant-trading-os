from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from packages.domain.base import require_aware_datetime, require_non_empty

from .evidence import EvidenceJournalVerification, EvidenceRecordType, LocalEvidenceJournal
from .local import ObservabilityError


@dataclass(frozen=True)
class EvidenceJournalReference:
    path: Path
    journal_id: str

    def __post_init__(self) -> None:
        require_non_empty(self.journal_id, "journal_id")
        if self.path.suffix != ".jsonl":
            raise ObservabilityError("evidence journal path must use .jsonl suffix")


@dataclass(frozen=True)
class EvidenceJournalSummary:
    journal_id: str
    path: str
    configured: bool
    exists: bool
    valid: bool
    entry_count: int
    last_entry_hash: str | None
    record_type_counts: dict[str, int]
    violations: tuple[str, ...]

    def __post_init__(self) -> None:
        require_non_empty(self.journal_id, "journal_id")
        require_non_empty(self.path, "path")
        if self.entry_count < 0:
            raise ObservabilityError("entry_count must be non-negative")


@dataclass(frozen=True)
class LoopEvidenceSummary:
    checked_at: datetime
    journal_count: int
    configured_journal_count: int
    valid_journal_count: int
    invalid_journal_count: int
    total_entry_count: int
    record_type_counts: dict[str, int]
    required_record_types: tuple[str, ...]
    missing_record_types: tuple[str, ...]
    integrity_score: Decimal
    coverage_score: Decimal
    tamper_detected: bool
    journal_summaries: tuple[EvidenceJournalSummary, ...]
    violations: tuple[str, ...]
    network_allowed: bool = False
    credentials_allowed: bool = False
    external_services_used: bool = False
    remediation_allowed: bool = False
    trading_allowed: bool = False
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        require_aware_datetime(self.checked_at, "checked_at")
        for field_name, value in (
            ("journal_count", self.journal_count),
            ("configured_journal_count", self.configured_journal_count),
            ("valid_journal_count", self.valid_journal_count),
            ("invalid_journal_count", self.invalid_journal_count),
            ("total_entry_count", self.total_entry_count),
        ):
            if value < 0:
                raise ObservabilityError(f"{field_name} must be non-negative")

    def to_dict(self) -> dict[str, object]:
        return {
            "checked_at": self.checked_at.isoformat(),
            "journal_count": self.journal_count,
            "configured_journal_count": self.configured_journal_count,
            "valid_journal_count": self.valid_journal_count,
            "invalid_journal_count": self.invalid_journal_count,
            "total_entry_count": self.total_entry_count,
            "record_type_counts": dict(self.record_type_counts),
            "required_record_types": list(self.required_record_types),
            "missing_record_types": list(self.missing_record_types),
            "integrity_score": str(self.integrity_score),
            "coverage_score": str(self.coverage_score),
            "tamper_detected": self.tamper_detected,
            "journal_summaries": [
                {
                    "journal_id": summary.journal_id,
                    "path": summary.path,
                    "configured": summary.configured,
                    "exists": summary.exists,
                    "valid": summary.valid,
                    "entry_count": summary.entry_count,
                    "last_entry_hash": summary.last_entry_hash,
                    "record_type_counts": dict(summary.record_type_counts),
                    "violations": list(summary.violations),
                }
                for summary in self.journal_summaries
            ],
            "violations": list(self.violations),
            "network_allowed": self.network_allowed,
            "credentials_allowed": self.credentials_allowed,
            "external_services_used": self.external_services_used,
            "remediation_allowed": self.remediation_allowed,
            "trading_allowed": self.trading_allowed,
            "execution_allowed": self.execution_allowed,
        }


DEFAULT_LOOP_REQUIRED_RECORD_TYPES = (
    EvidenceRecordType.LOOP_RUN_REPORT,
)


def summarize_loop_evidence(
    references: tuple[EvidenceJournalReference, ...],
    *,
    required_record_types: tuple[EvidenceRecordType, ...] = DEFAULT_LOOP_REQUIRED_RECORD_TYPES,
    checked_at: datetime | None = None,
) -> LoopEvidenceSummary:
    timestamp = checked_at or datetime.now(timezone.utc)
    if not references:
        required = tuple(item.value for item in required_record_types)
        return LoopEvidenceSummary(
            checked_at=timestamp,
            journal_count=0,
            configured_journal_count=0,
            valid_journal_count=0,
            invalid_journal_count=0,
            total_entry_count=0,
            record_type_counts={},
            required_record_types=required,
            missing_record_types=required,
            integrity_score=Decimal("1.000000"),
            coverage_score=Decimal("0.000000"),
            tamper_detected=False,
            journal_summaries=(),
            violations=(),
        )

    journal_summaries: list[EvidenceJournalSummary] = []
    aggregate_counts: dict[str, int] = {}
    aggregate_violations: list[str] = []
    valid_count = 0
    invalid_count = 0

    for reference in references:
        summary = _summarize_journal(reference, checked_at=timestamp)
        journal_summaries.append(summary)
        if summary.valid:
            valid_count += 1
        else:
            invalid_count += 1
        for record_type, count in summary.record_type_counts.items():
            aggregate_counts[record_type] = aggregate_counts.get(record_type, 0) + count
        aggregate_violations.extend(f"{summary.journal_id}:{violation}" for violation in summary.violations)

    required_values = tuple(item.value for item in required_record_types)
    missing = tuple(item for item in required_values if aggregate_counts.get(item, 0) == 0)
    total_entries = sum(summary.entry_count for summary in journal_summaries)
    integrity_score = _ratio(valid_count, len(journal_summaries))
    coverage_score = _ratio(len(required_values) - len(missing), len(required_values)) if required_values else Decimal("1.000000")

    return LoopEvidenceSummary(
        checked_at=timestamp,
        journal_count=len(journal_summaries),
        configured_journal_count=len(references),
        valid_journal_count=valid_count,
        invalid_journal_count=invalid_count,
        total_entry_count=total_entries,
        record_type_counts=dict(sorted(aggregate_counts.items())),
        required_record_types=required_values,
        missing_record_types=missing,
        integrity_score=integrity_score,
        coverage_score=coverage_score,
        tamper_detected=invalid_count > 0,
        journal_summaries=tuple(journal_summaries),
        violations=tuple(aggregate_violations),
        network_allowed=False,
        credentials_allowed=False,
        external_services_used=False,
        remediation_allowed=False,
        trading_allowed=False,
        execution_allowed=False,
    )


def _summarize_journal(
    reference: EvidenceJournalReference,
    *,
    checked_at: datetime,
) -> EvidenceJournalSummary:
    journal = LocalEvidenceJournal(reference.path, journal_id=reference.journal_id)
    verification = journal.verify(checked_at=checked_at)
    counts: dict[str, int] = {}
    entry_count = verification.entry_count
    violations = list(verification.violations)
    if reference.path.exists() and _verification_records_are_parseable(verification):
        try:
            for entry in journal.read_entries(validate=False):
                counts[entry.record_type.value] = counts.get(entry.record_type.value, 0) + 1
        except Exception as exc:
            violations.append(f"read_entries_failed:{exc}")
            verification = EvidenceJournalVerification(
                journal_id=verification.journal_id,
                checked_at=verification.checked_at,
                valid=False,
                entry_count=verification.entry_count,
                last_entry_hash=verification.last_entry_hash,
                violations=tuple(violations),
            )

    return EvidenceJournalSummary(
        journal_id=reference.journal_id,
        path=reference.path.as_posix(),
        configured=True,
        exists=reference.path.exists(),
        valid=verification.valid,
        entry_count=entry_count,
        last_entry_hash=verification.last_entry_hash,
        record_type_counts=dict(sorted(counts.items())),
        violations=tuple(violations),
    )


def _verification_records_are_parseable(verification: EvidenceJournalVerification) -> bool:
    return not any(violation.startswith("line_") for violation in verification.violations)


def _ratio(numerator: int, denominator: int) -> Decimal:
    if denominator <= 0:
        return Decimal("0.000000")
    return (Decimal(numerator) / Decimal(denominator)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
