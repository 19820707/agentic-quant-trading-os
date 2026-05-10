from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "docs" / "security" / "security_tooling_integration_policy.md"
CODEQL_WORKFLOW = ROOT / ".github" / "workflows" / "codeql.yml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
SECRET_ARTIFACT_AUDIT = ROOT / "scripts" / "secret_artifact_audit.py"


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
            "no wallet keys",
            "no trading secrets",
            "no production market data entitlements",
            "no live execution infrastructure access",
            "no live trading paths",
            "no order submission",
            "no bypass of deterministic-risk-gateway",
            "no model checkpoints committed to the repository",
            "no local databases or market-data entitlement dumps committed to the repository",
            "no real `.env` files committed to the repository",
            "no offensive or autonomous security tool may run against external targets",
        ):
            self.assertIn(phrase, text)

    def test_codeql_workflow_is_present_without_project_secrets(self) -> None:
        text = CODEQL_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("github/codeql-action/init@v4", text)
        self.assertIn("github/codeql-action/analyze@v4", text)
        self.assertIn("languages: python", text)
        self.assertIn("queries: security-extended", text)
        self.assertNotIn("security-and-quality", text)
        self.assertIn("security-events: write", text)
        self.assertIn("packages: read", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("concurrency:", text)
        self.assertIn("continue-on-error: true", text)
        self.assertIn("Advisory until GitHub Code Scanning is enabled", text)
        self.assertNotIn("secrets.", text)

    def test_local_secret_artifact_audit_is_enabled_without_external_tools(self) -> None:
        policy_text = POLICY.read_text(encoding="utf-8")
        ci_text = CI_WORKFLOW.read_text(encoding="utf-8")
        audit_text = SECRET_ARTIFACT_AUDIT.read_text(encoding="utf-8")

        self.assertIn("local_secret_artifact_audit_enabled: true", policy_text)
        self.assertIn("secret-artifact-audit:", ci_text)
        self.assertIn("python scripts/secret_artifact_audit.py", ci_text)
        self.assertIn("BLOCKED_FILE_SUFFIXES", audit_text)
        self.assertIn("SECRET_PATTERNS", audit_text)
        self.assertNotIn("requests", audit_text)
        self.assertNotIn("urllib", audit_text)
        self.assertNotIn("subprocess", audit_text)

    def test_sensitive_tools_require_explicit_policy_changes(self) -> None:
        policy_text = POLICY.read_text(encoding="utf-8").lower()
        activation_text = "\n".join(
            (
                CODEQL_WORKFLOW.read_text(encoding="utf-8"),
                CI_WORKFLOW.read_text(encoding="utf-8"),
            )
        ).lower()

        disabled_markers = (
            "snyk_enabled: false",
            "sonarqube_enabled: false",
            "coderabbit_enabled: false",
            "codeql_hard_gate_enabled: false",
            "codeql_requires_code_scanning_enabled: true",
            "offensive_lab_tools_enabled: false",
            "web3_static_analysis_enabled: false",
        )
        for marker in disabled_markers:
            self.assertIn(marker, policy_text)

        forbidden_activation_markers = (
            "snyk/actions",
            "sonarsource/sonarqube-scan-action",
            "coderabbit",
            "coderabbitai",
            "pentestgpt",
            "xalgorix",
            "hackcode",
            "aderyn",
            "openrouter_api_key",
            "snyk_token",
            "sonar_token",
        )
        for marker in forbidden_activation_markers:
            self.assertNotIn(marker, activation_text)


if __name__ == "__main__":
    unittest.main()
