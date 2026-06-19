# External Trading Platform Capability Registry

The registry turns external-platform evaluation into deterministic architecture
data. It does not install or run any external trading platform.

## Platform boundaries

| Platform | Category | Required boundary | Current stage |
|---|---|---|---|
| QuantConnect / LEAN | research/backtesting engine | research sandbox | CONTRACT |
| Interactive Brokers API | execution broker API | execution-engine only | CONTRACT |
| Hummingbot | crypto strategy runtime | isolated strategy sandbox | REFERENCE |
| TradingView Alerts | signal source | signal intake only | CONTRACT |
| MetaTrader 5 | forex/CFD terminal | terminal adapter boundary | REFERENCE |
| cTrader Open API / Algo | forex/CFD platform | terminal adapter boundary | REFERENCE |
| 3Commas | commercial crypto bot SaaS | external SaaS reference | REFERENCE |
| Cryptohopper | commercial crypto bot SaaS | external SaaS reference | REFERENCE |
| Pionex | exchange-native bot | exchange-native automation | REFERENCE |
| Coinrule | commercial crypto bot SaaS | external SaaS reference | REFERENCE |
| Bitsgap | commercial crypto bot SaaS | external SaaS reference | REFERENCE |
| TradeSanta | commercial crypto bot SaaS | external SaaS reference | REFERENCE |
| WunderTrading | commercial crypto bot SaaS | external SaaS reference | REFERENCE |
| TrendSpider | technical-analysis automation | signal intake only | CONTRACT |

## Operational model

The registry supports these promotion stages:

```text
REFERENCE -> CONTRACT -> FAKE -> PAPER -> CONTROLLED_LIVE
```

Development is deliberately permissive in the first four stages:

- architecture/reference review;
- internal contracts;
- fake adapters and deterministic failure tests;
- local paper simulation and reconciliation replay.

Controlled-live requests derive additional gates for credential vaulting,
network approval, human approval, rollback and incident response. The assessment
itself never grants those capabilities.

## Routing rules

- LEAN belongs in research/backtest isolation. Its brokerage routing is not an
  internal execution path.
- IBKR belongs only inside a future execution-engine adapter and requires TWS or
  IB Gateway health/session recovery.
- Hummingbot contains direct order-management strategies and must remain process
  isolated. Strategy logic may be studied independently.
- TradingView webhooks become validated `SignalCandidate` inputs only. TradingView
  explicitly warns against putting credentials in webhook URLs or payloads.
- MT5 Expert Advisors and ONNX inference remain inside a terminal boundary.
- cTrader Open API uses OAuth 2.0 and supports trading/account operations, so its
  tokens may only exist inside a future approved adapter boundary.
- Commercial bot SaaS products are external execution systems, not trusted
  internal strategy engines. Their grid, DCA, copy and no-code semantics may be
  studied, but their credentials and order authority remain outside this
  repository.
- Pionex bots execute inside an exchange-native boundary. They cannot be treated
  as an internal adapter or as evidence that a strategy is safe.
- TrendSpider alerts follow the same signal-intake rule as TradingView:
  authenticated, replay-protected payloads may become `SignalCandidate`; they
  never become orders.

## Commercial automation safety model

Commercial automation is useful as a source of product semantics:

- grid range, inventory and active-order controls;
- DCA safety-order and aggregate-position limits;
- copy-source provenance, latency and independent risk limits;
- deterministic translation of no-code rules;
- trailing-order semantics;
- demo/paper workflow and emergency bot-stop design.

It is not an approved runtime. Any future evaluation must prove:

- vendor security, incident response and data-retention posture;
- isolated capital subaccounts;
- trade-only keys with withdrawal disabled;
- IP allowlisting where the vendor supports it;
- key rotation and credential-scope review;
- rate-limit, maximum-order and maximum-notional controls;
- deterministic-risk-gateway and `ApprovedOrder` enforcement;
- reconciliation, kill switch, rollback and audit evidence.

Marketplace strategies, copy leaders and vendor-labelled "AI" settings are
untrusted inputs. They require independent validation and never inherit trading
authority from the vendor platform.

Any execution-capable integration must preserve:

```text
SignalCandidate
  -> OrderIntent
  -> deterministic-risk-gateway
  -> ApprovedOrder
  -> execution-engine adapter
  -> ExecutionReport
  -> reconciliation and audit
```

## Official references

- QuantConnect / LEAN: <https://www.quantconnect.com/docs/v2/>
- IBKR TWS API: <https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/>
- Hummingbot: <https://hummingbot.org/>
- TradingView webhooks: <https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/>
- MetaTrader 5 / MQL5: <https://www.mql5.com/en/docs>
- cTrader Open API: <https://help.ctrader.com/open-api/>
- 3Commas: <https://help.3commas.io/en/articles/4430555-all-about-3commas-features-tools-history-and-benefits>
- Cryptohopper: <https://docs.cryptohopper.com/docs/how-to-connect>
- Pionex: <https://www.pionex.com/blog/category/trading-bots/>
- Coinrule: <https://help.coinrule.com/articles/711711-what-is-coinrule>
- Bitsgap: <https://bitsgap.com/crypto-trading-bot/dca-bot>
- TradeSanta: <https://tradesanta.com/setting-up-bots>
- WunderTrading: <https://wundertrading.com/en>
- TrendSpider: <https://help.trendspider.com/kb/alerts/webhooks>
