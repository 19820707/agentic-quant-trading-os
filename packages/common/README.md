# Common

`packages.common` contains shared value objects used across internal package boundaries.

Current scope:

- read-only market data request and response value objects
- standard-library-only dataclasses
- no services
- no broker or exchange execution
- no credentials
- no network calls

These objects describe data shape only. They do not place orders, decide risk, approve execution, or connect to external systems.

## Security Utilities

`packages.common.security` provides local-only redaction helpers for nested dictionaries, lists, tuples and scalar values before logging, audit events, reports, errors or debugging output.

The redaction helpers:

- do not call network
- do not access credentials
- do not read environment variables
- do not access files
- do not validate or store secrets
- do not replace Vault, Infisical, SOPS or another managed secret system

Withdrawal keys must never be used. If a withdrawal-related key appears in diagnostic data, it must be redacted before the data reaches logs, reports, audit events or prompts.

### Redaction Before Audit and Reports

Use `redact_secrets()` on structured audit-like, execution-report-like, error and report payloads before they reach logs, audit sinks, reports or debugging output.

Current redaction is key-based. Sensitive values must be carried in structured fields such as `api_key`, `token`, `authorization`, `broker_key`, `exchange_key`, `credentials` or `withdrawal_key` so they can be redacted deterministically. Free-form strings are not parsed for secret patterns in this scaffold phase.

## Audit Event Emitter Interface

`packages.common.audit` provides a local interface for preparing redacted AuditEvent-like payloads before a future audit sink receives them.

The audit helpers:

- redact structured sensitive fields before emission
- require `append_only` to be true
- require `contains_secrets` to be false
- do not persist audit events
- do not call network
- do not import services
- do not access credentials
- do not decide risk, approve execution or interpret trading semantics

This is not an audit service implementation. It is a local interface for safe payload preparation only.
