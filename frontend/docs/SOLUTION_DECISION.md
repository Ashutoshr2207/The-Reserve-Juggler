# Reserve Juggler — Phase 02 solution decision

Version: 1.1 | Selection recorded: 2026-10-17 (Asia/Calcutta)

**Selection status: ACCEPTED BY HUMAN-DELEGATED SELECTION. Option RG-02, unchanged scope 0.2.0, branch T-EXP experiment first.** The user delegated the choice in response to the exact named-option question; the agent selected this option. Exact human wording, interpretation and original scope hash are in SELECTION_RECORD.json. Phase 03/03A documentation is authorized by the direct request; product implementation/training is not claimed. Sections 6–9 retain the original accepted scope text, including its conditional experiment and unresolved gates. Prior Phase 02 version is preserved in docs/history/phase02/.


## 1. Recommendation and evidence

Recommend **RG-02 — Cash-first Four-Tier Treasury Replay with Decision Evidence**: an offline, single-currency policy-comparison tool that accounts for accessible cash, repo lock/maturity timing, marked bond/equity exposures, liquidation costs and finite funding, with reproducible decision records. Default policy may allocate only cash and repo; bonds/equities are explicitly separated risk scenarios. An optional, gated forecasting comparison can earn inclusion later. This merges credible concepts from the supplied projects while filling *their documented or supplied-snapshot* intraday evaluation gaps. It does not establish a market-unique product.

The supplied D07 data makes an evidence dashboard alone too narrow for the actual evaluation task. Conversely, the structural cash deficit and missing instrument/endowment terms make an autonomous four-asset yield optimizer premature. Recommend proving bookkeeping, funding sufficiency and honest policy comparison first. If buyers do not need this beyond a spreadsheet or existing TMS, stop or retain it as a learning/research tool rather than claiming a commercial treasury platform.

Supporting records: [dataset audit](DATASET_AUDIT.md), [actual profile](DATASET_PROFILE.json), [independent research amendments](PHASE_02_RESEARCH_AMENDMENTS.md). Labels: OBSERVED-FILE = our descriptive checks; VERIFIED-DOCUMENTED = opened primary documentation/code; SUPPLIED = user-provided report; HYPOTHESIS/INFERENCE/TARGET = unvalidated proposition/judgment/proposed threshold.

**Key evidence:** D07 contains 8,760 hours ×16 fields, including repo timing, prices, duration and penalties. Gross flows produce −$2,530,706,370.55 annual net, so investment cannot manufacture the missing principal. Initial endowment/credit rights are not data columns. These are descriptive facts, not a simulated policy result. The spreadsheet source remains unchanged.

**Independent counterevidence:** [Nilus's dated workflow](https://www.nilus.com/blog/bounded-autonomy-why-the-best-agentic-treasury-systems-still-need-you-in-the-loop/) documents approval gates and exportable action records; [Kyriba](https://www.kyriba.com/resources/fact-sheets/liquidity-performance-platform/) documents broad integrated treasury capabilities. Thus explanation, monitoring and audit logs alone cannot sustain the previous differentiation. Primary pages were opened 2026-10-17; vendor claims were not operationally tested. Exact equivalent offline replay in these products is unknown, not assumed absent.

No product code, forecast fit, training, optimizer, policy replay, interview or user prototype was executed in Phase 02. The only computation was source integrity and descriptive data profiling. S5's reported tests/results remain attributed to its author, not our experiments. No accepted selection was found in existing records; a request to merge concepts does not select this exact scope.

## 2. Named options, comparison, and disposition

Scores are skeptical reviewer judgments from 1 (weak) to 5 (strong), not measured performance, probabilities or user ratings. “Fit” refers to the supplied simulated dataset; commercial demand remains unconfirmed for every build. Do not add scores into an objective-looking winner without considering dependencies.

| Option | Mechanism | Dataset/task fit | Credible incremental value | Feasibility now | Adoption/maintainability | Decision / tradeoff |
|---|---|---:|---:|---:|---:|---|
| RG-00 — conventional baseline / existing tool | Cash-only plus fixed-floor/threshold repo sweeps; spreadsheet and ordinary review records; no learned prediction | 4 | 3 | 5 | 5 | **Retain as mandatory comparator and fallback.** Could be the best final choice if more machinery adds no benefit; does not explain all risky-tier tradeoffs without extra sheets |
| RG-01 — evidence-only overlay (Phase 01 M1) | Bind policy, inputs, allow/block/unknown and approvals into a replayable packet | 2 | 2 | 4 | 3 | **Merge into RG-02, reject as standalone assumed wedge.** Incumbent audit/workflow overlap is stronger than initial framing; balance authenticity remains unresolved |
| RG-02 — cash-first four-tier replay + evidence | Shared hourly ledger, product timing/costs, comparable policy/stress results and traceable decisions; T-EXP optional | 5 | 4 for evaluation; commercial unknown | 4 after assumptions agreed | 3 | **Recommend PROPOSED.** Closest to actual data/task; more work than spreadsheet; no automated live investment or claim of superior returns |
| RG-03 — forecast-led autonomous four-tier optimizer (broad M2) | Fit ensemble/deep models; optimize/rebalance risky assets automatically | 3 | 2 without measured lift | 1 | 1 | **Reject now.** Missing initial funding, product contracts and honest OOS results; adds modeling/operational risk. Preserve simple quantile experiment as T-EXP rather than mandate an ensemble |
| RG-04 — parametric funding/network extension (M3 / peer index) | Contract-triggered credit or multi-participant signal | 1 | Unknown | 1 | 1 | **Defer.** A penalty APR is not a lender, and no peer dataset/consortium exists. Simulated overdraft cost belongs in RG-02 without claiming actual backstop capacity |

Usefulness/impact: RG-02 could reveal when an apparent yield gain is financed by additional credit or risky asset appreciation, and why a sweep was blocked. Innovation is the bounded integration/evaluation contract, not new ML, optimization or signatures. Growth should follow one verified instrument/account adapter at a time; one synthetic year establishes no enterprise scalability, network moat or TAM.

Cost judgment [ASSUMPTION]: a later local technical proof plus honest report prototype might require 120–240 combined engineering/review hours at hypothetical $25–$75/hour ($3,000–$18,000). T-EXP adds roughly 16–40h ($400–$3,000) and capped local CPU experiments, excluding licenses. These are planning envelopes, not estimates validated against a known team or deadline. Current cost authority is none; local review did not purchase services. RG-00 is cheaper and should win if additional benefit is weak.

## 3. Which concepts merge, and which do not

| Supplied source concept | Proposed adaptation | Gap/error it addresses | Evidence boundary |
|---|---|---|---|
| P1 validation → forecast → balance → funding and chronological baseline | Keep module boundaries; forecast gross hourly deposits/withdrawals separately; evaluate availability paths, model/fallback identity and the same true horizons used by decisions | Daily net flows and one-shot funding hide timing/path effects | [P1 README](https://github.com/Andorta/LiquidityForecasting) independently documents its daily workflow; deeper S5 execution findings not rerun |
| P2 constraints, scenario economics and explanation | One liquidity/cost contract, finite funding, fail-closed allocation status, independent constraint residual checks and explicit stress narratives | A returned allocation must not imply a feasible optimum; capital and cash cannot be conflated | [P2 README](https://github.com/rvb10/Bank-Capital-Liquidity-Optimizer) independently establishes illustrative strategic scope; solver defects are S5 findings |
| P3 readable dashboard/report concepts | Clear policy comparisons, signed amounts, uncertainty/fallback labels, source/run-linked exports | Communication is useful only when displays reflect actual runs | [Opened P3 HTML](https://github.com/arham7s/cashlens-ai-treasury-forecasting/blob/main/index.html) shows future-actual-based curves; discard that mechanism |
| Reserve Juggler attestation concept | Evidence record for each simulated decision; integrity/replay as control properties | Makes comparison inspectable; cannot prove external assets | Internal reproducibility is not independent balance verification or solvency |

No entire project is selected as the product foundation. Public source/license pinning and narrow testing are prerequisites to any code reuse. P1's root lists MIT; P2 reuse rights are unresolved; P3's documentation license assertion needs artifact-level verification. No copied code or attribution obligation is silently assumed resolved. No single ML technique is implemented in all three projects.

## 4. Five weaknesses most likely to invalidate the proposal

| ID | Weakness / evidence | Consequence | Cheapest resolving experiment and proposed stop/change rule |
|---|---|---|---|
| W1 | **Funding and instrument assumptions may make the task infeasible.** D07 annual net is −$2.531B; opening assets/finite credit/coupon/settlement terms are absent; constant penalty APR is not a commitment | Any “safe surplus” or net-yield result could be an artifact of free capital, impossible redemption or unbounded debt | Human reviews one assumption sheet and a hand-reconciled 17:00→08:00 example (2–4h). Fail if cash/positions/credit cannot be defined consistently. Keep an intentionally underfunded case showing exhaustion; never reset cash or scale deposits to force success |
| W2 | **Pain and buyer are unconfirmed.** No interviews, institutional cases or sponsor provided; D07 is a participant-style simulated task, not demand evidence | May be useful only as an educational benchmark; no commercial willingness-to-pay claim | After separately authorized recruitment, 5 treasury/risk participants across ≥2 organizations compare one real anonymized decision and existing reports (8–16h). Stop commercial positioning unless ≥3 identify a recent relevant problem and one accountable sponsor sees a justified read-only evaluation |
| W3 | **Limited differentiation against actual workflows.** Nilus already documents explanations, approvals and exportable action records; Kyriba integrates treasury functions; spreadsheet suffices for many one-file tasks | M1-only wedge may not justify switching or new operating burden | Compare required evidence/replay tasks against current TMS configuration and RG-00; counterbalance ten cases (8–16h). Target ≥30% less reconstruction time with no more critical mistakes. If incumbent configuration provides equivalent value cheaply, integrate or choose RG-00 |
| W4 | **Synthetic-data/model advantage may not generalize.** One generated year; constant volatility/duration/penalties; no executed-action labels; P3's forecast display uses future outcomes; local ML libraries unavailable | A complex model can overfit the generator, leak labels or fail to improve a decision despite low mean error | Freeze T-EXP chronological splits/features and compare seasonal rules vs one small quantile model after rights/environment gates (16–40h). No-go ML if leakage, weak calibration, no decision improvement or unstable fold results; obtain independent seed/year before stronger generalization claims |
| W5 | **Operational/economic burden can erase gains.** No live data semantics, connector SLA, tenant permissions, deployment, support costs or verified coupon/fee model. Hourly data cannot prove intrahour safety | Apparent profit could be risky exposure, unpriced liquidity or costs omitted; usable production system much harder than a demo | Tabletop delayed deposit, missed maturity, denied credit, stale source and failed solver; common-accounting sensitivity sheet (8–12h). Fail on silent infeasibility or unknown funds counted as cash. Later adoption gate needs positive net value under declared fees/funding/maintenance and human-readable accessible workflow |

No experiment in this table has been performed. Time/participant counts are proposed low-cost bounds, not evidence of completed interviews or implementation.

## 5. User, pains, outcome, and provisional USP

**Primary evaluation user [PROPOSED]:** a treasury analyst/research participant comparing simulated reserve and allocation policies, with a treasury/risk reviewer responsible for interpreting assumptions. For a commercial version, the buyer would likely be a treasury leader/CFO at a fintech with controlled funds; that buyer and rights to invest customer assets are unverified. Depositors/payment recipients are indirect beneficiaries, not dashboard seats. No geography is selected; USD in D07 defines simulation units, not US legal authorization.

Pains prioritized: P01 insufficient accessible cash at obligation time; P02 misleading/stale/semantically wrong positions; P03 unreconstructable decisions; P04 idle-cash cost after risk; P05 ambiguous funding/transfer state; P06 adoption/review burden. Existing Phase 01 IDs remain stable. RG-02 addresses P01–P05 as *simulation/evaluation* problems; P06 must be tested with people.

**Outcome hypothesis:** identify a policy with better net treasury economics at the same declared funding/risk envelope, or establish that the conventional baseline is adequate, with reproducible reasons for each decision and all failures disclosed. A negative result is a useful outcome. No guaranteed yield, liquidity, compliance or model-accuracy claim.

**Provisional USP:** “Compare treasury policies on the same hourly cashflows and funding assumptions, with repo timing, liquidation costs and a replayable explanation of every decision.”

This is a bounded task proposition against P1's daily funding, P2's strategic balance sheet and P3's illustrative forecasts. It is not proof competitors lack similar functionality. Against Nilus/Kyriba and a spreadsheet, usefulness/price/switching incentive must still be demonstrated.

## 6. Exact proposed scope v0.2.0

This version is the acceptance unit. Any material addition to live execution, risky-asset allocation, AI release, geography, data rights or funding terms requires an explicit version change and decision record.

### Included workflows and capabilities

1. **Local dataset intake and provenance:** read unchanged D07; validate schema, sorted hourly continuity, numeric finiteness, flags, cents and gross-derived net; record hash, units and declared synthetic clock. New financial assumptions live separately from source data.
2. **Funding/availability model:** track Tier 0 accessible USD cash, Tier 1 repo lots locked 17:00→08:00, Tier 2 bond-index units, Tier 3 equity-index units, encumbrances, pending settlements, finite overdraft principal and cost. Never count inventory value as cash or debt as income. Tier numbering means investment layers, not regulatory capital tiers.
3. **Common conservative comparison:** RG-00 cash-only reference and threshold repo-sweep baseline. Recommended decision path uses **Tier 0 + Tier 1 only**. Tier 2/3 are **what-if stress portfolios with explicitly configured holdings/caps**, not automated return forecasts or suggested reserve investments. All four tiers appear in the analysis; zero exposure remains a meaningful default.
4. **Timing contract:** proposed row t = interval [t,t+1); decisions at start t use only completed data through t−1. Known schedule flags may be used as synthetic calendar rules. Evaluate conservative payout-before-deposit ordering separately from netted end-hour sensitivity. No sub-hour certainty. First-day 08:00 cannot release nonexistent positions; no new repo lock with maturity beyond the file under the conservative terminal rule.
5. **Declared economics:** effective-APY fixed-entry-rate repo accrual over actual hours is a provisional scenario; alternative simple-rate basis if terms clarified. Early repo release disabled by default despite supplied haircut; enabled only in a labeled scenario. Bonds/equities price-only unless coupon/dividend terms supplied. No YTM-plus-price or duration-plus-actual-price double count; apply liquidation haircuts once. Unknown fees/settlement delays are explicit inputs or sensitivity dimensions, not silently zero as real-world facts.
6. **Funding cases:** do not tune opening balance separately for each policy using hindsight. Include (a) underfunded illustration, e.g. $50M opening cash/zero credit; (b) declared funded illustration, e.g. $3B opening cash/zero credit; (c) a human-provided endowment and finite facility case if available. These round examples were suggested after file profiling for sensitivity, not independently prespecified or calibrated capital recommendations; all policies share each case's endowment. Reserve floor and exposure caps remain owner-defined inputs. Until supplied or explicitly approved as fictional assumptions, no safe/optimal allocation result is releasable. No actual backstop implied by the 12% APR column.
7. **Stress and failures:** delayed deposits, withdrawal shocks, unavailable repo/late maturity, policy conflicts, stale/missing sources and denied/exhausted credit as separate labeled synthetic injections. Reject infeasible optimizer outputs; any future solver is an implementation choice, not a scope requirement. A simple rule can win.
8. **Evaluation/reporting:** same-clock comparisons of gross flows, usable cash, holdings, equity value, net external flows, debt, accrued interest, liquidation costs, unpaid obligations and terminal wealth. Report shortfall count/duration/amount, minimum available cash, peak/mean debt, transaction count/cost and net treasury result, with benchmark/scenario identities. No synthetic model cards or fixed accuracy badges.
9. **Decision evidence:** hash/version of data and assumptions, decision origin and available history, policy/model/fallback version, proposed action, limits/evidence quality, feasible/blocked/unknown result, actor label and reconciled consequence. Typed records/templates first; digital signing is optional only if verification adds measured value. Never call internal history an externally verified proof of reserves.
10. **Optional branch T-EXP:** limited local comparison of seasonal/statistical flow estimates and one small quantile ML candidate; pretrained model only if separately accessible/approved. Results stay experimental and cannot authorize investments. No ML dependency in core arithmetic or baseline usability.

### Roles, accessibility, and capacity

- Analyst/maker: load a permitted file, propose fictional settings, compare scenarios. Reviewer/policy owner: approve assumption versions and interpret results. Auditor/evaluator: read/export a run. Runtime maintainer: dependency and integrity checks. These are local workflow roles; naming them does not implement secure authentication, segregation of duties or banking permissions.
- Proposed local demonstration: one dataset, one currency, one analyst and one reviewer, at most two simultaneous review sessions; 8,760 source rows are a volume, not a user count. No tenant, bank API, streaming or enterprise concurrency claim. Later proof target: reproducible baseline year replay within 60s on a declared CPU machine; optional forecast batch p95 <5s after warmup. These are untested targets with hardware disclosure, not measured capacity.
- Reports must preserve negative signs, readable units/timestamps, keyboard navigation and text statuses alongside colors; support tabular export and show unknown values without converting them to zero. Accessibility conformance requires later evaluation, not claimed now.

### AI decisions and non-goals

**Prediction:** T-EXP only, subject to Section 7. **Retrieval:** structured policy/run lookup; no RAG corpus need established. **Generation:** templates; no LLM needed in minimum scope. **Orchestration:** explicit state transitions; no LangGraph/agent layer required for one file. **Automation:** deterministic validation, arithmetic and replay, not autonomous financial authority. **Extraction/multimodal:** unnecessary for this structured CSV. **Hardware:** existing CPU evaluation; no device/HSM procurement need established.

Excluded: live money movement, bank/custodian connectors, actual lending/insurance, custody, tokenization/blockchain/MPC consortium, autonomous stock/bond trading, capital/LCR/NSFR/SIMM/RAROC engines, market-return prediction, foundation-model development, production authentication/security certification, regulatory approval, guaranteed liquidity, commercial-readiness claims and automatic data/model downloads. No paid API/cloud/compute budget is approved.

### Dependencies and unresolved constraints

Human financial-policy owner must declare endowment, reserve floor, credit cap, eligible exposures and instrument/accrual/settlement conventions. Human rights owner must confirm original data/code licenses and allowed training/sharing. Agent can implement only after selection and subsequent applicable authorization. Team, actual skills, deadline, business buyer, budget, target geography and deployment context remain unknown. Scope is deliberately a local research/prototype candidate under labeled scenarios; it cannot satisfy a live-bank request without a new scope.

## 7. Optional branch T — explicit dataset/model decision

**Branch ID T-EXP; status PROPOSED; disposition EXPERIMENT FIRST; suggested owner Hybrid.** This branch is optional within v0.2.0, not a condition that the core product must contain ML. Acceptance endorses investigation of the branch; it does not waive rights, runtime or release gates. No trained model selected, trained, downloaded or evaluated.

### Data, rights and quality

- Primary candidate is D07, the supplied CSV; local access/profile verified. Human supplied a simulated-data description but no publisher license, generator/seed, redistribution terms or explicit commercial/model-training rights. Local requested analysis is authorized; do not infer broader rights. Do not replace D07 with NN5 or reuse S5 metrics. D01 real-partner data and an independent synthetic seed/year remain unavailable.
- Labels: next-hour gross deposits/withdrawals; for decision risk, future maximum cumulative net outflow over each lead to maturity (15h from 17:00) and 24h. Derive labels only within the matching partition. No optimal-allocation, solvency or real credit-approval labels. No fabricated model scores. Human reviewer confirms semantic labels, not thousands of manual annotations; initial review target 50 intervals plus all special boundaries.
- One year has a small number of seasons/crises, not 8,760 independent rare-event examples. Constant volatility/duration/haircuts have no within-file predictive variance. No distributional claim about real markets; scenario stress remains synthetic.

### Minimum model comparison and choice

| Technique | Role / decision | Why |
|---|---|---|
| No trained model: seasonal 24h/168h forecast, empirical historical path buffer and fixed rules | **Mandatory comparison within T-EXP**, when/if it runs | Low burden; tests whether learning is necessary. Choose lag using development/validation, not final test |
| Traditional quantile ML (small gradient-boosting or quantile regression) | **First fitting candidate**, not selected winner | Suitable structured hourly labels; cheap CPU; can model asymmetric error. Model family/library finalized only after accepted experiment setup |
| SARIMAX | **Secondary statistical comparator if justified**, not copied P1 settings | Legitimate seasonal model, but hourly horizons need appropriate specification; cap tuning effort |
| Pretrained time-series AI such as Chronos-2 | **Optional inference comparator; defer download/access** | [Publisher model card](https://huggingface.co/amazon/chronos-2) supports a relevant pretrained alternative; task lift/overlap/access unknown. Do not assume generic chat model required |
| Pretrained LLM / RAG | **No predictive role in minimum scope** | No document corpus or language task requiring them; retrieval cannot estimate future numeric cash paths by itself |
| LSTM/Transformer trained locally, learned ensemble, fine-tuning | **No-go now** | Single simulated series/year and no demonstrated simple-model deficiency; extra hyperparameters/compute weaken evidence. Reconsider only with more independent data and a measured gap |
| Foundation training from scratch / RL policy agent | **No-go for v0.2.0** | No justified corpus/environment/reward/budget or safety case; not needed for accounting and rule comparisons |

### Leakage controls, metrics, feasibility gate

Proposed split: January–June 4,344 rows for development; July–September 2,208 validation; October–December 2,208 final evaluation. Whole-file structure and funding totals were already profiled, so call this a **frozen final evaluation segment, not an analyst-blind holdout**. Use rolling origins within development, remove origins whose future labels cross boundaries, and purge a 24h overlap at each split. Parameter/calibration choices use development/validation only; no fitting/scaling on final rows and no tune-to-test ensemble. Preserve raw identities and prediction origins. Require a fresh seed/year or external holdout for any generalization claim beyond this scenario.

Shift every lag/rolling feature; current-hour gross/net outcomes are not available at start t. Scheduled flags/calendar can be known in the synthetic clock; future bond/equity prices or volatility cannot. At each origin evaluate predictions on exactly the horizon used by the decision; per-step marginal intervals do not establish probability of avoiding *any* path breach. Use empirical calibration of path shortfall targets, with clearly uncalibrated stress cases kept separate.

Proposed metrics: per-target/horizon MAE/MASE (development-fitted scaling), pinball loss at q=0.90/0.95, interval coverage/width, path-quantile calibration, fallback count; then unpaid obligation count/duration/amount, debt/interest/haircuts and net treasury cost at the same funding envelope. No MAPE ranking of signed/near-zero net flow. For q=.95, target validation/final empirical path coverage in 92–98% as a screening band, report sample counts and day-block uncertainty; this is not a regulatory risk tolerance or guarantee.

**T experiment go/no-go targets:** zero known leakage; complete origin/prediction/model records; ≥10% lower final pinball loss versus the strongest frozen simple baseline; no worse unpaid amount/duration, no larger peak overdraft, and improved all-in economics in the same eligible funding cases. Prefer paired day-block uncertainty estimates; if improvement is not stable across temporal folds or uncertainty includes no gain, mark inconclusive and release the conventional baseline only. Calibration failure, unavailable rights/setup, generator dependence or no policy benefit = no-go ML in MVP. Do not relax criteria after seeing final performance.

No percentage-economic improvement threshold is meaningful when baseline treasury cost is zero/negative; agree a positive dollar materiality threshold before evaluation. For positive-cost baseline cases, proposed ≥5% cost reduction after interest, haircuts, fees and support assumptions is a practical screen, not achieved ROI. Losses from risky Tier 2/3 scenarios cannot be offset against a safer baseline without matched exposure/funding constraints.

**Compute/setup:** bundled module discovery found pandas/NumPy but not SciPy/scikit-learn/statsmodels/PyTorch/Chronos. After acceptance and rights confirmation, propose an isolated pinned CPU environment with license/solver checks; 4–8 cores/16GB RAM is an initial sizing assumption, not verified hardware. Cap first model-family fitting/comparison at 8 CPU-hours and ≤3 families including statistical choices; no GPU or external APIs needed. If cloud ever proposed, hypothetical $0–$1/CPU-hour yields $0–$8 compute, excluding labor/data/licenses; that is a cost envelope, not spending approval. Failure to finish within cap triggers simplification, not uncontrolled search.

**Responsibilities:** Human owns rights, timing/economics, risk limits and approval of claims; Agent owns approved profiling, causal features, reproducible experiment artifacts and honest failure reporting; Hybrid signs off evaluation interpretation. Current human owner is the requesting user; actual domain/rights specialists not assigned.

**Release implications:** successful synthetic experiment supports an experimental forecast feature only. Failed/inconclusive T leaves RG-02 fully usable with conventional policy rules and explicit fallback. No model influences live funds. Further real-data validation, governance, monitoring, security and explicit scope approval are required for pilot/production. T changes the evaluation evidence, not the truth of external balances.

## 8. Distinguish proof, prototype, demo, MVP, pilot, production

All stages below are future requirements; none was completed in Phase 02.

| Stage | Purpose and required evidence | Does not establish |
|---|---|---|
| Technical proof | Reviewed cash/position/credit invariants, repo lot/timing/boundary cases, penny reconciliation, matched baselines, explicit infeasibility; signed record only if needed; optional T has real prediction manifests | Usability, market demand, real-world accuracy or fund availability |
| User prototype | Inspectable assumption input, policy comparison and decision explanation; counterbalanced reviewer tasks; keyboard/text/negative-sign checks | Working model, validated economics or secure financial permissions |
| Demo | A clearly labeled frozen synthetic run showing normal operation, withdrawal shock, locked/late funds and blocked/unknown state; every displayed metric tied to the run | Production reliability; a scripted demo is not independent validation |
| MVP | End-to-end local CSV intake/replay/report with reproducible runs, conventional baselines and tested failures; optional model excluded unless T gates pass; clear parameter ownership | Permission to operate a bank, accept deposits or trade customer assets |
| Read-only institutional pilot | Named sponsor and consenting users; rights-cleared real historical data; source reconciliation, security/retention review, policy owner approval, incumbent comparison and measured benefit | Autonomous execution or general institutional fit |
| Production | New accepted scope; contractual bank/facility/instrument integrations, legal applicability, access controls, credential/key lifecycle, reconciliation, idempotency, observability, recovery, incident/support ownership, capacity and accessibility testing, risk/model governance | No production guarantee can be inferred from passing any earlier stage |

## 9. Validation thresholds and stop/change conditions

- **V01 accounting/funding:** every hand-reviewed case conserves cash/positions/debt to declared cents; no nonexistent maturity, reused locked cash, free credit, lost terminal debt or infeasible recommendation labeled valid. Any failure blocks policy comparisons. The $0.01 source-net tolerance does not excuse internal conservation errors.
- **V02 policy benefit:** same starting endowment, external cashflows, transaction/settlement rules, exposure caps and credit cap across policies; target no worse unpaid count/duration/amount or peak debt and improved net economics under the owner-declared risk envelope. No benefit established = choose RG-00 or narrow to educational analysis.
- **V03 buyer/prototype:** W2/W3 criteria met with authentic cases and consent before a commercial claim. If only participants/judges find it useful, label its market accordingly; do not invent a fintech buyer.
- **V04 training:** apply T-EXP gates unchanged; failed T does not block a no-AI core. No extra models to compensate for unsupported labels or generator dependence.
- **V05 feasibility/operations:** surface missing settings and unavailable funds explicitly; no output may silently imply coverage. Later CPU target and accessibility checks must pass before claiming demo/MVP readiness. Missing runtime, rights, policy owner or known terms blocks only the dependent activity; it does not retroactively invalidate the documented review.

Proceeding without these conditions risks a convincing but financially incoherent demo, performance inflated by leakage, mistaken bank-compliance claims, or an expensive duplicate of incumbent capabilities. Failing a gate must change scope or stop the claim, not merely add a disclaimer to a success dashboard.

## 10. Selection record and Phase 03 handoff

| Field | Recorded value |
|---|---|
| Selected option | RG-02 — Cash-first Four-Tier Treasury Replay with Decision Evidence |
| Accepted scope | 0.2.0, unchanged Sections 6–9; original file hash and scope-region hash in SELECTION_RECORD.json |
| Branch T | T-EXP experiment first; optional model, no training performed; rights/setup/release gates retained |
| Acceptance basis | Explicit human delegation in response to the named selection question; agent selected unchanged recommendation |
| Human reply (verbatim) | “do whatever u think will be giving the best output for unique project , from existing solutions” |
| Status | ACCEPTED by delegation; no repeat selection request needed |
| Authority | Phase 03 blueprint and Phase 03A assignments/packets; Phase 04 implementation remains next task |
| Integrator | Proposed BACKEND teammate also coordinates product acceptance; actual person unassigned; no fourth member |
| Evidence gaps | W1–W5 and A09–A13 remain open; selection does not certify financial assumptions, rights, installed tools or live operations |

The record does not assert the human typed the exact option acceptance phrase. The direct reply delegates judgment; current choice and unchanged scope are made explicit in the handoff. No material new scope is accepted through implementation detail. Previous waiting-for-selection state is historical, preserved in the prior version. Phase 03/03A records and packet references are in PROJECT_STATUS.md.
