# Safety Review Template

Use this for changes touching data, models, risk, execution, agentic workflows, integrations, security or operations.

## Change Summary

- Files:
- Services:
- Environment:
- Requested scope:

## Stop Condition Check

Does the change require any of these?

- live trading logic:
- broker/exchange order submission:
- real API credentials:
- external repository clone:
- major dependency install:
- Git submodule:
- Risk Gateway bypass:
- agent execution permission:
- critical safety rule change:
- audit/security deletion:

If any answer is yes, stop and request explicit instruction.

## Risk Review

- Capital impact:
- Risk Gateway impact:
- Execution Engine impact:
- Model authority impact:
- Paper/live separation impact:

## Security Review

- Secret exposure:
- Credential path:
- External integration:
- Logging/tracing exposure:
- Privileged action:

## Audit Review

- Required IDs:
- Audit event impact:
- Evidence retained:
- Rollback evidence:

## Result

Approved | Rejected | Needs changes

