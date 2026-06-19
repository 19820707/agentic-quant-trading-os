# Professional Trading Stack Governance

This architecture converts a tool list into a governed six-layer system. It
does not install external platforms or approve runtime connectivity.

## Six layers

| Layer | Current internal purpose | Reference technologies | Required boundary |
|---|---|---|---|
| Research and AI | Reproducible research, forecasting, walk-forward and out-of-sample evidence | Python, Jupyter, pandas, scikit-learn, PyTorch, statsmodels, TimesFM, LEAN | Produces research evidence or forecasts only |
| Data intelligence | Validated point-in-time market and alternative data | Candles, trades, order book, funding, open interest, news, on-chain, macro, volatility, correlations | Produces normalized events and governed features |
| Strategy | Versioned hypotheses and deterministic signal generation | Trend following, mean reversion, breakout, statistical arbitrage, market making, sentiment, volatility targeting | Produces non-executable signals and `OrderIntent` |
| Execution | Idempotent order lifecycle, partial fills and reconciliation | Future IBKR adapter, isolated Hummingbot reference, future venue adapters | Accepts `ApprovedOrder` only |
| Risk | Final pre-trade authority and portfolio constraints | Kill switch, drawdown, leverage, position, daily loss, circuit breakers, VaR/ES, exposure caps | Only deterministic-risk-gateway may produce `ApprovedOrder` |
| Security and operations | Credential isolation, audit, alerting and recovery | Secrets manager, IP allowlist, immutable evidence, Slack/Telegram alert adapters, backups | Never exposes credentials to models, agents or dashboards |

The named technologies are references. No dependency, external service,
credential, network path or live runtime is approved by this document.

## Canonical flow

```text
Validated data
  -> governed features
  -> research forecast
  -> versioned strategy
  -> SignalCandidate
  -> OrderIntent
  -> deterministic-risk-gateway
  -> ApprovedOrder
  -> execution-engine
  -> ExecutionReport
  -> reconciliation
  -> immutable audit evidence
```

Forbidden paths include:

- model, notebook, LLM or research engine directly to execution;
- TradingView or TrendSpider webhook directly to a broker;
- strategy directly to an exchange;
- raw `SignalCandidate` or `OrderIntent` accepted by execution-engine;
- external bot SaaS receiving platform-owned master credentials;
- any credential with withdrawal permission.

## Research discipline

Research promotion requires reproducibility, versioned datasets and models,
point-in-time lineage, leakage review, walk-forward validation and
out-of-sample evidence. Monte Carlo perturbation is required before a future
controlled-live review. A forecast is evidence, not an order.

## Strategy discipline

Strategy families are independent modules with deterministic IDs, versioned
parameters and explicit market-regime assumptions. Market making additionally
requires inventory controls; statistical arbitrage requires relationship and
breakdown monitoring; sentiment requires source provenance; volatility
targeting must respect portfolio and venue exposure caps.

No strategy owns broker credentials or execution authority.

## Execution discipline

The future execution layer must implement:

- `ApprovedOrder`-only input;
- idempotent client order IDs;
- bounded retries and rate-limit handling;
- explicit partial-fill state transitions;
- reconciliation against venue state;
- kill-switch enforcement;
- `ExecutionReport` and audit evidence for every transition.

IBKR and other broker APIs belong only behind execution-engine adapters.
Hummingbot remains an isolated external runtime reference. TradingView remains
a signal source.

## Risk discipline

Paper and future controlled-live stages require deterministic controls for:

- maximum position and notional;
- maximum leverage;
- maximum daily loss and drawdown;
- asset, venue, strategy and account exposure;
- stale data and anomalous price circuit breakers;
- liquidity, spread, slippage and price-band checks;
- VaR and expected shortfall as portfolio diagnostics;
- global and scoped kill switches.

VaR/ES complement hard limits; they never replace them.

## Security and operations discipline

Future credential-bearing integrations require trade-only keys, withdrawal
disabled, least privilege, IP allowlisting where supported, key rotation,
secrets-manager custody and isolated runtime identities. Credentials must never
enter prompts, notebooks, dashboards, logs or agent memory.

Operational readiness requires immutable evidence, redacted structured logs,
alert routing, incident response, backups, restoration tests, rollback and
human approval. Telegram or Slack are notification adapters only and must not
be command channels for trading.

## Promotion model

```text
DESIGN -> CONTRACT -> FAKE -> PAPER -> CONTROLLED_LIVE
```

The current approved maximum is `CONTRACT`. The evaluator may identify missing
gates for later stages, but it never grants credentials, network runtime or
live execution.
