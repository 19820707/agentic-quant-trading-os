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
    "strategy_research_pattern": {
        "fixture": "strategy_research_pattern.valid.json",
        "primary_id": "strategy_research_pattern_id",
        "enum_field": "pattern_category",
        "invalid_enum": "EXECUTION_PATTERN",
        "timestamp_field": "created_at",
    },
    "strategy_risk_guard_profile": {
        "fixture": "strategy_risk_guard_profile.valid.json",
        "primary_id": "strategy_risk_guard_profile_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "liquidity_depth_check": {
        "fixture": "liquidity_depth_check.valid.json",
        "primary_id": "liquidity_depth_check_id",
        "enum_field": "liquidity_state",
        "invalid_enum": "READY_TO_TRADE",
        "timestamp_field": "observed_at",
    },
    "orderbook_imbalance_feature": {
        "fixture": "orderbook_imbalance_feature.valid.json",
        "primary_id": "orderbook_imbalance_feature_id",
        "enum_field": "feature_direction",
        "invalid_enum": "PLACE_ORDER",
        "timestamp_field": "observed_at",
    },
    "wallet_activity_observation": {
        "fixture": "wallet_activity_observation.valid.json",
        "primary_id": "wallet_activity_observation_id",
        "enum_field": "activity_type",
        "invalid_enum": "MIRROR_TRADE",
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

    def test_strategy_pattern_contracts_are_non_executable(self):
        for name in (
            "strategy_research_pattern",
            "strategy_risk_guard_profile",
            "liquidity_depth_check",
            "orderbook_imbalance_feature",
            "wallet_activity_observation",
        ):
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                self.assertFalse(fixture["execution_allowed"])
                if "network_allowed" in fixture:
                    self.assertFalse(fixture["network_allowed"])
                if "order_intent_allowed" in fixture:
                    self.assertFalse(fixture["order_intent_allowed"])
                if "risk_approval_allowed" in fixture:
                    self.assertFalse(fixture["risk_approval_allowed"])
                if "copy_allowed" in fixture:
                    self.assertFalse(fixture["copy_allowed"])

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
