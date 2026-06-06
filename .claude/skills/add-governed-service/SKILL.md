---
name: add-governed-service
description: Use when adding or changing a service in Agentic Quant Trading OS. Enforces the service structure (placeholder app with /health + /ready, no external calls), the authority boundary (may/must-not), small safe phases, and the scaffold audit.
---

# Add or change a governed service

> Bound by [`AGENTS.md`](../../../AGENTS.md) (Operating Mode + Token Discipline):
> work in small explicit phases; prefer minimal safe placeholders; do not rewrite
> existing files unless necessary; do not expand scope.

## When to use
Creating/extending one of the 16 services under `services/<name>/`.

## Procedure
1. **Confirm the boundary first** from the service `README.md` (its may / must-NOT).
   State it before coding.
2. **Structure:** `README.md` (boundary), `app/__init__.py`, `app/main.py`
   (placeholder exposing `GET /health` + `GET /ready`, **no external calls**),
   `app/<core>.py` (pure, deterministic, no I/O/network/credentials), `tests/`.
3. **Emit contract-shaped payloads only** (use `contract-first`); preserve the
   identity chain and `trace_id`/`correlation_id`/`schema_version`.
4. **Verify:** `make scaffold-check` (`scripts/scaffold_audit.py`) + run the
   `run-checks` skill.

## Non-negotiables
- A service never places orders except via the governed flow; only the Risk Gateway
  emits an `ApprovedOrder`.
- No network/broker/FIX imports in `app/`; no secrets; `/health`+`/ready` make no
  external calls.
- Minimal, focused changes; report what was intentionally not done.

## Definition of done
- Boundary respected; placeholder/core + tests; `make scaffold-check` clean; checks green.
