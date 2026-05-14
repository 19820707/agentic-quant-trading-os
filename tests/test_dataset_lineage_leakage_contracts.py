import copy
import json
import unittest
from datetime import datetime
from pathlib import Path

from packages.contracts import ContractValidator
from packages.contracts.registry import SchemaRegistry


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts" / "data"

DATASET_LINEAGE_FIXTURE = FIXTURE_ROOT / "dataset_lineage_record.valid.json"
LEAKAGE_REVIEW_FIXTURE = FIXTURE_ROOT / "leakage_review_report.valid.json"


class DatasetLineageLeakageContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.registry = SchemaRegistry()
        self.dataset_lineage = self._load(DATASET_LINEAGE_FIXTURE)
        self.leakage_review = self._load(LEAKAGE_REVIEW_FIXTURE)

    def test_data_domain_schemas_are_registered(self):
        names = {entry.name for entry in self.registry.list_schemas("data")}

        self.assertIn("dataset_lineage_record", names)
        self.assertIn("leakage_review_report", names)

    def test_valid_dataset_lineage_fixture_matches_schema(self):
        result = self.validator.validate("data", "dataset_lineage_record", self.dataset_lineage)

        self.assertTrue(result.valid, result.errors)

    def test_valid_leakage_review_fixture_matches_schema(self):
        result = self.validator.validate("data", "leakage_review_report", self.leakage_review)

        self.assertTrue(result.valid, result.errors)

    def test_dataset_and_leakage_review_are_correlated(self):
        self.assertEqual(
            self.dataset_lineage["dataset_lineage_id"],
            self.leakage_review["dataset_lineage_id"],
        )
        self.assertEqual(self.dataset_lineage["dataset_id"], self.leakage_review["dataset_id"])
        self.assertEqual(self.dataset_lineage["correlation_id"], self.leakage_review["correlation_id"])
        self.assertEqual(
            self.dataset_lineage["leakage_review_report_id"],
            self.leakage_review["leakage_review_report_id"],
        )

    def test_dataset_lineage_is_non_runtime_and_secret_free(self):
        self.assertTrue(self.dataset_lineage["non_executable"])
        self.assertFalse(self.dataset_lineage["contains_secrets"])
        self.assertFalse(self.dataset_lineage["live_data_included"])
        self.assertFalse(self.dataset_lineage["external_network_required"])

    def test_leakage_review_does_not_approve_training_backtest_or_live_use(self):
        self.assertTrue(self.leakage_review["non_executable"])
        self.assertFalse(self.leakage_review["contains_secrets"])
        self.assertFalse(self.leakage_review["external_network_required"])
        self.assertFalse(self.leakage_review["approved_for_model_training"])
        self.assertFalse(self.leakage_review["approved_for_backtest"])
        self.assertFalse(self.leakage_review["approved_for_live_use"])

    def test_point_in_time_controls_are_fail_safe_required(self):
        controls = self.dataset_lineage["point_in_time_controls"]
        split_policy = self.dataset_lineage["split_policy"]

        self.assertTrue(controls["as_of_join_required"])
        self.assertTrue(controls["future_data_excluded"])
        self.assertTrue(split_policy["temporal_order_preserved"])
        self.assertFalse(split_policy["overlap_allowed"])

    def test_temporal_bounds_are_ordered_for_fixture(self):
        bounds = self.dataset_lineage["temporal_bounds"]
        observation_start = self._parse(bounds["observation_start_at"])
        observation_end = self._parse(bounds["observation_end_at"])
        max_event_time = self._parse(bounds["max_event_time_at"])
        as_of_cutoff = self._parse(bounds["as_of_cutoff_at"])
        label_start = self._parse(bounds["label_start_at"])

        self.assertLess(observation_start, observation_end)
        self.assertLessEqual(max_event_time, as_of_cutoff)
        self.assertGreaterEqual(label_start, as_of_cutoff)

    def test_future_information_transformations_are_rejected_by_schema(self):
        payload = copy.deepcopy(self.dataset_lineage)
        payload["transformations"][0]["uses_future_information"] = True

        result = self.validator.validate("data", "dataset_lineage_record", payload)

        self.assertFalse(result.valid)

    def test_model_training_approval_is_rejected_by_schema(self):
        payload = copy.deepcopy(self.leakage_review)
        payload["approved_for_model_training"] = True

        result = self.validator.validate("data", "leakage_review_report", payload)

        self.assertFalse(result.valid)

    def test_live_use_approval_is_rejected_by_schema(self):
        payload = copy.deepcopy(self.leakage_review)
        payload["approved_for_live_use"] = True

        result = self.validator.validate("data", "leakage_review_report", payload)

        self.assertFalse(result.valid)

    def test_fixtures_do_not_contain_live_or_secret_markers(self):
        for path in (DATASET_LINEAGE_FIXTURE, LEAKAGE_REVIEW_FIXTURE):
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8").lower()
                for marker in (
                    "api_key",
                    "private_key",
                    "secret",
                    "password",
                    "broker",
                    "exchange_secret",
                    "wallet",
                ):
                    self.assertNotIn(marker, text)

    def _load(self, path):
        with path.open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)

    def _parse(self, value):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


if __name__ == "__main__":
    unittest.main()
