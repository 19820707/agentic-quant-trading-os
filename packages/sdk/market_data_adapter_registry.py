from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .market_data_adapter import ReadOnlyMarketDataAdapter


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
    """In-memory registry for read-only market data adapter factories."""

    def __init__(self) -> None:
        self._factories: dict[str, AdapterFactory] = {}
        self._metadata: dict[str, MarketDataAdapterInfo] = {}

    def register(self, name: str, factory: AdapterFactory, description: str = "") -> None:
        self._validate_name(name)
        if name in self._factories:
            raise DuplicateMarketDataAdapterError(f"market data adapter already registered: {name}")

        self._factories[name] = factory
        self._metadata[name] = MarketDataAdapterInfo(
            name=name,
            description=description,
            read_only=True,
        )

    def list_adapters(self) -> tuple[MarketDataAdapterInfo, ...]:
        return tuple(self._metadata[name] for name in sorted(self._metadata))

    def exists(self, name: str) -> bool:
        return name in self._factories

    def get_info(self, name: str) -> MarketDataAdapterInfo:
        try:
            return self._metadata[name]
        except KeyError as exc:
            raise UnknownMarketDataAdapterError(f"market data adapter is not registered: {name}") from exc

    def create(self, name: str) -> ReadOnlyMarketDataAdapter:
        try:
            factory = self._factories[name]
        except KeyError as exc:
            raise UnknownMarketDataAdapterError(f"market data adapter is not registered: {name}") from exc
        return factory()

    def _validate_name(self, name: str) -> None:
        if not name:
            raise MarketDataAdapterRegistryError("adapter name is required")
        if "/" in name or "\\" in name or ".." in name:
            raise MarketDataAdapterRegistryError("adapter name must be a simple identifier")
