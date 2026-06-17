import unittest
from datetime import datetime, timezone

from oms import (
    ALLOWED_TRANSITIONS,
    TERMINAL_STATUSES,
    OrderStateTransition,
    OrderStateTransitionError,
    allowed_next_statuses,
    assert_transition_allowed,
)
from packages.domain import AuditEvent, AuditEventType, CausationId, CorrelationId, OrderStatus


NOW = datetime(2026, 5, 15, 13, 0, tzinfo=timezone.utc)


class OmsStateMachineTests(unittest.TestCase):
    def test_created_order_can_move_to_risk_checked(self):
        assert_transition_allowed(OrderStatus.CREATED, OrderStatus.RISK_CHECKED)

        transition = OrderStateTransition(
            order_id="order_001",
            previous_status=OrderStatus.CREATED,
            next_status=OrderStatus.RISK_CHECKED,
            occurred_at=NOW,
            reason="risk gate accepted for next lifecycle stage",
            correlation_id=CorrelationId("corr_oms_001"),
            causation_id=CausationId("risk_result_001"),
        )

        self.assertTrue(transition.transition_id.startswith("ordst_"))

    def test_allowed_transition_map_covers_every_order_status(self):
        self.assertEqual(set(OrderStatus), set(ALLOWED_TRANSITIONS))
        for status in OrderStatus:
            with self.subTest(status=status):
                self.assertIsInstance(allowed_next_statuses(status), frozenset)

    def test_invalid_transition_is_rejected(self):
        with self.assertRaises(OrderStateTransitionError):
            assert_transition_allowed(OrderStatus.CREATED, OrderStatus.FILLED)

    def test_terminal_statuses_cannot_transition(self):
        for status in TERMINAL_STATUSES:
            with self.subTest(status=status):
                with self.assertRaises(OrderStateTransitionError):
                    assert_transition_allowed(status, OrderStatus.FAILED)

    def test_partial_fill_can_repeat_or_complete(self):
        self.assertIn(OrderStatus.PARTIALLY_FILLED, allowed_next_statuses(OrderStatus.PARTIALLY_FILLED))
        self.assertIn(OrderStatus.FILLED, allowed_next_statuses(OrderStatus.PARTIALLY_FILLED))

    def test_state_transition_builds_audit_event(self):
        transition = OrderStateTransition(
            order_id="order_002",
            previous_status=OrderStatus.ACKNOWLEDGED,
            next_status=OrderStatus.PARTIALLY_FILLED,
            occurred_at=NOW,
            reason="local lifecycle fixture",
            correlation_id=CorrelationId("corr_oms_002"),
        )

        event = transition.to_audit_event()

        self.assertIsInstance(event, AuditEvent)
        self.assertEqual(event.event_type, AuditEventType.ORDER_STATE_CHANGED)
        self.assertEqual(event.subject, "order_002")
        self.assertEqual(event.outcome, "PARTIALLY_FILLED")
        self.assertEqual(event.metadata["previous_status"], "ACKNOWLEDGED")

    def test_state_machine_exposes_no_execution_methods(self):
        import oms.state_machine as state_machine

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

        self.assertTrue(forbidden_names.isdisjoint(dir(state_machine)))


if __name__ == "__main__":
    unittest.main()
