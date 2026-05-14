import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "integrations" / "calculadora_investimento_reference_review.md"
ARCHITECTURE = ROOT / "docs" / "architecture" / "investment_scenario_simulation.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = ROOT / "pyproject.toml"


class CalculadoraInvestimentoReferenceReviewTests(unittest.TestCase):
    def test_review_keeps_repository_reference_only(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        required_flags = (
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "xlsx_copy_allowed: false",
            "excel_runtime_allowed: false",
            "vba_allowed: false",
            "market_data_allowed: false",
            "personalized_advice_allowed: false",
            "recommendation_allowed: false",
            "trading_methods_allowed: false",
            "risk_approval_allowed: false",
            "execution_approval_allowed: false",
            "production_enabled: false",
        )

        for flag in required_flags:
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_review_documents_safe_patterns(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        safe_patterns = (
            "investment scenario input",
            "scenario projection",
            "investor profile allocation",
            "long horizon comparison",
            "assumption sensitivity",
            "financial education disclaimer",
        )

        for pattern in safe_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_review_rejects_excel_and_advisory_runtime(self) -> None:
        text = REVIEW.read_text(encoding="utf-8").lower()

        rejected = (
            "excel workbook",
            "screenshots or images",
            "spreadsheet formulas as authoritative source",
            "vba automation",
            "profile allocations as real advice",
            "dividend estimates as guarantees",
            "real market data integrations",
            "deployment as financial advisory tool",
        )

        for item in rejected:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_architecture_keeps_simulation_non_advisory(self) -> None:
        text = ARCHITECTURE.read_text(encoding="utf-8").lower()

        required = (
            "calculator_runtime_allowed: false",
            "xlsx_runtime_allowed: false",
            "vba_allowed: false",
            "market_data_allowed: false",
            "personalized_advice_allowed: false",
            "recommendation_allowed: false",
            "trading_methods_allowed: false",
            "risk_approval_allowed: false",
            "execution_approval_allowed: false",
            "production_enabled: false",
            "this is not financial advice",
            "educational projections are not backtests",
            "backtests are not production approval",
            "deterministic-risk-gateway",
        )

        for item in required:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_pyproject_does_not_add_excel_or_market_data_dependencies(self) -> None:
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        forbidden_terms = (
            "openpyxl",
            "xlwings",
            "xlsxwriter",
            "calculadora_investimento",
            "augusto-belussi",
            "vba",
        )

        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_ci_runs_reference_review_tests(self) -> None:
        text = CI.read_text(encoding="utf-8")
        self.assertIn("test_calculadora_investimento_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
