from pathlib import Path
import unittest


README_PATH = Path("integrations/market-data/ccxt/README.md")
CHECKLIST_PATH = Path("integrations/market-data/ccxt/adapter_review_checklist.md")
PROHIBITED_IMPLEMENTATION_PATHS = (
    Path("packages/sdk/ccxt_adapter.py"),
    Path("integrations/market-data/ccxt/ccxt_adapter.py"),
)


def _readme_text() -> str:
    return README_PATH.read_text(encoding="utf-8")


def _checklist_text() -> str:
    return CHECKLIST_PATH.read_text(encoding="utf-8")


class CcxtReadOnlyAdapterSafetyHarnessTests(unittest.TestCase):
    def test_upstream_url_is_documented(self):
        self.assertIn("https://github.com/ccxt/ccxt", _readme_text())
        self.assertIn("https://github.com/ccxt/ccxt", _checklist_text())

    def test_target_interface_is_documented(self):
        self.assertIn("ReadOnlyMarketDataAdapter", _readme_text())

    def test_allowed_read_only_operations_are_documented(self):
        text = _readme_text().lower()

        for operation in (
            "fetch ohlcv",
            "fetch public trades",
            "fetch order book snapshots",
            "fetch funding rates",
            "fetch market metadata",
        ):
            self.assertIn(operation, text)

    def test_prohibited_dangerous_operations_are_documented(self):
        text = _readme_text()

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

    def test_credential_boundaries_are_documented(self):
        text = _readme_text().lower()

        self.assertIn("no credentials in unit tests", text)
        self.assertIn("no trade credentials", text)
        self.assertIn("no withdrawal credentials", text)

    def test_network_boundary_is_documented(self):
        text = _readme_text().lower()

        self.assertIn("no network calls in unit tests", text)
        self.assertIn("no real exchange calls in ci", text)

    def test_future_adapter_must_not_expose_dangerous_methods(self):
        text = _readme_text().lower()

        self.assertIn("avoid dangerous method names", text)
        self.assertIn("must not expose or implement", text)

    def test_future_adapter_must_not_bypass_risk_gateway(self):
        self.assertIn("bypass deterministic-risk-gateway", _readme_text())

    def test_current_status_is_safety_harness_only(self):
        text = _readme_text().lower()

        self.assertIn("current status: safety harness only", text)
        self.assertIn("does not implement a ccxt adapter", text)
        self.assertIn("does not import `ccxt`", text)

    def test_checklist_has_required_review_items(self):
        text = _checklist_text().lower()

        self.assertIn("current classification: research-only / safety-harness-only", text)
        self.assertIn("license reviewed", text)
        self.assertIn("no credentials for unit tests", text)
        self.assertIn("no network calls in unit tests", text)
        self.assertIn("fake/in-memory client used first", text)

    def test_no_ccxt_adapter_implementation_file_exists_yet(self):
        for path in PROHIBITED_IMPLEMENTATION_PATHS:
            self.assertFalse(path.exists(), f"{path} must not exist in safety harness PR")

    def test_harness_files_are_local_docs_only(self):
        self.assertTrue(README_PATH.is_file())
        self.assertTrue(CHECKLIST_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
