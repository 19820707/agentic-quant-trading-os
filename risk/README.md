# Risk

Boundary for deterministic risk controls.

Current state:

- local deterministic pre-trade risk evaluator;
- fail-closed decision posture: clean checks return `REVIEW`, not execution approval;
- no live approvals;
- no execution approval;
- no production runtime.

Implemented local checks:

- kill switch;
- stale price reference;
- max order notional;
- price band;
- minimum liquidity;
- projected symbol exposure;
- projected venue exposure;
- projected gross exposure;
- projected leverage;
- open order count;
- order rate;
- daily loss;
- drawdown.

Runtime activation:

- `trading_runtime_gate` evaluates requests to move toward backtest, paper, controlled-live or production modes;
- the gate is executable and auditable, but remains fail-closed;
- broker SDKs, exchange SDKs, credentials, network access, order submission, order cancellation and live trading are always denied in the current phase;
- every future execution path must still require deterministic risk review, `ApprovedOrder`, execution-engine isolation and audit evidence.
