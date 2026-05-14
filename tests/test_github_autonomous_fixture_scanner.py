import json
import unittest
from pathlib import Path

from packages.sdk.github_autonomous_fixture_scanner import (
    AutonomousCredentialBlocked,
    FixtureDrivenAutonomousMaintenanceScanner,
    FixtureScannerError,
    LocalWorkflowFixtureScanner,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "github_autonomous_maintenance"


class GitHubAutonomousFixtureScannerTests(unittest.TestCase):
    def test_loads_local_workflow_fixture(self):
        fixture = LocalWorkflowFixtureScanner().load(FIXTURE_ROOT / "workflow_run_failure.json")

        self.assertEqual(fixture.repository, "19820707/agentic-quant-trading-os")
        self.assertEqual(fixture.workflow_name, "CI Quality Gates")
        self.assertEqual(fixture.failed_check_summaries, ("Contract tests: test_contract_validator.py failed",))

    def test_fixture_driven_scanner_creates_evidence_without_writes(self):
        records = FixtureDrivenAutonomousMaintenanceScanner().run([FIXTURE_ROOT / "workflow_run_failure.json"])

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].repository, "19820707/agentic-quant-trading-os")
        self.assertFalse(records[0].repository_write_performed)
        self.assertFalse(records[0].auto_merge_performed)
        self.assertIn("Contract tests: test_contract_validator.py failed", records[0].evidence_items)

    def test_sensitive_fixture_is_blocked_by_policy_engine(self):
        scanner = FixtureDrivenAutonomousMaintenanceScanner()

        records = scanner.run([FIXTURE_ROOT / "workflow_run_security_blocked.json"])

        self.assertEqual(len(records), 1)
        self.assertFalse(records[0].repository_write_performed)
        self.assertFalse(records[0].auto_merge_performed)
        self.assertIn("Artifact hygiene audit: execution path changed in protected area", records[0].evidence_items)

    def test_fixture_missing_required_fields_fails_closed(self):
        scanner = LocalWorkflowFixtureScanner()

        with self.assertRaises(FixtureScannerError):
            scanner._parse({"repository": "19820707/agentic-quant-trading-os"})

    def test_fixture_with_credential_like_value_is_rejected(self):
        scanner = LocalWorkflowFixtureScanner()
        payload = {
            "repository": "19820707/token-repo",
            "workflow_name": "CI Quality Gates",
            "event": "pull_request",
            "head_branch": "codex/example",
            "checks": [],
        }

        with self.assertRaises(AutonomousCredentialBlocked):
            scanner._parse(payload)

    def test_scanner_does_not_import_network_or_process_modules(self):
        import packages.sdk.github_autonomous_fixture_scanner as module

        forbidden = {"requests", "urllib", "httpx", "socket", "subprocess", "github", "octokit"}

        self.assertTrue(forbidden.isdisjoint(set(module.__dict__)))

    def test_fixture_json_files_remain_parseable_and_local_only(self):
        for fixture_path in FIXTURE_ROOT.glob("*.json"):
            with self.subTest(fixture=fixture_path.name):
                payload = json.loads(fixture_path.read_text(encoding="utf-8"))
                self.assertEqual(payload["repository"], "19820707/agentic-quant-trading-os")
                self.assertNotIn("token", fixture_path.read_text(encoding="utf-8").lower())
                self.assertNotIn("secret", fixture_path.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
