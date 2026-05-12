from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/haredoggy_prediction_market_toolkits_reference_review.md")
ARCH_PATH = Path("docs/architecture/prediction_market_strategy_patterns.md")
CI_WORKFLOW = Path(".github/workflows/ci.yml")
PYPROJECT = Path("pyproject.toml")


class HaredoggyPredictionMarketToolkitsReferenceReviewTests(unittest.TestCase):
    def test_reference_review_exists(self) -> None:
        self.assertTrue(REVIEW_PATH.is_file())

    def test_reference_review_rejects_runtime_and_credentials(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "rust_runtime_allowed: false",
            "tokio_runtime_allowed: false",
            "venue_client_allowed: false",
            "polymarket_clob_allowed: false",
            "kalshi_client_allowed: false",
            "limitless_client_allowed: false",
            "wallet_tracking_runtime_allowed: false",
            "credential_configuration_allowed: false",
            "network_access_allowed: false",
            "trading_methods_allowed: false",
            "production_enabled: false",
        ):
            self.assertIn(phrase, text)

    def test_reference_review_extracts_safe_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "strategy taxonomy",
            "venue-agnostic adapter layering",
            "dry-run-first workflow",
            "circuit breaker concept",
            "liquidity/depth guard concept",
            "order book imbalance as a read-only feature",
            "public wallet activity as an observation source",
        ):
            self.assertIn(phrase, text)

    def test_architecture_doc_keeps_patterns_non_executable(self) -> None:
        text = ARCH_PATH.read_text(encoding="utf-8")

        for phrase in (
            "research classification",
            "feature planning",
            "risk review only",
            "Forbidden",
            "executable bots",
            "wallet mirroring",
            "venue account access",
            "OrderIntent",
            "ApprovedOrder",
        ):
            self.assertIn(phrase, text)

    def test_no_external_runtime_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "prediction-markets-trading-bot-toolkits",
            "tokio",
            "ratatui",
            "alloy",
            "polymarket",
            "kalshi",
            "limitless",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_reference_review_test(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_haredoggy_prediction_market_toolkits_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
