.PHONY: help scaffold-check secret-audit test check

help:
	@echo "Agentic Quant Trading OS scaffold"
	@echo "Available targets:"
	@echo "  scaffold-check  Verify placeholder scaffold files and safety markers"
	@echo "  secret-audit    Scan the repository for secrets and blocked artifacts"
	@echo "  test            Run the unit test suite (FastAPI import test is skipped if FastAPI is absent)"
	@echo "  check           Run every local gate: scaffold-check, secret-audit, test"

scaffold-check:
	@python scripts/scaffold_audit.py

secret-audit:
	@python scripts/secret_artifact_audit.py

test:
	@python -m unittest discover -s tests -p "test_*.py"

check: scaffold-check secret-audit test
