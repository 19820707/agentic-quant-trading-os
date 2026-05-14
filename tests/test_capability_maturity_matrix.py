import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "architecture" / "capability_maturity_matrix.md"


class CapabilityMaturityMatrixTests(unittest.TestCase):
    def test_matrix_document_exists(self):
        self.assertTrue(MATRIX.is_file())

    def test_matrix_defines_required_columns(self):
        text = MATRIX.read_text(encoding="utf-8")

        for column in (
            "Domain",
            "Current status",
            "Allowed capability",
            "Forbidden capability",
            "Required contracts",
            "Required tests",
            "Required approval gate",
            "Promotion target",
            "Owner boundary",
        ):
            with self.subTest(column=column):
                self.assertIn(column, text)

    def test_matrix_defines_maturity_states(self):
        text = MATRIX.read_text(encoding="utf-8")

        for state in (
            "SCAFFOLD_ONLY",
            "CONTRACT_DEFINED",
            "FAKE_RUNTIME_ONLY",
            "READ_ONLY_ADAPTER_ONLY",
            "PAPER_ONLY",
            "GATED_LIVE_READ_ONLY",
            "GATED_LIVE_EXECUTION",
            "PRODUCTION_BLOCKED",
        ):
            with self.subTest(state=state):
                self.assertIn(state, text)

    def test_matrix_covers_core_repository_domains(self):
        text = MATRIX.read_text(encoding="utf-8")

        for domain in (
            "Service scaffold",
            "Trading contracts",
            "Audit contracts",
            "Prediction research contracts",
            "Agent orchestration governance",
            "Market data adapters",
            "CCXT optional dependency",
            "Security tooling",
            "Execution engine",
        ):
            with self.subTest(domain=domain):
                self.assertIn(domain, text)

    def test_matrix_requires_traceability_evidence(self):
        text = MATRIX.read_text(encoding="utf-8")

        for phrase in (
            "a documented owner boundary",
            "a contract or explicit policy document",
            "a valid fixture",
            "a local test proving the allowed behavior",
            "a local test proving forbidden behavior remains blocked",
            "an approval gate reference",
            "a rollback or demotion path",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
