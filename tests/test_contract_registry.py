import unittest

from packages.contracts.registry import SCHEMA_ROOT, get_schema_entry, list_schemas


class ContractRegistryTests(unittest.TestCase):
    def test_lists_known_core_contract_schemas(self):
        names = {(entry.domain, entry.name) for entry in list_schemas()}

        self.assertEqual(
            names,
            {
                ("audit", "audit_event"),
                ("trading", "approved_order"),
                ("trading", "execution_report"),
                ("trading", "order_intent"),
                ("trading", "risk_decision"),
            },
        )

    def test_registered_paths_are_local_and_exist(self):
        for entry in list_schemas():
            with self.subTest(schema=f"{entry.domain}/{entry.name}"):
                resolved = entry.path.resolve()
                resolved.relative_to(SCHEMA_ROOT.resolve())
                self.assertTrue(resolved.is_file())
                self.assertTrue(resolved.name.endswith(".schema.json"))

    def test_get_schema_entry_accepts_name_with_or_without_suffix(self):
        plain = get_schema_entry("trading", "order_intent")
        suffixed = get_schema_entry("trading", "order_intent.schema.json")

        self.assertEqual(plain, suffixed)
        self.assertEqual(plain.title, "OrderIntent")

    def test_unknown_schema_is_rejected(self):
        with self.assertRaises(KeyError):
            get_schema_entry("trading", "missing_schema")

    def test_registry_has_no_runtime_execution_capability(self):
        entry = get_schema_entry("audit", "audit_event")

        self.assertFalse(hasattr(entry, "validate"))
        self.assertFalse(hasattr(entry, "execute"))
        self.assertFalse(hasattr(entry, "approve"))


if __name__ == "__main__":
    unittest.main()
