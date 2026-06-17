import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "packages" / "contracts" / "schemas" / "trading" / "backtest_review_contract.schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "backtest_review_contract.valid.json"
POLICY_PATH = ROOT / "docs" / "architecture" / "backtest_review_contract.md"


class BacktestReviewContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_schema_is_closed_trading_contract(self):
        schema = self._schema()

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(schema["$id"].endswith("/schemas/trading/backtest_review_contract.schema.json"))

    def test_fixture_validates(self):
        result = self.validator.validate(
            "trading",
            "backtest_review_contract",
            self._fixture(),
        )

        self.assertTrue(result.valid, result.errors)

    def test_review_references_required_evidence(self):
        fixture = self._fixture()

        self.assertRegex(fixture["dataset_lineage_record_id"], r"^dlr_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["leakage_review_report_id"], r"^lrr_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["feature_store_approval_gate_id"], r"^fsag_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["fake_offline_materialization_review_id"], r"^fomr_[A-Za-z0-9_\-]+$")
        self.assertEqual(
            set(fixture["required_evidence"]),
            {
                "dataset_lineage_record",
                "leakage_review_report",
                "feature_store_approval_gate",
                "fake_offline_materialization_review",
                "point_in_time_replay_plan",
                "fee_model_plan",
                "slippage_model_plan",
                "overfitting_review_plan",
                "rollback_plan",
                "human_review_record",
            },
        )

    def test_data_replay_boundary_is_point_in_time_and_local(self):
        boundary = self._fixture()["data_replay_boundary"]

        self.assertTrue(boundary["point_in_time_required"])
        self.assertTrue(boundary["future_data_blocked"])
        self.assertFalse(boundary["external_reads_allowed"])
        self.assertEqual(boundary["source_mode"], "static_fixture")

    def test_modeling_assumptions_require_realistic_cost_and_bias_reviews(self):
        assumptions = self._fixture()["modeling_assumptions"]

        for field in (
            "fee_model_required",
            "slippage_model_required",
            "latency_model_required",
            "spread_model_required",
            "fill_model_required",
            "survivorship_bias_review_required",
            "lookahead_bias_review_required",
        ):
            with self.subTest(field=field):
                self.assertTrue(assumptions[field])

    def test_review_is_rejected_and_all_runtime_paths_are_disabled(self):
        fixture = self._fixture()

        self.assertEqual(fixture["readiness_decision"], "rejected")
        for field in (
            "backtest_runtime_allowed",
            "strategy_execution_allowed",
            "market_data_ingestion_allowed",
            "paper_mode_allowed",
            "portfolio_mutation_allowed",
            "order_intent_creation_allowed",
            "risk_approval_allowed",
            "execution_allowed",
            "broker_or_exchange_access_allowed",
            "network_allowed",
            "credentials_allowed",
            "production_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(fixture[field])

    def test_enabling_any_runtime_or_execution_path_is_rejected(self):
        for field in (
            "backtest_runtime_allowed",
            "strategy_execution_allowed",
            "market_data_ingestion_allowed",
            "paper_mode_allowed",
            "portfolio_mutation_allowed",
            "order_intent_creation_allowed",
            "risk_approval_allowed",
            "execution_allowed",
            "broker_or_exchange_access_allowed",
            "network_allowed",
            "credentials_allowed",
            "production_allowed",
        ):
            fixture = self._fixture()
            fixture[field] = True

            with self.subTest(field=field):
                result = self.validator.validate("trading", "backtest_review_contract", fixture)
                self.assertFalse(result.valid)

    def test_policy_documents_fail_closed_boundaries(self):
        text = POLICY_PATH.read_text(encoding="utf-8").lower()

        self.assertIn("does not approve a backtest engine", text)
        self.assertIn("backtest runtime is not enabled", text)
        self.assertIn("strategy execution is not enabled", text)
        self.assertIn("market data ingestion is not enabled", text)
        self.assertIn("network access is not allowed", text)
        self.assertIn("credentials are not allowed", text)

    def _schema(self):
        with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self):
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
