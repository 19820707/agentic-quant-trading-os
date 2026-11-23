"""Cross-field invariants for trading contracts.

A JSON Schema checks each field on its own. It cannot say that a rejected risk
decision must not be approved for execution, or that an order cannot fill more
than was requested. This module holds those cross-field rules.

The rules are deterministic and pure: they read one payload and return a list of
problems. They do not decide trades, approve risk, call services or access
credentials. They only reject payloads that contradict themselves.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

_TOLERANCE = 1e-9

_APPROVING_DECISIONS = frozenset({"APPROVE", "RESIZE"})
_BLOCKING_CHECK_SEVERITIES = frozenset({"HIGH", "CRITICAL"})
_LIMIT_PRICE_ORDER_TYPES = frozenset({"LIMIT", "STOP_LIMIT", "TAKE_PROFIT_LIMIT"})
_STOP_PRICE_ORDER_TYPES = frozenset({"STOP", "STOP_LIMIT"})
_PAPER_ONLY_STATUSES = frozenset({"PAPER_FILLED", "PAPER_REJECTED"})
_BROKER_ONLY_EVENTS = frozenset({"ORDER_SUBMITTED", "BROKER_ACK", "BROKER_REJECT"})
_FULLY_FILLED_STATUSES = frozenset({"FILLED", "PAPER_FILLED"})


def _number(payload: Mapping[str, Any], field: str) -> float | None:
    value = payload.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _exceeds(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return False
    return left > right + _TOLERANCE * max(1.0, abs(right))


def _differs(left: float, right: float) -> bool:
    return abs(left - right) > _TOLERANCE * max(1.0, abs(left), abs(right))


def _non_empty_list(payload: Mapping[str, Any], field: str) -> bool:
    value = payload.get(field)
    return isinstance(value, list) and bool(value)


def check_risk_decision(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    decision = payload.get("decision")
    approved = payload.get("approved_for_execution") is True

    if approved and decision not in _APPROVING_DECISIONS:
        errors.append(f"approved_for_execution is true but decision is {decision!r}")
    if approved and payload.get("kill_switch_triggered") is True:
        errors.append("approved_for_execution is true while kill_switch_triggered is true")
    if approved and payload.get("manual_approval_required") is True:
        errors.append("approved_for_execution is true while manual_approval_required is true")
    if approved and _non_empty_list(payload, "hard_limits_triggered"):
        errors.append("approved_for_execution is true while hard limits are triggered")

    checks = payload.get("checks")
    if approved and isinstance(checks, list):
        for check in checks:
            if (
                isinstance(check, Mapping)
                and check.get("result") == "FAIL"
                and check.get("severity") in _BLOCKING_CHECK_SEVERITIES
            ):
                errors.append(
                    f"approved_for_execution is true while check {check.get('check_name')!r} "
                    f"failed with severity {check.get('severity')}"
                )

    scope = payload.get("kill_switch_scope")
    if payload.get("kill_switch_triggered") is True and scope == "NONE":
        errors.append("kill_switch_triggered is true but kill_switch_scope is NONE")
    if payload.get("kill_switch_triggered") is False and scope not in (None, "NONE"):
        errors.append(f"kill_switch_scope is {scope!r} but kill_switch_triggered is false")

    original_quantity = _number(payload, "original_quantity")
    approved_quantity = _number(payload, "approved_quantity")
    if _exceeds(approved_quantity, original_quantity):
        errors.append("approved_quantity exceeds original_quantity")
    if _exceeds(_number(payload, "approved_notional"), _number(payload, "original_notional")):
        errors.append("approved_notional exceeds original_notional")
    if _exceeds(_number(payload, "approved_notional"), _number(payload, "max_allowed_notional")):
        errors.append("approved_notional exceeds max_allowed_notional")

    if not approved and approved_quantity is not None and approved_quantity > _TOLERANCE:
        errors.append("approved_quantity is positive but the decision is not approved for execution")
    if (
        decision == "RESIZE"
        and original_quantity is not None
        and approved_quantity is not None
        and not _exceeds(original_quantity, approved_quantity)
    ):
        errors.append("decision is RESIZE but approved_quantity is not below original_quantity")

    return errors


def _check_order_prices(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    order_type = payload.get("order_type")

    if order_type in _LIMIT_PRICE_ORDER_TYPES and _number(payload, "limit_price") is None:
        errors.append(f"order_type {order_type} requires limit_price")
    if order_type in _STOP_PRICE_ORDER_TYPES and _number(payload, "stop_price") is None:
        errors.append(f"order_type {order_type} requires stop_price")
    if order_type == "MARKET" and payload.get("post_only") is True:
        errors.append("post_only cannot be combined with order_type MARKET")

    return errors


def check_order_intent(payload: Mapping[str, Any]) -> list[str]:
    return _check_order_prices(payload)


def check_approved_order(payload: Mapping[str, Any]) -> list[str]:
    errors = _check_order_prices(payload)

    summary = payload.get("risk_summary")
    if isinstance(summary, Mapping) and _non_empty_list(summary, "hard_limits_triggered"):
        errors.append("approved order carries triggered hard limits in risk_summary")

    mode = payload.get("execution_mode")
    status = payload.get("status")
    if mode == "PAPER" and status == "QUEUED_FOR_EXECUTION":
        errors.append("execution_mode PAPER cannot be queued for live execution")
    if mode == "CONTROLLED_LIVE" and status == "QUEUED_FOR_PAPER":
        errors.append("execution_mode CONTROLLED_LIVE cannot be queued for paper execution")

    return errors


def check_execution_report(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    requested = _number(payload, "requested_quantity")
    filled = _number(payload, "filled_quantity")
    remaining = _number(payload, "remaining_quantity")
    last_fill = _number(payload, "last_fill_quantity")
    status = payload.get("status")

    if _exceeds(filled, requested):
        errors.append("filled_quantity exceeds requested_quantity")
    if _exceeds(last_fill, filled):
        errors.append("last_fill_quantity exceeds filled_quantity")
    if requested is not None and filled is not None and remaining is not None:
        if _differs(remaining, requested - filled):
            errors.append("remaining_quantity does not equal requested_quantity minus filled_quantity")

    if status in _FULLY_FILLED_STATUSES and requested is not None and filled is not None:
        if _differs(filled, requested):
            errors.append(f"status {status} requires filled_quantity to equal requested_quantity")
    if status == "PARTIALLY_FILLED" and requested is not None and filled is not None:
        if filled <= _TOLERANCE or not _exceeds(requested, filled):
            errors.append("status PARTIALLY_FILLED requires 0 < filled_quantity < requested_quantity")

    mode = payload.get("execution_mode")
    if mode == "CONTROLLED_LIVE" and status in _PAPER_ONLY_STATUSES:
        errors.append(f"status {status} is not valid for execution_mode CONTROLLED_LIVE")
    if mode == "PAPER" and payload.get("event_type") in _BROKER_ONLY_EVENTS:
        errors.append(f"event_type {payload.get('event_type')} is not valid for execution_mode PAPER")

    return errors


InvariantCheck = Callable[[Mapping[str, Any]], list[str]]

INVARIANT_CHECKS: dict[tuple[str, str], InvariantCheck] = {
    ("trading", "risk_decision"): check_risk_decision,
    ("trading", "order_intent"): check_order_intent,
    ("trading", "approved_order"): check_approved_order,
    ("trading", "execution_report"): check_execution_report,
}


def check_invariants(domain: str, name: str, payload: object) -> list[str]:
    """Return cross-field problems for a contract payload, or an empty list."""

    check = INVARIANT_CHECKS.get((domain, name.removesuffix(".schema.json")))
    if check is None or not isinstance(payload, Mapping):
        return []
    return [f"invariant violated: {message}" for message in check(payload)]
