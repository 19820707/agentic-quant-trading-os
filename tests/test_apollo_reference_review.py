import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "integrations" / "apollo_reference_review.md"
MAPPING = ROOT / "docs" / "architecture" / "critical_control_loop_mapping.md"
SERVICE_BOUNDARIES = ROOT / "docs" / "architecture" / "service_boundaries.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = ROOT / "pyproject.toml"


class ApolloReferenceReviewTests(unittest.TestCase):
    def test_reference_review_keeps_apollo_reference_only(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        required_flags = [
            "apollo_reference_reviewed: true",
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "apollo_runtime_allowed: false",
            "cyber_rt_allowed: false",
            "bazel_build_allowed: false",
            "cpp_runtime_allowed: false",
            "perception_runtime_allowed: false",
            "localization_runtime_allowed: false",
            "mapping_runtime_allowed: false",
            "planning_runtime_allowed: false",
            "control_runtime_allowed: false",
            "vehicle_interface_allowed: false",
            "sensor_stack_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "trading_methods_allowed: false",
            "production_enabled: false",
        ]

        for flag in required_flags:
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_reference_review_documents_safe_patterns_only(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        safe_patterns = [
            "sense predict plan control loop",
            "typed message boundaries",
            "prediction module pattern",
            "planning and control separation",
            "guardian and monitor pattern",
            "replay and scenario discipline",
        ]

        for pattern in safe_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_reference_review_rejects_runtime_components(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        rejected_components = [
            "apollo runtime",
            "cyber rt runtime",
            "bazel build system",
            "c++ autonomous driving modules",
            "perception runtime",
            "localization runtime",
            "hd map runtime",
            "routing runtime",
            "planning runtime",
            "vehicle control runtime",
            "sensor stack",
            "dreamview or hmi runtime",
        ]

        for component in rejected_components:
            with self.subTest(component=component):
                self.assertIn(component, text)

    def test_control_loop_mapping_preserves_risk_gateway_authority(self):
        text = MAPPING.read_text(encoding="utf-8").lower()

        required_boundaries = [
            "market observations -> forecasts -> signal and intent planning -> deterministic risk control -> execution boundary",
            "prediction cannot approve risk",
            "signal generation cannot execute",
            "orderintent is not executable",
            "deterministic-risk-gateway remains the final pre-trade authority",
            "execution engine must reject raw signals and raw order intents",
            "backtest and replay evidence cannot grant production permission",
        ]

        for boundary in required_boundaries:
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, text)

    def test_service_boundaries_include_critical_control_loop(self):
        text = SERVICE_BOUNDARIES.read_text(encoding="utf-8").lower()

        for phrase in (
            "critical control loop boundary",
            "observation -> prediction -> planning -> control -> execution-boundary",
            "deterministic-risk-gateway remains the final pre-trade control boundary",
            "no model, agent, dashboard, notebook, research service, backtest or signal service",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pyproject_does_not_add_apollo_runtime_dependencies(self):
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        forbidden_terms = [
            "apolloauto",
            "cyberrt",
            "cyber-rt",
            "bazel",
            "dreamview",
            "canbus",
            "autonomous-driving",
        ]

        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_ci_runs_apollo_reference_review_tests(self):
        text = CI.read_text(encoding="utf-8")
        self.assertIn("test_apollo_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
