import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts" / "ml"


class SafeRLGovernanceContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.policy = self._fixture("rl_safety_policy.valid.json")
        self.violation = self._fixture("rl_constraint_violation_record.valid.json")
        self.recovery = self._fixture("recovery_policy_decision.valid.json")

    def test_rl_safety_policy_validates(self):
        result = self.validator.validate("ml", "rl_safety_policy", self.policy)

        self.assertTrue(result.valid, result.errors)

    def test_rl_constraint_violation_record_validates(self):
        result = self.validator.validate("ml", "rl_constraint_violation_record", self.violation)

        self.assertTrue(result.valid, result.errors)

    def test_recovery_policy_decision_validates(self):
        result = self.validator.validate("ml", "recovery_policy_decision", self.recovery)

        self.assertTrue(result.valid, result.errors)

    def test_rl_safety_policy_requires_safety_layer_and_gateway(self):
        self.assertTrue(self.policy["safety_layer_required"])
        self.assertTrue(self.policy["deterministic_gateway_required"])
        self.assertTrue(self.policy["audit_required"])
        self.assertFalse(self.policy["network_allowed"])
        self.assertFalse(self.policy["credentials_allowed"])
        self.assertFalse(self.policy["runtime_training_allowed"])
        self.assertFalse(self.policy["policy_execution_allowed"])
        self.assertFalse(self.policy["risk_approval_allowed"])
        self.assertFalse(self.policy["execution_allowed"])

    def test_rl_policy_forbids_direct_execution_and_credentials(self):
        forbidden = set(self.policy["forbidden_action_space"])

        self.assertIn("execute_order", forbidden)
        self.assertIn("approve_risk", forbidden)
        self.assertIn("access_credentials", forbidden)
        self.assertIn("call_private_endpoint", forbidden)

    def test_constraint_violation_is_blocked_and_reviewed(self):
        self.assertEqual(self.violation["severity"], "critical")
        self.assertTrue(self.violation["blocked"])
        self.assertTrue(self.violation["audit_required"])
        self.assertTrue(self.violation["manual_review_required"])
        self.assertTrue(self.violation["recovery_required"])
        self.assertFalse(self.violation["execution_allowed"])

    def test_recovery_decision_is_non_executable(self):
        self.assertEqual(self.recovery["proposed_recovery_action"], "FREEZE_POLICY")
        self.assertTrue(self.recovery["deterministic_gateway_required"])
        self.assertTrue(self.recovery["manual_review_required"])
        self.assertFalse(self.recovery["network_allowed"])
        self.assertFalse(self.recovery["credentials_allowed"])
        self.assertFalse(self.recovery["risk_approval_allowed"])
        self.assertFalse(self.recovery["execution_allowed"])

    def test_policy_rejects_execution_enablement(self):
        payload = copy.deepcopy(self.policy)
        payload["execution_allowed"] = True

        result = self.validator.validate("ml", "rl_safety_policy", payload)

        self.assertFalse(result.valid)

    def test_recovery_rejects_risk_approval(self):
        payload = copy.deepcopy(self.recovery)
        payload["risk_approval_allowed"] = True

        result = self.validator.validate("ml", "recovery_policy_decision", payload)

        self.assertFalse(result.valid)

    def _fixture(self, name):
        with (FIXTURE_ROOT / name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
