"""Local development-environment diagnostics.

This script does not install packages, call network, read secrets, start
services, or access broker/exchange systems.
"""

from __future__ import annotations

import importlib.util
import sys


EXPECTED_PYTHON = (3, 11)
REQUIRED_PACKAGES = ("fastapi", "jsonschema", "uvicorn")


def is_importable(package: str) -> bool:
    return importlib.util.find_spec(package) is not None


def main() -> int:
    print("Development environment check")
    print(f"Python: {sys.version.split()[0]}")

    if sys.version_info < EXPECTED_PYTHON:
        print("WARNING: project expects Python 3.11 or newer.")
        print("Select a Python 3.11+ interpreter in your editor or virtual environment.")

    missing = [package for package in REQUIRED_PACKAGES if not is_importable(package)]
    if missing:
        print("Missing packages:")
        for package in missing:
            print(f"- {package}")
        print("Install local project dependencies with:")
        print("python -m pip install -e .")
        return 1

    print("Required scaffold development packages are importable.")
    print("No credentials, broker connections, network calls, or services were started.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
