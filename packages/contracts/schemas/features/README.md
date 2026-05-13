# Feature Schemas

Feature contracts define point-in-time dataset and feature lineage payloads.

Current schemas:

- `DatasetLineageRecord`: dataset version, source snapshots and required
  timestamp-field mappings.
- `LeakageReviewReport`: point-in-time and leakage review checks.

Feature contracts must preserve `event_timestamp`, `created_timestamp`,
`available_timestamp`, feature view versions, point-in-time availability and
leakage audit evidence.

Feature contracts do not approve model training, production use, risk or
execution.

