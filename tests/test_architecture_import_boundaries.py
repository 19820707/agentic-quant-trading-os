"""Architecture fitness tests for import boundaries.

AGENTS.md states that only the execution engine may ever reach a broker or
exchange, and that shared packages perform no network, process or environment
access. These tests enforce both rules on the source tree, so a violating import
fails review instead of relying on convention.
"""

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SOURCE_DIRECTORIES = ("packages", "services", "scripts", "apps", "integrations", "agentic", "strategies")

# Libraries that can submit, cancel or move real orders and funds.
BROKER_EXCHANGE_MODULES = frozenset(
    {
        "ccxt",
        "ib_insync",
        "ibapi",
        "alpaca",
        "alpaca_trade_api",
        "binance",
        "krakenex",
        "kucoin",
        "bybit",
        "pybit",
        "okx",
        "oandapyV20",
        "MetaTrader5",
        "quickfix",
        "simplefix",
        "web3",
        "py_clob_client",
    }
)

# The only place a broker or exchange library may be imported, in a future
# controlled-live implementation behind the Deterministic Risk Gateway.
BROKER_IMPORT_ALLOWED_PREFIXES = ("services/execution-engine/",)

# docs/integrations/ccxt_import_guard_design.md names one further location: a
# future, separately approved, public read-only client factory may import ccxt
# inside this single module, and nowhere else.
READ_ONLY_IMPORT_EXCEPTIONS = {
    "packages/sdk/market_data_adapters/ccxt_factory.py": frozenset({"ccxt"}),
}

# Shared packages are pure: no network, no subprocesses.
NETWORK_AND_PROCESS_MODULES = frozenset(
    {
        "socket",
        "ssl",
        "http",
        "urllib",
        "ftplib",
        "smtplib",
        "telnetlib",
        "requests",
        "httpx",
        "aiohttp",
        "websocket",
        "websockets",
        "grpc",
        "subprocess",
        "multiprocessing",
    }
)
PURE_PACKAGE_PREFIXES = ("packages/",)

ENVIRONMENT_ACCESSORS = frozenset({"environ", "getenv", "putenv", "environb"})


def _python_sources() -> list[Path]:
    sources: list[Path] = []
    for directory in SOURCE_DIRECTORIES:
        base = ROOT / directory
        if base.is_dir():
            sources.extend(path for path in base.rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(sources)


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def imported_top_level_modules(tree: ast.AST) -> set[str]:
    """Top-level module names imported statically or by a literal dynamic import."""

    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                modules.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            function = node.func
            name = function.id if isinstance(function, ast.Name) else getattr(function, "attr", "")
            if name in {"__import__", "import_module"} and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    modules.add(first.value.split(".")[0])
    return modules


def reads_process_environment(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in ENVIRONMENT_ACCESSORS:
            if isinstance(node.value, ast.Name) and node.value.id == "os":
                return True
        elif isinstance(node, ast.ImportFrom) and node.module == "os":
            if any(alias.name in ENVIRONMENT_ACCESSORS for alias in node.names):
                return True
    return False


class ImportBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trees = {
            _relative(path): ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for path in _python_sources()
        }

    def test_source_tree_is_scanned(self):
        self.assertGreater(len(self.trees), 30)
        self.assertIn("packages/common/security.py", self.trees)
        self.assertIn("services/execution-engine/app/main.py", self.trees)

    def test_broker_and_exchange_libraries_are_imported_only_by_the_execution_engine(self):
        violations = [
            f"{path}: {sorted(found)}"
            for path, tree in self.trees.items()
            if not path.startswith(BROKER_IMPORT_ALLOWED_PREFIXES)
            for found in [
                (imported_top_level_modules(tree) & BROKER_EXCHANGE_MODULES)
                - READ_ONLY_IMPORT_EXCEPTIONS.get(path, frozenset())
            ]
            if found
        ]

        self.assertEqual(violations, [])

    def test_read_only_import_exceptions_match_the_documented_location(self):
        design = (ROOT / "docs" / "integrations" / "ccxt_import_guard_design.md").read_text(encoding="utf-8")

        for path, modules in READ_ONLY_IMPORT_EXCEPTIONS.items():
            with self.subTest(path=path):
                self.assertIn(path, design)
                self.assertTrue((ROOT / path).is_file())
                self.assertEqual(modules, frozenset({"ccxt"}))
        self.assertIn("no import in services", design)

    def test_scaffold_phase_has_no_broker_or_exchange_imports_at_all(self):
        # Research-only phase: not even the execution engine imports one yet.
        # Relaxing this test is a deliberate, reviewed step towards live trading.
        violations = [
            f"{path}: {sorted(found)}"
            for path, tree in self.trees.items()
            for found in [imported_top_level_modules(tree) & BROKER_EXCHANGE_MODULES]
            if found
        ]

        self.assertEqual(violations, [])

    def test_shared_packages_do_not_import_network_or_process_modules(self):
        violations = [
            f"{path}: {sorted(found)}"
            for path, tree in self.trees.items()
            if path.startswith(PURE_PACKAGE_PREFIXES)
            for found in [imported_top_level_modules(tree) & NETWORK_AND_PROCESS_MODULES]
            if found
        ]

        self.assertEqual(violations, [])

    def test_shared_packages_do_not_read_the_process_environment(self):
        violations = [
            path
            for path, tree in self.trees.items()
            if path.startswith(PURE_PACKAGE_PREFIXES) and reads_process_environment(tree)
        ]

        self.assertEqual(violations, [])


class ImportScannerSelfTests(unittest.TestCase):
    """The scanner itself must detect what it claims to detect."""

    def test_detects_static_and_dynamic_imports(self):
        tree = ast.parse(
            "import ccxt.async_support\n"
            "from web3 import Web3\n"
            "import importlib\n"
            "importlib.import_module('quickfix')\n"
            "__import__('ib_insync')\n"
            "from . import local_module\n"
        )

        self.assertEqual(
            imported_top_level_modules(tree) & BROKER_EXCHANGE_MODULES,
            {"ccxt", "web3", "quickfix", "ib_insync"},
        )

    def test_detects_environment_access(self):
        self.assertTrue(reads_process_environment(ast.parse("import os\nvalue = os.environ['A']\n")))
        self.assertTrue(reads_process_environment(ast.parse("import os\nvalue = os.getenv('A')\n")))
        self.assertTrue(reads_process_environment(ast.parse("from os import environ\n")))
        self.assertFalse(reads_process_environment(ast.parse("import os\nvalue = os.path.join('a', 'b')\n")))


if __name__ == "__main__":
    unittest.main()
