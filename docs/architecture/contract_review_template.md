# Contract Review Template

Use this before implementing cross-service behavior.

## Contract Summary

- Producer:
- Consumer:
- Schema path:
- Version:
- Lifecycle IDs:

## Required Fields

- `trace_id`:
- `correlation_id`:
- Domain IDs:
- Timestamp semantics:
- Validation status:

## Compatibility

- Backward compatible:
- Breaking change:
- Migration required:
- Deprecation plan:

## Safety Boundary

- Can this create an executable order?
- Can this bypass the Risk Gateway?
- Can this expose credentials?
- Can this mutate audit history?

Any "yes" requires explicit approval and additional review.

## Tests

- Schema validation:
- Producer contract test:
- Consumer contract test:
- Negative validation test:

## Decision

Approved | Rejected | Needs changes

