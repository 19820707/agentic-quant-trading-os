import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_DOC = ROOT / "docs" / "integrations" / "lmhtq_polymarket_ai_agent_reference_review.md"
ARCH_DOC = ROOT / "docs" / "architecture" / "prediction_research_contracts.md"
PYPROJECT = ROOT / "pyproject.toml"


class LmhtqPolymarketAiAgentReferenceReviewTests(unittest.TestCase):
    def test_reference_review_exists_and_rejects_runtime(self):
        text = REVIEW_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("reference_only: true", text)
        self.assertIn("direct_dependency_allowed: false", text)
        self.assertIn("polymarket_clob_allowed: false", text)
        self.assertIn("llm_runtime_allowed: false", text)
        self.assertIn("scheduler_runtime_allowed: false", text)
        self.assertIn("network_access_allowed: false", text)
        self.assertIn("credentials_allowed: false", text)
        self.assertIn("trading_methods_allowed: false", text)

    def test_review_rejects_dangerous_runtime_patterns(self):
        text = REVIEW_DOC.read_text(encoding="utf-8").lower()

        for phrase in (
            "polymarket clob execution",
            "polygon wallet private keys",
            "llm api keys",
            "scheduler loops",
            "paper or live executor runtime",
            "direct path from llm output to orders",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_safe_patterns_are_contract_first(self):
        text = REVIEW_DOC.read_text(encoding="utf-8")

        for contract_name in (
            "TieredResearchStage",
            "MarketNewsRelevanceScore",
            "ResearchCadencePlan",
            "ModelLimitationRecord",
            "DryRunEvaluationSummary",
        ):
            with self.subTest(contract=contract_name):
                self.assertIn(contract_name, text)

    def test_architecture_doc_mentions_research_discipline_boundaries(self):
        text = ARCH_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("tiered research", text)
        self.assertIn("market-news relevance", text)
        self.assertIn("research cadence", text)
        self.assertIn("model limitation", text)
        self.assertIn("dry-run evaluation", text)
        self.assertIn("non-executable", text)

    def test_project_does_not_add_external_runtime_dependencies(self):
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "py-clob-client",
            "polymarket",
            "openai",
            "boto3",
            "feedparser",
            "praw",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
