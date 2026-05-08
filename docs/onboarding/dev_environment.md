# Development Environment

This repository is a governed scaffold. The local development environment exists to run placeholder services, contract tests and safety checks. It is not a trading runtime.

## Python Version

Use Python 3.11 or newer. The project declares this in `pyproject.toml`.

If your editor reports unresolved imports, first confirm that it is using the same interpreter where the project dependencies are installed.

## Create A Virtual Environment

From the repository root:

```bash
python -m venv .venv
```

Activate it with the command appropriate for your shell, then install the local project dependencies:

```bash
python -m pip install -e .
```

Do not install external trading libraries such as CCXT, OpenBB, Hummingbot, Trading Economics, QuestDB or broker SDKs unless a specific approved task asks for them.

## VS Code Interpreter

In VS Code:

1. Open the command palette.
2. Select `Python: Select Interpreter`.
3. Choose the `.venv` interpreter created for this repository.
4. Reload the editor if unresolved imports persist.

## Local Checks

Run the scaffold audit:

```bash
python scripts/scaffold_audit.py
```

Run contract tests:

```bash
python -m unittest discover -s tests -p "test_core_contract_schemas.py"
python -m unittest discover -s tests -p "test_contract_validator.py"
python -m unittest discover -s tests -p "test_contract_registry.py"
python -m unittest discover -s tests -p "test_contract_fixtures.py"
```

Check the local development environment:

```bash
python scripts/check_dev_environment.py
```

## Safety Boundary

No broker credentials are required for local development.

This scaffold does not implement live trading, broker integrations, order submission, execution approval or autonomous trading. Placeholder FastAPI services expose only static `/health` and `/ready` endpoints.
