import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_DOC = ROOT / "docs" / "integrations" / "neilt_prediction_market_agent_reference_review.md"
ARCH_DOC = ROOT / "docs" / "architecture" / "prediction_research_contracts.md"
PYPROJECT = ROOT / "pyproject.toml"


class NeiltPredictionMarketAgentReferenceReviewTests(unittest.TestCase):
    def test_reference_review_exists_and_is_not_runtime_approval(self):
        text = REVIEW_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("reference_only: true", text)
        self.assertIn("direct_dependency_allowed: false", text)
        self.assertIn("clone_allowed: false", text)
        self.assertIn("vendoring_allowed: false", text)
        self.assertIn("network_access_allowed: false", text)
        self.assertIn("credentials_allowed: false", text)
        self.assertIn("trading_methods_allowed: false", text)

    def test_review_rejects_live_prediction_market_runtime(self):
        text = REVIEW_DOC.read_text(encoding="utf-8").lower()

        for phrase in (
            "live kalshi trading",
            "polymarket clob clients",
            "venue api clients",
            "order placement",
            "position management",
            "credential configuration",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_safe_patterns_are_contract_first(self):
        text = REVIEW_DOC.read_text(encoding="utf-8")

        for contract_name in (
            "ForecastEvidenceItem",
            "MarketRuleParse",
            "ForecastCalibrationRecord",
            "ForecastPostmortem",
            "ForecastFeatureSnapshot",
        ):
            with self.subTest(contract=contract_name):
                self.assertIn(contract_name, text)

    def test_architecture_doc_mentions_forecasting_boundaries(self):
        text = ARCH_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("forecast evidence", text)
        self.assertIn("rule parsing", text)
        self.assertIn("calibration", text)
        self.assertIn("postmortem", text)
        self.assertIn("point-in-time", text)
        self.assertIn("non-executable", text)

    def test_project_does_not_add_external_runtime_dependencies(self):
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "kalshi",
            "polymarket",
            "lightgbm",
            "ollama",
            "celery",
            "redis",
            "pgvector",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
