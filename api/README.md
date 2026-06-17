# API

Local control-plane API scaffold.

Current state:

- FastAPI app factory;
- health/readiness/status payloads;
- risk status and kill-switch activation endpoint;
- kill-switch deactivation is blocked by design;
- execution status reports fail-closed adapter;
- local audit/metrics read endpoints;
- auth/RBAC placeholder only;
- no external network calls;
- no credentials;
- no live trading.

The API is a local control-plane surface, not an execution API.
