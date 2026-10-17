# Forecast evaluation and promotion

Blueprint 1.0 | T-EXP | No experiments performed

Authoritative financial and model go/no-go thresholds: SOLUTION_DECISION.md Section 7. This document owns evaluation procedure, not a competing set of numerical targets. MODEL_TRAINING_PLAN.md owns setup/task handoff; AI_DESIGN.md owns preprocessing/adapter behavior.

## Frozen protocol

Use D07 hash from source manifest. January–June development 4,344 rows; July–September validation 2,208; October–December frozen final 2,208 before purging. Entire-file structural/economic profiling already occurred, so final segment is not analyst-blind. Remove origins whose target horizon crosses a partition boundary; 24h purge at boundaries for shared-label leakage. Rolling origins in development; select lag/model/hyperparameters on development/validation only. Do not run repeated final-set selection. Save split/origin IDs before fitting, then version/freeze them.

Evaluate next-hour gross flows and 15h-to-repo-release/24h cumulative-deficit tasks as separate metrics. At 17:00, horizon 15 covers intervals 17 through next 07; history ends at 16. If a non-17 origin requests horizon15, label it rolling15 rather than a repo-release horizon. No future coupon/price/flow feature permitted. Sparse tail samples and dependent hours require event/day counts and paired day-block uncertainty estimates; zero observed shortfalls is not zero risk.

## Comparisons and metrics

Common data/endowment/limits/order/cost assumptions for all policies. Compare cash-only and fixed-floor repo without learned forecast; then seasonal24/168 and empirical path-buffer baseline; at most three model families total if an experiment runs. Pinball loss q=.90/.95, interval coverage/width, MAE and development-scaled MASE by target/horizon, fallback rate and latency. Record denominator, origins dropped and reason. No MAPE ranking on signed or near-zero net values; MASE undefined denominator is explicit unavailable.

Downstream ledger metrics come from ARCHITECTURE.md, not reimplemented in the notebook. Check unchanged risk/credit/exposure envelope, total unpaid/shortfall hours/peak debt, costs and treasury result. Fit a model only if its task could plausibly change a useful decision. Target model gate in accepted scope includes ≥10% pinball improvement, coverage screening and no worsening specified risk metrics; inconclusive uncertainty/fold instability means baseline-only release. Dollar materiality remains an open owner decision; do not tune it after final results.

## Evidence and failures

Each evaluation writes: configuration/split/features/model manifest, predictions keyed by origin/horizon, labels, per-fold/aggregate metrics with counts, latency samples, known failures, paired comparison and reviewer sign-off. Failing/timeout/nonconvergent model includes reason and effective fallback; do not pool fallback as if model succeeded. Recompute report metrics independently from saved prediction/label files. Artifact promotion changes manifest state EXPERIMENTAL → EVALUATED → REVIEWED_EXPERIMENTAL; it never grants live-money authority.

Adversarial/contract tests: current/future row in history, shift omitted, target in features, split-boundary windows, global fit transform, correlated repeated samples, missing/zero/infinite values, synthetic timestamp mismatch, model unavailable, future market value, wrong quantile ordering, negative gross prediction, changed dataset hash and mislabeled fixture. Trained outputs with an unknown version are rejected. Signing/evidence tests do not validate real balances.

Fresh generator seed/year or authorized real partner holdout is required before any generalization claim beyond the supplied scenario. No real-user/financial success can be inferred from passing this synthetic evaluation. FRONTEND must show experimental/fallback status without fake accuracy badges; BACKEND must maintain policy floors independently.
