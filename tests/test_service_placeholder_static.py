"""Dependency-free structural checks for the service placeholders.

``test_service_placeholders.py`` imports each service and therefore needs
FastAPI, which CI does not install. These checks read the source with ``ast``
instead, so the safety properties of every service are verified in CI too:
each service exposes only read-only health routes and contains no other logic.
"""

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE_MAIN_FILES = sorted((ROOT / "services").glob("*/app/main.py"))

ALLOWED_IMPORTS = {"fastapi"}
ALLOWED_ROUTES = {"/health": "external_calls", "/ready": "trading_logic"}
MUTATING_OR_STREAMING_METHODS = {"post", "put", "patch", "delete", "websocket", "api_route", "route", "on_event"}


def _route_decorators(function: ast.FunctionDef) -> list[tuple[str, str]]:
    routes = []
    for decorator in function.decorator_list:
        if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
            path = decorator.args[0].value if decorator.args and isinstance(decorator.args[0], ast.Constant) else None
            routes.append((decorator.func.attr, path))
    return routes


def _returned_dict(function: ast.FunctionDef) -> dict[str, ast.expr]:
    for node in ast.walk(function):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict):
            return {
                key.value: value
                for key, value in zip(node.value.keys, node.value.values)
                if isinstance(key, ast.Constant)
            }
    return {}


class ServicePlaceholderStaticTests(unittest.TestCase):
    def test_all_sixteen_services_are_checked(self):
        self.assertEqual(len(SERVICE_MAIN_FILES), 16)

    def test_services_import_only_the_web_framework(self):
        for path in SERVICE_MAIN_FILES:
            with self.subTest(service=path.parts[-3]):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                imported = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        imported.add((node.module or "").split(".")[0])
                self.assertEqual(imported, ALLOWED_IMPORTS)

    def test_service_name_matches_its_directory(self):
        for path in SERVICE_MAIN_FILES:
            with self.subTest(service=path.parts[-3]):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                names = [
                    node.value.value
                    for node in tree.body
                    if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "SERVICE_NAME" for target in node.targets)
                    and isinstance(node.value, ast.Constant)
                ]
                self.assertEqual(names, [path.parts[-3]])

    def test_services_expose_only_read_only_health_routes(self):
        for path in SERVICE_MAIN_FILES:
            with self.subTest(service=path.parts[-3]):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
                routes = [route for function in functions for route in _route_decorators(function)]

                self.assertEqual(sorted(routes), sorted(("get", route) for route in ALLOWED_ROUTES))
                self.assertEqual(len(functions), len(ALLOWED_ROUTES))
                for method, _ in routes:
                    self.assertNotIn(method, MUTATING_OR_STREAMING_METHODS)

    def test_health_routes_report_no_external_calls_and_no_trading_logic(self):
        for path in SERVICE_MAIN_FILES:
            with self.subTest(service=path.parts[-3]):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for function in (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)):
                    for _, route in _route_decorators(function):
                        flag = ALLOWED_ROUTES[route]
                        returned = _returned_dict(function)
                        self.assertIn(flag, returned)
                        self.assertIsInstance(returned[flag], ast.Constant)
                        self.assertIs(returned[flag].value, False)

    def test_services_contain_no_logic_beyond_the_placeholder(self):
        allowed_calls = {"FastAPI", "get"}
        for path in SERVICE_MAIN_FILES:
            with self.subTest(service=path.parts[-3]):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                calls = {
                    node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "?")
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Call)
                }
                self.assertLessEqual(calls, allowed_calls)
                self.assertFalse(
                    [node for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.While, ast.For, ast.With, ast.Try))]
                )


if __name__ == "__main__":
    unittest.main()
