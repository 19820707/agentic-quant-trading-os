# Feature Schemas

Feature contracts define point-in-time feature metadata and join plans.

Current schemas:

- `FeatureViewContract`: feature view name, version, entity keys, feature list
  and timestamp field requirements.
- `PointInTimeJoinPlan`: safe join plan that blocks future-data joins and
  requires leakage review.

Future schemas must preserve feature view versions, point-in-time availability
and leakage audit evidence.

Feature contracts do not materialize features, train models, approve production
use, approve risk or approve execution.

