"""Local secret and artifact hygiene auditor.

This script uses only the Python standard library. It performs deterministic
local repository checks and never calls external services.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

SKIPPED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "agentic_quant_trading_os.egg-info",
    "node_modules",
}

SKIPPED_FILE_SUFFIXES = {
    ".pyc",
    ".pyo",
}

BLOCKED_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.dev",
    ".env.development",
    ".env.prod",
    ".env.production",
    ".env.staging",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
}

ALLOWED_FILE_NAMES = {
    ".env.example",
}

BLOCKED_FILE_SUFFIXES = {
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".duckdb",
    ".parquet",
    ".feather",
    ".h5",
    ".hdf5",
    ".onnx",
    ".pt",
    ".pth",
    ".ckpt",
    ".joblib",
    ".pkl",
    ".pickle",
}

BLOCKED_DIRECTORY_NAMES = {
    "artifacts",
    "checkpoints",
    "models",
    "runs",
    "mlruns",
    "wandb",
}

SECRET_PATTERNS = {
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "aws_access_key_id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "openai_api_key": re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    "openrouter_api_key": re.compile(r"\bsk-or-v1-[A-Za-z0-9]{20,}\b"),
    "generic_secret_assignment": re.compile(
        r"(?i)\b(api[_-]?key|secret|private[_-]?key|token|password)\b\s*=\s*['\"]?[^'\"\s]{12,}"
    ),
}

TEXT_FILE_SUFFIX_ALLOWLIST = {
    "",
    ".cfg",
    ".css",
    ".csv",
    ".ini",
    ".json",
    ".lock",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


class HygieneFinding(ValueError):
    """Raised when repository hygiene validation finds unsafe content."""


class SecretFinding(HygieneFinding):
    """Raised when a secret-like value is detected."""


class ArtifactFinding(HygieneFinding):
    """Raised when a blocked artifact or sensitive file is detected."""


def relative(path: Path) -> Path:
    return path.relative_to(ROOT)


def iter_repository_paths() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if any(part in SKIPPED_DIRECTORY_NAMES for part in path.relative_to(ROOT).parts):
            continue
        yield path


def is_text_candidate(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix in SKIPPED_FILE_SUFFIXES:
        return False
    return path.suffix in TEXT_FILE_SUFFIX_ALLOWLIST


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def find_blocked_artifact_paths() -> list[str]:
    findings: list[str] = []
    for path in iter_repository_paths():
        rel = relative(path)
        if path.is_dir() and path.name in BLOCKED_DIRECTORY_NAMES:
            findings.append(f"blocked directory: {rel}")
            continue
        if not path.is_file():
            continue
        if path.name in ALLOWED_FILE_NAMES:
            continue
        if path.name in BLOCKED_FILE_NAMES:
            findings.append(f"blocked sensitive filename: {rel}")
            continue
        if path.suffix in BLOCKED_FILE_SUFFIXES:
            findings.append(f"blocked generated/sensitive artifact suffix: {rel}")
    return findings


def find_secret_patterns() -> list[str]:
    findings: list[str] = []
    self_path = Path(__file__).resolve()
    for path in iter_repository_paths():
        if path.resolve() == self_path:
            continue
        if not is_text_candidate(path):
            continue
        text = read_text(path)
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"secret-like pattern {name!r} in {relative(path)}")
    return findings


def audit_repository_hygiene() -> None:
    artifact_findings = find_blocked_artifact_paths()
    if artifact_findings:
        raise ArtifactFinding("; ".join(artifact_findings))

    secret_findings = find_secret_patterns()
    if secret_findings:
        raise SecretFinding("; ".join(secret_findings))


def main() -> None:
    audit_repository_hygiene()
    print("secret/artifact audit passed: no blocked repository artifacts or secret-like values detected")


if __name__ == "__main__":
    main()
