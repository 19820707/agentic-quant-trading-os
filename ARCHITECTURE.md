# Architecture

This platform is an AI-native quantitative trading system scaffold with deterministic governance around risk, portfolio construction, execution, audit, and production promotion.

`AGENTS.md` is the primary operating manual for agents and governs how automated contributors must work in this repository.

## Architectural Tenets

- Modular services with explicit ownership.
- Contract-first integration between services.
- Deterministic enforcement for risk and execution.
- AI-assisted intelligence with validated downstream controls.
- Auditability across code, data, configuration, models, prompts, orders, and decisions.
- Fail-closed behavior for uncertain risk, security, or execution state.
- No direct path from AI, models, signals, dashboards, notebooks, agents or backtests to brokers or exchanges.

## Core Service Domains

- Data ingestion and quality.
- Feature engineering and research.
- Model and signal generation.
- Strategy decisioning.
- Portfolio construction.
- Deterministic risk engine.
- Deterministic execution engine.
- Compliance, audit, and evidence capture.
- Operations, observability, and incident response.

## Allowed Future Flow

The only allowed future live-capable flow is:

Market Data Engine -> Feature Engine -> Feature Store Service -> Deep Learning Engine -> Model Monitoring Service -> Signal Engine -> Order Intent Service -> Deterministic Risk Gateway -> ApprovedOrder -> Execution Engine -> Broker / Exchange -> Reconciliation -> Observability Audit Service.

This scaffold does not implement that flow. It only reserves the boundaries and placeholder services.

## Architecture References

- [Service Boundaries](docs/architecture/service_boundaries.md)
- [Integration Strategy](docs/architecture/integration_strategy.md)
- [Promotion Gates](docs/architecture/promotion_gates.md)
- [External Projects Catalog](docs/architecture/external_projects_catalog.md)
- [Engineering Discipline](docs/architecture/engineering_discipline.md)

Any change that crosses service boundaries or affects trading behavior must update the relevant architecture document.
