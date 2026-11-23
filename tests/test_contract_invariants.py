"""Tests for cross-field invariants on trading contracts.

Each case starts from a valid fixture and breaks exactly one rule, so a failure
points at the rule that stopped working.
"""

import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator, check_invariants


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "contracts"


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.valid.json").read_text(encoding="utf-8"))


class ContractInvariantTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def _assert_rejected(self, name: str, changes: dict, expected_fragment: str, remove: tuple = ()):
        payload = copy.deepcopy(_fixture(name))
        payload.update(changes)
        for field in remove:
            payload.pop(field, None)

        result = self.validator.validate("trading", name, payload)

        self.assertFalse(result.valid, f"{name} with {changes} should be rejected")
        self.assertTrue(
            any("invariant violated" in error and expected_fragment in error for error in result.errors),
            result.errors,
        )

    def test_valid_trading_fixtures_satisfy_all_invariants(self):
        for name in ("order_intent", "risk_decision", "approved_order", "execution_report"):
            with self.subTest(name=name):
                self.assertEqual(check_invariants("trading", name, _fixture(name)), [])
                self.assertTrue(self.validator.validate("trading", name, _fixture(name)).valid)

    def test_rejecting_decisions_cannot_be_approved_for_execution(self):
        for decision in ("REJECT", "CANCEL_ALL", "REQUIRE_MANUAL_APPROVAL"):
            with self.subTest(decision=decision):
                self._assert_rejected("risk_decision", {"decision": decision}, "approved_for_execution is true but decision")

    def test_kill_switch_blocks_approval(self):
        self._assert_rejected(
            "risk_decision",
            {"kill_switch_triggered": True, "kill_switch_scope": "GLOBAL"},
            "kill_switch_triggered is true",
        )

    def test_kill_switch_flag_and_scope_must_agree(self):
        self._assert_rejected(
            "risk_decision",
            {"approved_for_execution": False, "approved_quantity": 0, "approved_notional": 0, "decision": "REJECT",
             "kill_switch_triggered": True, "kill_switch_scope": "NONE"},
            "kill_switch_scope is NONE",
        )
        self._assert_rejected(
            "risk_decision",
            {"kill_switch_triggered": False, "kill_switch_scope": "ACCOUNT"},
            "kill_switch_triggered is false",
        )

    def test_manual_approval_and_hard_limits_block_approval(self):
        self._assert_rejected("risk_decision", {"manual_approval_required": True}, "manual_approval_required")
        self._assert_rejected(
            "risk_decision", {"hard_limits_triggered": ["max_order_notional"]}, "hard limits are triggered"
        )

    def test_failed_high_severity_check_blocks_approval(self):
        checks = copy.deepcopy(_fixture("risk_decision")["checks"])
        checks[0]["result"] = "FAIL"
        checks[0]["severity"] = "CRITICAL"

        self._assert_rejected("risk_decision", {"checks": checks}, "failed with severity CRITICAL")

    def test_failed_low_severity_check_does_not_block_approval(self):
        payload = _fixture("risk_decision")
        payload["checks"][0]["result"] = "FAIL"
        payload["checks"][0]["severity"] = "WARNING"

        self.assertEqual(check_invariants("trading", "risk_decision", payload), [])

    def test_approved_amounts_cannot_exceed_original_or_limit(self):
        self._assert_rejected("risk_decision", {"approved_quantity": 9.0}, "approved_quantity exceeds")
        self._assert_rejected("risk_decision", {"approved_notional": 9_000_000.0}, "approved_notional exceeds")
        self._assert_rejected("risk_decision", {"max_allowed_notional": 1.0}, "exceeds max_allowed_notional")

    def test_unapproved_decision_cannot_carry_an_approved_quantity(self):
        self._assert_rejected(
            "risk_decision",
            {"decision": "REJECT", "approved_for_execution": False},
            "approved_quantity is positive",
        )

    def test_resize_must_reduce_quantity(self):
        original = _fixture("risk_decision")["original_quantity"]

        self._assert_rejected("risk_decision", {"approved_quantity": original}, "decision is RESIZE")

    def test_priced_order_types_require_their_prices(self):
        for name in ("order_intent", "approved_order"):
            with self.subTest(name=name):
                self._assert_rejected(name, {}, "requires limit_price", remove=("limit_price",))
                self._assert_rejected(name, {"order_type": "STOP_LIMIT"}, "requires stop_price")

    def test_post_only_market_order_is_rejected(self):
        self._assert_rejected(
            "order_intent", {"order_type": "MARKET", "post_only": True}, "post_only cannot be combined"
        )

    def test_approved_order_mode_and_queue_must_agree(self):
        self._assert_rejected(
            "approved_order", {"status": "QUEUED_FOR_EXECUTION"}, "PAPER cannot be queued for live execution"
        )

    def test_approved_order_cannot_carry_triggered_hard_limits(self):
        summary = copy.deepcopy(_fixture("approved_order")["risk_summary"])
        summary["hard_limits_triggered"] = ["max_leverage"]

        self._assert_rejected("approved_order", {"risk_summary": summary}, "triggered hard limits")

    def test_execution_report_quantities_must_add_up(self):
        self._assert_rejected("execution_report", {"filled_quantity": 5.0}, "filled_quantity exceeds")
        self._assert_rejected("execution_report", {"remaining_quantity": 0.05}, "remaining_quantity does not equal")
        self._assert_rejected(
            "execution_report",
            {"filled_quantity": 0.05, "remaining_quantity": 0.05, "last_fill_quantity": 0.05},
            "requires filled_quantity to equal requested_quantity",
        )

    def test_paper_execution_report_cannot_claim_broker_events(self):
        self._assert_rejected("execution_report", {"event_type": "BROKER_ACK"}, "not valid for execution_mode PAPER")

    def test_live_execution_report_cannot_use_paper_statuses(self):
        self._assert_rejected(
            "execution_report", {"execution_mode": "CONTROLLED_LIVE"}, "not valid for execution_mode CONTROLLED_LIVE"
        )

    def test_contracts_without_invariants_and_non_mapping_payloads_are_ignored(self):
        self.assertEqual(check_invariants("audit", "audit_event", {"anything": True}), [])
        self.assertEqual(check_invariants("trading", "risk_decision", ["not", "a", "mapping"]), [])

    def test_schema_suffix_is_accepted(self):
        payload = _fixture("risk_decision")
        payload["decision"] = "REJECT"

        self.assertTrue(check_invariants("trading", "risk_decision.schema.json", payload))


if __name__ == "__main__":
    unittest.main()
