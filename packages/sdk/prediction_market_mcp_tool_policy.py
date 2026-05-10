from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class MCPToolSafetyClass(str, Enum):
    READ_ONLY = "read_only"
    REJECTED = "rejected"


class MCPToolPolicyError(ValueError):
    """Raised when an MCP-style prediction-market tool violates local safety policy."""


class UnknownMCPToolError(MCPToolPolicyError):
    """Raised when a tool is not explicitly allowlisted."""


class UnsafeMCPToolError(MCPToolPolicyError):
    """Raised when a tool has destructive, account, or credential-bearing behavior."""


READ_ONLY_TOOL_ALLOWLIST = frozenset(
    {
        "fetchMarkets",
        "fetchMarketsPaginated",
        "fetchEvents",
        "fetchEvent",
        "fetchMarket",
        "fetchOrderBook",
        "fetchTrades",
        "fetchOHLCV",
        "compareMarketPrices",
        "fetchEventMatches",
        "fetchArbitrage",
    }
)

REJECTED_TOOL_DENYLIST = frozenset(
    {
        "buildOrder",
        "createOrder",
        "submitOrder",
        "cancelOrder",
        "fetchBalance",
        "fetchPositions",
        "fetchOpenOrders",
        "fetchClosedOrders",
        "fetchAllOrders",
        "fetchOrder",
        "fetchMyTrades",
        "loadMarkets",
    }
)

PROHIBITED_SCHEMA_FIELDS = frozenset(
    {
        "credentials",
        "apiKey",
        "apiSecret",
        "apiToken",
        "privateKey",
        "passphrase",
        "funderAddress",
        "secret",
    }
)

PROHIBITED_NAME_FRAGMENTS = (
    "order",
    "balance",
    "position",
    "credential",
    "secret",
    "private",
    "wallet",
    "withdraw",
    "transfer",
)


@dataclass(frozen=True)
class MCPToolDefinition:
    name: str
    input_schema: dict[str, Any]
    annotations: dict[str, Any] | None = None


def classify_prediction_market_mcp_tool(tool: MCPToolDefinition) -> MCPToolSafetyClass:
    """Classify a local MCP-style tool definition without executing it."""

    _validate_tool_name(tool.name)
    _reject_destructive_annotation(tool)
    _reject_credential_fields(tool.input_schema)

    if tool.name in READ_ONLY_TOOL_ALLOWLIST:
        return MCPToolSafetyClass.READ_ONLY

    raise UnknownMCPToolError(f"MCP tool is not explicitly allowlisted: {tool.name}")


def assert_prediction_market_mcp_tool_allowed(tool: MCPToolDefinition) -> None:
    safety_class = classify_prediction_market_mcp_tool(tool)
    if safety_class is not MCPToolSafetyClass.READ_ONLY:
        raise UnsafeMCPToolError(f"MCP tool is not read-only: {tool.name}")


def _validate_tool_name(name: str) -> None:
    if not name.strip():
        raise UnknownMCPToolError("MCP tool name is required")
    if name in REJECTED_TOOL_DENYLIST:
        raise UnsafeMCPToolError(f"MCP tool is explicitly rejected: {name}")
    lowered = name.lower()
    for fragment in PROHIBITED_NAME_FRAGMENTS:
        if fragment in lowered and name not in READ_ONLY_TOOL_ALLOWLIST:
            raise UnsafeMCPToolError(f"MCP tool name contains prohibited behavior: {name}")


def _reject_destructive_annotation(tool: MCPToolDefinition) -> None:
    annotations = tool.annotations or {}
    if annotations.get("destructiveHint") is True:
        raise UnsafeMCPToolError(f"MCP tool has destructive annotation: {tool.name}")
    if annotations.get("readOnlyHint") is False and tool.name not in READ_ONLY_TOOL_ALLOWLIST:
        raise UnsafeMCPToolError(f"MCP tool is not marked read-only: {tool.name}")


def _reject_credential_fields(schema: Any) -> None:
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key in PROHIBITED_SCHEMA_FIELDS:
                raise UnsafeMCPToolError(f"MCP tool schema contains prohibited field: {key}")
            if isinstance(key, str) and key in PROHIBITED_SCHEMA_FIELDS:
                raise UnsafeMCPToolError(f"MCP tool schema contains prohibited field: {key}")
            _reject_credential_fields(value)
    elif isinstance(schema, list):
        for item in schema:
            _reject_credential_fields(item)
