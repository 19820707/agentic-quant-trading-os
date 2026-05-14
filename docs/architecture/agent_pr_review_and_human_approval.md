# Agent PR Review And Human Approval

## Purpose

This control layer defines the evidence required before an agent-authored change can move from sandbox/test evidence to human review.

It does not approve autonomous merge, direct main writes, GitHub token use, production deployment, network access, credentials, risk approval, execution approval, broker access, exchange access, or trading behavior.

## Review Chain

The expected chain is:

1. `AgentTaskSpec`
2. `AgentPatchPlan`
3. `AgentRiskAssessment`
4. `SandboxExecutionReport`
5. `TestEvidenceReport`
6. `RollbackPlan`
7. `AgentPRReviewEvidence`
8. `HumanApprovalRecord`

The final two records provide review evidence only. They do not grant runtime authority.

## Required Review Evidence

Every agent-authored pull request must show:

- reviewed files;
- risk level;
- test evidence reference;
- rollback plan reference;
- unresolved blocking finding count;
- security boundary decision;
- human review requirement.

## Human Approval Boundary

Human approval remains explicit and scoped. A human record may document review state, but it must not create automatic merge authority or runtime privileges.

Current default:

- auto-merge remains disabled;
- direct main write remains disabled;
- network remains disabled;
- credentials remain disabled;
- trading changes remain disabled;
- risk approval remains disabled;
- execution remains disabled;
- production remains disabled.

## Non-Goals

- no real PR bot;
- no GitHub token;
- no GitHub App;
- no webhook receiver;
- no auto-merge;
- no direct main write;
- no production deployment;
- no broker or exchange integration;
- no trading logic.
