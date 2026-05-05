# AGENTS.md

Agentic Quant Trading OS is a critical, auditable, modular and governed AI-native quantitative trading platform for real assets.

This is not a trading bot.

Core principle:

AI proposes.
Models predict.
Risk Gateway decides.
Execution Engine executes.
Audit proves.
Human governance supervises.

## Operating Mode

- Work in small, explicit phases.
- Do not expand scope beyond the current task.
- Do not implement features that were not requested.
- Do not install dependencies unless explicitly requested.
- Do not clone external repositories unless explicitly requested.
- Do not add Git submodules unless explicitly requested.
- Do not vendor external code.
- Do not perform broad refactors unless explicitly requested.
- Do not rewrite existing files unless necessary.
- Prefer creating minimal, safe placeholders over large speculative implementations.
- Stop after completing the requested step and summarize what changed.

## Token Discipline

- Read only the files needed for the current task.
- Do not scan the entire repository unless the task requires it.
- Do not print large file contents unless asked.
- Do not repeat long architecture text in every response.
- Use concise summaries.
- Keep generated files focused and non-redundant.
- Avoid duplicating the same rules across many files unless required.
- For large tasks, propose a phased plan instead of doing everything at once.
- If a task is too broad, implement the smallest safe useful subset and report what remains.

## Required Workflow

For every task:

1. Read this AGENTS.md.
2. Identify the task scope.
3. List the files you expect to touch.
4. Make the minimal changes needed.
5. Do not add unrelated improvements.
6. Run only relevant checks if available.
7. Report:
   - files changed
   - what was done
   - what was intentionally not done
   - next recommended step

## Stop Conditions

Stop and ask for explicit instruction if the task would require:

- live trading logic
- broker/exchange order submission
- real API credentials
- cloning external repositories
- installing major dependencies
- adding Git submodules
- bypassing the Risk Gateway
- giving agents execution permission
- changing critical safety rules
- large architectural rewrites
- deleting audit/security files
- modifying secrets or credential paths

## Non-Negotiable Safety Rules

- AI, LLM agents, notebooks, dashboards, research services and model services must never send orders directly to a broker or exchange.
- Deep Learning Engine only produces predictions.
- Signal Engine only produces normalized signals.
- Order Intent Service only creates OrderIntent objects.
- OrderIntent is not executable.
- Deterministic Risk Gateway is the final pre-trade authority.
- Execution Engine is the only service allowed to access live broker/exchange trading credentials in a future controlled-live implementation.
- No component may bypass the Deterministic Risk Gateway.
- Backtest approval never means live approval.
- Paper trading is mandatory before controlled live trading.
- Secrets must never be committed, logged, exposed to agents, exposed to dashboards, exposed in prompts, or passed to model services.
- Broker/exchange withdrawal permissions must never be used.
- Agentic tools must not execute trades.

## Allowed Future Flow

Market Data Engine
-> Feature Engine
-> Feature Store Service
-> Deep Learning Engine
-> Model Monitoring Service
-> Signal Engine
-> Order Intent Service
-> Deterministic Risk Gateway
-> ApprovedOrder
-> Execution Engine
-> Broker / Exchange
-> Reconciliation
-> Observability Audit Service

Any direct path from AI, model, signal, dashboard, notebook, agent or backtest to broker/exchange is forbidden.

## Contract-First Rule

- Define or update contracts before implementing cross-service behavior.
- JSON Schemas live under `packages/contracts/schemas/`.
- Cross-service payloads must include `trace_id` and `correlation_id` where relevant.
- Do not exchange undocumented payloads.

## Testing Rule

- Add tests for non-trivial behavior.
- Feature and dataset code requires point-in-time and leakage tests.
- Trading/risk/execution code requires replay tests.
- Contract changes require schema validation tests.
- No test may require real broker credentials.
- No test may place real orders.

## External Integration Rule

- External projects are cataloged before integration.
- Integrate through adapters, wrappers, package dependencies, Docker services or reference-only docs.
- Do not copy external repositories into this repo.
- Do not install external dependencies unless the task explicitly asks.
- No external project may bypass deterministic-risk-gateway.
- MCP tools must never receive broker credentials.
- FIX engines must only be integrated inside execution-engine adapters.

## Documentation Rule

Update documentation only when relevant to the current change.

Prefer linking to existing docs instead of duplicating long explanations.

## Current Phase Discipline

Until explicitly changed, assume the project is in scaffold/research-only phase.

Therefore:

- no live trading
- no broker submission
- no real credentials
- no autonomous execution
- no production deployment
- placeholders are preferred over speculative implementations

