import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "integrations" / "ruflo_reference_review.md"
BOUNDARY = ROOT / "docs" / "architecture" / "agent_orchestration_safety_boundary.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = ROOT / "pyproject.toml"


class RufloReferenceReviewTests(unittest.TestCase):
    def test_reference_review_keeps_ruflo_reference_only(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        required_flags = [
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "npm_runtime_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "trading_methods_allowed: false",
            "mcp_runtime_allowed: false",
            "swarm_runtime_allowed: false",
            "federation_runtime_allowed: false",
            "memory_runtime_allowed: false",
            "background_worker_runtime_allowed: false",
            "neural_trader_runtime_allowed: false",
            "market_data_runtime_allowed: false",
        ]

        for flag in required_flags:
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_reference_review_documents_safe_patterns_only(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        safe_patterns = [
            "agent orchestration governance",
            "swarm topology policy",
            "federation boundary",
            "agent memory governance",
            "mcp tool registration policy",
            "background worker policy",
            "cost budget policy",
            "prompt injection review",
        ]

        for pattern in safe_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_reference_review_rejects_runtime_components(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        rejected_components = [
            "npm or npx installation flows",
            "shell install scripts",
            "mcp server runtime",
            "plugin marketplace runtime",
            "swarm runtime",
            "federation runtime",
            "vector memory runtime",
            "rag runtime",
            "background workers",
            "browser automation runtime",
            "neural trading runtime",
            "market data runtime",
        ]

        for component in rejected_components:
            with self.subTest(component=component):
                self.assertIn(component, text)

    def test_agent_orchestration_boundary_blocks_runtime_authority(self):
        text = BOUNDARY.read_text(encoding="utf-8").lower()

        required_boundaries = [
            "does not approve agent runtime",
            "mcp runtime",
            "swarm runtime",
            "federation",
            "memory databases",
            "background workers",
            "credential access",
            "trading decisions",
            "risk approval",
            "execution approval",
            "every agentic capability starts disabled",
            "deterministic-risk-gateway",
        ]

        for boundary in required_boundaries:
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, text)

    def test_pyproject_does_not_add_ruflo_runtime_dependencies(self):
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        forbidden_terms = [
            "ruflo",
            "ruvnet",
            "agentdb",
            "vector db",
            "browser automation",
            "neural-trader",
            "market-data plugin",
        ]

        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_ci_runs_ruflo_reference_review_tests(self):
        text = CI.read_text(encoding="utf-8")
        self.assertIn("test_ruflo_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
