# CCXT Import Guard Design

## Purpose

This document defines how a future optional CCXT import guard should work.

This document does not approve installing `ccxt`.

This document does not implement the import guard.

This document does not enable real exchange access.

## Current Status

- CCXT dependency is not installed.
- CCXT is not imported anywhere.
- CCXT runtime is disabled.
- CCXT production use is disabled.
- Network access is disabled.
- Credentials are not allowed.
- Only fake/mocked clients are currently tested.

## Import-Guard Principles

- no top-level `ccxt` import
- import only inside a future explicitly gated factory function
- feature flag must default false
- failure must be explicit and safe
- missing dependency must raise a clear local error
- CI must remain fake/mocked only
- no credentials required
- no network call during import
- no exchange client creation unless explicitly enabled by approved gate

## Future Error Behavior

A future local error class may be named `CCXTDependencyUnavailable`.

The message must explain that `ccxt` is optional and not installed.

The message must not include credentials, environment variable values or secrets.

The message must direct developers to the dependency approval docs.

The error must not attempt installation.

## Future Factory Behavior

A future factory function may be shaped conceptually as:

```python
create_ccxt_public_client(exchange_id: str, *, enabled: bool = False)
```

Required behavior:

- if `enabled` is false, fail closed
- if `ccxt` is missing, raise `CCXTDependencyUnavailable`
- if `exchange_id` is not allowlisted, fail closed
- create public/read-only client only
- do not accept API key parameters
- do not read environment variables
- do not call private endpoints
- do not enable trading methods

## Allowed Future Import Location

- only inside `packages/sdk/market_data_adapters/ccxt_factory.py`
- no global import in package `__init__.py`
- no import in tests that run in CI unless the dependency gate is explicitly approved
- no import in services

## Feature Flag Policy

- default: false
- must be explicitly enabled only after approval gate
- CI remains disabled
- production remains disabled until separate production gate
- feature flag must not imply credentials or trading permission

## CI Policy

- CI must not install `ccxt` by default
- CI must not call exchanges
- CI must not require secrets
- CI must use fake/mocked clients
- any real public smoke test must be manual, non-CI and separately approved

## Security Boundaries

- no credentials
- no API keys
- no private endpoints
- no account reads
- no position reads
- no order history
- no trading methods
- no withdrawal permissions
- no transfer permissions

## Prohibited Implementation Patterns

- import `ccxt` at module top level
- import `ccxt` in package `__init__.py`
- silently fallback to real exchange
- read API keys from env vars
- create authenticated clients
- enable trading methods
- run network smoke tests in CI
- catch all exceptions and hide dependency state

## Required Tests Before Implementation

- missing dependency raises local explicit error
- disabled feature flag fails closed
- non-allowlisted exchange fails closed
- no env vars are read
- no credentials are accepted
- fake/mocked tests still pass
- scaffold audit passes
- CI remains network-free

## Relationship To Approval Gate

See `docs/integrations/ccxt_approval_gate.md`.

See `docs/adr/0016-ccxt-optional-readonly-dependency-gate.md`.

The approval gate still controls whether implementation may proceed.

## Non-Goals

- no dependency installation
- no runtime implementation
- no real client factory
- no exchange access
- no private endpoints
- no trading
- no credentials
- no production enablement
