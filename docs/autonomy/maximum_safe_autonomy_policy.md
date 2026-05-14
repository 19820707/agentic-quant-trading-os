# Maximum Safe Autonomy Policy

## Purpose

This policy changes the intended operating model from human-approval-first to maximum safe autonomy.

The system should act autonomously whenever the action is reversible, bounded, tested, non-critical, policy-approved, auditable, and rollback-safe.

Human approval is reserved for exceptions: critical risk, unknown risk, protected paths, credential exposure, production promotion, broker/exchange/risk/execution mutation, live trading enablement, or attempts to weaken security gates.

## Operating principle

```text
autonomous by default
human approval by exception
fail-closed for critical or unknown risk
```

## Autonomy ladder

| Level | Behavior | Human approval |
|---|---|---|
| L0 Manual | Humans perform the work | Required |
| L1 Assisted | System proposes changes only | Required |
| L2 Auto plan | System plans, classifies and prepares evidence | Exception-based |
| L3 Auto PR | System creates branch, patch, tests and PR | Not required for low/medium if policy allows |
| L4 Auto merge | System merges low-risk safe changes after gates pass | Not required for low risk |
| L5 Critical autonomy | System can affect runtime/financial/production control loops | Not allowed by this policy |

Current target: L3 by default and L4 for tightly bounded low-risk changes.

## Risk-to-action matrix

| Risk class | Autonomous action | Merge behavior | Human approval |
|---|---|---|---|
| low | patch, branch, test, PR, evidence | auto-merge allowed if all gates pass | no |
| medium | patch, branch, test, PR, evidence | auto-merge allowed only if no protected path and confidence is high | exception-only |
| high | sandbox patch and draft PR only | no auto-merge | required for merge |
| critical | block, alert, evidence record | no merge | required |
| unknown | block or simulation-only | no merge | required |

## Auto-patch eligibility

A change is eligible for autonomous patching when all conditions are true:

- risk is low or medium;
- confidence is high;
- change is reversible through branch deletion, PR closure, or commit revert;
- patch is generated in a non-main branch;
- no secret is read, printed, copied, committed, or exposed;
- no production deployment is triggered;
- no trading, broker, exchange, risk, execution, auth, credential, or live-capital behavior is modified;
- tests and static checks are declared;
- rollback plan is declared;
- audit evidence is emitted.

## Auto-merge eligibility

Auto-merge is eligible only for low-risk changes that satisfy all conditions:

- all local and remote gates pass, or remote checks are unavailable only through a documented infrastructure exception;
- no protected path is touched;
- no runtime behavior changes;
- no dependency major upgrade;
- no GitHub Actions permission broadening;
- no security gate weakening;
- no auto-merge policy weakening;
- no generated credential, token, key, seed phrase, private endpoint, broker secret, or exchange secret appears in diff or logs;
- rollback is trivial.

Medium-risk auto-merge may be allowed only for documentation, evidence records, fixtures, tests, or schemas that do not alter runtime behavior and do not touch protected paths.

## Protected paths

The following path families require stricter treatment:

```text
broker/
exchange/
execution/
risk/
auth/
secrets/
credentials/
keys/
wallet/
mcp/runtime/
agents/runtime/
.github/workflows/
packages/runtime/
packages/execution/
packages/risk/
```

Changes touching protected paths are not eligible for blind auto-merge.

## Critical actions

The following actions are always blocked or require explicit exception handling:

- enabling live trading;
- adding broker or exchange write APIs;
- bypassing deterministic risk gates;
- weakening redaction or secret scanning;
- expanding GitHub token scopes;
- printing authorization headers;
- enabling auto-merge for high or critical risk;
- disabling tests, audits, evidence capture, or rollback requirements;
- modifying production deployment behavior;
- allowing unrestricted shell execution by agents;
- allowing network calls from untrusted agent tools;
- converting read-only market adapters into write-capable execution adapters.

## Deterministic policy decision

A future runtime controller must return exactly one policy decision:

| Decision | Meaning |
|---|---|
| ALLOW_AUTO_MERGE | Low-risk change may be merged after all gates pass |
| ALLOW_AUTO_PR | Patch may be created and PR opened automatically |
| SANDBOX_ONLY | Patch may be simulated but not opened as mergeable PR |
| REQUIRE_EXCEPTION | Human exception required before merge or activation |
| BLOCK | No patch/write action allowed |

## Evidence required for autonomous action

Every autonomous action must preserve:

- repository;
- branch;
- trigger;
- finding ID;
- risk class;
- confidence;
- changed files;
- protected path evaluation;
- policy decision;
- tests planned;
- tests executed;
- secret/redaction scan result;
- rollback plan;
- audit correlation ID.

## Safety boundary

This document does not implement runtime automation, GitHub App installation, webhook receivers, repository write tokens, auto-merge execution, LLM runtime, network calls, credentials, trading, broker/exchange integration, risk approval, execution approval, or production promotion.

It defines the policy boundary for future implementation.
