# Phased Execution Plan

Use this plan to keep Codex work small, auditable and low-token.

## Rule

One task. One scope. Few files. No unrelated improvements. Stop and summarize.

## Standard Prompt Shape

```text
Read AGENTS.md first and follow it strictly.

Task scope:
<one small task only>

Files expected to touch:
<list files/folders>

Rules:
- Do not expand scope.
- Do not install dependencies.
- Do not clone repositories.
- Do not implement trading logic.
- Do not add credentials.
- Stop after this task and summarize files changed.
```

## Scaffold Phases

1. Create or update `AGENTS.md`.
2. Create only base directories.
3. Create minimal root docs.
4. Create service READMEs.
5. Create FastAPI `/health` and `/ready` placeholders.
6. Create JSON Schema placeholders.
7. Create integration catalog.
8. Create security scaffolding.
9. Create agentic placeholders.
10. Create safe scripts and Makefile targets.
11. Validate structure.

## Stop Conditions

Stop before work that requires:

- live trading logic
- broker submission
- credentials
- external repository cloning
- dependency installation
- Git submodules
- Risk Gateway bypass
- broad architecture rewrites

## Report Format

- Files changed:
- What was done:
- What was intentionally not done:
- Checks:
- Next recommended step:

