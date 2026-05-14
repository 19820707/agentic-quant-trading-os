import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_ROOT = ROOT / "apps" / "control-plane-dashboard"
INDEX = DASHBOARD_ROOT / "index.html"
STYLES = DASHBOARD_ROOT / "styles.css"
README = DASHBOARD_ROOT / "README.md"
CONTRACT_REGISTRY = DASHBOARD_ROOT / "contract-registry.json"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


class ControlPlaneDashboardScaffoldTests(unittest.TestCase):
    def test_dashboard_static_files_exist(self):
        self.assertTrue(INDEX.is_file())
        self.assertTrue(STYLES.is_file())
        self.assertTrue(README.is_file())
        self.assertTrue(CONTRACT_REGISTRY.is_file())

    def test_dashboard_declares_control_plane_sections(self):
        text = INDEX.read_text(encoding="utf-8")

        for section in (
            "System Status",
            "Security Gates",
            "Contract Registry",
            "Static Contract Browser",
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

    def test_static_contract_browser_lists_core_contracts(self):
        text = INDEX.read_text(encoding="utf-8")

        for contract_name in (
            "AuditEvent",
            "FeatureStoreApprovalGate",
            "AgentTaskSpec",
            "AgentPatchPlan",
            "AgentRiskAssessment",
            "SandboxExecutionReport",
            "TestEvidenceReport",
            "RollbackPlan",
            "AgentPRReviewEvidence",
            "HumanApprovalRecord",
            "ResearchDossier",
            "ProbabilityEstimate",
            "SignalCandidate",
            "OrderIntent",
            "RiskDecision",
        ):
            with self.subTest(contract_name=contract_name):
                self.assertIn(contract_name, text)

    def test_static_contract_registry_manifest_is_local_only(self):
        import json

        manifest = json.loads(CONTRACT_REGISTRY.read_text(encoding="utf-8"))
        manifest_text = CONTRACT_REGISTRY.read_text(encoding="utf-8").lower()

        self.assertEqual(manifest["runtime_mode"], "local_static_only")
        self.assertFalse(manifest["network_required"])
        self.assertFalse(manifest["credentials_required"])
        self.assertNotIn("http://", manifest_text)
        self.assertNotIn("https://", manifest_text)
        self.assertNotIn("fetch(", manifest_text)

        domains = {domain["domain"] for domain in manifest["domains"]}
        self.assertEqual(domains, {"audit", "features", "governance", "research", "trading"})

    def test_ci_runs_dashboard_scaffold_tests(self):
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_control_plane_dashboard_scaffold.py", text)


if __name__ == "__main__":
    unittest.main()
