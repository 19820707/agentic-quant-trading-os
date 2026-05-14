from pathlib import Path
import unittest

from scripts import scaffold_audit


class ScaffoldAuditTests(unittest.TestCase):
    def test_generated_python_cache_files_are_not_scanned(self) -> None:
        self.assertFalse(
            scaffold_audit.should_scan_file(
                Path("scripts") / "__pycache__" / "scaffold_audit.cpython-310.pyc"
            )
        )

    def test_regular_source_files_are_scanned(self) -> None:
        self.assertTrue(scaffold_audit.should_scan_file(Path("scripts") / "scaffold_audit.py"))

    def test_forbidden_capability_states_are_tracked(self) -> None:
        self.assertIn("LIVE_TRADING_ENABLED", scaffold_audit.FORBIDDEN_CAPABILITY_STATES)
        self.assertIn("BYPASS_DETERMINISTIC_RISK_GATEWAY", scaffold_audit.FORBIDDEN_CAPABILITY_STATES)

    def test_capability_governance_check_passes_for_repository_fixture(self) -> None:
        scaffold_audit.check_capability_governance()


if __name__ == "__main__":
    unittest.main()
