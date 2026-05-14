from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


RISK_GATEWAY_VERSION = "fail-closed-risk-gateway.0.1.0"
RISK_POLICY_VERSION = "fail-closed-risk-policy.0.1.0"


@dataclass(frozen=True)
class FailClosedRiskLimits:
    limit_profile_id: str = "fail_closed_default"
    max_order_notional: float = 0.0
    max_position_notional: float = 0.0
    max_total_gross_exposure: float = 0.0
    max_intraday_drawdown: float = 0.0
    global_kill_switch: bool = True


class FailClosedRiskGateway:
    """Deterministic risk gateway scaffold that never grants execution approval."""

    def __init__(self, limits: FailClosedRiskLimits | None = None):
        self._limits = limits or FailClosedRiskLimits()

    def evaluate_order_intent(
        self,
        order_intent: Mapping[str, Any],
        *,
        evaluated_at: datetime | None = None,
    ) -> dict[str, Any]:
        timestamp = _utc_timestamp(evaluated_at)
        quantity = _as_float(order_intent.get("quantity"))
        price = _as_float(order_intent.get("limit_price") or order_intent.get("stop_price"))
        original_notional = quantity * price if quantity is not None and price is not None else 0.0

        checks = [
            _check(
                "global_kill_switch",
                "FAIL",
                "CRITICAL",
                "Fail-closed scaffold keeps global kill switch active.",
                True,
                False,
            ),
            _check(
                "max_order_notional",
                "FAIL",
                "HIGH",
                "Fail-closed scaffold permits no executable order notional.",
                original_notional,
                self._limits.max_order_notional,
            ),
            _check(
                "max_position_notional",
                "FAIL",
                "HIGH",
                "Fail-closed scaffold has no approved position capacity.",
                original_notional,
                self._limits.max_position_notional,
            ),
            _check(
                "max_total_gross_exposure",
                "FAIL",
                "HIGH",
                "Fail-closed scaffold has no approved gross exposure capacity.",
                original_notional,
                self._limits.max_total_gross_exposure,
            ),
            _check(
                "max_intraday_drawdown",
                "FAIL",
                "HIGH",
                "Fail-closed scaffold requires drawdown review before any execution path.",
                None,
                self._limits.max_intraday_drawdown,
            ),
        ]

        return {
            "schema_version": "0.1.0",
            "trace_id": str(order_intent["trace_id"]),
            "correlation_id": str(order_intent["correlation_id"]),
            "risk_decision_id": f"risk_fail_closed_{order_intent['order_intent_id']}",
            "order_intent_id": str(order_intent["order_intent_id"]),
            "signal_id": str(order_intent["signal_id"]),
            "strategy_id": str(order_intent["strategy_id"]),
            "model_version": str(order_intent["model_version"]),
            "portfolio_id": order_intent.get("portfolio_id"),
            "account_id": order_intent.get("account_id"),
            "symbol": str(order_intent["symbol"]),
            "venue": str(order_intent["venue"]),
            "decision": "REJECT",
            "approved_for_execution": False,
            "original_quantity": quantity or 0.0,
            "approved_quantity": 0.0,
            "original_notional": original_notional,
            "approved_notional": 0.0,
            "max_allowed_notional": self._limits.max_order_notional,
            "risk_gateway_version": RISK_GATEWAY_VERSION,
            "risk_policy_version": RISK_POLICY_VERSION,
            "limit_profile_id": self._limits.limit_profile_id,
            "checks": checks,
            "hard_limits_triggered": [check["check_name"] for check in checks],
            "soft_limits_triggered": [],
            "manual_approval_required": True,
            "manual_approval_reason": "Fail-closed scaffold rejects all intents until a real policy is separately approved.",
            "kill_switch_triggered": True,
            "kill_switch_scope": "GLOBAL",
            "final_reason": "Fail-closed deterministic-risk-gateway scaffold rejected the OrderIntent.",
            "evaluated_at": timestamp,
            "evaluated_by": "deterministic-risk-gateway-fail-closed-scaffold",
            "metadata": {
                "runtime_mode": "local_only",
                "network_allowed": False,
                "credentials_allowed": False,
            },
        }


def _check(
    check_name: str,
    result: str,
    severity: str,
    reason: str,
    observed_value: str | float | bool | None,
    limit_value: str | float | bool | None,
) -> dict[str, Any]:
    return {
        "check_name": check_name,
        "result": result,
        "severity": severity,
        "reason": reason,
        "observed_value": observed_value,
        "limit_value": limit_value,
    }


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _utc_timestamp(value: datetime | None) -> str:
    if value is None:
        value = datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
