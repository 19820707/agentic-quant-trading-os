"""Thread-safe in-memory registry for read-only market data adapter factories."""

from __future__ import annotations

import re
import threading
from dataclasses import dataclass
from typing import Callable

from .market_data_adapter import ReadOnlyMarketDataAdapter

__all__ = [
    "AdapterFactory",
    "CCXT_READONLY_ADAPTER_NAME",
    "DuplicateMarketDataAdapterError",
    "MarketDataAdapterInfo",
    "MarketDataAdapterRegistry",
    "MarketDataAdapterRegistryError",
    "UnknownMarketDataAdapterError",
    "register_ccxt_readonly_adapter",
]

# Adapter names must start with a letter and contain only letters, digits,
# hyphens, or underscores — no path separators, dots, or whitespace.
_ADAPTER_NAME_RE: re.Pattern[str] = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")

CCXT_READONLY_ADAPTER_NAME = "ccxt-readonly"


class MarketDataAdapterRegistryError(Exception):
    """Raised when the read-only market data adapter registry cannot resolve an adapter."""


class UnknownMarketDataAdapterError(MarketDataAdapterRegistryError):
    """Raised when a requested adapter is not registered."""


class DuplicateMarketDataAdapterError(MarketDataAdapterRegistryError):
    """Raised when an adapter name is already registered."""


@dataclass(frozen=True)
class MarketDataAdapterInfo:
    name: str
    description: str
    read_only: bool = True


AdapterFactory = Callable[[], ReadOnlyMarketDataAdapter]


class MarketDataAdapterRegistry:
    """Thread-safe in-memory registry for read-only market data adapter factories.

    All public methods acquire an internal RLock so concurrent registration and
    lookup from multiple threads is safe. The factory callable is invoked outside
    the lock so that slow or blocking constructors do not hold the registry lock
    for extended periods.
    """

    def __init__(self) -> None:
        self._factories: dict[str, AdapterFactory] = {}
        self._metadata: dict[str, MarketDataAdapterInfo] = {}
        self._lock = threading.RLock()

    def register(self, name: str, factory: AdapterFactory, description: str = "") -> None:
        _validate_adapter_name(name)
        with self._lock:
            if name in self._factories:
                raise DuplicateMarketDataAdapterError(
                    f"market data adapter already registered: {name}"
                )
            self._factories[name] = factory
            self._metadata[name] = MarketDataAdapterInfo(
                name=name,
                description=description,
                read_only=True,
            )

    def list_adapters(self) -> tuple[MarketDataAdapterInfo, ...]:
        with self._lock:
            return tuple(self._metadata[name] for name in sorted(self._metadata))

    def exists(self, name: str) -> bool:
        with self._lock:
            return name in self._factories

    def get_info(self, name: str) -> MarketDataAdapterInfo:
        with self._lock:
            try:
                return self._metadata[name]
            except KeyError as exc:
                raise UnknownMarketDataAdapterError(
                    f"market data adapter is not registered: {name}"
                ) from exc

    def create(self, name: str) -> ReadOnlyMarketDataAdapter:
        with self._lock:
            try:
                factory = self._factories[name]
            except KeyError as exc:
                raise UnknownMarketDataAdapterError(
                    f"market data adapter is not registered: {name}"
                ) from exc
        # Factory called outside the lock: slow/blocking constructors must not
        # hold the registry lock during their execution.
        return factory()


def _validate_adapter_name(name: str) -> None:
    if not _ADAPTER_NAME_RE.fullmatch(name or ""):
        raise MarketDataAdapterRegistryError(
            f"adapter name must match [a-zA-Z][a-zA-Z0-9_-]*; got {name!r}"
        )


def register_ccxt_readonly_adapter(
    registry: MarketDataAdapterRegistry,
    client: object,
    name: str = CCXT_READONLY_ADAPTER_NAME,
) -> None:
    """Register the CCXT read-only skeleton with an injected fake/client object.

    This helper does not import ccxt, create exchange clients, call network, or
    access credentials. The injected client is validated by the skeleton.
    """
    from .market_data_adapters.ccxt_readonly import CcxtReadOnlyMarketDataAdapter

    CcxtReadOnlyMarketDataAdapter(client, name=name)
    registry.register(
        name,
        lambda: CcxtReadOnlyMarketDataAdapter(client, name=name),
        "CCXT read-only adapter skeleton using an injected fake/in-memory client",
    )
