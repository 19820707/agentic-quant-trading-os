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
    "research_escalation_decision": {
        "fixture": "research_escalation_decision.valid.json",
        "primary_id": "research_escalation_decision_id",
        "enum_field": "decision",
        "invalid_enum": "AUTO_EXECUTE",
        "timestamp_field": "created_at",
    },
    "alpha_claim_review": {
        "fixture": "alpha_claim_review.valid.json",
        "primary_id": "alpha_claim_review_id",
        "enum_field": "support_level",
        "invalid_enum": "PRODUCTION_APPROVED",
        "timestamp_field": "reviewed_at",
    },
    "human_research_review_request": {
        "fixture": "human_research_review_request.valid.json",
        "primary_id": "human_research_review_request_id",
        "enum_field": "priority",
        "invalid_enum": "AUTO_APPROVE",
        "timestamp_field": "created_at",
    },
    "paper_to_production_gap_assessment": {
        "fixture": "paper_to_production_gap_assessment.valid.json",
        "primary_id": "paper_to_production_gap_assessment_id",
        "enum_field": "gap_severity",
        "invalid_enum": "READY",
        "timestamp_field": "assessed_at",
    },
    "news_freshness_assessment": {
        "fixture": "news_freshness_assessment.valid.json",
        "primary_id": "news_freshness_assessment_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "assessed_at",
    },
    "market_ambiguity_assessment": {
        "fixture": "market_ambiguity_assessment.valid.json",
        "primary_id": "market_ambiguity_assessment_id",
        "enum_field": "resolution_risk",
        "invalid_enum": "AUTO_RESOLVED",
        "timestamp_field": "assessed_at",
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

    def test_research_escalation_remains_local_and_non_executable(self):
        fixture = self._fixture("research_escalation_decision")

        self.assertFalse(fixture["network_allowed"])
        self.assertFalse(fixture["credentials_allowed"])
        self.assertFalse(fixture["execution_allowed"])
        self.assertEqual(fixture["decision"], "require_human_review")

    def test_alpha_claim_review_cannot_approve_production_or_execution(self):
        fixture = self._fixture("alpha_claim_review")

        self.assertFalse(fixture["production_approval_allowed"])
        self.assertFalse(fixture["risk_approval_allowed"])
        self.assertFalse(fixture["execution_allowed"])
        self.assertEqual(fixture["support_level"], "unsupported")

    def test_human_review_request_is_pending_not_approval(self):
        fixture = self._fixture("human_research_review_request")

        self.assertTrue(fixture["decision_pending"])
        self.assertFalse(fixture["execution_allowed"])

    def test_paper_to_production_gap_blocks_production(self):
        fixture = self._fixture("paper_to_production_gap_assessment")

        self.assertEqual(fixture["gap_severity"], "high")
        self.assertFalse(fixture["production_approval_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_news_freshness_assessment_is_local_only(self):
        fixture = self._fixture("news_freshness_assessment")

        self.assertTrue(fixture["is_stale"])
        self.assertFalse(fixture["network_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_market_ambiguity_requires_human_review_and_cannot_execute(self):
        fixture = self._fixture("market_ambiguity_assessment")

        self.assertTrue(fixture["human_review_required"])
        self.assertFalse(fixture["execution_allowed"])

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
