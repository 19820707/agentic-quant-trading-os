# External Adapter Review Checklist

## 1. Purpose

This checklist is required before implementing any external adapter.

It applies to:

- market data adapters
- storage adapters
- feature store adapters
- model monitoring adapters
- observability adapters
- security adapters
- paper trading adapters
- MCP / agentic adapters
- future execution adapters

Example market-data candidates include CCXT, OpenBB and Trading Economics. Each candidate must complete this checklist before implementation.

## 2. Adapter Identity

Complete these fields before implementation:

- [ ] adapter name:
- [ ] upstream repository URL:
- [ ] upstream license:
- [ ] upstream maintenance status:
- [ ] integration category:
- [ ] target internal service/package:
- [ ] integration mode:
- [ ] production readiness classification:
  - reference-only
  - research-only
  - paper-only
  - read-only production candidate
  - controlled-live candidate

## 3. Safety Boundary

- [ ] adapter purpose documented
- [ ] allowed operations documented
- [ ] forbidden operations documented
- [ ] no bypass of deterministic-risk-gateway
- [ ] no direct path from AI/agent/model/dashboard to broker/exchange
- [ ] no broker credentials unless future approved execution-engine adapter
- [ ] no withdrawal permissions
- [ ] no hidden execution paths

## 4. Dependency Review

- [ ] license reviewed
- [ ] dependency tree reviewed
- [ ] known vulnerabilities reviewed
- [ ] maintenance activity reviewed
- [ ] issue tracker reviewed
- [ ] release history reviewed
- [ ] transitive dependency risk documented
- [ ] no vendoring unless approved
- [ ] no Git submodule unless approved

## 5. Credential and Secret Review

- [ ] no credentials required for unit tests
- [ ] no credentials committed
- [ ] no credentials in examples
- [ ] no credentials in logs/errors/audit
- [ ] redaction applied to errors
- [ ] no environment variable requirement in unit tests
- [ ] no withdrawal keys
- [ ] no broad-scope API keys

## 6. Network Behavior Review

- [ ] no network calls in unit tests
- [ ] network calls are explicit in integration tests only
- [ ] timeouts configured
- [ ] retries bounded
- [ ] rate limits respected
- [ ] stale data behavior documented
- [ ] failure mode is fail-closed or read-only degraded

## 7. Contract Boundary Review

- [ ] internal contract selected
- [ ] adapter input/output mapped to internal contracts
- [ ] schema validation strategy documented
- [ ] trace_id/correlation_id propagation documented where relevant
- [ ] no undocumented payload exchange

## 8. Category-Specific Review

### Market Data

- [ ] read-only only
- [ ] no order methods
- [ ] no trade credentials
- [ ] no OrderIntent creation
- [ ] no ApprovedOrder creation
- [ ] stale feed detection planned

### Feature Store

- [ ] point-in-time correctness
- [ ] event_timestamp/created_timestamp/available_timestamp preserved
- [ ] leakage audit supported
- [ ] dataset versioning supported

### Model Monitoring

- [ ] reports drift/degradation only
- [ ] cannot modify execution state
- [ ] cannot override risk

### Paper Trading

- [ ] simulated execution only
- [ ] no live credentials
- [ ] cannot promote to live

### MCP / Agentic

- [ ] cannot access broker credentials
- [ ] cannot execute trades
- [ ] cannot change risk limits
- [ ] cannot disable kill switches

### Future Execution

- [ ] execution-engine only
- [ ] ApprovedOrder only
- [ ] reject raw OrderIntent
- [ ] idempotency required
- [ ] kill switch required
- [ ] ExecutionReport required
- [ ] AuditEvent required
- [ ] no withdrawal permissions

## 9. Testing Requirements

- [ ] local fake/in-memory tests first
- [ ] unit tests local-only
- [ ] no network in unit tests
- [ ] no secrets in tests
- [ ] prohibited method names tested
- [ ] adapter registry tests updated
- [ ] CI quality gates updated
- [ ] scaffold_audit.py passes

## 10. Approval Gates

- [ ] engineering review
- [ ] security review
- [ ] risk review where applicable
- [ ] governance review where applicable
- [ ] CI pass
- [ ] documentation complete
- [ ] PR approved before merge

## 11. Final Decision

Complete before approval:

- approved status:
  - rejected
  - reference-only
  - approved for research
  - approved for paper
  - approved for read-only production
  - approved for controlled-live execution
- reviewer:
- date:
- notes:
