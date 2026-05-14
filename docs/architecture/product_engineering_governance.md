# Product Engineering Governance

## Purpose

Product engineering governance defines how ideas, requirements, technical designs, agent instructions, implementation plans and verification evidence are recorded before code changes.

This is governance only. It does not approve prompt runtime, LLM runtime, automatic code generation, deployment, production use, trading, risk approval or execution approval.

## Current Default State

product_engineering_governance_enabled: true
prompt_runtime_allowed: false
llm_runtime_allowed: false
network_access_allowed: false
credentials_allowed: false
auto_code_generation_allowed: false
auto_build_allowed: false
auto_deploy_allowed: false
scope_expansion_allowed: false
production_enabled: false
trading_methods_allowed: false

## Contract Set

The safe contract set contains:

- `ResearchBrief`
- `ProductRequirementRecord`
- `TechnicalDesignRecord`
- `AgentInstructionPack`
- `ImplementationPlanRecord`
- `AcceptanceCriteriaRecord`
- `PlanExecuteVerifyCycle`
- `MVPBoundaryRecord`
- `AgentHandoffArtifact`
- `BuildReadinessChecklist`
- `PostBuildVerificationRecord`

## Safety Boundary

These records may describe:

- discovery evidence
- requirements
- acceptance criteria
- design choices
- intended file scope
- validation commands
- rollback plan
- handoff context
- readiness checks
- post-build verification

They must not:

- replace AGENTS.md
- call LLMs
- read credentials
- call network
- generate code automatically
- deploy services
- expand scope without review
- approve risk
- approve execution
- submit orders
- access broker or exchange systems

## Required Flow

Safe product engineering flow:

1. Create `ResearchBrief`.
2. Create `ProductRequirementRecord`.
3. Create `AcceptanceCriteriaRecord`.
4. Create `TechnicalDesignRecord`.
5. Create `MVPBoundaryRecord`.
6. Create `ImplementationPlanRecord`.
7. Check `BuildReadinessChecklist`.
8. Execute separately reviewed implementation work.
9. Record `PostBuildVerificationRecord`.
10. Capture `AgentHandoffArtifact` when context changes.

## Plan Execute Verify Rule

The implementation loop is:

1. Plan.
2. Execute the approved, bounded change.
3. Verify locally.
4. Report residual risks.
5. Stop for review.

Automatic continuation is disabled by default.

## Handoff Rule

Handoff artifacts must:

- summarize only necessary context
- reference files instead of embedding large content
- list open decisions
- confirm redaction
- exclude credentials
- remain non-executable

## Production Boundary

MVP readiness is not production readiness.

Local verification is not production approval.

A completed plan-execute-verify cycle is not risk approval or execution approval.

Any future move from governance records to automated prompt/runtime workflows requires a separate approval PR and must pass `docs/integrations/agent_runtime_approval_gate.md`.

## Non-Goals

- no prompt runtime
- no LLM runtime
- no code generation runtime
- no deployment automation
- no production approval
- no trading
- no credential handling
