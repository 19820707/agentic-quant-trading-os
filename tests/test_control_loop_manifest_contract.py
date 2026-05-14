import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "governance" / "control_loop_manifest.valid.json"


class ControlLoopManifestContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.fixture = self._fixture()

    def test_control_loop_manifest_fixture_validates(self):
        result = self.validator.validate("governance", "control_loop_manifest", self.fixture)

        self.assertTrue(result.valid, result.errors)

    def test_control_loop_manifest_maps_required_reference_stages(self):
        stages = {stage["reference_stage"]: stage for stage in self.fixture["stages"]}

        for stage_name in ("PERCEPTION", "PREDICTION", "PLANNING", "CONTROL", "ACTUATION"):
            with self.subTest(stage=stage_name):
                self.assertIn(stage_name, stages)
                self.assertTrue(stages[stage_name]["deterministic_gate_required"])
                self.assertTrue(stages[stage_name]["trace_required"])

    def test_control_loop_manifest_runtime_defaults_fail_closed(self):
        defaults = self.fixture["runtime_defaults"]

        self.assertFalse(defaults["apollo_runtime_allowed"])
        self.assertFalse(defaults["cyber_rt_allowed"])
        self.assertFalse(defaults["bazel_build_allowed"])
        self.assertFalse(defaults["cpp_runtime_allowed"])
        self.assertFalse(defaults["sensor_stack_allowed"])
        self.assertFalse(defaults["vehicle_control_allowed"])
        self.assertFalse(defaults["network_allowed"])
        self.assertFalse(defaults["credentials_allowed"])
        self.assertFalse(defaults["trading_execution_allowed"])
        self.assertFalse(defaults["risk_bypass_allowed"])
        self.assertFalse(defaults["production_enabled"])

    def test_control_loop_manifest_blocks_direct_execution_paths(self):
        forbidden = set(self.fixture["forbidden_capabilities"])

        self.assertIn("direct_model_execution", forbidden)
        self.assertIn("direct_agent_execution", forbidden)
        self.assertIn("risk_gateway_bypass", forbidden)
        self.assertIn("raw_signal_execution", forbidden)
        self.assertIn("raw_order_intent_execution", forbidden)
        self.assertIn("broker_or_exchange_call", forbidden)
        self.assertIn("private_endpoint_use", forbidden)
        self.assertIn("credential_access", forbidden)
        self.assertIn("production_enablement", forbidden)

    def test_control_loop_manifest_rejects_runtime_enablement(self):
        payload = copy.deepcopy(self.fixture)
        payload["runtime_defaults"]["apollo_runtime_allowed"] = True

        result = self.validator.validate("governance", "control_loop_manifest", payload)

        self.assertFalse(result.valid)

    def test_control_loop_manifest_rejects_missing_trace_requirement(self):
        payload = copy.deepcopy(self.fixture)
        payload["stages"][0]["trace_required"] = False

        result = self.validator.validate("governance", "control_loop_manifest", payload)

        self.assertFalse(result.valid)

    def _fixture(self):
        with FIXTURE.open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
