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
    "prediction_market_toolkit_assessment": {
        "fixture": "prediction_market_toolkit_assessment.valid.json",
        "primary_id": "prediction_market_toolkit_assessment_id",
        "enum_field": "default_state",
        "invalid_enum": "RUNTIME_APPROVED",
        "timestamp_field": "assessed_at",
    },
    "strategy_pattern_classification": {
        "fixture": "strategy_pattern_classification.valid.json",
        "primary_id": "strategy_pattern_classification_id",
        "enum_field": "pattern_type",
        "invalid_enum": "ORDER_EXECUTION",
        "timestamp_field": "classified_at",
    },
    "integration_readiness_assessment": {
        "fixture": "integration_readiness_assessment.valid.json",
        "primary_id": "integration_readiness_assessment_id",
        "enum_field": "approval_recommendation",
        "invalid_enum": "APPROVE_RUNTIME",
        "timestamp_field": "assessed_at",
    },
    "market_making_research_policy": {
        "fixture": "market_making_research_policy.valid.json",
        "primary_id": "market_making_research_policy_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "liquidity_quality_observation": {
        "fixture": "liquidity_quality_observation.valid.json",
        "primary_id": "liquidity_quality_observation_id",
        "enum_field": "liquidity_quality",
        "invalid_enum": "EXECUTABLE",
        "timestamp_field": "observed_at",
    },
    "spread_risk_estimate": {
        "fixture": "spread_risk_estimate.valid.json",
        "primary_id": "spread_risk_estimate_id",
        "enum_field": "risk_level",
        "invalid_enum": "APPROVED",
        "timestamp_field": "estimated_at",
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

    def test_toolkit_governance_assessments_do_not_enable_runtime(self):
        for name in ("prediction_market_toolkit_assessment", "integration_readiness_assessment"):
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                self.assertFalse(fixture["dependency_allowed"])
                self.assertFalse(fixture["runtime_enabled"])
                self.assertFalse(fixture["execution_allowed"])

    def test_strategy_pattern_classification_stops_before_execution(self):
        fixture = self._fixture("strategy_pattern_classification")

        self.assertTrue(fixture["deterministic_gateway_required"])
        self.assertFalse(fixture["order_intent_allowed"])
        self.assertFalse(fixture["risk_approval_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_market_making_research_policy_cannot_publish_quotes(self):
        fixture = self._fixture("market_making_research_policy")

        self.assertFalse(fixture["inventory_rebalance_allowed"])
        self.assertFalse(fixture["quote_publication_allowed"])
        self.assertFalse(fixture["network_allowed"])
        self.assertFalse(fixture["credentials_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_liquidity_and_spread_contracts_are_research_only(self):
        liquidity = self._fixture("liquidity_quality_observation")
        spread = self._fixture("spread_risk_estimate")

        self.assertTrue(liquidity["observation_only"])
        self.assertFalse(liquidity["network_allowed"])
        self.assertFalse(liquidity["execution_allowed"])
        self.assertFalse(spread["risk_approval_allowed"])
        self.assertFalse(spread["execution_allowed"])

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
