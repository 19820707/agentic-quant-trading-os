from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import hashlib
import json
from pathlib import Path
from typing import Any

from packages.domain.base import deterministic_id, require_aware_datetime, require_non_empty, to_primitive

from .local import LocalObservabilitySink, MetricPoint, MetricsSnapshot, ObservabilityError, StructuredLogRecord, sanitize_attributes


GENESIS_HASH = "0" * 64


class EvidenceRecordType(str, Enum):
    AUDIT_EVENT = "AUDIT_EVENT"
    LOG_RECORD = "LOG_RECORD"
    METRIC_POINT = "METRIC_POINT"
    METRICS_SNAPSHOT = "METRICS_SNAPSHOT"
    LOOP_RUN_REPORT = "LOOP_RUN_REPORT"
    GENERIC_EVIDENCE = "GENERIC_EVIDENCE"


@dataclass(frozen=True)
class EvidenceJournalEntry:
    journal_id: str
    sequence: int
    record_type: EvidenceRecordType
    occurred_at: datetime
    previous_hash: str
    payload_hash: str
    entry_hash: str
    payload: dict[str, Any]

    def __post_init__(self) -> None:
        require_non_empty(self.journal_id, "journal_id")
        require_aware_datetime(self.occurred_at, "occurred_at")
        if self.sequence < 1:
            raise ObservabilityError("journal sequence must start at 1")
        _require_sha256_hex(self.previous_hash, "previous_hash")
        _require_sha256_hex(self.payload_hash, "payload_hash")
        _require_sha256_hex(self.entry_hash, "entry_hash")


@dataclass(frozen=True)
class EvidenceJournalVerification:
    journal_id: str
    checked_at: datetime
    valid: bool
    entry_count: int
    last_entry_hash: str
    violations: tuple[str, ...]

    def __post_init__(self) -> None:
        require_non_empty(self.journal_id, "journal_id")
        require_aware_datetime(self.checked_at, "checked_at")
        if self.entry_count < 0:
            raise ObservabilityError("entry_count must be non-negative")


class LocalEvidenceJournal:
    """Append-only local JSONL evidence journal with hash-chain verification.

    The journal does not call network, export telemetry, read credentials,
    connect to a database, or approve trading activity.
    """

    def __init__(self, path: Path, *, journal_id: str = "local-evidence-journal") -> None:
        self.path = path
        self.journal_id = require_non_empty(journal_id, "journal_id")
        if self.path.suffix != ".jsonl":
            raise ObservabilityError("evidence journal path must use .jsonl suffix")

    def append_audit_event(self, event: object) -> EvidenceJournalEntry:
        return self.append(EvidenceRecordType.AUDIT_EVENT, event)

    def append_log_record(self, record: StructuredLogRecord) -> EvidenceJournalEntry:
        return self.append(EvidenceRecordType.LOG_RECORD, record)

    def append_metric_point(self, point: MetricPoint) -> EvidenceJournalEntry:
        return self.append(EvidenceRecordType.METRIC_POINT, point)

    def append_metrics_snapshot(self, snapshot: MetricsSnapshot) -> EvidenceJournalEntry:
        return self.append(EvidenceRecordType.METRICS_SNAPSHOT, snapshot)

    def append_loop_run_report(self, report: object) -> EvidenceJournalEntry:
        payload = report.to_evidence_payload() if hasattr(report, "to_evidence_payload") else report
        return self.append(EvidenceRecordType.LOOP_RUN_REPORT, payload, occurred_at=_payload_timestamp(report))

    def append(
        self,
        record_type: EvidenceRecordType,
        payload: object,
        *,
        occurred_at: datetime | None = None,
    ) -> EvidenceJournalEntry:
        timestamp = occurred_at or _payload_timestamp(payload) or datetime.now(timezone.utc)
        payload_dict = _canonical_payload(payload)
        existing = self.read_entries(validate=False)
        previous_hash = existing[-1].entry_hash if existing else GENESIS_HASH
        sequence = len(existing) + 1
        payload_hash = _sha256_json(payload_dict)
        entry_hash = _entry_hash(
            journal_id=self.journal_id,
            sequence=sequence,
            record_type=record_type,
            occurred_at=timestamp,
            previous_hash=previous_hash,
            payload_hash=payload_hash,
            payload=payload_dict,
        )
        entry = EvidenceJournalEntry(
            journal_id=self.journal_id,
            sequence=sequence,
            record_type=record_type,
            occurred_at=timestamp,
            previous_hash=previous_hash,
            payload_hash=payload_hash,
            entry_hash=entry_hash,
            payload=payload_dict,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as output:
            output.write(_canonical_json(_entry_to_record(entry)))
            output.write("\n")
        return entry

    def read_entries(self, *, validate: bool = True) -> tuple[EvidenceJournalEntry, ...]:
        if not self.path.exists():
            return ()
        entries: list[EvidenceJournalEntry] = []
        with self.path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                try:
                    entries.append(_entry_from_record(json.loads(line)))
                except Exception as exc:
                    if validate:
                        raise ObservabilityError(f"invalid evidence journal entry at line {line_number}: {exc}") from exc
                    raise
        if validate:
            verification = self.verify()
            if not verification.valid:
                raise ObservabilityError("; ".join(verification.violations))
        return tuple(entries)

    def verify(self, *, checked_at: datetime | None = None) -> EvidenceJournalVerification:
        timestamp = checked_at or datetime.now(timezone.utc)
        violations: list[str] = []
        entries: list[EvidenceJournalEntry] = []

        if not self.path.exists():
            return EvidenceJournalVerification(
                journal_id=self.journal_id,
                checked_at=timestamp,
                valid=True,
                entry_count=0,
                last_entry_hash=GENESIS_HASH,
                violations=(),
            )

        with self.path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                try:
                    entries.append(_entry_from_record(json.loads(line)))
                except Exception as exc:
                    violations.append(f"line_{line_number}:invalid_record:{exc}")

        previous_hash = GENESIS_HASH
        for expected_sequence, entry in enumerate(entries, start=1):
            if entry.journal_id != self.journal_id:
                violations.append(f"sequence_{entry.sequence}:journal_id_mismatch")
            if entry.sequence != expected_sequence:
                violations.append(f"sequence_{entry.sequence}:sequence_gap")
            if entry.previous_hash != previous_hash:
                violations.append(f"sequence_{entry.sequence}:previous_hash_mismatch")
            expected_payload_hash = _sha256_json(entry.payload)
            if entry.payload_hash != expected_payload_hash:
                violations.append(f"sequence_{entry.sequence}:payload_hash_mismatch")
            expected_entry_hash = _entry_hash(
                journal_id=entry.journal_id,
                sequence=entry.sequence,
                record_type=entry.record_type,
                occurred_at=entry.occurred_at,
                previous_hash=entry.previous_hash,
                payload_hash=entry.payload_hash,
                payload=entry.payload,
            )
            if entry.entry_hash != expected_entry_hash:
                violations.append(f"sequence_{entry.sequence}:entry_hash_mismatch")
            previous_hash = entry.entry_hash

        return EvidenceJournalVerification(
            journal_id=self.journal_id,
            checked_at=timestamp,
            valid=not violations,
            entry_count=len(entries),
            last_entry_hash=previous_hash,
            violations=tuple(violations),
        )


def _canonical_payload(payload: object) -> dict[str, Any]:
    primitive = to_primitive(payload)
    if not isinstance(primitive, dict):
        primitive = {"value": primitive}
    return _sanitize_payload(primitive)


def _sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, dict):
            sanitized[str(key)] = _sanitize_payload(value)
        elif isinstance(value, list):
            sanitized[str(key)] = [_sanitize_payload(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[str(key)] = sanitize_attributes({str(key): value}).get(str(key))
    return sanitized


def _payload_timestamp(payload: object) -> datetime | None:
    for attribute in ("occurred_at", "observed_at", "captured_at", "generated_at", "checked_at"):
        value = getattr(payload, attribute, None)
        if isinstance(value, datetime):
            return require_aware_datetime(value, attribute)
    return None


def _entry_to_record(entry: EvidenceJournalEntry) -> dict[str, Any]:
    return {
        "journal_id": entry.journal_id,
        "sequence": entry.sequence,
        "record_type": entry.record_type.value,
        "occurred_at": entry.occurred_at.isoformat(),
        "previous_hash": entry.previous_hash,
        "payload_hash": entry.payload_hash,
        "entry_hash": entry.entry_hash,
        "payload": entry.payload,
    }


def _entry_from_record(record: dict[str, Any]) -> EvidenceJournalEntry:
    return EvidenceJournalEntry(
        journal_id=str(record["journal_id"]),
        sequence=int(record["sequence"]),
        record_type=EvidenceRecordType(str(record["record_type"])),
        occurred_at=datetime.fromisoformat(str(record["occurred_at"])),
        previous_hash=str(record["previous_hash"]),
        payload_hash=str(record["payload_hash"]),
        entry_hash=str(record["entry_hash"]),
        payload=dict(record["payload"]),
    )


def _entry_hash(
    *,
    journal_id: str,
    sequence: int,
    record_type: EvidenceRecordType,
    occurred_at: datetime,
    previous_hash: str,
    payload_hash: str,
    payload: dict[str, Any],
) -> str:
    return _sha256_json(
        {
            "journal_id": journal_id,
            "sequence": sequence,
            "record_type": record_type.value,
            "occurred_at": require_aware_datetime(occurred_at, "occurred_at").isoformat(),
            "previous_hash": previous_hash,
            "payload_hash": payload_hash,
            "payload": payload,
        }
    )


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(_json_ready(value), sort_keys=True, separators=(",", ":"))


def _json_ready(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return require_aware_datetime(value, "datetime").isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    return value


def _require_sha256_hex(value: str, field_name: str) -> None:
    require_non_empty(value, field_name)
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ObservabilityError(f"{field_name} must be a sha256 hex digest")


def evidence_journal_id_for_path(path: Path) -> str:
    return deterministic_id("journal", path.as_posix())


def append_observability_sink_contents(
    journal: LocalEvidenceJournal,
    sink: LocalObservabilitySink,
) -> tuple[EvidenceJournalEntry, ...]:
    entries: list[EvidenceJournalEntry] = []
    for event in sink.audit_events:
        entries.append(journal.append_audit_event(event))
    for record in sink.logs:
        entries.append(journal.append_log_record(record))
    for point in sink.metric_points:
        entries.append(journal.append_metric_point(point))
    return tuple(entries)
