import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "integrations" / "saferl_trusted_rl_reference_review.md"
GOVERNANCE = ROOT / "docs" / "architecture" / "safe_rl_governance.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = ROOT / "pyproject.toml"


class SafeRLReferenceReviewTests(unittest.TestCase):
    def test_reference_review_keeps_saferl_reference_only(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        required_flags = [
            "saferl_reference_reviewed: true",
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "rl_runtime_allowed: false",
            "training_runtime_allowed: false",
            "simulator_runtime_allowed: false",
            "multi_agent_rl_runtime_allowed: false",
            "policy_execution_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "trading_methods_allowed: false",
            "production_enabled: false",
        ]

        for flag in required_flags:
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_reference_review_documents_safe_patterns(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        for pattern in (
            "safety layer pattern",
            "constraint-first policy",
            "recovery policy pattern",
            "zero-violation benchmark mindset",
            "single-agent and multi-agent safety",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_reference_review_rejects_runtime_components(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        for component in (
            "rl algorithms",
            "training loops",
            "simulation environments",
            "multi-agent rl runtime",
            "policy checkpoints",
            "autonomous policy execution",
            "evaluator runtime",
        ):
            with self.subTest(component=component):
                self.assertIn(component, text)

    def test_reference_review_allows_only_contract_governance_targets(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        for target in (
            "rl safety policy contracts",
            "constraint violation records",
            "recovery policy decision records",
            "safe policy evaluation reports",
            "scenario stress test reports",
            "policy promotion gates",
        ):
            with self.subTest(target=target):
                self.assertIn(target, text)

    def test_safe_rl_governance_blocks_execution_authority(self):
        text = GOVERNANCE.read_text(encoding="utf-8").lower()

        for phrase in (
            "safe rl governance",
            "an rl policy may only propose research actions",
            "create executable orders",
            "create `approvedorder`",
            "approve risk",
            "approve execution",
            "bypass deterministic-risk-gateway",
            "zero unauthorized execution",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pyproject_does_not_add_saferl_runtime_dependencies(self):
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "saferl",
            "trusted-rl",
            "safe-rl",
            "gymnasium",
            "stable-baselines",
            "ray[rllib]",
            "rllib",
            "maddpg",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_ci_runs_saferl_reference_review_tests(self):
        text = CI.read_text(encoding="utf-8")
        self.assertIn("test_saferl_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
