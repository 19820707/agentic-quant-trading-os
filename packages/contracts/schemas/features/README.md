# Feature Schemas

Feature contracts define point-in-time dataset and feature lineage payloads.

Current schemas:

- `DatasetLineageRecord`: dataset version, source snapshots, transformation
  identifiers, dataset window, label horizon, availability lag and temporal
  split policy.
- `LeakageReviewReport`: point-in-time, target leakage, cross-sectional
  leakage and survivorship-bias review checks.

Feature contracts must preserve `event_timestamp`, `created_timestamp`,
`available_timestamp`, feature view versions, point-in-time availability and
leakage audit evidence.

Feature contracts do not approve model training, backtesting, network access,
credentials, production use, risk or execution.

