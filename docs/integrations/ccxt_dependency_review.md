# CCXT Dependency Review And Production Readiness

## Purpose

CCXT is a candidate dependency for public, read-only crypto market data.

This document does not approve installation, production use, private endpoints, credentials or live trading. It defines the review that must pass before any future real CCXT read-only integration is implemented.

## Current Status

- Skeleton adapter exists.
- Registry registration uses fake/in-memory client only.
- No `ccxt` dependency is installed.
- No real exchange client is instantiated.
- No network calls are made.
- No credentials are used.

## Allowed Future Scope

- public OHLCV
- public trades
- public order book snapshots
- public funding rates where supported
- exchange metadata if public and read-only

## Explicitly Prohibited Scope

- `create_order`
- `cancel_order`
- `edit_order`
- `withdraw`
- `transfer`
- `borrow`
- `repay`
- `set_leverage`
- private endpoints
- authenticated trading keys
- withdrawal keys
- live execution
- risk approval
- `OrderIntent` creation
- `ApprovedOrder` creation

## Dependency Review Checklist

- license reviewed
- maintenance activity reviewed
- release cadence reviewed
- security advisories reviewed
- transitive dependencies reviewed
- API stability reviewed
- supported exchanges reviewed
- rate limits reviewed
- error handling reviewed
- timestamp behavior reviewed
- precision/decimal behavior reviewed

## Security Checklist

- no API keys required for public read-only mode
- no secrets in tests
- no credentials in environment examples
- no private endpoints
- no logs containing secrets
- no trading permissions
- no withdrawal permissions
- adapter rejects execution-like client methods

## Reliability Checklist

- deterministic tests with mocked/fake client
- stale data detection plan
- rate limit handling plan
- retry/backoff plan
- timeout plan
- partial outage behavior
- degraded mode behavior
- exchange-specific capability detection
- schema/contract conversion tests

## Observability Checklist

- adapter health events
- latency metrics
- error metrics
- stale-feed metrics
- rate-limit metrics
- audit events for adapter configuration changes

## Production-Readiness Gates

- dependency review approved
- security review approved
- read-only integration tests passed
- no credentials required
- no prohibited methods exposed
- no private endpoints used
- market data stale guards implemented
- observability implemented
- runbook exists
- rollback plan exists

## Future Implementation Plan

Phase 1: mocked client integration tests.

Phase 2: optional dependency declaration after approval.

Phase 3: public read-only sandbox/manual smoke test.

Phase 4: controlled read-only deployment.

Phase 5: production read-only market data use.

## Non-Goals

- no live trading
- no broker execution
- no private account access
- no order management
- no portfolio mutation
- no risk decisioning
