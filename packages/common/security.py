"""Local security helpers for safe redaction before logging or reporting.

These utilities are generic shape-preserving helpers. They do not read
credentials, inspect environment variables, access files, call network, or
interpret trading semantics.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, Final

__all__ = [
    "REDACTED_VALUE",
    "MAX_REDACTION_DEPTH",
    "DEFAULT_SENSITIVE_KEYS",
    "is_sensitive_key",
    "redact_value",
    "redact_mapping",
    "redact_sequence",
    "redact_secrets",
    "redact_for_log",
]

REDACTED_VALUE: Final[str] = "[REDACTED]"

# Fail-safe depth limit: subtrees beyond this depth are redacted entirely
# rather than traversed.  Prevents stack overflow on adversarially nested
# payloads and ensures O(n·MAX_REDACTION_DEPTH) worst-case traversal cost.
MAX_REDACTION_DEPTH: Final[int] = 32

DEFAULT_SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
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

_COMPACT_SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    key.replace("_", "") for key in DEFAULT_SENSITIVE_KEYS
)


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def is_sensitive_key(key: str) -> bool:
    """Return true when a mapping key is known to carry sensitive material."""
    normalized = _normalize_key(key)
    compact = normalized.replace("_", "")
    return normalized in DEFAULT_SENSITIVE_KEYS or compact in _COMPACT_SENSITIVE_KEYS


def redact_value(value: object, _depth: int = 0) -> object:
    """Redact nested containers while leaving scalar values unchanged.

    When depth exceeds MAX_REDACTION_DEPTH the entire subtree is replaced
    with REDACTED_VALUE as a fail-safe — never silently pass-through.
    """
    if _depth >= MAX_REDACTION_DEPTH:
        return REDACTED_VALUE

    if isinstance(value, Mapping):
        return redact_mapping(value, _depth=_depth)
    if isinstance(value, (str, bytes, bytearray)):
        return value
    if isinstance(value, Sequence):
        return redact_sequence(value, _depth=_depth)
    return value


def redact_mapping(data: Mapping[str, object], *, _depth: int = 0) -> dict[str, object]:
    """Return a redacted copy of a mapping without mutating the input."""
    if _depth >= MAX_REDACTION_DEPTH:
        return {str(k): REDACTED_VALUE for k in data}

    redacted: dict[str, object] = {}
    for key, value in data.items():
        if is_sensitive_key(str(key)):
            redacted[key] = REDACTED_VALUE
        else:
            redacted[key] = redact_value(value, _depth + 1)
    return redacted


def redact_sequence(data: Sequence[object], *, _depth: int = 0) -> list[object]:
    """Return a redacted list copy of a sequence without mutating the input."""
    if isinstance(data, (str, bytes, bytearray)):
        return [data]
    if _depth >= MAX_REDACTION_DEPTH:
        return [REDACTED_VALUE for _ in data]
    return [redact_value(item, _depth + 1) for item in data]


def redact_secrets(data: object) -> object:
    """Redact sensitive values from nested JSON-compatible data."""
    return redact_value(data)


def redact_for_log(value: object, *, label: str = "payload") -> str:
    """Return a JSON string of a redacted value, safe for log output.

    Never raises: if redaction or serialisation fails the returned string
    identifies the label and the failure mode without leaking content.
    """
    try:
        redacted = redact_secrets(value)
        return json.dumps(redacted, default=str)
    except Exception:  # noqa: BLE001 — must not propagate from a logging helper
        return f'{{"{label}": "<redaction-failed>"}}'
