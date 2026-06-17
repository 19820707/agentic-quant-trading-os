# Paper Trading

Local-only paper trading harness.

Current state:

- deterministic simulated fills;
- local paper account state;
- portfolio snapshots from paper fills;
- OMS lifecycle audit events;
- no exchange client;
- no broker client;
- no network;
- no credentials;
- no live trading;
- no autonomous trading loop.

The simulator only accepts an `OrderIntent` after a `RiskCheckResult` with
`APPROVE` and `approved_for_execution=true`. The deterministic risk evaluator in
this scaffold remains fail-closed by default, so this module is a harness for
future approved paper workflows, not a live execution path.

Paper fills do not imply live approval. Any future live execution still requires
separate gates, credentials policy, deterministic risk approval, kill-switch
controls and audit/reconciliation.
