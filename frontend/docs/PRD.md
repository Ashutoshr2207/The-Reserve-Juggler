# Reserve Juggler — master PRD and coding-agent context

PRD 1.1 | Handoff revision 1.1 | 2026-10-17 | Accepted option RG-02, scope 0.2.0; T-EXP experiment first


## Start here: what we are building

Reserve Juggler is a **local treasury-policy simulator and evidence viewer**. It helps an analyst answer: “Given these hourly deposits, withdrawals, opening funds and investment rules, could this policy pay its obligations, what did it cost, and why was each investment allowed or blocked?” It does not operate a bank or move money. The product is the shared, reproducible comparison and decision explanation; forecasting is an optional input to evaluate.

**Current state:** Phase 00 intake, Phase 01 research, Phase 02 independent review, Phase 03 blueprint and Phase 03A assignments are complete. No product implementation, policy backtest, trained model or user validation exists. One illustrative interface fixture exists. This PRD update is a handoff clarification, not a new scope or authorization to build all modules in one agent. Accepted choice is RG-02 / scope 0.2.0 / optional T-EXP experiment first. The user's delegated acceptance is recorded; do not ask them to select it again. Historical “PROPOSED” passages in preserved research/accepted scope describe their original phase; current selection is authoritative.

This file owns **product intent, FR/NFR/AC requirements and the navigation to every implementation authority**. It gives a coding agent the context to begin; detailed schemas, screen rules and accounting rules remain in their canonical files, linked below. Send the complete folder/ZIP with this PRD. Sending only this Markdown file loses the executable interface specifications and evidence. Original wording stays in PROJECT_CONTEXT and source archives, separate from this synthesis.

## Users, pain and intended outcome

| Participant | Job and access | Evidence boundary |
|---|---|---|
| Analyst / research participant | Import simulated data, declare assumptions, compare policies, inspect decisions | Primary local evaluation user; no actual recruited user evidenced |
| Treasury / risk reviewer | Inspect scenario revision, acknowledge fictional assumptions, review limits and outcomes | Local workflow role; not proof of institutional approval |
| Auditor / evaluator | Inspect/export reproducible run evidence | Read/export role; not external asset attestation |
| Operator | Maintain one local workspace and runtime | OS/local boundary; production identity/tenancy excluded |
| Future buyer / indirect beneficiaries | Possible treasury leader/CFO; depositors/payment recipients may benefit indirectly | Buyer, demand, geography and impact unvalidated; not current seats |

P01: insufficient accessible cash when obligations clear. P02: misleading/stale data or misunderstood asset availability. P03: inability to reconstruct a decision. P04: avoidable idle-cash cost after funding/risk costs. P05: ambiguous settlement/funding states. P06: review/adoption burden. These are stable research IDs, not validated interview findings. The intended outcome is a defensible matched-policy choice, including a finding that the simple baseline is sufficient. USD is the simulation currency; target geography, team identities, budget and deadline remain unknown.

## Source ideas, merger and provisional differentiation

| Input / alternative | Keep or compare | Revise / exclude |
|---|---|---|
| LiquidityForecasting / supplied P1 | Chronological forecast–balance–funding separation and simple baselines | Use hourly gross flows and true decision horizons; do not assume daily settings or audit results were reproduced |
| Bank-Capital-Liquidity-Optimizer / supplied P2 | Explicit constraints, scenarios, cost visibility and independent feasibility checks | No capital/regulatory engine; no claim a solver output proves liquid cash or optimality |
| CashLens / supplied P3 | Readable dashboard and report ideas | Do not copy future-actual-derived forecast curves or call them a trained model |
| Reserve Juggler evidence concept | Bind decision to inputs, policy, assumptions and outcome | Integrity does not prove real balances, solvency or contractual fund access |
| Spreadsheet / RG-00 | Mandatory cash-only and fixed-floor repo comparator | Must be allowed to win if the new workflow adds no benefit |
| Nilus / Kyriba | Named incumbent comparison; substantial workflow/approval/audit overlap | Unknown capabilities stay unknown; audit logs alone are not differentiation |

Provisional USP: **compare cash availability, repo locks, finite funding and risky what-if exposures under one ledger, then replay why a decision happened**. This is an integration and evaluation hypothesis, not a proven market-first claim. Evidence, source links, counterarguments and five invalidators are in [SOLUTION_DECISION.md](SOLUTION_DECISION.md) and [PHASE_02_RESEARCH_AMENDMENTS.md](PHASE_02_RESEARCH_AMENDMENTS.md). No repository code has been adopted; source licenses/versions must be checked before reuse.

## Dataset and financial meaning: read before coding

D07 is the supplied **simulated 2026 year**, 8,760 hourly rows ×16 columns, not live/future-observed banking data. It is archived unchanged at `docs/sources/phase02/treasury_4tier_dataset.csv`; identity, quality, units and calculations are authoritative in [DATASET_AUDIT.md](DATASET_AUDIT.md), [DATASET_PROFILE.json](DATASET_PROFILE.json) and [source manifest](sources/phase02/MANIFEST.json). SHA-256: `2e7c1d2e5b678e9975250211e7e0017022049c510e1dd90cd7f29e931837b0c5`.

| Data group | Actual columns | How to interpret |
|---|---|---|
| Clock and flows | timestamp; deposits_usd; withdrawals_usd; net_flow_usd | Hourly gross flows are not opening cash. Derive canonical net from gross cents; supplied net is reconciliation only |
| Repo | repo_sweep_window_open; repo_sweep_mature; tier1_repo_rate_apy; tier1_early_redemption_haircut_pct | Synthetic 17:00 entry / 08:00 release schedule; a flag does not create an existing lot or contractual early access |
| Bonds | tier2_bond_yield_pct; tier2_bond_price_index; tier2_bond_mod_duration; tier2_bond_liquidation_haircut_pct | Price-only what-if exposure; yield is not a second coupon stream; do not double-count duration and observed price changes |
| Equities | tier3_stock_index_price; tier3_stock_volatility_pct; tier3_stock_liquidation_haircut_pct | Risky marked assets, not immediately spendable reserves or established tradable contracts |
| Funding | emergency_overdraft_penalty_apr_pct | Borrowing cost assumption, not proof of facility availability or unlimited credit |

The initial description listed ten fields; use the actual sixteen-column file. Gross annual deposits minus withdrawals is **−$2,530,706,370.55**. This is descriptive arithmetic, not a strategy result. Investment returns cannot replace absent principal. The dataset supplies no opening cash/holdings, reserve floor, finite credit authorization, full instrument terms or intra-hour order. Require explicit scenario inputs or acknowledged fictional settings; never choose opening cash from the full future path and then claim a predictive success. Rates, percentage units, penalties and settlement conventions follow the audit/architecture, not guesses from column names. Data/model-training and broader sharing rights remain unresolved; do not publish the source publicly.

The four tiers are accessible cash (tier 0), repo (tier 1), bonds (tier 2), equities (tier 3). Default allocation uses cash/repo. Bonds/equities are separate capped price-only what-if cases. Whether a tier is marked valuable differs from whether its proceeds are available before payouts. Missing funds, debt and unpaid obligations stay visible.

## End-to-end product behavior and first build outcome

1. **Data:** import/validate CSV and show profile/hash or useful row/field errors.
2. **Scenario:** declare endowment, reserve, credit, timing, costs and caps; unknown mandatory values block runs.
3. **Review:** acknowledge a versioned scenario; edits create another draft, preserving prior evidence.
4. **Compare:** execute conventional policies under identical assumptions; show shortfalls, debt, costs and terminal positions. A completed calculation may correctly report unpaid obligations.
5. **Decision:** open an hour to inspect usable cash, encumbrance, information cutoff, action/blocked reason and consequence.
6. **Evidence:** export inputs/versions, assumptions, signed amounts, metrics and warnings with hashes.

Screens, loading/empty/error/recovery states, responsive behavior and backend validation are authoritative in [DESIGN.md](DESIGN.md) and [FLOW.md](FLOW.md). No fake success on upload, client-calculated finance, hidden negative amounts or mock metrics labeled as real results.

First Phase 04 milestone: FRONTEND + BACKEND + AI_ML connect one **real 24-hour conventional vertical slice**, including terminal repo blocking and explicit unavailable/baseline adapter. Then expand to the year, stress and what-if cases. The current [first-slice fixture](../contracts/examples/first_slice.json) is illustrative contract data, not an executed ledger. Stage gates below and SOLUTION_DECISION Section 8 distinguish proof, prototype, demo, MVP, pilot and production; a demo does not satisfy them all automatically.

## Engineering and AI decisions in plain language

Blueprint implementation choice: React/TypeScript frontend, Python 3.12/FastAPI backend, SQLite local storage, exact posted cents, one worker and a typed forecast adapter. Exact dependencies/build versions must be pinned and tested during setup; no product runtime has been installed. These choices support separate ownership and deterministic comparison. Technology freedom permits alternatives only through reviewed decisions, not silent contract forks.

One backend ledger owns finance; the browser displays it; the AI_ML adapter returns estimates only. Decisions at origin t use completed history before t, not row t outcomes or future prices. Repo principal must leave/return once at the correct lock/maturity; marked prices are not settled cash; credit is finite; terminal debt/unpaid obligations remain liabilities. Exact invariant and metric definitions are owned by [ARCHITECTURE.md](ARCHITECTURE.md).

Minimum scope requires **no LLM, RAG, agents, hosted AI, fine-tuning or from-scratch training**. Conventional causal seasonal/history estimates and fallback come first. Optional T-EXP compares a small quantile model, with SARIMAX secondary and pretrained time-series inference optional after access. Fitting requires recorded rights/label/timing/runtime gates; model inclusion requires frozen evaluation criteria. No trained weights or accuracy results exist. See [AI_DESIGN.md](AI_DESIGN.md), [AI_EVALUATION.md](AI_EVALUATION.md) and [MODEL_TRAINING_PLAN.md](MODEL_TRAINING_PLAN.md). Start Branch T preparation alongside app work; it must not block the conventional slice.

## Coding-agent source-of-truth map

| Question | Authoritative files |
|---|---|
| What instructions apply; what was originally supplied? | [root AGENTS](../AGENTS.md), [PROJECT_CONTEXT](../PROJECT_CONTEXT.md); immutable docs/sources/ archives |
| What is selected; why; what is still unknown? | [SOLUTION_DECISION](SOLUTION_DECISION.md), [SELECTION_RECORD](SELECTION_RECORD.json), [DECISIONS](DECISIONS.md) |
| What must the product do and how is it accepted? | This PRD, FR/NFR/AC IDs below |
| What research supports or challenges it? | [RESEARCH](RESEARCH.md), [AI_OPPORTUNITIES](AI_OPPORTUNITIES.md), [amendments](PHASE_02_RESEARCH_AMENDMENTS.md), [SOURCE_LOG](SOURCE_LOG.md), [EVIDENCE_LEDGER](EVIDENCE_LEDGER.md) |
| What do data/finance/storage/time mean? | [DATASET_AUDIT](DATASET_AUDIT.md), [DATASET_PROFILE](DATASET_PROFILE.json), [ARCHITECTURE](ARCHITECTURE.md) |
| Which screens, states and validations must match? | [DESIGN](DESIGN.md), [FLOW](FLOW.md); both frontend and backend must follow DESIGN |
| What are exact HTTP/forecast fields and errors? | [API_CONTRACT](API_CONTRACT.md), [OpenAPI](../contracts/openapi.json), [adapter schema](../contracts/forecast-adapter.schema.json); machine specs own field shapes |
| What permissions and data boundaries apply? | [AUTH_SECURITY](AUTH_SECURITY.md); local OS boundary, no invented production tenancy |
| What AI work is allowed and how is it evaluated? | AI_DESIGN, AI_EVALUATION, MODEL_TRAINING_PLAN; financial/model gates in accepted scope Section 7 |
| What should each teammate implement/review? | [TEAM_PLAN](TEAM_PLAN.md), [assignment index](assignments/INDEX.md), role assignment and owned docs/module_status record |
| What tests/setup/release evidence is required? | [TESTING](TESTING.md), [RELEASE_RUNBOOK](RELEASE_RUNBOOK.md), [BLUEPRINT_CHECKS](BLUEPRINT_CHECKS.md); planned tests are not completed evidence |
| Which files do we send and what is current? | [SEND_FILES](SEND_FILES.md), [PROJECT_STATUS](PROJECT_STATUS.md), [INTEGRATION_HANDOFF](INTEGRATION_HANDOFF.md), assignments/SYNC_MANIFEST.json |

On conflict: preserve accepted scope; exact interface shapes come from machine specifications; file-specific detail follows the authority map. Record the conflicting requirement/example, propose a shared change to BACKEND integrator, obtain affected peer review and update dependent contracts/design/tests together. Do not silently pick a convenient version or infer approval from old research. Material changes remain Proposed. No named integrator or peer review has occurred yet.

## Team ownership and handoff contract

Exactly three proposed engineering roles: **FRONTEND** owns UI/client/accessibility; **BACKEND** owns validation, ledger/API/storage/security and also integration/product acceptance coordination; **AI_ML** owns causal baseline adapter, optional gated experiment and independent result checks. Actual names/skills remain unknown. Each implements, verifies and reviews peers. Do not hand one coding agent all three modules. User remains final scope/release authority; no fourth engineer is invented.

Task IDs FE-01–03, BE-01–05 and AIM-01–03 already define paths, dependencies, reviewers, acceptance IDs and checks in the three assignment files. Work in the same repository, or merge reviewed owned changes into one shared baseline. Update only your own module status; submit shared-record/spec changes to BACKEND. Use synchronized packet hashes and the same interface versions. Runtime secrets belong in approved ignored/OS-backed configuration, never chat or documentation. Documentation handoff does not authorize deployment, paid services, private bank access, outreach or real transactions.

## Evidence and release boundary

The user delegated selection in response to the exact option/scope question. The agent selected unchanged RG-02/0.2.0 with T-EXP; [selection evidence](SELECTION_RECORD.json) records the human's actual reply rather than inventing a verbatim named acceptance. [SOLUTION_DECISION.md](SOLUTION_DECISION.md) is authoritative for scope and financial/ML success gates. [DATASET_AUDIT.md](DATASET_AUDIT.md) supplies observed D07 facts; [research amendments](PHASE_02_RESEARCH_AMENDMENTS.md) constrain differentiation claims.

Primary user: treasury analyst/research participant evaluating simulated policies. Reviewer: treasury/risk evaluator. Commercial buyer/geography remain unknown. P01–P06 from research remain stable pain IDs. Goal: compare policies on identical cashflows, endowment and constraints, including the possibility that the conventional baseline wins. No claim of market uniqueness, real-bank safety, solvency or proven ROI.

Release R0 is the first technical proof; R1 is a local user prototype/demo/MVP with synthetic inputs and explicit assumptions. Read-only institutional pilot and production need new scope/rights/security reviews; they are not R1 deliverables. No live transactions, bank integrations, automatic risky-asset allocation, regulatory ratios or production identity service. Tier 2/3 are price-only what-if exposures. App development and Branch T begin in Phase 04, not this documentation phase. Training is optional; deployable AI is not accepted by default.

## Functional requirements

| ID | Requirement / pain | Release | Acceptance |
|---|---|---|---|
| FR-01 | Import D07-style CSV; preserve bytes/hash; validate schema, money, ordering, gaps and boolean flags / P02 | R0 | AC-01 |
| FR-02 | Require versioned endowment, reserve, credit, timing, fees and instrument assumptions; distinguish fictional acknowledgment from real authorization / P01,P02 | R0 | AC-02 |
| FR-03 | Track cash, repo lots, marked holdings, settlements, debt, unpaid obligations and accruals using one ledger / P01 | R0 | AC-03 |
| FR-04 | Respect start-of-hour information, 17:00 locks, 08:00 existing-lot release and terminal boundary / P01,P05 | R0 | AC-04 |
| FR-05 | Compare cash-only and fixed-floor repo baseline under common endowment; selected policy can remain conventional / P04 | R0 | AC-05 |
| FR-06 | Show all four investment tiers; default decisions cash/repo, Tier 2/3 separate capped what-if holdings / P01,P04 | R1 | AC-06 |
| FR-07 | Inject labeled withdrawal/deposit/availability/funding stresses; report infeasible, blocked and unknown honestly / P01,P05 | R1 | AC-07 |
| FR-08 | Produce policy-comparison metrics using identical accounting/funding assumptions / P04 | R0 | AC-05 |
| FR-09 | Trace each decision to source, assumption, policy, adapter and consequence; replay/export inspectable evidence / P03 | R0 | AC-08 |
| FR-10 | Support review, immutable scenario revision and run lifecycle with safe retry/cancel/recovery / P05,P06 | R1 | AC-09 |
| FR-11 | Integrate a labeled no-training forecast adapter; optional experiment cannot override reserve/accounting rules / P01 | R0 | AC-10 |
| FR-12 | Evaluate T-EXP independently; promote model only after frozen gates and reviewer sign-off / P01,P04 | optional T | AC-11 |
| FR-13 | Export signed amounts, assumptions, metrics, evidence and warnings without unrelated workspace files / P03 | R1 | AC-08 |

## Nonfunctional requirements

| ID | Target, not measured result | Acceptance |
|---|---|---|
| NFR-01 | Exact cents for posted cash/debt; deterministic accrual/quantity rules and replay versioning | AC-03,AC-08 |
| NFR-02 | One local workspace; no default network exposure or tenant isolation claim | AC-12 |
| NFR-03 | Schema-first interfaces; no silent breaking changes or independently edited schema copies | AC-13 |
| NFR-04 | Keyboard-complete journeys, text statuses, preserved negative signs, responsive readable tables; WCAG 2.2 AA target, not certified | AC-14 |
| NFR-05 | D07 year baseline replay ≤60s on declared CPU, forecast batch p95 <5s warm; 2 review sessions, 1 active worker | AC-15 |
| NFR-06 | Failed/partial run never displayed as successful; restart marks interrupted work; bounded queues/storage | AC-07,AC-09 |
| NFR-07 | Source minimization, safe upload/export, deny outside-workspace resource access | AC-01,AC-12 |
| NFR-08 | Dependency locks, tests, migration/backup instructions and per-module reviewer before release | AC-13,AC-16 |

## Acceptance IDs

AC-01 valid D07 profile matches archived counts/hash; malformed/nonfinite/gapped input rejected or quarantined with row/field errors, unchanged source. AC-02 missing/unknown assumptions block execution; changing an approved revision creates a new draft; fictional acknowledgment explicit. AC-03 reviewed ledger fixtures conserve cents, units/debt/obligations and terminal wealth with no double count. AC-04 boundary fixtures prevent future-data use, phantom maturity and beyond-file locks. AC-05 policies use identical scenario fingerprints and benchmark; no raw-return-only winner ranking. AC-06 bonds/equities never become default payout reserves or automatic recommendations. AC-07 every seeded unavailable/stale/denied-credit/infeasible condition gives specified blocked/unknown/failure result. AC-08 stored inputs/versions reproduce metrics/evidence exactly; exports retain warnings and integrity hashes. AC-09 idempotency/conflict/cancel/restart behaviors match the API and state design. AC-10 disabled/unavailable model uses explicitly labeled conventional fallback with zero fake accuracy. AC-11 frozen T evaluation meets scope Section 7 or model stays experimental/excluded. AC-12 forged role, wrong workspace/resource, cross-origin and path traversal cases denied; no production security claim. AC-13 interfaces/fixtures/generated clients pass contract checks and changed dependents reviewed. AC-14 keyboard and screen-reader/manual checks plus automated accessibility checks cover all screens/states. AC-15 benchmark includes machine/version/workload and repeated timings; no unrun throughput claim. AC-16 reproducible setup/locks, clean backup/restore and startup recovery demonstrated before R1.

## Metrics, risks, and open decisions

Metric definitions belong to [ARCHITECTURE.md](ARCHITECTURE.md), not the frontend. Compare unpaid amount/duration, cash minimum, debt/interest, realized costs, terminal wealth and net treasury result. Financial and T promotion thresholds remain in accepted scope; proposed usability target is ≥30% faster reconstruction without more critical mistakes (unvalidated). Research recruitment and private data use are not authorized by this blueprint.

Material risks W1–W5 and A09–A13 remain open. [DECISIONS.md](DECISIONS.md) assigns all unresolved choices, including actual people/skills, reserve/caps, rights, instrument terms, fees, hardware and dependency pins. Example scenarios are fictional tests, not accepted banking policies. New material scope stays Proposed and requires versioned review.
