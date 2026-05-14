import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts" / "ml"


class ModelEvaluationGovernanceContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.manifest = self._fixture("model_evaluation_manifest.valid.json")
        self.benchmark = self._fixture("benchmark_result_record.valid.json")

    def test_model_evaluation_manifest_validates(self):
        result = self.validator.validate("ml", "model_evaluation_manifest", self.manifest)

        self.assertTrue(result.valid, result.errors)

    def test_benchmark_result_record_validates(self):
        result = self.validator.validate("ml", "benchmark_result_record", self.benchmark)

        self.assertTrue(result.valid, result.errors)

    def test_model_evaluation_manifest_is_local_and_non_executable(self):
        self.assertEqual(self.manifest["evaluation_mode"], "OPEN_LOOP")
        self.assertTrue(self.manifest["calibration_required"])
        self.assertTrue(self.manifest["cost_model_required"])
        self.assertTrue(self.manifest["slippage_model_required"])
        self.assertTrue(self.manifest["risk_constraints_required"])
        self.assertFalse(self.manifest["network_allowed"])
        self.assertFalse(self.manifest["credentials_allowed"])
        self.assertFalse(self.manifest["runtime_training_allowed"])
        self.assertFalse(self.manifest["execution_allowed"])

    def test_benchmark_result_cannot_approve_risk_execution_or_production(self):
        self.assertFalse(self.benchmark["production_approval_allowed"])
        self.assertFalse(self.benchmark["risk_approval_allowed"])
        self.assertFalse(self.benchmark["execution_allowed"])

    def test_benchmark_tracks_required_failure_modes(self):
        failure_modes = set(self.benchmark["failure_modes_checked"])

        for failure_mode in (
            "data_leakage",
            "lookahead_bias",
            "survivorship_bias",
            "stale_data",
            "calibration_drift",
            "overfitting",
            "cherry_picked_period",
            "missing_costs",
            "missing_slippage",
            "unstable_closed_loop_feedback",
        ):
            with self.subTest(failure_mode=failure_mode):
                self.assertIn(failure_mode, failure_modes)

    def test_manifest_rejects_execution_enablement(self):
        payload = copy.deepcopy(self.manifest)
        payload["execution_allowed"] = True

        result = self.validator.validate("ml", "model_evaluation_manifest", payload)

        self.assertFalse(result.valid)

    def test_benchmark_rejects_production_approval(self):
        payload = copy.deepcopy(self.benchmark)
        payload["production_approval_allowed"] = True

        result = self.validator.validate("ml", "benchmark_result_record", payload)

        self.assertFalse(result.valid)

    def _fixture(self, name):
        with (FIXTURE_ROOT / name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
