from __future__ import annotations

import unittest

from packages.contracts import ContractValidator
from packages.sdk import (
    AuthenticationModel,
    DeploymentModel,
    IntegrationBoundary,
    IntegrationPriority,
    PlatformRole,
    PlatformDueDiligenceError,
    SimulationModel,
    build_default_external_platform_due_diligence_catalog,
    build_default_external_trading_platform_registry,
)


class ExternalPlatformDueDiligenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = build_default_external_trading_platform_registry()
        self.catalog = build_default_external_platform_due_diligence_catalog(self.registry)

    def test_registry_adds_missing_professional_platforms_with_safe_boundaries(self) -> None:
        alpaca = self.registry.get("alpaca")
        ninja = self.registry.get("ninjatrader")
        tradestation = self.registry.get("tradestation")

        self.assertEqual(alpaca.boundary, IntegrationBoundary.EXECUTION_ENGINE_ONLY)
        self.assertEqual(ninja.boundary, IntegrationBoundary.TERMINAL_ADAPTER_BOUNDARY)
        self.assertEqual(tradestation.boundary, IntegrationBoundary.EXECUTION_ENGINE_ONLY)
        self.assertTrue(alpaca.supports_demo_or_paper)
        self.assertTrue(ninja.requires_terminal_or_gateway)
        self.assertTrue(tradestation.supports_demo_or_paper)

    def test_catalog_uses_official_https_evidence_and_remains_reference_only(self) -> None:
        records = self.catalog.list_records()

        self.assertEqual(len(records), 9)
        for record in records:
            with self.subTest(platform=record.platform_id):
                self.assertTrue(record.reference_only)
                self.assertTrue(record.approved_order_only)
                self.assertFalse(record.credentials_allowed)
                self.assertFalse(record.network_runtime_allowed)
                self.assertFalse(record.live_execution_allowed)
                self.assertTrue(all(item.url.startswith("https://") for item in record.evidence))
                self.assertTrue(record.official_hosts)

    def test_alpaca_is_a_paper_candidate_with_explicit_simulation_caveats(self) -> None:
        record = self.catalog.get("alpaca")

        self.assertEqual(record.role, PlatformRole.DEVELOPER_BROKER_API)
        self.assertEqual(record.deployment_model, DeploymentModel.CLOUD_API)
        self.assertEqual(record.authentication_model, AuthenticationModel.API_KEY)
        self.assertEqual(record.simulation_model, SimulationModel.VENDOR_SIM_API)
        self.assertEqual(record.integration_priority, IntegrationPriority.PAPER_ADAPTER_CANDIDATE)
        self.assertIn("paper_live_endpoint_separation", record.required_controls)
        self.assertTrue(any("liquidity" in caveat for caveat in record.operational_caveats))

    def test_ibkr_due_diligence_requires_gateway_session_and_pacing_controls(self) -> None:
        record = self.catalog.get("interactive-brokers")

        self.assertEqual(record.deployment_model, DeploymentModel.LOCAL_GATEWAY)
        for control in ("gateway_health", "session_recovery", "pacing_budget"):
            self.assertIn(control, record.required_controls)

    def test_ninjatrader_distinguishes_ati_from_general_broker_api(self) -> None:
        record = self.catalog.get("ninjatrader")

        claims = " ".join(item.claim for item in record.evidence)
        self.assertIn("not a general brokerage or market-data API", claims)
        self.assertIn("ati_semantics_review", record.required_controls)
        self.assertEqual(record.integration_priority, IntegrationPriority.ISOLATED_RUNTIME_REVIEW)

    def test_tradestation_requires_sim_live_and_oauth_scope_separation(self) -> None:
        record = self.catalog.get("tradestation")

        self.assertEqual(record.authentication_model, AuthenticationModel.OAUTH2)
        for control in ("sim_live_url_separation", "oauth_scope_review", "token_rotation"):
            self.assertIn(control, record.required_controls)
        self.assertTrue(any("instant fills" in caveat for caveat in record.operational_caveats))

    def test_tradingview_is_signal_contract_only(self) -> None:
        record = self.catalog.get("tradingview")

        self.assertEqual(record.role, PlatformRole.SIGNAL_SOURCE)
        self.assertEqual(record.integration_priority, IntegrationPriority.SIGNAL_CONTRACT_ONLY)
        self.assertIn("signal_candidate_mapping", record.required_controls)
        self.assertNotIn("approved_order_submission", record.required_controls)

    def test_due_diligence_payload_validates_against_contract(self) -> None:
        payload = self.catalog.get("alpaca").to_contract_payload()
        validation = ContractValidator().validate(
            "governance",
            "external_platform_due_diligence",
            payload,
        )

        self.assertTrue(validation.valid, validation.errors)

    def test_unapproved_evidence_host_is_rejected(self) -> None:
        record = self.catalog.get("alpaca")

        with self.assertRaises(PlatformDueDiligenceError):
            type(record)(
                platform_id=record.platform_id,
                role=record.role,
                deployment_model=record.deployment_model,
                authentication_model=record.authentication_model,
                simulation_model=record.simulation_model,
                integration_priority=record.integration_priority,
                official_hosts=record.official_hosts,
                evidence=(
                    type(record.evidence[0])(
                        claim="Affiliate comparison claim.",
                        url="https://example.com/ranking",
                    ),
                ),
                operational_caveats=record.operational_caveats,
                required_controls=record.required_controls,
            )

    def test_catalog_exposes_no_execution_methods(self) -> None:
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

        self.assertTrue(forbidden.isdisjoint(dir(self.catalog)))


if __name__ == "__main__":
    unittest.main()
