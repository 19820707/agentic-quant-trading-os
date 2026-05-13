from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/sxai_prediction_market_arbitrage_lifecycle_reference_review.md")
RUNBOOK_PATH = Path("docs/architecture/prediction_market_arbitrage_research_runbook.md")
PYPROJECT = Path("pyproject.toml")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


class SxaiPredictionMarketArbitrageLifecycleReferenceReviewTests(unittest.TestCase):
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
            "polymarket_clob_allowed: false",
            "wallet_runtime_allowed: false",
            "settlement_allowed: false",
            "hedge_execution_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_review_extracts_lifecycle_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "market discovery record",
            "price snapshot record",
            "simulation history record",
            "configuration policy",
            "stale-data boundaries",
            "source lag",
        ):
            self.assertIn(phrase, text)

    def test_review_rejects_runtime_components(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "typescript or npm runtime",
            "clob client runtime",
            "wallet or proxy-wallet workflows",
            "signature workflows",
            "credential environment workflow",
            "production flag workflow",
            "order placement",
            "redeem or settlement workflow",
            "live endpoint polling",
            "hedge execution workflow",
        ):
            self.assertIn(phrase, text)

    def test_runbook_keeps_research_local_only(self) -> None:
        text = RUNBOOK_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "local-only research process",
            "does not approve runtime market access",
            "synthetic `predictionmarketdiscoveryrecord`",
            "synthetic `predictionmarketpricesnapshot`",
            "stop at research output",
            "forbidden",
            "network enablement",
            "production enablement",
            "execution enablement",
        ):
            self.assertIn(phrase, text)

    def test_no_arbitrage_runtime_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "@polymarket/clob-client",
            "clob-client",
            "ethers",
            "wagmi",
            "viem",
            "gnosis",
            "sxai-lab",
            "prediction-market-arbitrage",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_lifecycle_reference_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_sxai_prediction_market_arbitrage_lifecycle_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
