"""Local market data abstraction layer.

This package provides deterministic mock/replay adapters and storage hooks. It
does not connect to real exchanges, brokers, paid data feeds or WebSockets.
"""

from .adapters import BaseLocalMarketDataAdapter, MockMarketDataAdapter, ReplayMarketDataAdapter, write_replay_file
from .errors import (
    MarketDataConnectionError,
    MarketDataError,
    MarketDataNormalizationError,
    MarketDataRateLimitError,
    MarketDataReplayError,
    MarketDataSubscriptionError,
)
from .interfaces import MarketDataAdapter, MarketDataEvent, MarketDataWriter
from .normalization import event_to_record, normalize_event
from .resilience import AdapterHealth, AdapterHealthState, HeartbeatMonitor, RateLimitPolicy, ReconnectPolicy
from .storage import InMemoryMarketDataWriter, JsonLinesMarketDataWriter

__all__ = [
    "AdapterHealth",
    "AdapterHealthState",
    "BaseLocalMarketDataAdapter",
    "HeartbeatMonitor",
    "InMemoryMarketDataWriter",
    "JsonLinesMarketDataWriter",
    "MarketDataAdapter",
    "MarketDataConnectionError",
    "MarketDataError",
    "MarketDataEvent",
    "MarketDataNormalizationError",
    "MarketDataRateLimitError",
    "MarketDataReplayError",
    "MarketDataSubscriptionError",
    "MarketDataWriter",
    "MockMarketDataAdapter",
    "RateLimitPolicy",
    "ReconnectPolicy",
    "ReplayMarketDataAdapter",
    "event_to_record",
    "normalize_event",
    "write_replay_file",
]
