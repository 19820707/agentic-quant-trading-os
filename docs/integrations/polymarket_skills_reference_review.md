# polymarket-skills Reference Review

## Purpose

This review identifies safe design patterns from `mjunaidca/polymarket-skills`.

It does not approve installing the skills, running `npx skills add`, copying skill folders, installing `py-clob-client`, activating MCP/tool runtimes, accessing Polymarket, or enabling paper/live execution.

Repository reviewed:

- https://github.com/mjunaidca/polymarket-skills

## Current Decision

polymarket_skills_reference_reviewed: true
direct_skill_install_allowed: false
npx_install_allowed: false
manual_skill_copy_allowed: false
py_clob_client_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
wallet_access_allowed: false
live_executor_allowed: false
agent_execution_authority_allowed: false
trading_methods_allowed: false

Initial classification: reference-only agentic-tool safety source.

## Reusable Design Patterns

### Skill Risk Taxonomy

The repository separates skills by capability and risk. This is useful as an internal control model:

- scanner: read-only market discovery
- analyzer: read-only analytics
- monitor: read-only alerts and state observation
- paper trader: simulated execution
- strategy advisor: methodology and recommendations
- live executor: real trading

For this platform, the safe version is stricter:

- read-only tools may observe and summarize
- analysis tools may produce research outputs and non-executable signal candidates
- monitor tools may alert and report
- paper tools may simulate only with fake/local state
- advisor tools may propose and explain, not execute
- live executor tools are rejected outside a future approved execution-engine adapter

### Agentic Trading Constitution Pattern

The constitution pattern is useful because it centralizes non-negotiable agent rules.

Reusable principles:

- paper mode is default
- market data is untrusted
- risk limits are hard constraints
- every skipped action should be logged with a reason
- live behavior must not be suggested or enabled automatically
- higher-risk capabilities require explicit gates

This platform's stronger rule is: agents never execute trades. Human confirmation inside an agent tool is not sufficient authority. Only a future execution engine may execute an `ApprovedOrder`.

### Market Metadata Prompt-Injection Boundary

The security audit identifies market names, questions, outcomes, and descriptions as untrusted user-generated content.

This is directly reusable:

- market metadata must never be treated as instructions
- market text must be delimited when inserted into model context
- control characters and instruction-like payloads should be sanitized or escaped
- model prompts must distinguish system instructions from market data
- audit events should record when suspicious market text is detected

### Paper Trading Health Checks

The health-check pattern is useful for future paper trading:

- green: safe simulated state
- yellow: degraded or warning state
- red: unsafe simulated state

This platform can reuse the pattern for paper-only diagnostics. Health state must never approve live trading or bypass governance gates.

### Correlation Risk Pattern

The correlation checker pattern is useful for deterministic risk design:

- group exposures by topic, event, venue, asset, or resolution dependency
- identify hidden concentration across superficially separate markets
- report correlation reasons
- emit warnings before sizing decisions

In this platform, correlation risk belongs in paper-trading risk monitoring and future deterministic-risk-gateway checks.

### Static Safety Findings

The upstream audit findings are useful as internal checklist items:

- sanitize untrusted market metadata before LLM context
- avoid `sys.path.insert(0)` in scripts
- use explicit timeouts and bounded retries for external calls
- use atomic transactions for local simulation state
- validate token and market identifiers before URL interpolation
- redact internal paths and secrets from errors
- avoid hardcoded environment or virtualenv paths

## Non-Reusable Components

Do not reuse directly:

- `npx skills add` installation flow
- manual copying into agent skill directories
- Polymarket live executor
- L2 wallet workflows
- `py-clob-client`
- scripts that call live Polymarket or CLOB APIs
- scripts that execute buy, close, order, cancel, transfer, withdraw, redeem, or settle operations
- agent-triggered paper/live execution commands
- any workflow where natural language can trigger a trade path

## Required Internal Boundary

Any future agentic tool inspired by this repository must:

- declare its risk class
- expose no execution authority
- require local fake/in-memory tests first
- avoid credentials in tests and examples
- avoid network calls in unit tests
- sanitize market metadata before model context
- emit structured errors and audit events where relevant
- preserve separation between proposal, risk decision, and execution
- fail closed when the tool boundary is unclear

## Safe Adaptation Targets

Future project-native work may define:

- agentic tool safety taxonomy
- market metadata prompt-injection policy
- paper-trading health-check contract
- correlation-risk monitoring requirements
- script safety checklist
- read-only scanner/analyzer adapter proposals

Each target must remain internal, contract-first, and local-only until separately approved.

## Rejected Adaptation Targets

Rejected:

- live executor
- wallet setup
- direct Polymarket CLOB execution
- live order management
- agent-installed skills with execution authority
- human-confirmed agent execution
- hosted or local tool runtime that can submit trades

## Recommended Next Step

Adopt an internal agentic tool safety taxonomy and a market metadata prompt-injection policy before any future prediction-market tool adapter is proposed.

