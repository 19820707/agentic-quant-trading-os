from pathlib import Path
import unittest


HARNESS_PATH = Path("docs/integrations/ccxt_readonly_adapter_safety_harness.md")


def _harness_text() -> str:
    return HARNESS_PATH.read_text(encoding="utf-8")


class CcxtReadOnlyAdapterSafetyHarnessTests(unittest.TestCase):
    def test_required_sections_exist(self):
        text = _harness_text()

        for section in (
            "## 1. Purpose",
            "## 2. Scope",
            "## 3. Required Internal Interfaces",
            "## 4. Credential Boundary",
            "## 5. Network Boundary",
            "## 6. Prohibited Method Names",
            "## 7. Testing Harness Requirements",
            "## 8. Review Gates",
            "## 9. Current Decision",
        ):
            self.assertIn(section, text)

    def test_harness_is_not_an_adapter_implementation(self):
        text = _harness_text().lower()

        self.assertIn("not an adapter implementation", text)
        self.assertIn("does not add the `ccxt` dependency", text)
        self.assertIn("must not add ccxt", text)

    def test_harness_limits_ccxt_to_read_only_market_data(self):
        text = _harness_text().lower()

        self.assertIn("read-only market data", text)
        self.assertIn("fetch ohlcv", text)
        self.assertIn("fetch recent trades", text)
        self.assertIn("fetch order book snapshots", text)
        self.assertIn("fetch funding rates", text)
        self.assertIn("fetch open interest", text)

    def test_harness_requires_internal_adapter_interface(self):
        text = _harness_text()

        self.assertIn("ReadOnlyMarketDataAdapter", text)
        self.assertIn("packages.common.market_data", text)
        self.assertIn("market data adapter registry", text)

    def test_harness_prohibits_order_and_execution_behavior(self):
        text = _harness_text()

        for phrase in (
            "create OrderIntent",
            "create ApprovedOrder",
            "submit orders",
            "create orders",
            "cancel orders",
            "modify orders",
            "execute trades",
            "approve risk",
            "approve execution",
        ):
            self.assertIn(phrase, text)

    def test_harness_prohibits_credentials_and_withdrawal_permissions(self):
        text = _harness_text().lower()

        self.assertIn("must not require credentials for unit tests", text)
        self.assertIn("api keys", text)
        self.assertIn("secret keys", text)
        self.assertIn("withdrawal keys", text)
        self.assertIn("must not include", text)

    def test_harness_prohibits_network_in_unit_tests(self):
        text = _harness_text().lower()

        self.assertIn("unit tests must not call network", text)
        self.assertIn("explicit timeouts", text)
        self.assertIn("bounded retries", text)
        self.assertIn("rate-limit handling", text)
        self.assertIn("stale data behavior", text)

    def test_harness_documents_prohibited_method_names(self):
        text = _harness_text()

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

    def test_harness_requires_fake_in_memory_tests_first(self):
        text = _harness_text().lower()

        self.assertIn("fake/in-memory exchange clients are used first", text)
        self.assertIn("no `ccxt` import is required for unit tests", text)
        self.assertIn("no network is called", text)
        self.assertIn("no credentials are required", text)

    def test_harness_references_review_gates(self):
        text = _harness_text().lower()

        self.assertIn("external adapter review checklist completed", text)
        self.assertIn("external adapter safety policy followed", text)
        self.assertIn("dependency addition explicitly approved", text)
        self.assertIn("ci quality gates updated", text)

    def test_harness_test_is_local_only(self):
        self.assertTrue(HARNESS_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
