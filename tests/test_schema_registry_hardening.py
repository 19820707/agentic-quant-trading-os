"""Tests for SchemaRegistry mtime-aware schema_id caching."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from packages.contracts.registry import SchemaInfo, SchemaRegistry, UnknownSchemaError

_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://example.com/sample.schema.json",
    "type": "object",
}


class SchemaIdCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.domain_dir = Path(self.tmpdir) / "test_domain"
        self.domain_dir.mkdir()
        self.schema_path = self.domain_dir / "sample.schema.json"
        self._write_schema(_SCHEMA)
        self.registry = SchemaRegistry(schema_root=self.tmpdir)

    def _write_schema(self, schema: dict) -> None:
        self.schema_path.write_text(json.dumps(schema), encoding="utf-8")

    def test_schema_id_returned_on_first_get(self):
        info = self.registry.get("test_domain", "sample")
        self.assertIsInstance(info, SchemaInfo)
        self.assertEqual(info.schema_id, _SCHEMA["$id"])

    def test_schema_id_consistent_on_repeated_get(self):
        info_a = self.registry.get("test_domain", "sample")
        info_b = self.registry.get("test_domain", "sample")
        self.assertEqual(info_a.schema_id, info_b.schema_id)

    def test_cache_invalidated_on_mtime_advance(self):
        self.registry.get("test_domain", "sample")

        updated_id = "https://example.com/updated.schema.json"
        self._write_schema({**_SCHEMA, "$id": updated_id})
        new_mtime = os.stat(self.schema_path).st_mtime + 1
        os.utime(self.schema_path, (new_mtime, new_mtime))

        info = self.registry.get("test_domain", "sample")
        self.assertEqual(info.schema_id, updated_id)

    def test_schema_without_id_field_returns_none(self):
        self._write_schema({"type": "object"})
        new_mtime = os.stat(self.schema_path).st_mtime + 1
        os.utime(self.schema_path, (new_mtime, new_mtime))
        info = self.registry.get("test_domain", "sample")
        self.assertIsNone(info.schema_id)

    def test_independent_registries_have_independent_caches(self):
        r1 = SchemaRegistry(schema_root=self.tmpdir)
        r2 = SchemaRegistry(schema_root=self.tmpdir)
        self.assertEqual(
            r1.get("test_domain", "sample").schema_id,
            r2.get("test_domain", "sample").schema_id,
        )

    def test_list_schemas_uses_cached_id(self):
        self.registry.get("test_domain", "sample")
        schemas = self.registry.list_schemas("test_domain")
        self.assertEqual(len(schemas), 1)
        self.assertEqual(schemas[0].schema_id, _SCHEMA["$id"])

    def test_cache_populated_via_list_schemas(self):
        self.registry.list_schemas("test_domain")
        cached_entry = self.registry._id_cache.get(self.schema_path.resolve())
        self.assertIsNotNone(cached_entry)
        self.assertEqual(cached_entry.schema_id, _SCHEMA["$id"])


class SchemaRegistryTraversalTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.registry = SchemaRegistry(schema_root=self.tmpdir)

    def test_absolute_domain_rejected(self):
        with self.assertRaises(UnknownSchemaError):
            self.registry.get("/absolute/domain", "schema")

    def test_traversal_in_domain_rejected(self):
        with self.assertRaises(UnknownSchemaError):
            self.registry.get("../escape", "schema")

    def test_traversal_in_name_rejected(self):
        domain_dir = Path(self.tmpdir) / "safe_domain"
        domain_dir.mkdir()
        with self.assertRaises(UnknownSchemaError):
            self.registry.get("safe_domain", "../escape")

    def test_nonexistent_schema_raises_unknown(self):
        with self.assertRaises(UnknownSchemaError):
            self.registry.get("no_domain", "no_schema")

    def test_exists_returns_false_for_missing_schema(self):
        self.assertFalse(self.registry.exists("no_domain", "no_schema"))


if __name__ == "__main__":
    unittest.main()
