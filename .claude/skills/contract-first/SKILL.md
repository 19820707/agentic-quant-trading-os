---
name: contract-first
description: Use when defining or changing any cross-service payload. JSON Schemas under packages/contracts/schemas are the source of truth; validate with packages.contracts ContractValidator / SchemaRegistry. Research contracts are non-executable.
---

# Contract-first development

> Bound by [`AGENTS.md`](../../../AGENTS.md). No service exchanges an undocumented
> payload. Define the contract **before** the code.

## When to use
Adding/changing a payload in any domain: `research`, `ml`, `trading`, `features`,
`paper`, `audit`, `governance`, `market`, `security`.

## Procedure
1. **Add/modify the schema** under `packages/contracts/schemas/<domain>/<name>.schema.json`
   (top-level forbidden additional properties; required fields incl. `schema_version`,
   `trace_id`, `correlation_id` and the relevant identity ids). Preserve the chain
   (`research_dossier_id → … → audit_id`).
2. **Honour the distinctions:** research contracts are **non-executable**;
   `SignalCandidate` is **not** `OrderIntent`; `RiskReviewInput` is **not**
   `RiskDecision`. Encode safety with const/enum where possible.
3. **Validate** with the local utility (no network, no risk decisions):
   ```python
   from packages.contracts import ContractValidator
   ContractValidator().validate("<domain>", "<name>", payload)   # .valid
   ```
   Use `SchemaRegistry` to list/resolve schemas. `jsonschema` is used if present,
   else conservative local checks (required fields, forbidden extras, const).
4. **Fixtures:** add paper-only JSON under `tests/fixtures/contracts/` — never
   credentials, live config, or real broker identifiers.

## Non-negotiables
- Source of truth = schemas; any change needs schema + tests.
- The validator checks shape only — it never decides risk, approves, or calls out.

## Definition of done
- Schema + fixture + validation pass; checks green.
