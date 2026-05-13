from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/pnlclaw_community_reference_review.md")
BOUNDARY_PATH = Path("docs/architecture/local_first_agentic_quant_boundary.md")
PYPROJECT = Path("pyproject.toml")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


class PnlclawCommunityReferenceReviewTests(unittest.TestCase):
    def test_review_document_exists(self) -> None:
        self.assertTrue(REVIEW_PATH.is_file())

    def test_review_keeps_repository_reference_only(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "trading_methods_allowed: false",
            "agent_runtime_allowed: false",
            "mcp_runtime_allowed: false",
            "llm_provider_runtime_allowed: false",
            "exchange_runtime_allowed: false",
            "paper_runtime_allowed: false",
            "desktop_runtime_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_review_extracts_local_first_agent_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "skill registry",
            "tool policy",
            "react loop guard",
            "local-first boundary",
            "agent skill definition contracts",
            "tool call audit records",
            "agent loop guard contracts",
        ):
            self.assertIn(phrase, text)

    def test_review_rejects_runtime_components(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "desktop application runtime",
            "local api runtime",
            "agent runtime",
            "mcp runtime",
            "llm provider runtime",
            "exchange websocket runtime",
            "strategy compiler runtime",
            "backtest or paper trading execution runtime",
            "deployment workflows",
        ):
            self.assertIn(phrase, text)

    def test_boundary_blocks_agent_operational_authority(self) -> None:
        text = BOUNDARY_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "does not approve agent runtime",
            "shell execution",
            "file writes",
            "network calls",
            "credential access",
            "broker or exchange access",
            "order creation",
            "risk approval",
            "execution approval",
            "all skills and tools start disabled",
        ):
            self.assertIn(phrase, text)

    def test_no_pnlclaw_runtime_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "pnlclaw",
            "tauri",
            "ollama",
            "langchain",
            "mcp",
            "openai-compatible",
            "binance",
            "okx",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_pnlclaw_reference_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_pnlclaw_community_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
