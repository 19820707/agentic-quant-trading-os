# Trading Schemas

Placeholder for trading lifecycle contracts.

Future schemas must preserve OrderIntent, risk decision, ApprovedOrder, execution order and fill identifiers.

OrderIntent is not executable.

Current safety contracts also include execution venue capability, broker adapter safety policy, paper trading session and strategy runtime approval gates. These are governance contracts only; they do not enable broker connectivity, credentials, private endpoints or trading.

