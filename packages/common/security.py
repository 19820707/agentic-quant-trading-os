"""Local security helpers for safe redaction before logging or reporting.

These utilities are generic shape-preserving helpers. They do not read
credentials, inspect environment variables, access files, call network, or
interpret trading semantics.
"""

from __future__ import annotations

import re
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
        "passphrase",
        "access_key",
        "signing_key",
        "encryption_key",
        "cookie",
        "set_cookie",
        "jwt",
    }
)

# Names that only count as sensitive on an exact match. As a suffix they are
# common in harmless metadata (for example ``random_seed``).
_EXACT_ONLY_SENSITIVE_KEYS = frozenset({"seed"})

_CAMEL_CASE_BOUNDARY = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")


def _tokenize_key(key: str) -> tuple[str, ...]:
    """Split a key into lowercase words across separators and camelCase."""

    spaced = _CAMEL_CASE_BOUNDARY.sub("_", key.strip())
    return tuple(token for token in _NON_ALPHANUMERIC.split(spaced.lower()) if token)


_SENSITIVE_TOKEN_SUFFIXES = frozenset(
    _tokenize_key(key) for key in DEFAULT_SENSITIVE_KEYS - _EXACT_ONLY_SENSITIVE_KEYS
)
_MAX_SENSITIVE_SUFFIX_LENGTH = max(len(suffix) for suffix in _SENSITIVE_TOKEN_SUFFIXES)

_COMPACT_SENSITIVE_KEYS = frozenset(key.replace("_", "") for key in DEFAULT_SENSITIVE_KEYS)


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def is_sensitive_key(key: str) -> bool:
    """Return true when a mapping key is known to carry sensitive material.

    A key is sensitive when it equals a known sensitive name, or when its words
    end with one (``client_secret``, ``X-Api-Key``, ``dbPassword``,
    ``session_token``). Matching on whole trailing words keeps policy flags such
    as ``contains_secrets`` or ``token_id`` readable.
    """

    normalized = _normalize_key(key)
    compact = normalized.replace("_", "")
    if normalized in DEFAULT_SENSITIVE_KEYS or compact in _COMPACT_SENSITIVE_KEYS:
        return True

    tokens = _tokenize_key(key)
    for length in range(1, min(len(tokens), _MAX_SENSITIVE_SUFFIX_LENGTH) + 1):
        if tokens[-length:] in _SENSITIVE_TOKEN_SUFFIXES:
            return True
    return False


# Nesting deeper than this is replaced rather than walked, so a cyclic or
# hostile payload cannot exhaust the stack while being redacted.
MAX_REDACTION_DEPTH = 64

# Secret-shaped substrings inside free text. Each match is replaced as a whole,
# except where a named ``keep`` group marks a prefix that stays readable.
_SECRET_TEXT_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(?:-----END [A-Z ]*PRIVATE KEY-----|\Z)", re.DOTALL),
    re.compile(r"(?i)(?P<keep>\bbearer\s+)(?=[A-Za-z0-9._~+/=\-]*[0-9._=\-])[A-Za-z0-9._~+/=\-]{8,}"),
    re.compile(r"(?P<keep>[a-zA-Z][a-zA-Z0-9+.\-]*://[^/\s:@]+:)[^@\s/]+(?=@)"),
    re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-(?:[a-z0-9]+-)*[A-Za-z0-9_\-]{20,}"),
    re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"),
)


def _replace_secret_match(match: re.Match[str]) -> str:
    kept = match.groupdict().get("keep") or ""
    return kept + REDACTED_VALUE


def redact_text(text: str) -> str:
    """Replace secret-shaped substrings in free text and keep the rest readable.

    Covers bearer credentials, passwords embedded in URLs, private key blocks,
    JSON Web Tokens and common provider key formats. Ordinary prose that only
    mentions words such as "token" is returned unchanged.
    """

    for pattern in _SECRET_TEXT_PATTERNS:
        text = pattern.sub(_replace_secret_match, text)
    return text


def _redact(value: object, depth: int) -> object:
    if depth > MAX_REDACTION_DEPTH:
        return REDACTED_VALUE
    if isinstance(value, Mapping):
        return {
            key: REDACTED_VALUE if is_sensitive_key(str(key)) else _redact(item, depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, (bytes, bytearray)):
        return value
    if isinstance(value, Sequence):
        return [_redact(item, depth + 1) for item in value]
    return value


def redact_value(value: object) -> object:
    """Redact nested containers and secret-shaped text; other scalars are unchanged."""

    return _redact(value, 0)


def redact_mapping(data: Mapping[str, object]) -> dict[str, object]:
    """Return a redacted copy of a mapping without mutating the input."""

    redacted = _redact(data, 0)
    assert isinstance(redacted, dict)
    return redacted


def redact_sequence(data: Sequence[object]) -> list[object]:
    """Return a redacted list copy of a sequence without mutating the input."""

    if isinstance(data, (str, bytes, bytearray)):
        return [redact_value(data)]
    redacted = _redact(data, 0)
    assert isinstance(redacted, list)
    return redacted


def redact_secrets(data: object) -> object:
    """Redact sensitive values from nested JSON-compatible data."""

    return redact_value(data)
