# ML Schemas

Placeholder for model and prediction contracts.

Future schemas must preserve model version, prediction ID, confidence, freshness and validation status.

Current contracts:

- `time_series_forecast_request`: point-in-time numeric context and horizon request;
- `time_series_forecast_result`: local numeric point/quantile forecast output.

Forecast contracts are non-executable and cannot create signals, orders, risk
approvals or execution.

