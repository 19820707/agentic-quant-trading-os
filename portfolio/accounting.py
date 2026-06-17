from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from packages.domain import Balance, ExposureSnapshot, Fill, PnL, PortfolioSnapshot, Position, SignalSide, Symbol, Venue
from packages.domain.base import require_aware_datetime, require_non_empty, require_positive


class PortfolioAccountingError(ValueError):
    """Raised when local portfolio accounting input is invalid."""


@dataclass(frozen=True)
class PositionLot:
    symbol: Symbol
    venue: Venue
    quantity: Decimal
    average_entry_price: Decimal
    realized_pnl: Decimal = Decimal("0")
    fees: Decimal = Decimal("0")


@dataclass(frozen=True)
class SideAwareFill:
    fill_id: str
    order_id: str
    symbol: Symbol
    venue: Venue
    side: SignalSide
    filled_at: datetime
    quantity: Decimal
    price: Decimal
    fee: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        require_non_empty(self.fill_id, "fill_id")
        require_non_empty(self.order_id, "order_id")
        require_aware_datetime(self.filled_at, "filled_at")
        require_positive(self.quantity, "quantity")
        require_positive(self.price, "price")
        if self.side is SignalSide.HOLD:
            raise PortfolioAccountingError("HOLD cannot be a fill side")
        if self.fee < Decimal("0"):
            raise PortfolioAccountingError("fee must be non-negative")


@dataclass(frozen=True)
class MarkPrice:
    symbol: Symbol
    venue: Venue
    price: Decimal


def build_portfolio_snapshot(
    *,
    portfolio_id: str,
    timestamp: datetime,
    cash_balances: dict[str, Decimal],
    position_lots: tuple[PositionLot, ...],
    mark_prices: dict[tuple[str, str], Decimal],
) -> PortfolioSnapshot:
    """Build a deterministic local portfolio snapshot.

    This function does not read broker accounts, connect to exchanges, mutate
    state, persist data, approve risk or create orders.
    """

    require_non_empty(portfolio_id, "portfolio_id")
    require_aware_datetime(timestamp, "timestamp")

    positions: list[Position] = []
    by_symbol: dict[str, Decimal] = {}
    by_venue: dict[str, Decimal] = defaultdict(Decimal)
    realized = Decimal("0")
    unrealized = Decimal("0")
    fees = Decimal("0")

    for lot in position_lots:
        mark = _mark_price_for(lot, mark_prices)
        notional = lot.quantity * mark
        lot_unrealized = (mark - lot.average_entry_price) * lot.quantity
        positions.append(
            Position(
                symbol=lot.symbol,
                venue=lot.venue,
                quantity=lot.quantity,
                average_entry_price=lot.average_entry_price,
                unrealized_pnl=lot_unrealized,
                realized_pnl=lot.realized_pnl,
            )
        )
        by_symbol[lot.symbol.value] = by_symbol.get(lot.symbol.value, Decimal("0")) + notional
        by_venue[lot.venue.value] += notional
        realized += lot.realized_pnl
        unrealized += lot_unrealized
        fees += lot.fees

    balances = tuple(
        Balance(asset=asset, total=amount, available=amount, locked=Decimal("0"))
        for asset, amount in sorted(cash_balances.items())
    )
    gross_exposure = sum((abs(value) for value in by_symbol.values()), Decimal("0"))
    net_exposure = sum(by_symbol.values(), Decimal("0"))

    return PortfolioSnapshot(
        portfolio_id=portfolio_id,
        timestamp=timestamp,
        balances=balances,
        positions=tuple(positions),
        exposure=ExposureSnapshot(
            gross_exposure=gross_exposure,
            net_exposure=net_exposure,
            by_symbol=dict(sorted(by_symbol.items())),
            by_venue=dict(sorted(by_venue.items())),
        ),
        pnl=PnL(realized=realized, unrealized=unrealized, fees=fees),
    )


def position_lots_from_fills(fills: tuple[Fill, ...]) -> tuple[PositionLot, ...]:
    """Create long-only aggregate lots from local Fill records.

    The current domain Fill model does not carry side, so this helper treats
    fills as local long exposure fixtures only. Shorting, reductions and closing
    logic require an explicit side-aware fill model in a later PR.
    """

    grouped: dict[tuple[str, str], list[Fill]] = defaultdict(list)
    for fill in fills:
        grouped[(fill.symbol.value, fill.venue.value)].append(fill)

    lots: list[PositionLot] = []
    for (_, _), group in sorted(grouped.items()):
        first = group[0]
        quantity = sum((fill.quantity for fill in group), Decimal("0"))
        if quantity <= Decimal("0"):
            raise PortfolioAccountingError("aggregate fill quantity must be positive")
        notional = sum((fill.quantity * fill.price for fill in group), Decimal("0"))
        fees = sum((fill.fee for fill in group), Decimal("0"))
        lots.append(
            PositionLot(
                symbol=first.symbol,
                venue=first.venue,
                quantity=quantity,
                average_entry_price=notional / quantity,
                fees=fees,
            )
        )
    return tuple(lots)


def reduce_position_lots_from_side_aware_fills(fills: tuple[SideAwareFill, ...]) -> tuple[PositionLot, ...]:
    """Reduce side-aware local fills into signed position lots.

    BUY increases long exposure or reduces shorts. SELL increases short
    exposure or reduces longs. Realized PnL is calculated for closed quantity.

    This is local accounting only. It does not submit orders, reconcile with an
    exchange, approve risk, or mutate any external portfolio.
    """

    grouped: dict[tuple[str, str], list[SideAwareFill]] = defaultdict(list)
    for fill in sorted(fills, key=lambda item: (item.filled_at, item.fill_id)):
        grouped[(fill.symbol.value, fill.venue.value)].append(fill)

    lots: list[PositionLot] = []
    for (_, _), group in sorted(grouped.items()):
        current_quantity = Decimal("0")
        average_entry_price = Decimal("0")
        realized_pnl = Decimal("0")
        fees = Decimal("0")
        first = group[0]

        for fill in group:
            signed_quantity = fill.quantity if fill.side is SignalSide.BUY else -fill.quantity
            fees += fill.fee

            if current_quantity == Decimal("0"):
                current_quantity = signed_quantity
                average_entry_price = fill.price
                continue

            if _same_direction(current_quantity, signed_quantity):
                new_quantity = current_quantity + signed_quantity
                average_entry_price = (
                    (abs(current_quantity) * average_entry_price) + (abs(signed_quantity) * fill.price)
                ) / abs(new_quantity)
                current_quantity = new_quantity
                continue

            closing_quantity = min(abs(current_quantity), abs(signed_quantity))
            realized_pnl += _realized_pnl(
                current_quantity=current_quantity,
                average_entry_price=average_entry_price,
                close_price=fill.price,
                closing_quantity=closing_quantity,
            )
            new_quantity = current_quantity + signed_quantity

            if new_quantity == Decimal("0"):
                current_quantity = Decimal("0")
                average_entry_price = Decimal("0")
            elif _same_direction(current_quantity, new_quantity):
                current_quantity = new_quantity
            else:
                current_quantity = new_quantity
                average_entry_price = fill.price

        lots.append(
            PositionLot(
                symbol=first.symbol,
                venue=first.venue,
                quantity=current_quantity,
                average_entry_price=average_entry_price,
                realized_pnl=realized_pnl,
                fees=fees,
            )
        )
    return tuple(lots)


def _mark_price_for(lot: PositionLot, mark_prices: dict[tuple[str, str], Decimal]) -> Decimal:
    key = (lot.symbol.value, lot.venue.value)
    mark = mark_prices.get(key)
    if mark is None:
        raise PortfolioAccountingError(f"missing mark price for {lot.symbol.value}@{lot.venue.value}")
    if mark <= Decimal("0"):
        raise PortfolioAccountingError("mark price must be positive")
    return mark


def _same_direction(left: Decimal, right: Decimal) -> bool:
    return (left > Decimal("0") and right > Decimal("0")) or (left < Decimal("0") and right < Decimal("0"))


def _realized_pnl(
    *,
    current_quantity: Decimal,
    average_entry_price: Decimal,
    close_price: Decimal,
    closing_quantity: Decimal,
) -> Decimal:
    if current_quantity > Decimal("0"):
        return (close_price - average_entry_price) * closing_quantity
    return (average_entry_price - close_price) * closing_quantity
