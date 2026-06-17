# Adapters

Adapter boundary for future broker, exchange and external service integrations.

Current state:

- fail-closed execution adapter boundary;
- no broker SDKs;
- no exchange SDKs;
- no network clients;
- no credentials;
- no order submission.

Future adapters must remain behind explicit approval gates and the deterministic risk gateway.
