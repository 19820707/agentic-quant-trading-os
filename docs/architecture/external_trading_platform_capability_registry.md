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
