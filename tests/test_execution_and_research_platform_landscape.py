import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANDSCAPE = ROOT / "docs" / "architecture" / "execution_and_research_platform_landscape.md"
CATALOG = ROOT / "docs" / "architecture" / "external_projects_catalog.md"


class ExecutionAndResearchPlatformLandscapeTests(unittest.TestCase):
    def setUp(self):
        self.landscape = LANDSCAPE.read_text(encoding="utf-8")
        self.catalog = CATALOG.read_text(encoding="utf-8")
        self.landscape_lower = self.landscape.lower()

    def test_platform_landscape_document_exists(self):
        self.assertTrue(LANDSCAPE.is_file())
        self.assertIn("Execution and Research Platform Landscape", self.landscape)

    def test_core_platforms_are_classified(self):
        required_platforms = [
            "QuantConnect / LEAN",
            "Interactive Brokers API",
            "Alpaca",
            "Hummingbot",
            "TradingView",
            "3Commas",
            "Bitsgap",
            "Cryptohopper",
            "Pionex",
            "Coinrule",
            "NinjaTrader",
            "TradeStation",
            "MetaTrader 5",
            "cTrader",
        ]

        for platform in required_platforms:
            with self.subTest(platform=platform):
                self.assertIn(platform, self.landscape)

    def test_platforms_remain_reference_blocked_or_deferred(self):
        required_states = [
            "Research reference only",
            "Blocked",
            "Blocked until adapter gates",
            "Isolated review candidate",
            "Contract-only first",
            "Reference only",
            "Deferred",
        ]

        for state in required_states:
            with self.subTest(state=state):
                self.assertIn(state, self.landscape)

    def test_landscape_forbids_unsafe_paths_and_live_execution(self):
        required_boundaries = [
            "direct AI/model/dashboard/agent to broker or exchange",
            "credentials in agents, dashboards, notebooks or tests",
            "raw `OrderIntent` execution",
            "live order submission",
            "transfer or withdrawal",
            "production enablement without explicit gates",
            "never AI/model/dashboard direct",
            "never webhook-to-order",
        ]

        for boundary in required_boundaries:
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, self.landscape)

    def test_landscape_requires_risk_gateway_and_contract_flow(self):
        required_terms = [
            "deterministic risk gateway",
            "SignalCandidate",
            "RiskReviewInput",
            "ApprovedOrder",
            "ExecutionReport",
            "Broker adapter safety policy",
            "Execution venue capability contract",
        ]

        for term in required_terms:
            with self.subTest(term=term):
                self.assertIn(term, self.landscape)

    def test_document_does_not_approve_install_or_runtime(self):
        forbidden_claims = [
            "approved for installation",
            "runtime enabled",
            "production ready",
            "live trading enabled",
            "credentials allowed",
            "network enabled",
        ]

        for claim in forbidden_claims:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, self.landscape_lower)

    def test_external_catalog_links_to_landscape(self):
        self.assertIn("execution_and_research_platform_landscape.md", self.catalog)
        self.assertIn("Broker/exchange APIs are blocked", self.catalog)
        self.assertIn("Commercial bot platforms are UX/reference-only", self.catalog)


if __name__ == "__main__":
    unittest.main()
