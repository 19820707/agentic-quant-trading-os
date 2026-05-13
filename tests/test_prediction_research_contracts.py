import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas" / "research"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts"

RESEARCH_CONTRACTS = {
    "research_dossier": {
        "fixture": "research_dossier.valid.json",
        "primary_id": "research_dossier_id",
        "enum_field": "market_category",
        "invalid_enum": "INVALID_CATEGORY",
        "timestamp_field": "created_at",
    },
    "probability_estimate": {
        "fixture": "probability_estimate.valid.json",
        "primary_id": "probability_estimate_id",
        "enum_field": "method",
        "invalid_enum": "INVALID_METHOD",
        "timestamp_field": "estimated_at",
    },
    "hypothesis_record": {
        "fixture": "hypothesis_record.valid.json",
        "primary_id": "hypothesis_id",
        "enum_field": "status",
        "invalid_enum": "INVALID_STATUS",
        "timestamp_field": "created_at",
    },
    "analyst_report": {
        "fixture": "analyst_report.valid.json",
        "primary_id": "analyst_report_id",
        "enum_field": "analyst_role",
        "invalid_enum": "INVALID_ROLE",
        "timestamp_field": "created_at",
    },
    "debate_transcript": {
        "fixture": "debate_transcript.valid.json",
        "primary_id": "debate_transcript_id",
        "enum_field": "debate_type",
        "invalid_enum": "INVALID_DEBATE",
        "timestamp_field": "created_at",
    },
    "signal_candidate": {
        "fixture": "signal_candidate.valid.json",
        "primary_id": "signal_candidate_id",
        "enum_field": "signal",
        "invalid_enum": "BUY_YES",
        "timestamp_field": "created_at",
    },
    "risk_review_input": {
        "fixture": "risk_review_input.valid.json",
        "primary_id": "risk_review_input_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "order_book_imbalance_observation": {
        "fixture": "order_book_imbalance_observation.valid.json",
        "primary_id": "order_book_imbalance_observation_id",
        "enum_field": "trend_state",
        "invalid_enum": "EXECUTE",
        "timestamp_field": "observed_at",
    },
    "trend_state_observation": {
        "fixture": "trend_state_observation.valid.json",
        "primary_id": "trend_state_observation_id",
        "enum_field": "current_trend",
        "invalid_enum": "BUY",
        "timestamp_field": "observed_at",
    },
    "trend_flip_observation": {
        "fixture": "trend_flip_observation.valid.json",
        "primary_id": "trend_flip_observation_id",
        "enum_field": "to_side",
        "invalid_enum": "SELL",
        "timestamp_field": "flip_detected_at",
    },
    "preflight_safety_review": {
        "fixture": "preflight_safety_review.valid.json",
        "primary_id": "preflight_safety_review_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "simulation_mode_policy": {
        "fixture": "simulation_mode_policy.valid.json",
        "primary_id": "simulation_mode_policy_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "arbitrage_pnl_simulation_summary": {
        "fixture": "arbitrage_pnl_simulation_summary.valid.json",
        "primary_id": "arbitrage_pnl_simulation_summary_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "computed_at",
    },
    "strategy_history_event": {
        "fixture": "strategy_history_event.valid.json",
        "primary_id": "strategy_history_event_id",
        "enum_field": "event_type",
        "invalid_enum": "ORDER",
        "timestamp_field": "observed_at",
    },
}

FORBIDDEN_SCHEMA_TEXT = (
    "api_key",
    "private_key",
    "broker_secret",
    "exchange_secret",
    "wallet_private_key",
    "submit_order",
    "create_order",
    "cancel_order",
    "withdraw",
    "transfer",
    "ApprovedOrder creation",
)


class PredictionResearchContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_research_schemas_exist_and_are_closed(self):
        for name in RESEARCH_CONTRACTS:
            with self.subTest(schema=name):
                schema = self._schema(name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertIn("$id", schema)
                self.assertTrue(schema["$id"].endswith(f"/schemas/research/{name}.schema.json"))

    def test_research_fixtures_validate(self):
        for name in RESEARCH_CONTRACTS:
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                result = self.validator.validate("research", name, fixture)
                self.assertTrue(result.valid, result.errors)

    def test_research_contracts_are_non_executable(self):
        for name in RESEARCH_CONTRACTS:
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                self.assertFalse(fixture.get("execution_allowed", True))
                self.assertNotIn("approved_order_id", fixture)
                self.assertNotIn("order_intent_id", fixture)

    def test_signal_candidate_cannot_create_order_intent(self):
        fixture = self._fixture("signal_candidate")

        self.assertFalse(fixture["order_intent_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_risk_review_input_cannot_approve_risk(self):
        fixture = self._fixture("risk_review_input")

        self.assertTrue(fixture["deterministic_gateway_required"])
        self.assertFalse(fixture["risk_approval_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_trend_observations_are_non_executable(self):
        for name in (
            "order_book_imbalance_observation",
            "trend_state_observation",
            "trend_flip_observation",
        ):
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                self.assertFalse(fixture["execution_allowed"])
                if "observation_only" in fixture:
                    self.assertTrue(fixture["observation_only"])

    def test_preflight_and_simulation_policies_fail_closed(self):
        preflight = self._fixture("preflight_safety_review")
        simulation = self._fixture("simulation_mode_policy")

        self.assertTrue(preflight["simulation_mode_required"])
        self.assertFalse(preflight["account_check_allowed"])
        self.assertFalse(preflight["balance_check_allowed"])
        self.assertFalse(preflight["credentials_allowed"])
        self.assertFalse(preflight["network_allowed"])
        self.assertFalse(preflight["production_enabled"])
        self.assertFalse(preflight["execution_allowed"])
        self.assertTrue(simulation["simulation_required"])
        self.assertFalse(simulation["production_mode_allowed"])
        self.assertFalse(simulation["runtime_order_allowed"])
        self.assertFalse(simulation["settlement_allowed"])
        self.assertFalse(simulation["execution_allowed"])

    def test_pnl_and_history_records_are_research_only(self):
        pnl = self._fixture("arbitrage_pnl_simulation_summary")
        event = self._fixture("strategy_history_event")

        self.assertTrue(pnl["simulation_only"])
        self.assertFalse(pnl["production_approval_allowed"])
        self.assertFalse(pnl["execution_allowed"])
        self.assertFalse(event["secrets_allowed"])
        self.assertFalse(event["execution_allowed"])

    def test_missing_required_fields_are_rejected(self):
        for name in RESEARCH_CONTRACTS:
            with self.subTest(schema=name):
                schema = self._schema(name)
                fixture = self._fixture(name)
                fixture.pop(schema["required"][0])
                result = self.validator.validate("research", name, fixture)
                self.assertFalse(result.valid)

    def test_invalid_enums_are_rejected(self):
        for name, contract in RESEARCH_CONTRACTS.items():
            if contract["enum_field"] is None:
                continue
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                fixture[contract["enum_field"]] = contract["invalid_enum"]
                result = self.validator.validate("research", name, fixture)
                self.assertFalse(result.valid)

    def test_invalid_id_patterns_are_rejected(self):
        for name, contract in RESEARCH_CONTRACTS.items():
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                fixture[contract["primary_id"]] = "invalid-id"
                result = self.validator.validate("research", name, fixture)
                self.assertFalse(result.valid)

    def test_additional_properties_are_rejected(self):
        for name in RESEARCH_CONTRACTS:
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                fixture["unexpected_field"] = "not allowed"
                result = self.validator.validate("research", name, fixture)
                self.assertFalse(result.valid)

    def test_schema_text_does_not_introduce_credentials_or_execution_methods(self):
        for path in sorted(SCHEMA_ROOT.glob("*.schema.json")):
            text = path.read_text(encoding="utf-8").lower()
            with self.subTest(schema=path.name):
                for forbidden in FORBIDDEN_SCHEMA_TEXT:
                    self.assertNotIn(forbidden.lower(), text)

    def _schema(self, name):
        with (SCHEMA_ROOT / f"{name}.schema.json").open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self, name):
        fixture_name = RESEARCH_CONTRACTS[name]["fixture"]
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
