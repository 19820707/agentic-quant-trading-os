# Trading Schemas

Placeholder for trading lifecycle contracts.

Future schemas must preserve OrderIntent, risk decision, ApprovedOrder, execution order and fill identifiers.

OrderIntent is not executable.

`trading_runtime_activation_gate` records fail-closed runtime activation decisions. It does not enable backtesting, paper trading, live trading, broker SDKs, exchange SDKs, network access, credentials or execution.

`backtest_review_contract` records evidence required before any future local deterministic backtest runtime work. It does not enable strategy execution, market data ingestion, paper trading, broker or exchange access, credentials, risk approval or execution.

