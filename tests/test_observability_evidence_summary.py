from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from observability import (
    EvidenceJournalReference,
    EvidenceRecordType,
    LocalEvidenceJournal,
    ObservabilityError,
    summarize_loop_evidence,
)


NOW = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)


class EvidenceSummaryTests(unittest.TestCase):
    def test_empty_summary_is_local_safe_and_missing_required_loop_report(self) -> None:
        summary = summarize_loop_evidence((), checked_at=NOW)

        self.assertEqual(summary.journal_count, 0)
        self.assertEqual(summary.integrity_score, Decimal("1.000000"))
        self.assertEqual(summary.coverage_score, Decimal("0.000000"))
        self.assertEqual(summary.missing_record_types, ("LOOP_RUN_REPORT",))
        self.assertFalse(summary.tamper_detected)
        self.assertFalse(summary.network_allowed)
        self.assertFalse(summary.credentials_allowed)
        self.assertFalse(summary.external_services_used)
        self.assertFalse(summary.remediation_allowed)
        self.assertFalse(summary.trading_allowed)
        self.assertFalse(summary.execution_allowed)

    def test_summary_scores_valid_journal_and_required_coverage(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "loop.jsonl"
            journal = LocalEvidenceJournal(path, journal_id="loop-journal")
            journal.append(EvidenceRecordType.LOOP_RUN_REPORT, {"decision": "continue"}, occurred_at=NOW)
            journal.append(EvidenceRecordType.GENERIC_EVIDENCE, {"component": "loop"}, occurred_at=NOW)

            summary = summarize_loop_evidence(
                (EvidenceJournalReference(path=path, journal_id="loop-journal"),),
                checked_at=NOW,
            )

            self.assertEqual(summary.journal_count, 1)
            self.assertEqual(summary.valid_journal_count, 1)
            self.assertEqual(summary.invalid_journal_count, 0)
            self.assertEqual(summary.total_entry_count, 2)
            self.assertEqual(summary.integrity_score, Decimal("1.000000"))
            self.assertEqual(summary.coverage_score, Decimal("1.000000"))
            self.assertEqual(summary.missing_record_types, ())
            self.assertEqual(summary.record_type_counts["LOOP_RUN_REPORT"], 1)
            self.assertFalse(summary.tamper_detected)

    def test_summary_detects_tamper_without_external_services(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "loop.jsonl"
            journal = LocalEvidenceJournal(path, journal_id="loop-journal")
            journal.append(EvidenceRecordType.LOOP_RUN_REPORT, {"decision": "continue"}, occurred_at=NOW)
            record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
            record["payload"]["decision"] = "changed"
            path.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")

            summary = summarize_loop_evidence(
                (EvidenceJournalReference(path=path, journal_id="loop-journal"),),
                checked_at=NOW,
            )

            self.assertEqual(summary.valid_journal_count, 0)
            self.assertEqual(summary.invalid_journal_count, 1)
            self.assertEqual(summary.integrity_score, Decimal("0.000000"))
            self.assertTrue(summary.tamper_detected)
            self.assertTrue(any("payload_hash_mismatch" in item for item in summary.violations))
            self.assertFalse(summary.network_allowed)
            self.assertFalse(summary.credentials_allowed)

    def test_summary_serializes_for_control_plane_payloads(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "loop.jsonl"
            journal = LocalEvidenceJournal(path, journal_id="loop-journal")
            journal.append(EvidenceRecordType.LOOP_RUN_REPORT, {"decision": "continue"}, occurred_at=NOW)

            payload = summarize_loop_evidence(
                (EvidenceJournalReference(path=path, journal_id="loop-journal"),),
                checked_at=NOW,
            ).to_dict()

            self.assertEqual(payload["integrity_score"], "1.000000")
            self.assertEqual(payload["coverage_score"], "1.000000")
            self.assertEqual(payload["journal_summaries"][0]["journal_id"], "loop-journal")
            self.assertFalse(payload["network_allowed"])
            self.assertFalse(payload["credentials_allowed"])

    def test_reference_requires_jsonl_suffix(self) -> None:
        with self.assertRaises(ObservabilityError):
            EvidenceJournalReference(path=Path("bad.txt"), journal_id="loop-journal")


if __name__ == "__main__":
    unittest.main()
