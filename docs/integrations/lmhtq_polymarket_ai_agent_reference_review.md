# lmhtq Polymarket AI Agent Reference Review

## Purpose

This document records what can be safely reused from
`https://github.com/lmhtq/polymarket-ai-agent` as reference architecture.

The repository is not approved as a dependency, runtime, adapter, scheduler,
dashboard, data source or execution path. No code is copied, vendored or cloned
into this project.

## Current Decision

reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
polymarket_clob_allowed: false
llm_runtime_allowed: false
rss_runtime_allowed: false
reddit_runtime_allowed: false
scheduler_runtime_allowed: false
sqlite_runtime_allowed: false
dashboard_runtime_allowed: false
email_notification_allowed: false
network_access_allowed: false
credentials_allowed: false
trading_methods_allowed: false
production_enabled: false

## Useful Reference Patterns

- Tiered research stages for relevance classification, market-news scoring,
  probability estimation and deep analysis.
- Market-news relevance scoring before expensive analysis.
- Dry-run-first operating mode and explicit paper-only evaluation.
- Research cadence separation for ingest, analysis, monitoring and postmortem.
- Honest limitation records that document negative results and weak assumptions.
- Advisory risk-limit concepts such as max exposure, min edge, fractional
  sizing and stop-loss review.

## Rejected Runtime Patterns

- Polymarket CLOB execution.
- Polygon wallet private keys.
- OpenAI-compatible LLM API keys.
- RSS or Reddit live crawlers.
- Scheduler loops.
- SQLite runtime storage.
- FastAPI dashboard runtime.
- Email/AWS SES notifications.
- Paper or live executor runtime.
- Stop-loss automation.
- Market making.
- Any direct path from LLM output to orders.

## Safe Adaptation

The safe adaptation is contract-first:

- `TieredResearchStage`
- `MarketNewsRelevanceScore`
- `ResearchCadencePlan`
- `ModelLimitationRecord`
- `DryRunEvaluationSummary`

These contracts are local-only, non-executable and do not approve risk or
execution.

## Required Future Review

Any future runtime use would require a separate external adapter review,
dependency review, security review, deterministic-risk-gateway review and
explicit approval. Until then this project only reuses the concepts as local
schemas, fixtures and tests.
