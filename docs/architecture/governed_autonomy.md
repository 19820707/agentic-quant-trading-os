# Governed Autonomy Execution Plan

The system can plan, rank and prepare safe engineering work. It cannot write to
`main`, auto-merge, use credentials, call broker/exchange networks, approve
risk, approve execution or submit orders.

## Operating boundary

Autonomy is limited to:

- local planning;
- branch-scoped file preparation for low-risk work;
- local test evidence;
- draft PR preparation;
- evidence recording;
- explicit human review requests.

Critical or ambiguous work is not executed autonomously. It is converted into a
human-review work order with required evidence.

## Work order states

| State | Meaning | File changes allowed |
|---|---|---|
| `ready_for_pr_preparation` | Low-risk PR-only work may be prepared on a branch | Yes, branch only |
| `human_review_required` | Safe to plan, but needs human review before modification | No |
| `blocked` | Scope violates policy or critical capability boundary | No |
| `deferred` | Valid but outside current capacity | No |

## Safety invariants

Every governed autonomy plan keeps these fields false:

- `direct_main_write_allowed`
- `auto_merge_allowed`
- `network_allowed`
- `credentials_allowed`
- `risk_approval_allowed`
- `execution_allowed`

The planner does not run shell commands, edit files by itself, open PRs, merge
branches, read secrets, approve risk, or approve execution. It emits a contract
that another controlled workflow can use as a checklist.

## Evidence model

Every work order requires rollback and test evidence. Additional evidence is
derived from risk and touched paths:

- docs require documentation review;
- SDK changes require SDK unit tests;
- schema changes require contract validation;
- CI/scripts require CI safety review;
- risk/execution/trading paths require deterministic-risk-gateway review.

This keeps autonomy useful while preserving the project rule:

```text
AI proposes.
Models predict.
Risk Gateway decides.
Execution Engine executes.
Audit proves.
Human governance supervises.
```
