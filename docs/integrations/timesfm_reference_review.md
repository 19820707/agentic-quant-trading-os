# TimesFM Reference Review

## Source

- Repository: <https://github.com/google-research/timesfm>
- Package: `timesfm`
- Reviewed package version: `2.0.1`
- Current model family: TimesFM 2.5, 200M parameters
- Default model identifier: `google/timesfm-2.5-200m-pytorch`
- License: Apache-2.0
- Upstream status: open research release, not an officially supported Google product

## Integration decision

TimesFM is integrated as an optional forecasting dependency, not vendored source.

```text
Historical point-in-time series
  -> TimeSeriesForecastRequest
  -> TimesFMForecastEngine
  -> TimeSeriesForecastResult
  -> evaluation/calibration
  -> future SignalCandidate conversion
```

TimesFM is not allowed to create signals, orders, risk approvals or execution
requests directly.

## Runtime controls

- The optional package is pinned as `timesfm[torch]==2.0.1`.
- TimesFM runtime is disabled by default.
- Import happens only inside `create_timesfm_engine`.
- Remote checkpoint download is disabled by default.
- A local checkpoint path must exist unless remote download is explicitly enabled.
- CI and unit tests use a deterministic injected backend.
- No credentials or environment-variable reads are required.
- No broker, exchange or market-data network access is part of this integration.

## Financial-model limitations

TimesFM forecasts numeric sequences. It does not establish profitability,
causality or market edge. Before a forecast can influence a strategy it requires:

- point-in-time lineage and leakage review;
- walk-forward and out-of-sample evaluation;
- MASE, sMAPE, RMSE and directional-accuracy reporting;
- calibration and quantile-coverage review;
- regime and drift monitoring;
- benchmark comparison against simple statistical baselines;
- deterministic risk review after any later signal conversion.

## Explicit non-goals

- no checkpoint downloaded by this PR;
- no fine-tuning or model training;
- no Hugging Face token;
- no real market-data ingestion;
- no automatic signal creation;
- no `OrderIntent`, `ApprovedOrder` or `ExecutionReport` creation;
- no broker/exchange access;
- no trading execution.
