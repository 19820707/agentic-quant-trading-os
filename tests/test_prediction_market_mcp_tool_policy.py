import inspect
import unittest
from pathlib import Path

from packages.sdk.prediction_market_mcp_tool_policy import (
    MCPToolDefinition,
    MCPToolSafetyClass,
    UnsafeMCPToolError,
    UnknownMCPToolError,
    assert_prediction_market_mcp_tool_allowed,
    classify_prediction_market_mcp_tool,
)


MODULE_PATH = Path("packages/sdk/prediction_market_mcp_tool_policy.py")

READ_ONLY_TOOLS = (
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
)

DANGEROUS_TOOLS = (
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
)


class PredictionMarketMCPToolPolicyTests(unittest.TestCase):
    def test_read_only_tools_are_allowlisted(self) -> None:
        for name in READ_ONLY_TOOLS:
            with self.subTest(name=name):
                tool = MCPToolDefinition(
                    name=name,
                    input_schema={"type": "object", "properties": {"exchange": {"type": "string"}}},
                    annotations={"readOnlyHint": True},
                )
                self.assertEqual(MCPToolSafetyClass.READ_ONLY, classify_prediction_market_mcp_tool(tool))

    def test_destructive_and_account_tools_are_rejected(self) -> None:
        for name in DANGEROUS_TOOLS:
            with self.subTest(name=name):
                tool = MCPToolDefinition(
                    name=name,
                    input_schema={"type": "object", "properties": {"exchange": {"type": "string"}}},
                    annotations={"readOnlyHint": True},
                )
                with self.assertRaises(UnsafeMCPToolError):
                    assert_prediction_market_mcp_tool_allowed(tool)

    def test_unknown_tools_fail_closed(self) -> None:
        tool = MCPToolDefinition(
            name="fetchVenueSecretState",
            input_schema={"type": "object", "properties": {"exchange": {"type": "string"}}},
            annotations={"readOnlyHint": True},
        )

        with self.assertRaises(UnsafeMCPToolError):
            classify_prediction_market_mcp_tool(tool)

        unknown_safe_name = MCPToolDefinition(
            name="fetchPublicSomethingElse",
            input_schema={"type": "object", "properties": {"exchange": {"type": "string"}}},
            annotations={"readOnlyHint": True},
        )
        with self.assertRaises(UnknownMCPToolError):
            classify_prediction_market_mcp_tool(unknown_safe_name)

    def test_destructive_annotation_is_rejected(self) -> None:
        tool = MCPToolDefinition(
            name="fetchMarkets",
            input_schema={"type": "object", "properties": {"exchange": {"type": "string"}}},
            annotations={"destructiveHint": True},
        )

        with self.assertRaises(UnsafeMCPToolError):
            classify_prediction_market_mcp_tool(tool)

    def test_credential_schema_fields_are_rejected(self) -> None:
        forbidden_fields = ("credentials", "apiKey", "apiSecret", "apiToken", "privateKey", "passphrase")

        for field in forbidden_fields:
            with self.subTest(field=field):
                tool = MCPToolDefinition(
                    name="fetchMarkets",
                    input_schema={"type": "object", "properties": {field: {"type": "string"}}},
                    annotations={"readOnlyHint": True},
                )
                with self.assertRaises(UnsafeMCPToolError):
                    classify_prediction_market_mcp_tool(tool)

    def test_policy_module_does_not_import_mcp_network_or_env_runtimes(self) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8").lower()

        for forbidden in (
            "@modelcontextprotocol",
            "pmxt",
            "requests",
            "urllib",
            "socket",
            "subprocess",
            "os.environ",
            "process.env",
            "npx",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_module_exposes_no_execution_functions(self) -> None:
        import packages.sdk.prediction_market_mcp_tool_policy as policy

        names = set(dir(policy))
        for _, member in inspect.getmembers(policy):
            if inspect.isclass(member):
                names.update(dir(member))

        for prohibited in ("createOrder", "submitOrder", "cancelOrder", "buildOrder", "execute", "withdraw", "transfer"):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, names)


if __name__ == "__main__":
    unittest.main()
