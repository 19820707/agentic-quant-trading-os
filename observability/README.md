# Observability

Local-only observability scaffold for logs, metrics, traces and audit timelines.

Current state:

- in-memory structured logs;
- in-memory counters and gauges;
- audit event collection;
- local JSONL evidence journal with hash-chain verification;
- trace reports by correlation id;
- sensitive attribute redaction;
- no OpenTelemetry exporters;
- no Prometheus endpoint;
- no external alert hooks;
- no sockets;
- no network;
- no credentials.

This module is intentionally local. It gives strategy, risk, OMS, paper trading
and backtesting code a common evidence surface before any external monitoring
system is approved.

The evidence journal is append-only by convention and tamper-evident by hash
chain verification. It is suitable for local tests, development evidence and
future control-plane review workflows. It is not a production audit store yet.
