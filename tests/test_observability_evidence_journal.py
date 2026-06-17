from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
from tempfile import TemporaryDirectory
from pathlib import Path
import unittest

from observability import (
    EvidenceRecordType,
    LocalEvidenceJournal,
    LocalObservabilitySink,
    LogLevel,
    ObservabilityError,
    append_observability_sink_contents,
    evidence_journal_id_for_path,
)
from observability.local import MetricKind, MetricPoint, StructuredLogRecord
from packages.domain import AuditEvent, AuditEventType, CausationId, CorrelationId


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)


def audit_event() -> AuditEvent:
    return AuditEvent(
        audit_event_id="audit_fixture",
        event_type=AuditEventType.RISK_CHECKED,
        occurred_at=NOW,
        correlation_id=CorrelationId("corr_evidence"),
        causation_id=CausationId("cause_evidence"),
        actor="risk",
        subject="risk_result",
        outcome="review",
        metadata={"safe": True},
    )


def log_record() -> StructuredLogRecord:
    return StructuredLogRecord(
        log_id="log_fixture",
        occurred_at=NOW,
        level=LogLevel.INFO,
        component="risk",
        message="local evidence",
        correlation_id=CorrelationId("corr_evidence"),
        attributes={"safe": "yes"},
    )


def metric_point() -> MetricPoint:
    return MetricPoint(
        name="risk_checks_total",
        kind=MetricKind.COUNTER,
        value=Decimal("1"),
        observed_at=NOW,
        tags={"component": "risk"},
    )


class EvidenceJournalTests(unittest.TestCase):
    def test_journal_requires_jsonl_suffix(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaises(ObservabilityError):
                LocalEvidenceJournal(Path(directory) / "evidence.json")

    def test_append_creates_hash_chain_and_verifies(self) -> None:
        with TemporaryDirectory() as directory:
            journal = LocalEvidenceJournal(Path(directory) / "evidence.jsonl")

            first = journal.append_audit_event(audit_event())
            second = journal.append_log_record(log_record())
            third = journal.append_metric_point(metric_point())
            verification = journal.verify(checked_at=NOW)

            self.assertEqual(first.sequence, 1)
            self.assertEqual(second.sequence, 2)
            self.assertEqual(third.sequence, 3)
            self.assertEqual(second.previous_hash, first.entry_hash)
            self.assertEqual(third.previous_hash, second.entry_hash)
            self.assertTrue(verification.valid)
            self.assertEqual(verification.entry_count, 3)
            self.assertEqual(verification.last_entry_hash, third.entry_hash)

    def test_entries_roundtrip_with_record_types(self) -> None:
        with TemporaryDirectory() as directory:
            journal = LocalEvidenceJournal(Path(directory) / "evidence.jsonl")

            journal.append_audit_event(audit_event())
            journal.append_log_record(log_record())
            journal.append_metric_point(metric_point())
            entries = journal.read_entries()

            self.assertEqual(
                [entry.record_type for entry in entries],
                [EvidenceRecordType.AUDIT_EVENT, EvidenceRecordType.LOG_RECORD, EvidenceRecordType.METRIC_POINT],
            )
            self.assertEqual(entries[0].payload["actor"], "risk")
            self.assertEqual(entries[2].payload["value"], "1")

    def test_tamper_detection_reports_payload_and_entry_hash_mismatch(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "evidence.jsonl"
            journal = LocalEvidenceJournal(path)
            journal.append_audit_event(audit_event())

            line = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            line["payload"]["actor"] = "changed-risk"
            path.write_text(json.dumps(line, sort_keys=True) + "\n", encoding="utf-8")

            verification = journal.verify(checked_at=NOW)

            self.assertFalse(verification.valid)
            self.assertIn("sequence_1:payload_hash_mismatch", verification.violations)
            self.assertIn("sequence_1:entry_hash_mismatch", verification.violations)
            with self.assertRaises(ObservabilityError):
                journal.read_entries()

    def test_sensitive_payload_attributes_are_redacted_before_hashing(self) -> None:
        with TemporaryDirectory() as directory:
            journal = LocalEvidenceJournal(Path(directory) / "evidence.jsonl")
            sensitive_key = "api" + "_key"
            entry = journal.append(
                EvidenceRecordType.GENERIC_EVIDENCE,
                {"component": "risk", sensitive_key: "local-test-value"},
                occurred_at=NOW,
            )

            self.assertEqual(entry.payload[sensitive_key], "[REDACTED]")
            self.assertTrue(journal.verify(checked_at=NOW).valid)

    def test_journal_id_for_path_is_deterministic(self) -> None:
        path = Path("local") / "evidence.jsonl"

        self.assertEqual(evidence_journal_id_for_path(path), evidence_journal_id_for_path(path))

    def test_observability_sink_contents_can_be_exported_to_journal(self) -> None:
        with TemporaryDirectory() as directory:
            sink = LocalObservabilitySink()
            sink.record_audit_event(audit_event())
            sink.log(
                level=LogLevel.INFO,
                component="risk",
                message="evidence export",
                correlation_id=CorrelationId("corr_evidence"),
                occurred_at=NOW,
            )
            sink.increment_counter("risk_checks_total", observed_at=NOW, tags={"component": "risk"})
            journal = LocalEvidenceJournal(Path(directory) / "evidence.jsonl")

            entries = append_observability_sink_contents(journal, sink)

            self.assertEqual(len(entries), 5)
            self.assertTrue(journal.verify(checked_at=NOW).valid)
            self.assertEqual(journal.read_entries()[0].record_type, EvidenceRecordType.AUDIT_EVENT)


if __name__ == "__main__":
    unittest.main()
