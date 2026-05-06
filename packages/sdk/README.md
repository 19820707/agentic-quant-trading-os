# SDK

`packages.sdk` defines internal SDK-facing interfaces for future adapters.

Current scope:

- read-only market data adapter interface
- no execution adapters
- no external integrations
- no network implementation
- no credentials

Future adapters must remain behind these interfaces and must not bypass `deterministic-risk-gateway`. This package does not approve risk, approve execution, submit orders, or access broker/exchange trade credentials.
