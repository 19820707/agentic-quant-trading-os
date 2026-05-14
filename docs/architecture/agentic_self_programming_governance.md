# Agentic Self-Programming Governance

## Purpose

This governance layer defines how LLM-assisted engineering agents may propose code changes without receiving direct execution authority.

The platform model is:

1. LLM proposes a task or patch plan.
2. Policy engine classifies risk.
3. Sandbox and test evidence are required before a pull request.
4. Human review remains required.
5. Main branch writes and auto-merge remain forbidden.

This document does not approve autonomous runtime, credentials, network access, direct GitHub writes, production deployment, risk approval, execution approval, broker access, exchange access, or trading behavior.

## Current State

The current state is fail-closed:

- no real LLM agent runtime;
- no GitHub token integration;
- no webhook receiver;
- no scheduler;
- no sandbox command execution;
- no branch creation by runtime code;
- no pull request creation by runtime code;
- no auto-merge;
- no direct write to main;
- no credentials;
- no network;
- no trading changes without human review.

## Allowed Local Scope

The only allowed scope in the current phase is local contract and policy classification:

- define an `AgentTaskSpec`;
- define an `AgentPatchPlan`;
- define an `AgentRiskAssessment`;
- classify proposed work using deterministic local rules;
- fail closed for sensitive files, credentials, network, trading, risk and execution paths.

## Agent Roles

Allowed future roles are advisory only:

- code maintainer;
- test runner;
- PR reviewer;
- security reviewer;
- architecture reviewer.

These roles may propose work. They cannot execute work, approve risk, approve execution, access secrets, or merge code.

## Risk Model

Low-risk changes may be eligible for pull-request-only flow.

Medium-risk changes require human review.

High-risk changes require human review and sandbox/test evidence.

Critical-risk changes are blocked by default.

Critical indicators include:

- broker or exchange integration;
- credentials or secret handling;
- network access;
- Risk Gateway changes;
- Execution Engine changes;
- order submission or cancellation;
- transfer or withdrawal behavior;
- production enablement;
- auto-merge;
- direct writes to main.

## Non-Negotiable Boundaries

- Agents must never write directly to `main`.
- Agents must never receive broker, exchange, wallet or GitHub credentials.
- Agents must never submit, cancel, edit, transfer or withdraw.
- Agents must never approve risk or execution.
- Agents must never bypass deterministic-risk-gateway.
- Agents must never auto-merge critical platform changes.

## Promotion Rule

Any future real agent runtime requires a separate approval gate and must remain pull-request-only until explicitly promoted. Runtime enablement, network access, credentials, GitHub App writes, webhook receivers and schedulers are separate capabilities and remain disabled.

## Non-Goals

- no real LLM runtime;
- no autonomous execution;
- no GitHub App or token integration;
- no webhook processing;
- no scheduler;
- no sandbox command runner;
- no auto-merge;
- no broker or exchange integration;
- no trading logic.
