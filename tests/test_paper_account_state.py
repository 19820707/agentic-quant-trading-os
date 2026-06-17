from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from packages.domain import (
    CorrelationId,
    OrderIntent,
    OrderType,
    RiskCheckResult,
    RiskDecision,
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
from paper_trading import (
    PaperAccountState,
    PaperRuntimeConfig,
    PaperTradingError,
    apply_paper_trade_result,
    paper_account_portfolio_snapshot,
    simulate_paper_trade,
)
from risk import PriceReference


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)
BTC = Symbol("BTC/USDT")
PAPER = Venue("paper")


def signal(side: SignalSide) -> Signal:
    return Signal.deterministic(
        strategy_id=StrategyId("paper.account"),
        strategy_version=StrategyVersion("1.0.0"),
        symbol=BTC,
        venue=PAPER,
        side=side,
        strength=SignalStrength(Decimal("0.9")),
        generated_at=NOW,
        metadata=SignalMetadata(model_version="paper.account.fixture"),
    )


def intent(side: SignalSide, quantity: Decimal = Decimal("1")) -> OrderIntent:
    return OrderIntent.from_signal(
        signal(side),
        quantity=quantity,
        order_type=OrderType.MARKET,
        created_at=NOW,
        time_in_force=TimeInForce.GTC,
    )


def approval(order_intent: OrderIntent) -> RiskCheckResult:
    return RiskCheckResult(
        risk_check_result_id=f"risk_{order_intent.order_intent_id}",
        request_id="risk_request",
        decision=RiskDecision.APPROVE,
        checked_at=NOW,
        violations=(),
        approved_quantity=order_intent.quantity,
        approved_notional=Decimal("100000"),
        approved_for_execution=True,
    )


def paper_result(order_intent: OrderIntent, price: Decimal = Decimal("100")):
    return simulate_paper_trade(
        intent=order_intent,
        risk_result=approval(order_intent),
        price_reference=PriceReference(
            symbol=BTC,
            venue=PAPER,
            price=price,
            observed_at=NOW,
            liquidity_notional=Decimal("100000"),
        ),
        config=PaperRuntimeConfig(paper_runtime_enabled=True),
        evaluated_at=NOW,
        correlation_id=CorrelationId("corr_paper_account"),
    )


class PaperAccountStateTests(unittest.TestCase):
    def test_account_state_rejects_unsafe_flags(self) -> None:
        for flag in ("live_trading_enabled", "network_used", "credentials_used"):
            with self.subTest(flag=flag):
                with self.assertRaises(PaperTradingError):
                    PaperAccountState(
                        portfolio_id="paper_portfolio",
                        cash_asset="USDT",
                        cash_balance=Decimal("1000"),
                        side_aware_fills=(),
                        updated_at=NOW,
                        **{flag: True},
                    )

    def test_buy_fill_reduces_cash_and_creates_position_snapshot(self) -> None:
        account = PaperAccountState(
            portfolio_id="paper_portfolio",
            cash_asset="USDT",
            cash_balance=Decimal("1000"),
            side_aware_fills=(),
            updated_at=NOW,
        )
        updated = apply_paper_trade_result(account, paper_result(intent(SignalSide.BUY)))

        self.assertEqual(updated.cash_balance, Decimal("900"))
        self.assertEqual(len(updated.side_aware_fills), 1)

        snapshot = paper_account_portfolio_snapshot(
            updated,
            timestamp=NOW,
            mark_prices={("BTC/USDT", "paper"): Decimal("110")},
        )

        self.assertEqual(snapshot.positions[0].quantity, Decimal("1"))
        self.assertEqual(snapshot.pnl.unrealized, Decimal("10"))
        self.assertEqual(snapshot.exposure.by_symbol["BTC/USDT"], Decimal("110"))

    def test_sell_fill_increases_cash_and_side_aware_position(self) -> None:
        account = PaperAccountState(
            portfolio_id="paper_portfolio",
            cash_asset="USDT",
            cash_balance=Decimal("1000"),
            side_aware_fills=(),
            updated_at=NOW,
        )
        updated = apply_paper_trade_result(account, paper_result(intent(SignalSide.SELL), Decimal("50")))

        self.assertEqual(updated.cash_balance, Decimal("1050"))
        snapshot = paper_account_portfolio_snapshot(
            updated,
            timestamp=NOW,
            mark_prices={("BTC/USDT", "paper"): Decimal("45")},
        )

        self.assertEqual(snapshot.positions[0].quantity, Decimal("-1"))
        self.assertEqual(snapshot.pnl.unrealized, Decimal("5"))

    def test_buy_cannot_make_cash_negative(self) -> None:
        account = PaperAccountState(
            portfolio_id="paper_portfolio",
            cash_asset="USDT",
            cash_balance=Decimal("10"),
            side_aware_fills=(),
            updated_at=NOW,
        )

        with self.assertRaises(PaperTradingError):
            apply_paper_trade_result(account, paper_result(intent(SignalSide.BUY), Decimal("100")))


if __name__ == "__main__":
    unittest.main()
