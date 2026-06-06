---
name: dependency-review
description: Use before adding ANY dependency, external project, submodule, or MCP/FIX integration. Enforces the no-clone/no-vendor default, a license/security/maintenance/production review, and that nothing bypasses the Risk Gateway or touches broker credentials.
---

# Dependency & external-integration review

> Bound by [`AGENTS.md`](../../../AGENTS.md) (Operating Mode): external projects are
> not vendored by default; nothing is cloned/installed/submoduled without explicit
> instruction. Prefer minimal, safe placeholders.

## When to use
Before adding a library, cloning a repo, adding a submodule, or wiring an MCP/FIX/
broker integration.

## Procedure
1. **Default: don't.** Prefer the standard library and existing `packages/`
   (`common`, `contracts`, `sdk`).
2. **If genuinely needed,** review and record: license, security/CVE posture,
   maintenance health, production suitability. Add only with **explicit approval** —
   never silently.
3. **Integration shape:** adapters / wrappers / reference-only docs. **No external
   project may bypass the Risk Gateway** or access live broker credentials.
4. **Hard bans:** MCP tools never receive broker credentials; paper MCP tools are
   isolated from live; FIX engines only inside execution-engine adapters; backtesting
   tools never promote straight to live; reference architectures stay reference-only
   unless explicitly approved.

## Non-negotiables
- No clone / vendor / install / submodule without explicit human instruction.
- Nothing bypasses the Risk Gateway; no broker credentials to tools.

## Definition of done
- A written review + explicit approval recorded; integration via an adapter; checks green.
