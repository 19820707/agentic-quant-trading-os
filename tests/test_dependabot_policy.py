"""Dependabot is approved for GitHub Actions version updates only."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
POLICY = ROOT / "docs" / "security" / "security_tooling_integration_policy.md"


class DependabotPolicyTests(unittest.TestCase):
    def setUp(self):
        self.text = DEPENDABOT.read_text(encoding="utf-8")

    def test_only_the_github_actions_ecosystem_is_configured(self):
        ecosystems = [
            line.split(":", 1)[1].strip().strip('"')
            for line in self.text.splitlines()
            if line.strip().startswith("- package-ecosystem:")
        ]

        self.assertEqual(ecosystems, ["github-actions"])

    def test_updates_are_scheduled_bounded_and_not_auto_merged(self):
        self.assertIn('interval: "weekly"', self.text)
        self.assertIn("open-pull-requests-limit:", self.text)
        settings = "\n".join(line for line in self.text.splitlines() if not line.lstrip().startswith("#"))
        self.assertNotIn("merge", settings.lower())

    def test_configuration_needs_no_secrets_or_registries(self):
        for fragment in ("registries:", "token", "password", "secrets."):
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.text)

    def test_policy_document_records_the_approval_and_its_scope(self):
        policy = POLICY.read_text(encoding="utf-8")

        self.assertIn("Dependabot version updates are approved for the `github-actions` ecosystem only", policy)
        self.assertIn("requires a separate approval PR", policy)


if __name__ == "__main__":
    unittest.main()
