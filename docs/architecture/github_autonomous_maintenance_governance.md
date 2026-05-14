# GitHub Autonomous Maintenance Governance

## Purpose

This document defines a controlled architecture for future GitHub autonomous
maintenance. It converts repository-monitoring and PR-automation patterns into
internal governance contracts.

This does not approve production automation, GitHub App installation, webhook
deployment, repository writes, autonomous patching, auto-merge, external SaaS
reviewers, LLM runtime, credentials, trading logic or broker/exchange access.

## Reference Patterns

The future design is informed by these external references:

- Dependabot: dependency monitoring and automated pull requests
- GitHub Copilot coding agent: task to branch to pull request workflow
- PR-Agent: automated pull request review summaries and risk comments
- Probot and Octokit: GitHub App, webhook and API patterns
- Semgrep, CodeQL and Trivy: finding generation and security scanning patterns
- GitHub Actions: sandboxed validation and test execution

These are references only. This repository must not vendor or install them
without a separate external adapter and dependency approval process.

## Capability Blocks

The intended control-plane blocks are:

1. repository discovery
2. multi-repository monitor
3. webhook receiver
4. scheduled scanner
5. finding engine
6. patch planner
7. risk classifier
8. policy engine
9. sandbox patch runner
10. test runner
11. branch, commit and pull request bot
12. pull request reviewer agent
13. evidence index
14. rollback engine
15. audit log

## Safety Model

Autonomy is allowed only as controlled PR production:

- low risk: may propose a branch and draft pull request after approval
- medium risk: may generate plan and patch proposal, review required
- high risk: may generate plan only
- critical risk: must block execution and raise an alert

All future write actions must be blocked by default.

## Hard Boundaries

The autonomous maintenance system must never:

- write directly to `main`
- auto-merge its own pull requests
- read or print GitHub tokens
- read broker, exchange, wallet or trading credentials
- modify risk, execution or broker code without explicit human approval
- bypass CI quality gates
- bypass deterministic-risk-gateway
- run live trading, private endpoints or production automation
- run unreviewed code from forks with privileged credentials

## Required Evidence

Every proposed autonomous maintenance action must preserve:

- repository identity
- source trigger
- finding classification
- risk classification
- policy decision
- planned patch summary
- files expected to change
- tests planned
- rollback plan
- audit correlation identifiers

## Current Status

github_autonomous_maintenance_reference_reviewed: true
github_app_enabled: false
webhook_receiver_enabled: false
scheduled_scanner_enabled: false
repository_write_enabled: false
auto_pr_enabled: false
auto_merge_enabled: false
llm_runtime_enabled: false
credentials_allowed: false
production_enabled: false

