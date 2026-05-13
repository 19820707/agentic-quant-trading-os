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
    "agent_skill_definition": {
        "fixture": "agent_skill_definition.valid.json",
        "primary_id": "agent_skill_definition_id",
        "enum_field": "skill_category",
        "invalid_enum": "EXECUTOR",
        "timestamp_field": "created_at",
    },
    "skill_dependency_declaration": {
        "fixture": "skill_dependency_declaration.valid.json",
        "primary_id": "skill_dependency_declaration_id",
        "enum_field": "missing_tool_behavior",
        "invalid_enum": "AUTO_ENABLE",
        "timestamp_field": "declared_at",
    },
    "agent_tool_permission_policy": {
        "fixture": "agent_tool_permission_policy.valid.json",
        "primary_id": "agent_tool_permission_policy_id",
        "enum_field": "risk_level",
        "invalid_enum": "APPROVED",
        "timestamp_field": "created_at",
    },
    "tool_risk_classification": {
        "fixture": "tool_risk_classification.valid.json",
        "primary_id": "tool_risk_classification_id",
        "enum_field": "tool_category",
        "invalid_enum": "BROKER_EXECUTION",
        "timestamp_field": "classified_at",
    },
    "tool_call_audit_record": {
        "fixture": "tool_call_audit_record.valid.json",
        "primary_id": "tool_call_audit_record_id",
        "enum_field": "policy_decision",
        "invalid_enum": "EXECUTE",
        "timestamp_field": "recorded_at",
    },
    "agent_loop_guard": {
        "fixture": "agent_loop_guard.valid.json",
        "primary_id": "agent_loop_guard_id",
        "enum_field": "termination_behavior",
        "invalid_enum": "CONTINUE_FOREVER",
        "timestamp_field": "created_at",
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

    def test_agent_skill_definition_is_disabled_by_default(self):
        fixture = self._fixture("agent_skill_definition")

        self.assertFalse(fixture["enabled_by_default"])
        self.assertFalse(fixture["tool_use_allowed"])
        self.assertFalse(fixture["network_allowed"])
        self.assertFalse(fixture["credentials_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_skill_dependency_declaration_does_not_activate_tools(self):
        fixture = self._fixture("skill_dependency_declaration")

        self.assertTrue(fixture["dependency_validation_required"])
        self.assertFalse(fixture["tool_activation_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_agent_tool_policy_blocks_operational_authority(self):
        fixture = self._fixture("agent_tool_permission_policy")

        self.assertFalse(fixture["shell_allowed"])
        self.assertFalse(fixture["file_write_allowed"])
        self.assertFalse(fixture["network_allowed"])
        self.assertFalse(fixture["credentials_allowed"])
        self.assertFalse(fixture["trading_allowed"])
        self.assertFalse(fixture["risk_approval_allowed"])
        self.assertFalse(fixture["execution_allowed"])

    def test_tool_risk_and_audit_records_remain_non_executable(self):
        classification = self._fixture("tool_risk_classification")
        audit = self._fixture("tool_call_audit_record")

        self.assertTrue(classification["manual_approval_required"])
        self.assertFalse(classification["runtime_activation_allowed"])
        self.assertFalse(classification["execution_allowed"])
        self.assertTrue(audit["redaction_applied"])
        self.assertFalse(audit["sensitive_payload_allowed"])
        self.assertFalse(audit["execution_allowed"])

    def test_agent_loop_guard_fails_closed(self):
        fixture = self._fixture("agent_loop_guard")

        self.assertEqual(fixture["termination_behavior"], "fail_closed")
        self.assertTrue(fixture["hallucination_review_required"])
        self.assertFalse(fixture["autonomous_action_allowed"])
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
