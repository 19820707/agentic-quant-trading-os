---
name: model-predictions
description: Use when training/serving models or producing probability estimates in the deep-learning-engine. Predictions/probabilities ONLY — never orders, signals, or risk approval. No-look-ahead walk-forward, honest confidence, versioned lineage.
---

# Model predictions & probability estimates (predictions only)

> Bound by [`AGENTS.md`](../../../AGENTS.md). The engine ONLY produces predictions;
> outputs are probabilistic, NOT authoritative. No DL framework is installed unless
> explicitly requested — prefer a transparent, deterministic baseline (be honest).

## When to use
Working in `deep-learning-engine`; emitting `ml`/`research:probability_estimate`.

## Procedure
1. **Train** on point-in-time features (the `feature-pipeline` skill). Seed any
   randomness; keep it deterministic.
2. **No look-ahead walk-forward:** each fold trains on the PAST prefix only;
   evaluate out-of-sample.
3. **Honest confidence:** derive confidence from validated OOS skill; beat a naive
   baseline; record a drift baseline (for `model-monitoring`). A weak model reports
   low confidence — never a fabricated number.
4. **Lineage:** link `model_version` to `dataset_snapshot_id` + feature-view version
   (no duplicate versions). Emit a `probability_estimate` carrying lineage and the
   research chain id; never an order/signal field.

## Non-negotiables
- Predictions/probabilities only; never create orders, signals, or approve risk.
- No unvalidated model is promotable; no look-ahead; honest negatives.

## Definition of done
- Walk-forward + beats-baseline + lineage tests green; checks green.
