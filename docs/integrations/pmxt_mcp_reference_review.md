# PMXT MCP Reference Review

## Purpose

This document reviews `pmxt-dev/pmxt-mcp` as a reference for future prediction-market MCP safety boundaries.

Repository: https://github.com/pmxt-dev/pmxt-mcp

This review does not approve installation, `npx` execution, PMXT API access, credentials, network calls, MCP runtime integration, trading tools or production use.

## Current Decision State

```text
direct_dependency_allowed: false
npx_execution_allowed: false
clone_allowed: false
vendoring_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
pmxt_api_key_allowed: false
pmxt_api_url_allowed: false
private_endpoints_allowed: false
trading_tools_allowed: false
account_tools_allowed: false
mcp_runtime_allowed: false
```

## What Is Useful

The repository is useful as a reference for:

- MCP tool catalog structure
- generated tool definitions from an OpenAPI-style spec
- read-only tool annotations
- destructive tool annotations
- separating market discovery, pricing, order book and trade data from trading/account tools
- explicit tool naming that can feed local allowlist and denylist tests

## Safe Read-Only Tool Patterns

Future internal MCP-compatible tools may model only these read-only patterns:

- `fetchMarkets`
- `fetchMarketsPaginated`
- `fetchEvents`
- `fetchEvent`
- `fetchMarket`
- `fetchOrderBook`
- `fetchTrades`
- `fetchOHLCV`
- `compareMarketPrices`
- `fetchEventMatches`
- `fetchArbitrage`

These names are reference patterns only. They do not approve PMXT installation or API calls.

## Explicitly Prohibited Tool Patterns

The following PMXT MCP patterns must not be exposed to agents in this platform:

- `buildOrder`
- `createOrder`
- `submitOrder`
- `cancelOrder`
- `fetchBalance`
- `fetchPositions`
- `fetchOpenOrders`
- `fetchClosedOrders`
- `fetchAllOrders`
- `fetchOrder`
- `fetchMyTrades`
- `loadMarkets` when it requires credentials or account context
- any tool accepting `credentials`
- any tool requiring API keys
- any tool reading private account state

## Credential And Network Boundary

The upstream MCP server supports hosted and sidecar modes. Both are out of scope for this platform now.

Forbidden:

- `PMXT_API_KEY`
- `PMXT_API_URL`
- hosted PMXT API calls
- local PMXT sidecar calls
- `npx @pmxt/mcp`
- Claude Desktop MCP configuration
- environment-variable based credentials
- credential forwarding through MCP tools

## MCP Safety Rule

MCP tools may analyze, summarize, compare, retrieve public read-only market data through separately approved adapters, and report.

MCP tools must not:

- build orders
- create orders
- submit orders
- cancel orders
- read balances
- read positions
- read open or closed orders
- read account trade history
- accept credentials
- change risk limits
- disable kill switches
- bypass deterministic-risk-gateway
- create `OrderIntent`
- create `ApprovedOrder`

## Future Internal Adaptation

The safe adaptation path is:

1. Keep PMXT MCP reference-only.
2. Maintain a local read-only tool allowlist.
3. Maintain a destructive/account tool denylist.
4. Add local fake/in-memory tool catalog tests first.
5. Map allowed tools to internal contracts before runtime work.
6. Require external adapter review before any dependency or network integration.

## Non-Goals

- no PMXT dependency
- no MCP server runtime
- no `npx`
- no PMXT hosted API
- no sidecar API
- no credentials
- no account tools
- no order tools
- no trading
- no live execution
- no production enablement
