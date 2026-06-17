from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from oms.state_machine import OrderStateTransition
from packages.domain import (
    AuditEvent,
    CausationId,
    CorrelationId,
    ExecutionReport,
    Fill,
    Order,
    OrderIntent,
    OrderStatus,
    OrderType,
    RiskCheckResult,
    RiskDecision,
    SignalSide,
)
from packages.domain.base import deterministic_id, require_aware_datetime, require_non_empty, require_non_negative, require_positive
from risk.evaluator import PriceReference


class PaperTradingError(ValueError):
    """Raised when paper trading cannot proceed safely."""


@dataclass(frozen=True)
class PaperRuntimeConfig:
    paper_runtime_enabled: bool = False
    live_trading_enabled: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False
    fee_bps: Decimal = Decimal("0")
    slippage_bps: Decimal = Decimal("0")
    max_fill_fraction: Decimal = Decimal("1")

    def __post_init__(self) -> None:
        if not self.paper_runtime_enabled:
            raise PaperTradingError("paper runtime must be explicitly enabled")
        if self.live_trading_enabled:
            raise PaperTradingError("live trading must remain disabled for paper runtime")
        if self.network_allowed:
            raise PaperTradingError("paper runtime must not allow network access")
        if self.credentials_allowed:
            raise PaperTradingError("paper runtime must not allow credentials")
        require_non_negative(self.fee_bps, "fee_bps")
        require_non_negative(self.slippage_bps, "slippage_bps")
        require_positive(self.max_fill_fraction, "max_fill_fraction")
        if self.max_fill_fraction > Decimal("1"):
            raise PaperTradingError("max_fill_fraction must be <= 1")


@dataclass(frozen=True)
class PaperTradeResult:
    order: Order
    fills: tuple[Fill, ...]
    execution_report: ExecutionReport
    audit_events: tuple[AuditEvent, ...]
    runtime_mode: str = "paper_local_only"
    live_trading_used: bool = False
    network_used: bool = False
    credentials_used: bool = False

    def __post_init__(self) -> None:
        if self.runtime_mode != "paper_local_only":
            raise PaperTradingError("paper trade result must remain paper_local_only")
        if self.live_trading_used or self.network_used or self.credentials_used:
            raise PaperTradingError("paper trade result cannot use live trading, network or credentials")


def simulate_paper_trade(
    *,
    intent: OrderIntent,
    risk_result: RiskCheckResult,
    price_reference: PriceReference,
    config: PaperRuntimeConfig,
    evaluated_at: datetime,
    correlation_id: CorrelationId,
) -> PaperTradeResult:
    """Run a deterministic local paper fill path after risk approval.

    This function deliberately does not talk to brokers, exchanges, sockets or
    credentials. It is a local harness for exercising OMS lifecycle semantics.
    """

    require_aware_datetime(evaluated_at, "evaluated_at")
    require_non_empty(correlation_id.value, "correlation_id")
    _require_paper_safe_approval(intent, risk_result)

    order = Order(
        order_id=deterministic_id("paper_order", intent.order_intent_id, risk_result.risk_check_result_id),
        client_order_id=deterministic_id("paper_client", intent.order_intent_id),
        symbol=intent.symbol,
        venue=intent.venue,
        side=intent.side,
        order_type=intent.order_type,
        status=OrderStatus.CREATED,
        quantity=intent.quantity,
        created_at=evaluated_at,
        time_in_force=intent.time_in_force,
    )

    transitions = [
        _transition(order.order_id, OrderStatus.CREATED, OrderStatus.RISK_CHECKED, evaluated_at, "risk_result_verified", correlation_id),
        _transition(order.order_id, OrderStatus.RISK_CHECKED, OrderStatus.SUBMITTED, evaluated_at, "paper_local_submission", correlation_id),
        _transition(order.order_id, OrderStatus.SUBMITTED, OrderStatus.ACKNOWLEDGED, evaluated_at, "paper_local_acknowledged", correlation_id),
    ]

    executable, fill_price = _determine_fill_price(intent, price_reference, config)
    if not executable:
        report = ExecutionReport(
            execution_report_id=deterministic_id("paper_report", order.order_id, "resting", evaluated_at.isoformat()),
            order_id=order.order_id,
            status=OrderStatus.ACKNOWLEDGED,
            reported_at=evaluated_at,
            filled_quantity=Decimal("0"),
            remaining_quantity=intent.quantity,
            average_fill_price=None,
            client_order_id=order.client_order_id,
            requested_quantity=intent.quantity,
            reconciliation_required=False,
        )
        acknowledged = _replace_order_status(order, OrderStatus.ACKNOWLEDGED)
        return PaperTradeResult(
            order=acknowledged,
            fills=(),
            execution_report=report,
            audit_events=tuple(transition.to_audit_event() for transition in transitions),
        )

    fill_quantity = intent.quantity * config.max_fill_fraction
    remaining_quantity = intent.quantity - fill_quantity
    fee = fill_quantity * fill_price * config.fee_bps / Decimal("10000")
    fill = Fill(
        fill_id=deterministic_id("paper_fill", order.order_id, fill_quantity, fill_price, evaluated_at.isoformat()),
        order_id=order.order_id,
        symbol=order.symbol,
        venue=order.venue,
        filled_at=evaluated_at,
        quantity=fill_quantity,
        price=fill_price,
        fee=fee,
    )
    final_status = OrderStatus.FILLED if remaining_quantity == Decimal("0") else OrderStatus.PARTIALLY_FILLED
    transitions.append(
        _transition(order.order_id, OrderStatus.ACKNOWLEDGED, final_status, evaluated_at, "paper_local_fill_model", correlation_id)
    )
    report = ExecutionReport(
        execution_report_id=deterministic_id("paper_report", order.order_id, final_status.value, evaluated_at.isoformat()),
        order_id=order.order_id,
        status=final_status,
        reported_at=evaluated_at,
        filled_quantity=fill_quantity,
        remaining_quantity=remaining_quantity,
        average_fill_price=fill_price,
        client_order_id=order.client_order_id,
        requested_quantity=intent.quantity,
        reconciliation_required=False,
    )
    return PaperTradeResult(
        order=_replace_order_status(order, final_status),
        fills=(fill,),
        execution_report=report,
        audit_events=tuple(transition.to_audit_event() for transition in transitions),
    )


def _require_paper_safe_approval(intent: OrderIntent, risk_result: RiskCheckResult) -> None:
    if risk_result.decision is not RiskDecision.APPROVE:
        raise PaperTradingError("paper runtime requires an APPROVE risk decision")
    if not risk_result.approved_for_execution:
        raise PaperTradingError("paper runtime requires approved_for_execution")
    if risk_result.approved_quantity < intent.quantity:
        raise PaperTradingError("approved quantity is lower than intent quantity")


def _determine_fill_price(
    intent: OrderIntent,
    price_reference: PriceReference,
    config: PaperRuntimeConfig,
) -> tuple[bool, Decimal]:
    if intent.symbol != price_reference.symbol or intent.venue != price_reference.venue:
        raise PaperTradingError("price reference must match paper order intent")

    slippage = config.slippage_bps / Decimal("10000")
    if intent.side is SignalSide.BUY:
        slipped = price_reference.price * (Decimal("1") + slippage)
        if intent.order_type is OrderType.LIMIT and intent.limit_price is not None:
            if intent.limit_price < price_reference.price:
                return False, intent.limit_price
            return True, min(intent.limit_price, slipped)
        return True, slipped

    if intent.side is SignalSide.SELL:
        slipped = price_reference.price * (Decimal("1") - slippage)
        if intent.order_type is OrderType.LIMIT and intent.limit_price is not None:
            if intent.limit_price > price_reference.price:
                return False, intent.limit_price
            return True, max(intent.limit_price, slipped)
        return True, slipped

    raise PaperTradingError("HOLD intent cannot be paper traded")


def _transition(
    order_id: str,
    previous: OrderStatus,
    next_status: OrderStatus,
    occurred_at: datetime,
    reason: str,
    correlation_id: CorrelationId,
) -> OrderStateTransition:
    return OrderStateTransition(
        order_id=order_id,
        previous_status=previous,
        next_status=next_status,
        occurred_at=occurred_at,
        reason=reason,
        correlation_id=correlation_id,
        causation_id=CausationId(order_id),
    )


def _replace_order_status(order: Order, status: OrderStatus) -> Order:
    return Order(
        order_id=order.order_id,
        client_order_id=order.client_order_id,
        symbol=order.symbol,
        venue=order.venue,
        side=order.side,
        order_type=order.order_type,
        status=status,
        quantity=order.quantity,
        created_at=order.created_at,
        time_in_force=order.time_in_force,
    )
