from __future__ import annotations

from pathlib import Path
import unittest


try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - project expects Python 3.11+
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]


class PackagingConfigurationTests(unittest.TestCase):
    def test_pyproject_uses_explicit_build_backend(self) -> None:
        self.assertIsNotNone(tomllib, "Python 3.11+ tomllib is required for packaging checks")

        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

        self.assertEqual(pyproject["build-system"]["build-backend"], "setuptools.build_meta")
        self.assertIn("setuptools>=69", pyproject["build-system"]["requires"])

    def test_pyproject_uses_explicit_package_discovery(self) -> None:
        self.assertIsNotNone(tomllib, "Python 3.11+ tomllib is required for packaging checks")

        pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        package_find = pyproject["tool"]["setuptools"]["packages"]["find"]

        for package_prefix in (
            "adapters*",
            "api*",
            "backtesting*",
            "config*",
            "market_data*",
            "oms*",
            "packages*",
            "portfolio*",
            "risk*",
            "strategies*",
        ):
            self.assertIn(package_prefix, package_find["include"])

        for excluded_prefix in ("docs*", "integrations*", "scripts*", "services*", "tests*"):
            self.assertIn(excluded_prefix, package_find["exclude"])


if __name__ == "__main__":
    unittest.main()
