from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, IntEnum

from packages.domain.base import deterministic_id, require_aware_datetime


class TradingStackGovernanceError(ValueError):
    """Raised when a professional trading stack request is invalid."""


class StackLayer(str, Enum):
    RESEARCH_AI = "research_ai"
    DATA_INTELLIGENCE = "data_intelligence"
    STRATEGY = "strategy"
    EXECUTION = "execution"
    RISK = "risk"
    SECURITY_OPERATIONS = "security_operations"


class StackStage(IntEnum):
    DESIGN = 0
    CONTRACT = 1
    FAKE = 2
    PAPER = 3
    CONTROLLED_LIVE = 4


class StackCapability(str, Enum):
    REPRODUCIBLE_RESEARCH = "reproducible_research"
    MODEL_VERSIONING = "model_versioning"
    WALK_FORWARD_VALIDATION = "walk_forward_validation"
    OUT_OF_SAMPLE_VALIDATION = "out_of_sample_validation"
    MONTE_CARLO_PERTURBATION = "monte_carlo_perturbation"
    DATA_VALIDATION = "data_validation"
    POINT_IN_TIME_LINEAGE = "point_in_time_lineage"
    STALENESS_DETECTION = "staleness_detection"
    ORDER_BOOK_DATA = "order_book_data"
    FUNDING_OPEN_INTEREST = "funding_open_interest"
    ALTERNATIVE_DATA_GOVERNANCE = "alternative_data_governance"
    STRATEGY_VERSIONING = "strategy_versioning"
    SIGNAL_ONLY_OUTPUT = "signal_only_output"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    STATISTICAL_ARBITRAGE = "statistical_arbitrage"
    MARKET_MAKING = "market_making"
    SENTIMENT = "sentiment"
    VOLATILITY_TARGETING = "volatility_targeting"
    APPROVED_ORDER_ONLY = "approved_order_only"
    IDEMPOTENT_ORDER_IDS = "idempotent_order_ids"
    PARTIAL_FILL_HANDLING = "partial_fill_handling"
    RECONCILIATION = "reconciliation"
    RETRY_BUDGET = "retry_budget"
    RATE_LIMIT_CONTROL = "rate_limit_control"
    KILL_SWITCH = "kill_switch"
    MAX_DRAWDOWN = "max_drawdown"
    MAX_LEVERAGE = "max_leverage"
    MAX_POSITION = "max_position"
    DAILY_LOSS_LIMIT = "daily_loss_limit"
    CIRCUIT_BREAKER = "circuit_breaker"
    VAR_EXPECTED_SHORTFALL = "var_expected_shortfall"
    EXPOSURE_CAP = "exposure_cap"
    TRADE_ONLY_CREDENTIALS = "trade_only_credentials"
    NO_WITHDRAWAL = "no_withdrawal"
    IP_ALLOWLIST = "ip_allowlist"
    SECRETS_MANAGER = "secrets_manager"
    IMMUTABLE_AUDIT = "immutable_audit"
    ALERTING = "alerting"
    RUNTIME_ISOLATION = "runtime_isolation"
    BACKUP_RECOVERY = "backup_recovery"
    CODE_REVIEW = "code_review"


class StackArtifact(str, Enum):
    NORMALIZED_MARKET_EVENT = "NormalizedMarketEvent"
    FEATURE_VECTOR = "FeatureVector"
    FORECAST = "Forecast"
    SIGNAL_CANDIDATE = "SignalCandidate"
    ORDER_INTENT = "OrderIntent"
    RISK_DECISION = "RiskDecision"
    APPROVED_ORDER = "ApprovedOrder"
    EXECUTION_REPORT = "ExecutionReport"
    AUDIT_EVENT = "AuditEvent"


class StackDecision(str, Enum):
    ALLOWED_FOR_LOCAL_STAGE = "allowed_for_local_stage"
    REQUIRES_GATES = "requires_gates"
    REJECTED_INCOMPLETE_STACK = "rejected_incomplete_stack"
    REJECTED_FORBIDDEN_PATH = "rejected_forbidden_path"


@dataclass(frozen=True)
class LayerCapabilitySelection:
    layer: StackLayer
    capabilities: frozenset[StackCapability]

    def __post_init__(self) -> None:
        if not self.capabilities:
            raise TradingStackGovernanceError(f"{self.layer.value} capabilities must not be empty")


@dataclass(frozen=True)
class StackConnection:
    source: StackLayer
    target: StackLayer
    artifact: StackArtifact

    def label(self) -> str:
        return f"{self.source.value}->{self.target.value}:{self.artifact.value}"


@dataclass(frozen=True)
class ProfessionalTradingStackRequest:
    requested_stage: StackStage
    selections: tuple[LayerCapabilitySelection, ...]
    connections: tuple[StackConnection, ...]
    completed_gates: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        layers = [selection.layer for selection in self.selections]
        if len(layers) != len(set(layers)):
            raise TradingStackGovernanceError("each stack layer may be selected only once")
        if any(not gate.strip() for gate in self.completed_gates):
            raise TradingStackGovernanceError("completed gate names must be non-empty")


@dataclass(frozen=True)
class ProfessionalTradingStackAssessment:
    requested_stage: StackStage
    decision: StackDecision
    missing_layers: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    missing_connections: tuple[str, ...]
    invalid_connections: tuple[str, ...]
    required_gates: tuple[str, ...]
    missing_gates: tuple[str, ...]
    reasons: tuple[str, ...]
    canonical_flow_enforced: bool = True
    deterministic_risk_gateway_required: bool = True
    approved_order_only: bool = True
    no_withdrawal_enforced: bool = True
    credentials_allowed: bool = False
    network_runtime_allowed: bool = False
    live_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not all(
            (
                self.canonical_flow_enforced,
                self.deterministic_risk_gateway_required,
                self.approved_order_only,
                self.no_withdrawal_enforced,
            )
        ):
            raise TradingStackGovernanceError("mandatory safety invariants cannot be disabled")
        if self.credentials_allowed or self.network_runtime_allowed or self.live_execution_allowed:
            raise TradingStackGovernanceError("stack assessment cannot grant runtime authority")

    def to_contract_payload(
        self,
        *,
        trace_id: str,
        correlation_id: str,
        assessed_at: datetime,
    ) -> dict[str, object]:
        if not trace_id.strip() or not correlation_id.strip():
            raise TradingStackGovernanceError("trace_id and correlation_id must be non-empty")
        require_aware_datetime(assessed_at, "assessed_at")
        return {
            "schema_version": "0.1.0",
            "trace_id": trace_id,
            "correlation_id": correlation_id,
            "assessment_id": deterministic_id(
                "ptsa",
                self.requested_stage.name,
                correlation_id,
                assessed_at.isoformat(),
            ),
            "requested_stage": self.requested_stage.name,
            "decision": self.decision.value,
            "missing_layers": list(self.missing_layers),
            "missing_capabilities": list(self.missing_capabilities),
            "missing_connections": list(self.missing_connections),
            "invalid_connections": list(self.invalid_connections),
            "required_gates": list(self.required_gates),
            "missing_gates": list(self.missing_gates),
            "reasons": list(self.reasons),
            "canonical_flow_enforced": True,
            "deterministic_risk_gateway_required": True,
            "approved_order_only": True,
            "no_withdrawal_enforced": True,
            "credentials_allowed": False,
            "network_runtime_allowed": False,
            "live_execution_allowed": False,
            "assessed_at": assessed_at.isoformat(),
        }


class ProfessionalTradingStackGovernance:
    """Deterministic composition and promotion policy for the six-layer stack."""

    current_stage = StackStage.CONTRACT

    def assess(self, request: ProfessionalTradingStackRequest) -> ProfessionalTradingStackAssessment:
        selected = {selection.layer: selection.capabilities for selection in request.selections}
        missing_layers = tuple(sorted(layer.value for layer in StackLayer if layer not in selected))
        missing_capabilities = _missing_capabilities(selected, request.requested_stage)
        connection_set = set(request.connections)
        missing_connections = tuple(
            sorted(connection.label() for connection in _REQUIRED_CONNECTIONS if connection not in connection_set)
        )
        invalid_connections = tuple(
            sorted(
                connection.label()
                for connection in request.connections
                if not _connection_is_allowed(connection)
            )
        )
        required_gates = tuple(sorted(_required_gates(request.requested_stage)))
        missing_gates = tuple(sorted(set(required_gates).difference(request.completed_gates)))
        reasons: list[str] = []

        if invalid_connections:
            decision = StackDecision.REJECTED_FORBIDDEN_PATH
            reasons.append("one or more connections bypass the canonical contract flow")
        elif missing_layers or missing_capabilities or missing_connections:
            decision = StackDecision.REJECTED_INCOMPLETE_STACK
            if missing_layers:
                reasons.append(f"missing layers: {', '.join(missing_layers)}")
            if missing_capabilities:
                reasons.append(f"missing capabilities: {', '.join(missing_capabilities)}")
            if missing_connections:
                reasons.append(f"missing connections: {', '.join(missing_connections)}")
        elif request.requested_stage > self.current_stage or missing_gates:
            decision = StackDecision.REQUIRES_GATES
            if request.requested_stage > self.current_stage:
                reasons.append("requested runtime stage requires a separate approval PR")
            if missing_gates:
                reasons.append(f"missing gates: {', '.join(missing_gates)}")
        else:
            decision = StackDecision.ALLOWED_FOR_LOCAL_STAGE
            reasons.append("complete contract-stage architecture with no runtime authority")

        return ProfessionalTradingStackAssessment(
            requested_stage=request.requested_stage,
            decision=decision,
            missing_layers=missing_layers,
            missing_capabilities=missing_capabilities,
            missing_connections=missing_connections,
            invalid_connections=invalid_connections,
            required_gates=required_gates,
            missing_gates=missing_gates,
            reasons=tuple(reasons),
        )


def build_recommended_professional_stack_request(
    requested_stage: StackStage,
    *,
    completed_gates: frozenset[str] = frozenset(),
) -> ProfessionalTradingStackRequest:
    return ProfessionalTradingStackRequest(
        requested_stage=requested_stage,
        selections=tuple(
            LayerCapabilitySelection(layer=layer, capabilities=capabilities)
            for layer, capabilities in _recommended_capabilities().items()
        ),
        connections=_REQUIRED_CONNECTIONS,
        completed_gates=completed_gates,
    )


def build_default_professional_trading_stack_governance() -> ProfessionalTradingStackGovernance:
    return ProfessionalTradingStackGovernance()


def _recommended_capabilities() -> dict[StackLayer, frozenset[StackCapability]]:
    return {
        StackLayer.RESEARCH_AI: frozenset(
            {
                StackCapability.REPRODUCIBLE_RESEARCH,
                StackCapability.MODEL_VERSIONING,
                StackCapability.WALK_FORWARD_VALIDATION,
                StackCapability.OUT_OF_SAMPLE_VALIDATION,
                StackCapability.MONTE_CARLO_PERTURBATION,
            }
        ),
        StackLayer.DATA_INTELLIGENCE: frozenset(
            {
                StackCapability.DATA_VALIDATION,
                StackCapability.POINT_IN_TIME_LINEAGE,
                StackCapability.STALENESS_DETECTION,
                StackCapability.ORDER_BOOK_DATA,
                StackCapability.FUNDING_OPEN_INTEREST,
                StackCapability.ALTERNATIVE_DATA_GOVERNANCE,
            }
        ),
        StackLayer.STRATEGY: frozenset(
            {
                StackCapability.STRATEGY_VERSIONING,
                StackCapability.SIGNAL_ONLY_OUTPUT,
                StackCapability.TREND_FOLLOWING,
                StackCapability.MEAN_REVERSION,
                StackCapability.BREAKOUT,
                StackCapability.STATISTICAL_ARBITRAGE,
                StackCapability.MARKET_MAKING,
                StackCapability.SENTIMENT,
                StackCapability.VOLATILITY_TARGETING,
            }
        ),
        StackLayer.EXECUTION: frozenset(
            {
                StackCapability.APPROVED_ORDER_ONLY,
                StackCapability.IDEMPOTENT_ORDER_IDS,
                StackCapability.PARTIAL_FILL_HANDLING,
                StackCapability.RECONCILIATION,
                StackCapability.RETRY_BUDGET,
                StackCapability.RATE_LIMIT_CONTROL,
            }
        ),
        StackLayer.RISK: frozenset(
            {
                StackCapability.KILL_SWITCH,
                StackCapability.MAX_DRAWDOWN,
                StackCapability.MAX_LEVERAGE,
                StackCapability.MAX_POSITION,
                StackCapability.DAILY_LOSS_LIMIT,
                StackCapability.CIRCUIT_BREAKER,
                StackCapability.VAR_EXPECTED_SHORTFALL,
                StackCapability.EXPOSURE_CAP,
            }
        ),
        StackLayer.SECURITY_OPERATIONS: frozenset(
            {
                StackCapability.TRADE_ONLY_CREDENTIALS,
                StackCapability.NO_WITHDRAWAL,
                StackCapability.IP_ALLOWLIST,
                StackCapability.SECRETS_MANAGER,
                StackCapability.IMMUTABLE_AUDIT,
                StackCapability.ALERTING,
                StackCapability.RUNTIME_ISOLATION,
                StackCapability.BACKUP_RECOVERY,
                StackCapability.CODE_REVIEW,
            }
        ),
    }


def _minimum_capabilities(stage: StackStage) -> dict[StackLayer, set[StackCapability]]:
    minimum: dict[StackLayer, set[StackCapability]] = {
        StackLayer.RESEARCH_AI: {
            StackCapability.REPRODUCIBLE_RESEARCH,
            StackCapability.MODEL_VERSIONING,
        },
        StackLayer.DATA_INTELLIGENCE: {
            StackCapability.DATA_VALIDATION,
            StackCapability.POINT_IN_TIME_LINEAGE,
            StackCapability.STALENESS_DETECTION,
        },
        StackLayer.STRATEGY: {
            StackCapability.STRATEGY_VERSIONING,
            StackCapability.SIGNAL_ONLY_OUTPUT,
        },
        StackLayer.EXECUTION: {
            StackCapability.APPROVED_ORDER_ONLY,
            StackCapability.IDEMPOTENT_ORDER_IDS,
            StackCapability.RECONCILIATION,
        },
        StackLayer.RISK: {
            StackCapability.KILL_SWITCH,
            StackCapability.MAX_DRAWDOWN,
            StackCapability.MAX_POSITION,
            StackCapability.EXPOSURE_CAP,
        },
        StackLayer.SECURITY_OPERATIONS: {
            StackCapability.NO_WITHDRAWAL,
            StackCapability.SECRETS_MANAGER,
            StackCapability.IMMUTABLE_AUDIT,
            StackCapability.CODE_REVIEW,
        },
    }
    if stage >= StackStage.PAPER:
        minimum[StackLayer.RESEARCH_AI].update(
            {StackCapability.WALK_FORWARD_VALIDATION, StackCapability.OUT_OF_SAMPLE_VALIDATION}
        )
        minimum[StackLayer.EXECUTION].update(
            {StackCapability.PARTIAL_FILL_HANDLING, StackCapability.RETRY_BUDGET}
        )
        minimum[StackLayer.RISK].update(
            {
                StackCapability.MAX_LEVERAGE,
                StackCapability.DAILY_LOSS_LIMIT,
                StackCapability.CIRCUIT_BREAKER,
            }
        )
        minimum[StackLayer.SECURITY_OPERATIONS].update(
            {
                StackCapability.ALERTING,
                StackCapability.RUNTIME_ISOLATION,
                StackCapability.BACKUP_RECOVERY,
            }
        )
    if stage >= StackStage.CONTROLLED_LIVE:
        minimum[StackLayer.RESEARCH_AI].add(StackCapability.MONTE_CARLO_PERTURBATION)
        minimum[StackLayer.EXECUTION].add(StackCapability.RATE_LIMIT_CONTROL)
        minimum[StackLayer.RISK].add(StackCapability.VAR_EXPECTED_SHORTFALL)
        minimum[StackLayer.SECURITY_OPERATIONS].update(
            {
                StackCapability.TRADE_ONLY_CREDENTIALS,
                StackCapability.IP_ALLOWLIST,
            }
        )
    return minimum


def _missing_capabilities(
    selected: dict[StackLayer, frozenset[StackCapability]],
    stage: StackStage,
) -> tuple[str, ...]:
    missing: list[str] = []
    for layer, required in _minimum_capabilities(stage).items():
        available = selected.get(layer, frozenset())
        missing.extend(
            f"{layer.value}:{capability.value}"
            for capability in sorted(required.difference(available), key=lambda item: item.value)
        )
    strategy_capabilities = selected.get(StackLayer.STRATEGY, frozenset())
    strategy_families = {
        StackCapability.TREND_FOLLOWING,
        StackCapability.MEAN_REVERSION,
        StackCapability.BREAKOUT,
        StackCapability.STATISTICAL_ARBITRAGE,
        StackCapability.MARKET_MAKING,
        StackCapability.SENTIMENT,
        StackCapability.VOLATILITY_TARGETING,
    }
    if strategy_capabilities.isdisjoint(strategy_families):
        missing.append("strategy:at_least_one_versioned_strategy_family")
    return tuple(sorted(missing))


def _connection_is_allowed(connection: StackConnection) -> bool:
    if connection.artifact is StackArtifact.AUDIT_EVENT:
        return connection.target is StackLayer.SECURITY_OPERATIONS
    allowed = set(_REQUIRED_CONNECTIONS)
    return connection in allowed


_REQUIRED_CONNECTIONS = (
    StackConnection(
        StackLayer.DATA_INTELLIGENCE,
        StackLayer.RESEARCH_AI,
        StackArtifact.FEATURE_VECTOR,
    ),
    StackConnection(
        StackLayer.DATA_INTELLIGENCE,
        StackLayer.STRATEGY,
        StackArtifact.NORMALIZED_MARKET_EVENT,
    ),
    StackConnection(StackLayer.RESEARCH_AI, StackLayer.STRATEGY, StackArtifact.FORECAST),
    StackConnection(StackLayer.STRATEGY, StackLayer.RISK, StackArtifact.ORDER_INTENT),
    StackConnection(StackLayer.RISK, StackLayer.EXECUTION, StackArtifact.APPROVED_ORDER),
    StackConnection(
        StackLayer.RISK,
        StackLayer.SECURITY_OPERATIONS,
        StackArtifact.RISK_DECISION,
    ),
    StackConnection(
        StackLayer.EXECUTION,
        StackLayer.SECURITY_OPERATIONS,
        StackArtifact.EXECUTION_REPORT,
    ),
)


def _required_gates(stage: StackStage) -> set[str]:
    gates = {
        "architecture_boundary_review",
        "contract_defined",
        "data_classification",
        "failure_mode_catalog",
        "owner_assigned",
        "traceability_plan",
    }
    if stage >= StackStage.FAKE:
        gates.update(
            {
                "audit_event_mapping",
                "deterministic_fixture_tests",
                "forbidden_edge_tests",
                "local_only_runtime",
            }
        )
    if stage >= StackStage.PAPER:
        gates.update(
            {
                "backtest_review",
                "dataset_lineage_review",
                "deterministic_risk_gateway",
                "incident_runbook",
                "kill_switch",
                "leakage_review",
                "observability_slo",
                "paper_trading_evidence",
                "reconciliation",
            }
        )
    if stage >= StackStage.CONTROLLED_LIVE:
        gates.update(
            {
                "capital_limit_approval",
                "credential_vault",
                "disaster_recovery_test",
                "human_approval",
                "ip_allowlist",
                "key_rotation",
                "network_approval",
                "production_readiness_review",
                "rollback_plan",
                "trade_only_credentials",
                "withdrawal_permissions_disabled",
            }
        )
    return gates
