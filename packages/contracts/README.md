# Contracts

Cross-service payloads must be defined here before implementation.

JSON Schemas are the source of truth for service boundaries. No service should exchange undocumented payloads.

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

