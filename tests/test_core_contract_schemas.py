import copy
import json
import re
import unittest
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


CONTRACTS = {
    "order_intent": {
        "path": ROOT / "packages/contracts/schemas/trading/order_intent.schema.json",
        "primary_id": "order_intent_id",
        "enum_field": "side",
        "timestamp_field": "created_at",
        "valid": {
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
            "risk_required": True
        }
    },
    "risk_decision": {
        "path": ROOT / "packages/contracts/schemas/trading/risk_decision.schema.json",
        "primary_id": "risk_decision_id",
        "enum_field": "decision",
        "timestamp_field": "evaluated_at",
        "valid": {
            "schema_version": "0.1.0",
            "trace_id": "trace_risk_decision_001",
            "correlation_id": "corr_risk_decision_001",
            "risk_decision_id": "risk_example_001",
            "order_intent_id": "intent_example_001",
            "decision": "RESIZE",
            "risk_gateway_version": "risk_gateway_v0_1_0",
            "evaluated_at": "2026-01-01T00:00:01Z",
            "evaluated_by": "deterministic-risk-gateway",
            "checks": [
                {
                    "check_name": "max_order_notional",
                    "result": "PASS",
                    "severity": "INFO"
                }
            ],
            "final_reason": "Resized order intent for paper lifecycle.",
            "approved_for_execution": True
        }
    },
    "approved_order": {
        "path": ROOT / "packages/contracts/schemas/trading/approved_order.schema.json",
        "primary_id": "approved_order_id",
        "enum_field": "execution_mode",
        "timestamp_field": "approved_at",
        "valid": {
            "schema_version": "0.1.0",
            "trace_id": "trace_approved_order_001",
            "correlation_id": "corr_approved_order_001",
            "approved_order_id": "approved_example_001",
            "order_intent_id": "intent_example_001",
            "risk_decision_id": "risk_example_001",
            "strategy_id": "mean_reversion_paper",
            "symbol": "BTC/USDT",
            "venue": "paper",
            "asset_class": "crypto",
            "instrument_type": "perpetual",
            "side": "BUY",
            "order_type": "LIMIT",
            "approved_quantity": 0.25,
            "time_in_force": "GTC",
            "approved_at": "2026-01-01T00:00:02Z",
            "approved_by": "deterministic-risk-gateway",
            "execution_allowed": True,
            "execution_mode": "PAPER",
            "status": "QUEUED_FOR_PAPER"
        }
    },
    "execution_report": {
        "path": ROOT / "packages/contracts/schemas/trading/execution_report.schema.json",
        "primary_id": "execution_report_id",
        "enum_field": "status",
        "timestamp_field": "reported_at",
        "valid": {
            "schema_version": "0.1.0",
            "trace_id": "trace_execution_report_001",
            "correlation_id": "corr_execution_report_001",
            "execution_report_id": "exec_report_example_001",
            "approved_order_id": "approved_example_001",
            "execution_order_id": "exec_order_example_001",
            "execution_mode": "PAPER",
            "venue": "paper",
            "symbol": "BTC/USDT",
            "status": "PAPER_FILLED",
            "event_type": "PAPER_EXECUTION",
            "reported_at": "2026-01-01T00:00:03Z",
            "reported_by": "paper-trading-engine",
            "reconciliation_required": False,
            "reconciliation_status": "NOT_REQUIRED"
        }
    },
    "audit_event": {
        "path": ROOT / "packages/contracts/schemas/audit/audit_event.schema.json",
        "primary_id": "audit_id",
        "enum_field": "event_type",
        "timestamp_field": "occurred_at",
        "valid": {
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
            "risk_decision_id": "risk_example_001"
        }
    }
}


class MinimalSchemaValidator:
    """Small stdlib validator for the schema keywords used by core contracts."""

    def validate(self, schema, instance, path="$"):
        errors = []
        self._validate(schema, instance, path, errors)
        return errors

    def _validate(self, schema, instance, path, errors):
        if "const" in schema and instance != schema["const"]:
            errors.append(f"{path}: expected const {schema['const']!r}")

        if "enum" in schema and instance not in schema["enum"]:
            errors.append(f"{path}: value {instance!r} not in enum")

        expected_type = schema.get("type")
        if expected_type is not None and not self._matches_type(instance, expected_type):
            errors.append(f"{path}: expected type {expected_type!r}")
            return

        if isinstance(instance, dict):
            self._validate_object(schema, instance, path, errors)
        elif isinstance(instance, list):
            self._validate_array(schema, instance, path, errors)
        elif isinstance(instance, str):
            self._validate_string(schema, instance, path, errors)
        elif isinstance(instance, (int, float)) and not isinstance(instance, bool):
            self._validate_number(schema, instance, path, errors)

    def _validate_object(self, schema, instance, path, errors):
        for field in schema.get("required", []):
            if field not in instance:
                errors.append(f"{path}: missing required field {field!r}")

        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, value in instance.items():
            child_path = f"{path}.{key}"
            if key in properties:
                self._validate(properties[key], value, child_path, errors)
            elif additional is False:
                errors.append(f"{child_path}: additional property is forbidden")
            elif isinstance(additional, dict):
                self._validate(additional, value, child_path, errors)

    def _validate_array(self, schema, instance, path, errors):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: expected at least {schema['minItems']} items")

        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(instance):
                self._validate(item_schema, item, f"{path}[{index}]", errors)

    def _validate_string(self, schema, instance, path, errors):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")

        pattern = schema.get("pattern")
        if pattern and not re.match(pattern, instance):
            errors.append(f"{path}: value {instance!r} does not match pattern")

        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(instance.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}: invalid date-time")

    def _validate_number(self, schema, instance, path, errors):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")

        if "exclusiveMinimum" in schema and instance <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: not above exclusiveMinimum {schema['exclusiveMinimum']}")

    def _matches_type(self, instance, expected_type):
        if isinstance(expected_type, list):
            return any(self._matches_type(instance, item) for item in expected_type)

        checks = {
            "object": lambda value: isinstance(value, dict),
            "array": lambda value: isinstance(value, list),
            "string": lambda value: isinstance(value, str),
            "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
            "boolean": lambda value: isinstance(value, bool),
            "null": lambda value: value is None
        }
        return checks[expected_type](instance)


def load_schema(contract_name):
    with CONTRACTS[contract_name]["path"].open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


class CoreContractSchemaTests(unittest.TestCase):
    def setUp(self):
        self.validator = MinimalSchemaValidator()

    def test_contract_schemas_use_draft_2020_12_and_closed_objects(self):
        for contract_name in CONTRACTS:
            with self.subTest(contract=contract_name):
                schema = load_schema(contract_name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertIn("$id", schema)
                self.assertIn("title", schema)

    def test_valid_fixtures_match_contract_schemas(self):
        for contract_name, contract in CONTRACTS.items():
            with self.subTest(contract=contract_name):
                schema = load_schema(contract_name)
                errors = self.validator.validate(schema, contract["valid"])
                self.assertEqual(errors, [])

    def test_missing_required_fields_are_rejected(self):
        for contract_name, contract in CONTRACTS.items():
            with self.subTest(contract=contract_name):
                schema = load_schema(contract_name)
                fixture = copy.deepcopy(contract["valid"])
                fixture.pop(schema["required"][0])
                errors = self.validator.validate(schema, fixture)
                self.assertTrue(errors)

    def test_invalid_enums_are_rejected(self):
        for contract_name, contract in CONTRACTS.items():
            with self.subTest(contract=contract_name):
                schema = load_schema(contract_name)
                fixture = copy.deepcopy(contract["valid"])
                fixture[contract["enum_field"]] = "INVALID_ENUM_VALUE"
                errors = self.validator.validate(schema, fixture)
                self.assertTrue(errors)

    def test_invalid_timestamps_are_rejected(self):
        for contract_name, contract in CONTRACTS.items():
            with self.subTest(contract=contract_name):
                schema = load_schema(contract_name)
                fixture = copy.deepcopy(contract["valid"])
                fixture[contract["timestamp_field"]] = "not-a-timestamp"
                errors = self.validator.validate(schema, fixture)
                self.assertTrue(errors)

    def test_invalid_id_patterns_are_rejected(self):
        for contract_name, contract in CONTRACTS.items():
            with self.subTest(contract=contract_name):
                schema = load_schema(contract_name)
                fixture = copy.deepcopy(contract["valid"])
                fixture[contract["primary_id"]] = "invalid-id"
                errors = self.validator.validate(schema, fixture)
                self.assertTrue(errors)

    def test_forbidden_additional_properties_are_rejected(self):
        for contract_name, contract in CONTRACTS.items():
            with self.subTest(contract=contract_name):
                schema = load_schema(contract_name)
                fixture = copy.deepcopy(contract["valid"])
                fixture["unexpected_field"] = "not allowed"
                errors = self.validator.validate(schema, fixture)
                self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
