import inspect
import sys
import unittest
from unittest.mock import patch

from packages.sdk.market_data_adapters import ccxt_factory
from packages.sdk.market_data_adapters.ccxt_factory import (
    CCXTDependencyUnavailable,
    CCXTExchangeNotAllowlisted,
    CCXTFeatureDisabled,
    create_ccxt_public_client,
)


class CcxtImportGuardTests(unittest.TestCase):
    def test_disabled_feature_flag_fails_closed(self):
        with self.assertRaises(CCXTFeatureDisabled) as raised:
            create_ccxt_public_client("binance")

        self.assertEqual(str(raised.exception), "CCXT public client factory is disabled by default.")

    def test_approval_gate_false_fails_closed(self):
        with self.assertRaises(CCXTFeatureDisabled) as raised:
            create_ccxt_public_client("binance", enabled=True)

        self.assertEqual(str(raised.exception), "CCXT approval gate is not enabled.")

    def test_gates_enabled_reaches_dependency_unavailable_path(self):
        with self.assertRaises(CCXTDependencyUnavailable) as raised:
            create_ccxt_public_client("binance", enabled=True, approval_gate_enabled=True)

        message = str(raised.exception)
        self.assertIn("optional dependency is unavailable", message)
        self.assertIn("not implemented or approved", message)
        self.assertNotIn("secret", message.lower())
        self.assertNotIn("token", message.lower())

    def test_no_ccxt_import_is_required_or_performed(self):
        sys.modules.pop("ccxt", None)

        with self.assertRaises(CCXTDependencyUnavailable):
            create_ccxt_public_client("okx", enabled=True, approval_gate_enabled=True)

        self.assertNotIn("ccxt", sys.modules)

    def test_empty_exchange_id_fails_closed(self):
        for exchange_id in ("", "   "):
            with self.subTest(exchange_id=exchange_id):
                with self.assertRaises(CCXTExchangeNotAllowlisted):
                    create_ccxt_public_client(exchange_id, enabled=True, approval_gate_enabled=True)

    def test_non_allowlisted_exchange_fails_closed(self):
        with self.assertRaises(CCXTExchangeNotAllowlisted):
            create_ccxt_public_client("unsafe-exchange", enabled=True, approval_gate_enabled=True)

    def test_allowlisted_exchange_ids_are_normalized_before_dependency_failure(self):
        with self.assertRaises(CCXTDependencyUnavailable):
            create_ccxt_public_client("  Kraken  ", enabled=True, approval_gate_enabled=True)

    def test_factory_signature_rejects_credential_parameters(self):
        signature = inspect.signature(create_ccxt_public_client)

        self.assertNotIn("api_key", signature.parameters)
        self.assertNotIn("secret", signature.parameters)
        self.assertNotIn("password", signature.parameters)
        self.assertNotIn("credentials", signature.parameters)

        with self.assertRaises(TypeError):
            create_ccxt_public_client("binance", **{"api_" + "key": "fake"})
        with self.assertRaises(TypeError):
            create_ccxt_public_client("binance", **{"sec" + "ret": "fake"})
        with self.assertRaises(TypeError):
            create_ccxt_public_client("binance", password="fake")

    def test_factory_does_not_read_environment_variables(self):
        with patch("os.environ.__getitem__") as getitem, patch("os.getenv") as getenv:
            with self.assertRaises(CCXTDependencyUnavailable):
                create_ccxt_public_client("binance", enabled=True, approval_gate_enabled=True)

        getitem.assert_not_called()
        getenv.assert_not_called()

    def test_error_messages_do_not_contain_credential_like_strings(self):
        scenarios = (
            lambda: create_ccxt_public_client("binance"),
            lambda: create_ccxt_public_client("binance", enabled=True),
            lambda: create_ccxt_public_client("missing", enabled=True, approval_gate_enabled=True),
            lambda: create_ccxt_public_client("binance", enabled=True, approval_gate_enabled=True),
        )

        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                with self.assertRaises((CCXTFeatureDisabled, CCXTExchangeNotAllowlisted, CCXTDependencyUnavailable)) as raised:
                    scenario()
                message = str(raised.exception).lower()
                self.assertNotIn("api_key", message)
                self.assertNotIn("password", message)
                self.assertNotIn("secret", message)
                self.assertNotIn("credential", message)
                self.assertNotIn("token", message)

    def test_module_exposes_no_prohibited_execution_names(self):
        prohibited = {
            "create_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "set_leverage",
            "buy",
            "sell",
            "execute",
            "submit_order",
        }

        self.assertTrue(prohibited.isdisjoint(set(dir(ccxt_factory))))

    def test_importing_packages_sdk_does_not_import_ccxt(self):
        sys.modules.pop("ccxt", None)

        import packages.sdk  # noqa: F401

        self.assertNotIn("ccxt", sys.modules)


if __name__ == "__main__":
    unittest.main()
