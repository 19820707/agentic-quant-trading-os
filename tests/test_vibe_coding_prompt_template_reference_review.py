import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "integrations" / "vibe_coding_prompt_template_reference_review.md"
GOVERNANCE = ROOT / "docs" / "architecture" / "product_engineering_governance.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = ROOT / "pyproject.toml"


class VibeCodingPromptTemplateReferenceReviewTests(unittest.TestCase):
    def test_review_keeps_repository_reference_only(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        required_flags = (
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "template_copy_allowed: false",
            "prompt_runtime_allowed: false",
            "llm_runtime_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "auto_code_generation_allowed: false",
            "auto_build_allowed: false",
            "auto_deploy_allowed: false",
            "production_enabled: false",
            "trading_methods_allowed: false",
        )

        for flag in required_flags:
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_review_documents_safe_patterns(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        safe_patterns = (
            "research before build",
            "prd and requirement discipline",
            "technical design before editing",
            "agent instruction pack",
            "plan execute verify cycle",
            "mvp boundary",
            "handoff artifacts",
            "build readiness and post-build verification",
        )

        for pattern in safe_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_review_rejects_runtime_and_template_copying(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        rejected = (
            "raw prompt templates as authority",
            "generic mvp deployment guidance",
            "clone-based setup",
            "template repository structure",
            "automatic code generation flows",
            "ai ide runtime workflows",
            "production deployment steps",
            "generated agents.md replacement",
        )

        for item in rejected:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_governance_keeps_engineering_flow_fail_closed(self) -> None:
        text = GOVERNANCE.read_text(encoding="utf-8").lower()

        required = (
            "prompt_runtime_allowed: false",
            "llm_runtime_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "auto_code_generation_allowed: false",
            "auto_build_allowed: false",
            "auto_deploy_allowed: false",
            "scope_expansion_allowed: false",
            "production_enabled: false",
            "trading_methods_allowed: false",
            "mvp readiness is not production readiness",
            "local verification is not production approval",
            "docs/integrations/agent_runtime_approval_gate.md",
        )

        for item in required:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_pyproject_does_not_add_prompt_template_runtime_dependencies(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        forbidden_terms = (
            "vibe-coding-prompt-template",
            "khazp",
            "lovable",
            "v0",
            "cursor",
            "copilot cli",
        )

        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_ci_runs_reference_review_tests(self) -> None:
        text = CI.read_text(encoding="utf-8")
        self.assertIn("test_vibe_coding_prompt_template_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
