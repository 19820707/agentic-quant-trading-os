from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import unittest

from packages.contracts import ContractValidator
from packages.sdk import (
    LayerCapabilitySelection,
    ProfessionalTradingStackRequest,
    StackArtifact,
    StackCapability,
    StackConnection,
    StackDecision,
    StackLayer,
    StackStage,
    build_default_professional_trading_stack_governance,
    build_recommended_professional_stack_request,
)

NOW = datetime(2026, 6, 19, 12, 0, tzinfo=timezone.utc)
CONTRACT_GATES = frozenset(
    {
        "architecture_boundary_review",
        "contract_defined",
        "data_classification",
        "failure_mode_catalog",
        "owner_assigned",
        "traceability_plan",
    }
)


class ProfessionalTradingStackGovernanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.governance = build_default_professional_trading_stack_governance()

    def test_recommended_stack_covers_all_six_layers_and_strategy_families(self) -> None:
        request = build_recommended_professional_stack_request(StackStage.CONTRACT)
        selections = {selection.layer: selection.capabilities for selection in request.selections}

        self.assertEqual(set(selections), set(StackLayer))
        for capability in (
            StackCapability.TREND_FOLLOWING,
            StackCapability.MEAN_REVERSION,
            StackCapability.BREAKOUT,
            StackCapability.STATISTICAL_ARBITRAGE,
            StackCapability.MARKET_MAKING,
            StackCapability.SENTIMENT,
            StackCapability.VOLATILITY_TARGETING,
        ):
            self.assertIn(capability, selections[StackLayer.STRATEGY])

    def test_complete_contract_stack_is_allowed_without_runtime_authority(self) -> None:
        request = build_recommended_professional_stack_request(
            StackStage.CONTRACT,
            completed_gates=CONTRACT_GATES,
        )

        assessment = self.governance.assess(request)

        self.assertEqual(assessment.decision, StackDecision.ALLOWED_FOR_LOCAL_STAGE)
        self.assertEqual(assessment.missing_layers, ())
        self.assertEqual(assessment.missing_capabilities, ())
        self.assertEqual(assessment.missing_connections, ())
        self.assertEqual(assessment.invalid_connections, ())
        self.assertFalse(assessment.credentials_allowed)
        self.assertFalse(assessment.network_runtime_allowed)
        self.assertFalse(assessment.live_execution_allowed)

        payload = assessment.to_contract_payload(
            trace_id="trace_professional_stack_001",
            correlation_id="corr_professional_stack_001",
            assessed_at=NOW,
        )
        validation = ContractValidator().validate(
            "governance",
            "professional_trading_stack_assessment",
            payload,
        )
        self.assertTrue(validation.valid, validation.errors)

    def test_direct_strategy_to_execution_path_is_rejected(self) -> None:
        request = build_recommended_professional_stack_request(StackStage.CONTRACT)
        unsafe = StackConnection(
            StackLayer.STRATEGY,
            StackLayer.EXECUTION,
            StackArtifact.SIGNAL_CANDIDATE,
        )

        assessment = self.governance.assess(replace(request, connections=request.connections + (unsafe,)))

        self.assertEqual(assessment.decision, StackDecision.REJECTED_FORBIDDEN_PATH)
        self.assertIn(unsafe.label(), assessment.invalid_connections)

    def test_execution_accepts_only_approved_order_from_risk(self) -> None:
        request = build_recommended_professional_stack_request(StackStage.CONTRACT)
        unsafe = StackConnection(
            StackLayer.RESEARCH_AI,
            StackLayer.EXECUTION,
            StackArtifact.APPROVED_ORDER,
        )

        assessment = self.governance.assess(replace(request, connections=(unsafe,)))

        self.assertEqual(assessment.decision, StackDecision.REJECTED_FORBIDDEN_PATH)
        self.assertTrue(assessment.approved_order_only)
        self.assertTrue(assessment.deterministic_risk_gateway_required)

    def test_missing_risk_to_execution_connection_is_rejected(self) -> None:
        request = build_recommended_professional_stack_request(StackStage.CONTRACT)
        connections = tuple(
            connection
            for connection in request.connections
            if not (
                connection.source is StackLayer.RISK
                and connection.target is StackLayer.EXECUTION
            )
        )

        assessment = self.governance.assess(replace(request, connections=connections))

        self.assertEqual(assessment.decision, StackDecision.REJECTED_INCOMPLETE_STACK)
        self.assertIn(
            "risk->execution:ApprovedOrder",
            assessment.missing_connections,
        )

    def test_incomplete_security_and_risk_layers_fail_closed(self) -> None:
        request = build_recommended_professional_stack_request(StackStage.CONTRACT)
        reduced = tuple(
            selection
            for selection in request.selections
            if selection.layer not in {StackLayer.RISK, StackLayer.SECURITY_OPERATIONS}
        )

        assessment = self.governance.assess(replace(request, selections=reduced))

        self.assertEqual(assessment.decision, StackDecision.REJECTED_INCOMPLETE_STACK)
        self.assertIn(StackLayer.RISK.value, assessment.missing_layers)
        self.assertIn(StackLayer.SECURITY_OPERATIONS.value, assessment.missing_layers)

    def test_strategy_layer_requires_signal_only_and_a_versioned_family(self) -> None:
        request = build_recommended_professional_stack_request(StackStage.CONTRACT)
        selections = tuple(
            LayerCapabilitySelection(
                layer=selection.layer,
                capabilities=(
                    frozenset({StackCapability.STRATEGY_VERSIONING})
                    if selection.layer is StackLayer.STRATEGY
                    else selection.capabilities
                ),
            )
            for selection in request.selections
        )

        assessment = self.governance.assess(replace(request, selections=selections))

        self.assertEqual(assessment.decision, StackDecision.REJECTED_INCOMPLETE_STACK)
        self.assertIn("strategy:signal_only_output", assessment.missing_capabilities)
        self.assertIn("strategy:at_least_one_versioned_strategy_family", assessment.missing_capabilities)

    def test_paper_stage_requires_data_risk_execution_and_operations_evidence(self) -> None:
        assessment = self.governance.assess(
            build_recommended_professional_stack_request(StackStage.PAPER)
        )

        self.assertEqual(assessment.decision, StackDecision.REQUIRES_GATES)
        for gate in (
            "dataset_lineage_review",
            "leakage_review",
            "backtest_review",
            "paper_trading_evidence",
            "deterministic_risk_gateway",
            "kill_switch",
            "reconciliation",
            "observability_slo",
        ):
            self.assertIn(gate, assessment.required_gates)
        self.assertFalse(assessment.live_execution_allowed)

    def test_controlled_live_never_grants_authority_and_requires_security_controls(self) -> None:
        assessment = self.governance.assess(
            build_recommended_professional_stack_request(StackStage.CONTROLLED_LIVE)
        )

        self.assertEqual(assessment.decision, StackDecision.REQUIRES_GATES)
        for gate in (
            "credential_vault",
            "trade_only_credentials",
            "withdrawal_permissions_disabled",
            "ip_allowlist",
            "key_rotation",
            "network_approval",
            "human_approval",
            "capital_limit_approval",
            "rollback_plan",
            "disaster_recovery_test",
        ):
            self.assertIn(gate, assessment.required_gates)
        self.assertTrue(assessment.no_withdrawal_enforced)
        self.assertFalse(assessment.credentials_allowed)
        self.assertFalse(assessment.network_runtime_allowed)
        self.assertFalse(assessment.live_execution_allowed)

    def test_governance_exposes_no_execution_methods(self) -> None:
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
            "create_order",
        }

        self.assertTrue(forbidden.isdisjoint(dir(self.governance)))


if __name__ == "__main__":
    unittest.main()
