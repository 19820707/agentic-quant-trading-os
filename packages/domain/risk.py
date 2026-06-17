from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .base import SerializableModel, require_aware_datetime, require_non_empty, require_non_negative
from .orders import OrderIntent


class RiskDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class RiskViolation(SerializableModel):
    rule_id: str
    message: str
    severity: str

    def __post_init__(self) -> None:
        require_non_empty(self.rule_id, "rule_id")
        require_non_empty(self.message, "message")
        require_non_empty(self.severity, "severity")


@dataclass(frozen=True)
class RiskCheckRequest(SerializableModel):
    risk_check_request_id: str
    order_intent: OrderIntent
    portfolio_id: str
    requested_at: datetime

    def __post_init__(self) -> None:
        require_non_empty(self.risk_check_request_id, "risk_check_request_id")
        require_non_empty(self.portfolio_id, "portfolio_id")
        require_aware_datetime(self.requested_at, "requested_at")


@dataclass(frozen=True)
class RiskCheckResult(SerializableModel):
    risk_check_result_id: str
    request_id: str
    decision: RiskDecision
    checked_at: datetime
    violations: tuple[RiskViolation, ...]
    approved_quantity: Decimal = Decimal("0")
    approved_notional: Decimal = Decimal("0")
    approved_for_execution: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.risk_check_result_id, "risk_check_result_id")
        require_non_empty(self.request_id, "request_id")
        require_aware_datetime(self.checked_at, "checked_at")
        require_non_negative(self.approved_quantity, "approved_quantity")
        require_non_negative(self.approved_notional, "approved_notional")
        if self.decision is not RiskDecision.APPROVE and self.approved_for_execution:
            raise ValueError("only APPROVE decisions can be approved for execution")
