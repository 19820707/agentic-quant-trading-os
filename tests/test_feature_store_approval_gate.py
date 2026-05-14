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
    / "feature_store_approval_gate.schema.json"
)
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "feature_store_approval_gate.valid.json"
POLICY_PATH = ROOT / "docs" / "architecture" / "feature_store_approval_gate.md"


class FeatureStoreApprovalGateTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_schema_is_closed_feature_contract(self):
        schema = self._schema()

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(schema["$id"].endswith("/schemas/features/feature_store_approval_gate.schema.json"))

    def test_fixture_validates(self):
        result = self.validator.validate(
            "features",
            "feature_store_approval_gate",
            self._fixture(),
        )

        self.assertTrue(result.valid, result.errors)

    def test_gate_references_required_evidence_by_id(self):
        fixture = self._fixture()

        self.assertRegex(fixture["feature_view_contract_id"], r"^fvc_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["dataset_lineage_record_id"], r"^dlr_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["leakage_review_report_id"], r"^lrr_[A-Za-z0-9_\-]+$")
        self.assertEqual(
            set(fixture["required_evidence"]),
            {
                "dataset_lineage_record",
                "leakage_review_report",
                "feature_view_contract",
                "point_in_time_join_plan",
                "rollback_plan",
                "human_review_record",
            },
        )

    def test_gate_is_not_an_approval(self):
        fixture = self._fixture()

        for field in (
            "approved_for_fake_offline_materialization",
            "real_feature_store_allowed",
            "online_serving_allowed",
            "materialization_allowed",
            "model_training_approval_allowed",
            "backtest_approval_allowed",
            "network_allowed",
            "credentials_allowed",
            "production_approval_allowed",
            "risk_approval_allowed",
            "execution_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(fixture[field])

    def test_enabling_materialization_is_rejected(self):
        fixture = self._fixture()
        fixture["materialization_allowed"] = True

        result = self.validator.validate("features", "feature_store_approval_gate", fixture)

        self.assertFalse(result.valid)

    def test_enabling_network_or_credentials_is_rejected(self):
        for field in ("network_allowed", "credentials_allowed"):
            fixture = self._fixture()
            fixture[field] = True

            with self.subTest(field=field):
                result = self.validator.validate("features", "feature_store_approval_gate", fixture)
                self.assertFalse(result.valid)

    def test_enabling_training_backtest_risk_or_execution_is_rejected(self):
        for field in (
            "model_training_approval_allowed",
            "backtest_approval_allowed",
            "risk_approval_allowed",
            "execution_allowed",
        ):
            fixture = self._fixture()
            fixture[field] = True

            with self.subTest(field=field):
                result = self.validator.validate("features", "feature_store_approval_gate", fixture)
                self.assertFalse(result.valid)

    def test_policy_documents_fail_closed_boundaries(self):
        text = POLICY_PATH.read_text(encoding="utf-8").lower()

        self.assertIn("does not approve a real feature store", text)
        self.assertIn("offline materialization is not enabled", text)
        self.assertIn("network access is not allowed", text)
        self.assertIn("credentials are not allowed", text)
        self.assertIn("no trading logic", text)

    def _schema(self):
        with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self):
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
