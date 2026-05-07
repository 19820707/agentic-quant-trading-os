import copy
import unittest
from collections.abc import Mapping

from packages.common.audit import (
    AuditEventEmitter,
    AuditEventEmitterError,
    LocalRedactingAuditEventEmitter,
    PreparedAuditEvent,
    prepare_audit_event,
)
from packages.common.security import REDACTED_VALUE


def _safe_audit_event() -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "trace_id": "trace_example_001",
        "correlation_id": "corr_example_001",
        "audit_id": "audit_example_001",
        "event_type": "RISK_DECISION_CREATED",
        "event_category": "RISK",
        "occurred_at": "2026-05-07T00:00:00Z",
        "actor_type": "SERVICE",
        "actor_id": "deterministic-risk-gateway",
        "action": "record_risk_decision",
        "entity_type": "RISK_DECISION",
        "entity_id": "risk_example_001",
        "outcome": "SUCCESS",
        "append_only": True,
        "contains_secrets": False,
        "metadata": {
            "api_key": "fake-api-key",
            "secret": "fake-secret-value",
            "message": "local-only audit preparation",
        },
    }


class AuditEventEmitterInterfaceTests(unittest.TestCase):
    def test_prepare_audit_event_redacts_sensitive_fields(self):
        payload = _safe_audit_event()

        prepared = prepare_audit_event(payload)

        self.assertIsInstance(prepared, PreparedAuditEvent)
        self.assertEqual(prepared.payload["metadata"]["api_key"], REDACTED_VALUE)
        self.assertEqual(prepared.payload["metadata"]["secret"], REDACTED_VALUE)
        self.assertEqual(prepared.payload["metadata"]["message"], "local-only audit preparation")

    def test_prepare_audit_event_does_not_mutate_input(self):
        payload = _safe_audit_event()
        original = copy.deepcopy(payload)

        prepared = prepare_audit_event(payload)

        self.assertEqual(payload, original)
        self.assertNotEqual(prepared.payload, payload)

    def test_local_redacting_emitter_returns_prepared_event(self):
        emitter: AuditEventEmitter = LocalRedactingAuditEventEmitter()

        prepared = emitter.emit(_safe_audit_event())

        self.assertIsInstance(prepared, PreparedAuditEvent)
        self.assertEqual(prepared.payload["append_only"], True)
        self.assertEqual(prepared.payload["contains_secrets"], False)

    def test_rejects_non_mapping_payload(self):
        with self.assertRaises(AuditEventEmitterError):
            prepare_audit_event(["not", "a", "mapping"])  # type: ignore[arg-type]

    def test_rejects_non_append_only_payload(self):
        payload = _safe_audit_event()
        payload["append_only"] = False

        with self.assertRaises(AuditEventEmitterError):
            prepare_audit_event(payload)

    def test_rejects_payload_declaring_secrets(self):
        payload = _safe_audit_event()
        payload["contains_secrets"] = True

        with self.assertRaises(AuditEventEmitterError):
            prepare_audit_event(payload)

    def test_emitter_has_no_persistence_or_network_methods(self):
        prohibited = {
            "send",
            "post",
            "publish",
            "persist",
            "write",
            "connect",
            "request",
            "execute",
            "submit_order",
        }

        exposed = set(dir(LocalRedactingAuditEventEmitter()))

        self.assertTrue(prohibited.isdisjoint(exposed))

    def test_payloads_are_plain_mappings_without_credentials_required(self):
        payload = _safe_audit_event()

        self.assertIsInstance(payload, Mapping)
        self.assertNotIn("broker_key", payload)
        self.assertNotIn("exchange_key", payload)
        self.assertNotIn("withdrawal_key", payload)


if __name__ == "__main__":
    unittest.main()
