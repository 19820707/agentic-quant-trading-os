# ML Schemas

ML schemas define model evaluation and prediction governance contracts.

Future schemas must preserve model version, prediction ID, confidence, freshness and validation status.

`ModelEvaluationManifest` defines model family, dataset lineage, evaluation
mode, leakage review, calibration requirements and fail-closed runtime flags.

`BenchmarkResultRecord` captures benchmark metrics, reproducibility status and
failure modes. Benchmark evidence must not approve risk, execution or production
use by itself.

