# Capability Maturity Matrix

## Purpose

This matrix is the central map for repository capabilities. It links each domain to its current maturity, allowed behavior, forbidden behavior, required contracts, required tests, approval gate, promotion target and owner boundary.

It exists to prevent scaffold drift. A capability must not move from documentation or contract state into runtime behavior without an explicit promotion path and test evidence.

## Maturity States

| State | Meaning |
| --- | --- |
| `SCAFFOLD_ONLY` | Directory, placeholder or policy exists. No behavior is active. |
| `CONTRACT_DEFINED` | JSON Schema and fixtures define the payload boundary. |
| `FAKE_RUNTIME_ONLY` | Local fake or in-memory behavior exists for tests only. |
| `READ_ONLY_ADAPTER_ONLY` | Adapter boundary allows read-only data access after review. |
| `PAPER_ONLY` | Paper or simulation behavior only. No capital impact. |
| `GATED_LIVE_READ_ONLY` | Future read-only external access with explicit gates. |
| `GATED_LIVE_EXECUTION` | Future execution path with explicit risk, security and operations gates. |
| `PRODUCTION_BLOCKED` | Capability is intentionally blocked from production use. |

## Global Forbidden States

These states are forbidden by default and require separate governance before any appearance in code, tests, examples or docs as enabled behavior:

- `LIVE_TRADING_ENABLED`
- `BROKER_PRIVATE_ENDPOINTS`
- `ORDER_SUBMISSION`
- `ORDER_CANCELLATION`
- `POSITION_MUTATION`
- `UNREVIEWED_AGENT_RUNTIME`
- `UNGATED_MEMORY_RUNTIME`
- `UNGATED_NETWORK_ACCESS`
- `UNGATED_CREDENTIAL_ACCESS`
- `BYPASS_DETERMINISTIC_RISK_GATEWAY`

## Capability Matrix

| Domain | Current status | Allowed capability | Forbidden capability | Required contracts | Required tests | Required approval gate | Promotion target | Owner boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Service scaffold | `SCAFFOLD_ONLY` | Health and readiness placeholders | Business runtime, broker calls, credentials | Service README and placeholder tests | `test_service_placeholders.py`, `scaffold_audit.py` | Architecture review | `CONTRACT_DEFINED` | Service owner |
| Trading contracts | `CONTRACT_DEFINED` | OrderIntent, RiskDecision, ApprovedOrder and ExecutionReport schemas | Direct execution, broker calls, risk bypass | Trading schemas | Contract schema, fixture and validator tests | Risk architecture review | `PAPER_ONLY` | Risk and execution boundaries |
| Audit contracts | `CONTRACT_DEFINED` | Structured audit payloads and redaction checks | Secret-bearing audit payloads | AuditEvent schema | Audit emitter and redaction tests | Security review | `FAKE_RUNTIME_ONLY` | Observability boundary |
| Prediction research contracts | `CONTRACT_DEFINED` | Dossiers, probabilities, hypotheses, debates, signal candidates and advisory inputs | Order creation, execution approval, risk approval | Research schemas | Prediction research contract tests | Governance review | `FAKE_RUNTIME_ONLY` | Research boundary |
| Agent orchestration governance | `CONTRACT_DEFINED` | Plans, roles, handoffs, consensus and disabled runtime policies | Autonomous agent runtime, MCP runtime, federation, background workers | Agent governance schemas | Agent runtime approval gate tests | Agent runtime approval gate | `FAKE_RUNTIME_ONLY` | Governance boundary |
| Agent memory governance | `CONTRACT_DEFINED` | Redacted memory records, recall contracts, retention and conflict policy | External memory runtime, embeddings, automatic context priming, federation | Memory governance schemas | Memory governance contract tests | Memory runtime approval gate | `FAKE_RUNTIME_ONLY` | Governance and security boundary |
| Market data adapters | `FAKE_RUNTIME_ONLY` | In-memory adapter and fake-client CCXT skeleton | Real exchange clients, private endpoints, credentials | Market data interfaces and CCXT docs | Adapter registry and CCXT safety tests | External adapter review checklist | `READ_ONLY_ADAPTER_ONLY` | Market data boundary |
| CCXT optional dependency | `PRODUCTION_BLOCKED` | Documentation, fail-closed import guard and fake tests | Dependency install, real import, real client, network, credentials | CCXT approval docs | CCXT import guard and mocked tests | CCXT approval gate | `GATED_LIVE_READ_ONLY` | Market data and security boundary |
| Security tooling | `FAKE_RUNTIME_ONLY` | CodeQL, local policy tests, secret and artifact audit | Tokens for external SaaS tools, autonomous offensive tools | Security policy docs | Security tooling and artifact audit tests | Security tooling policy review | `READ_ONLY_ADAPTER_ONLY` | Security boundary |
| Execution engine | `SCAFFOLD_ONLY` | Placeholder service only | Order submission, cancellation, private endpoint access, portfolio mutation | ExecutionReport and ApprovedOrder schemas | Contract tests and scaffold audit | Execution approval gate | `GATED_LIVE_EXECUTION` | Execution boundary |

## Traceability Rule

Every promoted capability must have:

- a documented owner boundary;
- a contract or explicit policy document;
- a valid fixture when payloads cross service boundaries;
- a local test proving the allowed behavior;
- a local test proving forbidden behavior remains blocked;
- an approval gate reference;
- a rollback or demotion path.

## Default Runtime Position

The repository remains scaffold and research-only by default. Runtime behavior that touches network, credentials, private endpoints, trading, execution or production deployment is blocked unless a specific gate changes that state in a separate reviewed PR.
