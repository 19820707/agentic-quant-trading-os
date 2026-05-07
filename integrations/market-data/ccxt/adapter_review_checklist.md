# CCXT Adapter Review Checklist

## 1. Identity

- [ ] adapter name: CCXT read-only market data adapter
- [ ] upstream repository URL: https://github.com/ccxt/ccxt
- [ ] upstream license: pending review
- [ ] upstream maintenance status: pending review
- [ ] integration category: market-data
- [ ] target internal service/package: packages/sdk
- [ ] integration mode: future dependency / adapter
- [ ] current classification: research-only / safety-harness-only

## 2. License, Security and Maintenance Review

- [ ] license reviewed
- [ ] dependency tree reviewed
- [ ] known vulnerabilities reviewed
- [ ] maintenance activity reviewed
- [ ] issue tracker reviewed
- [ ] release history reviewed
- [ ] transitive dependency risk documented

## 3. Allowed Read-Only Operations

- [ ] fetch OHLCV
- [ ] fetch public trades
- [ ] fetch order book snapshots
- [ ] fetch funding rates where supported
- [ ] fetch market metadata where supported

## 4. Prohibited Operations

- [ ] no buy
- [ ] no sell
- [ ] no order
- [ ] no create_order
- [ ] no submit_order
- [ ] no cancel_order
- [ ] no modify_order
- [ ] no withdraw
- [ ] no transfer
- [ ] no execute
- [ ] no place_order
- [ ] no OrderIntent creation
- [ ] no ApprovedOrder creation
- [ ] no deterministic-risk-gateway bypass

## 5. Credential Review

- [ ] no credentials for unit tests
- [ ] no trade credentials
- [ ] no withdrawal credentials
- [ ] no credentials in examples
- [ ] no credentials in logs/errors/audit
- [ ] redaction applied to errors

## 6. Network Behavior Review

- [ ] no network calls in unit tests
- [ ] no real exchange calls in CI
- [ ] future integration-test network behavior explicit
- [ ] timeouts configured before any network implementation
- [ ] retries bounded before any network implementation
- [ ] stale data behavior documented before any network implementation

## 7. Unit Test Requirements

- [ ] fake/in-memory client used first
- [ ] no `ccxt` import required for unit tests
- [ ] prohibited method names tested
- [ ] adapter registry tests updated
- [ ] CI quality gates updated
- [ ] scaffold_audit.py passes

## 8. Final Decision

- approved status: research-only / safety-harness-only
- reviewer:
- date:
- notes:
