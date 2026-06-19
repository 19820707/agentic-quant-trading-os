# Institutional External Platform Due Diligence

This review separates product capability from integration approval. Official
documentation can prove that a platform exposes a feature; it cannot prove
strategy profitability, operational fitness or approval for this repository.

## Decision matrix

| Platform | Primary role | Operating model | Current priority | Critical caveat |
|---|---|---|---|---|
| QuantConnect / LEAN | Research and backtest engine | Local/cloud engine | Research reference | Brokerage models do not prove live fill equivalence |
| Interactive Brokers | Institutional multi-asset broker API | TWS/IB Gateway or Web API session | Deferred execution adapter | Gateway lifecycle, sessions, pacing and market-data permissions |
| Alpaca | Developer broker API | Cloud API | Paper adapter candidate | Paper fills omit important live liquidity effects |
| NinjaTrader | Futures strategy terminal | Desktop terminal | Isolated runtime review | NinjaScript, ATM and ATI have different semantics |
| TradeStation | Traditional multi-asset API | Cloud REST/streaming API | Paper adapter candidate | SIM instant fills and LIVE must remain strictly separated |
| MetaTrader 5 | Forex/CFD terminal | Desktop terminal | Isolated runtime review | Broker-specific symbols, fills and CFD behavior |
| cTrader | Forex/CFD API and terminal | OAuth cloud API / terminal | Isolated runtime review | Broker-specific capability and token boundaries |
| Hummingbot | Crypto strategy runtime | External connector runtime | Isolated runtime review | Strategies create and refresh orders autonomously |
| TradingView | Signal source | Cloud webhook | Signal contract only | Webhook delivery is not execution authorization |

## Evidence standard

Claims in the typed catalog use official platform documentation. Comparative
blogs, affiliate rankings, marketplace claims and vendor-labelled AI features
are not accepted as evidence of safety or expected return.

The catalog records:

- primary role rather than marketing category;
- deployment and authentication model;
- paper/simulation model;
- integration priority;
- operational caveats;
- mandatory controls;
- official evidence URLs.

## Corrected classification

### QuantConnect / LEAN

Best treated as a research and backtesting reference. LEAN brokerage models
represent fees, leverage, settlement and supported order behavior. They improve
realism but cannot prove live fill equivalence. Live brokerage routing is not
part of the research trust boundary.

### Interactive Brokers

An institutional execution candidate, not a research runtime. TWS API requires
TWS or IB Gateway; Web API adds authorization, brokerage-session and pacing
constraints. A future adapter requires gateway supervision, session recovery,
rate budgets and reconciliation.

### Alpaca

A practical first paper-adapter candidate because paper and live expose similar
workflows. The official documentation warns that paper trading does not model
all market impact, queue position and liquidity effects. Paper/live endpoint
separation must be structural, not a mutable string selected by a strategy.

### NinjaTrader

A futures strategy and terminal ecosystem. NinjaScript automated strategies,
ATM position-management templates and ATI external-signal processing are
different mechanisms. ATI is explicitly not a full brokerage or market-data
API. Any future integration needs a terminal boundary and OMS reconciliation.

### TradeStation

A traditional multi-asset API for stocks, options and futures with market-data
streaming and order endpoints. SIM uses a distinct base URL and simulated
instant fills. OAuth trade scopes and refresh-token behavior require
least-privilege and rotation review.

### MT5 and cTrader

Useful forex/CFD references, but broker-specific contract, leverage, symbol and
fill semantics are material. Expert Advisors and cBots are independent runtimes
that must not bypass internal risk or own platform credentials.

### Hummingbot

Useful for connector, market-making and arbitrage semantics. It is an external
execution runtime, not a library to embed casually. Connector source review,
process isolation and independent risk limits are mandatory.

### TradingView

Signal transport only. Alerts may become validated `SignalCandidate` records.
They never become `OrderIntent` or broker calls directly.

## Non-negotiable integration boundary

```text
research/model/signal
  -> SignalCandidate
  -> OrderIntent
  -> deterministic-risk-gateway
  -> ApprovedOrder
  -> execution-engine adapter
  -> broker or exchange
  -> ExecutionReport
  -> reconciliation and audit
```

Every platform remains reference-only. No SDK, credential, account, network
runtime, paper endpoint or live endpoint is enabled by this review.

## Official references

- QuantConnect brokerage models: <https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/brokerages/key-concepts>
- QuantConnect supported models: <https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/brokerages/supported-models>
- IBKR TWS API: <https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/>
- IBKR Web API: <https://ibkrcampus.com/campus/ibkr-api-page/webapi-doc/>
- Alpaca paper trading: <https://docs.alpaca.markets/us/docs/paper-trading>
- Alpaca Trading API: <https://docs.alpaca.markets/us/docs/trading-api>
- NinjaTrader help guide: <https://ninjatrader.com/support/helpguides/nt8/>
- NinjaTrader ATI: <https://ninjatrader.com/support/helpguides/nt8/automated_trading_interface_at.htm>
- TradeStation API: <https://api.tradestation.com/docs/>
- TradeStation SIM vs LIVE: <https://api.tradestation.com/docs/fundamentals/sim-vs-live/>
- TradeStation OAuth scopes: <https://api.tradestation.com/docs/fundamentals/authentication/scopes/>
- MetaTrader 5: <https://www.mql5.com/en/docs>
- cTrader authentication: <https://help.ctrader.com/open-api/account-authentication/>
- Hummingbot: <https://hummingbot.org/>
- TradingView webhooks: <https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/>
