import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_ROOT = ROOT / "apps" / "control-plane-dashboard"
INDEX = DASHBOARD_ROOT / "index.html"
STYLES = DASHBOARD_ROOT / "styles.css"
README = DASHBOARD_ROOT / "README.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


class ControlPlaneDashboardScaffoldTests(unittest.TestCase):
    def test_dashboard_static_files_exist(self):
        self.assertTrue(INDEX.is_file())
        self.assertTrue(STYLES.is_file())
        self.assertTrue(README.is_file())

    def test_dashboard_declares_control_plane_sections(self):
        text = INDEX.read_text(encoding="utf-8")

        for section in (
            "System Status",
            "Security Gates",
            "Contract Registry",
            "Risk Gateway Status",
            "Data Lineage Gates",
            "Feature Gates",
            "Recent PR Readiness",
            "Roadmap",
        ):
            with self.subTest(section=section):
                self.assertIn(section, text)

    def test_dashboard_is_static_and_local_only(self):
        text = INDEX.read_text(encoding="utf-8").lower()
        readme = README.read_text(encoding="utf-8").lower()

        forbidden_fragments = (
            "http://",
            "https://",
            "fetch(",
            "websocket",
            "localstorage",
            "apikey",
            "api_key",
            "broker",
            "exchange access",
            "submit_order",
            "create_order",
            "cancel_order",
            "withdraw",
            "transfer",
        )

        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, text)

        self.assertIn("no api calls", readme)
        self.assertIn("no external network access", readme)
        self.assertIn("no credentials", readme)
        self.assertIn("no trading actions", readme)

    def test_dashboard_documents_future_frontend_dependency_gate(self):
        readme = README.read_text(encoding="utf-8").lower()

        self.assertIn("future react/vite/typescript implementation requires a separate approval pr", readme)

    def test_ci_runs_dashboard_scaffold_tests(self):
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_control_plane_dashboard_scaffold.py", text)


if __name__ == "__main__":
    unittest.main()
