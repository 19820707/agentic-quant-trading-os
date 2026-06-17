from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from observability import (
    EvidenceGateDecision,
    EvidenceJournalReference,
    EvidenceQualityGatePolicy,
    EvidenceRecordType,
    LocalEvidenceJournal,
    ObservabilityError,
    evaluate_evidence_quality_gate,
    summarize_loop_evidence,
)


NOW = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)


class EvidenceQualityGateTests(unittest.TestCase):
    def test_gate_passes_complete_valid_local_evidence(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "loop.jsonl"
            journal = LocalEvidenceJournal(path, journal_id="loop-journal")
            journal.append(EvidenceRecordType.LOOP_RUN_REPORT, {"decision": "continue"}, occurred_at=NOW)
            summary = summarize_loop_evidence(
                (EvidenceJournalReference(path=path, journal_id="loop-journal"),),
                checked_at=NOW,
            )

            result = evaluate_evidence_quality_gate(summary)

            self.assertEqual(result.decision, EvidenceGateDecision.PASS)
            self.assertTrue(result.promotion_allowed)
            self.assertIn("evidence_quality_gate_passed", result.reasons)
            self.assertFalse(result.remediation_allowed)
            self.assertFalse(result.trading_allowed)
            self.assertFalse(result.execution_allowed)
            self.assertFalse(result.network_allowed)
            self.assertFalse(result.credentials_allowed)

    def test_gate_blocks_when_required_evidence_is_missing(self) -> None:
        summary = summarize_loop_evidence((), checked_at=NOW)

        result = evaluate_evidence_quality_gate(summary)

        self.assertEqual(result.decision, EvidenceGateDecision.BLOCK)
        self.assertFalse(result.promotion_allowed)
        self.assertIn("no_evidence_entries", result.reasons)
        self.assertIn("coverage_score_below_policy", result.reasons)
        self.assertIn("missing_required_evidence", result.reasons)

    def test_gate_blocks_when_tamper_is_detected(self) -> None:
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

            result = evaluate_evidence_quality_gate(summary)

            self.assertEqual(result.decision, EvidenceGateDecision.BLOCK)
            self.assertFalse(result.promotion_allowed)
            self.assertIn("tamper_detected", result.reasons)
            self.assertIn("integrity_score_below_policy", result.reasons)
            self.assertIn("summary_violations_present", result.reasons)

    def test_gate_policy_can_require_review_without_blocking_rules(self) -> None:
        summary = summarize_loop_evidence((), checked_at=NOW)
        policy = EvidenceQualityGatePolicy(
            min_integrity_score=Decimal("0"),
            min_coverage_score=Decimal("0"),
            require_entries=False,
            block_on_tamper=False,
            block_on_missing_required_evidence=False,
        )

        result = evaluate_evidence_quality_gate(summary, policy=policy)

        self.assertEqual(result.decision, EvidenceGateDecision.PASS)
        self.assertTrue(result.promotion_allowed)

    def test_policy_rejects_invalid_thresholds(self) -> None:
        with self.assertRaises(ObservabilityError):
            EvidenceQualityGatePolicy(min_integrity_score=Decimal("1.1"))

        with self.assertRaises(ObservabilityError):
            EvidenceQualityGatePolicy(min_coverage_score=Decimal("-0.1"))

    def test_gate_serializes_for_control_plane(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "loop.jsonl"
            journal = LocalEvidenceJournal(path, journal_id="loop-journal")
            journal.append(EvidenceRecordType.LOOP_RUN_REPORT, {"decision": "continue"}, occurred_at=NOW)
            summary = summarize_loop_evidence(
                (EvidenceJournalReference(path=path, journal_id="loop-journal"),),
                checked_at=NOW,
            )

            payload = evaluate_evidence_quality_gate(summary).to_dict()

            self.assertEqual(payload["decision"], "pass")
            self.assertEqual(payload["integrity_score"], "1.000000")
            self.assertEqual(payload["coverage_score"], "1.000000")
            self.assertTrue(payload["promotion_allowed"])
            self.assertFalse(payload["network_allowed"])
            self.assertFalse(payload["credentials_allowed"])


if __name__ == "__main__":
    unittest.main()
