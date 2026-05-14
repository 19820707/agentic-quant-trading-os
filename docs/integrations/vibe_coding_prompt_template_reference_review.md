# Vibe Coding Prompt Template Reference Review

## Purpose

This review identifies safe product-engineering discipline patterns from `KhazP/vibe-coding-prompt-template`.

It does not approve cloning, vendoring, copying templates verbatim, installing tooling, running LLM workflows, generating code automatically, deploying, or adapting the repository as an execution system.

Repository reviewed:

- https://github.com/KhazP/vibe-coding-prompt-template

## Current Decision

vibe_coding_prompt_template_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
template_copy_allowed: false
prompt_runtime_allowed: false
llm_runtime_allowed: false
network_access_allowed: false
credentials_allowed: false
auto_code_generation_allowed: false
auto_build_allowed: false
auto_deploy_allowed: false
production_enabled: false
trading_methods_allowed: false

Initial classification: reference-only product engineering discipline source.

## Reusable Patterns

### Research Before Build

Safe adaptation:

- define a research brief
- capture open questions
- require human review
- block implementation by default

### PRD And Requirement Discipline

Safe adaptation:

- record product requirements
- link acceptance criteria
- document out-of-scope items
- keep implementation disabled until approval

### Technical Design Before Editing

Safe adaptation:

- record selected design
- record alternatives
- record validation plan
- record risk controls

### Agent Instruction Pack

Safe adaptation:

- identify source documents
- define allowed actions
- define forbidden actions
- require plan before edit
- block credentials and execution

### Plan Execute Verify Cycle

Safe adaptation:

- document plan
- document execution summary
- document verification summary
- require human review before continuation

### MVP Boundary

Safe adaptation:

- define current scope
- define out-of-scope items
- define future work
- block scope expansion by default

### Handoff Artifacts

Safe adaptation:

- summarize context
- reference files
- list open decisions
- confirm redaction
- block credentials

### Build Readiness And Post-Build Verification

Safe adaptation:

- check docs exist
- check acceptance criteria exist
- check test plan exists
- check rollback plan exists
- record verification commands
- block promotion by default

## Non-Reusable Components

Do not reuse directly:

- raw prompt templates as authority
- generic MVP deployment guidance
- clone-based setup
- template repository structure
- automatic code generation flows
- AI IDE runtime workflows
- production deployment steps
- generated AGENTS.md replacement

## Required Internal Boundary

Any future implementation inspired by this repository must:

- preserve the existing AGENTS.md authority
- remain contract-first
- use local synthetic fixtures first
- require human review before implementation
- avoid LLM runtime calls in unit tests
- avoid network calls
- avoid credentials
- avoid deployment
- avoid trading
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

This project may safely define:

- research brief contracts
- product requirement contracts
- technical design contracts
- agent instruction pack contracts
- implementation plan contracts
- acceptance criteria contracts
- plan-execute-verify cycle contracts
- MVP boundary contracts
- handoff artifact contracts
- build readiness checklist contracts
- post-build verification contracts

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- copying the templates directly into the project as authoritative prompts
- replacing AGENTS.md
- running AI IDE workflows from the repository
- automatic code generation
- automatic deployment
- production promotion
- trading workflow authority

## Recommended Next Step

Review the product engineering discipline contracts before considering any future prompt or workflow template integration.
