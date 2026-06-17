import unittest

from config import ConfigurationError, Environment, TradingMode, load_settings


class ConfigSettingsTests(unittest.TestCase):
    def test_safe_defaults_disable_live_trading(self):
        settings = load_settings({})

        self.assertEqual(settings.environment, Environment.LOCAL)
        self.assertEqual(settings.trading_mode, TradingMode.DISABLED)
        self.assertFalse(settings.live_trading_enabled)
        self.assertFalse(settings.broker_exchange.integration_enabled)
        self.assertFalse(settings.broker_exchange.allow_withdrawals)
        self.assertFalse(settings.broker_exchange.allow_private_endpoints)
        self.assertTrue(settings.security.kill_switch_enabled)
        self.assertFalse(settings.security.allow_agent_execution)

    def test_paper_mode_is_separate_from_live_mode(self):
        settings = load_settings(
            {
                "AQTOS_ENVIRONMENT": "paper",
                "AQTOS_TRADING_MODE": "paper",
                "AQTOS_LIVE_TRADING_ENABLED": "false",
            }
        )

        self.assertEqual(settings.environment, Environment.PAPER)
        self.assertEqual(settings.trading_mode, TradingMode.PAPER)
        self.assertFalse(settings.live_trading_enabled)

    def test_live_flag_without_live_mode_is_rejected(self):
        with self.assertRaises(ConfigurationError):
            load_settings(
                {
                    "AQTOS_TRADING_MODE": "paper",
                    "AQTOS_LIVE_TRADING_ENABLED": "true",
                }
            )

    def test_live_mode_without_live_flag_is_rejected(self):
        with self.assertRaises(ConfigurationError):
            load_settings(
                {
                    "AQTOS_TRADING_MODE": "live",
                    "AQTOS_LIVE_TRADING_ENABLED": "false",
                }
            )

    def test_live_mode_requires_broker_integration(self):
        with self.assertRaisesRegex(ConfigurationError, "broker/exchange integration"):
            load_settings(
                {
                    "AQTOS_TRADING_MODE": "live",
                    "AQTOS_LIVE_TRADING_ENABLED": "true",
                }
            )

    def test_live_mode_requires_credential_reference_not_inline_secret(self):
        with self.assertRaisesRegex(ConfigurationError, "credential reference"):
            load_settings(
                {
                    "AQTOS_TRADING_MODE": "live",
                    "AQTOS_LIVE_TRADING_ENABLED": "true",
                    "AQTOS_BROKER_INTEGRATION_ENABLED": "true",
                }
            )

    def test_live_mode_requires_secrets_manager_controls(self):
        with self.assertRaisesRegex(ConfigurationError, "secrets_manager_enabled"):
            load_settings(
                {
                    "AQTOS_TRADING_MODE": "live",
                    "AQTOS_LIVE_TRADING_ENABLED": "true",
                    "AQTOS_BROKER_INTEGRATION_ENABLED": "true",
                    "AQTOS_BROKER_CREDENTIAL_REFERENCE": "paper_trading_reference",
                }
            )

    def test_production_live_requires_rbac(self):
        with self.assertRaisesRegex(ConfigurationError, "rbac_enabled"):
            load_settings(
                {
                    "AQTOS_ENVIRONMENT": "production",
                    "AQTOS_TRADING_MODE": "live",
                    "AQTOS_LIVE_TRADING_ENABLED": "true",
                    "AQTOS_BROKER_INTEGRATION_ENABLED": "true",
                    "AQTOS_BROKER_CREDENTIAL_REFERENCE": "production_reference",
                    "AQTOS_SECRETS_MANAGER_ENABLED": "true",
                    "AQTOS_KILL_SWITCH_ENABLED": "true",
                }
            )

    def test_production_rejects_disabled_kill_switch(self):
        with self.assertRaisesRegex(ConfigurationError, "kill_switch"):
            load_settings(
                {
                    "AQTOS_ENVIRONMENT": "production",
                    "AQTOS_KILL_SWITCH_ENABLED": "false",
                }
            )

    def test_withdrawals_are_never_allowed(self):
        with self.assertRaisesRegex(ConfigurationError, "withdrawal"):
            load_settings({"AQTOS_ALLOW_WITHDRAWALS": "true"})

    def test_agent_execution_authority_is_rejected(self):
        with self.assertRaisesRegex(ConfigurationError, "agent execution"):
            load_settings({"AQTOS_ALLOW_AGENT_EXECUTION": "true"})

    def test_invalid_environment_fails_explicitly(self):
        with self.assertRaisesRegex(ConfigurationError, "invalid environment"):
            load_settings({"AQTOS_ENVIRONMENT": "unsafe"})

    def test_invalid_boolean_fails_explicitly(self):
        with self.assertRaisesRegex(ConfigurationError, "invalid boolean"):
            load_settings({"AQTOS_LIVE_TRADING_ENABLED": "maybe"})

    def test_safe_live_configuration_can_be_loaded_but_does_not_execute(self):
        settings = load_settings(
            {
                "AQTOS_ENVIRONMENT": "staging",
                "AQTOS_TRADING_MODE": "live",
                "AQTOS_LIVE_TRADING_ENABLED": "true",
                "AQTOS_BROKER_INTEGRATION_ENABLED": "true",
                "AQTOS_BROKER_CREDENTIAL_REFERENCE": "staging_reference",
                "AQTOS_SECRETS_MANAGER_ENABLED": "true",
                "AQTOS_RBAC_ENABLED": "true",
                "AQTOS_KILL_SWITCH_ENABLED": "true",
            }
        )

        self.assertEqual(settings.environment, Environment.STAGING)
        self.assertEqual(settings.trading_mode, TradingMode.LIVE)
        self.assertTrue(settings.live_trading_enabled)
        self.assertEqual(settings.broker_exchange.credential_reference, "staging_reference")


if __name__ == "__main__":
    unittest.main()
