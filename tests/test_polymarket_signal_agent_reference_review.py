import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW_DOC = ROOT / "docs" / "integrations" / "polymarket_signal_agent_reference_review.md"
ARCH_DOC = ROOT / "docs" / "architecture" / "prediction_research_contracts.md"
PYPROJECT = ROOT / "pyproject.toml"


class PolymarketSignalAgentReferenceReviewTests(unittest.TestCase):
    def test_reference_review_exists_and_rejects_runtime(self):
        text = REVIEW_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("reference_only: true", text)
        self.assertIn("direct_dependency_allowed: false", text)
        self.assertIn("synthesis_runtime_allowed: false", text)
        self.assertIn("groq_runtime_allowed: false", text)
        self.assertIn("wallet_runtime_allowed: false", text)
        self.assertIn("network_access_allowed: false", text)
        self.assertIn("credentials_allowed: false", text)
        self.assertIn("trading_methods_allowed: false", text)

    def test_review_rejects_dangerous_runtime_patterns(self):
        text = REVIEW_DOC.read_text(encoding="utf-8").lower()

        for phrase in (
            "dashboard trade routes",
            "one-click buy or sell controls",
            "wallet api access",
            "order api access",
            "private keys",
            "automatic arbitrage execution",
            "direct path from signal output to orders",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_safe_patterns_are_contract_first(self):
        text = REVIEW_DOC.read_text(encoding="utf-8")

        for contract_name in (
            "PredictionMarketSignalClassification",
            "EdgeComputationRecord",
            "EnsembleProbabilityVote",
            "AdvisoryKellySizing",
            "SignalPipelineStatus",
        ):
            with self.subTest(contract=contract_name):
                self.assertIn(contract_name, text)

    def test_architecture_doc_mentions_signal_classification_boundaries(self):
        text = ARCH_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("signal classification", text)
        self.assertIn("edge computation", text)
        self.assertIn("ensemble probability", text)
        self.assertIn("advisory kelly", text)
        self.assertIn("pipeline status", text)
        self.assertIn("non-executable", text)

    def test_project_does_not_add_external_signal_runtime_dependencies(self):
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "synthesis",
            "groq",
            "feedparser",
            "openai",
            "next",
            "tailwind",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
