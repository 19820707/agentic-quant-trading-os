# Order Management

Boundary for future order lifecycle state machines.

Current state:

- local deterministic state transition validation only;
- no order submission;
- no cancel/replace;
- no exchange reconciliation;
- no live order state.

The current state machine produces audit events for lifecycle transitions, but
it does not communicate with brokers, exchanges or execution adapters.
