from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from packages.domain.base import deterministic_id, require_aware_datetime, require_non_empty


class TradingRuntimeGateError(ValueError):
    """Raised when runtime activation gate inputs are unsafe or invalid."""


class RuntimeMode(str, Enum):
    RESEARCH_ONLY = "RESEARCH_ONLY"
    BACKTEST = "BACKTEST"
    PAPER = "PAPER"
    CONTROLLED_LIVE = "CONTROLLED_LIVE"
    PRODUCTION = "PRODUCTION"


class RuntimeActivationDecision(str, Enum):
    REJECTED = "REJECTED"
    REQUIRES_SEPARATE_APPROVAL = "REQUIRES_SEPARATE_APPROVAL"


REQUIRED_RUNTIME_EVIDENCE = frozenset(
    {
        "dataset_lineage_record",
        "leakage_review_report",
        "feature_store_approval_gate",
        "fake_offline_materialization_review",
        "backtest_review_contract",
        "paper_trading_review_contract",
        "broker_adapter_safety_policy",
        "execution_venue_capability",
        "credential_vault_policy",
        "kill_switch_policy",
        "audit_event_policy",
        "human_approval_record",
    }
)


BLOCKED_RUNTIME_CAPABILITIES = (
    "backtest_runtime_allowed",
    "paper_runtime_allowed",
    "live_trading_allowed",
    "production_allowed",
    "market_data_ingestion_allowed",
    "webhook_ingestion_allowed",
    "signal_ingestion_allowed",
    "broker_sdk_allowed",
    "exchange_sdk_allowed",
    "network_allowed",
    "credentials_allowed",
    "order_submission_allowed",
    "order_cancellation_allowed",
    "withdrawal_allowed",
    "transfer_allowed",
    "model_training_allowed",
    "feature_store_runtime_allowed",
)


@dataclass(frozen=True)
class TradingRuntimeActivationRequest:
    requested_runtime_mode: RuntimeMode
    requested_by: str
    requested_at: datetime
    evidence: frozenset[str] = field(default_factory=frozenset)
    broker_sdk_requested: bool = False
    exchange_sdk_requested: bool = False
    network_requested: bool = False
    credentials_requested: bool = False
    order_submission_requested: bool = False
    order_cancellation_requested: bool = False
    live_trading_requested: bool = False
    production_requested: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.requested_by, "requested_by")
        require_aware_datetime(self.requested_at, "requested_at")
        if any(not isinstance(item, str) or not item.strip() for item in self.evidence):
            raise TradingRuntimeGateError("evidence entries must be non-empty strings")

    @property
    def unsafe_runtime_requested(self) -> bool:
        return any(
            (
                self.broker_sdk_requested,
                self.exchange_sdk_requested,
                self.network_requested,
                self.credentials_requested,
                self.order_submission_requested,
                self.order_cancellation_requested,
                self.live_trading_requested,
                self.production_requested,
            )
        )


@dataclass(frozen=True)
class TradingRuntimeActivationReport:
    runtime_activation_gate_id: str
    requested_runtime_mode: RuntimeMode
    decision: RuntimeActivationDecision
    final_reason: str
    required_evidence: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    evaluated_at: datetime
    reviewed_by: str
    risk_gateway_required: bool = True
    approved_order_required_for_execution: bool = True
    execution_engine_only_for_broker_access: bool = True
    direct_signal_to_order_forbidden: bool = True
    direct_ai_to_broker_forbidden: bool = True
    direct_dashboard_to_broker_forbidden: bool = True

    def __post_init__(self) -> None:
        require_non_empty(self.runtime_activation_gate_id, "runtime_activation_gate_id")
        require_non_empty(self.final_reason, "final_reason")
        require_non_empty(self.reviewed_by, "reviewed_by")
        require_aware_datetime(self.evaluated_at, "evaluated_at")
        if not self.risk_gateway_required:
            raise TradingRuntimeGateError("deterministic risk gateway must remain required")
        if not self.approved_order_required_for_execution:
            raise TradingRuntimeGateError("ApprovedOrder must remain required for execution")
        if not self.execution_engine_only_for_broker_access:
            raise TradingRuntimeGateError("only execution engine may access broker/exchange boundaries")
        if not self.direct_signal_to_order_forbidden:
            raise TradingRuntimeGateError("direct signal to order path must remain forbidden")
        if not self.direct_ai_to_broker_forbidden:
            raise TradingRuntimeGateError("direct AI to broker path must remain forbidden")
        if not self.direct_dashboard_to_broker_forbidden:
            raise TradingRuntimeGateError("direct dashboard to broker path must remain forbidden")

    def to_contract_payload(self, *, trace_id: str, correlation_id: str) -> dict[str, object]:
        require_non_empty(trace_id, "trace_id")
        require_non_empty(correlation_id, "correlation_id")
        payload: dict[str, object] = {
            "schema_version": "0.1.0",
            "trace_id": trace_id,
            "correlation_id": correlation_id,
            "runtime_activation_gate_id": self.runtime_activation_gate_id,
            "created_at": self.evaluated_at.isoformat(),
            "requested_runtime_mode": self.requested_runtime_mode.value,
            "decision": self.decision.value,
            "final_reason": self.final_reason,
            "required_evidence": list(self.required_evidence),
            "risk_gateway_required": self.risk_gateway_required,
            "approved_order_required_for_execution": self.approved_order_required_for_execution,
            "execution_engine_only_for_broker_access": self.execution_engine_only_for_broker_access,
            "direct_signal_to_order_forbidden": self.direct_signal_to_order_forbidden,
            "direct_ai_to_broker_forbidden": self.direct_ai_to_broker_forbidden,
            "direct_dashboard_to_broker_forbidden": self.direct_dashboard_to_broker_forbidden,
            "reviewed_by": self.reviewed_by,
            "metadata": {
                "fail_closed": True,
                "missing_evidence_count": len(self.missing_evidence),
            },
        }
        for capability in BLOCKED_RUNTIME_CAPABILITIES:
            payload[capability] = False
        return payload


def evaluate_trading_runtime_activation(
    request: TradingRuntimeActivationRequest,
    *,
    evaluated_at: datetime | None = None,
    reviewed_by: str = "trading-runtime-activation-gate",
) -> TradingRuntimeActivationReport:
    """Evaluate runtime activation while preserving a fail-closed live boundary.

    This function intentionally never enables broker SDKs, exchange SDKs,
    credentials, network access, order submission or live trading. It creates an
    auditable local decision that can be serialized to the existing contract.
    """

    if not isinstance(request, TradingRuntimeActivationRequest):
        raise TradingRuntimeGateError("request must be TradingRuntimeActivationRequest")
    timestamp = evaluated_at or datetime.now(timezone.utc)
    require_aware_datetime(timestamp, "evaluated_at")
    require_non_empty(reviewed_by, "reviewed_by")

    missing = tuple(sorted(REQUIRED_RUNTIME_EVIDENCE.difference(request.evidence)))
    if request.unsafe_runtime_requested:
        decision = RuntimeActivationDecision.REJECTED
        reason = "Unsafe runtime capability requested; live trading remains blocked."
    else:
        decision = RuntimeActivationDecision.REQUIRES_SEPARATE_APPROVAL
        reason = "Runtime activation requires separate approval and remains fail-closed."

    return TradingRuntimeActivationReport(
        runtime_activation_gate_id=deterministic_id(
            "trag",
            request.requested_runtime_mode.value,
            request.requested_by,
            timestamp.isoformat(),
            "fail_closed",
        ),
        requested_runtime_mode=request.requested_runtime_mode,
        decision=decision,
        final_reason=reason,
        required_evidence=tuple(sorted(REQUIRED_RUNTIME_EVIDENCE)),
        missing_evidence=missing,
        evaluated_at=timestamp,
        reviewed_by=reviewed_by,
    )
