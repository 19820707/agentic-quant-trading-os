from pathlib import Path
import unittest


POLICY_PATH = Path("docs/architecture/external_adapter_safety_policy.md")


def _policy_text() -> str:
    return POLICY_PATH.read_text(encoding="utf-8")


class ExternalAdapterSafetyPolicyTests(unittest.TestCase):
    def test_required_sections_are_present(self):
        text = _policy_text()

        for section in (
            "## 1. Purpose",
            "## 2. Integration Lifecycle",
            "## 3. Universal Adapter Rules",
            "## 4. Market Data Adapter Rules",
            "## 5. Feature Store Adapter Rules",
            "## 6. Model Monitoring Adapter Rules",
            "## 7. Paper Trading Adapter Rules",
            "## 8. Future Execution Adapter Rules",
            "## 9. MCP / Agentic Adapter Rules",
            "## 10. Prohibited Names and Behaviors",
            "## 11. Required Review Checklist",
            "## 12. Failure Posture",
        ):
            self.assertIn(section, text)

    def test_prohibited_method_names_are_documented(self):
        text = _policy_text()

        for method_name in (
            "buy",
            "sell",
            "order",
            "create_order",
            "submit_order",
            "cancel_order",
            "modify_order",
            "withdraw",
            "transfer",
            "execute",
            "place_order",
        ):
            self.assertIn(f"- {method_name}", text)

    def test_policy_mentions_credentials_withdrawal_and_risk_gateway(self):
        text = _policy_text().lower()

        self.assertIn("no credentials by default", text)
        self.assertIn("no live broker credentials", text)
        self.assertIn("never use withdrawal permissions", text)
        self.assertIn("no bypassing deterministic-risk-gateway", text)
        self.assertIn("never bypass deterministic-risk-gateway", text)
        self.assertIn("no broker/exchange credentials outside approved execution-engine adapters", text)

    def test_policy_mentions_approved_order_only_execution_adapters(self):
        text = _policy_text()

        self.assertIn("accept only ApprovedOrder", text)
        self.assertIn("reject raw OrderIntent", text)
        self.assertIn("execution-engine", text)

    def test_policy_mentions_read_only_market_data_adapters(self):
        text = _policy_text().lower()

        self.assertIn("market data adapters are read-only only", text)
        self.assertIn("ohlcv", text)
        self.assertIn("order book snapshots", text)
        self.assertIn("open interest", text)

    def test_policy_mentions_point_in_time_feature_store_rules(self):
        text = _policy_text().lower()

        self.assertIn("point-in-time correctness", text)
        self.assertIn("event_timestamp", text)
        self.assertIn("created_timestamp", text)
        self.assertIn("available_timestamp", text)
        self.assertIn("future data leakage", text)

    def test_policy_mentions_mcp_tools_cannot_execute_trades(self):
        text = _policy_text().lower()

        self.assertIn("mcp tools cannot execute trades", text)
        self.assertIn("mcp tools cannot submit orders", text)
        self.assertIn("mcp tools cannot access broker credentials", text)
        self.assertIn("mcp tools cannot disable kill switches", text)

    def test_policy_mentions_no_vendoring_or_submodules_without_approval(self):
        text = _policy_text().lower()

        self.assertIn("no external repo vendoring", text)
        self.assertIn("no git submodule without explicit approval", text)

    def test_policy_mentions_fail_closed_behavior(self):
        text = _policy_text().lower()

        self.assertIn("fail closed under uncertainty", text)
        self.assertIn("reject unsafe adapter behavior", text)
        self.assertIn("prefer read-only behavior", text)
        self.assertIn("prefer paper-only behavior", text)

    def test_policy_test_is_local_only(self):
        self.assertTrue(POLICY_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
