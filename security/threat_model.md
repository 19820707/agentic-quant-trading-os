# Threat Model

This is a scaffold-level threat model. It must evolve before any production or live-capable implementation.

## Assets

- Source code.
- Contracts and schemas.
- Configuration.
- Audit records.
- Data manifests and snapshots.
- Model artifacts and registry metadata.
- Future broker or exchange credentials.
- Future governance approval evidence.

## Trust Boundaries

- Agentic layer to deterministic services.
- Model services to signal services.
- Signal services to Order Intent Service.
- Order Intent Service to Deterministic Risk Gateway.
- Deterministic Risk Gateway to Execution Engine.
- Execution Engine to broker or exchange adapters.
- Services to observability and audit storage.

## Prohibited Credential Paths

- Agents must not receive broker credentials.
- Dashboards must not receive broker credentials.
- Model services must not receive broker credentials.
- Signal services must not receive broker credentials.
- Risk Gateway does not need broker credentials.
- Paper trading must not share live credentials.

## Threats

- Secret leakage through code, logs, traces, prompts or reports.
- Direct broker path bypassing Risk Gateway.
- Model output treated as authoritative.
- Contract drift across services.
- Audit record mutation or deletion.
- Training data leakage.
- Unreviewed external dependency or vendored code.
- Unsafe default configuration.
- Kill switch bypass or failure.

## STRIDE Summary

| Category | Scaffold concern | Baseline response |
| --- | --- | --- |
| Spoofing | Fake service or actor identity in future workflows | Require explicit identity model before privileged actions |
| Tampering | Contract, config, dataset or audit mutation | Versioned artifacts and append-only audit design |
| Repudiation | Missing evidence for decisions | `trace_id`, `correlation_id` and audit IDs at boundaries |
| Information disclosure | Secrets in prompts, logs, traces or reports | No credentials in repo; secret exposure tests before credentialed work |
| Denial of service | Dependency or queue failure in future services | Bounded retries, health checks and degradation plans |
| Elevation of privilege | Agent or model obtains execution capability | Agents and models cannot access broker credentials or bypass Risk Gateway |

## Abuse Cases

- Agent-generated code creates a direct broker path.
- Dashboard action submits an order without Risk Gateway approval.
- Model confidence is used as approval authority.
- Backtest result is treated as live approval.
- Paper trading environment shares live credentials.
- External adapter bypasses contract schemas.
- Logs capture token, key, account or credential material.

Each abuse case must remain blocked by architecture, contracts, tests and review.

## Baseline Controls

- Contract-first boundaries.
- No live credentials in repository.
- Execution isolated behind future approved adapters.
- Append-only audit expectation.
- Promotion gates before live use.
- Scaffold audit script for placeholder integrity.

## Security Review Triggers

Require security review before changes to:

- authentication or authorization
- secrets or credential paths
- external integrations
- execution adapters
- audit storage
- CI/CD or deployment
- dependency supply chain
- agentic tool permissions

## Open Work Before Production

- Full STRIDE review.
- Dependency threat review.
- Secrets management design.
- Identity and access-control model.
- Audit storage design.
- Incident response drills.
- Live credential rotation procedure.
