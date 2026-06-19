from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from .external_trading_platform_registry import (
    ExternalTradingPlatformRegistry,
    IntegrationBoundary,
)


class PlatformDueDiligenceError(ValueError):
    """Raised when platform evidence or classification is inconsistent."""


class PlatformRole(str, Enum):
    RESEARCH_BACKTEST = "research_backtest"
    INSTITUTIONAL_BROKER_API = "institutional_broker_api"
    DEVELOPER_BROKER_API = "developer_broker_api"
    FUTURES_STRATEGY_TERMINAL = "futures_strategy_terminal"
    TRADITIONAL_MULTI_ASSET_API = "traditional_multi_asset_api"
    FOREX_CFD_TERMINAL = "forex_cfd_terminal"
    CRYPTO_STRATEGY_RUNTIME = "crypto_strategy_runtime"
    SIGNAL_SOURCE = "signal_source"


class DeploymentModel(str, Enum):
    LOCAL_ENGINE = "local_engine"
    CLOUD_API = "cloud_api"
    LOCAL_GATEWAY = "local_gateway"
    DESKTOP_TERMINAL = "desktop_terminal"
    EXTERNAL_RUNTIME = "external_runtime"


class AuthenticationModel(str, Enum):
    BROKER_SESSION = "broker_session"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    EXCHANGE_API_KEYS = "exchange_api_keys"
    NONE_FOR_SIGNAL_PAYLOAD = "none_for_signal_payload"


class SimulationModel(str, Enum):
    LOCAL_BACKTEST = "local_backtest"
    BROKER_PAPER_ACCOUNT = "broker_paper_account"
    VENDOR_SIM_API = "vendor_sim_api"
    TERMINAL_SIMULATION = "terminal_simulation"
    CONNECTOR_PAPER_RUNTIME = "connector_paper_runtime"
    NONE = "none"


class IntegrationPriority(str, Enum):
    RESEARCH_REFERENCE = "research_reference"
    PAPER_ADAPTER_CANDIDATE = "paper_adapter_candidate"
    DEFERRED_EXECUTION_ADAPTER = "deferred_execution_adapter"
    ISOLATED_RUNTIME_REVIEW = "isolated_runtime_review"
    SIGNAL_CONTRACT_ONLY = "signal_contract_only"


@dataclass(frozen=True)
class OfficialEvidence:
    claim: str
    url: str

    def __post_init__(self) -> None:
        if not self.claim.strip():
            raise PlatformDueDiligenceError("evidence claim must be non-empty")
        if not self.url.startswith("https://"):
            raise PlatformDueDiligenceError("official evidence must use HTTPS")


@dataclass(frozen=True)
class PlatformDueDiligenceRecord:
    platform_id: str
    role: PlatformRole
    deployment_model: DeploymentModel
    authentication_model: AuthenticationModel
    simulation_model: SimulationModel
    integration_priority: IntegrationPriority
    official_hosts: frozenset[str]
    evidence: tuple[OfficialEvidence, ...]
    operational_caveats: tuple[str, ...]
    required_controls: frozenset[str]
    reference_only: bool = True
    approved_order_only: bool = True
    credentials_allowed: bool = False
    network_runtime_allowed: bool = False
    live_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.platform_id.strip():
            raise PlatformDueDiligenceError("platform_id must be non-empty")
        if not self.evidence:
            raise PlatformDueDiligenceError("at least one official evidence source is required")
        if not self.official_hosts:
            raise PlatformDueDiligenceError("official source hosts must be explicit")
        for item in self.evidence:
            hostname = (urlparse(item.url).hostname or "").casefold()
            if hostname not in self.official_hosts:
                raise PlatformDueDiligenceError(
                    f"evidence host is not approved for {self.platform_id}: {hostname}"
                )
        if not self.operational_caveats:
            raise PlatformDueDiligenceError("operational caveats must be explicit")
        if not self.required_controls:
            raise PlatformDueDiligenceError("required controls must be explicit")
        if not self.reference_only or not self.approved_order_only:
            raise PlatformDueDiligenceError("current due diligence must remain reference-only")
        if self.credentials_allowed or self.network_runtime_allowed or self.live_execution_allowed:
            raise PlatformDueDiligenceError("due diligence cannot grant runtime authority")

    def to_contract_payload(self) -> dict[str, object]:
        return {
            "schema_version": "0.1.0",
            "platform_id": self.platform_id,
            "role": self.role.value,
            "deployment_model": self.deployment_model.value,
            "authentication_model": self.authentication_model.value,
            "simulation_model": self.simulation_model.value,
            "integration_priority": self.integration_priority.value,
            "official_hosts": sorted(self.official_hosts),
            "evidence": [
                {"claim": item.claim, "url": item.url}
                for item in self.evidence
            ],
            "operational_caveats": list(self.operational_caveats),
            "required_controls": sorted(self.required_controls),
            "reference_only": True,
            "approved_order_only": True,
            "credentials_allowed": False,
            "network_runtime_allowed": False,
            "live_execution_allowed": False,
        }


class ExternalPlatformDueDiligenceCatalog:
    """Official-source catalog that separates product claims from integration decisions."""

    def __init__(
        self,
        registry: ExternalTradingPlatformRegistry,
        records: tuple[PlatformDueDiligenceRecord, ...],
    ) -> None:
        self._records: dict[str, PlatformDueDiligenceRecord] = {}
        for record in records:
            profile = registry.get(record.platform_id)
            expected_boundary = _ROLE_BOUNDARIES[record.role]
            if profile.boundary is not expected_boundary:
                raise PlatformDueDiligenceError(
                    f"{record.platform_id} role {record.role.value} requires "
                    f"{expected_boundary.value}, got {profile.boundary.value}"
                )
            if record.platform_id in self._records:
                raise PlatformDueDiligenceError(f"duplicate due diligence record: {record.platform_id}")
            self._records[record.platform_id] = record

    def get(self, platform_id: str) -> PlatformDueDiligenceRecord:
        try:
            return self._records[platform_id.casefold()]
        except KeyError as exc:
            raise PlatformDueDiligenceError(f"unknown due diligence platform: {platform_id}") from exc

    def list_records(self) -> tuple[PlatformDueDiligenceRecord, ...]:
        return tuple(sorted(self._records.values(), key=lambda record: record.platform_id))

    def by_role(self, role: PlatformRole) -> tuple[PlatformDueDiligenceRecord, ...]:
        return tuple(record for record in self.list_records() if record.role is role)


def build_default_external_platform_due_diligence_catalog(
    registry: ExternalTradingPlatformRegistry,
) -> ExternalPlatformDueDiligenceCatalog:
    common_execution_controls = frozenset(
        {
            "approved_order_only",
            "credential_vault",
            "deterministic_risk_gateway",
            "idempotency",
            "kill_switch",
            "no_withdrawal",
            "rate_limit_policy",
            "reconciliation",
        }
    )
    return ExternalPlatformDueDiligenceCatalog(
        registry,
        (
            PlatformDueDiligenceRecord(
                platform_id="quantconnect-lean",
                role=PlatformRole.RESEARCH_BACKTEST,
                deployment_model=DeploymentModel.LOCAL_ENGINE,
                authentication_model=AuthenticationModel.API_KEY,
                simulation_model=SimulationModel.LOCAL_BACKTEST,
                integration_priority=IntegrationPriority.RESEARCH_REFERENCE,
                official_hosts=frozenset({"www.quantconnect.com"}),
                evidence=(
                    OfficialEvidence(
                        "Brokerage models simulate fees, leverage, settlement and supported order behavior.",
                        "https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/brokerages/key-concepts",
                    ),
                    OfficialEvidence(
                        "LEAN exposes multiple integrated brokerage models and asset-specific constraints.",
                        "https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/brokerages/supported-models",
                    ),
                ),
                operational_caveats=(
                    "Brokerage models reduce mismatch but do not prove live fill equivalence.",
                    "LEAN live routing must remain outside the internal research boundary.",
                ),
                required_controls=frozenset(
                    {
                        "dataset_lineage",
                        "leakage_review",
                        "out_of_sample_validation",
                        "reproducible_backtest",
                    }
                ),
            ),
            PlatformDueDiligenceRecord(
                platform_id="interactive-brokers",
                role=PlatformRole.INSTITUTIONAL_BROKER_API,
                deployment_model=DeploymentModel.LOCAL_GATEWAY,
                authentication_model=AuthenticationModel.BROKER_SESSION,
                simulation_model=SimulationModel.BROKER_PAPER_ACCOUNT,
                integration_priority=IntegrationPriority.DEFERRED_EXECUTION_ADAPTER,
                official_hosts=frozenset({"ibkrcampus.com"}),
                evidence=(
                    OfficialEvidence(
                        "TWS API requires Trader Workstation or IB Gateway and uses a TCP socket protocol.",
                        "https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/",
                    ),
                    OfficialEvidence(
                        "Web API has session, pacing and market-data permission constraints.",
                        "https://ibkrcampus.com/campus/ibkr-api-page/webapi-doc/",
                    ),
                ),
                operational_caveats=(
                    "Gateway lifecycle and single-session behavior require supervision.",
                    "Paper permissions and market-data subscriptions mirror the associated live account.",
                ),
                required_controls=common_execution_controls
                | {"gateway_health", "pacing_budget", "session_recovery"},
            ),
            PlatformDueDiligenceRecord(
                platform_id="alpaca",
                role=PlatformRole.DEVELOPER_BROKER_API,
                deployment_model=DeploymentModel.CLOUD_API,
                authentication_model=AuthenticationModel.API_KEY,
                simulation_model=SimulationModel.VENDOR_SIM_API,
                integration_priority=IntegrationPriority.PAPER_ADAPTER_CANDIDATE,
                official_hosts=frozenset({"docs.alpaca.markets"}),
                evidence=(
                    OfficialEvidence(
                        "Paper trading follows the API workflow but uses simulated fills.",
                        "https://docs.alpaca.markets/us/docs/paper-trading",
                    ),
                    OfficialEvidence(
                        "Trading API covers stocks, options and crypto workflows.",
                        "https://docs.alpaca.markets/us/docs/trading-api",
                    ),
                ),
                operational_caveats=(
                    "Paper does not fully model market impact, queue position or all liquidity effects.",
                    "Paper and live endpoints require hard configuration separation.",
                ),
                required_controls=common_execution_controls
                | {"paper_live_endpoint_separation", "paper_fill_model_review"},
            ),
            PlatformDueDiligenceRecord(
                platform_id="ninjatrader",
                role=PlatformRole.FUTURES_STRATEGY_TERMINAL,
                deployment_model=DeploymentModel.DESKTOP_TERMINAL,
                authentication_model=AuthenticationModel.BROKER_SESSION,
                simulation_model=SimulationModel.TERMINAL_SIMULATION,
                integration_priority=IntegrationPriority.ISOLATED_RUNTIME_REVIEW,
                official_hosts=frozenset({"ninjatrader.com"}),
                evidence=(
                    OfficialEvidence(
                        "NinjaScript supports automated strategies and custom indicators.",
                        "https://ninjatrader.com/support/helpguides/nt8/",
                    ),
                    OfficialEvidence(
                        "ATI processes external trade signals and is not a general brokerage or market-data API.",
                        "https://ninjatrader.com/support/helpguides/nt8/automated_trading_interface_at.htm",
                    ),
                ),
                operational_caveats=(
                    "NinjaScript, ATM and ATI are distinct execution models and cannot share assumptions.",
                    "Terminal strategy state must be reconciled with the internal OMS.",
                ),
                required_controls=common_execution_controls
                | {"ati_semantics_review", "terminal_health", "strategy_state_reconciliation"},
            ),
            PlatformDueDiligenceRecord(
                platform_id="tradestation",
                role=PlatformRole.TRADITIONAL_MULTI_ASSET_API,
                deployment_model=DeploymentModel.CLOUD_API,
                authentication_model=AuthenticationModel.OAUTH2,
                simulation_model=SimulationModel.VENDOR_SIM_API,
                integration_priority=IntegrationPriority.PAPER_ADAPTER_CANDIDATE,
                official_hosts=frozenset({"api.tradestation.com"}),
                evidence=(
                    OfficialEvidence(
                        "The REST API provides brokerage and market-data services for stocks, options and futures.",
                        "https://api.tradestation.com/docs/",
                    ),
                    OfficialEvidence(
                        "SIM uses a distinct base URL and simulated instant fills.",
                        "https://api.tradestation.com/docs/fundamentals/sim-vs-live/",
                    ),
                    OfficialEvidence(
                        "OAuth scopes include market data, account reads and trade authority.",
                        "https://api.tradestation.com/docs/fundamentals/authentication/scopes/",
                    ),
                ),
                operational_caveats=(
                    "SIM instant fills are not evidence of live execution quality.",
                    "Default trade scope and non-expiring refresh-token settings require explicit hardening.",
                ),
                required_controls=common_execution_controls
                | {"oauth_scope_review", "sim_live_url_separation", "token_rotation"},
            ),
            PlatformDueDiligenceRecord(
                platform_id="metatrader-5",
                role=PlatformRole.FOREX_CFD_TERMINAL,
                deployment_model=DeploymentModel.DESKTOP_TERMINAL,
                authentication_model=AuthenticationModel.BROKER_SESSION,
                simulation_model=SimulationModel.TERMINAL_SIMULATION,
                integration_priority=IntegrationPriority.ISOLATED_RUNTIME_REVIEW,
                official_hosts=frozenset({"www.mql5.com"}),
                evidence=(
                    OfficialEvidence(
                        "MQL5 provides strategy, order, indicator and terminal APIs.",
                        "https://www.mql5.com/en/docs",
                    ),
                ),
                operational_caveats=(
                    "Broker-specific symbol, fill and CFD semantics vary materially.",
                    "Expert Advisors are independent execution runtimes and must remain isolated.",
                ),
                required_controls=common_execution_controls
                | {"broker_semantics_review", "expert_advisor_isolation", "terminal_health"},
            ),
            PlatformDueDiligenceRecord(
                platform_id="ctrader",
                role=PlatformRole.FOREX_CFD_TERMINAL,
                deployment_model=DeploymentModel.CLOUD_API,
                authentication_model=AuthenticationModel.OAUTH2,
                simulation_model=SimulationModel.TERMINAL_SIMULATION,
                integration_priority=IntegrationPriority.ISOLATED_RUNTIME_REVIEW,
                official_hosts=frozenset({"help.ctrader.com"}),
                evidence=(
                    OfficialEvidence(
                        "Open API account authentication is OAuth 2.0 based.",
                        "https://help.ctrader.com/open-api/account-authentication/",
                    ),
                    OfficialEvidence(
                        "Open API supports JSON or Protobuf messages for trading integrations.",
                        "https://help.ctrader.com/open-api/",
                    ),
                ),
                operational_caveats=(
                    "Broker-specific account and symbol behavior remains external.",
                    "OAuth tokens must remain inside a future execution adapter boundary.",
                ),
                required_controls=common_execution_controls
                | {"oauth_scope_review", "token_rotation", "venue_capability_detection"},
            ),
            PlatformDueDiligenceRecord(
                platform_id="hummingbot",
                role=PlatformRole.CRYPTO_STRATEGY_RUNTIME,
                deployment_model=DeploymentModel.EXTERNAL_RUNTIME,
                authentication_model=AuthenticationModel.EXCHANGE_API_KEYS,
                simulation_model=SimulationModel.CONNECTOR_PAPER_RUNTIME,
                integration_priority=IntegrationPriority.ISOLATED_RUNTIME_REVIEW,
                official_hosts=frozenset({"hummingbot.org"}),
                evidence=(
                    OfficialEvidence(
                        "Hummingbot is a modular framework for automated crypto strategies and connectors.",
                        "https://hummingbot.org/",
                    ),
                ),
                operational_caveats=(
                    "Strategies can create and refresh orders autonomously.",
                    "Connector behavior and exchange semantics require independent source review.",
                ),
                required_controls=common_execution_controls
                | {"connector_source_review", "process_isolation", "runtime_resource_limits"},
            ),
            PlatformDueDiligenceRecord(
                platform_id="tradingview",
                role=PlatformRole.SIGNAL_SOURCE,
                deployment_model=DeploymentModel.CLOUD_API,
                authentication_model=AuthenticationModel.NONE_FOR_SIGNAL_PAYLOAD,
                simulation_model=SimulationModel.NONE,
                integration_priority=IntegrationPriority.SIGNAL_CONTRACT_ONLY,
                official_hosts=frozenset({"www.tradingview.com"}),
                evidence=(
                    OfficialEvidence(
                        "Webhook alerts send HTTP POST payloads to an external application.",
                        "https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/",
                    ),
                ),
                operational_caveats=(
                    "Webhook delivery is signal transport, not execution authorization.",
                    "Credentials must not appear in webhook URLs or payloads.",
                ),
                required_controls=frozenset(
                    {
                        "payload_allowlist",
                        "replay_protection",
                        "schema_validation",
                        "signal_candidate_mapping",
                        "webhook_authentication",
                    }
                ),
            ),
        ),
    )


_ROLE_BOUNDARIES = {
    PlatformRole.RESEARCH_BACKTEST: IntegrationBoundary.RESEARCH_SANDBOX,
    PlatformRole.INSTITUTIONAL_BROKER_API: IntegrationBoundary.EXECUTION_ENGINE_ONLY,
    PlatformRole.DEVELOPER_BROKER_API: IntegrationBoundary.EXECUTION_ENGINE_ONLY,
    PlatformRole.FUTURES_STRATEGY_TERMINAL: IntegrationBoundary.TERMINAL_ADAPTER_BOUNDARY,
    PlatformRole.TRADITIONAL_MULTI_ASSET_API: IntegrationBoundary.EXECUTION_ENGINE_ONLY,
    PlatformRole.FOREX_CFD_TERMINAL: IntegrationBoundary.TERMINAL_ADAPTER_BOUNDARY,
    PlatformRole.CRYPTO_STRATEGY_RUNTIME: IntegrationBoundary.ISOLATED_STRATEGY_SANDBOX,
    PlatformRole.SIGNAL_SOURCE: IntegrationBoundary.SIGNAL_INTAKE_ONLY,
}
