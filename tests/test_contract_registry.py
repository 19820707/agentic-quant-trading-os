import unittest

from packages.contracts.registry import SchemaRegistry, UnknownSchemaError


class ContractRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = SchemaRegistry()

    def test_lists_expected_domains(self):
        domains = self.registry.list_domains()

        self.assertIn("trading", domains)
        self.assertIn("audit", domains)
        self.assertIn("research", domains)

    def test_lists_known_trading_schemas(self):
        names = {entry.name for entry in self.registry.list_schemas("trading")}

        self.assertTrue(
            {
                "order_intent",
                "risk_decision",
                "approved_order",
                "execution_report",
            }.issubset(names)
        )

    def test_lists_audit_event_under_audit(self):
        names = {entry.name for entry in self.registry.list_schemas("audit")}

        self.assertIn("audit_event", names)

    def test_lists_research_contracts_under_research(self):
        names = {entry.name for entry in self.registry.list_schemas("research")}

        self.assertTrue(
            {
                "research_dossier",
                "probability_estimate",
                "hypothesis_record",
                "analyst_report",
                "debate_transcript",
                "signal_candidate",
                "risk_review_input",
                "prediction_market_signal_classification",
                "edge_computation_record",
                "ensemble_probability_vote",
                "advisory_kelly_sizing",
                "signal_pipeline_status",
            }.issubset(names)
        )

    def test_get_order_intent_works_without_suffix(self):
        entry = self.registry.get("trading", "order_intent")

        self.assertEqual(entry.domain, "trading")
        self.assertEqual(entry.name, "order_intent")
        self.assertTrue(entry.path.name.endswith(".schema.json"))
        self.assertIsNotNone(entry.schema_id)

    def test_get_order_intent_works_with_suffix(self):
        plain = self.registry.get("trading", "order_intent")
        suffixed = self.registry.get("trading", "order_intent.schema.json")

        self.assertEqual(plain, suffixed)

    def test_exists_returns_true_for_known_schema(self):
        self.assertTrue(self.registry.exists("trading", "order_intent"))

    def test_exists_returns_false_for_unknown_schema(self):
        self.assertFalse(self.registry.exists("trading", "missing_schema"))

    def test_unknown_schema_raises_unknown_schema_error(self):
        with self.assertRaises(UnknownSchemaError):
            self.registry.get("trading", "missing_schema")

    def test_traversal_in_domain_is_rejected(self):
        with self.assertRaises(UnknownSchemaError):
            self.registry.get("../..", "some_file")

        with self.assertRaises(UnknownSchemaError):
            self.registry.get("trading/../../audit", "audit_event")

    def test_traversal_in_name_is_rejected(self):
        with self.assertRaises(UnknownSchemaError):
            self.registry.get("trading", "../audit/audit_event")

    def test_absolute_domain_or_name_is_rejected(self):
        absolute_root = self.registry.schema_root

        with self.assertRaises(UnknownSchemaError):
            self.registry.get(str(absolute_root), "order_intent")

        with self.assertRaises(UnknownSchemaError):
            self.registry.get("trading", str(absolute_root / "trading" / "order_intent"))

    def test_returned_paths_stay_inside_schema_root(self):
        for entry in self.registry.list_schemas():
            with self.subTest(schema=f"{entry.domain}/{entry.name}"):
                entry.path.relative_to(self.registry.schema_root)
                self.assertTrue(entry.path.is_file())

    def test_registry_does_not_require_network_or_credentials(self):
        entry = self.registry.get("audit", "audit_event")

        self.assertIsNotNone(entry.path)
        self.assertFalse(hasattr(entry, "api_key"))
        self.assertFalse(hasattr(entry, "broker_secret"))


if __name__ == "__main__":
    unittest.main()
