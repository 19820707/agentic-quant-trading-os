import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas" / "governance"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts"
POLICY_DOC = ROOT / "docs" / "architecture" / "agent_pr_review_and_human_approval.md"

REVIEW_CONTRACTS = {
    "agent_pr_review_evidence": "agent_pr_review_evidence.valid.json",
    "human_approval_record": "human_approval_record.valid.json",
}

FALSE_FIELDS = (
    "auto_merge_allowed",
    "direct_main_write_allowed",
    "network_allowed",
    "credentials_allowed",
    "trading_changes_allowed",
    "risk_approval_allowed",
    "execution_allowed",
    "production_allowed",
)


class AgentPRReviewHumanApprovalContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_review_schemas_are_closed(self):
        for name in REVIEW_CONTRACTS:
            with self.subTest(schema=name):
                schema = self._schema(name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue(schema["$id"].endswith(f"/schemas/governance/{name}.schema.json"))

    def test_review_fixtures_validate(self):
        for name in REVIEW_CONTRACTS:
            with self.subTest(schema=name):
                result = self.validator.validate("governance", name, self._fixture(name))
                self.assertTrue(result.valid, result.errors)

    def test_review_fixtures_keep_authority_disabled(self):
        for name in REVIEW_CONTRACTS:
            fixture = self._fixture(name)
            with self.subTest(schema=name):
                for field in FALSE_FIELDS:
                    self.assertFalse(fixture[field])

    def test_review_evidence_links_prior_evidence_chain(self):
        fixture = self._fixture("agent_pr_review_evidence")

        self.assertRegex(fixture["agent_patch_plan_id"], r"^app_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["agent_risk_assessment_id"], r"^ara_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["test_evidence_report_id"], r"^ter_[A-Za-z0-9_\-]+$")
        self.assertRegex(fixture["rollback_plan_id"], r"^rbp_[A-Za-z0-9_\-]+$")
        self.assertTrue(fixture["human_review_required"])
        self.assertTrue(fixture["security_boundary_verified"])

    def test_human_approval_record_is_review_scope_only(self):
        fixture = self._fixture("human_approval_record")

        self.assertEqual(fixture["approval_status"], "approved_for_manual_review_only")
        self.assertEqual(fixture["approval_scope"], "pull_request_review_only")
        self.assertTrue(fixture["manual_merge_review_required"])

    def test_enabling_auto_merge_or_runtime_authority_is_rejected(self):
        for schema_name in REVIEW_CONTRACTS:
            for field in FALSE_FIELDS:
                fixture = self._fixture(schema_name)
                fixture[field] = True
                with self.subTest(schema=schema_name, field=field):
                    result = self.validator.validate("governance", schema_name, fixture)
                    self.assertFalse(result.valid)

    def test_policy_doc_states_no_runtime_or_auto_merge(self):
        text = POLICY_DOC.read_text(encoding="utf-8").lower()

        self.assertIn("does not approve autonomous merge", text)
        self.assertIn("no real pr bot", text)
        self.assertIn("no github token", text)
        self.assertIn("no auto-merge", text)
        self.assertIn("no trading logic", text)

    def test_review_and_human_record_share_correlation_id(self):
        review = self._fixture("agent_pr_review_evidence")
        human = self._fixture("human_approval_record")

        self.assertEqual(review["correlation_id"], "corr_agentic_governance_001")
        self.assertEqual(human["correlation_id"], review["correlation_id"])
        self.assertEqual(human["agent_pr_review_evidence_id"], review["agent_pr_review_evidence_id"])

    def _schema(self, name):
        with (SCHEMA_ROOT / f"{name}.schema.json").open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self, name):
        fixture_name = REVIEW_CONTRACTS[name]
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
