from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from packages.domain import PortfolioSnapshot
from packages.domain.base import require_aware_datetime, require_non_empty, require_non_negative
from portfolio.accounting import SideAwareFill, build_portfolio_snapshot, reduce_position_lots_from_side_aware_fills

from .simulator import PaperTradeResult, PaperTradingError


@dataclass(frozen=True)
class PaperAccountState:
    portfolio_id: str
    cash_asset: str
    cash_balance: Decimal
    side_aware_fills: tuple[SideAwareFill, ...]
    updated_at: datetime
    live_trading_enabled: bool = False
    network_used: bool = False
    credentials_used: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.portfolio_id, "portfolio_id")
        require_non_empty(self.cash_asset, "cash_asset")
        require_non_negative(self.cash_balance, "cash_balance")
        require_aware_datetime(self.updated_at, "updated_at")
        if self.live_trading_enabled or self.network_used or self.credentials_used:
            raise PaperTradingError("paper account state must not use live trading, network or credentials")


def apply_paper_trade_result(account: PaperAccountState, result: PaperTradeResult) -> PaperAccountState:
    cash = account.cash_balance
    new_side_aware_fills = list(account.side_aware_fills)

    for fill in result.fills:
        notional = fill.quantity * fill.price
        if result.order.side.value == "BUY":
            cash -= notional + fill.fee
        elif result.order.side.value == "SELL":
            cash += notional - fill.fee
        else:
            raise PaperTradingError("paper account cannot apply HOLD fills")
        if cash < Decimal("0"):
            raise PaperTradingError("paper account cash cannot become negative")
        new_side_aware_fills.append(
            SideAwareFill(
                fill_id=fill.fill_id,
                order_id=fill.order_id,
                symbol=fill.symbol,
                venue=fill.venue,
                side=result.order.side,
                filled_at=fill.filled_at,
                quantity=fill.quantity,
                price=fill.price,
                fee=fill.fee,
            )
        )

    return PaperAccountState(
        portfolio_id=account.portfolio_id,
        cash_asset=account.cash_asset,
        cash_balance=cash,
        side_aware_fills=tuple(new_side_aware_fills),
        updated_at=result.execution_report.reported_at,
    )


def paper_account_portfolio_snapshot(
    account: PaperAccountState,
    *,
    timestamp: datetime,
    mark_prices: dict[tuple[str, str], Decimal],
) -> PortfolioSnapshot:
    require_aware_datetime(timestamp, "timestamp")
    lots = reduce_position_lots_from_side_aware_fills(account.side_aware_fills)
    return build_portfolio_snapshot(
        portfolio_id=account.portfolio_id,
        timestamp=timestamp,
        cash_balances={account.cash_asset: account.cash_balance},
        position_lots=lots,
        mark_prices=mark_prices,
    )
