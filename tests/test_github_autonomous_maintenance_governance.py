import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts" / "governance"
REFERENCE_REVIEW = ROOT / "docs" / "integrations" / "github_autonomous_maintenance_reference_review.md"
GOVERNANCE_DOC = ROOT / "docs" / "architecture" / "github_autonomous_maintenance_governance.md"


class GitHubAutonomousMaintenanceGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.monitor = self._fixture("repository_monitor_policy.valid.json")
        self.finding = self._fixture("maintenance_finding_record.valid.json")
        self.plan = self._fixture("patch_plan_record.valid.json")
        self.decision = self._fixture("autonomous_change_policy_decision.valid.json")
        self.evidence = self._fixture("maintenance_evidence_record.valid.json")

    def test_repository_monitor_policy_validates(self):
        result = self.validator.validate("governance", "repository_monitor_policy", self.monitor)

        self.assertTrue(result.valid, result.errors)

    def test_maintenance_finding_record_validates(self):
        result = self.validator.validate("governance", "maintenance_finding_record", self.finding)

        self.assertTrue(result.valid, result.errors)

    def test_patch_plan_record_validates(self):
        result = self.validator.validate("governance", "patch_plan_record", self.plan)

        self.assertTrue(result.valid, result.errors)

    def test_autonomous_change_policy_decision_validates(self):
        result = self.validator.validate("governance", "autonomous_change_policy_decision", self.decision)

        self.assertTrue(result.valid, result.errors)

    def test_maintenance_evidence_record_validates(self):
        result = self.validator.validate("governance", "maintenance_evidence_record", self.evidence)

        self.assertTrue(result.valid, result.errors)

    def test_monitor_policy_is_reference_only_and_read_only(self):
        self.assertFalse(self.monitor["github_app_enabled"])
        self.assertFalse(self.monitor["webhook_receiver_enabled"])
        self.assertFalse(self.monitor["repository_write_allowed"])
        self.assertFalse(self.monitor["auto_pr_allowed"])
        self.assertFalse(self.monitor["auto_merge_allowed"])
        self.assertFalse(self.monitor["network_access_allowed"])
        self.assertFalse(self.monitor["credentials_allowed"])
        self.assertFalse(self.monitor["production_enabled"])

    def test_patch_plan_blocks_branch_commit_pr_and_merge(self):
        self.assertTrue(self.plan["sandbox_required"])
        self.assertFalse(self.plan["branch_creation_allowed"])
        self.assertFalse(self.plan["commit_allowed"])
        self.assertFalse(self.plan["pull_request_allowed"])
        self.assertFalse(self.plan["auto_merge_allowed"])
        self.assertFalse(self.plan["touches_trading_or_execution"])
        self.assertFalse(self.plan["credentials_allowed"])

    def test_policy_decision_requires_human_review_and_blocks_writes(self):
        self.assertEqual(self.decision["decision"], "REQUIRE_HUMAN_REVIEW")
        self.assertTrue(self.decision["human_review_required"])
        self.assertFalse(self.decision["repository_write_allowed"])
        self.assertFalse(self.decision["branch_creation_allowed"])
        self.assertFalse(self.decision["pull_request_allowed"])
        self.assertFalse(self.decision["auto_merge_allowed"])
        self.assertFalse(self.decision["credentials_allowed"])
        self.assertFalse(self.decision["production_enabled"])

    def test_evidence_record_proves_no_write_or_auto_merge(self):
        self.assertTrue(self.evidence["audit_required"])
        self.assertTrue(self.evidence["rollback_required"])
        self.assertFalse(self.evidence["contains_credentials"])
        self.assertFalse(self.evidence["repository_write_performed"])
        self.assertFalse(self.evidence["auto_merge_performed"])

    def test_repository_write_enablement_is_rejected(self):
        payload = copy.deepcopy(self.monitor)
        payload["repository_write_allowed"] = True

        result = self.validator.validate("governance", "repository_monitor_policy", payload)

        self.assertFalse(result.valid)

    def test_auto_merge_enablement_is_rejected(self):
        payload = copy.deepcopy(self.decision)
        payload["auto_merge_allowed"] = True

        result = self.validator.validate("governance", "autonomous_change_policy_decision", payload)

        self.assertFalse(result.valid)

    def test_reference_review_documents_sources_and_blocks_runtime(self):
        text = REFERENCE_REVIEW.read_text(encoding="utf-8").lower()

        for source in ("dependabot", "copilot", "pr-agent", "probot", "octokit", "semgrep", "trivy"):
            with self.subTest(source=source):
                self.assertIn(source, text)

        for flag in (
            "reference_only: true",
            "dependency_allowed: false",
            "github_app_allowed: false",
            "repository_write_allowed: false",
            "auto_pr_allowed: false",
            "auto_merge_allowed: false",
            "credentials_allowed: false",
        ):
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_governance_doc_defines_required_blocks_and_boundaries(self):
        text = GOVERNANCE_DOC.read_text(encoding="utf-8").lower()

        for phrase in (
            "repository discovery",
            "webhook receiver",
            "finding engine",
            "patch planner",
            "policy engine",
            "sandbox patch runner",
            "evidence index",
            "audit log",
            "must never",
            "write directly to `main`",
            "auto-merge",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def _fixture(self, name):
        with (FIXTURE_ROOT / name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
