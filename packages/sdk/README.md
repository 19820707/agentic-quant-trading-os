# SDK

`packages.sdk` defines internal SDK-facing interfaces for future adapters.

Current scope:

- read-only market data adapter interface
- in-memory registry for read-only market data adapter factories
- in-memory read-only fixture adapter for tests and local development
- local dry-run GitHub autonomous maintenance control-plane components
- no execution adapters
- no external integrations
- no network implementation
- no credentials

Future adapters must remain behind these interfaces and must not bypass `deterministic-risk-gateway`. This package does not approve risk, approve execution, submit orders, or access broker/exchange trade credentials.

The autonomous maintenance components are dry-run only. They do not install a
GitHub App, receive real webhooks, read tokens, call the GitHub API, create
branches, commit files, open pull requests, auto-merge, or run production
automation.
