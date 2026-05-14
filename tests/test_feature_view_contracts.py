import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas" / "features"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts"
POLICY_DOC = ROOT / "docs" / "architecture" / "feature_view_point_in_time_policy.md"

FEATURE_VIEW_CONTRACTS = {
    "feature_view_contract": {
        "fixture": "feature_view_contract.valid.json",
        "primary_id": "feature_view_contract_id",
    },
    "point_in_time_join_plan": {
        "fixture": "point_in_time_join_plan.valid.json",
        "primary_id": "point_in_time_join_plan_id",
    },
}


class FeatureViewContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_feature_view_fixtures_validate(self):
        for name in FEATURE_VIEW_CONTRACTS:
            with self.subTest(schema=name):
                result = self.validator.validate("features", name, self._fixture(name))
                self.assertTrue(result.valid, result.errors)

    def test_feature_view_schemas_are_closed(self):
        for name in FEATURE_VIEW_CONTRACTS:
            with self.subTest(schema=name):
                schema = self._schema(name)
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue(schema["$id"].endswith(f"/schemas/features/{name}.schema.json"))

    def test_feature_view_requires_point_in_time_timestamp_fields(self):
        fixture = self._fixture("feature_view_contract")

        self.assertEqual(fixture["event_timestamp_field"], "event_timestamp")
        self.assertEqual(fixture["created_timestamp_field"], "created_timestamp")
        self.assertEqual(fixture["available_timestamp_field"], "available_timestamp")
        self.assertTrue(fixture["point_in_time_required"])
        self.assertTrue(fixture["feature_availability_lag_required"])
        self.assertTrue(fixture["leakage_review_required"])
        self.assertGreater(fixture["max_feature_staleness_seconds"], 0)
        self.assertRegex(fixture["dataset_lineage_record_id"], r"^dlr_")
        self.assertRegex(fixture["leakage_review_report_id"], r"^lrr_")

    def test_feature_view_contract_cannot_materialize_or_approve_training(self):
        fixture = self._fixture("feature_view_contract")

        self.assertFalse(fixture["materialization_allowed"])
        self.assertFalse(fixture["model_training_approval_allowed"])
        self.assertFalse(fixture["backtest_approval_allowed"])
        self.assertFalse(fixture["network_allowed"])
        self.assertFalse(fixture["credentials_allowed"])
        self.assertFalse(fixture["production_approval_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_each_feature_declares_availability_and_staleness(self):
        fixture = self._fixture("feature_view_contract")

        for feature in fixture["features"]:
            with self.subTest(feature=feature["name"]):
                self.assertTrue(feature["source_field"])
                self.assertGreaterEqual(feature["availability_lag_seconds"], 0)
                self.assertGreater(feature["max_staleness_seconds"], 0)
                self.assertTrue(feature["point_in_time_safe"])

    def test_point_in_time_join_plan_blocks_future_data_joins(self):
        fixture = self._fixture("point_in_time_join_plan")

        self.assertEqual(fixture["join_timestamp_field"], "event_timestamp")
        self.assertEqual(fixture["feature_available_timestamp_field"], "available_timestamp")
        self.assertEqual(fixture["join_semantics"], "asof_backward")
        self.assertTrue(fixture["temporal_order_preserved"])
        self.assertTrue(fixture["entity_key_match_required"])
        self.assertFalse(fixture["future_data_join_allowed"])
        self.assertTrue(fixture["leakage_review_required"])
        self.assertFalse(fixture["materialization_allowed"])
        self.assertFalse(fixture["model_training_approval_allowed"])
        self.assertFalse(fixture["backtest_approval_allowed"])
        self.assertFalse(fixture["network_allowed"])
        self.assertFalse(fixture["credentials_allowed"])
        self.assertFalse(fixture["production_approval_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_feature_view_contracts_are_non_executable(self):
        for name in FEATURE_VIEW_CONTRACTS:
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                self.assertFalse(fixture["execution_allowed"])
                self.assertNotIn("order_intent_id", fixture)
                self.assertNotIn("approved_order_id", fixture)
                if "network_allowed" in fixture:
                    self.assertFalse(fixture["network_allowed"])
                if "credentials_allowed" in fixture:
                    self.assertFalse(fixture["credentials_allowed"])

    def test_invalid_ids_are_rejected(self):
        for name, contract in FEATURE_VIEW_CONTRACTS.items():
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                fixture[contract["primary_id"]] = "invalid-id"
                result = self.validator.validate("features", name, fixture)
                self.assertFalse(result.valid)

    def test_additional_properties_are_rejected(self):
        for name in FEATURE_VIEW_CONTRACTS:
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                fixture["unexpected_field"] = "not allowed"
                result = self.validator.validate("features", name, fixture)
                self.assertFalse(result.valid)

    def test_feature_view_rejects_materialization_enablement(self):
        fixture = self._fixture("feature_view_contract")
        fixture["materialization_allowed"] = True

        result = self.validator.validate("features", "feature_view_contract", fixture)

        self.assertFalse(result.valid)

    def test_join_plan_rejects_future_data_join_enablement(self):
        fixture = self._fixture("point_in_time_join_plan")
        fixture["future_data_join_allowed"] = True

        result = self.validator.validate("features", "point_in_time_join_plan", fixture)

        self.assertFalse(result.valid)

    def test_policy_document_defines_feature_view_boundaries(self):
        text = POLICY_DOC.read_text(encoding="utf-8").lower()

        for phrase in (
            "datasetlineagerecord",
            "leakagereviewreport",
            "availability lag",
            "maximum staleness",
            "as-of semantics",
            "materialization_allowed",
            "model_training_approval_allowed",
            "backtest_approval_allowed",
            "network_allowed",
            "credentials_allowed",
            "execution_allowed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def _schema(self, name):
        with (SCHEMA_ROOT / f"{name}.schema.json").open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self, name):
        fixture_name = FEATURE_VIEW_CONTRACTS[name]["fixture"]
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
