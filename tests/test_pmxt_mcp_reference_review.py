from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/pmxt_mcp_reference_review.md")
SAFETY_PATH = Path("docs/architecture/mcp_prediction_market_tool_safety.md")
CI_WORKFLOW = Path(".github/workflows/ci.yml")
PYPROJECT = Path("pyproject.toml")


class PMXTMCPReferenceReviewTests(unittest.TestCase):
    def test_reference_review_exists(self) -> None:
        self.assertTrue(REVIEW_PATH.is_file())

    def test_reference_review_keeps_pmxt_mcp_disabled(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "direct_dependency_allowed: false",
            "npx_execution_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "pmxt_api_key_allowed: false",
            "pmxt_api_url_allowed: false",
            "trading_tools_allowed: false",
            "account_tools_allowed: false",
            "mcp_runtime_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_reference_review_extracts_safe_read_only_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8")

        for phrase in (
            "fetchMarkets",
            "fetchEvents",
            "fetchMarket",
            "fetchOrderBook",
            "fetchTrades",
            "fetchOHLCV",
            "compareMarketPrices",
            "fetchEventMatches",
            "fetchArbitrage",
        ):
            self.assertIn(phrase, text)

    def test_reference_review_rejects_destructive_account_and_credential_tools(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8")

        for phrase in (
            "buildOrder",
            "createOrder",
            "submitOrder",
            "cancelOrder",
            "fetchBalance",
            "fetchPositions",
            "fetchOpenOrders",
            "fetchClosedOrders",
            "fetchAllOrders",
            "fetchMyTrades",
            "credentials",
        ):
            self.assertIn(phrase, text)

    def test_architecture_doc_defines_mcp_tool_safety_boundary(self) -> None:
        text = SAFETY_PATH.read_text(encoding="utf-8")

        for phrase in (
            "Unknown tools fail closed.",
            "Tools containing credential fields fail closed.",
            "explicit read-only allowlist",
            "explicit destructive/account denylist",
            "no tool that can create `OrderIntent` or `ApprovedOrder`",
            "no bypass of deterministic-risk-gateway",
        ):
            self.assertIn(phrase, text)

    def test_pmxt_mcp_is_not_declared_as_dependency(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "@pmxt/mcp",
            "pmxt-mcp",
            "modelcontextprotocol",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_pmxt_mcp_reference_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_pmxt_mcp_reference_review.py", text)
        self.assertIn("test_prediction_market_mcp_tool_policy.py", text)


if __name__ == "__main__":
    unittest.main()
