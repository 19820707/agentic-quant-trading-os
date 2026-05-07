from pathlib import Path
import importlib.util
import unittest


ROOT = Path(__file__).resolve().parents[1]
SERVICE_MAIN_FILES = sorted((ROOT / "services").glob("*/app/main.py"))


class ServicePlaceholderTests(unittest.TestCase):
    def test_service_placeholders_import_and_expose_safe_routes(self):
        self.assertTrue(SERVICE_MAIN_FILES, "expected service placeholder modules")

        for index, path in enumerate(SERVICE_MAIN_FILES):
            with self.subTest(service=path.parts[-3]):
                module_name = f"service_placeholder_{index}"
                spec = importlib.util.spec_from_file_location(module_name, path)
                self.assertIsNotNone(spec)
                self.assertIsNotNone(spec.loader)

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                self.assertTrue(hasattr(module, "app"))
                paths = {route.path for route in module.app.routes}
                self.assertIn("/health", paths)
                self.assertIn("/ready", paths)

    def test_service_placeholders_remain_static_and_safe(self):
        for path in SERVICE_MAIN_FILES:
            with self.subTest(service=path.parts[-3]):
                text = path.read_text(encoding="utf-8")
                self.assertIn("external_calls", text)
                self.assertIn("False", text)
                self.assertIn("trading_logic", text)
                self.assertNotIn("os.environ", text)
                self.assertNotIn("submit_order", text)
                self.assertNotIn("place_order", text)
                self.assertNotIn("create_order", text)


if __name__ == "__main__":
    unittest.main()
