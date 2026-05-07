import copy
import unittest

from packages.common.security import REDACTED_VALUE, is_sensitive_key, redact_secrets, redact_value


class SecurityRedactionTests(unittest.TestCase):
    def test_exact_sensitive_key_redaction(self):
        payload = {"api_key": "example-api-key", "symbol": "BTC/USDT"}

        redacted = redact_secrets(payload)

        self.assertEqual(redacted["api_key"], REDACTED_VALUE)
        self.assertEqual(redacted["symbol"], "BTC/USDT")

    def test_case_insensitive_key_redaction(self):
        payload = {"Authorization": "Bearer example-token", "Password": "example-password"}

        redacted = redact_secrets(payload)

        self.assertEqual(redacted["Authorization"], REDACTED_VALUE)
        self.assertEqual(redacted["Password"], REDACTED_VALUE)

    def test_nested_dictionary_redaction(self):
        payload = {
            "metadata": {
                "secret_key": "example-secret",
                "safe_note": "paper-only fixture",
            }
        }

        redacted = redact_secrets(payload)

        self.assertEqual(redacted["metadata"]["secret_key"], REDACTED_VALUE)
        self.assertEqual(redacted["metadata"]["safe_note"], "paper-only fixture")

    def test_list_of_dictionaries_redaction(self):
        payload = {
            "events": [
                {"token": "example-token", "status": "INFO"},
                {"message": "safe"},
            ]
        }

        redacted = redact_secrets(payload)

        self.assertEqual(redacted["events"][0]["token"], REDACTED_VALUE)
        self.assertEqual(redacted["events"][0]["status"], "INFO")
        self.assertEqual(redacted["events"][1]["message"], "safe")

    def test_tuple_and_list_redaction(self):
        payload = ({"refresh_token": "example-refresh-token"}, ["safe", {"passwd": "example"}])

        redacted = redact_secrets(payload)

        self.assertIsInstance(redacted, list)
        self.assertEqual(redacted[0]["refresh_token"], REDACTED_VALUE)
        self.assertEqual(redacted[1][0], "safe")
        self.assertEqual(redacted[1][1]["passwd"], REDACTED_VALUE)

    def test_non_sensitive_values_preserved(self):
        payload = {"venue": "paper", "quantity": 1.5, "active": True, "note": None}

        redacted = redact_secrets(payload)

        self.assertEqual(redacted, payload)

    def test_input_object_is_not_mutated(self):
        payload = {"credentials": {"token": "example-token"}, "safe": ["value"]}
        original = copy.deepcopy(payload)

        redacted = redact_secrets(payload)

        self.assertEqual(payload, original)
        self.assertNotEqual(redacted, payload)
        self.assertEqual(redacted["credentials"], REDACTED_VALUE)

    def test_broker_and_exchange_key_names_are_redacted(self):
        payload = {
            "broker_key": "example-broker-key",
            "exchange_key": "example-exchange-key",
        }

        redacted = redact_secrets(payload)

        self.assertEqual(redacted["broker_key"], REDACTED_VALUE)
        self.assertEqual(redacted["exchange_key"], REDACTED_VALUE)

    def test_withdrawal_key_is_redacted(self):
        self.assertTrue(is_sensitive_key("withdrawal_key"))

        redacted = redact_secrets({"withdrawal_key": "never-use-withdrawal-key"})

        self.assertEqual(redacted["withdrawal_key"], REDACTED_VALUE)

    def test_arbitrary_non_sensitive_strings_are_not_modified(self):
        text = "authorization appears in this diagnostic sentence but is not keyed"

        self.assertEqual(redact_value(text), text)
        self.assertEqual(redact_secrets(text), text)

    def test_no_network_or_credentials_required(self):
        payload = {"message": "local-only redaction", "adapter": "in-memory"}

        redacted = redact_secrets(payload)

        self.assertEqual(redacted, payload)


if __name__ == "__main__":
    unittest.main()
