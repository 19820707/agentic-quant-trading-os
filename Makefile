.PHONY: help scaffold-check

help:
	@echo "Agentic Quant Trading OS scaffold"
	@echo "Available targets:"
	@echo "  scaffold-check  Verify placeholder scaffold files and safety markers"

scaffold-check:
	@python scripts/scaffold_audit.py
