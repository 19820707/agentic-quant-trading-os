from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from packages.domain import (
    CorrelationId,
    OrderIntent,
    OrderStatus,
    OrderType,
    RiskCheckResult,
    RiskDecision,
    RiskViolation,
    Signal,
    SignalMetadata,
    SignalSide,
    SignalStrength,
    StrategyId,
    StrategyVersion,
    Symbol,
    TimeInForce,
    Venue,
)
from paper_trading import PaperRuntimeConfig, PaperTradingError, simulate_paper_trade
from risk.evaluator import PriceReference


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)


def signal(side: SignalSide = SignalSide.BUY) -> Signal:
    return Signal.deterministic(
        strategy_id=StrategyId("paper.strategy"),
        strategy_version=StrategyVersion("1.0.0"),
        symbol=Symbol("BTC/USDT"),
        venue=Venue("paper"),
        side=side,
        strength=SignalStrength(Decimal("0.7")),
        generated_at=NOW,
        metadata=SignalMetadata(model_version="local.paper.fixture", rationale="paper fixture"),
    )


def intent(
    *,
    side: SignalSide = SignalSide.BUY,
    order_type: OrderType = OrderType.MARKET,
    limit_price: Decimal | None = None,
    quantity: Decimal = Decimal("1"),
) -> OrderIntent:
    return OrderIntent.from_signal(
        signal(side),
        quantity=quantity,
        order_type=order_type,
        created_at=NOW,
        time_in_force=TimeInForce.GTC,
        limit_price=limit_price,
    )


def approval(order_intent: OrderIntent, *, approved: bool = True) -> RiskCheckResult:
    if approved:
        return RiskCheckResult(
            risk_check_result_id="risk_approved_fixture",
            request_id="risk_request_fixture",
            decision=RiskDecision.APPROVE,
            checked_at=NOW,
            violations=(),
            approved_quantity=order_intent.quantity,
            approved_notional=Decimal("100000"),
            approved_for_execution=True,
        )
    return RiskCheckResult(
        risk_check_result_id="risk_rejected_fixture",
        request_id="risk_request_fixture",
        decision=RiskDecision.REJECT,
        checked_at=NOW,
        violations=(RiskViolation("fixture", "rejected", "blocking"),),
    )


def price_reference(price: Decimal = Decimal("100")) -> PriceReference:
    return PriceReference(
        symbol=Symbol("BTC/USDT"),
        venue=Venue("paper"),
        price=price,
        observed_at=NOW,
        liquidity_notional=Decimal("1000000"),
    )


def runtime(**overrides: object) -> PaperRuntimeConfig:
    values = {
        "paper_runtime_enabled": True,
        "fee_bps": Decimal("10"),
        "slippage_bps": Decimal("5"),
    }
    values.update(overrides)
    return PaperRuntimeConfig(**values)


class PaperTradingSimulatorTests(unittest.TestCase):
    def test_paper_runtime_is_disabled_by_default(self) -> None:
        with self.assertRaises(PaperTradingError):
            PaperRuntimeConfig()

    def test_paper_runtime_rejects_live_network_and_credentials(self) -> None:
        for unsafe_flag in ("live_trading_enabled", "network_allowed", "credentials_allowed"):
            with self.subTest(unsafe_flag=unsafe_flag):
                with self.assertRaises(PaperTradingError):
                    runtime(**{unsafe_flag: True})

    def test_rejects_non_approved_risk_result(self) -> None:
        order_intent = intent()
        with self.assertRaises(PaperTradingError):
            simulate_paper_trade(
                intent=order_intent,
                risk_result=approval(order_intent, approved=False),
                price_reference=price_reference(),
                config=runtime(),
                evaluated_at=NOW,
                correlation_id=CorrelationId("corr_paper"),
            )

    def test_market_buy_generates_deterministic_local_fill_and_audit_chain(self) -> None:
        order_intent = intent()
        result = simulate_paper_trade(
            intent=order_intent,
            risk_result=approval(order_intent),
            price_reference=price_reference(Decimal("100")),
            config=runtime(),
            evaluated_at=NOW,
            correlation_id=CorrelationId("corr_paper"),
        )

        self.assertEqual(result.order.status, OrderStatus.FILLED)
        self.assertEqual(result.execution_report.status, OrderStatus.FILLED)
        self.assertEqual(result.fills[0].price, Decimal("100.0500"))
        self.assertEqual(result.fills[0].fee, Decimal("0.1000500"))
        self.assertFalse(result.live_trading_used)
        self.assertFalse(result.network_used)
        self.assertFalse(result.credentials_used)
        self.assertEqual(
            [event.outcome for event in result.audit_events],
            ["RISK_CHECKED", "SUBMITTED", "ACKNOWLEDGED", "FILLED"],
        )

    def test_limit_order_can_rest_without_fill(self) -> None:
        order_intent = intent(order_type=OrderType.LIMIT, limit_price=Decimal("99"))
        result = simulate_paper_trade(
            intent=order_intent,
            risk_result=approval(order_intent),
            price_reference=price_reference(Decimal("100")),
            config=runtime(),
            evaluated_at=NOW,
            correlation_id=CorrelationId("corr_paper"),
        )

        self.assertEqual(result.order.status, OrderStatus.ACKNOWLEDGED)
        self.assertEqual(result.fills, ())
        self.assertEqual(result.execution_report.remaining_quantity, Decimal("1"))

    def test_partial_fill_is_deterministic(self) -> None:
        order_intent = intent(quantity=Decimal("2"))
        result = simulate_paper_trade(
            intent=order_intent,
            risk_result=approval(order_intent),
            price_reference=price_reference(Decimal("50")),
            config=runtime(max_fill_fraction=Decimal("0.25")),
            evaluated_at=NOW,
            correlation_id=CorrelationId("corr_paper"),
        )

        self.assertEqual(result.order.status, OrderStatus.PARTIALLY_FILLED)
        self.assertEqual(result.fills[0].quantity, Decimal("0.50"))
        self.assertEqual(result.execution_report.remaining_quantity, Decimal("1.50"))

    def test_sell_uses_negative_slippage_direction(self) -> None:
        order_intent = intent(side=SignalSide.SELL)
        result = simulate_paper_trade(
            intent=order_intent,
            risk_result=approval(order_intent),
            price_reference=price_reference(Decimal("100")),
            config=runtime(),
            evaluated_at=NOW,
            correlation_id=CorrelationId("corr_paper"),
        )

        self.assertEqual(result.fills[0].price, Decimal("99.9500"))


if __name__ == "__main__":
    unittest.main()
