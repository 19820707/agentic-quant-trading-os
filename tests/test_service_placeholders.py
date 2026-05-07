"""Import smoke tests for scaffold service apps (no servers, no network)."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _scaffold_services() -> list[str]:
    root = _repo_root()
    audit_path = root / "scripts" / "scaffold_audit.py"
    spec = importlib.util.spec_from_file_location(
        "scaffold_audit_services",
        audit_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scaffold audit module: {audit_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.SERVICES)


def _load_service_main(service: str):
    root = _repo_root()
    main_path = root / "services" / service / "app" / "main.py"
    safe_name = f"service_main_{service.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(safe_name, main_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {main_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestServicePlaceholderImports(unittest.TestCase):
    """Each scaffold service main defines FastAPI app and SERVICE_NAME."""

    def test_each_service_main_exposes_app_and_name(self) -> None:
        for service in _scaffold_services():
            with self.subTest(service=service):
                mod = _load_service_main(service)
                self.assertTrue(hasattr(mod, "app"))
                self.assertTrue(hasattr(mod, "SERVICE_NAME"))
                self.assertEqual(mod.SERVICE_NAME, service)
