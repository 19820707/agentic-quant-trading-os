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
        self.evaluation = self._fixture("safe_policy_evaluation_report.valid.json")
        self.stress = self._fixture("scenario_stress_test_report.valid.json")
        self.promotion = self._fixture("policy_promotion_gate.valid.json")

    def test_rl_safety_policy_validates(self):
        result = self.validator.validate("ml", "rl_safety_policy", self.policy)

        self.assertTrue(result.valid, result.errors)

    def test_rl_constraint_violation_record_validates(self):
        result = self.validator.validate("ml", "rl_constraint_violation_record", self.violation)

        self.assertTrue(result.valid, result.errors)

    def test_recovery_policy_decision_validates(self):
        result = self.validator.validate("ml", "recovery_policy_decision", self.recovery)

        self.assertTrue(result.valid, result.errors)

    def test_safe_policy_evaluation_report_validates(self):
        result = self.validator.validate("ml", "safe_policy_evaluation_report", self.evaluation)

        self.assertTrue(result.valid, result.errors)

    def test_scenario_stress_test_report_validates(self):
        result = self.validator.validate("ml", "scenario_stress_test_report", self.stress)

        self.assertTrue(result.valid, result.errors)

    def test_policy_promotion_gate_validates(self):
        result = self.validator.validate("ml", "policy_promotion_gate", self.promotion)

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

    def test_safe_policy_evaluation_is_not_promotion_approval(self):
        self.assertEqual(self.evaluation["evaluation_scope"], "research_only")
        self.assertEqual(self.evaluation["promotion_recommendation"], "RESEARCH_ONLY")
        self.assertTrue(self.evaluation["safety_layer_required"])
        self.assertTrue(self.evaluation["deterministic_gateway_required"])
        self.assertTrue(self.evaluation["manual_review_required"])
        self.assertTrue(self.evaluation["constraint_summary"]["zero_unauthorized_execution"])
        self.assertTrue(self.evaluation["constraint_summary"]["zero_credential_access"])
        self.assertTrue(self.evaluation["constraint_summary"]["zero_risk_gateway_bypass"])
        self.assertFalse(self.evaluation["approved_for_promotion"])
        self.assertFalse(self.evaluation["network_allowed"])
        self.assertFalse(self.evaluation["credentials_allowed"])
        self.assertFalse(self.evaluation["policy_execution_allowed"])
        self.assertFalse(self.evaluation["risk_approval_allowed"])
        self.assertFalse(self.evaluation["execution_allowed"])
        self.assertFalse(self.evaluation["production_enabled"])

    def test_stress_report_blocks_failure_without_execution(self):
        self.assertEqual(self.stress["market_regime"], "liquidity_shock")
        self.assertEqual(self.stress["policy_response"], "freeze_policy")
        self.assertEqual(self.stress["failure_mode"], "constraint_breach")
        self.assertFalse(self.stress["stress_passed"])
        self.assertTrue(self.stress["blocked_on_failure"])
        self.assertTrue(self.stress["manual_review_required"])
        self.assertFalse(self.stress["network_allowed"])
        self.assertFalse(self.stress["credentials_allowed"])
        self.assertFalse(self.stress["policy_execution_allowed"])
        self.assertFalse(self.stress["risk_approval_allowed"])
        self.assertFalse(self.stress["execution_allowed"])

    def test_promotion_gate_blocks_runtime_and_dependency_approval(self):
        self.assertEqual(self.promotion["promotion_stage"], "blocked")
        self.assertEqual(self.promotion["approval_status"], "HUMAN_REVIEW_REQUIRED")
        self.assertTrue(self.promotion["safety_layer_required"])
        self.assertTrue(self.promotion["deterministic_gateway_required"])
        self.assertTrue(self.promotion["human_governance_required"])
        self.assertFalse(self.promotion["approved_for_paper"])
        self.assertFalse(self.promotion["approved_for_market_execution"])
        self.assertFalse(self.promotion["pyproject_change_allowed"])
        self.assertFalse(self.promotion["dependency_allowed"])
        self.assertFalse(self.promotion["network_allowed"])
        self.assertFalse(self.promotion["credentials_allowed"])
        self.assertFalse(self.promotion["runtime_training_allowed"])
        self.assertFalse(self.promotion["policy_execution_allowed"])
        self.assertFalse(self.promotion["risk_approval_allowed"])
        self.assertFalse(self.promotion["execution_allowed"])
        self.assertFalse(self.promotion["production_enabled"])

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

    def test_evaluation_rejects_promotion_approval(self):
        payload = copy.deepcopy(self.evaluation)
        payload["approved_for_promotion"] = True

        result = self.validator.validate("ml", "safe_policy_evaluation_report", payload)

        self.assertFalse(result.valid)

    def test_promotion_gate_rejects_dependency_approval(self):
        payload = copy.deepcopy(self.promotion)
        payload["dependency_allowed"] = True

        result = self.validator.validate("ml", "policy_promotion_gate", payload)

        self.assertFalse(result.valid)

    def _fixture(self, name):
        with (FIXTURE_ROOT / name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
