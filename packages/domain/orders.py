from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .base import (
    SerializableModel,
    deterministic_id,
    parse_datetime,
    parse_decimal,
    require_aware_datetime,
    require_non_empty,
    require_non_negative,
    require_positive,
)
from .market_data import Symbol, Venue
from .strategy import Signal, SignalSide, StrategyId


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    RISK_CHECKED = "RISK_CHECKED"
    SUBMITTED = "SUBMITTED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    DAY = "DAY"
    GTD = "GTD"


class ExecutionMode(str, Enum):
    PAPER = "PAPER"
    CONTROLLED_LIVE = "CONTROLLED_LIVE"


class ApprovedOrderStatus(str, Enum):
    APPROVED = "APPROVED"
    QUEUED_FOR_PAPER = "QUEUED_FOR_PAPER"
    QUEUED_FOR_EXECUTION = "QUEUED_FOR_EXECUTION"
    CANCELLED_BEFORE_EXECUTION = "CANCELLED_BEFORE_EXECUTION"


@dataclass(frozen=True)
class OrderIntent(SerializableModel):
    order_intent_id: str
    signal_id: str
    strategy_id: StrategyId
    symbol: Symbol
    venue: Venue
    side: SignalSide
    order_type: OrderType
    quantity: Decimal
    created_at: datetime
    time_in_force: TimeInForce = TimeInForce.GTC
    limit_price: Decimal | None = None
    risk_required: bool = True

    def __post_init__(self) -> None:
        require_non_empty(self.order_intent_id, "order_intent_id")
        require_non_empty(self.signal_id, "signal_id")
        require_positive(self.quantity, "quantity")
        require_aware_datetime(self.created_at, "created_at")
        if self.limit_price is not None:
            require_positive(self.limit_price, "limit_price")
        if not self.risk_required:
            raise ValueError("OrderIntent must require risk review")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "OrderIntent":
        limit_price = data.get("limit_price")
        return cls(
            order_intent_id=str(data["order_intent_id"]),
            signal_id=str(data["signal_id"]),
            strategy_id=StrategyId(str(data["strategy_id"]["value"])),
            symbol=Symbol(str(data["symbol"]["value"])),
            venue=Venue(str(data["venue"]["value"])),
            side=SignalSide(str(data["side"])),
            order_type=OrderType(str(data["order_type"])),
            quantity=parse_decimal(data["quantity"], "quantity"),
            created_at=parse_datetime(data["created_at"], "created_at"),
            time_in_force=TimeInForce(str(data["time_in_force"])),
            limit_price=None if limit_price is None else parse_decimal(limit_price, "limit_price"),
            risk_required=bool(data["risk_required"]),
        )

    @classmethod
    def from_signal(
        cls,
        signal: Signal,
        *,
        quantity: Decimal,
        order_type: OrderType,
        created_at: datetime,
        time_in_force: TimeInForce = TimeInForce.GTC,
        limit_price: Decimal | None = None,
    ) -> "OrderIntent":
        if signal.side is SignalSide.HOLD:
            raise ValueError("HOLD signal cannot create an OrderIntent")
        order_intent_id = deterministic_id(
            "intent",
            signal.signal_id,
            signal.strategy_id.value,
            signal.symbol.value,
            signal.venue.value,
            signal.side.value,
            str(quantity),
            created_at.isoformat(),
        )
        return cls(
            order_intent_id=order_intent_id,
            signal_id=signal.signal_id,
            strategy_id=signal.strategy_id,
            symbol=signal.symbol,
            venue=signal.venue,
            side=signal.side,
            order_type=order_type,
            quantity=quantity,
            created_at=created_at,
            time_in_force=time_in_force,
            limit_price=limit_price,
        )


@dataclass(frozen=True)
class ApprovedOrder(SerializableModel):
    """Risk-gated order object accepted by future execution boundaries.

    This model is paper-only in the current scaffold. It is not a broker API
    request and does not submit, cancel, modify or route orders.
    """

    approved_order_id: str
    order_intent_id: str
    risk_decision_id: str
    strategy_id: StrategyId
    symbol: Symbol
    venue: Venue
    side: SignalSide
    order_type: OrderType
    approved_quantity: Decimal
    approved_at: datetime
    approved_by: str
    time_in_force: TimeInForce = TimeInForce.GTC
    client_order_id: str | None = None
    execution_allowed: bool = True
    execution_mode: ExecutionMode = ExecutionMode.PAPER
    status: ApprovedOrderStatus = ApprovedOrderStatus.QUEUED_FOR_PAPER
    limit_price: Decimal | None = None
    max_slippage_bps: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        require_non_empty(self.approved_order_id, "approved_order_id")
        require_non_empty(self.order_intent_id, "order_intent_id")
        require_non_empty(self.risk_decision_id, "risk_decision_id")
        require_positive(self.approved_quantity, "approved_quantity")
        require_aware_datetime(self.approved_at, "approved_at")
        require_non_empty(self.approved_by, "approved_by")
        require_non_negative(self.max_slippage_bps, "max_slippage_bps")
        if self.client_order_id is not None:
            require_non_empty(self.client_order_id, "client_order_id")
        if self.limit_price is not None:
            require_positive(self.limit_price, "limit_price")
        if not self.execution_allowed:
            raise ValueError("ApprovedOrder must be execution_allowed by deterministic risk")
        if self.execution_mode is not ExecutionMode.PAPER:
            raise ValueError("controlled live ApprovedOrder is not enabled in scaffold mode")
        if self.status not in {ApprovedOrderStatus.APPROVED, ApprovedOrderStatus.QUEUED_FOR_PAPER}:
            raise ValueError("ApprovedOrder scaffold may only be APPROVED or QUEUED_FOR_PAPER")

    @classmethod
    def from_intent_and_risk_result(
        cls,
        intent: OrderIntent,
        risk_result: object,
        *,
        approved_at: datetime,
        approved_by: str,
        status: ApprovedOrderStatus = ApprovedOrderStatus.QUEUED_FOR_PAPER,
    ) -> "ApprovedOrder":
        from .risk import RiskCheckResult, RiskDecision

        if not isinstance(risk_result, RiskCheckResult):
            raise ValueError("risk_result must be RiskCheckResult")
        if risk_result.decision is not RiskDecision.APPROVE:
            raise ValueError("ApprovedOrder requires APPROVE risk decision")
        if not risk_result.approved_for_execution:
            raise ValueError("ApprovedOrder requires approved_for_execution risk result")
        if risk_result.approved_quantity <= Decimal("0"):
            raise ValueError("ApprovedOrder requires positive approved quantity")
        if risk_result.approved_quantity > intent.quantity:
            raise ValueError("ApprovedOrder cannot exceed OrderIntent quantity")
        approved_order_id = deterministic_id(
            "approved",
            intent.order_intent_id,
            risk_result.risk_check_result_id,
            approved_at.isoformat(),
            "paper",
        )
        return cls(
            approved_order_id=approved_order_id,
            order_intent_id=intent.order_intent_id,
            risk_decision_id=risk_result.risk_check_result_id,
            strategy_id=intent.strategy_id,
            symbol=intent.symbol,
            venue=intent.venue,
            side=intent.side,
            order_type=intent.order_type,
            approved_quantity=risk_result.approved_quantity,
            approved_at=approved_at,
            approved_by=approved_by,
            time_in_force=intent.time_in_force,
            client_order_id=deterministic_id("client", approved_order_id),
            execution_allowed=True,
            execution_mode=ExecutionMode.PAPER,
            status=status,
            limit_price=intent.limit_price,
        )


@dataclass(frozen=True)
class OrderRequest(SerializableModel):
    order_request_id: str
    order_intent_id: str
    approved_order_id: str
    symbol: Symbol
    venue: Venue
    side: SignalSide
    order_type: OrderType
    quantity: Decimal
    created_at: datetime
    time_in_force: TimeInForce
    limit_price: Decimal | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.order_request_id, "order_request_id")
        require_non_empty(self.order_intent_id, "order_intent_id")
        require_non_empty(self.approved_order_id, "approved_order_id")
        require_positive(self.quantity, "quantity")
        require_aware_datetime(self.created_at, "created_at")
        if self.limit_price is not None:
            require_positive(self.limit_price, "limit_price")

    @classmethod
    def from_approved_order(
        cls,
        approved_order: ApprovedOrder,
        *,
        created_at: datetime,
    ) -> "OrderRequest":
        if approved_order.execution_mode is not ExecutionMode.PAPER:
            raise ValueError("OrderRequest scaffold accepts only PAPER ApprovedOrder")
        if not approved_order.execution_allowed:
            raise ValueError("OrderRequest requires execution_allowed ApprovedOrder")
        return cls(
            order_request_id=deterministic_id(
                "order_request",
                approved_order.approved_order_id,
                created_at.isoformat(),
            ),
            order_intent_id=approved_order.order_intent_id,
            approved_order_id=approved_order.approved_order_id,
            symbol=approved_order.symbol,
            venue=approved_order.venue,
            side=approved_order.side,
            order_type=approved_order.order_type,
            quantity=approved_order.approved_quantity,
            created_at=created_at,
            time_in_force=approved_order.time_in_force,
            limit_price=approved_order.limit_price,
        )


@dataclass(frozen=True)
class Order(SerializableModel):
    order_id: str
    client_order_id: str
    symbol: Symbol
    venue: Venue
    side: SignalSide
    order_type: OrderType
    status: OrderStatus
    quantity: Decimal
    created_at: datetime
    time_in_force: TimeInForce

    def __post_init__(self) -> None:
        require_non_empty(self.order_id, "order_id")
        require_non_empty(self.client_order_id, "client_order_id")
        require_positive(self.quantity, "quantity")
        require_aware_datetime(self.created_at, "created_at")


@dataclass(frozen=True)
class Fill(SerializableModel):
    fill_id: str
    order_id: str
    symbol: Symbol
    venue: Venue
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
        if self.fee < Decimal("0"):
            raise ValueError("fee must be non-negative")


@dataclass(frozen=True)
class ExecutionReport(SerializableModel):
    execution_report_id: str
    order_id: str
    status: OrderStatus
    reported_at: datetime
    filled_quantity: Decimal
    remaining_quantity: Decimal
    average_fill_price: Decimal | None = None
    approved_order_id: str | None = None
    execution_order_id: str | None = None
    client_order_id: str | None = None
    requested_quantity: Decimal | None = None
    reconciliation_required: bool = True

    def __post_init__(self) -> None:
        require_non_empty(self.execution_report_id, "execution_report_id")
        require_non_empty(self.order_id, "order_id")
        require_aware_datetime(self.reported_at, "reported_at")
        require_non_negative(self.filled_quantity, "filled_quantity")
        require_non_negative(self.remaining_quantity, "remaining_quantity")
        if self.average_fill_price is not None:
            require_positive(self.average_fill_price, "average_fill_price")
        if self.approved_order_id is not None:
            require_non_empty(self.approved_order_id, "approved_order_id")
        if self.execution_order_id is not None:
            require_non_empty(self.execution_order_id, "execution_order_id")
        if self.client_order_id is not None:
            require_non_empty(self.client_order_id, "client_order_id")
        if self.requested_quantity is not None:
            require_positive(self.requested_quantity, "requested_quantity")
            if self.filled_quantity + self.remaining_quantity != self.requested_quantity:
                raise ValueError("filled plus remaining quantity must equal requested quantity")
        if self.filled_quantity > Decimal("0") and self.average_fill_price is None:
            raise ValueError("average_fill_price is required when filled_quantity is positive")
        if self.filled_quantity == Decimal("0") and self.average_fill_price is not None:
            raise ValueError("average_fill_price requires positive filled_quantity")
        if self.status is OrderStatus.FILLED:
            if self.filled_quantity <= Decimal("0") or self.remaining_quantity != Decimal("0"):
                raise ValueError("FILLED reports require positive filled quantity and zero remaining quantity")
        if self.status is OrderStatus.PARTIALLY_FILLED:
            if self.filled_quantity <= Decimal("0") or self.remaining_quantity <= Decimal("0"):
                raise ValueError("PARTIALLY_FILLED reports require positive filled and remaining quantities")
        if self.status in {OrderStatus.REJECTED, OrderStatus.FAILED}:
            if self.filled_quantity != Decimal("0") or self.average_fill_price is not None:
                raise ValueError("REJECTED and FAILED reports cannot include fills")
