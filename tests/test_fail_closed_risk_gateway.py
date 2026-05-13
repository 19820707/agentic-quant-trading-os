import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from packages.contracts import ContractValidator
from packages.sdk.risk_gateway import FailClosedRiskGateway, FailClosedRiskLimits


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "order_intent.valid.json"


class FailClosedRiskGatewayTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        with FIXTURE.open(encoding="utf-8") as fixture_file:
            self.order_intent = json.load(fixture_file)

    def test_rejects_valid_order_intent_with_schema_valid_risk_decision(self):
        decision = self._evaluate()

        result = self.validator.validate("trading", "risk_decision", decision)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(decision["decision"], "REJECT")
        self.assertFalse(decision["approved_for_execution"])
        self.assertEqual(decision["approved_quantity"], 0.0)
        self.assertEqual(decision["approved_notional"], 0.0)

    def test_applies_theoretical_limit_checks_but_fails_closed(self):
        decision = self._evaluate()
        checks = {check["check_name"]: check for check in decision["checks"]}

        self.assertEqual(checks["global_kill_switch"]["result"], "FAIL")
        self.assertEqual(checks["max_order_notional"]["result"], "FAIL")
        self.assertEqual(checks["max_position_notional"]["result"], "FAIL")
        self.assertEqual(checks["max_total_gross_exposure"]["result"], "FAIL")
        self.assertEqual(checks["max_intraday_drawdown"]["result"], "FAIL")
        self.assertTrue(decision["kill_switch_triggered"])
        self.assertTrue(decision["manual_approval_required"])

    def test_computes_original_notional_without_allowing_execution(self):
        decision = self._evaluate()

        self.assertEqual(decision["original_quantity"], 0.25)
        self.assertEqual(decision["original_notional"], 7500.0)
        self.assertEqual(decision["max_allowed_notional"], 0.0)
        self.assertFalse(decision["approved_for_execution"])

    def test_uses_custom_limits_without_ever_approving(self):
        gateway = FailClosedRiskGateway(
            FailClosedRiskLimits(
                limit_profile_id="fixture_custom_limits",
                max_order_notional=100000.0,
                max_position_notional=100000.0,
                max_total_gross_exposure=100000.0,
                max_intraday_drawdown=0.2,
            )
        )

        decision = gateway.evaluate_order_intent(
            self.order_intent,
            evaluated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(decision["limit_profile_id"], "fixture_custom_limits")
        self.assertEqual(decision["decision"], "REJECT")
        self.assertFalse(decision["approved_for_execution"])

    def test_preserves_trace_and_correlation_ids(self):
        decision = self._evaluate()

        self.assertEqual(decision["trace_id"], self.order_intent["trace_id"])
        self.assertEqual(decision["correlation_id"], self.order_intent["correlation_id"])
        self.assertEqual(decision["order_intent_id"], self.order_intent["order_intent_id"])

    def test_does_not_read_credentials_or_network_configuration(self):
        decision = self._evaluate()

        self.assertFalse(decision["metadata"]["network_allowed"])
        self.assertFalse(decision["metadata"]["credentials_allowed"])
        serialized = json.dumps(decision).lower()
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("private_key", serialized)
        self.assertNotIn("secret", serialized)

    def test_input_payload_is_not_mutated(self):
        original = copy.deepcopy(self.order_intent)

        self._evaluate()

        self.assertEqual(self.order_intent, original)

    def _evaluate(self):
        gateway = FailClosedRiskGateway()
        return gateway.evaluate_order_intent(
            self.order_intent,
            evaluated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )


if __name__ == "__main__":
    unittest.main()
