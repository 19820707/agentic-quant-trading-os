# OpenDriveLab End-to-End Autonomous Driving Reference Review

## Purpose

This review identifies safe research-governance patterns from `OpenDriveLab/End-to-end-Autonomous-Driving`.

It does not approve installing, cloning, vendoring, importing, running or adapting autonomous-driving datasets, benchmarks, simulators, model code or runtime components.

Repository reviewed:

- https://github.com/OpenDriveLab/End-to-end-Autonomous-Driving

## Current Decision

opendrivelab_e2e_reference_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
dataset_download_allowed: false
benchmark_runtime_allowed: false
simulator_runtime_allowed: false
model_runtime_allowed: false
end_to_end_execution_allowed: false
network_access_allowed: false
credentials_allowed: false
trading_methods_allowed: false
production_enabled: false

Initial classification: reference-only model evaluation governance and benchmark taxonomy source.

## Reusable Patterns

### Research Taxonomy

The repository organizes end-to-end autonomous-driving research by methods, datasets, benchmarks, challenges and frontier papers.

Safe adaptation:

- model family taxonomy
- evaluation-mode taxonomy
- dataset lineage requirements
- benchmark result records
- failure-mode tracking

### Open-Loop And Closed-Loop Evaluation

The distinction between open-loop and closed-loop evaluation is useful for financial research.

Safe adaptation:

- `OPEN_LOOP` prediction evaluation without portfolio impact
- `CLOSED_LOOP_SIMULATED` replay evaluation with simulated feedback
- `PAPER_ONLY` evaluation without capital impact

### Benchmark Discipline

Autonomous-driving benchmarks highlight the risk of misleading metrics.

Safe adaptation:

- leakage checks
- lookahead-bias checks
- sample-period documentation
- cost and slippage assumptions
- calibration metrics
- drawdown and risk metrics
- reproducibility status

### Dataset Catalog Discipline

Benchmark datasets map cleanly to financial dataset governance.

Safe adaptation:

- dataset snapshot IDs
- point-in-time review
- feature lineage
- label horizon
- known data gaps

### Challenge And Leaderboard Pattern

The challenge pattern is useful internally only after strict governance.

Safe adaptation:

- internal benchmark suite
- model calibration leaderboard
- strategy replay leaderboard
- paper-only evaluation leaderboard

## Non-Reusable Components

Do not reuse directly:

- autonomous-driving datasets
- dataset download scripts
- simulator runtimes
- benchmark execution frameworks
- model training code
- pretrained model artifacts
- multimodal sensor pipelines
- end-to-end control policies
- challenge submissions
- external leaderboard integrations

## Required Internal Boundary

Any future implementation inspired by this repository must:

- remain contract-first
- use synthetic fixtures first
- avoid network calls in unit tests
- avoid credentials and environment reads
- avoid downloading datasets
- avoid model training runtime
- avoid simulators
- preserve deterministic-risk-gateway authority
- treat closed-loop results as simulation evidence only
- prevent benchmark results from granting production permission

## Safe Adaptation Targets

This project may safely define:

- model evaluation manifest contracts
- benchmark result record contracts
- evaluation failure-mode taxonomy
- open-loop versus closed-loop methodology
- dataset lineage requirements
- calibration and reproducibility fields

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- vendoring source code or paper lists
- dataset downloads
- simulator integration
- model runtime integration
- end-to-end model authority over signals, risk or execution
- production deployment based on benchmark score alone

## Recommended Next Step

Review the model evaluation governance contracts before any model runtime, dataset pipeline or benchmark harness is introduced.
