from __future__ import annotations


class MarketDataError(RuntimeError):
    """Base class for local market data layer errors."""


class MarketDataConnectionError(MarketDataError):
    """Raised when an adapter operation requires an active connection."""


class MarketDataSubscriptionError(MarketDataError):
    """Raised when a subscription request is invalid."""


class MarketDataNormalizationError(MarketDataError):
    """Raised when raw market data cannot be normalized safely."""


class MarketDataReplayError(MarketDataError):
    """Raised when local replay data is invalid or unavailable."""


class MarketDataRateLimitError(MarketDataError):
    """Raised when a local rate-limit policy blocks an operation."""
