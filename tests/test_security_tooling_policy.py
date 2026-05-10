from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs" / "security" / "security_tooling_integration_policy.md"
CODEQL_WORKFLOW = ROOT / ".github" / "workflows" / "codeql.yml"


class SecurityToolingPolicyTests(unittest.TestCase):
    def test_policy_documents_tool_classes(self) -> None:
        text = POLICY.read_text(encoding="utf-8")

        for phrase in (
            "Production CI Candidates",
            "Advisory Review Candidates",
            "Research-Only Candidates",
            "Isolated Lab Only",
            "Web3 Only",
        ):
            self.assertIn(phrase, text)

    def test_policy_keeps_external_tools_disabled_by_default(self) -> None:
        text = POLICY.read_text(encoding="utf-8")

        for phrase in (
            "snyk_enabled: false",
            "sonarqube_enabled: false",
            "coderabbit_enabled: false",
            "llm_council_enabled: false",
            "offensive_lab_tools_enabled: false",
            "external_security_tokens_allowed: false",
            "broker_credentials_allowed: false",
            "trading_authority_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_policy_forbids_credentials_and_trading_authority(self) -> None:
        text = POLICY.read_text(encoding="utf-8").lower()

        for phrase in (
            "no broker credentials",
            "no exchange trade credentials",
            "no withdrawal keys",
            "no live trading paths",
            "no order submission",
            "no bypass of deterministic-risk-gateway",
        ):
            self.assertIn(phrase, text)

    def test_codeql_workflow_is_present_without_project_secrets(self) -> None:
        text = CODEQL_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("github/codeql-action/init@v4", text)
        self.assertIn("github/codeql-action/analyze@v4", text)
        self.assertIn("languages: python", text)
        self.assertIn("security-events: write", text)
        self.assertNotIn("secrets.", text)


if __name__ == "__main__":
    unittest.main()
