import unittest
from datetime import datetime, timezone

from packages.contracts import ContractValidator
from risk import (
    BLOCKED_RUNTIME_CAPABILITIES,
    REQUIRED_RUNTIME_EVIDENCE,
    RuntimeActivationDecision,
    RuntimeMode,
    TradingRuntimeActivationRequest,
    TradingRuntimeGateError,
    evaluate_trading_runtime_activation,
)


NOW = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)


class TradingRuntimeGateImplementationTests(unittest.TestCase):
    def test_controlled_live_request_still_requires_separate_approval(self):
        request = TradingRuntimeActivationRequest(
            requested_runtime_mode=RuntimeMode.CONTROLLED_LIVE,
            requested_by="human-governance",
            requested_at=NOW,
            evidence=REQUIRED_RUNTIME_EVIDENCE,
        )

        report = evaluate_trading_runtime_activation(request, evaluated_at=NOW)

        self.assertEqual(report.decision, RuntimeActivationDecision.REQUIRES_SEPARATE_APPROVAL)
        self.assertEqual(report.missing_evidence, ())
        payload = report.to_contract_payload(trace_id="trace_runtime_gate_impl_001", correlation_id="corr_runtime_gate_impl_001")
        for capability in BLOCKED_RUNTIME_CAPABILITIES:
            with self.subTest(capability=capability):
                self.assertFalse(payload[capability])
        self.assertTrue(payload["risk_gateway_required"])
        self.assertTrue(payload["approved_order_required_for_execution"])
        self.assertTrue(payload["execution_engine_only_for_broker_access"])

    def test_payload_validates_against_contract_schema(self):
        request = TradingRuntimeActivationRequest(
            requested_runtime_mode=RuntimeMode.PAPER,
            requested_by="human-governance",
            requested_at=NOW,
            evidence=REQUIRED_RUNTIME_EVIDENCE,
        )
        report = evaluate_trading_runtime_activation(request, evaluated_at=NOW)
        payload = report.to_contract_payload(trace_id="trace_runtime_gate_impl_002", correlation_id="corr_runtime_gate_impl_002")

        result = ContractValidator().validate("trading", "trading_runtime_activation_gate", payload)

        self.assertTrue(result.valid, result.errors)

    def test_unsafe_runtime_capability_request_is_rejected(self):
        request = TradingRuntimeActivationRequest(
            requested_runtime_mode=RuntimeMode.CONTROLLED_LIVE,
            requested_by="human-governance",
            requested_at=NOW,
            evidence=REQUIRED_RUNTIME_EVIDENCE,
            live_trading_requested=True,
            network_requested=True,
            credentials_requested=True,
            order_submission_requested=True,
        )

        report = evaluate_trading_runtime_activation(request, evaluated_at=NOW)

        self.assertEqual(report.decision, RuntimeActivationDecision.REJECTED)
        payload = report.to_contract_payload(trace_id="trace_runtime_gate_impl_003", correlation_id="corr_runtime_gate_impl_003")
        self.assertFalse(payload["live_trading_allowed"])
        self.assertFalse(payload["network_allowed"])
        self.assertFalse(payload["credentials_allowed"])
        self.assertFalse(payload["order_submission_allowed"])

    def test_missing_evidence_is_reported_but_does_not_enable_runtime(self):
        request = TradingRuntimeActivationRequest(
            requested_runtime_mode=RuntimeMode.PAPER,
            requested_by="human-governance",
            requested_at=NOW,
            evidence=frozenset({"dataset_lineage_record"}),
        )

        report = evaluate_trading_runtime_activation(request, evaluated_at=NOW)

        self.assertIn("paper_trading_review_contract", report.missing_evidence)
        self.assertIn("kill_switch_policy", report.missing_evidence)
        payload = report.to_contract_payload(trace_id="trace_runtime_gate_impl_004", correlation_id="corr_runtime_gate_impl_004")
        self.assertFalse(payload["paper_runtime_allowed"])
        self.assertFalse(payload["live_trading_allowed"])

    def test_invalid_request_inputs_fail_closed(self):
        with self.assertRaises(TradingRuntimeGateError):
            TradingRuntimeActivationRequest(
                requested_runtime_mode=RuntimeMode.RESEARCH_ONLY,
                requested_by="human-governance",
                requested_at=NOW,
                evidence=frozenset({""}),
            )

    def test_gate_exposes_no_execution_methods(self):
        import risk.trading_runtime_gate as gate

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
            "place_order",
            "create_order",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(gate)))


if __name__ == "__main__":
    unittest.main()
