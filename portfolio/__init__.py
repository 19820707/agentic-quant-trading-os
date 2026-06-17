"""Portfolio accounting boundary.

Current implementation is local deterministic accounting only. It does not read
broker accounts, mutate portfolios externally or reconcile with exchanges.
"""

from .accounting import (
    MarkPrice,
    PortfolioAccountingError,
    PositionLot,
    SideAwareFill,
    build_portfolio_snapshot,
    position_lots_from_fills,
    reduce_position_lots_from_side_aware_fills,
)

__all__ = [
    "MarkPrice",
    "PortfolioAccountingError",
    "PositionLot",
    "SideAwareFill",
    "build_portfolio_snapshot",
    "position_lots_from_fills",
    "reduce_position_lots_from_side_aware_fills",
]
