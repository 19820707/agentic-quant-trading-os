"""Read-only market data adapter implementations and factory guards."""

from .ccxt_factory import (
    ALLOWED_PUBLIC_EXCHANGES,
    CCXTDependencyUnavailable,
    CCXTExchangeNotAllowlisted,
    CCXTFeatureDisabled,
    create_ccxt_public_client,
)
from .ccxt_readonly import (
    CcxtConversionError,
    CcxtReadOnlyMarketDataAdapter,
    PROHIBITED_CLIENT_METHODS,
    UnsafeCcxtClientError,
)

__all__ = [
    "ALLOWED_PUBLIC_EXCHANGES",
    "CCXTDependencyUnavailable",
    "CCXTExchangeNotAllowlisted",
    "CCXTFeatureDisabled",
    "CcxtConversionError",
    "CcxtReadOnlyMarketDataAdapter",
    "PROHIBITED_CLIENT_METHODS",
    "UnsafeCcxtClientError",
    "create_ccxt_public_client",
]
