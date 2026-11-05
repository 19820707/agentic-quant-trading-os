# PR Evidence Record Template

Use this template for every PR that changes governance, contracts, tests, runtime behavior, security posture, infrastructure, or autonomous maintenance boundaries.

## Pull request

- PR: #
- Title:
- Branch:
- Change class: documentation | contract | test | runtime | infrastructure
- Risk level: low | medium | high | critical
- Owner boundary:

## Summary

Describe what changed and why.

## Safety boundary

This PR does not approve or implement:

- runtime trading
- broker or exchange access
- credentials
- network calls
- autonomous repository writes
- auto-merge
- production promotion
- risk approval
- execution approval

Add any additional forbidden behavior here.

## Requirements evidence

| Requirement | Statement | Source |
|---|---|---|
| REQ-000 |  |  |

## Design evidence

| Design artifact | Path | Notes |
|---|---|---|
| DES-000 |  |  |

## Contract evidence

| Contract | Schema | Fixture | Test |
|---|---|---|---|
|  |  |  |  |

## Verification evidence

Local validation:

```bash
python -m unittest discover -s tests
python -m py_compile $(find . -name '*.py')
python scripts/scaffold_audit.py
python scripts/secret_artifact_audit.py
python scripts/check_dev_environment.py
```

Remote validation:

- Status: passed | failed | blocked | not_run
- Exception, if any:

## Risk review

| Risk | Control | Residual risk |
|---|---|---|
|  |  |  |

## Rollback plan

- Unmerged PR: close PR and delete branch.
- Merged PR: revert merge commit or squash commit.
- Data migration rollback: not applicable unless explicitly stated.
- Runtime rollback: not applicable unless explicitly stated.

## Decision

- Status: draft | ready for review | merged | rejected
- Decision rationale:
- Reviewer notes:
