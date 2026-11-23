import copy
import json
import tempfile
import unittest
from pathlib import Path

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


try:
    import jsonschema  # noqa: F401
except ImportError:
    JSONSCHEMA_AVAILABLE = False
else:
    JSONSCHEMA_AVAILABLE = True


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

    def test_invalid_date_time_is_rejected(self):
        payload = copy.deepcopy(ORDER_INTENT_PAYLOAD)
        payload["created_at"] = "not-a-timestamp"

        result = self.validator.validate("trading", "order_intent", payload)

        self.assertFalse(result.valid)

    def test_fallback_validator_rejects_invalid_date_time(self):
        schema = self.validator.load_schema("trading", "order_intent")
        payload = copy.deepcopy(ORDER_INTENT_PAYLOAD)
        payload["created_at"] = "not-a-timestamp"

        self.assertEqual(self.validator._minimal_validate(schema, copy.deepcopy(ORDER_INTENT_PAYLOAD)), [])
        self.assertTrue(self.validator._minimal_validate(schema, payload))

    @unittest.skipUnless(JSONSCHEMA_AVAILABLE, "jsonschema is not installed")
    def test_fallback_and_jsonschema_agree_on_representative_payloads(self):
        import jsonschema

        cases = []
        for name, base in (("order_intent", ORDER_INTENT_PAYLOAD), ("audit_event", AUDIT_EVENT_PAYLOAD)):
            domain = "trading" if name == "order_intent" else "audit"
            schema = self.validator.load_schema(domain, name)
            timestamp_field = "created_at" if name == "order_intent" else "occurred_at"
            missing = copy.deepcopy(base)
            missing.pop("trace_id")
            extra = copy.deepcopy(base)
            extra["unexpected_field"] = True
            bad_time = copy.deepcopy(base)
            bad_time[timestamp_field] = "yesterday"
            wrong_type = copy.deepcopy(base)
            wrong_type["trace_id"] = 123
            for label, payload in (
                ("valid", base),
                ("missing", missing),
                ("extra", extra),
                ("bad_time", bad_time),
                ("wrong_type", wrong_type),
            ):
                cases.append((f"{name}:{label}", schema, payload))

        for label, schema, payload in cases:
            with self.subTest(case=label):
                fallback_valid = not self.validator._minimal_validate(schema, copy.deepcopy(payload))
                library_valid = not self.validator._jsonschema_validate(jsonschema, schema, copy.deepcopy(payload))
                self.assertEqual(fallback_valid, library_valid)

    def test_fallback_validator_fails_closed_on_unsupported_keywords(self):
        with tempfile.TemporaryDirectory() as directory:
            domain = Path(directory) / "demo"
            domain.mkdir()
            (domain / "conditional.schema.json").write_text(
                json.dumps(
                    {
                        "type": "object",
                        "properties": {"mode": {"type": "string"}},
                        "allOf": [{"required": ["mode"]}],
                    }
                ),
                encoding="utf-8",
            )
            validator = ContractValidator(directory)
            schema = validator.load_schema("demo", "conditional")

            errors = validator._minimal_validate(schema, {})

        self.assertTrue(errors)
        self.assertIn("allOf", errors[0])

    def test_fallback_validator_enforces_unique_and_maximum_constraints(self):
        schema = {
            "type": "object",
            "properties": {
                "tags": {"type": "array", "uniqueItems": True, "maxItems": 3, "items": {"type": "string", "maxLength": 4}},
                "ratio": {"type": "number", "exclusiveMaximum": 1},
            },
        }

        self.assertEqual(self.validator._minimal_validate(schema, {"tags": ["a", "b"], "ratio": 0.5}), [])
        self.assertTrue(self.validator._minimal_validate(schema, {"tags": ["a", "a"]}))
        self.assertTrue(self.validator._minimal_validate(schema, {"tags": ["a", "b", "c", "d"]}))
        self.assertTrue(self.validator._minimal_validate(schema, {"tags": ["toolong"]}))
        self.assertTrue(self.validator._minimal_validate(schema, {"ratio": 1}))


if __name__ == "__main__":
    unittest.main()
