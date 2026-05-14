import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator
from packages.sdk.agentic_self_programming import (
    AgentPatchPlan,
    AgentPolicyDecision,
    AgentPolicyEngine,
    AgentPolicyError,
    AgentRiskLevel,
    AgentTask,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas" / "governance"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts"
POLICY_DOC = ROOT / "docs" / "architecture" / "agentic_self_programming_governance.md"

GOVERNANCE_CONTRACTS = {
    "agent_task_spec": "agent_task_spec.valid.json",
    "agent_patch_plan": "agent_patch_plan.valid.json",
    "agent_risk_assessment": "agent_risk_assessment.valid.json",
}

FALSE_BOUNDARY_FIELDS = (
    "direct_main_write_allowed",
    "apply_to_main_allowed",
    "auto_merge_allowed",
    "network_allowed",
    "credentials_allowed",
    "trading_changes_allowed",
    "risk_approval_allowed",
    "execution_allowed",
)


class AgenticSelfProgrammingGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.policy_engine = AgentPolicyEngine()

    def test_governance_schemas_are_closed(self):
        for name in GOVERNANCE_CONTRACTS:
            with self.subTest(schema=name):
                schema = self._schema(name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue(schema["$id"].endswith(f"/schemas/governance/{name}.schema.json"))

    def test_governance_fixtures_validate(self):
        for name in GOVERNANCE_CONTRACTS:
            with self.subTest(schema=name):
                result = self.validator.validate("governance", name, self._fixture(name))
                self.assertTrue(result.valid, result.errors)

    def test_governance_fixtures_keep_agent_authority_disabled(self):
        for name in GOVERNANCE_CONTRACTS:
            fixture = self._fixture(name)
            with self.subTest(schema=name):
                self.assertTrue(fixture.get("requires_human_review", fixture.get("human_review_required", True)))
                for field in FALSE_BOUNDARY_FIELDS:
                    if field in fixture:
                        self.assertFalse(fixture[field])

    def test_contracts_reject_direct_main_or_execution_enablement(self):
        for name in GOVERNANCE_CONTRACTS:
            for field in FALSE_BOUNDARY_FIELDS:
                fixture = self._fixture(name)
                if field not in fixture:
                    continue
                fixture[field] = True
                with self.subTest(schema=name, field=field):
                    result = self.validator.validate("governance", name, fixture)
                    self.assertFalse(result.valid)

    def test_policy_engine_allows_low_risk_pr_only_path(self):
        assessment = self.policy_engine.assess(
            AgentTask(
                task_id="task_001",
                requested_role="architecture_reviewer",
                task_type="documentation",
                summary="Update architecture documentation.",
                target_files=("docs/architecture/capability_maturity_matrix.md",),
            ),
            AgentPatchPlan(
                task_id="task_001",
                proposed_files=("docs/architecture/capability_maturity_matrix.md",),
                test_commands=("python scripts/scaffold_audit.py",),
                rollback_plan="Revert branch before merge.",
            ),
        )

        self.assertEqual(assessment.risk_level, AgentRiskLevel.LOW)
        self.assertEqual(assessment.policy_decision, AgentPolicyDecision.ALLOW_PR_ONLY)
        self.assertFalse(assessment.direct_main_write_allowed)
        self.assertFalse(assessment.auto_merge_allowed)
        self.assertFalse(assessment.execution_allowed)

    def test_policy_engine_requires_human_review_for_sdk_or_contract_paths(self):
        assessment = self.policy_engine.assess(
            AgentTask(
                task_id="task_002",
                requested_role="code_maintainer",
                task_type="runtime_scaffold",
                summary="Refine a local SDK scaffold.",
                target_files=("packages/sdk/agentic_self_programming.py",),
            ),
            AgentPatchPlan(
                task_id="task_002",
                proposed_files=("packages/sdk/agentic_self_programming.py",),
                test_commands=("python -m unittest discover -s tests",),
                rollback_plan="Revert branch before merge.",
            ),
        )

        self.assertEqual(assessment.risk_level, AgentRiskLevel.MEDIUM)
        self.assertEqual(assessment.policy_decision, AgentPolicyDecision.REQUIRE_HUMAN_REVIEW)

    def test_policy_engine_blocks_critical_paths(self):
        assessment = self.policy_engine.assess(
            AgentTask(
                task_id="task_003",
                requested_role="code_maintainer",
                task_type="runtime_scaffold",
                summary="Change order flow behavior.",
                target_files=("services/execution-engine/app/main.py",),
            ),
            AgentPatchPlan(
                task_id="task_003",
                proposed_files=("services/execution-engine/app/main.py",),
                test_commands=("python -m unittest discover -s tests",),
                rollback_plan="Revert branch before merge.",
            ),
        )

        self.assertEqual(assessment.risk_level, AgentRiskLevel.CRITICAL)
        self.assertEqual(assessment.policy_decision, AgentPolicyDecision.BLOCK)
        self.assertTrue(any("critical" in finding for finding in assessment.findings))

    def test_policy_engine_blocks_sensitive_capability_markers(self):
        assessment = self.policy_engine.assess(
            AgentTask(
                task_id="task_004",
                requested_role="code_maintainer",
                task_type="runtime_scaffold",
                summary="Add submit_order behavior.",
                target_files=("packages/sdk/example.py",),
            ),
            AgentPatchPlan(
                task_id="task_004",
                proposed_files=("packages/sdk/example.py",),
                test_commands=("python -m unittest discover -s tests",),
                rollback_plan="Revert branch before merge.",
            ),
        )

        self.assertEqual(assessment.policy_decision, AgentPolicyDecision.BLOCK)

    def test_policy_engine_blocks_missing_evidence_or_mismatched_task(self):
        mismatched = self.policy_engine.assess(
            AgentTask(
                task_id="task_005",
                requested_role="test_runner",
                task_type="test",
                summary="Add tests.",
                target_files=("tests/test_example.py",),
            ),
            AgentPatchPlan(
                task_id="other_task",
                proposed_files=("tests/test_example.py",),
                test_commands=("python -m unittest discover -s tests",),
                rollback_plan="Revert branch before merge.",
            ),
        )
        self.assertEqual(mismatched.policy_decision, AgentPolicyDecision.BLOCK)

        missing_tests = self.policy_engine.assess(
            AgentTask(
                task_id="task_006",
                requested_role="test_runner",
                task_type="test",
                summary="Add tests.",
                target_files=("tests/test_example.py",),
            ),
            AgentPatchPlan(
                task_id="task_006",
                proposed_files=("tests/test_example.py",),
                test_commands=(),
                rollback_plan="Revert branch before merge.",
            ),
        )
        self.assertEqual(missing_tests.policy_decision, AgentPolicyDecision.BLOCK)

    def test_pr_only_guard_rejects_human_review_or_blocked_assessments(self):
        assessment = self.policy_engine.assess(
            AgentTask(
                task_id="task_007",
                requested_role="code_maintainer",
                task_type="runtime_scaffold",
                summary="Refine local SDK.",
                target_files=("packages/sdk/example.py",),
            ),
            AgentPatchPlan(
                task_id="task_007",
                proposed_files=("packages/sdk/example.py",),
                test_commands=("python -m unittest discover -s tests",),
                rollback_plan="Revert branch before merge.",
            ),
        )

        with self.assertRaises(AgentPolicyError):
            self.policy_engine.ensure_pr_only_allowed(assessment)

    def test_policy_engine_contract_payload_never_grants_runtime_authority(self):
        assessment = self.policy_engine.assess(
            AgentTask(
                task_id="task_008",
                requested_role="architecture_reviewer",
                task_type="documentation",
                summary="Update docs.",
                target_files=("docs/architecture/example.md",),
            ),
            AgentPatchPlan(
                task_id="task_008",
                proposed_files=("docs/architecture/example.md",),
                test_commands=("python scripts/scaffold_audit.py",),
                rollback_plan="Revert branch before merge.",
            ),
        )
        payload = assessment.to_contract_payload()

        for field in FALSE_BOUNDARY_FIELDS:
            if field in payload:
                self.assertFalse(payload[field])

    def test_policy_doc_states_no_real_agent_runtime(self):
        text = POLICY_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("does not approve autonomous runtime", text)
        self.assertIn("no real llm agent runtime", text)
        self.assertIn("no github token integration", text)
        self.assertIn("no auto-merge", text)
        self.assertIn("no trading logic", text)

    def _schema(self, name):
        with (SCHEMA_ROOT / f"{name}.schema.json").open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self, name):
        fixture_name = GOVERNANCE_CONTRACTS[name]
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
