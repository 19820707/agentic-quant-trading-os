from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "security" / "prediction_market_repo_intake_audit.md"
CATALOG = ROOT / "docs" / "architecture" / "external_projects_catalog.md"
PYPROJECT = ROOT / "pyproject.toml"
PACKAGE_JSON = ROOT / "package.json"


EXPECTED_REPOSITORIES = (
    "https://github.com/datori/market-edge",
    "https://github.com/mjunaidca/polymarket-skills",
    "https://github.com/InjayTseng/Trading-Agent-Polymarket",
    "https://github.com/pmxt-dev/pmxt-mcp",
    "https://github.com/Composio-HQ/polymarket-kalshi-arbitrage-bot",
    "https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits",
    "https://github.com/neilt93/Prediction-Market-Agent",
    "https://github.com/lmhtq/polymarket-ai-agent",
    "https://github.com/yigitcankzl/PolymarketSignalAgent",
    "https://github.com/SXai-lab/prediction-market-arbitrage",
    "https://github.com/SXai-lab/prediction-market-copytrade",
    "https://github.com/zkOSAI/polymarket-arbitrage-bot",
)


class PredictionMarketRepoIntakeAuditTests(unittest.TestCase):
    def test_all_requested_unique_repositories_are_documented(self) -> None:
        text = AUDIT.read_text(encoding="utf-8")
        for url in EXPECTED_REPOSITORIES:
            self.assertIn(url, text)
        self.assertIn("Duplicate input", text)

    def test_decision_blocks_installation_and_runtime_wiring(self) -> None:
        text = AUDIT.read_text(encoding="utf-8").lower()
        for phrase in (
            "do not clone, vendor, install, import, execute or run",
            "reference-only intake gate",
            "no install",
            "read-only mcp candidate only",
            "live executor disabled",
            "order tools blocked",
            "deterministic-risk-gateway",
        ):
            self.assertIn(phrase, text)

    def test_catalog_links_intake_audit_and_blocks_default_installation(self) -> None:
        text = CATALOG.read_text(encoding="utf-8").lower()
        self.assertIn("prediction market repository intake audit", text)
        self.assertIn("do not clone, vendor, install or add submodules by default", text)
        self.assertIn("prediction-market trading bots require an intake audit", text)

    def test_no_requested_repositories_are_added_as_dependencies(self) -> None:
        combined = "\n".join(
            (
                PYPROJECT.read_text(encoding="utf-8"),
                PACKAGE_JSON.read_text(encoding="utf-8"),
            )
        ).lower()
        forbidden_dependency_markers = (
            "market-edge",
            "polymarket-skills",
            "trading-agent-polymarket",
            "pmxt-mcp",
            "@pmxt/mcp",
            "polymarket-kalshi-arbitrage-bot",
            "prediction-markets-trading-bot-toolkits",
            "prediction-market-agent",
            "polymarket-ai-agent",
            "polymarketsignalagent",
            "prediction-market-arbitrage",
            "prediction-market-copytrade",
            "polymarket-arbitrage-bot",
        )
        for marker in forbidden_dependency_markers:
            self.assertNotIn(marker, combined)


if __name__ == "__main__":
    unittest.main()
