# Agent Memory Governance

## Purpose

Agent memory governance defines local, non-executable contracts for future research memory. It provides a safe structure for capturing lessons, recall requests, recall results, consolidation, traits, intentions, conflicts, session digests and retention policy before any runtime memory system exists.

This document is contract-first scaffolding only. It does not approve memory databases, vector stores, embeddings, MCP runtime, dashboards, agent identity runtime, federation, networked storage, credentials or trading authority.

## Default State

```text
memory_runtime_enabled: false
external_memory_allowed: false
embedding_runtime_allowed: false
mcp_runtime_allowed: false
dashboard_runtime_allowed: false
auto_absorb_allowed: false
auto_digest_allowed: false
context_priming_allowed: false
federation_allowed: false
network_access_allowed: false
credentials_allowed: false
broker_context_allowed: false
trading_methods_allowed: false
execution_allowed: false
production_enabled: false
```

## Contract Set

- `AgentMemoryRecord`
- `MemoryRecallRequest`
- `MemoryRecallResult`
- `MemoryConsolidationRecord`
- `LessonRecord`
- `AgentTraitRecord`
- `IntentionRecord`
- `MemoryConflictRecord`
- `SessionDigestRecord`
- `MemoryRetentionPolicy`
- `FederatedMemoryPolicy`
- `MCPMemoryToolPolicy`

## Safety Boundary

Memory records may capture redacted governance metadata, research lessons, validation outcomes and supervised handoffs. They must not contain credentials, broker context, private endpoint payloads, executable orders, risk approval, execution approval or runtime tool authority.

All memory-related contracts include traceability fields and fail-closed flags. Where human review matters, contracts require explicit review state rather than automatic application.

## Recall Flow

A safe future recall flow is:

1. `MemoryRecallRequest` describes the local bounded query.
2. A local governed component returns `MemoryRecallResult`.
3. Results are redacted before use.
4. Research workflows may cite the result as context.
5. No memory result may approve risk, approve execution or bypass deterministic-risk-gateway.

## Consolidation And Retention

Memory consolidation is manual by default. `MemoryConsolidationRecord`, `MemoryConflictRecord` and `MemoryRetentionPolicy` require human review for deletion, conflict resolution and retention changes.

## Federation And MCP

`FederatedMemoryPolicy` and `MCPMemoryToolPolicy` are disabled by default. They document boundaries for future review; they do not enable runtime, registration, remote peers, credentials, network access, trading or execution.

## Future Approval Requirements

Any future memory runtime must go through:

- external adapter review checklist
- dependency review
- security review
- CI impact review
- secret and artifact hygiene review
- explicit approval gate
- local-only tests before runtime tests
