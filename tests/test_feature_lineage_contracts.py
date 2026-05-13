import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas" / "features"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts"

FEATURE_CONTRACTS = {
    "dataset_lineage_record": {
        "fixture": "dataset_lineage_record.valid.json",
        "primary_id": "dataset_lineage_record_id",
    },
    "leakage_review_report": {
        "fixture": "leakage_review_report.valid.json",
        "primary_id": "leakage_review_report_id",
    },
}


class FeatureLineageContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_feature_lineage_fixtures_validate(self):
        for name in FEATURE_CONTRACTS:
            with self.subTest(schema=name):
                result = self.validator.validate("features", name, self._fixture(name))
                self.assertTrue(result.valid, result.errors)

    def test_feature_lineage_schemas_are_closed(self):
        for name in FEATURE_CONTRACTS:
            with self.subTest(schema=name):
                schema = self._schema(name)
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue(schema["$id"].endswith(f"/schemas/features/{name}.schema.json"))

    def test_dataset_lineage_preserves_required_timestamp_fields(self):
        fixture = self._fixture("dataset_lineage_record")

        self.assertEqual(fixture["event_timestamp_field"], "event_timestamp")
        self.assertEqual(fixture["created_timestamp_field"], "created_timestamp")
        self.assertEqual(fixture["available_timestamp_field"], "available_timestamp")
        self.assertTrue(fixture["point_in_time_validated"])
        self.assertTrue(fixture["leakage_review_required"])

    def test_leakage_review_cannot_approve_training_production_or_execution(self):
        fixture = self._fixture("leakage_review_report")

        self.assertFalse(fixture["leakage_detected"])
        self.assertFalse(fixture["model_training_approval_allowed"])
        self.assertFalse(fixture["production_approval_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_feature_lineage_contracts_are_non_executable(self):
        for name in FEATURE_CONTRACTS:
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                self.assertFalse(fixture["execution_allowed"])
                self.assertNotIn("order_intent_id", fixture)
                self.assertNotIn("approved_order_id", fixture)

    def test_invalid_ids_are_rejected(self):
        for name, contract in FEATURE_CONTRACTS.items():
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                fixture[contract["primary_id"]] = "invalid-id"
                result = self.validator.validate("features", name, fixture)
                self.assertFalse(result.valid)

    def test_additional_properties_are_rejected(self):
        for name in FEATURE_CONTRACTS:
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                fixture["unexpected_field"] = "not allowed"
                result = self.validator.validate("features", name, fixture)
                self.assertFalse(result.valid)

    def _schema(self, name):
        with (SCHEMA_ROOT / f"{name}.schema.json").open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self, name):
        fixture_name = FEATURE_CONTRACTS[name]["fixture"]
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
