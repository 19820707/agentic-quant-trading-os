# Backtesting

Deterministic local event-driven research backtesting.

Current state:

- local OHLCV event loop;
- strategy signal generation;
- optional `OrderIntent` creation for research only;
- deterministic risk checks through the local risk evaluator;
- optional paper fill attempts through the local paper simulator;
- no external datasets;
- no network;
- no credentials;
- no live trading;
- no production approval.

Backtest results are evidence, not approval. A backtest cannot approve paper
trading, live trading, production deployment, broker credentials, exchange
access or execution. Any future execution path must still pass through the
deterministic risk gateway and separate approval gates.
