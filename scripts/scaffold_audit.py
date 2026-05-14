"""Safe scaffold auditor.

This script uses only the Python standard library. It performs local filesystem
checks and never calls external services.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SERVICES = [
    "market-data-engine",
    "feature-engine",
    "feature-store-service",
    "deep-learning-engine",
    "regime-detection-service",
    "model-monitoring-service",
    "signal-engine",
    "order-intent-service",
    "backtesting-engine",
    "deterministic-risk-gateway",
    "paper-trading-engine",
    "execution-engine",
    "portfolio-service",
    "observability-audit-service",
    "reporting-engine",
    "governance-service",
]

REQUIRED_ROOT_PATHS = [
    "AGENTS.md",
    "README.md",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODEOWNERS",
    "Makefile",
    "docker-compose.yml",
    "pyproject.toml",
    "package.json",
    ".env.example",
    "packages/contracts/schemas",
    "packages/contracts/schemas/governance/capability_manifest.schema.json",
    "docs/architecture",
    "docs/architecture/capability_maturity_matrix.md",
    "docs/runbooks",
    "security",
]

PROHIBITED_MARKERS = [
    "BEGIN PRIVATE KEY",
    "SECRET=",
    "API_KEY=",
    "PRIVATE_KEY=",
    "submit_order(",
    "place_order(",
    "create_order(",
    "withdraw(",
]

SKIPPED_DIRECTORY_NAMES = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    "agentic_quant_trading_os.egg-info",
}

SKIPPED_FILE_SUFFIXES = {
    ".pyc",
    ".pyo",
}

FORBIDDEN_CAPABILITY_STATES = {
    "LIVE_TRADING_ENABLED",
    "BROKER_PRIVATE_ENDPOINTS",
    "ORDER_SUBMISSION",
    "ORDER_CANCELLATION",
    "POSITION_MUTATION",
    "UNREVIEWED_AGENT_RUNTIME",
    "UNGATED_MEMORY_RUNTIME",
    "UNGATED_NETWORK_ACCESS",
    "UNGATED_CREDENTIAL_ACCESS",
    "BYPASS_DETERMINISTIC_RISK_GATEWAY",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def fail(message: str) -> None:
    raise SystemExit(f"scaffold audit failed: {message}")


def should_scan_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if any(part in SKIPPED_DIRECTORY_NAMES for part in path.parts):
        return False
    if path.suffix in SKIPPED_FILE_SUFFIXES:
        return False
    return True


def check_required_paths() -> None:
    for relative in REQUIRED_ROOT_PATHS:
        if not (ROOT / relative).exists():
            fail(f"missing required path: {relative}")


def check_services() -> None:
    for service in SERVICES:
        service_root = ROOT / "services" / service
        required = [
            service_root / "README.md",
            service_root / "app" / "__init__.py",
            service_root / "app" / "main.py",
            service_root / "tests" / "test_placeholder.py",
        ]
        for path in required:
            if not path.exists():
                fail(f"missing service scaffold file: {path.relative_to(ROOT)}")

        main_text = read_text(service_root / "app" / "main.py")
        if '@app.get("/health")' not in main_text:
            fail(f"missing /health endpoint: {service}")
        if '@app.get("/ready")' not in main_text:
            fail(f"missing /ready endpoint: {service}")
        if "external_calls" not in main_text or "False" not in main_text:
            fail(f"missing explicit no-external-calls marker: {service}")
        if "trading_logic" not in main_text or "False" not in main_text:
            fail(f"missing explicit no-trading-logic marker: {service}")


def check_prohibited_markers() -> None:
    self_path = Path(__file__).resolve()
    for path in ROOT.rglob("*"):
        if path.resolve() == self_path:
            continue
        if not should_scan_file(path):
            continue
        text = read_text(path)
        for marker in PROHIBITED_MARKERS:
            if marker.lower() not in text.lower():
                continue
            fail(f"prohibited marker {marker!r} found in {path.relative_to(ROOT)}")


def check_capability_governance() -> None:
    matrix_path = ROOT / "docs" / "architecture" / "capability_maturity_matrix.md"
    manifest_path = (
        ROOT / "tests" / "fixtures" / "contracts" / "governance" / "capability_manifest.valid.json"
    )

    matrix_text = read_text(matrix_path)
    for state in FORBIDDEN_CAPABILITY_STATES:
        if state not in matrix_text:
            fail(f"capability maturity matrix missing forbidden state: {state}")
        if f"{state}: true" in matrix_text or f"{state}=true" in matrix_text:
            fail(f"capability maturity matrix enables forbidden state: {state}")

    with manifest_path.open(encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)

    manifest_states = set(manifest.get("forbidden_global_states", []))
    missing_states = FORBIDDEN_CAPABILITY_STATES - manifest_states
    if missing_states:
        fail(f"capability manifest missing forbidden states: {sorted(missing_states)}")

    runtime_defaults = manifest.get("runtime_defaults", {})
    for flag in (
        "runtime_enabled",
        "production_enabled",
        "network_access_allowed",
        "credentials_allowed",
        "private_endpoints_allowed",
        "trading_methods_allowed",
        "risk_approval_allowed",
        "execution_approval_allowed",
    ):
        if runtime_defaults.get(flag) is not False:
            fail(f"capability manifest must keep {flag} false")


def check_auditor_guardrails() -> None:
    marker_hits = [
        marker for marker in PROHIBITED_MARKERS if marker.lower() in "withdraw(amount)"
    ]
    if "withdraw(" not in marker_hits:
        fail("auditor guardrail failed: withdraw calls are not detected")


def main() -> None:
    check_auditor_guardrails()
    check_required_paths()
    check_services()
    check_prohibited_markers()
    check_capability_governance()
    print("scaffold audit passed: placeholders present, no trading logic executed")


if __name__ == "__main__":
    main()
