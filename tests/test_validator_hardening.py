"""Tests for ContractValidator hardening: schema cache and validate_redacted boundary."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from packages.contracts.validator import (
    ContractValidator,
    RedactionViolationError,
    ValidationResult,
)

_MINIMAL_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://example.com/test.schema.json",
    "type": "object",
    "required": ["report_id"],
    "properties": {
        "report_id": {"type": "string"},
        "contains_secrets": {"type": "boolean"},
    },
}


class SchemaCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.domain_dir = Path(self.tmpdir) / "test_domain"
        self.domain_dir.mkdir()
        self.schema_path = self.domain_dir / "sample.schema.json"
        self._write_schema(_MINIMAL_SCHEMA)
        self.validator = ContractValidator(schema_root=self.tmpdir)

    def _write_schema(self, schema: dict) -> None:
        self.schema_path.write_text(json.dumps(schema), encoding="utf-8")

    def test_schema_loaded_on_first_call(self):
        schema = self.validator.load_schema("test_domain", "sample")
        self.assertEqual(schema["$id"], _MINIMAL_SCHEMA["$id"])

    def test_schema_returned_from_cache_on_second_call(self):
        schema_a = self.validator.load_schema("test_domain", "sample")
        schema_b = self.validator.load_schema("test_domain", "sample")
        self.assertIs(schema_a, schema_b)

    def test_cache_invalidated_when_file_changes(self):
        schema_a = self.validator.load_schema("test_domain", "sample")

        # Overwrite with a modified schema and bump the mtime by a second.
        updated = {**_MINIMAL_SCHEMA, "$id": "https://example.com/updated.schema.json"}
        self._write_schema(updated)
        # Force mtime change visible to os.stat (some filesystems have 1-second granularity).
        new_mtime = os.stat(self.schema_path).st_mtime + 1
        os.utime(self.schema_path, (new_mtime, new_mtime))

        schema_b = self.validator.load_schema("test_domain", "sample")
        self.assertIsNot(schema_a, schema_b)
        self.assertEqual(schema_b["$id"], "https://example.com/updated.schema.json")

    def test_multiple_validators_have_independent_caches(self):
        v1 = ContractValidator(schema_root=self.tmpdir)
        v2 = ContractValidator(schema_root=self.tmpdir)
        s1 = v1.load_schema("test_domain", "sample")
        s2 = v2.load_schema("test_domain", "sample")
        # Same content, but independent cache objects.
        self.assertEqual(s1, s2)


class ValidateRedactedTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.domain_dir = Path(self.tmpdir) / "test_domain"
        self.domain_dir.mkdir()
        schema_path = self.domain_dir / "report.schema.json"
        schema_path.write_text(json.dumps(_MINIMAL_SCHEMA), encoding="utf-8")
        self.validator = ContractValidator(schema_root=self.tmpdir)

    def test_valid_redacted_payload_passes(self):
        payload = {"report_id": "rpt-001", "contains_secrets": False}
        result = self.validator.validate_redacted("test_domain", "report", payload)
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.valid)

    def test_payload_without_contains_secrets_passes(self):
        # `contains_secrets` absent is fine — only True is rejected.
        payload = {"report_id": "rpt-002"}
        result = self.validator.validate_redacted("test_domain", "report", payload)
        self.assertTrue(result.valid)

    def test_payload_with_contains_secrets_true_raises(self):
        payload = {"report_id": "rpt-003", "contains_secrets": True}
        with self.assertRaises(RedactionViolationError) as ctx:
            self.validator.validate_redacted("test_domain", "report", payload)
        self.assertIn("contains_secrets", str(ctx.exception))

    def test_violation_raised_before_schema_validation(self):
        # Even a schema-invalid payload raises RedactionViolationError first.
        payload = {"contains_secrets": True}  # missing required report_id
        with self.assertRaises(RedactionViolationError):
            self.validator.validate_redacted("test_domain", "report", payload)

    def test_schema_errors_still_reported_for_safe_payload(self):
        payload = {"contains_secrets": False}  # missing required report_id
        result = self.validator.validate_redacted("test_domain", "report", payload)
        self.assertFalse(result.valid)
        self.assertTrue(any("report_id" in e for e in result.errors))


if __name__ == "__main__":
    unittest.main()
