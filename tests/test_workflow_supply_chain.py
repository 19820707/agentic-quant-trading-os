"""Supply-chain and least-privilege checks for GitHub Actions workflows.

A version tag such as ``@v4`` can be moved to different code by whoever controls
the action repository. Pinning to a full commit hash makes the code that runs in
CI immutable and reviewable.
"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))

USES_LINE = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<reference>\S+)(?P<trailer>.*)$")
PINNED_REFERENCE = re.compile(r"^[\w.\-]+/[\w.\-/]+@[0-9a-f]{40}$")
VERSION_COMMENT = re.compile(r"^\s+#\s+v\d+(\.\d+){0,2}\s*$")


def _uses_lines(text: str) -> list[tuple[str, str]]:
    found = []
    for line in text.splitlines():
        match = USES_LINE.match(line)
        if match:
            found.append((match.group("reference"), match.group("trailer")))
    return found


class WorkflowSupplyChainTests(unittest.TestCase):
    def test_workflows_exist(self):
        self.assertGreaterEqual(len(WORKFLOWS), 2)

    def test_every_action_is_pinned_to_a_full_commit_hash_with_a_version_comment(self):
        for workflow in WORKFLOWS:
            uses = _uses_lines(workflow.read_text(encoding="utf-8"))
            self.assertTrue(uses, f"{workflow.name} uses no actions")
            for reference, trailer in uses:
                with self.subTest(workflow=workflow.name, reference=reference):
                    self.assertRegex(reference, PINNED_REFERENCE)
                    self.assertRegex(trailer, VERSION_COMMENT)

    def test_workflows_declare_explicit_token_permissions(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding="utf-8")
                self.assertRegex(text, r"(?m)^permissions:\s*$")
                self.assertNotIn("write-all", text)
                self.assertNotRegex(text, r"(?m)^\s*contents:\s*write\s*$")

    def test_workflows_do_not_run_untrusted_code_with_repository_privileges(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding="utf-8")
                self.assertNotIn("pull_request_target", text)
                self.assertNotIn("secrets.", text)

    def test_every_job_has_a_timeout(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = workflow.read_text(encoding="utf-8")
                jobs = len(re.findall(r"(?m)^    runs-on:", text))
                timeouts = len(re.findall(r"(?m)^    timeout-minutes:", text))
                self.assertGreater(jobs, 0)
                self.assertEqual(jobs, timeouts)

    def test_pinning_check_rejects_tag_and_branch_references(self):
        for reference in ("actions/checkout@v4", "actions/checkout@main", "actions/checkout@11d5960"):
            with self.subTest(reference=reference):
                self.assertNotRegex(reference, PINNED_REFERENCE)


if __name__ == "__main__":
    unittest.main()
