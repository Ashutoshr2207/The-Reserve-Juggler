# Local architecture and financial invariants

Blueprint 1.0 | RG-02/0.2.0 | 2026-10-17

## Components and technology choices

Proposed implementation decisions within accepted local scope: React + TypeScript browser UI; Python 3.12 backend with FastAPI/Pydantic; Python Decimal for rates/accrual and integer cents for posted money; SQLite for local metadata/evidence plus workspace-owned immutable source/artifact files. One local worker, one active run, queue maximum 5; poll HTTP, no streaming/broker/agent service. No model is required for baseline. Use a small JSON forecast adapter boundary so AI_ML can evolve independently.

React supports composable stateful components ([official guide](https://react.dev/learn)); FastAPI exposes OpenAPI ([documentation](https://fastapi.tiangolo.com/tutorial/metadata/)); Decimal supports controlled decimal arithmetic ([Python docs](https://docs.python.org/3.12/library/decimal.html)); SQLite foreign-key enforcement must be enabled per connection ([SQLite docs](https://www.sqlite.org/foreignkeys.html)). Sources accessed 2026-10-17. These justify mechanisms, not measured performance or installed runtime. Exact package/Node/build-tool versions must be resolved and locked by module owners in Phase 04; current bundled Python is 3.12.14 but FastAPI/test/ML packages are not prepared. Vite is a proposed frontend build choice; its guide fetch failed, so do not invent a version/engine requirement. No dependencies installed in Phase 03.

Alternative Streamlit would reduce UI effort, but separate teammates need an explicit frontend/backend contract and reviewer-oriented interaction. A React/FastAPI split adds setup and contract maintenance; if team skills make it infeasible, propose ADR change before code. No Docker, Redis, cloud DB or GPU needed for R1. No borrowed repo implementation until source/license gates resolved. Chosen technologies are blueprint decisions authorized by delegated choice; external services and material scope remain unapproved.

Planned files: `frontend/src/` screens/components/client; `backend/app/api/`, `domain/`, `services/`, `storage/`; `ai_ml/` causal adapters/evaluation; `contracts/` shared interface authorities; `tests/` shared contract/integration tests; `migrations/` sequential storage versions. These are future paths, not a claim an application exists. Present executable work is contract checking only.

## Trust boundaries

Untrusted CSV/browser/forecast output → validated API → application services → pure deterministic ledger → scoped storage. HTTP accepts IDs, never caller-selected filesystem paths. Server session context determines workspace/local role; client labels cannot grant access. Forecast adapter sees approved historical data only and returns estimates, never executable financial actions. External network/model APIs absent. OS account and local workspace are the actual isolation boundary; no enterprise multi-tenant security claim. Detailed identity/lifecycle in AUTH_SECURITY.md.

## Data entities

Workspace (local ID, storage root), Dataset (source hash/path, schema/profile, validated clock), ScenarioRevision (immutable settings, dataset reference, content hash/review), Run (scenario/contract/engine/adapter versions, status and timestamps), RepoLot (principal/rate/entry/maturity/encumbrance), Position (tier/quantity/mark), Settlement (due time/amount/state), LedgerEvent (cash/debt/obligation postings), Decision (origin/input cutoff/action/reasons/result), MetricSet (definitions and run summary), ExportManifest (member hashes), AdapterArtifact (provenance/status, optional), IdempotencyEntry (workspace/key/body hash/result/expiry), ReviewRecord (revision/hash/actor/mode). HTTP serialized shapes are authoritative in contracts/openapi.json; adapter shapes in contracts/forecast-adapter.schema.json. No independent ORM schema is delivered as a competing interface spec.

Monetary wire values are signed integer-cent **strings**, not floating numbers; decimal rates/quantities are strings. SQLite posted money uses INTEGER only after int64 bounds checked, otherwise reject with AMOUNT_OUT_OF_RANGE. Times use naive `YYYY-MM-DD HH:MM:SS` under a declared synthetic clock; API creation timestamps are UTC metadata and distinct from simulation origins. Do not append Z to simulation time. File names/resources use generated IDs.

## Authoritative invariants I01–I12

| ID | Invariant / implementation boundary |
|---|---|
| I01 | Source bytes immutable; canonical hourly net = gross deposits − gross withdrawals in cents. Supplied net is reconciliation only; per-row source tolerance ≤1 cent |
| I02 | All decisions at start t use completed rows strictly before t. Scheduled flags are allowed calendar knowledge, future outcome/market data is not |
| I03 | Cash postings conserve: closing cash = opening cash + settled proceeds + deposits + credit draws − actually paid obligations − purchases − repayments − paid fees. Unsettled marked value is not cash |
| I04 | Repo entry at allowed 17:00 only, one lot lifecycle; principal removed once, returned once at eligible maturity. No initial phantom lot or entry maturing after available horizon |
| I05 | Repo accrual is fixed entry-rate effective APY over actual hours/8,760, quantized HALF_EVEN to cents only when posted. Alternative simple-rate basis is a separate declared scenario, not mixed inside a run |
| I06 | Price-only bond/equity marks; no yield-as-coupon or duration-plus-observed-price duplicate income. Liquidation haircuts apply once to proceeds; positions/settlement states track quantity until disposed |
| I07 | Credit principal ≥0 and ≤configured finite limit; interest accrues on actual outstanding time at scenario APR/8,760. Debt and unpaid interest remain liabilities at terminal time. No implicit unlimited lender or reset |
| I08 | Unpaid requested withdrawals become explicit liabilities. Track newly unpaid, outstanding and later paid separately; do not silently drop them or count repeated outstanding stock as new unpaid flow |
| I09 | Net wealth = accessible cash + noncash receivables/marked positions − debt − outstanding unpaid obligations − unpaid interest/fees, without counting assets twice. Net treasury result = wealth change − (gross deposits − requested withdrawals), with other external funding recorded separately as capital/debt, never income |
| I10 | Compared policies share dataset, initial endowment, rates/costs, exposure/currency/risk/credit limits and stress schedule; only declared policy/adapter differs. Risky scenario not ranked as equivalent to cash/repo safety |
| I11 | Any material input/evidence unknown → BLOCKED/UNKNOWN decision, never implicit safe zero. Runtime failure invalidates complete metrics. Financial shortfalls in a valid calculation remain visible even when run state COMPLETED |
| I12 | Immutable scenario/run version graph; input, engine and adapter identities retained. Replays must reproduce posted ledger/evidence; safe fallback identity recorded. No edit to completed results |

Scenario cash reserve, cap amounts, fees and settlement delays have no hidden financial defaults. User supplies them or explicitly acknowledges fictional settings. Quantity calculation uses Decimal precision 28; retain residual dust in cash; price-only demonstration lots may use fractional units to 8 decimal places, round toward zero on buy, never invent money. This numerical convention is provisional implementation detail within what-if scope, not real exchange lot rules. Nonzero initial investments require price at time before first decision or an explicitly declared opening cost/mark; otherwise initial positions must be zero.

## Metrics (single authority)

Unpaid-new amount = sum of newly unserved requested payouts; outstanding unpaid is a stock. Shortfall hours = count of hours with positive outstanding unpaid, episode count = transitions into that state; do not sum stock as cumulative loss. Minimum usable cash is cash available before required payouts under ordering convention. Peak/mean overdraft uses outstanding principal at recorded hour boundaries; accrued interest recorded separately. Terminal wealth and treasury result follow I09; total costs separate borrowing interest, fees and liquidation haircuts. Returns on investment alone never determine winner. Exports include metric_definition_version `1.0` and scenario fingerprint. Future model metrics live in AI_EVALUATION.md.

## Persistence, migrations and recovery

SQLite metadata and ledger events committed in one transaction per simulated hour/checkpoint; raw source files move atomically to content-addressed workspace paths after validation. Enable foreign_keys=ON on every connection. Use unique (workspace,idempotency_key) and (run,event_sequence) constraints. Do not duplicate a run on retry; if worker crashes, mark run INTERRUPTED on restart and preserve partial events as incomplete. R1 restarts from beginning into a new run rather than claiming checkpoint resume.

First Phase 04 migration `migrations/001_initial.sql` creates entity relationships and schema_version=1; subsequent forward numbered migrations, backup-before-migration, verify foreign keys and ledger totals. Roll back by restoring prior DB+artifact snapshot, not attempting untested reverse financial migrations. No actual DB/migrations exist in Phase 03. Retention/deletion and workspace lifecycle are in AUTH_SECURITY.md; operating steps in RELEASE_RUNBOOK.md.

Integration must fail if schema version is unsupported; no auto-downgrade. The executable HTTP/adapter specifications, fixture hashes and blueprint_version are the shared contract; changes follow DECISIONS.md before regeneration of clients/validators. Finance logic is server-owned; frontend displays values, AI_ML returns estimates only.
