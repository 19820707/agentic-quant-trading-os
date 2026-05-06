# Schema Registry

This document defines the local JSON Schema registry for Agentic Quant Trading OS.

The registry is contract-first infrastructure. It defines payload shape at service boundaries. It does not implement trading logic, risk approval, execution approval, broker access, or live trading.

## Registry Location

Schemas live under:

```text
packages/contracts/schemas/
```

Each schema is grouped by domain:

| Domain | Purpose |
| --- | --- |
| `market` | Market data payload contracts. |
| `features` | Feature and feature snapshot payload contracts. |
| `ml` | Prediction, model, and monitoring payload contracts. |
| `trading` | Trading lifecycle contracts before and after deterministic risk review. |
| `paper` | Paper trading contracts. |
| `audit` | Append-only audit and observability event contracts. |
| `security` | Security, secret handling, and access policy contracts. |
| `governance` | Human approval, promotion gate, and policy decision contracts. |

## Naming Convention

Schema files use lowercase snake case and the `.schema.json` suffix:

```text
<domain>/<contract_name>.schema.json
```

Examples:

```text
trading/order_intent.schema.json
trading/risk_decision.schema.json
trading/approved_order.schema.json
trading/execution_report.schema.json
audit/audit_event.schema.json
```

Schema titles use PascalCase, such as `OrderIntent` and `AuditEvent`.

Schema `$id` values must be stable and must follow the local project URI pattern:

```text
https://agentic-quant-trading-os.local/schemas/<domain>/<contract_name>.schema.json
```

## Versioning

Every schema must include:

```json
"schema_version": {
  "type": "string",
  "const": "0.1.0"
}
```

Rules:

- Patch-level compatible changes may add optional fields.
- Required fields, enum removals, pattern tightening, or semantic changes require a new schema version.
- Payload changes require schema updates and tests in the same PR.
- Cross-service payloads must include `trace_id` and `correlation_id` where relevant.
- Trading lifecycle contracts must preserve lifecycle identifiers across the flow.

## Core Contract Flow

The governed trading lifecycle is:

```text
OrderIntent -> RiskDecision -> ApprovedOrder -> ExecutionReport -> AuditEvent
```

Contract authority:

| Contract | Created By | Meaning | Not Allowed |
| --- | --- | --- | --- |
| `OrderIntent` | order-intent-service | Non-executable request for risk review. | Broker submission or execution. |
| `RiskDecision` | deterministic-risk-gateway | Final pre-trade risk decision. | Broker submission or execution. |
| `ApprovedOrder` | deterministic-risk-gateway | Only object execution-engine may accept in future controlled-live mode. | Direct broker API behavior in the contract. |
| `ExecutionReport` | execution-engine or paper-trading-engine | Execution or paper execution event record. | Credentials or broker submission implementation. |
| `AuditEvent` | observability-audit-service or critical services | Append-only proof of critical events. | Secrets, credentials, or mutable audit history. |

## Required Safety Properties

- Schemas must use JSON Schema draft 2020-12.
- Root schemas should use `type: object`.
- Boundary contracts should use `additionalProperties: false`.
- IDs must be pattern-constrained where lifecycle naming exists.
- Examples must be safe paper or audit examples only.
- Examples must not contain credentials, tokens, keys, or live broker configuration.

## Contract Validator

`packages.contracts.ContractValidator` loads schemas from the local registry and validates JSON-compatible payloads.

The validator:

- loads schemas only from `packages/contracts/schemas/`
- rejects path traversal and absolute schema paths
- validates payload shape
- returns structured validation results
- can raise validation exceptions when requested

The validator does not:

- decide risk
- approve execution
- interpret trading semantics
- submit orders
- call services
- call the network
- access broker or exchange code
- access credentials
- read secrets
- require broker or exchange API keys

Use it for local contract validation only.
