from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from packages.domain import AuditEvent, AuditEventType, CausationId, CorrelationId, OrderStatus
from packages.domain.base import deterministic_id, require_aware_datetime, require_non_empty


class OrderStateTransitionError(ValueError):
    """Raised when an order lifecycle transition is invalid."""


TERMINAL_STATUSES = frozenset(
    {
        OrderStatus.FILLED,
        OrderStatus.CANCELED,
        OrderStatus.REJECTED,
        OrderStatus.EXPIRED,
        OrderStatus.FAILED,
    }
)

ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.CREATED: frozenset({OrderStatus.RISK_CHECKED, OrderStatus.REJECTED, OrderStatus.FAILED}),
    OrderStatus.RISK_CHECKED: frozenset({OrderStatus.SUBMITTED, OrderStatus.REJECTED, OrderStatus.FAILED}),
    OrderStatus.SUBMITTED: frozenset({OrderStatus.ACKNOWLEDGED, OrderStatus.REJECTED, OrderStatus.FAILED}),
    OrderStatus.ACKNOWLEDGED: frozenset(
        {
            OrderStatus.PARTIALLY_FILLED,
            OrderStatus.FILLED,
            OrderStatus.CANCELED,
            OrderStatus.EXPIRED,
            OrderStatus.FAILED,
        }
    ),
    OrderStatus.PARTIALLY_FILLED: frozenset({OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED, OrderStatus.CANCELED, OrderStatus.FAILED}),
    OrderStatus.FILLED: frozenset(),
    OrderStatus.CANCELED: frozenset(),
    OrderStatus.REJECTED: frozenset(),
    OrderStatus.EXPIRED: frozenset(),
    OrderStatus.FAILED: frozenset(),
}


@dataclass(frozen=True)
class OrderStateTransition:
    order_id: str
    previous_status: OrderStatus
    next_status: OrderStatus
    occurred_at: datetime
    reason: str
    correlation_id: CorrelationId
    causation_id: CausationId | None = None

    def __post_init__(self) -> None:
        require_non_empty(self.order_id, "order_id")
        require_aware_datetime(self.occurred_at, "occurred_at")
        require_non_empty(self.reason, "reason")
        assert_transition_allowed(self.previous_status, self.next_status)

    @property
    def transition_id(self) -> str:
        return deterministic_id(
            "ordst",
            self.order_id,
            self.previous_status.value,
            self.next_status.value,
            self.occurred_at.isoformat(),
        )

    def to_audit_event(self) -> AuditEvent:
        return AuditEvent(
            audit_event_id=deterministic_id("audit", self.transition_id),
            event_type=AuditEventType.ORDER_STATE_CHANGED,
            occurred_at=self.occurred_at,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            actor="oms-state-machine",
            subject=self.order_id,
            outcome=self.next_status.value,
            metadata={
                "previous_status": self.previous_status.value,
                "next_status": self.next_status.value,
                "reason": self.reason,
            },
        )


def allowed_next_statuses(status: OrderStatus) -> frozenset[OrderStatus]:
    return ALLOWED_TRANSITIONS[status]


def assert_transition_allowed(previous_status: OrderStatus, next_status: OrderStatus) -> None:
    if previous_status in TERMINAL_STATUSES:
        raise OrderStateTransitionError(f"terminal order status cannot transition: {previous_status.value}")
    if next_status not in ALLOWED_TRANSITIONS[previous_status]:
        raise OrderStateTransitionError(
            f"invalid order status transition: {previous_status.value} -> {next_status.value}"
        )
