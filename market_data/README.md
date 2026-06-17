# Market Data

Local market data abstraction layer for normalized events, deterministic mock
streams, local replay and storage hooks.

Current state:

- no live feeds;
- no exchange connectivity;
- no WebSocket clients;
- no paid data entitlements;
- no background ingestion;
- no credentials.

Implemented boundaries:

- `MarketDataAdapter` protocol;
- deterministic `MockMarketDataAdapter`;
- local-file `ReplayMarketDataAdapter`;
- event normalization into `packages.domain` models;
- heartbeat/staleness state;
- reconnect policy model;
- rate-limit policy model;
- in-memory and JSON-lines writer hooks.

The streaming abstraction is local iterator based in this phase. Real REST
polling, WebSocket streaming, external storage and exchange adapters require
separate approval gates.
