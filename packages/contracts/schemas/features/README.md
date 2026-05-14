# Feature Schemas

Feature contracts define metadata and approval gates for future feature engineering work.

Future schemas must preserve feature view versions, point-in-time availability and leakage audit evidence.

Current schemas:

- `feature_store_approval_gate.schema.json`: fail-closed approval-gate contract for future feature store work. It does not approve real feature store runtime, materialization, online serving, model training, backtesting, risk approval or execution.

