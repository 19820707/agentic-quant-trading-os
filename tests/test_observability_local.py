from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from backtesting import BacktestMetrics
from observability import LocalObservabilitySink, LogLevel, ObservabilityError, sanitize_attributes
from packages.domain import AuditEvent, AuditEventType, CausationId, CorrelationId


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)


def audit_event(
    index: int,
    *,
    correlation_id: CorrelationId,
    causation_id: CausationId | None = None,
    actor: str = "risk",
    outcome: str = "checked",
) -> AuditEvent:
    return AuditEvent(
        audit_event_id=f"audit_{index:03d}",
        event_type=AuditEventType.RISK_CHECKED,
        occurred_at=NOW + timedelta(seconds=index),
        correlation_id=correlation_id,
        causation_id=causation_id,
        actor=actor,
        subject=f"subject_{index:03d}",
        outcome=outcome,
        metadata={"safe": True},
    )


class LocalObservabilityTests(unittest.TestCase):
    def test_structured_logs_redact_sensitive_attributes(self) -> None:
        sink = LocalObservabilitySink()
        secret_key = "pass" + "word"
        record = sink.log(
            level=LogLevel.INFO,
            component="strategy",
            message="local event",
            correlation_id=CorrelationId("corr_obs"),
            occurred_at=NOW,
            attributes={secret_key: "local-test-value", "safe": "visible"},
        )

        self.assertEqual(record.attributes[secret_key], "[REDACTED]")
        self.assertEqual(record.attributes["safe"], "visible")

    def test_sanitize_attributes_redacts_sensitive_keys_only(self) -> None:
        secret_key = "api" + "_credential"
        sanitized = sanitize_attributes({secret_key: "value", "component": "risk"})

        self.assertEqual(sanitized[secret_key], "[REDACTED]")
        self.assertEqual(sanitized["component"], "risk")

    def test_audit_events_are_sorted_and_metrics_are_recorded(self) -> None:
        sink = LocalObservabilitySink()
        corr = CorrelationId("corr_obs")

        sink.record_audit_event(audit_event(2, correlation_id=corr, actor="oms", outcome="submitted"))
        sink.record_audit_event(audit_event(1, correlation_id=corr, actor="risk", outcome="rejected"))

        self.assertEqual([event.audit_event_id for event in sink.audit_events], ["audit_001", "audit_002"])
        snapshot = sink.metrics_snapshot(captured_at=NOW)
        self.assertIn("audit_events_total{actor=risk,event_type=RISK_CHECKED,outcome=rejected}", snapshot.counters)
        self.assertEqual(snapshot.counters["audit_events_total{actor=risk,event_type=RISK_CHECKED,outcome=rejected}"], Decimal("1"))

    def test_trace_report_groups_by_correlation_id_and_causation(self) -> None:
        sink = LocalObservabilitySink()
        corr = CorrelationId("corr_trace")
        other = CorrelationId("corr_other")

        sink.record_audit_event(audit_event(1, correlation_id=corr, causation_id=CausationId("cause_001"), actor="strategy"))
        sink.record_audit_event(audit_event(2, correlation_id=corr, actor="risk", outcome="review"))
        sink.record_audit_event(audit_event(3, correlation_id=other, actor="risk", outcome="ignored"))
        sink.log(level=LogLevel.WARNING, component="risk", message="review", correlation_id=corr, occurred_at=NOW)

        report = sink.trace_report(corr, generated_at=NOW)

        self.assertEqual(report.audit_event_count, 2)
        self.assertEqual(report.log_count, 1)
        self.assertEqual(report.actors, ("risk", "strategy"))
        self.assertEqual(report.missing_causation_count, 1)
        self.assertEqual(report.causal_edges, (("cause_001", "audit_001"),))
        self.assertEqual(report.outcomes, ("checked", "review"))

    def test_backtest_metrics_are_exported_to_local_gauges(self) -> None:
        sink = LocalObservabilitySink()
        metrics = BacktestMetrics(
            events_seen=4,
            candles_seen=4,
            signals_emitted=2,
            order_intents_created=0,
            risk_checks=0,
            rejected_risk_checks=0,
            review_risk_checks=0,
            approved_risk_checks=0,
            paper_orders=0,
            paper_fills=0,
            final_equity=Decimal("9990"),
            total_pnl=Decimal("-10"),
            max_drawdown=Decimal("10"),
        )

        sink.record_backtest_metrics(
            backtest_id="bt_obs",
            correlation_id=CorrelationId("corr_obs"),
            observed_at=NOW,
            metrics=metrics,
        )
        snapshot = sink.metrics_snapshot(captured_at=NOW)

        self.assertEqual(snapshot.gauges["backtest_events_seen{backtest_id=bt_obs,correlation_id=corr_obs}"], Decimal("4"))
        self.assertEqual(snapshot.gauges["backtest_total_pnl{backtest_id=bt_obs,correlation_id=corr_obs}"], Decimal("-10"))

    def test_counter_rejects_negative_values(self) -> None:
        sink = LocalObservabilitySink()

        with self.assertRaises(ValueError):
            sink.increment_counter("unsafe_counter", amount=Decimal("-1"), observed_at=NOW)

    def test_sink_exposes_no_execution_surface(self) -> None:
        sink = LocalObservabilitySink()
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

        self.assertTrue(forbidden.isdisjoint(dir(sink)))

    def test_metric_tags_reject_sensitive_identifiers(self) -> None:
        sink = LocalObservabilitySink()
        secret_tag = "private" + "_identifier"

        with self.assertRaises(ObservabilityError):
            sink.set_gauge("unsafe_metric", Decimal("1"), observed_at=NOW, tags={secret_tag: "x"})


if __name__ == "__main__":
    unittest.main()
