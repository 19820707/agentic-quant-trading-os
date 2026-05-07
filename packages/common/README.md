# Common

`packages.common` contains shared value objects used across internal package boundaries.

Current scope:

- read-only market data request and response value objects
- standard-library-only dataclasses
- no services
- no broker or exchange execution
- no credentials
- no network calls

These objects describe data shape only. They do not place orders, decide risk, approve execution, or connect to external systems.

## Security Utilities

`packages.common.security` provides local-only redaction helpers for nested dictionaries, lists, tuples and scalar values before logging, audit events, reports, errors or debugging output.

The redaction helpers:

- do not call network
- do not access credentials
- do not read environment variables
- do not access files
- do not validate or store secrets
- do not replace Vault, Infisical, SOPS or another managed secret system

Withdrawal keys must never be used. If a withdrawal-related key appears in diagnostic data, it must be redacted before the data reaches logs, reports, audit events or prompts.
