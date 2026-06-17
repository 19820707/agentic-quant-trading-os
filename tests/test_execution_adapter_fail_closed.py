from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from adapters import (
    ExecutionAdapterConfig,
    ExecutionAdapterError,
    ExecutionAdapterState,
    FailClosedExecutionAdapter,
    validate_execution_adapter_surface,
)
from packages.domain import OrderRequest, OrderStatus, OrderType, SignalSide, Symbol, TimeInForce, Venue


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)


def order_request() -> OrderRequest:
    return OrderRequest(
        order_request_id="order_request_fixture",
        order_intent_id="intent_fixture",
        approved_order_id="approved_fixture",
        symbol=Symbol("BTC/USDT"),
        venue=Venue("paper"),
        side=SignalSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1"),
        created_at=NOW,
        time_in_force=TimeInForce.GTC,
        limit_price=Decimal("100"),
    )


class FailClosedExecutionAdapterTests(unittest.TestCase):
    def test_config_rejects_live_network_credentials_and_non_paper_mode(self) -> None:
        for flag in ("live_trading_enabled", "network_allowed", "credentials_allowed"):
            with self.subTest(flag=flag):
                with self.assertRaises(ExecutionAdapterError):
                    ExecutionAdapterConfig(adapter_name="local", **{flag: True})

        with self.assertRaises(ExecutionAdapterError):
            ExecutionAdapterConfig(adapter_name="local", paper_only=False)

    def test_disabled_adapter_reports_disabled_health(self) -> None:
        adapter = FailClosedExecutionAdapter(ExecutionAdapterConfig(adapter_name="local"))

        health = adapter.health()

        self.assertEqual(health.state, ExecutionAdapterState.DISABLED)
        self.assertFalse(health.live_trading_enabled)
        self.assertFalse(health.network_allowed)
        self.assertFalse(health.credentials_allowed)

    def test_enabled_adapter_is_review_only_and_rejects_request(self) -> None:
        adapter = FailClosedExecutionAdapter(ExecutionAdapterConfig(adapter_name="local", enabled=True))

        health = adapter.health()
        report = adapter.review_order_request(order_request(), requested_at=NOW)

        self.assertEqual(health.state, ExecutionAdapterState.PAPER_ONLY)
        self.assertEqual(report.status, OrderStatus.REJECTED)
        self.assertEqual(report.filled_quantity, Decimal("0"))
        self.assertEqual(report.remaining_quantity, Decimal("1"))
        self.assertIsNone(report.average_fill_price)

    def test_report_id_is_deterministic(self) -> None:
        adapter = FailClosedExecutionAdapter(ExecutionAdapterConfig(adapter_name="local", enabled=True))

        first = adapter.review_order_request(order_request(), requested_at=NOW)
        second = adapter.review_order_request(order_request(), requested_at=NOW)

        self.assertEqual(first.execution_report_id, second.execution_report_id)

    def test_adapter_surface_rejects_execution_like_methods(self) -> None:
        unsafe_name = "submit_" + "order"
        UnsafeAdapter = type("UnsafeAdapter", (), {unsafe_name: lambda self: None})

        with self.assertRaises(ExecutionAdapterError):
            validate_execution_adapter_surface(UnsafeAdapter())

    def test_fail_closed_adapter_exposes_no_prohibited_methods(self) -> None:
        adapter = FailClosedExecutionAdapter(ExecutionAdapterConfig(adapter_name="local"))
        forbidden = {
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

        self.assertTrue(forbidden.isdisjoint(dir(adapter)))


if __name__ == "__main__":
    unittest.main()
