# Engineering Evidence Index

## Purpose

This index links research, requirements, design, contracts, verification, safety boundaries, rollback evidence, and pull-request decisions into one auditable engineering chain.

The repository is still contract-first and fail-closed. This document does not enable runtime automation, trading, broker access, network access, background workers, or autonomous code modification.

## Evidence discipline

Every material pull request should be traceable across the following dimensions:

| Dimension | Required evidence |
|---|---|
| Research | Reference source, local review, explicit non-vendoring boundary |
| Requirements | Requirement record or acceptance criteria |
| Design | Technical design record, architecture note, or governance contract |
| Contracts | JSON schema, fixture, or registry entry where applicable |
| Verification | Unit tests, static checks, scaffold audit, secret audit, JSON validation |
| Safety | Forbidden behavior, fail-closed defaults, protected paths, human approval gates |
| Rollback | Revert strategy and scope of impact |
| Decision | PR status, reviewer decision, exception record, merge rationale |

## Current evidence map

| PR | Area | Evidence class | Safety boundary | Verification evidence | Status |
|---|---|---|---|---|---|
| #68 | Agent runtime approval gate | Runtime governance | No runtime agents, MCP runtime, tools, network, credentials, broker/exchange, trading, risk approval, execution approval, or production use | Local unit tests, py_compile, JSON validation, scaffold audit, secret artifact audit, environment check | Merged |
| #70 | Product engineering discipline contracts | Research → requirements → design → plan → verify discipline | No LLM runtime, prompt runtime, automatic generation, automatic build/deploy, production promotion, trading, risk approval, or execution approval | Local tests and static validation reported in PR body | Open / review candidate |
| #71 | Investment scenario simulation contracts | Educational financial simulation contracts | No real market data, personalized financial advice, signals, order intents, trading methods, risk approval, or execution approval | Local tests and static validation reported in PR body | Open / draft |
| #72 | Agent memory governance contracts | Local-only memory governance | No storage runtime, embeddings, MCP runtime, dashboard, network access, credentials, trading, broker integration, risk approval, or execution approval | Local tests and static validation reported in PR body | Open / draft |
| #73 | Capability maturity traceability gates | Capability maturity and forbidden runtime states | No runtime implementation, trading logic, broker/exchange calls, credentials, network behavior, or external dependencies | Local tests, scaffold audit extension, static validation | Open / draft |
| #74 | Apollo control-loop governance contracts | Autonomous systems control-loop reference | No Apollo runtime, vehicle stack, network, credentials, broker/exchange calls, trading logic, risk approval, or execution approval | Local tests and static validation reported in PR body | Open / draft |
| #75 | E2E model evaluation governance contracts | Model evaluation governance | No datasets, simulators, training runtime, pretrained artifacts, benchmark execution, network, credentials, trading logic, risk approval, or execution approval | Local tests and static validation reported in PR body | Open / draft |
| #76 | Safe RL governance contracts | Constraint-first RL safety governance | No RL frameworks, training loops, simulators, checkpoints, multi-agent RL runtime, network, credentials, broker/exchange calls, trading logic, risk approval, execution approval, or production enablement | Local tests and static validation reported in PR body | Open / draft |
| #77 | GitHub autonomous maintenance governance contracts | Future maintenance-agent control plane | No GitHub App, webhook receiver, repository write token, automatic branch/commit/PR creation, auto-merge, LLM runtime, network calls, credentials, trading, broker, exchange, risk, or execution changes | Local tests and static validation reported in PR body | Open / draft |

## Required PR evidence record

Each PR should include or link to an evidence record containing:

```yaml
pr: 0
title: ""
area: ""
change_class: "documentation | contract | test | runtime | infrastructure"
risk_level: "low | medium | high | critical"
safety_boundary:
  forbidden:
    - ""
requirements:
  - id: "REQ-000"
    statement: ""
design:
  - id: "DES-000"
    artifact: ""
contracts:
  - schema: ""
    fixture: ""
verification:
  local:
    - "python -m unittest discover -s tests"
    - "python -m py_compile ..."
    - "python scripts/scaffold_audit.py"
    - "python scripts/secret_artifact_audit.py"
  remote:
    status: "passed | failed | blocked | not_run"
    exception: ""
rollback:
  strategy: "git revert <merge_commit> or close unmerged PR"
  impact: ""
decision:
  status: "draft | review | merged | rejected"
  rationale: ""
```

## Remote check exception policy

If GitHub Actions checks fail immediately because of the known Actions/billing restriction, the PR may still proceed only when all conditions are true:

1. The failure is classified as infrastructure/billing-related, not implementation-related.
2. Local validation evidence is explicitly recorded in the PR body.
3. The PR does not modify runtime trading, broker, exchange, risk, execution, credentials, or autonomous write paths.
4. The safety boundary is explicit and fail-closed.
5. Rollback is straightforward through PR closure or commit revert.

## Promotion rule

A contract-only PR can only promote toward runtime when a future PR provides:

- implementation design;
- threat model;
- policy gate;
- test harness;
- rollback plan;
- audit event model;
- protected-path review;
- explicit human approval.

Until then, all reference integrations remain research/governance inputs only.
