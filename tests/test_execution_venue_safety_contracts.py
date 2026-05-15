import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator
from packages.contracts.registry import SchemaRegistry


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts"

SAFETY_CONTRACTS = {
    "execution_venue_capability": "execution_venue_capability.valid.json",
    "broker_adapter_safety_policy": "broker_adapter_safety_policy.valid.json",
    "paper_trading_session": "paper_trading_session.valid.json",
    "strategy_runtime_approval_gate": "strategy_runtime_approval_gate.valid.json",
}

PROHIBITED_METHODS = {
    "create_order",
    "cancel_order",
    "edit_order",
    "withdraw",
    "transfer",
    "set_leverage",
    "buy",
    "sell",
    "execute",
    "submit_order",
}


class ExecutionVenueSafetyContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.registry = SchemaRegistry()

    def test_safety_contracts_are_registered_under_trading(self):
        names = {entry.name for entry in self.registry.list_schemas("trading")}

        self.assertTrue(set(SAFETY_CONTRACTS).issubset(names))

    def test_safety_fixtures_validate(self):
        for schema_name, fixture_name in SAFETY_CONTRACTS.items():
            with self.subTest(schema=schema_name):
                result = self.validator.validate("trading", schema_name, self._load(fixture_name))
                self.assertTrue(result.valid, result.errors)

    def test_execution_venue_capability_is_fail_closed_for_execution(self):
        payload = self._load("execution_venue_capability.valid.json")

        self.assertFalse(payload["order_submission_allowed"])
        self.assertFalse(payload["order_cancellation_allowed"])
        self.assertFalse(payload["position_mutation_allowed"])
        self.assertFalse(payload["withdrawal_allowed"])
        self.assertFalse(payload["transfer_allowed"])
        self.assertFalse(payload["private_endpoint_allowed"])
        self.assertFalse(payload["credentials_allowed"])
        self.assertTrue(payload["risk_gateway_required"])
        self.assertTrue(payload["approved_order_required"])
        self.assertTrue(payload["direct_ai_to_venue_forbidden"])
        self.assertTrue(PROHIBITED_METHODS.issubset(set(payload["prohibited_methods"])))

    def test_broker_adapter_policy_blocks_direct_paths_and_raw_order_intents(self):
        payload = self._load("broker_adapter_safety_policy.valid.json")

        self.assertTrue(payload["risk_gateway_required"])
        self.assertTrue(payload["approved_order_only"])
        self.assertTrue(payload["order_intent_rejected"])
        self.assertTrue(payload["direct_model_path_forbidden"])
        self.assertTrue(payload["direct_dashboard_path_forbidden"])
        self.assertTrue(payload["direct_agent_path_forbidden"])
        self.assertFalse(payload["credentials_allowed"])
        self.assertFalse(payload["private_endpoint_allowed"])
        self.assertFalse(payload["live_order_submission_allowed"])
        self.assertTrue(payload["kill_switch_required"])
        self.assertTrue(payload["idempotency_key_required"])
        self.assertTrue(payload["execution_report_required"])
        self.assertTrue(payload["audit_event_required"])

    def test_paper_session_has_no_real_broker_or_credentials(self):
        payload = self._load("paper_trading_session.valid.json")

        self.assertEqual(payload["session_status"], "READY_FOR_FAKE_RUN")
        self.assertTrue(payload["risk_gateway_required"])
        self.assertTrue(payload["approved_order_required"])
        self.assertFalse(payload["real_broker_allowed"])
        self.assertFalse(payload["credentials_allowed"])
        self.assertFalse(payload["production_allowed"])
        self.assertEqual(payload["allowed_venues"], ["paper"])

    def test_strategy_runtime_gate_keeps_execution_and_production_blocked(self):
        payload = self._load("strategy_runtime_approval_gate.valid.json")

        self.assertEqual(payload["runtime_status"], "RESEARCH_ONLY")
        self.assertTrue(payload["research_only"])
        self.assertFalse(payload["paper_trading_allowed"])
        self.assertFalse(payload["live_trading_allowed"])
        self.assertFalse(payload["production_allowed"])
        self.assertFalse(payload["broker_credentials_allowed"])
        self.assertTrue(payload["lineage_review_required"])
        self.assertTrue(payload["leakage_review_required"])
        self.assertTrue(payload["backtest_evidence_required"])
        self.assertTrue(payload["paper_evidence_required"])

    def test_schema_const_guards_reject_unsafe_approval_flips(self):
        unsafe_cases = [
            ("execution_venue_capability", "execution_venue_capability.valid.json", "order_submission_allowed"),
            ("execution_venue_capability", "execution_venue_capability.valid.json", "credentials_allowed"),
            ("broker_adapter_safety_policy", "broker_adapter_safety_policy.valid.json", "approved_order_only"),
            ("broker_adapter_safety_policy", "broker_adapter_safety_policy.valid.json", "credentials_allowed"),
            ("paper_trading_session", "paper_trading_session.valid.json", "real_broker_allowed"),
            ("strategy_runtime_approval_gate", "strategy_runtime_approval_gate.valid.json", "production_allowed"),
        ]

        for schema_name, fixture_name, field_name in unsafe_cases:
            with self.subTest(schema=schema_name, field=field_name):
                payload = copy.deepcopy(self._load(fixture_name))
                payload[field_name] = not payload[field_name]
                result = self.validator.validate("trading", schema_name, payload)
                self.assertFalse(result.valid)

    def test_fixtures_do_not_contain_secret_material_or_runtime_clients(self):
        forbidden_markers = [
            "api_key",
            "secret",
            "password",
            "private_key",
            "client_secret",
            "broker_token",
            "exchange_token",
            "real_exchange_client",
        ]

        for fixture_name in SAFETY_CONTRACTS.values():
            with self.subTest(fixture=fixture_name):
                text = (FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8").lower()
                for marker in forbidden_markers:
                    self.assertNotIn(marker, text)

    def test_execution_report_schema_supports_expired_and_accepted_lifecycle_states(self):
        payload = self._load("execution_report.valid.json")

        for status, event_type in [
            ("ACCEPTED", "ORDER_ACCEPTED"),
            ("EXPIRED", "ORDER_EXPIRED"),
        ]:
            with self.subTest(status=status):
                candidate = copy.deepcopy(payload)
                candidate["status"] = status
                candidate["event_type"] = event_type
                result = self.validator.validate("trading", "execution_report", candidate)
                self.assertTrue(result.valid, result.errors)

    def _load(self, fixture_name):
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
