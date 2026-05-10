from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/market_edge_reference_review.md")
PIPELINE_PATH = Path("docs/architecture/prediction_market_research_pipeline.md")
PYPROJECT = Path("pyproject.toml")


class MarketEdgeReferenceReviewTests(unittest.TestCase):
    def test_review_document_exists(self) -> None:
        self.assertTrue(REVIEW_PATH.is_file())

    def test_review_keeps_market_edge_reference_only(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "reference-only architecture source",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "polymarket_clob_allowed: false",
            "live_executor_allowed: false",
            "wallet_access_allowed: false",
            "trading_methods_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_review_extracts_safe_design_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "research / strategy / tactical separation",
            "multi-pass probability estimation",
            "market selection thesis",
            "hypothesis lifecycle",
            "backtest and calibration evaluation",
            "observability dashboard concepts",
        ):
            self.assertIn(phrase, text)

    def test_review_rejects_runtime_components(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "do not reuse directly",
            "polymarket clob client",
            "live executor",
            "wallet or private-key configuration",
            "kelly sizing connected to execution",
            "autonomous agent run command",
            "any code path that can place, cancel, modify, transfer, redeem, or settle orders",
        ):
            self.assertIn(phrase, text)

    def test_pipeline_document_exists(self) -> None:
        self.assertTrue(PIPELINE_PATH.is_file())

    def test_pipeline_outputs_are_non_executable(self) -> None:
        text = PIPELINE_PATH.read_text(encoding="utf-8")

        for phrase in (
            "research dossiers",
            "market selection notes",
            "probability estimates",
            "model forecasts",
            "signal candidates",
            "calibration records",
            "hypothesis records",
            "audit events",
        ):
            self.assertIn(phrase, text)

    def test_pipeline_forbids_execution_outputs(self) -> None:
        text = PIPELINE_PATH.read_text(encoding="utf-8")

        for phrase in (
            "executable orders",
            "OrderIntent without a separate approved order-intent service",
            "ApprovedOrder",
            "broker or exchange requests",
            "wallet transactions",
            "private endpoint calls",
            "risk approvals",
            "execution approvals",
        ):
            self.assertIn(phrase, text)

    def test_pipeline_defines_safe_research_loops(self) -> None:
        text = PIPELINE_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "research loop",
            "strategy loop",
            "tactical analysis loop",
            "base rate",
            "evidence update",
            "adversarial review",
            "calibration adjustment",
            "hypothesis lifecycle",
            "brier score tracking",
        ):
            self.assertIn(phrase, text)

    def test_no_market_edge_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "market-edge",
            "py-clob-client",
            "tavily-python",
            "anthropic>=",
        ):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
