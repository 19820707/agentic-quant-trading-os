---
name: agentic-self-programming-governance
description: Use when an agent proposes code changes. Enforces a 9-stage gated flow (policy check → risk assessment → patch → isolated sandbox → verifier → audit → human approval → controlled rollout → rollback validation). Human approval is MANDATORY for any persistent change. The most critical governance skill.
category: governance
---

# Agentic self-programming governance

> Governance skill, bound by [`AGENTS.md`](../../../../AGENTS.md). Agents may
> propose code; **humans approve**. No autonomous merge, deploy, or go-live.

## Mandatory rule

```
human_approval_required = true        # for ANY persistent change
```

## The 9 stages (each is a contract; preserve lineage; fail-closed)

```
stage_0  policy_check          -> agent_task_spec (scope, forbidden boundaries)
stage_1  risk_assessment       -> agent_risk_assessment (blast radius, critical surfaces)
stage_2  patch_generation      -> agent_patch_plan (minimal change; rollback defined FIRST)
stage_3  isolated_sandbox      -> sandbox_execution_report (no live, no creds, no broker egress)
stage_4  verifier_execution    -> test_evidence_report (relevant checks pass)
stage_5  audit_generation      -> append-only audit event (tamper-evident)
stage_6  human_approval        -> human_approval_record (named human; REQUIRED)
stage_7  controlled_rollout    -> staged, reversible, monitored
stage_8  rollback_validation   -> rollback_plan proven to restore the prior state
```

## Discipline
- A stage only proceeds if the previous one passed. Any failure halts (fail-closed).
- The agentic layer can **never** approve its own change to a critical surface
  (risk / execution / secrets / auth).
- The rollback plan exists **before** any edit and is **validated** at stage_8.

## Non-negotiables
- `human_approval_required = true` for any persistent change — no exceptions.
- Sandbox first; no secrets; no live; every step contract-shaped and audited.

## Definition of done
- The full evidence chain (stage_0 → stage_8) is contract-conformant; human approval
  recorded; rollback validated; checks green.
