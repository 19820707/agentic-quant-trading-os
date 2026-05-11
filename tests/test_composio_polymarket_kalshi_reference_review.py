from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/composio_polymarket_kalshi_reference_review.md")
ARCH_PATH = Path("docs/architecture/cross_venue_prediction_market_research.md")
CI_WORKFLOW = Path(".github/workflows/ci.yml")
PYPROJECT = Path("pyproject.toml")


class ComposioPolymarketKalshiReferenceReviewTests(unittest.TestCase):
    def test_reference_review_exists(self) -> None:
        self.assertTrue(REVIEW_PATH.is_file())

    def test_reference_review_rejects_runtime_and_credentials(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "wallet_access_allowed: false",
            "polymarket_clob_client_allowed: false",
            "kalshi_api_runtime_allowed: false",
            "trading_methods_allowed: false",
            "order_submission_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_reference_review_extracts_safe_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "cross-venue price normalization to cents",
            "venue status tracking",
            "venue freshness timestamps",
            "thin-liquidity flags",
            "resolution timing mismatch detection",
            "spread anomaly thresholds",
            "read-only status dashboard concepts",
        ):
            self.assertIn(phrase, text)

    def test_architecture_doc_preserves_execution_boundary(self) -> None:
        text = ARCH_PATH.read_text(encoding="utf-8")

        for phrase in (
            "VenueResolutionState",
            "CrossVenuePriceSnapshot",
            "CrossVenueArbitrageObservation",
            "Forbidden outputs",
            "OrderIntent",
            "ApprovedOrder",
            "deterministic-risk-gateway",
            "execution-engine only",
        ):
            self.assertIn(phrase, text)

    def test_no_external_runtime_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "@polymarket/clob-client",
            "ethers",
            "dotenv",
            "axios",
            "express",
            "kalshi",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_reference_review_test(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_composio_polymarket_kalshi_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
