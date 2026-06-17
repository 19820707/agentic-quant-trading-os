# Portfolio

Boundary for future balances, positions, accounting and reconciliation.

Current state:

- local deterministic snapshot calculator;
- local long-only lot aggregation from fixture fills;
- side-aware local fill reducer for BUY/SELL fixtures;
- no live balances;
- no broker account reads;
- no portfolio mutation;
- no reconciliation jobs.

The current accounting module calculates local `PortfolioSnapshot` values from
in-memory inputs only. It does not connect to brokers, exchanges, databases or
market data services.
