"""Local security helpers for safe redaction before logging or reporting.

These utilities are generic shape-preserving helpers. They do not read
credentials, inspect environment variables, access files, call network, or
interpret trading semantics.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


REDACTED_VALUE = "[REDACTED]"

DEFAULT_SENSITIVE_KEYS = frozenset(
    {
        "api_key",
        "apikey",
        "secret",
        "secret_key",
        "private_key",
        "password",
        "passwd",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "auth",
        "bearer",
        "credential",
        "credentials",
        "broker_key",
        "exchange_key",
        "withdrawal_key",
        "seed",
        "mnemonic",
    }
)

_COMPACT_SENSITIVE_KEYS = frozenset(key.replace("_", "") for key in DEFAULT_SENSITIVE_KEYS)


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def is_sensitive_key(key: str) -> bool:
    """Return true when a mapping key is known to carry sensitive material."""

    normalized = _normalize_key(key)
    compact = normalized.replace("_", "")
    return normalized in DEFAULT_SENSITIVE_KEYS or compact in _COMPACT_SENSITIVE_KEYS


def redact_value(value: object) -> object:
    """Redact nested containers while leaving scalar values unchanged."""

    if isinstance(value, Mapping):
        return redact_mapping(value)
    if isinstance(value, (str, bytes, bytearray)):
        return value
    if isinstance(value, Sequence):
        return redact_sequence(value)
    return value


def redact_mapping(data: Mapping[str, object]) -> dict[str, object]:
    """Return a redacted copy of a mapping without mutating the input."""

    redacted: dict[str, object] = {}
    for key, value in data.items():
        redacted[key] = REDACTED_VALUE if is_sensitive_key(str(key)) else redact_value(value)
    return redacted


def redact_sequence(data: Sequence[object]) -> list[object]:
    """Return a redacted list copy of a sequence without mutating the input."""

    if isinstance(data, (str, bytes, bytearray)):
        return [data]
    return [redact_value(item) for item in data]


def redact_secrets(data: object) -> object:
    """Redact sensitive values from nested JSON-compatible data."""

    return redact_value(data)
