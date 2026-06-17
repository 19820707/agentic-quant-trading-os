# SDK

`packages.sdk` defines internal SDK-facing interfaces for future adapters.

Current scope:

- read-only market data adapter interface
- in-memory registry for read-only market data adapter factories
- in-memory read-only fixture adapter for tests and local development
- deterministic autonomous sprint planning
- deterministic deep learning loop mission planning
- deterministic cognitive autonomy diagnostics
- deterministic advanced cognitive autonomy diagnostics
- deterministic persistence discipline governance
- deterministic loop engineering governance
- no execution adapters
- no external integrations
- no network implementation
- no credentials

Future adapters must remain behind these interfaces and must not bypass `deterministic-risk-gateway`. This package does not approve risk, approve execution, submit orders, or access broker/exchange trade credentials.

`cognitive_autonomy` is local diagnostics only. It provides consensus,
calibration, fractal, stability and self-healing planning signals without LLM
runtime, external model calls, network access, credentials or trading authority.

`deep_learning_loop_planner` generates as many deep-learning governance
missions as requested within an explicit `max_missions` limit. It creates
contract-first work for lineage, leakage review, fake materialization review,
model cards, training-run metadata, evaluation, calibration, monitoring and
deployment gates. It does not train models, import ML frameworks, serve models,
call network, read credentials, generate trading signals, create order intents,
approve risk or approve execution.

`cognitive_autonomy_advanced` extends the local-only diagnostics with neural
activation stability checks, collective-intelligence resilience, reliability
buckets, physics-style stress diagnostics, scientific validity checks and
evidence-based self-healing plans. It remains fail-closed: no model training,
LLM runtime, network access, credentials, file mutation, risk approval,
execution approval or trading authority is granted.

`loop_engineering` is a local autonomous-control loop for observe -> diagnose
-> plan -> policy verify -> evidence -> review. It never edits files, opens
pull requests, merges, calls network, reads credentials, approves risk or
enables execution.

`persistence_discipline` turns persistence into measurable engineering rules:
repeat small evidenced progress, reduce scope on evidence gaps, require review
on regressions, and block after repeated unresolved blockers. It does not
approve remediation, runtime changes, network access, credentials, risk,
execution or trading.

Loop run reports can be appended to the local evidence journal as
`LOOP_RUN_REPORT` records, producing tamper-evident audit history without a
database, external service or runtime permission escalation.
