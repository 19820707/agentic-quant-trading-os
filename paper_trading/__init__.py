"""Paper trading boundary placeholders.

No simulated exchange runtime is implemented here yet.
"""
from .account import PaperAccountState, apply_paper_trade_result, paper_account_portfolio_snapshot
from .simulator import PaperRuntimeConfig, PaperTradeResult, PaperTradingError, simulate_paper_trade

__all__ = [
    "PaperAccountState",
    "PaperRuntimeConfig",
    "PaperTradeResult",
    "PaperTradingError",
    "apply_paper_trade_result",
    "paper_account_portfolio_snapshot",
    "simulate_paper_trade",
]
