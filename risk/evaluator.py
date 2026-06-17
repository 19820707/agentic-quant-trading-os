from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal

from packages.domain import (
    OrderIntent,
    PortfolioSnapshot,
    RiskCheckRequest,
    RiskCheckResult,
    RiskDecision,
    RiskViolation,
    SignalSide,
    Symbol,
    Venue,
)
from packages.domain.base import deterministic_id, require_aware_datetime, require_non_empty, require_non_negative, require_positive


class RiskEvaluationError(ValueError):
    """Raised when a local risk evaluation cannot be performed safely."""


@dataclass(frozen=True)
class PriceReference:
    symbol: Symbol
    venue: Venue
    price: Decimal
    observed_at: datetime
    liquidity_notional: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        require_positive(self.price, "price")
        require_aware_datetime(self.observed_at, "observed_at")
        require_non_negative(self.liquidity_notional, "liquidity_notional")


@dataclass(frozen=True)
class RiskLimits:
    max_order_notional: Decimal
    max_symbol_exposure: Decimal
    max_venue_exposure: Decimal
    max_gross_exposure: Decimal
    max_leverage: Decimal
    max_daily_loss: Decimal
    max_drawdown: Decimal
    max_open_orders: int
    max_orders_per_minute: int
    stale_price_after: timedelta
    max_price_deviation_bps: Decimal
    min_liquidity_notional: Decimal

    def __post_init__(self) -> None:
        for field_name in (
            "max_order_notional",
            "max_symbol_exposure",
            "max_venue_exposure",
            "max_gross_exposure",
            "max_leverage",
            "max_daily_loss",
            "max_drawdown",
            "max_price_deviation_bps",
            "min_liquidity_notional",
        ):
            require_non_negative(getattr(self, field_name), field_name)
        if self.max_open_orders < 0:
            raise RiskEvaluationError("max_open_orders must be non-negative")
        if self.max_orders_per_minute < 0:
            raise RiskEvaluationError("max_orders_per_minute must be non-negative")
        if self.stale_price_after.total_seconds() <= 0:
            raise RiskEvaluationError("stale_price_after must be positive")


@dataclass(frozen=True)
class RiskRuntimeState:
    kill_switch_active: bool = True
    open_orders: int = 0
    orders_last_minute: int = 0
    daily_pnl: Decimal = Decimal("0")
    peak_equity: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.open_orders < 0:
            raise RiskEvaluationError("open_orders must be non-negative")
        if self.orders_last_minute < 0:
            raise RiskEvaluationError("orders_last_minute must be non-negative")
        require_non_negative(self.peak_equity, "peak_equity")


@dataclass(frozen=True)
class RiskEvaluation:
    request: RiskCheckRequest
    portfolio: PortfolioSnapshot
    limits: RiskLimits
    runtime: RiskRuntimeState
    price_reference: PriceReference
    evaluated_at: datetime

    def __post_init__(self) -> None:
        require_aware_datetime(self.evaluated_at, "evaluated_at")
        if self.request.order_intent.symbol != self.price_reference.symbol:
            raise RiskEvaluationError("price reference symbol must match order intent")
        if self.request.order_intent.venue != self.price_reference.venue:
            raise RiskEvaluationError("price reference venue must match order intent")


def evaluate_risk(evaluation: RiskEvaluation) -> RiskCheckResult:
    intent = evaluation.request.order_intent
    price = _effective_price(intent, evaluation.price_reference)
    notional = intent.quantity * price
    signed_notional = _signed_notional(intent, notional)
    projected_symbol_exposure = evaluation.portfolio.exposure.by_symbol.get(intent.symbol.value, Decimal("0")) + signed_notional
    projected_venue_exposure = evaluation.portfolio.exposure.by_venue.get(intent.venue.value, Decimal("0")) + signed_notional
    projected_gross_exposure = _projected_gross_exposure(evaluation.portfolio, intent.symbol.value, projected_symbol_exposure)
    equity = _portfolio_equity(evaluation.portfolio)

    violations = tuple(
        violation for violation in (
            _kill_switch_violation(evaluation.runtime),
            _stale_price_violation(evaluation),
            _order_notional_violation(notional, evaluation.limits),
            _price_band_violation(intent, evaluation.price_reference, evaluation.limits),
            _liquidity_violation(evaluation.price_reference, evaluation.limits),
            _symbol_exposure_violation(projected_symbol_exposure, evaluation.limits),
            _venue_exposure_violation(projected_venue_exposure, evaluation.limits),
            _gross_exposure_violation(projected_gross_exposure, evaluation.limits),
            _leverage_violation(projected_gross_exposure, equity, evaluation.limits),
            _open_orders_violation(evaluation.runtime, evaluation.limits),
            _order_rate_violation(evaluation.runtime, evaluation.limits),
            _daily_loss_violation(evaluation.runtime, evaluation.limits),
            _drawdown_violation(equity, evaluation.runtime, evaluation.limits),
        )
        if violation is not None
    )

    decision = RiskDecision.REJECT if violations else RiskDecision.REVIEW
    return RiskCheckResult(
        risk_check_result_id=deterministic_id(
            "risk_result",
            evaluation.request.risk_check_request_id,
            intent.order_intent_id,
            evaluation.evaluated_at.isoformat(),
            decision.value,
        ),
        request_id=evaluation.request.risk_check_request_id,
        decision=decision,
        checked_at=evaluation.evaluated_at,
        violations=violations,
        approved_quantity=Decimal("0"),
        approved_notional=Decimal("0"),
        approved_for_execution=False,
    )


def _effective_price(intent: OrderIntent, price_reference: PriceReference) -> Decimal:
    return intent.limit_price if intent.limit_price is not None else price_reference.price


def _signed_notional(intent: OrderIntent, notional: Decimal) -> Decimal:
    if intent.side is SignalSide.BUY:
        return notional
    if intent.side is SignalSide.SELL:
        return -notional
    raise RiskEvaluationError("HOLD order intent cannot be risk evaluated")


def _projected_gross_exposure(portfolio: PortfolioSnapshot, symbol: str, projected_symbol_exposure: Decimal) -> Decimal:
    projected = dict(portfolio.exposure.by_symbol)
    projected[symbol] = projected_symbol_exposure
    return sum((abs(value) for value in projected.values()), Decimal("0"))


def _portfolio_equity(portfolio: PortfolioSnapshot) -> Decimal:
    cash = sum((balance.total for balance in portfolio.balances), Decimal("0"))
    return cash + portfolio.pnl.total


def _violation(rule_id: str, message: str, severity: str = "blocking") -> RiskViolation:
    require_non_empty(rule_id, "rule_id")
    return RiskViolation(rule_id=rule_id, message=message, severity=severity)


def _kill_switch_violation(runtime: RiskRuntimeState) -> RiskViolation | None:
    if runtime.kill_switch_active:
        return _violation("kill_switch", "global kill switch is active")
    return None


def _stale_price_violation(evaluation: RiskEvaluation) -> RiskViolation | None:
    age = evaluation.evaluated_at - evaluation.price_reference.observed_at
    if age > evaluation.limits.stale_price_after:
        return _violation("stale_price", "price reference is stale")
    return None


def _order_notional_violation(notional: Decimal, limits: RiskLimits) -> RiskViolation | None:
    if notional > limits.max_order_notional:
        return _violation("max_order_notional", "order notional exceeds configured limit")
    return None


def _price_band_violation(intent: OrderIntent, price_reference: PriceReference, limits: RiskLimits) -> RiskViolation | None:
    if intent.limit_price is None:
        return None
    deviation_bps = abs(intent.limit_price - price_reference.price) / price_reference.price * Decimal("10000")
    if deviation_bps > limits.max_price_deviation_bps:
        return _violation("price_band", "limit price deviates too far from reference price")
    return None


def _liquidity_violation(price_reference: PriceReference, limits: RiskLimits) -> RiskViolation | None:
    if price_reference.liquidity_notional < limits.min_liquidity_notional:
        return _violation("minimum_liquidity", "available reference liquidity is below minimum")
    return None


def _symbol_exposure_violation(projected_symbol_exposure: Decimal, limits: RiskLimits) -> RiskViolation | None:
    if abs(projected_symbol_exposure) > limits.max_symbol_exposure:
        return _violation("max_symbol_exposure", "projected symbol exposure exceeds limit")
    return None


def _venue_exposure_violation(projected_venue_exposure: Decimal, limits: RiskLimits) -> RiskViolation | None:
    if abs(projected_venue_exposure) > limits.max_venue_exposure:
        return _violation("max_venue_exposure", "projected venue exposure exceeds limit")
    return None


def _gross_exposure_violation(projected_gross_exposure: Decimal, limits: RiskLimits) -> RiskViolation | None:
    if projected_gross_exposure > limits.max_gross_exposure:
        return _violation("max_gross_exposure", "projected gross exposure exceeds limit")
    return None


def _leverage_violation(projected_gross_exposure: Decimal, equity: Decimal, limits: RiskLimits) -> RiskViolation | None:
    if projected_gross_exposure == Decimal("0"):
        return None
    if equity <= Decimal("0"):
        return _violation("max_leverage", "portfolio equity must be positive for leveraged exposure")
    projected_leverage = projected_gross_exposure / equity
    if projected_leverage > limits.max_leverage:
        return _violation("max_leverage", "projected leverage exceeds limit")
    return None


def _open_orders_violation(runtime: RiskRuntimeState, limits: RiskLimits) -> RiskViolation | None:
    if runtime.open_orders >= limits.max_open_orders:
        return _violation("max_open_orders", "open order count is at or above limit")
    return None


def _order_rate_violation(runtime: RiskRuntimeState, limits: RiskLimits) -> RiskViolation | None:
    if runtime.orders_last_minute >= limits.max_orders_per_minute:
        return _violation("max_orders_per_minute", "order rate is at or above limit")
    return None


def _daily_loss_violation(runtime: RiskRuntimeState, limits: RiskLimits) -> RiskViolation | None:
    if runtime.daily_pnl < -limits.max_daily_loss:
        return _violation("max_daily_loss", "daily loss exceeds limit")
    return None


def _drawdown_violation(equity: Decimal, runtime: RiskRuntimeState, limits: RiskLimits) -> RiskViolation | None:
    if runtime.peak_equity <= Decimal("0"):
        return None
    drawdown = runtime.peak_equity - equity
    if drawdown > limits.max_drawdown:
        return _violation("max_drawdown", "drawdown exceeds limit")
    return None
