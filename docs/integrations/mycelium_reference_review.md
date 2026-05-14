# Mycelium Reference Review

## Purpose

This review captures safe architectural patterns from `Dewinator/mycelium` without adopting the repository as a dependency, runtime, service, database, MCP server or dashboard.

Mycelium is useful as a reference for agent memory governance: persistent memory records, recall requests, recall results, consolidation, lessons, traits, intentions, conflicts, retention and federated-memory policy. This project only adopts those ideas as local contracts and policy documents.

## Current Decision State

```text
mycelium_reference_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
docker_runtime_allowed: false
supabase_allowed: false
postgres_allowed: false
pgvector_allowed: false
ollama_allowed: false
embedding_runtime_allowed: false
mcp_runtime_allowed: false
dashboard_runtime_allowed: false
auto_absorb_allowed: false
auto_digest_allowed: false
context_priming_allowed: false
federation_allowed: false
network_access_allowed: false
credentials_allowed: false
trading_methods_allowed: false
production_enabled: false
```

## Safe Patterns Adopted

- Agent memory record for redacted local memory metadata.
- Memory recall request for bounded local recall.
- Memory recall result for redacted local matches.
- Memory consolidation record for reviewed compaction.
- Lesson record for human-reviewed guidance.
- Agent trait record for non-runtime behavioral guidance.
- Intention record for explicit objectives and blocked actions.
- Memory conflict record for manual contradiction review.
- Session digest record for supervised work summaries.
- Memory retention policy for redaction and retention boundaries.
- Federated memory policy with federation disabled.
- MCP memory tool policy with tool runtime disabled.

## Runtime Components Rejected

The following Mycelium-style runtime components are not adopted:

- Docker runtime.
- Supabase runtime.
- PostgreSQL runtime.
- pgvector storage.
- Ollama runtime.
- embedding runtime.
- Node MCP server.
- dashboard runtime.
- automatic context priming.
- automatic memory absorption.
- automatic session digest runtime.
- swarm or federation runtime.
- node identity runtime.
- environment configuration files carrying secrets.
- networked memory storage.
- credential-bearing tool runtime.

## Security Boundary

Agent memory governance must remain local, redacted, contract-first and fail-closed. Memory contracts must not store secrets, broker context, private endpoint payloads, executable decisions, risk approval or execution approval.

MCP memory tools remain disabled. Any future runtime, storage, embedding, dashboard or MCP integration requires a separate external adapter review, dependency review, security review, approval gate and CI policy update.

## What Was Intentionally Not Adopted

This PR does not clone Mycelium, vendor Mycelium code, install Mycelium dependencies, start databases, run containers, create embeddings, run MCP servers, open dashboards, synchronize memory between nodes, call networks or introduce credentials.
