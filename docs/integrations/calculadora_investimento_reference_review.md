# Calculadora Investimento Reference Review

## Purpose

This review identifies safe educational simulation patterns from `Augusto-Belussi/Calculadora_Investimento`.

It does not approve copying the Excel workbook, running Excel formulas as source of truth, adding VBA, adding spreadsheet runtime, calling market data, providing personalized financial advice, trading, risk approval, execution approval or production use.

Repository reviewed:

- https://github.com/Augusto-Belussi/Calculadora_Investimento

## Current Decision

calculadora_investimento_reference_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
xlsx_copy_allowed: false
excel_runtime_allowed: false
vba_allowed: false
market_data_allowed: false
personalized_advice_allowed: false
recommendation_allowed: false
trading_methods_allowed: false
risk_approval_allowed: false
execution_approval_allowed: false
production_enabled: false

Initial classification: reference-only educational investment scenario simulation source.

## Reusable Patterns

### Investment Scenario Input

Safe adaptation:

- capture initial capital
- capture monthly contribution
- capture static return assumption
- capture horizon
- record assumption source
- block market data and advice

### Scenario Projection

Safe adaptation:

- record total contributed
- record estimated growth
- record projected value
- record estimated monthly income
- keep results educational only

### Investor Profile Allocation

Safe adaptation:

- record conservative, moderate or growth profile
- record bucket weights
- verify total weight
- block personalized recommendations

### Long Horizon Comparison

Safe adaptation:

- compare multiple horizons
- use static assumptions
- record educational projections
- avoid real market feeds

### Assumption Sensitivity

Safe adaptation:

- compare lower, base and higher assumptions
- document sensitivity axis
- record key observation
- block recommendation authority

### Financial Education Disclaimer

Safe adaptation:

- state educational-only boundary
- state not financial advice
- state not personalized recommendation
- state not risk approval
- state not execution approval

## Non-Reusable Components

Do not reuse directly:

- Excel workbook
- screenshots or images
- spreadsheet formulas as authoritative source
- VBA automation
- profile allocations as real advice
- dividend estimates as guarantees
- real market data integrations
- deployment as financial advisory tool

## Required Internal Boundary

Any future implementation inspired by this repository must:

- remain contract-first
- use synthetic assumptions first
- avoid market data in unit tests
- avoid credentials
- avoid personalized financial advice
- avoid trading
- avoid risk approval
- avoid execution approval
- include explicit educational disclaimer
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

This project may safely define:

- investment scenario input contracts
- investment scenario projection contracts
- investor profile allocation contracts
- long horizon scenario contracts
- assumption sensitivity contracts
- financial education disclaimer contracts

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- copying the workbook
- using Excel runtime
- adding VBA
- adding real market data
- generating personalized advice
- recommending investments
- producing trade instructions
- approving risk
- approving execution

## Recommended Next Step

Review the educational simulation contracts before considering any local calculator implementation.
