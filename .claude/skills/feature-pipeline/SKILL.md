---
name: feature-pipeline
description: Use when building point-in-time market data / features / dataset snapshots and the feature-store approval gate. Enforces no look-ahead, versioned snapshots, and leakage audit. Leakage is the #1 silent killer.
---

# Point-in-time feature pipeline (→ feature-store approval gate)

> Bound by [`AGENTS.md`](../../../AGENTS.md). Every dataset is point-in-time correct,
> versioned, leakage-audited.

## When to use
Working in `market-data-engine`, `feature-engine`, or `feature-store-service`.

## Procedure
1. **PIT data:** a read "as of t" must NEVER return data with timestamp > t. Version
   snapshots with a deterministic content hash (`dataset_snapshot_id`).
2. **Features:** compute ONLY from data ≤ `as_of`; version the feature view; emit
   the `features` contract with lineage (`dataset_snapshot_id`, feature-view version).
3. **Leakage audit:** perturb data strictly AFTER `as_of` and assert features are
   UNCHANGED (a leaky function fails). The audit must have teeth.
4. **Feature-store approval gate:** the `features/feature_store_approval_gate`
   contract gates promotion — manifest exists, PIT correctness, leakage passed,
   feature availability, snapshot versioned. Refuse unversioned / look-ahead reads.

## Non-negotiables
- No look-ahead anywhere; no fabricated data (missing ⇒ flagged/empty, never invented).
- Datasets are versioned + leakage-audited before approval.

## Definition of done
- PIT + leakage tests green (incl. leaky-fails); approval gate wired; checks green.
