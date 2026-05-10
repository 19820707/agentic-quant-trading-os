# MCP Prediction Market Tool Safety

## Purpose

This document defines the local safety boundary for future MCP-style prediction-market tools.

It is inspired by `pmxt-dev/pmxt-mcp`, but it does not approve installing PMXT MCP, running MCP servers, calling network APIs, reading credentials, exposing account tools or enabling trading.

## Tool Classes

### Read-Only Market Discovery

Allowed future patterns:

- fetch events
- fetch markets
- fetch a market by public identifier
- fetch public event matches

Required boundary:

- no credentials
- no private endpoint
- no account state
- no order creation

### Read-Only Market Data

Allowed future patterns:

- fetch public order book snapshots
- fetch public trades
- fetch public OHLCV
- compare public market prices
- identify public arbitrage candidates as research only

Required boundary:

- output must remain research or market data
- arbitrage findings are not execution permission
- no direct path to broker, exchange, wallet or PMXT hosted trading tools

### Destructive Or Account Tools

Rejected by default:

- order building
- order submission
- order cancellation
- balance reads
- position reads
- open-order reads
- closed-order reads
- private trade history reads
- credential-bearing tools

These tools are not allowed for MCP/agentic surfaces in this platform.

## Required Local Policy

Every future prediction-market MCP tool catalog must enforce:

- explicit read-only allowlist
- explicit destructive/account denylist
- no credentials in schemas
- no API key fields
- no private key fields
- no network calls in unit tests
- no tool named `createOrder`, `submitOrder`, `cancelOrder` or `buildOrder`
- no tool that can create `OrderIntent` or `ApprovedOrder`
- no bypass of deterministic-risk-gateway

## Failure Posture

Unknown tools fail closed.

Tools with missing annotations fail closed.

Tools containing credential fields fail closed.

Tools with order, account, position, balance, transfer or withdrawal semantics fail closed.

## Internal Contract Boundary

Future allowed tools must map to internal contracts before runtime use.

Allowed outputs may include:

- research dossiers
- probability estimates
- signal candidates
- risk-review inputs
- read-only market data snapshots

Forbidden outputs:

- `OrderIntent`
- `ApprovedOrder`
- `ExecutionReport`
- wallet transactions
- broker or exchange requests
- risk approvals
- execution approvals

## Non-Goals

- no MCP runtime
- no external PMXT dependency
- no hosted PMXT API calls
- no sidecar calls
- no credentials
- no private endpoints
- no account access
- no order management
- no live trading
