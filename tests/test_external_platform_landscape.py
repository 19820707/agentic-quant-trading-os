import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "architecture" / "external_platform_landscape.md"


PLATFORMS = [
    "QuantConnect / LEAN",
    "Interactive Brokers API",
    "Alpaca API",
    "Hummingbot",
    "TradingView",
    "NinjaTrader",
    "TradeStation",
    "MetaTrader 5",
    "cTrader",
    "3Commas",
    "Cryptohopper",
    "Bitsgap",
    "Pionex",
    "Coinrule",
    "WunderTrading",
    "TradeSanta",
    "TrendSpider",
]

CATEGORIES = [
    "research_backtesting_engine",
    "execution_broker_api",
    "crypto_strategy_runtime",
    "signal_source",
    "commercial_bot_reference",
    "futures_trading_platform",
    "forex_cfd_platform",
    "ux_research_only",
]


class ExternalPlatformLandscapeTests(unittest.TestCase):
    def setUp(self):
        self.text = DOCUMENT.read_text(encoding="utf-8")
        self.lower_text = self.text.lower()

    def test_document_exists(self):
        self.assertTrue(DOCUMENT.is_file())
        self.assertIn("External Platform Landscape", self.text)

    def test_every_platform_is_documented(self):
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                self.assertIn(platform, self.text)

    def test_every_category_is_documented(self):
        for category in CATEGORIES:
            with self.subTest(category=category):
                self.assertIn(category, self.text)

    def test_all_platforms_are_reference_only_for_now(self):
        self.assertIn("All platforms listed here are reference-only for now.", self.text)
        self.assertGreaterEqual(self.text.count("Reference-only documentation"), len(PLATFORMS))

    def test_current_state_blocks_runtime_install_network_and_credentials(self):
        required_blocks = [
            "No runtime integration is approved.",
            "No dependency installation is approved.",
            "No broker, exchange or client SDK is approved.",
            "No credentials are allowed.",
            "No network access is allowed.",
            "No live trading is approved.",
            "No paper trading runtime is approved.",
            "No backtesting runtime is approved.",
            "No market data ingestion is approved.",
            "No webhook ingestion is approved.",
            "No signal ingestion is approved.",
            "No broker or exchange execution is approved.",
            "No autonomous order submission is approved.",
        ]

        for block in required_blocks:
            with self.subTest(block=block):
                self.assertIn(block, self.text)

    def test_deterministic_risk_gateway_is_mandatory(self):
        self.assertIn("deterministic-risk-gateway", self.text)
        self.assertIn("Any future execution path must pass through deterministic-risk-gateway", self.text)

    def test_signal_tools_are_distinguished_from_execution_tools(self):
        self.assertIn("Signal tools and execution tools are different classes of systems.", self.text)
        self.assertIn("Signal tools may only be considered as future sources for normalized `SignalCandidate` records.", self.text)
        self.assertIn("Execution tools may only be considered as future execution-engine adapters", self.text)

    def test_tradingview_alerts_become_signal_candidate_only(self):
        self.assertIn("TradingView-style alerts must become `SignalCandidate` only.", self.text)
        self.assertIn("They must never trigger direct execution.", self.text)

    def test_broker_apis_only_receive_approved_order_in_future(self):
        self.assertIn("Broker APIs may only receive `ApprovedOrder` in the future", self.text)
        self.assertIn("They must never receive direct calls from LLMs, models, agents, dashboards, notebooks, backtests or signal services.", self.text)

    def test_llms_must_never_call_broker_or_exchange_apis_directly(self):
        self.assertIn("No LLM, agent, model, dashboard, notebook or research service may call broker or exchange APIs directly.", self.text)

    def test_document_does_not_claim_approval_for_runtime_capabilities(self):
        forbidden_claims = [
            "runtime integration is enabled",
            "dependency installation is allowed",
            "credentials may be used",
            "network access may be used",
            "live trading is enabled",
            "paper trading runtime is enabled",
            "backtesting runtime is enabled",
            "market data ingestion is enabled",
            "signal ingestion is enabled",
            "autonomous order submission is enabled",
            "broker execution is enabled",
            "exchange execution is enabled",
        ]

        for claim in forbidden_claims:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, self.lower_text)


if __name__ == "__main__":
    unittest.main()
