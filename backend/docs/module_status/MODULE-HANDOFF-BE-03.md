# MODULE-HANDOFF — BACKEND / BE-03

Version 2.1.0 | Phase 04 | 2026-10-18 (Asia/Calcutta)

To: BACKEND integration/leader role and requesting user. From: BACKEND coding session.
**Status: Local implementation and comprehensive test verification complete (117/117 passing); awaiting FRONTEND review (FE-02) and integrated acceptance.**

---

## 1. Assignment and Scope

- **Task:** **BE-03 — Stress Injections, Four-Tier Attribution, Policy Comparison, and Evidence Export**
- **Baseline:** Commit `73d6527`, packet `RG02-030A-1.0` / revision 1.1, scope 0.2.0, PRD 1.1, HTTP 0.1.0, adapter 1.0.
- **Authority:** Direct user instruction authorizing Phase 04 backend execution for BE-03.
- **Boundary Preservation:** All changes are strictly confined to `backend/`. All **37 shared baseline files** in `docs/assignments/SYNC_MANIFEST.json` remain untouched and match their exact SHA-256 digests.

---

## 2. Delivered Components

### A. Synthetic Stress Injections (FR-07, AC-07)
Implemented within `app/domain/ledger.py` supporting deterministic stress testing:
- **`withdrawal_shock`**: Applies a 50% surge (1.5x multiplier) to requested client payouts, stress-testing intraday liquidity buffers.
- **`deposit_delay`**: Enqueues incoming gross deposits in a 1-hour settlement delay queue, shifting receipt by 1 hour (and deferring hour-23 deposits past the dataset horizon) to test sensitivity to delayed liquidity inflows.
- **`late_maturity`**: Delays the release of matured overnight repo lots from 08:00 to 12:00 noon, creating an extended morning liquidity blackout window.
- **`denied_credit`**: Sets the effective emergency credit facility limit to 0 (`effective_credit_limit = 0`), denying borrowing and forcing all liquidity deficits to manifest immediately as unpaid obligations and shortfall hours.

### B. Ordering Semantics & Repo Accrual Basis (I05)
- **Ordering Conventions**:
  - `payout_before_deposit`: Gross payouts are evaluated against available cash *before* incoming hourly deposits arrive. If cash is insufficient, credit is drawn or unpaid obligations are incurred.
  - `netted_end_hour`: Hourly deposits and withdrawals are netted at the end of the hour before liquidity buffers are evaluated.
- **Repo Accrual Basis (Invariant I05)**:
  - `effective_apy`: Compound accrual formula `P * ((1 + r)**(hours / 8760) - 1)` quantized to integer cents using `ROUND_HALF_EVEN`.
  - `simple_apr`: Linear accrual formula `P * (r * hours / 8760)` quantized to integer cents using `ROUND_HALF_EVEN`.

### C. Four-Tier Investment Framework (FR-06, AC-06, I06)
- **Tier 0 Cash**: Available operational cash used for payouts and sweeps.
- **Tier 1 Repo**: Overnight reverse repo sweeps locked at 17:00 and released at 08:00 (or 12:00 under `late_maturity`).
- **Tier 2 Bonds**: Medium-term securities marked to market via `tier2_bond_price_index` in terminal wealth; validated against `bond_cap_pct`.
- **Tier 3 Equities**: Risk assets marked to market via `tier3_stock_index_price` in terminal wealth; validated against `equity_cap_pct`.
- **Marked-to-Market Without Liquidation (AC-06)**: Non-cash holdings (Bonds, Equities) are marked to market at scenario prices in terminal wealth attribution without automated liquidation or being treated as default payout reserves. Non-cash exposure caps are strictly validated (`bond_cap_pct + equity_cap_pct <= 100%`).

### D. Policy Comparison Service (`app/services/comparison.py`)
- Computes policy comparison between `cash_only` and `fixed_repo`:
  - **Metrics Deltas**: Treasury result delta, terminal wealth delta, shortfall hours delta, unpaid obligations delta, peak debt delta, and borrowing cost delta.
  - **Four-Tier Summary**: Asset allocation across Cash, Repo, Bonds, and Equities.
  - **Winner Assessment Enforcing AC-05 ("Returns alone never determine winner; safety is prioritized over yield")**: A policy is only preferred if liquidity safety is strictly preserved (zero shortfall hours, zero unpaid obligations, and no increased borrowing distress). If a policy yields higher return but causes shortfalls, `cash_only` is preferred with clear safety rationale.

### E. Evidence Export Bundle with `comparison.json` (FR-09, FR-13, AC-08)
- Updated `build_evidence_bundle()` in `app/services/simulation.py`.
- Generates `comparison.json` containing the policy comparison and embeds it in the verifiable JSON `EvidenceBundle`.
- Updates `manifest.json` with the exact SHA-256 hash of `comparison.json` alongside `scenario.json`, `cash_only_metrics.json`, `fixed_repo_metrics.json`, `cash_only_decisions.json`, and `fixed_repo_decisions.json`.
- Export verified via `GET /api/v1/runs/{id}/export`.

---

## 3. Verification Evidence

- **Test Suite Results:**
  - Command: `.venv\Scripts\python.exe -m pytest -p no:cacheprovider --junitxml=outputs/BE-03-tests.xml`
  - Collected: **117 tests**
  - Passed: **117 passed, 0 failed, 0 errors, 1 warning (Starlette httpx testclient deprecation)**
  - Execution Time: **3.98s**
- **Baseline Verification:**
  - `test_storage_contracts.py::test_all_shared_baseline_hashes_unchanged`: **PASSED (37/37 shared files matched)**
- **Test Breakdown:**
  - `test_http_smoke`: 1 passed (loopback HTTP smoke test)
  - `test_intake`: 36 passed (streamed CSV parser, schema validation, money quantization)
  - `test_ledger_invariants`: 11 passed (Invariants I01–I12, cash conservation law, accrual, credit)
  - `test_runs_api`: 5 passed (run lifecycle, telemetry, pagination, cancellation)
  - `test_scenarios`: 24 passed (scenario validation, caps, fingerprinting, idempotency)
  - `test_security`: 19 passed (auth token bootstrap, CSRF, headers, role matrix)
  - `test_storage_contracts`: 12 passed (OpenAPI contract, schema v2 migration, baseline hashes)
  - `test_stresses_and_comparison`: 9 passed
    - `test_stress_withdrawal_shock`: PASS (50% surge scaled payouts)
    - `test_stress_deposit_delay`: PASS (1-hour delay queue and overdraft interest)
    - `test_stress_late_maturity`: PASS (repo release delayed to 12:00)
    - `test_stress_denied_credit`: PASS (effective credit limit 0, deficits become unpaid)
    - `test_ordering_netted_vs_payout_before_deposit`: PASS (ordering semantics verified)
    - `test_repo_basis_simple_vs_compound`: PASS (linear vs compound accrual verified)
    - `test_four_tiers_marked_holdings_ac06`: PASS (marked holdings in terminal wealth without liquidation)
    - `test_policy_comparison_service_winner_ranking_ac05`: PASS (AC-05 safety-first ranking enforced)
    - `test_evidence_bundle_contains_comparison_json_and_hashes_reconcile`: PASS (comparison.json in export bundle with reconciled SHA-256)
- **Artifacts Generated:**
  - [BE-03-VERIFICATION.json](../../outputs/BE-03-VERIFICATION.json)
  - [BE-03-tests.xml](../../outputs/BE-03-tests.xml)

---

## 4. Integration Notes for Peers

### For Frontend (FE-02)
- Stress injections (`stress_ids`: `["none"]`, `["withdrawal_shock"]`, `["deposit_delay"]`, `["late_maturity"]`, `["denied_credit"]`) can be selected in scenario settings.
- Ordering (`ordering`: `"payout_before_deposit"` or `"netted_end_hour"`) and repo basis (`repo_basis`: `"effective_apy"` or `"simple_apr"`) are fully supported.
- `GET /api/v1/runs/{id}/export` returns an evidence bundle containing `comparison.json` with the exact comparison summary and winner assessment.

### For AI_ML (AIM-02)
- All stress scenarios and four-tier holdings can be paired with forecasting modes (`disabled`, `baseline`, `experimental`) without affecting baseline forecast contracts.

---

## 5. Security and Compliance

- No secrets, keys, or credentials stored or transmitted.
- No remote network communication; execution restricted to local loopback.
- No unapproved package additions.
- All 37 shared baseline files remain intact and hash-verified.
