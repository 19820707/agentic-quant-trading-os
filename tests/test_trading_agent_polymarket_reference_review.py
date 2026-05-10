from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/trading_agent_polymarket_reference_review.md")
GRAPH_PATH = Path("docs/architecture/multi_agent_research_graph.md")
PYPROJECT = Path("pyproject.toml")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


class TradingAgentPolymarketReferenceReviewTests(unittest.TestCase):
    def test_review_document_exists(self) -> None:
        self.assertTrue(REVIEW_PATH.is_file())

    def test_review_keeps_repository_reference_only(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "langgraph_allowed: false",
            "langchain_allowed: false",
            "llm_provider_sdk_allowed: false",
            "polymarket_gamma_allowed: false",
            "polymarket_websocket_allowed: false",
            "newsapi_allowed: false",
            "trading_decision_authority_allowed: false",
            "kelly_sizing_for_execution_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_review_extracts_safe_multi_agent_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "multi-agent state machine",
            "specialized analyst team",
            "yes / no research debate",
            "advisory risk debate",
            "structured signal processor",
            "similar-market memory",
            "llm provider abstraction",
        ):
            self.assertIn(phrase, text)

    def test_review_rejects_runtime_components(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "do not reuse directly",
            "langgraph runtime",
            "langchain dependencies",
            "provider sdks",
            "python-dotenv",
            "newsapi integration",
            "live polymarket gamma calls",
            "polymarket websocket calls",
            "kelly sizing connected to a trading decision",
            "buy_yes or buy_no as operational commands",
        ):
            self.assertIn(phrase, text)

    def test_graph_document_exists(self) -> None:
        self.assertTrue(GRAPH_PATH.is_file())

    def test_graph_defines_non_executable_outputs(self) -> None:
        text = GRAPH_PATH.read_text(encoding="utf-8")

        for phrase in (
            "analyst reports",
            "debate transcripts",
            "research manager summaries",
            "probability estimates",
            "signal candidates",
            "risk-review inputs",
            "audit events",
        ):
            self.assertIn(phrase, text)

    def test_graph_forbids_execution_outputs(self) -> None:
        text = GRAPH_PATH.read_text(encoding="utf-8")

        for phrase in (
            "executable orders",
            "ApprovedOrder",
            "broker or exchange calls",
            "wallet actions",
            "private endpoint calls",
            "execution approval",
            "risk approval",
            "live trading decisions",
        ):
            self.assertIn(phrase, text)

    def test_graph_defines_required_phases(self) -> None:
        text = GRAPH_PATH.read_text(encoding="utf-8")

        for phrase in (
            "Phase 1: Analyst Reports",
            "Phase 2: YES / NO Debate",
            "Phase 3: Signal Candidate Formatting",
            "Phase 4: Advisory Risk Review",
            "event analyst",
            "odds analyst",
            "information analyst",
            "sentiment analyst",
        ):
            self.assertIn(phrase, text)

    def test_graph_preserves_deterministic_risk_gateway_authority(self) -> None:
        text = GRAPH_PATH.read_text(encoding="utf-8")

        for phrase in (
            "Forbidden outputs",
            "APPROVE",
            "ApprovedOrder",
            "execution permission",
            "risk-limit override",
            "kill-switch disablement",
            "deterministic-risk-gateway remains the only future pre-trade authority",
        ):
            self.assertIn(phrase, text)

    def test_no_trading_agent_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "trading-agent-polymarket",
            "langgraph",
            "langchain",
            "langchain-openai",
            "langchain-anthropic",
            "langchain-google-genai",
            "python-dotenv",
            "rank-bm25",
            "newsapi",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_trading_agent_reference_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_trading_agent_polymarket_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
