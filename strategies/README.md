# Strategies

Local-only strategy research scaffolds.

Current guarantees:

- strategies emit `Signal` objects only;
- strategies do not create `OrderIntent`;
- strategies do not submit, cancel, edit or execute orders;
- strategies do not read credentials;
- strategies do not call network;
- live trading is not supported by this module.
- local strategy modes support research, backtest and paper signal generation without broker access.

Included research examples:

- moving average crossover;
- mean reversion;
- volatility breakout;
- grid research, local-only and still signal-only;
- inventory-aware market making, local-only and still signal-only.

Portfolio allocation:

- `StrategyPortfolioAllocator` combines weighted local strategy signals for one symbol/venue;
- it produces an `AllocatedSignalCandidate`, not an `OrderIntent`;
- it detects low confidence, HOLD/unweighted inputs and strategy conflict;
- it sets `order_intent_allowed: false` and `execution_allowed: false`;
- it exposes no broker, exchange, order submission, cancellation or credential methods.

Backtests, research signals and paper-only observations do not imply live approval.
Any future path from signal to order must pass through the deterministic risk gateway.

