import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    ROOT
    / "packages"
    / "contracts"
    / "schemas"
    / "features"
    / "fake_offline_materialization_review.schema.json"
)
FIXTURE_PATH = (
    ROOT / "tests" / "fixtures" / "contracts" / "fake_offline_materialization_review.valid.json"
)
POLICY_PATH = ROOT / "docs" / "architecture" / "fake_offline_materialization_review.md"


class FakeOfflineMaterializationReviewTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_schema_is_closed_feature_contract(self):
        schema = self._schema()

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(schema["$id"].endswith("/schemas/features/fake_offline_materialization_review.schema.json"))

    def test_fixture_validates(self):
        result = self.validator.validate(
            "features",
            "fake_offline_materialization_review",
            self._fixture(),
        )

        self.assertTrue(result.valid, result.errors)

    def test_review_references_required_feature_evidence(self):
        fixture = self._fixture()

        self.assertRegex(fixture["feature_store_approval_gate_id"], r"^fsag_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["feature_view_contract_id"], r"^fvc_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["dataset_lineage_record_id"], r"^dlr_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["leakage_review_report_id"], r"^lrr_[A-Za-z0-9_\-]+$")
        self.assertEqual(
            set(fixture["required_evidence"]),
            {
                "feature_store_approval_gate",
                "dataset_lineage_record",
                "leakage_review_report",
                "feature_view_contract",
                "point_in_time_join_plan",
                "rollback_plan",
                "human_review_record",
            },
        )

    def test_point_in_time_plan_blocks_future_data(self):
        fixture = self._fixture()
        plan = fixture["point_in_time_join_plan"]

        self.assertTrue(plan["future_data_blocked"])
        self.assertIn("as_of_timestamp", plan["as_of_timestamp_field"])
        self.assertIn("event_timestamp", plan["event_timestamp_field"])
        self.assertIn("market_id", plan["join_keys"])

    def test_review_is_rejected_and_all_runtime_paths_are_disabled(self):
        fixture = self._fixture()

        self.assertEqual(fixture["readiness_decision"], "rejected")
        for field in (
            "approved_for_fake_offline_materialization",
            "fake_materialization_allowed",
            "real_materialization_allowed",
            "real_feature_store_allowed",
            "online_serving_allowed",
            "model_training_allowed",
            "backtest_allowed",
            "market_data_ingestion_allowed",
            "signal_creation_allowed",
            "order_intent_creation_allowed",
            "risk_approval_allowed",
            "execution_allowed",
            "network_allowed",
            "credentials_allowed",
            "production_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(fixture[field])

    def test_enabling_any_runtime_or_trading_path_is_rejected(self):
        for field in (
            "fake_materialization_allowed",
            "real_materialization_allowed",
            "real_feature_store_allowed",
            "online_serving_allowed",
            "model_training_allowed",
            "backtest_allowed",
            "market_data_ingestion_allowed",
            "signal_creation_allowed",
            "order_intent_creation_allowed",
            "risk_approval_allowed",
            "execution_allowed",
            "network_allowed",
            "credentials_allowed",
            "production_allowed",
        ):
            fixture = self._fixture()
            fixture[field] = True

            with self.subTest(field=field):
                result = self.validator.validate("features", "fake_offline_materialization_review", fixture)
                self.assertFalse(result.valid)

    def test_external_reads_or_mutable_sources_are_rejected(self):
        for field in ("external_reads_allowed", "mutable_source_allowed"):
            fixture = self._fixture()
            fixture["data_boundary"][field] = True

            with self.subTest(field=field):
                result = self.validator.validate("features", "fake_offline_materialization_review", fixture)
                self.assertFalse(result.valid)

    def test_policy_documents_fail_closed_boundaries(self):
        text = POLICY_PATH.read_text(encoding="utf-8").lower()

        self.assertIn("does not approve real materialization", text)
        self.assertIn("fake offline materialization is not enabled", text)
        self.assertIn("network access is not allowed", text)
        self.assertIn("credentials are not allowed", text)
        self.assertIn("no model training", text)
        self.assertIn("no backtesting", text)

    def _schema(self):
        with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self):
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
