---
name: run-checks
description: Use to verify a change before considering it done. Runs the project's real checks — scaffold audit, secret-artifact audit, contract validation, dev-environment check, and tests — interpreting failures fail-closed.
---

# Run the project checks (verify a change)

> Bound by [`AGENTS.md`](../../../AGENTS.md) (Required Workflow): make minimal
> changes, run relevant checks, report what changed and what was intentionally not
> done. A red check blocks the change — fix the code, never weaken the check.

## When to use
Closing any task; before commit; whenever you touch code, schemas, or services.

## Procedure
1. **Scaffold + safety:** `make scaffold-check` (`scripts/scaffold_audit.py`) and
   `python scripts/secret_artifact_audit.py` — placeholder integrity, safety markers,
   no secret artifacts.
2. **Contracts:** validate touched payloads with `packages.contracts`
   `ContractValidator` (and list via `SchemaRegistry`); ensure every contract has a
   fixture under `tests/fixtures/contracts/`.
3. **Environment:** `python scripts/check_dev_environment.py` if relevant.
4. **Tests:** run only the relevant tests for the change (token discipline); for
   trading/risk/execution prefer deterministic/replay tests.
5. **Interpret fail-closed:** distinguish pre-existing vs introduced failures. A
   contract/safety failure is a **policy** failure — fix the code, not the check.
6. **Report:** files changed, checks run + results, residual risk, rollback, and
   what was intentionally not done.

## Non-negotiables
- Checks are deterministic; no test requires broker credentials or submits a real order.
- Never weaken/skip a check to make it pass.

## Definition of done
- Relevant checks green; change reported with residual risk and rollback.
