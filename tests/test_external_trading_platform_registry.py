from __future__ import annotations

from datetime import datetime, timezone
import unittest

from packages.contracts import ContractValidator
from packages.sdk import (
    AssessmentDecision,
    CredentialBoundary,
    IntegrationBoundary,
    IntegrationStage,
    PlatformCapability,
    PlatformIntegrationRequest,
    PlatformRegistryError,
    build_default_external_trading_platform_registry,
)

NOW = datetime(2026, 6, 19, 12, 0, tzinfo=timezone.utc)


class ExternalTradingPlatformRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = build_default_external_trading_platform_registry()

    def test_registry_contains_all_ranked_platforms_with_explicit_boundaries(self) -> None:
        profiles = {profile.platform_id: profile for profile in self.registry.list_profiles()}

        self.assertEqual(
            set(profiles),
            {
                "quantconnect-lean",
                "interactive-brokers",
                "alpaca",
                "ninjatrader",
                "tradestation",
                "hummingbot",
                "tradingview",
                "metatrader-5",
                "ctrader",
                "3commas",
                "cryptohopper",
                "pionex",
                "coinrule",
                "bitsgap",
                "tradesanta",
                "wundertrading",
                "trendspider",
            },
        )
        self.assertEqual(profiles["interactive-brokers"].boundary, IntegrationBoundary.EXECUTION_ENGINE_ONLY)
        self.assertEqual(profiles["alpaca"].boundary, IntegrationBoundary.EXECUTION_ENGINE_ONLY)
        self.assertEqual(profiles["ninjatrader"].boundary, IntegrationBoundary.TERMINAL_ADAPTER_BOUNDARY)
        self.assertEqual(profiles["tradestation"].boundary, IntegrationBoundary.EXECUTION_ENGINE_ONLY)
        self.assertEqual(profiles["tradingview"].boundary, IntegrationBoundary.SIGNAL_INTAKE_ONLY)
        self.assertEqual(profiles["hummingbot"].boundary, IntegrationBoundary.ISOLATED_STRATEGY_SANDBOX)
        self.assertEqual(profiles["3commas"].boundary, IntegrationBoundary.EXTERNAL_SAAS_REFERENCE)
        self.assertEqual(profiles["pionex"].boundary, IntegrationBoundary.EXCHANGE_NATIVE_AUTOMATION)
        self.assertEqual(profiles["trendspider"].boundary, IntegrationBoundary.SIGNAL_INTAKE_ONLY)
        self.assertEqual(profiles["cryptohopper"].credential_boundary, CredentialBoundary.EXTERNAL_SAAS)
        self.assertEqual(profiles["pionex"].credential_boundary, CredentialBoundary.EXCHANGE_NATIVE)

    def test_contract_stage_is_available_without_runtime_authority(self) -> None:
        request = PlatformIntegrationRequest(
            platform_id="interactive-brokers",
            requested_stage=IntegrationStage.CONTRACT,
            requested_capabilities=frozenset({PlatformCapability.ACCOUNT_STATE}),
            target_boundary=IntegrationBoundary.EXECUTION_ENGINE_ONLY,
            completed_gates=frozenset(
                {
                    "license_review",
                    "security_review",
                    "architecture_boundary_review",
                    "contract_defined",
                    "owner_assigned",
                    "terminal_gateway_health",
                    "session_recovery",
                    "credential_scope_review",
                    "key_rotation",
                    "withdrawal_permission_forbidden",
                }
            ),
        )

        assessment = self.registry.assess(request)

        self.assertEqual(assessment.decision, AssessmentDecision.ALLOWED_FOR_CURRENT_STAGE)
        self.assertFalse(assessment.credentials_allowed)
        self.assertFalse(assessment.network_runtime_allowed)
        self.assertFalse(assessment.live_execution_allowed)
        self.assertTrue(assessment.execution_engine_only)

    def test_tradingview_signal_intake_derives_webhook_safety_gates(self) -> None:
        request = PlatformIntegrationRequest(
            platform_id="tradingview",
            requested_stage=IntegrationStage.FAKE,
            requested_capabilities=frozenset({PlatformCapability.SIGNAL_INGESTION}),
            target_boundary=IntegrationBoundary.SIGNAL_INTAKE_ONLY,
        )

        assessment = self.registry.assess(request)

        self.assertEqual(assessment.decision, AssessmentDecision.REQUIRES_GATES)
        for gate in ("webhook_authentication", "schema_validation", "replay_protection", "rate_limit_policy"):
            self.assertIn(gate, assessment.required_gates)
        self.assertIn("signal_candidate_mapping", assessment.allowed_actions)
        self.assertFalse(assessment.risk_gateway_required)

    def test_execution_request_requires_full_execution_and_live_gates(self) -> None:
        request = PlatformIntegrationRequest(
            platform_id="interactive-brokers",
            requested_stage=IntegrationStage.CONTROLLED_LIVE,
            requested_capabilities=frozenset(
                {
                    PlatformCapability.LIVE_MARKET_DATA,
                    PlatformCapability.ORDER_EXECUTION,
                    PlatformCapability.RECONCILIATION,
                }
            ),
            target_boundary=IntegrationBoundary.EXECUTION_ENGINE_ONLY,
        )

        assessment = self.registry.assess(request)

        self.assertEqual(assessment.decision, AssessmentDecision.REQUIRES_GATES)
        for gate in (
            "deterministic_risk_gateway",
            "approved_order_only",
            "credential_vault",
            "network_approval",
            "idempotency",
            "order_state_machine",
            "execution_report",
            "reconciliation",
            "no_withdrawal_permissions",
        ):
            self.assertIn(gate, assessment.required_gates)
        self.assertTrue(assessment.risk_gateway_required)
        self.assertTrue(assessment.approved_order_required)
        self.assertFalse(assessment.live_execution_allowed)

        payload = assessment.to_contract_payload(
            trace_id="trace_platform_registry_001",
            correlation_id="corr_platform_registry_001",
            assessed_at=NOW,
        )
        validation = ContractValidator().validate(
            "governance",
            "external_platform_capability_assessment",
            payload,
        )
        self.assertTrue(validation.valid, validation.errors)

    def test_hummingbot_requires_isolation_and_rejects_wrong_boundary(self) -> None:
        request = PlatformIntegrationRequest(
            platform_id="hummingbot",
            requested_stage=IntegrationStage.FAKE,
            requested_capabilities=frozenset({PlatformCapability.MARKET_MAKING}),
            target_boundary=IntegrationBoundary.EXECUTION_ENGINE_ONLY,
        )

        assessment = self.registry.assess(request)

        self.assertEqual(assessment.decision, AssessmentDecision.REJECTED_BOUNDARY_MISMATCH)
        self.assertIn("process_isolation", assessment.required_gates)
        self.assertIn("runtime_kill_switch", assessment.required_gates)
        self.assertIn("strategy_logic_reference", assessment.allowed_actions)

    def test_commercial_grid_and_dca_request_derives_operational_risk_gates(self) -> None:
        assessment = self.registry.assess(
            PlatformIntegrationRequest(
                platform_id="3commas",
                requested_stage=IntegrationStage.PAPER,
                requested_capabilities=frozenset(
                    {
                        PlatformCapability.GRID_TRADING,
                        PlatformCapability.DCA_TRADING,
                        PlatformCapability.ORDER_EXECUTION,
                    }
                ),
                target_boundary=IntegrationBoundary.EXTERNAL_SAAS_REFERENCE,
            )
        )

        self.assertEqual(assessment.decision, AssessmentDecision.REQUIRES_GATES)
        for gate in (
            "vendor_due_diligence",
            "vendor_incident_response",
            "capital_subaccount_isolation",
            "trade_only_api_key",
            "withdrawal_permission_forbidden",
            "ip_allowlist",
            "grid_range_guard",
            "max_active_orders",
            "range_breakout_policy",
            "max_safety_orders",
            "max_position_notional",
            "dca_drawdown_policy",
            "deterministic_risk_gateway",
            "approved_order_only",
        ):
            self.assertIn(gate, assessment.required_gates)
        self.assertTrue(assessment.risk_gateway_required)
        self.assertTrue(assessment.approved_order_required)
        self.assertFalse(assessment.credentials_allowed)
        self.assertFalse(assessment.network_runtime_allowed)
        self.assertFalse(assessment.live_execution_allowed)

    def test_copy_trading_requires_provenance_and_independent_risk_limits(self) -> None:
        assessment = self.registry.assess(
            PlatformIntegrationRequest(
                platform_id="cryptohopper",
                requested_stage=IntegrationStage.FAKE,
                requested_capabilities=frozenset({PlatformCapability.COPY_TRADING}),
                target_boundary=IntegrationBoundary.EXTERNAL_SAAS_REFERENCE,
            )
        )

        for gate in ("copy_source_provenance", "copy_risk_limits", "copy_latency_review"):
            self.assertIn(gate, assessment.required_gates)
        self.assertIn("strategy_semantics_review", assessment.allowed_actions)
        self.assertFalse(assessment.live_execution_allowed)

    def test_trendspider_alerts_remain_signal_intake_only(self) -> None:
        assessment = self.registry.assess(
            PlatformIntegrationRequest(
                platform_id="trendspider",
                requested_stage=IntegrationStage.FAKE,
                requested_capabilities=frozenset(
                    {
                        PlatformCapability.SIGNAL_INGESTION,
                        PlatformCapability.TRADINGVIEW_BRIDGE,
                    }
                ),
                target_boundary=IntegrationBoundary.SIGNAL_INTAKE_ONLY,
            )
        )

        for gate in ("webhook_authentication", "replay_protection", "payload_allowlist"):
            self.assertIn(gate, assessment.required_gates)
        self.assertIn("alert_semantics_review", assessment.allowed_actions)
        self.assertFalse(assessment.risk_gateway_required)
        self.assertFalse(assessment.live_execution_allowed)

    def test_unsupported_capability_is_rejected(self) -> None:
        assessment = self.registry.assess(
            PlatformIntegrationRequest(
                platform_id="tradingview",
                requested_stage=IntegrationStage.CONTRACT,
                requested_capabilities=frozenset({PlatformCapability.ORDER_EXECUTION}),
                target_boundary=IntegrationBoundary.SIGNAL_INTAKE_ONLY,
            )
        )

        self.assertEqual(assessment.decision, AssessmentDecision.REJECTED_UNSUPPORTED_CAPABILITY)
        self.assertEqual(assessment.unsupported_capabilities, ("order_execution",))

    def test_unknown_platform_fails_explicitly(self) -> None:
        with self.assertRaises(PlatformRegistryError):
            self.registry.get("unknown-platform")

    def test_registry_exposes_no_execution_methods(self) -> None:
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

        self.assertTrue(forbidden.isdisjoint(dir(self.registry)))


if __name__ == "__main__":
    unittest.main()
