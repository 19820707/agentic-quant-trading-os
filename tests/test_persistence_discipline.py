import unittest
from decimal import Decimal

from packages.sdk.persistence_discipline import (
    PersistenceDecision,
    PersistenceDisciplineEngine,
    PersistenceDisciplineError,
    PersistenceHealth,
    PersistenceIteration,
    build_default_persistence_discipline_engine,
)


class PersistenceDisciplineTests(unittest.TestCase):
    def setUp(self):
        self.engine = PersistenceDisciplineEngine()

    def test_no_history_reduces_scope_to_next_small_step(self):
        report = self.engine.evaluate(())

        self.assertEqual(report.decision, PersistenceDecision.REDUCE_SCOPE)
        self.assertEqual(report.health, PersistenceHealth.WATCH)
        self.assertIn("no_iteration_history", report.reasons)
        self.assertIn("define_next_small_testable_step", report.required_actions)
        self.assertFalse(report.autonomous_remediation_allowed)
        self.assertFalse(report.runtime_change_allowed)
        self.assertFalse(report.trading_allowed)
        self.assertFalse(report.execution_allowed)
        self.assertFalse(report.network_allowed)
        self.assertFalse(report.credentials_allowed)

    def test_evidenced_progress_streak_can_continue_without_operational_permission(self):
        report = self.engine.evaluate(
            (
                PersistenceIteration("iter_001", True, True, ("unit:test",)),
                PersistenceIteration("iter_002", True, True, ("audit:green",)),
            )
        )

        self.assertEqual(report.decision, PersistenceDecision.CONTINUE)
        self.assertEqual(report.health, PersistenceHealth.STABLE)
        self.assertEqual(report.consecutive_progress_count, 2)
        self.assertEqual(report.persistence_score, Decimal("1.000000"))
        self.assertIn("evidenced_progress_streak", report.reasons)
        self.assertFalse(report.runtime_change_allowed)
        self.assertFalse(report.execution_allowed)

    def test_completed_work_without_evidence_reduces_scope(self):
        report = self.engine.evaluate(
            (
                PersistenceIteration("iter_001", True, True, ()),
                PersistenceIteration("iter_002", True, True, ("ci:green",)),
            )
        )

        self.assertEqual(report.decision, PersistenceDecision.REDUCE_SCOPE)
        self.assertEqual(report.evidence_gap_count, 1)
        self.assertIn("completed_work_missing_evidence", report.reasons)
        self.assertIn("attach_validation_evidence", report.required_actions)

    def test_regression_requires_human_review(self):
        report = self.engine.evaluate(
            (
                PersistenceIteration("iter_001", True, True, ("ci:green",)),
                PersistenceIteration("iter_002", True, False, ("ci:failed",), regression_detected=True),
            )
        )

        self.assertEqual(report.decision, PersistenceDecision.REQUIRE_HUMAN_REVIEW)
        self.assertEqual(report.health, PersistenceHealth.DEGRADED)
        self.assertEqual(report.regression_count, 1)
        self.assertIn("regression_detected", report.reasons)

    def test_three_consecutive_blockers_block(self):
        report = self.engine.evaluate(
            (
                PersistenceIteration("iter_001", False, False, ("ci:failed",), blockers=("ci_failure",)),
                PersistenceIteration("iter_002", False, False, ("ci:failed",), blockers=("audit_failure",)),
                PersistenceIteration("iter_003", False, False, ("ci:failed",), blockers=("same_failure",)),
            )
        )

        self.assertEqual(report.decision, PersistenceDecision.BLOCK)
        self.assertEqual(report.health, PersistenceHealth.BLOCKED)
        self.assertEqual(report.consecutive_blocked_count, 3)
        self.assertIn("three_consecutive_blocked_iterations", report.reasons)
        self.assertIn("produce_rollback_or_recovery_plan", report.required_actions)

    def test_report_serializes(self):
        report = self.engine.evaluate(
            (
                PersistenceIteration("iter_001", True, True, ("ci:green",)),
                PersistenceIteration("iter_002", True, True, ("audit:green",)),
            )
        )
        payload = report.to_dict()

        self.assertEqual(payload["decision"], "continue")
        self.assertEqual(payload["persistence_score"], "1.000000")
        self.assertFalse(payload["network_allowed"])
        self.assertFalse(payload["credentials_allowed"])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(PersistenceDisciplineError):
            PersistenceIteration("", True, True)

        with self.assertRaises(PersistenceDisciplineError):
            PersistenceIteration("iter", True, True, ("",))

    def test_factory_returns_engine(self):
        self.assertIsInstance(build_default_persistence_discipline_engine(), PersistenceDisciplineEngine)

    def test_module_exposes_no_operational_methods(self):
        import packages.sdk.persistence_discipline as persistence_discipline

        forbidden_names = {
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "auto_merge",
            "write_to_main",
            "execute",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(persistence_discipline)))


if __name__ == "__main__":
    unittest.main()
