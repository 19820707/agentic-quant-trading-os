# Governance Skills

A distinct category, separate from implementation / QA / operations skills, because
these skills **govern the behaviour of other agents and capabilities** — they set
policy, not implementation. Bound by the root [`AGENTS.md`](../../../AGENTS.md).

| Skill | Governs |
|-------|---------|
| [`research-and-debate`](research-and-debate/SKILL.md) | how agents produce knowledge (non-executable, structured) |
| [`agentic-self-programming-governance`](agentic-self-programming-governance/SKILL.md) | how agents change code (9-stage gated flow; human approval mandatory) |
| [`agent-orchestration-and-swarm`](agent-orchestration-and-swarm/SKILL.md) | how agents coordinate (fail-closed; unsafe consensus blocked) |
| [`mcp-tool-governance`](mcp-tool-governance/SKILL.md) | how external tools/output are trusted (untrusted by default; no broker creds) |

## Why a separate category

Keeping these apart lets the governance/assurance layers — **SC-01 (Architect
Prime)**, **SC-02 (Safety Oracle)**, the **Failure Intelligence Layer**, and the
**Runtime Assurance Layer** — apply policy specifically to agent-governing skills
without mixing them with implementation, QA, or operations skills. The result is a
cleaner, more auditable, higher-rigour governance model.

## Invariants common to all governance skills

- They **govern**; they do not implement, execute, or approve on their own.
- **Fail-closed** by default; uncertainty/unsafe state blocks, never escalates.
- **Human approval is mandatory** for any persistent or critical change.
- **No broker credentials**, ever, to any governed agent or tool.
- Every governed action is **contract-shaped and audited** end-to-end.
