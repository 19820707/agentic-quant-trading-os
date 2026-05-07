import copy
import unittest
from datetime import datetime, timezone

from packages.common.audit import AuditEventBuildError, AuditEventEmitter
from packages.common.security import REDACTED_VALUE


def _builder() -> AuditEventEmitter:
    return AuditEventEmitter(source_service="observability-audit-service")


def _required_inputs() -> dict[str, str]:
    return {
        "trace_id": "trace_example_001",
        "correlation_id": "corr_example_001",
        "event_type": "RISK_DECISION_CREATED",
        "event_category": "RISK",
        "actor_type": "SERVICE",
        "actor_id": "deterministic-risk-gateway",
        "action": "record_risk_decision",
        "entity_type": "RISK_DECISION",
        "entity_id": "risk_example_001",
        "outcome": "SUCCESS",
    }


class AuditEventEmitterInterfaceTests(unittest.TestCase):
    def test_emitter_requires_non_empty_source_service(self):
        with self.assertRaises(AuditEventBuildError):
            AuditEventEmitter(source_service="")

    def test_build_event_returns_required_audit_fields(self):
        payload = _builder().build_event(**_required_inputs())

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["trace_id"], "trace_example_001")
        self.assertEqual(payload["correlation_id"], "corr_example_001")
        self.assertEqual(payload["event_type"], "RISK_DECISION_CREATED")
        self.assertEqual(payload["event_category"], "RISK")
        self.assertEqual(payload["actor_type"], "SERVICE")
        self.assertEqual(payload["actor_id"], "deterministic-risk-gateway")
        self.assertEqual(payload["action"], "record_risk_decision")
        self.assertEqual(payload["entity_type"], "RISK_DECISION")
        self.assertEqual(payload["entity_id"], "risk_example_001")
        self.assertEqual(payload["outcome"], "SUCCESS")
        self.assertEqual(payload["source_service"], "observability-audit-service")

    def test_generated_audit_id_starts_with_audit_prefix(self):
        payload = _builder().build_event(**_required_inputs())

        self.assertTrue(str(payload["audit_id"]).startswith("audit_"))

    def test_safety_flags_are_enforced(self):
        payload = _builder().build_event(**_required_inputs())

        self.assertEqual(payload["append_only"], True)
        self.assertEqual(payload["contains_secrets"], False)

    def test_occurred_at_is_iso_datetime_string(self):
        occurred_at = datetime(2026, 5, 7, 12, 30, tzinfo=timezone.utc)

        payload = _builder().build_event(**_required_inputs(), occurred_at=occurred_at)

        self.assertEqual(payload["occurred_at"], "2026-05-07T12:30:00+00:00")

    def test_metadata_before_and_after_are_redacted(self):
        payload = _builder().build_event(
            **_required_inputs(),
            metadata={"api_key": "fake-api-key", "safe": "value"},
            before={"secret": "fake-secret-value"},
            after={"authorization": "Bearer fake-token"},
        )

        self.assertEqual(payload["metadata"]["api_key"], REDACTED_VALUE)
        self.assertEqual(payload["metadata"]["safe"], "value")
        self.assertEqual(payload["before"]["secret"], REDACTED_VALUE)
        self.assertEqual(payload["after"]["authorization"], REDACTED_VALUE)
        self.assertEqual(payload["redaction_applied"], True)

    def test_metadata_before_and_after_inputs_are_not_mutated(self):
        metadata = {"token": "fake-token", "safe": "value"}
        before = {"broker_key": "fake-broker-key"}
        after = {"withdrawal_key": "never-use-withdrawal-key"}
        originals = copy.deepcopy((metadata, before, after))

        _builder().build_event(
            **_required_inputs(),
            metadata=metadata,
            before=before,
            after=after,
        )

        self.assertEqual((metadata, before, after), originals)

    def test_lifecycle_ids_are_included_when_allowed(self):
        payload = _builder().build_event(
            **_required_inputs(),
            lifecycle_ids={
                "order_intent_id": "intent_example_001",
                "risk_decision_id": "risk_example_001",
                "execution_report_id": "exec_report_example_001",
            },
        )

        self.assertEqual(payload["order_intent_id"], "intent_example_001")
        self.assertEqual(payload["risk_decision_id"], "risk_example_001")
        self.assertEqual(payload["execution_report_id"], "exec_report_example_001")

    def test_unknown_lifecycle_id_key_raises(self):
        with self.assertRaises(AuditEventBuildError):
            _builder().build_event(
                **_required_inputs(),
                lifecycle_ids={"broker_order_id": "external-order-id"},
            )

    def test_empty_required_input_raises(self):
        inputs = _required_inputs()
        inputs["trace_id"] = ""

        with self.assertRaises(AuditEventBuildError):
            _builder().build_event(**inputs)

    def test_no_persistence_network_or_broker_credentials_are_required(self):
        payload = _builder().build_event(**_required_inputs())

        self.assertNotIn("broker_key", payload)
        self.assertNotIn("exchange_key", payload)
        self.assertNotIn("withdrawal_key", payload)

    def test_no_dangerous_methods_are_exposed(self):
        prohibited = {
            "emit",
            "send",
            "publish",
            "persist",
            "write",
            "execute",
            "submit_order",
            "withdraw",
        }

        self.assertTrue(prohibited.isdisjoint(set(dir(_builder()))))


if __name__ == "__main__":
    unittest.main()
