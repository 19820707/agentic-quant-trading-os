# SDK

`packages.sdk` defines internal SDK-facing interfaces for future adapters.

Current scope:

- read-only market data adapter interface
- in-memory registry for read-only market data adapter factories
- in-memory read-only fixture adapter for tests and local development
- fail-closed deterministic risk gateway scaffold for local message-flow tests
- no execution adapters
- no external integrations
- no network implementation
- no credentials

The fail-closed risk gateway scaffold evaluates theoretical checks and always
returns a `REJECT` `RiskDecision` with `approved_for_execution: false`.

Future adapters must remain behind these interfaces and must not bypass `deterministic-risk-gateway`. This package does not approve risk, approve execution, submit orders, or access broker/exchange trade credentials.
