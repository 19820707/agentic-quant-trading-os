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
    "agent_orchestration_plan": {
        "fixture": "agent_orchestration_plan.valid.json",
        "primary_id": "agent_orchestration_plan_id",
        "enum_field": "coordination_mode",
        "invalid_enum": "AUTO_RUN",
        "timestamp_field": "created_at",
    },
    "agent_role_assignment": {
        "fixture": "agent_role_assignment.valid.json",
        "primary_id": "agent_role_assignment_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "assigned_at",
    },
    "agent_handoff_record": {
        "fixture": "agent_handoff_record.valid.json",
        "primary_id": "agent_handoff_record_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "agent_consensus_record": {
        "fixture": "agent_consensus_record.valid.json",
        "primary_id": "agent_consensus_record_id",
        "enum_field": "consensus_state",
        "invalid_enum": "APPROVE_TRADE",
        "timestamp_field": "created_at",
    },
    "swarm_topology_policy": {
        "fixture": "swarm_topology_policy.valid.json",
        "primary_id": "swarm_topology_policy_id",
        "enum_field": "allowed_topology",
        "invalid_enum": "AUTO_SWARM",
        "timestamp_field": "created_at",
    },
    "agent_federation_policy": {
        "fixture": "agent_federation_policy.valid.json",
        "primary_id": "agent_federation_policy_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "agent_memory_policy": {
        "fixture": "agent_memory_policy.valid.json",
        "primary_id": "agent_memory_policy_id",
        "enum_field": "memory_scope",
        "invalid_enum": "REMOTE_VECTOR_DB",
        "timestamp_field": "created_at",
    },
    "mcp_tool_registration_policy": {
        "fixture": "mcp_tool_registration_policy.valid.json",
        "primary_id": "mcp_tool_registration_policy_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "background_worker_policy": {
        "fixture": "background_worker_policy.valid.json",
        "primary_id": "background_worker_policy_id",
        "enum_field": None,
        "invalid_enum": None,
        "timestamp_field": "created_at",
    },
    "agent_cost_budget_policy": {
        "fixture": "agent_cost_budget_policy.valid.json",
        "primary_id": "agent_cost_budget_policy_id",
        "enum_field": "budget_breach_behavior",
        "invalid_enum": "KEEP_RUNNING",
        "timestamp_field": "created_at",
    },
    "prompt_injection_review": {
        "fixture": "prompt_injection_review.valid.json",
        "primary_id": "prompt_injection_review_id",
        "enum_field": "finding_level",
        "invalid_enum": "IGNORE",
        "timestamp_field": "reviewed_at",
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

    def test_agent_orchestration_contracts_do_not_execute(self):
        for name in (
            "agent_orchestration_plan",
            "agent_role_assignment",
            "agent_handoff_record",
            "agent_consensus_record",
        ):
            with self.subTest(schema=name):
                fixture = self._fixture(name)
                self.assertFalse(fixture["execution_allowed"])
                if "autonomous_execution_allowed" in fixture:
                    self.assertFalse(fixture["autonomous_execution_allowed"])
                if "risk_approval_allowed" in fixture:
                    self.assertFalse(fixture["risk_approval_allowed"])

    def test_swarm_and_federation_are_disabled(self):
        swarm = self._fixture("swarm_topology_policy")
        federation = self._fixture("agent_federation_policy")

        self.assertFalse(swarm["federation_allowed"])
        self.assertFalse(swarm["autonomous_loop_allowed"])
        self.assertFalse(swarm["network_allowed"])
        self.assertFalse(swarm["execution_allowed"])
        self.assertFalse(federation["cross_machine_allowed"])
        self.assertFalse(federation["remote_agent_allowed"])
        self.assertFalse(federation["credentials_allowed"])
        self.assertFalse(federation["network_allowed"])
        self.assertFalse(federation["execution_allowed"])

    def test_memory_mcp_and_workers_are_fail_closed(self):
        memory = self._fixture("agent_memory_policy")
        mcp = self._fixture("mcp_tool_registration_policy")
        worker = self._fixture("background_worker_policy")

        self.assertFalse(memory["secret_storage_allowed"])
        self.assertFalse(memory["credential_storage_allowed"])
        self.assertFalse(memory["external_memory_allowed"])
        self.assertFalse(memory["execution_allowed"])
        self.assertFalse(mcp["registration_allowed"])
        self.assertFalse(mcp["broker_credentials_allowed"])
        self.assertFalse(mcp["trading_allowed"])
        self.assertFalse(mcp["execution_allowed"])
        self.assertFalse(worker["schedule_allowed"])
        self.assertFalse(worker["autonomous_execution_allowed"])
        self.assertFalse(worker["execution_allowed"])

    def test_budget_and_prompt_defence_are_research_only(self):
        budget = self._fixture("agent_cost_budget_policy")
        prompt_review = self._fixture("prompt_injection_review")

        self.assertEqual(budget["budget_breach_behavior"], "fail_closed")
        self.assertFalse(budget["autonomous_spend_allowed"])
        self.assertFalse(budget["execution_allowed"])
        self.assertTrue(prompt_review["sanitization_required"])
        self.assertTrue(prompt_review["tool_call_blocked"])
        self.assertFalse(prompt_review["credential_exposure_detected"])
        self.assertFalse(prompt_review["execution_allowed"])

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
