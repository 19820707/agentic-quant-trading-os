# CI Quality Gates

CI quality gates provide automatic safety checks for every pull request and every push to `main`.

CI is a safety gate, not a trading runtime. CI must never place orders, call brokers, access secrets, run live integrations, or test with real exchange credentials.

## Jobs

### Scaffold Audit

Runs:

```bash
python scripts/scaffold_audit.py
```

This validates the governed scaffold and scans for prohibited implementation markers.

### Contract Tests

Runs:

```bash
python -m unittest discover -s tests -p "test_core_contract_schemas.py"
python -m unittest discover -s tests -p "test_contract_validator.py"
python -m unittest discover -s tests -p "test_contract_registry.py"
python -m unittest discover -s tests -p "test_contract_fixtures.py"
```

These checks protect JSON Schemas, the local contract validator, the schema registry, and safe fixture examples.

### Adapter Interface Tests

Runs:

```bash
python -m unittest discover -s tests -p "test_market_data_adapter_interfaces.py"
python -m unittest discover -s tests -p "test_market_data_adapter_registry.py"
```

These checks ensure market data adapter boundaries remain read-only and do not expose execution behavior.

## Security Policy

CI must not:

- use credentials or GitHub secrets
- call broker or exchange APIs
- place, cancel, modify, or simulate real orders
- install external trading libraries such as CCXT, OpenBB, Hummingbot, Trading Economics, QuestDB, or broker SDKs
- run network-dependent tests
- exercise live integrations

## Required Before Merge

Every PR should pass:

- scaffold audit
- contract tests
- adapter interface tests

Failing checks must be investigated before merge. Do not bypass CI for convenience.

## Failure Response

When CI fails:

1. Identify the failed job.
2. Reproduce the failing command locally.
3. Fix only the relevant scope.
4. Re-run the local validation.
5. Push the minimal correction.

If the failure indicates potential trading logic, broker integration, credential exposure, or risk-gateway bypass, stop and escalate for explicit review.

## Relationship To AGENTS.md

`AGENTS.md` defines the operating rules for agents and contributors. CI enforces the subset that can be checked automatically today.

## Relationship To scaffold_audit.py

`scripts/scaffold_audit.py` is the local safety scanner used by CI. It is intentionally local-only and must not call external services.
