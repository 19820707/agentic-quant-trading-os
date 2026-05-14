import copy
import json
import unittest
from datetime import datetime
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas" / "features"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts"
POLICY_DOC = ROOT / "docs" / "architecture" / "data_lineage_and_leakage_policy.md"

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
        self.assertEqual(fixture["label_timestamp_field"], "label_timestamp")
        self.assertGreater(fixture["label_horizon_seconds"], 0)
        self.assertGreaterEqual(fixture["feature_availability_lag_seconds"], 0)
        self.assertTrue(fixture["point_in_time_validated"])
        self.assertTrue(fixture["leakage_review_required"])
        self.assertTrue(fixture["split_policy"]["temporal_order_preserved"])
        self.assertFalse(fixture["split_policy"]["shuffle_allowed"])

    def test_dataset_lineage_window_is_temporally_ordered(self):
        fixture = self._fixture("dataset_lineage_record")
        window = fixture["dataset_window"]

        start = datetime.fromisoformat(window["start_timestamp"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(window["end_timestamp"].replace("Z", "+00:00"))

        self.assertLess(start, end)
        self.assertTrue(fixture["source_snapshots"])
        self.assertTrue(fixture["transformation_ids"])

    def test_leakage_review_cannot_approve_training_production_or_execution(self):
        fixture = self._fixture("leakage_review_report")
        check_names = {check["check_name"] for check in fixture["checks"]}
        required = {
            "event_timestamp_present",
            "created_timestamp_present",
            "available_timestamp_present",
            "label_horizon_validated",
            "future_data_join_guard",
            "train_validation_split_temporal",
            "feature_availability_lag_reviewed",
            "target_leakage_guard",
            "cross_sectional_leakage_guard",
            "survivorship_bias_reviewed",
        }

        self.assertTrue(required.issubset(check_names))
        self.assertTrue(fixture["required_checks_complete"])
        self.assertFalse(fixture["leakage_detected"])
        self.assertTrue(fixture["blocked_on_leakage"])
        self.assertTrue(fixture["manual_review_required"])
        self.assertFalse(fixture["model_training_approval_allowed"])
        self.assertFalse(fixture["backtest_approval_allowed"])
        self.assertFalse(fixture["production_approval_allowed"])
        self.assertFalse(fixture["network_allowed"])
        self.assertFalse(fixture["credentials_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_feature_lineage_contracts_are_non_executable(self):
        for name in FEATURE_CONTRACTS:
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

    def test_lineage_rejects_model_training_approval(self):
        fixture = self._fixture("dataset_lineage_record")
        fixture["model_training_approval_allowed"] = True

        result = self.validator.validate("features", "dataset_lineage_record", fixture)

        self.assertFalse(result.valid)

    def test_leakage_review_rejects_backtest_approval(self):
        fixture = self._fixture("leakage_review_report")
        fixture["backtest_approval_allowed"] = True

        result = self.validator.validate("features", "leakage_review_report", fixture)

        self.assertFalse(result.valid)

    def test_policy_document_defines_point_in_time_and_leakage_boundaries(self):
        text = POLICY_DOC.read_text(encoding="utf-8").lower()

        for phrase in (
            "point-in-time rule",
            "available_timestamp",
            "label_timestamp",
            "target leakage guard",
            "cross-sectional leakage guard",
            "survivorship bias review",
            "model_training_approval_allowed",
            "backtest_approval_allowed",
            "credentials_allowed",
            "execution_allowed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def _schema(self, name):
        with (SCHEMA_ROOT / f"{name}.schema.json").open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self, name):
        fixture_name = FEATURE_CONTRACTS[name]["fixture"]
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
