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

    def test_local_virtual_environment_files_are_not_scanned(self) -> None:
        self.assertFalse(
            scaffold_audit.should_scan_file(
                Path(".venv") / "Lib" / "site-packages" / "fastapi" / "security" / "oauth2.py"
            )
        )

    def test_regular_source_files_are_scanned(self) -> None:
        self.assertTrue(scaffold_audit.should_scan_file(Path("scripts") / "scaffold_audit.py"))


if __name__ == "__main__":
    unittest.main()
