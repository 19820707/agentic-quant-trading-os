# Contracts

Cross-service payloads must be defined here before implementation.

JSON Schemas are the source of truth for service boundaries. No service should exchange undocumented payloads.

See `docs/architecture/schema_registry.md` for schema domains, naming, versioning, and registry rules.

Required lifecycle identifiers should be preserved where relevant:

- `trace_id`
- `correlation_id`
- `prediction_id`
- `signal_id`
- `order_intent_id`
- `risk_decision_id`
- `approved_order_id`
- `execution_order_id`
- `fill_id`
- `audit_id`

Core lifecycle contracts currently follow:

```text
OrderIntent -> RiskDecision -> ApprovedOrder -> ExecutionReport -> AuditEvent
```

The validator can verify contract shape, but it does not decide risk, approve orders, approve execution, submit orders, call services, call the network, or access broker/exchange code.

## Local Validation Utility

`packages.contracts` provides a small local loader and validator for schemas under `packages/contracts/schemas/`.

The utility validates contract format only. It does not know trading semantics, approve risk, approve execution, call services, call the network, or access broker/exchange code.

Example:

```python
from packages.contracts import ContractValidator

payload = {
    "schema_version": "0.1.0",
    "trace_id": "trace_order_intent_001",
    "correlation_id": "corr_order_intent_001",
    "order_intent_id": "intent_example_001",
    "signal_id": "sig_example_001",
    "strategy_id": "mean_reversion_paper",
    "model_version": "model_v0_1_0",
    "symbol": "BTC/USDT",
    "venue": "paper",
    "asset_class": "crypto",
    "instrument_type": "perpetual",
    "side": "BUY",
    "order_type": "LIMIT",
    "quantity": 0.5,
    "time_in_force": "GTC",
    "created_at": "2026-01-01T00:00:00Z",
    "status": "PENDING_RISK",
    "risk_required": True,
}

result = ContractValidator().validate("trading", "order_intent", payload)
assert result.valid
```

If `jsonschema` is available in the environment, the validator uses it. If not, it falls back to conservative local checks for object payloads, required fields, top-level forbidden additional properties, and top-level const values.

Limitations:

- It validates JSON-compatible payload shape, not trading intent.
- It does not decide risk.
- It does not approve orders.
- It does not approve execution.
- It does not call external services.

