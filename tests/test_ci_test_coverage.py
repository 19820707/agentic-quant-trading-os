"""Guard that every test module is executed by the CI workflow.

CI lists test files one by one, so a new test file that is not added to the
workflow would silently never run. This guard fails until it is listed.
"""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

# Test modules that are not listed one by one, with the reason. Keep this short.
EXCLUDED_FROM_CI = {
    "test_service_placeholders.py": "imports FastAPI; it runs in the full-suite job, which installs it",
}


class CiTestCoverageTests(unittest.TestCase):
    def test_every_test_module_is_listed_in_ci_or_explicitly_excluded(self):
        workflow_text = CI_WORKFLOW.read_text(encoding="utf-8")
        test_modules = sorted(path.name for path in (ROOT / "tests").glob("test_*.py"))

        missing = [
            name
            for name in test_modules
            if f'"{name}"' not in workflow_text and name not in EXCLUDED_FROM_CI
        ]

        self.assertEqual(missing, [], f"test modules not run by CI: {missing}")

    def test_exclusions_refer_to_existing_unlisted_modules(self):
        workflow_text = CI_WORKFLOW.read_text(encoding="utf-8")

        for name, reason in EXCLUDED_FROM_CI.items():
            with self.subTest(name=name):
                self.assertTrue((ROOT / "tests" / name).is_file())
                self.assertTrue(reason.strip())
                self.assertNotIn(f'"{name}"', workflow_text)

    def test_ci_references_only_existing_test_modules(self):
        workflow_text = CI_WORKFLOW.read_text(encoding="utf-8")
        referenced = {
            token.strip('"')
            for token in workflow_text.split()
            if token.startswith('"test_') and token.endswith('.py"') and "*" not in token
        }

        for name in sorted(referenced):
            with self.subTest(name=name):
                self.assertTrue((ROOT / "tests" / name).is_file())

    def test_full_suite_job_runs_every_test_module_with_declared_dependencies(self):
        workflow_text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("full-suite:", workflow_text)
        self.assertIn("tomllib", workflow_text)
        self.assertIn("['project']['dependencies']", workflow_text)
        self.assertIn('python -m unittest discover -s tests -p "test_*.py"', workflow_text)
        # Dependencies come only from pyproject.toml; no package is named in CI.
        self.assertNotRegex(workflow_text, r"pip install [A-Za-z]")


if __name__ == "__main__":
    unittest.main()
