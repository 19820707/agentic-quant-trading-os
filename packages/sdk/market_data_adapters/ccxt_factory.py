"""Fail-closed placeholder for a future public read-only CCXT client factory.

This module does not import ccxt, read environment variables, call network,
accept credentials, or create real exchange clients. It is a design gate only.
"""

from __future__ import annotations

from typing import Final

__all__ = [
    "ALLOWED_PUBLIC_EXCHANGES",
    "CCXTDependencyUnavailable",
    "CCXTExchangeNotAllowlisted",
    "CCXTFeatureDisabled",
    "create_ccxt_public_client",
]

ALLOWED_PUBLIC_EXCHANGES: Final[frozenset[str]] = frozenset({"binance", "okx", "kraken"})


class CCXTDependencyUnavailable(RuntimeError):
    """Raised when the optional CCXT dependency path remains unavailable."""


class CCXTFeatureDisabled(RuntimeError):
    """Raised when the CCXT public client factory is not explicitly enabled."""


class CCXTExchangeNotAllowlisted(ValueError):
    """Raised when an exchange is not approved for the public client factory."""


def create_ccxt_public_client(
    exchange_id: str,
    *,
    enabled: bool = False,
    approval_gate_enabled: bool = False,
) -> object:
    """Fail-closed placeholder for a future public read-only CCXT client factory.

    This function does not import ccxt, read environment variables, call network,
    accept credentials, or create real exchange clients.
    """
    if not enabled:
        raise CCXTFeatureDisabled("CCXT public client factory is disabled by default.")

    if not approval_gate_enabled:
        raise CCXTFeatureDisabled("CCXT approval gate is not enabled.")

    normalized_exchange_id = exchange_id.strip().lower()
    if not normalized_exchange_id or normalized_exchange_id not in ALLOWED_PUBLIC_EXCHANGES:
        raise CCXTExchangeNotAllowlisted(
            "CCXT exchange is not allowlisted for public read-only access."
        )

    raise CCXTDependencyUnavailable(
        "CCXT optional dependency is unavailable: real CCXT import is not implemented or approved in this scaffold."
    )
