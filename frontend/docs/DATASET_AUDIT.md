# Phase 02 dataset audit

Version: 1.0 | Checked: 2026-10-17 (Asia/Calcutta) | Dataset ID: D07

## Source and authority

Original: `C:\Users\ASUS\Downloads\treasury_4tier_dataset.csv`. Byte-identical archive: docs/sources/phase02/treasury_4tier_dataset.csv; SHA-256 and original byte count are in docs/sources/phase02/MANIFEST.json. The user explicitly requested analysis and changes to the plan using this file. That authorizes the present local descriptive review, not assumed public redistribution, model training rights, or claims of real institutional provenance. The user's schema description is source material; recommendations in the accompanying comparative audit are not accepted decisions.

The user describes one simulated calendar year. No generator, seed, original publisher, license, data-sharing contract, instrument specification or real institution is supplied. Treat the entire 2026 series as a simulated scenario, including dates after today's research date, not observed future financial data.

Actual checks used the bundled Python runtime with standard-library CSV parsing and Decimal money reconciliation. Results are retained in [DATASET_PROFILE.json](DATASET_PROFILE.json). No policy replay, optimizer, model fit, training, performance experiment or product code was run.

## Observed structure and quality

| Check | Observed result |
|---|---|
| Shape | 8,760 rows × 16 columns; user listed 10 fields, CSV supplies 6 additional fields |
| Date range | 2026-01-01 00:00:00 through 2026-12-31 23:00:00 |
| Coverage | Strictly sorted, 365 days × 24 rows; no duplicate dates/rows or non-hour steps |
| Missing/nonfinite | No blank cells; all 13 numeric columns parse and contain no nonfinite values |
| Flow signs | Deposits and withdrawals strictly positive; net can be positive/negative |
| Net consistency | Supplied net differs from deposits minus withdrawals by at most $0.01 per row; 2,118 such rounding differences, +$0.10 aggregate supplied-net residual |
| Repo entry flag | True on 365 rows, exactly hour 17, including 104 weekend entries |
| Repo maturity flag | True on 365 rows, exactly hour 08 |
| Timezone | Absent; naive datetime strings, no UTC offset or business calendar |
| Other metadata | No account IDs, arrival timestamps, opening cash/positions, trade records, obligations schedule, actual funding access, executed actions or outcome labels |

Keep source bytes unchanged. In a future simulation derive canonical net from the two gross USD fields using cents, retaining supplied net as a reconciliation field. Do not report the $0.10 yearly rounding difference as missing money or alter the raw file. Adopt a one-cent per-row input-reconciliation tolerance; computed ledger conservation should use exact cent arithmetic and explicit rounding rules.

## Fields, units, and implications

| Field(s) | Observed range / behavior | Interpretation and proposed use |
|---|---|---|
| timestamp | 8,760 hourly values, no gaps | One synthetic clock; start/end-of-hour semantics require a declared scenario |
| deposits_usd | $3,881,238.01–$37,777,699.02 per hour | Gross inbound flow, not starting cash or confirmed future available cash |
| withdrawals_usd | $3,251,685.47–$45,692,972.02 per hour | Gross clearing obligations; forecast separately from deposits |
| net_flow_usd (additional) | −$32,476,942.90 to +$24,130,707.41 | Redundant outcome/reconciliation field, never a same-hour predictor of either gross target |
| repo_sweep_window_open / repo_sweep_mature | 17:00 / 08:00 daily | Synthetic product schedule; not evidence of an actual bank repo agreement or rail hours |
| tier1_repo_rate_apy | 3.725–4.374 | Values appear in percentage points; divide by 100 in a declared accrual convention. Effective APY versus simple policy-rate quotation not independently specified |
| tier2_bond_yield_pct | 3.760–5.924 | YTM is not a realizable guaranteed hourly return or an additional coupon stream |
| tier2_bond_price_index | 97.841–101.997 | Clean synthetic price index; instrument coupon/accrual not supplied |
| tier2_bond_mod_duration (additional) | Constant 1.92 | Sensitivity input; not a training signal that varies in this file; don't add duration P&L on top of the actual observed index move |
| tier3_stock_index_price | 3,470.95–5,470.67 | Risky price series; index values alone do not establish tradable instrument/dividends or settlement rules |
| tier3_stock_volatility_pct | Constant 18.0 | Cannot learn volatility-regime response from this constant feature; not validated realized volatility |
| tier1_early_redemption_haircut_pct (additional) | Constant 0.5 | Scenario penalty, not proof early redemption is contractually available |
| tier2_bond_liquidation_haircut_pct (additional) | Constant 2.0 | Distinguish liquidation haircut from mark-to-market move; apply once to liquidation proceeds only |
| tier3_stock_liquidation_haircut_pct (additional) | Constant 15.0 | Same distinction; these assets cannot be counted as cash merely because a price exists |
| emergency_overdraft_penalty_apr_pct (additional) | Constant 12.0 | Scenario APR cost, not a facility limit, commitment or entitlement to unlimited borrowing |

These last six fields (net, duration and four penalty/haircut columns) materially improve simulation cost coverage versus the pasted schema. They do not resolve opening balances, facility capacity or instrument economics.

## Funding sufficiency changes the plan

| Descriptive calculation | Observed value |
|---|---:|
| Total deposits | $88,843,172,871.39 |
| Total withdrawals | $91,373,879,241.94 |
| Gross-derived annual net | **−$2,530,706,370.55** |
| Supplied net column sum | −$2,530,706,370.45 |
| Minimum cumulative gross-derived net from zero opening | **−$2,589,146,839.86**, at 2026-12-26 23:00:00 |
| Bond-index maximum observed peak-to-trough drawdown | Approximately 4.075% |
| Equity-index maximum observed peak-to-trough drawdown | Approximately 36.553% |

The cumulative figure is retrospective arithmetic: for a cash-only end-of-hour ledger, with no fees, yield, other assets or borrowing, at least $2,589,146,839.86 opening cash is needed to avoid negative hourly *closing* cash along this exact historical path. It is not a deployable reserve rule, an intrahour sufficiency guarantee, or a statistically estimated stress buffer. Withdrawal-before-deposit ordering within an hour may require more. Do not choose opening cash from this whole-year minimum and present that as a forecast-driven policy.

Therefore a small-buffer “sweep everything else” demo could be infeasible even with perfect forecasts. Proposed comparisons must retain original gross flows, opening endowment, finite facility cap and costs equally across policies. No reset of balances each day, free top-up, post-hoc deposit scaling or unlimited overdraft may manufacture feasibility. A deliberately unfunded case should correctly expose exhaustion. Any financed/funded case must be labeled as an assumption, not data-derived surplus or actual bank capital.

## Required scenario declarations before later simulation

1. **Funding/endowment:** opening cash, repo lots, bond/equity units, reserve floor, permitted exposure caps, finite facility limit and repayment terms. Distinguish these from flow totals and bank regulatory capital. Zero initial investment lots is the proposed neutral starting state; no 08:00 maturity creates cash without a real prior lot.
2. **Time:** propose row t = interval [t,t+1), decisions at the start of t using completed rows through t−1 only. Scheduled 08:00 maturity is processed only for existing positions; 17:00 entry locks until next 08:00 (15 hours). Use the dataset's synthetic clock; timezone unknown. No same-hour flows/prices/volatility as already-known predictors unless an alternative observation convention is explicitly declared and tested.
3. **Within-hour ordering:** conservative payout-before-deposit scenario and a separate netted end-hour sensitivity. The CSV cannot identify real intra-hour payment order. Do not advertise sub-hour coverage.
4. **Repo:** propose fixed entry-rate effective-APY accrual over actual locked hours; alternative simple-APR scenario if organizer clarification differs. Entry-rate versus variable-rate, day count, early redemption availability and haircut basis remain assumptions. No simultaneous free use of locked cash; early release is a scenario toggle, not implied by the column.
5. **Bonds/equities:** price-only marked scenarios until coupon/dividend conventions supplied. No automatic YTM/8,760 carry in addition to clean-price gains; no duration-shock P&L layered over observed price P&L. Record holdings, settlement delay, costs and liquidation haircuts once. Marked assets ≠ usable settlement cash.
6. **Boundary:** no phantom repo release at the first 08:00; no new lock with maturity beyond the file in the proposed conservative terminal rule. Show closing holdings/encumbrances and outstanding debt; do not liquidate at cost or write off debt to improve final wealth.
7. **Observation rights:** no true freshness, delayed arrival or reconciliation labels exist. Inject those into separate, labeled cases; synthetic record integrity must not be called independent asset verification.

These are proposed scope assumptions to be accepted or changed, not facts supplied by the dataset. No assumption gate was silently resolved in this audit.

## Training suitability and frozen evaluation proposal

The file can support **a simulated hourly-flow forecasting comparison**, not a real-bank forecast or a market-return forecasting claim. Gross flows provide potential labels for next-hour and path outcomes; no hand annotations are needed to sum future flows, but a reviewer must validate timing/availability semantics. Net flow is not a safe substitute for gross liquidity stress. No actual “safe sweep,” credit approval, loss event or optimal action label exists.

Proposed calendar partitions: development January–June, 4,344 rows; validation July–September, 2,208 rows; final evaluation October–December, 2,208 rows. Profile counts/ranges and whole-year funding diagnostics have been inspected, so the final interval is **not claimed blind to the analyst**. Freeze the selection plan and stop using final-set diagnostics for tuning; obtain an independent generator seed/year or real partner holdout before stronger generalization claims.

At each origin, include only fully observed history. Shift lag/rolling features; exclude contemporaneous deposits/withdrawals/net, future market prices and future rolling-volatility values. Fit preprocessing/quantiles on training only; tune on validation only. Purge 24-hour overlapping labels at boundaries and omit origins with incomplete future horizons. Use daily/weekly blocks for paired uncertainty analysis; hourly observations are dependent and are not 8,760 independent banking crises.

Branch T decision: **PROPOSED — experiment first**, not trained. Seasonal 24h/168h comparators and empirical path buffers first; small quantile ML/SARIMAX optional after rights/timing gates. Deep learning, learned ensembles, fine-tuning and training from scratch are not justified by this single simulated year alone. RAG does not predict numeric flows. Full branch terms and thresholds are in SOLUTION_DECISION.md.

## Environment and rights dependencies

Read-only module discovery in the bundled runtime found pandas/NumPy available but no SciPy, scikit-learn, statsmodels, PyTorch or Chronos module. This is availability discovery, not an environment installation or version-compatibility test. A later CPU experiment needs an isolated, pinned environment and local runtime/solver checks after selection; no download, model call or install was performed.

Human: confirm permitted local training/public sharing, synthetic origin/generator if available, timing/product terms and financial-policy assumptions. Agent: preserve hashes, profile, draft leakage-safe evaluation and later implement approved calculations. Hybrid: adjudicate ledger/economic semantics and the minimum meaningful improvement. No secrets are needed for this dataset-only work. Commercial rights, real institutional representativeness, pilot data, compute spend and external access remain unapproved/unknown.
