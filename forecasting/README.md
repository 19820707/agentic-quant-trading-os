# Forecasting

Forecasting engines produce numeric forecasts only.

Current TimesFM integration:

- uses the official optional package `timesfm[torch]==2.0.1`;
- targets the TimesFM 2.5 200M PyTorch API;
- does not vendor or copy the upstream repository;
- does not download checkpoints by default;
- supports a deterministic injected backend for CI and local contract tests;
- validates point-in-time context, context/horizon limits and output shape;
- never creates `Signal`, `SignalCandidate`, `OrderIntent`, `RiskDecision` or `ApprovedOrder`;
- never submits, cancels or modifies orders.

Install explicitly when model evaluation is approved:

```bash
python -m pip install -e ".[timesfm]"
```

Checkpoint downloads and remote Hugging Face access remain disabled unless an
operator explicitly enables `allow_remote_checkpoint_download`.
