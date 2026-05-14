import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "integrations" / "claude_octopus_reference_review.md"
GOVERNANCE = ROOT / "docs" / "architecture" / "multi_model_review_governance.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = ROOT / "pyproject.toml"


class ClaudeOctopusReferenceReviewTests(unittest.TestCase):
    def test_review_keeps_claude_octopus_reference_only(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        required_flags = (
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "plugin_install_allowed: false",
            "npm_runtime_allowed: false",
            "mcp_runtime_allowed: false",
            "provider_runtime_allowed: false",
            "model_calls_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "reaction_engine_runtime_allowed: false",
            "autonomous_pipeline_allowed: false",
            "auto_fix_allowed: false",
            "auto_merge_allowed: false",
            "production_enabled: false",
            "trading_methods_allowed: false",
        )

        for flag in required_flags:
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_review_documents_safe_patterns(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        safe_patterns = (
            "multi-model review planning",
            "consensus gates",
            "adversarial debate",
            "agent status ledger",
            "provider capability policy",
            "reaction engine policy",
            "phase quality gates",
            "prompt preflight",
            "security review workflow",
        )

        for pattern in safe_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_review_rejects_runtime_components(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        rejected = (
            "plugin marketplace installation",
            "clone-based installation",
            "npm or npx setup flows",
            "mcp server runtime",
            "provider command runtime",
            "external model dispatch",
            "remote session autonomy",
            "persistent memory runtime",
            "autonomous factory pipelines",
            "reaction engine runtime",
            "automatic ci remediation",
            "automatic pr merge behavior",
            "provider key configuration",
        )

        for item in rejected:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_governance_keeps_runtime_disabled(self) -> None:
        text = GOVERNANCE.read_text(encoding="utf-8").lower()

        required = (
            "multi_model_review_runtime_allowed: false",
            "provider_runtime_allowed: false",
            "model_calls_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "mcp_runtime_allowed: false",
            "plugin_runtime_allowed: false",
            "reaction_engine_runtime_allowed: false",
            "auto_fix_allowed: false",
            "auto_merge_allowed: false",
            "trading_methods_allowed: false",
            "production_enabled: false",
            "consensus is not approval",
            "advisory review is not risk approval",
            "phase quality gates are not production approval",
            "docs/integrations/agent_runtime_approval_gate.md",
        )

        for item in required:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_pyproject_does_not_add_claude_octopus_runtime_dependencies(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        forbidden_terms = (
            "claude-octopus",
            "octopus",
            "opencode",
            "openclaw",
            "perplexity",
            "openrouter",
            "qwen",
        )

        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_ci_runs_claude_octopus_reference_review_tests(self) -> None:
        text = CI.read_text(encoding="utf-8")
        self.assertIn("test_claude_octopus_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
