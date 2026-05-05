# Roadmap

This roadmap is governed by `AGENTS.md`. The current phase is a safe scaffold only.

## Phase 0: Governance Scaffold

- Root documentation.
- Service boundaries.
- Contract folders.
- Placeholder FastAPI apps.
- Safe scripts.
- Integration catalog.
- Security scaffolding.

No trading logic, broker integration, credentials or live trading code belongs in this phase.

## Phase 1: Contracts and Schemas

- Define JSON Schemas in `packages/contracts/schemas`.
- Add schema validation tests.
- Add lifecycle identifiers for prediction, signal, order intent, risk decision, approved order, execution order, fill and audit events.

## Phase 2: Deterministic Domain Cores

- Implement deterministic domain logic behind contract boundaries.
- Keep adapters separate from domain logic.
- Add unit, contract and replay tests before integration.

## Phase 3: Simulation and Paper Readiness

- Add controlled backtesting and paper-trading flows.
- Preserve point-in-time correctness and leakage audits.
- Generate paper readiness evidence.

## Phase 4: Controlled Live Readiness

Controlled live work requires explicit instruction and promotion gates. It is not part of this scaffold.

