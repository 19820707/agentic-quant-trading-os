# Feature Schemas

Feature contracts define metadata and approval gates for future feature engineering work.

Future schemas must preserve feature view versions, point-in-time availability and leakage audit evidence.

Current schemas:

- `feature_store_approval_gate.schema.json`: fail-closed approval-gate contract for future feature store work. It does not approve real feature store runtime, materialization, online serving, model training, backtesting, risk approval or execution.
- `fake_offline_materialization_review.schema.json`: review-only contract for a future fake local materialization harness. It does not approve materialization jobs, real feature store runtime, training, backtesting, risk approval or execution.

