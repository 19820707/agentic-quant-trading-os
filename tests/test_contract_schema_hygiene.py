"""Hygiene rules that every contract schema must satisfy.

AGENTS.md requires cross-service payloads to be documented, closed and
traceable. These checks apply that to every schema file, so a new contract
cannot be added without trace identifiers or with fields that accept anything.
"""

import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator
from packages.contracts.validator import (
    MAX_PAYLOAD_DEPTH,
    MAX_PAYLOAD_NODES,
    MAX_PAYLOAD_STRING_LENGTH,
    check_payload_limits,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas"
SCHEMA_FILES = sorted(SCHEMA_ROOT.glob("*/*.schema.json"))
FIXTURES = ROOT / "tests" / "fixtures" / "contracts"

TRACE_FIELDS = ("schema_version", "trace_id", "correlation_id")
STRING_CONSTRAINTS = ("enum", "const", "format", "pattern", "minLength")
# Free-form bags that are deliberately open. Their content is redacted before
# it is logged; see packages/common/security.py.
OPEN_OBJECT_FIELD_NAMES = {"metadata", "before", "after"}


def _walk(schema: dict, path: str):
    yield path, schema
    for name, child in schema.get("properties", {}).items():
        if isinstance(child, dict):
            yield from _walk(child, f"{path}.{name}")
    items = schema.get("items")
    if isinstance(items, dict):
        yield from _walk(items, f"{path}[]")


class ContractSchemaHygieneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schemas = {
            path.relative_to(SCHEMA_ROOT).as_posix(): json.loads(path.read_text(encoding="utf-8"))
            for path in SCHEMA_FILES
        }

    def test_all_schemas_are_loaded(self):
        self.assertGreaterEqual(len(self.schemas), 32)

    def test_every_schema_is_identified_closed_and_traceable(self):
        for name, schema in self.schemas.items():
            with self.subTest(schema=name):
                self.assertIsInstance(schema.get("$id"), str)
                self.assertIs(schema.get("additionalProperties"), False)
                for field in TRACE_FIELDS:
                    self.assertIn(field, schema.get("properties", {}))
                    self.assertIn(field, schema.get("required", []))

    def test_schema_ids_are_unique(self):
        identifiers = [schema["$id"] for schema in self.schemas.values()]

        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_no_text_field_accepts_an_empty_or_arbitrary_value(self):
        for name, schema in self.schemas.items():
            for path, node in _walk(schema, "$"):
                if node.get("type") == "string":
                    with self.subTest(schema=name, path=path):
                        self.assertTrue(
                            any(keyword in node for keyword in STRING_CONSTRAINTS),
                            "string field needs enum, const, format, pattern or minLength",
                        )

    def test_nested_objects_are_closed_unless_explicitly_free_form(self):
        for name, schema in self.schemas.items():
            for path, node in _walk(schema, "$"):
                if node.get("type") == "object" and node.get("additionalProperties") is not False:
                    with self.subTest(schema=name, path=path):
                        self.assertIn(path.rsplit(".", 1)[-1], OPEN_OBJECT_FIELD_NAMES)

    def test_arrays_declare_their_item_type(self):
        for name, schema in self.schemas.items():
            for path, node in _walk(schema, "$"):
                if node.get("type") == "array":
                    with self.subTest(schema=name, path=path):
                        self.assertIsInstance(node.get("items"), dict)

    def test_timestamp_fields_use_the_date_time_format(self):
        for name, schema in self.schemas.items():
            for path, node in _walk(schema, "$"):
                field = path.rsplit(".", 1)[-1]
                if node.get("type") == "string" and (field.endswith("_at") or field == "timestamp"):
                    with self.subTest(schema=name, path=path):
                        self.assertEqual(node.get("format"), "date-time")

    def test_empty_optional_identifier_is_rejected(self):
        payload = json.loads((FIXTURES / "risk_decision.valid.json").read_text(encoding="utf-8"))
        payload["strategy_id"] = ""

        self.assertFalse(ContractValidator().validate("trading", "risk_decision", payload).valid)


class PayloadLimitTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.payload = json.loads((FIXTURES / "order_intent.valid.json").read_text(encoding="utf-8"))

    def test_valid_fixture_is_within_limits(self):
        self.assertEqual(check_payload_limits(self.payload), [])

    def test_oversized_string_is_rejected_before_schema_validation(self):
        payload = copy.deepcopy(self.payload)
        payload["rationale"] = "x" * (MAX_PAYLOAD_STRING_LENGTH + 1)

        result = self.validator.validate("trading", "order_intent", payload)

        self.assertFalse(result.valid)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("longer than", result.errors[0])

    def test_string_at_the_limit_is_allowed_by_the_size_check(self):
        self.assertEqual(check_payload_limits({"note": "x" * MAX_PAYLOAD_STRING_LENGTH}), [])

    def test_excessive_nesting_is_rejected(self):
        nested: dict = {}
        cursor = nested
        for _ in range(MAX_PAYLOAD_DEPTH + 2):
            cursor["child"] = {}
            cursor = cursor["child"]

        self.assertIn("nesting is deeper", check_payload_limits(nested)[0])

    def test_nesting_far_beyond_the_recursion_limit_does_not_crash(self):
        nested: list = []
        cursor = nested
        for _ in range(5_000):
            cursor.append([])
            cursor = cursor[0]

        self.assertTrue(check_payload_limits(nested))

    def test_too_many_values_are_rejected(self):
        self.assertIn("more than", check_payload_limits(list(range(MAX_PAYLOAD_NODES + 1)))[0])

    def test_oversized_metadata_bag_is_rejected_by_the_validator(self):
        payload = copy.deepcopy(self.payload)
        payload["metadata"] = {"blob": ["x" * 10] * (MAX_PAYLOAD_NODES + 1)}

        self.assertFalse(self.validator.validate("trading", "order_intent", payload).valid)


if __name__ == "__main__":
    unittest.main()
