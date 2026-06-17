"""Adapter boundaries.

No broker, exchange or external client SDK is implemented here yet.
"""

from .execution import (
    ExecutionAdapter,
    ExecutionAdapterConfig,
    ExecutionAdapterError,
    ExecutionAdapterHealth,
    ExecutionAdapterState,
    FailClosedExecutionAdapter,
    validate_execution_adapter_surface,
)

__all__ = [
    "ExecutionAdapter",
    "ExecutionAdapterConfig",
    "ExecutionAdapterError",
    "ExecutionAdapterHealth",
    "ExecutionAdapterState",
    "FailClosedExecutionAdapter",
    "validate_execution_adapter_surface",
]
