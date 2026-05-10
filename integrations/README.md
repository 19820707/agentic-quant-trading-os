# Integrations

This directory is for safe integration documentation and future adapter boundaries.

Do not clone, vendor, install or execute external projects from this directory unless explicitly instructed.

No integration may bypass the Deterministic Risk Gateway. No integration may access live broker or exchange credentials except future approved execution-engine adapters.

Future integrations must pass the [External Adapter Safety Policy](../docs/architecture/external_adapter_safety_policy.md) before implementation.

Cataloging a repository does not mean it is trusted, approved or production-ready.

Future integrations must use internal contracts and governed adapters before they can interact with the platform.

Every future integration folder should include a completed [External Adapter Review Checklist](../docs/integrations/external_adapter_review_checklist.md) or a link to the approved checklist record.

Prediction-market repositories are cataloged in the [Prediction Market Repository Audit](../docs/integrations/prediction_market_repo_audit.md).

That audit is reference-only. It does not approve cloning, installing, vendoring, MCP activation, live trading, wallet access, broker/exchange credentials or runtime coupling.

The `datori/market-edge` repository has a separate [market-edge Reference Review](../docs/integrations/market_edge_reference_review.md). Reusable ideas are captured in the [Prediction Market Research Pipeline](../docs/architecture/prediction_market_research_pipeline.md) without importing its dependencies or runtime behavior.

The `mjunaidca/polymarket-skills` repository has a separate [polymarket-skills Reference Review](../docs/integrations/polymarket_skills_reference_review.md). Reusable ideas are captured in the [Agentic Tool Safety Taxonomy](../docs/architecture/agentic_tool_safety_taxonomy.md) without installing skills, enabling MCP runtimes, using `py-clob-client`, wallet credentials or live-executor behavior.

