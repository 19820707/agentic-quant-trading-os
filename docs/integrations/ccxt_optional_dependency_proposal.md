# CCXT Optional Dependency Proposal

## Purpose

This is a proposal only.

It does not approve installation, production use, real exchange access, private endpoints, credentials or live trading. It defines how CCXT could later be considered as an optional public read-only market data dependency.

## Current Baseline

- CCXT skeleton adapter exists.
- Registry registration exists using fake/in-memory client.
- Mocked integration tests exist.
- No `ccxt` dependency is installed.
- No `ccxt` import exists.
- No network calls exist.
- No credentials exist.

## Proposed Dependency Mode

- optional dependency only
- public market data only
- no private endpoints
- no authenticated client
- no exchange credentials
- no trading methods
- no live execution

## Allowed Public Read-Only Methods

- `fetch_ohlcv`
- `fetch_trades`
- `fetch_order_book`
- public funding-rate methods only if available and unauthenticated
- public exchange metadata only if needed

## Explicitly Prohibited Methods And Capabilities

- `create_order`
- `cancel_order`
- `edit_order`
- `withdraw`
- `transfer`
- `borrow`
- `repay`
- `set_leverage`
- `private_*` endpoints
- authenticated trading
- account balance reads
- position reads
- order history reads
- private portfolio state
- any method requiring API keys

## Dependency Addition Gates

- license reviewed
- dependency security reviewed
- transitive dependencies reviewed
- maintenance status reviewed
- public-only configuration reviewed
- allowed methods allowlisted
- prohibited methods blocked
- CI tests passing
- scaffold_audit passing
- no credentials introduced
- no network tests in CI
- manual approval recorded

## Implementation Plan If Approved

Phase 1: add optional dependency declaration only.

Phase 2: add import guard with clear error if `ccxt` is missing.

Phase 3: add real client factory disabled by default.

Phase 4: add mocked tests for client factory.

Phase 5: add manually-run smoke test script marked non-CI and public-only.

Phase 6: add observability and stale-data guards.

Phase 7: production read-only approval gate.

## Runtime Safety Design

- feature flag disabled by default
- no API key parameters
- public endpoints only
- explicit allowlist of methods
- explicit denylist of dangerous methods
- timeout plan
- rate-limit plan
- stale-data handling
- deterministic error handling

## CI Policy

- CI must not call exchanges
- CI must not require `ccxt` unless dependency gate is explicitly approved
- CI must not require secrets
- CI must use fake/mocked clients only

## Rollback Plan

- remove optional dependency
- disable feature flag
- fallback to fake/in-memory adapter
- block adapter registration
- preserve audit trail

## Decision Record Placeholder

- approved: false
- approver: TBD
- approval_date: TBD
- conditions: TBD

## Non-Goals

- no live trading
- no broker execution
- no private endpoints
- no credentials
- no order management
- no account management
- no portfolio mutation
- no risk approval
- no execution approval
