from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Protocol, runtime_checkable

from packages.domain import ExecutionReport, OrderRequest, OrderStatus
from packages.domain.base import deterministic_id, require_aware_datetime, require_non_empty


class ExecutionAdapterError(ValueError):
    """Raised when an execution adapter rejects unsafe operation."""


class ExecutionAdapterState(str, Enum):
    DISABLED = "DISABLED"
    PAPER_ONLY = "PAPER_ONLY"
    LIVE_BLOCKED = "LIVE_BLOCKED"


PROHIBITED_EXECUTION_ADAPTER_METHOD_NAMES = frozenset(
    {
        "buy",
        "sell",
        "order",
        "submit_order",
        "cancel_order",
        "edit_order",
        "withdraw",
        "transfer",
        "execute",
        "place_order",
        "create_order",
    }
)


@dataclass(frozen=True)
class ExecutionAdapterConfig:
    adapter_name: str
    enabled: bool = False
    live_trading_enabled: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False
    paper_only: bool = True

    def __post_init__(self) -> None:
        require_non_empty(self.adapter_name, "adapter_name")
        if self.live_trading_enabled:
            raise ExecutionAdapterError("live trading is not approved for execution adapters")
        if self.network_allowed:
            raise ExecutionAdapterError("network access is not approved for execution adapters")
        if self.credentials_allowed:
            raise ExecutionAdapterError("credentials are not approved for execution adapters")
        if not self.paper_only:
            raise ExecutionAdapterError("execution adapter must remain paper_only in scaffold mode")


@dataclass(frozen=True)
class ExecutionAdapterHealth:
    adapter_name: str
    state: ExecutionAdapterState
    checked_at: datetime
    live_trading_enabled: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False
    message: str = "fail_closed"

    def __post_init__(self) -> None:
        require_non_empty(self.adapter_name, "adapter_name")
        require_aware_datetime(self.checked_at, "checked_at")
        if self.live_trading_enabled or self.network_allowed or self.credentials_allowed:
            raise ExecutionAdapterError("execution adapter health cannot report unsafe enabled state")


@runtime_checkable
class ExecutionAdapter(Protocol):
    def health(self) -> ExecutionAdapterHealth:
        raise NotImplementedError

    def review_order_request(self, request: OrderRequest, *, requested_at: datetime | None = None) -> ExecutionReport:
        raise NotImplementedError


class FailClosedExecutionAdapter:
    """Local adapter boundary that rejects all order requests by design."""

    def __init__(self, config: ExecutionAdapterConfig) -> None:
        validate_execution_adapter_surface(self)
        self.config = config

    def health(self) -> ExecutionAdapterHealth:
        if not self.config.enabled:
            state = ExecutionAdapterState.DISABLED
            message = "adapter_disabled"
        else:
            state = ExecutionAdapterState.PAPER_ONLY
            message = "adapter_enabled_for_review_only"
        return ExecutionAdapterHealth(
            adapter_name=self.config.adapter_name,
            state=state,
            checked_at=datetime.now(timezone.utc),
            live_trading_enabled=False,
            network_allowed=False,
            credentials_allowed=False,
            message=message,
        )

    def review_order_request(self, request: OrderRequest, *, requested_at: datetime | None = None) -> ExecutionReport:
        timestamp = requested_at or datetime.now(timezone.utc)
        require_aware_datetime(timestamp, "requested_at")
        return ExecutionReport(
            execution_report_id=deterministic_id(
                "exec_report",
                self.config.adapter_name,
                request.order_request_id,
                timestamp.isoformat(),
                "fail_closed",
            ),
            order_id=request.order_request_id,
            status=OrderStatus.REJECTED,
            reported_at=timestamp,
            filled_quantity=Decimal("0"),
            remaining_quantity=request.quantity,
            average_fill_price=None,
            approved_order_id=request.approved_order_id,
            requested_quantity=request.quantity,
            reconciliation_required=False,
        )


def validate_execution_adapter_surface(adapter: object) -> None:
    exposed = set(dir(adapter))
    prohibited = sorted(exposed.intersection(PROHIBITED_EXECUTION_ADAPTER_METHOD_NAMES))
    if prohibited:
        raise ExecutionAdapterError(f"execution adapter exposes prohibited methods: {', '.join(prohibited)}")
