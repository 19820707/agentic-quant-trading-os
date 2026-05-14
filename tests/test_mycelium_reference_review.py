import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "integrations" / "mycelium_reference_review.md"
GOVERNANCE = ROOT / "docs" / "architecture" / "agent_memory_governance.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = ROOT / "pyproject.toml"


class MyceliumReferenceReviewTests(unittest.TestCase):
    def test_reference_review_keeps_mycelium_reference_only(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        required_flags = [
            "mycelium_reference_reviewed: true",
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "docker_runtime_allowed: false",
            "supabase_allowed: false",
            "postgres_allowed: false",
            "pgvector_allowed: false",
            "ollama_allowed: false",
            "embedding_runtime_allowed: false",
            "mcp_runtime_allowed: false",
            "dashboard_runtime_allowed: false",
            "auto_absorb_allowed: false",
            "auto_digest_allowed: false",
            "context_priming_allowed: false",
            "federation_allowed: false",
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
            "agent memory record",
            "memory recall request",
            "memory recall result",
            "memory consolidation record",
            "lesson record",
            "agent trait record",
            "intention record",
            "memory conflict record",
            "session digest record",
            "memory retention policy",
            "federated memory policy",
            "mcp memory tool policy",
        ]

        for pattern in safe_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_reference_review_rejects_runtime_components(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        rejected_components = [
            "docker runtime",
            "supabase runtime",
            "postgresql runtime",
            "pgvector storage",
            "ollama runtime",
            "embedding runtime",
            "node mcp server",
            "dashboard runtime",
            "automatic context priming",
            "automatic memory absorption",
            "swarm or federation runtime",
            "networked memory storage",
            "credential-bearing tool runtime",
        ]

        for component in rejected_components:
            with self.subTest(component=component):
                self.assertIn(component, text)

    def test_agent_memory_governance_blocks_runtime_authority(self):
        text = GOVERNANCE.read_text(encoding="utf-8").lower()

        required_boundaries = [
            "memory_runtime_enabled: false",
            "external_memory_allowed: false",
            "embedding_runtime_allowed: false",
            "mcp_runtime_allowed: false",
            "dashboard_runtime_allowed: false",
            "federation_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "broker_context_allowed: false",
            "trading_methods_allowed: false",
            "execution_allowed: false",
            "production_enabled: false",
            "deterministic-risk-gateway",
        ]

        for boundary in required_boundaries:
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, text)

    def test_pyproject_does_not_add_mycelium_runtime_dependencies(self):
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        forbidden_terms = [
            "mycelium",
            "supabase",
            "pgvector",
            "ollama",
            "postgres",
            "mcp-memory",
            "agentdb",
        ]

        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_ci_runs_mycelium_reference_review_tests(self):
        text = CI.read_text(encoding="utf-8")
        self.assertIn("test_mycelium_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
