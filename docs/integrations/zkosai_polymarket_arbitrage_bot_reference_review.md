# zkOSAI Polymarket Arbitrage Bot Reference Review

## Purpose

This review identifies safe research patterns from `zkOSAI/polymarket-arbitrage-bot`.

It does not approve installing, cloning, vendoring, importing, running, or adapting the repository runtime.

Repository reviewed:

- https://github.com/zkOSAI/polymarket-arbitrage-bot

## Current Decision

zkosai_polymarket_arbitrage_bot_reference_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
npm_runtime_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
clob_runtime_allowed: false
wallet_runtime_allowed: false
settlement_allowed: false
hedge_execution_allowed: false
rpc_runtime_allowed: false

Initial classification: reference-only trend, preflight and simulation-audit source.

## Reusable Patterns

### Order Book Imbalance Observation

The repository uses order-book depth to infer trend state.

Safe adaptation:

- record depth levels
- record synthetic YES and NO bid depth
- record imbalance score
- record trend state
- keep network and execution disabled

### Trend State Observation

The repository tracks trend state transitions.

Safe adaptation:

- record previous and current trend
- record threshold
- record whether trend changed
- disallow signal authority and execution

### Trend Flip Observation

Trend flips are useful for research but dangerous as commands.

Safe adaptation:

- record from-side and to-side
- record reason
- keep switch execution disabled

### Preflight Safety Review

The repository performs live preflight checks before production execution.

Safe adaptation:

- require simulation mode
- disallow account checks
- disallow balance checks
- disallow credentials
- disallow network, production and execution

### Simulation Mode Policy

The repository separates simulation from production.

Safe adaptation:

- require simulation
- disallow production mode
- disallow live orders
- disallow settlement

### PnL Simulation Summary

PnL tracking is useful only as local simulation at this stage.

Safe adaptation:

- record period PnL
- record total PnL
- record fee and slippage estimates
- keep production approval and execution disabled

### Strategy History Event

Append-only history is useful for audit and debugging.

Safe adaptation:

- record local decision context
- record simulated result
- disallow secrets
- disallow execution

## Non-Reusable Components

Do not reuse directly:

- TypeScript or npm runtime
- live market discovery
- live order book polling
- CLOB client runtime
- signer or account runtime
- proxy account workflow
- chain RPC runtime
- balance preflight runtime
- production mode workflow
- order placement workflow
- position switch workflow
- redeem or settlement workflow
- notification runtime

## Required Internal Boundary

Any future implementation inspired by this repository must:

- remain contract-first
- use synthetic fixtures first
- avoid network calls in unit tests
- avoid credentials and environment reads
- avoid account, signer, proxy, chain RPC or settlement material
- treat trend and imbalance as untrusted research signals
- preserve trace_id and correlation_id
- emit non-executable research records only
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

This project may safely define:

- order book imbalance observation contracts
- trend state observation contracts
- trend flip observation contracts
- preflight safety review contracts
- simulation mode policy contracts
- PnL simulation summary contracts
- strategy history event contracts

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- vendoring source code
- npm runtime adoption
- live CLOB calls
- private endpoint calls
- account operations
- settlement operations
- hedge execution
- production mode
- model or agent authority to place trades

## Recommended Next Step

Review trend and preflight contracts before adding any runtime adapter or external dependency.
