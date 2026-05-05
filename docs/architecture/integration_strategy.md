# Integration Strategy

Platform integration must preserve modularity, auditability, deterministic controls, and operational clarity. `AGENTS.md` governs how agents must approach integration work.

The current scaffold contains integration folders and documentation only. It does not clone, vendor, install or execute external projects.

## Preferred Integration Patterns

- Contract-first APIs for request/response workflows.
- Versioned event schemas for asynchronous workflows.
- Idempotent commands for order, execution, and reconciliation flows.
- Correlation identifiers across services.
- Explicit timeout, retry, and backoff policies.
- Structured logs and metrics for all production-facing integrations.

## AI Integration

AI services may enrich research, signals, explanations, documentation, monitoring, and operator support. AI output must be validated before it reaches strategy, risk, portfolio, or execution paths.

AI payloads should carry:

- Input references.
- Model or prompt version.
- Timestamp and freshness.
- Confidence or uncertainty metadata.
- Validation status.
- Audit correlation identifiers.

AI output must not directly place orders, change limits, promote models, or override controls.

## External Integration

External providers, brokers, venues, data vendors, and model APIs must have:

- Documented purpose.
- Authentication and authorization model.
- Timeout and retry behavior.
- Rate-limit behavior.
- Failure and degradation mode.
- Audit and observability plan.
- Test or simulation approach.

## Integration Review Checklist

- Are contracts explicit and versioned?
- Are failures observable and bounded?
- Is sensitive data protected?
- Is the integration deterministic where enforcement is required?
- Is rollback possible?
- Are tests sufficient for the operational risk?

## Explicitly Forbidden Direct Paths

- AI, LLM agents, dashboards, notebooks or backtests directly to brokers or exchanges.
- Model services directly to brokers or exchanges.
- Signal services directly to brokers or exchanges.
- Paper trading tools sharing live execution credentials.
