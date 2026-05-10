from pathlib import Path
import unittest


AUDIT_PATH = Path("docs/integrations/prediction_market_repo_audit.md")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


class PredictionMarketRepoAuditTests(unittest.TestCase):
    def test_audit_document_exists(self) -> None:
        self.assertTrue(AUDIT_PATH.is_file())

    def test_all_requested_repositories_are_cataloged(self) -> None:
        text = AUDIT_PATH.read_text(encoding="utf-8")

        for url in (
            "https://github.com/datori/market-edge",
            "https://github.com/mjunaidca/polymarket-skills",
            "https://github.com/InjayTseng/Trading-Agent-Polymarket",
            "https://github.com/pmxt-dev/pmxt-mcp",
            "https://github.com/Composio-HQ/polymarket-kalshi-arbitrage-bot",
            "https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits",
            "https://github.com/neilt93/Prediction-Market-Agent",
            "https://github.com/lmhtq/polymarket-ai-agent",
            "https://github.com/yigitcankzl/PolymarketSignalAgent",
            "https://github.com/SXai-lab/prediction-market-arbitrage",
            "https://github.com/SXai-lab/prediction-market-copytrade",
            "https://github.com/zkOSAI/polymarket-arbitrage-bot",
        ):
            self.assertIn(url, text)

    def test_decision_state_blocks_direct_coupling(self) -> None:
        text = AUDIT_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "direct_installation_allowed: false",
            "external_repo_cloning_allowed: false",
            "vendoring_allowed: false",
            "submodules_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "private_endpoints_allowed: false",
            "trading_methods_allowed: false",
            "broker_exchange_execution_allowed: false",
            "mcp_trading_tools_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_high_risk_behaviors_are_documented(self) -> None:
        text = AUDIT_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "live or automated trading claims",
            "wallet/private-key requirements",
            "order submission",
            "copy-trading",
            "arbitrage",
            "mcp tools",
            "missing licenses",
        ):
            self.assertIn(phrase, text)

    def test_installation_is_explicitly_not_approved(self) -> None:
        text = AUDIT_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "do not install any listed repository",
            "do not clone any listed repository",
            "do not add any listed repository as a dependency",
            "do not add any listed repository as a dependency, git submodule, vendored folder",
        ):
            self.assertIn(phrase, text)

    def test_future_work_requires_governed_adapter_review(self) -> None:
        text = AUDIT_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "completed external adapter review checklist",
            "license review",
            "dependency and transitive dependency review",
            "security and credential-boundary review",
            "explicit internal contract mapping",
            "local-only fake/in-memory tests",
            "no network calls in unit tests",
            "prohibited method denylist tests",
        ):
            self.assertIn(phrase, text)

    def test_policy_prevents_direct_ai_to_execution_paths(self) -> None:
        text = AUDIT_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "direct path from ai/agent/model/dashboard/notebook",
            "deterministic-risk-gateway",
            "must not create orderintent",
            "approvedorder",
            "wallet transactions",
            "risk approvals",
        ):
            self.assertIn(phrase, text)

    def test_ci_runs_prediction_market_audit_test(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_prediction_market_repo_audit.py", text)


if __name__ == "__main__":
    unittest.main()
