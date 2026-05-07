import copy
import unittest

from packages.common.security import REDACTED_VALUE, redact_secrets


class RedactionAuditPayloadTests(unittest.TestCase):
    def test_audit_event_like_payload_redacts_structured_secret_fields(self):
        payload = {
            "audit_id": "audit_example_001",
            "event_type": "SECRET_LEAK_DETECTED",
            "event_category": "SECURITY",
            "contains_secrets": False,
            "before": {
                "api_key": "example-api-key",
                "secret": "fake-secret-value",
                "status": "unredacted",
            },
            "after": {
                "api_key": REDACTED_VALUE,
                "secret": REDACTED_VALUE,
                "status": "redacted",
            },
            "metadata": {
                "authorization": "Bearer example-token",
                "source": "local-test",
            },
        }
        original = copy.deepcopy(payload)

        redacted = redact_secrets(payload)

        self.assertEqual(payload, original)
        self.assertEqual(redacted["before"]["api_key"], REDACTED_VALUE)
        self.assertEqual(redacted["before"]["secret"], REDACTED_VALUE)
        self.assertEqual(redacted["after"]["api_key"], REDACTED_VALUE)
        self.assertEqual(redacted["after"]["secret"], REDACTED_VALUE)
        self.assertEqual(redacted["metadata"]["authorization"], REDACTED_VALUE)
        self.assertEqual(redacted["metadata"]["source"], "local-test")

    def test_execution_report_like_payload_redacts_error_context(self):
        payload = {
            "execution_report_id": "exec_report_example_001",
            "execution_mode": "PAPER",
            "venue": "paper",
            "status": "PAPER_REJECTED",
            "error_context": {
                "token": "example-token",
                "broker_key": "example-broker-key",
                "message": "paper adapter rejected an invalid request",
            },
        }

        redacted = redact_secrets(payload)

        self.assertEqual(redacted["error_context"]["token"], REDACTED_VALUE)
        self.assertEqual(redacted["error_context"]["broker_key"], REDACTED_VALUE)
        self.assertEqual(
            redacted["error_context"]["message"],
            "paper adapter rejected an invalid request",
        )

    def test_report_payload_redacts_nested_lists(self):
        payload = {
            "report_id": "report_example_001",
            "sections": [
                {
                    "title": "security summary",
                    "credentials": {
                        "exchange_key": "example-exchange-key",
                    },
                },
                {
                    "title": "safe metrics",
                    "values": [1, 2, 3],
                },
            ],
        }

        redacted = redact_secrets(payload)

        self.assertEqual(redacted["sections"][0]["credentials"], REDACTED_VALUE)
        self.assertEqual(redacted["sections"][1]["values"], [1, 2, 3])

    def test_error_payload_redacts_withdrawal_key_without_mutating_input(self):
        payload = {
            "error_code": "LOCAL_VALIDATION_ERROR",
            "error": {
                "withdrawal_key": "never-use-withdrawal-key",
                "message": "local validation failed",
            },
        }
        original = copy.deepcopy(payload)

        redacted = redact_secrets(payload)

        self.assertEqual(payload, original)
        self.assertEqual(redacted["error"]["withdrawal_key"], REDACTED_VALUE)
        self.assertEqual(redacted["error"]["message"], "local validation failed")

    def test_free_form_messages_are_not_parsed_for_secret_patterns(self):
        payload = {
            "audit_id": "audit_example_002",
            "reason": "token appears as ordinary text and is not parsed without a sensitive key",
        }

        redacted = redact_secrets(payload)

        self.assertEqual(redacted, payload)

    def test_payload_redaction_is_local_only_and_requires_no_credentials(self):
        payload = {
            "report_id": "report_example_002",
            "environment": "local-test",
            "contains_secrets": False,
        }

        redacted = redact_secrets(payload)

        self.assertEqual(redacted, payload)


if __name__ == "__main__":
    unittest.main()
