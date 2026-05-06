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
