# Multi-Model Review Governance

## Purpose

Multi-model review governance defines how future model-assisted review, debate and consensus workflows must be controlled before any runtime provider integration is considered.

This is governance only. It does not approve model calls, provider setup, network access, credentials, MCP runtime, plugin runtime, automatic remediation, production use, risk approval or execution approval.

## Current Default State

multi_model_review_runtime_allowed: false
provider_runtime_allowed: false
model_calls_allowed: false
network_access_allowed: false
credentials_allowed: false
mcp_runtime_allowed: false
plugin_runtime_allowed: false
reaction_engine_runtime_allowed: false
auto_fix_allowed: false
auto_merge_allowed: false
trading_methods_allowed: false
production_enabled: false

## Contract Set

The safe contract set contains:

- `MultiModelReviewPlan`
- `ConsensusGateRecord`
- `AdversarialDebateRecord`
- `AgentStatusLedger`
- `ProviderCapabilityPolicy`
- `ReactionEnginePolicy`
- `PhaseQualityGate`
- `PromptPreflightPolicy`
- `SecurityReviewWorkflowRecord`

## Safety Boundary

These records may describe:

- planned reviewer roles
- advisory consensus
- dissent and unresolved risks
- phase readiness
- provider capability policy
- prompt safety preflight
- security review findings
- manual triage state

They must not:

- call external models
- activate provider CLIs
- install plugins
- start MCP servers
- read credentials
- call network
- automatically patch code
- automatically merge PRs
- approve risk
- approve execution
- submit orders
- access broker or exchange systems

## Review Flow

Safe future review flow:

1. Create a `MultiModelReviewPlan`.
2. Run local/static checks only.
3. Capture structured debate in `AdversarialDebateRecord`.
4. Capture agreement and dissent in `ConsensusGateRecord`.
5. Apply `PhaseQualityGate`.
6. Require human review before any promotion.

## Prompt Safety

Market metadata, repository text, issue comments, PR comments and external research snippets are untrusted input.

Before any future model dispatch, `PromptPreflightPolicy` must verify:

- sensitive data is absent
- untrusted market text is delimited as data
- tool-like instructions are blocked
- prompt size is bounded
- dispatch remains disabled until a separate approval gate changes it

## Reaction Engine Boundary

Reaction engine concepts are record-only in this project.

Allowed:

- record CI failure
- record review requested
- record changes requested
- require manual triage

Forbidden:

- automatic code changes
- automatic retries
- automatic branch pushes
- automatic merges
- network calls
- credential access

## Promotion Boundary

Consensus is not approval.

Advisory review is not risk approval.

Phase quality gates are not production approval.

Any future move toward runtime provider integration requires a separate approval PR and must pass `docs/integrations/agent_runtime_approval_gate.md`.

## Non-Goals

- no provider setup
- no model runtime
- no plugin installation
- no MCP runtime
- no remote autonomous session
- no persistent external memory
- no automatic remediation
- no trading
- no production enablement
