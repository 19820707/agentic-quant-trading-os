import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from packages.domain import (
    Balance,
    ExposureSnapshot,
    OrderIntent,
    OrderType,
    PnL,
    PortfolioSnapshot,
    RiskCheckRequest,
    RiskDecision,
    SignalSide,
    StrategyId,
    Symbol,
    TimeInForce,
    Venue,
)
from risk import PriceReference, RiskEvaluation, RiskEvaluationError, RiskLimits, RiskRuntimeState, evaluate_risk


NOW = datetime(2026, 6, 14, 12, 0, tzinfo=timezone.utc)
BTC = Symbol("BTC/USDT")
PAPER = Venue("paper")


class RiskEvaluatorTests(unittest.TestCase):
    def test_clean_request_returns_review_not_execution_approval(self):
        result = evaluate_risk(self._evaluation())

        self.assertEqual(result.decision, RiskDecision.REVIEW)
        self.assertFalse(result.approved_for_execution)
        self.assertEqual(result.approved_quantity, Decimal("0"))
        self.assertEqual(result.approved_notional, Decimal("0"))
        self.assertEqual(result.violations, ())

    def test_kill_switch_rejects(self):
        result = evaluate_risk(self._evaluation(runtime=RiskRuntimeState(kill_switch_active=True, peak_equity=Decimal("10000"))))

        self.assertEqual(result.decision, RiskDecision.REJECT)
        self.assertIn("kill_switch", self._rule_ids(result))

    def test_order_notional_limit_rejects(self):
        result = evaluate_risk(
            self._evaluation(
                intent=self._intent(quantity=Decimal("2"), limit_price=Decimal("100")),
                limits=self._limits(max_order_notional=Decimal("100")),
            )
        )

        self.assertIn("max_order_notional", self._rule_ids(result))

    def test_stale_price_rejects(self):
        result = evaluate_risk(
            self._evaluation(
                price_reference=PriceReference(
                    symbol=BTC,
                    venue=PAPER,
                    price=Decimal("100"),
                    observed_at=NOW - timedelta(minutes=10),
                    liquidity_notional=Decimal("100000"),
                )
            )
        )

        self.assertIn("stale_price", self._rule_ids(result))

    def test_price_band_rejects_bad_limit_price(self):
        result = evaluate_risk(
            self._evaluation(
                intent=self._intent(quantity=Decimal("1"), limit_price=Decimal("120")),
                limits=self._limits(max_price_deviation_bps=Decimal("100")),
            )
        )

        self.assertIn("price_band", self._rule_ids(result))

    def test_minimum_liquidity_rejects(self):
        result = evaluate_risk(
            self._evaluation(
                price_reference=PriceReference(
                    symbol=BTC,
                    venue=PAPER,
                    price=Decimal("100"),
                    observed_at=NOW,
                    liquidity_notional=Decimal("50"),
                ),
                limits=self._limits(min_liquidity_notional=Decimal("1000")),
            )
        )

        self.assertIn("minimum_liquidity", self._rule_ids(result))

    def test_projected_exposure_and_leverage_reject(self):
        result = evaluate_risk(
            self._evaluation(
                portfolio=self._portfolio(cash=Decimal("100"), symbol_exposure=Decimal("900")),
                intent=self._intent(quantity=Decimal("2"), limit_price=Decimal("100")),
                limits=self._limits(
                    max_symbol_exposure=Decimal("1000"),
                    max_gross_exposure=Decimal("1000"),
                    max_leverage=Decimal("5"),
                ),
            )
        )

        self.assertIn("max_symbol_exposure", self._rule_ids(result))
        self.assertIn("max_gross_exposure", self._rule_ids(result))
        self.assertIn("max_leverage", self._rule_ids(result))

    def test_order_count_and_rate_reject(self):
        result = evaluate_risk(
            self._evaluation(
                runtime=RiskRuntimeState(
                    kill_switch_active=False,
                    open_orders=10,
                    orders_last_minute=5,
                    peak_equity=Decimal("10000"),
                ),
                limits=self._limits(max_open_orders=10, max_orders_per_minute=5),
            )
        )

        self.assertIn("max_open_orders", self._rule_ids(result))
        self.assertIn("max_orders_per_minute", self._rule_ids(result))

    def test_loss_and_drawdown_reject(self):
        result = evaluate_risk(
            self._evaluation(
                portfolio=self._portfolio(cash=Decimal("8000")),
                runtime=RiskRuntimeState(
                    kill_switch_active=False,
                    daily_pnl=Decimal("-600"),
                    peak_equity=Decimal("10000"),
                ),
                limits=self._limits(max_daily_loss=Decimal("500"), max_drawdown=Decimal("1000")),
            )
        )

        self.assertIn("max_daily_loss", self._rule_ids(result))
        self.assertIn("max_drawdown", self._rule_ids(result))

    def test_mismatched_price_reference_fails_closed(self):
        with self.assertRaises(RiskEvaluationError):
            self._evaluation(
                price_reference=PriceReference(
                    symbol=Symbol("ETH/USDT"),
                    venue=PAPER,
                    price=Decimal("100"),
                    observed_at=NOW,
                    liquidity_notional=Decimal("100000"),
                )
            )

    def test_evaluator_exposes_no_execution_methods(self):
        import risk.evaluator as evaluator

        forbidden_names = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "execute",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(evaluator)))

    def _evaluation(
        self,
        *,
        intent: OrderIntent | None = None,
        portfolio: PortfolioSnapshot | None = None,
        limits: RiskLimits | None = None,
        runtime: RiskRuntimeState | None = None,
        price_reference: PriceReference | None = None,
    ) -> RiskEvaluation:
        intent = intent or self._intent()
        return RiskEvaluation(
            request=RiskCheckRequest(
                risk_check_request_id="risk_request_001",
                order_intent=intent,
                portfolio_id="portfolio_001",
                requested_at=NOW,
            ),
            portfolio=portfolio or self._portfolio(),
            limits=limits or self._limits(),
            runtime=runtime or RiskRuntimeState(kill_switch_active=False, peak_equity=Decimal("10000")),
            price_reference=price_reference
            or PriceReference(
                symbol=BTC,
                venue=PAPER,
                price=Decimal("100"),
                observed_at=NOW,
                liquidity_notional=Decimal("100000"),
            ),
            evaluated_at=NOW,
        )

    def _intent(self, *, quantity: Decimal = Decimal("1"), limit_price: Decimal = Decimal("100")) -> OrderIntent:
        return OrderIntent(
            order_intent_id="intent_risk_fixture_001",
            signal_id="sig_risk_fixture_001",
            strategy_id=StrategyId("risk_fixture_strategy"),
            symbol=BTC,
            venue=PAPER,
            side=SignalSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            limit_price=limit_price,
            created_at=NOW,
            time_in_force=TimeInForce.GTC,
        )

    def _portfolio(self, *, cash: Decimal = Decimal("10000"), symbol_exposure: Decimal = Decimal("0")) -> PortfolioSnapshot:
        return PortfolioSnapshot(
            portfolio_id="portfolio_001",
            timestamp=NOW,
            balances=(Balance(asset="USDT", total=cash, available=cash, locked=Decimal("0")),),
            positions=(),
            exposure=ExposureSnapshot(
                gross_exposure=abs(symbol_exposure),
                net_exposure=symbol_exposure,
                by_symbol={"BTC/USDT": symbol_exposure},
                by_venue={"paper": symbol_exposure},
            ),
            pnl=PnL(realized=Decimal("0"), unrealized=Decimal("0"), fees=Decimal("0")),
        )

    def _limits(self, **overrides: object) -> RiskLimits:
        values = {
            "max_order_notional": Decimal("1000"),
            "max_symbol_exposure": Decimal("5000"),
            "max_venue_exposure": Decimal("5000"),
            "max_gross_exposure": Decimal("10000"),
            "max_leverage": Decimal("2"),
            "max_daily_loss": Decimal("1000"),
            "max_drawdown": Decimal("2000"),
            "max_open_orders": 100,
            "max_orders_per_minute": 20,
            "stale_price_after": timedelta(seconds=30),
            "max_price_deviation_bps": Decimal("250"),
            "min_liquidity_notional": Decimal("1000"),
        }
        values.update(overrides)
        return RiskLimits(**values)

    def _rule_ids(self, result):
        return {violation.rule_id for violation in result.violations}


if __name__ == "__main__":
    unittest.main()
