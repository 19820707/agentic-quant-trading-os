"""Deterministic risk boundary.

Current implementation evaluates local pre-trade risk and remains fail-closed:
successful checks return REVIEW, not execution approval.
"""

from .evaluator import (
    PriceReference,
    RiskEvaluation,
    RiskEvaluationError,
    RiskLimits,
    RiskRuntimeState,
    evaluate_risk,
)
from .trading_runtime_gate import (
    BLOCKED_RUNTIME_CAPABILITIES,
    REQUIRED_RUNTIME_EVIDENCE,
    RuntimeActivationDecision,
    RuntimeMode,
    TradingRuntimeActivationReport,
    TradingRuntimeActivationRequest,
    TradingRuntimeGateError,
    evaluate_trading_runtime_activation,
)

__all__ = [
    "BLOCKED_RUNTIME_CAPABILITIES",
    "PriceReference",
    "REQUIRED_RUNTIME_EVIDENCE",
    "RiskEvaluation",
    "RiskEvaluationError",
    "RiskLimits",
    "RiskRuntimeState",
    "RuntimeActivationDecision",
    "RuntimeMode",
    "TradingRuntimeActivationReport",
    "TradingRuntimeActivationRequest",
    "TradingRuntimeGateError",
    "evaluate_risk",
    "evaluate_trading_runtime_activation",
]
