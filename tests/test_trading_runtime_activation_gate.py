import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator
from packages.contracts.registry import SchemaRegistry


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "packages" / "contracts" / "schemas" / "trading" / "trading_runtime_activation_gate.schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "contracts" / "trading_runtime_activation_gate.valid.json"
DOC_PATH = ROOT / "docs" / "architecture" / "trading_runtime_activation_gate.md"


class TradingRuntimeActivationGateTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.registry = SchemaRegistry()

    def test_schema_is_registered_under_trading(self):
        names = {entry.name for entry in self.registry.list_schemas("trading")}

        self.assertIn("trading_runtime_activation_gate", names)

    def test_schema_is_closed_contract(self):
        schema = self._schema()

        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["type"], "object")
        self.assertFalse(schema["additionalProperties"])
        self.assertTrue(schema["$id"].endswith("/schemas/trading/trading_runtime_activation_gate.schema.json"))

    def test_fixture_validates(self):
        result = self.validator.validate("trading", "trading_runtime_activation_gate", self._fixture())

        self.assertTrue(result.valid, result.errors)

    def test_runtime_modes_are_blocked_by_default(self):
        payload = self._fixture()

        blocked_fields = [
            "backtest_runtime_allowed",
            "paper_runtime_allowed",
            "live_trading_allowed",
            "production_allowed",
            "market_data_ingestion_allowed",
            "webhook_ingestion_allowed",
            "signal_ingestion_allowed",
            "broker_sdk_allowed",
            "exchange_sdk_allowed",
            "network_allowed",
            "credentials_allowed",
            "order_submission_allowed",
            "order_cancellation_allowed",
            "withdrawal_allowed",
            "transfer_allowed",
            "model_training_allowed",
            "feature_store_runtime_allowed",
        ]

        for field in blocked_fields:
            with self.subTest(field=field):
                self.assertFalse(payload[field])

    def test_mandatory_execution_boundary_is_encoded(self):
        payload = self._fixture()

        self.assertTrue(payload["risk_gateway_required"])
        self.assertTrue(payload["approved_order_required_for_execution"])
        self.assertTrue(payload["execution_engine_only_for_broker_access"])
        self.assertTrue(payload["direct_signal_to_order_forbidden"])
        self.assertTrue(payload["direct_ai_to_broker_forbidden"])
        self.assertTrue(payload["direct_dashboard_to_broker_forbidden"])

    def test_required_evidence_includes_data_feature_backtest_paper_and_safety_gates(self):
        payload = self._fixture()

        self.assertEqual(
            set(payload["required_evidence"]),
            {
                "dataset_lineage_record",
                "leakage_review_report",
                "feature_store_approval_gate",
                "fake_offline_materialization_review",
                "backtest_review_contract",
                "paper_trading_review_contract",
                "broker_adapter_safety_policy",
                "execution_venue_capability",
                "credential_vault_policy",
                "kill_switch_policy",
                "audit_event_policy",
                "human_approval_record",
            },
        )

    def test_schema_rejects_runtime_enablement_flips(self):
        for field in (
            "live_trading_allowed",
            "paper_runtime_allowed",
            "backtest_runtime_allowed",
            "network_allowed",
            "credentials_allowed",
            "order_submission_allowed",
            "broker_sdk_allowed",
            "exchange_sdk_allowed",
        ):
            payload = self._fixture()
            payload[field] = True

            with self.subTest(field=field):
                result = self.validator.validate("trading", "trading_runtime_activation_gate", payload)
                self.assertFalse(result.valid)

    def test_policy_document_describes_fail_closed_runtime_boundary(self):
        text = DOC_PATH.read_text(encoding="utf-8").lower()

        self.assertIn("fail-closed", text)
        self.assertIn("live trading is not enabled", text)
        self.assertIn("network access is not enabled", text)
        self.assertIn("credentials are not enabled", text)
        self.assertIn("deterministic-risk-gateway", text)
        self.assertIn("approvedorder", text)
        self.assertIn("executionreport", text)

    def test_fixture_does_not_contain_credential_material(self):
        text = FIXTURE_PATH.read_text(encoding="utf-8").lower()

        for marker in ("api_key", "password", "private_key", "broker_secret", "exchange_secret", "access_token"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, text)

    def test_additional_properties_are_rejected(self):
        payload = copy.deepcopy(self._fixture())
        payload["unsafe_extra_field"] = True

        result = self.validator.validate("trading", "trading_runtime_activation_gate", payload)

        self.assertFalse(result.valid)

    def _schema(self):
        with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self):
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
