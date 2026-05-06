import copy
import unittest

from packages.contracts import ContractValidator, SchemaNotFoundError


ORDER_INTENT_PAYLOAD = {
    "schema_version": "0.1.0",
    "trace_id": "trace_order_intent_001",
    "correlation_id": "corr_order_intent_001",
    "order_intent_id": "intent_example_001",
    "signal_id": "sig_example_001",
    "strategy_id": "mean_reversion_paper",
    "model_version": "model_v0_1_0",
    "symbol": "BTC/USDT",
    "venue": "paper",
    "asset_class": "crypto",
    "instrument_type": "perpetual",
    "side": "BUY",
    "order_type": "LIMIT",
    "quantity": 0.5,
    "time_in_force": "GTC",
    "created_at": "2026-01-01T00:00:00Z",
    "status": "PENDING_RISK",
    "risk_required": True,
}


AUDIT_EVENT_PAYLOAD = {
    "schema_version": "0.1.0",
    "trace_id": "trace_audit_risk_001",
    "correlation_id": "corr_audit_risk_001",
    "audit_id": "audit_risk_decision_001",
    "event_type": "RISK_DECISION_CREATED",
    "event_category": "RISK",
    "occurred_at": "2026-01-01T00:00:03Z",
    "actor_type": "SERVICE",
    "actor_id": "deterministic-risk-gateway",
    "action": "record_risk_decision",
    "entity_type": "RISK_DECISION",
    "entity_id": "risk_example_001",
    "outcome": "SUCCESS",
    "append_only": True,
    "contains_secrets": False,
    "order_intent_id": "intent_example_001",
    "risk_decision_id": "risk_example_001",
}


class ContractValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_loads_order_intent_schema(self):
        schema = self.validator.load_schema("trading", "order_intent")
        self.assertEqual(schema["title"], "OrderIntent")

    def test_rejects_traversal_in_domain(self):
        with self.assertRaises(SchemaNotFoundError):
            self.validator.schema_path("../..", "some_file")

        with self.assertRaises(SchemaNotFoundError):
            self.validator.schema_path("trading/../../audit", "audit_event")

    def test_rejects_traversal_in_name(self):
        with self.assertRaises(SchemaNotFoundError):
            self.validator.schema_path("trading", "../audit/audit_event")

        with self.assertRaises(SchemaNotFoundError):
            self.validator.schema_path("trading", "../../outside")

    def test_rejects_absolute_domain_or_name(self):
        absolute_schema_root = self.validator.schema_root

        with self.assertRaises(SchemaNotFoundError):
            self.validator.schema_path(str(absolute_schema_root), "order_intent")

        with self.assertRaises(SchemaNotFoundError):
            self.validator.schema_path("trading", str(absolute_schema_root / "trading" / "order_intent"))

    def test_validates_safe_order_intent_payload(self):
        result = self.validator.validate("trading", "order_intent", ORDER_INTENT_PAYLOAD)
        self.assertTrue(result.valid)
        self.assertEqual(result.errors, [])
        self.assertTrue(result.schema_id.endswith("/schemas/trading/order_intent.schema.json"))

    def test_fails_when_required_field_is_missing(self):
        payload = copy.deepcopy(ORDER_INTENT_PAYLOAD)
        payload.pop("trace_id")

        result = self.validator.validate("trading", "order_intent", payload)

        self.assertFalse(result.valid)
        self.assertTrue(result.errors)

    def test_fails_when_extra_top_level_field_is_present(self):
        payload = copy.deepcopy(ORDER_INTENT_PAYLOAD)
        payload["unexpected_field"] = "not allowed"

        result = self.validator.validate("trading", "order_intent", payload)

        self.assertFalse(result.valid)
        self.assertTrue(result.errors)

    def test_loads_audit_event_schema(self):
        schema = self.validator.load_schema("audit", "audit_event")
        self.assertEqual(schema["title"], "AuditEvent")

    def test_loads_audit_event_schema_with_suffix(self):
        schema = self.validator.load_schema("audit", "audit_event.schema.json")
        self.assertEqual(schema["title"], "AuditEvent")

    def test_validates_safe_audit_event_payload(self):
        result = self.validator.validate("audit", "audit_event", AUDIT_EVENT_PAYLOAD)
        self.assertTrue(result.valid)
        self.assertEqual(result.errors, [])
        self.assertTrue(result.schema_id.endswith("/schemas/audit/audit_event.schema.json"))

    def test_missing_schema_raises_schema_not_found_error(self):
        with self.assertRaises(SchemaNotFoundError):
            self.validator.load_schema("trading", "missing_contract")

    def test_validator_does_not_require_network_or_broker_credentials(self):
        payload = copy.deepcopy(ORDER_INTENT_PAYLOAD)

        result = self.validator.validate("trading", "order_intent", payload)

        self.assertTrue(result.valid)
        self.assertNotIn("api_key", payload)
        self.assertNotIn("broker_secret", payload)


if __name__ == "__main__":
    unittest.main()
