from pathlib import Path
import unittest


REVIEW_PATH = Path("docs/integrations/polymarket_skills_reference_review.md")
TAXONOMY_PATH = Path("docs/architecture/agentic_tool_safety_taxonomy.md")
PYPROJECT = Path("pyproject.toml")
CI_WORKFLOW = Path(".github/workflows/ci.yml")


class PolymarketSkillsReferenceReviewTests(unittest.TestCase):
    def test_review_document_exists(self) -> None:
        self.assertTrue(REVIEW_PATH.is_file())

    def test_review_keeps_skills_reference_only(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "direct_skill_install_allowed: false",
            "npx_install_allowed: false",
            "manual_skill_copy_allowed: false",
            "py_clob_client_allowed: false",
            "runtime_enabled: false",
            "production_enabled: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "wallet_access_allowed: false",
            "live_executor_allowed: false",
            "agent_execution_authority_allowed: false",
            "trading_methods_allowed: false",
        ):
            self.assertIn(phrase, text)

    def test_review_extracts_safe_patterns(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "skill risk taxonomy",
            "agentic trading constitution pattern",
            "market metadata prompt-injection boundary",
            "paper trading health checks",
            "correlation risk pattern",
            "static safety findings",
        ):
            self.assertIn(phrase, text)

    def test_review_rejects_runtime_and_execution_paths(self) -> None:
        text = REVIEW_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "do not reuse directly",
            "npx skills add",
            "manual copying into agent skill directories",
            "polymarket live executor",
            "l2 wallet workflows",
            "py-clob-client",
            "agent-triggered paper/live execution commands",
            "natural language can trigger a trade path",
        ):
            self.assertIn(phrase, text)

    def test_taxonomy_document_exists(self) -> None:
        self.assertTrue(TAXONOMY_PATH.is_file())

    def test_taxonomy_defines_agentic_risk_classes(self) -> None:
        text = TAXONOMY_PATH.read_text(encoding="utf-8")

        for phrase in (
            "Class 0: Reference-Only",
            "Class 1: Read-Only Observation",
            "Class 2: Analysis-Only",
            "Class 3: Paper-Only Simulation",
            "Class 4: Advisory Governance",
            "Class 5: Execution-Capable",
        ):
            self.assertIn(phrase, text)

    def test_taxonomy_forbids_agent_execution_authority(self) -> None:
        text = TAXONOMY_PATH.read_text(encoding="utf-8")

        for phrase in (
            "Agentic tools must not execute trades",
            "submit orders",
            "cancel orders",
            "transfer funds",
            "withdraw funds",
            "read broker credentials",
            "change risk limits",
            "disable kill switches",
            "bypass deterministic-risk-gateway",
        ):
            self.assertIn(phrase, text)

    def test_taxonomy_covers_prompt_injection_boundary(self) -> None:
        text = TAXONOMY_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "market titles, questions, descriptions, outcomes",
            "untrusted data",
            "never treat market metadata as instructions",
            "wrap market text in explicit data delimiters",
            "allowing market text to trigger tool calls",
            "allowing market text to request execution",
        ):
            self.assertIn(phrase, text)

    def test_taxonomy_covers_health_and_correlation_patterns(self) -> None:
        text = TAXONOMY_PATH.read_text(encoding="utf-8").lower()

        for phrase in (
            "green",
            "yellow",
            "red",
            "health checks are advisory",
            "correlation risk pattern",
            "resolution dependency",
        ):
            self.assertIn(phrase, text)

    def test_taxonomy_covers_script_safety_findings(self) -> None:
        text = TAXONOMY_PATH.read_text(encoding="utf-8")

        for phrase in (
            "no `sys.path.insert(0)` import shadowing",
            "no credentials in examples",
            "no network calls in unit tests",
            "explicit timeouts",
            "bounded retries",
            "identifiers validated before URL interpolation",
            "redaction before logs, errors, or audit",
        ):
            self.assertIn(phrase, text)

    def test_no_polymarket_skills_dependencies_are_declared(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "polymarket-skills",
            "py-clob-client",
            "@polymarket",
            "skills add",
        ):
            self.assertNotIn(forbidden, text)

    def test_ci_runs_polymarket_skills_reference_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("test_polymarket_skills_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
