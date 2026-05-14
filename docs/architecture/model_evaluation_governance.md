# Model Evaluation Governance

## Purpose

Model evaluation governance defines how future deep-learning, forecasting, research and strategy models are evaluated before they can influence downstream workflows.

This document adopts benchmark discipline from end-to-end autonomous-driving research without adopting autonomous-driving runtime components.

## Evaluation Modes

| Mode | Meaning | Runtime permission |
| --- | --- | --- |
| `OPEN_LOOP` | Model predicts against fixed historical observations. | No portfolio feedback. |
| `CLOSED_LOOP_SIMULATED` | Model output is replayed through simulated downstream effects. | Simulation evidence only. |
| `PAPER_ONLY` | Model is evaluated in a paper environment. | No capital impact. |

## Required Evaluation Evidence

Every future model evaluation must record:

- model family
- model version
- dataset snapshot ID
- feature snapshot ID
- evaluation mode
- sample period
- label horizon
- leakage review status
- calibration metrics
- cost and slippage assumptions where applicable
- known failure modes
- reproducibility status
- approval status

## Benchmark Failure Modes

Benchmark records must explicitly track:

- data leakage
- lookahead bias
- survivorship bias
- stale data
- calibration drift
- overfitting
- cherry-picked sample periods
- missing transaction costs
- missing slippage
- unstable closed-loop feedback

## Safety Boundary

Model evaluation does not approve trading, risk, execution, production deployment, external dataset downloads, model training runtime or network access.

Evaluation results are evidence only. They cannot create `OrderIntent`, approve risk, create `ApprovedOrder`, call brokers or bypass deterministic-risk-gateway.

## Promotion Boundary

Before any model output can influence a paper or production-adjacent workflow, the system must have:

- valid evaluation contracts
- dataset lineage review
- point-in-time review
- calibration review
- replay evidence
- risk review
- human governance approval
- rollback plan
