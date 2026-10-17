# Forecast adapter design

Blueprint 1.0 | Branch T-EXP experiment first | Adapter contract 1.0

Accepted scope includes investigation, not a production model or training rights waiver. No retrieval/generation/orchestration service is needed for structured D07. Use conventional baseline estimates first; traditional quantile ML is a gated experiment; SARIMAX secondary; pretrained time-series inference optional after access; fine-tuning/deep learning/foundation/RL training unjustified in minimum scope. Thresholds are authoritative in SOLUTION_DECISION.md Section 7, operational evaluation details in AI_EVALUATION.md.

## Flow and boundary

Approved historical rows → causal preparation → adapter family → predicted gross path and path-deficit quantiles → deterministic backend policy gate → decision/evidence. Estimates never execute actions or change obligations/cash. Adapter has no bank credentials/network/file-system authority. Request contains approved history, origin, required horizons, schema/version and data fingerprint; no future labels. The backend slices data before invoking the adapter, then verifies its returned origin/units/version. Family is `seasonal_baseline`, `quantile_experiment`, `sarimax_experiment`, `pretrained_experiment`, or `unavailable`, never a decorative model name.

Canonical executable specification is [forecast-adapter.schema.json](../contracts/forecast-adapter.schema.json). Baseline/experimental result includes effective family, artifact ID or null, quality label, predicted gross series, optional maximum-cumulative-deficit quantiles, warnings, origin and training cutoff. `unavailable` returns no predictions with a reason; backend selects explicit conventional fallback. No confidence percentages unless computed under the evaluated metric/version. Contract fixtures use `illustrative_fixture`, not measured accuracy.

## Preprocessing contract

Simulation row t describes interval [t,t+1); at origin t, only rows with timestamp <t. Dollar inputs are cents strings internally, fixed precision and nonnegative gross amounts. Timestamp/calendar in synthetic clock, no invented timezone. Unit/rate conversions handled by the shared input adapter; training features cannot silently reinterpret units. Schema tests reject simultaneous/future labels in history and unsupported horizon.

Candidate features: lags 1, 24, 168 for gross flows; shifted trailing 24/168-hour means/quantiles; hour/day-of-week calendar; historical observed market values only if justified by ablation. Net may be derived from lagged gross values but is not a current target predictor. Constant volatility/duration/haircut columns excluded from learned features for D07, retained as scenario assumptions. Missing history produces explicit unavailable/short-history fallback, not forward-filled future target labels. No global scaling/imputation before time split.

Path target is maximum cumulative net outflow over next horizon relative to origin, not sum of marginal gross quantiles; preserve correlation using training-only empirical path residuals or directly fitted deficit target. Marginal confidence intervals do not promise a probability of no payout shortfall. Pure calendar baseline repeats observed 24h/168h patterns and records chosen lag using development/validation only. Exact model parameters and preprocessing version enter artifact manifest if fitted; no trained weights delivered in Phase 03.

## Versioning, latency, fallback

Artifacts identify dataset hash, split manifest, feature/label version, model/library versions, parameters/seed, fit cutoff, evaluation report and approval state. Backend loads only allowed local versioned manifests; no arbitrary pickle upload. Reject schema/unit/origin mismatch; timeout/disabled/gate failure chooses baseline and records reason. Target warm batch p95 <5s on declared CPU, recorded actual machine/context sizes; not measured now. Financial arithmetic never waits for an unavailable model to invent cash. No hosted inference cost/latency assumptions in baseline.

Mocking boundary: FRONTEND uses contract fixtures explicitly labeled illustrative; BACKEND uses deterministic baseline/unavailable adapter; AI_ML can later replace internal function behind schema without changing screen contracts. Everyone tests the actual effective family and cutoff. The first application integration must work when Branch T is blocked; no module waits for training before implementing its own verified slice.
