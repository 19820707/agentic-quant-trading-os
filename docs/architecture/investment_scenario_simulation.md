# Investment Scenario Simulation

## Purpose

Investment scenario simulation records educational, deterministic assumptions and projections for long-horizon planning examples.

This is not financial advice, not a recommendation engine, not a portfolio optimizer, not a trading strategy, not risk approval and not execution approval.

## Current Default State

investment_scenario_contracts_enabled: true
calculator_runtime_allowed: false
xlsx_runtime_allowed: false
vba_allowed: false
market_data_allowed: false
personalized_advice_allowed: false
recommendation_allowed: false
trading_methods_allowed: false
risk_approval_allowed: false
execution_approval_allowed: false
production_enabled: false

## Contract Set

The safe contract set contains:

- `InvestmentScenarioInput`
- `InvestmentScenarioProjection`
- `InvestorProfileAllocation`
- `LongHorizonScenarioSet`
- `AssumptionSensitivityReport`
- `FinancialEducationDisclaimer`

## Safety Boundary

These records may describe:

- static assumptions
- monthly contributions
- long-horizon projections
- scenario comparisons
- educational profile buckets
- sensitivity observations
- disclaimer state

They must not:

- use real market data without a separate adapter approval
- provide personalized financial advice
- recommend assets
- create signals
- create order intents
- approve risk
- approve execution
- submit orders
- access broker or exchange systems

## Calculation Boundary

Any future local calculator must:

- use deterministic local arithmetic
- accept only explicit input assumptions
- avoid network access
- avoid credentials
- emit educational results only
- include `FinancialEducationDisclaimer`
- keep recommendation and execution flags false

## Profile Boundary

Investor profiles are educational buckets only.

They are not suitability assessments, not individualized advice and not permission to trade.

## Production Boundary

Educational projections are not backtests.

Backtests are not production approval.

Scenario outputs must never bypass deterministic-risk-gateway or create execution authority.

## Non-Goals

- no Excel workbook ingestion
- no VBA
- no spreadsheet runtime
- no market data integration
- no personalized advice
- no trade recommendations
- no production use
- no broker or exchange integration
