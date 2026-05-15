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
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "fake_offline_materialization_review.valid.json"
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

    def test_review_links_required_prior_evidence(self):
        fixture = self._fixture()

        self.assertRegex(fixture["feature_store_approval_gate_id"], r"^fsag_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["feature_view_contract_id"], r"^fvc_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["dataset_lineage_record_id"], r"^dlr_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["leakage_review_report_id"], r"^lrr_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["point_in_time_join_plan_id"], r"^pitjp_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["rollback_plan_id"], r"^rbp_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["human_review_record_id"], r"^hrr_[A-Za-z0-9_\-]+$")

    def test_required_checks_cover_local_point_in_time_and_blocked_runtime(self):
        fixture = self._fixture()

        self.assertEqual(
            set(fixture["required_checks"]),
            {
                "local_only",
                "deterministic_inputs",
                "point_in_time_join_verified",
                "leakage_review_linked",
                "rollback_plan_linked",
                "training_blocked",
                "execution_blocked",
            },
        )

    def test_review_is_not_materialization_or_runtime_approval(self):
        fixture = self._fixture()

        for field in (
            "fake_materialization_harness_allowed",
            "real_materialization_allowed",
            "real_feature_store_allowed",
            "online_serving_allowed",
            "database_write_allowed",
            "external_data_fetch_allowed",
            "network_allowed",
            "credentials_allowed",
            "model_training_allowed",
            "backtest_allowed",
            "signal_candidate_allowed",
            "order_intent_allowed",
            "risk_approval_allowed",
            "execution_allowed",
            "production_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(fixture[field])

    def test_runtime_or_training_enablement_is_rejected(self):
        for field in (
            "fake_materialization_harness_allowed",
            "real_materialization_allowed",
            "model_training_allowed",
            "backtest_allowed",
            "signal_candidate_allowed",
        ):
            fixture = self._fixture()
            fixture[field] = True

            with self.subTest(field=field):
                result = self.validator.validate("features", "fake_offline_materialization_review", fixture)
                self.assertFalse(result.valid)

    def test_network_credentials_or_execution_enablement_is_rejected(self):
        for field in (
            "network_allowed",
            "credentials_allowed",
            "order_intent_allowed",
            "risk_approval_allowed",
            "execution_allowed",
            "production_allowed",
        ):
            fixture = self._fixture()
            fixture[field] = True

            with self.subTest(field=field):
                result = self.validator.validate("features", "fake_offline_materialization_review", fixture)
                self.assertFalse(result.valid)

    def test_policy_documents_review_only_boundary(self):
        text = POLICY_PATH.read_text(encoding="utf-8").lower()

        self.assertIn("does not approve materialization jobs", text)
        self.assertIn("future fake materialization plan", text)
        self.assertIn("network access", text)
        self.assertIn("credentials", text)
        self.assertIn("no trading or execution", text)

    def _schema(self):
        with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self):
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
