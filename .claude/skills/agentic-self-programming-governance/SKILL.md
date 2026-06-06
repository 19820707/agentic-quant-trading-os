---
name: agentic-self-programming-governance
description: Use when an agent proposes code changes to the platform. Enforces the governed self-programming flow — task spec → risk assessment → patch plan → sandbox execution → test evidence → PR review evidence → human approval → rollback plan. Agents propose; humans approve; nothing merges or goes live autonomously.
---

# Agentic self-programming governance

> Bound by [`AGENTS.md`](../../../AGENTS.md). Agents may propose code, but **humans
> approve**. No autonomous merge, deploy, or go-live. Every privileged action is
> auditable and reversible.

## When to use
Working with the `governance` contract domain for agent-authored changes:
`agent_task_spec`, `agent_risk_assessment`, `agent_patch_plan`,
`sandbox_execution_report`, `test_evidence_report`, `agent_pr_review_evidence`,
`human_approval_record`, `rollback_plan`.

## Procedure (each step is a contract; preserve lineage)
1. **`agent_task_spec`** — scope, target files, forbidden boundaries, expected cost.
   Small, explicit, no scope creep.
2. **`agent_risk_assessment`** — blast radius, critical-surface flags (risk/auth/
   execution/secrets), required approvals.
3. **`agent_patch_plan`** — the minimal change, with a **`rollback_plan`** defined
   before any edit.
4. **`sandbox_execution_report`** — run in an isolated sandbox (no live, no creds, no
   network egress to brokers).
5. **`test_evidence_report`** — relevant checks pass (the `run-checks` skill).
6. **`agent_pr_review_evidence`** — the change is reviewed; evidence recorded.
7. **`human_approval_record`** — a **named human** approves before merge. The agentic
   layer can never approve its own change to a critical surface alone.

## Non-negotiables
- Agents propose; **humans approve** critical/irreversible changes. No auto-merge.
- A rollback plan exists before editing; sandbox first; no secrets; no live.
- Every step is contract-shaped and audited.

## Definition of done
- The full evidence chain (spec→…→human_approval) is contract-conformant; rollback
  defined; checks green; human approval recorded for critical surfaces.
