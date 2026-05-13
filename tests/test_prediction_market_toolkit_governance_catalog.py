from pathlib import Path
import unittest


CATALOG_PATH = Path("docs/integrations/prediction_market_toolkit_governance_catalog.md")
BOUNDARY_PATH = Path("docs/architecture/prediction_market_research_safety_boundary.md")
PYPROJECT = Path("pyproject.toml")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


class PredictionMarketToolkitGovernanceCatalogTests(unittest.TestCase):
    def test_catalog_document_exists(self) -> None:
        self.assertTrue(CATALOG_PATH.is_file())

    def test_catalog_keeps_toolkits_reference_only(self) -> None:
        text = CATALOG_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "private_endpoints_allowed: false",
            "trading_methods_allowed: false",
            "toolkit_runtime_allowed: false",
            "market_making_runtime_allowed: false",
            "copy_trade_runtime_allowed: false",
            "arbitrage_runtime_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_catalog_defines_capability_and_strategy_taxonomy(self) -> None:
        text = CATALOG_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "data ingestion",
            "market discovery",
            "signal research",
            "arbitrage research",
            "copy-trade observation",
            "market-making research",
            "spread monitoring",
            "research-to-execution escalation map",
        ):
            self.assertIn(phrase, text)

    def test_boundary_blocks_runtime_and_execution_outputs(self) -> None:
        text = BOUNDARY_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "does not approve external sdks",
            "forbidden outputs",
            "executable orders",
            "order intents",
            "approved orders",
            "quote publication",
            "risk approval",
            "execution approval",
            "deterministic-risk-gateway",
        ):
            self.assertIn(phrase, text)

    def test_no_toolkit_runtime_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "prediction-markets-trading-bot-toolkits",
            "haredoggy",
            "polymarket",
            "kalshi",
            "clob-client",
            "ethers",
            "wagmi",
            "viem",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_toolkit_governance_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_prediction_market_toolkit_governance_catalog.py", text)


if __name__ == "__main__":
    unittest.main()
