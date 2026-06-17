import unittest
from datetime import datetime, timezone
from decimal import Decimal

from packages.domain import (
    ApprovedOrder,
    ApprovedOrderStatus,
    AuditEvent,
    AuditEventType,
    Balance,
    CausationId,
    CorrelationId,
    ExecutionMode,
    ExecutionReport,
    ExposureSnapshot,
    Fill,
    OHLCVCandle,
    OrderBookLevel,
    OrderBookSnapshot,
    OrderIntent,
    OrderRequest,
    OrderStatus,
    OrderType,
    PnL,
    PortfolioSnapshot,
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
    Ticker,
    TimeInForce,
    Trade,
    Venue,
)
from packages.domain.base import DomainModelError


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)


class DomainModelTests(unittest.TestCase):
    def test_market_data_models_validate_decimal_values(self):
        candle = OHLCVCandle(
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            timestamp=NOW,
            open=Decimal("100.10"),
            high=Decimal("101.20"),
            low=Decimal("99.90"),
            close=Decimal("100.40"),
            volume=Decimal("12.34567890123456789"),
        )

        self.assertEqual(candle.to_dict()["volume"], "12.34567890123456789")

    def test_market_data_rejects_invalid_prices_and_spreads(self):
        with self.assertRaises(ValueError):
            Ticker(
                symbol=Symbol("BTC/USDT"),
                venue=Venue("paper"),
                timestamp=NOW,
                bid=Decimal("101"),
                ask=Decimal("100"),
                last=Decimal("100.5"),
            )

        with self.assertRaises(DomainModelError):
            Trade(
                trade_id="trade_001",
                symbol=Symbol("BTC/USDT"),
                venue=Venue("paper"),
                timestamp=NOW,
                price=100.0,
                quantity=Decimal("1"),
            )

    def test_order_book_snapshot_serialization_roundtrip(self):
        snapshot = OrderBookSnapshot(
            symbol=Symbol("ETH/USDT"),
            venue=Venue("paper"),
            timestamp=NOW,
            bids=(OrderBookLevel(price=Decimal("2000.01"), quantity=Decimal("1.25")),),
            asks=(OrderBookLevel(price=Decimal("2000.05"), quantity=Decimal("2.50")),),
        )

        restored = OrderBookSnapshot.from_dict(snapshot.to_dict())

        self.assertEqual(restored, snapshot)
        self.assertEqual(restored.to_dict()["bids"][0]["price"], "2000.01")

    def test_signal_uses_deterministic_id_and_roundtrips(self):
        signal = Signal.deterministic(
            strategy_id=StrategyId("mean_reversion"),
            strategy_version=StrategyVersion("1.0.0"),
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            side=SignalSide.BUY,
            strength=SignalStrength(Decimal("0.81234567890123456789")),
            generated_at=NOW,
            metadata=SignalMetadata(model_version="model.local.1", rationale="fixture"),
        )
        same_signal = Signal.deterministic(
            strategy_id=StrategyId("mean_reversion"),
            strategy_version=StrategyVersion("1.0.0"),
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            side=SignalSide.BUY,
            strength=SignalStrength(Decimal("0.81234567890123456789")),
            generated_at=NOW,
            metadata=SignalMetadata(model_version="model.local.1", rationale="fixture"),
        )

        self.assertEqual(signal.signal_id, same_signal.signal_id)
        self.assertEqual(Signal.from_dict(signal.to_dict()), signal)

    def test_signal_strength_rejects_out_of_range_values(self):
        with self.assertRaises(DomainModelError):
            SignalStrength(Decimal("1.01"))

    def test_signal_to_order_intent_conversion_requires_risk(self):
        signal = Signal.deterministic(
            strategy_id=StrategyId("breakout"),
            strategy_version=StrategyVersion("2.0.0"),
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            side=SignalSide.SELL,
            strength=SignalStrength(Decimal("0.7")),
            generated_at=NOW,
            metadata=SignalMetadata(model_version="model.local.2"),
        )

        intent = OrderIntent.from_signal(
            signal,
            quantity=Decimal("0.01"),
            order_type=OrderType.LIMIT,
            created_at=NOW,
            time_in_force=TimeInForce.GTC,
            limit_price=Decimal("65000.25"),
        )

        self.assertTrue(intent.risk_required)
        self.assertEqual(intent.signal_id, signal.signal_id)
        self.assertEqual(OrderIntent.from_dict(intent.to_dict()), intent)

    def test_approved_order_requires_positive_approved_risk_result(self):
        signal = Signal.deterministic(
            strategy_id=StrategyId("breakout"),
            strategy_version=StrategyVersion("2.0.0"),
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            side=SignalSide.BUY,
            strength=SignalStrength(Decimal("0.7")),
            generated_at=NOW,
            metadata=SignalMetadata(model_version="model.local.2"),
        )
        intent = OrderIntent.from_signal(
            signal,
            quantity=Decimal("0.25"),
            order_type=OrderType.LIMIT,
            created_at=NOW,
            limit_price=Decimal("65000.25"),
        )
        risk_result = RiskCheckResult(
            risk_check_result_id="risk_result_approved",
            request_id="risk_request_approved",
            decision=RiskDecision.APPROVE,
            checked_at=NOW,
            violations=(),
            approved_quantity=Decimal("0.10"),
            approved_notional=Decimal("6500.025"),
            approved_for_execution=True,
        )

        approved = ApprovedOrder.from_intent_and_risk_result(
            intent,
            risk_result,
            approved_at=NOW,
            approved_by="deterministic-risk-gateway",
        )

        self.assertEqual(approved.execution_mode, ExecutionMode.PAPER)
        self.assertEqual(approved.status, ApprovedOrderStatus.QUEUED_FOR_PAPER)
        self.assertEqual(approved.approved_quantity, Decimal("0.10"))
        self.assertEqual(approved.limit_price, Decimal("65000.25"))
        self.assertTrue(approved.client_order_id.startswith("client_"))

    def test_approved_order_rejects_non_approved_or_oversized_risk_result(self):
        signal = Signal.deterministic(
            strategy_id=StrategyId("breakout"),
            strategy_version=StrategyVersion("2.0.0"),
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            side=SignalSide.BUY,
            strength=SignalStrength(Decimal("0.7")),
            generated_at=NOW,
            metadata=SignalMetadata(model_version="model.local.2"),
        )
        intent = OrderIntent.from_signal(
            signal,
            quantity=Decimal("0.25"),
            order_type=OrderType.MARKET,
            created_at=NOW,
        )
        rejected = RiskCheckResult(
            risk_check_result_id="risk_result_rejected",
            request_id="risk_request_rejected",
            decision=RiskDecision.REJECT,
            checked_at=NOW,
            violations=(RiskViolation("max_notional", "blocked", "blocking"),),
        )
        oversized = RiskCheckResult(
            risk_check_result_id="risk_result_oversized",
            request_id="risk_request_oversized",
            decision=RiskDecision.APPROVE,
            checked_at=NOW,
            violations=(),
            approved_quantity=Decimal("0.50"),
            approved_notional=Decimal("32500.00"),
            approved_for_execution=True,
        )

        with self.assertRaises(ValueError):
            ApprovedOrder.from_intent_and_risk_result(
                intent,
                rejected,
                approved_at=NOW,
                approved_by="deterministic-risk-gateway",
            )
        with self.assertRaises(ValueError):
            ApprovedOrder.from_intent_and_risk_result(
                intent,
                oversized,
                approved_at=NOW,
                approved_by="deterministic-risk-gateway",
            )

    def test_order_request_can_be_created_only_from_paper_approved_order(self):
        approved = ApprovedOrder(
            approved_order_id="approved_001",
            order_intent_id="intent_001",
            risk_decision_id="risk_result_001",
            strategy_id=StrategyId("breakout"),
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            side=SignalSide.BUY,
            order_type=OrderType.MARKET,
            approved_quantity=Decimal("0.10"),
            approved_at=NOW,
            approved_by="deterministic-risk-gateway",
        )

        request = OrderRequest.from_approved_order(approved, created_at=NOW)

        self.assertEqual(request.approved_order_id, approved.approved_order_id)
        self.assertEqual(request.quantity, approved.approved_quantity)
        self.assertEqual(request.limit_price, approved.limit_price)

        with self.assertRaises(ValueError):
            ApprovedOrder(
                approved_order_id="approved_live",
                order_intent_id="intent_live",
                risk_decision_id="risk_result_live",
                strategy_id=StrategyId("breakout"),
                symbol=Symbol("BTC/USDT"),
                venue=Venue("paper"),
                side=SignalSide.BUY,
                order_type=OrderType.MARKET,
                approved_quantity=Decimal("0.10"),
                approved_at=NOW,
                approved_by="deterministic-risk-gateway",
                execution_mode=ExecutionMode.CONTROLLED_LIVE,
            )

    def test_execution_report_enforces_lifecycle_quantities(self):
        report = ExecutionReport(
            execution_report_id="execution_report_001",
            order_id="paper_order_001",
            status=OrderStatus.PARTIALLY_FILLED,
            reported_at=NOW,
            filled_quantity=Decimal("0.04"),
            remaining_quantity=Decimal("0.06"),
            average_fill_price=Decimal("65000.25"),
            approved_order_id="approved_001",
            client_order_id="client_001",
            requested_quantity=Decimal("0.10"),
            reconciliation_required=False,
        )

        self.assertEqual(report.to_dict()["requested_quantity"], "0.10")

        with self.assertRaises(ValueError):
            ExecutionReport(
                execution_report_id="execution_report_bad_average",
                order_id="paper_order_001",
                status=OrderStatus.ACKNOWLEDGED,
                reported_at=NOW,
                filled_quantity=Decimal("0"),
                remaining_quantity=Decimal("0.10"),
                average_fill_price=Decimal("65000.25"),
                requested_quantity=Decimal("0.10"),
            )
        with self.assertRaises(ValueError):
            ExecutionReport(
                execution_report_id="execution_report_bad_quantity",
                order_id="paper_order_001",
                status=OrderStatus.FILLED,
                reported_at=NOW,
                filled_quantity=Decimal("0.08"),
                remaining_quantity=Decimal("0.01"),
                average_fill_price=Decimal("65000.25"),
                requested_quantity=Decimal("0.10"),
            )

    def test_hold_signal_cannot_create_order_intent(self):
        signal = Signal.deterministic(
            strategy_id=StrategyId("observer"),
            strategy_version=StrategyVersion("1.0.0"),
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            side=SignalSide.HOLD,
            strength=SignalStrength(Decimal("0.5")),
            generated_at=NOW,
            metadata=SignalMetadata(model_version="model.local.3"),
        )

        with self.assertRaises(ValueError):
            OrderIntent.from_signal(
                signal,
                quantity=Decimal("1"),
                order_type=OrderType.MARKET,
                created_at=NOW,
            )

    def test_order_status_enum_covers_lifecycle(self):
        self.assertEqual(
            {status.value for status in OrderStatus},
            {
                "CREATED",
                "RISK_CHECKED",
                "SUBMITTED",
                "ACKNOWLEDGED",
                "PARTIALLY_FILLED",
                "FILLED",
                "CANCELED",
                "REJECTED",
                "EXPIRED",
                "FAILED",
            },
        )

    def test_fill_uses_decimal_precision(self):
        fill = Fill(
            fill_id="fill_001",
            order_id="order_001",
            symbol=Symbol("BTC/USDT"),
            venue=Venue("paper"),
            filled_at=NOW,
            quantity=Decimal("0.00000001"),
            price=Decimal("65000.12345678"),
            fee=Decimal("0.00000002"),
        )

        self.assertEqual(fill.to_dict()["quantity"], "1E-8")
        self.assertEqual(fill.to_dict()["price"], "65000.12345678")

    def test_portfolio_snapshot_serialization_roundtrip(self):
        snapshot = PortfolioSnapshot(
            portfolio_id="portfolio_fixture",
            timestamp=NOW,
            balances=(
                Balance(
                    asset="USDT",
                    total=Decimal("1000.00"),
                    available=Decimal("900.00"),
                    locked=Decimal("100.00"),
                ),
            ),
            positions=(),
            exposure=ExposureSnapshot(
                gross_exposure=Decimal("500.00"),
                net_exposure=Decimal("-250.00"),
                by_symbol={"BTC/USDT": Decimal("500.00")},
                by_venue={"paper": Decimal("500.00")},
            ),
            pnl=PnL(realized=Decimal("10.00"), unrealized=Decimal("-2.50"), fees=Decimal("0.25")),
        )

        restored = PortfolioSnapshot.from_dict(snapshot.to_dict())

        self.assertEqual(restored.to_dict(), snapshot.to_dict())
        self.assertEqual(snapshot.pnl.total, Decimal("7.25"))

    def test_balance_rejects_inconsistent_amounts(self):
        with self.assertRaises(ValueError):
            Balance(
                asset="USDT",
                total=Decimal("100"),
                available=Decimal("80"),
                locked=Decimal("30"),
            )

    def test_risk_result_cannot_mark_rejected_decision_as_executable(self):
        with self.assertRaises(ValueError):
            RiskCheckResult(
                risk_check_result_id="risk_result_001",
                request_id="risk_request_001",
                decision=RiskDecision.REJECT,
                checked_at=NOW,
                violations=(RiskViolation("max_notional", "blocked", "blocking"),),
                approved_for_execution=True,
            )

    def test_audit_event_serialization_roundtrip(self):
        event = AuditEvent(
            audit_event_id="audit_001",
            event_type=AuditEventType.RISK_CHECKED,
            occurred_at=NOW,
            correlation_id=CorrelationId("corr_001"),
            causation_id=CausationId("cause_001"),
            actor="deterministic-risk-gateway",
            subject="risk_result_001",
            outcome="rejected",
            metadata={"safe": True},
        )

        self.assertEqual(AuditEvent.from_dict(event.to_dict()), event)

    def test_naive_datetimes_are_rejected(self):
        with self.assertRaises(DomainModelError):
            Trade(
                trade_id="trade_002",
                symbol=Symbol("BTC/USDT"),
                venue=Venue("paper"),
                timestamp=datetime(2026, 5, 15, 12, 0),
                price=Decimal("1"),
                quantity=Decimal("1"),
            )


if __name__ == "__main__":
    unittest.main()
