from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, IntEnum

from packages.domain.base import deterministic_id, require_aware_datetime


class PlatformRegistryError(ValueError):
    """Raised when an external platform integration request is invalid."""


class PlatformCategory(str, Enum):
    RESEARCH_BACKTEST_ENGINE = "research_backtesting_engine"
    EXECUTION_BROKER_API = "execution_broker_api"
    DEVELOPER_BROKER_API = "developer_broker_api"
    FUTURES_TRADING_PLATFORM = "futures_trading_platform"
    TRADITIONAL_TRADING_PLATFORM = "traditional_trading_platform"
    CRYPTO_STRATEGY_RUNTIME = "crypto_strategy_runtime"
    SIGNAL_SOURCE = "signal_source"
    FOREX_CFD_PLATFORM = "forex_cfd_platform"
    COMMERCIAL_BOT_SAAS = "commercial_bot_saas"
    EXCHANGE_NATIVE_BOT = "exchange_native_bot"
    TECHNICAL_ANALYSIS_AUTOMATION = "technical_analysis_automation"


class IntegrationBoundary(str, Enum):
    RESEARCH_SANDBOX = "research_sandbox"
    EXECUTION_ENGINE_ONLY = "execution_engine_only"
    ISOLATED_STRATEGY_SANDBOX = "isolated_strategy_sandbox"
    SIGNAL_INTAKE_ONLY = "signal_intake_only"
    TERMINAL_ADAPTER_BOUNDARY = "terminal_adapter_boundary"
    EXTERNAL_SAAS_REFERENCE = "external_saas_reference"
    EXCHANGE_NATIVE_AUTOMATION = "exchange_native_automation"


class IntegrationStage(IntEnum):
    REFERENCE = 0
    CONTRACT = 1
    FAKE = 2
    PAPER = 3
    CONTROLLED_LIVE = 4


class PlatformCapability(str, Enum):
    RESEARCH = "research"
    BACKTEST = "backtest"
    OPTIMIZATION = "optimization"
    PAPER_TRADING = "paper_trading"
    LIVE_MARKET_DATA = "live_market_data"
    HISTORICAL_MARKET_DATA = "historical_market_data"
    SIGNAL_INGESTION = "signal_ingestion"
    ORDER_EXECUTION = "order_execution"
    ACCOUNT_STATE = "account_state"
    RECONCILIATION = "reconciliation"
    MARKET_MAKING = "market_making"
    ARBITRAGE = "arbitrage"
    MODEL_INFERENCE = "model_inference"
    GRID_TRADING = "grid_trading"
    DCA_TRADING = "dca_trading"
    COPY_TRADING = "copy_trading"
    SMART_TRADING = "smart_trading"
    NO_CODE_RULES = "no_code_rules"
    TRADINGVIEW_BRIDGE = "tradingview_bridge"
    TRAILING_CONTROLS = "trailing_controls"
    DEMO_TRADING = "demo_trading"


class CredentialBoundary(str, Enum):
    NONE = "none"
    EXTERNAL_SAAS = "external_saas"
    EXCHANGE_NATIVE = "exchange_native"
    LOCAL_TERMINAL = "local_terminal"
    EXECUTION_ENGINE = "execution_engine"


class AssetClass(str, Enum):
    CRYPTO = "crypto"
    EQUITY = "equity"
    ETF = "etf"
    OPTION = "option"
    FUTURE = "future"
    FOREX = "forex"
    CFD = "cfd"
    BOND = "bond"
    FUND = "fund"


class AssessmentDecision(str, Enum):
    ALLOWED_FOR_CURRENT_STAGE = "allowed_for_current_stage"
    REQUIRES_GATES = "requires_gates"
    REJECTED_BOUNDARY_MISMATCH = "rejected_boundary_mismatch"
    REJECTED_UNSUPPORTED_CAPABILITY = "rejected_unsupported_capability"


@dataclass(frozen=True)
class ExternalPlatformProfile:
    platform_id: str
    display_name: str
    category: PlatformCategory
    boundary: IntegrationBoundary
    asset_classes: frozenset[AssetClass]
    capabilities: frozenset[PlatformCapability]
    current_stage: IntegrationStage
    requires_network: bool
    requires_credentials: bool
    direct_execution_capable: bool
    external_runtime: bool
    requires_terminal_or_gateway: bool
    credential_boundary: CredentialBoundary
    supports_no_withdrawal_permissions: bool
    supports_ip_allowlisting: bool
    supports_demo_or_paper: bool
    official_documentation: str
    operational_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.platform_id.strip() or not self.display_name.strip():
            raise PlatformRegistryError("platform identifiers must be non-empty")
        if not self.asset_classes:
            raise PlatformRegistryError("platform must declare at least one asset class")
        if not self.capabilities:
            raise PlatformRegistryError("platform must declare at least one capability")
        if self.direct_execution_capable and PlatformCapability.ORDER_EXECUTION not in self.capabilities:
            raise PlatformRegistryError("direct execution platforms must declare order_execution")
        if self.requires_credentials and self.credential_boundary is CredentialBoundary.NONE:
            raise PlatformRegistryError("credential-requiring platforms must declare credential boundary")
        if not self.requires_credentials and self.credential_boundary is not CredentialBoundary.NONE:
            raise PlatformRegistryError("credential-free profile has incompatible credential boundary")
        if (
            PlatformCapability.PAPER_TRADING in self.capabilities
            or PlatformCapability.DEMO_TRADING in self.capabilities
        ) and not self.supports_demo_or_paper:
            raise PlatformRegistryError("paper/demo capability requires declared support")
        if not self.official_documentation.startswith("https://"):
            raise PlatformRegistryError("official documentation must use HTTPS")


@dataclass(frozen=True)
class PlatformIntegrationRequest:
    platform_id: str
    requested_stage: IntegrationStage
    requested_capabilities: frozenset[PlatformCapability]
    target_boundary: IntegrationBoundary
    completed_gates: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.platform_id.strip():
            raise PlatformRegistryError("platform_id must be non-empty")
        if not self.requested_capabilities:
            raise PlatformRegistryError("requested_capabilities must not be empty")
        if any(not gate.strip() for gate in self.completed_gates):
            raise PlatformRegistryError("completed gate names must be non-empty")


@dataclass(frozen=True)
class PlatformIntegrationAssessment:
    platform_id: str
    requested_stage: IntegrationStage
    decision: AssessmentDecision
    required_gates: tuple[str, ...]
    missing_gates: tuple[str, ...]
    unsupported_capabilities: tuple[str, ...]
    reasons: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    risk_gateway_required: bool
    approved_order_required: bool
    execution_engine_only: bool
    credentials_allowed: bool = False
    network_runtime_allowed: bool = False
    live_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.platform_id.strip():
            raise PlatformRegistryError("platform_id must be non-empty")
        if self.credentials_allowed or self.network_runtime_allowed or self.live_execution_allowed:
            raise PlatformRegistryError("assessment cannot grant runtime authority")
        if PlatformCapability.ORDER_EXECUTION.value in self.unsupported_capabilities:
            if self.approved_order_required is False:
                raise PlatformRegistryError("execution assessment must preserve ApprovedOrder boundary")

    def to_contract_payload(
        self,
        *,
        trace_id: str,
        correlation_id: str,
        assessed_at: datetime,
    ) -> dict[str, object]:
        if not trace_id.strip() or not correlation_id.strip():
            raise PlatformRegistryError("trace_id and correlation_id must be non-empty")
        require_aware_datetime(assessed_at, "assessed_at")
        return {
            "schema_version": "0.1.0",
            "trace_id": trace_id,
            "correlation_id": correlation_id,
            "assessment_id": deterministic_id(
                "epca",
                self.platform_id,
                self.requested_stage.name,
                assessed_at.isoformat(),
                correlation_id,
            ),
            "platform_id": self.platform_id,
            "requested_stage": self.requested_stage.name,
            "decision": self.decision.value,
            "required_gates": list(self.required_gates),
            "missing_gates": list(self.missing_gates),
            "reasons": list(self.reasons),
            "allowed_actions": list(self.allowed_actions),
            "risk_gateway_required": self.risk_gateway_required,
            "approved_order_required": self.approved_order_required,
            "execution_engine_only": self.execution_engine_only,
            "credentials_allowed": False,
            "network_runtime_allowed": False,
            "live_execution_allowed": False,
            "assessed_at": assessed_at.isoformat(),
        }


class ExternalTradingPlatformRegistry:
    """Capability registry and deterministic integration-stage planner."""

    def __init__(self, profiles: tuple[ExternalPlatformProfile, ...]) -> None:
        self._profiles: dict[str, ExternalPlatformProfile] = {}
        for profile in profiles:
            normalized = profile.platform_id.casefold()
            if normalized in self._profiles:
                raise PlatformRegistryError(f"duplicate platform profile: {profile.platform_id}")
            self._profiles[normalized] = profile

    def list_profiles(self) -> tuple[ExternalPlatformProfile, ...]:
        return tuple(sorted(self._profiles.values(), key=lambda profile: profile.platform_id))

    def get(self, platform_id: str) -> ExternalPlatformProfile:
        try:
            return self._profiles[platform_id.casefold()]
        except KeyError as exc:
            raise PlatformRegistryError(f"unknown platform: {platform_id}") from exc

    def assess(self, request: PlatformIntegrationRequest) -> PlatformIntegrationAssessment:
        profile = self.get(request.platform_id)
        unsupported = tuple(
            sorted(
                capability.value
                for capability in request.requested_capabilities
                if capability not in profile.capabilities
            )
        )
        boundary_mismatch = request.target_boundary is not profile.boundary
        required_gates = tuple(sorted(_required_gates(profile, request)))
        missing_gates = tuple(sorted(set(required_gates).difference(request.completed_gates)))
        reasons: list[str] = []

        if unsupported:
            decision = AssessmentDecision.REJECTED_UNSUPPORTED_CAPABILITY
            reasons.append(f"unsupported capabilities: {', '.join(unsupported)}")
        elif boundary_mismatch:
            decision = AssessmentDecision.REJECTED_BOUNDARY_MISMATCH
            reasons.append(
                f"requested boundary {request.target_boundary.value} does not match "
                f"required boundary {profile.boundary.value}"
            )
        elif request.requested_stage <= profile.current_stage and not missing_gates:
            decision = AssessmentDecision.ALLOWED_FOR_CURRENT_STAGE
            reasons.append("request fits the currently approved local integration stage")
        else:
            decision = AssessmentDecision.REQUIRES_GATES
            if request.requested_stage > profile.current_stage:
                reasons.append(
                    f"requested stage {request.requested_stage.name} exceeds "
                    f"current stage {profile.current_stage.name}"
                )
            if missing_gates:
                reasons.append(f"missing gates: {', '.join(missing_gates)}")

        execution_requested = PlatformCapability.ORDER_EXECUTION in request.requested_capabilities
        return PlatformIntegrationAssessment(
            platform_id=profile.platform_id,
            requested_stage=request.requested_stage,
            decision=decision,
            required_gates=required_gates,
            missing_gates=missing_gates,
            unsupported_capabilities=unsupported,
            reasons=tuple(reasons),
            allowed_actions=_allowed_actions(profile, request),
            risk_gateway_required=execution_requested,
            approved_order_required=execution_requested,
            execution_engine_only=profile.boundary is IntegrationBoundary.EXECUTION_ENGINE_ONLY,
        )


def build_default_external_trading_platform_registry() -> ExternalTradingPlatformRegistry:
    return ExternalTradingPlatformRegistry(
        (
            ExternalPlatformProfile(
                platform_id="quantconnect-lean",
                display_name="QuantConnect / LEAN",
                category=PlatformCategory.RESEARCH_BACKTEST_ENGINE,
                boundary=IntegrationBoundary.RESEARCH_SANDBOX,
                asset_classes=frozenset(
                    {
                        AssetClass.CRYPTO,
                        AssetClass.EQUITY,
                        AssetClass.ETF,
                        AssetClass.OPTION,
                        AssetClass.FUTURE,
                        AssetClass.FOREX,
                        AssetClass.CFD,
                    }
                ),
                capabilities=frozenset(
                    {
                        PlatformCapability.RESEARCH,
                        PlatformCapability.BACKTEST,
                        PlatformCapability.OPTIMIZATION,
                        PlatformCapability.PAPER_TRADING,
                        PlatformCapability.HISTORICAL_MARKET_DATA,
                        PlatformCapability.LIVE_MARKET_DATA,
                        PlatformCapability.ORDER_EXECUTION,
                    }
                ),
                current_stage=IntegrationStage.CONTRACT,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=True,
                requires_terminal_or_gateway=False,
                credential_boundary=CredentialBoundary.EXTERNAL_SAAS,
                supports_no_withdrawal_permissions=False,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://www.quantconnect.com/docs/v2/",
                operational_notes=(
                    "Use as a research/backtest reference before any runtime integration.",
                    "Live brokerage routing must not bypass the internal execution engine.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="interactive-brokers",
                display_name="Interactive Brokers API",
                category=PlatformCategory.EXECUTION_BROKER_API,
                boundary=IntegrationBoundary.EXECUTION_ENGINE_ONLY,
                asset_classes=frozenset(
                    {
                        AssetClass.EQUITY,
                        AssetClass.ETF,
                        AssetClass.OPTION,
                        AssetClass.FUTURE,
                        AssetClass.FOREX,
                        AssetClass.BOND,
                        AssetClass.FUND,
                    }
                ),
                capabilities=frozenset(
                    {
                        PlatformCapability.LIVE_MARKET_DATA,
                        PlatformCapability.HISTORICAL_MARKET_DATA,
                        PlatformCapability.ORDER_EXECUTION,
                        PlatformCapability.ACCOUNT_STATE,
                        PlatformCapability.RECONCILIATION,
                    }
                ),
                current_stage=IntegrationStage.CONTRACT,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=False,
                requires_terminal_or_gateway=True,
                credential_boundary=CredentialBoundary.EXECUTION_ENGINE,
                supports_no_withdrawal_permissions=True,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/",
                operational_notes=(
                    "TWS API requires a running TWS or IB Gateway instance.",
                    "Only execution-engine may own future connectivity.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="alpaca",
                display_name="Alpaca Trading API",
                category=PlatformCategory.DEVELOPER_BROKER_API,
                boundary=IntegrationBoundary.EXECUTION_ENGINE_ONLY,
                asset_classes=frozenset(
                    {
                        AssetClass.CRYPTO,
                        AssetClass.EQUITY,
                        AssetClass.ETF,
                        AssetClass.OPTION,
                    }
                ),
                capabilities=frozenset(
                    {
                        PlatformCapability.PAPER_TRADING,
                        PlatformCapability.LIVE_MARKET_DATA,
                        PlatformCapability.HISTORICAL_MARKET_DATA,
                        PlatformCapability.ORDER_EXECUTION,
                        PlatformCapability.ACCOUNT_STATE,
                        PlatformCapability.RECONCILIATION,
                    }
                ),
                current_stage=IntegrationStage.REFERENCE,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=False,
                requires_terminal_or_gateway=False,
                credential_boundary=CredentialBoundary.EXECUTION_ENGINE,
                supports_no_withdrawal_permissions=True,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://docs.alpaca.markets/us/docs/trading-api",
                operational_notes=(
                    "Paper uses the API workflow but simulated fills do not reproduce every live constraint.",
                    "A future adapter must keep paper and live endpoints in separate configuration domains.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="ninjatrader",
                display_name="NinjaTrader",
                category=PlatformCategory.FUTURES_TRADING_PLATFORM,
                boundary=IntegrationBoundary.TERMINAL_ADAPTER_BOUNDARY,
                asset_classes=frozenset({AssetClass.FUTURE, AssetClass.OPTION}),
                capabilities=frozenset(
                    {
                        PlatformCapability.BACKTEST,
                        PlatformCapability.OPTIMIZATION,
                        PlatformCapability.PAPER_TRADING,
                        PlatformCapability.LIVE_MARKET_DATA,
                        PlatformCapability.HISTORICAL_MARKET_DATA,
                        PlatformCapability.ORDER_EXECUTION,
                        PlatformCapability.ACCOUNT_STATE,
                    }
                ),
                current_stage=IntegrationStage.REFERENCE,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=True,
                requires_terminal_or_gateway=True,
                credential_boundary=CredentialBoundary.LOCAL_TERMINAL,
                supports_no_withdrawal_permissions=False,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://ninjatrader.com/support/helpguides/nt8/",
                operational_notes=(
                    "NinjaScript strategies, ATM strategies and ATI have distinct semantics.",
                    "ATI is signal processing, not a general brokerage or market-data API.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="tradestation",
                display_name="TradeStation API",
                category=PlatformCategory.TRADITIONAL_TRADING_PLATFORM,
                boundary=IntegrationBoundary.EXECUTION_ENGINE_ONLY,
                asset_classes=frozenset(
                    {
                        AssetClass.EQUITY,
                        AssetClass.ETF,
                        AssetClass.OPTION,
                        AssetClass.FUTURE,
                    }
                ),
                capabilities=frozenset(
                    {
                        PlatformCapability.PAPER_TRADING,
                        PlatformCapability.LIVE_MARKET_DATA,
                        PlatformCapability.HISTORICAL_MARKET_DATA,
                        PlatformCapability.ORDER_EXECUTION,
                        PlatformCapability.ACCOUNT_STATE,
                        PlatformCapability.RECONCILIATION,
                    }
                ),
                current_stage=IntegrationStage.REFERENCE,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=False,
                requires_terminal_or_gateway=False,
                credential_boundary=CredentialBoundary.EXECUTION_ENGINE,
                supports_no_withdrawal_permissions=True,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://api.tradestation.com/docs/",
                operational_notes=(
                    "SIM and LIVE use distinct base URLs and must be impossible to confuse at runtime.",
                    "OAuth scopes include trade authority and require least-privilege review.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="hummingbot",
                display_name="Hummingbot",
                category=PlatformCategory.CRYPTO_STRATEGY_RUNTIME,
                boundary=IntegrationBoundary.ISOLATED_STRATEGY_SANDBOX,
                asset_classes=frozenset({AssetClass.CRYPTO}),
                capabilities=frozenset(
                    {
                        PlatformCapability.PAPER_TRADING,
                        PlatformCapability.LIVE_MARKET_DATA,
                        PlatformCapability.ORDER_EXECUTION,
                        PlatformCapability.MARKET_MAKING,
                        PlatformCapability.ARBITRAGE,
                        PlatformCapability.ACCOUNT_STATE,
                    }
                ),
                current_stage=IntegrationStage.REFERENCE,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=True,
                requires_terminal_or_gateway=False,
                credential_boundary=CredentialBoundary.LOCAL_TERMINAL,
                supports_no_withdrawal_permissions=True,
                supports_ip_allowlisting=True,
                supports_demo_or_paper=True,
                official_documentation="https://hummingbot.org/",
                operational_notes=(
                    "Strategies create and refresh orders and therefore require process isolation.",
                    "Use strategy logic as reference; never expose exchange credentials to agents.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="tradingview",
                display_name="TradingView Alerts",
                category=PlatformCategory.SIGNAL_SOURCE,
                boundary=IntegrationBoundary.SIGNAL_INTAKE_ONLY,
                asset_classes=frozenset(
                    {
                        AssetClass.CRYPTO,
                        AssetClass.EQUITY,
                        AssetClass.ETF,
                        AssetClass.FUTURE,
                        AssetClass.FOREX,
                        AssetClass.CFD,
                    }
                ),
                capabilities=frozenset({PlatformCapability.SIGNAL_INGESTION}),
                current_stage=IntegrationStage.CONTRACT,
                requires_network=True,
                requires_credentials=False,
                direct_execution_capable=False,
                external_runtime=False,
                requires_terminal_or_gateway=False,
                credential_boundary=CredentialBoundary.NONE,
                supports_no_withdrawal_permissions=False,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=False,
                official_documentation="https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/",
                operational_notes=(
                    "Alerts become SignalCandidate only.",
                    "Credentials must never appear in webhook URL or payload.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="metatrader-5",
                display_name="MetaTrader 5",
                category=PlatformCategory.FOREX_CFD_PLATFORM,
                boundary=IntegrationBoundary.TERMINAL_ADAPTER_BOUNDARY,
                asset_classes=frozenset(
                    {
                        AssetClass.FOREX,
                        AssetClass.CFD,
                        AssetClass.FUTURE,
                        AssetClass.EQUITY,
                    }
                ),
                capabilities=frozenset(
                    {
                        PlatformCapability.BACKTEST,
                        PlatformCapability.OPTIMIZATION,
                        PlatformCapability.LIVE_MARKET_DATA,
                        PlatformCapability.HISTORICAL_MARKET_DATA,
                        PlatformCapability.ORDER_EXECUTION,
                        PlatformCapability.MODEL_INFERENCE,
                    }
                ),
                current_stage=IntegrationStage.REFERENCE,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=True,
                requires_terminal_or_gateway=True,
                credential_boundary=CredentialBoundary.LOCAL_TERMINAL,
                supports_no_withdrawal_permissions=True,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://www.mql5.com/en/docs",
                operational_notes=(
                    "Expert Advisors and ONNX models execute inside the terminal boundary.",
                    "Future integration must translate ApprovedOrder through an execution adapter.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="ctrader",
                display_name="cTrader Open API / Algo",
                category=PlatformCategory.FOREX_CFD_PLATFORM,
                boundary=IntegrationBoundary.TERMINAL_ADAPTER_BOUNDARY,
                asset_classes=frozenset(
                    {
                        AssetClass.FOREX,
                        AssetClass.CFD,
                        AssetClass.EQUITY,
                        AssetClass.FUTURE,
                    }
                ),
                capabilities=frozenset(
                    {
                        PlatformCapability.BACKTEST,
                        PlatformCapability.OPTIMIZATION,
                        PlatformCapability.PAPER_TRADING,
                        PlatformCapability.LIVE_MARKET_DATA,
                        PlatformCapability.HISTORICAL_MARKET_DATA,
                        PlatformCapability.ORDER_EXECUTION,
                        PlatformCapability.ACCOUNT_STATE,
                    }
                ),
                current_stage=IntegrationStage.REFERENCE,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=True,
                requires_terminal_or_gateway=False,
                credential_boundary=CredentialBoundary.LOCAL_TERMINAL,
                supports_no_withdrawal_permissions=True,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://help.ctrader.com/open-api/",
                operational_notes=(
                    "Open API uses OAuth 2.0 and supports JSON or Protobuf messages.",
                    "cBots support Python/C# and platform backtesting.",
                ),
            ),
            _commercial_crypto_profile(
                platform_id="3commas",
                display_name="3Commas",
                capabilities={
                    PlatformCapability.GRID_TRADING,
                    PlatformCapability.DCA_TRADING,
                    PlatformCapability.SMART_TRADING,
                    PlatformCapability.COPY_TRADING,
                    PlatformCapability.BACKTEST,
                    PlatformCapability.ORDER_EXECUTION,
                    PlatformCapability.ACCOUNT_STATE,
                    PlatformCapability.TRAILING_CONTROLS,
                },
                supports_ip_allowlisting=True,
                supports_demo_or_paper=True,
                official_documentation="https://help.3commas.io/en/articles/4430555-all-about-3commas-features-tools-history-and-benefits",
                notes=(
                    "Grid and DCA automation can create many exchange orders and hit rate limits.",
                    "Treat all strategy templates and AI-labelled settings as untrusted configuration.",
                ),
            ),
            _commercial_crypto_profile(
                platform_id="cryptohopper",
                display_name="Cryptohopper",
                capabilities={
                    PlatformCapability.DCA_TRADING,
                    PlatformCapability.COPY_TRADING,
                    PlatformCapability.MARKET_MAKING,
                    PlatformCapability.ARBITRAGE,
                    PlatformCapability.PAPER_TRADING,
                    PlatformCapability.ORDER_EXECUTION,
                    PlatformCapability.ACCOUNT_STATE,
                    PlatformCapability.TRADINGVIEW_BRIDGE,
                },
                supports_ip_allowlisting=True,
                supports_demo_or_paper=True,
                official_documentation="https://docs.cryptohopper.com/docs/how-to-connect",
                notes=(
                    "Marketplace strategies, copy bots and signals require provenance review.",
                    "Exchange keys must exclude withdrawal and transfer permissions.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="pionex",
                display_name="Pionex",
                category=PlatformCategory.EXCHANGE_NATIVE_BOT,
                boundary=IntegrationBoundary.EXCHANGE_NATIVE_AUTOMATION,
                asset_classes=frozenset({AssetClass.CRYPTO}),
                capabilities=frozenset(
                    {
                        PlatformCapability.GRID_TRADING,
                        PlatformCapability.DCA_TRADING,
                        PlatformCapability.ORDER_EXECUTION,
                        PlatformCapability.ACCOUNT_STATE,
                        PlatformCapability.TRAILING_CONTROLS,
                    }
                ),
                current_stage=IntegrationStage.REFERENCE,
                requires_network=True,
                requires_credentials=True,
                direct_execution_capable=True,
                external_runtime=True,
                requires_terminal_or_gateway=False,
                credential_boundary=CredentialBoundary.EXCHANGE_NATIVE,
                supports_no_withdrawal_permissions=False,
                supports_ip_allowlisting=False,
                supports_demo_or_paper=False,
                official_documentation="https://www.pionex.com/blog/category/trading-bots/",
                operational_notes=(
                    "Bots execute inside an exchange-native environment.",
                    "Use only as strategy/UX reference until an exchange-specific approval exists.",
                ),
            ),
            _commercial_crypto_profile(
                platform_id="coinrule",
                display_name="Coinrule",
                capabilities={
                    PlatformCapability.NO_CODE_RULES,
                    PlatformCapability.ORDER_EXECUTION,
                    PlatformCapability.ACCOUNT_STATE,
                    PlatformCapability.TRADINGVIEW_BRIDGE,
                },
                supports_ip_allowlisting=True,
                supports_demo_or_paper=True,
                official_documentation="https://help.coinrule.com/articles/711711-what-is-coinrule",
                notes=(
                    "Rule templates are external execution policies and require deterministic translation review.",
                    "API keys are documented as trade-only and without withdrawal rights.",
                ),
            ),
            _commercial_crypto_profile(
                platform_id="bitsgap",
                display_name="Bitsgap",
                capabilities={
                    PlatformCapability.GRID_TRADING,
                    PlatformCapability.DCA_TRADING,
                    PlatformCapability.BACKTEST,
                    PlatformCapability.DEMO_TRADING,
                    PlatformCapability.ORDER_EXECUTION,
                    PlatformCapability.ACCOUNT_STATE,
                    PlatformCapability.TRAILING_CONTROLS,
                },
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://bitsgap.com/crypto-trading-bot/dca-bot",
                notes=(
                    "Grid, DCA and leveraged futures variants have materially different risk profiles.",
                    "Demo results must not be treated as live execution evidence.",
                ),
            ),
            _commercial_crypto_profile(
                platform_id="tradesanta",
                display_name="TradeSanta",
                capabilities={
                    PlatformCapability.GRID_TRADING,
                    PlatformCapability.DCA_TRADING,
                    PlatformCapability.SMART_TRADING,
                    PlatformCapability.TRADINGVIEW_BRIDGE,
                    PlatformCapability.ORDER_EXECUTION,
                    PlatformCapability.ACCOUNT_STATE,
                    PlatformCapability.TRAILING_CONTROLS,
                },
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://tradesanta.com/setting-up-bots",
                notes=(
                    "Grid/DCA strategies and TradingView signals become external order flows.",
                    "Safety orders and futures access require explicit capital and leverage limits.",
                ),
            ),
            _commercial_crypto_profile(
                platform_id="wundertrading",
                display_name="WunderTrading",
                capabilities={
                    PlatformCapability.GRID_TRADING,
                    PlatformCapability.DCA_TRADING,
                    PlatformCapability.COPY_TRADING,
                    PlatformCapability.TRADINGVIEW_BRIDGE,
                    PlatformCapability.ARBITRAGE,
                    PlatformCapability.DEMO_TRADING,
                    PlatformCapability.ORDER_EXECUTION,
                    PlatformCapability.ACCOUNT_STATE,
                    PlatformCapability.TRAILING_CONTROLS,
                },
                supports_ip_allowlisting=False,
                supports_demo_or_paper=True,
                official_documentation="https://wundertrading.com/en",
                notes=(
                    "TradingView bridges and copy trading require source authentication and provenance.",
                    "MCP or AI integrations must never receive exchange credentials.",
                ),
            ),
            ExternalPlatformProfile(
                platform_id="trendspider",
                display_name="TrendSpider",
                category=PlatformCategory.TECHNICAL_ANALYSIS_AUTOMATION,
                boundary=IntegrationBoundary.SIGNAL_INTAKE_ONLY,
                asset_classes=frozenset(
                    {
                        AssetClass.CRYPTO,
                        AssetClass.EQUITY,
                        AssetClass.ETF,
                        AssetClass.FUTURE,
                        AssetClass.FOREX,
                        AssetClass.CFD,
                    }
                ),
                capabilities=frozenset(
                    {
                        PlatformCapability.RESEARCH,
                        PlatformCapability.BACKTEST,
                        PlatformCapability.NO_CODE_RULES,
                        PlatformCapability.SIGNAL_INGESTION,
                        PlatformCapability.TRADINGVIEW_BRIDGE,
                    }
                ),
                current_stage=IntegrationStage.CONTRACT,
                requires_network=True,
                requires_credentials=False,
                direct_execution_capable=False,
                external_runtime=False,
                requires_terminal_or_gateway=False,
                credential_boundary=CredentialBoundary.NONE,
                supports_no_withdrawal_permissions=False,
                supports_ip_allowlisting=True,
                supports_demo_or_paper=False,
                official_documentation="https://help.trendspider.com/kb/alerts/webhooks",
                operational_notes=(
                    "Strategy bot webhooks are signal intake only in this platform.",
                    "Third-party bridges that convert webhooks into orders are explicitly outside the trust boundary.",
                ),
            ),
        )
    )


def _required_gates(
    profile: ExternalPlatformProfile,
    request: PlatformIntegrationRequest,
) -> set[str]:
    gates = {"license_review", "security_review", "architecture_boundary_review"}
    if request.requested_stage >= IntegrationStage.CONTRACT:
        gates.update({"contract_defined", "owner_assigned"})
    if request.requested_stage >= IntegrationStage.FAKE:
        gates.update({"fake_adapter_tests", "failure_mode_tests", "audit_event_mapping"})
    if request.requested_stage >= IntegrationStage.PAPER:
        gates.update(
            {
                "paper_evidence",
                "deterministic_risk_gateway",
                "kill_switch",
                "reconciliation",
                "operations_runbook",
            }
        )
    if request.requested_stage >= IntegrationStage.CONTROLLED_LIVE:
        gates.update(
            {
                "credential_vault",
                "network_approval",
                "human_approval",
                "rollback_plan",
                "incident_runbook",
                "no_withdrawal_permissions",
            }
        )
    capabilities = request.requested_capabilities
    if PlatformCapability.SIGNAL_INGESTION in capabilities:
        gates.update({"webhook_authentication", "schema_validation", "replay_protection", "rate_limit_policy"})
    if PlatformCapability.LIVE_MARKET_DATA in capabilities:
        gates.update({"read_only_adapter", "stale_data_guard", "reconnect_policy", "rate_limit_policy"})
    if PlatformCapability.ORDER_EXECUTION in capabilities:
        gates.update(
            {
                "execution_engine_boundary",
                "approved_order_only",
                "idempotency",
                "order_state_machine",
                "execution_report",
            }
        )
    if profile.external_runtime:
        gates.update({"process_isolation", "resource_limits", "runtime_kill_switch"})
    if profile.requires_terminal_or_gateway:
        gates.update({"terminal_gateway_health", "session_recovery"})
    if profile.category in {
        PlatformCategory.COMMERCIAL_BOT_SAAS,
        PlatformCategory.EXCHANGE_NATIVE_BOT,
    }:
        gates.update(
            {
                "vendor_due_diligence",
                "vendor_incident_response",
                "vendor_data_retention_review",
                "capital_subaccount_isolation",
                "bot_stop_procedure",
                "strategy_parameter_limits",
            }
        )
    if profile.requires_credentials:
        gates.update({"credential_scope_review", "key_rotation"})
    if profile.supports_no_withdrawal_permissions:
        gates.add("withdrawal_permission_forbidden")
    if profile.credential_boundary is CredentialBoundary.EXTERNAL_SAAS:
        gates.add("trade_only_api_key")
    if profile.supports_ip_allowlisting:
        gates.add("ip_allowlist")
    if PlatformCapability.COPY_TRADING in capabilities:
        gates.update({"copy_source_provenance", "copy_risk_limits", "copy_latency_review"})
    if PlatformCapability.GRID_TRADING in capabilities:
        gates.update({"grid_range_guard", "max_active_orders", "range_breakout_policy"})
    if PlatformCapability.DCA_TRADING in capabilities:
        gates.update({"max_safety_orders", "max_position_notional", "dca_drawdown_policy"})
    if PlatformCapability.NO_CODE_RULES in capabilities:
        gates.update({"rule_translation_review", "rule_conflict_detection"})
    if PlatformCapability.TRADINGVIEW_BRIDGE in capabilities:
        gates.update({"webhook_authentication", "replay_protection", "payload_allowlist"})
    if PlatformCapability.TRAILING_CONTROLS in capabilities:
        gates.add("trailing_order_semantics_review")
    return gates


def _allowed_actions(
    profile: ExternalPlatformProfile,
    request: PlatformIntegrationRequest,
) -> tuple[str, ...]:
    actions = {
        "reference_review",
        "contract_design",
        "local_fixture_tests",
        "failure_mode_design",
    }
    if request.requested_stage >= IntegrationStage.FAKE:
        actions.update({"fake_adapter", "mocked_integration_tests"})
    if request.requested_stage >= IntegrationStage.PAPER:
        actions.update({"local_paper_simulation", "reconciliation_replay"})
    if profile.category is PlatformCategory.RESEARCH_BACKTEST_ENGINE:
        actions.add("backtest_semantics_review")
    if profile.category is PlatformCategory.SIGNAL_SOURCE:
        actions.add("signal_candidate_mapping")
    if profile.category is PlatformCategory.CRYPTO_STRATEGY_RUNTIME:
        actions.add("strategy_logic_reference")
    if profile.category in {
        PlatformCategory.COMMERCIAL_BOT_SAAS,
        PlatformCategory.EXCHANGE_NATIVE_BOT,
    }:
        actions.update({"ux_workflow_review", "strategy_semantics_review", "security_posture_review"})
    if profile.category is PlatformCategory.TECHNICAL_ANALYSIS_AUTOMATION:
        actions.update({"alert_semantics_review", "strategy_tester_comparison"})
    return tuple(sorted(actions))


def _commercial_crypto_profile(
    *,
    platform_id: str,
    display_name: str,
    capabilities: set[PlatformCapability],
    supports_ip_allowlisting: bool,
    supports_demo_or_paper: bool,
    official_documentation: str,
    notes: tuple[str, ...],
) -> ExternalPlatformProfile:
    return ExternalPlatformProfile(
        platform_id=platform_id,
        display_name=display_name,
        category=PlatformCategory.COMMERCIAL_BOT_SAAS,
        boundary=IntegrationBoundary.EXTERNAL_SAAS_REFERENCE,
        asset_classes=frozenset({AssetClass.CRYPTO}),
        capabilities=frozenset(capabilities),
        current_stage=IntegrationStage.REFERENCE,
        requires_network=True,
        requires_credentials=True,
        direct_execution_capable=True,
        external_runtime=True,
        requires_terminal_or_gateway=False,
        credential_boundary=CredentialBoundary.EXTERNAL_SAAS,
        supports_no_withdrawal_permissions=True,
        supports_ip_allowlisting=supports_ip_allowlisting,
        supports_demo_or_paper=supports_demo_or_paper,
        official_documentation=official_documentation,
        operational_notes=notes,
    )
