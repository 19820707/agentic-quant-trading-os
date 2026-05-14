import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "contracts"

FIXTURES = {
    "order_intent.valid.json": ("trading", "order_intent"),
    "risk_decision.valid.json": ("trading", "risk_decision"),
    "approved_order.valid.json": ("trading", "approved_order"),
    "execution_report.valid.json": ("trading", "execution_report"),
    "audit_event.valid.json": ("audit", "audit_event"),
    "research_dossier.valid.json": ("research", "research_dossier"),
    "probability_estimate.valid.json": ("research", "probability_estimate"),
    "hypothesis_record.valid.json": ("research", "hypothesis_record"),
    "analyst_report.valid.json": ("research", "analyst_report"),
    "debate_transcript.valid.json": ("research", "debate_transcript"),
    "signal_candidate.valid.json": ("research", "signal_candidate"),
    "risk_review_input.valid.json": ("research", "risk_review_input"),
    "agent_orchestration_plan.valid.json": ("research", "agent_orchestration_plan"),
    "agent_role_assignment.valid.json": ("research", "agent_role_assignment"),
    "agent_handoff_record.valid.json": ("research", "agent_handoff_record"),
    "agent_consensus_record.valid.json": ("research", "agent_consensus_record"),
    "swarm_topology_policy.valid.json": ("research", "swarm_topology_policy"),
    "agent_federation_policy.valid.json": ("research", "agent_federation_policy"),
    "agent_memory_policy.valid.json": ("research", "agent_memory_policy"),
    "mcp_tool_registration_policy.valid.json": ("research", "mcp_tool_registration_policy"),
    "background_worker_policy.valid.json": ("research", "background_worker_policy"),
    "agent_cost_budget_policy.valid.json": ("research", "agent_cost_budget_policy"),
    "prompt_injection_review.valid.json": ("research", "prompt_injection_review"),
    "feature_store_approval_gate.valid.json": ("features", "feature_store_approval_gate"),
    "agent_task_spec.valid.json": ("governance", "agent_task_spec"),
    "agent_patch_plan.valid.json": ("governance", "agent_patch_plan"),
    "agent_risk_assessment.valid.json": ("governance", "agent_risk_assessment"),
    "sandbox_execution_report.valid.json": ("governance", "sandbox_execution_report"),
    "test_evidence_report.valid.json": ("governance", "test_evidence_report"),
    "rollback_plan.valid.json": ("governance", "rollback_plan"),
}

FORBIDDEN_KEYS = {
    "api_key",
    "password",
    "private_key",
    "broker_secret",
    "exchange_secret",
    "access_token",
    "refresh_token",
}


class ContractFixtureTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_all_contract_fixtures_validate(self):
        for fixture_name, (domain, schema_name) in FIXTURES.items():
            with self.subTest(fixture=fixture_name):
                payload = self._load_fixture(fixture_name)
                result = self.validator.validate(domain, schema_name, payload)
                self.assertTrue(result.valid, result.errors)

    def test_fixtures_are_paper_only_where_execution_context_exists(self):
        for fixture_name in FIXTURES:
            with self.subTest(fixture=fixture_name):
                payload = self._load_fixture(fixture_name)
                if "venue" in payload:
                    self.assertEqual(payload["venue"], "paper")
                if "execution_mode" in payload:
                    self.assertEqual(payload["execution_mode"], "PAPER")

    def test_fixtures_do_not_include_credentials_or_live_markers(self):
        for fixture_name in FIXTURES:
            with self.subTest(fixture=fixture_name):
                payload_text = (FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8").lower()
                for forbidden_key in FORBIDDEN_KEYS:
                    self.assertNotIn(forbidden_key, payload_text)
                self.assertNotIn("live", payload_text)

    def test_fixtures_share_lifecycle_correlation_id(self):
        correlation_ids = {
            self._load_fixture(fixture_name)["correlation_id"]
            for fixture_name in FIXTURES
        }

        self.assertEqual(
            correlation_ids,
            {
                "corr_fixture_lifecycle_001",
                "corr_research_contracts_001",
                "corr_feature_controls_001",
                "corr_agentic_governance_001",
            },
        )

    def test_research_fixtures_are_non_executable(self):
        for fixture_name, (domain, _) in FIXTURES.items():
            if domain != "research":
                continue
            with self.subTest(fixture=fixture_name):
                payload = self._load_fixture(fixture_name)
                if "execution_allowed" in payload:
                    self.assertFalse(payload["execution_allowed"])
                if "order_intent_allowed" in payload:
                    self.assertFalse(payload["order_intent_allowed"])
                if "risk_approval_allowed" in payload:
                    self.assertFalse(payload["risk_approval_allowed"])

    def _load_fixture(self, fixture_name):
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
