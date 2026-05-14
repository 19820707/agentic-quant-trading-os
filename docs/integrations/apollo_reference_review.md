# Apollo Reference Review

## Purpose

This review identifies safe architecture patterns from `ApolloAuto/apollo` for a critical financial platform.

It does not approve installing, cloning, vendoring, importing, running or adapting Apollo runtime components.

Repository reviewed:

- https://github.com/ApolloAuto/apollo

## Current Decision

apollo_reference_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
apollo_runtime_allowed: false
cyber_rt_allowed: false
bazel_build_allowed: false
cpp_runtime_allowed: false
perception_runtime_allowed: false
localization_runtime_allowed: false
mapping_runtime_allowed: false
planning_runtime_allowed: false
control_runtime_allowed: false
vehicle_interface_allowed: false
sensor_stack_allowed: false
network_access_allowed: false
credentials_allowed: false
trading_methods_allowed: false
production_enabled: false

Initial classification: reference-only critical control-loop architecture source.

## Reusable Patterns

### Sense Predict Plan Control Loop

Apollo separates sensing, prediction, planning and control. The safe trading analogue is:

- market data and research observations
- probability and regime prediction
- signal and order-intent planning
- deterministic risk control
- execution only after explicit approval in a future gated path

### Typed Message Boundaries

Apollo-style module boundaries are useful as a design reference for typed messages, traceable inputs and replayable outputs.

Safe adaptation:

- JSON Schema contracts
- `trace_id`
- `correlation_id`
- explicit producer and consumer boundaries
- local replay fixtures
- audit event linkage

### Prediction Module Pattern

Apollo prediction separates scenario context, evaluation and prediction.

Safe adaptation:

- scenario classification for market regimes
- forecast evaluation
- uncertainty and confidence fields
- advisory-only probability estimates

### Planning And Control Separation

Apollo planning produces candidate trajectories, while control applies low-level authority. The trading analogue must keep signal and intent separate from risk and execution.

Safe adaptation:

- `SignalCandidate` is non-executable
- `OrderIntent` is not executable
- deterministic-risk-gateway remains final pre-trade authority
- execution engine remains the only future execution boundary

### Guardian And Monitor Pattern

Apollo-style monitor and guardian patterns map to safety monitoring for financial systems.

Safe adaptation:

- stale data guardian
- drift monitor
- kill-switch monitor
- exposure monitor
- audit monitor
- runtime health monitor

### Replay And Scenario Discipline

Autonomous driving systems rely on scenario replay and repeatable validation.

Safe adaptation:

- market replay
- signal replay
- risk decision replay
- paper execution replay
- incident reconstruction

## Non-Reusable Components

Do not reuse directly:

- Apollo runtime
- Cyber RT runtime
- Bazel build system
- C++ autonomous driving modules
- perception runtime
- localization runtime
- HD map runtime
- routing runtime
- planning runtime
- vehicle control runtime
- CanBus or vehicle interface components
- sensor stack
- Dreamview or HMI runtime
- Docker runtime for Apollo
- autonomous driving datasets or model artifacts

## Required Internal Boundary

Any future implementation inspired by Apollo must:

- remain contract-first
- preserve service boundaries
- preserve deterministic-risk-gateway authority
- keep planning separate from control
- keep prediction separate from execution
- use synthetic fixtures first
- avoid network calls in unit tests
- avoid credentials and environment reads
- avoid broker/exchange calls
- avoid runtime dependencies on Apollo components
- emit non-executable governance records only until separately approved

## Safe Adaptation Targets

This project may safely define:

- control loop mapping documentation
- control loop manifest contracts
- scenario classification contracts
- replay discipline contracts
- monitor and guardian policy contracts
- traceable module-boundary tests

## Rejected Adaptation Targets

Rejected:

- direct dependency on Apollo
- vendoring Apollo source code
- Apollo runtime services
- Cyber RT adoption
- Bazel adoption
- C++ autonomous driving runtime
- sensor or map runtime
- vehicle control patterns as executable financial control
- any path that bypasses deterministic-risk-gateway

## Recommended Next Step

Review the control-loop manifest and critical-control mapping before adding any runtime workflow inspired by autonomous systems.
