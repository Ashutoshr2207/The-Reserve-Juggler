# MODULE-HANDOFF — BACKEND / BE-02

Version 2.0.0 | Phase 04 | 2026-10-18 (Asia/Calcutta)

To: BACKEND integration/leader role and requesting user. From: BACKEND coding session.
**Status: Local implementation and comprehensive test verification complete (108/108 passing); awaiting FRONTEND review (FE-02) and integrated acceptance.**

---

## 1. Assignment and Scope

- **Task:** **BE-02 — Evidence Ledger and Schema Version 2 Migration**
- **Baseline:** Commit `73d6527`, packet `RG02-030A-1.0` / revision 1.1, scope 0.2.0, PRD 1.1, HTTP 0.1.0, adapter 1.0.
- **Authority:** Direct user instruction authorizing Phase 04 backend execution.
- **Boundary Preservation:** All changes are strictly confined to `backend/`. All **37 shared baseline files** in `docs/assignments/SYNC_MANIFEST.json` remain untouched and match their exact SHA-256 digests.

---

## 2. Delivered Components

### A. Schema Version 2 Migration (`migrations/002_evidence_ledger.sql`)
- Forward-numbered migration upgrading `schema_version` to `2`.
- Exact tables implemented:
  - `runs`: Run metadata, scenario foreign key, dataset hash, status (`PENDING`, `COMPLETED`, `CANCELLED`, `FAILED`), error redaction, timestamp tracking.
  - `run_policies`: Policies assigned to runs (`cash_only`, `fixed_repo`).
  - `decisions`: Per-origin sweep decisions with proposed cents, result (`ALLOWED`, `BLOCKED`, `UNKNOWN`), reason codes, effective family, and 64-hex SHA-256 `input_hash`.
  - `metrics`: Exact-cent integer metrics per policy (`terminal_wealth_cents`, `treasury_result_cents`, `peak_debt_cents`, `unpaid_new_cents`, `shortfall_hours`, `total_cost_cents`, etc.).
  - `metric_sets`: Versioned collections of run metrics.
  - `ledger_events`: Event-sourced cash, debt, and shortfall movements.
  - `repo_lots`: Lot-level tracking of active and matured repo sweeps with compound accrual.
- Composite foreign keys and strict immutability triggers (`trg_runs_immutable`, `trg_decisions_immutable`, `trg_metrics_immutable`, `trg_ledger_events_immutable`, `trg_repo_lots_immutable`).
- Database migration engine verified: fresh migration to v2, forward migration v1->v2, atomic rollback on failure, and future versions (v3+) fail-closed.

### B. Pure Domain Simulation Engine & Invariants I01–I12 (`app/domain/ledger.py`)
- **Exact Cent Math:** All monetary quantities stored and computed as exact integers (`int64`, non-floating-point).
- **Cash Conservation Law (I03):** Proves mathematically that for every policy:
  `closing_cash == opening_cash + external_net_flow + matured_repo - sweep_cash - borrowing_costs - tx_fees`.
- **Repo Timing (I04):** Repo sweeps only allowed during 17:00 window, locked until 08:00 T+1 maturity. Rejects sweeps maturing beyond the dataset horizon.
- **Compound Effective APY Accrual (I05):** Exact formula `P * ((1 + r)**(hours/8760) - 1)` quantized to the nearest integer cent using bankers' rounding (`ROUND_HALF_EVEN`).
- **Finite Emergency Credit & Overdraft Interest (I07):** Draws credit limit during cash deficits; accrues penalty overdraft interest hourly.
- **Explicit Unpaid Obligations (I08):** Deficits exceeding available credit are tracked explicitly as unpaid flow shortfalls, strictly separated from cash stock.
- **Terminal Wealth & Treasury Result Formula (I09):** Computes `treasury_result = (terminal_wealth - opening_wealth) - external_net_flow`.
- **Policy Comparison (I10):** Runs `cash_only` and `fixed_repo` side-by-side against identical dataset fingerprints.
- **Explicit Adapter Fallback (I11):** Explicitly maps adapter `unavailable` status to contract-compliant `disabled` family with clear quality labeling.
- **Deterministic Replay (I12):** Decision input digests are reproducible across identical runs.

### C. Internal Forecast Adapter Gateway (`app/domain/adapter.py`)
- Conforms strictly to `contracts/forecast-adapter.schema.json`.
- Normalizes dataset hashes to lowercase 64-hex SHA-256 digests.
- Implements causal seasonal baseline forecasting over trailing 24-hour history.
- Handles disabled, unavailable, and experimental modes with explicit fallback quality labels and warnings.

### D. Run Lifecycle API Endpoints (`app/api/application.py`)
- Implemented all 6 run operations:
  - `POST /api/v1/runs`: Creates and triggers simulation for reviewed scenarios.
  - `GET /api/v1/runs/{id}`: Returns run status, scenario details, and summary.
  - `POST /api/v1/runs/{id}/cancel`: Cancels in-flight runs.
  - `GET /api/v1/runs/{id}/metrics`: Returns exact-cent metrics for all executed policies.
  - `GET /api/v1/runs/{id}/decisions`: Returns deterministic decisions with cursor pagination and `input_hash`.
  - `GET /api/v1/runs/{id}/export`: Exports verifiable JSON evidence bundle containing manifest, scenario snapshot, metrics, and decision hashes.
- All 12 OpenAPI endpoints validated against canonical `contracts/openapi.json`.
- 24-hour operation-scoped idempotency, role-based authorization matrix, and workspace isolation enforced.

---

## 3. Verification Evidence

- **Test Suite Results:**
  - Command: `.venv\Scripts\python.exe -m pytest --junitxml=outputs/BE-02-tests.xml`
  - Collected: **108 tests**
  - Passed: **108 passed, 0 failed, 0 errors, 1 warning (Starlette httpx testclient deprecation)**
  - Execution Time: **3.88s**
- **Test Breakdown:**
  - `test_http_smoke`: 1 passed (live loopback HTTP intake, draft, review)
  - `test_intake`: 36 passed (streaming CSV parser, 16 column schema, exact cents, net flow residual tolerance, overflow protection)
  - `test_ledger_invariants`: 11 passed (Invariants I01 through I12, exact cent math, repo accrual, debt, treasury formula)
  - `test_runs_api`: 5 passed (full run lifecycle, metrics, cursor pagination, cancellation, auditor authorization)
  - `test_scenarios`: 24 passed (settings semantics, fictional acknowledgment, 24h idempotency, review preconditions)
  - `test_security`: 19 passed (session bootstrap, CSRF, Host/Origin headers, role authorization matrix, tenant isolation)
  - `test_storage_contracts`: 12 passed (OpenAPI 3.1 contract conformance, all 37 shared baseline hashes unchanged, schema v2 migration, v1->v2 forward migration, atomic rollback, table immutability triggers)
- **Artifacts Generated:**
  - [BE-02-VERIFICATION.json](../../outputs/BE-02-VERIFICATION.json)
  - [BE-02-tests.xml](../../outputs/BE-02-tests.xml)

---

## 4. Integration Notes for Peers

### For Frontend (FE-02)
- All 12 canonical routes defined in `contracts/openapi.json` are now live and functional.
- The UI can create simulations via `POST /api/v1/runs`, poll progress via `GET /api/v1/runs/{id}`, fetch telemetry via `GET /api/v1/runs/{id}/metrics`, paginate decisions via `GET /api/v1/runs/{id}/decisions`, and export evidence via `GET /api/v1/runs/{id}/export`.
- All monetary amounts in requests and responses are strings of integer cents (e.g. `"5000000000"` for $50M).
- Cursor pagination for decisions accepts `limit` and `cursor`, returning next cursor in standard format.

### For AI_ML (AIM-02)
- The backend communicates with forecasting via the `ForecastGateway` abstraction adhering to `contracts/forecast-adapter.schema.json`.
- The gateway currently executes a causal trailing-24h seasonal baseline when `forecast_mode == 'baseline'`, and returns explicit labeled fallback when `disabled` or unavailable.
- Containerized or external models can be mounted directly behind this gateway by satisfying the schema.

---

## 5. Security and Compliance

- No credentials, secrets, or private keys are stored or transmitted.
- No network requests outside the local loopback boundary.
- No paid cloud services, GPU provisioning, external messaging, or live fund transfers were initiated.
- All shared baseline files remain intact and hash-verified.
