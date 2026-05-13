from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/sxai_prediction_market_copytrade_reference_review.md")
RUNBOOK_PATH = Path("docs/architecture/prediction_market_copytrade_research_runbook.md")
PYPROJECT = Path("pyproject.toml")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


class SxaiPredictionMarketCopytradeReferenceReviewTests(unittest.TestCase):
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
            "copy_execution_allowed: false",
            "wallet_runtime_allowed: false",
            "target_resolution_runtime_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_review_extracts_copytrade_research_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "target observation",
            "observed trader activity",
            "copy trade policy",
            "copy trade simulation",
            "trader reliability profile",
            "copy trade risk review input",
        ):
            self.assertIn(phrase, text)

    def test_review_rejects_runtime_components(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "typescript or npm runtime",
            "target username or address resolver runtime",
            "account activity polling runtime",
            "wallet or funder workflows",
            "signature workflows",
            "credential environment workflow",
            "copy-trade executor",
            "real account client",
            "order placement workflow",
            "production mode workflow",
        ):
            self.assertIn(phrase, text)

    def test_runbook_keeps_research_local_only(self) -> None:
        text = RUNBOOK_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "local-only research process",
            "does not approve runtime market access",
            "synthetic `copytradetargetobservation`",
            "observedtraderactivity",
            "copytradepolicy",
            "copytradesimulationrecord",
            "traderreliabilityprofile",
            "stop at research output",
            "automatic trade mirroring",
        ):
            self.assertIn(phrase, text)

    def test_no_copytrade_runtime_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "@polymarket/clob-client",
            "clob-client",
            "ethers",
            "wagmi",
            "viem",
            "gnosis",
            "sxai-lab",
            "prediction-market-copytrade",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_copytrade_reference_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_sxai_prediction_market_copytrade_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
