from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/zkosai_polymarket_arbitrage_bot_reference_review.md")
RUNBOOK_PATH = Path("docs/architecture/prediction_market_trend_preflight_research_runbook.md")
PYPROJECT = Path("pyproject.toml")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


class ZkOSaiPolymarketArbitrageBotReferenceReviewTests(unittest.TestCase):
    def test_review_document_exists(self) -> None:
        self.assertTrue(REVIEW_PATH.is_file())

    def test_review_keeps_repository_reference_only(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "npm_runtime_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "private_endpoints_allowed: false",
            "trading_methods_allowed: false",
            "clob_runtime_allowed: false",
            "wallet_runtime_allowed: false",
            "settlement_allowed: false",
            "hedge_execution_allowed: false",
            "rpc_runtime_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_review_extracts_trend_and_preflight_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "order book imbalance observation",
            "trend state observation",
            "trend flip observation",
            "preflight safety review",
            "simulation mode policy",
            "pnl simulation summary",
            "strategy history event",
        ):
            self.assertIn(phrase, text)

    def test_review_rejects_runtime_components(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "typescript or npm runtime",
            "live market discovery",
            "live order book polling",
            "clob client runtime",
            "signer or account runtime",
            "proxy account workflow",
            "chain rpc runtime",
            "balance preflight runtime",
            "production mode workflow",
            "order placement workflow",
            "position switch workflow",
            "redeem or settlement workflow",
        ):
            self.assertIn(phrase, text)

    def test_runbook_keeps_research_local_only(self) -> None:
        text = RUNBOOK_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "local-only research process",
            "does not approve runtime market access",
            "synthetic `orderbookimbalanceobservation`",
            "trendstateobservation",
            "trendflipobservation",
            "preflightsafetyreview",
            "simulationmodepolicy",
            "arbitragepnlsimulationsummary",
            "strategyhistoryevent",
            "stop at research output",
        ):
            self.assertIn(phrase, text)

    def test_no_zkosai_runtime_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "@polymarket/clob-client",
            "clob-client",
            "ethers",
            "wagmi",
            "viem",
            "gnosis",
            "zkosai",
            "polymarket-arbitrage-bot",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_zkosai_reference_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_zkosai_polymarket_arbitrage_bot_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
